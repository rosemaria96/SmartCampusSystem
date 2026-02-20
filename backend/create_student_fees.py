import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academics.models import Student
from finance.models import FeeStructure, StudentFee

print("=== CREATING STUDENT FEE RECORDS ===\n")

# Get all students
students = Student.objects.all()
print(f"Found {students.count()} students\n")

# Get all fee structures
fee_structures = FeeStructure.objects.all()
print(f"Found {fee_structures.count()} fee structures\n")

created_count = 0

for student in students:
    print(f"Processing: {student.user.name}")
    print(f"  Course: {student.course.course_name}")
    print(f"  Semester: {student.semester.semester_number}")
    
    # Find matching fee structures
    matching_fees = fee_structures.filter(
        course=student.course,
        semester=student.semester
    )
    
    print(f"  Matching fee structures: {matching_fees.count()}")
    
    for fee_structure in matching_fees:
        obj, created = StudentFee.objects.get_or_create(
            student=student,
            fee_structure=fee_structure,
            defaults={
                'payable_amount': fee_structure.total_amount,
                'status': 'PENDING'
            }
        )
        
        if created:
            print(f"    ✓ Created StudentFee ID: {obj.id} - ₹{obj.payable_amount}")
            created_count += 1
        else:
            print(f"    - Already exists: StudentFee ID: {obj.id}")
    
    print()

print(f"\n=== SUMMARY ===")
print(f"Total StudentFee records created: {created_count}")
print(f"Total StudentFee records in DB: {StudentFee.objects.count()}")
