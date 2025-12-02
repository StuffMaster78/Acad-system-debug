"""
Order Drafts ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from orders.order_drafts import OrderDraft
from orders.serializers.order_drafts import (
    OrderDraftSerializer,
    OrderDraftCreateSerializer,
    OrderDraftConvertSerializer,
)
from orders.services.order_service import OrderService
from orders.services.pricing_calculator import PricingCalculatorService


class OrderDraftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing order drafts.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDraftSerializer
    
    def get_queryset(self):
        """Get drafts for current user."""
        queryset = OrderDraft.objects.filter(
            client=self.request.user,
            website=self.request.user.website
        ).select_related(
            'type_of_work', 'english_type', 'preferred_writer', 'converted_to_order'
        ).prefetch_related('extra_services')
        
        # Filter by is_quote if provided
        is_quote = self.request.query_params.get('is_quote')
        if is_quote is not None:
            queryset = queryset.filter(is_quote=is_quote.lower() == 'true')
        
        # Search by title or topic
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(topic__icontains=search)
            )
        
        return queryset.order_by('-updated_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return OrderDraftCreateSerializer
        return OrderDraftSerializer
    
    def perform_create(self, serializer):
        """Create draft for current user."""
        serializer.save(
            client=self.request.user,
            website=self.request.user.website
        )
    
    @action(detail=True, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request, pk=None):
        """Calculate estimated price for draft."""
        draft = self.get_object()
        
        if not draft.number_of_pages:
            return Response(
                {'error': 'Number of pages is required to calculate price'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create temporary order data for price calculation
            order_data = {
                'website': draft.website,
                'client': draft.client,
                'number_of_pages': draft.number_of_pages,
                'number_of_slides': draft.number_of_slides,
                'number_of_refereces': draft.number_of_refereces,
                'type_of_work': draft.type_of_work,
                'english_type': draft.english_type,
                'deadline': draft.deadline,
            }
            
            # Calculate price
            calculator = PricingCalculatorService()
            estimated_price = calculator.calculate_total_price(**order_data)
            
            # Update draft
            draft.estimated_price = estimated_price
            draft.save(update_fields=['estimated_price'])
            
            return Response({
                'estimated_price': str(estimated_price),
                'currency': draft.website.currency or 'USD',
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to calculate price: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='convert-to-order')
    def convert_to_order(self, request, pk=None):
        """Convert draft to actual order."""
        draft = self.get_object()
        
        if draft.converted_to_order:
            return Response(
                {'error': 'This draft has already been converted to an order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderDraftConvertSerializer(
            data=request.data,
            context={'draft': draft, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            order = draft.convert_to_order()
            
            # Calculate price if requested
            if serializer.validated_data.get('calculate_price', True):
                calculator = PricingCalculatorService()
                order.total_price = calculator.calculate_total_price(
                    website=order.website,
                    client=order.client,
                    number_of_pages=order.number_of_pages,
                    number_of_slides=order.number_of_slides,
                    number_of_refereces=order.number_of_refereces,
                    type_of_work=order.type_of_work,
                    english_type=order.english_type,
                    deadline=order.deadline,
                )
                order.save(update_fields=['total_price'])
            
            from orders.serializers import OrderSerializer
            order_serializer = OrderSerializer(order, context={'request': request})
            
            return Response({
                'message': 'Draft converted to order successfully',
                'order': order_serializer.data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to convert draft: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['patch'], url_path='update-last-viewed')
    def update_last_viewed(self, request, pk=None):
        """Update last viewed timestamp."""
        draft = self.get_object()
        from django.utils import timezone
        draft.last_viewed_at = timezone.now()
        draft.save(update_fields=['last_viewed_at'])
        
        return Response({'message': 'Last viewed updated'})

