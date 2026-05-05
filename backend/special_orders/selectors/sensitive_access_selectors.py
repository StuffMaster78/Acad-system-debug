from __future__ import annotations

from django.db.models import QuerySet

from special_orders.models import (
    SpecialOrderAccessGrant,
    SpecialOrderAccessLog,
    SpecialOrderExternalLink,
    SpecialOrderInstitutionProfile,
    SpecialOrderPlatformAccessVault,
    SpecialOrderTwoFactorRequest,
)


class SpecialOrderSensitiveAccessSelector:
    """
    Tenant-safe read layer for sensitive access records.
    """

    @staticmethod
    def get_institution_profile(*, website, special_order):
        return SpecialOrderInstitutionProfile.objects.get(
            website=website,
            special_order=special_order,
        )

    @staticmethod
    def list_vaults(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderPlatformAccessVault]:
        return (
            SpecialOrderPlatformAccessVault.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related("special_order", "created_by")
            .order_by("-created_at")
        )

    @staticmethod
    def get_vault(
        *,
        website,
        vault_id: int,
    ) -> SpecialOrderPlatformAccessVault:
        return (
            SpecialOrderPlatformAccessVault.objects.select_related(
                "special_order",
                "created_by",
            )
            .get(
                id=vault_id,
                website=website,
            )
        )

    @staticmethod
    def list_external_links(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderExternalLink]:
        return (
            SpecialOrderExternalLink.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related("created_by")
            .order_by("label")
        )

    @staticmethod
    def list_grants(
        *,
        website,
        vault,
    ) -> QuerySet[SpecialOrderAccessGrant]:
        return (
            SpecialOrderAccessGrant.objects.filter(
                website=website,
                vault=vault,
            )
            .select_related("granted_to", "granted_by", "revoked_by")
            .order_by("-created_at")
        )

    @staticmethod
    def get_grant(
        *,
        website,
        grant_id: int,
    ) -> SpecialOrderAccessGrant:
        return (
            SpecialOrderAccessGrant.objects.select_related(
                "vault",
                "special_order",
                "granted_to",
                "granted_by",
                "revoked_by",
            )
            .get(id=grant_id, website=website)
        )

    @staticmethod
    def list_access_logs(
        *,
        website,
        vault,
    ) -> QuerySet[SpecialOrderAccessLog]:
        return (
            SpecialOrderAccessLog.objects.filter(
                website=website,
                vault=vault,
            )
            .select_related("accessed_by")
            .order_by("-created_at")
        )

    @staticmethod
    def list_two_factor_requests(
        *,
        website,
        special_order,
    ) -> QuerySet[SpecialOrderTwoFactorRequest]:
        return (
            SpecialOrderTwoFactorRequest.objects.filter(
                website=website,
                special_order=special_order,
            )
            .select_related("vault", "requested_by", "client")
            .order_by("-created_at")
        )

    @staticmethod
    def get_two_factor_request(
        *,
        website,
        request_id: int,
    ) -> SpecialOrderTwoFactorRequest:
        return (
            SpecialOrderTwoFactorRequest.objects.select_related(
                "vault",
                "special_order",
                "requested_by",
                "client",
            )
            .get(id=request_id, website=website)
        )