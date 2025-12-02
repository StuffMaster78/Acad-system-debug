from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .models import (
    CommunicationMessage, DisputeMessage,
    CommunicationThread, CommunicationNotification,
    ScreenedWord, FlaggedMessage, CommunicationLog,
    WebSocketAuditLog, SystemAlert
)
from .services.communication_guard import CommunicationGuardService
from .services.messages import MessageService
from .services.notification_service import NotificationService
from .services.thread_service import ThreadService

from .serializers import (
    CommunicationMessageSerializer, CommunicationThreadSerializer, 
    CommunicationNotificationSerializer, ScreenedWordSerializer,
    FlaggedMessageSerializer, AdminReviewSerializer,
    AdminEditFlaggedMessageSerializer, DisputeMessageSerializer,
    CommunicationThreadSerializer, CommunicationMessageSerializer,
    CommunicationLogSerializer, WebSocketAuditLogSerializer,
    OrderMessageNotificationSerializer
)
from .permissions import IsAdminOrOwner, CanSendOrderMessage
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from communications.throttles import AuditLogThrottle
from rest_framework.permissions import IsAuthenticated
from communications.permissions import IsSuperAdmin
from .throttles import SuperAdminAuditThrottle


class MessageThrottle(UserRateThrottle):
    rate = '30/min'  # Increased from 10/min for better messaging experience

