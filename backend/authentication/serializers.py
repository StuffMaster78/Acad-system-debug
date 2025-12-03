import requests
from django.conf import settings
from rest_framework import serializers
from .models import AuditLog, TrustedDevice, BlockedIP, AccountDeletionRequest
from .models.magic_links import MagicLink
from rest_framework import serializers
from websites.models import Website
from django.contrib.auth import get_user_model
from users.models import UserProfile  # Adjusted to import UserProfile from users app
from .models import AuditLog
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField # type: ignore
from django.contrib.auth.password_validation import validate_password
from .models.deletion_requests import AccountDeletionRequest
from authentication.models.impersonation import ImpersonationLog, ImpersonationToken
from authentication.models.login import LoginSession
from authentication.models.lockout import AccountLockout
from authentication.models.mfa_settings import MFASettings
from authentication.models.logout import LogoutEvent
from rest_framework import serializers
from django.contrib.auth.models import User
from authentication.utilsy import decode_verification_token
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from authentication.models.sessions import UserSession
from authentication.models.tokens import SecureToken, SecureTokenManager
from authentication.models.security_questions import (
    SecurityQuestion,
    UserSecurityQuestion,
)
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from authentication.utils.jwt import decode_password_reset_token
from authentication.utils.mfa import get_mfa_session_by_token, verify_mfa_code
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from authentication.models.login import LoginSession
from authentication.models.logout import LogoutEvent
from django.utils.timezone import now
from authentication.models.otp import OTP
from authentication.models.password_reset import PasswordResetRequest
from authentication.services.password_reset_service import PasswordResetService
from authentication.services.token_services import SecureTokenService
from authentication.models.backup_code import BackupCode
from authentication.models.register import RegistrationToken
from authentication.services.otp_service import OTPService
from authentication.services.registration_token_service import (
    RegistrationTokenService
)

from rest_framework.permissions import AllowAny
from authentication.services.totp_service import TOTPService
from authentication.models.tokens import SecureToken, EncryptedRefreshToken
from authentication.models.password_security import PasswordHistory, PasswordExpirationPolicy, PasswordBreachCheck
from authentication.models.account_security import (
    AccountSuspension, IPWhitelist, UserIPWhitelistSettings,
    EmailChangeRequest, PhoneVerification
)
from authentication.models.session_limits import SessionLimitPolicy
from authentication.models.magic_links import MagicLink
from authentication.services.magic_link_service import MagicLinkService

User = get_user_model()

