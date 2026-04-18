from django.apps import apps
from django.conf import settings

from datetime import timedelta
from django.db import models
from orders.models.orders import Order

from django.apps import apps
from orders.order_enums import (
    DisputeStatusEnum,
)


User = settings.AUTH_USER_MODEL 


class Dispute(models.Model):
    """
    Tracks disputes raised for an order.
    The order status is automatically updated when 
    disputes are raised, reviewed, or resolved.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='order_dispute'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='disputes',
        help_text="The order associated with this dispute."
    )
    raised_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_raised',
        help_text="The user who raised the dispute."
    )
    dispute_status = models.CharField(
        max_length=20,
        choices=DisputeStatusEnum.choices(),
        default=DisputeStatusEnum.OPEN.value,
        help_text="The current status of the dispute."
    )
    resolution_outcome = models.CharField(
        max_length=20,
        choices=[
            ('writer_wins', 'Writer Wins'),
            ('client_wins', 'Client Wins'),
            ('extend_deadline', 'Extend Deadline'),
            ('reassign', 'Reassign Order'),
        ],
        null=True,
        blank=True,
        help_text="Outcome of the dispute resolution."
    )
    reason = models.TextField(
        help_text="Reason for raising the dispute."
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes or comments regarding the resolution."
    )
    writer_responded = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer has responded."
    )
    admin_extended_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, admin has manually extended the deadline."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dispute was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the dispute was last updated."
    )

    def save(self, *args, **kwargs):
        """
        Persist the dispute without directly mutating the related order's status.

        Order status transitions are handled centrally via the
        `orders.services.disputes.DisputeService` and `OrderTransitionHelper`,
        ensuring consistent validation, logging, and hooks.
        """
        if self._state.adding and self.order.status == 'cancelled':
            raise ValueError("Cannot raise a dispute for a cancelled order.")

        if self._state.adding and self.order.status == 'progress':
            raise ValueError("Cannot raise a dispute for an order in progress.")

        super().save(*args, **kwargs)

    def resolve_dispute_action(self, resolved_by=None):
        """
        Backwards‑compat shim for legacy admin actions.

        Delegates to `DisputeService.resolve_dispute` so that resolution
        uses the unified transition helper and central business rules.
        """
        from orders.services.disputes import DisputeService
        from websites.models.websites import Website

        website: Website = self.website
        service = DisputeService(dispute=self)
        service.resolve_dispute(
            resolution_outcome=self.resolution_outcome,
            resolved_by=resolved_by or self.raised_by,
            website=website,
            resolution_notes=self.resolution_notes,
        )

    def notify_users(self, subject, message):
        recipients = []

        # Notify assigned writer
        if self.order.writer:
            recipients.append(self.order.writer.email)

        # Notify the person who raised the dispute
        if self.raised_by:
            recipients.append(self.raised_by.email)

        # Notify admins
        admin_emails = User.objects.filter(
            role__in=['admin', 'superadmin', 'support']
        ).values_list('email', flat=True)

        if recipients:
            send_mail(
                subject,
                message, 
                "no-reply@yourdomain.com",
                recipients
            )

    def __str__(self):
        return f"Dispute #{self.id} for Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class DisputeWriterResponse(models.Model):
    """
    Model to track writer responses to disputes.
    Writers must respond before a final decision.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='dispute_writer_response'
    )
    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.CASCADE,
        related_name='writer_responses_to_disputes',
        help_text="The dispute being responded to."
    )
    responded_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='dispute_writer_responses',
        limit_choices_to={'role': 'writer'},
        help_text="The writer responding to the dispute."
    )
    response_text = models.TextField(
        help_text="Writer's response or clarification."
    )
    response_file = models.FileField(
        upload_to='dispute_responses/',
        null=True,
        blank=True,
        help_text="Optional file upload for revised work."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time of response."
    )

    def __str__(self):
        return (
            f"Writer Response for Dispute #{self.dispute.id} by "
            f"{self.responded_by.username}"
        )


    def save(self, *args, **kwargs):
        """
        Mark dispute as responded
        when a writer submits a response.
        """
        self.dispute.writer_responded = True
        self.dispute.save()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('dispute', 'responded_by')
        ordering = ['-timestamp']

