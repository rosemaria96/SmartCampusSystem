from django.contrib import admin
from .models import FeePayment, Transaction

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'semester', 'total_amount', 'paid_amount', 'status', 'due_date']
    list_filter = ['status', 'academic_year', 'semester']
    search_fields = ['student__username', 'student__email']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'fee_payment', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['transaction_id', 'fee_payment__student__username']
