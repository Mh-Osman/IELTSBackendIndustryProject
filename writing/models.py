from django.db import models
from django.core.exceptions import ValidationError

from users.models import CustomUser

class WritingTypeTask(models.Model):
    TYPE_CHOICES = [
        ("Academic", "Academic"),
        ("General", "General"),
    ]

    TASK_CHOICES = [
        ("task1", "Task 1"),  # expects an image (e.g., graph / chart / diagram)
        ("task2", "Task 2"),
    ]

    writing_type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, default="Academic"
    )
    writing_task = models.CharField(
        max_length=50, choices=TASK_CHOICES, default="task1"
    )

    image = models.ImageField(
        upload_to="writing_task_images/",
        blank=True,
        null=True,
       help_text="Required for Task 1 (e.g., graph/chart images).",
    )

    text = models.TextField(blank=True, default="")

    def clean(self):
        errors = {}

        if self.writing_task == "task1":
            # if instance has no file assigned
            if not self.image:
                errors["image"] = ValidationError(
                    "Image is required for Task 1."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
      
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_writing_type_display()} - {self.get_writing_task_display()}"


from django.utils import timezone
class WritingPracticeSession(models.Model):
    user = models.ForeignKey(

        CustomUser,on_delete=models.CASCADE
    )
 
    task_list = models.ManyToManyField(
        WritingTypeTask,
        blank=True,
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    
    def is_expired(self):
        from django.utils import timezone
        if self.end_time:
            return timezone.now() > self.end_time
        return False
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        self.end_time = self.start_time + timezone.timedelta(minutes=61)
        self.full_clean()
        super().save(*args, **kwargs)
    

class WritingAnswer(models.Model):
    """
    Stores a user's Task1 + Task2 answers and the WritingTypeTask references.
    Validates that task1_type is a 'task1' type and task2_type is 'task2'.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="writing_answers"
    )
    
    session = models.OneToOneField(

        WritingPracticeSession,
        on_delete= models.SET_NULL,
        null=True,
        blank=True,
        help_text="Without a linked active session this will not  be evaluated.",
    )
    # student answers
    task1 = models.TextField(blank=True, default="")
    task2 = models.TextField(blank=True, default="")

    # which task/problem they responded to
    task1_type = models.ForeignKey(
        WritingTypeTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task1_answers",
        help_text="Should reference a WritingTypeTask with writing_task='task1'"
    )

    task2_type = models.ForeignKey(
        WritingTypeTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task2_answers",
        help_text="Should reference a WritingTypeTask with writing_task='task2'"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"WritingAnswer(id={self.id}, user={self.user_id}, created={self.created_at})"

    def clean(self):
        """
        Custom validation:
         - If task1_type provided, it must be a WritingTypeTask where writing_task == 'task1'
         - If task2_type provided, it must be writing_task == 'task2'
        """
        errors = {}

        if self.task1_type and getattr(self.task1_type, "writing_task", None) != "task1":
            errors["task1_type"] = ValidationError(
                "task1_type must point to a WritingTypeTask with writing_task='task1'."
            )

        if self.task2_type and getattr(self.task2_type, "writing_task", None) != "task2":
            errors["task2_type"] = ValidationError(
                "task2_type must point to a WritingTypeTask with writing_task='task2'."
            )

        if errors:
            raise ValidationError(errors)

        super().clean()

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.full_clean()
        super().save(*args, **kwargs)




class WritingEvaluation(models.Model):

    writing_answer = models.OneToOneField(
        WritingAnswer,
        on_delete=models.CASCADE,
        related_name="evaluation"
    )

    # TASK 1
    task_achievement_score_task1 = models.FloatField(null=True, blank=True)
    coherence_cohesion_score_task1 = models.FloatField(null=True, blank=True)
    lexical_resource_score_task1 = models.FloatField(null=True, blank=True)
    grammatical_range_accuracy_score_task1 = models.FloatField(null=True, blank=True)
    overall_band_score_task1 = models.FloatField(null=True, blank=True)

    # TASK 2
    task_achievement_score_task2 = models.FloatField(null=True, blank=True)
    coherence_cohesion_score_task2 = models.FloatField(null=True, blank=True)
    lexical_resource_score_task2 = models.FloatField(null=True, blank=True)
    grammatical_range_accuracy_score_task2 = models.FloatField(null=True, blank=True)
    overall_band_score_task2 = models.FloatField(null=True, blank=True)

    # FINAL
    overall_writing_band = models.FloatField(null=True, blank=True)


    #feedback
    strengths = models.JSONField(null=True, blank=True)  # stores list of strings
    areas_for_improvement = models.JSONField(null=True, blank=True)  # stores list of strings

    def ielts_round(self, score):
        decimal = score - int(score)
        if decimal < 0.25:
            return float(int(score))
        elif decimal < 0.75:
            return float(int(score)) + 0.5
        else:
            return float(int(score) + 1)

    def calculate_scores(self):

        # --- TASK 1 ---
        if all([
            self.task_achievement_score_task1,
            self.coherence_cohesion_score_task1,
            self.lexical_resource_score_task1,
            self.grammatical_range_accuracy_score_task1
        ]):
            avg1 = (
                self.task_achievement_score_task1 +
                self.coherence_cohesion_score_task1 +
                self.lexical_resource_score_task1 +
                self.grammatical_range_accuracy_score_task1
            ) / 4

            self.overall_band_score_task1 = self.ielts_round(avg1)

        # --- TASK 2 ---
        if all([
            self.task_achievement_score_task2,
            self.coherence_cohesion_score_task2,
            self.lexical_resource_score_task2,
            self.grammatical_range_accuracy_score_task2
        ]):

            avg2 = (
                self.task_achievement_score_task2 +
                self.coherence_cohesion_score_task2 +
                self.lexical_resource_score_task2 +
                self.grammatical_range_accuracy_score_task2
            ) / 4

            self.overall_band_score_task2 = self.ielts_round(avg2)

        # --- FINAL WRITING BAND (TASK2 weighted double) ---
        if self.overall_band_score_task1 and self.overall_band_score_task2:
            final_avg = (
                self.overall_band_score_task1 +
                2 * self.overall_band_score_task2
            ) / 3

            self.overall_writing_band = self.ielts_round(final_avg)

    def save(self, *args, **kwargs):
        self.calculate_scores()
        super().save(*args, **kwargs)
