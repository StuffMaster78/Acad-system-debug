from __future__ import annotations


class CommunicationEventRecipientService:
    """
    Resolve event recipients for communication events.
    """

    @staticmethod
    def active_thread_participant_ids(
        *,
        thread,
        exclude_user=None,
    ) -> list[int]:
        """
        Return active participant user IDs for a thread.
        """
        queryset = thread.participants.filter(
            can_view=True,
            removed_at__isnull=True,
        )

        if exclude_user is not None:
            queryset = queryset.exclude(user=exclude_user)

        return list(queryset.values_list("user_id", flat=True))

    @staticmethod
    def staff_recipient_ids_for_thread(
        *,
        thread,
    ) -> list[int]:
        """
        Placeholder for staff recipients.

        Replace with your real user/role selector once roles are centralized.
        """
        return list(
            thread.participants.filter(
                can_view=True,
                removed_at__isnull=True,
                role__in=[
                    "admin",
                    "superadmin",
                    "support",
                ],
            ).values_list("user_id", flat=True),
        )

    @staticmethod
    def message_created_recipients(
        *,
        message,
    ) -> list[int]:
        """
        Return recipients for message created event.
        """
        return CommunicationEventRecipientService.active_thread_participant_ids(
            thread=message.thread,
            exclude_user=message.sender,
        )
