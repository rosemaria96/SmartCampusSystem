from django.urls import path
from . import views
from academics import student_views

urlpatterns = [
    path('admin/fee-payment/', views.admin_fee_payment, name='admin_fee_payment'),
    path('student/fee-payment/', student_views.student_fee_payment, name='student_fee_payment_legacy'),
]
