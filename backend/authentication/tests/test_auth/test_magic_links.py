"""
Comprehensive magic link tests (10+ tests).

Tests cover:
- Magic link generation
- Magic link validation
- Magic link expiration
- Magic link single-use
- Edge cases
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from authentication.services.magic_link_service import MagicLinkService
from authentication.models.magic_links import MagicLink


@pytest.mark.django_db
class TestMagicLinkGeneration:
    """Test magic link generation."""
    
    def test_send_magic_link_success(self, client_user, website):
        """Test successfully sending magic link."""
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'), \
             patch.object(MagicLinkService, '_send_magic_link_email'):
            result = MagicLinkService.send_magic_link(
                email=client_user.email,
                website=website,
                request=request
            )
        
        assert result['email_sent'] is True
        assert 'expires_in' in result
        assert 'expires_at' in result
    
    def test_send_magic_link_creates_token(self, client_user, website):
        """Test magic link creates token."""
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'), \
             patch.object(MagicLinkService, '_send_magic_link_email'):
            result = MagicLinkService.send_magic_link(
                email=client_user.email,
                website=website,
                request=request
            )
        
        # Token should be created
        magic_link = MagicLink.objects.filter(user=client_user, website=website).latest('created_at')
        assert magic_link.token is not None
    
    def test_send_magic_link_invalid_email(self, website):
        """Test sending magic link to invalid email."""
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'):
            with pytest.raises(ValidationError) as exc:
                MagicLinkService.send_magic_link(
                    email='nonexistent@test.com',
                    website=website,
                    request=request
                )
            
            assert 'not found' in str(exc.value).lower()


@pytest.mark.django_db
class TestMagicLinkValidation:
    """Test magic link validation."""
    
    def test_verify_magic_link_success(self, client_user, website):
        """Test successfully verifying magic link."""
        # Create magic link
        import uuid
        token = uuid.uuid4()
        magic_link = MagicLink.objects.create(
            user=client_user,
            website=website,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15),
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'):
            result = MagicLinkService.verify_magic_link(str(token), request)
        
        assert 'access' in result or 'access_token' in result
        assert 'user' in result
    
    def test_verify_magic_link_invalid_token(self, website):
        """Test verifying invalid magic link."""
        import uuid
        invalid_token = str(uuid.uuid4())
        
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'):
            with pytest.raises(ValidationError) as exc:
                MagicLinkService.verify_magic_link(invalid_token, request)
            
            assert 'Invalid' in str(exc.value) or 'expired' in str(exc.value).lower()
    
    def test_verify_magic_link_expired(self, client_user, website):
        """Test verifying expired magic link."""
        import uuid
        token = uuid.uuid4()
        magic_link = MagicLink.objects.create(
            user=client_user,
            website=website,
            token=token,
            expires_at=timezone.now() - timedelta(minutes=1),  # Expired
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'):
            with pytest.raises(ValidationError) as exc:
                MagicLinkService.verify_magic_link(str(token), request)
            
            assert 'expired' in str(exc.value).lower() or 'Invalid' in str(exc.value)
    
    def test_verify_magic_link_single_use(self, client_user, website):
        """Test magic link can only be used once."""
        import uuid
        token = uuid.uuid4()
        magic_link = MagicLink.objects.create(
            user=client_user,
            website=website,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15),
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'):
            # First use
            result1 = MagicLinkService.verify_magic_link(str(token), request)
            assert 'access' in result1 or 'access_token' in result1
            
            # Second use should fail
            with pytest.raises(ValidationError):
                MagicLinkService.verify_magic_link(str(token), request)


@pytest.mark.django_db
class TestMagicLinkEdgeCases:
    """Test magic link edge cases."""
    
    def test_magic_link_expires_after_15_minutes(self, client_user, website):
        """Test magic link expires after 15 minutes."""
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'), \
             patch.object(MagicLinkService, '_send_magic_link_email'):
            result = MagicLinkService.send_magic_link(
                email=client_user.email,
                website=website,
                request=request,
                expiry_minutes=15
            )
        
        # Check expiry
        expires_at = timezone.datetime.fromisoformat(result['expires_at'].replace('Z', '+00:00'))
        expected_expiry = timezone.now() + timedelta(minutes=15)
        
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute
    
    def test_magic_link_custom_expiry(self, client_user, website):
        """Test magic link with custom expiry time."""
        request = MagicMock()
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.magic_link_service.get_client_ip', return_value='127.0.0.1'), \
             patch.object(MagicLinkService, '_send_magic_link_email'):
            result = MagicLinkService.send_magic_link(
                email=client_user.email,
                website=website,
                request=request,
                expiry_minutes=30
            )
        
        assert result['expires_in'] == 30 * 60  # 30 minutes in seconds

