from django.db import models
from django.conf import settings
from academics.models import Subject


class QuestionPaper(models.Model):
    """Question paper repository"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='question_papers')
    exam_year = models.IntegerField()
    pdf_path = models.FileField(upload_to='question_papers/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_papers'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.subject_code} - {self.exam_year}"
    
    class Meta:
        db_table = 'question_papers'
        ordering = ['-exam_year', 'subject__subject_code']
