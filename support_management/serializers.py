from rest_framework import serializers
from .models import (
    SupportProfile,
    SupportActionLog,
    SupportActivityLog,
    DisputeResolutionLog,
    TicketAssignment,
    SupportAvailability,
    SupportPerformance,
    SupportNotification,
    EscalationLog,
)

class SupportProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportProfile
        fields = "__all__"

class SupportActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportActionLog
        fields = "__all__"

class SupportActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportActivityLog
        fields = "__all__"

class DisputeResolutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeResolutionLog
        fields = "__all__"

class TicketAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAssignment
        fields = "__all__"

class SupportAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAvailability
        fields = "__all__"

class SupportPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportPerformance
        fields = "__all__"

class SupportNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportNotification
        fields = "__all__"

class EscalationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationLog
        fields = "__all__"