from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from communications.models.thread import CommunicationThread
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)


class CommunicationThreadSelector:
    """
    Thread query helpers.
    """

    @staticmethod
    def visible_to_user(
        *,
        website,
        user,
    ) -> QuerySet[CommunicationThread]:
        """
        Return threads visible to a user.
        """
        base_qs = CommunicationThread.objects.all()

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return base_qs

        return (
            base_qs
            .filter(
                website=website,
                participants__user=user,
                participants__can_view=True,
                participants__removed_at__isnull=True,
            )
            .distinct()
        )

    @staticmethod
    def for_target(
        *,
        website,
        target,
    ) -> QuerySet[CommunicationThread]:
        """
        Return threads for a domain object.
        """
        return CommunicationThread.objects.filter(
            website=website,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.id,
        )

    @staticmethod
    def for_target_visible_to_user(
        *,
        website,
        user,
        target,
    ) -> QuerySet[CommunicationThread]:
        """
        Return threads for a target visible to a user.
        """
        qs = CommunicationThreadSelector.for_target(
            website=website,
            target=target,
        )

        if CommunicationThreadGuardService._has_platform_access(user=user):
            return qs

        return (
            qs.filter(
                participants__user=user,
                participants__can_view=True,
                participants__removed_at__isnull=True,
            )
            .distinct()
        )
