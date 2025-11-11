from django.db import models

from users.models import CustomUser
class ReadingPassageModel(models.Model):
    Type = [

        ("Academic", "Academic"),
        ("General", "General"),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    exam_type = models.CharField(max_length=30, choices=Type)

    def __str__(self):
        return self.title
    

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


class 5(models.Model):
    question = models.ForeignKey(
        ReadingQuestionModel,
        on_delete=models.CASCADE,
        related_name='options'
    )

    question_text = models.TextField()    
    options = models.JSONField()
    question_answer_one = models.CharField(max_length=255)
    question_answer_multiple = models.JSONField()

class ReadingAnswerModel(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reading_answers'
    )

    
