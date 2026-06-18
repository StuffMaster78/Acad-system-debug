"""
Pytest configuration and shared fixtures for all tests.

This module provides:
- Database fixtures
- User factories
- API client fixtures
- Common test utilities
"""
import pytest
from django.conf import settings

# The development container exports a short SECRET_KEY and keeps
# DJANGO_SETTINGS_MODULE pointed at the environment-selecting settings module.
# PyJWT correctly warns when HS256 receives fewer than 32 bytes. Configure a
# strong, deterministic key for pytest before SimpleJWT is imported so test
# tokens never inherit development credentials or emit insecure-key warnings.
TEST_JWT_SIGNING_KEY = (
    "writing-system-pytest-jwt-signing-key-"
    "replace-only-in-tests-2026"
)
settings.SECRET_KEY = TEST_JWT_SIGNING_KEY
settings.SIMPLE_JWT = {
    **settings.SIMPLE_JWT,
    "SIGNING_KEY": TEST_JWT_SIGNING_KEY,
}

from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken
from websites.models.websites import Website
from decimal import Decimal
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site

User = get_user_model()

# Django may import SimpleJWT while populating installed apps, before pytest
# imports this conftest module. Update the already-created backend as well as
# settings so both newly created and cached token backends use the test key.
token_backend.signing_key = TEST_JWT_SIGNING_KEY
token_backend.verifying_key = TEST_JWT_SIGNING_KEY



# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up test database once per session."""
    from django.db import connection

    with django_db_blocker.unblock():
        # pytest-django's django_db_setup dependency has already created and
        # migrated the test database. Running migrate again here can replay
        # operations while the reusable database is still being finalized,
        # leaving partially applied migrations and duplicate-column failures.
        # Keep only the project-specific cleanup and seed work below.

        # Fix corrupted content types before test model operations.
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

# @pytest.fixture
# def website(db):
# """Create a test website."""
# return Website.objects.get_or_create(
# domain="test.local",
# defaults={
# "name": "Test Website",
# "slug": "test",
# "is_active": True
# }
# )[0]


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


# @pytest.fixture
# def writer_user(website):
# """Create a test writer user."""
# return User.objects.create_user(
# username="test_writer",
# email="writer@test.com",
# password="testpass123",
# role="writer",
# website=website,
# is_active=True
# )


# @pytest.fixture
# def editor_user(website):
# """Create a test editor user."""
# return User.objects.create_user(
# username="test_editor",
# email="editor@test.com",
# password="testpass123",
# role="editor",
# website=website,
# is_active=True
# )


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


# @pytest.fixture
# def admin_user(website):
# """Create a test admin user."""
# return User.objects.create_user(
# username="test_admin",
# email="admin@test.com",
# password="testpass123",
# role="admin",
# website=website,
# is_active=True,
# is_staff=True
# )


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
    from orders.models.orders import Order
    from order_configs.models import PaperType
    from datetime import timedelta
    from django.utils import timezone

    paper_type, _ = PaperType.objects.get_or_create(
        website=website,
        name="Essay",
    )

    return Order.objects.create(
        client=client_user,
        website=website,
        topic="Test Order Topic",
        paper_type=paper_type,
        total_price=Decimal("100.00"),
        client_deadline=timezone.now() + timedelta(days=7),
        order_instructions="Test instructions",
        status="draft",
    )


