from django.db import models
from django.core.exceptions import ValidationError
from cloudinary_storage.storage import MediaCloudinaryStorage

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
        storage=MediaCloudinaryStorage(),
        upload_to="writing_images/",
        null=True,
        blank=True,
        max_length=255,
        help_text="Required for Task 1 (upload an image)."
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
    
    
