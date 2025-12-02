"""
Holiday Management ViewSets
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models import SpecialDay, HolidayReminder, HolidayDiscountCampaign
from .serializers import (
    SpecialDaySerializer, SpecialDayCreateSerializer,
    HolidayReminderSerializer, HolidayDiscountCampaignSerializer
)
from .services import (
    HolidayReminderService, HolidayDiscountService, HolidayNotificationService
)
from admin_management.permissions import IsAdmin


class SpecialDayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing special days and holidays.
    """
    queryset = SpecialDay.objects.prefetch_related('countries').all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return SpecialDayCreateSerializer
        return SpecialDaySerializer
    
    def get_queryset(self):
        """Filter special days based on query parameters."""
        qs = super().get_queryset()
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            qs = qs.filter(
                Q(is_international=True) | Q(countries__contains=country)
            ).distinct()
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            qs = qs.filter(event_type=event_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        
        # Filter upcoming
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            days_ahead = int(self.request.query_params.get('days_ahead', 30))
            country_code = self.request.query_params.get('country')
            qs = qs.filter(
                id__in=[day.id for day in HolidayReminderService.get_upcoming_special_days(days_ahead, country_code)]
            )
        
        return qs.order_by('date', 'priority')
    
    def perform_create(self, serializer):
        """Create special day with creator."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_discount(self, request, pk=None):
        """Manually generate discount for a special day."""
        special_day = self.get_object()
        year = request.data.get('year', timezone.now().year)
        
        discount = HolidayDiscountService.create_discount_for_special_day(
            special_day,
            year=year,
            created_by=request.user
        )
        
        campaign = HolidayDiscountCampaign.objects.get(
            special_day=special_day,
            year=year
        )
        
        return Response(
            HolidayDiscountCampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming special days."""
        days_ahead = int(request.query_params.get('days_ahead', 30))
        country_code = request.query_params.get('country')
        
        upcoming = HolidayReminderService.get_upcoming_special_days(
            days_ahead=days_ahead,
            country_code=country_code
        )
        
        serializer = SpecialDaySerializer(upcoming, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def auto_generate_discounts(self, request):
        """Auto-generate discounts for upcoming special days."""
        discounts = HolidayDiscountService.auto_generate_discounts_for_upcoming()
        
        return Response({
            'message': f'Generated {len(discounts)} discount codes',
            'discounts': [discount.code for discount in discounts]
        })


class HolidayReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing holiday reminders.
    """
    queryset = HolidayReminder.objects.select_related('special_day', 'sent_to').all()
    serializer_class = HolidayReminderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Filter reminders based on query parameters."""
        qs = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        # Filter pending only
        pending = self.request.query_params.get('pending')
        if pending == 'true':
            qs = qs.filter(status='pending')
        
        return qs.order_by('-reminder_date', '-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark reminder as sent."""
        reminder = self.get_object()
        reminder = HolidayReminderService.mark_reminder_sent(reminder.id, request.user)
        
        return Response(
            HolidayReminderSerializer(reminder).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def create_discount(self, request, pk=None):
        """Create discount for this reminder's special day."""
        reminder = self.get_object()
        special_day = reminder.special_day
        
        year = request.data.get('year', timezone.now().year)
        discount = HolidayDiscountService.create_discount_for_special_day(
            special_day,
            year=year,
            created_by=request.user
        )
        
        reminder.discount_created = True
        reminder.discount_code = discount.code
        reminder.save()
        
        return Response({
            'message': 'Discount created successfully',
            'discount_code': discount.code,
            'discount_id': discount.id
        })
    
    @action(detail=False, methods=['post'])
    def check_and_create(self, request):
        """Check for special days needing reminders and create them."""
        reminders = HolidayReminderService.check_and_create_reminders()
        
        return Response({
            'message': f'Created {len(reminders)} new reminders',
            'reminders': HolidayReminderSerializer(reminders, many=True).data
        })
    
    @action(detail=False, methods=['post'])
    def notify_admins(self, request):
        """Send notifications to admins about pending reminders."""
        HolidayNotificationService.notify_admins_of_upcoming_holidays()
        
        return Response({
            'message': 'Notifications sent to admins'
        })


class HolidayDiscountCampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing holiday discount campaigns.
    """
    queryset = HolidayDiscountCampaign.objects.select_related(
        'special_day', 'discount', 'created_by'
    ).all()
    serializer_class = HolidayDiscountCampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Filter campaigns based on query parameters."""
        qs = super().get_queryset()
        
        # Filter by special day
        special_day_id = self.request.query_params.get('special_day')
        if special_day_id:
            qs = qs.filter(special_day_id=special_day_id)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        
        return qs.order_by('-year', '-created_at')

