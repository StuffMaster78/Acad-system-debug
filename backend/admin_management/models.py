"""
admin_management/models.py — fixes applied:
1. AdminActivityLog: added details field (views were writing to it, field didn't exist)
2. BlacklistedUser: marked for deprecation — use superadmin_management.Blacklist
3. Everything else preserved exactly as-is
"""

from django.db import models
from django.conf import settings
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


class AdminProfile(models.Model):
    """
    Granular permission store for admin users.
    Admins have attenuated authority relative to superadmins.
    can_blacklist_users defaults False — superadmin-only action.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        unique=True,
        related_name="admin_profile",
    )
    is_superadmin = models.BooleanField(
        default=False,
        help_text="Unrestricted access flag. Set by superadmin only.",
    )

    # Capabilities
    can_manage_users = models.BooleanField(default=True)
    can_suspend_users = models.BooleanField(default=True)
    can_put_on_probation = models.BooleanField(default=True)
    can_handle_orders = models.BooleanField(default=True)
    can_resolve_disputes = models.BooleanField(default=True)
    can_manage_payouts = models.BooleanField(default=True)
    can_manage_financials = models.BooleanField(default=True)
    can_manage_tickets = models.BooleanField(default=True)
    can_view_reports = models.BooleanField(default=True)
    can_blacklist_users = models.BooleanField(
        default=False,
        help_text="Superadmin-granted only.",
    )
    can_manage_writers = models.BooleanField(default=False)
    can_manage_clients = models.BooleanField(default=False)
    can_manage_editors = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    last_login = models.DateTimeField(null=True, blank=True)
    last_action = models.CharField(max_length=255, blank=True, null=True)
    action_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_last_action(self, action: str) -> None:
        self.last_login = now()
        self.last_action = action
        self.action_count += 1
        self.save(update_fields=[
            "last_login", "last_action", "action_count"
        ])

    def __str__(self) -> str:
        return f"AdminProfile — {self.user}"

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        ordering = ["-created_at"]


class BlacklistedUser(models.Model):
    """
    DEPRECATED — use superadmin_management.Blacklist instead.

    Kept for backwards compatibility during migration.
    New code must not write to this model.
    Existing data will be migrated to superadmin_management.Blacklist.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="blacklisted_users",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blacklisted_user",
        null=True,
        blank=True,
    )
    email = models.EmailField(unique=True)
    blacklisted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blacklisted_users",
    )
    reason = models.TextField(blank=True, null=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        by = self.blacklisted_by.username if self.blacklisted_by else "System"
        return f"{self.email} — blacklisted by {by}"

    class Meta:
        verbose_name = "Blacklisted User (DEPRECATED)"
        verbose_name_plural = "Blacklisted Users (DEPRECATED)"


class AdminPromotionRequest(models.Model):
    """Promotion request from admin to superadmin."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="promotion_requests",
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="promotion_requests",
    )
    requested_role = models.CharField(max_length=50, default="superadmin")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_promotion_requests",
    )
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="rejected_promotion_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"PromotionRequest — {self.requested_by} ({self.status})"

    class Meta:
        verbose_name = "Admin Promotion Request"
        verbose_name_plural = "Admin Promotion Requests"
        ordering = ["-requested_at"]


class AdminActivityLog(models.Model):
    """
    Admin action audit log.

    FIX: Added `details` field — views were writing `details=...`
    but the field did not exist on the model, causing TypeError
    at runtime on every log creation.
    """

    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_activity_logs",
    )
    action = models.CharField(max_length=255)
    details = models.TextField(
        blank=True,
        default="",
        help_text="Additional context for the action.",
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_log_targets",
        help_text="User the action was performed on, if applicable.",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_activity_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.admin} — {self.action} @ {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        verbose_name = "Admin Activity Log"
        verbose_name_plural = "Admin Activity Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["admin", "timestamp"]),
            models.Index(fields=["target_user", "timestamp"]),
        ]


class StaffWebsiteAssignment(models.Model):
    """
    M2M bridge: staff users ↔ websites.

    Staff (admin, support, editor, superadmin) serve multiple websites.
    This model tracks which websites each staff member is assigned to.
    Used by NotificationService.notify_staff() to resolve recipients.
    """

    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="website_assignments",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="staff_assignments",
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_assignments_made",
    )

    def __str__(self) -> str:
        state = "active" if self.is_active else "inactive"
        return f"{self.staff_member} → {self.website} ({state})"

    class Meta:
        unique_together = ("staff_member", "website")
        ordering = ["-assigned_at"]