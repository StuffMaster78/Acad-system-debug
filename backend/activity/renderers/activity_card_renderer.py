from __future__ import annotations

from typing import Any

from activity.models import ActivityEvent


class ActivityCardRenderer:
    """
    Converts activity events into frontend friendly cards.
    """

    @staticmethod
    def render(event: ActivityEvent) -> dict[str, Any]:
        """
        Render an activity event into a feed card payload.
        """
        return {
            "id": str(event.id),
            "verb": event.verb,
            "severity": event.severity,
            "title": event.title,
            "summary": event.summary,
            "metadata": event.metadata,
            "occurred_at": event.occurred_at.isoformat(),
            "actor": ActivityCardRenderer._render_actor(event),
            "target": ActivityCardRenderer._render_target(event),
            "subject": ActivityCardRenderer._render_subject(event),
        }

    @staticmethod
    def _render_actor(event: ActivityEvent) -> dict[str, Any] | None:
        """
        Render the activity actor.
        """
        actor = event.actor
        content_type = event.actor_content_type

        if actor is None or content_type is None:
            return None

        return {
            "type": content_type.model,
            "id": event.actor_object_id,
            "label": str(actor),
        }

    @staticmethod
    def _render_target(event: ActivityEvent) -> dict[str, Any]:
        """
        Render the activity target.
        """
        return {
            "type": event.target_content_type.model,
            "id": event.target_object_id,
            "label": str(event.target),
        }

    @staticmethod
    def _render_subject(event: ActivityEvent) -> dict[str, Any] | None:
        """
        Render the activity subject.
        """
        subject = event.subject
        content_type = event.subject_content_type

        if subject is None or content_type is None:
            return None

        return {
            "type": content_type.model,
            "id": event.subject_object_id,
            "label": str(subject),
        }