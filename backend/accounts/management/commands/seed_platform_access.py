from __future__ import annotations

from django.core.management.base import BaseCommand

from accounts.models import (
    PermissionDefinition,
    PortalDefinition,
    RoleDefinition,
    RolePermission,
)
from websites.models.websites import Website


class Command(BaseCommand):
    help = "Seed platform portals, roles, permissions, and role permissions."

    PORTALS = [
        {
            "code": "internal_admin",
            "name": "Internal Admin",
            "domain": "ordermanagement.com",
        },
        {
            "code": "writer_portal",
            "name": "Writer Portal",
            "domain": "writers.ordermanagement.com",
        },
        {
            "code": "client_portal",
            "name": "Client Portal",
            "domain": "dynamic",
        },
    ]

    ROLES = [
        {
            "key": "superadmin",
            "label": "Superadmin",
            "description": "Platform level administrator.",
        },
        {
            "key": "admin",
            "label": "Admin",
            "description": "Tenant administrator.",
        },
        {
            "key": "support",
            "label": "Support",
            "description": "Support operations user.",
        },
        {
            "key": "writer",
            "label": "Writer",
            "description": "Writer portal user.",
        },
        {
            "key": "client",
            "label": "Client",
            "description": "Client portal user.",
        },
        {
            "key": "editor",
            "label": "Editor",
            "description": "Quality/editorial reviewer.",
        },
        {
            "key": "content_manager",
            "label": "Content Manager",
            "description": "CMS and SEO content manager.",
        },
        {
            "key": "finance_manager",
            "label": "Finance Manager",
            "description": "Payments, wallet, and ledger reviewer.",
        },
        {
            "key": "quality_manager",
            "label": "Quality Manager",
            "description": "Quality assurance manager.",
        },
    ]

    PERMISSIONS = [
        ("accounts.manage_users", "Manage Users"),
        ("accounts.assign_roles", "Assign Roles"),
        ("accounts.suspend_user", "Suspend User"),
        ("accounts.view_users", "View Users"),
        ("orders.view_all", "View All Orders"),
        ("orders.view_own", "View Own Orders"),
        ("orders.create", "Create Orders"),
        ("orders.assign_writer", "Assign Writer"),
        ("orders.cancel_order", "Cancel Order"),
        ("orders.message_users", "Message Order Users"),
        ("writers.manage_levels", "Manage Writer Levels"),
        ("writers.manage_capacity", "Manage Writer Capacity"),
        ("writers.view_performance", "View Writer Performance"),
        ("support.handle_cases", "Handle Support Cases"),
        ("support.escalate_cases", "Escalate Support Cases"),
        ("payments.view", "View Payments"),
        ("payments.refund", "Refund Payments"),
        ("wallets.adjust", "Adjust Wallets"),
        ("ledger.view", "View Ledger"),
        ("cms.create_content", "Create Content"),
        ("cms.edit_content", "Edit Content"),
        ("cms.publish_content", "Publish Content"),
        ("files.upload", "Upload Files"),
        ("files.review_delete_request", "Review File Delete Request"),
        ("files.approve_delete", "Approve File Delete"),
        ("editor.view_tasks", "View Editor Tasks"),
        ("editor.review_submissions", "Review Submissions"),
        ("quality.approve_delivery", "Approve Delivery"),
    ]

    ROLE_PERMISSION_MAP = {
        "superadmin": "__all__",
        "admin": [
            "accounts.view_users",
            "orders.view_all",
            "orders.assign_writer",
            "orders.cancel_order",
            "orders.message_users",
            "writers.manage_capacity",
            "writers.view_performance",
            "support.handle_cases",
            "cms.create_content",
            "cms.edit_content",
            "cms.publish_content",
            "files.review_delete_request",
        ],
        "support": [
            "accounts.view_users",
            "orders.view_all",
            "orders.message_users",
            "support.handle_cases",
            "support.escalate_cases",
            "payments.view",
            "files.review_delete_request",
        ],
        "writer": [
            "orders.view_own",
            "orders.message_users",
            "files.upload",
        ],
        "client": [
            "orders.create",
            "orders.view_own",
            "orders.message_users",
            "files.upload",
        ],
        "editor": [
            "editor.view_tasks",
            "editor.review_submissions",
            "quality.approve_delivery",
            "orders.view_all",
            "files.review_delete_request",
        ],
        "content_manager": [
            "cms.create_content",
            "cms.edit_content",
            "cms.publish_content",
        ],
        "finance_manager": [
            "payments.view",
            "payments.refund",
            "wallets.adjust",
            "ledger.view",
        ],
        "quality_manager": [
            "editor.view_tasks",
            "editor.review_submissions",
            "quality.approve_delivery",
            "orders.view_all",
        ],
    }

    def handle(self, *args, **options):
        self._seed_portals()
        self._seed_roles()
        self._seed_permissions()
        self._seed_role_permissions()

        self.stdout.write(
            self.style.SUCCESS("Platform access seed completed.")
        )

    def _seed_portals(self) -> None:
        for item in self.PORTALS:
            PortalDefinition.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "domain": item["domain"],
                    "is_active": True,
                },
            )

    def _seed_roles(self) -> None:
        websites = Website.objects.all()

        for website in websites:
            for item in self.ROLES:
                RoleDefinition.objects.update_or_create(
                    website=website,
                    key=item["key"],
                    defaults={
                        "name": item["label"],  # use name not label
                        "description": item["description"],
                        "is_system_role": True,
                        "is_active": True,
                    },
                )

    def _seed_permissions(self) -> None:
        for code, name in self.PERMISSIONS:
            PermissionDefinition.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )

    def _seed_role_permissions(self) -> None:
        websites = Website.objects.all()

        all_permission_codes = [
            code for code, _name in self.PERMISSIONS
        ]

        for website in websites:
            for role_key, permission_codes in self.ROLE_PERMISSION_MAP.items():
                role = RoleDefinition.objects.get(
                    website=website,
                    key=role_key,
                )

                if permission_codes == "__all__":
                    codes = all_permission_codes
                else:
                    codes = permission_codes

                for code in codes:
                    permission = PermissionDefinition.objects.get(code=code)

                    RolePermission.objects.update_or_create(
                        role=role,
                        permission=permission,
                        defaults={"is_active": True},
                    )