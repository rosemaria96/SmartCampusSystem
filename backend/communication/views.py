from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, NotificationRead

@login_required
def admin_noti(request):
    if not request.user.role == 'ADMIN':
        return redirect('login')
    # Admin sees all sent notifications
    notifications = Notification.objects.all().order_by('-created_at')[:50]
    return render(request, 'admin/admin_noti.html', {'notifications': notifications})

@login_required
def student_notifications(request):
    if not request.user.role == 'STUDENT':
        return redirect('login')
    return get_user_notifications(request, 'student/student_notifications.html')

@login_required
def teacher_notifications(request):
    if not request.user.role == 'TEACHER':
        return redirect('login')
    return get_user_notifications(request, 'teacher/teacher_notifications.html')

def get_user_notifications(request, template_name):
    # Get direct notifications
    direct_notis = Notification.objects.filter(user=request.user)
    # Get broadcast notifications
    broadcast_notis = Notification.objects.filter(user__isnull=True)
    
    # Combine and exclude read ones
    all_notis = (direct_notis | broadcast_notis).order_by('-created_at')
    
    # Filter out read broadcast notifications
    read_ids = NotificationRead.objects.filter(user=request.user).values_list('notification_id', flat=True)
    
    unread_notis = []
    for noti in all_notis:
        if noti.is_read: # Direct notification read status
            continue
        if noti.id in read_ids: # Broadcast notification read status
            continue
        unread_notis.append(noti)
        
    return render(request, template_name, {'notifications': unread_notis})

@login_required
def mark_notification_read(request, pk):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=pk)
        
        if notification.user:
            # Direct notification
            if notification.user == request.user:
                notification.is_read = True
                notification.save()
        else:
            # Broadcast notification
            NotificationRead.objects.get_or_create(user=request.user, notification=notification)
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
