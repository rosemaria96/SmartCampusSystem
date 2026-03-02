import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academics.models import Student
from finance.models import StudentFee
from django.contrib.auth import get_user_model

User = get_user_model()
username = "msccs2523"  # Ragendhu

print(f"Checking for duplicates for user: {username}\n")

user = User.objects.get(username=username)
print(f"User ID: {user.id}")

# Check Student table directly
students = Student.objects.filter(user=user)
print(f"Found {students.count()} Student records for this user:")

for s in students:
    print(f"  - Student PK: {s.pk}, Enrollment: {s.enrollment_number}")
    fees = StudentFee.objects.filter(student=s)
    print(f"    Linked Fees: {fees.count()}")

print("\nChecking all Students table:")
all_s = Student.objects.all()
for s in all_s:
    if s.user.username == username:
         print(f"  MATCH:  PK: {s.pk}, User: {s.user.username}")
