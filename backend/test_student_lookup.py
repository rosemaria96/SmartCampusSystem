import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academics.models import Student
from finance.models import StudentFee

User = get_user_model()

# Get ragendhu user
user = User.objects.get(username="msccs2523")
print(f"User: {user.username} (ID: {user.id})")

# Try different ways to get Student
print("\n1. Using Student.objects.get(user=user):")
try:
    student = Student.objects.get(user=user)
    print(f"   ✓ Found: {student}")
    print(f"   Primary Key: {student.pk}")
    print(f"   User ID: {student.user_id}")
except Student.DoesNotExist:
    print(f"   ✗ NOT FOUND")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Using user.student_profile:")
try:
    student = user.student_profile
    print(f"   ✓ Found: {student}")
    print(f"   Primary Key: {student.pk}")
except Student.DoesNotExist:
    print(f"   ✗ NOT FOUND")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Listing ALL Student records:")
all_students = Student.objects.all()
print(f"   Total: {all_students.count()}")
for s in all_students:
    print(f"   - PK: {s.pk}, User ID: {s.user_id}, Name: {s.user.name}")

print("\n4. Checking StudentFee for user_id=36:")
fees = StudentFee.objects.filter(student__user_id=36)
print(f"   Found {fees.count()} fees")
for fee in fees:
    print(f"   - Fee ID: {fee.id}, Student PK: {fee.student.pk}")
