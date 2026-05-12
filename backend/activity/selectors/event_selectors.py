from __future__ import annotations

from django.db.models import QuerySet

from activity.constants import ActivityAudience
from activity.models import ActivityEvent


class ActivityEventSelector:
    """
    Read helpers for activity events.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[ActivityEvent]:
        """
        Return activity events for a tenant.
        """
        return ActivityEvent.objects.filter(
            website=website,
        )

    @staticmethod
    def for_target(
        *,
        website,
        target,
    ) -> QuerySet[ActivityEvent]:
        """
        Return activity events for a target object.
        """
        return ActivityEvent.objects.filter(
            website=website,
            target_content_type__app_label=target._meta.app_label,
            target_content_type__model=target._meta.model_name,
            target_object_id=str(target.pk),
        )

    @staticmethod
    def visible_to_audience(
        *,
        website,
        audience: str,
    ) -> QuerySet[ActivityEvent]:
        """
        Return events visible to a given audience.
        """
        return ActivityEvent.objects.filter(
            website=website,
            audiences__contains=[audience],
        )

    @staticmethod
    def visible_to_user(
        *,
        website,
        user,
    ) -> QuerySet[ActivityEvent]:
        """
        Return events visible to the given user.
        """
        audience = ActivityEventSelector.get_user_audience(user=user)

        return ActivityEventSelector.visible_to_audience(
            website=website,
            audience=audience,
        ).select_related(
            "website",
            "actor_content_type",
            "target_content_type",
            "subject_content_type",
        )

    @staticmethod
    def user_can_view(
        *,
        event: ActivityEvent,
        user,
    ) -> bool:
        """
        Return whether a user can view an event.
        """
        audience = ActivityEventSelector.get_user_audience(user=user)

        return audience in event.audiences

    @staticmethod
    def get_user_audience(*, user) -> str:
        """
        Resolve a user's activity audience.
        """
        if getattr(user, "is_superuser", False):
            return ActivityAudience.SUPERADMIN

        if getattr(user, "is_staff", False):
            return ActivityAudience.STAFF

        role = getattr(user, "role", "")

        if role == ActivityAudience.WRITER:
            return ActivityAudience.WRITER

        return ActivityAudience.CLIENT