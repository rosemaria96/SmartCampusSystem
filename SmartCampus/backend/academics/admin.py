from django.contrib import admin
from .models import Department, Course, Class, Enrollment, Attendance

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_of_department']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'credits']
    list_filter = ['department']
    search_fields = ['code', 'name']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher', 'section', 'room_number']
    list_filter = ['course__department', 'teacher']
    search_fields = ['course__name', 'course__code']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'enrolled_class', 'date_enrolled', 'grade']
    list_filter = ['enrolled_class__course__department', 'enrolled_class']
    search_fields = ['student__username', 'enrolled_class__course__name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'enrolled_class', 'date', 'status']
    list_filter = ['status', 'date', 'enrolled_class']
    search_fields = ['student__username', 'enrolled_class__course__name']