# Defining constants for MFA methods
MFA_METHODS = (
    ('qr_code', 'QR Code (TOTP)'),
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
        model = MagicLink
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


class LoginSessionSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    device_type = serializers.SerializerMethodField()
    browser = serializers.SerializerMethodField()
    os = serializers.SerializerMethodField()
    
    class Meta:
        model = LoginSession
        fields = [
            "id", "user", "website", "ip_address", "user_agent",
            "device_name", "logged_in_at", "last_activity", "is_active", 
            "token", "revoked_at", "is_current", "location", "device_type",
            "browser", "os"
        ]
        read_only_fields = ["logged_in_at", "id", "user", "last_activity", "revoked_at"]
    
    def get_is_current(self, obj):
        """Check if this is the current session."""
        request = self.context.get('request')
        if not request:
            return False
        # Try to match by token or session ID
        current_token = getattr(request, 'auth', None)
        if current_token and hasattr(current_token, 'token'):
            return obj.token == current_token.token
        return False
    
    def get_location(self, obj):
        """Extract location from IP if available."""
        # This would typically use a geolocation service
        # For now, return IP-based location if we have country info
        if hasattr(obj, 'country'):
            return obj.country
        return None
    
    def get_device_type(self, obj):
        """Parse device type from user agent."""
        if not obj.user_agent:
            return 'unknown'
        ua = obj.user_agent.lower()
        if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
            return 'mobile'
        if 'tablet' in ua or 'ipad' in ua:
            return 'tablet'
        return 'desktop'
    
    def get_browser(self, obj):
        """Parse browser from user agent."""
        if not obj.user_agent:
            return 'Unknown'
        ua = obj.user_agent.lower()
        if 'chrome' in ua and 'edg' not in ua:
            return 'Chrome'
        if 'firefox' in ua:
            return 'Firefox'
        if 'safari' in ua and 'chrome' not in ua:
            return 'Safari'
        if 'edg' in ua:
            return 'Edge'
        if 'opera' in ua:
            return 'Opera'
        return 'Unknown'
    
    def get_os(self, obj):
        """Parse OS from user agent."""
        if not obj.user_agent:
            return 'Unknown'
        ua = obj.user_agent.lower()
        if 'windows' in ua:
            return 'Windows'
        if 'mac' in ua or 'darwin' in ua:
            return 'macOS'
        if 'linux' in ua:
            return 'Linux'
        if 'android' in ua:
            return 'Android'
        if 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
            return 'iOS'
        return 'Unknown'

class LoginSerializer(serializers.Serializer):
    """ Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField()

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
        mfa_settings, created = MFASettings.get_or_create_for_user(validated_data['user'])
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


class ImpersonationTokenSerializer(serializers.ModelSerializer):
    """
    Full token detail serializer.
    """

    class Meta:
        model = ImpersonationToken
        fields = [
            "id",
            "token",
            "admin_user",
            "target_user",
            "created_at",
            "expires_at"
        ]
        read_only_fields = ["token", "admin_user", "created_at", "expires_at"]


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

    def validate(self, attrs):
        """Validate registration data."""
        # Check if username already exists
        if User.objects.filter(username=attrs.get('username')).exists():
            raise serializers.ValidationError({'username': 'A user with this username already exists.'})
        
        # Check if email already exists
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance, securely hashing the password.
        """
        from websites.models import Website
        
        # Get or create a default website for registration
        website = Website.objects.filter(is_active=True).first()
        if not website:
            # Create a default website if none exists
            website = Website.objects.create(
                name="Default Website",
                domain='http://localhost',
                is_active=True,
                slug='default'
            )
        
        # Create user with default role 'client' and assign website
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            role='client',  # Default role for registration
            website=website,  # Assign website
            is_active=True,  # Activate immediately (can be changed later)
        )
        
        # Force save to ensure user is persisted
        user.save()
        
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
    """
    Serializer for displaying and managing user sessions.
    """

    class Meta:
        model = UserSession
        fields = [
            "id",
            "session_key",
            "ip_address",
            "device_type",
            "user_agent",
            "country",
            "created_at",
            "last_activity",
            "expires_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "session_key",
            "created_at",
            "last_activity",
            "expires_at",
            "is_active"
        ]


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Validates the email field for requesting a password reset.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        # Optional: Check if user exists, silently ignore if not.
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Validates new password and token for confirming the reset.
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            # We don’t reveal if the email exists for security reasons
            return value
        self.context['user'] = user
        return value

    @property
    def validated_data(self):
        # Expose user for the view after validation
        data = super().validated_data
        data["user"] = self.context.get("user")
        return data


class PasswordResetTokenValidationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = decode_password_reset_token(value)
        except Exception as e:
            raise serializers.ValidationError("Invalid or expired token.")
        self.context['user'] = user
        return value

    @property
    def validated_data(self):
        data = super().validated_data
        data["user"] = self.context.get("user")
        return data


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate_token(self, value):
        try:
            user = decode_password_reset_token(value)
        except Exception:
            raise serializers.ValidationError("Invalid or expired token.")
        self.context['user'] = user
        return value

    def validate_password(self, value):
        # Add your custom password validators here if any
        return value

    def validate(self, attrs):
        # Make user available after full validation
        attrs['user'] = self.context.get('user')
        return attrs


class MFAChallengeSerializer(serializers.Serializer):
    """
    Serializer for handling MFA challenge verification.
    """
    mfa_token = serializers.CharField(
        help_text="Temporary MFA session token issued after initial login."
    )
    code = serializers.CharField(
        max_length=6,
        help_text="The 6-digit MFA code from your authenticator or SMS."
    )

    def validate(self, data):
        token = data.get("mfa_token")
        code = data.get("code")

        # Replace with your actual token/session lookup
        mfa_session = get_mfa_session_by_token(token)
        if not mfa_session:
            raise serializers.ValidationError("Invalid or expired MFA token.")

        # Replace with your actual code validation
        if not verify_mfa_code(mfa_session.user, code):
            raise serializers.ValidationError("Invalid MFA code.")

        data["user"] = mfa_session.user
        return data


class MFAChallengeVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying the MFA challenge response.
    """
    mfa_token = serializers.CharField(
        help_text="Temporary MFA token issued after initial authentication."
    )
    code = serializers.CharField(
        max_length=6,
        help_text="The MFA code (e.g., TOTP, SMS) submitted by the user."
    )

    def validate(self, data):
        mfa_token = data.get("mfa_token")
        code = data.get("code")

        # Hypothetical function to fetch MFA session/context
        mfa_session = get_mfa_session_by_token(mfa_token)
        if not mfa_session:
            raise serializers.ValidationError("Invalid or expired MFA token.")

        # Hypothetical function to verify the MFA code
        if not verify_mfa_code(mfa_session.user, code):
            raise serializers.ValidationError("MFA code verification failed.")

        # Mark the session as verified or return user info
        data["user"] = mfa_session.user
        data["verified"] = True

        return data
    


class CreateImpersonationTokenSerializer(serializers.Serializer):
    """
    Serializer to accept target user ID.
    """
    target_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())



class AccountLockoutSerializer(serializers.ModelSerializer):
    """
    Serializer for account lockout records.
    """
    user_email = serializers.EmailField(source="user.email", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)

    class Meta:
        model = AccountLockout
        fields = [
            "id",
            "user",
            "user_email",
            "website",
            "website_domain",
            "reason",
            "locked_at",
            "active",
        ]
        read_only_fields = [
            "id", "locked_at", "user_email", "website_domain"
        ]

class LogoutEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogoutEvent
        fields = [
            'id', 'user', 'website', 'timestamp', 'ip_address',
            'user_agent', 'session_key', 'reason'
        ]
        read_only_fields = ['id', 'timestamp', 'user']

class AdminKickoutSerializer(serializers.Serializer):
    """
    Validates input for admin-initiated user kickout.
    """
    user_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)
    ip_address = serializers.IPAddressField(required=False)
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional reason for the kickout (audit, security, etc.)"
    )

    def validate(self, attrs):
        """
        Ensure at least one identifier is provided and user exists.
        """
        user_id = attrs.get("user_id")
        username = attrs.get("username")

        if not user_id and not username:
            raise serializers.ValidationError(
                "Either user_id or username is required."
            )

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this ID not found.")
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this username not found.")

        attrs["target_user"] = user
        return attrs
    
class SessionManagementViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def kick_others(self, request):
        """
        Ends all other active sessions except the current one.
        """
        user = request.user
        current_token = request.auth  # Assuming JWT or session token

        sessions = LoginSession.objects.filter(
            user=user,
            website=user.website,
            is_active=True
        ).exclude(token=current_token)

        for session in sessions:
            from authentication.services.logout_event_service import LogoutEventService
            LogoutEventService.log_event(
                user=user,
                website=user.website,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                session_key=session.token,
                reason="kick_other_sessions"
            )
            session.is_active = False
            session.save()

        return Response(
            {"detail": "All other sessions have been logged out."},
            status=status.HTTP_200_OK
        )
    

class OTPSerializer(serializers.ModelSerializer):
    """
    Serializer for OTP data (mostly for debug or testing).
    """

    class Meta:
        model = OTP
        fields = ["id", "user", "website", "otp_code", "expiration_time"]
        read_only_fields = fields

class PasswordResetRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the PasswordResetRequest model.
    """

    class Meta:
        model = PasswordResetRequest
        fields = [
            "id",
            "user",
            "website",
            "token",
            "created_at",
            "is_used"
        ]
        read_only_fields = ["token", "created_at", "is_used"]


class InitiatePasswordResetSerializer(serializers.Serializer):
    """
    Serializer to initiate a password reset via email and website context.
    """
    email = serializers.EmailField()
    website = serializers.SlugRelatedField(
        slug_field="domain",
        queryset=Website.objects.all()
    )

    def validate(self, attrs):
        """
        Checks if the user exists for the given website and email.
        """
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """
        Generates a password reset token.
        """
        service = PasswordResetService(
            user=validated_data["user"],
            website=validated_data["website"]
        )
        reset_obj = service.generate_reset_token()
        return reset_obj
    

class VerifyResetTokenSerializer(serializers.Serializer):
    """
    Serializer to verify a password reset token.
    """
    token = serializers.CharField(max_length=255)

    def validate_token(self, value):
        """
        Validates that the token exists, is not used, and is not expired.
        """
        try:
            reset_obj = PasswordResetRequest.objects.get(token=value)
        except PasswordResetRequest.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")

        if reset_obj.is_used:
            raise serializers.ValidationError("Token already used.")

        if reset_obj.is_expired():
            raise serializers.ValidationError("Token has expired.")

        return value
    

