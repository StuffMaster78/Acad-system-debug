from django.core.exceptions import ValidationError
from django.utils import timezone
from orders.models import Dispute, DisputeWriterResponse, Order
from django.db import transaction
from django.apps import apps
from orders.utils import send_notification_email  # Assume you have this
from users.models import User


class DisputeService:
    """
    Service for managing disputes related to orders.
    Includes logic for raising, resolving, and updating disputes.
    """
    def __init__(self, dispute: Dispute):
        """
        Initializes the dispute service with the given dispute.

        Args:
            dispute (Dispute): The dispute object associated with the service.
        """
        self.dispute = dispute
        self.order = dispute.order

    @classmethod
    def raise_dispute(cls, order, raised_by, reason, website):
        """
        Raises a new dispute for a given order.

        Args:
            order (Order): The order for which the dispute is raised.
            raised_by (User): The user who raised the dispute.
            reason (str): The reason for raising the dispute.
            website (Website): The website where the dispute is raised.

        Returns:
            Dispute: The created dispute object.
        
        Raises:
            ValidationError: If the order cannot have a dispute raised.
        """
        if order.status in ['cancelled', 'progress']:
            raise ValidationError("Cannot raise dispute for this order.")

        dispute = Dispute.objects.create(
            website=website,
            order=order,
            raised_by=raised_by,
            reason=reason,
            status='open',
        )
        order.status = 'disputed'
        order.save()

        cls.notify_users(
            dispute,
            subject="New Dispute Raised",
            message=f"A dispute has been raised for Order #{order.id}. "
                    "Admin attention required."
        )

        return dispute

    def update_status(self, new_status):
        """
        Updates the status of the dispute.

        Args:
            new_status (str): The new status for the dispute.

        Raises:
            ValidationError: If the status is invalid or not allowed.
        """
        valid_statuses = ['in_review', 'escalated', 'resolved']
        if new_status not in valid_statuses:
            raise ValidationError("Invalid dispute status.")

        self.dispute.status = new_status

        if new_status == 'resolved':
            raise ValidationError("Use `resolve_dispute` method to resolve.")

        self.order.status = new_status
        self.order.save()
        self.dispute.save()

    @transaction.atomic
    def resolve_dispute(self, resolution_outcome, resolved_by,
                        resolution_notes=None, extended_deadline=None):
        """
        Resolves the dispute and updates the order status.

        Args:
            resolution_outcome (str): The outcome of the dispute resolution.
            resolved_by (User): The user resolving the dispute.
            resolution_notes (str, optional): Additional notes on the resolution.
            extended_deadline (datetime, optional): New deadline if extended.

        Returns:
            Dispute: The resolved dispute object.

        Raises:
            ValidationError: If the resolution outcome is unknown or invalid.
        """
        self.dispute.status = 'resolved'
        self.dispute.resolution_outcome = resolution_outcome
        self.dispute.resolution_notes = resolution_notes
        self.dispute.save()

        if resolution_outcome == 'writer_wins':
            self.order.status = 'completed'

        elif resolution_outcome == 'client_wins':
            self.order.status = 'cancelled'

        elif resolution_outcome == 'extend_deadline':
            if not extended_deadline:
                raise ValidationError("Extended deadline must be provided.")
            self.order.change_deadline(extended_deadline)
            self.order.status = 'revision'
            self.dispute.admin_extended_deadline = extended_deadline

        elif resolution_outcome == 'reassign':
            self.order.status = 'available'
            self.order.writer = None

        else:
            raise ValidationError("Unknown resolution outcome.")

        self.order.save()
        self.dispute.save()

        self.notify_users(
            self.dispute,
            subject="Dispute Resolved",
            message=f"Dispute for Order #{self.order.id} has been resolved: "
                    f"{resolution_outcome.replace('_', ' ').title()}."
        )

        return self.dispute

    @staticmethod
    def notify_users(dispute, subject, message):
        """
        Sends notification emails to relevant users.

        Args:
            dispute (Dispute): The dispute object to notify about.
            subject (str): The subject of the email.
            message (str): The message body of the email.
        """
        recipients = []

        if dispute.order.writer:
            recipients.append(dispute.order.writer.email)

        if dispute.raised_by:
            recipients.append(dispute.raised_by.email)

        admin_emails = User.objects.filter(role__in=['admin', 'support', 'superadmin']) \
                                   .values_list('email', flat=True)

        recipients.extend(admin_emails)

        recipients = list(set(recipients))  # avoid duplicates

        if recipients:
            send_notification_email(subject, message, recipients)


class DisputeWriterResponseService:
    """
    Service for handling writer responses to disputes.
    """
    def __init__(self, dispute, writer):
        """
        Initializes the service for managing writer responses.

        Args:
            dispute (Dispute): The dispute the writer is responding to.
            writer (User): The writer submitting the response.
        """
        self.dispute = dispute
        self.writer = writer

    def submit_response(self, response_text, response_file=None):
        """
        Submits a response from the writer to the dispute.

        Args:
            response_text (str): The text of the writer's response.
            response_file (File, optional): An optional file upload for the
                                             writer's response.

        Returns:
            DisputeWriterResponse: The created writer response object.

        Raises:
            ValidationError: If the writer has already responded.
        """
        if self.dispute.writer_responded:
            raise ValidationError("Writer has already responded to this dispute.")

        response = DisputeWriterResponse.objects.create(
            dispute=self.dispute,
            responded_by=self.writer,
            response_text=response_text,
            response_file=response_file
        )
        self.dispute.writer_responded = True
        self.dispute.save()
        return response