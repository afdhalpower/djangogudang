from .models import ActivityLog

def log_activity(user, action, details=""):
    """
    Helper function to write to the ActivityLog.
    """
    if user and user.is_anonymous:
        user = None
    return ActivityLog.objects.create(user=user, action=action, details=details)
