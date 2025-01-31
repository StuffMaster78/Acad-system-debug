from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

User = get_user_model()

class AdminProfile(models.Model):
    """
    Stores Admin-specific details & permissions.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    can_manage_writers = models.BooleanField(default=True, help_text="Can manage writers.")
    can_manage_support = models.BooleanField(default=True, help_text="Can manage support staff.")
    can_manage_editors = models.BooleanField(default=True, help_text="Can manage editors.")
    can_suspend_users = models.BooleanField(default=True, help_text="Can suspend writers, editors, and clients.")
    can_handle_orders = models.BooleanField(default=True, help_text="Can manage order assignments and reassignments.")
    can_resolve_disputes = models.BooleanField(default=True, help_text="Can handle disputes between clients and writers.")
    can_manage_payouts = models.BooleanField(default=True, help_text="Can approve writer payouts.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Profile - {self.user.username}"

class AdminLog(models.Model):
    """
    Logs actions performed by Admins.
    """
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admin_logs")
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.timestamp}"

# Assign default permissions when an admin is created
def assign_admin_permissions(sender, instance, created, **kwargs):
    if created and instance.role == "admin":
        admin_group, _ = Group.objects.get_or_create(name="Admin")

        permissions = [
            "add_user", "change_user", "delete_user",
            "view_order", "change_order",
            "resolve_disputes"
        ]

        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            admin_group.permissions.add(permission)

        instance.groups.add(admin_group)

models.signals.post_save.connect(assign_admin_permissions, sender=User)