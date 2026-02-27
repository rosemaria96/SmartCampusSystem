from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from academics.models import Attendance, Timetable, Student, Course, Semester, Subject
from communication.models import Notification
from assessments.models import QuestionPaper
from finance.models import StudentFee, Payment, FeeStructure
from datetime import date, datetime


def require_student(view_func):
    """Decorator to require student role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'STUDENT':
            messages.error(request, 'Access denied. Student privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_student
def student_dashboard(request):
    """Student dashboard"""
    try:
        student = request.user.student_profile
        
        # Calculate overall attendance
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, status='PRESENT').count()
        attendance_rate = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        context = {
            'student': student,
            'attendance_rate': round(attendance_rate, 2),
            'total_classes': total_classes,
            'present_classes': present_classes,
            'notifications': Notification.objects.filter(
                Q(user=request.user) | Q(user__isnull=True)
            )[:5],
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found. Please contact admin.')
        context = {}
    
    return render(request, 'student/student_dashboard.html', context)


@login_required
@require_student
def student_attendance(request):
    """View attendance records"""
    try:
        student = request.user.student_profile
        
        # Get all attendance records
        attendance_records = Attendance.objects.filter(student=student).order_by('-date')
        
        # Calculate overall attendance
        total_classes = attendance_records.count()
        present_classes = attendance_records.filter(status='PRESENT').count()
        absent_classes = attendance_records.filter(status='ABSENT').count()
        attendance_rate = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get subject-wise attendance
        subjects = student.semester.subjects.all()
        subject_attendance = []
        
        for subject in subjects:
            subject_total = Attendance.objects.filter(student=student, subject=subject).count()
            subject_present = Attendance.objects.filter(student=student, subject=subject, status='PRESENT').count()
            subject_percentage = (subject_present / subject_total * 100) if subject_total > 0 else 0
            
            subject_attendance.append({
                'subject': subject,
                'total': subject_total,
                'present': subject_present,
                'percentage': round(subject_percentage, 2)
            })
        
        context = {
            'attendance_rate': round(attendance_rate, 2),
            'total_classes': total_classes,
            'present_classes': present_classes,
            'absent_classes': absent_classes,
            'attendance_records': attendance_records[:20],
            'subject_attendance': subject_attendance,
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_attendance.html', context)


@login_required
@require_student
def student_timetable(request):
    """View class timetable"""
    try:
        student = request.user.student_profile
        
        # Get timetable for student's semester
        raw_timetable = Timetable.objects.filter(semester=student.semester)
        
        # Define Slots
        # 09:00 - 10:00 (Lecture)
        # 10:00 - 10:30 (Lecture)
        # 10:30 - 11:00 (Break)
        # 11:00 - 12:00 (Lecture)
        # 12:00 - 01:00 (Lecture)
        # 01:00 - 02:00 (Lunch)
        # 02:00 - 03:00 (Lecture)
        # 03:00 - 04:00 (Lecture)
        
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        timetable_grid = []
        
        for day in days:
            day_entry = {'day': day, 'slots': []}
            
            # Helper to find class at specific time
            def get_class(time_str):
                return raw_timetable.filter(day_of_week=day, start_time=time_str).first()

            # 9-10
            day_entry['slots'].append({'type': 'class', 'entry': get_class('09:00')})
            # 10-10:30
            day_entry['slots'].append({'type': 'class', 'entry': get_class('10:00')})
            # 10:30-11 Break
            day_entry['slots'].append({'type': 'break', 'label': 'Break'})
            # 11-12
            day_entry['slots'].append({'type': 'class', 'entry': get_class('11:00')})
            # 12-1
            day_entry['slots'].append({'type': 'class', 'entry': get_class('12:00')})
            # 1-2 Lunch
            day_entry['slots'].append({'type': 'break', 'label': 'Lunch'})
            # 2-3
            day_entry['slots'].append({'type': 'class', 'entry': get_class('14:00')})
            # 3-4
            day_entry['slots'].append({'type': 'class', 'entry': get_class('15:00')})
            
            timetable_grid.append(day_entry)
        
        context = {
            'timetable_grid': timetable_grid,
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_timetable.html', context)


@login_required
@require_student
def student_academics(request):
    """View academic information"""
    try:
        student = request.user.student_profile
        
        context = {
            'student': student,
            'course': student.course,
            'semester': student.semester,
            'subjects': student.semester.subjects.all(),
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_academics.html', context)


@login_required
@require_student
def student_notifications(request):
    """View notifications"""
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')
    
    # Mark as read
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'student/student_notifications.html', context)


@login_required
@require_student
def student_question_bank(request):
    """View and download question papers"""
    try:
        student = request.user.student_profile
        
        # Filter parameters
        course_id = request.GET.get('course')
        semester_id = request.GET.get('semester')
        subject_id = request.GET.get('subject')
        
        papers = QuestionPaper.objects.all().order_by('-exam_year')
        
        if course_id:
            papers = papers.filter(subject__semester__course_id=course_id)
        if semester_id:
            papers = papers.filter(subject__semester_id=semester_id)
        if subject_id:
            papers = papers.filter(subject_id=subject_id)
            
        context = {
            'question_papers': papers,
            'courses': Course.objects.all(),
            'semesters': Semester.objects.all(),
            'subjects': Subject.objects.all(),
            'selected_course': int(course_id) if course_id else None,
            'selected_semester': int(semester_id) if semester_id else None,
            'selected_subject': int(subject_id) if subject_id else None,
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_question_bank.html', context)


@login_required
@require_student
def student_fee_payment(request):
    """View fee structure and payment history"""
    # Get the logged-in student
    student = Student.objects.get(user=request.user)
    
    # Handle Payment
    if request.method == 'POST':
        fee_id = request.POST.get('fee_id')
        student_fee = get_object_or_404(StudentFee, id=fee_id, student=student)
        
        if student_fee.status != 'PAID':
            # Create Payment Record
            Payment.objects.create(
                student_fee=student_fee,
                amount_paid=student_fee.payable_amount,
                payment_method='Online Transfer',
                transaction_reference=f"TXN-{int(datetime.now().timestamp())}",
            )
            
            # Update Fee Status
            student_fee.status = 'PAID'
            student_fee.save()
            
            messages.success(request, f'Payment of ₹{student_fee.payable_amount} successful!')
        return redirect('student_fee_payment')
    
    # Get fee structures and student fees - EXACT SAME AS ADMIN
    fee_structures = FeeStructure.objects.all()
    # Get ALL student's fee records
    student_fees = StudentFee.objects.filter(student=student).select_related('fee_structure', 'fee_structure__course', 'fee_structure__semester')
    
    context = {
        'fee_structures': fee_structures,
        'student_fees': student_fees,
    }
    
    return render(request, 'student/student_fee_payment.html', context)
