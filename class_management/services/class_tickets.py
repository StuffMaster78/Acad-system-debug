"""
Service for handling tickets related to class bundles.
"""

import logging
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError

from class_management.models import ClassBundle
from tickets.models import Ticket, TicketMessage, TicketAttachment

logger = logging.getLogger(__name__)


class ClassBundleTicketService:
    """
    Service for managing tickets related to class bundles.
    """
    
    @staticmethod
    @transaction.atomic
    def create_ticket_for_bundle(
        bundle: ClassBundle,
        created_by,
        title: str,
        description: str,
        priority: str = 'medium',
        category: str = 'general'
    ) -> Ticket:
        """
        Create a support ticket related to a class bundle.
        
        Args:
            bundle: ClassBundle instance
            created_by: User creating the ticket
            title: Ticket title
            description: Ticket description
            priority: Priority level
            category: Ticket category
            
        Returns:
            Ticket: Created ticket
        """
        # Validate user can create ticket for this bundle
        if bundle.client != created_by and not created_by.is_staff:
            raise PermissionDenied(
                "Only the client or staff can create tickets for this bundle."
            )
        
        # Get content type for ClassBundle
        from django.contrib.contenttypes.models import ContentType
        bundle_content_type = ContentType.objects.get_for_model(ClassBundle)
        
        # Create ticket
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            created_by=created_by,
            website=bundle.website,
            priority=priority,
            category=category,
            status='open',
            content_type=bundle_content_type,
            object_id=bundle.id
        )
        
        # Add reference to bundle in description if not already there
        if f"Class Bundle #{bundle.id}" not in ticket.description:
            ticket.description = f"[Class Bundle #{bundle.id}]\n\n{ticket.description}"
            ticket.save(update_fields=['description'])
        
        logger.info(
            f"Created ticket {ticket.id} for class bundle {bundle.id} by user {created_by.id}"
        )
        
        return ticket
    
    @staticmethod
    @transaction.atomic
    def add_message_to_ticket(
        ticket: Ticket,
        sender,
        message: str,
        is_internal: bool = False
    ) -> TicketMessage:
        """
        Add a message to a ticket.
        
        Args:
            ticket: Ticket instance
            sender: User sending message
            message: Message content
            is_internal: Whether message is internal (admin-only)
            
        Returns:
            TicketMessage: Created message
        """
        # Validate permissions
        if is_internal and not sender.is_staff:
            raise PermissionDenied("Only staff can send internal messages.")
        
        # Validate sender can access ticket
        if ticket.created_by != sender and not sender.is_staff:
            raise PermissionDenied("You do not have access to this ticket.")
        
        # Create message
        ticket_message = TicketMessage.objects.create(
            ticket=ticket,
            sender=sender,
            message=message,
            is_internal=is_internal,
            website=ticket.website
        )
        
        logger.info(
            f"Added message {ticket_message.id} to ticket {ticket.id} by user {sender.id}"
        )
        
        return ticket_message
    
    @staticmethod
    @transaction.atomic
    def attach_file_to_ticket(
        ticket: Ticket,
        uploaded_by,
        file
    ) -> TicketAttachment:
        """
        Attach a file to a ticket.
        
        Args:
            ticket: Ticket instance
            uploaded_by: User uploading file
            file: File object
            
        Returns:
            TicketAttachment: Created attachment
        """
        # Validate permissions
        if ticket.created_by != uploaded_by and not uploaded_by.is_staff:
            raise PermissionDenied("You do not have permission to attach files to this ticket.")
        
        # Create attachment
        attachment = TicketAttachment.objects.create(
            ticket=ticket,
            uploaded_by=uploaded_by,
            file=file
        )
        
        logger.info(
            f"Attached file {attachment.id} to ticket {ticket.id} by user {uploaded_by.id}"
        )
        
        return attachment
    
    @staticmethod
    def get_tickets_for_bundle(bundle: ClassBundle, user):
        """
        Get all tickets related to a class bundle that user can access.
        
        Args:
            bundle: ClassBundle instance
            user: User requesting tickets
            
        Returns:
            QuerySet: Ticket instances
        """
        # Get tickets via GenericRelation
        tickets = bundle.support_tickets.all()
        
        # Filter by user permissions
        if not user.is_staff:
            tickets = tickets.filter(created_by=user)
        
        return tickets

