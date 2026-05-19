"""
writer_management/models/logs.py

Writer-scoped audit and activity log models.

WHAT STAYS HERE
---------------
These models log events where the WRITER is the subject —
discipline actions on the writer, the writer's platform activity,
the writer's presence tracking, fraud detection.

WHAT MOVED OUT
--------------
The following order-scoped log models moved to order_actions app:
    WriterOrderRequestLog
    WriterOrderTakeLog
    WriterOrderCompletionLog
    WriterOrderReassignmentLog
    WriterOrderDeadlineExtensionLog
    WriterOrderReopenLog
    WriterOrderMessageLog
    WriterRatingLog  (→ reviews_system)

MODELS IN THIS FILE
-------------------
WriterActionLog       — discipline events (warning, strike, suspension, etc.)
WriterActivityLog     — writer's own platform actions (order accepted, etc.)
WriterActivityTracking — last seen / last login presence cache
WriterIPLog           — IP addresses used (fraud detection)
WriterProfileUpdateLog — profile field changes (audit)
WriterFileDownloadLog  — file access by writer (stays until central files app
                         provides its own download log)

WHAT WAS FIXED
--------------
- All __str__ using writer.user.username fixed to writer_id
- WriterActionLog.action choices expanded to cover all discipline events
  including strike and void operations
- WriterActivityLog.action_type choices updated — order-scoped actions
  removed, writer-identity actions added
- WriterActivityTracking.update_last_seen() kept as convenience method
  — only writes update_fields, no recursion risk
- WriterProfileUpdateLog.updated_fields changed from TextField to JSONField
  — structured field list is queryable; free text is not
- WriterFileDownloadLog.file FK changed to string reference
  (central files app may own this model in future)
- null=True removed from reason/description fields — use blank=True + default=""
"""

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class WriterActionLog(models.Model):
    """
    Append-only log of discipline actions taken against a writer.

    Created by DisciplineService and WriterWarningService after
    every discipline event. Never updated.

    This is the single audit trail for:
        - warnings issued / voided
        - strikes issued / voided
        - suspensions created / lifted
        - blacklist entries created / lifted
        - probation placed / ended
        - penalties applied

    Differs from WriterDisciplineState (cache) and the source
    discipline models — this is the permanent event log.
    """

    class ActionType(models.TextChoices):
        # Warnings
        WARNING_ISSUED   = "warning_issued",   "Warning Issued"
        WARNING_VOIDED   = "warning_voided",   "Warning Voided"
        # Strikes
        STRIKE_ISSUED    = "strike_issued",    "Strike Issued"
        STRIKE_VOIDED    = "strike_voided",    "Strike Voided"
        # Suspension
        SUSPENDED        = "suspended",        "Suspended"
        SUSPENSION_LIFTED = "suspension_lifted", "Suspension Lifted"
        # Blacklist
        BLACKLISTED      = "blacklisted",      "Blacklisted"
        BLACKLIST_LIFTED = "blacklist_lifted", "Blacklist Lifted"
        # Probation
        PROBATION_PLACED = "probation_placed", "Probation Placed"
        PROBATION_ENDED  = "probation_ended",  "Probation Ended"
        # Penalty
        PENALTY_APPLIED  = "penalty_applied",  "Penalty Applied"
        # Other
        DEACTIVATED      = "deactivated",      "Deactivated"
        REACTIVATED      = "reactivated",      "Reactivated"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_action_logs",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="action_logs",
    )
    action = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        db_index=True,
    )
    reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason or notes for this action.",
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_action_log_entries",
        help_text="Admin who performed the action. Null = system.",
    )
    # Reference to the source record (strike PK, warning PK, etc.)
    source_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "PK of the source discipline record. "
            "e.g. WriterStrike.pk, WriterWarning.pk, WriterSuspension.pk."
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Action Log"
        verbose_name_plural = "Writer Action Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["writer", "action", "created_at"],
                name="action_log_writer_action_idx",
            ),
            models.Index(
                fields=["website", "action", "created_at"],
                name="action_log_site_action_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterActionLog<{self.writer.id}> "
            f"[{self.action}] @ {self.created_at:%Y-%m-%d}"
        )


