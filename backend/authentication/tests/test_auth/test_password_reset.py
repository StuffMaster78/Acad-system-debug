"""
Comprehensive password reset tests (20+ tests).

Tests cover:
- Password reset request
- Token validation
- OTP validation
- Password reset completion
- Token expiration
- Security features
- Edge cases
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from authentication.services.password_reset_service import PasswordResetService
from authentication.models.password_reset import PasswordResetRequest


@pytest.mark.django_db
class TestPasswordResetRequest:
    """Test password reset request scenarios."""
    
    def test_generate_reset_token_success(self, client_user, website):
        """Test successfully generating reset token."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        assert reset_request.user == client_user
        assert reset_request.website == website
        assert reset_request.token is not None
        assert reset_request.otp_code is not None
        assert len(reset_request.otp_code) == 6
        assert reset_request.is_used is False
    
    def test_generate_reset_token_creates_unique_tokens(self, client_user, website):
        """Test multiple reset requests create unique tokens."""
        service = PasswordResetService(user=client_user, website=website)
        
        request1 = service.generate_reset_token()
        request2 = service.generate_reset_token()
        
        assert request1.token != request2.token
        assert request1.otp_code != request2.otp_code
    
    def test_generate_reset_token_creates_otp(self, client_user, website):
        """Test reset token includes OTP code."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        assert reset_request.otp_code is not None
        assert reset_request.otp_code.isdigit()
        assert len(reset_request.otp_code) == 6


@pytest.mark.django_db
class TestPasswordResetValidation:
    """Test password reset token/OTP validation."""
    
    def test_validate_token_success(self, client_user, website):
        """Test successfully validating reset token."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        validated = service.validate_token(reset_request.token)
        
        assert validated.id == reset_request.id
        assert validated.user == client_user
    
    def test_validate_token_invalid(self, client_user, website):
        """Test validating invalid token raises error."""
        service = PasswordResetService(user=client_user, website=website)
        
        with pytest.raises(ValidationError) as exc:
            service.validate_token('invalid_token')
        
        assert 'Invalid' in str(exc.value) or 'used' in str(exc.value).lower()
    
    def test_validate_token_expired(self, client_user, website):
        """Test validating expired token raises error."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Manually expire the token
        reset_request.created_at = timezone.now() - timedelta(hours=2)
        reset_request.save()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_token(reset_request.token)
        
        assert 'expired' in str(exc.value).lower()
    
    def test_validate_token_already_used(self, client_user, website):
        """Test validating used token raises error."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Mark as used
        reset_request.is_used = True
        reset_request.save()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_token(reset_request.token)
        
        assert 'used' in str(exc.value).lower() or 'Invalid' in str(exc.value)
    
    def test_validate_otp_success(self, client_user, website):
        """Test successfully validating OTP."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        validated = service.validate_otp(reset_request.otp_code)
        
        assert validated.id == reset_request.id
        assert validated.user == client_user
    
    def test_validate_otp_invalid(self, client_user, website):
        """Test validating invalid OTP raises error."""
        service = PasswordResetService(user=client_user, website=website)
        
        with pytest.raises(ValidationError) as exc:
            service.validate_otp('000000')
        
        assert 'Invalid' in str(exc.value) or 'used' in str(exc.value).lower()
    
    def test_validate_otp_expired(self, client_user, website):
        """Test validating expired OTP raises error."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Manually expire the OTP
        reset_request.created_at = timezone.now() - timedelta(hours=2)
        reset_request.save()
        
        with pytest.raises(ValidationError) as exc:
            service.validate_otp(reset_request.otp_code)
        
        assert 'expired' in str(exc.value).lower()
    
    def test_validate_otp_wrong_user(self, client_user, client_user2, website):
        """Test OTP validation fails for wrong user."""
        service1 = PasswordResetService(user=client_user, website=website)
        reset_request = service1.generate_reset_token()
        
        service2 = PasswordResetService(user=client_user2, website=website)
        
        with pytest.raises(ValidationError):
            service2.validate_otp(reset_request.otp_code)


