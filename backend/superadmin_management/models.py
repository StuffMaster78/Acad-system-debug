"""
superadmin_management/models.py

Platform governance models.

OWNERSHIP
---------
SuperadminProfile   — permission store for superadmin users
SuperadminLog       — high-fidelity audit of all superadmin actions
Appeal              — escalation gateway for all user roles
Blacklist           — email/IP/user platform blacklist

EXPLICITLY NOT OWNED HERE
--------------------------
Writer discipline (suspend/blacklist/probation) → writer_management
Client suspension                               → client_management
Editor suspension                               → editor_management
Order management                                → orders app
Payment overrides                               → writer_compensation

DEPRECATION NOTES
-----------------
Probation   — removed. For writers use writer_management.WriterProbation.
              For non-writers use User.is_on_probation flag directly.
UserActionLog — removed. Consolidated into SuperadminLog.
              SuperadminLog already captures all superadmin actions with
              more structure.
"""

from django.conf import settings
from django.db import models
from django.utils.timezone import now

User = settings.AUTH_USER_MODEL


class SuperadminProfile(models.Model):
    """
    Permission store for superadmin users.

    All permissions default True — superadmins have full access
    unless a specific capability is revoked.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="superadmin_profile",
    )

    can_manage_users     = models.BooleanField(default=True)
    can_manage_payments  = models.BooleanField(default=True)
    can_view_reports     = models.BooleanField(default=True)
    can_modify_settings  = models.BooleanField(default=True)
    can_promote_users    = models.BooleanField(default=True)
    can_suspend_users    = models.BooleanField(default=True)
    can_blacklist_users  = models.BooleanField(default=True)
    can_resolve_disputes = models.BooleanField(default=True)
    can_override_payments = models.BooleanField(default=True)
    can_track_admins     = models.BooleanField(default=True)
    can_impersonate_users = models.BooleanField(
        default=False,
        help_text="Can use security app impersonation. Requires separate approval.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_permission(self, perm: str) -> bool:
        return getattr(self, perm, False)

    def __str__(self) -> str:
        return f"SuperadminProfile — {self.user}"

    class Meta:
        verbose_name = "Superadmin Profile"
        verbose_name_plural = "Superadmin Profiles"


class SuperadminLog(models.Model):
    """
    High-fidelity audit log of all superadmin actions.

    Written by SuperadminService after every governance action.
    Immutable after creation — do not update existing rows.

    NOTE: For business-level audit (orders, payments, discipline)
    use audit_logging.AuditService.record() in addition to this log.
    This log is for the superadmin dashboard and governance oversight.
    audit_logging is for compliance and legal hold.
    """

    class ActionType(models.TextChoices):
        USER_MANAGE        = "user_manage",        "User Management"
        PAYMENT            = "payment",            "Payment Override"
        REPORT_ACCESS      = "report_access",      "Report Access"
        SETTINGS_CHANGE    = "settings_change",    "Settings Modification"
        PROMOTION          = "promotion",          "User Promotion / Demotion"
        SUSPENSION         = "suspension",         "User Suspension"
        REACTIVATION       = "reactivation",       "User Reactivation"
        PROBATION          = "probation",          "User Probation"
        BLACKLIST          = "blacklist",          "User Blacklisting"
        BLACKLIST_LIFTED   = "blacklist_lifted",   "Blacklist Lifted"
        DISPUTE_RESOLUTION = "dispute_resolution", "Dispute Resolution"
        APPEAL_APPROVED    = "appeal_approved",    "Appeal Approved"
        APPEAL_REJECTED    = "appeal_rejected",    "Appeal Rejected"
        ADMIN_TRACKING     = "admin_tracking",     "Admin Tracking"
        OVERRIDE           = "override",           "System Override"
        IMPERSONATION      = "impersonation",      "User Impersonation"

    superadmin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="superadmin_logs",
    )
    action_type = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        db_index=True,
    )
    action = models.CharField(max_length=255)
    action_details = models.TextField(blank=True, default="")
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superadmin_log_targets",
        help_text="User the action was performed on, if applicable.",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superadmin_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self) -> str:
        return (
            f"{self.superadmin} — "
            f"{self.get_action_type_display()} — "
            f"{self.timestamp:%Y-%m-%d %H:%M}"
        )

    class Meta:
        verbose_name = "Superadmin Log"
        verbose_name_plural = "Superadmin Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["superadmin", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
            models.Index(fields=["target_user", "timestamp"]),
        ]


class Appeal(models.Model):
    """
    Escalation gateway for probation, blacklist, and suspension appeals.

    Any user role can submit an appeal.
    SuperadminService.approve_appeal() routes the approval to the
    correct domain service based on the user's role.

    Writers  → writer_management.DisciplineService
    Others   → User flags directly
    """

    class AppealType(models.TextChoices):
        PROBATION  = "probation",  "Probation"
        BLACKLIST  = "blacklist",  "Blacklist"
        SUSPENSION = "suspension", "Suspension"

    class Status(models.TextChoices):
        PENDING  = "pending",  "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="appeals",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appeals",
    )
    appeal_type = models.CharField(
        max_length=10,
        choices=AppealType.choices,
        db_index=True,
    )
    reason = models.TextField(
        help_text="Why should this decision be reconsidered?",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appeal_reviews",
    )
    review_notes = models.TextField(
        blank=True,
        default="",
        help_text="Internal notes from the reviewing superadmin.",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return (
            f"{self.user} — "
            f"{self.get_appeal_type_display()} — "
            f"{self.get_status_display()}"
        )

    class Meta:
        verbose_name = "Appeal"
        verbose_name_plural = "Appeals"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["status", "submitted_at"]),
            models.Index(fields=["user", "status"]),
        ]


class Blacklist(models.Model):
    """
    Platform-level blacklist for email addresses, IP addresses,
    and non-writer user accounts.

    For writer-specific discipline blacklisting use
    writer_management.DisciplineService.blacklist() which creates
    a writer_management.WriterBlacklist source record and updates
    WriterDisciplineState.

    This model covers:
        email   — blocks registration and login with this email
        ip      — blocks all requests from this IP
        user    — blocks non-writer user accounts (clients, editors, support)

    For writer users, this model ALSO creates a record so that
    email/IP lookups work platform-wide. The canonical discipline
    record lives in writer_management.WriterBlacklist.
    """

    class BlacklistType(models.TextChoices):
        USER  = "user",  "User Account"
        EMAIL = "email", "Email Address"
        IP    = "ip",    "IP Address"

    blacklist_type = models.CharField(
        max_length=10,
        choices=BlacklistType.choices,
        default=BlacklistType.USER,
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_records",
    )
    email = models.EmailField(
        null=True,
        blank=True,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
    )
    reason = models.TextField()
    blacklisted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_entries_created",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="blacklist_entries",
        null=True,
        blank=True,
        help_text="Null = platform-wide blacklist.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    date_blacklisted = models.DateTimeField(auto_now_add=True)
    lifted_at = models.DateTimeField(null=True, blank=True)
    lift_reason = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        target = (
            self.user or
            self.email or
            self.ip_address or
            "unknown"
        )
        return f"Blacklist({self.blacklist_type}): {target}"

    class Meta:
        verbose_name = "Blacklist Record"
        verbose_name_plural = "Blacklist Records"
        indexes = [
            models.Index(fields=["blacklist_type", "is_active"]),
            models.Index(fields=["email"]),
            models.Index(fields=["ip_address"]),
        ]