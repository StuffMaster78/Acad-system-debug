from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
import random
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings

User = get_user_model()

class SuperadminProfile(models.Model):
    """
    Profile for Superadmins. Grants full system control.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="superadmin_profile")

    # Superadmin Permissions
    can_manage_users = models.BooleanField(default=True, help_text="Can add/edit/suspend/delete users.")
    can_manage_payments = models.BooleanField(default=True, help_text="Can oversee all payments.")
    can_view_reports = models.BooleanField(default=True, help_text="Can view financial and operational reports.")
    can_modify_settings = models.BooleanField(default=True, help_text="Can modify system-wide settings.")
    can_promote_users = models.BooleanField(default=True, help_text="Can promote/demote users.")
    can_suspend_users = models.BooleanField(default=True, help_text="Can suspend or reactivate users.")
    can_blacklist_users = models.BooleanField(default=True, help_text="Can blacklist and unblacklist emails.")
    can_resolve_disputes = models.BooleanField(default=True, help_text="Can resolve order disputes.")
    can_override_payments = models.BooleanField(default=True, help_text="Can manually adjust payments.")
    can_track_admins = models.BooleanField(default=True, help_text="Can track all admin actions.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Superadmin Profile - {self.user.username}"

    class Meta:
        verbose_name = "Superadmin Profile"
        verbose_name_plural = "Superadmin Profiles"


class SuperadminLog(models.Model):
    """
    Logs actions performed by Superadmins for security tracking.
    """
    superadmin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="superadmin_logs")
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.superadmin.username} - {self.action} - {self.timestamp}"
