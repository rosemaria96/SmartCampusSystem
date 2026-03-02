from django.contrib import admin
from .models import (
    Department, Course, Semester, Subject, TeacherSubjectAssignment,
    Student, Attendance, Timetable, Exam, Result
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'department_name')
    search_fields = ('department_name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'department', 'duration_years')
    list_filter = ('department',)
    search_fields = ('course_name',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'semester_number')
    list_filter = ('course',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_code', 'subject_name', 'semester', 'credits')
    list_filter = ('semester__course',)
    search_fields = ('subject_code', 'subject_name')


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'subject')
    list_filter = ('subject__semester__course',)
    search_fields = ('teacher__name', 'subject__subject_name')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_number', 'course', 'semester')
    list_filter = ('course', 'semester')
    search_fields = ('user__name', 'enrollment_number')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'marked_by')
    list_filter = ('status', 'date', 'subject')
    search_fields = ('student__user__name', 'subject__subject_name')
    date_hierarchy = 'date'


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'semester', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'semester')
    search_fields = ('subject__subject_name', 'teacher__name')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'exam_type', 'exam_date', 'start_time', 'total_marks')
    list_filter = ('exam_type', 'exam_date')
    search_fields = ('subject__subject_name',)
    date_hierarchy = 'exam_date'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam__exam_type', 'grade')
    search_fields = ('student__user__name', 'exam__subject__subject_name')
