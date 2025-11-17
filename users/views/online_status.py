"""
Online status tracking views for users.
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from django.db.models import Q
from datetime import timedelta
import pytz


class OnlineStatusMixin:
    """
    Mixin to add online status tracking functionality to ViewSets.
    """
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_online_status(self, request):
        """
        Update the current user's online status.
        Called periodically by the frontend to keep status current.
        Optimized with caching to reduce database writes.
        """
        from django.core.cache import cache
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            user = request.user
            current_time = now()
            
            # Cache check - only update DB if last update was > 30 seconds ago
            cache_key = f'online_status_update_{user.id}'
            last_update = cache.get(cache_key)
            
            if last_update:
                # Skip if updated recently (within 30 seconds)
                return Response({
                    "status": "online",
                    "last_active": current_time.isoformat(),
                    "cached": True
                })
            
            # Update last_active based on role
            try:
                if hasattr(user, 'writer_profile'):
                    user.writer_profile.last_active = current_time
                    user.writer_profile.save(update_fields=['last_active'])
                elif hasattr(user, 'client_profile'):
                    user.client_profile.last_online = current_time
                    user.client_profile.save(update_fields=['last_online'])
                
                # Also update UserProfile if it exists
                if hasattr(user, 'user_main_profile'):
                    user.user_main_profile.last_active = current_time
                    user.user_main_profile.save(update_fields=['last_active'])
                
                # Cache for 30 seconds to prevent excessive DB writes
                cache.set(cache_key, current_time.isoformat(), 30)
            except Exception as e:
                logger.error(f"Error updating online status: {e}", exc_info=True)
            
            return Response({
                "status": "online",
                "last_active": current_time.isoformat()
            })
        except Exception as e:
            logger.error(f"Unexpected error in update_online_status: {e}", exc_info=True)
            return Response({
                "status": "online",
                "last_active": now().isoformat()
            }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_online_statuses(self, request):
        """
        Get online status for multiple users.
        Query params: user_ids (comma-separated list of user IDs)
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_ids = request.query_params.get('user_ids', '').split(',')
        user_ids = [int(uid) for uid in user_ids if uid.strip().isdigit()]
        
        if not user_ids:
            return Response({"error": "user_ids parameter required"}, status=400)
        
        # Consider user online if last_active is within last 5 minutes
        online_threshold = now() - timedelta(minutes=5)
        
        statuses = {}
        users = User.objects.filter(id__in=user_ids).select_related(
            'writer_profile', 'client_profile', 'user_main_profile'
        )
        
        for user in users:
            last_active = None
            is_online = False
            
            if hasattr(user, 'writer_profile') and user.writer_profile.last_active:
                last_active = user.writer_profile.last_active
                is_online = last_active >= online_threshold
            elif hasattr(user, 'client_profile') and user.client_profile.last_online:
                last_active = user.client_profile.last_online
                is_online = last_active >= online_threshold
            elif hasattr(user, 'user_main_profile') and user.user_main_profile.last_active:
                last_active = user.user_main_profile.last_active
                is_online = last_active >= online_threshold
            
            statuses[user.id] = {
                "is_online": is_online,
                "last_active": last_active.isoformat() if last_active else None
            }
        
        return Response(statuses)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_user_online_status(self, request, pk=None):
        """
        Get online status and timezone info for a specific user.
        Includes day/night indicator based on user's timezone.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            target_user = User.objects.select_related(
                'writer_profile', 'client_profile', 'user_main_profile'
            ).get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        # Get timezone
        timezone_str = "UTC"
        if hasattr(target_user, 'writer_profile'):
            timezone_str = target_user.writer_profile.timezone or "UTC"
        elif hasattr(target_user, 'client_profile'):
            timezone_str = target_user.client_profile.timezone or "UTC"
        elif hasattr(target_user, 'user_main_profile'):
            # Try to get from user's detected timezone
            timezone_str = getattr(target_user, 'detected_timezone', None) or "UTC"
        
        # Get last active
        last_active = None
        is_online = False
        online_threshold = now() - timedelta(minutes=5)
        
        if hasattr(target_user, 'writer_profile') and target_user.writer_profile.last_active:
            last_active = target_user.writer_profile.last_active
            is_online = last_active >= online_threshold
        elif hasattr(target_user, 'client_profile') and target_user.client_profile.last_online:
            last_active = target_user.client_profile.last_online
            is_online = last_active >= online_threshold
        elif hasattr(target_user, 'user_main_profile') and target_user.user_main_profile.last_active:
            last_active = target_user.user_main_profile.last_active
            is_online = last_active >= online_threshold
        
        # Calculate day/night based on timezone
        try:
            tz = pytz.timezone(timezone_str)
            local_time = now().astimezone(tz)
            hour = local_time.hour
            is_daytime = 6 <= hour < 20  # Daytime: 6 AM to 8 PM
        except Exception:
            is_daytime = True  # Default to daytime if timezone parsing fails
        
        return Response({
            "user_id": target_user.id,
            "is_online": is_online,
            "last_active": last_active.isoformat() if last_active else None,
            "timezone": timezone_str,
            "is_daytime": is_daytime,
            "local_time": local_time.isoformat() if 'local_time' in locals() else None
        })

