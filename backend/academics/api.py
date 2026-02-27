from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Semester

@login_required
def get_semesters(request):
    course_id = request.GET.get('course_id')
    semesters = Semester.objects.filter(course_id=course_id).values('id', 'semester_number')
    return JsonResponse(list(semesters), safe=False)
