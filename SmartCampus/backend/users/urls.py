from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='index'),
    path('logout/', views.logout_view, name='logout'),
    
    # General Dashboard (public/landing)
    path('dashboard/', views.dashboard, name='home'),
    path('dashboard/academics/', views.dashboard_academics, name='dashboard_academics'),
    path('dashboard/about-us/', views.dashboard_about_us, name='about_us'),
    path('dashboard/help/', views.dashboard_help, name='help'),
    
    # Student Dashboard (main dashboard only, other routes in respective apps)
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Teacher Dashboard
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    # Admin Dashboard and User Management
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/user-management/', views.admin_user_management, name='admin_user_management'),
]


