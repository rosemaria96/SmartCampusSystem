import os
import django
import random
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User, StudentProfile, TeacherProfile
from academics.models import Department, Course, Class, Enrollment, Attendance
from assessments.models import Assessment, Submission, Grade
from finance.models import FeePayment, Transaction
from communication.models import Notification, Announcement

def create_comprehensive_data():
    print("Starting Comprehensive Data Seeding...")
    
    # 1. Create Roles
    def get_or_create_user(username, email, password, is_student=False, is_teacher=False, is_admin=False):
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'is_student': is_student,
            'is_teacher': is_teacher,
            'is_admin': is_admin
        })
        if created:
            user.set_password(password)
            user.save()
        return user

    admin = get_or_create_user('admin', 'admin@cruz.edu', '123', is_admin=True)

    # 2. Departments
    depts = [
        ('Computer Science', 'Cutting edge Computing and AI'),
        ('Physics', 'Quantum Mechanics and Astrophysics'),
        ('Mathematics', 'Advanced Calculus and Logic'),
        ('English', 'Modern Literature and Linguistics')
    ]
    department_objs = []
    for name, desc in depts:
        obj, _ = Department.objects.get_or_create(name=name, defaults={'description': desc})
        department_objs.append(obj)

    # 3. Teachers & Profiles
    teachers = []
    designations = ['Professor', 'Assistant Professor', 'Senior Lecturer', 'Department Head']
    for i in range(1, 11):
        username = f'teacher{i}'
        t_user = get_or_create_user(username, f'{username}@cruz.edu', '123', is_teacher=True)
        TeacherProfile.objects.get_or_create(user=t_user, defaults={
            'employee_id': f'EMP{100+i}',
            'designation': random.choice(designations)
        })
        teachers.append(t_user)
        # Assign head of department for some
        if i <= len(department_objs):
            dept = department_objs[i-1]
            dept.head_of_department = t_user
            dept.save()

    # 4. Courses & Classes
    course_list = [
        ('Intro to Python', 'CS101', 'Computer Science'),
        ('Data Structures', 'CS201', 'Computer Science'),
        ('Quantum Physics', 'PHY101', 'Physics'),
        ('Linear Algebra', 'MAT101', 'Mathematics'),
        ('Creative Writing', 'ENG101', 'English'),
    ]
    class_objs = []
    for name, code, dept_name in course_list:
        dept = Department.objects.get(name=dept_name)
        course, _ = Course.objects.get_or_create(name=name, code=code, department=dept)
        
        # Create 2 sections for each course
        for sec in ['A', 'B']:
            teacher = random.choice(teachers)
            cls, _ = Class.objects.get_or_create(
                course=course, 
                section=sec, 
                defaults={
                    'teacher': teacher,
                    'room_number': f'R{random.randint(100, 500)}',
                    'schedule_info': f'{random.choice(["Mon", "Tue", "Wed", "Thu", "Fri"])} {random.randint(9, 16)}:00'
                }
            )
            class_objs.append(cls)

    # 5. Students & Enrollments
    students = []
    for i in range(1, 51):
        username = f'student{i}'
        s_user = get_or_create_user(username, f'{username}@cruz.edu', '123', is_student=True)
        StudentProfile.objects.get_or_create(user=s_user, defaults={
            'student_id': f'STU{1000+i}',
            'current_year': random.randint(1, 4)
        })
        students.append(s_user)
        
        # Enroll in 3 random classes
        enrolled_classes = random.sample(class_objs, 3)
        for cls in enrolled_classes:
            Enrollment.objects.get_or_create(student=s_user, enrolled_class=cls)

    # 6. Attendance Seeding (Last 7 days)
    today = date.today()
    for i in range(7):
        curr_date = today - timedelta(days=i)
        for cls in class_objs:
            enrollments = Enrollment.objects.filter(enrolled_class=cls)
            for enr in enrollments:
                status = 'present' if random.random() > 0.1 else 'absent'
                Attendance.objects.get_or_create(
                    student=enr.student,
                    enrolled_class=cls,
                    date=curr_date,
                    defaults={'status': status}
                )

    # 7. Assessments & Grades
    for cls in class_objs:
        ass, _ = Assessment.objects.get_or_create(
            class_instance=cls,
            title=f"Midterm Quiz - {cls.course.name}",
            defaults={
                'assessment_type': 'quiz',
                'due_date': timezone.now() - timedelta(days=2),
                'max_score': 100
            }
        )
        # Grade 50% of students
        enrollments = Enrollment.objects.filter(enrolled_class=cls)[:10]
        for enr in enrollments:
            sub, _ = Submission.objects.get_or_create(assessment=ass, student=enr.student)
            Grade.objects.get_or_create(
                submission=sub,
                defaults={
                    'score': random.randint(60, 100),
                    'graded_by': cls.teacher,
                    'feedback': 'Good effort!'
                }
            )

    # 8. Finance (Fees)
    for s_user in students[:20]:
        fp, _ = FeePayment.objects.get_or_create(
            student=s_user,
            academic_year='2024-25',
            semester='1',
            defaults={
                'total_amount': 5000,
                'paid_amount': 2500 if random.random() > 0.5 else 0,
                'status': 'partial' if random.random() > 0.5 else 'pending',
                'due_date': date.today() + timedelta(days=30)
            }
        )

    # 9. Communication
    Announcement.objects.get_or_create(
        title='Welcome to Cruz Horizon!',
        content='Official start of the 2024 Academic Year is next Monday.',
        target_audience='all',
        created_by=admin
    )

    print(f"Seeding Complete! Created {len(students)} students, {len(teachers)} teachers, and {len(class_objs)} classes.")

if __name__ == '__main__':
    create_comprehensive_data()
