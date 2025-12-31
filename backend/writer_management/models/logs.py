from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.file_management import WriterFile
from writer_management.models.profile import WriterProfile
from orders.models import Order

from django.contrib.auth import get_user_model

User = get_user_model()

class WriterActionLog(models.Model):
    """
    Logs actions taken on writers (e.g., warnings, probation, suspension).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_action_log"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="action_logs",
        help_text="The writer this action applies to."
    )
    action = models.CharField(
        max_length=20,
        choices=(
            ("warning", "Warning"),
            ("probation", "Probation"),
            ("suspension", "Suspension"),
            ("deactivation", "Deactivation"),
        ),
        help_text="The type of action taken."
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for taking this action."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Action: {self.action} for {self.writer.user.username}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['writer', 'created_at']),
            models.Index(fields=['website', 'action', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

class WriterActivityLog(models.Model):
    """
    Tracks every action performed by a writer.
    """
    ACTION_TYPES = [
        ("Order Accepted", "Order Accepted"),
        ("Order Submitted", "Order Submitted"),
        ("File Uploaded", "File Uploaded"),
        ("Message Sent", "Message Sent"),
        ("Request Made", "Request Made"),
        ("Reopened Order", "Reopened Order"),
        ("Deadline Extension Requested", "Deadline Extension Requested"),
        ("Reassignment Requested", "Reassignment Requested"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="activity_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="activity_logs"
    )
    action_type = models.CharField(
        max_length=50, choices=ACTION_TYPES,
        help_text="Type of action performed."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Additional details about the action."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the action was recorded."
    )

    def __str__(self):
        return f"Activity: {self.writer.user.username} - {self.action_type} ({self.timestamp})"
    

class WriterActivityTracking(models.Model):
    """
    Tracks when a writer was last active.
    Helps admins monitor writer activity.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.OneToOneField(
        WriterProfile, on_delete=models.CASCADE,
        related_name="activity_tracking"
    )
    last_login = models.DateTimeField(
        blank=True, null=True,
        help_text="Last time the writer logged in."
    )
    last_seen = models.DateTimeField(
        blank=True, null=True,
        help_text="Last time the writer was active."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_last_seen(self):
        self.last_seen = now()
        self.save()

    def __str__(self):
        return f"Activity Tracking: {self.writer.user.username} (Last Seen: {self.last_seen})"


class WriterIPLog(models.Model):
    """
    Logs multiple IP addresses used by a writer.
    Helps detect account sharing or fraud.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="ip_logs"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address used by the writer."
    )
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IP Log: {self.writer.user.username} - {self.ip_address} ({self.logged_at})"
    
class WriterOrderRequestLog(models.Model):
    """
    Logs all writer order requests for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_request_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_request_logs"
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was made."
    )
    approved = models.BooleanField(
        default=False, help_text="Has the request been approved?"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="order_request_review_logs"
    )

    def __str__(self):
        return f"Request Log: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"
    
    class Meta:
        verbose_name = "Writer Order Request Log"
        verbose_name_plural = "Writer Order Request Logs"
        ordering = ['-requested_at']

class WriterOrderTakeLog(models.Model):
    """
    Logs all writer order takes for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_take_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_take_logs"
    )
    taken_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the order was taken."
    )

    def __str__(self):
        return f"Take Log: {self.writer.user.username} - Order {self.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Take Log"
        verbose_name_plural = "Writer Order Take Logs"
        ordering = ['-taken_at']    

class WriterOrderCompletionLog(models.Model):
    """
    Logs all writer order completions for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_completion_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_completion_logs"
    )
    completed_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the order was completed."
    )

    def __str__(self):
        return f"Completion Log: {self.writer.user.username} - Order {self.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Completion Log"
        verbose_name_plural = "Writer Order Completion Logs"
        ordering = ['-completed_at']


class WriterOrderReassignmentLog(models.Model):
    """
    Logs all writer order reassignments for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_reassignment_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_reassignment_logs"
    )
    reassigned_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the order was reassigned."
    )

    def __str__(self):
        return f"Reassignment Log: {self.writer.user.username} - Order {self.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Reassignment Log"
        verbose_name_plural = "Writer Order Reassignment Logs"
        ordering = ['-reassigned_at']

class WriterOrderDeadlineExtensionLog(models.Model):
    """
    Logs all writer order deadline extensions for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_deadline_extension_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_deadline_extension_logs"
    )
    extension_requested_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the deadline extension was requested."
    )
    new_deadline = models.DateTimeField(
        help_text="New deadline after extension."
    )

    def __str__(self):
        return f"Deadline Extension Log: {self.writer.user.username} - Order {self.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Deadline Extension Log"
        verbose_name_plural = "Writer Order Deadline Extension Logs"
        ordering = ['-extension_requested_at']


class WriterOrderReopenLog(models.Model):
    """
    Logs all writer order reopen requests for auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_reopen_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_reopen_logs"
    )
    reopened_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the order was reopened."
    )

    def __str__(self):
        return f"Reopen Log: {self.writer.user.username} - Order {self.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Reopen Log"
        verbose_name_plural = "Writer Order Reopen Logs"
        ordering = ['-reopened_at']


class WriterOrderMessageLog(models.Model):
    """
    Logs all messages sent by writers regarding orders.
    Helps track communication and accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_message_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_message_logs"
    )
    message_content = models.TextField(
        help_text="Content of the message sent by the writer."
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message Log: {self.writer.user.username} - Order {self.order.id} ({self.sent_at})"
    

    class Meta:
        verbose_name = "Writer Order Message Log"
        verbose_name_plural = "Writer Order Message Logs"
        ordering = ['-sent_at'] 


class WriterRatingLog(models.Model):
    """
    Logs all writer ratings given by clients.
    Helps track writer performance over time.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="rating_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="rating_logs"
    )
    rating = models.PositiveIntegerField(
        help_text="Rating given to the writer (1-5)."
    )
    feedback = models.TextField(
        blank=True, null=True,
        help_text="Client feedback for the rating."
    )
    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating Log: {self.writer.user.username} - Order {self.order.id} ({self.rating})"
    
    class Meta:
        verbose_name = "Writer Rating Log"
        verbose_name_plural = "Writer Rating Logs"
        ordering = ['-rated_at']    


class WriterProfileUpdateLog(models.Model):
    """
    Logs updates made to writer profiles.
    Useful for tracking changes and auditing.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="profile_update_logs"
    )
    updated_fields = models.TextField(
        help_text="Fields that were updated in the profile."
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="profile_update_logs"
    )

    def __str__(self):
        return f"Profile Update Log: {self.writer.user.username} ({self.updated_at})"
    
    class Meta:
        verbose_name = "Writer Profile Update Log"
        verbose_name_plural = "Writer Profile Update Logs"
        ordering = ['-updated_at']


class WriterFileDownloadLog(models.Model):
    """
    Logs all file downloads by writers.
    Helps track file access and accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="file_download_logs"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_download_logs"
    )
    file = models.ForeignKey(
        WriterFile, on_delete=models.CASCADE,
        related_name="file_download_name_log"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Download Log: {self.writer.user.username} - File {self.file.id} ({self.downloaded_at})"

    class Meta:
        verbose_name = "Writer File Download Log"
        verbose_name_plural = "Writer File Download Logs"
        ordering = ['-downloaded_at']