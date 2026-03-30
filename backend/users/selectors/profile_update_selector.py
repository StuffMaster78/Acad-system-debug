from __future__ import annotations

from django.db.models import QuerySet

from users.models.profile import (
    ProfileUpdateRequest,
    ProfileUpdateRequestStatus,
)


def get_profile_update_request_by_id(
    request_id: int,
) -> ProfileUpdateRequest:
    """
    Return a profile update request by id with related objects loaded.
    """
    return ProfileUpdateRequest.objects.select_related(
        "user",
        "user__website",
        "profile",
        "website",
        "reviewed_by",
    ).get(id=request_id)


def list_profile_update_requests_for_user(
    user_id: int,
) -> QuerySet[ProfileUpdateRequest]:
    """
    Return all profile update requests for a user.
    """
    return ProfileUpdateRequest.objects.select_related(
        "user",
        "profile",
        "website",
        "reviewed_by",
    ).filter(user_id=user_id).order_by("-created_at")


def list_open_profile_update_requests_for_website(
    website_id: int,
) -> QuerySet[ProfileUpdateRequest]:
    """
    Return open profile update requests for a website review queue.
    """
    return ProfileUpdateRequest.objects.select_related(
        "user",
        "profile",
        "website",
        "reviewed_by",
    ).filter(
        website_id=website_id,
        status__in=[
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
            ProfileUpdateRequestStatus.APPROVED,
        ],
    ).order_by("created_at")


def list_reviewable_profile_update_requests_for_website(
    website_id: int,
) -> QuerySet[ProfileUpdateRequest]:
    """
    Return pending and under-review profile update requests for a website.
    """
    return ProfileUpdateRequest.objects.select_related(
        "user",
        "profile",
        "website",
        "reviewed_by",
    ).filter(
        website_id=website_id,
        status__in=[
            ProfileUpdateRequestStatus.PENDING,
            ProfileUpdateRequestStatus.UNDER_REVIEW,
        ],
    ).order_by("created_at")


def get_latest_open_profile_update_request_for_user(
    user_id: int,
) -> ProfileUpdateRequest | None:
    """
    Return the latest open profile update request for a user, if one exists.
    """
    return (
        ProfileUpdateRequest.objects.select_related(
            "user",
            "profile",
            "website",
            "reviewed_by",
        )
        .filter(
            user_id=user_id,
            status__in=[
                ProfileUpdateRequestStatus.PENDING,
                ProfileUpdateRequestStatus.UNDER_REVIEW,
                ProfileUpdateRequestStatus.APPROVED,
            ],
        )
        .order_by("-created_at")
        .first()
    )