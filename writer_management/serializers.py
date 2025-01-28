from rest_framework import serializers
from .models import (
    WriterProfile,
    WriterLevel,
    WriterLeave,
    WriterActionLog,
    WriterEducation,
    PaymentHistory,
    WriterReward,
    WriterRating,
)


class WriterProfileSerializer(serializers.ModelSerializer):
    average_rating = serializers.DecimalField(
        max_digits=3, decimal_places=2, read_only=True
    )
    wallet_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = WriterProfile
        fields = [
            'user',
            'registration_id',
            'email',
            'phone_number',
            'country',
            'timezone',
            'ip_address',
            'location_verified',
            'website',
            'joined',
            'last_logged_in',
            'writer_level',
            'completed_orders',
            'number_of_takes',
            'total_earnings',
            'verification_status',
            'verification_documents',
            'skills',
            'subject_preferences',
            'education',
            'rating',
            'average_rating',
            'wallet_balance',
        ]
        read_only_fields = ['user', 'total_earnings', 'completed_orders', 'rating']


class WriterLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterLeave
        fields = '__all__'


class WriterActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterActionLog
        fields = '__all__'


class WriterEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterEducation
        fields = '__all__'


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = '__all__'


class WriterRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterReward
        fields = '__all__'


class WriterRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterRating
        fields = '__all__'