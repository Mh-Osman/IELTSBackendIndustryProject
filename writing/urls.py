from django.urls import path, include
from rest_framework.routers import DefaultRouter 
from .views import (
    UploadQuestionView,
    PracticeExamView,

)


urlpatterns =[

      path("upload-question/",UploadQuestionView.as_view()),
      path("practice-exam/",PracticeExamView.as_view()),
      

]