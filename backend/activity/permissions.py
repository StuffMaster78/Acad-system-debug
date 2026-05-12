from __future__ import annotations

from rest_framework.permissions import BasePermission

from activity.selectors.event_selectors import ActivityEventSelector


class CanViewActivityEvent(BasePermission):
    """
    Allows access only to tenant scoped visible activity events.
    """

    def has_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request,
            view,
        ):  
        """
        Allow authenticated users only.
        """
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission( # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            request,
            view,
            obj,
        ):  
        """
        Check object visibility for the current user.
        """
        website = getattr(request, "website", None)

        if website is None:
            return False

        if obj.website_id != website.id:
            return False

        return ActivityEventSelector.user_can_view(
            event=obj,
            user=request.user,
        )