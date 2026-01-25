from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        notifications = Notification.objects.filter(
            receiver=request.user
        ).order_by("-created_at")[:10]

        return {
            "unread_count": unread_count,
            "notifications": notifications
        }

    return {}
