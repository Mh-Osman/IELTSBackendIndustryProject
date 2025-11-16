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
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from .serializers import PracticeExamSerializer


class FivePerMinuteThrottle(UserRateThrottle):
    rate = '10/minute'


class PracticeExameView(APIView):
    throttle_classes = [FivePerMinuteThrottle]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam_type = request.data.get("exam_type")  # FIXED
        locks = LockExamSession.objects.filter(user=request.user)

        try:
            for l in locks:
                if l.is_locked:
                    return Response({


                        "message": "you cant do any other writing exam because u have active exam ",
                    
                    })
        except LockExamSession.DoesNotExist:
            return None

     
        # Load from cache
        t1 = cache.get("task1_ids")
        t2 = cache.get("task2_ids")

        # If not in cache → load & set
        if not t1 or not t2:
            t1 = list(
                WritingTypeTaskModel.objects
                .filter(task="task1", exam_type=exam_type)
                .values_list("id", flat=True)  # FIXED
            )

            t2 = list(
                WritingTypeTaskModel.objects
                .filter(task="task2", exam_type=exam_type)
                .values_list("id", flat=True)  # FIXED
            )

            cache.set("task1_ids", t1, 500)
            cache.set("task2_ids", t2, 500)

        # Pick random IDs
        try:

            random_id1 = random.choice(t1)
            random_id2 = random.choice(t2)
        except IndexError:
            return Response({

                "msg": "invalid",
            })
        

        task1 = WritingTypeTaskModel.objects.filter(id=random_id1).first()
        task2 = WritingTypeTaskModel.objects.filter(id=random_id2).first()

        return Response({
            "message": "success",
            "task1_id": random_id1,
            "task2_id": random_id2,
            "task1_question": PracticeExamSerializer(task1).data,
            "task2_question": PracticeExamSerializer(task2).data,
        })

from rest_framework.views import APIView
from rest_framework import status

from .models import LockExamSession

class LockPracticeExamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        task_ids = request.data.get("locked_tasks")

        if not task_ids or not isinstance(task_ids, list):
            return Response({
                "lock": False,
                "message": "locked_tasks field must be a list ex: [1,2]"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch tasks
        tasks = WritingTypeTaskModel.objects.filter(id__in=task_ids)

        if tasks.count() != len(task_ids):
            return Response({
                "lock": False,
                "message": "One or more tasks are invalid"
            })
        
        # Create one session
        session = LockExamSession.objects.create(
            user=user,
            is_locked=True
        )

        # Assign tasks
        session.locked_tasks.set(tasks)

        return Response({
            "locked": True,
            "duration": session.duration_time,
            "expire_at": session.expire_at,
            "tasks": list(tasks.values("id", "task"))
        })

