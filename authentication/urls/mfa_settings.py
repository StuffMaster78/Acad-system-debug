# authentication/urls/mfa_settings.py

from django.urls import path
from authentication.views.mfa_settings import (
    MFASettingsView,
    MFAQRCodeView,
    MFAOTPVerifyView,
    MFAPasskeySetupView,
    MFAPasskeyVerifyView,
)

urlpatterns = [
    # View to retrieve and update MFA settings for the user
    path('mfa/settings/', MFASettingsView.as_view(), name='mfa-settings'),
    
    # View to generate and retrieve the QR code for TOTP MFA setup
    path('mfa/qr-code/', MFAQRCodeView.as_view(), name='mfa-qr-code'),
    
    # View to verify the OTP entered by the user
    path('mfa/otp/verify/', MFAOTPVerifyView.as_view(), name='mfa-otp-verify'),
    
    # View to handle passkey (WebAuthn) setup for the user
    path('mfa/passkey/setup/', MFAPasskeySetupView.as_view(), name='mfa-passkey-setup'),
    
    # View to verify the passkey challenge (WebAuthn)
    path('mfa/passkey/verify/', MFAPasskeyVerifyView.as_view(), name='mfa-passkey-verify'),
]
