from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/django/', admin.site.urls), # Renamed to avoid overlap with custom admin paths
    path('admin/', lambda request: redirect('admin_dashboard', permanent=True)),
    path('', include('users.urls')),
    path('', include('academics.urls')),
    path('', include('finance.urls')),
    path('', include('communication.urls')),
    path('', include('assessments.urls')),
]

