from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notifications"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True  # Null means broadcast to all users
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.user:
            return f"Notification for {self.user.name}: {self.message[:50]}"
        return f"Broadcast: {self.message[:50]}"
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class NotificationRead(models.Model):
    """Track read status of broadcast notifications"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='read_by')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_reads'
        unique_together = ('user', 'notification')
