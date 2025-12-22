import json
import time

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import BaseRenderer
from rest_framework.negotiation import BaseContentNegotiation
from django.http import StreamingHttpResponse
from django.db.models import Q, Exists, OuterRef, Prefetch

from orders.models import Order
from .models import CommunicationThread, CommunicationMessage
from .serializers import CommunicationThreadSerializer, CommunicationMessageSerializer
from .services.messages import MessageService

# Import JWT authentication for query param token support
try:
    from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
except ImportError:
    # Fallback if package not available (shouldn't happen in production)
    JWTAuthentication = None


class SSERenderer(BaseRenderer):
    """Custom renderer for Server-Sent Events."""
    media_type = 'text/event-stream'
    format = 'sse'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # This won't be called for StreamingHttpResponse, but we need it for DRF content negotiation
        return data


class SSEContentNegotiation(BaseContentNegotiation):
    """Content negotiation that accepts text/event-stream for SSE."""
    
    def select_parser(self, request, parsers):
        # SSE doesn't need parsing
        return None
    
    def select_renderer(self, request, renderers, format_suffix=None):
        # Always return the SSE renderer if available
        for renderer in renderers:
            if hasattr(renderer, 'media_type') and renderer.media_type == 'text/event-stream':
                return (renderer, renderer.media_type)
        # If no SSE renderer found, return the first available renderer
        if renderers:
            return (renderers[0], renderers[0].media_type)
        return (None, None)


class OrderCommunicationsStream(APIView):
    """
    Server-Sent Events stream for order communications.

    Sends a lightweight snapshot of all threads the current user can see.
    This is used by the frontend to keep the messaging UI in sync without
    aggressive polling.
    """

    stream_interval_seconds = 15
    renderer_classes = [SSERenderer]
    content_negotiation_class = SSEContentNegotiation
    
    # Bypass DRF content negotiation for SSE
    def finalize_response(self, request, response, *args, **kwargs):
        # For SSE, return the StreamingHttpResponse directly without DRF processing
        if isinstance(response, StreamingHttpResponse):
            return response
        return super().finalize_response(request, response, *args, **kwargs)

    def _get_threads_for_user(self, request):
        """
        Filter threads based on participants and role-based visibility.
        
        Rules:
        - Users can see threads where they are participants (always)
        - Admin/superadmin/support/editor can see client-writer threads as observers
        - Writers CANNOT see admin-client threads (only their own participant threads)
        - Clients CANNOT see threads they're not participants in
        """
        user = request.user
        role = getattr(user, "role", None)

        base_qs = CommunicationThread.objects.select_related(
            "order",
            "website",
            "order__client",
            "order__assigned_writer",
            "order__website",
        ).prefetch_related(
            "participants",
            Prefetch(
                "messages",
                queryset=CommunicationMessage.objects.filter(is_deleted=False)
                .select_related("sender", "recipient")
                .prefetch_related("read_by")
                .order_by("sent_at"),  # Oldest first for chronological display
            ),
        )

        # Threads where user is a participant (always visible)
        participant_filter = Q(participants=user)

        # For writers and clients: ONLY threads where they are participants
        if role in {"writer", "client"}:
            return base_qs.filter(participant_filter).distinct().order_by("-updated_at", "-id")

        # For admin/superadmin: can see all threads
        if role in {"admin", "superadmin"}:
            return base_qs.order_by("-updated_at", "-id")

        # For support/editor: can see threads where they are participants OR client-writer threads
        # But NOT admin-client threads where they're not participants
        if role in {"support", "editor"}:
            # Threads where they are participants
            participant_threads = Q(participants=user)
            
            # Client-writer threads (where sender_role is client and recipient_role is writer, or vice versa)
            # AND user is NOT a participant (so they're observing)
            client_writer_threads = (
                (
                    (Q(sender_role='client') & Q(recipient_role='writer')) |
                    (Q(sender_role='writer') & Q(recipient_role='client'))
                ) &
                ~Q(participants=user)  # Not a participant
            )
            
            # Exclude admin-client threads where they're not participants
            # Admin-client threads have admin/superadmin/support/editor as sender/recipient and client as the other
            admin_client_threads = (
                (
                    (Q(sender_role__in=['admin', 'superadmin', 'support', 'editor']) & Q(recipient_role='client')) |
                    (Q(sender_role='client') & Q(recipient_role__in=['admin', 'superadmin', 'support', 'editor']))
                ) &
                ~Q(participants=user)  # Not a participant
            )
            
            # Combine: participant threads OR client-writer threads (but exclude admin-client threads where not participant)
            combined_filter = participant_threads | (client_writer_threads & ~admin_client_threads)
            return base_qs.filter(combined_filter).distinct().order_by("-updated_at", "-id")

        # Default: only participant threads
        return base_qs.filter(participant_filter).distinct().order_by("-updated_at", "-id")

    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        # Ensure Accept header includes text/event-stream for SSE
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'text/event-stream' not in accept_header:
            request.META['HTTP_ACCEPT'] = 'text/event-stream, */*'
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Support JWT token authentication via query parameter (for EventSource)
        token = request.query_params.get('token')
        if token:
            if JWTAuthentication:
                try:
                    auth = JWTAuthentication()
                    # Manually set Authorization header for JWT auth
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                    user, _ = auth.authenticate(request)
                    if user:
                        request.user = user
                    else:
                        return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    # Log the exception for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"SSE authentication failed: {str(e)}")
                    return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"detail": "JWT authentication not available."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        def event_stream():
            try:
                while True:
                    threads = self._get_threads_for_user(request)
                    payload = CommunicationThreadSerializer(
                        threads, many=True, context={"request": request}
                    ).data
                    yield f"event: threads_update\ndata: {json.dumps(payload)}\n\n"
                    time.sleep(self.stream_interval_seconds)
            except GeneratorExit:
                return

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # Disable nginx buffering
        response["Connection"] = "keep-alive"
        return response


