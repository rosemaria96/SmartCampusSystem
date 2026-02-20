import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Student
from finance.models import StudentFee

User = get_user_model()

# Get the username from command line or use default
username = sys.argv[1] if len(sys.argv) > 1 else "msccs2524"

print(f"Checking user: {username}\n")

try:
    user = User.objects.get(username=username)
    print(f"✓ User found: {user.name}")
    print(f"  Role: {user.role}")
    print(f"  ID: {user.id}")
    
    # Try to access student_profile
    try:
        student = user.student_profile
        print(f"\n✓ Student Profile found!")
        print(f"  Student ID: {student.user_id}")
        print(f"  Enrollment: {student.enrollment_number}")
        print(f"  Course: {student.course.course_name} (ID: {student.course.id})")
        print(f"  Semester: {student.semester.semester_number} (ID: {student.semester.id})")
        
        # Query fees
        fees = StudentFee.objects.filter(student=student)
        print(f"\n  StudentFee Query: StudentFee.objects.filter(student={student.user_id})")
        print(f"  Result: {fees.count()} records")
        
        for fee in fees:
            print(f"    - Fee ID: {fee.id}")
            print(f"      Amount: ₹{fee.payable_amount}")
            print(f"      Status: {fee.status}")
            print(f"      Structure Course: {fee.fee_structure.course.course_name}")
            print(f"      Structure Semester: {fee.fee_structure.semester.semester_number}")
            
    except Student.DoesNotExist:
        print(f"\n✗ NO student_profile found for this user!")
        print(f"  Checking Student table directly...")
        students = Student.objects.filter(user=user)
        print(f"  Direct query result: {students.count()} records")
        
except User.DoesNotExist:
    print(f"✗ User '{username}' not found!")
