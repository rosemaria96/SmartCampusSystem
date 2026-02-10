from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def admin_noti(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_noti.html')

@login_required
def student_notifications(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_notifications.html', {'student': request.user})

@login_required
def teacher_notifications(request):
    if not request.user.is_teacher:
        return redirect('login')
    return render(request, 'teacher/teacher_notifications.html', {'teacher': request.user})
