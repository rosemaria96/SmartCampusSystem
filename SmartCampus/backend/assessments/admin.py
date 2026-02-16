from django.contrib import admin
from .models import QuestionPaper


@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('subject', 'exam_year', 'uploaded_by', 'uploaded_at')
    list_filter = ('exam_year', 'subject__semester__course')
    search_fields = ('subject__subject_name', 'subject__subject_code')
    date_hierarchy = 'uploaded_at'
