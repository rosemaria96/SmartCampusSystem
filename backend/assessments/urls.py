from django.urls import path
from . import views

urlpatterns = [
    path('admin/question-bank/', views.admin_qn_bank, name='admin_qn_bank'),
    path('student/question-bank/', views.student_question_bank, name='student_question_bank'),
    path('teacher/question-bank/', views.teacher_question_bank, name='teacher_question_bank'),
]
