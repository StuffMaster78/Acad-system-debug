"""
Tests for tenant service — the Site ↔ Website bridge.
"""

import pytest


@pytest.mark.django_db
class TestTenantService:

    def test_get_sites_for_superuser_returns_all(self, admin_user, tenant_site):
        from cms_core.services.tenant_service import get_sites_for_user

        sites = get_sites_for_user(admin_user)
        assert len(sites) >= 1

    def test_get_sites_for_editor(self, editor_user, tenant_site):
        from cms_core.services.tenant_service import get_sites_for_user

        sites = get_sites_for_user(editor_user)
        # Editor should have access to at least the test tenant
        assert any(s.pk == tenant_site.pk for s in sites)

    def test_filter_queryset_by_user_sites(self, editor_user, tenant_site, blog_category):
        from cms_core.models import BlogCategory
        from cms_core.services.tenant_service import filter_queryset_by_user_sites

        qs = BlogCategory.objects.all()
        filtered = filter_queryset_by_user_sites(qs, editor_user)
        assert filtered.filter(pk=blog_category.pk).exists()


@pytest.mark.django_db
class TestPermissionsService:

    def test_setup_creates_three_groups(self, tenant_site):
        from django.contrib.auth.models import Group

        from cms_core.services.permissions_service import TenantPermissionsService

        groups = TenantPermissionsService.setup_tenant_permissions(tenant_site)
        assert "admin" in groups
        assert "editor" in groups
        assert "writer" in groups

    def test_assign_user_to_tenant(self, tenant_site):
        from django.contrib.auth import get_user_model

        from cms_core.services.permissions_service import TenantPermissionsService

        User = get_user_model()
        user = User.objects.create_user("testuser", "test@test.com", "pass")
        group = TenantPermissionsService.assign_user_to_tenant(user, tenant_site, "editor")
        assert user.groups.filter(pk=group.pk).exists()

    def test_can_user_access_site(self, editor_user, tenant_site):
        from cms_core.services.permissions_service import TenantPermissionsService

        assert TenantPermissionsService.can_user_access_site(editor_user, tenant_site)
