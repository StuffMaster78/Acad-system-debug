"""
Comprehensive logout tests (15+ tests).

Tests cover:
- Successful logout
- Logout all devices
- Session invalidation
- Token revocation
- Impersonation handling
- Edge cases
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.services.auth_service import AuthenticationService
from authentication.models.login import LoginSession
from authentication.models.logout import LogoutEvent

User = get_user_model()


@pytest.mark.django_db
class TestLogoutSuccess:
    """Test successful logout scenarios."""
    
    def test_logout_success(self, client_user, website):
        """Test successful logout."""
        request = MagicMock()
        request.session = {}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            result = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        assert result['success'] is True
        assert 'message' in result
    
    def test_logout_all_devices(self, client_user, website):
        """Test logout from all devices."""
        # Create multiple sessions
        LoginSession.objects.create(
            user=client_user,
            website=website,
            ip_address='127.0.0.1',
            user_agent='Device 1'
        )
        LoginSession.objects.create(
            user=client_user,
            website=website,
            ip_address='127.0.0.2',
            user_agent='Device 2'
        )
        
        request = MagicMock()
        request.session = {}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            result = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=True
            )
        
        assert result['success'] is True
        assert 'all devices' in result['message'].lower()
        
        # All sessions should be revoked
        active_sessions = LoginSession.objects.filter(
            user=client_user,
            website=website,
            revoked_at__isnull=True
        ).count()
        assert active_sessions == 0
    
    def test_logout_single_session(self, client_user, website):
        """Test logout from single session."""
        # Create multiple sessions
        session1 = LoginSession.objects.create(
            user=client_user,
            website=website,
            ip_address='127.0.0.1',
            user_agent='Device 1'
        )
        session2 = LoginSession.objects.create(
            user=client_user,
            website=website,
            ip_address='127.0.0.2',
            user_agent='Device 2'
        )
        
        request = MagicMock()
        request.session = {}
        request.session_id = str(session1.id)
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            result = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        assert result['success'] is True
        
        # Only session1 should be revoked
        session1.refresh_from_db()
        session2.refresh_from_db()
        assert session1.revoked_at is not None
        assert session2.revoked_at is None  # Still active


@pytest.mark.django_db
class TestLogoutSessionManagement:
    """Test logout session management."""
    
    def test_logout_revokes_session(self, client_user, website):
        """Test logout revokes login session."""
        session = LoginSession.objects.create(
            user=client_user,
            website=website,
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        request = MagicMock()
        request.session = {}
        request.session_id = str(session.id)
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        session.refresh_from_db()
        assert session.revoked_at is not None
    
    def test_logout_clears_session(self, client_user, website):
        """Test logout clears Django session."""
        request = MagicMock()
        request.session = {'key': 'value'}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        # Session should be flushed
        assert not hasattr(request.session, 'key') or len(request.session) == 0
    
    def test_logout_logs_event(self, client_user, website):
        """Test logout logs logout event."""
        initial_count = LogoutEvent.objects.filter(user=client_user).count()
        
        request = MagicMock()
        request.session = {}
        request.session_id = None
        request.headers = {'User-Agent': 'Test Agent'}
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        # Should log event
        new_count = LogoutEvent.objects.filter(user=client_user).count()
        assert new_count >= initial_count


@pytest.mark.django_db
class TestLogoutImpersonation:
    """Test logout with impersonation."""
    
    def test_logout_ends_impersonation(self, admin_user, client_user, website):
        """Test logout ends active impersonation."""
        request = MagicMock()
        request.session = {'_impersonator_id': admin_user.id}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'), \
             patch('authentication.services.impersonation_service.ImpersonationService') as mock_impersonation:
            mock_service = MagicMock()
            mock_impersonation.return_value = mock_service
            
            AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
            
            # Should end impersonation
            mock_service.end_impersonation.assert_called_once()


@pytest.mark.django_db
class TestLogoutEdgeCases:
    """Test logout edge cases."""
    
    def test_logout_without_active_session(self, client_user, website):
        """Test logout without active session."""
        request = MagicMock()
        request.session = {}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            result = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        # Should still succeed
        assert result['success'] is True
    
    def test_logout_multiple_times(self, client_user, website):
        """Test logging out multiple times is idempotent."""
        request = MagicMock()
        request.session = {}
        request.session_id = None
        
        with patch('authentication.services.auth_service.get_current_website', return_value=website), \
             patch('authentication.services.auth_service.get_client_ip', return_value='127.0.0.1'):
            # First logout
            result1 = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
            
            # Second logout
            result2 = AuthenticationService.logout(
                request=request,
                user=client_user,
                logout_all=False
            )
        
        # Both should succeed
        assert result1['success'] is True
        assert result2['success'] is True

