from rest_framework import serializers
from .models import AuditLog, TrustedDevice, MagicLinkToken, BlockedIP, User, AccountDeletionRequest
from rest_framework import serializers
from websites.models import Website
from django.contrib.auth import get_user_model
from users.models import UserProfile  # Adjusted to import UserProfile from users app
from .models import MagicLinkToken, AuditLog
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField # type: ignore
from django.contrib.auth.password_validation import validate_password
from .models.deletion_requests import DeletionRequest
from authentication.models.mfa_settings import MFASettings
from rest_framework import serializers
from django.contrib.auth.models import User
from authentication.utilsy import decode_verification_token
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from authentication.models.sessions import UserSession
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator

# Defining constants for MFA methods
MFA_METHODS = (
    ('qr_code', 'QR Code (TOTP)'),
    ('passkey', 'Passkey (WebAuthn)'),
    ('email', 'Email Verification'),
    ('sms', 'SMS Verification'),
)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model, exposing additional user profile data.
    """
    password = serializers.CharField(write_only=True)
    class Meta:
        model = UserProfile
        fields = (
            'id', 'bio', 'profile_picture', 'preferences',
            'website', 'avatar', 'country', 'state', 'phone_number', 
            'date_joined', 'last_active' 'email', 'password', 
            'first_name', 'last_name', 'is_active'
        )

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        # Hash password before saving the user
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model. This is used for registration, login, and user profile updates.
    Includes basic fields for user management.
    """
    profile = UserProfileSerializer(read_only=True)
    phone_number = PhoneNumberField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'is_active', 'is_staff', 'is_superuser',
            'phone_number', 'profile', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'profile')

    def validate_email(self, value):
        """
        Ensure the email is unique.
        """
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError(_("This email address is already in use."))
        return value
    

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
        password = validated_data.pop("password") # Remove Password before saving
        validated_data.pop("password2")  # Remove password2 before saving
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MagicLinkTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for magic link token used for password-less authentication.
    """
    class Meta:
        model = MagicLinkToken
        fields = ('token', 'created_at', 'expires_at')
        read_only_fields = ('token', 'created_at', 'expires_at')


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit log entries tracking user activity.
    """
    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'action', 'timestamp', 'ip_address', 'user_agent')
        read_only_fields = ('id', 'timestamp')


c

class LoginUserSerializer(serializers.Serializer):
    """
    Serializer for user login. It only needs to validate the provided credentials.
    """
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
            user = authenticate(**data)
            if user and user.is_active:
                return user
            raise serializers.ValidationError("Incorrect Credentials!")  

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # Include role in JWT
        return token


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing the user's password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        """
        Add custom validation for the new password (e.g., minimum length).
        """
        if len(value) < 8:
            raise serializers.ValidationError(_("Password must be at least 8 characters long."))
        return value


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class TrustedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustedDevice
        fields = ['device_token', 'device_info', 'last_used', 'expires_at']


class BlockedIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedIP
        fields = '__all__'


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin updates on user status such as suspension and probation.
    """
    class Meta:
        model = User
        fields = [
            'is_suspended', 'suspension_reason',
            'suspension_start_date', 'suspension_end_date',
            'is_on_probation', 'probation_reason', 'is_available'
        ]


