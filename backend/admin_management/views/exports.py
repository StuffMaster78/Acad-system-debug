"""
Export views for generating CSV and Excel reports.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from admin_management.services.export_service import ExportService
from orders.models import Order
from order_payments_management.models import OrderPayment
from users.models import User
from authentication.permissions import IsAdmin, IsSuperadminOrAdmin


class ExportViewSet(viewsets.ViewSet):
    """
    Export endpoints for orders, payments, users, and financial reports.
    """
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    
    @action(detail=False, methods=['get'], url_path='orders')
    def export_orders(self, request):
        """
        Export orders to CSV or Excel.
        
        Query parameters:
        - format: 'csv' or 'xlsx' (default: 'csv')
        - status: Filter by order status (comma-separated)
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
        - is_paid: Filter by payment status (true/false)
        """
        format_type = request.query_params.get('format', 'csv').lower()
        if format_type not in ['csv', 'xlsx']:
            return Response(
                {'error': "Format must be 'csv' or 'xlsx'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build queryset
        queryset = Order.objects.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
            queryset = queryset.filter(status__in=statuses)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__gte=date_from_obj)
            except ValueError:
                pass
        
        date_to = request.query_params.get('date_to')
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() + timedelta(days=1)
                queryset = queryset.filter(created_at__lt=date_to_obj)
            except ValueError:
                pass
        
        is_paid = request.query_params.get('is_paid')
        if is_paid is not None:
            queryset = queryset.filter(is_paid=(is_paid.lower() in ['true', '1', 'yes']))
        
        # Role-based filtering
        user_role = getattr(request.user, 'role', None)
        if user_role == 'client':
            queryset = queryset.filter(client=request.user)
        elif user_role == 'writer':
            queryset = queryset.filter(assigned_writer=request.user)
        
        # Prepare export data
        export_data = ExportService.prepare_orders_export(queryset)
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'orders_export_{timestamp}.{format_type}'
        
        # Export
        if format_type == 'csv':
            response, _ = ExportService.export_to_csv(export_data, filename)
        else:
            response, _ = ExportService.export_to_excel(export_data, filename, 'Orders')
        
        return response
    
    @action(detail=False, methods=['get'], url_path='payments')
    def export_payments(self, request):
        """
        Export payments to CSV or Excel.
        
        Query parameters:
        - format: 'csv' or 'xlsx' (default: 'csv')
        - status: Filter by payment status (comma-separated)
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
        - payment_type: Filter by payment type
        """
        format_type = request.query_params.get('format', 'csv').lower()
        if format_type not in ['csv', 'xlsx']:
            return Response(
                {'error': "Format must be 'csv' or 'xlsx'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build queryset
        queryset = OrderPayment.objects.all()
        
        # Role-based filtering
        user_role = getattr(request.user, 'role', None)
        if user_role == 'client':
            queryset = queryset.filter(client=request.user)
        elif user_role not in ['admin', 'superadmin', 'support']:
            queryset = queryset.none()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(',') if s.strip()]
            queryset = queryset.filter(status__in=statuses)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__gte=date_from_obj)
            except ValueError:
                pass
        
        date_to = request.query_params.get('date_to')
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() + timedelta(days=1)
                queryset = queryset.filter(created_at__lt=date_to_obj)
            except ValueError:
                pass
        
        payment_type = request.query_params.get('payment_type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # Prepare export data
        export_data = ExportService.prepare_payments_export(queryset)
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'payments_export_{timestamp}.{format_type}'
        
        # Export
        if format_type == 'csv':
            response, _ = ExportService.export_to_csv(export_data, filename)
        else:
            response, _ = ExportService.export_to_excel(export_data, filename, 'Payments')
        
        return response
    
    @action(detail=False, methods=['get'], url_path='users')
    def export_users(self, request):
        """
        Export users to CSV or Excel.
        
        Query parameters:
        - format: 'csv' or 'xlsx' (default: 'csv')
        - role: Filter by user role (comma-separated)
        - is_active: Filter by active status (true/false)
        """
        format_type = request.query_params.get('format', 'csv').lower()
        if format_type not in ['csv', 'xlsx']:
            return Response(
                {'error': "Format must be 'csv' or 'xlsx'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build queryset
        queryset = User.objects.all()
        
        # Apply filters
        role_filter = request.query_params.get('role')
        if role_filter:
            roles = [r.strip() for r in role_filter.split(',') if r.strip()]
            queryset = queryset.filter(role__in=roles)
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() in ['true', '1', 'yes']))
        
        # Prepare export data
        export_data = ExportService.prepare_users_export(queryset)
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'users_export_{timestamp}.{format_type}'
        
        # Export
        if format_type == 'csv':
            response, _ = ExportService.export_to_csv(export_data, filename)
        else:
            response, _ = ExportService.export_to_excel(export_data, filename, 'Users')
        
        return response
    
    @action(detail=False, methods=['get'], url_path='financial-report')
    def export_financial_report(self, request):
        """
        Export financial overview to CSV or Excel.
        
        Query parameters:
        - format: 'csv' or 'xlsx' (default: 'csv')
        - date_from: Start date (YYYY-MM-DD)
        - date_to: End date (YYYY-MM-DD)
        """
        format_type = request.query_params.get('format', 'csv').lower()
        if format_type not in ['csv', 'xlsx']:
            return Response(
                {'error': "Format must be 'csv' or 'xlsx'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get financial data (reuse existing financial overview logic)
        from admin_management.views.financial_overview import FinancialOverviewViewSet
        financial_view = FinancialOverviewViewSet()
        financial_view.request = request
        financial_response = financial_view.overview(request)
        
        if financial_response.status_code != 200:
            return Response(
                {'error': 'Failed to fetch financial data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        financial_data = financial_response.data
        
        # Prepare export data
        export_data = ExportService.prepare_financial_report_export(financial_data)
        
        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'financial_report_{timestamp}.{format_type}'
        
        # Export
        if format_type == 'csv':
            response, _ = ExportService.export_to_csv(export_data, filename)
        else:
            response, _ = ExportService.export_to_excel(export_data, filename, 'Financial Report')
        
        return response

