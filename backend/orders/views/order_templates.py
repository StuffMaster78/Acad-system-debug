"""
Views for order templates.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from orders.models import OrderTemplate
from orders.serializers.order_templates import (
    OrderTemplateSerializer,
    OrderTemplateCreateSerializer,
    OrderFromTemplateSerializer
)
from orders.models import Order
from orders.serializers import OrderSerializer


class OrderTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing order templates.
    Clients can create, view, update, and delete their templates.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderTemplateSerializer
    
    def get_queryset(self):
        """Return templates for the current user."""
        queryset = OrderTemplate.objects.filter(client=self.request.user, is_active=True)
        
        # Filter by website if provided
        website_id = self.request.query_params.get('website')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        return queryset.order_by('-last_used_at', '-created_at')
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return OrderTemplateCreateSerializer
        return OrderTemplateSerializer
    
    def perform_create(self, serializer):
        """Set client and website on creation."""
        website_id = self.request.data.get('website') or self.request.user.website_id
        serializer.save(
            client=self.request.user,
            website_id=website_id
        )
    
    @action(detail=True, methods=['post'], url_path='create-order')
    def create_order_from_template(self, request, pk=None):
        """
        Create a new order from this template.
        
        POST /api/v1/orders/templates/{id}/create-order/
        """
        template = self.get_object()
        
        # Validate request
        serializer = OrderFromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Calculate deadlines
        if not data.get('client_deadline'):
            if template.preferred_deadline_days:
                client_deadline = timezone.now() + timedelta(days=template.preferred_deadline_days)
            else:
                # Default to 7 days
                client_deadline = timezone.now() + timedelta(days=7)
        else:
            client_deadline = data['client_deadline']
        
        if not data.get('writer_deadline'):
            # Writer deadline is typically 1 day before client deadline
            writer_deadline = client_deadline - timedelta(days=1)
        else:
            writer_deadline = data['writer_deadline']
        
        # Build order data from template
        order_data = {
            'client': request.user.id,
            'website': template.website.id,
            'topic': data.get('override_topic') or template.topic,
            'paper_type': template.paper_type.id if template.paper_type else None,
            'academic_level': template.academic_level.id if template.academic_level else None,
            'subject': template.subject.id if template.subject else None,
            'number_of_pages': data.get('override_pages') or template.number_of_pages,
            'order_instructions': data.get('custom_instructions') or template.order_instructions,
            'client_deadline': client_deadline.isoformat(),
            'writer_deadline': writer_deadline.isoformat(),
            'preferred_writer_id': template.preferred_writer_id,
        }
        
        # Create order using order serializer
        try:
            # Use the OrderSerializer to create the order
            order_serializer = OrderSerializer(data=order_data, context={'request': request})
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()
            
            # Mark template as used
            template.mark_used()
            
            return Response(
                {
                    'detail': 'Order created successfully from template',
                    'order': OrderSerializer(order, context={'request': request}).data,
                    'template': self.get_serializer(template).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'detail': f'Failed to create order: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='most-used')
    def most_used(self, request):
        """Get most frequently used templates."""
        templates = self.get_queryset().order_by('-usage_count', '-last_used_at')[:10]
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """Get recently used templates."""
        templates = self.get_queryset().filter(
            last_used_at__isnull=False
        ).order_by('-last_used_at')[:10]
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)