# MFASettings Serializer to handle MFA configurations and settings
class MFASettingsSerializer(serializers.ModelSerializer):
    """
    Serializer to manage MFA settings and configurations, supporting multiple MFA methods.
    """
    mfa_method = serializers.ChoiceField(
        choices=MFA_METHODS,
        required=True
    )
    mfa_secret = serializers.CharField(
        write_only=True, required=False,
        allow_blank=True, max_length=256
    )
    mfa_phone_number = serializers.CharField(
        write_only=True, required=False,
        allow_blank=True
    )
    passkey_public_key = serializers.CharField(
        write_only=True, required=False,
        allow_blank=True, max_length=512
    )
    is_mfa_enabled = serializers.BooleanField(default=False)
    backup_codes = serializers.ListField(
        child=serializers.CharField(max_length=16),
        required=False, write_only=True
    )
    mfa_email_verified = serializers.BooleanField(default=False)

    class Meta:
        model = MFASettings
        fields = [
            'user', 'mfa_method', 'mfa_secret', 'mfa_phone_number',
            'passkey_public_key', 'is_mfa_enabled', 'backup_codes', 'mfa_email_verified'
        ]

    def create(self, validated_data):
        """
        Create MFA settings for a user, ensuring they can choose from multiple MFA methods.
        """
        mfa_settings, created = MFASettings.objects.get_or_create(
            user=validated_data['user']
        )
        mfa_settings.mfa_method = validated_data.get(
            'mfa_method', 'qr_code'
        )  # Default to QR code
        mfa_settings.mfa_secret = validated_data.get('mfa_secret', '')
        mfa_settings.passkey_public_key = validated_data.get(
            'passkey_public_key', ''
        )
        mfa_settings.mfa_phone_number = validated_data.get(
            'mfa_phone_number', ''
        )
        mfa_settings.is_mfa_enabled = validated_data.get(
            'is_mfa_enabled', False
        )
        mfa_settings.backup_codes = validated_data.get('backup_codes', [])
        mfa_settings.mfa_email_verified = validated_data.get(
            'mfa_email_verified', False
        )
        mfa_settings.save()
        return mfa_settings

    def update(self, instance, validated_data):
        """
        Update existing MFA settings, including
        changing MFA methods or secret.
        """
        instance.mfa_method = validated_data.get(
            'mfa_method', instance.mfa_method
        )
        instance.mfa_secret = validated_data.get(
            'mfa_secret', instance.mfa_secret
        )
        instance.passkey_public_key = validated_data.get(
            'passkey_public_key', instance.passkey_public_key
        )
        instance.mfa_phone_number = validated_data.get(
            'mfa_phone_number', instance.mfa_phone_number
        )
        instance.is_mfa_enabled = validated_data.get(
            'is_mfa_enabled', instance.is_mfa_enabled
        )
        instance.backup_codes = validated_data.get(
            'backup_codes', instance.backup_codes
        )
        instance.mfa_email_verified = validated_data.get(
            'mfa_email_verified', instance.mfa_email_verified
        )
        instance.save()
        return instance


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ["id", "reason", "status", "requested_at", "admin_response"]


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
    impersonated_by = serializers.ReadOnlyField(
        source='impersonated_by.username'
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'is_impersonated', 'impersonated_by'
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


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ['user', 'request_time', 'status',
                  'confirmation_time', 'rejection_time', 'reason'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration. This will validate the incoming
    data and save a new user record.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create and return a new user instance, securely hashing the password.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class FinalizeAccountSerializer(serializers.Serializer):
    """
    Serializer for finalizing account activation using the verification token.
    This is used in the FinalizeAccountView to validate the token.
    """

    token = serializers.CharField()

    def validate_token(self, value):
        """
        Validates the provided token and ensures it is correct.
        """
        try:
            user = decode_verification_token(value)
            if not user:
                raise serializers.ValidationError("Invalid or expired token.")
            return value
        except Exception:
            raise serializers.ValidationError("Invalid or expired token.")


class ActivationSerializer(serializers.Serializer):
    """
    Serializer for handling the account activation using the token.
    """

    token = serializers.CharField()
    email = serializers.EmailField()

    def validate_token(self, value):
        """
        Validates the provided token. If the token is expired or incorrect,
        a validation error will be raised.
        """
        try:
            user = User.objects.get(email=self.initial_data.get('email'))
            if not default_token_generator.check_token(user, value):
                raise serializers.ValidationError("Invalid or expired token.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

# Serializer for OTP (One-Time Password) verification
class OTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, required=True)

    def validate_otp_code(self, value):
        # Validate the OTP code length
        if len(value) != 6:
            raise serializers.ValidationError("Invalid OTP code length.")
        return value


# MFA Recovery Serializer for recovering MFA when the user is locked out
class MFARecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_mfa_enabled:
                raise serializers.ValidationError("MFA is not enabled on this account.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


# Serializer to represent active user sessions
class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ['id', 'device_info', 'ip_address', 'last_active']