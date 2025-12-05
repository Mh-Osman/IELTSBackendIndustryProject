# ai_evaluator.py
import os
import json
import base64
import imghdr
import openai

from django.shortcuts import get_object_or_404
from .models import WritingAnswer, WritingEvaluation

openai.api_key = os.getenv("OPENAI_API_KEY")


def _extract_json_from_str(s: str):
    """Try to parse JSON string robustly, including heuristic extraction."""
    s = s.strip()
    if not s:
        return None
    # direct parse
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # heuristic: find first {...} block
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                return None
        return None


def _prepare_image_data_url(image_bytes: bytes):
    """Return data URL or None."""
    if not image_bytes:
        return None
    fmt = imghdr.what(None, h=image_bytes) or "jpeg"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/{fmt};base64,{b64}"


def generate_ielts_feedback(task1_text: str,
                            task2_text: str,
                            question_data: dict,
                            task1_image_bytes: bytes = None,
                            include_scores: bool = False,
                            model: str = "gpt-4o",
                            temperature: float = 0.0,
                            max_tokens: int = 800):
    """
    Call OpenAI to get an IELTS evaluation.
    - include_scores: if True, instruct the model to include numeric scores for each criterion.
    Returns parsed dict or None on failure.
    """

    # Build strict JSON schema depending on include_scores
    if include_scores:
        schema_example = {
            "task1": {
                "task_achievement": 7.0,
                "coherence_cohesion": 6.5,
                "lexical_resource": 7.0,
                "grammar_accuracy": 6.5
            },
            "task2": {
                "task_achievement": 7.0,
                "coherence_cohesion": 7.0,
                "lexical_resource": 7.5,
                "grammar_accuracy": 7.0
            },
            "strengths": ["..."],
            "areas_for_improvement": ["..."],
            "comments": "..."
        }
        system_msg = (
            "You are a Senior IELTS Writing Examiner. RESPOND ONLY in valid JSON and match EXACTLY the schema. "
            "Include numeric scores between 0.0 and 9.0 for each criterion in 'task1' and 'task2'. "
            "Return numeric scores as floats (e.g. 7.0). Provide 3-6 short strengths and 3-6 short improvement points. "
            "Return only the JSON object, nothing else. Example:\n" + json.dumps(schema_example, indent=2)
        )
    else:
        schema_example = {
            "strengths": ["Clear overview of main trends", "Good use of data"],
            "areas_for_improvement": ["Include more specific data comparisons"],
            "comments": "Optional paragraph-style feedback."
        }
        system_msg = (
            "You are a Senior IELTS Writing Examiner. RESPOND ONLY in valid JSON and match EXACTLY the schema. "
            "Do NOT include any numeric scores or band values. Provide 3-6 concise strengths and 3-6 improvement points. "
            "Return only the JSON object, nothing else. Example:\n" + json.dumps(schema_example, indent=2)
        )

    # Build user message with content
    user_content = f"""
Task 1 Prompt: {question_data.get('task1_prompt','(none)')}

Task 1 Student Answer:
{task1_text}

Task 2 Prompt: {question_data.get('task2_question','(none)')}

Task 2 Student Answer:
{task2_text}

Instructions: Evaluate the student's writing according to IELTS writing band descriptors.
"""

    # Attach image as data url if provided
    image_data_url = _prepare_image_data_url(task1_image_bytes)
    if image_data_url:
        user_content += f"\nTask 1 Image (data URL): {image_data_url}\n"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content}
    ]

    try:
        # NOTE: adapt to your installed OpenAI SDK method name; using ChatCompletion style used earlier
        resp = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            # response_format={"type":"json_object"}  # optional structured output if supported
        )
    except Exception as e:
        print("OpenAI API call failed:", e)
        return None

    # Extract message content robustly
    content_candidate = None
    try:
        # support both object-like and dict-style responses
        if getattr(resp, "choices", None):
            choice = resp.choices[0]
            # try new style: choice.message.content
            msg = getattr(choice, "message", None) or (choice.get("message") if isinstance(choice, dict) else None)
            if msg is not None:
                content_candidate = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
            # fallback to text
            if content_candidate is None:
                content_candidate = getattr(choice, "text", None) or (choice.get("text") if isinstance(choice, dict) else None)
        elif isinstance(resp, dict) and resp.get("choices"):
            choice = resp["choices"][0]
            content_candidate = (choice.get("message") or {}).get("content") or choice.get("text")
        else:
            # maybe top-level output
            if isinstance(resp, dict):
                content_candidate = resp.get("output") or resp.get("output_text") or None
    except Exception:
        content_candidate = None

    if content_candidate is None:
        print("Could not find content in OpenAI response. Response repr:", repr(resp)[:1000])
        return None

    # If dict already
    if isinstance(content_candidate, dict):
        return content_candidate

    # If bytes, decode
    if isinstance(content_candidate, (bytes, bytearray)):
        try:
            content_candidate = content_candidate.decode("utf-8")
        except Exception as e:
            print("Failed to decode bytes content:", e)
            return None

    # If string — parse JSON
    if isinstance(content_candidate, str):
        parsed = _extract_json_from_str(content_candidate)
        if parsed is None:
            print("Failed to parse JSON from model output. Model output (trim):", content_candidate[:2000])
            return None
        return parsed

    # Unexpected type
    print("Unexpected content type from model:", type(content_candidate))
    return None


