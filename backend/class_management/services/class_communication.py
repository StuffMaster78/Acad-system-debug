"""
Service for handling communications (messages, threads) related to class bundles.
"""

import logging
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType

from class_management.models import ClassBundle
from communications.models import CommunicationThread, CommunicationMessage, CommRole
from websites.models import Website

logger = logging.getLogger(__name__)


class ClassBundleCommunicationService:
    """
    Service for managing communications related to class bundles.
    Allows writers, clients, admins, editors, superadmins to communicate.
    """
    
    @staticmethod
    @transaction.atomic
    def create_thread_for_bundle(
        bundle: ClassBundle,
        created_by,
        recipient,
        subject: str = None,
        initial_message: str = None
    ) -> CommunicationThread:
        """
        Create a communication thread for a class bundle.
        
        Args:
            bundle: ClassBundle instance
            created_by: User creating the thread
            recipient: User to communicate with
            subject: Optional thread subject
            initial_message: Optional initial message
            
        Returns:
            CommunicationThread: Created thread
            
        Raises:
            PermissionDenied: If user doesn't have permission
        """
        # Validate participants
        can_create = (
            bundle.client == created_by or 
            bundle.client == recipient or
            bundle.assigned_writer == created_by or
            bundle.assigned_writer == recipient or
            created_by.is_staff
        )
        
        if not can_create:
            raise PermissionDenied(
                "Only the client, assigned writer, or staff can create threads for this bundle."
            )
        
        # Determine roles
        sender_role = ClassBundleCommunicationService._get_user_role(created_by)
        recipient_role = ClassBundleCommunicationService._get_user_role(recipient)
        
        # Get content type for ClassBundle to link via GenericForeignKey
        from django.contrib.contenttypes.models import ContentType
        
        bundle_content_type = ContentType.objects.get_for_model(ClassBundle)
        
        # Create thread
        thread = CommunicationThread.objects.create(
            website=bundle.website,
            thread_type='class_bundle',
            order=None,  # Not linked to order
            special_order=None,  # Not special order
            content_type=bundle_content_type,  # Link to ClassBundle
            object_id=bundle.id,
            subject=subject or f"Class Bundle #{bundle.id} Communication",
            sender_role=sender_role,
            recipient_role=recipient_role,
            is_active=True,
        )
        
        # Add participants
        participants = [created_by, recipient, bundle.client]
        if bundle.assigned_writer:
            participants.append(bundle.assigned_writer)
        thread.participants.add(*participants)
        
        logger.info(
            f"Created communication thread {thread.id} for class bundle {bundle.id} "
            f"between {created_by.id} and {recipient.id}"
        )
        
        # Add initial message if provided
        if initial_message:
            CommunicationMessage.objects.create(
                thread=thread,
                sender=created_by,
                recipient=recipient,
                sender_role=sender_role,
                message=initial_message,
                message_type='text'
            )
        
        return thread
    
    @staticmethod
    def _get_user_role(user):
        """Get communication role for user."""
        if hasattr(user, 'role'):
            role_mapping = {
                'client': CommRole.CLIENT,
                'writer': CommRole.WRITER,
                'admin': CommRole.ADMIN,
                'editor': CommRole.EDITOR,
                'superadmin': CommRole.SUPERADMIN,
            }
            return role_mapping.get(user.role, CommRole.CLIENT)
        
        if user.is_superuser:
            return CommRole.SUPERADMIN
        if user.is_staff:
            return CommRole.ADMIN
        
        return CommRole.CLIENT
    
    @staticmethod
    def get_threads_for_bundle(bundle: ClassBundle, user):
        """
        Get all communication threads for a class bundle that user can access.
        
        Args:
            bundle: ClassBundle instance
            user: User requesting threads
            
        Returns:
            QuerySet: CommunicationThread instances
        """
        # Get threads via GenericRelation
        threads = bundle.message_threads.all()
        
        # Filter by participation
        if not user.is_staff:
            threads = threads.filter(participants=user)
        
        return threads.distinct()
    
    @staticmethod
    @transaction.atomic
    def send_message(
        thread: CommunicationThread,
        sender,
        recipient,
        message: str,
        attachment=None,
        message_type: str = 'text'
    ) -> CommunicationMessage:
        """
        Send a message in a class bundle thread.
        
        Args:
            thread: CommunicationThread instance
            sender: User sending message
            recipient: User receiving message
            message: Message content
            attachment: Optional file attachment
            message_type: Type of message ('text', 'file', etc.)
            
        Returns:
            CommunicationMessage: Created message
        """
        # Validate sender is participant
        if not thread.participants.filter(id=sender.id).exists():
            raise PermissionDenied("You are not a participant in this thread.")
        
        # Determine role
        sender_role = ClassBundleCommunicationService._get_user_role(sender)
        
        # Create message
        msg = CommunicationMessage.objects.create(
            thread=thread,
            sender=sender,
            recipient=recipient,
            sender_role=sender_role,
            message=message,
            message_type=message_type,
            attachment=attachment
        )
        
        logger.info(
            f"Message {msg.id} sent in thread {thread.id} from {sender.id} to {recipient.id}"
        )
        
        return msg
    
    @staticmethod
    def can_access_bundle_communication(user, bundle: ClassBundle) -> bool:
        """
        Check if user can access communications for a class bundle.
        
        Args:
            user: User to check
            bundle: ClassBundle instance
            
        Returns:
            bool: True if user can access
        """
        # Client can always access their bundles
        if bundle.client == user:
            return True
        
        # Staff (admin, editor, superadmin, support) can access all
        if user.is_staff or user.is_superuser:
            return True
        
        # Check user role for support/editor access
        if hasattr(user, 'role'):
            if user.role in ['admin', 'superadmin', 'editor', 'support']:
                return True
        
        # Assigned writer can access
        if bundle.assigned_writer == user:
            return True
        
        # Check if user is participant in any thread
        return bundle.message_threads.filter(participants=user).exists()