@pytest.fixture
def client_wallet(client_user, website):
    """Create a test client wallet."""
    from wallets.services.client_wallet_service import ClientWalletService
    return ClientWalletService.get_wallet(website=website, client=client_user)


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
    from orders.models.orders import Order
    from datetime import timedelta
    from django.utils import timezone

    from order_configs.models import PaperType
    paper_type, _ = PaperType.objects.get_or_create(website=website, name="Essay")
    return Order.objects.create(
        client=other_client,
        website=website,
        topic='Other Client Order',
        paper_type=paper_type,
        total_price=Decimal('50.00'),
        client_deadline=timezone.now() + timedelta(days=5),
        order_instructions="",
        status='draft',
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


def _ensure_wagtail_locale():
    """Create the default Wagtail Locale if it doesn't exist yet."""
    from wagtail.coreutils import get_supported_content_language_variant
    from wagtail.models import Locale

    try:
        lang_code = get_supported_content_language_variant(
            __import__("django.conf", fromlist=["settings"]).settings.LANGUAGE_CODE
        )
    except LookupError:
        lang_code = "en"
    Locale.objects.get_or_create(language_code=lang_code)


@pytest.fixture
def root_page(db):
    """The Wagtail root page, created if migrations left none."""
    _ensure_wagtail_locale()
    root = Page.objects.filter(depth=1).first()
    if root is None:
        root = Page.add_root(title="Root", slug="root")
    return root


@pytest.fixture
def tenant_site(root_page):
    """A test tenant: Site + TenantHomePage + child index pages."""
    from cms_core.models import (
        AuthorIndexPage,
        ResourceIndexPage,
        TenantHomePage,
    )

    _ensure_wagtail_locale()

    home = TenantHomePage(title="Test Tenant", slug="test-tenant")
    root_page.add_child(instance=home)

    site = Site.objects.create(
        hostname="test.localhost",
        root_page=home,
        is_default_site=False,
        site_name="Test Tenant",
    )

    # Create index pages
    try:
        from cms_blog.models import BlogIndexPage
        home.add_child(instance=BlogIndexPage(title="Blog", slug="blog"))
    except ImportError:
        pass

    try:
        from cms_service_pages.models import ServiceIndexPage
        home.add_child(instance=ServiceIndexPage(title="Services", slug="services"))
    except ImportError:
        pass

    home.add_child(instance=AuthorIndexPage(title="Authors", slug="authors"))
    home.add_child(instance=ResourceIndexPage(title="Resources", slug="resources"))

    return site


@pytest.fixture
def website(tenant_site):
    """A Website model instance linked to the test tenant site.
    Adjust this if your Website model has required fields beyond domain."""
    try:
        from websites.models.websites import Website

        w, _ = Website.objects.get_or_create(
            domain="test.localhost",
            defaults={
                "name": "Test Tenant",
                "is_active": True,
            },
        )
        if hasattr(w, "wagtail_site"):
            w.wagtail_site = tenant_site
            w.save(update_fields=["wagtail_site"])
        return w
    except ImportError:
        return None


@pytest.fixture
def admin_user(db):
    """A superuser for admin tests."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@test.localhost",
        password="testpass123",
    )


@pytest.fixture
def editor_user(db, tenant_site):
    """An editor with permissions on the test tenant."""
    user = User.objects.create_user(
        username="editor",
        email="editor@test.localhost",
        password="testpass123",
    )
    try:
        from cms_core.services.permissions_service import TenantPermissionsService
        TenantPermissionsService.assign_user_to_tenant(user, tenant_site, role="editor")
    except Exception:
        pass
    return user


@pytest.fixture
def writer_user(db, tenant_site):
    """A writer with limited permissions on the test tenant."""
    user = User.objects.create_user(
        username="writer",
        email="writer@test.localhost",
        password="testpass123",
    )
    try:
        from cms_core.services.permissions_service import TenantPermissionsService
        TenantPermissionsService.assign_user_to_tenant(user, tenant_site, role="writer")
    except Exception:
        pass
    return user


@pytest.fixture
def test_author(tenant_site):
    """A test Author snippet."""
    from cms_authors.models import Author

    return Author.objects.create(
        site=tenant_site,
        name="Dr. Jane Smith",
        slug="jane-smith",
        bio="Board-certified RN with 15 years of nursing education experience.",
        credentials="MSN, RN, CCRN",
        degrees=[{"degree": "MSN", "institution": "Johns Hopkins", "year": 2015}],
        areas_of_expertise="Nursing Care Plans, Evidence-Based Practice",
        years_experience=15,
        role="senior_writer",
        is_active=True,
        show_publicly=True,
    )


@pytest.fixture
def blog_category(tenant_site):
    """A test blog category."""
    from cms_core.models import BlogCategory

    return BlogCategory.objects.create(
        site=tenant_site,
        name="Nursing Guides",
        slug="nursing-guides",
        is_active=True,
    )


@pytest.fixture
def service_category(tenant_site):
    """A test service category."""
    from cms_core.models import ServiceCategory

    return ServiceCategory.objects.create(
        site=tenant_site,
        name="Nursing Services",
        slug="nursing-services",
    )


@pytest.fixture
def blog_index(tenant_site):
    """The blog index page for the test tenant."""
    from cms_blog.models import BlogIndexPage

    return BlogIndexPage.objects.descendant_of(
        tenant_site.root_page
    ).first()


@pytest.fixture
def service_index(tenant_site):
    """The service index page for the test tenant."""
    from cms_service_pages.models import ServiceIndexPage

    return ServiceIndexPage.objects.descendant_of(
        tenant_site.root_page
    ).first()


@pytest.fixture
def test_blog_post(blog_index, test_author, blog_category):
    """A published test blog post."""
    from cms_blog.models import BlogPostPage

    post = BlogPostPage(
        title="How to Write a Nursing Care Plan",
        slug="how-to-write-nursing-care-plan",
        primary_author=test_author,
        category=blog_category,
        excerpt="A step-by-step guide to writing effective nursing care plans.",
        body=[
            ("heading", {"text": "Introduction", "level": "h2"}),
            ("paragraph", "<p>Nursing care plans are essential documents...</p>"),
            ("heading", {"text": "Step 1: Assessment", "level": "h2"}),
            ("paragraph", "<p>Begin by assessing the patient...</p>"),
            ("heading", {"text": "Step 2: Diagnosis", "level": "h2"}),
            ("paragraph", "<p>Use NANDA-I nursing diagnoses...</p>"),
        ],
    )
    blog_index.add_child(instance=post)
    post.save_revision().publish()
    return post


@pytest.fixture
def test_service_page(service_index, service_category):
    """A published test service page."""
    from cms_service_pages.models import ServicePage

    page = ServicePage(
        title="Nursing Care Plan Writing Help",
        slug="nursing-care-plan-writing",
        service_category=service_category,
        pricing_from=15.99,
        pricing_to=45.99,
        turnaround_hours_fastest=6,
        turnaround_hours_standard=168,
        primary_cta_text="Order Now",
        primary_cta_url="/order/",
        body=[
            ("hero", {
                "headline": "Expert Nursing Care Plan Writing",
                "subheadline": "Written by real RNs",
                "cta_text": "Order Now",
                "cta_url": "/order/",
            }),
            ("paragraph", "<p>Our team of certified nurses...</p>"),
        ],
    )
    service_index.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.fixture
def test_pillar(tenant_site, test_service_page, test_blog_post):
    """A test content pillar linking a service page to blog content."""
    from cms_content_graph.models import ContentPillar

    pillar = ContentPillar.objects.create(
        site=tenant_site,
        name="Nursing Care Plans",
        slug="nursing-care-plans",
        service_page=test_service_page,
        hub_post=test_blog_post,
        target_keywords=["nursing care plan", "care plan example"],
    )

    # Link the blog post to this pillar
    test_blog_post.pillar = pillar
    test_blog_post.primary_service = test_service_page
    test_blog_post.save()

    return pillar
