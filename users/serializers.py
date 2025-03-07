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
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from websites.models import Website
from users.models import AccountDeletionRequest

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)  # Confirm password

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'role', 'website')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        request = self.context.get("request")
        request_host = request.get_host().replace("www.", "")

        # Validate if the website exists and is active
        website = Website.objects.filter(domain__icontains=request_host, is_active=True).first()
        if not website:
            raise serializers.ValidationError({"website": "This website is not registered or is inactive."})

        # Validate if registration is allowed on this website
        if not website.allow_registration:
            raise serializers.ValidationError({"website": "Registration is disabled for this website."})

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        request_host = request.get_host().replace("www.", "")

        # Assign the detected website
        website = Website.objects.filter(domain__icontains=request_host, is_active=True).first()
        validated_data["website"] = website.domain
        validated_data.pop("password2")  # Remove password2 before saving
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # Include role in JWT
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    """
    General User profile serializer for retrieving user details.
    Includes profile picture and avatar display.
    """
    display_avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'avatar', 'profile_picture', 'display_avatar',
            'phone_number', 'role', 'is_suspended', 'is_on_probation',
            'is_available', 'date_joined', 'last_active'
        ]

    # def get_display_avatar(self, obj):
    #     """
    #     Returns the profile picture if available, otherwise the selected avatar.
    #     Ensures fallback to the default avatar if the image is missing.
    #     """
    #     if obj.profile_picture:
    #         return obj.profile_picture.url
    #     avatar_path = os.path.join(settings.MEDIA_ROOT, obj.avatar)
    #     if not os.path.exists(avatar_path):
    #         return "/media/avatars/universal.png"  # Fallback image
    #     return f"/media/{obj.avatar}"
    def get_display_avatar(self, obj):
            """Returns profile picture URL or fallback avatar."""
            if obj.profile_picture:
                return obj.profile_picture.url
            return f"{settings.MEDIA_URL}avatars/universal.png"  # Fallback image

class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Client profiles.
    Retrieves additional client-specific information from `ClientProfile`.
    """
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'user', 'loyalty_points', 'membership_tier', 'notes', 'tasks'
        ]


class WriterProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WriterProfile
        fields = [
            'user', 'bio', 'writer_level', 'rating', 'average_rating', 
            'total_ratings', 'completed_orders', 'active_orders', 
            'verification_documents', 'total_earnings', 'last_payment_date'
        ]

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
    Serializer for uploading  or removing a profile picture.
    """
    remove_picture = serializers.BooleanField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ['profile_picture', 'remove_picture']

    def update(self, instance, validated_data):
        if validated_data.get('remove_picture'):
            instance.profile_picture.delete(save=True)
            instance.profile_picture = None  # Reset the field
            instance.save()  # Ensure changes are saved
        return super().update(instance, validated_data)


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin updates on user status such as suspension and probation.
    """
    class Meta:
        model = User
        fields = [
            'is_suspended', 'suspension_reason', 'suspension_start_date', 'suspension_end_date',
            'is_on_probation', 'probation_reason', 'is_available'
        ]


class UserDeletionRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for handling account deletion requests.
    """
    class Meta:
        model = User
        fields = [
            'is_deletion_requested', 'deletion_requested_at', 'deletion_date', 'is_frozen'
        ]


class ImpersonationSerializer(serializers.ModelSerializer):
    """
    Serializer for impersonation control.
    """
    impersonated_by = serializers.ReadOnlyField(source='impersonated_by.username')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_impersonated', 'impersonated_by'
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

class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ["id", "reason", "status", "requested_at", "admin_response"]
