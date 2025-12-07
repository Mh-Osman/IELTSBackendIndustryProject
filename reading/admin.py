from django.contrib import admin
import nested_admin
from .models import(
     ReadingExamModel,
       ReadingPassageModel,
       ReadingPassage,
       PassagePart,
       ReadingMcq,
       ReadingMcqOption,
       ReadingQuestionRange,
       TFNGQuestion

)

class TFNGQuestionInline(nested_admin.NestedTabularInline):
    model = TFNGQuestion
    extra = 1

class ReadingMcqOptionInline(nested_admin.NestedTabularInline):
    model = ReadingMcqOption
    extra = 1
class ReadingMcqInline(nested_admin.NestedTabularInline):
    model = ReadingMcq
    extra = 1
    inlines = [ReadingMcqOptionInline]

class ReadingQuestionRangeInline(nested_admin.NestedTabularInline):
    model = ReadingQuestionRange
    extra = 1
    inlines = [ReadingMcqInline, TFNGQuestionInline]

class PassagePartInline(nested_admin.NestedTabularInline):
    model = PassagePart
    extra = 1

class ReadingPassageAdmin(nested_admin.NestedTabularInline):
    model = ReadingPassage
    extra = 1
    inlines = [PassagePartInline]

class ReadingExamAdmin(nested_admin.NestedModelAdmin):
    inlines = [ReadingPassageAdmin, ReadingQuestionRangeInline]

admin.site.register(ReadingExamModel, ReadingExamAdmin)
