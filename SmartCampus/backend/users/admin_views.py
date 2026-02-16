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
from datetime import datetime, timedelta


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
                semester_id = request.POST.get('semester')
                
                Student.objects.create(
                    user=user,
                    enrollment_number=enrollment_number,
                    course_id=course_id,
                    semester_id=semester_id
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
def attendance_reports(request):
    """View attendance reports"""
    attendances = Attendance.objects.all().select_related('student', 'subject', 'marked_by')
    
    # Filter by course/semester
    course_id = request.GET.get('course')
    semester_id = request.GET.get('semester')
    
    if course_id:
        attendances = attendances.filter(student__course_id=course_id)
    if semester_id:
        attendances = attendances.filter(student__semester_id=semester_id)
    
    context = {
        'attendances': attendances[:100],  # Limit for performance
        'courses': Course.objects.all(),
        'semesters': Semester.objects.all(),
    }
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
            form.save()
            messages.success(request, 'Fee structure added successfully!')
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
