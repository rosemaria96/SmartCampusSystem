from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path('admin/academic/', views.admin_academic, name='admin_academic'),
    path('admin/timetable/', views.admin_timetable, name='admin_timetable'),
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    # Student
    path('student/academics/', views.student_academics, name='student_academics'),
    path('student/timetable/', views.student_timetable, name='student_timetable'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    # Teacher
    path('teacher/academics/', views.teacher_academics, name='teacher_academics'),
    path('teacher/timetable/', views.teacher_timetable, name='teacher_timetable'),
    path('teacher/attendance/', views.teacher_attendance, name='teacher_attendance'),
]
