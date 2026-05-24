from __future__ import annotations

import pytest
from wagtail.models import Page, Site


@pytest.fixture
def root_page(db):
    """
    Return the Wagtail root page.
    """

    root_page = Page.objects.filter(depth=1).first()

    assert root_page is not None

    return root_page


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