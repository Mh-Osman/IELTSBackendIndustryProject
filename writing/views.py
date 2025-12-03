import random
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

        return Response({
            "session_id": session.id,
            "locked_task_ids": list(found_ids)
        }, status=status.HTTP_201_CREATED)
        


