from django.contrib import admin

from authentication.models.account_deletion_request import (
    AccountDeletionRequest,
)
from authentication.models.account_unlock_request import (
    AccountUnlockRequest,
)
from authentication.models.backup_code import BackupCode
from authentication.models.device_fingerprinting import DeviceFingerprint
from authentication.models.impersonation_log import ImpersonationLog
from authentication.models.impersonation_token import ImpersonationToken
from authentication.models.login_session import LoginSession
from authentication.models.mfa_device import MFADevice
from authentication.models.mfa_settings import MFASettings
from authentication.models.otp_code import OTPCode
from authentication.models.password_reset_request import PasswordResetRequest
from authentication.models.registration_token import RegistrationToken
from authentication.models.security_events import SecurityEvent


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "session_type",
        "ip_address",
        "device_name",
        "logged_in_at",
        "last_activity_at",
        "expires_at",
        "revoked_at",
        "is_active_display",
    )
    list_filter = (
        "session_type",
        "website",
        "logged_in_at",
        "expires_at",
        "revoked_at",
    )
    search_fields = (
        "user__email",
        "user__username",
        "ip_address",
        "device_name",
        "fingerprint_hash",
    )
    readonly_fields = (
        "logged_in_at",
        "last_activity_at",
        "expires_at",
        "revoked_at",
    )

    @admin.display(boolean=True, description="Is active")
    def is_active_display(self, obj):
        return obj.is_active


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "device_name",
        "ip_address",
        "is_trusted",
        "trust_score",
        "login_count",
        "last_seen_at",
        "created_at",
    )
    list_filter = (
        "website",
        "is_trusted",
        "created_at",
        "last_seen_at",
    )
    search_fields = (
        "user__email",
        "user__username",
        "device_name",
        "ip_address",
        "fingerprint_hash",
    )
    readonly_fields = (
        "fingerprint_hash",
        "created_at",
        "last_seen_at",
    )


@admin.register(MFASettings)
class MFASettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "is_enabled",
        "preferred_method",
        "skip_on_trusted",
        "updated_at",
    )
    list_filter = (
        "website",
        "is_enabled",
        "preferred_method",
        "skip_on_trusted",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(MFADevice)
class MFADeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "name",
        "method",
        "is_primary",
        "is_verified",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "website",
        "method",
        "is_primary",
        "is_verified",
        "is_active",
    )
    search_fields = (
        "user__email",
        "user__username",
        "name",
        "email",
        "phone_number",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "used_at",
        "created_at",
    )
    list_filter = (
        "website",
        "used_at",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "code_hash",
        "used_at",
        "created_at",
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "purpose",
        "expires_at",
        "used_at",
        "attempts",
        "max_attempts",
        "created_at",
        "is_valid_display",
    )
    list_filter = (
        "website",
        "purpose",
        "used_at",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "code_hash",
        "created_at",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid_display(self, obj):
        return obj.is_valid


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "expires_at",
        "used_at",
        "created_at",
        "is_valid_display",
    )
    list_filter = (
        "website",
        "used_at",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "token_hash",
        "otp_hash",
        "created_at",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid_display(self, obj):
        return obj.is_valid


@admin.register(RegistrationToken)
class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "expires_at",
        "used_at",
        "created_at",
        "is_valid_display",
    )
    list_filter = (
        "website",
        "used_at",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "token_hash",
        "created_at",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid_display(self, obj):
        return obj.is_valid


@admin.register(AccountUnlockRequest)
class AccountUnlockRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "expires_at",
        "used_at",
        "created_at",
        "is_valid_display",
    )
    list_filter = (
        "website",
        "used_at",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "user__email",
        "user__username",
    )
    readonly_fields = (
        "token_hash",
        "created_at",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid_display(self, obj):
        return obj.is_valid


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "status",
        "requested_at",
        "confirmed_at",
        "scheduled_deletion_at",
        "retained_until",
        "completed_at",
        "purged_at",
    )
    list_filter = (
        "website",
        "status",
        "requested_at",
        "scheduled_deletion_at",
        "retained_until",
        "completed_at",
        "purged_at",
    )
    search_fields = (
        "user__email",
        "user__username",
        "reason",
    )
    readonly_fields = (
        "requested_at",
        "confirmed_at",
        "access_revoked_at",
        "scheduled_deletion_at",
        "retained_until",
        "completed_at",
        "purged_at",
    )


@admin.register(ImpersonationToken)
class ImpersonationTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "admin_user",
        "target_user",
        "website",
        "created_at",
        "expires_at",
        "used_at",
        "is_valid_display",
    )
    list_filter = (
        "website",
        "created_at",
        "expires_at",
        "used_at",
    )
    search_fields = (
        "admin_user__email",
        "target_user__email",
    )
    readonly_fields = (
        "token_hash",
        "created_at",
        "used_at",
    )

    @admin.display(boolean=True, description="Is valid")
    def is_valid_display(self, obj):
        return obj.is_valid


@admin.register(ImpersonationLog)
class ImpersonationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "admin_user",
        "target_user",
        "website",
        "action",
        "ip_address",
        "created_at",
    )
    list_filter = (
        "website",
        "action",
        "created_at",
    )
    search_fields = (
        "admin_user__email",
        "target_user__email",
        "reason",
        "ip_address",
    )
    readonly_fields = (
        "created_at",
    )


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "website",
        "event_type",
        "severity",
        "is_suspicious",
        "ip_address",
        "created_at",
    )
    list_filter = (
        "website",
        "event_type",
        "severity",
        "is_suspicious",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__username",
        "ip_address",
        "location",
        "device",
    )
    readonly_fields = (
        "created_at",
        "metadata",
    )