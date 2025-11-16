from django.contrib import admin, messages
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    WritingTypeTaskModel,
      WritingAnswerModel,
        WritingEvaluationModel,
        LockExamSession,

)
admin.site.register(WritingTypeTaskModel)
admin.site.register(WritingAnswerModel)
admin.site.register(WritingEvaluationModel)
admin.site.register(LockExamSession)