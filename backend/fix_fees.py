import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academics.models import Student
from finance.models import FeeStructure, StudentFee

print("--- FIXING MISSING FEE RECORDS ---")

students = Student.objects.all()

for student in students:
    print(f"\nProcessing Student: {student.user.username}")
    
    # distinct() to avoid duplicates if any logic issues
    applicable_fees = FeeStructure.objects.filter(
        course=student.course,
        semester=student.semester
    )
    
    print(f"  Found {applicable_fees.count()} applicable fee structures.")
    
    for fee_structure in applicable_fees:
        obj, created = StudentFee.objects.get_or_create(
            student=student,
            fee_structure=fee_structure,
            defaults={
                'payable_amount': fee_structure.total_amount,
                'status': 'PENDING'
            }
        )
        if created:
            print(f"  [CREATED] Fee record for {fee_structure} - ₹{obj.payable_amount}")
        else:
            print(f"  [EXISTS] Fee record for {fee_structure} - Status: {obj.status}")

print("\nFix complete.")
