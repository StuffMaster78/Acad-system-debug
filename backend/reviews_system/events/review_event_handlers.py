from reviews_system.events.review_event_types import ReviewEventType


class ReviewEventHandlers:
    """
    Handles side effects for review events.

    IMPORTANT:
        This layer should NOT contain business logic.
        Only orchestration (notifications, reputation triggers).
    """

    @staticmethod
    def handle(event: dict) -> None:
        """
        Dispatch event to correct handler.
        """

        event_type = event.get("event_type")

        if event_type == ReviewEventType.APPROVED:
            ReviewEventHandlers._on_approved(event)

        elif event_type == ReviewEventType.SHADOWED:
            ReviewEventHandlers._on_shadowed(event)

        elif event_type == ReviewEventType.CREATED:
            ReviewEventHandlers._on_created(event)

    @staticmethod
    def _on_created(event: dict) -> None:
        """Handle review created event."""
        pass

    @staticmethod
    def _on_approved(event: dict) -> None:
        """Handle review approved event."""
        pass

    @staticmethod
    def _on_shadowed(event: dict) -> None:
        """Handle review shadowed event."""
        pass