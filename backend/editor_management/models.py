from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from orders.models import Order

User = settings.AUTH_USER_MODEL 


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
    email = models.EmailField(
        unique=True,
        help_text="Editor's email address."
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Editor's phone number."
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
    
    # Editor preferences/settings
    can_self_assign = models.BooleanField(
        default=True,
        help_text="Whether editor can claim orders themselves."
    )
    max_concurrent_tasks = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of concurrent editing tasks."
    )
    
    # Expertise areas (optional - for auto-assignment)
    expertise_subjects = models.ManyToManyField(
        'order_configs.Subject',
        blank=True,
        related_name="expert_editors",
        help_text="Subjects this editor specializes in."
    )
    expertise_paper_types = models.ManyToManyField(
        'order_configs.PaperType',
        blank=True,
        related_name="expert_editors",
        help_text="Paper types this editor specializes in."
    )

    def __str__(self):
        return f"{self.name} (Editor Profile: {self.user.username}, {self.registration_id})"
    
    def get_active_tasks_count(self):
        """Get count of currently active editing tasks."""
        return EditorTaskAssignment.objects.filter(
            assigned_editor=self,
            review_status__in=["pending", "in_review"]
        ).count()
    
    def can_take_more_tasks(self):
        """Check if editor can take more tasks."""
        return self.get_active_tasks_count() < self.max_concurrent_tasks


class EditorTaskAssignment(models.Model):
    """
    Tracks task assignments to editors, including fallback tracking.
    """
    ASSIGNMENT_TYPE_CHOICES = [
        ("auto", "Auto-Assigned"),
        ("manual", "Manually Assigned"),
        ("claimed", "Self-Claimed"),
    ]
    
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
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPE_CHOICES,
        default="auto",
        help_text="How this task was assigned."
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editor_assignments_made",
        help_text="User who assigned this task (admin/system for auto-assigned)."
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this task was assigned."
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
            ("rejected", "Rejected"),
            ("unclaimed", "Unclaimed"),
        ),
        default="pending",
        help_text="The current review status of the task."
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the editor started reviewing this task."
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
    editor_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quality rating given by admin/superadmin (1-5)."
    )
    
    class Meta:
        ordering = ["-assigned_at"]
        indexes = [
            models.Index(fields=["assigned_editor", "review_status"]),
            models.Index(fields=["review_status", "assigned_at"]),
            models.Index(fields=["order"]),
        ]

    def __str__(self):
        editor_name = self.assigned_editor.name if self.assigned_editor else "Unassigned"
        return f"Task {self.order.id} - {editor_name} ({self.review_status})"
    
    def start_review(self):
        """Mark task as in review and record start time."""
        if self.review_status not in ["pending", "unclaimed"]:
            raise ValueError(f"Cannot start review from status: {self.review_status}")
        self.review_status = "in_review"
        if not self.started_at:
            self.started_at = now()
        self.save(update_fields=["review_status", "started_at"])
    
    def complete_review(self):
        """Mark task as completed."""
        if self.review_status != "in_review":
            raise ValueError(f"Cannot complete review from status: {self.review_status}")
        self.review_status = "completed"
        self.reviewed_at = now()
        self.save(update_fields=["review_status", "reviewed_at"])
        # Update editor's orders_reviewed count
        if self.assigned_editor:
            from django.db.models import F
            EditorProfile.objects.filter(id=self.assigned_editor.id).update(
                orders_reviewed=F('orders_reviewed') + 1
            )


class EditorReviewSubmission(models.Model):
    """
    Tracks editor review submissions with details of edits made.
    """
    task_assignment = models.OneToOneField(
        EditorTaskAssignment,
        on_delete=models.CASCADE,
        related_name="review_submission",
        help_text="The task assignment this review belongs to."
    )
    editor = models.ForeignKey(
        EditorProfile,
        on_delete=models.CASCADE,
        related_name="review_submissions",
        help_text="Editor who submitted the review."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="editor_reviews",
        help_text="Order that was reviewed."
    )
    
    # Review details
    quality_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Quality score given by editor (0.00-10.00)."
    )
    issues_found = models.TextField(
        blank=True,
        help_text="Issues/problems found during review."
    )
    corrections_made = models.TextField(
        blank=True,
        help_text="Corrections/edits made by the editor."
    )
    recommendations = models.TextField(
        blank=True,
        help_text="Recommendations for writer or client."
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether editor approves the work for client delivery."
    )
    requires_revision = models.BooleanField(
        default=False,
        help_text="Whether editor requests revision from writer."
    )
    revision_notes = models.TextField(
        blank=True,
        help_text="Notes for writer if revision is required."
    )
    
    # File attachments (optional)
    edited_files = models.JSONField(
        default=list,
        blank=True,
        help_text="List of file IDs that were edited/reviewed."
    )
    
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this review was submitted."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time."
    )
    
    class Meta:
        ordering = ["-submitted_at"]
    
    def __str__(self):
        status = "Approved" if self.is_approved else "Revision Required"
        return f"Review for Order {self.order.id} by {self.editor.name} - {status}"


class EditorActionLog(models.Model):
    """
    Logs actions performed by editors.
    """
    ACTION_TYPES = [
        ("claimed_task", "Claimed Task"),
        ("started_review", "Started Review"),
        ("submitted_review", "Submitted Review"),
        ("completed_task", "Completed Task"),
        ("rejected_task", "Rejected Task"),
        ("unclaimed_task", "Unclaimed Task"),
    ]
    
    editor = models.ForeignKey(
        EditorProfile,
        on_delete=models.CASCADE,
        related_name="action_logs",
        help_text="The editor performing the action."
    )
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        help_text="Type of action performed."
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
    related_task = models.ForeignKey(
        EditorTaskAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
        help_text="The task assignment associated with this action."
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action."
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the action.")

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["editor", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
        ]

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
    average_quality_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average quality score given by admin."
    )
    revisions_requested_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of revisions requested."
    )
    approvals_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of orders approved for delivery."
    )
    last_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When performance metrics were last calculated."
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
    related_task = models.ForeignKey(
        EditorTaskAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Related task assignment, if applicable."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp of the notification."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates whether the notification has been read."
    )
    notification_type = models.CharField(
        max_length=50,
        default="info",
        choices=[
            ("info", "Info"),
            ("task_assigned", "Task Assigned"),
            ("task_claimed", "Task Claimed"),
            ("reminder", "Reminder"),
            ("urgent", "Urgent"),
        ],
        help_text="Type of notification."
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["editor", "is_read", "created_at"]),
        ]

    def __str__(self):
        return f"Notification for {self.editor.name}: {self.message[:30]}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save(update_fields=["is_read"])
