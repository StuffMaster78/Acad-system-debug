"""
Tip-related views for writer management.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from writer_management.models.tipping import Tip
from writer_management.serializers import TipListSerializer, TipCreateSerializer, TipDetailSerializer


class TipViewSet(ModelViewSet):
    """
    ViewSet for managing tips.
    Supports creating tips (direct, order-based, class-based) and listing tips.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TipCreateSerializer
        elif self.action == 'retrieve':
            return TipDetailSerializer
        return TipListSerializer
    
    def get_queryset(self):
        user = self.request.user
        website = getattr(self.request, 'website', None)
        
        queryset = Tip.objects.all()
        
        if user.role == "client":
            queryset = queryset.filter(client=user)
        elif user.role == "writer":
            queryset = queryset.filter(writer=user)
        elif user.role not in ["admin", "superadmin"]:
            return Tip.objects.none()
        
        if website:
            queryset = queryset.filter(website=website)
        
        # Filter by tip type if provided
        tip_type = self.request.query_params.get('tip_type')
        if tip_type:
            queryset = queryset.filter(tip_type=tip_type)
        
        # Filter by order if provided
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by related entity if provided
        related_entity_type = self.request.query_params.get('related_entity_type')
        related_entity_id = self.request.query_params.get('related_entity_id')
        if related_entity_type:
            queryset = queryset.filter(related_entity_type=related_entity_type)
        if related_entity_id:
            queryset = queryset.filter(related_entity_id=related_entity_id)
        
        return queryset.select_related("writer", "client", "order", "writer_level", "payment")
    
    def perform_create(self, serializer):
        """Ensure the client is set from the request user."""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Process payment for a pending tip.
        """
        tip = self.get_object()
        
        # Only the client who sent the tip can process payment
        if tip.client != request.user and request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'You do not have permission to process this tip payment.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if tip.payment_status != 'pending':
            return Response(
                {'error': f'Tip payment is already {tip.payment_status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method', 'wallet')
        discount_code = request.data.get('discount_code')
        
        from writer_management.services.tip_service import TipService
        try:
            payment = TipService.process_tip_payment(
                tip=tip,
                payment_method=payment_method,
                discount_code=discount_code
            )
            return Response({
                'status': 'success',
                'payment_id': payment.id,
                'payment_status': payment.status,
                'tip_payment_status': tip.payment_status,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TipListView(generics.ListAPIView):
    """
    Legacy list view for backward compatibility.
    """
    serializer_class = TipListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        website = getattr(self.request, 'website', None)

        queryset = Tip.objects.all()
        
        if user.role == "client":
            queryset = queryset.filter(client=user)
        elif user.role == "writer":
            queryset = queryset.filter(writer=user)
        else:
            return Tip.objects.none()
        
        if website:
            queryset = queryset.filter(website=website)
        
        return queryset.select_related("writer", "client", "order", "writer_level")

