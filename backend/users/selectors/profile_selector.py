from __future__ import annotations

from django.db.models import QuerySet

from users.models.profile import UserProfile


def get_profile_by_user_id(user_id: int) -> UserProfile:
    """
    Return the profile for a given user id.
    """
    return UserProfile.objects.select_related(
        "user",
        "user__website",
    ).get(user_id=user_id)


def get_profile_by_id(profile_id: int) -> UserProfile:
    """
    Return a profile by id.
    """
    return UserProfile.objects.select_related(
        "user",
        "user__website",
    ).get(id=profile_id)


def list_profiles_for_website(website_id: int) -> QuerySet[UserProfile]:
    """
    Return profiles for users belonging to a website.
    """
    return UserProfile.objects.select_related(
        "user",
        "user__website",
    ).filter(user__website_id=website_id)


def list_recently_seen_profiles_for_website(
    website_id: int,
) -> QuerySet[UserProfile]:
    """
    Return website profiles ordered by most recent seen timestamp.
    """
    return UserProfile.objects.select_related(
        "user",
        "user__website",
    ).filter(
        user__website_id=website_id
    ).order_by(
        "-last_seen_at",
        "-updated_at",
    )