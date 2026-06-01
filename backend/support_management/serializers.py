from rest_framework import serializers
from django.conf import settings
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, SupportMessageAccess, SupportGlobalAccess,
    SupportPermission, DisputeResolutionLog, SupportActionLog,
    EscalationLog, SupportAvailability, SupportActivityLog,
    PaymentIssueLog, SupportOrderFileManagement, WriterPerformanceLog,
    SupportWorkloadTracker, OrderDisputeSLA, FAQCategory, FAQManagement,
    SupportDashboard
)
from orders.models.orders import Order
from orders.models.legacy_models.order_disputes import Dispute
from tickets.models import Ticket

User = settings.AUTH_USER_MODEL


### ** Support Profile Serializer**
class SupportProfileSerializer(serializers.ModelSerializer):
    """Handles serialization of support agent profiles."""
    class Meta:
        model = SupportProfile
        fields = '__all__'


### ** Support Notifications Serializer**
class SupportNotificationSerializer(serializers.ModelSerializer):
    """Handles notifications for support agents."""

    class Meta:
        model = SupportNotification
        fields = '__all__'


### ** Support Order Management Serializer**
class SupportOrderManagementSerializer(serializers.ModelSerializer):
    """Allows support to manage order statuses & dispute resolutions."""

    class Meta:
        model = SupportOrderManagement
        fields = '__all__'


### ** Support Messages Serializer**
class SupportMessageSerializer(serializers.ModelSerializer):
    """Allows support to send messages to clients, writers, editors, and admins."""

    class Meta:
        model = SupportMessage
        fields = '__all__'


### ** Support Message Access Serializer**
class SupportMessageAccessSerializer(serializers.ModelSerializer):
    """Controls support's ability to view and moderate messages."""

    class Meta:
        model = SupportMessageAccess
        fields = '__all__'


### ** Support Global Access Serializer**
class SupportGlobalAccessSerializer(serializers.ModelSerializer):
    """Ensures support has full access to all orders, clients, and writers."""

    class Meta:
        model = SupportGlobalAccess
        fields = '__all__'


### ** Support Permissions Serializer**
class SupportPermissionSerializer(serializers.ModelSerializer):
    """Defines permissions for support roles."""

    class Meta:
        model = SupportPermission
        fields = '__all__'


### ** Dispute Resolution Log Serializer**
class DisputeResolutionLogSerializer(serializers.ModelSerializer):
    """Tracks dispute resolutions handled by support agents."""

    class Meta:
        model = DisputeResolutionLog
        fields = '__all__'


### ** Support Action Log Serializer**
class SupportActionLogSerializer(serializers.ModelSerializer):
    """Tracks actions performed by support agents."""

    class Meta:
        model = SupportActionLog
        fields = '__all__'


### ** Escalation Log Serializer**
class EscalationLogSerializer(serializers.ModelSerializer):
    """Logs cases escalated by support agents."""

    class Meta:
        model = EscalationLog
        fields = '__all__'


### ** Support Availability Serializer**
class SupportAvailabilitySerializer(serializers.ModelSerializer):
    """Tracks support availability and online status."""

    class Meta:
        model = SupportAvailability
        fields = '__all__'


### ** Support Activity Log Serializer**
class SupportActivityLogSerializer(serializers.ModelSerializer):
    """Logs all actions performed by support staff for auditing."""

    class Meta:
        model = SupportActivityLog
        fields = '__all__'


### ** Payment Issue Log Serializer**
class PaymentIssueLogSerializer(serializers.ModelSerializer):
    """Tracks financial issues and escalations for payment disputes."""

    class Meta:
        model = PaymentIssueLog
        fields = '__all__'


### ** Support Order File Management Serializer**
class SupportOrderFileManagementSerializer(serializers.ModelSerializer):
    """Handles file uploads, deletions, and access control by support."""

    class Meta:
        model = SupportOrderFileManagement
        fields = '__all__'


### ** Writer Performance Log Serializer**
class WriterPerformanceLogSerializer(serializers.ModelSerializer):
    """Logs writer performance issues and complaints for review."""

    class Meta:
        model = WriterPerformanceLog
        fields = '__all__'


### ** Support Workload Tracker Serializer**
class SupportWorkloadTrackerSerializer(serializers.ModelSerializer):
    """Tracks the workload of each support agent."""

    class Meta:
        model = SupportWorkloadTracker
        fields = '__all__'


### ** Order Dispute SLA Serializer**
class OrderDisputeSLASerializer(serializers.ModelSerializer):
    """Ensures support agents meet SLA compliance for orders and disputes."""

    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    dispute_id = serializers.IntegerField(source='dispute.id', read_only=True)
    time_remaining_display = serializers.SerializerMethodField()
    breach_duration_display = serializers.SerializerMethodField()

    class Meta:
        model = OrderDisputeSLA
        fields = '__all__'
        extra_fields = [
            'assigned_to_username',
            'assigned_to_email',
            'order_id',
            'dispute_id',
            'time_remaining_display',
            'breach_duration_display',
        ]

    def get_time_remaining_display(self, obj):
        """Get human-readable time remaining."""
        if obj.time_remaining_minutes is None:
            return None
        if obj.time_remaining_minutes < 0:
            return "Breached"
        hours = obj.time_remaining_minutes // 60
        minutes = obj.time_remaining_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def get_breach_duration_display(self, obj):
        """Get human-readable breach duration."""
        if obj.breach_duration_minutes is None:
            return None
        hours = obj.breach_duration_minutes // 60
        minutes = obj.breach_duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


### ** FAQ Category Serializer**
class FAQCategorySerializer(serializers.ModelSerializer):
    """Defines categories for FAQs (Writer FAQs, Client FAQs)."""

    class Meta:
        model = FAQCategory
        fields = '__all__'


### ** FAQ Management Serializer**
class FAQManagementSerializer(serializers.ModelSerializer):
    """Allows support to create, update, and manage FAQs."""

    class Meta:
        model = FAQManagement
        fields = '__all__'


### ** Support Dashboard Serializer**
class SupportDashboardSerializer(serializers.ModelSerializer):
    """Provides an overview of support workload and flagged issues."""

    class Meta:
        model = SupportDashboard
        fields = '__all__'
