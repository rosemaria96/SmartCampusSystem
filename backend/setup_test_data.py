import os
import sys
import django
from datetime import date, time, timedelta, datetime
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from academics.models import (
    Department, Course, Semester, Subject, Student, 
    TeacherSubjectAssignment, Attendance, Timetable, Exam, Result
)
from finance.models import FeeStructure, StudentFee, Payment
from communication.models import Notification
from assessments.models import QuestionPaper

def create_test_data():
    print("🗑️  Cleaning up existing data...")
    User.objects.all().delete()
    Department.objects.all().delete()
    # Cascading deletes will handle the rest

    print("👥 Creating Users...")
    # Admin
    admin = User.objects.create_superuser(
        username='admin', email='admin@cruzhorizon.com', password='password123',
        name='Super Admin', role='ADMIN'
    )
    print(f"   Created Admin: {admin.username}")

    # Teachers
    teachers = []
    teacher_names = ['John Smith', 'Sarah Wilson', 'Michael Brown', 'Emily Davis', 'Robert Johnson']
    for i, name in enumerate(teacher_names):
        t = User.objects.create_user(
            username=f'teacher{i+1}', email=f'teacher{i+1}@cruzhorizon.com', password='password123',
            name=name, role='TEACHER'
        )
        teachers.append(t)
    print(f"   Created {len(teachers)} Teachers")

    print("🏫 Creating Academics Structure...")
    # Departments
    dept_cs = Department.objects.create(department_name='Computer Science')
    dept_eng = Department.objects.create(department_name='Engineering')
    
    # Courses
    course_btech = Course.objects.create(department=dept_cs, course_name='B.Tech CS', duration_years=4)
    course_mech = Course.objects.create(department=dept_eng, course_name='B.Tech Mechanical', duration_years=4)

    # Semesters
    sem1_btech = Semester.objects.create(course=course_btech, semester_number=1)
    sem2_btech = Semester.objects.create(course=course_btech, semester_number=2)
    sem1_mech = Semester.objects.create(course=course_mech, semester_number=1)

    # Subjects
    subjects = []
    sub_data = [
        (sem1_btech, 'CS101', 'Intro to Programming', 4),
        (sem1_btech, 'MAT101', 'Calculus I', 3),
        (sem1_btech, 'PHY101', 'Physics I', 3),
        (sem2_btech, 'CS102', 'Data Structures', 4),
        (sem1_mech, 'ME101', 'Thermodynamics', 4),
    ]
    for sem, code, name, credits in sub_data:
        s = Subject.objects.create(semester=sem, subject_code=code, subject_name=name, credits=credits)
        subjects.append(s)
    
    print(f"   Created Departments, Courses, Semesters, and {len(subjects)} Subjects")

    print("🎓 Creating Students...")
    students = []
    for i in range(1, 21):
        s_user = User.objects.create_user(
            username=f'student{i}', email=f'student{i}@cruzhorizon.com', password='password123',
            name=f'Student {i}', role='STUDENT'
        )
        # Assign to B.Tech Sem 1 or 2 randomly
        sem = sem1_btech if i <= 10 else sem2_btech
        course = course_btech
        
        student = Student.objects.create(
            user=s_user,
            course=course,
            semester=sem,
            enrollment_number=f'CS2026{i:03d}'
        )
        students.append(student)
    print(f"   Created {len(students)} Students")

    print("📚 Assigning Teachers to Subjects...")
    # Assign each subject a random teacher
    for subject in subjects:
        teacher = random.choice(teachers)
        TeacherSubjectAssignment.objects.create(teacher=teacher, subject=subject)
    
    print("📅 Creating Timetable...")
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    times = [time(9, 0), time(10, 0), time(11, 0), time(14, 0)]
    
    for subject in subjects:
        # Create 2 slots per week for each subject
        for _ in range(2):
            Timetable.objects.create(
                subject=subject,
                teacher=subject.teacher_assignments.first().teacher,
                semester=subject.semester,
                day_of_week=random.choice(days),
                start_time=random.choice(times),
                end_time=time(hour=random.choice(times).hour + 1, minute=0)
            )

    print("✅ Marking Attendance (Past 7 days)...")
    today = date.today()
    for i in range(7):
        curr_date = today - timedelta(days=i)
        if curr_date.weekday() >= 5: continue # Skip weekends
        
        for student in students:
            # Mark for all subjects in their semester
            student_subjects = student.semester.subjects.all()
            for sub in student_subjects:
                status = 'PRESENT' if random.random() > 0.1 else 'ABSENT'
                teacher = sub.teacher_assignments.first().teacher
                Attendance.objects.create(
                    student=student,
                    subject=sub,
                    date=curr_date,
                    status=status,
                    marked_by=teacher
                )

    print("💰 Creating Fees & Payments...")
    # Fee Structure
    fee_sem1 = FeeStructure.objects.create(
        course=course_btech, semester=sem1_btech, 
        total_amount=50000.00, due_date=today + timedelta(days=30)
    )
    
    # Assign fees to students
    for student in students:
        if student.semester == sem1_btech:
            sf = StudentFee.objects.create(
                student=student, fee_structure=fee_sem1, 
                payable_amount=50000.00, status='PENDING'
            )
            # Make some paid
            if random.random() > 0.5:
                Payment.objects.create(
                    student_fee=sf, amount_paid=50000.00, 
                    payment_method='ONLINE', transaction_reference=f'TXN{random.randint(10000,99999)}'
                )
                sf.status = 'PAID'
                sf.save()

    print("📢 Creating Notifications...")
    Notification.objects.create(message="Welcome to the Smart Campus System! Semester started.", user=None) # Broadcast
    for student in students[:3]:
        Notification.objects.create(user=student.user, message="Your fee payment is successful.")

    print("\n✅ Test Data Setup Complete!")
    print("------------------------------------------")
    print("Admin: admin / password123")
    print("Teacher: teacher1 / password123")
    print("Student: student1 / password123")
    print("------------------------------------------")

if __name__ == '__main__':
    create_test_data()
