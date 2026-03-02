from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Semester, Student


@receiver(post_save, sender=Course)
def create_semesters(sender, instance, created, **kwargs):
    if created:
        total_semesters = instance.duration_years * 2
        for i in range(1, total_semesters + 1):
            Semester.objects.create(course=instance, semester_number=i)


@receiver(post_save, sender=Student)
def assign_fees_to_new_student(sender, instance, created, **kwargs):
    """When a new student is created, auto-create StudentFee records
    for every FeeStructure that matches their course and semester."""
    if not created:
        return
    try:
        from finance.models import FeeStructure, StudentFee
        matching = FeeStructure.objects.filter(
            course=instance.course,
            semester=instance.semester
        )
        for fs in matching:
            StudentFee.objects.get_or_create(
                student=instance,
                fee_structure=fs,
                defaults={'payable_amount': fs.total_amount, 'status': 'PENDING'}
            )
    except Exception:
        pass  # Never break student creation


def assign_fees_for_new_structure(fee_structure):
    """Assign a FeeStructure to all existing matching students.
    Called directly AND via signal so it works everywhere."""
    try:
        from finance.models import StudentFee
        matching_students = Student.objects.filter(
            course=fee_structure.course,
            semester=fee_structure.semester
        )
        for student in matching_students:
            StudentFee.objects.get_or_create(
                student=student,
                fee_structure=fee_structure,
                defaults={'payable_amount': fee_structure.total_amount, 'status': 'PENDING'}
            )
    except Exception:
        pass  # Never break fee structure creation


# Import FeeStructure lazily to avoid circular imports at module load time
def connect_fee_structure_signal():
    try:
        from finance.models import FeeStructure

        @receiver(post_save, sender=FeeStructure)
        def on_fee_structure_saved(sender, instance, created, **kwargs):
            """Auto-assign newly created FeeStructure to all existing matching students."""
            if created:
                assign_fees_for_new_structure(instance)

    except Exception:
        pass


connect_fee_structure_signal()
