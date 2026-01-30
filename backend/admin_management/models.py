from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
# from admin_management.managers import AdminManager 

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
    can_manage_editors = models.BooleanField(default=False)
    
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

        # if is_new:  # Assign permissions only on creation
        #     AdminManager.assign_permissions(self)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"
        ordering = ["-created_at"]  
    


    def __str__(self):
        return f"Admin Profile - {self.user.username}"


class BlacklistedUser(models.Model):
    """
    Stores users who are blacklisted from the system.
    """
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="blacklisted_users",
        help_text="Website to which the blacklisted user belongs."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blacklisted_user",
        null=True,
        blank=True,
        help_text="User object of the blacklisted user."
    )
    # Email is unique to prevent multiple entries for the same email
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
    """Stores requests for admin promotions.
    Admins can request to be promoted to superadmin.
    Superadmins can approve or reject these requests.
    """
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="promotion_requests",
        help_text="Website for which the promotion request is made."
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="promotion_requests",
        help_text="Admin requesting promotion."
    )
    requested_role = models.CharField(
        max_length=50,
        default="superadmin",
        help_text="Role being requested for promotion."
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ],
        default="pending",
        help_text="Current status of the promotion request."
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for requesting promotion."
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the request was made."
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_promotion_requests",
        help_text="Admin who approved the request."
    )
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_promotion_requests",
        help_text="Admin who rejected the request."
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request was approved."
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the request was rejected."
    )

    def save(self, *args, **kwargs):
        """Ensure requested_by is a valid admin."""
        if not self.requested_by.admin_profile.is_active:
            raise ValueError("Cannot request promotion for an inactive admin.")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Admin Promotion Request"
        verbose_name_plural = "Admin Promotion Requests"
        ordering = ["-requested_at"]  # Newest requests first


    def __str__(self):
        return f"Promotion Request by {self.requested_by.username}"
    

class AdminActivityLog(models.Model):
    """
    Logs significant actions taken by admins for auditing purposes.
    """
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="admin_activity_logs",
        help_text="Admin who performed the action."
    )
    action = models.CharField(
        max_length=255,
        help_text="Description of the action performed."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action} at {self.timestamp}"

    class Meta:
        verbose_name = "Admin Activity Log"
        verbose_name_plural = "Admin Activity Logs"
        ordering = ["-timestamp"]  # Newest logs first
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["admin", "timestamp"]),
        ]