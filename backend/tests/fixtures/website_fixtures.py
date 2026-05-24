from __future__ import annotations

import pytest


@pytest.fixture
def website(db, tenant_site):
    """
    Create a Website model instance linked to the test Wagtail site.
    """

    from websites.models.websites import Website

    website, _ = Website.objects.get_or_create(
        domain="test.localhost",
        defaults={
            "name": "Test Tenant",
            "slug": "test",
            "is_active": True,
        },
    )

    if hasattr(website, "wagtail_site"):
        website.wagtail_site = tenant_site
        website.save(update_fields=["wagtail_site"])

    return website


@pytest.fixture
def db_with_website(website):
    """
    Ensure the test database has a default website.
    """

    return website