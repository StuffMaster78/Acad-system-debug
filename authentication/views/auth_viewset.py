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
                
                # Create activation token
                token = default_token_generator.make_token(user)
                activation_url = f"{settings.FRONTEND_URL or 'http://localhost:5173'}/activate/{token}/?email={user.email}"
                
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

