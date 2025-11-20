"""
SSE (Server-Sent Events) views for real-time notifications.
"""
from __future__ import annotations

import logging
import time
import json
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from notifications_system.delivery.sse import SSEDeliveryBackend, get_connection_manager
from notifications_system.utils.logging import notification_logger

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SSEStreamView(View):
    """
    SSE stream endpoint for real-time notifications.
    
    Usage:
        GET /notifications/sse/stream/
        
    Headers:
        - Accept: text/event-stream
        - Cache-Control: no-cache
    """
    
    def get(self, request):
        """Handle SSE stream requests."""
        user = request.user
        
        # Check if user has SSE enabled
        if not hasattr(user, 'notification_preferences') or not getattr(
            user.notification_preferences, 'receive_sse', True
        ):
            return StreamingHttpResponse(
                self._format_sse_event('error', {
                    'message': 'SSE notifications disabled for user',
                    'timestamp': time.time()
                }),
                content_type='text/event-stream'
            )
        
        # Create SSE stream
        sse_backend = SSEDeliveryBackend()
        return sse_backend.create_sse_stream(user.id, request)
    
    def _format_sse_event(self, event_type: str, data: dict) -> str:
        """Format data as SSE event."""
        lines = []
        lines.append(f"event: {event_type}")
        lines.append(f"data: {json.dumps(data)}")
        lines.append("")  # Empty line to end event
        return "\n".join(lines) + "\n"


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SSEStatusView(View):
    """
    SSE connection status endpoint.
    
    Usage:
        GET /notifications/sse/status/
    """
    
    def get(self, request):
        """Get SSE connection status."""
        user = request.user
        sse_backend = SSEDeliveryBackend()
        
        status = sse_backend.get_connection_stats(user.id)
        
        return JsonResponse({
            'user_id': user.id,
            'is_connected': status['is_connected'],
            'last_update': status['last_update'],
            'event_count': status['event_count'],
            'connection_timeout': status['connection_timeout']
        })


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SSECloseView(View):
    """
    Close SSE connection endpoint.
    
    Usage:
        POST /notifications/sse/close/
    """
    
    def post(self, request):
        """Close SSE connection for user."""
        user = request.user
        sse_backend = SSEDeliveryBackend()
        
        sse_backend.close_connection(user.id)
        
        return JsonResponse({
            'status': 'success',
            'message': 'SSE connection closed'
        })