from django.contrib import admin
from .models import (
    WritingTypeTask,
    WritingPracticeSession,
    WritingAnswer,
    WritingEvaluation,

)
admin.site.register(WritingTypeTask)
admin.site.register(WritingPracticeSession)
admin.site.register(WritingAnswer)
admin.site.register(WritingEvaluation)
