from accounts.models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        # Fetch notifications for the logged-in user (doctor)
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        
        # Count the number of unread notifications
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

        return {
            'notifications': notifications,
            'unread_count': unread_count,
        }
    return {}  # If the user is not authenticated, return an empty context
