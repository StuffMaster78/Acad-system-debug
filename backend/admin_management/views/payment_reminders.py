"""
Payment reminder configuration management for admin/superadmin.
Allows managing reminders sent to clients with unpaid orders.
"""
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_management.permissions import IsAdmin
from admin_management.views.config_management import WebsiteFilteredMixin


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class PaymentReminderConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)

    class Meta:
        from orders.models.unpaid_order_payment_reminders import PaymentReminderConfig
        model = PaymentReminderConfig
        fields = [
            'id', 'website', 'website_name', 'name', 'deadline_percentage',
            'message', 'send_as_notification', 'send_as_email', 'email_subject',
            'is_active', 'display_order', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'website_name']


class PaymentReminderDeletionMessageSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)

    class Meta:
        from orders.models.unpaid_order_payment_reminders import PaymentReminderDeletionMessage
        model = PaymentReminderDeletionMessage
        fields = [
            'id', 'website', 'website_name', 'message',
            'send_as_notification', 'send_as_email', 'email_subject',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'website_name']


class PaymentReminderSentSerializer(serializers.ModelSerializer):
    client_email = serializers.EmailField(source='client.email', read_only=True)
    reminder_name = serializers.CharField(source='reminder_config.name', read_only=True)
    deadline_percentage = serializers.DecimalField(
        source='reminder_config.deadline_percentage',
        max_digits=5, decimal_places=2, read_only=True,
    )

    class Meta:
        from orders.models.unpaid_order_payment_reminders import PaymentReminderSent
        model = PaymentReminderSent
        fields = [
            'id', 'reminder_name', 'deadline_percentage', 'client_email',
            'order', 'sent_at', 'sent_as_notification', 'sent_as_email',
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# ViewSets
# ---------------------------------------------------------------------------

class PaymentReminderConfigViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """CRUD for deadline-percentage-based payment reminder configs."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = PaymentReminderConfigSerializer

    def get_queryset(self):
        from orders.models.unpaid_order_payment_reminders import PaymentReminderConfig
        return self.get_website_filtered_queryset(
            PaymentReminderConfig.objects.select_related('website').order_by('display_order', 'deadline_percentage')
        )

    def perform_create(self, serializer):
        self.perform_create_with_website(serializer, "payment reminder config")

    def perform_update(self, serializer):
        self.perform_update_with_log(serializer, "payment reminder config")

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, _request):
        """Summary counts: total, active, sent in last 7 days."""
        from orders.models.unpaid_order_payment_reminders import (
            PaymentReminderConfig, PaymentReminderSent,
        )
        from django.utils import timezone
        from datetime import timedelta

        qs = self.get_queryset()
        total = qs.count()
        active = qs.filter(is_active=True).count()
        week_ago = timezone.now() - timedelta(days=7)
        sent_recent = PaymentReminderSent.objects.filter(sent_at__gte=week_ago).count()
        return Response({'total': total, 'active': active, 'sent_last_7_days': sent_recent})


class PaymentReminderDeletionMessageViewSet(WebsiteFilteredMixin, viewsets.ModelViewSet):
    """CRUD for messages sent when an unpaid order is deleted after deadline."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = PaymentReminderDeletionMessageSerializer

    def get_queryset(self):
        from orders.models.unpaid_order_payment_reminders import PaymentReminderDeletionMessage
        return self.get_website_filtered_queryset(
            PaymentReminderDeletionMessage.objects.select_related('website')
        )

    def perform_create(self, serializer):
        self.perform_create_with_website(serializer, "payment deletion message")

    def perform_update(self, serializer):
        self.perform_update_with_log(serializer, "payment deletion message")


class PaymentReminderSentViewSet(WebsiteFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only log of reminders sent to clients."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = PaymentReminderSentSerializer

    def get_queryset(self):
        from orders.models.unpaid_order_payment_reminders import PaymentReminderSent
        qs = PaymentReminderSent.objects.select_related(
            'reminder_config__website', 'client', 'order',
        ).order_by('-sent_at')
        website = self._get_user_website()
        if not self._is_superadmin() and website:
            qs = qs.filter(reminder_config__website=website)
        return qs
