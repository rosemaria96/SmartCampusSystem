from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Admin
@login_required
def admin_academic(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_academic.html')

@login_required
def admin_timetable(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_timetable.html')

@login_required
def admin_attendance(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_attendance.html')

# Student
@login_required
def student_academics(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_academics.html', {'student': request.user})

@login_required
def student_timetable(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_timetable.html', {'student': request.user})

@login_required
def student_attendance(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_attendance.html', {'student': request.user})

# Teacher
@login_required
def teacher_academics(request):
    if not request.user.is_teacher:
        return redirect('login')
    return render(request, 'teacher/teacher_academics.html', {'teacher': request.user})

@login_required
def teacher_timetable(request):
    if not request.user.is_teacher:
        return redirect('login')
    return render(request, 'teacher/teacher_timetable.html', {'teacher': request.user})

@login_required
def teacher_attendance(request):
    if not request.user.is_teacher:
        return redirect('login')
    return render(request, 'teacher/teacher_attendance.html', {'teacher': request.user})
