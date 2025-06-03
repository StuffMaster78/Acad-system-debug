from django.db import models
from django.conf import settings
from django.utils import timezone


class FineType(models.TextChoices):
    """Enum of fine types writers can be charged for."""

    LATE_SUBMISSION = "late_submission", "Late Submission"
    QUALITY = "quality", "Quality Penalty"
    PLAGIARISM = "plagiarism", "Plagiarism"
    INACTIVITY = "inactivity", "Inactivity/Abandonment"
    COMM_BREACH = "comm_breach", "Communication Breach"
    EXCESSIVE_REVISIONS = "excessive_revisions", "Excessive Revisions"
    EXTENSION_OVERUSE = "extension_overuse", "Deadline Extension Overuse"
    MANUAL_VIOLATION = "manual_violation", "Manual Violation"


class FineStatus(models.TextChoices):
    """Enum for the lifecycle status of a fine."""

    ISSUED = "issued", "Issued"
    APPEALED = "appealed", "Appealed"
    RESOLVED = "resolved", "Resolved"
    WAIVED = "waived", "Waived"


class FinePolicy(models.Model):
    """Defines configurable fine rules and percentages over time.

    Attributes:
        fine_type (str): The fine category this policy applies to.
        percentage (Decimal): Percentage of base amount to fine.
        fixed_amount (Decimal): Fixed amount to fine (overrides percentage).
        start_date (DateTime): When this policy becomes active.
        end_date (DateTime): When this policy expires.
        active (bool): Whether the policy is currently active.
        description (str): Admin notes about this policy.
    """

    fine_type = models.CharField(
        max_length=30, choices=FineType.choices, db_index=True
    )
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    fixed_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_waived",
        help_text="User who waived the fine, if applicable."
    )
    waived_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the fine was waived."
    )
    waiver_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason given for waiving the fine."
    )

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["fine_type", "start_date"])]

    def __str__(self):
        return (
            f"{self.get_fine_type_display()} Policy "
            f"({self.start_date:%Y-%m-%d} to "
            f"{self.end_date:%Y-%m-%d if self.end_date else 'ongoing'})"
        )

    def is_active(self):
        """Returns True if the policy is currently active."""
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Fine(models.Model):
    """Represents a fine issued to an order.

    Attributes:
        order (ForeignKey): The order associated with the fine.
        fine_type (str): The category of fine.
        amount (Decimal): The monetary value of the fine.
        reason (Text): Explanation for issuing the fine.
        issued_by (ForeignKey): The user who issued the fine.
        status (str): Current state of the fine.
        imposed_at (DateTime): Timestamp when the fine was created.
        resolved (bool): Whether the fine has been resolved.
        resolved_at (DateTime): Timestamp when resolved.
        resolved_reason (Text): Reason for resolution.
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="fines",
    )
    fine_type = models.CharField(
        max_length=30,
        choices=FineType.choices,
        default=FineType.LATE_SUBMISSION,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fines_issued",
    )
    status = models.CharField(
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.ISSUED,
        db_index=True,
    )
    imposed_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_reason = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-imposed_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["fine_type"]),
            models.Index(fields=["status"]),
        ]

    def waive(self, by_user, reason=None):
        """
        Waive this fine using the action system.

        Args:
            by_user (User): The user attempting to waive the fine.
            reason (str, optional): Reason for waiving the fine.

        Returns:
            Fine: The updated Fine instance after waiving.

        Raises:
            PermissionDenied: If the user lacks required permissions.
            ValidationError: If the fine is in an invalid state.
        """
        from actions.dispatcher import dispatch_action
        return dispatch_action(
            name="waive_fine",
            actor=by_user,
            fine=self,
            waived_by=by_user,
            reason=reason
        )

    def void(self, by_user, reason=None):
        """
        Void this fine using the action system.

        Args:
            by_user (User): The user attempting to void the fine.
            reason (str, optional): Reason for voiding the fine.

        Returns:
            Fine: The updated Fine instance after voiding.

        Raises:
            PermissionDenied: If the user lacks required permissions.
            ValidationError: If the fine is in an invalid state.
        """
        from actions.dispatcher import dispatch_action
        return dispatch_action(
            name="void_fine",
            actor=by_user,
            fine=self,
            voided_by=by_user,
            reason=reason
        )

    def appeal(self, by_user, reason):
        """
        Submit an appeal for this fine using the action system.

        Args:
            by_user (User): The writer submitting the appeal.
            reason (str): Reason for appealing the fine.

        Returns:
            FineAppeal: The created appeal instance.

        Raises:
            PermissionDenied: If the user lacks required permissions.
            ValidationError: If the fine is already appealed.
        """
        from actions.dispatcher import dispatch_action
        return dispatch_action(
            name="submit_fine_appeal",
            actor=by_user,
            fine=self,
            appealed_by=by_user,
            reason=reason
        )

    def __str__(self):
        return f"Fine #{self.id} on Order #{self.order_id} - {self.status}"


class FineAppeal(models.Model):
    """Represents an appeal against a fine.

    Attributes:
        fine (OneToOne): The fine being appealed.
        reason (Text): Justification for the appeal.
        appealed_by (ForeignKey): The user submitting the appeal.
        created_at (DateTime): Timestamp when the appeal was created.
        reviewed_by (ForeignKey): The admin who reviewed the appeal.
        reviewed_at (DateTime): Timestamp when the appeal was reviewed.
        accepted (bool): Outcome of the appeal (True, False, or None).
    """

    fine = models.OneToOneField(
        Fine,
        on_delete=models.CASCADE,
        related_name="appeal",
    )
    reason = models.TextField()
    appealed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fines_appealed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fine_appeals_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(null=True, blank=True)


    def review(self, by_user, accept: bool, notes=None):
        """
        Review this fine appeal using the action system.

        Args:
            by_user (User): The admin reviewing the appeal.
            accept (bool): Whether to accept or reject the appeal.
            notes (str, optional): Reviewer comments.

        Returns:
            FineAppeal: The updated appeal instance.

        Raises:
            PermissionDenied: If the user lacks required permissions.
            ValidationError: If the appeal has already been reviewed.
        """
        from actions.dispatcher import dispatch_action
        return dispatch_action(
            name="review_fine_appeal",
            actor=by_user,
            appeal=self,
            reviewed_by=by_user,
            accept=accept,
            review_notes=notes
        )


    def __str__(self):
        return f"Appeal for Fine #{self.fine_id}"