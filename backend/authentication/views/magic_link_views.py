"""
Magic Link Authentication Views - Passwordless login endpoints.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from authentication.services.magic_link_service import MagicLinkService
from websites.utils import get_current_website


class MagicLinkViewSet(viewsets.ViewSet):
    """
    ViewSet for magic link (passwordless) authentication.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='request')
    def request_magic_link(self, request):
        """
        Request a magic link for passwordless login.
        
        Request body:
        {
            "email": "user@example.com"
        }
        
        Response:
        {
            "message": "Magic link sent to your email",
            "expires_in": 900,
            "expires_at": "2025-12-01T10:30:00Z"
        }
        """
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        website = get_current_website(request)
        if not website:
            return Response(
                {"error": "Website not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = MagicLinkService.send_magic_link(
                email=email,
                website=website,
                request=request
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Failed to send magic link. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_magic_link(self, request):
        """
        Verify magic link token and authenticate user.
        
        Request body:
        {
            "token": "uuid-token-here"
        }
        
        Response:
        {
            "access": "jwt-access-token",
            "refresh": "jwt-refresh-token",
            "user": {...},
            "session_id": "..."
        }
        """
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = MagicLinkService.verify_magic_link(token, request)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Invalid or expired magic link"},
                status=status.HTTP_400_BAD_REQUEST
            )

