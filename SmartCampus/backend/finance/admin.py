from django.contrib import admin
from .models import FeeStructure, StudentFee, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'total_amount', 'due_date')
    list_filter = ('course', 'semester')
    date_hierarchy = 'due_date'


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'payable_amount', 'status', 'total_paid', 'remaining_amount')
    list_filter = ('status', 'fee_structure__course')
    search_fields = ('student__user__name', 'student__enrollment_number')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'student_fee', 'amount_paid', 'payment_method', 'payment_date')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('transaction_reference', 'student_fee__student__user__name')
    date_hierarchy = 'payment_date'
