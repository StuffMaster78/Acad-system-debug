from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models.passkeys import WebAuthnCredential
from authentication.models import MFASettings

# Register WebAuthnCredential model in the admin
@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    """
    Admin interface for WebAuthn credentials, including the ability to view,
    search, and revoke credentials.
    """
    list_display = (
        'user', 'credential_id_display', 'public_key_display',
        'sign_count', 'created_at', 'updated_at'
    )
    search_fields = ('user__username', 'credential_id', 'public_key')
    list_filter = ('user', 'created_at')
    actions = ['revoke_credentials']

    def credential_id_display(self, obj):
        """
        Displays the first 10 characters of the credential ID for easier
        identification in the admin interface.
        """
        return format_html('<span>{}</span>', obj.credential_id[:10] + '...')
    credential_id_display.short_description = 'Credential ID'

    def public_key_display(self, obj):
        """
        Displays the first 10 characters of the public key for easier
        identification in the admin interface.
        """
        return format_html('<span>{}</span>', obj.public_key[:10] + '...')
    public_key_display.short_description = 'Public Key'

    def revoke_credentials(self, request, queryset):
        """
        Revokes selected WebAuthn credentials by deleting them from the database.
        """
        for credential in queryset:
            credential.delete()
        self.message_user(request, f'{queryset.count()} credentials revoked.')
    revoke_credentials.short_description = 'Revoke selected credentials'

    def view_on_site(self, obj):
        """
        Custom link to view the WebAuthn credential details on the site.
        """
        return f"/admin/authentication/webauthncredential/{obj.pk}/"


# Register User model with additional WebAuthn credential data
User = get_user_model()

class CustomUserAdmin(UserAdmin):
    """
    Custom user admin interface to display additional WebAuthn credential data
    alongside the default user details.
    """
    list_display = UserAdmin.list_display + ('web_authn_credential_count',)

    def web_authn_credential_count(self, obj):
        """
        Displays the count of passkeys associated with the user.
        """
        return WebAuthnCredential.objects.filter(user=obj).count()
    web_authn_credential_count.short_description = 'Passkeys Count'

    # Optionally, you can use inline editing of WebAuthn credentials within the User model
    inlines = []

# Register the custom UserAdmin to replace the default UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Register MFASettings model in the admin
@admin.register(MFASettings)
class MFASettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing MFA settings for users.
    """
    list_display = (
        'user', 'mfa_enabled', 'mfa_method',
        'mfa_phone_number', 'mfa_email_verified'
    )
