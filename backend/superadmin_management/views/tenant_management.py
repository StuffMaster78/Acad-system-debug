"""
Superadmin Multi-Tenant Management Endpoints

This module provides comprehensive tenant (website) management endpoints for superadmins.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from superadmin_management.permissions import IsSuperadmin
from websites.models import Website
from websites.serializers import WebsiteSerializer
from orders.models import Order, Dispute
from orders.order_enums import OrderStatus
from users.models import User
from order_payments_management.models import OrderPayment


class SuperadminTenantManagementViewSet(viewsets.ViewSet):
    """Multi-tenant management endpoints for superadmins."""
    permission_classes = [IsAuthenticated, IsSuperadmin]
    
    @action(detail=False, methods=['get'])
    def list_tenants(self, request):
        """List all tenants/websites."""
        websites = Website.objects.all().order_by('-created_at' if hasattr(Website, 'created_at') else '-id')
        
        # Get query parameters
        is_active = request.query_params.get('is_active', None)
        is_deleted = request.query_params.get('is_deleted', None)
        search = request.query_params.get('search', None)
        
        # Apply filters
        if is_active is not None:
            websites = websites.filter(is_active=is_active.lower() == 'true')
        
        if is_deleted is not None:
            websites = websites.filter(is_deleted=is_deleted.lower() == 'true')
        else:
            # By default, exclude deleted websites
            websites = websites.filter(is_deleted=False)
        
        if search:
            websites = websites.filter(
                Q(name__icontains=search) | 
                Q(domain__icontains=search) |
                Q(slug__icontains=search)
            )
        
        serializer = WebsiteSerializer(websites, many=True)
        
        # Get summary stats
        total_tenants = Website.objects.filter(is_deleted=False).count()
        active_tenants = Website.objects.filter(is_active=True, is_deleted=False).count()
        inactive_tenants = Website.objects.filter(is_active=False, is_deleted=False).count()
        deleted_tenants = Website.objects.filter(is_deleted=True).count()
        
        return Response({
            'tenants': serializer.data,
            'count': len(serializer.data),
            'summary': {
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'inactive_tenants': inactive_tenants,
                'deleted_tenants': deleted_tenants,
            }
        })
    
    @action(detail=False, methods=['post'])
    def create_tenant(self, request):
        """Create a new tenant/website."""
        serializer = WebsiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        website = serializer.save()
        
        # Log the action
        from superadmin_management.models import SuperadminLog
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Tenant Created",
            action_details=f"Created tenant: {website.name} ({website.domain})"
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def tenant_details(self, request, pk=None):
        """Get detailed information about a specific tenant."""
        website = get_object_or_404(Website, id=pk)
        
        # Get tenant statistics
        user_count = User.objects.filter(website=website).count()
        order_count = Order.objects.filter(website=website).count()
        total_revenue = OrderPayment.objects.filter(
            order__website=website,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get recent activity (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_orders = Order.objects.filter(
            website=website,
            created_at__gte=month_ago
        ).count()
        
        new_users = User.objects.filter(
            website=website,
            date_joined__gte=month_ago
        ).count()
        
        serializer = WebsiteSerializer(website)
        
        return Response({
            'tenant': serializer.data,
            'statistics': {
                'user_count': user_count,
                'order_count': order_count,
                'total_revenue': str(total_revenue),
                'recent_orders_30d': recent_orders,
                'new_users_30d': new_users,
            }
        })
    
    @action(detail=True, methods=['put', 'patch'])
    def update_tenant(self, request, pk=None):
        """Update a tenant/website."""
        website = get_object_or_404(Website, id=pk)
        serializer = WebsiteSerializer(website, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log the action
        from superadmin_management.models import SuperadminLog
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Tenant Updated",
            action_details=f"Updated tenant: {website.name} ({website.domain})"
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def delete_tenant(self, request, pk=None):
        """Soft delete a tenant/website."""
        website = get_object_or_404(Website, id=pk)
        
        # Soft delete
        website.soft_delete()
        
        # Log the action
        from superadmin_management.models import SuperadminLog
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Tenant Deleted",
            action_details=f"Deleted tenant: {website.name} ({website.domain})"
        )
        
        return Response(
            {"message": f"Tenant {website.name} has been deleted."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def restore_tenant(self, request, pk=None):
        """Restore a soft-deleted tenant."""
        website = get_object_or_404(Website, id=pk)
        
        if not website.is_deleted:
            return Response(
                {"error": "Tenant is not deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        website.restore()
        
        # Log the action
        from superadmin_management.models import SuperadminLog
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Tenant Restored",
            action_details=f"Restored tenant: {website.name} ({website.domain})"
        )
        
        serializer = WebsiteSerializer(website)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='analytics')
    def tenant_analytics(self, request, pk=None):
        """Get analytics for a specific tenant."""
        website = get_object_or_404(Website, id=pk)
        
        # Time range
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # User growth
        user_growth = User.objects.filter(
            website=website,
            date_joined__gte=date_from
        ).extra(
            select={'day': "DATE(date_joined)"}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Order trends
        order_trends = Order.objects.filter(
            website=website,
            created_at__gte=date_from
        ).extra(
            select={'day': "DATE(created_at)"}
        ).values('day').annotate(
            count=Count('id'),
            revenue=Sum('total_price', filter=Q(is_paid=True))
        ).order_by('day')
        
        # Revenue breakdown
        revenue_by_status = Order.objects.filter(
            website=website,
            created_at__gte=date_from
        ).values('status').annotate(
            count=Count('id'),
            revenue=Sum('total_price', filter=Q(is_paid=True))
        )
        
        # Top clients
        top_clients = User.objects.filter(
            website=website,
            role='client',
            orders_as_client__is_paid=True
        ).annotate(
            total_spent=Sum('orders_as_client__total_price', filter=Q(orders_as_client__is_paid=True)),
            order_count=Count('orders_as_client', filter=Q(orders_as_client__is_paid=True))
        ).order_by('-total_spent')[:10]
        
        # Top writers
        top_writers = User.objects.filter(
            website=website,
            role='writer',
            orders_as_writer__status=OrderStatus.COMPLETED.value
        ).annotate(
            completed_orders=Count('orders_as_writer', filter=Q(orders_as_writer__status=OrderStatus.COMPLETED.value)),
            total_earnings=Sum('orders_as_writer__writer_compensation', filter=Q(orders_as_writer__status=OrderStatus.COMPLETED.value))
        ).order_by('-completed_orders')[:10]
        
        return Response({
            'user_growth': [
                {
                    'date': item['day'].isoformat() if item['day'] else None,
                    'count': item['count']
                }
                for item in user_growth
            ],
            'order_trends': [
                {
                    'date': item['day'].isoformat() if item['day'] else None,
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0)
                }
                for item in order_trends
            ],
            'revenue_by_status': [
                {
                    'status': item['status'],
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0)
                }
                for item in revenue_by_status
            ],
            'top_clients': [
                {
                    'id': client.id,
                    'username': client.username,
                    'email': client.email,
                    'total_spent': str(client.total_spent or 0),
                    'order_count': client.order_count
                }
                for client in top_clients
            ],
            'top_writers': [
                {
                    'id': writer.id,
                    'username': writer.username,
                    'email': writer.email,
                    'completed_orders': writer.completed_orders,
                    'total_earnings': str(writer.total_earnings or 0)
                }
                for writer in top_writers
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='comparison')
    def tenant_comparison(self, request):
        """Compare all tenants side-by-side."""
        websites = Website.objects.filter(is_deleted=False)
        
        # Get comparison metrics
        comparison_data = []
        for website in websites:
            user_count = User.objects.filter(website=website).count()
            order_count = Order.objects.filter(website=website).count()
            total_revenue = OrderPayment.objects.filter(
                order__website=website,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Recent activity (last 30 days)
            month_ago = timezone.now() - timedelta(days=30)
            recent_orders = Order.objects.filter(
                website=website,
                created_at__gte=month_ago
            ).count()
            
            new_users = User.objects.filter(
                website=website,
                date_joined__gte=month_ago
            ).count()
            
            comparison_data.append({
                'id': website.id,
                'name': website.name,
                'domain': website.domain,
                'is_active': website.is_active,
                'user_count': user_count,
                'order_count': order_count,
                'total_revenue': str(total_revenue),
                'recent_orders_30d': recent_orders,
                'new_users_30d': new_users,
                'avg_order_value': str(total_revenue / order_count) if order_count > 0 else '0',
            })
        
        return Response({
            'tenants': comparison_data,
            'count': len(comparison_data)
        })
    
    @action(detail=False, methods=['get'], url_path='cross-tenant-analytics')
    def cross_tenant_analytics(self, request):
        """Get cross-tenant analytics comparing all tenants."""
        websites = Website.objects.filter(is_deleted=False)
        
        # Time range
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Aggregate metrics across all tenants
        cross_tenant_data = []
        
        for website in websites:
            # User metrics
            user_count = User.objects.filter(website=website).count()
            new_users = User.objects.filter(
                website=website,
                date_joined__gte=date_from
            ).count()
            
            # Order metrics
            orders = Order.objects.filter(website=website, created_at__gte=date_from)
            order_count = orders.count()
            completed_orders = orders.filter(status=OrderStatus.COMPLETED.value).count()
            
            # Revenue metrics
            revenue = OrderPayment.objects.filter(
                order__website=website,
                order__created_at__gte=date_from,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Average order value
            avg_order_value = orders.filter(is_paid=True).aggregate(
                avg=Avg('total_price')
            )['avg'] or 0
            
            # Completion rate
            completion_rate = (completed_orders / order_count * 100) if order_count > 0 else 0
            
            # Dispute metrics
            disputes = Dispute.objects.filter(
                order__website=website,
                created_at__gte=date_from
            )
            dispute_count = disputes.count()
            dispute_resolution_rate = (disputes.filter(dispute_status='resolved').count() / dispute_count * 100) if dispute_count > 0 else 0
            
            # Ticket metrics
            from tickets.models import Ticket
            tickets = Ticket.objects.filter(
                website=website,
                created_at__gte=date_from
            )
            ticket_count = tickets.count()
            ticket_resolution_rate = (tickets.filter(status='closed').count() / ticket_count * 100) if ticket_count > 0 else 0
            
            cross_tenant_data.append({
                'tenant_id': website.id,
                'tenant_name': website.name,
                'domain': website.domain,
                'is_active': website.is_active,
                'metrics': {
                    'users': {
                        'total': user_count,
                        'new_this_period': new_users,
                    },
                    'orders': {
                        'total': order_count,
                        'completed': completed_orders,
                        'completion_rate': round(completion_rate, 2),
                        'avg_order_value': str(avg_order_value),
                    },
                    'revenue': {
                        'total': str(revenue),
                        'avg_per_order': str(revenue / completed_orders) if completed_orders > 0 else '0',
                    },
                    'disputes': {
                        'total': dispute_count,
                        'resolution_rate': round(dispute_resolution_rate, 2),
                    },
                    'support': {
                        'total_tickets': ticket_count,
                        'resolution_rate': round(ticket_resolution_rate, 2),
                    },
                },
            })
        
        # Calculate aggregate totals
        total_revenue = sum(float(item['metrics']['revenue']['total']) for item in cross_tenant_data)
        total_orders = sum(item['metrics']['orders']['total'] for item in cross_tenant_data)
        total_users = sum(item['metrics']['users']['total'] for item in cross_tenant_data)
        total_disputes = sum(item['metrics']['disputes']['total'] for item in cross_tenant_data)
        total_tickets = sum(item['metrics']['support']['total_tickets'] for item in cross_tenant_data)
        
        # Top performers
        top_tenants_by_revenue = sorted(
            cross_tenant_data,
            key=lambda x: float(x['metrics']['revenue']['total']),
            reverse=True
        )[:5]
        
        top_tenants_by_orders = sorted(
            cross_tenant_data,
            key=lambda x: x['metrics']['orders']['total'],
            reverse=True
        )[:5]
        
        return Response({
            'summary': {
                'total_tenants': len(cross_tenant_data),
                'active_tenants': len([t for t in cross_tenant_data if t['is_active']]),
                'total_revenue': str(total_revenue),
                'total_orders': total_orders,
                'total_users': total_users,
                'total_disputes': total_disputes,
                'total_tickets': total_tickets,
            },
            'tenants': cross_tenant_data,
            'top_performers': {
                'by_revenue': top_tenants_by_revenue,
                'by_orders': top_tenants_by_orders,
            },
            'period': {
                'days': days,
                'from': date_from.isoformat(),
                'to': timezone.now().isoformat(),
            },
        })

