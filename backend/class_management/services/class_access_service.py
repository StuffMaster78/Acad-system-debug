from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassAccessGrantStatus,
    ClassTimelineEventType,
    TwoFactorRequestStatus,
)
from class_management.exceptions import ClassAccessDeniedError
from class_management.models.class_access import (
    ClassAccessDetail,
    ClassAccessGrant,
    ClassAccessLog,
    ClassTwoFactorRequest,
    ClassTwoFactorWindow,
)
from class_management.models.class_order import (
    ClassOrder,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassAccessService:
    """
    Service for protected class portal access.

    Access details should never be read directly from views.
    Always use this service so access grants and audit logs are enforced.
    """
    @staticmethod
    def _get_related_pk(
        *,
        obj: Any,
        field_name: str
    ) -> Any:
        related_obj = getattr(
            obj,
            field_name,
            None,
        )
        return getattr(
            related_obj,
            "pk",
            None,
        )
    
    @staticmethod
    def _get_user_pk(
        user: Any
    ) -> Any:
        return getattr(user, "pk", None)

    @classmethod
    @transaction.atomic
    def create_or_update_access_detail(
        cls,
        *,
        class_order: ClassOrder,
        actor,
        institution_name: str = "",
        institution_state: str = "",
        class_portal_url: str = "",
        class_name: str = "",
        class_code: str = "",
        login_username: str = "",
        login_password: str = "",
        requires_two_factor: bool = False,
        two_factor_method: str = "",
        preferred_contact_method: str = "",
        extra_login_notes: str = "",
        emergency_contact_notes: str = "",
    ) -> ClassAccessDetail:
        """
        Create or update protected class access details.
        """
        encrypted_password = ""

        if login_password:
            encrypted_password = cls._encrypt_secret(
                raw_value=login_password,
            )

        existing_access_detail = ClassAccessDetail.objects.filter(
            class_order=class_order,
        ).first()

        defaults: dict[str, Any] = {
            "institution_name": institution_name,
            "institution_state": institution_state,
            "class_portal_url": class_portal_url,
            "class_name": class_name,
            "class_code": class_code,
            "login_username": login_username,
            "requires_two_factor": requires_two_factor,
            "two_factor_method": two_factor_method,
            "preferred_contact_method": preferred_contact_method,
            "extra_login_notes": extra_login_notes,
            "emergency_contact_notes": emergency_contact_notes,
            "updated_by": actor,
        }

        if encrypted_password:
            defaults["login_password_encrypted"] = encrypted_password

        if existing_access_detail is None:
            defaults["created_by"] = actor

        access_detail, created = ClassAccessDetail.objects.update_or_create(
            class_order=class_order,
            defaults=defaults,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.ACCESS_VIEWED,
            title=(
                "Class access details created"
                if created
                else "Class access details updated"
            ),
            triggered_by=actor,
            metadata={
                "access_detail_id": access_detail.pk,
                "requires_two_factor": requires_two_factor,
            },
        )

        return access_detail

    @classmethod
    @transaction.atomic
    def replace_two_factor_windows(
        cls,
        *,
        access_detail: ClassAccessDetail,
        windows: list[dict[str, Any]],
        actor,
    ) -> list[ClassTwoFactorWindow]:
        """
        Replace 2FA availability windows for a class access detail.
        """
        ClassTwoFactorWindow.objects.filter(
            access_detail=access_detail,
        ).delete()

        created_windows: list[ClassTwoFactorWindow] = []

        for window in windows:
            created_windows.append(
                ClassTwoFactorWindow.objects.create(
                    access_detail=access_detail,
                    weekday=window["weekday"],
                    starts_at=window["starts_at"],
                    ends_at=window["ends_at"],
                    timezone=window.get("timezone", "America/New_York"),
                    is_active=window.get("is_active", True),
                )
            )

        ClassTimelineService.record(
            class_order=access_detail.class_order,
            event_type=ClassTimelineEventType.TWO_FACTOR_REQUESTED,
            title="Class 2FA windows updated",
            triggered_by=actor,
            metadata={
                "access_detail_id": access_detail.pk,
                "window_count": len(created_windows),
            },
        )

        return created_windows

    @classmethod
    @transaction.atomic
    def grant_access(
        cls,
        *,
        class_order: ClassOrder,
        user,
        granted_by,
        reason: str = "",
        expires_at=None,
    ) -> ClassAccessGrant:
        """
        Grant a user permission to view protected access details.
        """
        grant, _ = ClassAccessGrant.objects.update_or_create(
            class_order=class_order,
            user=user,
            status=ClassAccessGrantStatus.ACTIVE,
            defaults={
                "reason": reason,
                "expires_at": expires_at,
                "granted_by": granted_by,
                "revoked_at": None,
            },
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.ACCESS_VIEWED,
            title="Class access granted",
            description=reason,
            triggered_by=granted_by,
            metadata={
                "granted_user_id": cls._get_user_pk(user),
                "grant_id": grant.pk,
                "expires_at": expires_at.isoformat()
                if expires_at
                else "",
            },
        )

        NotificationService.notify(
            event_key="class.access_granted",
            recipient=user,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
                "reason": reason,
            },
            triggered_by=granted_by,
        )

        return grant

    @classmethod
    @transaction.atomic
    def revoke_access(
        cls,
        *,
        class_order: ClassOrder,
        user,
        revoked_by,
        reason: str = "",
    ) -> None:
        """
        Revoke active access grants for a user.
        """
        now = timezone.now()

        ClassAccessGrant.objects.filter(
            class_order=class_order,
            user=user,
            status=ClassAccessGrantStatus.ACTIVE,
        ).update(
            status=ClassAccessGrantStatus.REVOKED,
            revoked_at=now,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.ACCESS_VIEWED,
            title="Class access revoked",
            description=reason,
            triggered_by=revoked_by,
            metadata={
                "revoked_user_id": cls._get_user_pk(user),
            },
        )

    @classmethod
    @transaction.atomic
    def view_access_detail(
        cls,
        *,
        class_order: ClassOrder,
        viewer,
        reason: str = "",
        ip_address: str | None = None,
        user_agent: str = "",
    ) -> dict[str, Any]:
        """
        Return decrypted access details after permission and audit logging.
        """
        if not cls.can_view_access_detail(
            class_order=class_order,
            user=viewer,
        ):
            raise ClassAccessDeniedError(
                "You do not have permission to view class access details."
            )

        access_detail = ClassAccessDetail.objects.filter(
            class_order=class_order,
        ).first()

        if access_detail is None:
            raise ClassAccessDeniedError(
                "This class order has no access details."
            )

        ClassAccessLog.objects.create(
            class_order=class_order,
            viewed_by=viewer,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.ACCESS_VIEWED,
            title="Class access details viewed",
            description=reason,
            triggered_by=viewer,
        )

        return {
            "institution_name": access_detail.institution_name,
            "institution_state": access_detail.institution_state,
            "class_portal_url": access_detail.class_portal_url,
            "class_name": access_detail.class_name,
            "class_code": access_detail.class_code,
            "login_username": access_detail.login_username,
            "login_password": cls._decrypt_secret(
                encrypted_value=access_detail.login_password_encrypted,
            ),
            "requires_two_factor": access_detail.requires_two_factor,
            "two_factor_method": access_detail.two_factor_method,
            "preferred_contact_method": (
                access_detail.preferred_contact_method
            ),
            "extra_login_notes": access_detail.extra_login_notes,
            "emergency_contact_notes": (
                access_detail.emergency_contact_notes
            ),
            "two_factor_windows": [
                {
                    "weekday": window.weekday,
                    "starts_at": window.starts_at,
                    "ends_at": window.ends_at,
                    "timezone": window.timezone,
                    "is_active": window.is_active,
                }
                for window in ClassTwoFactorWindow.objects.filter(
                    access_detail=access_detail,
                    is_active=True,
                )
            ],
        }

    @classmethod
    def can_view_access_detail(
        cls,
        *,
        class_order: ClassOrder,
        user,
    ) -> bool:
        """
        Determine whether a user may view protected class access details.
        """
        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_staff", False):
            return True
        
        assigned_writer_pk = cls._get_related_pk(
            obj=class_order,
            field_name="assigned_writer",
        )

        user_pk = cls._get_user_pk(user)

        if assigned_writer_pk == user_pk:
            return cls._has_active_grant(
                class_order=class_order,
                user=user,
            )

        return cls._has_active_grant(
            class_order=class_order,
            user=user,
        )

    @classmethod
    @transaction.atomic
    def request_two_factor(
        cls,
        *,
        class_order: ClassOrder,
        requested_by,
        needed_by=None,
        request_notes: str = "",
    ) -> ClassTwoFactorRequest:
        """
        Request 2FA help from the client.
        """
        two_factor_request = ClassTwoFactorRequest.objects.create(
            class_order=class_order,
            requested_by=requested_by,
            needed_by=needed_by,
            request_notes=request_notes,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.TWO_FACTOR_REQUESTED,
            title="Class 2FA requested",
            description=request_notes,
            triggered_by=requested_by,
            metadata={
                "two_factor_request_id": two_factor_request.pk,
                "needed_by": needed_by.isoformat()
                if needed_by
                else "",
            },
        )

        NotificationService.notify(
            event_key="class.two_factor_requested",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
                "needed_by": needed_by,
                "request_notes": request_notes,
            },
            triggered_by=requested_by,
        )

        return two_factor_request

    @classmethod
    @transaction.atomic
    def mark_two_factor_sent(
        cls,
        *,
        request: ClassTwoFactorRequest,
        actor,
        notes: str = "",
    ) -> ClassTwoFactorRequest:
        """
        Mark 2FA request as sent by the client.
        """
        if request.status != TwoFactorRequestStatus.PENDING:
            raise ClassAccessDeniedError(
                "Only pending 2FA requests can be marked sent."
            )

        request.status = TwoFactorRequestStatus.SENT
        request.resolution_notes = notes
        request.save(
            update_fields=[
                "status",
                "resolution_notes",
            ]
        )

        ClassTimelineService.record(
            class_order=request.class_order,
            event_type=ClassTimelineEventType.TWO_FACTOR_REQUESTED,
            title="Class 2FA sent",
            description=notes,
            triggered_by=actor,
            metadata={
                "two_factor_request_id": request.pk,
            },
        )

        return request

    @classmethod
    @transaction.atomic
    def resolve_two_factor_request(
        cls,
        *,
        request: ClassTwoFactorRequest,
        resolved_by,
        notes: str = "",
    ) -> ClassTwoFactorRequest:
        """
        Resolve a 2FA request.
        """
        if request.status not in {
            TwoFactorRequestStatus.PENDING,
            TwoFactorRequestStatus.SENT,
        }:
            raise ClassAccessDeniedError(
                "Only pending or sent 2FA requests can be resolved."
            )

        request.status = TwoFactorRequestStatus.RESOLVED
        request.resolved_at = timezone.now()
        request.resolution_notes = notes
        request.save(
            update_fields=[
                "status",
                "resolved_at",
                "resolution_notes",
            ]
        )

        ClassTimelineService.record(
            class_order=request.class_order,
            event_type=ClassTimelineEventType.TWO_FACTOR_REQUESTED,
            title="Class 2FA resolved",
            description=notes,
            triggered_by=resolved_by,
            metadata={
                "two_factor_request_id": request.pk,
            },
        )

        return request

    @staticmethod
    def _has_active_grant(
        *,
        class_order: ClassOrder,
        user,
    ) -> bool:
        """
        Check if a user has an active, non-expired grant.
        """
        grants = ClassAccessGrant.objects.filter(
            class_order=class_order,
            user=user,
            status=ClassAccessGrantStatus.ACTIVE,
        )

        for grant in grants:
            if grant.is_current():
                return True

        return False

    @staticmethod
    def _encrypt_secret(*, raw_value: str) -> str:
        """
        Encrypt a secret value before storage.

        Replace this with your real vault/encryption utility.
        """
        from django.core.signing import dumps

        return dumps(raw_value)

    @staticmethod
    def _decrypt_secret(*, encrypted_value: str) -> str:
        """
        Decrypt a stored secret value.

        Replace this with your real vault/encryption utility.
        """
        if not encrypted_value:
            return ""

        from django.core.signing import loads

        return str(loads(encrypted_value))