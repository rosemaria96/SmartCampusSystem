from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, TeacherProfile
from academics.models import Enrollment, Class, Course, Department
from assessments.models import Assessment, Submission
from django.utils import timezone

def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role') # 'student', 'faculty', 'admin'
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if role == 'student' and user.is_student:
                return redirect('student_dashboard')
            elif role == 'faculty' and user.is_teacher:
                return redirect('teacher_dashboard')
            elif role == 'admin' and user.is_admin:
                return redirect('admin_dashboard')
            else:
                # Redirect based on flags if role mismatched
                if user.is_student: return redirect('student_dashboard')
                if user.is_teacher: return redirect('teacher_dashboard')
                if user.is_admin: return redirect('admin_dashboard')
        else:
            error_message = 'Invalid credentials'

    return render(request, 'login/index.html', {'error': error_message})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('login') # Or forbidden page

    try:
        enrollments = Enrollment.objects.filter(student=request.user)
        active_courses_count = enrollments.count()
        
        # Calculate attendance (Mock logic or simple calculation if Attendance model existed)
        attendance_rate = 94.5 
        
        # Pending Tasks
        current_classes = [e.enrolled_class for e in enrollments]
        pending_assessments = Assessment.objects.filter(
            class_instance__in=current_classes,
            due_date__gte=timezone.now()
        ).exclude(submissions__student=request.user)[:5]
        
        pending_count = pending_assessments.count()
        
        context = {
            'student': request.user,
            'attendance_rate': attendance_rate,
            'active_courses_count': active_courses_count,
            'pending_count': pending_count,
            'gpa': 3.8, 
            'pending_assessments': pending_assessments,
        }
        return render(request, 'student/student_dashboard.html', context)
    except Exception as e:
        # Fallback if something breaks (e.g. models not migrated)
        print(f"Error in dashboard: {e}")
        return render(request, 'student/student_dashboard.html', {'error': str(e)})

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('login')
        
    classes_taught = Class.objects.filter(teacher=request.user)
    total_students = Enrollment.objects.filter(enrolled_class__in=classes_taught).values('student').distinct().count()
    
    context = {
        'teacher': request.user,
        'total_classes': classes_taught.count(),
        'total_students_taught': total_students,
        'classes': classes_taught[:5], # Show recent classes
    }
    return render(request, 'teacher/teacher_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('login')
    
    context = {
        'total_students': User.objects.filter(is_student=True).count(),
        'total_teachers': User.objects.filter(is_teacher=True).count(),
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
    }
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
def admin_user_management(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_user_management.html')

# General/Public Dashboard Views
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

def dashboard_academics(request):
    return render(request, 'dashboard/dashboard_academics.html')

def dashboard_about_us(request):
    return render(request, 'dashboard/dash_about_us.html')

def dashboard_help(request):
    return render(request, 'dashboard/dash_help.html')
