from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/django/', admin.site.urls), # Renamed to avoid overlap with custom admin paths
    path('admin/', lambda request: redirect('admin_dashboard', permanent=True)),
    path('', include('users.urls')),
    path('', include('academics.urls')),
    path('', include('finance.urls')),
    path('', include('communication.urls')),
    path('', include('assessments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
