from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import (
    UploadQuestionView,
    PracticeExameView,
    LockPracticeExamView,

)


urlpatterns =[

    path("upload-question/",UploadQuestionView.as_view()),
    path("practice/exam/",PracticeExameView.as_view()),
    path("lock/practice/",LockPracticeExamView.as_view()),
      

]