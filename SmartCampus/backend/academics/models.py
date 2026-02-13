from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'is_teacher': True},
        related_name='headed_departments'
    )

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.IntegerField(default=3)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'is_teacher': True},
        related_name='classes_taught'
    )
    section = models.CharField(max_length=10, blank=True) # e.g. "Section A"
    room_number = models.CharField(max_length=20, blank=True)
    schedule_info = models.CharField(max_length=255, blank=True) # Simple text for now, e.g. "Mon 10am"

    def __str__(self):
        return f"{self.course.code} ({self.section})"

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_student': True},
        related_name='enrollments'
    )
    enrolled_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    date_enrolled = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=5, blank=True, null=True) # Final Grade

    class Meta:
        unique_together = ('student', 'enrolled_class')

    def __str__(self):
        return f"{self.student.username} in {self.enrolled_class}"

class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_student': True},
        related_name='attendance_records'
    )
    enrolled_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='present')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'enrolled_class', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.enrolled_class} ({self.date}): {self.status}"
