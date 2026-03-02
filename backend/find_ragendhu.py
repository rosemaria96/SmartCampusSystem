import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Student
from finance.models import StudentFee

User = get_user_model()

# Find user by name
users = User.objects.filter(name__icontains="ragendhu")
print(f"Found {users.count()} users matching 'ragendhu':\n")

for user in users:
    print(f"Username: {user.username}")
    print(f"Name: {user.name}")
    print(f"Role: {user.role}")
    print(f"ID: {user.id}")
    
    # Check for Student record
    try:
        student = Student.objects.get(user=user)
        print(f"✓ Student record found!")
        print(f"  Student primary key: {student.pk}")
        print(f"  Course: {student.course.course_name}")
        print(f"  Semester: {student.semester.semester_number}")
        
        # Check StudentFee records
        fees = StudentFee.objects.filter(student=student)
        print(f"  StudentFee records: {fees.count()}")
        for fee in fees:
            print(f"    - ID: {fee.id}, Amount: ₹{fee.payable_amount}, Status: {fee.status}")
    except Student.DoesNotExist:
        print(f"✗ NO Student record found")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
