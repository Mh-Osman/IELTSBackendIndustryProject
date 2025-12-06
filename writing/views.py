import random
from unittest import result
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import WritingTypeTask
from .serializers import WritingTypeTaskSerializer
from rest_framework.views import APIView

class WritingTypeTaskViewSet(viewsets.ModelViewSet):
 
    queryset = WritingTypeTask.objects.all().order_by("-id")
    serializer_class = WritingTypeTaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # supports file uploads

    def create(self, request, *args, **kwargs):
     
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # serializer.create will call full_clean()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # serializer.update will call full_clean()
        return Response(serializer.data)


from .models import WritingTypeTask
class GetExamSessionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request):

        type=request.data.get("exam_type")
        if type not in ["Academic","General"]:
            return Response({"error":"Invalid exam type"}, status=status.HTTP_400_BAD_REQUEST)
        t1 = WritingTypeTask.objects.filter(writing_task= "task1", writing_type=type).values_list('id', flat=True)
        t2 = WritingTypeTask.objects.filter(writing_task= "task2", writing_type=type).values_list('id', flat=True)
        task1= random.choice(t1)
        task2= random.choice(t2)
        return Response({"task1":task1,"task2":task2}, status=status.HTTP_200_OK)
    


from .models import WritingPracticeSession
from django.db import transaction
class LockSessionView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user

        if WritingPracticeSession.objects.filter(user=user, is_locked=True):
            WritingPracticeSession.objects.filter(user=user, is_locked=True).delete()

        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication required to lock a session."},
                            status=status.HTTP_401_UNAUTHORIZED)

        locked_tasks = request.data.get("locked_tasks", [])
        if not isinstance(locked_tasks, list):
            return Response({"error": "locked_tasks must be a list."},
                            status=status.HTTP_400_BAD_REQUEST)

        
        try:
            locked_ids = [int(i) for i in locked_tasks]
        except (ValueError, TypeError):
            return Response({"error": "locked_tasks must be a list of integer IDs."},
                            status=status.HTTP_400_BAD_REQUEST)

        
        tasks_qs = WritingTypeTask.objects.filter(id__in=locked_ids)
        found_ids = set(tasks_qs.values_list("id", flat=True))
        missing = set(locked_ids) - found_ids
        if missing:
            return Response({"error": "Some task IDs were not found.", "missing_ids": list(missing)},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            
            session = WritingPracticeSession.objects.create(user=user)
            session.task_list.set(tasks_qs)
            session.is_locked=True
            session.save()
            print("hello")

        return Response({
            "session_id": session.id,
            "locked_task_ids": list(found_ids)
        }, status=status.HTTP_201_CREATED)
        

from .models import WritingAnswer
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user
        task1_id = request.data.get("task1_id")
        task2_id = request.data.get("task2_id")
        answer_text1 = request.data.get("answer_text1", "")
        answer_text2 = request.data.get("answer_text2", "")
        
        last_session = WritingPracticeSession.objects.filter(user=user, is_locked=True).first()
        if not last_session:
            return Response({"error": "No locked session found for user."},
                            status=status.HTTP_400_BAD_REQUEST)
        if last_session.is_expired():
            return Response({"error": "The session has expired."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        try:
            task1 = WritingTypeTask.objects.get(id=task1_id, writing_task="task1")
            
            task2 = WritingTypeTask.objects.get(id=task2_id, writing_task="task2")
        except WritingTypeTask.DoesNotExist:
            return Response({"error": "One or both task IDs are invalid."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        if WritingAnswer.objects.filter(user=user, session=last_session).exists():
            return Response({"error": "Answers for this session have already been submitted."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        writing_answer = WritingAnswer.objects.create(
            user=user,
            session=last_session,
            task1=answer_text1,
            task2=answer_text2,
            task1_type=task1,
            task2_type=task2
        )   

        return Response({
            "message": "Answers submitted successfully.",
            "answer_id": writing_answer.id
        }, status=status.HTTP_201_CREATED)
    


        
import writing.writing_evaluation

class GetAIWritingEvaluationView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        answer_id = request.data.get("answer_id")
   
        try:
            writing_answer = WritingAnswer.objects.get(id=answer_id)
        except WritingAnswer.DoesNotExist:
            return Response({"error": "WritingAnswer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        task1_text = writing_answer.task1
       
        task1_image= writing_answer.task1_type.image
        image_path = task1_image.path
        print("Image Path:", image_path)  # Debugging line
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        result = writing.writing_evaluation.generate_ielts_feedback(
        task1_text=writing_answer.task1,#task1 answer
        task2_text=writing_answer.task2,
        question_data={
            "task1_prompt": writing_answer.task1_type.text,
            "task2_question": writing_answer.task2_type.text
        },
        task1_image_bytes=image_bytes
     )
        
        print(result)

      

        return Response({"message": "Evaluation in progress.",
                         }, status=status.HTTP_200_OK)




