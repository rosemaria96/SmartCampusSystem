from django.db import models
from django.conf import settings
from academics.models import Course, Semester, Student


class FeeStructure(models.Model):
    """Fee structure for courses and semesters"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_structures')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='fee_structures')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    
    def __str__(self):
        return f"{self.course.course_name} - Semester {self.semester.semester_number} - ₹{self.total_amount}"
    
    class Meta:
        db_table = 'fee_structure'
        unique_together = ('course', 'semester')


class StudentFee(models.Model):
    """Individual student fee records"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_fees')
    payable_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"{self.student.user.name} - {self.fee_structure.course.course_name} - {self.status}"
    
    class Meta:
        db_table = 'student_fees'
        unique_together = ('student', 'fee_structure')
    
    @property
    def total_paid(self):
        return sum(payment.amount_paid for payment in self.payments.all())
    
    @property
    def remaining_amount(self):
        return self.payable_amount - self.total_paid


class Payment(models.Model):
    """Payment transactions"""
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_reference = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_reference} - ₹{self.amount_paid}"
    
    class Meta:
        db_table = 'payments'