class WriterActivityLog(models.Model):
    """
    Log of actions performed BY a writer on the platform.

    High volume — append only. Used for:
        - Admin monitoring of writer engagement
        - Fraud detection (unusual activity patterns)
        - Support investigations

    Order-scoped actions (request, take, complete, reassign) are
    logged in order_actions app. This model logs writer-identity
    and platform-engagement actions only.
    """

    class ActionType(models.TextChoices):
        # Profile
        PROFILE_UPDATED      = "profile_updated",      "Profile Updated"
        BIO_UPDATED          = "bio_updated",           "Bio Updated"
        QUALIFICATIONS_UPDATED = "qualifications_updated", "Qualifications Updated"
        PEN_NAME_REQUESTED   = "pen_name_requested",   "Pen Name Change Requested"
        # Availability
        AVAILABILITY_SET     = "availability_set",     "Availability Set"
        WINDOW_DECLARED      = "window_declared",      "Unavailability Window Declared"
        WINDOW_ENDED         = "window_ended",         "Unavailability Window Ended"
        # Authentication
        LOGIN                = "login",                "Logged In"
        LOGOUT               = "logout",               "Logged Out"
        PASSWORD_CHANGED     = "password_changed",     "Password Changed"
        # Resources
        RESOURCE_VIEWED      = "resource_viewed",      "Resource Viewed"
        RESOURCE_DOWNLOADED  = "resource_downloaded",  "Resource Downloaded"
        # Other
        OTHER                = "other",                "Other"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_activity_logs",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action_type = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Additional context about the action.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Structured context. "
            "Schema varies by action_type. "
            "e.g. {'fields_changed': ['bio', 'timezone']} for profile updates."
        ),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address at time of action.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Activity Log"
        verbose_name_plural = "Writer Activity Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["writer", "action_type", "timestamp"],
                name="activity_log_writer_type_idx",
            ),
            models.Index(
                fields=["website", "timestamp"],
                name="activity_log_site_time_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterActivityLog<{self.writer.id}> "
            f"[{self.action_type}] @ {self.timestamp:%Y-%m-%d %H:%M}"
        )


