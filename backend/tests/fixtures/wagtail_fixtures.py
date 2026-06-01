from __future__ import annotations

import pytest
from wagtail.models import Page, Site


def _ensure_wagtail_locale():
    from wagtail.coreutils import get_supported_content_language_variant
    from wagtail.models import Locale
    from django.conf import settings as _settings

    try:
        lang_code = get_supported_content_language_variant(_settings.LANGUAGE_CODE)
    except LookupError:
        lang_code = "en"
    Locale.objects.get_or_create(language_code=lang_code)


@pytest.fixture
def root_page(db):
    """Return the Wagtail root page, created if migrations left none."""
    _ensure_wagtail_locale()
    root = Page.objects.filter(depth=1).first()
    if root is None:
        root = Page.add_root(title="Root", slug="root")
    return root


@pytest.fixture
def tenant_site(root_page):
    """
    Create a test Wagtail tenant site with root pages.
    """
    from cms_core.models import (
        AuthorIndexPage,
        ResourceIndexPage,
        TenantHomePage,
    )

    _ensure_wagtail_locale()

    existing = Site.objects.filter(hostname="test.localhost").first()
    if existing:
        return existing

    home = TenantHomePage(
        title="Test Tenant",
        slug="test-tenant",
    )
    root_page.add_child(instance=home)

    site = Site.objects.create(
        hostname="test.localhost",
        root_page=home,
        is_default_site=False,
        site_name="Test Tenant",
    )

    try:
        from cms_blog.models import BlogIndexPage

        home.add_child(
            instance=BlogIndexPage(
                title="Blog",
                slug="blog",
            )
        )
    except ImportError:
        pass

    try:
        from cms_service_pages.models import ServiceIndexPage

        home.add_child(
            instance=ServiceIndexPage(
                title="Services",
                slug="services",
            )
        )
    except ImportError:
        pass

    home.add_child(
        instance=AuthorIndexPage(
            title="Authors",
            slug="authors",
        )
    )
    home.add_child(
        instance=ResourceIndexPage(
            title="Resources",
            slug="resources",
        )
    )

    return site