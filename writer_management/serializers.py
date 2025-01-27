from rest_framework import serializers
from .models import (
    WriterLevel,
    PaymentHistory,
    WriterProgress,
    WriterAvailability,
    WriterOrderAssignment,
    WriterPerformance,
    WriterReview,
)


class WriterLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for WriterLevel model.
    """
    class Meta:
        model = WriterLevel
        fields = '__all__'

class WriterReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for WriterReview model.
    """
    client_name = serializers.ReadOnlyField(source='client.username')
    order_title = serializers.ReadOnlyField(source='order.title')

    class Meta:
        model = WriterReview
        fields = [
            'id',
            'writer',
            'client',
            'client_name',
            'order',
            'order_title',
            'rating',
            'feedback',
            'timestamp',
        ]

class PaymentHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentHistory model.
    """
    class Meta:
        model = PaymentHistory
        fields = '__all__'


class WriterProgressSerializer(serializers.ModelSerializer):
    """
    Serializer for WriterProgress model.
    """
    order_id = serializers.ReadOnlyField(source='order.id')
    order_title = serializers.ReadOnlyField(source='order.title')

    class Meta:
        model = WriterProgress
        fields = ['id', 'writer', 'order_id', 'order_title', 'progress', 'timestamp']


class WriterAvailabilitySerializer(serializers.ModelSerializer):
    """
    Serializer for WriterAvailability model.
    """
    writer_name = serializers.ReadOnlyField(source='writer.username')

    class Meta:
        model = WriterAvailability
        fields = ['id', 'writer', 'writer_name', 'start_time', 'end_time', 'is_recurring']


class WriterOrderAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for WriterOrderAssignment model.
    """
    order_title = serializers.ReadOnlyField(source='order.title')

    class Meta:
        model = WriterOrderAssignment
        fields = [
            'id',
            'writer',
            'order',
            'order_title',
            'status',
            'assigned_date',
            'completed_date',
        ]


class WriterPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for WriterPerformance model.
    """
    writer_name = serializers.ReadOnlyField(source='writer.username')

    class Meta:
        model = WriterPerformance
        fields = [
            'id',
            'writer',
            'writer_name',
            'average_rating',
            'on_time_delivery_rate',
            'late_submissions',
            'total_orders',
        ]
