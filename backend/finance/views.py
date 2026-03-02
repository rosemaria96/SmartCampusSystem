from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from finance.models import FeeStructure, StudentFee
from academics.models import Student


@login_required
def admin_fee_payment(request):
    if not request.user.is_staff and request.user.role != 'ADMIN':
        return redirect('login')
    return redirect('manage_fees')


@login_required
def student_fee_payment(request):
    """Show the logged-in student their fee records."""
    if request.user.role != 'STUDENT':
        return redirect('login')

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return render(request, 'student/student_fee_payment.html', {'student_fees': []})

    # Auto-create missing StudentFee records for this student
    matching_structures = FeeStructure.objects.filter(
        course=student.course,
        semester=student.semester
    )
    for fs in matching_structures:
        StudentFee.objects.get_or_create(
            student=student,
            fee_structure=fs,
            defaults={'payable_amount': fs.total_amount, 'status': 'PENDING'}
        )

    # Handle Pay Now submission
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        try:
            sf = StudentFee.objects.get(id=fee_id, student=student)
            sf.status = 'PAID'
            sf.save()
            messages.success(request, 'Payment recorded successfully!')
        except StudentFee.DoesNotExist:
            messages.error(request, 'Fee record not found.')
        return redirect('student_fee_payment')

    student_fees = StudentFee.objects.filter(student=student).select_related('fee_structure__course', 'fee_structure__semester')

    context = {
        'student': student,
        'student_fees': student_fees,
    }
    return render(request, 'student/student_fee_payment.html', context)
