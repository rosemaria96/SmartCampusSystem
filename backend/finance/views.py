from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def admin_fee_payment(request):
    if not request.user.is_admin:
        return redirect('login')
    return render(request, 'admin/admin_fee_payment.html')

@login_required
def student_fee_payment(request):
    if not request.user.is_student:
        return redirect('login')
    return render(request, 'student/student_fee_payment.html', {'student': request.user})
