from django.urls import path
from . import teacher_views, student_views, api

urlpatterns = [
    # Teacher URLs
    path('teacher/dashboard/', teacher_views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/timetable/', teacher_views.teacher_timetable, name='teacher_timetable'),
    path('teacher/attendance/take/', teacher_views.take_attendance, name='take_attendance'),
    path('teacher/attendance/view/', teacher_views.view_attendance, name='view_attendance'),
    path('teacher/notifications/', teacher_views.teacher_notifications, name='teacher_notifications'),
    path('teacher/question-papers/', teacher_views.teacher_question_papers, name='teacher_question_papers'),
    
    # Student URLs
    path('student/dashboard/', student_views.student_dashboard, name='student_dashboard'),
    path('student/attendance/', student_views.student_attendance, name='student_attendance'),
    path('student/timetable/', student_views.student_timetable, name='student_timetable'),
    path('student/academics/', student_views.student_academics, name='student_academics'),
    path('student/notifications/', student_views.student_notifications, name='student_notifications'),
    path('student/question-bank/', student_views.student_question_bank, name='student_question_bank'),
    path('student/fees/', student_views.student_fee_payment, name='student_fee_payment'),
    
    # API endpoints
    path('api/get-semesters/', api.get_semesters, name='get_semesters'),
]