def save_ai_evaluation(writing_answer_id: int, include_scores: bool = False):
    """
    Fetch writing answer, call generate_ielts_feedback, and update/create WritingEvaluation.
    - If AI returns numeric scores and include_scores True, numeric DB fields will be updated.
    - If AI does not return numeric scores, numeric fields are left unchanged.
    """
    wa = get_object_or_404(WritingAnswer, id=writing_answer_id)

    task1_text = getattr(wa, "task1_text", None) or getattr(wa, "task1", "")  # adjust field names
    task2_text = getattr(wa, "task2_text", None) or getattr(wa, "task2", "")

    # read image bytes if present
    img_bytes = None
    try:
        img_field = getattr(wa, "task1_image", None)
        if img_field and hasattr(img_field, "open"):
            img_field.open("rb")
            img_bytes = img_field.read()
            img_field.close()
    except Exception as e:
        print("Warning reading image:", e)
        img_bytes = None

    ai_resp = generate_ielts_feedback(task1_text, task2_text, {
        "task1_prompt": getattr(wa, "task1_prompt", ""),
        "task2_question": getattr(wa, "task2_question", "")
    }, task1_image_bytes=img_bytes, include_scores=include_scores)

    if not ai_resp:
        print("AI returned nothing for WritingAnswer id:", writing_answer_id)
        return None

    # Prepare defaults for update_or_create; only include numeric fields if present in ai_resp
    defaults = {}

    # Qualitative fields
    strengths = ai_resp.get("strengths")
    areas = ai_resp.get("areas_for_improvement") or ai_resp.get("areas")
    comments = ai_resp.get("comments") or ai_resp.get("feedback")

    if strengths is not None:
        # normalize to list of strings
        if isinstance(strengths, str):
            strengths_list = [s.strip() for s in strengths.splitlines() if s.strip()]
        elif isinstance(strengths, list):
            strengths_list = [str(s).strip() for s in strengths if str(s).strip()]
        else:
            strengths_list = []
        defaults["strengths"] = strengths_list or []

    if areas is not None:
        if isinstance(areas, str):
            areas_list = [s.strip() for s in areas.splitlines() if s.strip()]
        elif isinstance(areas, list):
            areas_list = [str(s).strip() for s in areas if str(s).strip()]
        else:
            areas_list = []
        defaults["areas_for_improvement"] = areas_list or []

    # Optional free text field; only set if field exists on model
    if comments and hasattr(WritingEvaluation, "free_feedback"):
        defaults["free_feedback"] = str(comments)[:2000]

    # Numeric scores (only if include_scores True and AI provided them)
    def _safe_get_score(obj, path_list):
        cur = obj
        try:
            for p in path_list:
                cur = cur[p]
            return float(cur)
        except Exception:
            return None

    if include_scores:
        # task1 scores path: ai_resp["task1"]["task_achievement"], etc.
        t1 = ai_resp.get("task1", {})
        t2 = ai_resp.get("task2", {})

        t1_task_achievement = _safe_get_score(ai_resp, ["task1", "task_achievement"])
        t1_coh = _safe_get_score(ai_resp, ["task1", "coherence_cohesion"])
        t1_lex = _safe_get_score(ai_resp, ["task1", "lexical_resource"])
        t1_gram = _safe_get_score(ai_resp, ["task1", "grammar_accuracy"]) or _safe_get_score(ai_resp, ["task1", "grammatical_range_accuracy"])

        if t1_task_achievement is not None:
            defaults["task_achievement_score_task1"] = t1_task_achievement
        if t1_coh is not None:
            defaults["coherence_cohesion_score_task1"] = t1_coh
        if t1_lex is not None:
            defaults["lexical_resource_score_task1"] = t1_lex
        if t1_gram is not None:
            defaults["grammatical_range_accuracy_score_task1"] = t1_gram

        t2_task_achievement = _safe_get_score(ai_resp, ["task2", "task_achievement"])
        t2_coh = _safe_get_score(ai_resp, ["task2", "coherence_cohesion"])
        t2_lex = _safe_get_score(ai_resp, ["task2", "lexical_resource"])
        t2_gram = _safe_get_score(ai_resp, ["task2", "grammar_accuracy"]) or _safe_get_score(ai_resp, ["task2", "grammatical_range_accuracy"])

        if t2_task_achievement is not None:
            defaults["task_achievement_score_task2"] = t2_task_achievement
        if t2_coh is not None:
            defaults["coherence_cohesion_score_task2"] = t2_coh
        if t2_lex is not None:
            defaults["lexical_resource_score_task2"] = t2_lex
        if t2_gram is not None:
            defaults["grammatical_range_accuracy_score_task2"] = t2_gram

    # Update or create evaluation
    evaluation_obj, created = WritingEvaluation.objects.update_or_create(
        writing_answer=wa,
        defaults=defaults
    )

    # Recalculate final bands if necessary (model.save() calls calculate_scores() already)
    evaluation_obj.calculate_scores()
    evaluation_obj.save()

    return evaluation_obj
