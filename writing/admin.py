from django.contrib import admin

# Register your models here.
from .models import WritingTypeTaskModel,WritingAnswerModel,WritingEvaluationModel
admin.site.register(WritingTypeTaskModel)
admin.site.register(WritingAnswerModel)
admin.site.register(WritingEvaluationModel)