class WriterActivityTracking(models.Model):
    """
    Presence cache for a writer.

    One row per writer. Updated on every login, logout,
    and periodic heartbeat.

    Differs from WriterStatus (ONLINE/OFFLINE/AWAY/BUSY):
        WriterStatus = real-time presence state
        WriterActivityTracking = last seen timestamps for admin reporting

    Used for:
        - Admin "last active" display on writer management dashboard
        - Detecting dormant writers for outreach
        - Fraud investigation (unusual login patterns)

    update_last_seen() is called by the heartbeat endpoint.
    update_last_login() is called by the login signal.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_activity_tracking",
    )
    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="activity_tracking",
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful login timestamp.",
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Last confirmed activity timestamp. "
            "Updated on heartbeat, API calls, and page loads."
        ),
    )
    total_login_count = models.PositiveIntegerField(
        default=0,
        help_text="Lifetime login count.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Activity Tracking"
        verbose_name_plural = "Writer Activity Tracking"
        indexes = [
            models.Index(
                fields=["last_seen"],
                name="writer_act_last_seen_idx",
            ),
        ]

    def __str__(self) -> str:
        last = self.last_seen.strftime("%Y-%m-%d %H:%M") if self.last_seen else "never"
        return f"WriterActivityTracking<{self.writer.id}> last_seen={last}"

    def update_last_seen(self) -> None:
        """Record current time as last_seen. Minimal write."""
        self.last_seen = now()
        self.save(update_fields=["last_seen", "updated_at"])

    def update_last_login(self) -> None:
        """Record login event."""
        self.last_login = now()
        self.last_seen = self.last_login
        self.total_login_count += 1
        self.save(update_fields=[
            "last_login", "last_seen",
            "total_login_count", "updated_at",
        ])


class WriterIPLog(models.Model):
    """
    Log of IP addresses used by a writer.

    Append-only. One entry per unique IP per writer per day
    (enforced at service layer — not DB constraint, to avoid
    blocking legitimate activity).

    Used for:
        - Detecting account sharing (multiple simultaneous IPs)
        - Fraud investigation (geographic anomalies)
        - Security audits

    Created by: login signal and heartbeat endpoint.
    Retention: configurable — old entries can be purged by
    a periodic cleanup task after N months.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_ip_logs",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="ip_logs",
    )
    ip_address = models.GenericIPAddressField(
        db_index=True,
        help_text="IP address observed.",
    )
    user_agent = models.TextField(
        blank=True,
        default="",
        help_text="Browser/client user agent string.",
    )
    logged_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer IP Log"
        verbose_name_plural = "Writer IP Logs"
        ordering = ["-logged_at"]
        indexes = [
            models.Index(
                fields=["writer", "ip_address"],
                name="ip_log_writer_ip_idx",
            ),
            models.Index(
                fields=["ip_address", "logged_at"],
                name="ip_log_ip_time_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterIPLog<{self.writer.id}> "
            f"{self.ip_address} @ {self.logged_at:%Y-%m-%d %H:%M}"
        )


class WriterProfileUpdateLog(models.Model):
    """
    Append-only log of changes to WriterProfile fields.

    Created by profile_service after every profile update.
    Stores the previous values so any change can be fully audited
    and reversed if needed.

    updated_fields is a JSON list of field names that changed.
    previous_values is a JSON dict of field → old value.

    Example:
        updated_fields: ["bio", "timezone"]
        previous_values: {
            "bio": "Old bio text here.",
            "timezone": "UTC"
        }
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_profile_update_logs",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="profile_update_logs",
    )
    updated_fields = models.JSONField(
        default=list,
        help_text="List of field names that were updated.",
    )
    previous_values = models.JSONField(
        default=dict,
        help_text=(
            "Previous values of the updated fields. "
            "Schema: {field_name: old_value}."
        ),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_profile_update_log_entries",
        help_text="Who made the change. Null = writer themselves.",
    )
    updated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Profile Update Log"
        verbose_name_plural = "Writer Profile Update Logs"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(
                fields=["writer", "updated_at"],
                name="profile_update_log_writer_idx",
            ),
        ]

    def __str__(self) -> str:
        fields = ", ".join(self.updated_fields) if self.updated_fields else "?"
        return (
            f"WriterProfileUpdateLog<{self.writer.id}> "
            f"[{fields}] @ {self.updated_at:%Y-%m-%d %H:%M}"
        )


class WriterFileDownloadLog(models.Model):
    """
    Log of file downloads accessed by a writer.

    References the central files app via a string FK.
    When the central files app is fully integrated, this model
    may be superseded by the files app's own download log.

    Until then this provides writer-scoped file access audit.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_file_download_logs",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="file_download_logs",
    )
    # String reference — central files app may use a different model name
    file_id = models.PositiveIntegerField(
        help_text="PK of the file in the central files app.",
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Snapshot of file name at download time.",
    )
    order_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Order the file belongs to.",
    )
    downloaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer File Download Log"
        verbose_name_plural = "Writer File Download Logs"
        ordering = ["-downloaded_at"]
        indexes = [
            models.Index(
                fields=["writer", "downloaded_at"],
                name="file_dl_log_writer_idx",
            ),
            models.Index(
                fields=["file_id", "downloaded_at"],
                name="file_dl_log_file_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterFileDownloadLog<{self.writer.id}> "
            f"{self.file_name} @ {self.downloaded_at:%Y-%m-%d %H:%M}"
        )
