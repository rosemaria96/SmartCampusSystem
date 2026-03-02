from django.core.management.base import BaseCommand
from academics.models import Timetable, TeacherSubjectAssignment

class Command(BaseCommand):
    help = 'Populates TeacherSubjectAssignment table from existing Timetable entries'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting population of teacher assignments...')
        
        timetables = Timetable.objects.all().select_related('subject', 'teacher')
        count = 0
        
        for entry in timetables:
            # We use get_or_create to avoid duplicates
            obj, created = TeacherSubjectAssignment.objects.get_or_create(
                teacher=entry.teacher,
                subject=entry.subject
            )
            if created:
                count += 1
                self.stdout.write(f'Assigned {entry.teacher.name} to {entry.subject.subject_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} new assignments.'))
