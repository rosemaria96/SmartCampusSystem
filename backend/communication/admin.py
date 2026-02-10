from django.contrib import admin
from .models import Notification, Announcement

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_audience', 'created_by', 'is_active', 'created_at']
    list_filter = ['target_audience', 'is_active', 'created_at']
    search_fields = ['title', 'content']
