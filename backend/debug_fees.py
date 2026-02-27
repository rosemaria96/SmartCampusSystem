import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academics.models import Student, Course, Semester
from finance.models import FeeStructure, StudentFee

with open('fees_debug.txt', 'w', encoding='utf-8') as f:
    def log(msg):
        print(msg)
        f.write(msg + '\n')

    log("--- DEBUGGING FEE VISIBILITY ---")

    students = Student.objects.all()
    log(f"Total Students: {students.count()}")

    for student in students:
        log(f"\nStudent: {student.user.username} ({student.user.name})")
        log(f"  Enrolled Course: {student.course.course_name} (ID: {student.course.id})")
        if student.semester:
            log(f"  Semester: Sem {student.semester.semester_number} (ID: {student.semester.id}) - Course ID: {student.semester.course_id}")
        else:
            log("  Semester: None")
        
        # Check for applicable fee structures
        fees = FeeStructure.objects.filter(course=student.course, semester=student.semester)
        log(f"  Applicable Fee Structures Found: {fees.count()}")
        for fee in fees:
            log(f"    - ID: {fee.id}, Amount: {fee.total_amount}")

        # Check for existing student fees
        s_fees = StudentFee.objects.filter(student=student)
        log(f"  Existing Student Fee Records: {s_fees.count()}")
        for sf in s_fees:
            log(f"    - ID: {sf.id}, Status: {sf.status}, Structure ID: {sf.fee_structure.id}")

    log("\n--- ALL FEE STRUCTURES ---")
    for fs in FeeStructure.objects.all():
        log(f"ID: {fs.id}, Course: {fs.course.course_name} (ID: {fs.course.id}), Sem: {fs.semester.semester_number} (ID: {fs.semester.id})")

    log("\n--- ALL SEMESTERS ---")
    for s in Semester.objects.all():
        log(f"ID: {s.id}, Course: {s.course.course_name}, Number: {s.semester_number}")
