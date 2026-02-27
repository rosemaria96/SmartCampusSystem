from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from academics.models import (
    Subject, Student, 
    TeacherSubjectAssignment, Semester, Course
)
from .models import Attendance, Timetable
# Trigger reload, 
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
    raw_timetable = Timetable.objects.filter(teacher=request.user)
    
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    timetable_grid = []
    
    for day in days:
        day_entry = {'day': day, 'slots': []}
        
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
    return render(request, 'teacher/teacher_timetable.html', context)


@login_required
@require_teacher
def take_attendance(request):
    """Take attendance for a class (Weekly Grid View)"""
    from datetime import timedelta
    
    # Calculate start of current week (Monday)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=5) # Saturday
    
    # Mapping for date calculation
    week_dates = {
        'MONDAY': start_of_week,
        'TUESDAY': start_of_week + timedelta(days=1),
        'WEDNESDAY': start_of_week + timedelta(days=2),
        'THURSDAY': start_of_week + timedelta(days=3),
        'FRIDAY': start_of_week + timedelta(days=4),
        'SATURDAY': start_of_week + timedelta(days=5),
        'SUNDAY': start_of_week + timedelta(days=6),
    }

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        semester_id = request.POST.get('semester')
        
        # Iterate through POST data to find attendance entries
        for key, status in request.POST.items():
            if key.startswith('attendance_'):
                # Format: attendance_{student_id}_{date_str}_{slot_id}
                try:
                    parts = key.split('_')
                    if len(parts) == 4:
                        student_id = parts[1]
                        date_str = parts[2]
                        slot_id = parts[3]
                        
                        Attendance.objects.update_or_create(
                            student_id=student_id,
                            subject_id=subject_id,
                            date=date_str,
                            timetable_slot_id=slot_id,
                            defaults={
                                'status': status,
                                'marked_by': request.user
                            }
                        )
                except (IndexError, ValueError):
                    continue
        
        messages.success(request, 'Attendance updated successfully!')
        # Redirect to preserve filters
        return redirect(f"{request.path}?course={request.POST.get('course_id')}&semester={semester_id}&subject={subject_id}")
    
    # Get teacher's subjects
    assigned_subjects = TeacherSubjectAssignment.objects.filter(teacher=request.user).values_list('subject_id', flat=True)
    timetable_subjects = Timetable.objects.filter(teacher=request.user).values_list('subject_id', flat=True)
    subject_ids = set(list(assigned_subjects) + list(timetable_subjects))
    my_subjects = Subject.objects.filter(id__in=subject_ids)
    
    # Filter Logic
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    selected_subject_id = request.GET.get('subject')
    
    courses = Course.objects.filter(semesters__subjects__in=my_subjects).distinct()
    semesters = Semester.objects.none()
    subjects = Subject.objects.none()
    
    # Grid Data
    grid_columns = []
    students_data = []
    
    if selected_course_id:
        semesters = Semester.objects.filter(course_id=selected_course_id)
        
    if selected_semester_id:
        subjects = Subject.objects.filter(semester_id=selected_semester_id, id__in=subject_ids)
        
    if selected_subject_id and selected_semester_id:
        # 1. Build Grid Columns (Chronological M-S)
        ordered_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        
        # Fetch all timetable slots for this subject
        all_slots = Timetable.objects.filter(subject_id=selected_subject_id)
        
        for day in ordered_days:
            day_date = week_dates[day]
            day_slots = all_slots.filter(day_of_week=day).order_by('start_time')
            
            for slot in day_slots:
                grid_columns.append({
                    'date': str(day_date), # Convert to string YYYY-MM-DD for consistency
                    'day_name': day, # e.g. MONDAY
                    'short_day': day[:3], # MON
                    'start_time': slot.start_time,
                    'slot_id': slot.id
                })
        
        # 2. Fetch Students and their Attendance
        students = Student.objects.filter(semester_id=selected_semester_id).order_by('enrollment_number')
        
        # Fetch existing attendance for this week
        week_start = week_dates['MONDAY']
        week_end = week_dates['SATURDAY']
        
        existing_records = Attendance.objects.filter(
            subject_id=selected_subject_id,
            date__range=[week_start, week_end],
            student__semester_id=selected_semester_id
        )
        
        # Map: student_id -> { date_slot_id : status }
        attendance_map = {}
        for record in existing_records:
            if record.timetable_slot:
                 key = f"{record.date}_{record.timetable_slot.id}"
                 if record.student_id not in attendance_map:
                     attendance_map[record.student_id] = {}
                 attendance_map[record.student_id][key] = record.status

        # 3. Build Row Data
        for student in students:
            row = {'student': student, 'cells': []}
            student_att = attendance_map.get(student.pk, {})
            
            for col in grid_columns:
                # Key must match what we built above
                key = f"{col['date']}_{col['slot_id']}"
                status = student_att.get(key, None) # None means not marked yet
                
                row['cells'].append({
                    'status': status,
                    'input_name': f"attendance_{student.pk}_{col['date']}_{col['slot_id']}",
                    'col_id': f"{col['date']}_{col['slot_id']}" # To link with column header if needed
                })
            students_data.append(row)

    context = {
        'courses': courses,
        'semesters': semesters,
        'subjects': subjects,
        'grid_columns': grid_columns,
        'students_data': students_data,
        'selected_course_id': int(selected_course_id) if selected_course_id else None,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id else None,
        'selected_subject_id': int(selected_subject_id) if selected_subject_id else None,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        # Pass context for preserving filter
        'course_id': selected_course_id, 
    }
    return render(request, 'teacher/teacher_attendance_final.html', context)


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
    
    # Get teacher's subjects from Assignments AND Timetable
    assigned_subjects = TeacherSubjectAssignment.objects.filter(teacher=request.user).values_list('subject_id', flat=True)
    timetable_subjects = Timetable.objects.filter(teacher=request.user).values_list('subject_id', flat=True)
    
    subject_ids = set(list(assigned_subjects) + list(timetable_subjects))
    my_subjects = Subject.objects.filter(id__in=subject_ids)
    
    # Filter Papers (Global View)
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
        'my_subjects': my_subjects,
        'courses': Course.objects.filter(semesters__subjects__in=my_subjects).distinct(),
        'semesters': Semester.objects.all(),
        'subjects': my_subjects,  # Show only my subjects in upload/filter list? Or all? User implies my subjects.
        'selected_course': int(course_id) if course_id else None,
        'selected_semester': int(semester_id) if semester_id else None,
        'selected_subject': int(subject_id) if subject_id else None,
    }
    return render(request, 'teacher/teacher_question_bank.html', context)
