import logging
import requests
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import action, throttle_classes
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity  # Fuzzy Search
from rest_framework.pagination import PageNumberPagination
from users.utils import send_deletion_confirmation_email, send_unlock_email, send_security_alert
from django.core.mail import send_mail
from users.models import (
    User, ProfileUpdateRequest,
)
from authentication.models import (
    AccountDeletionRequest, SecureToken, UserSession
)
from users.utils import (
    notify_mfa_enabled, notify_mfa_disabled, notify_mfa_reset,
    send_mfa_recovery_email
)
from audit_logging.services.audit_log_service import AuditLogService

from .serializers import (
    UserActivitySerializer,
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    SuperadminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
    UserProfileSerializer,
    ImpersonateSerializer,
)
from client_management.models import ClientProfile
from writer_management.models.profile import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from superadmin_management.models import SuperadminProfile
from admin_management.models import AdminProfile
from websites.models import Website
from users.utils import get_client_ip, generate_otp, send_otp_email, send_otp_sms, verify_totp
from django.utils.timezone import now, timedelta
from users.utils import get_client_ip, get_device_info
from django.http import JsonResponse
from datetime import timedelta
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import base64
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.utils.timezone import now, timedelta
import base64
from .utils import generate_totp_qr_code, send_unlock_email
from users.utils import store_active_token, revoke_token, is_token_revoked
from io import BytesIO
from authentication.throttling import LoginRateThrottle, MagicLinkThrottle
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
import uuid
import pytz
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

def check_admin_access(user):
    if not user.is_authenticated or user.role not in ["admin", "superadmin"]:
        raise PermissionDenied("You do not have admin access.")



