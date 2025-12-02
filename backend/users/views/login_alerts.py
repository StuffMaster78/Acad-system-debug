"""
Login Alert Preferences ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.login_alerts import LoginAlertPreference
from users.serializers.login_alerts import (
    LoginAlertPreferenceSerializer,
    LoginAlertPreferenceUpdateSerializer,
)


class LoginAlertPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing login alert preferences.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LoginAlertPreferenceSerializer
    
    def get_queryset(self):
        """Get preferences for current user."""
        return LoginAlertPreference.objects.filter(
            user=self.request.user,
            website=self.request.user.website
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return LoginAlertPreferenceUpdateSerializer
        return LoginAlertPreferenceSerializer
    
    def perform_create(self, serializer):
        """Create preference for current user."""
        serializer.save(
            user=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's login alert preferences."""
        try:
            preference = LoginAlertPreference.objects.get(
                user=request.user,
                website=request.user.website
            )
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        except LoginAlertPreference.DoesNotExist:
            # Return defaults
            return Response({
                'notify_new_login': True,
                'notify_new_device': True,
                'notify_new_location': True,
                'email_enabled': True,
                'push_enabled': False,
                'in_app_enabled': True,
            })

