from django import forms
from .models import Department, Course, Subject, Semester

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name']
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department Name'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'department', 'duration_years']
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Course Name'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Duration (Years)'}),
        }

class SubjectForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))


    
    teacher_1 = forms.ModelChoiceField(
        queryset=None, 
        required=False,
        label="Teacher 1",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    teacher_2 = forms.ModelChoiceField(
        queryset=None, 
        required=False,
        label="Teacher 2 (Optional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Subject
        fields = ['course', 'subject_name', 'subject_code', 'semester', 'credits', 'teacher_1', 'teacher_2']
        widgets = {
            'subject_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject Name'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Subject Code'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Credits'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        teacher_qs = User.objects.filter(role='TEACHER')
        self.fields['teacher_1'].queryset = teacher_qs
        self.fields['teacher_2'].queryset = teacher_qs
        
        if self.instance.pk:
            self.fields['course'].initial = self.instance.semester.course
            self.fields['semester'].queryset = Semester.objects.filter(course=self.instance.semester.course)
            # Pre-select assigned teachers
            assigned_teachers = list(self.instance.teacher_assignments.values_list('teacher', flat=True))
            if len(assigned_teachers) > 0:
                self.fields['teacher_1'].initial = assigned_teachers[0]
            if len(assigned_teachers) > 1:
                self.fields['teacher_2'].initial = assigned_teachers[1]
        elif 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['semester'].queryset = Semester.objects.filter(course_id=course_id)
            except (ValueError, TypeError):
                pass
        else:
            self.fields['semester'].queryset = Semester.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        t1 = cleaned_data.get('teacher_1')
        t2 = cleaned_data.get('teacher_2')
        
        if t1 and t2 and t1 == t2:
            raise forms.ValidationError("Teacher 1 and Teacher 2 cannot be the same person.")
        return cleaned_data

    def save(self, commit=True):
        subject = super().save(commit=commit)
        if commit:
            from .models import TeacherSubjectAssignment
            # Update assignments
            t1 = self.cleaned_data.get('teacher_1')
            t2 = self.cleaned_data.get('teacher_2')
            
            # Clear existing
            TeacherSubjectAssignment.objects.filter(subject=subject).delete()
            
            # Add new
            if t1:
                TeacherSubjectAssignment.objects.create(subject=subject, teacher=t1)
            if t2:
                TeacherSubjectAssignment.objects.create(subject=subject, teacher=t2)
        return subject

from .models import Timetable

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['subject', 'teacher', 'semester', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

from finance.models import FeeStructure, StudentFee

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['course', 'semester', 'total_amount', 'due_date']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['semester'].queryset = Semester.objects.filter(course_id=course_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['semester'].queryset = self.instance.course.semesters.all()
        else:
            self.fields['semester'].queryset = Semester.objects.none()

class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['student', 'fee_structure', 'payable_amount', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'fee_structure': forms.Select(attrs={'class': 'form-select'}),
            'payable_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