class CompletePasswordResetSerializer(serializers.Serializer):
    """
    Serializer to set a new password using a valid reset token.
    """
    token = serializers.CharField(max_length=255)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        """
        Validates the new password with Django's built-in validators.
        """
        validate_password(value)
        return value

    def validate(self, attrs):
        """
        Validates token and attaches user instance for password update.
        """
        try:
            reset_obj = PasswordResetRequest.objects.get(token=attrs["token"])
        except PasswordResetRequest.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})

        if reset_obj.is_used:
            raise serializers.ValidationError({"token": "Token already used."})

        if reset_obj.is_expired():
            raise serializers.ValidationError({"token": "Token has expired."})

        attrs["user"] = reset_obj.user
        attrs["reset_obj"] = reset_obj
        return attrs

    def save(self):
        """
        Updates the user's password and marks the token as used.
        """
        user = self.validated_data["user"]
        reset_obj = self.validated_data["reset_obj"]
        password = self.validated_data["new_password"]

        user.set_password(password)
        user.save()

        reset_obj.is_used = True
        reset_obj.save()

        return user
    
class BackupCodeGenerateSerializer(serializers.Serializer):
    """
    Serializer for generating backup codes.
    """
    count = serializers.IntegerField(
        min_value=1,
        max_value=20,
        default=10,
        help_text="Number of backup codes to generate (1–20)"
    )


class BackupCodeVerifySerializer(serializers.Serializer):
    """
    Serializer for validating a submitted backup code.
    """
    code = serializers.CharField(
        max_length=64,
        help_text="The backup code provided by the user"
    )


class BackupCodeListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer to list previously issued backup codes
    (hashed, no plaintext returned).
    """

    class Meta:
        model = BackupCode
        fields = ["id", "used", "created_at", "used_at"]
        read_only_fields = fields



class RegistrationTokenSerializer(serializers.ModelSerializer):
    """
    Serializes RegistrationToken data.
    """

    class Meta:
        model = RegistrationToken
        fields = [
            "id",
            "token",
            "created_at",
            "expires_at",
            "is_used"
        ]
        read_only_fields = ["id", "token", "created_at", "expires_at", "is_used"]


class RegistrationTokenValidationSerializer(serializers.Serializer):
    """
    Accepts token string input for registration token validation.
    """
    token = serializers.UUIDField()

class RegistrationTokenConfirmationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    otp_code = serializers.CharField()
    captcha_token = serializers.CharField()

    def validate_captcha_token(self, value):
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': value
            }
        )
        result = response.json()
        if not result.get("success"):
            raise serializers.ValidationError("CAPTCHA validation failed.")
        return value
    


class RegistrationConfirmationViewSet(viewsets.ViewSet):
    """
    Confirms a user registration via token and OTP.
    """
    permission_classes = [AllowAny]

    def create(self, request):
        """
        POST /api/v1/auth/registration/confirm/
        """
        serializer = RegistrationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user  # or fetch based on token if unauthenticated
        website = request.headers.get("X-Website")  # or however you're passing it
        token = serializer.validated_data['token']
        otp_code = serializer.validated_data['otp_code']

        confirmation_service = RegistrationTokenService(user, website)
        otp_service = OTPService(user, website)

        try:
            confirmation_service.confirm_registration(token, otp_code, otp_service)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Registration confirmed successfully."},
            status=status.HTTP_200_OK
        )
    

class MFASettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for reading and updating MFA settings.
    """

    class Meta:
        model = MFASettings
        fields = [
            "is_mfa_enabled",
            "mfa_method",
            "mfa_phone_number",
            "mfa_email_verified",
        ]
        read_only_fields = ["mfa_email_verified"]


class MFAOtpVerificationSerializer(serializers.Serializer):
    """
    Serializer to verify an OTP code for 2FA.
    """
    otp_code = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text="The 6-digit OTP code."
    )


class MFAEnableSerializer(serializers.Serializer):
    """
    Serializer to enable MFA for a user.
    """
    method = serializers.ChoiceField(
        choices=[
            ("qr_code", "QR Code (TOTP)"),
            ("email", "Email Verification"),
            ("sms", "SMS Verification"),
        ],
        help_text="The MFA method to enable."
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required if SMS is chosen as MFA method."
    )


class MFARecoveryTokenSerializer(serializers.Serializer):
    """
    Serializer for verifying an MFA recovery token.
    """
    recovery_token = serializers.CharField(
        help_text="The recovery token used for MFA recovery."
    )



