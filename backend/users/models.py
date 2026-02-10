from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    # Department will be linked later to avoid circular imports if possible, or added now if we define Department here.
    # For now, simplistic fields.
    current_year = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"
