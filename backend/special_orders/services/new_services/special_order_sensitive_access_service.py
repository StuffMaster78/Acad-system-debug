from __future__ import annotations

from typing import Any

from django.db import models, transaction
from django.utils import timezone

from special_orders.constants import (
    SensitiveAccessAction,
    SensitiveAccessLevel,
    TwoFactorRequestStatus,
)
from special_orders.models import (
    SpecialOrder,
    SpecialOrderAccessGrant,
    SpecialOrderAccessLog,
    SpecialOrderExternalLink,
    SpecialOrderInstitutionProfile,
    SpecialOrderPlatformAccessVault,
    SpecialOrderTwoFactorRequest,
)


class SpecialOrderSensitiveAccessService:
    """
    Manage protected special order access details.

    Default rule:
        Admins and superadmins can access.
        Everyone else needs an explicit active grant.
    """

    ADMIN_ROLES = {
        "admin",
        "superadmin",
    }

    STAFF_ROLES = {
        "admin",
        "superadmin",
        "support",
        "editor",
        "content_manager",
    }

    @classmethod
    @transaction.atomic
    def create_or_update_institution_profile(
        cls,
        *,
        special_order: SpecialOrder,
        institution_name: str,
        institution_type: str,
        country: str = "",
        state_region: str = "",
        city: str = "",
        program_name: str = "",
        course_code: str = "",
        course_name: str = "",
        instructor_name: str = "",
        term_or_semester: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderInstitutionProfile:
        """
        Create or update institution context for a special order.
        """
        if not institution_name.strip():
            raise ValueError("Institution name is required.")

        profile, _created = SpecialOrderInstitutionProfile.objects.update_or_create(
            website=special_order.website,
            special_order=special_order,
            defaults={
                "institution_name": institution_name.strip(),
                "institution_type": institution_type,
                "country": country.strip(),
                "state_region": state_region.strip(),
                "city": city.strip(),
                "program_name": program_name.strip(),
                "course_code": course_code.strip(),
                "course_name": course_name.strip(),
                "instructor_name": instructor_name.strip(),
                "term_or_semester": term_or_semester.strip(),
                "metadata": metadata or {},
            },
        )
        return profile

    @classmethod
    @transaction.atomic
    def create_vault(
        cls,
        *,
        special_order: SpecialOrder,
        platform: str,
        created_by,
        platform_label: str = "",
        login_url: str = "",
        username: str = "",
        encrypted_password: str = "",
        recovery_email: str = "",
        recovery_phone_last4: str = "",
        access_notes: str = "",
        requires_2fa: bool = False,
        preferred_2fa_method: str = "",
        preferred_2fa_window_start=None,
        preferred_2fa_window_end=None,
        timezone_name: str = "UTC",
        metadata: dict[str, Any] | None = None,
        request=None,
    ) -> SpecialOrderPlatformAccessVault:
        """
        Create protected platform access details.
        """
        vault = SpecialOrderPlatformAccessVault.objects.create(
            website=special_order.website,
            special_order=special_order,
            platform=platform,
            platform_label=platform_label.strip(),
            login_url=login_url.strip(),
            username=username.strip(),
            encrypted_password=encrypted_password,
            recovery_email=recovery_email.strip(),
            recovery_phone_last4=recovery_phone_last4.strip(),
            access_notes=access_notes.strip(),
            requires_2fa=requires_2fa,
            preferred_2fa_method=preferred_2fa_method,
            preferred_2fa_window_start=preferred_2fa_window_start,
            preferred_2fa_window_end=preferred_2fa_window_end,
            timezone=timezone_name,
            created_by=created_by,
            metadata=metadata or {},
        )

        cls._record_access_log(
            vault=vault,
            actor=created_by,
            action=SensitiveAccessAction.VAULT_CREATED,
            request=request,
        )

        return vault

    @classmethod
    @transaction.atomic
    def create_external_link(
        cls,
        *,
        special_order: SpecialOrder,
        label: str,
        url: str,
        created_by,
        link_type: str = "other",
        requires_login: bool = False,
        notes: str = "",
    ) -> SpecialOrderExternalLink:
        """
        Create non-secret external link.
        """
        if not label.strip():
            raise ValueError("Link label is required.")

        if not url.strip():
            raise ValueError("URL is required.")

        return SpecialOrderExternalLink.objects.create(
            website=special_order.website,
            special_order=special_order,
            label=label.strip(),
            url=url.strip(),
            link_type=link_type,
            requires_login=requires_login,
            notes=notes.strip(),
            created_by=created_by,
        )

    @classmethod
    @transaction.atomic
    def grant_access(
        cls,
        *,
        vault: SpecialOrderPlatformAccessVault,
        granted_to,
        granted_by,
        access_level: str,
        reason: str,
        expires_at=None,
        request=None,
    ) -> SpecialOrderAccessGrant:
        """
        Grant explicit sensitive access to a user.
        """
        cls._validate_admin(actor=granted_by)

        if granted_to.website_id != vault.website_id:
            raise ValueError("Granted user belongs to another tenant.")

        if not reason.strip():
            raise ValueError("Grant reason is required.")

        grant = SpecialOrderAccessGrant.objects.create(
            website=vault.website,
            vault=vault,
            special_order=vault.special_order,
            granted_to=granted_to,
            granted_by=granted_by,
            access_level=access_level,
            reason=reason.strip(),
            expires_at=expires_at,
        )

        cls._record_access_log(
            vault=vault,
            actor=granted_by,
            action=SensitiveAccessAction.GRANT_CREATED,
            request=request,
            metadata={
                "granted_to_id": granted_to.id,
                "access_level": access_level,
                "grant_id": grant.id,
            },
        )

        return grant

    @classmethod
    @transaction.atomic
    def revoke_access(
        cls,
        *,
        grant: SpecialOrderAccessGrant,
        revoked_by,
        request=None,
    ) -> SpecialOrderAccessGrant:
        """
        Revoke a sensitive access grant.
        """
        cls._validate_admin(actor=revoked_by)

        grant.revoked_at = timezone.now()
        grant.revoked_by = revoked_by
        grant.save(
            update_fields=[
                "revoked_at",
                "revoked_by",
                "updated_at",
            ]
        )

        cls._record_access_log(
            vault=grant.vault,
            actor=revoked_by,
            action=SensitiveAccessAction.GRANT_REVOKED,
            request=request,
            metadata={
                "grant_id": grant.id,
                "granted_to_id": grant.granted_to_id,
            },
        )

        return grant

    @classmethod
    def reveal_vault(
        cls,
        *,
        vault: SpecialOrderPlatformAccessVault,
        actor,
        access_level: str,
        request=None,
    ) -> SpecialOrderPlatformAccessVault:
        """
        Return vault after checking access and logging reveal action.

        Decryption should happen outside or inside a dedicated encryption
        adapter depending on your project setup.
        """
        cls._validate_can_access(
            vault=vault,
            actor=actor,
            required_level=access_level,
        )

        action = SensitiveAccessAction.OPENED_VAULT
        if access_level == SensitiveAccessLevel.REVEAL_PASSWORD:
            action = SensitiveAccessAction.REVEALED_PASSWORD
        elif access_level == SensitiveAccessLevel.VIEW_USERNAME:
            action = SensitiveAccessAction.VIEWED_USERNAME
        elif access_level == SensitiveAccessLevel.VIEW_LINK:
            action = SensitiveAccessAction.OPENED_LINK

        cls._record_access_log(
            vault=vault,
            actor=actor,
            action=action,
            request=request,
            metadata={
                "access_level": access_level,
            },
        )

        return vault

    @classmethod
    @transaction.atomic
    def request_two_factor_code(
        cls,
        *,
        vault: SpecialOrderPlatformAccessVault,
        requested_by,
        message: str = "",
        requested_for_time=None,
        expires_at=None,
        request=None,
    ) -> SpecialOrderTwoFactorRequest:
        """
        Create a 2FA coordination request for the client.
        """
        cls._validate_can_access(
            vault=vault,
            actor=requested_by,
            required_level=SensitiveAccessLevel.MANAGE_2FA,
        )

        two_factor_request = SpecialOrderTwoFactorRequest.objects.create(
            website=vault.website,
            special_order=vault.special_order,
            vault=vault,
            requested_by=requested_by,
            client=vault.special_order.client,
            status=TwoFactorRequestStatus.PENDING,
            preferred_method=vault.preferred_2fa_method,
            message=message.strip(),
            requested_for_time=requested_for_time,
            expires_at=expires_at,
        )

        cls._record_access_log(
            vault=vault,
            actor=requested_by,
            action=SensitiveAccessAction.TWO_FACTOR_REQUESTED,
            request=request,
            metadata={
                "two_factor_request_id": two_factor_request.id,
            },
        )

        return two_factor_request

    @classmethod
    @transaction.atomic
    def complete_two_factor_request(
        cls,
        *,
        two_factor_request: SpecialOrderTwoFactorRequest,
        completed_by,
        code_reference: str = "",
        request=None,
    ) -> SpecialOrderTwoFactorRequest:
        """
        Mark a 2FA coordination request as completed.
        """
        two_factor_request.status = TwoFactorRequestStatus.COMPLETED
        two_factor_request.completed_at = timezone.now()
        two_factor_request.code_reference = code_reference
        two_factor_request.save(
            update_fields=[
                "status",
                "completed_at",
                "code_reference",
                "updated_at",
            ]
        )

        cls._record_access_log(
            vault=two_factor_request.vault,
            actor=completed_by,
            action=SensitiveAccessAction.TWO_FACTOR_COMPLETED,
            request=request,
            metadata={
                "two_factor_request_id": two_factor_request.id,
            },
        )

        return two_factor_request

    @classmethod
    def _validate_can_access(
        cls,
        *,
        vault: SpecialOrderPlatformAccessVault,
        actor,
        required_level: str,
    ) -> None:
        """
        Validate actor can access sensitive vault details.
        """
        if getattr(actor, "website_id", None) != vault.website_id:
            raise ValueError("Cross-tenant sensitive access blocked.")

        if cls._is_admin(actor=actor):
            return

        now = timezone.now()

        grant = SpecialOrderAccessGrant.objects.filter(
            website=vault.website,
            vault=vault,
            granted_to=actor,
            revoked_at__isnull=True,
        ).filter(
            models.Q(expires_at__isnull=True)
            | models.Q(expires_at__gt=now)
        ).order_by("-created_at").first()

        if grant is None:
            raise PermissionError("Sensitive access grant is required.")

        if grant.access_level == SensitiveAccessLevel.FULL:
            return

        allowed = cls._access_level_allows(
            granted_level=grant.access_level,
            required_level=required_level,
        )

        if not allowed:
            raise PermissionError("Sensitive access level is insufficient.")

    @staticmethod
    def _access_level_allows(
        *,
        granted_level: str,
        required_level: str,
    ) -> bool:
        """
        Check whether grant level satisfies required level.
        """
        if granted_level == required_level:
            return True

        if granted_level == SensitiveAccessLevel.REVEAL_PASSWORD:
            return required_level in {
                SensitiveAccessLevel.VIEW_LINK,
                SensitiveAccessLevel.VIEW_USERNAME,
                SensitiveAccessLevel.REVEAL_PASSWORD,
            }

        if granted_level == SensitiveAccessLevel.MANAGE_2FA:
            return required_level in {
                SensitiveAccessLevel.VIEW_LINK,
                SensitiveAccessLevel.VIEW_USERNAME,
                SensitiveAccessLevel.MANAGE_2FA,
            }

        if granted_level == SensitiveAccessLevel.VIEW_USERNAME:
            return required_level in {
                SensitiveAccessLevel.VIEW_LINK,
                SensitiveAccessLevel.VIEW_USERNAME,
            }

        return False

    @classmethod
    def _validate_admin(cls, *, actor) -> None:
        """
        Ensure actor has admin authority.
        """
        if not cls._is_admin(actor=actor):
            raise PermissionError("Admin access is required.")

    @classmethod
    def _is_admin(cls, *, actor) -> bool:
        """
        Return true if actor is admin or superadmin.
        """
        role = str(getattr(actor, "role", "")).lower()
        return role in cls.ADMIN_ROLES

    @staticmethod
    def _record_access_log(
        *,
        vault: SpecialOrderPlatformAccessVault,
        actor,
        action: str,
        request=None,
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderAccessLog:
        """
        Record sensitive access action.
        """
        ip_address = None
        user_agent = ""

        if request is not None:
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")

        return SpecialOrderAccessLog.objects.create(
            website=vault.website,
            vault=vault,
            special_order=vault.special_order,
            accessed_by=actor,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )