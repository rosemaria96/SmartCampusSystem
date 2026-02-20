from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Course, Semester

@receiver(post_save, sender=Course)
def create_semesters(sender, instance, created, **kwargs):
    if created:
        # Assuming 2 semesters per year
        total_semesters = instance.duration_years * 2
        for i in range(1, total_semesters + 1):
            Semester.objects.create(course=instance, semester_number=i)
