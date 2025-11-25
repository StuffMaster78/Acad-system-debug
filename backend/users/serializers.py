from django.templatetags.static import static
from django.conf import settings
from rest_framework import serializers
from .models import User
from users.models import UserProfile
from client_management.models import ClientProfile
from writer_management.models.profile import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from superadmin_management.models import SuperadminProfile
from django.contrib.auth import get_user_model
from websites.models import Website
from authentication.models import AccountDeletionRequest
from rest_framework.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from django_countries.serializer_fields import CountryField as CountrySerializerField

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        
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
    Includes User and UserProfile fields for complete profile data.
    """
    user = UserDetailSerializer(read_only=True)
    # Include UserProfile fields directly
    phone_number = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    registration_id = serializers.CharField(read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'user', 'loyalty_points', 'membership_tier', 'notes', 'tasks',
            'phone_number', 'bio', 'avatar', 'avatar_url', 'country', 'state',
            'email', 'username', 'first_name', 'last_name', 'full_name',
            'registration_id'
        ]

    def get_phone_number(self, obj):
        """Get phone number from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return str(obj.user.user_main_profile.phone_number) if obj.user.user_main_profile.phone_number else None
        return None
    
    def get_bio(self, obj):
        """Get bio from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.bio
        return None
    
    def get_avatar(self, obj):
        """Get avatar from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.avatar
        return None
    
    def get_avatar_url(self, obj):
        """Get avatar URL from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.get_avatar_url()
        return None
    
    def get_country(self, obj):
        """Get country from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return str(obj.user.user_main_profile.country) if obj.user.user_main_profile.country else None
        return None
    
    def get_state(self, obj):
        """Get state from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.state
        return None
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
    
    def get_full_name(self, obj):
        """Get full name from first_name and last_name."""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.first_name:
            return obj.user.first_name
        elif obj.user.last_name:
            return obj.user.last_name
        return obj.user.username

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        # Ensure UserProfile is loaded
        if not hasattr(instance.user, 'user_main_profile'):
            from users.models import UserProfile
            try:
                instance.user.user_main_profile = UserProfile.objects.get(user=instance.user)
            except UserProfile.DoesNotExist:
                pass
        return super().to_representation(instance)

class WriterProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # Include User and UserProfile fields directly
    phone_number = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    pen_name = serializers.CharField(read_only=True)
    registration_id = serializers.CharField(read_only=True)
    bio = serializers.SerializerMethodField()  # Map to introduction for backward compatibility

    class Meta:
        model = WriterProfile
        fields = [
            'user', 'introduction', 'bio', 'writer_level', 'rating', 'average_rating', 
            'total_ratings', 'completed_orders', 'active_orders', 
            'verification_documents', 'total_earnings', 'last_payment_date',
            'phone_number', 'avatar', 'avatar_url', 'country', 'state',
            'email', 'username', 'first_name', 'last_name', 'full_name',
            'pen_name', 'registration_id'
        ]

    def get_bio(self, obj):
        """Get bio from WriterProfile introduction field, or from UserProfile if available."""
        # First try WriterProfile introduction
        if hasattr(obj, 'introduction') and obj.introduction:
            return obj.introduction
        # Fallback to UserProfile bio
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.bio
        return None

    def get_phone_number(self, obj):
        """Get phone number from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return str(obj.user.user_main_profile.phone_number) if obj.user.user_main_profile.phone_number else None
        return None
    
    def get_avatar(self, obj):
        """Get avatar from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.avatar
        return None
    
    def get_avatar_url(self, obj):
        """Get avatar URL from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.get_avatar_url()
        return None
    
    def get_country(self, obj):
        """Get country from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return str(obj.user.user_main_profile.country) if obj.user.user_main_profile.country else None
        return None
    
    def get_state(self, obj):
        """Get state from UserProfile if available."""
        if hasattr(obj.user, 'user_main_profile') and obj.user.user_main_profile:
            return obj.user.user_main_profile.state
        return None
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
    
    def get_full_name(self, obj):
        """Get full name from first_name and last_name."""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        elif obj.user.first_name:
            return obj.user.first_name
        elif obj.user.last_name:
            return obj.user.last_name
        return obj.user.username

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        # Ensure UserProfile is loaded
        if not hasattr(instance.user, 'user_main_profile'):
            from users.models import UserProfile
            try:
                instance.user.user_main_profile = UserProfile.objects.get(user=instance.user)
            except UserProfile.DoesNotExist:
                pass
        return super().to_representation(instance)

class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin profiles (Uses base `User` model).
    Includes UserProfile fields for complete profile data.
    """
    phone_number = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'bio', 'avatar', 'avatar_url', 'country', 'state',
            'role', 'is_suspended', 'is_on_probation', 'date_joined'
        ]

    def get_phone_number(self, obj):
        """Get phone number from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return str(obj.user_main_profile.phone_number) if obj.user_main_profile.phone_number else None
        return None
    
    def get_bio(self, obj):
        """Get bio from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return obj.user_main_profile.bio
        return None
    
    def get_avatar(self, obj):
        """Get avatar from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return obj.user_main_profile.avatar
        return None
    
    def get_avatar_url(self, obj):
        """Get avatar URL from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return obj.user_main_profile.get_avatar_url()
        return None
    
    def get_country(self, obj):
        """Get country from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return str(obj.user_main_profile.country) if obj.user_main_profile.country else None
        return None
    
    def get_state(self, obj):
        """Get state from UserProfile if available."""
        if hasattr(obj, 'user_main_profile') and obj.user_main_profile:
            return obj.user_main_profile.state
        return None
    
    def get_full_name(self, obj):
        """Get full name from first_name and last_name."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username

    def to_representation(self, instance):
        """Override to optimize database query by using select_related."""
        # Ensure UserProfile is loaded
        if not hasattr(instance, 'user_main_profile'):
            from users.models import UserProfile
            try:
                instance.user_main_profile = UserProfile.objects.get(user=instance)
            except UserProfile.DoesNotExist:
                pass
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
        fields = [
            'id', 'user', 'created_at', 'updated_at',
            'can_manage_users', 'can_manage_payments', 'can_view_reports',
            'can_modify_settings', 'can_promote_users', 'can_suspend_users',
            'can_blacklist_users', 'can_resolve_disputes', 'can_override_payments',
            'can_track_admins'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user avatar selection.
    """
    class Meta:
        model = User
        fields = ['avatar']


class UserSerializer(serializers.ModelSerializer):
    """
    Minimal User serializer to expose username and role.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile, handling nested user and computed fields.
    """
    user = UserSerializer(read_only=True)
    phone_number = PhoneNumberField(required=False, allow_null=True)
    country = CountrySerializerField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField()
    full_bio = serializers.SerializerMethodField()
    website = serializers.PrimaryKeyRelatedField(
        queryset=Website.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'preferences',
            'profile_picture',
            'avatar',
            'avatar_url',
            'website',
            'country',
            'state',
            'bio',
            'full_bio',
            'phone_number',
            'is_deleted',
            'deletion_reason',
            'date_joined',
            'last_active',
        ]
        read_only_fields = ['id', 'date_joined', 'last_active']

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()

    def get_full_bio(self, obj):
        return obj.get_full_bio()

class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading or removing a profile picture.
    """
    remove_picture = serializers.BooleanField(
        write_only=True,
        required=False
    )

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
            user = User.objects.get(id=value)
        except User.DoesNotExist:
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
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    request_time = serializers.DateTimeField(read_only=True)
    scheduled_deletion_time = serializers.DateTimeField(read_only=True)
    status = serializers.ChoiceField(
        choices=AccountDeletionRequest.STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        model = AccountDeletionRequest
        fields = [
            'id',
            'user_id',
            'user_email',
            'user_username',
            'user_role',
            'user_full_name',
            'reason',
            'status',
            'admin_response',
            'request_time',
            'scheduled_deletion_time',
            'confirmation_time',
            'rejection_time',
            'website'
        ]
        read_only_fields = ['id', 'request_time', 'confirmation_time', 'rejection_time', 'scheduled_deletion_time']

    def get_user_full_name(self, obj):
        user = obj.user
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.username