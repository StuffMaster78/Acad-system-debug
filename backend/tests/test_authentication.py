"""
Comprehensive tests for authentication endpoints.
"""
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from tests.factories import ClientUserFactory, WebsiteFactory

User = get_user_model()


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationAPI:
    """Tests for authentication endpoints."""
    
    def test_user_registration_success(self, api_client, website):
        """Test successful user registration."""
        url = '/api/v1/auth/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'client',
            'website': website.id,
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']
        assert response.data['user']['username'] == data['username']
    
    def test_user_registration_duplicate_email(self, api_client, website, client_user):
        """Test registration with duplicate email fails."""
        url = '/api/v1/auth/auth/register/'
        data = {
            'username': 'anotheruser',
            'email': client_user.email,  # Duplicate email
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'client',
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_weak_password(self, api_client, website):
        """Test registration with weak password fails."""
        url = '/api/v1/auth/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': '123',  # Too weak
            'password_confirm': '123',
            'role': 'client',
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_login_success(self, api_client, client_user):
        """Test successful user login."""
        url = '/api/v1/auth/auth/login/'
        data = {
            'email': client_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data or 'access_token' in response.data
        assert 'refresh' in response.data or 'refresh_token' in response.data
        assert 'user' in response.data
    
    def test_user_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials fails."""
        url = '/api/v1/auth/auth/login/'
        data = {
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_user_login_inactive_account(self, api_client, website):
        """Test login with inactive account fails."""
        user = ClientUserFactory(website=website, is_active=False)
        
        url = '/api/v1/auth/auth/login/'
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_token_refresh(self, api_client, client_user):
        """Test token refresh endpoint."""
        refresh = RefreshToken.for_user(client_user)
        
        url = '/api/v1/auth/auth/refresh-token/'
        data = {
            'refresh': str(refresh)
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data or 'access_token' in response.data
    
    def test_logout_requires_authentication(self, api_client):
        """Test logout requires authentication."""
        url = '/api/v1/auth/auth/logout/'
        response = api_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        url = '/api/v1/auth/auth/logout/'
        response = authenticated_client.post(url, format='json')
        
        # Logout might return 200 or 204
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT
        ]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.auth
class TestUserProfile:
    """Tests for user profile endpoints."""
    
    def test_get_profile_requires_authentication(self, api_client):
        """Test getting profile requires authentication."""
        url = '/api/v1/users/profile/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_own_profile(self, authenticated_client, client_user):
        """Test user can get their own profile."""
        url = '/api/v1/users/profile/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == client_user.id
        assert response.data['email'] == client_user.email
    
    def test_update_own_profile(self, authenticated_client, client_user):
        """Test user can update their own profile."""
        url = '/api/v1/users/profile/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = authenticated_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == data['first_name']
        assert response.data['last_name'] == data['last_name']