class TOTPSetupSerializer(serializers.Serializer):
    """
    Handles TOTP setup: generates secret, QR code.
    """
    qr_code = serializers.CharField(read_only=True)
    secret = serializers.CharField(read_only=True)

    def create(self, validated_data):
        user = self.context["request"].user
        secret = TOTPService.generate_totp_secret()
        qr_code = TOTPService.generate_qr_code(
            username=user.email,  # Or username
            secret=secret,
            issuer="YourApp"  # Replace with your app name
        )

        mfa_settings, _ = MFASettings.get_or_create_for_user(user)
        mfa_settings.mfa_method = "qr_code"
        mfa_settings.mfa_secret = secret
        mfa_settings.save()

        return {
            "qr_code": qr_code,
            "secret": secret
        }


class TOTPVerifySerializer(serializers.Serializer):
    """
    Verifies the TOTP code provided by the user.
    """
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user = self.context["request"].user
        otp_code = attrs.get("otp_code")

        try:
            mfa = MFASettings.objects.get(user=user)
        except MFASettings.DoesNotExist:
            raise serializers.ValidationError("MFA not initialized.")

        if not mfa.mfa_secret:
            raise serializers.ValidationError("TOTP secret not found.")

        if not TOTPService.verify_totp(mfa.mfa_secret, otp_code):
            raise serializers.ValidationError("Invalid OTP code.")

        # If successful, enable MFA
        mfa.is_mfa_enabled = True
        mfa.otp_code = None
        mfa.otp_expires_at = None
        mfa.save()

        return {"success": True}



