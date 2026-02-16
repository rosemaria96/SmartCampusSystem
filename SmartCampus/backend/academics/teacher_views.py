from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from academics.models import (
    Subject, Student, Attendance, Timetable, 
    TeacherSubjectAssignment, Semester
)
from communication.models import Notification
from assessments.models import QuestionPaper
from datetime import datetime, date


def require_teacher(view_func):
    """Decorator to require teacher role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'TEACHER':
            messages.error(request, 'Access denied. Teacher privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_teacher
def teacher_dashboard(request):
    """Teacher dashboard"""
    # Get teacher's assigned subjects
    assignments = TeacherSubjectAssignment.objects.filter(teacher=request.user)
    
    # Get today's timetable
    today = date.today()
    day_name = today.strftime('%A').upper()
    today_classes = Timetable.objects.filter(
        teacher=request.user,
        day_of_week=day_name
    ).order_by('start_time')
    
    context = {
        'assigned_subjects': assignments,
        'today_classes': today_classes,
        'notifications': Notification.objects.filter(user=request.user)[:5],
    }
    return render(request, 'teacher/teacher_dashboard.html', context)


@login_required
@require_teacher
def teacher_timetable(request):
    """View teacher's weekly timetable"""
    timetable = Timetable.objects.filter(teacher=request.user).order_by('day_of_week', 'start_time')
    
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
    return render(request, 'teacher/teacher_timetable.html', context)


@login_required
@require_teacher
def take_attendance(request):
    """Take attendance for a class"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        semester_id = request.POST.get('semester')
        attendance_date = request.POST.get('date', date.today())
        
        # Get all students in the semester
        students = Student.objects.filter(semester_id=semester_id)
        
        # Process attendance
        for student in students:
            status = request.POST.get(f'attendance_{student.user_id}', 'ABSENT')
            
            # Create or update attendance
            Attendance.objects.update_or_create(
                student=student,
                subject_id=subject_id,
                date=attendance_date,
                defaults={
                    'status': status,
                    'marked_by': request.user
                }
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('take_attendance')
    
    # Get teacher's subjects
    teacher_subjects = TeacherSubjectAssignment.objects.filter(teacher=request.user)
    subjects = [assignment.subject for assignment in teacher_subjects]
    
    # If subject and semester selected, get students
    selected_subject_id = request.GET.get('subject')
    selected_semester_id = request.GET.get('semester')
    students = []
    
    if selected_subject_id and selected_semester_id:
        students = Student.objects.filter(semester_id=selected_semester_id)
        
        # Get existing attendance for today
        today = date.today()
        existing_attendance = {}
        for att in Attendance.objects.filter(
            subject_id=selected_subject_id,
            date=today,
            student__semester_id=selected_semester_id
        ):
            existing_attendance[att.student.user_id] = att.status
    
    context = {
        'subjects': subjects,
        'semesters': Semester.objects.all(),
        'students': students,
        'selected_subject_id': selected_subject_id,
        'selected_semester_id': selected_semester_id,
        'existing_attendance': existing_attendance if selected_subject_id and selected_semester_id else {},
    }
    return render(request, 'teacher/teacher_attendance.html', context)


@login_required
@require_teacher
def view_attendance(request):
    """View and filter attendance records"""
    # Get teacher's subjects
    teacher_subjects = TeacherSubjectAssignment.objects.filter(teacher=request.user)
    subjects = [assignment.subject for assignment in teacher_subjects]
    
    selected_subject_id = request.GET.get('subject')
    selected_semester_id = request.GET.get('semester')
    min_percentage = request.GET.get('min_percentage', 0)
    
    students_data = []
    
    if selected_subject_id and selected_semester_id:
        students = Student.objects.filter(semester_id=selected_semester_id)
        
        for student in students:
            total_classes = Attendance.objects.filter(
                student=student,
                subject_id=selected_subject_id
            ).count()
            
            present_classes = Attendance.objects.filter(
                student=student,
                subject_id=selected_subject_id,
                status='PRESENT'
            ).count()
            
            percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
            
            # Filter by minimum percentage
            if percentage >= float(min_percentage):
                students_data.append({
                    'student': student,
                    'total_classes': total_classes,
                    'present_classes': present_classes,
                    'percentage': round(percentage, 2)
                })
    
    context = {
        'subjects': subjects,
        'semesters': Semester.objects.all(),
        'students_data': students_data,
        'selected_subject_id': selected_subject_id,
        'selected_semester_id': selected_semester_id,
        'min_percentage': min_percentage,
    }
    return render(request, 'teacher/teacher_academics.html', context)


@login_required
@require_teacher
def teacher_notifications(request):
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
    return render(request, 'teacher/teacher_notifications.html', context)


@login_required
@require_teacher
def teacher_question_papers(request):
    """Upload and view question papers"""
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        exam_year = request.POST.get('exam_year')
        pdf_file = request.FILES.get('pdf_file')
        
        QuestionPaper.objects.create(
            subject_id=subject_id,
            exam_year=exam_year,
            pdf_path=pdf_file,
            uploaded_by=request.user
        )
        messages.success(request, 'Question paper uploaded successfully!')
        return redirect('teacher_question_papers')
    
    # Get teacher's subjects
    teacher_subjects = TeacherSubjectAssignment.objects.filter(teacher=request.user)
    subject_ids = [assignment.subject.id for assignment in teacher_subjects]
    
    context = {
        'question_papers': QuestionPaper.objects.filter(subject_id__in=subject_ids),
        'subjects': [assignment.subject for assignment in teacher_subjects],
    }
    return render(request, 'teacher/teacher_question_bank.html', context)
