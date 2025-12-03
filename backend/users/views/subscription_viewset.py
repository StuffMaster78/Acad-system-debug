"""
ViewSet for managing client subscriptions.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError

from users.services.subscription_service import SubscriptionService
from users.serializers.subscriptions import (
    ClientSubscriptionSerializer,
    SubscriptionPreferenceSerializer,
    SubscriptionListSerializer,
    SubscribeRequestSerializer,
    UnsubscribeRequestSerializer,
    UpdateFrequencySerializer,
    UpdateChannelsSerializer,
)


class SubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet for managing client subscriptions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_service(self):
        """Get subscription service instance for current user."""
        return SubscriptionService(self.request.user)
    
    @action(detail=False, methods=['get'])
    def list_all(self, request):
        """
        List all available subscriptions with current status.
        
        GET /api/users/subscriptions/list-all/
        """
        try:
            service = self.get_service()
            subscriptions = service.get_all_subscriptions()
            
            # Convert to list format
            result = [
                {
                    'subscription_type': sub_type,
                    'is_subscribed': data['is_subscribed'],
                    'subscribed_at': data['subscribed_at'],
                    'unsubscribed_at': data['unsubscribed_at'],
                    'frequency': data['frequency'],
                    'preferred_channels': data['preferred_channels'],
                }
                for sub_type, data in subscriptions.items()
            ]
            
            serializer = SubscriptionListSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """
        Subscribe to a subscription type.
        
        POST /api/users/subscriptions/subscribe/
        Body: {
            "subscription_type": "newsletter",
            "frequency": "weekly",
            "preferred_channels": ["email", "in_app"]
        }
        """
        serializer = SubscribeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            subscription = service.subscribe(
                subscription_type=serializer.validated_data['subscription_type'],
                frequency=serializer.validated_data.get('frequency', 'immediate'),
                preferred_channels=serializer.validated_data.get('preferred_channels', [])
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        """
        Unsubscribe from a subscription type.
        
        POST /api/users/subscriptions/unsubscribe/
        Body: {
            "subscription_type": "newsletter"
        }
        """
        serializer = UnsubscribeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            subscription = service.unsubscribe(
                subscription_type=serializer.validated_data['subscription_type']
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['put'])
    def update_frequency(self, request):
        """
        Update subscription frequency.
        
        PUT /api/users/subscriptions/update-frequency/
        Body: {
            "subscription_type": "newsletter",
            "frequency": "daily"
        }
        """
        serializer = UpdateFrequencySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            subscription = service.update_frequency(
                subscription_type=serializer.validated_data['subscription_type'],
                frequency=serializer.validated_data['frequency']
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['put'])
    def update_channels(self, request):
        """
        Update preferred channels for a subscription.
        
        PUT /api/users/subscriptions/update-channels/
        Body: {
            "subscription_type": "newsletter",
            "preferred_channels": ["email", "push"]
        }
        """
        serializer = UpdateChannelsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            subscription = service.update_channels(
                subscription_type=serializer.validated_data['subscription_type'],
                preferred_channels=serializer.validated_data['preferred_channels']
            )
            
            result_serializer = ClientSubscriptionSerializer(subscription)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['get'])
    def preferences(self, request):
        """
        Get subscription preferences.
        
        GET /api/users/subscriptions/preferences/
        """
        try:
            service = self.get_service()
            prefs = service.get_preferences()
            return Response(prefs, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['put'])
    def update_preferences(self, request):
        """
        Update subscription preferences.
        
        PUT /api/users/subscriptions/update-preferences/
        Body: {
            "all_subscriptions_enabled": true,
            "marketing_consent": true,
            "email_enabled": true,
            "sms_enabled": false,
            "push_enabled": false,
            "in_app_enabled": true,
            "dnd_enabled": false,
            "dnd_start_hour": 22,
            "dnd_end_hour": 6
        }
        """
        serializer = SubscriptionPreferenceSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            preferences = service.update_preferences(**serializer.validated_data)
            
            result_serializer = SubscriptionPreferenceSerializer(preferences)
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))

