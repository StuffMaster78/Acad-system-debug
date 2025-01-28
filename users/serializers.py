from rest_framework import serializers
from .models import User


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Client profiles.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'avatar', 'phone_number', 'role',
            'is_suspended', 'is_on_probation', 'date_joined', 'is_available',
            'is_deletion_requested', 'deletion_requested_at', 'deletion_date'
        ]


class WriterProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Writer profiles.
    Includes writer-specific fields such as writer level, ratings, and orders.
    """
    average_rating = serializers.ReadOnlyField(source='average_rating')
    total_ratings = serializers.ReadOnlyField(source='total_ratings')

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'bio', 'writer_level', 'rating', 
            'average_rating', 'total_ratings', 'completed_orders', 
            'active_orders', 'verification_documents', 'total_earnings', 
            'phone_number', 'role', 'is_suspended', 'is_on_probation', 
            'date_joined', 'is_available', 'last_payment_date'
        ]


class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin profiles.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number', 'role', 
            'is_suspended', 'is_on_probation', 'date_joined'
        ]


class EditorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Editor profiles.
    Includes editor-specific fields like edited orders and bio.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'bio', 'role', 
            'is_suspended', 'is_on_probation', 'date_joined'
        ]


class SupportProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Support profiles.
    Includes support-specific fields like handled tickets.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number', 'role', 
            'is_suspended', 'is_on_probation', 'date_joined', 'is_available'
        ]


class ImpersonationSerializer(serializers.ModelSerializer):
    """
    Serializer to manage impersonation by admins or superadmins.
    """
    impersonated_by = serializers.ReadOnlyField(source='impersonated_by.username')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_impersonated', 
            'impersonated_by'
        ]


class SuspensionSerializer(serializers.ModelSerializer):
    """
    Serializer to handle user suspension and probation updates.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_suspended', 
            'suspension_reason', 'suspension_start_date', 
            'suspension_end_date', 'is_on_probation', 'probation_reason'
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer to track user activity and availability.
    """
    last_active = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_available', 
            'last_active'
        ]