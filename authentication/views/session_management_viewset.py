# authentication/viewsets/session_management_viewset.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from authentication.models.login import LoginSession
from authentication.models.logout import LogoutEvent
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from django.shortcuts import get_object_or_404

from authentication.models.sessions import UserSession
from authentication.serializers import UserSessionSerializer
from authentication.serializers import LoginSessionSerializer


class SessionManagementThrottle(UserRateThrottle):
    """
    Custom throttle for session management endpoints.
    Allows more frequent requests for status/extend endpoints.
    Increased significantly to handle activity tracking scripts.
    """
    rate = '5000/hour'  # 5000 requests per hour = ~83 per minute (significantly increased for activity tracking)


class SessionManagementViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SessionManagementThrottle]

    @action(detail=False, methods=["post"])
    def kick_others(self, request):
        """
        Ends all other active sessions except the current one.
        """
        user = request.user
        current_token = request.auth  # Assuming JWT or session token

        sessions = LoginSession.objects.filter(
            user=user,
            website=user.website,
            is_active=True
        ).exclude(token=current_token)

        for session in sessions:
            from authentication.services.logout_event_service import LogoutEventService
            LogoutEventService.log_event(
                user=user,
                website=user.website,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                session_key=session.token,
                reason="kick_other_sessions"
            )
            session.is_active = False
            session.save()

        return Response(
            {"detail": "All other sessions have been logged out."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["get"])
    def current_sessions(self, request):
        """
        List active login sessions for the current user.
        """
        user = request.user
        sessions = LoginSession.objects.filter(
            user=user,
            website=user.website,
            is_active=True
        )
        serializer = LoginSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], throttle_classes=[SessionManagementThrottle])
    def status(self, request):
        """
        Get current session status including remaining time and warning status.
        Used for idle timeout detection.
        Optimized for frequent polling - lightweight and fast.
        
        Returns:
        {
            "is_active": true,
            "remaining_seconds": 1800,
            "idle_seconds": 0,
            "warning_threshold": 300,
            "should_warn": false,
            "timeout_seconds": 1800
        }
        """
        from django.conf import settings
        from django.utils import timezone
        from django.core.cache import cache
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            user = request.user
            
            # Get timeout settings
            idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 30 * 60)  # 30 minutes
            warning_time = getattr(settings, 'SESSION_WARNING_TIME', 5 * 60)  # 5 minutes
            
            # Try to get from cache first (cache for 30 seconds to reduce DB load and rate limit hits)
            cache_key = f'session_status_{user.id}'
            cached_status = cache.get(cache_key)
            if cached_status:
                return Response(cached_status, status=status.HTTP_200_OK)
            
            # Get last activity from session
            last_activity_key = f'last_activity_{user.id}'
            last_activity = request.session.get(last_activity_key, timezone.now().timestamp())
            
            # Calculate times
            now = timezone.now().timestamp()
            idle_seconds = int(now - last_activity)
            remaining_seconds = max(0, idle_timeout - idle_seconds)
            should_warn = remaining_seconds <= warning_time and remaining_seconds > 0
            
            response_data = {
                "is_active": True,
                "remaining_seconds": remaining_seconds,
                "idle_seconds": idle_seconds,
                "warning_threshold": warning_time,
                "should_warn": should_warn,
                "timeout_seconds": idle_timeout,
                "last_activity": last_activity,
            }
            
            # Cache for 30 seconds to reduce load on frequent polling and prevent rate limiting
            cache.set(cache_key, response_data, 30)
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting session status: {e}", exc_info=True)
            # Return safe default on error
            return Response({
                "is_active": True,
                "remaining_seconds": 1800,
                "idle_seconds": 0,
                "warning_threshold": 300,
                "should_warn": False,
                "timeout_seconds": 1800,
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], throttle_classes=[SessionManagementThrottle])
    def extend(self, request):
        """
        Extend session by updating last activity timestamp.
        This resets the idle timer.
        
        Returns:
        {
            "message": "Session extended",
            "remaining_seconds": 1800
        }
        """
        from django.conf import settings
        from django.utils import timezone
        from django.core.cache import cache
        
        user = request.user
        
        # Update last activity
        now = timezone.now().timestamp()
        last_activity_key = f'last_activity_{user.id}'
        request.session[last_activity_key] = now
        request.session.modified = True
        
        # Clear status cache so next status check gets fresh data
        cache_key = f'session_status_{user.id}'
        cache.delete(cache_key)
        
        # Get timeout settings
        idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 30 * 60)
        
        return Response({
            "message": "Session extended successfully",
            "remaining_seconds": idle_timeout,
            "extended_at": now,
        }, status=status.HTTP_200_OK)

    

class ActiveSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve active sessions for the authenticated user."""
        sessions = UserSession.objects.filter(user=request.user)
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        """Log out a specific session by session_id."""
        session = get_object_or_404(UserSession, id=session_id, user=request.user)

        if session.session_key == request.session.session_key:
            return Response(
                {"error": "You can't log out of your current session."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.delete()
        return Response({"message": "Session logged out successfully."}, status=status.HTTP_200_OK)


class LogoutAllSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Log out all sessions except the current one."""
        UserSession.objects.filter(user=request.user).exclude(
            session_key=request.session.session_key
        ).delete()
        return Response({"message": "All other sessions have been logged out."}, status=status.HTTP_200_OK)