from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import WritingTypeTaskModel, WritingAnswerModel, WritingEvaluationModel


# --- Inline for Writing Answers inside Type Task ---
class WritingAnswerInline(TabularInline):
    model = WritingAnswerModel
    extra = 0
    readonly_fields = ("user", "submitted_at")
    show_change_link = True


# --- Writing Task Model Admin ---
@admin.register(WritingTypeTaskModel)
class WritingTypeTaskAdmin(ModelAdmin):
    icon = "book-open"
    list_display = ("number", "exam_type", "task", "has_image", "question_preview")
    list_filter = ("exam_type", "task")
    search_fields = ("question",)
    inlines = [WritingAnswerInline]
    ordering = ("number",)

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "Has Image"

    def question_preview(self, obj):
        return (obj.question[:80] + "...") if len(obj.question) > 80 else obj.question
    question_preview.short_description = "Question Preview"


# --- Inline for Evaluation inside Writing Answer ---
class WritingEvaluationInline(TabularInline):
    model = WritingEvaluationModel
    extra = 0
    readonly_fields = ("total_overall_band",)
    show_change_link = True


# --- Writing Answer Admin ---
@admin.register(WritingAnswerModel)
class WritingAnswerAdmin(ModelAdmin):
    icon = "file-text"
    list_display = ("user", "type_task", "submitted_at", "short_answer_preview")
    list_filter = ("submitted_at",)
    search_fields = ("user__username", "type_task__exam_type")
    inlines = [WritingEvaluationInline]
    ordering = ("-submitted_at",)

    def short_answer_preview(self, obj):
        return (obj.task1_answer[:70] + "...") if len(obj.task1_answer) > 70 else obj.task1_answer
    short_answer_preview.short_description = "Answer Preview"


# --- Writing Evaluation Admin ---
@admin.register(WritingEvaluationModel)
class WritingEvaluationAdmin(ModelAdmin):
    icon = "award"
    list_display = (
        "number",
        "writing_answer",
        "overall_band_task1",
        "overall_band_task2",
        "total_overall_band",
    )
    list_filter = ("total_overall_band",)
    search_fields = ("writing_answer__user__username",)
    readonly_fields = (
        "overall_band_task1",
        "overall_band_task2",
        "total_overall_band",
    )
    ordering = ("-number",)
