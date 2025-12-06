from django.contrib import admin

from .models import ReadingExamModel, ReadingPassageModel
admin.site.register(ReadingExamModel)
admin.site.register(ReadingPassageModel)