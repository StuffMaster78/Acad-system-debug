"""
Geographic and Subject Analytics Endpoints

This module provides analytics endpoints for admins to view:
- Largest spend by country, state, and subject
- Number of orders by country, state, and subject
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from admin_management.permissions import IsAdmin
from orders.models import Order
from orders.order_enums import OrderStatus
from client_management.models import ClientProfile


class GeographicAnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints for geographic and subject-based insights.
    Provides data on spending and order counts by country, state,
    and subject.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        Get comprehensive geographic and subject analytics.
        
        Returns:
        - Spending by country
        - Spending by state
        - Spending by subject
        - Order counts by country
        - Order counts by state
        - Order counts by subject
        """
        # Filter by website if user has website context and is not
        # superadmin
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website

        # Time range filter (optional)
        days = int(request.query_params.get('days', 0))
        date_from = None
        if days > 0:
            date_from = timezone.now() - timedelta(days=days)

        # Base queryset for paid orders
        orders = Order.objects.filter(is_paid=True)
        if website_filter:
            orders = orders.filter(website=website_filter)
        if date_from:
            orders = orders.filter(created_at__gte=date_from)

        # Get country data from ClientProfile
        # Join through client -> client_profile
        country_spend = (
            orders
            .filter(client__client_profile__country__isnull=False)
            .values('client__client_profile__country')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        # Get state data from UserProfile
        # Join through client -> user_main_profile
        state_spend = (
            orders
            .filter(client__user_main_profile__state__isnull=False)
            .exclude(client__user_main_profile__state='')
            .values('client__user_main_profile__state')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        # Get subject data from Order
        subject_spend = (
            orders
            .filter(subject__isnull=False)
            .values('subject__name')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        # Format country data
        country_data = [
            {
                'country': item['client__client_profile__country'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in country_spend
        ]

        # Format state data
        state_data = [
            {
                'state': item['client__userprofile__state'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in state_spend
        ]

        # Format subject data
        subject_data = [
            {
                'subject': item['subject__name'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in subject_spend
        ]

        return Response({
            'by_country': country_data,
            'by_state': state_data,
            'by_subject': subject_data,
            'summary': {
                'total_countries': len(country_data),
                'total_states': len(state_data),
                'total_subjects': len(subject_data),
                'date_range_days': days if days > 0 else None,
            }
        })

    @action(detail=False, methods=['get'], url_path='by-country')
    def by_country(self, request):
        """
        Get spending and order counts grouped by country.
        """
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website

        days = int(request.query_params.get('days', 0))
        date_from = None
        if days > 0:
            date_from = timezone.now() - timedelta(days=days)

        orders = Order.objects.filter(is_paid=True)
        if website_filter:
            orders = orders.filter(website=website_filter)
        if date_from:
            orders = orders.filter(created_at__gte=date_from)

        country_data = (
            orders
            .filter(client__client_profile__country__isnull=False)
            .values('client__client_profile__country')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        result = [
            {
                'country': item['client__client_profile__country'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in country_data
        ]

        return Response(result)

    @action(detail=False, methods=['get'], url_path='by-state')
    def by_state(self, request):
        """
        Get spending and order counts grouped by state/province.
        """
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website

        days = int(request.query_params.get('days', 0))
        date_from = None
        if days > 0:
            date_from = timezone.now() - timedelta(days=days)

        orders = Order.objects.filter(is_paid=True)
        if website_filter:
            orders = orders.filter(website=website_filter)
        if date_from:
            orders = orders.filter(created_at__gte=date_from)

        state_data = (
            orders
            .filter(client__user_main_profile__state__isnull=False)
            .exclude(client__user_main_profile__state='')
            .values('client__user_main_profile__state')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        result = [
            {
                'state': item['client__user_main_profile__state'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in state_data
        ]

        return Response(result)

    @action(detail=False, methods=['get'], url_path='by-subject')
    def by_subject(self, request):
        """
        Get spending and order counts grouped by subject.
        """
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website

        days = int(request.query_params.get('days', 0))
        date_from = None
        if days > 0:
            date_from = timezone.now() - timedelta(days=days)

        orders = Order.objects.filter(is_paid=True)
        if website_filter:
            orders = orders.filter(website=website_filter)
        if date_from:
            orders = orders.filter(created_at__gte=date_from)

        subject_data = (
            orders
            .filter(subject__isnull=False)
            .values('subject__name')
            .annotate(
                total_spend=Sum('total_price'),
                order_count=Count('id')
            )
            .order_by('-total_spend')
        )

        result = [
            {
                'subject': item['subject__name'],
                'total_spend': float(item['total_spend']),
                'order_count': item['order_count'],
            }
            for item in subject_data
        ]

        return Response(result)