class CustomUserPagination(PageNumberPagination):
    """Pagination settings for user listings."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """Handles user-related operations including profile, impersonation, and activity"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination  # Enable pagination
    serializer_class = UserProfileSerializer  # Default serializer
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def update_online_status(self, request):
        """Update the current user's online status."""
        from django.utils.timezone import now
        user = request.user
        current_time = now()
        
        if hasattr(user, 'writer_profile'):
            user.writer_profile.last_active = current_time
            user.writer_profile.save(update_fields=['last_active'])
        elif hasattr(user, 'client_profile'):
            user.client_profile.last_online = current_time
            user.client_profile.save(update_fields=['last_online'])
        
        if hasattr(user, 'user_main_profile'):
            user.user_main_profile.last_active = current_time
            user.user_main_profile.save(update_fields=['last_active'])
        
        return Response({
            "status": "online",
            "last_active": current_time.isoformat()
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_online_statuses(self, request):
        """Get online status for multiple users."""
        from django.utils.timezone import now
        from datetime import timedelta
        
        user_ids = request.query_params.get('user_ids', '').split(',')
        user_ids = [int(uid) for uid in user_ids if uid.strip().isdigit()]
        
        if not user_ids:
            return Response({"error": "user_ids parameter required"}, status=400)
        
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
        """Get online status and timezone info for a specific user."""
        from django.utils.timezone import now
        from datetime import timedelta
        import pytz
        
        try:
            target_user = User.objects.select_related(
                'writer_profile', 'client_profile', 'user_main_profile'
            ).get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        timezone_str = "UTC"
        if hasattr(target_user, 'writer_profile'):
            timezone_str = target_user.writer_profile.timezone or "UTC"
        elif hasattr(target_user, 'client_profile'):
            timezone_str = target_user.client_profile.timezone or "UTC"
        elif hasattr(target_user, 'detected_timezone'):
            timezone_str = target_user.detected_timezone or "UTC"
        
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
        
        try:
            tz = pytz.timezone(timezone_str)
            local_time = now().astimezone(tz)
            hour = local_time.hour
            is_daytime = 6 <= hour < 20
        except Exception:
            is_daytime = True
            local_time = None
        
        return Response({
            "user_id": target_user.id,
            "is_online": is_online,
            "last_active": last_active.isoformat() if last_active else None,
            "timezone": timezone_str,
            "is_daytime": is_daytime,
            "local_time": local_time.isoformat() if local_time else None
        })

    def get_serializer_class(self):
        """Dynamically return the correct serializer based on the user role."""
        from users.serializers.privacy import get_privacy_aware_serializer
        
        role_serializers = {
            "client": ClientProfileSerializer,
            "writer": WriterProfileSerializer,
            "editor": EditorProfileSerializer,
            "support": SupportProfileSerializer,
            "admin": AdminProfileSerializer,
            "superadmin": SuperadminProfileSerializer,
        }
        role = self.request.user.role
        if role not in role_serializers:
            raise ValueError(f"Unknown role: {role}")
        
        base_serializer = role_serializers.get(role, UserProfileSerializer)
        
        # Apply privacy masking for detail views
        if self.action == 'retrieve' and self.request.user:
            # Get the target user being viewed
            if hasattr(self, 'get_object'):
                try:
                    target_user = self.get_object()
                    privacy_serializer = get_privacy_aware_serializer(
                        target_user.role,
                        self.request.user.role,
                        self.request.user
                    )
                    if privacy_serializer:
                        return privacy_serializer
                except Exception:
                    pass
        
        return base_serializer

    # user = User.objects.select_related("writer_profile", "client_profile").get(id=request.user.id)


    def get_queryset(self):
        """Restrict access based on user roles."""
        user = self.request.user

        # Optimize queryset with select_related to prevent N+1 queries
        base_queryset = User.objects.all().select_related(
            'website',
            'notification_profile',
        ).prefetch_related(
            'user_main_profile',
        )

        if user.role in ["client", "writer"]:
            return base_queryset.filter(id=user.id)  # Clients & Writers only see themselves

        elif user.role == "editor":
            return base_queryset.filter(role="writer")  # Editors only see writers

        elif user.role == "support":
            return base_queryset.filter(role="client")  # Support staff only see clients

        return base_queryset  # Admins & Superadmins see all users



    def list(self, request, *args, **kwargs):
        """List users with filtering, search, sorting, and pagination."""
        
        check_admin_access(request.user)

        # Filters
        role = request.query_params.get("role")
        search_query = request.query_params.get("search")
        sort_by = request.query_params.get("sort")

        # Validate role filter
        allowed_roles = ["client", "writer", "editor", "support", "admin", "superadmin"]
        if role and role not in allowed_roles:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        # Get queryset based on role
        users = User.objects.filter(role=role) if role else User.objects.all()
        
        # Track if similarity has been annotated
        has_similarity = False

        # Apply search filter if provided
        if search_query:
            direct_matches = users.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )

            if direct_matches.exists():
                users = direct_matches
            else:
                # Use fuzzy search with trigram similarity
                users = users.annotate(similarity=TrigramSimilarity("username", search_query)).filter(similarity__gt=0.3)
                has_similarity = True
        else:
            # No search query, use base queryset
            pass

        # Sorting - only order by similarity if it was annotated
        if has_similarity:
            users = users.order_by("-similarity")
        elif sort_by:
            sorting_options = {
                "newest": "-date_joined",
                "oldest": "date_joined",
                "alphabetical": "username",
                "reverse-alphabetical": "-username",
                "last-active": "-last_active",
            }
            if sort_by in sorting_options:
                users = users.order_by(sorting_options[sort_by])
        else:
            # Default sorting when no search and no sort_by
            users = users.order_by("-date_joined")

        # Paginate results
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request, view=self)
        
        # Apply privacy-aware serialization
        from users.serializers.privacy import get_privacy_aware_serializer
        serializer_class = self.get_serializer_class()
        
        # For list view, apply privacy masking based on viewer role
        if request.user.role not in ['admin', 'superadmin']:
            serialized_data = []
            for user in paginated_users:
                privacy_serializer = get_privacy_aware_serializer(
                    user.role,
                    request.user.role,
                    request.user
                )
                if privacy_serializer:
                    serialized_data.append(privacy_serializer(user).data)
                else:
                    serialized_data.append(serializer_class(user).data)
            return paginator.get_paginated_response(serialized_data)
        
        return paginator.get_paginated_response(serializer_class(paginated_users, many=True).data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific user's profile with privacy masking."""
        from users.serializers.privacy import get_privacy_aware_serializer
        
        instance = self.get_object()
        serializer_class = self.get_serializer_class()
        
        # Apply privacy masking if needed
        if request.user.role not in ['admin', 'superadmin']:
            privacy_serializer = get_privacy_aware_serializer(
                instance.role,
                request.user.role,
                request.user
            )
            if privacy_serializer:
                serializer = privacy_serializer(instance)
                return Response(serializer.data)
        
        serializer = serializer_class(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_tokens(self, request):
        """Retrieve all active tokens for the logged-in user."""
        tokens = SecureToken.objects.filter(user=request.user, is_active=True).order_by("-created_at")
        token_data = [
            {
                "id": token.id,
                "purpose": token.purpose,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "is_active": token.is_active,
            }
            for token in tokens
        ]
        return Response({"active_tokens": token_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_update(self, request, pk=None):
        """Allows clients & writers to request a profile update."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request updates for your own profile.")

        requested_data = request.data
        ProfileUpdateRequest.objects.create(user=user, requested_data=requested_data)

        return Response({"message": "Profile update request submitted successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_deletion(self, request, pk=None):
        """Allows clients & writers to request account deletion."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATE)
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        # Notify admins
        admin_emails = User.objects.filter(role="admin").values_list("email", flat=True)
        send_mail(
            "New Account Deletion Request",
            f"User {user.email} has requested account deletion. Please review.",
            settings.DEFAULT_FROM_EMAIL,
            list(admin_emails),
            fail_silently=False,
        )

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Retrieve the authenticated user's profile with optimized queries.
        Uses select_related and prefetch_related to minimize database hits.
        """
        from django.core.cache import cache
        from django.utils.decorators import method_decorator
        from django.views.decorators.cache import cache_page
        from django.views.decorators.vary import vary_on_headers
        
        user = request.user
        
        # Cache key based on user ID and role
        cache_key = f"user_profile_{user.id}_{user.role}"
        cached_data = cache.get(cache_key)
        
        # Return cached data if available (5 minute cache)
        if cached_data:
            return Response(cached_data)
        
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (User, AdminProfileSerializer),
            "superadmin": (User, AdminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            # Optimize queries based on role
            try:
                if user.role == "client":
                    profile_instance = ClientProfile.objects.select_related(
                        'user', 'user__user_main_profile', 'website'
                    ).prefetch_related(
                        'user__notification_profile'
                    ).get(user=user)
                elif user.role == "writer":
                    profile_instance = WriterProfile.objects.select_related(
                        'user', 'user__user_main_profile', 'website', 'writer_level'
                    ).prefetch_related(
                        'user__notification_profile'
                    ).get(user=user)
                elif user.role == "editor":
                    profile_instance = EditorProfile.objects.select_related(
                        'user', 'user__user_main_profile', 'website'
                    ).prefetch_related(
                        'user__notification_profile'
                    ).get(user=user)
                elif user.role == "support":
                    profile_instance = SupportProfile.objects.select_related(
                        'user', 'user__user_main_profile', 'website'
                    ).prefetch_related(
                        'user__notification_profile'
                    ).get(user=user)
                else:
                    # Admin/Superadmin - no separate profile model
                    profile_instance = user
            except (ClientProfile.DoesNotExist, WriterProfile.DoesNotExist, 
                    EditorProfile.DoesNotExist, SupportProfile.DoesNotExist):
                raise PermissionDenied("Profile not found for this user.")
            
            serializer = serializer_class(profile_instance)
            data = serializer.data
            
            # Cache the response for 5 minutes
            cache.set(cache_key, data, 300)
            
            return Response(data)

        raise PermissionDenied("Invalid role or unauthorized access.")

    @action(detail=False, methods=['patch', 'put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """
        Update the authenticated user's profile with cache invalidation.
        Handles profile_picture uploads separately since it's on UserProfile, not the role-specific profile.
        """
        from django.core.cache import cache
        from users.models import UserProfile
        # User is already imported at the top of the file
        
        user = request.user
        
        # Invalidate cache
        cache_key = f"user_profile_{user.id}_{user.role}"
        cache.delete(cache_key)
        
        # Handle profile_picture upload separately (it's on UserProfile, not role-specific profile)
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            # Get or create UserProfile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            # Update profile_picture
            user_profile.profile_picture = profile_picture
            user_profile.save(update_fields=['profile_picture'])
            # Refresh from database to get the updated URL
            user_profile.refresh_from_db()
        
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (User, AdminProfileSerializer),
            "superadmin": (User, AdminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            if user.role in ["admin", "superadmin"]:
                profile_instance = user
            else:
                # Use select_related to ensure user_main_profile is loaded
                profile_instance = get_object_or_404(
                    profile_model.objects.select_related('user', 'user__user_main_profile'),
                    user=user
                )
            
            # Remove profile_picture from request.data if it was handled above
            # (to avoid serializer errors)
            # For multipart/form-data, request.data is a QueryDict which needs special handling
            if profile_picture and 'profile_picture' in request.data:
                # Create a mutable copy of request.data
                from django.http import QueryDict
                if isinstance(request.data, QueryDict):
                    serializer_data = request.data.copy()
                    serializer_data.pop('profile_picture', None)
                else:
                    serializer_data = dict(request.data)
                    serializer_data.pop('profile_picture', None)
            else:
                serializer_data = request.data
            
            serializer = serializer_class(profile_instance, data=serializer_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Invalidate cache after update
                cache.delete(cache_key)
                
                # Re-fetch the instance with related objects to ensure avatar_url is calculated correctly
                if user.role in ["admin", "superadmin"]:
                    # For admin/superadmin, refresh user with user_main_profile
                    # User is already imported at the top of the file
                    profile_instance = User.objects.select_related('user_main_profile').get(pk=user.pk)
                else:
                    # Re-fetch with select_related to ensure relationships are loaded
                    profile_instance = profile_model.objects.select_related(
                        'user', 'user__user_main_profile'
                    ).get(pk=profile_instance.pk)
                
                # Re-serialize with fresh data to ensure avatar_url is included
                updated_serializer = serializer_class(profile_instance)
                
                # Return updated serializer data
                return Response(updated_serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raise PermissionDenied("Invalid role or unauthorized access.")
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def location_info(self, request):
        """
        Get user's location information including country.
        Returns:
        - User-selected country (from UserProfile)
        - Detected country (from User.detected_country or real-time detection)
        - Current session country (from UserSession if available)
        - Current IP address
        """
        user = request.user
        ip_address = get_client_ip(request)
        
        # Get user-selected country from UserProfile
        user_profile = getattr(user, 'user_main_profile', None)
        user_selected_country = None
        if user_profile:
            user_selected_country = str(user_profile.country) if user_profile.country else None
        
        # Get detected country from User model (GeoDetectionMixin)
        detected_country = user.detected_country
        
        # Try to detect country from current IP if not already detected
        current_country = None
        current_timezone = None
        if ip_address:
            try:
                # Use the existing auto_detect_country method
                # This will update user.detected_country if not set
                if not detected_country:
                    user.auto_detect_country(request)
                    user.refresh_from_db()
                    detected_country = user.detected_country
                    current_timezone = user.detected_timezone
                
                # Also get real-time country from IP for current session
                try:
                    response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        current_country = data.get("country", None)
                        if not current_timezone:
                            current_timezone = data.get("timezone", None)
                except requests.RequestException:
                    pass
            except Exception as e:
                logger.warning(f"Failed to detect country from IP: {e}")
        
        # Get country from current session if available
        session_country = None
        try:
            from authentication.models import UserSession
            session_key = request.session.session_key
            if session_key:
                user_session = UserSession.objects.filter(
                    user=user,
                    session_key=session_key,
                    is_active=True
                ).first()
                if user_session:
                    session_country = user_session.country
        except Exception as e:
            logger.warning(f"Failed to get session country: {e}")
        
        return Response({
            "ip_address": ip_address,
            "user_selected_country": user_selected_country,
            "detected_country": detected_country,
            "current_country": current_country or detected_country,
            "session_country": session_country,
            "timezone": current_timezone or user.detected_timezone,
            "country_source": (
                "user_selected" if user_selected_country else
                "session" if session_country else
                "detected" if detected_country else
                "current_ip" if current_country else
                "unknown"
            )
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='update-timezone')
    def update_timezone(self, request):
        """
        Update the user's timezone based on client/browser detection.

        - Accepts an IANA timezone string (e.g., \"America/New_York\").
        - Validates the timezone.
        - Persists it on the appropriate role profile (client or writer).
        - Also updates `detected_timezone` on the User model if present.
        """
        timezone_str = request.data.get('timezone')

        if not timezone_str or not isinstance(timezone_str, str):
            return Response(
                {"error": "Field 'timezone' is required and must be a string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        timezone_str = timezone_str.strip()
        try:
            # Validate that it's a known timezone
            pytz.timezone(timezone_str)
        except Exception:
            return Response(
                {"error": "Invalid timezone identifier."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        updated_fields = []

        # Update role-specific profiles if present
        if hasattr(user, 'client_profile'):
            user.client_profile.timezone = timezone_str
            user.client_profile.save(update_fields=['timezone'])
            updated_fields.append('client_profile')

        if hasattr(user, 'writer_profile'):
            user.writer_profile.timezone = timezone_str
            user.writer_profile.save(update_fields=['timezone'])
            updated_fields.append('writer_profile')

        # Also update detected_timezone if the field exists on the User model
        if hasattr(user, 'detected_timezone'):
            user.detected_timezone = timezone_str
            user.save(update_fields=['detected_timezone'])
            updated_fields.append('detected_timezone')

        return Response(
            {
                "timezone": timezone_str,
                "updated": bool(updated_fields),
                "updated_fields": updated_fields,
            },
            status=status.HTTP_200_OK,
        )

    @method_decorator(ratelimit(key="user", rate="3/m", method="POST", block=True))
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def impersonate(self, request, pk=None):
        """
        DEPRECATED: Use /api/v1/auth/impersonate/create_token/ instead.
        
        This method is kept for backward compatibility but creates a token
        using the new token-based impersonation system.
        """
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)
        
        # Use new token-based impersonation system
        from websites.utils import get_current_website
        from authentication.services.impersonation_service import ImpersonationService
        
        website = get_current_website(request)
        
        try:
            # Check if admin can impersonate
            can_impersonate, reason = ImpersonationService.can_impersonate(request.user, target_user)
            if not can_impersonate:
                return Response(
                    {"error": reason},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate impersonation token
            token_obj = ImpersonationService.generate_token(
                admin_user=request.user,
                target_user=target_user,
                website=website,
                expires_hours=1
            )
            
            # Log impersonation action
            AuditLogService.log_auto(request.user, "USER_IMPERSONATION", request)
            
            return Response({
                "token": token_obj.token,
                "expires_at": token_obj.expires_at,
                "message": "Use this token with /api/v1/auth/impersonate/start/ to begin impersonation.",
                "impersonation_url": "/api/v1/auth/impersonate/start/"
            }, status=status.HTTP_201_CREATED)
            
        except (PermissionDenied, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
    def stop_impersonation(self, request, pk=None):
        """Stops impersonation of a user."""
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if not target_user.is_impersonated:
            return Response({"error": "User is not being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.stop_impersonation()
        return Response({"message": "Impersonation stopped."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def activity(self, request, pk=None):
        """Fetches user activity logs."""
        check_admin_access(request.user)

        user = get_object_or_404(User, id=pk)
        serializer = UserActivitySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unlock_user(self, request, pk=None):
        """Admin manually unlocks a locked user account."""
        user = get_object_or_404(User, id=pk)
        if not user.is_locked:
            return Response({"message": "User is not locked."}, status=status.HTTP_400_BAD_REQUEST)

        user.unlock_account()
        return Response({"message": "User account has been unlocked."}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """Returns a list of active sessions for the logged-in user."""
        sessions = UserSession.objects.filter(user=request.user).order_by("-last_active")
        session_data = [
            {
                "session_key": session.session_key,
                "ip_address": session.ip_address,
                "device": session.device,
                "login_time": session.login_time,
                "last_active": session.last_active,
                "expires_at": session.expires_at,
            }
            for session in sessions
        ]
        return Response({"active_sessions": session_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def logout_session(self, request, pk=None):
        """Allows a user to log out from a specific session."""
        session = get_object_or_404(UserSession, session_key=pk, user=request.user)
        session.delete()  # Ends session
        return Response({"message": "Session logged out successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path="terminate-session")
    def terminate_session(self, request, pk=None):
        """Terminates a specific session for the user."""
        session = get_object_or_404(UserSession, id=pk, user=request.user, is_active=True)
        if not session:
            return Response({"error": "Session not found or already logged out."}, status=404)
        session.terminate()
        return Response({"message": "Session terminated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def force_logout_all(self, request):
        """Admin can log out all users from all sessions."""
        current_admin_session = request.session.session_key
        UserSession.objects.exclude(session_key=current_admin_session).delete()
        return Response({"message": "All user sessions have been terminated, except the current admin.."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout_all_sessions(self, request):
        """Terminates all active sessions for the user."""
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        
        for session in sessions:
            session.terminate()
        
        return Response({"message": "All sessions terminated successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="logout-from-all-devices")
    def logout_from_all_devices(self, request):
        """
        Logs out the user from all devices except the current session.
        """
        current_session = request.session.session_key
        request.user.sessions.exclude(session_key=current_session).update(is_active=False)
        
        for session in request.user.sessions.exclude(session_key=current_session):
            session.terminate()

        return Response({"message": "Logged out from all devices except the current one."})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def admin_terminate_all_sessions(self, request, pk=None):
        """Admin forcibly logs out all sessions of a user."""
        user = get_object_or_404(User, id=pk)
        sessions = UserSession.objects.filter(user=user, is_active=True)

        for session in sessions:
            session.terminate()

        return Response({"message": f"All sessions for {user.email} terminated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="expire-old-sessions")
    def expire_old_sessions(self, request):
        """
        Automatically expires sessions inactive for more than 24 hours.
        """
        expired_sessions = request.user.sessions.filter(last_activity__lt=now() - timedelta(hours=24))
        count = expired_sessions.count()

        for session in expired_sessions:
            session.terminate()

        return Response({"message": f"{count} expired sessions have been removed."})


class AccountDeletionRequestViewSet(viewsets.ViewSet):
    """Handles user account deletion requests."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser], url_path='list')
    def list_requests(self, request):
        """Admin/Superadmin can view all account deletion requests."""
        from users.serializers import AccountDeletionRequestSerializer
        
        status_filter = request.query_params.get('status', None)
        queryset = AccountDeletionRequest.objects.all().select_related('user', 'website').order_by('-request_time')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = AccountDeletionRequestSerializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "requests": serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """Clients, Writers, Support, and Editors can request account deletion.
        Admin and Superadmin accounts cannot be deleted."""
        user = request.user
        
        # Prevent admin and superadmin from requesting deletion
        if user.role in ['admin', 'superadmin']:
            return Response({
                "error": "Admin and Superadmin accounts cannot be deleted. Please contact system administrator."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Only allow clients, writers, support, and editors
        if user.role not in ['client', 'writer', 'support', 'editor']:
            return Response({
                "error": "Account deletion is not available for your role."
            }, status=status.HTTP_403_FORBIDDEN)
        
        if user.is_frozen:
            return Response({"error": "Your account is already scheduled for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get("reason", "No reason provided")
        website = getattr(user, 'website', None) or Website.objects.first()
        
        if not website:
            return Response({
                "error": "Unable to process deletion request. Please contact support."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        AccountDeletionRequest.objects.create(user=user, website=website, reason=reason)
        user.freeze_account()

        return Response({"message": "Your account is now frozen and scheduled for deletion in 3 months."}, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def confirm_deletion(self, request, pk=None):
        """Confirms the account deletion request and freezes the account."""
        user = get_object_or_404(User, id=pk)

        # Ensure the request exists and is pending confirmation
        deletion_request = AccountDeletionRequest.objects.filter(user=user, status="Pending Confirmation").first()
        if not deletion_request:
            return Response({"error": "No pending deletion request found."}, status=status.HTTP_400_BAD_REQUEST)

        # Freeze account and update request status
        user.freeze_account()
        deletion_request.status = "confirmed"
        deletion_request.save()

        return Response({"message": "Account deletion confirmed. Your account is now frozen for 3 months."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_deletion(self, request, pk=None):
        """Admin/Superadmin approves account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")

        # Log admin action
        logger.info(f"Admin {request.user.email} approved deletion for {deletion_request.user.email}")

        deletion_request.status = "confirmed"
        deletion_request.confirmation_time = now()
        deletion_request.save()

        # Freeze the user
        deletion_request.user.freeze_account()

        return Response({"message": "Account deletion request approved. Account is now frozen."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject_deletion(self, request, pk=None):
        """Admin/Superadmin rejects account deletion request."""
        deletion_request = get_object_or_404(
            AccountDeletionRequest,
            id=pk,
            status="pending"
        )
        reason = request.data.get("reason", "No reason provided")
        deletion_request.status = "rejected"
        deletion_request.admin_response = reason
        deletion_request.rejection_time = now()
        deletion_request.save()

        # Unfreeze the user if they were frozen
        if deletion_request.user.is_frozen:
            deletion_request.user.cancel_deletion()

        return Response({"message": "Account deletion request rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reinstate_account(self, request, pk=None):
        """Admin/Superadmin reinstates a frozen account."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk)
        user = deletion_request.user
        
        if not user.is_frozen:
            return Response({"error": "Account is not frozen."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.cancel_deletion()
        deletion_request.status = "rejected"
        deletion_request.admin_response = "Account reinstated by admin"
        deletion_request.rejection_time = now()
        deletion_request.save()

        logger.info(f"Admin {request.user.email} reinstated account for {user.email}")
        return Response({"message": "User account has been reinstated."}, status=status.HTTP_200_OK)

class AdminProfileRequestViewSet(viewsets.ViewSet):
    """Allows admins to review and approve/reject profile update and deletion requests."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve_update(self, request, pk=None):
        """Approve a profile update request."""
        update_request = get_object_or_404(ProfileUpdateRequest, id=pk, status="pending")
        update_request.approve()
        return Response({"message": "Profile update approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_update(self, request, pk=None):
        """Reject a profile update request."""
        update_request = get_object_or_404(
            ProfileUpdateRequest,
            id=pk,
            status="pending"
        )
        reason = request.data.get("reason")
        update_request.reject(reason)
        return Response({"message": "Profile update rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve_deletion(self, request, pk=None):
        """Approve an account deletion request."""
        deletion_request = get_object_or_404(
            AccountDeletionRequest,
            id=pk,
            status="pending"
        )
        deletion_request.approve()
        return Response({"message": "Account deletion approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_deletion(self, request, pk=None):
        """Reject an account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        reason = request.data.get("reason")
        deletion_request.reject(reason)
        return Response({"message": "Account deletion rejected."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        """
        Allows users to update their profile. 
        - Basic updates (bio, phone number, avatar) are auto-approved.
        - Sensitive updates (email, role, website) require admin approval.
        """
        user = request.user
        update_fields = request.data

        # Fields that require admin approval
        admin_approval_fields = ["email", "role", "website"]

        # Separate updates
        auto_approve_updates = {}
        admin_approval_updates = {}

        for field, value in update_fields.items():
            if field in admin_approval_fields:
                admin_approval_updates[field] = value
            else:
                auto_approve_updates[field] = value

        # Auto-approve basic updates
        for field, value in auto_approve_updates.items():
            setattr(user, field, value)
        user.save()

        # Store admin approval request if necessary
        if admin_approval_updates:
            # Get user's website or use a default
            user_website = getattr(user, 'website', None)
            if not user_website:
                # Try to get website from user's profile or use first available
                from websites.models import Website
                try:
                    user_website = Website.objects.first()
                except:
                    pass
            
            if user_website:
                ProfileUpdateRequest.objects.create(user=user, website=user_website, requested_data=admin_approval_updates)
            else:
                # If no website available, just log a warning
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Cannot create ProfileUpdateRequest for user {user.id}: no website available")
            return Response({"message": "Profile updated. Some changes require admin approval."})

        return Response({"message": "Profile updated successfully."})

    @action(detail=False, methods=["get"], url_path="profile-update-requests", permission_classes=[IsAuthenticated])
    def get_update_requests(self, request):
        """
        Allows users to view their pending profile update requests.
        """
        try:
            # Use the correct related_name: update_requests_users
            from users.models import ProfileUpdateRequest
            requests = ProfileUpdateRequest.objects.filter(
                user=request.user,
                status="pending"
            ).values('id', 'requested_data', 'status', 'admin_response', 'created_at', 'updated_at')
            return Response({"pending_requests": list(requests)})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fetching profile update requests: {e}", exc_info=True)
            return Response({"pending_requests": [], "error": "Failed to fetch update requests"})
class AdminUserManagementViewSet(viewsets.ViewSet):
    """Allows admins to manage user accounts."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def restore_archived_account(self, request, pk=None):
        """Restores an archived account."""
        user = get_object_or_404(User, id=pk, is_archived=True)
        user.is_archived = False
        user.is_active = True
        user.save()

        return Response({"message": "User account restored successfully."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="2/m", method="POST", block=True))    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Admin suspends a user."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "No reason provided")
        user.suspension_start_date = now()
        user.suspension_end_date = now() + timedelta(days=30)  # Default 30-day suspension
        user.save()

        logger.info(f"Admin {request.user.email} suspended {user.email}")
        return Response({"message": "User suspended."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def lift_suspension(self, request, pk=None):
        """Admin lifts a user's suspension."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = False
        user.suspension_reason = None
        user.suspension_start_date = None
        user.suspension_end_date = None
        user.save()

        logger.info(f"Admin {request.user.email} lifted suspension for {user.email}")
        return Response({"message": "User suspension lifted."}, status=status.HTTP_200_OK)

# Moved to Auth
    # @action(detail=True, methods=['post'])
    # def force_reset_password(self, request, pk=None):
    #     """Admin forces a user to reset their password."""
    #     user = get_object_or_404(User, id=pk)
    #     new_password = "TemporaryPass123"  # Generate a secure random password in production
    #     user.set_password(new_password)
    #     user.save()

    #     send_mail(
    #         "Your Password Has Been Reset",
    #         f"Your new temporary password is: {new_password}. Please change it after login.",
    #         "no-reply@yourdomain.com",
    #         [user.email]
    #     )

    #     logger.info(f"Admin {request.user.email} forced password reset for {user.email}")
    #     return Response({"message": "User password has been reset and emailed to them."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="1/m", method="POST", block=True))
    @action(detail=False, methods=['get'])
    def user_reports(self, request):
        """Admin gets reports on user activities."""
        active_users = User.objects.filter(is_active=True).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        pending_deletion = AccountDeletionRequest.objects.filter(status="pending").count()

        return Response({
            "total_users": User.objects.count(),
            "active_users": active_users,
            "suspended_users": suspended_users,
            "pending_deletion_requests": pending_deletion
        }, status=status.HTTP_200_OK)