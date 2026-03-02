from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    """Login view for all users"""
    if request.user.is_authenticated:
        # Redirect based on role
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'TEACHER':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'TEACHER':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login/index.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, user_id=None):
    """Profile view for all users"""
    if user_id and request.user.role == 'ADMIN':
        from django.shortcuts import get_object_or_404
        from .models import User
        user = get_object_or_404(User, pk=user_id)
    else:
        user = request.user

    context = {
        'profile_user': user
    }
    
    # Add role-specific data
    if user.role == 'STUDENT':
        try:
            student = user.student_profile
            context['student_profile'] = student
        except:
            pass
    elif user.role == 'TEACHER':
        context['assigned_subjects'] = user.subject_assignments.select_related('subject', 'subject__semester', 'subject__semester__course').all()
    
    return render(request, 'dashboard/profile.html', context)