class MessagePagination(PageNumberPagination):
    """Pagination for messages in threads."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommunicationThreadViewSet(viewsets.ModelViewSet):
    queryset = CommunicationThread.objects.select_related(
        'order',
        'website',
        'order__client',
        'order__assigned_writer',
        'order__website'
    ).prefetch_related(
        'participants',
        'messages'
    )
    serializer_class = CommunicationThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MessageThrottle]

    def get_serializer_class(self):
        """Use CreateCommunicationThreadSerializer for POST requests."""
        if self.action == 'create':
            from .serializers import CreateCommunicationThreadSerializer
            return CreateCommunicationThreadSerializer
        return self.serializer_class

    def get_queryset(self):
        """Filter threads based on user's order access."""
        queryset = super().get_queryset()
        user = self.request.user
        role = getattr(user, "role", None)
        
        # Admins can see all threads
        if role in {"admin", "superadmin"}:
            return queryset
        
        # Filter threads where user is a participant OR has access to the order
        from django.db.models import Q
        from orders.models import Order
        
        # Threads where user is a participant
        participant_threads = queryset.filter(participants=user)
        
        # Threads for orders where user has access
        order_access_filter = Q()
        
        # Client's orders
        client_orders = Order.objects.filter(client=user)
        order_access_filter |= Q(order__in=client_orders)
        
        # Writer's assigned orders
        writer_orders = Order.objects.filter(assigned_writer=user)
        order_access_filter |= Q(order__in=writer_orders)
        
        # Staff roles can see all order threads
        if role in {"editor", "support"}:
            order_access_filter |= Q(order__isnull=False)
        
        order_threads = queryset.filter(order_access_filter)
        
        # Combine both and order by most recent first
        return (participant_threads | order_threads).distinct().order_by('-updated_at', '-id')

    @action(detail=True, methods=['post'], url_path='typing')
    def typing(self, request, pk=None):
        """
        Lightweight endpoint used by the frontend to signal that the user is typing.

        Note:
        - We intentionally do not persist typing state in the database here.
        - The main goal is to provide a valid endpoint so clients and the schema
          generator do not hit 500s when calling `/typing/`.
        """
        thread = self.get_object()
        user = request.user

        # Reuse existing guard to ensure only authorized participants can hit this.
        if not CommunicationGuardService.can_send_message(user, thread):
            return Response(
                {"detail": "You do not have permission to send typing events in this thread."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # No-op success response
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """
        Override create to handle thread creation properly.
        Auto-determines participants if not provided, making it easier to use.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = serializer.validated_data.get("order")  # Can be None for general threads
        participants = serializer.validated_data.get("participants", [])
        created_by = request.user

        # Check thread creation permission (only for order threads)
        if order and not getattr(created_by, "role", None) in ["admin", "superadmin"]:
            ThreadService.assert_can_create_thread(order)

        # Auto-determine participants if not provided (simplified approach)
        if not participants and order:
            # If no participants specified, auto-determine based on order
            participants = [created_by]  # Always include the creator
            
            # Add order client if exists and different from creator
            if order.client and order.client != created_by:
                participants.append(order.client)
            
            # Add assigned writer if exists and different from creator
            if order.assigned_writer and order.assigned_writer != created_by:
                participants.append(order.assigned_writer)
            
            # Ensure we have at least 2 participants (creator + one other)
            # If no client or writer, add support/admin as fallback
            if len(participants) == 1:
                website = order.website
                if website:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    support_user = User.objects.filter(
                        role__in=['admin', 'superadmin', 'support'],
                        website=website
                    ).first()
                    if support_user and support_user != created_by:
                        participants.append(support_user)
        else:
            # Participants were provided, but ensure creator is included
            if created_by not in participants:
                participants.append(created_by)
            
            # Also auto-add order-related users if not already included
            if order:
                if order.client and order.client not in participants:
                    participants.append(order.client)
                if order.assigned_writer and order.assigned_writer not in participants:
                    participants.append(order.assigned_writer)

        # Get thread_type from serializer if provided
        thread_type = serializer.validated_data.get("thread_type", "order")
        website = serializer.validated_data.get("website") or (order.website if order else None)
        
        # Actually create the thread
        try:
            thread = ThreadService.create_thread(
                order=order,
                created_by=created_by,
                participants=participants,
                thread_type=thread_type,
                website=website
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except (ValueError, TypeError) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return the created thread using the read serializer
        response_serializer = CommunicationThreadSerializer(thread, context={'request': request})
        headers = self.get_success_headers(response_serializer.data)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @action(detail=False, methods=['get'], url_path='order-recipients')
    def order_recipients(self, request):
        """Get list of available recipients for an order (before creating a thread)."""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {"detail": "order_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from orders.models import Order
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sender = request.user
        sender_role = getattr(sender, 'role', None)
        recipients = []
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        website = order.website
        
        # Clients can message: support, admin, writer, editor
        if sender_role == "client":
            # Get assigned writer (anonymized)
            if order.assigned_writer and order.assigned_writer != sender:
                recipients.append({
                    'id': order.assigned_writer.id,
                    'username': f"Writer #{order.assigned_writer.id}",
                    'email': None,
                    'role': 'writer',
                })
            
            # Get all staff (support, admin, editor)
            if website:
                staff_users = User.objects.filter(
                    role__in=['admin', 'superadmin', 'editor', 'support'],
                    website=website
                ).exclude(id=sender.id).distinct()
                
                for staff_user in staff_users:
                    display_name = "Support" if staff_user.role in ['admin', 'superadmin', 'support'] else "Editor"
                    recipients.append({
                        'id': staff_user.id,
                        'username': display_name,
                        'email': None,
                        'role': getattr(staff_user, 'role', None),
                    })
        
        # Writers can message: clients, admin, support, editor
        elif sender_role == "writer":
            # Get client (anonymized)
            if order.client and order.client != sender:
                recipients.append({
                    'id': order.client.id,
                    'username': "Client",
                    'email': None,
                    'role': 'client',
                })
            
            # Get all staff
            if website:
                staff_users = User.objects.filter(
                    role__in=['admin', 'superadmin', 'editor', 'support'],
                    website=website
                ).exclude(id=sender.id).distinct()
                
                for staff_user in staff_users:
                    display_name = "Support" if staff_user.role in ['admin', 'superadmin', 'support'] else "Editor"
                    recipients.append({
                        'id': staff_user.id,
                        'username': display_name,
                        'email': None,
                        'role': getattr(staff_user, 'role', None),
                    })
        
        # Staff can see all (no anonymization)
        elif sender_role in {'admin', 'superadmin', 'editor', 'support'}:
            # Get client
            if order.client and order.client != sender:
                recipients.append({
                    'id': order.client.id,
                    'username': order.client.username,
                    'email': order.client.email,
                    'role': getattr(order.client, 'role', None),
                })
            
            # Get assigned writer
            if order.assigned_writer and order.assigned_writer != sender:
                recipients.append({
                    'id': order.assigned_writer.id,
                    'username': order.assigned_writer.username,
                    'email': order.assigned_writer.email,
                    'role': getattr(order.assigned_writer, 'role', None),
                })
            
            # Get all staff
            if website:
                staff_users = User.objects.filter(
                    role__in=['admin', 'superadmin', 'editor', 'support'],
                    website=website
                ).exclude(id=sender.id).distinct()
                
                for staff_user in staff_users:
                    if not any(r['id'] == staff_user.id for r in recipients):
                        recipients.append({
                            'id': staff_user.id,
                            'username': staff_user.username,
                            'email': staff_user.email,
                            'role': getattr(staff_user, 'role', None),
                        })
        
        return Response(recipients)
    
    @action(detail=False, methods=['post'], url_path='create-general-thread')
    def create_general_thread(self, request):
        """
        Create a general messaging thread without requiring an order.
        This is for direct communication between users (not order-related).
        
        POST /api/v1/order-communications/communication-threads/create-general-thread/
        
        Body:
        {
            "recipient_id": 123,
            "message": "Your initial message",
            "thread_type": "general" (optional)
        }
        """
        recipient_id = request.data.get('recipient_id')
        initial_message = request.data.get('message', '').strip()
        thread_type = request.data.get('thread_type', 'general')
        
        if not recipient_id:
            return Response(
                {"detail": "recipient_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not initial_message:
            return Response(
                {"detail": "Initial message is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Recipient not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        
        # Check if thread already exists between these two users
        existing_thread = CommunicationThread.objects.filter(
            participants=user
        ).filter(
            participants=recipient
        ).filter(
            order__isnull=True,
            thread_type=thread_type
        ).first()
        
        if existing_thread:
            # Thread exists, just send the message
            try:
                sender_role = getattr(user, 'role', None) or 'client'
                comm_message = MessageService.create_message(
                    thread=existing_thread,
                    sender=user,
                    recipient=recipient,
                    sender_role=sender_role,
                    message=initial_message,
                    message_type="text"
                )
                serializer = CommunicationThreadSerializer(existing_thread, context={'request': request})
                return Response(
                    {
                        "detail": "Message sent to existing conversation.",
                        "thread": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"detail": f"Failed to send message: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create new thread
        try:
            # Get website from current user
            website = getattr(user, 'website', None)
            if not website:
                # Try to get from user's profile
                if hasattr(user, 'user_main_profile') and user.user_main_profile:
                    website = getattr(user.user_main_profile, 'website', None)
            
            if not website:
                return Response(
                    {"detail": "Unable to determine website. Please contact support."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Determine roles
            sender_role = getattr(user, 'role', None) or 'client'
            recipient_role = getattr(recipient, 'role', None) or 'client'
            
            # Create thread without order
            thread = CommunicationThread.objects.create(
                order=None,
                website=website,
                thread_type=thread_type,
                sender_role=sender_role,
                recipient_role=recipient_role,
                is_active=True
            )
            
            thread.participants.set([user, recipient])
            
            # Send initial message
            comm_message = MessageService.create_message(
                thread=thread,
                sender=user,
                recipient=recipient,
                sender_role=sender_role,
                message=initial_message,
                message_type="text"
            )
            
            serializer = CommunicationThreadSerializer(thread, context={'request': request})
            return Response(
                {
                    "detail": "Conversation started successfully.",
                    "thread": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error creating general thread: {e}")
            return Response(
                {"detail": f"Failed to create conversation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='start-for-order')
    def start_for_order(self, request):
        """
        Start a conversation thread for an order.
        This is a simplified endpoint that automatically sets up participants.
        
        POST /api/v1/order-communications/communication-threads/start-for-order/
        
        Body:
        {
            "order_id": 123
        }
        """
        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {"detail": "order_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from orders.models import Order
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if thread already exists for this order
        existing_thread = CommunicationThread.objects.filter(order=order).first()
        if existing_thread:
            # Return existing thread
            serializer = CommunicationThreadSerializer(existing_thread, context={'request': request})
            return Response(
                {
                    "detail": "Conversation thread already exists for this order.",
                    "thread": serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        # Check permissions using the guard service
        user = request.user
        
        # Use the existing permission check
        try:
            CommunicationGuardService.assert_can_start_thread(user, order)
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as perm_error:
            # Catch any other permission-related errors
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Permission check failed for user {user.id} on order {order_id}: {str(perm_error)}")
            return Response(
                {"detail": "You do not have permission to create a thread for this order."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Auto-determine participants
        participants = [user]  # Always include the creator
        
        # Add order client if exists and different from creator
        if order.client and order.client != user:
            participants.append(order.client)
        
        # Add assigned writer if exists and different from creator
        if order.assigned_writer and order.assigned_writer != user:
            participants.append(order.assigned_writer)
        
        # Ensure we have at least 2 participants (creator + one other)
        # If no client or writer, add support/admin as fallback
        if len(participants) == 1:
            # Only creator, try to add support/admin
            from django.contrib.auth import get_user_model
            User = get_user_model()
            website = order.website
            if website:
                support_user = User.objects.filter(
                    role__in=['admin', 'superadmin', 'support'],
                    website=website
                ).first()
                if support_user and support_user != user:
                    participants.append(support_user)
        
        # Create the thread
        try:
            thread = ThreadService.create_thread(
                order=order,
                created_by=user,
                participants=participants,
                thread_type="order",
                website=order.website
            )
            
            # Return the created thread
            serializer = CommunicationThreadSerializer(thread, context={'request': request})
            return Response(
                {
                    "detail": "Conversation thread created successfully.",
                    "thread": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except (ValueError, TypeError) as e:
            # Handle validation errors
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error creating conversation thread for order {order_id}: {e}")
            
            return Response(
                {"detail": "An error occurred while creating the conversation thread. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='send-message-simple')
    def send_message_simple(self, request, pk=None):
        """
        Simplified message sending endpoint that auto-detects recipient.
        This makes sending messages much easier - just provide the message text.
        
        POST /api/v1/order-communications/communication-threads/{id}/send-message-simple/
        
        Body:
        {
            "message": "Your message text here",
            "attachment": <file> (optional),
            "reply_to": <message_id> (optional)
        }
        """
        thread = self.get_object()
        user = request.user
        
        # Check permissions
        if not CommunicationGuardService.can_send_message(user, thread):
            return Response(
                {"detail": "You do not have permission to send messages in this thread."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Auto-detect recipient (the other participant in the thread)
        participants = list(thread.participants.exclude(id=user.id))
        
        if not participants:
            # If no other participants, try to get from order
            order = getattr(thread, 'order', None)
            if order:
                if user == order.client and order.assigned_writer:
                    recipient = order.assigned_writer
                elif user == order.assigned_writer and order.client:
                    recipient = order.client
                else:
                    # For staff, default to client or writer
                    recipient = order.client or order.assigned_writer
            else:
                return Response(
                    {"detail": "Cannot determine recipient. Please specify a recipient."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Use the first other participant (most common case: 2-person thread)
            recipient = participants[0]
            # If multiple participants and user is staff, prefer client or writer
            if len(participants) > 1 and getattr(user, 'role', None) in ['admin', 'superadmin', 'support', 'editor']:
                order = getattr(thread, 'order', None)
                if order:
                    if order.client in participants:
                        recipient = order.client
                    elif order.assigned_writer in participants:
                        recipient = order.assigned_writer
        
        message_text = request.data.get('message', '').strip()
        attachment_file = request.FILES.get('attachment')
        reply_to_id = request.data.get('reply_to')
        
        if not message_text and not attachment_file:
            return Response(
                {"detail": "Message text or attachment is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get reply_to message if provided
        reply_to = None
        if reply_to_id:
            try:
                reply_to = CommunicationMessage.objects.get(
                    id=reply_to_id,
                    thread=thread
                )
            except CommunicationMessage.DoesNotExist:
                return Response(
                    {"detail": "Reply-to message not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            sender_role = getattr(user, 'role', None) or 'client'
            
            # Create message using the service
            comm_message = MessageService.create_message(
                thread=thread,
                sender=user,
                recipient=recipient,
                sender_role=sender_role,
                message=message_text or "📎 File attachment",
                message_type="file" if attachment_file else "text",
                reply_to=reply_to,
                attachment_file=attachment_file
            )
            
            # Serialize and return
            serializer = CommunicationMessageSerializer(comm_message, context={'request': request})
            return Response(
                {
                    "detail": "Message sent successfully.",
                    "message": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
            return Response(
                {"detail": "An error occurred while sending the message. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_destroy(self, instance):
        """Only admin/superadmin can delete threads."""
        from rest_framework.exceptions import PermissionDenied
        role = getattr(self.request.user, "role", None)
        
        if role not in {"admin", "superadmin"}:
            raise PermissionDenied("Only administrators can delete threads.")
        
        # Delete the thread (this will cascade delete messages)
        instance.delete()


class CommunicationMessageViewSet(viewsets.ModelViewSet):
    queryset = CommunicationMessage.objects.all()
    serializer_class = CommunicationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_serializer_class(self):
        """Use CreateCommunicationMessageSerializer for POST requests."""
        if self.action == 'create':
            from .serializers import CreateCommunicationMessageSerializer
            return CreateCommunicationMessageSerializer
        return self.serializer_class

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_pk")
        thread = CommunicationThread.objects.get(pk=thread_id)
        user = self.request.user
        user_role = getattr(user, "role", None)
        
        # Editors can see all messages in threads they have access to
        if user_role == "editor":
            return thread.messages.filter(is_deleted=False).order_by("-sent_at")
        
        return MessageService.get_visible_messages(user, thread)

    def get_serializer_context(self):
        """Add thread context to serializer."""
        context = super().get_serializer_context()
        if self.action == 'create':
            thread_id = self.kwargs.get("thread_pk")
            thread = CommunicationThread.objects.get(pk=thread_id)
            context['thread'] = thread
        return context

    def perform_create(self, serializer):
        thread_id = self.kwargs.get("thread_pk")
        thread = CommunicationThread.objects.get(pk=thread_id)
        sender = self.request.user
        recipient = serializer.validated_data.get("recipient")
        message = serializer.validated_data["message"]
        reply_to = serializer.validated_data.get("reply_to")
        message_type = serializer.validated_data.get("message_type", "text")
        sender_role = getattr(sender, "role", None)

        # 💥 Guard message creation
        CommunicationGuardService.assert_can_send_message(sender, thread)

        # Recipient must be explicitly provided by the user
        if not recipient:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Recipient is required. Please select a recipient before sending the message.")

        # Validate recipient has access to the order
        if thread.order:
            order = thread.order
            role = getattr(recipient, "role", None)
            has_access = (
                order.client == recipient or
                order.assigned_writer == recipient or
                role in {"admin", "superadmin", "editor", "support"} or
                recipient in thread.participants.all()
            )
            if not has_access:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Selected recipient does not have access to this order.")

        # ✍️ Create via service
        msg = MessageService.create_message(
            thread=thread,
            sender=sender,
            recipient=recipient,
            sender_role=sender_role,
            message=message,
            reply_to=reply_to,
            message_type=message_type
        )
        return Response(
            CommunicationMessageSerializer(msg, context={'request': self.request}).data,
            status=status.HTTP_201_CREATED
        )
    
    def perform_destroy(self, instance):
        """Only admin/superadmin can delete messages."""
        from rest_framework.exceptions import PermissionDenied
        from .permissions import can_delete_message
        
        if not can_delete_message(self.request.user, instance):
            raise PermissionDenied("Only administrators can delete messages.")
        
        # Soft delete by setting is_deleted flag
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['get'])
    def download_attachment(self, request, thread_pk=None, pk=None):
        """Download a message attachment."""
        from django.http import FileResponse, Http404
        from django.shortcuts import get_object_or_404
        
        message = get_object_or_404(CommunicationMessage, pk=pk, thread_id=thread_pk)
        
        if not message.attachment:
            raise Http404("No attachment found")
        
        # Check if user has access to the thread
        if not CommunicationGuardService.can_view_thread(request.user, message.thread):
            return Response({"error": "Access denied"}, status=403)
        
        try:
            response = FileResponse(message.attachment.open(), content_type='application/octet-stream')
            file_name = message.attachment.name.split('/')[-1] if '/' in message.attachment.name else message.attachment.name
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            return Response({"error": f"Failed to download file: {str(e)}"}, status=500)
    
    @action(detail=False, methods=['get'])
    def available_recipients(self, request, thread_pk=None):
        """Get list of available recipients for this thread."""
        thread = CommunicationThread.objects.get(pk=thread_pk)
        sender = request.user
        
        # Get all users with access to the order
        recipients = []
        
        if thread.order:
            order = thread.order
            # Add client
            if order.client and order.client != sender:
                recipients.append({
                    'id': order.client.id,
                    'username': order.client.username,
                    'email': order.client.email,
                    'role': getattr(order.client, 'role', None),
                })
            # Add assigned writer
            if order.assigned_writer and order.assigned_writer != sender:
                recipients.append({
                    'id': order.assigned_writer.id,
                    'username': order.assigned_writer.username,
                    'email': order.assigned_writer.email,
                    'role': getattr(order.assigned_writer, 'role', None),
                })
            # Add all participants
            for participant in thread.participants.exclude(id=sender.id):
                if not any(r['id'] == participant.id for r in recipients):
                    recipients.append({
                        'id': participant.id,
                        'username': participant.username,
                        'email': participant.email,
                        'role': getattr(participant, 'role', None),
                    })
        else:
            # For threads without orders, just return participants
            for participant in thread.participants.exclude(id=sender.id):
                recipients.append({
                    'id': participant.id,
                    'username': participant.username,
                    'email': participant.email,
                    'role': getattr(participant, 'role', None),
                })
        
        return Response(recipients)


class OrderMessageNotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing message notifications.
    """
    serializer_class = OrderMessageNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only notifications for the logged-in user."""
        return CommunicationNotification.objects.filter(recipient=self.request.user)


class ScreenedWordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admin-controlled banned words.
    """
    queryset = ScreenedWord.objects.all()
    serializer_class = ScreenedWordSerializer
    permission_classes = [permissions.IsAdminUser]


class FlaggedMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to retrieve and manage flagged messages.
    Only accessible by admins.
    """
    queryset = FlaggedMessage.objects.all().order_by("-flagged_at")
    serializer_class = FlaggedMessageSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access

    @action(detail=True, methods=["PATCH"])
    def update_category(self, request, pk=None):
        """
        Allows admins to update the category of a flagged message.
        """
        flagged_message = self.get_object()
        category = request.data.get("category")

        if category not in dict(FlaggedMessage.CATEGORY_CHOICES):
            return Response({"error": "Invalid category choice."}, status=status.HTTP_400_BAD_REQUEST)

        flagged_message.category = category
        flagged_message.save()

        return Response({"detail": f"Category updated to {flagged_message.get_category_display()}."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def statistics(self, request):
        """
        Returns statistics about flagged messages.
        """
        total_flagged = FlaggedMessage.objects.count()
        total_reviewed = FlaggedMessage.objects.filter(reviewed_by__isnull=False).count()
        total_pending = total_flagged - total_reviewed

        return Response({
            "total_flagged": total_flagged,
            "total_reviewed": total_reviewed,
            "total_pending": total_pending
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def unblock(self, request, pk=None):
        """
        Admin manually unblocks a flagged message with a comment.
        """
        flagged_message = self.get_object()
        serializer = AdminReviewSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            flagged_message.admin_comment = serializer.validated_data.get("admin_comment", "")
            flagged_message.reviewed_by = request.user
            flagged_message.reviewed_at = flagged_message.reviewed_at or flagged_message.flagged_at
            flagged_message.is_unblocked = True
            flagged_message.save()
            return Response({"detail": "Message has been unblocked successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def edit(self, request, pk=None):
        """
        Allows admins to edit flagged messages.
        """
        flagged_message = self.get_object()
        serializer = AdminEditFlaggedMessageSerializer(flagged_message, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Flagged message updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"])
    def reflag(self, request, pk=None):
        """
        Admin manually re-flags a message that was previously unblocked.
        """
        flagged_message = self.get_object()

        if flagged_message.is_unblocked:
            flagged_message.is_unblocked = False
            flagged_message.reviewed_by = None
            flagged_message.reviewed_at = None
            flagged_message.admin_comment = "Message re-flagged by admin."
            flagged_message.save()
            return Response({"detail": "Message has been re-flagged successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "This message is already flagged."}, status=status.HTTP_400_BAD_REQUEST)
    

class DisputeMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage dispute messages.
    Admins can resolve and update dispute messages.
    """
    queryset = DisputeMessage.objects.all()
    serializer_class = DisputeMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def perform_create(self, serializer):
        """Attach sender information before saving."""
        serializer.save(sender=self.request.user, sender_role=getattr(self.request.user, "role", None))

    @action(detail=True, methods=["POST"])
    def resolve(self, request, pk=None):
        """
        Admin resolves a dispute message.
        """
        dispute_message = self.get_object()
        resolution_comment = request.data.get("resolution_comment", "")

        if not resolution_comment:
            return Response({"error": "Resolution comment is required."}, status=status.HTTP_400_BAD_REQUEST)

        dispute_message.resolve(admin_user=request.user, resolution_comment=resolution_comment)

        return Response({"detail": "Dispute message resolved successfully."}, status=status.HTTP_200_OK)


class MessageAttachmentUploadView(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        file = request.FILES.get("file")
        thread_id = request.data.get("thread_id")
        recipient_id = request.data.get("recipient_id")

        if not all([file, thread_id, recipient_id]):
            return Response({"error": "Missing fields."},
                            status=status.HTTP_400_BAD_REQUEST)

        thread = CommunicationThread.objects.get(id=thread_id)
        recipient = User.objects.get(id=recipient_id)
        sender = request.user

        msg = MessageService.create_message(
            thread=thread,
            sender=sender,
            recipient=recipient,
            message=f"[Attachment: {file.name}]",
            message_type="file",
            attachment_file=file,
            sender_role=getattr(sender, "role", None),
        )

        # Send notification via socket layer too, if needed
        return Response(CommunicationMessageSerializer(msg).data,
                        status=status.HTTP_201_CREATED)
    




class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationLog.objects.all().order_by("-timestamp")
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuditLogThrottle]
