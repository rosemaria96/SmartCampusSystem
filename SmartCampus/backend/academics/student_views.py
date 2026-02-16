from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from academics.models import Attendance, Timetable, Student
from communication.models import Notification
from assessments.models import QuestionPaper
from finance.models import StudentFee, Payment
from datetime import date


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
        timetable = Timetable.objects.filter(semester=student.semester).order_by('day_of_week', 'start_time')
        
        # Organize by day
        days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        timetable_list = []
        for day in days:
            classes = timetable.filter(day_of_week=day)
            timetable_list.append({
                'day': day,
                'classes': classes
            })
        
        context = {
            'timetable_list': timetable_list,
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
        
        # Get question papers for student's subjects
        subject_ids = student.semester.subjects.values_list('id', flat=True)
        question_papers = QuestionPaper.objects.filter(subject_id__in=subject_ids).order_by('-exam_year')
        
        context = {
            'question_papers': question_papers,
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_question_bank.html', context)


@login_required
@require_student
def student_fee_payment(request):
    """View fee structure and payment history"""
    try:
        student = request.user.student_profile
        
        # Get student's fee records
        student_fees = StudentFee.objects.filter(student=student)
        
        context = {
            'student_fees': student_fees,
        }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {}
    
    return render(request, 'student/student_fee_payment.html', context)
