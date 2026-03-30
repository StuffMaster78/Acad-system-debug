from __future__ import annotations

from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

if TYPE_CHECKING:
    from users.models.user import User

UserModel = get_user_model()


def get_user_by_id(user_id: int) -> User:
    """
    Return a user by id with commonly needed relations loaded.
    """
    return User.objects.select_related("website", "profile").get(id=user_id)


def get_user_by_email(email: str) -> User:
    """
    Return a user by email with commonly needed relations loaded.
    """
    return User.objects.select_related("website", "profile").get(email=email)


def list_users_for_website(website_id: int) -> QuerySet[User]:
    """
    Return users that belong to a given website.
    """
    return User.objects.select_related("website", "profile").filter(
        website_id=website_id
    )


def list_active_users_for_website(website_id: int) -> QuerySet[User]:
    """
    Return active users that belong to a given website.
    """
    return User.objects.select_related("website", "profile").filter(
        website_id=website_id,
        is_active=True,
    )