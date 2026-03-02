from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from users.models import User
from academics.models import (
    Department, Course, Semester, Subject, Student, 
    Attendance, Timetable, TeacherSubjectAssignment
)
from communication.models import Notification
from assessments.models import QuestionPaper
from finance.models import FeeStructure, StudentFee, Payment
from datetime import datetime, timedelta, date


def require_admin(view_func):
    """Decorator to require admin role"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ADMIN':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_admin
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': User.objects.filter(role='TEACHER').count(),
        'total_courses': Course.objects.count(),
        'total_departments': Department.objects.count(),
        'recent_notifications': Notification.objects.all()[:5],
    }
    return render(request, 'admin/admin_dashboard.html', context)


@login_required
@require_admin
def user_management(request):
    """User management page"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'users': users,
        'total_students': User.objects.filter(role='STUDENT').count(),
        'total_teachers': User.objects.filter(role='TEACHER').count(),
        'selected_role': role_filter,
        'is_student_selected': role_filter == 'STUDENT',
        'is_teacher_selected': role_filter == 'TEACHER',
        'is_admin_selected': role_filter == 'ADMIN',
    }
    return render(request, 'admin/admin_user_management.html', context)


@login_required
@require_admin
def create_user(request):
    """Create new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        name = request.POST.get('name')
        role = request.POST.get('role')
        password = request.POST.get('password')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                name=name,
                role=role
            )
            
            # If student, create student profile
            if role == 'STUDENT':
                enrollment_number = request.POST.get('enrollment_number')
                course_id = request.POST.get('course')
                semester_number = request.POST.get('semester_number')
                
                try:
                    semester = Semester.objects.get(course_id=course_id, semester_number=semester_number)
                except Semester.DoesNotExist:
                    # Provide a fallback or create it? User requirement implies stricter control.
                    # For now, let's assume it exists or fail gracefully.
                    # Ideally, validation should happen before User creation, but for simplicity here:
                    user.delete() # Rollback user creation
                    messages.error(request, f'Semester {semester_number} does not exist for the selected course.')
                    return redirect('create_user')
                
                Student.objects.create(
                    user=user,
                    enrollment_number=enrollment_number,
                    course_id=course_id,
                    semester=semester
                )
            
            messages.success(request, f'User {username} created successfully!')
            return redirect('user_management')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    context = {
        'courses': Course.objects.all(),
        'semesters': Semester.objects.all(),
    }
    return render(request, 'admin/create_user.html', context)


@login_required
@require_admin
def manage_academics(request):
    """Manage departments, courses, subjects"""
    context = {
        'departments': Department.objects.all(),
        'courses': Course.objects.all(),
        'subjects': Subject.objects.all(),
    }
    return render(request, 'admin/admin_academic.html', context)

# --- Department Management ---
from academics.forms import DepartmentForm, CourseForm, SubjectForm

@login_required
@require_admin
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('manage_academics')
    else:
        form = DepartmentForm()
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Add Department'})

@login_required
@require_admin
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('manage_academics')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Department'})

@login_required
@require_admin
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    messages.success(request, 'Department deleted successfully!')
    return redirect('manage_academics')

# --- Course Management ---
@login_required
@require_admin
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('manage_academics')
    else:
        form = CourseForm()
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Add Course'})

@login_required
@require_admin
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('manage_academics')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Course'})

@login_required
@require_admin
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted successfully!')
    return redirect('manage_academics')

# --- Subject Management ---
@login_required
@require_admin
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('manage_academics')
    else:
        form = SubjectForm()
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Add Subject'})

@login_required
@require_admin
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('manage_academics')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Subject'})

@login_required
@require_admin
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.delete()
    messages.success(request, 'Subject deleted successfully!')
    return redirect('manage_academics')


@login_required
@require_admin
def manage_timetable(request):
    """Manage timetable"""
    timetables = Timetable.objects.all().select_related('subject', 'teacher', 'semester')
    
    # Filter by semester if specified
    selected_semester_id = request.GET.get('semester')
    if selected_semester_id:
        try:
            selected_semester_id = int(selected_semester_id)
            timetables = timetables.filter(semester_id=selected_semester_id)
        except ValueError:
            selected_semester_id = None
    
    context = {
        'timetables': timetables,
        'semesters': Semester.objects.all(),
        'subjects': Subject.objects.all(),
        'teachers': User.objects.filter(role='TEACHER'),
        'selected_semester_id': selected_semester_id,
    }
    return render(request, 'admin/admin_timetable.html', context)

# --- Timetable Management ---
from academics.forms import TimetableForm

@login_required
@require_admin
def add_timetable(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry added successfully!')
            return redirect('manage_timetable')
    else:
        form = TimetableForm()
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Add Timetable Entry'})

@login_required
@require_admin
def edit_timetable(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated successfully!')
            return redirect('manage_timetable')
    else:
        form = TimetableForm(instance=entry)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Timetable Entry'})

@login_required
@require_admin
def delete_timetable(request, pk):
    entry = get_object_or_404(Timetable, pk=pk)
    entry.delete()
    messages.success(request, 'Timetable entry deleted successfully!')
    return redirect('manage_timetable')


@login_required
@require_admin
def create_timetable_grid(request):
    """Create timetable using grid view"""
    courses = Course.objects.all()
    # Initialize with default values
    semesters = Semester.objects.none()
    subjects = Subject.objects.none()
    
    selected_course_id = request.GET.get('course')
    selected_semester_id = request.GET.get('semester')
    
    if selected_course_id:
        try:
            selected_course_id = int(selected_course_id)
            semesters = Semester.objects.filter(course_id=selected_course_id)
        except ValueError:
            pass
            
    if selected_semester_id:
        try:
            selected_semester_id = int(selected_semester_id)
            subjects = Subject.objects.filter(semester_id=selected_semester_id)
        except ValueError:
            pass

    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    
    # Define slots based on user requirement: 
    # 9-10, 10-10:30, 10:30-11(Break), 11-12, 12-1, 1-2(Lunch), 2-3, 3-4
    slots = [
        {'start': '09:00', 'end': '10:00', 'is_break': False},
        {'start': '10:00', 'end': '10:30', 'is_break': False},
        {'start': '10:30', 'end': '11:00', 'is_break': True},
        {'start': '11:00', 'end': '12:00', 'is_break': False},
        {'start': '12:00', 'end': '13:00', 'is_break': False},
        {'start': '13:00', 'end': '14:00', 'is_break': True},
        {'start': '14:00', 'end': '15:00', 'is_break': False},
        {'start': '15:00', 'end': '16:00', 'is_break': False},
    ]

    if request.method == 'POST':
        semester_id = request.POST.get('semester_id')
        semester = get_object_or_404(Semester, pk=semester_id)
        
        # 1. Clear existing entries for this semester
        Timetable.objects.filter(semester=semester).delete()
        
        # 2. Iterate grids and save
        for day in days:
            for slot in slots:
                if slot.get('is_break'):
                    continue
                
                # Format time for keys
                start_key = slot['start'].replace(':', '')
                subject_key = f"subject_{day}_{start_key}"  # e.g., subject_MONDAY_0900
                teacher_key = f"teacher_{day}_{start_key}"
                
                # Check different key formats in case template uses formatted time
                # The template uses slot.start which creates '09:00'
                subject_key_tpl = f"subject_{day}_{slot['start']}"
                teacher_key_tpl = f"teacher_{day}_{slot['start']}"
                
                subject_id = request.POST.get(subject_key_tpl)
                teacher_id = request.POST.get(teacher_key_tpl)
                
                if subject_id and subject_id != 'NULL':
                    # Only save if we have a teacher or valid subject
                    if teacher_id: 
                        Timetable.objects.create(
                            semester=semester,
                            subject_id=subject_id,
                            teacher_id=teacher_id,
                            day_of_week=day,
                            start_time=slot['start'],
                            end_time=slot['end']
                        )
        
        messages.success(request, 'Timetable grid saved successfully!')
        return redirect('manage_timetable')

    # Create Subject -> Teachers map for dynamic filtering
    subject_teachers_map = {}
    all_subjects = Subject.objects.prefetch_related('teacher_assignments__teacher')
    
    for sub in all_subjects:
        teachers = sub.teacher_assignments.all()
        teacher_list = [{'id': t.teacher.id, 'name': t.teacher.name} for t in teachers]
        subject_teachers_map[sub.id] = teacher_list

    import json
    context = {
        'courses': courses,
        'semesters': semesters,
        'subjects': subjects,
        'teachers': User.objects.filter(role='TEACHER'), # Fallback/Initial
        'subject_teachers_map': json.dumps(subject_teachers_map),
        'selected_course_id': int(selected_course_id) if selected_course_id else None,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id else None,
        'days': days,
        'slots': slots,
    }
    return render(request, 'admin/timetable_creation.html', context)


@login_required
@require_admin
def attendance_reports(request):
    """View attendance reports (Class-wise Summary)"""
    # Filter by course/semester
    course_id = request.GET.get('course')
    semester_id = request.GET.get('semester')
    
    semesters = Semester.objects.select_related('course').prefetch_related('students')
    
    if course_id:
        semesters = semesters.filter(course_id=course_id)
    if semester_id:
        semesters = semesters.filter(id=semester_id)
        
    class_attendance_data = []
    
    for semester in semesters:
        student_count = semester.students.count()
        
        # Calculate overall attendance for this semester
        total_records = Attendance.objects.filter(student__semester=semester).count()
        present_records = Attendance.objects.filter(student__semester=semester, status='PRESENT').count()
        
        percentage = 0
        if total_records > 0:
            percentage = round((present_records / total_records) * 100, 1)
            
        class_attendance_data.append({
            'course_name': semester.course.course_name,
            'semester': semester,
            'student_count': student_count,
            'percentage': percentage,
            'total_records': total_records,
            'present_records': present_records
        })
    
    context = {
        'class_attendance_data': class_attendance_data,
        'courses': Course.objects.all(),
        'semesters': Semester.objects.all(),
        'selected_course_id': int(course_id) if course_id else None,
        'selected_semester_id': int(semester_id) if semester_id else None,
    }
    
    # Calculate Global Stats
    total_students = Student.objects.count()
    
    # Overall Rate
    total_att = Attendance.objects.count()
    present_att = Attendance.objects.filter(status='PRESENT').count()
    overall_rate = round((present_att / total_att * 100), 1) if total_att > 0 else 0
    
    # Today's Stats
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    today_recs = Attendance.objects.filter(date=today)
    today_total = today_recs.count()
    today_present = today_recs.filter(status='PRESENT').count()
    today_absent = today_recs.filter(status='ABSENT').count()
    
    today_rate = round((today_present / today_total * 100), 1) if today_total > 0 else 0
    
    context.update({
        'total_students': total_students,
        'overall_rate': overall_rate,
        'today_rate': today_rate,
        'absent_today': today_absent,
    })
    
    return render(request, 'admin/admin_attendance.html', context)


@login_required
@require_admin
def post_notification(request):
    """Post notification to all users or specific role"""
    if request.method == 'POST':
        message = request.POST.get('message')
        target_role = request.POST.get('target_role')  # 'ALL', 'STUDENT', 'TEACHER', 'ADMIN'
        
        if target_role == 'ALL':
            # Broadcast to all users
            users = User.objects.all()
        else:
            users = User.objects.filter(role=target_role)
        
        # Create notification for each user
        for user in users:
            Notification.objects.create(user=user, message=message)
        
        messages.success(request, f'Notification sent to {users.count()} users!')
        return redirect('admin_notifications')
    
    return render(request, 'admin/admin_noti.html')


@login_required
@require_admin
def admin_notifications(request):
    """View all notifications"""
    notifications = Notification.objects.all()[:50]
    return render(request, 'admin/admin_noti.html', {'notifications': notifications})


@login_required
@require_admin
def manage_question_papers(request):
    """Manage question papers"""
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
        return redirect('manage_question_papers')
    
    context = {
        'question_papers': QuestionPaper.objects.all(),
        'subjects': Subject.objects.all(),
    }
    return render(request, 'admin/admin_qn_bank.html', context)


@login_required
@require_admin
def manage_fees(request):
    """Manage fee structure"""
    context = {
        'fee_structures': FeeStructure.objects.all(),
        'student_fees': StudentFee.objects.all()[:50],
        'courses': Course.objects.all(),
        'semesters': Semester.objects.all(),
    }
    return render(request, 'admin/admin_fee_payment.html', context)

# --- Fee Management ---
from academics.forms import FeeStructureForm, StudentFeeForm

@login_required
@require_admin
def add_fee_structure(request):
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fee_structure = form.save()
            # Auto-assign this fee structure to all existing matching students
            from academics.signals import assign_fees_for_new_structure
            assign_fees_for_new_structure(fee_structure)
            messages.success(request, 'Fee structure added and assigned to existing students!')
            return redirect('manage_fees')
    else:
        form = FeeStructureForm()
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Add Fee Structure'})

@login_required
@require_admin
def edit_fee_structure(request, pk):
    fee = get_object_or_404(FeeStructure, pk=pk)
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure updated successfully!')
            return redirect('manage_fees')
    else:
        form = FeeStructureForm(instance=fee)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Fee Structure'})

@login_required
@require_admin
def delete_fee_structure(request, pk):
    fee = get_object_or_404(FeeStructure, pk=pk)
    fee.delete()
    messages.success(request, 'Fee structure deleted successfully!')
    return redirect('manage_fees')

@login_required
@require_admin
def edit_student_fee(request, pk):
    sf = get_object_or_404(StudentFee, pk=pk)
    if request.method == 'POST':
        form = StudentFeeForm(request.POST, instance=sf)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student fee updated successfully!')
            return redirect('manage_fees')
    else:
        form = StudentFeeForm(instance=sf)
    return render(request, 'admin/forms/academic_form.html', {'form': form, 'title': 'Edit Student Fee'})
