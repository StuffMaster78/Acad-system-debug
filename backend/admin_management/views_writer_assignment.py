"""
ViewSet for writer assignment with workload details.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg
from orders.models import Order
from writer_management.models import WriterProfile
from admin_management.permissions import IsAdmin

User = get_user_model()


class WriterAssignmentViewSet(viewsets.ViewSet):
    """
    ViewSet for getting writer details for assignment decisions.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='available-writers')
    def available_writers(self, request):
        """
        Get list of available writers with their workload and details.
        Optionally filter by order_id to get writers suitable for a specific order.
        Only returns writers for orders that are paid and in 'available' status.
        """
        order_id = request.query_params.get('order_id')
        order = None
        
        if order_id:
            try:
                order = Order.objects.select_related(
                    'client', 'assigned_writer', 'website',
                    'paper_type', 'academic_level', 'subject', 'type_of_work'
                ).get(id=order_id)
                
                # Check if order is paid and available for assignment
                if not order.is_paid:
                    return Response(
                        {"detail": "Only paid orders can be assigned to writers."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if order.status != 'available':
                    return Response(
                        {"detail": f"Order must be in 'available' status to be assigned. Current status: {order.status}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Order.DoesNotExist:
                return Response(
                    {"detail": "Order not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get all active writers
        writers = User.objects.filter(
            role='writer',
            is_active=True
        ).select_related('writer_profile').prefetch_related(
            'orders_as_writer'
        )
        
        # Get writer workload and details
        writer_list = []
        for writer in writers:
            try:
                profile = writer.writer_profile
            except WriterProfile.DoesNotExist:
                continue
            
            # Get current orders in progress
            active_orders = Order.objects.filter(
                assigned_writer=writer,
                status__in=['in_progress', 'revision_requested', 'revision_in_progress', 'on_revision']
            ).select_related('client', 'paper_type', 'academic_level', 'subject', 'type_of_work')
            
            # Get completed orders count (for rating calculation)
            completed_orders = Order.objects.filter(
                assigned_writer=writer,
                status='completed'
            ).count()
            
            # Get average rating from reviews
            from reviews_system.models.order_review import OrderReview
            avg_rating_result = OrderReview.objects.filter(
                order__assigned_writer=writer,
                order__status='completed'
            ).aggregate(avg_rating=Avg('rating'))
            avg_rating = avg_rating_result['avg_rating'] or 0
            
            # Get writer level info and max orders limit
            writer_level = None
            max_orders = 5  # Default limit
            if profile.writer_level:
                writer_level = {
                    'id': profile.writer_level.id,
                    'name': profile.writer_level.name,
                    'level': profile.writer_level.level,
                    'max_orders': profile.writer_level.max_orders or 5,
                }
                max_orders = profile.writer_level.max_orders or 5
            
            # Format active orders for display
            active_orders_list = []
            for o in active_orders[:10]:  # Limit to 10 most recent
                active_orders_list.append({
                    'id': o.id,
                    'topic': o.topic[:50] + '...' if len(o.topic) > 50 else o.topic,
                    'status': o.status,
                    'deadline': o.writer_deadline.isoformat() if o.writer_deadline else None,
                    'pages': getattr(o, 'number_of_pages', getattr(o, 'pages', 0)),
                    'paper_type': o.paper_type.name if o.paper_type else None,
                    'academic_level': o.academic_level.name if o.academic_level else None,
                })
            
            active_count = active_orders.count()
            capacity = max_orders - active_count  # Available slots
            
            writer_data = {
                'id': writer.id,
                'username': writer.username,
                'email': writer.email,
                'writer_id': f"WRTR{writer.id:06d}",  # Formatted ID
                'profile': {
                    'id': profile.id,
                    'rating': float(profile.average_rating) if profile.average_rating else 0,
                    'completed_orders': completed_orders,
                    'writer_level': writer_level,
                    'is_available': getattr(profile, 'is_available_for_auto_assignments', True),
                    'pen_name': getattr(profile, 'pen_name', None),
                },
                'workload': {
                    'active_orders_count': active_count,
                    'max_orders': max_orders,
                    'capacity': capacity,  # Available slots (max - active)
                    'active_orders': active_orders_list,
                    'avg_rating': round(avg_rating, 2),
                },
                'stats': {
                    'total_completed': completed_orders,
                    'on_time_completion_rate': getattr(profile, 'on_time_completion_rate', 0),
                }
            }
            
            writer_list.append(writer_data)
        
        # Sort writers by:
        # 1. Capacity (available slots) - higher capacity first
        # 2. Writer level (higher level first) - if level exists
        # 3. Active orders count (lower workload first)
        # 4. Rating (higher rating first) - as tiebreaker
        writer_list.sort(
            key=lambda w: (
                -w['workload']['capacity'],  # Higher capacity first (more available slots)
                -(w['profile']['writer_level']['level'] if w['profile']['writer_level'] else 0),  # Higher level first
                w['workload']['active_orders_count'],  # Lower workload first
                -w['profile']['rating'],  # Higher rating first (tiebreaker)
            )
        )
        
        return Response({
            'writers': writer_list,
            'order': {
                'id': order.id,
                'order_id': f"#{order.id:07d}",  # Formatted order ID
                'topic': order.topic,
                'paper_type': order.paper_type.name if order.paper_type else None,
                'academic_level': order.academic_level.name if order.academic_level else None,
                'pages': getattr(order, 'number_of_pages', getattr(order, 'pages', 0)),
            } if order else None
        })
    
    @action(detail=True, methods=['get'], url_path='workload')
    def writer_workload(self, request, pk=None):
        """
        Get detailed workload information for a specific writer.
        """
        try:
            writer = User.objects.get(id=pk, role='writer', is_active=True)
        except User.DoesNotExist:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            profile = writer.writer_profile
        except WriterProfile.DoesNotExist:
            return Response(
                {"detail": "Writer profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all active orders with details
        active_orders = Order.objects.filter(
            assigned_writer=writer,
            status__in=['in_progress', 'revision_requested', 'revision_in_progress', 'on_revision']
        ).select_related(
            'client', 'paper_type', 'academic_level', 'subject', 'type_of_work', 'website'
        ).order_by('-created_at')
        
        # Get pending requests
        from writer_management.models import WriterOrderRequest
        pending_requests = WriterOrderRequest.objects.filter(
            writer=profile,
            approved=False
        ).select_related('order').count()
        
        # Get recent completed orders
        recent_completed = Order.objects.filter(
            assigned_writer=writer,
            status='completed'
        ).select_related('client', 'paper_type').order_by('-submitted_at')[:5]
        
        return Response({
            'writer': {
                'id': writer.id,
                'writer_id': f"WRTR{writer.id:06d}",
                'username': writer.username,
                'email': writer.email,
                'rating': float(profile.rating) if profile.rating else 0,
                'writer_level': {
                    'name': profile.writer_level.name if profile.writer_level else None,
                    'level': profile.writer_level.level if profile.writer_level else None,
                } if profile.writer_level else None,
            },
            'workload': {
                'active_orders_count': active_orders.count(),
                'active_orders': [
                    {
                        'id': o.id,
                        'order_id': f"#{o.id:07d}",
                        'topic': o.topic,
                        'status': o.status,
                        'deadline': o.writer_deadline.isoformat() if o.writer_deadline else None,
                        'pages': getattr(o, 'number_of_pages', getattr(o, 'pages', 0)),
                        'paper_type': o.paper_type.name if o.paper_type else None,
                        'academic_level': o.academic_level.name if o.academic_level else None,
                        'client': {
                            'id': o.client.id,
                            'email': o.client.email if o.client else None,
                        } if o.client else None,
                        'created_at': o.created_at.isoformat() if o.created_at else None,
                    }
                    for o in active_orders
                ],
                'pending_requests': pending_requests,
                'recent_completed': [
                    {
                        'id': o.id,
                        'order_id': f"#{o.id:07d}",
                        'topic': o.topic,
                        'completed_at': o.submitted_at.isoformat() if o.submitted_at else None,
                    }
                    for o in recent_completed
                ],
            }
        })

