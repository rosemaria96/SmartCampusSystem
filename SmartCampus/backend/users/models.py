from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model with role-based access control"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    
    name = models.CharField(max_length=100, blank=True, default='')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, default='STUDENT')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_teacher(self):
        return self.role == 'TEACHER'
    
    @property
    def is_student(self):
        return self.role == 'STUDENT'
