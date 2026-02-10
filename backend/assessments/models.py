from django.db import models
from django.conf import settings
from academics.models import Class

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
    )

    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='assignment')
    due_date = models.DateTimeField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.title} ({self.class_instance})"

class Submission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'is_student': True},
        related_name='submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    content = models.TextField(blank=True, help_text="Text content if no file is uploaded")

    class Meta:
        unique_together = ('assessment', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title}"

class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='grade')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'is_teacher': True}
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission} - {self.score}"
