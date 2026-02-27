from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('', views.login_view, name='home'),
    path('index/', views.login_view, name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='user_profile'),
    
    # Admin URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.user_management, name='user_management'),
    path('admin/users/create/', admin_views.create_user, name='create_user'),
    path('admin/academics/', admin_views.manage_academics, name='manage_academics'),
    
    # Academic Management - Custom Forms
    path('admin/academics/department/add/', admin_views.add_department, name='add_department'),
    path('admin/academics/department/edit/<int:pk>/', admin_views.edit_department, name='edit_department'),
    path('admin/academics/department/delete/<int:pk>/', admin_views.delete_department, name='delete_department'),
    
    path('admin/academics/course/add/', admin_views.add_course, name='add_course'),
    path('admin/academics/course/edit/<int:pk>/', admin_views.edit_course, name='edit_course'),
    path('admin/academics/course/delete/<int:pk>/', admin_views.delete_course, name='delete_course'),
    
    path('admin/academics/subject/add/', admin_views.add_subject, name='add_subject'),
    path('admin/academics/subject/edit/<int:pk>/', admin_views.edit_subject, name='edit_subject'),
    path('admin/academics/subject/delete/<int:pk>/', admin_views.delete_subject, name='delete_subject'),
    path('admin/academics/subject/add/', admin_views.add_subject, name='add_subject'),
    path('admin/academics/subject/edit/<int:pk>/', admin_views.edit_subject, name='edit_subject'),
    path('admin/academics/subject/delete/<int:pk>/', admin_views.delete_subject, name='delete_subject'),
    
    # Timetable Management - Custom Forms
    path('admin/timetable/', admin_views.manage_timetable, name='manage_timetable'),
    path('admin/timetable/create-grid/', admin_views.create_timetable_grid, name='create_timetable_grid'),
    path('admin/timetable/add/', admin_views.add_timetable, name='add_timetable'),
    path('admin/timetable/edit/<int:pk>/', admin_views.edit_timetable, name='edit_timetable'),
    path('admin/timetable/delete/<int:pk>/', admin_views.delete_timetable, name='delete_timetable'),
    
    # Fee Management - Custom Forms
    path('admin/fees/structure/add/', admin_views.add_fee_structure, name='add_fee_structure'),
    path('admin/fees/structure/edit/<int:pk>/', admin_views.edit_fee_structure, name='edit_fee_structure'),
    path('admin/fees/structure/delete/<int:pk>/', admin_views.delete_fee_structure, name='delete_fee_structure'),
    path('admin/fees/student/edit/<int:pk>/', admin_views.edit_student_fee, name='edit_student_fee'),
    
    path('admin/attendance/', admin_views.attendance_reports, name='attendance_reports'),
    path('admin/notifications/', admin_views.admin_notifications, name='admin_notifications'),
    path('admin/notifications/post/', admin_views.post_notification, name='post_notification'),
    path('admin/question-papers/', admin_views.manage_question_papers, name='manage_question_papers'),
    path('admin/fees/', admin_views.manage_fees, name='manage_fees'),
    
    # Fallback/Legacy URLs
    path('dashboard/academics/', views.login_view, name='dashboard_academics'),
    path('dashboard/about-us/', views.login_view, name='about_us'),
    path('dashboard/help/', views.login_view, name='help'),
]
