from django.db import models
from django.core.exceptions import ValidationError

# ------------------------------
# WritingModel
# ------------------------------
class WritingExamModel(models.Model):
    TAG = [
        ("general", "General"),
        ("academic", "Academic"),
    ]

    title = models.CharField(max_length=100)
    tag = models.CharField(max_length=30, choices=TAG)

    def __str__(self):
        return f"{self.title} ({self.tag}) ({self.id})"
    




from cloudinary_storage.storage import MediaCloudinaryStorage


# ------------------------------
# WritingTaskModel
# ------------------------------
class WritingTaskModel(models.Model):
    TASK_CHOICES = [
        ("task1", "Task 1"),
        ("task2", "Task 2"),
    ]

    TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
    ]

    exam = models.ForeignKey(
        WritingExamModel,
        on_delete=models.CASCADE,
        related_name="all_questions"  # corrected spelling
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    task = models.CharField(max_length=10, choices=TASK_CHOICES)
    the_question = models.TextField(blank=True, null=True)
    image_file = models.FileField(
        storage=MediaCloudinaryStorage(),
        upload_to='images/writing/img/',
        null=True,
        blank=True
    )
    source = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f"{self.task} ({self.exam.title}) ({self.id})"

    def clean(self):
        """Custom validation based on type"""
        if self.type == 'image' and not self.image_file:
            raise ValidationError("Image file is required for image tasks.")
        if self.type == 'text' and not self.the_question:
            raise ValidationError("Question text is required for text tasks.")
        
    def save(self, *args,**kwargs):
        self.full_clean()
        super().save(*args, **kwargs)




from users.models import CustomUser
class WritingAnswerModel(models.Model):
    exam = models.ForeignKey(
            WritingExamModel , 
            on_delete=models.CASCADE, 
            related_name="answers"
            )
    answer = models.ForeignKey(
        WritingTaskModel,
          on_delete=models.CASCADE,
          related_name="answers_of_task"
          
        )
    user=models.ForeignKey(
        CustomUser,            
       on_delete=models.CASCADE, 
       related_name="writing_answers"
       
       )
    weight = models.PositiveIntegerField(default=1)


    def get_weight(self):
        if self.answer.task == "task1":
            self.weight=1
        else:
            self.weight=2

    def __str__(self):
        return f"{self.user} - {self.answer.task} ({self.exam.title})"       
    

    def save(self, *args,**kwargs):
       self.get_weight()
       super().save(*args,**kwargs)

class WritingEvalution(models.Model):
    evalute=models.OneToOneField(
        WritingAnswerModel,
        on_delete=models.CASCADE,
        related_name="evaluation"
        )
    task_response=models.FloatField()
    coherence_cohesion=models.FloatField()
    lexical_resource = models.FloatField()
    grammatical_range_accuracy=models.FloatField()
    overall_band=models.FloatField()
   
    
    def save(self, *args, **kwargs):
        """Auto-calculate overall band from 4 criteria"""
        self.overall_band = (
            self.task_response +
            self.coherence_cohesion +
            self.lexical_resource +
            self.grammatical_range_accuracy
        ) / 4
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation for {self.evalute.user} - {self.evalute.answer.task} ({self.id})"


class WrintingBandScoreModel(models.Model):
    user=models.ForeignKey(
        CustomUser ,
         on_delete=set.null,
         related_name="writing_bands"
         )

    exam = models.ForeignKey(
        WritingExamModel,
        on_delete=models.CASCADE,
        related_name="final_scores"
          )

    final_Band = models.FloatField()
    #user details
    #will be set in future 
    def calculate_final_band(self):
        """Calculate weighted band from user’s two tasks"""
        answers = WritingAnswerModel.objects.filter(user=self.user, exam=self.exam)
        if not answers.exists():
            return 0.0
        
        total = 0
        total_weight = 0
        for ans in answers:
            if hasattr(ans, "evaluation"):
                total += ans.evaluation.overall_band * ans.weight
                total_weight += ans.weight
        self.final_band = total / total_weight if total_weight else 0.0
        return self.final_band

    def __str__(self):
        return f"{self.user} - Final Band: {self.final_band}({self.id})"