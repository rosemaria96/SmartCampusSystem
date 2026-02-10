from django.contrib import admin
from .models import Assessment, Submission, Grade

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_instance', 'assessment_type', 'due_date', 'max_score']
    list_filter = ['assessment_type', 'class_instance__course__department', 'due_date']
    search_fields = ['title', 'class_instance__course__code']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'submitted_at']
    list_filter = ['submitted_at', 'assessment__assessment_type']
    search_fields = ['student__username', 'assessment__title']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['submission', 'score', 'graded_by', 'graded_at']
    list_filter = ['graded_at']
    search_fields = ['submission__student__username', 'submission__assessment__title']
