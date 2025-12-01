"""
Unified authentication ViewSet for login/logout.
Production-grade with security features.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.exceptions import ValidationError

from authentication.services.auth_service import AuthenticationService
from authentication.serializers import LoginSerializer, RegisterSerializer
from authentication.utils.ip import get_client_ip
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings


class LoginThrottle(AnonRateThrottle):
    """Rate limiting for login attempts."""
    rate = '5/minute'


class AuthenticationViewSet(viewsets.ViewSet):
    """
    Unified authentication ViewSet.
    Handles login, logout, token refresh, and 2FA verification.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate user and return JWT tokens.
        
        Request body:
        {
            "email": "user@example.com",
            "password": "password123",
            "remember_me": false
        }
        
        Response:
        {
            "access_token": "...",
            "refresh_token": "...",
            "user": {...},
            "session_id": "...",
            "expires_in": 3600
        }
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)
        
        # Get device info
        device_info = {
            'ip_address': get_client_ip(request),
            'user_agent': request.headers.get('User-Agent', ''),
            'device_name': request.data.get('device_name'),
        }
        
        try:
            result = AuthenticationService.login(
                request=request,
                email=email,
                password=password,
                remember_me=remember_me,
                device_info=device_info
            )
            
            # Handle 2FA requirement
            if result.get('requires_2fa'):
                return Response(result, status=status.HTTP_202_ACCEPTED)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            error_traceback = traceback.format_exc()
            logger.error(f"Login error: {e}\n{error_traceback}")
            # Return detailed error in development
            error_detail = {
                "error": "An error occurred during login.",
                "detail": str(e) if settings.DEBUG else None,
            }
            if settings.DEBUG:
                error_detail["traceback"] = error_traceback
            return Response(
                error_detail,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='verify-2fa', permission_classes=[AllowAny])
    def verify_2fa(self, request):
        """
        Verify 2FA code and complete login.
        
        Request body:
        {
            "user_id": 123,
            "session_id": "...",
            "totp_code": "123456"
        }
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_id = request.data.get('user_id')
        session_id = request.data.get('session_id')
        totp_code = request.data.get('totp_code')
        
        if not all([user_id, session_id, totp_code]):
            return Response(
                {"error": "user_id, session_id, and totp_code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            result = AuthenticationService.verify_2fa(
                user=user,
                session_id=session_id,
                totp_code=totp_code
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout user and invalidate session/tokens.
        
        Query params:
        - logout_all: If true, logout from all devices
        """
        logout_all = request.query_params.get('logout_all', 'false').lower() == 'true'
        
        try:
            result = AuthenticationService.logout(
                request=request,
                user=request.user,
                logout_all=logout_all
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Logout error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during logout."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        """
        Register a new user account.
        
        Request body:
        {
            "username": "johndoe",
            "email": "user@example.com",
            "password": "password123"
        }
        
        Response:
        {
            "message": "Registration successful. Please check your email for activation."
        }
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Ensure user is saved to database
                if not user.pk:
                    return Response(
                        {"error": "Failed to create user account."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Handle referral code from request data or query parameters
                referral_code = request.data.get("referral_code") or request.query_params.get("ref")
                if referral_code:
                    # Store in session for later use (when user activates account)
                    request.session['referral_code'] = referral_code
                    request.session.save()
                
                # Record referral if code is provided (for immediate activation)
                if referral_code and user.is_active:
                    try:
                        from referrals.services.referral_service import ReferralService
                        ReferralService.record_referral_for_user(user, request)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Referral recording error (non-blocking): {e}", exc_info=True)
                
                # Create activation token
                token = default_token_generator.make_token(user)
                activation_url = f"{settings.FRONTEND_URL or 'http://localhost:5173'}/activate/{token}/?email={user.email}"
                if referral_code:
                    activation_url += f"&ref={referral_code}"
                
                # Send activation email (fail silently in development)
                try:
                    if settings.DEFAULT_FROM_EMAIL:
                        send_mail(
                            'Activate your account',
                            f'Please click the link to activate your account: {activation_url}',
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=True,  # Changed to True to not block registration
                        )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Registration email error (non-blocking): {e}", exc_info=True)
                    # Don't fail registration if email fails
                
                return Response(
                    {
                        "message": "Registration successful. Please check your email for activation." if settings.DEFAULT_FROM_EMAIL else "Registration successful. You can now log in.",
                        "user_id": user.id,
                        "email": user.email,
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Registration error: {e}", exc_info=True)
                return Response(
                    {"error": f"Registration failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='refresh-token', permission_classes=[AllowAny])
    def refresh_token(self, request):
        """
        Refresh access token using refresh token.
        
        Request body:
        {
            "refresh_token": "..."
        }
        """
        refresh_token_str = request.data.get('refresh_token')
        
        if not refresh_token_str:
            return Response(
                {"error": "refresh_token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = AuthenticationService.refresh_token(refresh_token_str)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change password for authenticated user.
        
        Request body:
        {
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        Response:
        {
            "message": "Password changed successfully."
        }
        """
        from django.contrib.auth import update_session_auth_hash
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return Response(
                {"error": "current_password, new_password, and confirm_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify current password
        if not request.user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new password matches confirmation
        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirmation do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new password is same as current
        if request.user.check_password(new_password):
            return Response(
                {"error": "New password must be different from current password."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new password strength
        try:
            validate_password(new_password, user=request.user)
        except DjangoValidationError as e:
            return Response(
                {"error": "Password validation failed.", "details": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        try:
            request.user.set_password(new_password)
            request.user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, request.user)
            
            # Log password change
            from authentication.models.audit import AuditLog
            from authentication.utils.ip import get_client_ip
            AuditLog.objects.create(
                user=request.user,
                website=getattr(request, 'website', None),
                event="password_changed",
                ip_address=get_client_ip(request),
                device=request.headers.get('User-Agent', '')
            )
            
            # Send notification if enabled
            try:
                from notifications_system.services.core import NotificationService
                from websites.models import Website
                
                # Get user's website or use a default
                user_website = getattr(request.user, 'website', None)
                if not user_website:
                    try:
                        user_website = Website.objects.first()
                    except:
                        pass
                
                if user_website:
                    NotificationService.send_notification(
                        user=request.user,
                        event="password.changed",
                        payload={
                            "title": "Password Changed",
                            "message": "Your password has been successfully changed. If this wasn't you, please contact support immediately."
                        },
                        website=user_website,
                        category="security",
                        priority_label="normal"
                    )
            except Exception as e:
                # Log but don't fail if notification fails
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to send password change notification: {e}", exc_info=True)
            
            return Response(
                {"message": "Password changed successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Password change error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred while changing password."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='user', permission_classes=[IsAuthenticated])
    def get_user(self, request):
        """
        Get current authenticated user profile from database.
        
        Response:
        {
            "id": 1,
            "email": "user@example.com",
            "username": "username",
            "full_name": "John Doe",
            "role": "client",
            ...
        }
        """
        from users.views import UserViewSet
        from users.serializers import (
            ClientProfileSerializer, WriterProfileSerializer,
            EditorProfileSerializer, SupportProfileSerializer,
            AdminProfileSerializer, SuperadminProfileSerializer
        )
        # Import profile models from their respective apps
        from client_management.models import ClientProfile
        from writer_management.models import WriterProfile
        from editor_management.models import EditorProfile
        from support_management.models import SupportProfile
        from django.shortcuts import get_object_or_404
        from rest_framework.exceptions import PermissionDenied
        
        user = request.user
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (user.__class__, AdminProfileSerializer),
            "superadmin": (user.__class__, SuperadminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            if user.role in ["admin", "superadmin"]:
                # For admin/superadmin, serialize the user directly
                serializer = serializer_class(user)
            else:
                # For other roles, get the profile instance
                profile_instance = get_object_or_404(profile_model, user=user)
                serializer = serializer_class(profile_instance)
            return Response(serializer.data)

        raise PermissionDenied("Invalid role or unauthorized access.")
    
    @action(detail=False, methods=['patch', 'put'], url_path='user', permission_classes=[IsAuthenticated])
    def update_user(self, request):
        """
        Update current authenticated user profile.
        Updates are saved to the database.
        
        Request body:
        {
            "username": "newusername",
            "first_name": "John",
            "last_name": "Doe",
            ...
        }
        
        Response:
        {
            "message": "Profile updated successfully.",
            "user": {...}
        }
        """
        from users.models import ProfileUpdateRequest
        
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

        # Auto-approve basic updates - save to database
        # Separate User fields from UserProfile fields
        from users.models import UserProfile
        
        user_updates = {}
        profile_updates = {}
        
        # UserProfile fields that can be updated
        profile_fields = ['phone_number', 'bio', 'avatar', 'country', 'state', 'profile_picture']
        
        if auto_approve_updates:
            for field, value in auto_approve_updates.items():
                if field in profile_fields:
                    profile_updates[field] = value
                elif hasattr(user, field):
                    user_updates[field] = value
            
            # Update User model fields
            if user_updates:
                for field, value in user_updates.items():
                    setattr(user, field, value)
                user.save(update_fields=list(user_updates.keys()))
            
            # Update UserProfile fields
            if profile_updates:
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={}
                )
                for field, value in profile_updates.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
                profile.save(update_fields=list(profile_updates.keys()))

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
                ProfileUpdateRequest.objects.create(
                    user=user,
                    website=user_website,
                    requested_data=admin_approval_updates
                )
            else:
                # If no website available, just log a warning
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Cannot create ProfileUpdateRequest for user {user.id}: no website available")
            return Response({
                "message": "Profile updated. Some changes require admin approval.",
                "user": self._get_user_data(user)
            })

        # Return updated user data from database
        return Response({
            "message": "Profile updated successfully.",
            "user": self._get_user_data(user)
        })
    
    def _get_user_data(self, user):
        """Helper method to get user data for response."""
        from users.views import UserViewSet
        from users.serializers import (
            ClientProfileSerializer, WriterProfileSerializer,
            EditorProfileSerializer, SupportProfileSerializer,
            AdminProfileSerializer, SuperadminProfileSerializer
        )
        from users.models import (
            ClientProfile, WriterProfile, EditorProfile, SupportProfile
        )
        from django.shortcuts import get_object_or_404
        
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (user.__class__, AdminProfileSerializer),
            "superadmin": (user.__class__, SuperadminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            if user.role in ["admin", "superadmin"]:
                serializer = serializer_class(user)
            else:
                try:
                    profile_instance = profile_model.objects.get(user=user)
                    serializer = serializer_class(profile_instance)
                except profile_model.DoesNotExist:
                    # Return basic user data if profile doesn't exist
                    return {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "role": user.role,
                    }
            return serializer.data
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
        }

