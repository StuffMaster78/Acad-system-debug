"""
Session timeout middleware for idle timeout detection.
"""
import time
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SessionTimeoutMiddleware:
    """
    Middleware to handle session idle timeout.
    Tracks last activity and logs out users after idle period.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Get timeout settings (default: 30 minutes idle, 5 minutes warning)
        self.idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 30 * 60)  # 30 minutes in seconds
        self.warning_time = getattr(settings, 'SESSION_WARNING_TIME', 5 * 60)  # 5 minutes before timeout
        
    def __call__(self, request):
        # Skip for anonymous users
        if not request.user.is_authenticated:
            response = self.get_response(request)
            return response
        
        # Update last activity timestamp
        now = timezone.now().timestamp()
        last_activity_key = f'last_activity_{request.user.id}'
        
        # Get last activity from session
        last_activity = request.session.get(last_activity_key, now)
        
        # Calculate idle time
        idle_time = now - last_activity
        
        # Check if session should be expired
        if idle_time > self.idle_timeout:
            # Session expired - logout user
            logger.info(f"Session expired for user {request.user.id} due to {idle_time:.0f}s idle time")
            logout(request)
            request.session.flush()
        else:
            # Update last activity
            request.session[last_activity_key] = now
            request.session.modified = True
        
        response = self.get_response(request)
        
        # Add session timeout info to response headers
        if request.user.is_authenticated:
            remaining_time = self.idle_timeout - idle_time
            warning_threshold = self.warning_time
            
            response['X-Session-Timeout'] = str(self.idle_timeout)
            response['X-Session-Remaining'] = str(int(remaining_time))
            response['X-Session-Warning-Time'] = str(warning_threshold)
            response['X-Session-Idle-Time'] = str(int(idle_time))
        
        return response

