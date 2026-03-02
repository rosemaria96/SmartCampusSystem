from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def admin_qn_bank(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_qn_bank.html')

@login_required
def student_question_bank(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_question_bank.html', {'student': request.user})

@login_required
def teacher_question_bank(request):
    if not request.user.is_teacher:
        return redirect('login')
    return render(request, 'teacher/teacher_question_bank.html', {'teacher': request.user})
