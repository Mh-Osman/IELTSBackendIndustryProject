from rest_framework.generics import CreateAPIView
from .models import WritingTypeTaskModel
from .serializers import UploadQuestionSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
import random

class UploadQuestionView(CreateAPIView):
    queryset = WritingTypeTaskModel.objects.all()
    serializer_class = UploadQuestionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)


from django.core.cache import cache 
from django.utils import timezone
from rest_framework.response import Response
from .serializers import PracticeExamSerializer


class PracticeExamView(CreateAPIView):

    def store_in_cache(self):
        task1_ids= cache.get("task1_ids")
        task2_ids = cache.get("task2_ids")


        if not  task1_ids:
            task1_ids= list(
                
                WritingTypeTaskModel.objects.filter(task="task1").values_list("id",flat=True)
            )

            cache.set("task1_ids",task1_ids,timeout=3600)
            
        if not task2_ids:
            task2_ids = list(
                
                WritingTypeTaskModel.objects.filter(task="task2").values_list("id",flat=True)
            )

            cache.set("task2_ids",task2_ids,timeout=3600)

        return task1_ids, task2_ids
    
    def get_random_questions(self):
        task1_ids, task2_ids= self.store_in_cache()
        q1_id = random.choice(task1_ids)
        q2_id= random.choice(task2_ids)

        q1= WritingTypeTaskModel.objects.get(id= q1_id)
        q2= WritingTypeTaskModel.objects.get(id= q2_id)

        return  q1 , q2

    
    def create(self, request, *args, **kwargs):
        q1, q2 = self.get_random_questions()

        data = {
            "exam": {
                "type": "writing",
                "mode": "practice",
            },
            "info": {
                "generated": timezone.now(),
                "total_task1": WritingTypeTaskModel.objects.filter(task="task1").count(),
                "total_task2": WritingTypeTaskModel.objects.filter(task="task2").count(),
            },
            "questions": {
                "task1": PracticeExamSerializer(q1).data,
                "task2": PracticeExamSerializer(q2).data,
            }
        }

        return Response(data)


            
        


