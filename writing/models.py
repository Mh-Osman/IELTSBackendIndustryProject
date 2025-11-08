from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal
from users.models import CustomUser
from cloudinary_storage.storage import MediaCloudinaryStorage
import uuid

class WritingTypeTaskModel(models.Model):
    Type=[

        ("Academic","Academic"),
        ("General","General"),
    ]

    Task=[

        ("task1","Task 1"),#task 1 is imagefield
        ("task2","Task 2"),#task 2 is text field 
    ]

    uid =models.UUIDField(

        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    number=models.PositiveBigIntegerField(unique=True,editable=False)
    question=models.TextField()
    image = models.ImageField(

        storage= MediaCloudinaryStorage(),
        upload_to="writing_exam_images/",
        blank=True,
        null=True,
    )
    task=models.CharField(max_length=30,choices=Task)
    exam_type = models.CharField(max_length=30,choices=Type)


    def clean(self):
        if self.task=="task1" and not self.image:
            raise ValidationError("Image is required for Task 1 question.")
        if self.task =="task2" and self.image:
            raise ValidationError("NOt allow the image for Task 2")
    

    def save(self,*args,**kwargs):
        if not self.number:
            last= WritingTypeTaskModel.objects.order_by('-number').first()

            self.number=1 if not last else last.number + 1
        
        self.full_clean()
        super().save( *args, **kwargs)

    def __str__(self):
        return f"{self.exam_type} - {self.task} - {self.number}"

class WritingAnswerModel(models.Model):
    type_task = models.ForeignKey(WritingTypeTaskModel,on_delete=models.CASCADE, related_name="writing_answers")
    user =models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="submitted_writing_answers"
        
    )
    task1_answer = models.TextField()
    task2_answer= models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class WritingEvaluationModel(models.Model):

    uid = models.UUIDField(
        primary_key = True,
        default=uuid.uuid4,
        editable=False
    )

    number=models.PositiveBigIntegerField(unique=True,editable=False)
    writing_answer = models.OneToOneField(
        WritingAnswerModel,
        on_delete=models.CASCADE,
        related_name="writing_evaluation"
    )
    #task 1
    task_response_task1= models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )

    coherence_cohesion_task1=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    lexical_resource_taks1= models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    grammatical_range_accuracy_taks1=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    overall_band_task1=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    #task 2
    task_response_task2= models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )

    coherence_cohesion_task2=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    lexical_resource_taks2= models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    grammatical_range_accuracy_taks2=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )
    overall_band_task2=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )

    strengths = models.JSONField(default=list,blank=True)
    areas_for_improvement=models.JSONField(default=list,blank=True)
    
    def band_score_task1(self):
        total = (
            self.task_response_task1 +
            self.coherence_cohesion_task1 +
            self.lexical_resource_taks1 +
            self.grammatical_range_accuracy_taks1
        )
        return round(total / 4, 2)
    

    def band_score_task2(self):
        total = (
            self.task_response_task2 +
            self.coherence_cohesion_task2 +
            self.lexical_resource_taks2 +
            self.grammatical_range_accuracy_taks2
        )
        return round(total / 4, 2)

    total_overall_band=models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        default=Decimal("0.00")

    )

    def save(self,*args,**kwargs):
        self.overall_band_task1=self.band_score_task1()
        self.overall_band_task2=self.band_score_task2()
        weighted_score=(
            (self.overall_band_task1 * Decimal("0.33"))+
            (self.overall_band_task2 * Decimal("0.67"))
        )

        self.total_overall_band= round(weighted_score, 2)

        last = WritingEvaluationModel.objects.order_by('-number').first()
        if not self.number:
            self.number=1 if not last else last.number + 1
        super().save( *args, **kwargs)




    




