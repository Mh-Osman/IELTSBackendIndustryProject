from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    
    
    WritingTypeTaskViewSet,
    GetExamSessionView,
    LockSessionView,
    SubmitAnswerView,
    GetAIWritingEvaluationView,
)
router = DefaultRouter()
router.register("writing-tasks", WritingTypeTaskViewSet, basename="writingtask")

urlpatterns = [
    path("", include(router.urls)),
    path("get/exam/session/", GetExamSessionView.as_view()),
    path("lock/practice/",LockSessionView.as_view()),
    path("submit/answer/",SubmitAnswerView.as_view()),
    path("get/ai/evaluation/",GetAIWritingEvaluationView.as_view()),


]

