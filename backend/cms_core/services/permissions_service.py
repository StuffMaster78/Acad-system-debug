"""
Tenant Permissions Service
============================

Creates and manages per-tenant permission groups and their scoping.

Each tenant gets three Groups:
    • ``{Tenant} Admins``   — can add, edit, publish, lock any page in the
      tenant's tree.  Can also manage snippets and images for the tenant.
    • ``{Tenant} Editors``  — can add, edit, and submit for moderation.
      Cannot publish directly (unless overridden).
    • ``{Tenant} Writers``  — can add and edit own drafts only.
      Must submit for review.

Superusers bypass all of this (Django built-in).

Usage:
    from cms_core.services.permissions_service import TenantPermissionsService

    TenantPermissionsService.setup_tenant_permissions(site)
    TenantPermissionsService.assign_user_to_tenant(user, site, role="editor")
"""

from __future__ import annotations

import logging
from typing import Literal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from wagtail.models import (
    GroupCollectionPermission,
    GroupPagePermission,
    Page,
    Site,
)

logger = logging.getLogger(__name__)

User = get_user_model()

RoleName = Literal["admin", "editor", "writer"]

# Page permission types in Wagtail
PAGE_PERMISSION_TYPES = {
    "admin": ["add", "edit", "publish", "bulk_delete", "lock"],
    "editor": ["add", "edit", "publish"],
    "writer": ["add", "edit"],
}


