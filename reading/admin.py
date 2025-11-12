from django.contrib import admin
from .models import (
    ReadingExamModel,
    ReadingPassageModel,
    ReadingQuestionModel,
    ReadingOptionModel,
    ReadingAnswerModel,
    ReadingEvaluationModel
)


# -----------------------------
# 1️⃣ Inline Classes
# -----------------------------

class ReadingOptionInline(admin.TabularInline):
    model = ReadingOptionModel
    extra = 2
    min_num = 1
    max_num = 6
    fields = ['text', 'is_correct']
    show_change_link = True


class ReadingQuestionInline(admin.TabularInline):
    model = ReadingQuestionModel
    extra = 1
    show_change_link = True
    fields = ['question_text', 'question_type', 'order']


class ReadingPassageInline(admin.TabularInline):
    model = ReadingPassageModel
    extra = 1
    show_change_link = True
    fields = ['title', 'order']


# -----------------------------
# 2️⃣ ReadingExam Admin
# -----------------------------
@admin.register(ReadingExamModel)
class ReadingExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'total_passages', 'duration_minutes', 'created_at')
    list_filter = ('exam_type', 'created_at')
    search_fields = ('title',)
    inlines = [ReadingPassageInline]

    fieldsets = (
        ('Exam Information', {
            'fields': ('title', 'description', 'exam_type')
        }),
        ('Configuration', {
            'fields': ('total_passages', 'duration_minutes')
        }),
    )


# -----------------------------
# 3️⃣ ReadingPassage Admin
# -----------------------------
@admin.register(ReadingPassageModel)
class ReadingPassageAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam', 'order', 'created_at')
    list_filter = ('exam',)
    search_fields = ('title', 'content')
    ordering = ['exam', 'order']
    inlines = [ReadingQuestionInline]

    fieldsets = (
        ('Passage Details', {
            'fields': ('exam', 'title', 'content', 'order')
        }),
    )


# -----------------------------
# 4️⃣ ReadingQuestion Admin
# -----------------------------
@admin.register(ReadingQuestionModel)
class ReadingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'passage', 'question_type', 'order', 'marks')
    list_filter = ('question_type', 'passage')
    search_fields = ('question_text',)
    ordering = ['passage', 'order']
    inlines = [ReadingOptionInline]

    fieldsets = (
        ('Question Details', {
            'fields': ('passage', 'question_type', 'question_text', 'order', 'marks')
        }),
    )


# -----------------------------
# 5️⃣ ReadingOption Admin
# -----------------------------
@admin.register(ReadingOptionModel)
class ReadingOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)
    ordering = ['question']


# -----------------------------
# 6️⃣ ReadingAnswer Admin
# -----------------------------
@admin.register(ReadingAnswerModel)
class ReadingAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'passage', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'exam', 'answered_at')
    search_fields = ('user__username', 'question__question_text')
    readonly_fields = ('answered_at',)
    date_hierarchy = 'answered_at'


# -----------------------------
# 7️⃣ ReadingEvaluation Admin
# -----------------------------
@admin.register(ReadingEvaluationModel)
class ReadingEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam', 'correct_answers', 'total_questions', 'band_score', 'evaluated_at')
    list_filter = ('exam',)
    search_fields = ('user__username',)
    readonly_fields = ('evaluated_at',)

    fieldsets = (
        ('User Result', {
            'fields': ('user', 'exam', 'total_questions', 'correct_answers', 'band_score')
        }),
    )
