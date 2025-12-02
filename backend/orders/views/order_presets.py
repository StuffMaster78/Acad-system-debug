"""
Order Presets ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.order_presets import OrderPreset
from orders.serializers.order_presets import (
    OrderPresetSerializer,
    OrderPresetApplySerializer,
)


class OrderPresetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing order presets.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderPresetSerializer
    
    def get_queryset(self):
        """Get presets for current user."""
        queryset = OrderPreset.objects.filter(
            client=self.request.user,
            website=self.request.user.website,
            is_active=True
        ).select_related(
            'default_type_of_work', 'default_english_type', 'preferred_writer'
        ).prefetch_related('default_extra_services')
        
        return queryset.order_by('-is_default', '-usage_count', '-updated_at')
    
    def perform_create(self, serializer):
        """Create preset for current user."""
        serializer.save(
            client=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=True, methods=['post'], url_path='apply')
    def apply_preset(self, request, pk=None):
        """Apply preset to a draft or order."""
        preset = self.get_object()
        serializer = OrderPresetApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_type = serializer.validated_data['target_type']
        target_id = serializer.validated_data.get('target_id')
        
        try:
            if target_type == 'draft':
                from orders.order_drafts import OrderDraft
                
                if target_id:
                    draft = OrderDraft.objects.get(
                        id=target_id,
                        client=request.user,
                        website=request.user.website
                    )
                else:
                    # Create new draft
                    draft = OrderDraft.objects.create(
                        client=request.user,
                        website=request.user.website
                    )
                
                preset.apply_to_draft(draft)
                
                from orders.serializers.order_drafts import OrderDraftSerializer
                draft_serializer = OrderDraftSerializer(draft, context={'request': request})
                
                return Response({
                    'message': 'Preset applied to draft',
                    'draft': draft_serializer.data,
                })
            
            elif target_type == 'order':
                from orders.models import Order
                
                if not target_id:
                    return Response(
                        {'error': 'target_id is required for orders'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                order = Order.objects.get(
                    id=target_id,
                    client=request.user,
                    website=request.user.website
                )
                
                preset.apply_to_order(order)
                
                from orders.serializers import OrderSerializer
                order_serializer = OrderSerializer(order, context={'request': request})
                
                return Response({
                    'message': 'Preset applied to order',
                    'order': order_serializer.data,
                })
        
        except Exception as e:
            return Response(
                {'error': f'Failed to apply preset: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='default')
    def get_default(self, request):
        """Get default preset for current user."""
        try:
            preset = OrderPreset.objects.get(
                client=request.user,
                website=request.user.website,
                is_default=True,
                is_active=True
            )
            serializer = self.get_serializer(preset)
            return Response(serializer.data)
        except OrderPreset.DoesNotExist:
            return Response(
                {'message': 'No default preset found'},
                status=status.HTTP_404_NOT_FOUND
            )