class SecureTokenCreateSerializer(serializers.Serializer):
    purpose = serializers.ChoiceField(choices=SecureToken.TOKEN_PURPOSE_CHOICES)
    raw_token = serializers.CharField(write_only=True, max_length=4096)
    expires_at = serializers.DateTimeField()

    def validate_expires_at(self, value):
        if value <= now():
            raise serializers.ValidationError("Expiry must be in the future.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        website = self.context["website"]

        from authentication.services.token_services import SecureTokenService
        service = SecureTokenService(user=user, website=website)

        return service.create_token(
            raw_token=validated_data["raw_token"],
            purpose=validated_data["purpose"],
            expires_at=validated_data["expires_at"]
        )


class SecureTokenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecureToken
        fields = [
            "id", "purpose", "created_at", "expires_at", "is_active"
        ]


class SecureTokenDecryptSerializer(serializers.Serializer):
    token_id = serializers.UUIDField()

    def validate(self, data):
        user = self.context["request"].user
        website = self.context["website"]
        from authentication.services.token_services import SecureTokenService

        service = SecureTokenService(user=user, website=website)
        token = service.get_token_by_id(data["token_id"])

        if not token.is_active or token.expires_at <= now():
            raise serializers.ValidationError("Token is inactive or expired.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        website = self.context["website"]
        service = SecureTokenService(user=user, website=website)
        return {"decrypted_token": service.decrypt_token_by_id(validated_data["token_id"])}


class EncryptedRefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EncryptedRefreshToken
        fields = ["id", "created_at"]

class MagicLinkRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a magic link via email.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        website = self.context["website"]
        try:
            user = User.objects.get(email=value, website=website)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found for this website.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        website = self.context["website"]
        request = self.context["request"]
        user = User.objects.get(email=email, website=website)

        ip = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")

        service = MagicLinkService(website)
        magic_link = service.create_magic_link(user, ip=ip, user_agent=user_agent)

        # 👇 Plug your email service here
        # send_magic_link_email(user.email, token=magic_link.token)

        return {"message": "Magic link sent."}


class MagicLinkVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying the magic link token.
    """
    token = serializers.UUIDField()

    def validate_token(self, value):
        website = self.context["website"]
        service = MagicLinkService(website)

        try:
            self.link = service.validate_token(str(value))
        except Exception as e:
            raise serializers.ValidationError(str(e))

        return value

    def create(self, validated_data):
        website = self.context["website"]
        token = str(validated_data["token"])
        service = MagicLinkService(website)

        user = service.consume_token(token)
        return user


# Security Features Serializers

class PasswordHistorySerializer(serializers.ModelSerializer):
    """Serializer for password history."""
    class Meta:
        model = PasswordHistory
        fields = ['id', 'created_at']
        read_only_fields = ['id', 'created_at']


class PasswordExpirationPolicySerializer(serializers.ModelSerializer):
    """Serializer for password expiration policy."""
    expires_at = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    days_until_expiration = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordExpirationPolicy
        fields = [
            'id', 'password_changed_at', 'expires_in_days', 'warning_days_before',
            'is_exempt', 'last_warning_sent', 'expires_at', 'is_expired',
            'is_expiring_soon', 'days_until_expiration'
        ]
        read_only_fields = ['id', 'password_changed_at', 'last_warning_sent']
    
    def get_expires_at(self, obj):
        return obj.expires_at.isoformat() if obj.expires_at else None
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_is_expiring_soon(self, obj):
        return obj.is_expiring_soon
    
    def get_days_until_expiration(self, obj):
        return obj.days_until_expiration


class PasswordBreachCheckSerializer(serializers.ModelSerializer):
    """Serializer for password breach checks."""
    class Meta:
        model = PasswordBreachCheck
        fields = [
            'id', 'password_hash_prefix', 'is_breached', 'breach_count',
            'checked_at', 'action_taken'
        ]
        read_only_fields = ['id', 'checked_at']


class AccountSuspensionSerializer(serializers.ModelSerializer):
    """Serializer for account suspension."""
    class Meta:
        model = AccountSuspension
        fields = [
            'id', 'is_suspended', 'suspended_at', 'suspension_reason',
            'scheduled_reactivation', 'reactivated_at'
        ]
        read_only_fields = ['id', 'suspended_at', 'reactivated_at']


class IPWhitelistSerializer(serializers.ModelSerializer):
    """Serializer for IP whitelist entries."""
    class Meta:
        model = IPWhitelist
        fields = [
            'id', 'ip_address', 'label', 'created_at', 'last_used', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']


class UserIPWhitelistSettingsSerializer(serializers.ModelSerializer):
    """Serializer for IP whitelist settings."""
    class Meta:
        model = UserIPWhitelistSettings
        fields = [
            'id', 'is_enabled', 'allow_emergency_bypass', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailChangeRequestSerializer(serializers.ModelSerializer):
    """Serializer for email change requests."""
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    approved_by_email = serializers.CharField(source='approved_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = EmailChangeRequest
        fields = [
            'id', 'user', 'user_email', 'old_email', 'new_email', 'status', 'status_display',
            'verified', 'old_email_confirmed', 'admin_approved', 'approved_by', 'approved_by_email',
            'approved_at', 'rejection_reason', 'created_at', 'expires_at', 'completed_at',
            'is_expired', 'is_valid'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'expires_at', 'completed_at',
            'admin_approved', 'approved_by', 'approved_at'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_is_valid(self, obj):
        return obj.is_valid


class PhoneVerificationSerializer(serializers.ModelSerializer):
    """Serializer for phone verification."""
    is_expired = serializers.SerializerMethodField()
    is_exhausted = serializers.SerializerMethodField()
    attempts_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = PhoneVerification
        fields = [
            'id', 'phone_number', 'is_verified', 'verified_at',
            'created_at', 'expires_at', 'attempts', 'max_attempts',
            'is_expired', 'is_exhausted', 'attempts_remaining'
        ]
        read_only_fields = [
            'id', 'verification_code', 'created_at', 'expires_at',
            'attempts', 'verified_at'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired
    
    def get_is_exhausted(self, obj):
        return obj.is_exhausted
    
    def get_attempts_remaining(self, obj):
        return max(0, obj.max_attempts - obj.attempts)


class SessionLimitPolicySerializer(serializers.ModelSerializer):
    """Serializer for session limit policy."""
    active_sessions = serializers.SerializerMethodField()
    remaining_sessions = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionLimitPolicy
        fields = [
            'id', 'max_concurrent_sessions', 'allow_unlimited_trusted',
            'revoke_oldest_on_limit', 'active_sessions', 'remaining_sessions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_sessions(self, obj):
        from authentication.services.session_limit_service import SessionLimitService
        service = SessionLimitService(obj.user)
        return service.get_active_session_count()
    
    def get_remaining_sessions(self, obj):
        active = self.get_active_sessions(obj)
        return max(0, obj.max_concurrent_sessions - active)


class SecurityQuestionSerializer(serializers.ModelSerializer):
    """Serializer for security questions."""
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question_text', 'is_active']
        read_only_fields = ['id']


class UserSecurityQuestionSerializer(serializers.ModelSerializer):
    """Serializer for user security questions."""
    question_text = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSecurityQuestion
        fields = [
            'id', 'question', 'custom_question', 'question_text',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_text(self, obj):
        return obj.get_question_text()

