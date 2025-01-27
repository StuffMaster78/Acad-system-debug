from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from .models import (
    WriterLevel,
    PaymentHistory,
    WriterProgress,
    WriterAvailability,
    WriterPerformance,
    WriterOrderAssignment,
    WriterReview,
)

class WriterLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterLevel
        fields = ['name', 'base_pay_per_page', 'tip_percentage', 'max_orders', 'min_orders', 'min_rating']


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['writer', 'amount', 'bonuses', 'fines', 'tips', 'payment_date', 'description']


class WriterProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterProgress
        fields = ['writer', 'order', 'progress', 'timestamp']


class WriterAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterAvailability
        fields = ['writer', 'start_time', 'end_time', 'is_recurring']

class WriterAvailabilityListView(generics.ListCreateAPIView):
    """
    API to list and create availability schedules for writers.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WriterAvailabilitySerializer

    def get_queryset(self):
        return WriterAvailability.objects.filter(writer=self.request.user)


class WriterPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPerformance
        fields = ['writer', 'average_rating', 'on_time_delivery_rate', 'late_submissions', 'total_orders']


class WriterOrderAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterOrderAssignment
        fields = ['writer', 'order', 'status', 'assigned_date', 'completed_date']


class WriterReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterReview
        fields = ['writer', 'client', 'order', 'rating', 'feedback', 'timestamp']
