from .models import ActivityLog


def log_activity(user, action, details=None, request=None):
    ActivityLog.objects.create(
        user=user,
        action=action,
        details=details or {},
        ip_address=request.META.get("REMOTE_ADDR") if request else None,
    )
