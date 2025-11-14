from django.db import models
from users.models import CustomUser


# -----------------------------
# 1️⃣ Reading Exam / Task Model
# -----------------------------
class ReadingExamModel(models.Model):
    EXAM_TYPES = [
        ('academic', 'Academic'),
        ('general', 'General Training'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam_type = models.CharField(max_length=50, choices=EXAM_TYPES, default='academic')
    total_passages = models.PositiveIntegerField(default=3)
    duration_minutes = models.PositiveIntegerField(default=60)  # e.g., 60 mins

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.exam_type.capitalize()})"


# -----------------------------
# 2️⃣ Reading Passage Model
# -----------------------------
class ReadingPassageModel(models.Model):
    exam = models.ForeignKey(
        ReadingExamModel,
        on_delete=models.CASCADE,
        related_name='passages'
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exam.title} - Passage {self.order}: {self.title}"


# -----------------------------
# 3️⃣ Reading Question Model
# -----------------------------
class ReadingQuestionModel(models.Model):
    QUESTION_TYPES = [
        ('true_false_not_given', 'Identifying Information'),
        ('writer_view', 'Writer’s View/Claim'),
        ('multiple_choice', 'Multiple Choice'),
        ('matching_heading', 'Matching Headings'),
        ('matching_info', 'Matching Information'),
        ('matching_feature', 'Matching Features'),
        ('matching_sentence', 'Matching Sentence Ending'),
        ('sentence_completion', 'Sentence Completion'),
        ('summary_completion', 'Summary/Table/Flowchart'),
        ('diagram_label', 'Diagram Label Completion'),
        ('short_answer', 'Short Answer Question'),
    ]

    passage = models.ForeignKey(
        ReadingPassageModel,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=1)
    marks = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.passage.title} - Q{self.order}"


# -----------------------------
# 4️⃣ Reading Option Model
# -----------------------------
class ReadingOptionModel(models.Model):
    """
    
    Multiple choice, matching,
    """
    question = models.ForeignKey(
        ReadingQuestionModel,
        on_delete=models.CASCADE,
        related_name='options'
    )

    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question.id} - {self.text}"


# -----------------------------
# 5️⃣ Reading Answer Model
# -----------------------------
class ReadingAnswerModel(models.Model):
    """
    user will answer each question and store the response here.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reading_answers')
    exam = models.ForeignKey(ReadingExamModel, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    passage = models.ForeignKey(ReadingPassageModel, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    question = models.ForeignKey(ReadingQuestionModel, on_delete=models.CASCADE, related_name='answers')

    selected_answer = models.CharField(max_length=255, null=True, blank=True)
    selected_answers_multiple = models.JSONField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.exam and self.passage:
            self.exam = self.passage.exam
        elif not self.passage and self.question:
            self.passage = self.question.passage
            self.exam = self.question.passage.exam
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"


# -----------------------------
# 6️⃣ Reading Evaluation Model
# -----------------------------
class ReadingEvaluationModel(models.Model):
    """
    performance evaluation after completing the reading exam.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reading_evaluations')
    exam = models.ForeignKey(ReadingExamModel, on_delete=models.CASCADE, related_name='evaluations')

    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    band_score = models.FloatField(default=0.0)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def calculate_band_score(self):
        """
        Calculates the score based on the official IELTS band conversion.
        """
        if self.exam.exam_type == 'academic':
            mapping = [
                (39, 9), (37, 8.5), (35, 8), (33, 7.5),
                (30, 7), (27, 6.5), (23, 6), (19, 5.5),
                (15, 5), (13, 4.5), (10, 4), (7, 3.5),
                (5, 3), (3, 2.5)
            ]
        else:
            mapping = [
                (40, 9), (39, 8.5), (37, 8), (36, 7.5),
                (34, 7), (32, 6.5), (30, 6), (27, 5.5),
                (23, 5), (19, 4.5), (15, 4), (12, 3.5),
                (9, 3), (6, 2.5)
            ]

        band = 2  # default
        for min_score, b in mapping:
            if self.correct_answers >= min_score:
                band = b
                break

        self.band_score = band
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.exam.title} ({self.band_score})"