@pytest.mark.django_db
class TestPasswordResetCompletion:
    """Test password reset completion."""
    
    def test_mark_token_used(self, client_user, website):
        """Test marking token as used."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        service.mark_token_used(reset_request.token)
        
        reset_request.refresh_from_db()
        assert reset_request.is_used is True
    
    def test_mark_otp_used(self, client_user, website):
        """Test marking OTP as used."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        service.mark_otp_used(reset_request.otp_code)
        
        reset_request.refresh_from_db()
        assert reset_request.is_used is True
    
    def test_reset_password_with_token(self, client_user, website):
        """Test resetting password using token."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Validate token
        validated = service.validate_token(reset_request.token)
        
        # Reset password
        new_password = 'NewSecurePass123!'
        client_user.set_password(new_password)
        client_user.save()
        
        # Mark token as used
        service.mark_token_used(reset_request.token)
        
        # Verify password changed
        assert client_user.check_password(new_password)
        reset_request.refresh_from_db()
        assert reset_request.is_used is True
    
    def test_reset_password_with_otp(self, client_user, website):
        """Test resetting password using OTP."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Validate OTP
        validated = service.validate_otp(reset_request.otp_code)
        
        # Reset password
        new_password = 'NewSecurePass123!'
        client_user.set_password(new_password)
        client_user.save()
        
        # Mark OTP as used
        service.mark_otp_used(reset_request.otp_code)
        
        # Verify password changed
        assert client_user.check_password(new_password)
        reset_request.refresh_from_db()
        assert reset_request.is_used is True


@pytest.mark.django_db
class TestPasswordResetSecurity:
    """Test password reset security features."""
    
    def test_reset_token_expires_after_one_hour(self, client_user, website):
        """Test reset token expires after 1 hour."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Check expiration logic
        assert reset_request.is_expired() is False
        
        # Manually expire
        reset_request.created_at = timezone.now() - timedelta(hours=2)
        reset_request.save()
        
        assert reset_request.is_expired() is True
    
    def test_reset_token_single_use(self, client_user, website):
        """Test reset token can only be used once."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Use token once
        service.mark_token_used(reset_request.token)
        
        # Try to use again
        with pytest.raises(ValidationError):
            service.validate_token(reset_request.token)
    
    def test_reset_otp_single_use(self, client_user, website):
        """Test reset OTP can only be used once."""
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Use OTP once
        service.mark_otp_used(reset_request.otp_code)
        
        # Try to use again
        with pytest.raises(ValidationError):
            service.validate_otp(reset_request.otp_code)
    
    def test_reset_token_website_scoped(self, client_user, website, website2):
        """Test reset token is website-scoped."""
        service1 = PasswordResetService(user=client_user, website=website)
        reset_request = service1.generate_reset_token()
        
        service2 = PasswordResetService(user=client_user, website=website2)
        
        # Token from different website should not validate
        with pytest.raises(ValidationError):
            service2.validate_token(reset_request.token)


@pytest.mark.django_db
class TestPasswordResetEdgeCases:
    """Test password reset edge cases."""
    
    def test_multiple_reset_requests(self, client_user, website):
        """Test multiple reset requests for same user."""
        service = PasswordResetService(user=client_user, website=website)
        
        request1 = service.generate_reset_token()
        request2 = service.generate_reset_token()
        
        # Both should be valid
        assert request1.token != request2.token
        assert service.validate_token(request1.token).id == request1.id
        assert service.validate_token(request2.token).id == request2.id
    
    def test_reset_with_old_password(self, client_user, website):
        """Test resetting to old password (should be allowed or prevented)."""
        old_password = 'OldPass123!'
        client_user.set_password(old_password)
        client_user.save()
        
        service = PasswordResetService(user=client_user, website=website)
        reset_request = service.generate_reset_token()
        
        # Reset to same password
        # This might be prevented by password history service
        # For now, just test the flow
        validated = service.validate_token(reset_request.token)
        assert validated is not None

