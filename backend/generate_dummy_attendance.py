import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Student, Subject, Attendance

User = get_user_model()

def generate_attendance():
    print("=== Generating Dummy Attendance Data ===")

    # 1. Find a marker (Teacher)
    teacher = User.objects.filter(role='TEACHER').first()
    if not teacher:
        print("Error: No teacher found to mark attendance. Please create a teacher first.")
        return
    print(f"Marking as Teacher: {teacher.name}")

    # 2. Get all students
    students = Student.objects.all()
    print(f"Found {students.count()} students.")

    # 3. Date Range (Past 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    records_created = 0
    records_updated = 0

    for student in students:
        print(f"\nProcessing Student: {student.user.name} ({student.enrollment_number})")
        
        # Get subjects for student's semester
        subjects = Subject.objects.filter(semester=student.semester)
        if not subjects.exists():
            print(f"  No subjects found for semester {student.semester}")
            continue

        # Iterate days
        current_date = start_date
        while current_date <= end_date:
            # Skip Sundays
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            for subject in subjects:
                # 90% chance of being present, but vary per student/subject for realism
                # Add some randomness to the probability
                probability = random.uniform(0.80, 0.95) 
                is_present = random.random() < probability
                status = 'PRESENT' if is_present else 'ABSENT'

                obj, created = Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=current_date,
                    defaults={
                        'status': status,
                        'marked_by': teacher
                    }
                )
                
                if created:
                    records_created += 1
                else:
                    records_updated += 1
            
            current_date += timedelta(days=1)

    print(f"\n\n=== Completed ===")
    print(f"Records Created: {records_created}")
    print(f"Records Updated: {records_updated}")
    print(f"Total Attendance Records: {Attendance.objects.count()}")

if __name__ == "__main__":
    generate_attendance()
