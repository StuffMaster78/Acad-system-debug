from __future__ import annotations

from typing import Any, cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from users.models.profile import (
    ProfileUpdateRequest,
    ProfileUpdateRequestStatus,
    UserProfile,
)
from users.models.user import User
from audit_logging.services.audit_log_service import AuditLogService


class ProfileUpdateService:
    """
    Service for handling profile update request workflows.
    """

    REVIEWABLE_FIELDS = {
        "display_name",
        "bio",
        "avatar",
        "timezone",
        "locale",
        "country",
    }

    @classmethod
    def _validate_requested_changes(cls, changes: dict[str, Any]) -> None:
        """
        Validate requested profile changes.
        """
        if not isinstance(changes, dict):
            raise ValidationError(
                {"requested_changes": "Requested changes must be an object."}
            )

        invalid_fields = set(changes.keys()) - cls.REVIEWABLE_FIELDS
        if invalid_fields:
            raise ValidationError(
                {
                    "requested_changes": (
                        "These fields are not allowed for profile update "
                        f"requests: {sorted(invalid_fields)}"
                    )
                }
            )

    @classmethod
    @transaction.atomic
    def submit_request(
        cls,
        *,
        user: User,
        requested_changes: dict[str, Any],
        submitted_note: str = "",
    ) -> ProfileUpdateRequest:
        """
        Submit a new profile update request.

        This stores proposed changes without applying them to the live profile.
        """
        cls._validate_requested_changes(requested_changes)

        if user.website is None:
            raise ValidationError(
                {"user": "User must belong to a website to submit this request."}
            )

        profile, _ = UserProfile.objects.get_or_create(user=user)

        pending_exists = ProfileUpdateRequest.objects.filter(
            user=user,
            status__in=[
                ProfileUpdateRequestStatus.PENDING,
                ProfileUpdateRequestStatus.UNDER_REVIEW,
                ProfileUpdateRequestStatus.APPROVED,
            ],
        ).exists()

        if pending_exists:
            raise ValidationError(
                "You already have a pending profile update request."
            )

        request_obj = ProfileUpdateRequest.objects.create(
            user=user,
            website=user.website,
            profile=profile,
            requested_changes=requested_changes,
            submitted_note=submitted_note,
            status=ProfileUpdateRequestStatus.PENDING,
        )

        AuditLogService.log_auto(
            action="profile_update_submitted",
            actor=user,
            target=request_obj,
            metadata={
                "website_id": user.website.pk,
                "requested_fields": sorted(requested_changes.keys()),
            },
        )

        return request_obj

    @staticmethod
    @transaction.atomic
    def mark_under_review(
        *,
        request_obj: ProfileUpdateRequest,
        reviewer: User,
    ) -> ProfileUpdateRequest:
        """
        Move a pending request into under review state.
        """
        if request_obj.status != ProfileUpdateRequestStatus.PENDING:
            raise ValidationError(
                "Only pending requests can move to under review."
            )

        old_status = request_obj.status

        request_obj.status = ProfileUpdateRequestStatus.UNDER_REVIEW
        setattr(request_obj, "reviewed_by", reviewer)
        request_obj.reviewed_at = timezone.now()
        request_obj.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "updated_at",
            ]
        )

        AuditLogService.log_auto(
            action="profile_update_marked_under_review",
            actor=reviewer,
            target=request_obj,
            metadata={
                "website_id": request_obj.website.pk,
                "subject_user_id": request_obj.user.pk,
            },
            changes={
                "status": {
                    "from": old_status,
                    "to": request_obj.status,
                }
            },
        )

        return request_obj

    @staticmethod
    @transaction.atomic
    def approve(
        *,
        request_obj: ProfileUpdateRequest,
        reviewer: User,
        review_note: str = "",
    ) -> ProfileUpdateRequest:
        """
        Approve a profile update request.

        Approval does not automatically apply the changes unless you call
        apply_approved_request.
        """
        if request_obj.status not in {
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        }:
            raise ValidationError("This request cannot be approved.")

        old_status = request_obj.status

        setattr(request_obj, "reviewed_by", reviewer)
        request_obj.reviewed_at = timezone.now()
        request_obj.review_note = review_note
        request_obj.status = ProfileUpdateRequestStatus.APPROVED
        request_obj.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_note",
                "updated_at",
            ]
        )

        AuditLogService.log_auto(
            action="profile_update_approved",
            actor=reviewer,
            target=request_obj,
            metadata={
                "website_id": request_obj.website.pk,
                "subject_user_id": request_obj.user.pk,
            },
            changes={
                "status": {
                    "from": old_status,
                    "to": request_obj.status,
                }
            },
            notes=review_note,
        )
        return request_obj

    @staticmethod
    @transaction.atomic
    def reject(
        *,
        request_obj: ProfileUpdateRequest,
        reviewer: User,
        review_note: str,
    ) -> ProfileUpdateRequest:
        """
        Reject a profile update request.
        """
        if request_obj.status not in {
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        }:
            raise ValidationError("This request cannot be rejected.")

        if not review_note.strip():
            raise ValidationError(
                {"review_note": "A rejection reason is required."}
            )

        old_status = request_obj.status

        setattr(request_obj, "reviewed_by", reviewer)
        request_obj.reviewed_at = timezone.now()
        request_obj.review_note = review_note
        request_obj.status = ProfileUpdateRequestStatus.REJECTED
        request_obj.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_note",
                "updated_at",
            ]
        )

        AuditLogService.log_auto(
            action="profile_update_rejected",
            actor=reviewer,
            target=request_obj,
            metadata={
                "website_id": request_obj.website.pk,
                "subject_user_id": request_obj.user.pk,
            },
            changes={
                "status": {
                    "from": old_status,
                    "to": request_obj.status,
                }
            },
            notes=review_note,
        )
        return request_obj

    @staticmethod
    @transaction.atomic
    def cancel(
        *,
        request_obj: ProfileUpdateRequest,
        actor: User,
    ) -> ProfileUpdateRequest:
        """
        Cancel a pending or under-review request.

        Only the owner of the request should normally be allowed to do this,
        unless your permissions layer allows staff cancellation.
        """
        request_user_pk = request_obj.user.pk
        actor_pk = actor.pk

        if request_user_pk is None or actor_pk is None:
            raise ValidationError("User identity is invalid for cancellation.")

        if request_user_pk != actor_pk:
            raise ValidationError(
                "You can only cancel your own profile update request."
            )

        if request_obj.status not in {
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        }:
            raise ValidationError("This request cannot be cancelled.")

        old_status = request_obj.status

        request_obj.status = ProfileUpdateRequestStatus.CANCELLED
        request_obj.save(update_fields=["status", "updated_at"])

        AuditLogService.log_auto(
            action="profile_update_cancelled",
            actor=actor,
            target=request_obj,
            metadata={
                "website_id": request_obj.website.pk,
                "subject_user_id": request_obj.user.pk,
            },
            changes={
                "status": {
                    "from": old_status,
                    "to": request_obj.status,
                }
            },
        )

        return request_obj

    @classmethod
    @transaction.atomic
    def apply_approved_request(
        cls,
        *,
        request_obj: ProfileUpdateRequest,
    ) -> ProfileUpdateRequest:
        """
        Apply approved changes to the live profile.
        """
        if request_obj.status != ProfileUpdateRequestStatus.APPROVED:
            raise ValidationError("Only approved requests can be applied.")

        requested_changes = cast(dict[str, Any], request_obj.requested_changes)
        cls._validate_requested_changes(requested_changes)

        profile = request_obj.profile
        changed_fields: list[str] = []

        changes: dict[str, dict[str, Any]] = {}

        for field, value in requested_changes.items():
            old_value = getattr(profile, field)
            changes[field] = {
                "from": old_value,
                "to": value,
            }
            setattr(profile, field, value)
            changed_fields.append(field)

        if changed_fields:
            profile.save(update_fields=[*changed_fields, "updated_at"])

        old_status = request_obj.status

        request_obj.status = ProfileUpdateRequestStatus.APPLIED
        actor = request_obj.reviewed_by or request_obj.user
        request_obj.applied_at = timezone.now()
        
        request_obj.save(
            update_fields=[
                "status",
                "applied_at",
                "updated_at",
            ]
        )

        changes["__request_status__"] = {
            "from": old_status,
            "to": request_obj.status,
        }

        AuditLogService.log_auto(
            action="profile_update_applied",
            actor=actor,
            target=profile,
            metadata={
                "website_id": request_obj.website.pk,
                "profile_update_request_id": request_obj.pk,
                "subject_user_id": request_obj.user.pk,
            },
            changes=changes,
        )
        return request_obj