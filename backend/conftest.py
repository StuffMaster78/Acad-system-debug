"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database fixtures
- User factories
- API client fixtures
- Common test utilities
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from websites.models import Website
from decimal import Decimal

User = get_user_model()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database once per session."""
    with django_db_blocker.unblock():
        # Create default website if it doesn't exist
        Website.objects.get_or_create(
            domain="test.local",
            defaults={
                "name": "Test Website",
                "slug": "test",
                "is_active": True
            }
        )


@pytest.fixture
def db_with_website(db):
    """Ensure test database has a default website."""
    website, _ = Website.objects.get_or_create(
        domain="test.local",
        defaults={
            "name": "Test Website",
            "slug": "test",
            "is_active": True
        }
    )
    return website


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def website(db):
    """Create a test website."""
    return Website.objects.create(
        domain="test.local",
        name="Test Website",
        slug="test",
        is_active=True
    )


@pytest.fixture
def client_user(website):
    """Create a test client user."""
    return User.objects.create_user(
        username="test_client",
        email="client@test.com",
        password="testpass123",
        role="client",
        website=website,
        is_active=True
    )


@pytest.fixture
def writer_user(website):
    """Create a test writer user."""
    return User.objects.create_user(
        username="test_writer",
        email="writer@test.com",
        password="testpass123",
        role="writer",
        website=website,
        is_active=True
    )


@pytest.fixture
def editor_user(website):
    """Create a test editor user."""
    return User.objects.create_user(
        username="test_editor",
        email="editor@test.com",
        password="testpass123",
        role="editor",
        website=website,
        is_active=True
    )


@pytest.fixture
def support_user(website):
    """Create a test support user."""
    return User.objects.create_user(
        username="test_support",
        email="support@test.com",
        password="testpass123",
        role="support",
        website=website,
        is_active=True
    )


@pytest.fixture
def admin_user(website):
    """Create a test admin user."""
    return User.objects.create_user(
        username="test_admin",
        email="admin@test.com",
        password="testpass123",
        role="admin",
        website=website,
        is_active=True,
        is_staff=True
    )


@pytest.fixture
def superadmin_user(website):
    """Create a test superadmin user."""
    return User.objects.create_superuser(
        username="test_superadmin",
        email="superadmin@test.com",
        password="testpass123",
        role="superadmin",
        website=website
    )


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """Create an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, client_user):
    """Create an authenticated API client for a client user."""
    refresh = RefreshToken.for_user(client_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_writer_client(api_client, writer_user):
    """Create an authenticated API client for a writer user."""
    refresh = RefreshToken.for_user(writer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_editor_client(api_client, editor_user):
    """Create an authenticated API client for an editor user."""
    refresh = RefreshToken.for_user(editor_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_support_client(api_client, support_user):
    """Create an authenticated API client for a support user."""
    refresh = RefreshToken.for_user(support_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Create an authenticated API client for an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_superadmin_client(api_client, superadmin_user):
    """Create an authenticated API client for a superadmin user."""
    refresh = RefreshToken.for_user(superadmin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


# ============================================================================
# Django Client Fixtures
# ============================================================================

@pytest.fixture
def django_client():
    """Create a Django test client."""
    return Client()


@pytest.fixture
def authenticated_django_client(django_client, client_user):
    """Create an authenticated Django test client."""
    django_client.force_login(client_user)
    return django_client


# ============================================================================
# JWT Token Fixtures
# ============================================================================

@pytest.fixture
def client_token(client_user):
    """Generate JWT token for client user."""
    refresh = RefreshToken.for_user(client_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def writer_token(writer_user):
    """Generate JWT token for writer user."""
    refresh = RefreshToken.for_user(writer_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user."""
    refresh = RefreshToken.for_user(admin_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def sample_order_data(website, client_user):
    """Sample order data for testing."""
    from datetime import datetime, timedelta
    return {
        "title": "Test Order",
        "description": "This is a test order",
        "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
        "pages": 5,
        "academic_level": "undergraduate",
        "paper_type": "essay",
        "website": website.id,
        "client": client_user.id,
        "price": Decimal("100.00")
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass

