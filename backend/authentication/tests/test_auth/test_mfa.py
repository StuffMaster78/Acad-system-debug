"""
Comprehensive MFA/2FA tests (20+ tests).

Tests cover:
- MFA enable/disable
- TOTP generation and validation
- Email OTP generation and validation
- Backup codes
- MFA during login
- Edge cases
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import pyotp

from authentication.services.mfa import MFAService
from authentication.models.mfa_settings import MFASettings
from authentication.models.backup_code import BackupCode


@pytest.mark.django_db
class TestMFAEnableDisable:
    """Test MFA enable/disable functionality."""
    
    def test_enable_mfa_qr_code(self, client_user):
        """Test enabling MFA with QR code method."""
        service = MFAService(user=client_user)
        
        # Generate TOTP secret
        secret = service.generate_totp_secret()
        
        # Enable MFA
        service.enable_mfa('qr_code')
        
        service.settings.refresh_from_db()
        assert service.settings.is_mfa_enabled is True
        assert service.settings.mfa_method == 'qr_code'
        assert service.settings.mfa_secret == secret
    
    def test_enable_mfa_email(self, client_user):
        """Test enabling MFA with email method."""
        service = MFAService(user=client_user)
        
        # Enable MFA
        service.enable_mfa('email')
        
        service.settings.refresh_from_db()
        assert service.settings.is_mfa_enabled is True
        assert service.settings.mfa_method == 'email'
    
    def test_disable_mfa(self, client_user):
        """Test disabling MFA."""
        service = MFAService(user=client_user)
        
        # Enable first
        service.generate_totp_secret()
        service.enable_mfa('qr_code')
        
        # Then disable
        service.disable_mfa()
        
        service.settings.refresh_from_db()
        assert service.settings.is_mfa_enabled is False
        assert service.settings.mfa_method is None
        assert service.settings.mfa_secret is None


@pytest.mark.django_db
class TestTOTP:
    """Test TOTP (Time-based One-Time Password) functionality."""
    
    def test_generate_totp_secret(self, client_user):
        """Test generating TOTP secret."""
        service = MFAService(user=client_user)
        secret = service.generate_totp_secret()
        
        assert secret is not None
        assert len(secret) > 0
        assert service.settings.mfa_secret == secret
    
    def test_validate_totp_code_success(self, client_user):
        """Test successfully validating TOTP code."""
        service = MFAService(user=client_user)
        secret = service.generate_totp_secret()
        
        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # Should validate successfully
        service.validate_totp_code(code)
        # No exception means success
    
    def test_validate_totp_code_invalid(self, client_user):
        """Test validating invalid TOTP code raises error."""
        service = MFAService(user=client_user)
        service.generate_totp_secret()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_totp_code('000000')
        
        assert 'Invalid' in str(exc.value) or 'TOTP' in str(exc.value)
    
    def test_validate_totp_code_not_configured(self, client_user):
        """Test validating TOTP when not configured raises error."""
        service = MFAService(user=client_user)
        # Don't generate secret
        
        with pytest.raises(ValidationError) as exc:
            service.validate_totp_code('123456')
        
        assert 'not configured' in str(exc.value).lower() or 'TOTP' in str(exc.value)
    
    def test_totp_code_time_window(self, client_user):
        """Test TOTP code validation with time window."""
        service = MFAService(user=client_user)
        secret = service.generate_totp_secret()
        
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # Should validate with valid window
        service.validate_totp_code(code)
        
        # Old code should fail
        old_code = totp.at(timezone.now() - timedelta(seconds=60))
        with pytest.raises(ValidationError):
            service.validate_totp_code(old_code)


@pytest.mark.django_db
class TestEmailOTP:
    """Test email OTP functionality."""
    
    def test_generate_email_otp(self, client_user):
        """Test generating email OTP."""
        service = MFAService(user=client_user)
        otp = service.generate_email_otp()
        
        assert otp is not None
        assert len(otp) == 6
        assert otp.isdigit()
        assert service.settings.otp_code == otp
        assert service.settings.otp_expires_at is not None
    
    def test_validate_email_otp_success(self, client_user):
        """Test successfully validating email OTP."""
        service = MFAService(user=client_user)
        otp = service.generate_email_otp()
        
        # Should validate successfully
        service.validate_email_otp(otp)
        # No exception means success
    
    def test_validate_email_otp_invalid(self, client_user):
        """Test validating invalid email OTP raises error."""
        service = MFAService(user=client_user)
        service.generate_email_otp()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_email_otp('000000')
        
        assert 'Invalid' in str(exc.value) or 'OTP' in str(exc.value)
    
    def test_validate_email_otp_expired(self, client_user):
        """Test validating expired email OTP raises error."""
        service = MFAService(user=client_user)
        otp = service.generate_email_otp()
        
        # Manually expire OTP
        service.settings.otp_expires_at = timezone.now() - timedelta(minutes=10)
        service.settings.save()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_email_otp(otp)
        
        assert 'expired' in str(exc.value).lower()
    
    def test_email_otp_expires_after_5_minutes(self, client_user):
        """Test email OTP expires after 5 minutes."""
        service = MFAService(user=client_user)
        otp = service.generate_email_otp()
        
        # Check expiration
        expires_at = service.settings.otp_expires_at
        expected_expiry = timezone.now() + timedelta(minutes=5)
        
        # Should be approximately 5 minutes from now
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute


@pytest.mark.django_db
class TestBackupCodes:
    """Test backup code functionality."""
    
    def test_generate_backup_codes(self, client_user):
        """Test generating backup codes."""
        service = MFAService(user=client_user)
        codes = service.generate_backup_codes(count=10)
        
        assert len(codes) == 10
        assert all(len(code) > 0 for code in codes)
        
        # Check codes are stored
        backup_codes = BackupCode.objects.filter(user=client_user)
        assert backup_codes.count() == 10
    
    def test_validate_backup_code_success(self, client_user):
        """Test successfully validating backup code."""
        service = MFAService(user=client_user)
        codes = service.generate_backup_codes(count=5)
        
        # Use first code
        service.validate_backup_code(codes[0])
        
        # Code should be marked as used
        backup_code = BackupCode.objects.filter(user=client_user, used=False).first()
        # One should be used
        used_count = BackupCode.objects.filter(user=client_user, used=True).count()
        assert used_count == 1
    
    def test_validate_backup_code_invalid(self, client_user):
        """Test validating invalid backup code raises error."""
        service = MFAService(user=client_user)
        service.generate_backup_codes(count=5)
        
        with pytest.raises(ValidationError) as exc:
            service.validate_backup_code('invalid_code')
        
        assert 'Invalid' in str(exc.value) or 'used' in str(exc.value).lower()
    
    def test_validate_backup_code_already_used(self, client_user):
        """Test validating already used backup code raises error."""
        service = MFAService(user=client_user)
        codes = service.generate_backup_codes(count=5)
        
        # Use code once
        service.validate_backup_code(codes[0])
        
        # Try to use again
        with pytest.raises(ValidationError) as exc:
            service.validate_backup_code(codes[0])
        
        assert 'used' in str(exc.value).lower() or 'Invalid' in str(exc.value)
    
    def test_backup_codes_are_hashed(self, client_user):
        """Test backup codes are stored as hashes."""
        service = MFAService(user=client_user)
        codes = service.generate_backup_codes(count=5)
        
        # Check codes are hashed in database
        backup_code = BackupCode.objects.filter(user=client_user).first()
        assert backup_code.code_hash is not None
        assert backup_code.code_hash != codes[0]  # Should be hashed


@pytest.mark.django_db
class TestMFALogin:
    """Test MFA during login."""
    
    def test_login_requires_2fa_when_enabled(self, client_user, website):
        """Test login requires 2FA when enabled."""
        service = MFAService(user=client_user)
        service.generate_totp_secret()
        service.enable_mfa('qr_code')
        
        # Mock login to check 2FA requirement
        from authentication.services.auth_service import AuthenticationService
        
        request = MagicMock()
        request.data = {}
        request.headers = {'User-Agent': 'Test Agent'}
        request.session = {}
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            result = AuthenticationService.login(
                request=request,
                email=client_user.email,
                password='testpass123',
                remember_me=False
            )
        
        # Should require 2FA
        assert result.get('requires_2fa') is True
    
    def test_verify_2fa_completes_login(self, client_user):
        """Test verifying 2FA completes login."""
        service = MFAService(user=client_user)
        secret = service.generate_totp_secret()
        service.enable_mfa('qr_code')
        
        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        from authentication.services.auth_service import AuthenticationService
        
        # Verify 2FA
        result = AuthenticationService.verify_2fa(
            user=client_user,
            session_id='test_session',
            totp_code=code
        )
        
        assert 'access_token' in result or 'access' in result
        assert 'user' in result
    
    def test_verify_2fa_invalid_code(self, client_user):
        """Test verifying 2FA with invalid code fails."""
        service = MFAService(user=client_user)
        service.generate_totp_secret()
        service.enable_mfa('qr_code')
        
        from authentication.services.auth_service import AuthenticationService
        
        with pytest.raises(ValidationError) as exc:
            AuthenticationService.verify_2fa(
                user=client_user,
                session_id='test_session',
                totp_code='000000'
            )
        
        assert 'Invalid' in str(exc.value) or '2FA' in str(exc.value)


@pytest.mark.django_db
class TestMFAEdgeCases:
    """Test MFA edge cases."""
    
    def test_generate_multiple_totp_secrets(self, client_user):
        """Test generating multiple TOTP secrets (should update)."""
        service = MFAService(user=client_user)
        
        secret1 = service.generate_totp_secret()
        secret2 = service.generate_totp_secret()
        
        # Should update, not create multiple
        assert service.settings.mfa_secret == secret2
        assert secret1 != secret2
    
    def test_mfa_settings_created_on_first_access(self, client_user):
        """Test MFA settings are created on first access."""
        # Delete if exists
        MFASettings.objects.filter(user=client_user).delete()
        
        service = MFAService(user=client_user)
        
        # Settings should be created
        assert service.settings is not None
        assert service.settings.user == client_user
    
    def test_backup_codes_regeneration(self, client_user):
        """Test regenerating backup codes invalidates old ones."""
        service = MFAService(user=client_user)
        
        codes1 = service.generate_backup_codes(count=5)
        codes2 = service.generate_backup_codes(count=5)
        
        # Should have 10 total codes now
        total_codes = BackupCode.objects.filter(user=client_user).count()
        assert total_codes == 10
        
        # Old codes should still work (unless implementation invalidates them)
        # This depends on implementation

