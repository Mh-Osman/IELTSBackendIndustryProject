#response
# {
#   "task1": {
#     "task_achievement": 0.0,
#     "coherence_cohesion": 0.0,
#     "lexical_resource": 0.0,
#     "grammatical_range_accuracy": 0.0
#   },
#   "task2": {
#     "task_achievement": 0.0,
#     "coherence_cohesion": 0.0,
#     "lexical_resource": 0.0,
#     "grammatical_range_accuracy": 0.0
#   },
#   "strengths": [],
#   "areas_for_improvement": [],
#   "comments": ""
# }




# ai_evaluator.py
import os
import json
import base64
import imghdr
import openai

from django.shortcuts import get_object_or_404

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_ielts_feedback(task1_text: str,
                            task2_text: str,
                            question_data: dict,
                            task1_image_bytes: bytes = None,
                            model: str = "gpt-4o",
                            temperature: float = 0.0,
                            max_tokens: int = 100):
    print(openai.api_key)  # Debugging line to check if the API key is set
    system_msg = """
You are a Senior IELTS Writing Examiner.

Your ONLY output must be a valid JSON object that matches EXACTLY the schema below.
No explanations, no markdown, no additional text. JSON only.

SCHEMA:
{
  "task1": {
    "task_achievement": 0.0,
    "coherence_cohesion": 0.0,
    "lexical_resource": 0.0,
    "grammatical_range_accuracy": 0.0
  },
  "task2": {
    "task_achievement": 0.0,
    "coherence_cohesion": 0.0,
    "lexical_resource": 0.0,
    "grammatical_range_accuracy": 0.0
  },
  "strengths": [],
  "areas_for_improvement": [],
  "comments": ""
}

RULES:
- Use only floats for scores (e.g. 6.0, 7.5).
- Provide 3–6 strengths.
- Provide 3–6 improvement points.
- Comments should be 1 short paragraph.
- Do NOT include band labels.
- DO NOT return anything except valid JSON.
"""

    # Prepare user content
    user_content = f"""
Task 1 Question: {question_data.get('task1_prompt', '')}
Task 1 Answer:
{task1_text}

Task 2 Question: {question_data.get('task2_question', '')}
Task 2 Answer:
{task2_text}
"""

    # Add image if present
    if task1_image_bytes:
        fmt = imghdr.what(None, task1_image_bytes) or "jpeg"
        b64 = base64.b64encode(task1_image_bytes).decode()
        user_content += f"\nTask1 Image: data:image/{fmt};base64,{b64}\n"

    # Call OpenAI API
    resp = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Extract content
    output = resp.choices[0].message["content"]

    # Parse JSON
    return json.loads(output)
