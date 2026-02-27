import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Student
from finance.models import StudentFee

User = get_user_model()

with open('student_fees_diagnosis.txt', 'w', encoding='utf-8') as f:
    def log(msg):
        print(msg)
        f.write(msg + '\n')

    log("=== DIAGNOSING STUDENT FEE VISIBILITY ===\n")

    # List all users with STUDENT role
    students_users = User.objects.filter(role='STUDENT')
    log(f"Total STUDENT users: {students_users.count()}\n")

    for user in students_users:
        log(f"User: {user.username} ({user.name})")
        log(f"  Role: {user.role}")
        
        # Check if student profile exists
        try:
            student = user.student_profile
            log(f"  ✓ Student Profile EXISTS (ID: {student.id})")
            log(f"    Course: {student.course.course_name}")
            log(f"    Semester: {student.semester.semester_number if student.semester else 'None'}")
            
            # Query StudentFee records
            fees = StudentFee.objects.filter(student=student)
            log(f"    StudentFee records: {fees.count()}")
            for fee in fees:
                log(f"      - Fee ID: {fee.id}, Amount: ₹{fee.payable_amount}, Status: {fee.status}")
                log(f"        Structure: {fee.fee_structure.course.course_name} Sem {fee.fee_structure.semester.semester_number}")
        except Student.DoesNotExist:
            log(f"  ✗ NO Student Profile found!")
        except Exception as e:
            log(f"  ✗ Error: {e}")
        
        log("")

    log("\n=== ALL STUDENT FEE RECORDS ===")
    all_fees = StudentFee.objects.all()
    log(f"Total StudentFee records in DB: {all_fees.count()}")
    for fee in all_fees:
        log(f"  Fee ID: {fee.id}, Student: {fee.student.user.username}, Amount: ₹{fee.payable_amount}, Status: {fee.status}")
