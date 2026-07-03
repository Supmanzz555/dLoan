from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=[("admin", "Admin"), ("reviewer", "Reviewer"), ("officer", "Officer")],
        default="officer",
    )
    preferred_language = models.CharField(max_length=5, default="en")
    is_super_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_user"


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_log"
        ordering = ["-created_at"]