class TenantPermissionsService:
    """Manage per-tenant Groups and their page/collection permissions."""

    # ---------------------------------------------------------------
    # Group names
    # ---------------------------------------------------------------

    @staticmethod
    def _group_name(site: Site, role: RoleName) -> str:
        """Canonical group name for a tenant + role."""
        tenant_name = site.site_name or site.hostname
        return f"{tenant_name} {role.title()}s"

    # ---------------------------------------------------------------
    # Setup
    # ---------------------------------------------------------------

    @classmethod
    def setup_tenant_permissions(cls, site: Site) -> dict[str, Group]:
        """
        Create the three permission groups for a tenant and wire them
        to the tenant's page tree and image collection.

        Idempotent — safe to call repeatedly.

        Returns dict: {"admin": Group, "editor": Group, "writer": Group}
        """
        from wagtail.models import Collection

        root_page = site.root_page
        groups = {}

        for role in ("admin", "editor", "writer"):
            group_name = cls._group_name(site, role)
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                logger.info("Created group: %s", group_name)

            # --- Page permissions ---
            cls._set_page_permissions(group, root_page, role)

            # --- Collection permissions (for images/documents) ---
            cls._set_collection_permissions(group, site, role)

            # --- Wagtail admin access ---
            cls._ensure_wagtail_admin_access(group)

            groups[role] = group

        return groups

    @classmethod
    def _set_page_permissions(
        cls, group: Group, root_page: Page, role: RoleName
    ) -> None:
        """Grant page permissions on the tenant's entire subtree."""
        permission_types = PAGE_PERMISSION_TYPES.get(role, [])

        for perm_type in permission_types:
            _, created = GroupPagePermission.objects.get_or_create(
                group=group,
                page=root_page,
                permission_type=perm_type,
            )
            if created:
                logger.debug(
                    "Granted %s.%s on page %s",
                    group.name,
                    perm_type,
                    root_page.title,
                )

    @classmethod
    def _set_collection_permissions(
        cls, group: Group, site: Site, role: RoleName
    ) -> None:
        """
        Create a Collection for the tenant (if needed) and grant the
        group add/change/choose permissions on images and documents
        within that collection.
        """
        from wagtail.models import Collection

        # Get or create a tenant-specific collection under Root
        root_collection = Collection.objects.filter(depth=1).first()
        if root_collection is None:
            logger.warning("No root collection found — skipping collection permissions")
            return

        tenant_name = site.site_name or site.hostname
        tenant_collection = Collection.objects.filter(
            name=tenant_name,
            depth=2,
        ).first()

        if tenant_collection is None:
            tenant_collection = root_collection.add_child(name=tenant_name)
            logger.info("Created collection: %s", tenant_name)

        # Permission codenames for images and documents
        if role in ("admin", "editor"):
            codenames = [
                "add_image",
                "change_image",
                "choose_image",
                "add_document",
                "change_document",
                "choose_document",
            ]
        else:  # writer
            codenames = [
                "add_image",
                "choose_image",
                "add_document",
                "choose_document",
            ]

        for codename in codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                GroupCollectionPermission.objects.get_or_create(
                    group=group,
                    collection=tenant_collection,
                    permission=permission,
                )
            except Permission.DoesNotExist:
                logger.debug("Permission %s not found — skipping", codename)

    @classmethod
    def _ensure_wagtail_admin_access(cls, group: Group) -> None:
        """Ensure the group has access to the Wagtail admin."""
        try:
            admin_perm = Permission.objects.get(
                codename="access_admin",
                content_type__app_label="wagtailadmin",
            )
            group.permissions.add(admin_perm)
        except Permission.DoesNotExist:
            logger.debug("wagtailadmin.access_admin permission not found")

    # ---------------------------------------------------------------
    # User management
    # ---------------------------------------------------------------

    @classmethod
    def assign_user_to_tenant(
        cls,
        user,
        site: Site,
        role: RoleName = "editor",
    ) -> Group:
        """
        Add a user to a tenant's role group.

        If the groups don't exist yet, creates them first.

        Returns the Group the user was added to.
        """
        group_name = cls._group_name(site, role)

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            # Auto-create if missing
            groups = cls.setup_tenant_permissions(site)
            group = groups[role]

        user.groups.add(group)
        logger.info(
            "Assigned user '%s' to %s",
            user.get_username(),
            group_name,
        )
        return group

    @classmethod
    def remove_user_from_tenant(
        cls,
        user,
        site: Site,
        role: RoleName | None = None,
    ) -> None:
        """
        Remove a user from a tenant.
        If role is None, removes from all roles for that tenant.
        """
        if role:
            roles = [role]
        else:
            roles = ["admin", "editor", "writer"]

        for r in roles:
            group_name = cls._group_name(site, r)
            try:
                group = Group.objects.get(name=group_name)
                user.groups.remove(group)
                logger.info(
                    "Removed user '%s' from %s",
                    user.get_username(),
                    group_name,
                )
            except Group.DoesNotExist:
                pass

    @classmethod
    def get_user_tenant_roles(cls, user) -> list[dict]:
        """
        Return all (site, role) pairs for a user.

        Returns:
            [{"site": Site, "role": "editor"}, ...]
        """
        if user.is_superuser:
            return [
                {"site": site, "role": "superadmin"}
                for site in Site.objects.all()
            ]

        results = []
        for group in user.groups.all():
            for role in ("admin", "editor", "writer"):
                for site in Site.objects.all():
                    expected_name = cls._group_name(site, role)
                    if group.name == expected_name:
                        results.append({"site": site, "role": role})

        return results

    # ---------------------------------------------------------------
    # Queries
    # ---------------------------------------------------------------

    @classmethod
    def can_user_access_site(cls, user, site: Site) -> bool:
        """Check if a user has any CMS permission on a given Site."""
        if user.is_superuser:
            return True

        for role in ("admin", "editor", "writer"):
            group_name = cls._group_name(site, role)
            if user.groups.filter(name=group_name).exists():
                return True
        return False

    @classmethod
    def can_user_publish_on_site(cls, user, site: Site) -> bool:
        """Check if a user can publish (not just edit) on a Site."""
        if user.is_superuser:
            return True

        for role in ("admin", "editor"):
            group_name = cls._group_name(site, role)
            if user.groups.filter(name=group_name).exists():
                return True
        return False

    @classmethod
    def get_tenant_editors(cls, site: Site) -> list:
        """Return all users who have any CMS role on this tenant."""
        users = set()
        for role in ("admin", "editor", "writer"):
            group_name = cls._group_name(site, role)
            try:
                group = Group.objects.get(name=group_name)
                users.update(group.user_set.all())
            except Group.DoesNotExist:
                pass
        return list(users)
