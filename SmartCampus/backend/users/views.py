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
def profile_view(request):
    """Profile view for all users"""
    context = {
        'user': request.user
    }
    
    # Add role-specific data
    if request.user.role == 'STUDENT':
        try:
            student = request.user.student_profile
            context['student'] = student
        except:
            pass
    
    return render(request, 'dashboard/profile.html', context)
