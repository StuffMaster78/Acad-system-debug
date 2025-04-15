from django.templatetags.static import static
from django.conf import settings
from rest_framework import serializers
from .models import User
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from superadmin_management.models import SuperadminProfile
from django.contrib.auth import get_user_model
from websites.models import Website
from users.models import AccountDeletionRequest
from rest_framework.exceptions import ValidationError

User = get_user_model()



class UserListSerializer(serializers.ModelSerializer):
    website = serializers.SlugRelatedField(
        slug_field='domain',
        queryset=Website.objects.all(),
        required=False,
        allow_null=True
    )
    display_avatar = serializers.SerializerMethodField()
    profile_role = serializers.CharField(source='role', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'website', 'role', 'profile_role', 'display_avatar',
            'is_available', 'is_active', 'is_suspended', 'is_on_probation',
            'is_blacklisted', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']

    def get_display_avatar(self, obj):
        return obj.display_avatar

class UserDetailSerializer(serializers.ModelSerializer):
    display_avatar = serializers.SerializerMethodField()
    profile_data = serializers.SerializerMethodField()
    website = serializers.SlugRelatedField(
        slug_field='domain',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'avatar', 'profile_picture',
            'role', 'website', 'display_avatar', 'profile_data',
            'is_available', 'is_impersonated', 'is_suspended',
            'is_on_probation', 'is_blacklisted', 'date_joined'
        ]
        read_only_fields = ['id', 'role', 'email', 'date_joined']

    def get_display_avatar(self, obj):
        return obj.display_avatar

    def get_profile_data(self, obj):
        return obj.get_profile()

class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Client profiles.
    Retrieves additional client-specific information from `ClientProfile`.
    """
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'user', 'loyalty_points', 'membership_tier', 'notes', 'tasks'
        ]

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        instance = instance.select_related('user__profile_picture')
        return super().to_representation(instance)

class WriterProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WriterProfile
        fields = [
            'user', 'bio', 'writer_level', 'rating', 'average_rating', 
            'total_ratings', 'completed_orders', 'active_orders', 
            'verification_documents', 'total_earnings', 'last_payment_date'
        ]

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        instance = instance.select_related('user__profile_picture')
        return super().to_representation(instance)

class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin profiles (Uses base `User` model).
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number', 'role', 
            'is_suspended', 'is_on_probation', 'date_joined'
        ]

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        instance = instance.select_related('profile_picture', 'avatar')
        return super().to_representation(instance)


class EditorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Editor profiles.
    Retrieves editor-specific fields from `EditorProfile`.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EditorProfile
        fields = [
            'user', 'bio', 'edited_orders'
        ]

class SupportProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Support profiles.
    Retrieves support-specific fields from `SupportProfile`.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SupportProfile
        fields = [
            'user', 'handled_tickets', 'resolved_orders'
        ]
class SuperadminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperadminProfile
        fields = ['id', 'created_at', 'permissions', 'status']

class AvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user avatar selection.
    """
    class Meta:
        model = User
        fields = ['avatar']


class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading or removing a profile picture.
    """
    remove_picture = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['profile_picture', 'remove_picture']

    def update(self, instance, validated_data):
        if validated_data.get('remove_picture'):
            if instance.profile_picture:
                instance.profile_picture.delete(save=False)
            instance.profile_picture = None  # Reset the field
        return super().update(instance, validated_data)


class ImpersonateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """
        Validate the user_id is an actual existing user and that it's not the admin themselves.
        """
        try:
            user = get_user_model().objects.get(id=value)
        except get_user_model().DoesNotExist:
            raise ValidationError("User with this ID does not exist.")

        # Ensure the admin is not impersonating themselves
        admin_user = self.context.get('request').user
        if user == admin_user:
            raise ValidationError("You cannot impersonate yourself.")
        
        return user
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

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        instance = instance.select_related('profile_picture', 'avatar')
        return super().to_representation(instance)


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    status = serializers.ChoiceField(
        choices=AccountDeletionRequest.STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        model = AccountDeletionRequest
        fields = [
            'user',
            'reason',
            'status',
            'admin_response',
            'created_at'
        ]
        read_only_fields = ['created_at']