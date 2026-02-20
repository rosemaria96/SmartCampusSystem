from django.urls import path
from . import views

urlpatterns = [
    path('admin/notifications/', views.admin_noti, name='admin_noti'),
    path('student/notifications/', views.student_notifications, name='student_notifications'),
    path('teacher/notifications/', views.teacher_notifications, name='teacher_notifications'),
    path('api/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
]
