from django.db import models, transaction
from django.db.models import Max
from django.core.exceptions import ValidationError
from decimal import Decimal
from users.models import CustomUser
from cloudinary_storage.storage import MediaCloudinaryStorage


class WritingTypeTaskModel(models.Model):
    TYPE_CHOICES = [
        ("Academic", "Academic"),
        ("General", "General"),
    ]

    TASK_CHOICES = [
        ("task1", "Task 1"),  # Task 1 has image
        ("task2", "Task 2"),  # Task 2 is text only
    ]

    id = models.BigAutoField(primary_key=True)
    number = models.PositiveBigIntegerField(unique=True, editable=False)
    question_text = models.TextField()
    image = models.ImageField(
        storage=MediaCloudinaryStorage(),
        upload_to="writing_exam_images/",
        max_length=600,
        blank=True,
        null=True,
    )
    task = models.CharField(max_length=30, choices=TASK_CHOICES)
    exam_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def clean(self):
        if self.task == "task1" and not self.image:
            raise ValidationError({"image":"Image is required for Task 1 question."})
        if self.task == "task2" and self.image:
            raise ValidationError({"image":"Image not allowed for Task 2."})

    def save(self, *args, **kwargs):
        if not self.number:
            with transaction.atomic():
                last_number = (
                    WritingTypeTaskModel.objects.select_for_update()
                    .aggregate(max_num=Max("number"))
                    .get("max_num") or 0
                )
                self.number = last_number + 1
   
        self.full_clean()
        super().save(*args, **kwargs)
     
    def __str__(self):
        return f"{self.exam_type} - {self.task} - {self.number}"




# writing/models.py
from django.db import models
from django.utils import timezone
from users.models import CustomUser
import uuid


class WritingPracticeSession(models.Model):
    SESSION_DURATION_MINUTES = 60

    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    task1 = models.ForeignKey(
        "WritingTypeTaskModel",
        on_delete=models.SET_NULL,
        null=True,
        related_name="task1_sessions"
    )
    task2 = models.ForeignKey(
        "WritingTypeTaskModel",
        on_delete=models.SET_NULL,
        null=True,
        related_name="task2_sessions"
    )

    exam_type = models.CharField(max_length=20)  # Academic / General

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def expires_at(self):
        return self.start_time + timezone.timedelta(minutes=self.SESSION_DURATION_MINUTES)

    @property
    def is_expired(self):
        if self.end_time:
            return True
        return timezone.now() > self.expires_at()

    def expire(self):
        if not self.end_time:
            self.end_time = timezone.now()
            self.save(update_fields=["end_time"])

    def __str__(self):
        return f"{self.user.email} - {self.session_id}"


class LockExamSession(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name="exam_sessions"
    )

    is_locked = models.BooleanField(default=False)

    # MANY-TO-MANY HERE
    locked_tasks = models.ManyToManyField(
        WritingTypeTaskModel,
        related_name="locked_sessions"
    )

    start_time = models.DateTimeField(default=timezone.now)

    duration_time = models.IntegerField(default=60)

    @property
    def expire_at(self):
        return self.start_time + timedelta(minutes=self.duration_time)

    @property
    def is_expired(self):
        return timezone.now() > self.expire_at

    def __str__(self):
        return f"Session for {self.user} with {self.locked_tasks.count()} tasks"

    
    

from django.db import models
from django.utils import timezone
from datetime import timedelta


class WritingAnswerModel(models.Model):
    type_task = models.ForeignKey(
        WritingTypeTaskModel, on_delete=models.CASCADE, related_name="writing_answers"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="submitted_writing_answers"
    )
    task1_answer = models.TextField()
    task2_answer = models.TextField()

    # start_time = models.DateTimeField(default=timezone.now)
    # duration_time = models.IntegerField(default=60)  # minutes

    # created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    # @property
    # def expire_at(self):
    #     # dynamically calculate
    #     return self.start_time + timedelta(minutes=self.duration_time)

    # @property
    # def is_expired(self):
    #     return timezone.now() > self.expire_at

    def __str__(self):
        return f"Answer by {self.user} for {self.type_task}"


class WritingEvaluationModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    number = models.PositiveBigIntegerField(unique=True, editable=False)
    writing_answer = models.OneToOneField(
        WritingAnswerModel,
        on_delete=models.CASCADE,
        related_name="writing_evaluation",
    )

    # Task 1 fields
    task_response_task1 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    coherence_cohesion_task1 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    lexical_resource_task1 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    grammatical_range_accuracy_task1 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    overall_band_task1 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))

    # Task 2 fields
    task_response_task2 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    coherence_cohesion_task2 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    lexical_resource_task2 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    grammatical_range_accuracy_task2 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    overall_band_task2 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))

    strengths = models.JSONField(default=list, blank=True)
    areas_for_improvement = models.JSONField(default=list, blank=True)
    total_overall_band = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))

    def band_score_task1(self):
        total = (
            self.task_response_task1
            + self.coherence_cohesion_task1
            + self.lexical_resource_task1
            + self.grammatical_range_accuracy_task1
        )
        return round(total / 4, 2)

    def band_score_task2(self):
        total = (
            self.task_response_task2
            + self.coherence_cohesion_task2
            + self.lexical_resource_task2
            + self.grammatical_range_accuracy_task2
        )
        return round(total / 4, 2)

    def save(self, *args, **kwargs):
        self.overall_band_task1 = self.band_score_task1()
        self.overall_band_task2 = self.band_score_task2()

        weighted_score = (
            (self.overall_band_task1 * Decimal("0.33"))
            + (self.overall_band_task2 * Decimal("0.67"))
        )
        self.total_overall_band = round(weighted_score, 2)

        if not self.number:
            with transaction.atomic():
                last_number = (
                    WritingEvaluationModel.objects.select_for_update()
                    .aggregate(max_num=Max("number"))
                    .get("max_num") or 0
                )
                self.number = last_number + 1

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation #{self.number} ({self.total_overall_band})"
