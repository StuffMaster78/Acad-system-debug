"""
IP whitelist service.

Handle user-managed IP whitelist settings and login restriction checks
for a specific website context.
"""

from typing import Any

from django.db import transaction
from django.utils import timezone

from authentication.models.ip_whitelist import (
    IPWhitelist,
    UserIPWhitelistSettings,
)


class IPWhitelistService:
    """
    Manage IP whitelist settings and entries for a user on a website.
    """

    def __init__(self, user, website):
        """
        Initialize the IP whitelist service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for IP whitelist."
            )

        self.user = user
        self.website = website

    def get_or_create_settings(self) -> UserIPWhitelistSettings:
        """
        Get or create whitelist settings for the user and website.

        Returns:
            UserIPWhitelistSettings instance.
        """
        settings_obj, _ = (
            UserIPWhitelistSettings.objects.get_or_create(
                user=self.user,
                website=self.website,
                defaults={
                    "is_enabled": False,
                    "allow_emergency_bypass": True,
                },
            )
        )
        return settings_obj

    def is_enabled(self) -> bool:
        """
        Determine whether IP whitelisting is enabled.

        Returns:
            True if enabled, otherwise False.
        """
        return bool(self.get_or_create_settings().is_enabled)

    def is_ip_whitelisted(
        self,
        *,
        ip_address: str | None,
    ) -> bool:
        """
        Determine whether an IP address is whitelisted.

        Args:
            ip_address: IP address to check.

        Returns:
            True if the whitelist is disabled or the IP is whitelisted,
            otherwise False.
        """
        if not self.is_enabled():
            return True

        if not ip_address:
            return False

        return IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            is_active=True,
        ).exists()

    @transaction.atomic
    def add_ip(
        self,
        *,
        ip_address: str,
        label: str = "",
    ) -> IPWhitelist:
        """
        Add or reactivate an IP whitelist entry.

        Args:
            ip_address: IP address to whitelist.
            label: Optional label for the IP.

        Returns:
            IPWhitelist instance.
        """
        entry, created = IPWhitelist.objects.get_or_create(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            defaults={
                "label": label,
                "is_active": True,
            },
        )

        if not created:
            entry.is_active = True
            if label:
                entry.label = label
            entry.save(update_fields=["is_active", "label"])

        return entry

    @transaction.atomic
    def remove_ip(
        self,
        *,
        ip_address: str,
    ) -> int:
        """
        Deactivate an IP whitelist entry.

        Args:
            ip_address: IP address to deactivate.

        Returns:
            Number of updated rows.
        """
        return IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            is_active=True,
        ).update(is_active=False)

    def get_whitelisted_ips(self) -> list[IPWhitelist]:
        """
        Retrieve active whitelist entries.

        Returns:
            List of active IPWhitelist records.
        """
        return list(
            IPWhitelist.objects.filter(
                user=self.user,
                website=self.website,
                is_active=True,
            ).order_by("-created_at")
        )

    @transaction.atomic
    def enable_whitelist(self) -> UserIPWhitelistSettings:
        """
        Enable IP whitelisting for the user and website.

        Returns:
            Updated UserIPWhitelistSettings instance.
        """
        settings_obj = self.get_or_create_settings()
        settings_obj.is_enabled = True
        settings_obj.save(update_fields=["is_enabled"])
        return settings_obj

    @transaction.atomic
    def disable_whitelist(self) -> UserIPWhitelistSettings:
        """
        Disable IP whitelisting for the user and website.

        Returns:
            Updated UserIPWhitelistSettings instance.
        """
        settings_obj = self.get_or_create_settings()
        settings_obj.is_enabled = False
        settings_obj.save(update_fields=["is_enabled"])
        return settings_obj

    @transaction.atomic
    def mark_ip_used(
        self,
        *,
        ip_address: str,
    ) -> int:
        """
        Update the last-used timestamp for a whitelist entry.

        Args:
            ip_address: IP address used during login.

        Returns:
            Number of updated rows.
        """
        return IPWhitelist.objects.filter(
            user=self.user,
            website=self.website,
            ip_address=ip_address,
            is_active=True,
        ).update(last_used_at=timezone.now())

    def check_login_allowed(
        self,
        *,
        ip_address: str | None,
    ) -> dict[str, Any]:
        """
        Determine whether login is allowed from a given IP address.

        Args:
            ip_address: Source IP address.

        Returns:
            Structured login-allowance result.
        """
        settings_obj = self.get_or_create_settings()

        if not settings_obj.is_enabled:
            return {
                "allowed": True,
                "reason": "whitelist_disabled",
                "emergency_bypass_available": False,
            }

        if ip_address and self.is_ip_whitelisted(ip_address=ip_address):
            self.mark_ip_used(ip_address=ip_address)
            return {
                "allowed": True,
                "reason": "ip_whitelisted",
                "emergency_bypass_available": False,
            }

        return {
            "allowed": False,
            "reason": "ip_not_whitelisted",
            "emergency_bypass_available": bool(
                settings_obj.allow_emergency_bypass
            ),
        }