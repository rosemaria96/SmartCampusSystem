from django.db import models
from django.conf import settings


class Department(models.Model):
    """Academic departments"""
    department_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.department_name
    
    class Meta:
        db_table = 'departments'


class Course(models.Model):
    """Courses offered by departments"""
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=100)
    duration_years = models.IntegerField()
    
    def __str__(self):
        return f"{self.course_name} ({self.department.department_name})"
    
    class Meta:
        db_table = 'courses'


class Semester(models.Model):
    """Semesters within courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.IntegerField()
    
    def __str__(self):
        return f"{self.course.course_name} - Semester {self.semester_number}"
    
    class Meta:
        db_table = 'semesters'
        unique_together = ('course', 'semester_number')


class Subject(models.Model):
    """Subjects taught in semesters"""
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    credits = models.IntegerField()
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
    class Meta:
        db_table = 'subjects'


class TeacherSubjectAssignment(models.Model):
    """Assignment of teachers to subjects"""
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'},
        related_name='subject_assignments'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    
    def __str__(self):
        return f"{self.teacher.name} - {self.subject.subject_name}"
    
    class Meta:
        db_table = 'teacher_subject_assignment'
        unique_together = ('teacher', 'subject')


class Student(models.Model):
    """Student profile linked to User"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        limit_choices_to={'role': 'STUDENT'},
        related_name='student_profile'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='students')
    enrollment_number = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.enrollment_number}"
    
    class Meta:
        db_table = 'students'


class Attendance(models.Model):
    """Student attendance records"""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'},
        related_name='marked_attendances'
    )
    
    timetable_slot = models.ForeignKey(
        'Timetable', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='attendance_records'
    )

    def __str__(self):
        return f"{self.student.user.name} - {self.subject.subject_code} - {self.date}"
    
    class Meta:
        db_table = 'attendance'
        unique_together = ('student', 'subject', 'date', 'timetable_slot')


class Timetable(models.Model):
    """Class timetable"""
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'},
        related_name='timetable_entries'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetable_entries')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"{self.subject.subject_code} - {self.day_of_week} {self.start_time}"
    
    class Meta:
        db_table = 'timetable'


class Exam(models.Model):
    """Exam schedule"""
    EXAM_TYPE_CHOICES = [
        ('MID_TERM', 'Mid Term'),
        ('END_TERM', 'End Term'),
        ('QUIZ', 'Quiz'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.IntegerField()
    
    def __str__(self):
        return f"{self.subject.subject_code} - {self.get_exam_type_display()}"
    
    class Meta:
        db_table = 'exams'


class Result(models.Model):
    """Student exam results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    
    def __str__(self):
        return f"{self.student.user.name} - {self.exam.subject.subject_code} - {self.grade}"
    
    class Meta:
        db_table = 'results'
        unique_together = ('student', 'exam')
