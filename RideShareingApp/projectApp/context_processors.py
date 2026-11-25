from projectApp.models import Notification

def user_notifications(request):
    if request.user.is_authenticated:
        # 1. Get all notifications for the user ordered by newest first
        notifications_qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        
        # 2. Calculate unread count from the un-sliced query
        unread_count = notifications_qs.filter(is_read=False).count()
        
        # 3. Take the slice (top 10) for display purposes last
        notifications = notifications_qs[:10]
        
        return {
            'user_notifications': notifications,
            'unread_notifications_count': unread_count
        }
    return {}