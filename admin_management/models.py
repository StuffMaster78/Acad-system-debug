import json
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from admin_management.managers import AdminManager 
from django.contrib.auth.backends import BaseBackend

User = get_user_model()

class AdminProfile(models.Model):
    """
    Stores Admin-specific details & permissions.
    Admins manage everything except superadmin-only tasks.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        unique=True,
        related_name="admin_profile"
    )
    
    is_superadmin = models.BooleanField(
        default=False,
        help_text="Has unrestricted access (Superadmin Only)."
    )

    # Admin Capabilities - Everything except Superadmin-specific roles
    # Permissions
    can_manage_users = models.BooleanField(
        default=True,
        help_text="Can manage writers, editors, clients, and support staff."
    )
    can_suspend_users = models.BooleanField(
        default=True,
        help_text="Can suspend users (except superadmins)."
    )
    can_put_on_probation = models.BooleanField(
        default=True,
        help_text="Can place users on probation."
    )
    can_handle_orders = models.BooleanField(
        default=True,
        help_text="Can manage order assignments, edits, and cancellations."
    )
    can_resolve_disputes = models.BooleanField(
        default=True,
        help_text="Can handle disputes between clients and writers."
    )
    can_manage_payouts = models.BooleanField(
        default=True,
        help_text="Can approve writer payouts and financial transactions.")
    can_manage_financials = models.BooleanField(
        default=True,
        help_text="Can manage payments, refunds, and discounts."
    )
    can_manage_tickets = models.BooleanField(
        default=True,
        help_text="Can handle support tickets and client inquiries."
    )
    can_view_reports = models.BooleanField(
        default=True,
        help_text="Can access reporting and analytics."
    )
    can_blacklist_users = models.BooleanField(
        default=False,
        help_text="Can blacklist users (Superadmins only)."
    )
    can_manage_writers = models.BooleanField(default=False)
    can_manage_clients = models.BooleanField(default=False)

    is_active = models.BooleanField(
        default=True, 
        help_text="Soft delete instead of removing admin."
    )

    # Activity Tracking
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last login timestamp."
    )
    last_action = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Last performed action."
    )
    action_count = models.IntegerField(
        default=0,
        help_text="Total actions taken by the admin."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_manage_writers(self, obj):
        return obj.can_manage_writers 

    def update_last_action(self, action):
        """Updates last activity & action count for admin."""
        self.last_login = now()
        self.last_action = action
        self.action_count += 1
        self.save(update_fields=["last_login", "last_action", "action_count"])

    def save(self, *args, **kwargs):
        """Assign permissions only when an AdminProfile is first created."""
        is_new = self._state.adding  # Check if object is being created

        super().save(*args, **kwargs)

        if is_new:  # Assign permissions only on creation
            AdminManager.assign_permissions(self)


    def __str__(self):
        return f"Admin Profile - {self.user.username}"

class AdminActivityLog(models.Model):
    """
    Logs actions performed by Admins.
    """
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_logs"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="admin_actions_logs",
        help_text="User affected by the action"
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="If action is related to an order."
    )
    action = models.CharField(max_length=255)
    details = models.TextField(
        blank=True,
        null=True,
        help_text="Additional context about the action."
    )
    
    # Audit Fields - What Changed
    old_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous data before change."
    )
    new_data = models.JSONField(
        null=True,
        blank=True,
        help_text="New data after change."
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Ensure old/new data is stored in readable format."""
        if isinstance(self.old_data, dict):
            self.old_data = json.dumps(self.old_data, indent=4)
        if isinstance(self.new_data, dict):
            self.new_data = json.dumps(self.new_data, indent=4)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.timestamp}"
    

class BlacklistedUser(models.Model):
    """
    Stores users who are blacklisted from the system.
    """
    email = models.EmailField(unique=True, help_text="Email of the blacklisted user.")
    blacklisted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blacklisted_users"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for blacklisting."
    )
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - Blacklisted by {self.blacklisted_by.username if self.blacklisted_by else 'System'}"

    class Meta:
        verbose_name = "Blacklisted User"
        verbose_name_plural = "Blacklisted Users"

class AdminPromotionRequest(models.Model):
    # define your fields here
    request_date = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # other fields as necessary

    def __str__(self):
        return f"Promotion Request by {self.requested_by.username}"
