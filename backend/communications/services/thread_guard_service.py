from __future__ import annotations

from django.core.exceptions import PermissionDenied

from communications.models import CommunicationParticipant
from communications.constants import CommunicationThreadKind


class CommunicationThreadGuardService:
    """
    Central authority for thread access control.

    This service enforces:
        - platform wide staff access
        - tenant scoped access
        - participant level access
        - sensitive thread restrictions
    """

    @classmethod
    def can_view_thread(cls, *, user, website, thread) -> bool:
        """
        Return whether a user can view a thread.
        """
        if cls._has_platform_access(user=user):
            return cls._platform_staff_can_view(thread=thread, user=user)

        if thread.website_id != website.id:
            return False

        return cls._participant_can_view(
            user=user,
            website=website,
            thread=thread,
        )

    @classmethod
    def can_send_message(cls, *, user, website, thread) -> bool:
        """
        Return whether a user can send messages in a thread.
        """
        if thread.status != "open":
            return False

        if cls._has_platform_access(user=user):
            return cls._platform_staff_can_send(thread=thread, user=user)

        if thread.website_id != website.id:
            return False

        return CommunicationParticipant.objects.filter(
            website=website,
            thread=thread,
            user=user,
            can_view=True,
            can_send=True,
            removed_at__isnull=True,
        ).exists()

    @classmethod
    def enforce_can_view_thread(cls, *, user, website, thread) -> None:
        if not cls.can_view_thread(user=user, website=website, thread=thread):
            raise PermissionDenied("You cannot access this conversation.")

    @classmethod
    def enforce_can_send_message(cls, *, user, website, thread) -> None:
        if not cls.can_send_message(user=user, website=website, thread=thread):
            raise PermissionDenied("You cannot send messages in this thread.")

    @classmethod
    def _participant_can_view(cls, *, user, website, thread) -> bool:
        return CommunicationParticipant.objects.filter(
            website=website,
            thread=thread,
            user=user,
            can_view=True,
            removed_at__isnull=True,
        ).exists()

    @classmethod
    def _has_platform_access(cls, *, user) -> bool:
        if not user or not user.is_authenticated:
            return False

        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_support", False)
        )

    @classmethod
    def _platform_staff_can_view(cls, *, thread, user) -> bool:
        """
        Staff see everything except restricted sensitive threads.
        """
        if thread.kind != CommunicationThreadKind.SENSITIVE_COORDINATION:
            return True

        if getattr(user, "is_superuser", False):
            return True

        if getattr(user, "is_admin", False):
            return True

        return CommunicationParticipant.objects.filter(
            thread=thread,
            user=user,
            can_view=True,
            removed_at__isnull=True,
        ).exists()

    @classmethod
    def _platform_staff_can_send(cls, *, thread, user) -> bool:
        if thread.kind != CommunicationThreadKind.SENSITIVE_COORDINATION:
            return True

        return CommunicationParticipant.objects.filter(
            thread=thread,
            user=user,
            can_send=True,
            removed_at__isnull=True,
        ).exists()