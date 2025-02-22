from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from websites.models import Website
from orders.models import Order

User = get_user_model()


class EditorProfile(models.Model):
    """
    Profile for editors, managing their assignments and activities.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="editor_profile",
        limit_choices_to={"role": "editor"},
        help_text="The user associated with this editor profile."
    )
    name = models.CharField(
        max_length=255,
        help_text="Full name of the editor."
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique editor registration ID (e.g., Editor #12345)."
    )
    email = models.EmailField(unique=True, help_text="Editor’s email address.")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Editor’s phone number."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="editors",
        help_text="The website the editor is associated with."
    )
    last_logged_in = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The last time the editor logged in."
    )
    writers_assigned = models.ManyToManyField(
        'writer_management.WriterProfile',
        blank=True,
        related_name="editors",
        help_text="Writers assigned to this editor."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the editor is active."
    )
    orders_reviewed = models.PositiveIntegerField(
        default=0,
        help_text="Total number of orders reviewed by the editor."
    )

    def __str__(self):
        return f"{self.name} (Editor Profile: {self.user.username}, {self.registration_id})"


class EditorTaskAssignment(models.Model):
    """
    Tracks task assignments to editors, including fallback tracking.
    """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="editor_assignment",
        help_text="The order being assigned for review."
    )
    assigned_editor = models.ForeignKey(
        EditorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="The primary editor assigned to review this task."
    )
    fallback_editors = models.ManyToManyField(
        EditorProfile,
        blank=True,
        related_name="fallback_tasks",
        help_text="Fallback editors who can access this task."
    )
    review_status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("in_review", "In Review"),
            ("completed", "Completed"),
        ),
        default="pending",
        help_text="The current review status of the task."
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the task was reviewed."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or feedback from the editor."
    )

    def __str__(self):
        return f"Task {self.order.id} assigned to {self.assigned_editor.name if self.assigned_editor else 'Unassigned'}"


class EditorActionLog(models.Model):
    """
    Logs actions performed by editors.
    """
    editor = models.ForeignKey(
        EditorProfile,
        on_delete=models.CASCADE,
        related_name="action_logs",
        help_text="The editor performing the action."
    )
    action = models.CharField(
        max_length=255,
        help_text="Description of the action performed (e.g., 'Reviewed Order')."
    )
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editor_actions",
        help_text="The order associated with this action."
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the action.")

    def __str__(self):
        return f"Action by {self.editor.name}: {self.action} at {self.timestamp}"


class EditorPerformance(models.Model):
    """
    Tracks editor performance metrics.
    """
    editor = models.OneToOneField(
        EditorProfile,
        on_delete=models.CASCADE,
        related_name="performance",
        help_text="The editor whose performance is being tracked."
    )
    average_review_time = models.DurationField(
        blank=True,
        null=True,
        help_text="Average time taken to review tasks."
    )
    total_orders_reviewed = models.PositiveIntegerField(
        default=0,
        help_text="Total number of orders reviewed by the editor."
    )
    late_reviews = models.PositiveIntegerField(
        default=0,
        help_text="Number of reviews completed past the deadline."
    )

    def __str__(self):
        return f"Performance for {self.editor.name}"


class EditorNotification(models.Model):
    """
    Tracks notifications sent to editors.
    """
    editor = models.ForeignKey(
        EditorProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The editor receiving the notification."
    )
    message = models.TextField(help_text="Notification message.")
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editor_notifications",
        help_text="Related order, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the notification.")
    is_read = models.BooleanField(default=False, help_text="Indicates whether the notification has been read.")

    def __str__(self):
        return f"Notification for {self.editor.name}: {self.message[:30]}"