class OrderThreadMessagesStream(APIView):
    """SSE stream for messages in a single communication thread."""

    permission_classes = [IsAuthenticated]
    stream_interval_seconds = 5
    renderer_classes = [SSERenderer]
    content_negotiation_class = SSEContentNegotiation
    
    def dispatch(self, request, *args, **kwargs):
        # Ensure Accept header includes text/event-stream for SSE
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'text/event-stream' not in accept_header:
            request.META['HTTP_ACCEPT'] = 'text/event-stream, */*'
        return super().dispatch(request, *args, **kwargs)
    
    # Bypass DRF content negotiation for SSE
    def finalize_response(self, request, response, *args, **kwargs):
        # For SSE, return the StreamingHttpResponse directly without DRF processing
        if isinstance(response, StreamingHttpResponse):
            return response
        return super().finalize_response(request, response, *args, **kwargs)

    def get(self, request, thread_pk):
        # Support JWT token authentication via query parameter (for EventSource)
        token = request.query_params.get('token')
        if token:
            if JWTAuthentication:
                try:
                    auth = JWTAuthentication()
                    # Manually set Authorization header for JWT auth
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
                    user, _ = auth.authenticate(request)
                    if user:
                        request.user = user
                    else:
                        return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    # Log the exception for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"SSE thread authentication failed: {str(e)}")
                    return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"detail": "JWT authentication not available."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            thread = CommunicationThread.objects.get(pk=thread_pk)
        except CommunicationThread.DoesNotExist:
            return Response({"detail": "Thread not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        # Basic access check using MessageService
        if not MessageService.can_view_thread(request.user, thread):
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        def event_stream():
            try:
                while True:
                    messages_qs = MessageService.get_visible_messages(request.user, thread)
                    payload = CommunicationMessageSerializer(
                        messages_qs, many=True, context={"request": request}
                    ).data
                    yield f"event: thread_messages\ndata: {json.dumps(payload)}\n\n"
                    time.sleep(self.stream_interval_seconds)
            except GeneratorExit:
                return

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"  # Disable nginx buffering
        response["Connection"] = "keep-alive"
        return response

