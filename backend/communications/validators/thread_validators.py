from __future__ import annotations

from django.core.exceptions import ValidationError


class CommunicationThreadValidator:
    """
    Validators for communication threads.
    """

    @staticmethod
    def validate_thread_website(*, thread, website) -> None:
        """
        Validate thread belongs to website.
        """
        if thread.website_id != website.id:
            raise ValidationError(
                "Thread website does not match request website.",
            )

    @staticmethod
    def validate_thread_is_open(*, thread) -> None:
        """
        Validate thread is open.
        """
        if thread.status != "open":
            raise ValidationError("This conversation is not open.")

    @staticmethod
    def validate_target_exists(*, target) -> None:
        """
        Validate target object exists.
        """
        if target is None:
            raise ValidationError("Communication target does not exist.")