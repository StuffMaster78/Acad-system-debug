from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def client_user(website):
    return User.objects.create_user(
        username="test_client",
        email="client@test.com",
        password="testpass123",
        role="client",
        website=website,
        is_active=True,
    )


@pytest.fixture
def other_client(website):
    return User.objects.create_user(
        username="other_client",
        email="otherclient@test.com",
        password="testpass123",
        role="client",
        website=website,
        is_active=True,
    )


@pytest.fixture
def support_user(website):
    return User.objects.create_user(
        username="test_support",
        email="support@test.com",
        password="testpass123",
        role="support",
        website=website,
        is_active=True,
    )


@pytest.fixture
def admin_user(db, website):
    return User.objects.create_superuser(
        username="admin",
        email="admin@test.localhost",
        password="testpass123",
        role="superadmin",
        website=website,
    )


@pytest.fixture
def superadmin_user(admin_user):
    return admin_user


@pytest.fixture
def editor_user(db, tenant_site):
    user = User.objects.create_user(
        username="editor",
        email="editor@test.localhost",
        password="testpass123",
        role="editor",
        is_active=True,
    )

    try:
        from cms_core.services.permissions_service import (
            TenantPermissionsService,
        )

        TenantPermissionsService.assign_user_to_tenant(
            user,
            tenant_site,
            role="editor",
        )
    except Exception:
        pass

    return user


@pytest.fixture
def writer_user(db, tenant_site):
    user = User.objects.create_user(
        username="writer",
        email="writer@test.localhost",
        password="testpass123",
        role="writer",
        is_active=True,
    )

    try:
        from cms_core.services.permissions_service import (
            TenantPermissionsService,
        )

        TenantPermissionsService.assign_user_to_tenant(
            user,
            tenant_site,
            role="writer",
        )
    except Exception:
        pass

    return user


@pytest.fixture
def other_writer(website):
    return User.objects.create_user(
        username="other_writer",
        email="otherwriter@test.com",
        password="testpass123",
        role="writer",
        website=website,
        is_active=True,
    )