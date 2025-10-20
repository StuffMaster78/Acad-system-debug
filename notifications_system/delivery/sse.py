"""
Server-Sent Events (SSE) delivery backend for real-time notifications.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Set
from django.http import StreamingHttpResponse
from django.core.cache import cache
from notifications_system.delivery.base import BaseDeliveryBackend
from notifications_system.models.notifications import Notification

logger = logging.getLogger(__name__)


class SSEDeliveryBackend(BaseDeliveryBackend):
    """
    Server-Sent Events delivery backend for real-time notifications.
    
    Features:
    - Lightweight real-time communication
    - Automatic reconnection
    - Event filtering and batching
    - Connection management
    - Performance monitoring
    """
    
    def __init__(self):
        super().__init__()
        self.connection_timeout = 300  # 5 minutes
        self.heartbeat_interval = 30  # 30 seconds
        self.max_connections_per_user = 5
    
    def deliver(
        self,
        notification: Notification,
        user_id: int,
        **kwargs
    ) -> bool:
        """
        Deliver notification via SSE.
        
        Args:
            notification: The notification object
            user_id: Target user ID
            **kwargs: Additional delivery options
            
        Returns:
            True if delivery was successful
        """
        try:
            # Prepare SSE event data
            event_data = self._prepare_sse_event(notification, user_id)
            
            # Store event in cache for SSE streaming
            self._store_sse_event(user_id, event_data)
            
            # Trigger SSE update for connected clients
            self._trigger_sse_update(user_id)
            
            logger.debug(f"SSE notification delivered to user {user_id}: {notification.id}")
            return True
            
        except Exception as e:
            logger.exception(f"SSE delivery failed for user {user_id}: {e}")
            return False
    
    def _prepare_sse_event(self, notification: Notification, user_id: int) -> Dict[str, Any]:
        """Prepare SSE event data."""
        return {
            'id': str(notification.id),
            'event': 'notification',
            'data': {
                'notification_id': notification.id,
                'event_key': notification.event,
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'channels': notification.channels,
                'metadata': notification.metadata or {}
            },
            'timestamp': time.time()
        }
    
    def _store_sse_event(self, user_id: int, event_data: Dict[str, Any]):
        """Store SSE event in cache for streaming."""
        cache_key = f"sse_events:{user_id}"
        events = cache.get(cache_key, [])
        
        # Add new event
        events.append(event_data)
        
        # Keep only last 50 events per user
        if len(events) > 50:
            events = events[-50:]
        
        # Store in cache with 1 hour timeout
        cache.set(cache_key, events, 3600)
    
    def _trigger_sse_update(self, user_id: int):
        """Trigger SSE update for connected clients."""
        # Update connection status to trigger SSE refresh
        connection_key = f"sse_connection:{user_id}"
        cache.set(connection_key, {
            'last_update': time.time(),
            'event_count': cache.get(f"sse_events:{user_id}", [])
        }, self.connection_timeout)
    
    def create_sse_stream(self, user_id: int, request) -> StreamingHttpResponse:
        """
        Create SSE stream for a user.
        
        Args:
            user_id: User ID
            request: HTTP request object
            
        Returns:
            StreamingHttpResponse for SSE
        """
        def event_generator():
            """Generate SSE events."""
            connection_id = f"sse_conn_{user_id}_{int(time.time())}"
            last_event_id = 0
            
            try:
                # Send initial connection event
                yield self._format_sse_event('connection', {
                    'status': 'connected',
                    'connection_id': connection_id,
                    'user_id': user_id
                }, event_id=0)
                
                # Send heartbeat and events
                heartbeat_count = 0
                while True:
                    # Check for new events
                    events = cache.get(f"sse_events:{user_id}", [])
                    new_events = [e for e in events if e.get('timestamp', 0) > last_event_id]
                    
                    # Send new events
                    for event in new_events:
                        yield self._format_sse_event(
                            event.get('event', 'notification'),
                            event.get('data', {}),
                            event_id=event.get('timestamp', time.time())
                        )
                        last_event_id = event.get('timestamp', 0)
                    
                    # Send heartbeat every 30 seconds
                    heartbeat_count += 1
                    if heartbeat_count >= 10:  # 10 * 3 seconds = 30 seconds
                        yield self._format_sse_event('heartbeat', {
                            'timestamp': time.time(),
                            'connection_id': connection_id
                        })
                        heartbeat_count = 0
                    
                    # Sleep for 3 seconds
                    time.sleep(3)
                    
            except GeneratorExit:
                logger.debug(f"SSE connection closed for user {user_id}")
            except Exception as e:
                logger.exception(f"SSE stream error for user {user_id}: {e}")
                yield self._format_sse_event('error', {
                    'message': 'Connection error',
                    'timestamp': time.time()
                })
        
        response = StreamingHttpResponse(
            event_generator(),
            content_type='text/event-stream'
        )
        
        # Set SSE headers
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        
        return response
    
    def _format_sse_event(self, event_type: str, data: Dict[str, Any], event_id: Optional[float] = None) -> str:
        """Format data as SSE event."""
        lines = []
        
        if event_id is not None:
            lines.append(f"id: {event_id}")
        
        lines.append(f"event: {event_type}")
        lines.append(f"data: {json.dumps(data)}")
        lines.append("")  # Empty line to end event
        
        return "\n".join(lines) + "\n"
    
    def get_connection_stats(self, user_id: int) -> Dict[str, Any]:
        """Get SSE connection statistics for a user."""
        connection_key = f"sse_connection:{user_id}"
        connection_data = cache.get(connection_key, {})
        
        events = cache.get(f"sse_events:{user_id}", [])
        
        return {
            'user_id': user_id,
            'is_connected': bool(connection_data),
            'last_update': connection_data.get('last_update', 0),
            'event_count': len(events),
            'connection_timeout': self.connection_timeout
        }
    
    def close_connection(self, user_id: int):
        """Close SSE connection for a user."""
        connection_key = f"sse_connection:{user_id}"
        cache.delete(connection_key)
        logger.debug(f"SSE connection closed for user {user_id}")
    
    def broadcast_to_all(self, event_data: Dict[str, Any]):
        """Broadcast event to all connected users."""
        # This would require a more sophisticated implementation
        # For now, we'll store it as a system-wide event
        system_events = cache.get('sse_system_events', [])
        system_events.append({
            **event_data,
            'timestamp': time.time(),
            'type': 'broadcast'
        })
        
        # Keep only last 100 system events
        if len(system_events) > 100:
            system_events = system_events[-100:]
        
        cache.set('sse_system_events', system_events, 3600)
        logger.info("System-wide SSE event broadcasted")


class SSEConnectionManager:
    """Manage SSE connections and provide utilities."""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[str]] = {}
    
    def add_connection(self, user_id: int, connection_id: str):
        """Add a new SSE connection."""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(connection_id)
        logger.debug(f"SSE connection added: user {user_id}, connection {connection_id}")
    
    def remove_connection(self, user_id: int, connection_id: str):
        """Remove an SSE connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(connection_id)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.debug(f"SSE connection removed: user {user_id}, connection {connection_id}")
    
    def get_active_connections(self, user_id: int) -> Set[str]:
        """Get active connections for a user."""
        return self.active_connections.get(user_id, set())
    
    def get_all_connections(self) -> Dict[int, Set[str]]:
        """Get all active connections."""
        return self.active_connections.copy()
    
    def get_connection_count(self, user_id: int) -> int:
        """Get connection count for a user."""
        return len(self.active_connections.get(user_id, set()))


# Global connection manager
_connection_manager = SSEConnectionManager()

def get_connection_manager() -> SSEConnectionManager:
    """Get the global SSE connection manager."""
    return _connection_manager