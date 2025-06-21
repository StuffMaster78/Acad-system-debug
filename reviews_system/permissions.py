from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

def create_review_permissions():
    """
    Create permissions for the review models.
    """
    content_type = ContentType.objects.get_for_model(settings.AUTH_USER_MODEL)

    permissions = [
        ("can_create_review", "Can create review"),
        ("can_approve_review", "Can approve review"),
        ("can_shadow_review", "Can shadow review"),
        ("can_view_reviews", "Can view reviews"),
    ]

    for codename, name in permissions:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )

    def assign_review_permissions(user):
        """
        Assign review permissions to a user.
        """
        for codename, _ in permissions:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)

    def remove_review_permissions(user):
        """
        Remove review permissions from a user.
        """
        for codename, _ in permissions:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.remove(permission)

        return {
            "assign": assign_review_permissions,
            "remove": remove_review_permissions
        }

def get_review_permissions():
    """
    Get the review permissions for the current user.
    """
    user = settings.AUTH_USER_MODEL
    return {
        "can_create_review": user.has_perm("reviews_system.can_create_review"),
        "can_approve_review": user.has_perm("reviews_system.can_approve_review"),
        "can_shadow_review": user.has_perm("reviews_system.can_shadow_review"),
        "can_view_reviews": user.has_perm("reviews_system.can_view_reviews"),
    }

def has_review_permission(user, permission_codename):
    """
    Check if the user has a specific review permission.
    """
    return user.has_perm(f"reviews_system.{permission_codename}")

def IsReviewOwnerOrAdmin(user, review):
    """
    Check if the user is the owner of the review or an admin.
    """
    return review.reviewer == user or user.is_staff

def IsReviewApproved(review):
    """
    Check if the review is approved.
    """
    return review.is_approved   