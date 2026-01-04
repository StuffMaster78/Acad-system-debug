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
    import os
    from django.conf import settings
    from django.db import connection
    
    with django_db_blocker.unblock():
        # Ensure migrations are run first
        from django.core.management import call_command
        
        # Run migrations on test database
        try:
            call_command('migrate', verbosity=0, interactive=False, run_syncdb=False)
        except Exception as e:
            # If migrations fail, try to continue anyway
            print(f"Migration warning: {e}")
        
        # Fix corrupted content types IMMEDIATELY after migrations
        # This must happen before any model operations
        try:
            # Delete corrupted content types using raw SQL
            with connection.cursor() as cursor:
                # Delete content types with null names (corrupted during migrations)
                cursor.execute("""
                    DELETE FROM django_content_type 
                    WHERE name IS NULL 
                    OR name = ''
                    OR (app_label = 'migrations' AND model = 'migration')
                """)
        except Exception as e:
            # Table might not exist yet, continue
            if 'does not exist' not in str(e).lower() and 'relation' not in str(e).lower():
                print(f"Content type cleanup: {e}")
        
        # Now ensure proper content types exist for all apps
        try:
            from django.contrib.contenttypes.management import create_contenttypes
            from django.apps import apps
            
            for app_config in apps.get_app_configs():
                try:
                    # Skip migrations app (it has no real models and causes corruption)
                    if app_config.label == 'migrations':
                        continue
                    # Skip apps without models
                    if not app_config.models_module:
                        continue
                    # Create content types for this app
                    create_contenttypes(app_config, verbosity=0, interactive=False)
                except Exception:
                    # Some apps might not need content types, continue
                    pass
        except Exception as e:
            # Content types might already exist, continue
            print(f"Content types setup: {e}")
        
        # Create default website if it doesn't exist
        try:
            Website.objects.get_or_create(
                domain="test.local",
                defaults={
                    "name": "Test Website",
                    "slug": "test",
                    "is_active": True
                }
            )
        except Exception:
            # If website creation fails, continue - it might already exist
            pass


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
    return Website.objects.get_or_create(
        domain="test.local",
        defaults={
            "name": "Test Website",
            "slug": "test",
            "is_active": True
        }
    )[0]


@pytest.fixture
def mock_request_session():
    """Create a mock session object with all required methods."""
    from unittest.mock import MagicMock
    
    session = MagicMock()
    session.session_key = 'test-session-key-12345'
    session._session = {}
    
    # Make session dict-like for get/set operations
    def session_get(key, default=None):
        return session._session.get(key, default)
    
    def session_set(key, value):
        session._session[key] = value
    
    def session_pop(key, default=None):
        return session._session.pop(key, default)
    
    session.get = session_get
    session.__getitem__ = lambda self, key: session._session[key]
    session.__setitem__ = lambda self, key, value: session_set(key, value)
    session.__contains__ = lambda self, key: key in session._session
    session.pop = session_pop
    session.flush = MagicMock()
    session.save = MagicMock()
    session.set_expiry = MagicMock()
    session.modified = False
    
    return session


@pytest.fixture
def mock_request(mock_request_session):
    """Create a mock request object with proper session."""
    from unittest.mock import MagicMock
    
    request = MagicMock()
    request.data = {}
    request.headers = {'User-Agent': 'Test Agent'}
    request.session = mock_request_session
    request.get_host = MagicMock(return_value='test.local')
    request.META = {'REMOTE_ADDR': '127.0.0.1'}
    
    return request


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


# ============================================================================
# Additional Fixtures for Payment and Order Tests
# ============================================================================

@pytest.fixture
def order(client_user, website):
    """Create a test order."""
    from orders.models import Order
    from datetime import timedelta
    from django.utils import timezone
    
    return Order.objects.create(
        client=client_user,
        website=website,
        topic='Test Order Topic',
        number_of_pages=5,
        total_price=Decimal('100.00'),
        client_deadline=timezone.now() + timedelta(days=7),
        order_instructions='Test instructions',
        status='draft'
    )


@pytest.fixture
def client_wallet(client_user, website):
    """Create a test client wallet."""
    from client_wallet.models import ClientWallet
    
    wallet, _ = ClientWallet.objects.get_or_create(
        client=client_user,
        website=website,
        defaults={
            'balance': Decimal('0.00')
        }
    )
    return wallet


@pytest.fixture
def discount(website):
    """Create a test discount."""
    from discounts.models import Discount
    
    return Discount.objects.create(
        website=website,
        code='TEST10',
        discount_type='percentage',
        value=Decimal('10.00'),
        is_active=True
    )


@pytest.fixture
def writer_profile(writer_user, website):
    """Create a test writer profile."""
    from writer_management.models import WriterProfile
    
    profile, _ = WriterProfile.objects.get_or_create(
        user=writer_user,
        website=website,
        defaults={
            'is_available_for_auto_assignments': True,
            'verification_status': 'verified'
        }
    )
    return profile


@pytest.fixture
def authenticated_writer(api_client, writer_user):
    """Create authenticated writer client."""
    refresh = RefreshToken.for_user(writer_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_admin(api_client, admin_user):
    """Create authenticated admin client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def other_writer(website):
    """Create another writer user for testing."""
    return User.objects.create_user(
        username="other_writer",
        email="otherwriter@test.com",
        password="testpass123",
        role="writer",
        website=website,
        is_active=True
    )


@pytest.fixture
def other_client_order(other_client, website):
    """Create an order for another client."""
    from orders.models import Order
    from datetime import timedelta
    from django.utils import timezone
    
    return Order.objects.create(
        client=other_client,
        website=website,
        topic='Other Client Order',
        number_of_pages=3,
        total_price=Decimal('50.00'),
        client_deadline=timezone.now() + timedelta(days=5),
        status='draft'
    )


@pytest.fixture
def other_client(website):
    """Create another client user for testing."""
    return User.objects.create_user(
        username="other_client",
        email="otherclient@test.com",
        password="testpass123",
        role="client",
        website=website,
        is_active=True
    )

