from __future__ import annotations

from typing import Any, cast
from collections.abc import Sequence
from celery import Task

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model

from activity.constants import ActivityActorType
from activity.constants import ActivityAudience
from activity.constants import ActivitySeverity
from activity.constants import ActivityVerb
from activity.exceptions import InvalidActivityAudienceError
from activity.exceptions import InvalidActivityVerbError
from activity.models import ActivityEvent
from activity.realtime.publisher import ActivityRealtimePublisher
from activity.services.metadata_sanitizer import ActivityMetadataSanitizer
from activity.services.activity_notification_orchestrator import (
    ActivityNotificationOrchestrator,
)
from activity.tasks.notification_tasks import (
    dispatch_activity_notifications,
)


class ActivityService:
    """
    Writes canonical activity events.

    Domain apps should use this service instead of creating ActivityEvent
    rows directly. This keeps activity creation consistent across the
    platform.
    """

    @staticmethod
    @transaction.atomic
    def record_event(
        *,
        website,
        verb: str,
        target: Model,
        actor: Model | None = None,
        subject: Model | None = None,
        actor_type: str = ActivityActorType.SYSTEM,
        audiences: list[str] | None = None,
        severity: str = ActivitySeverity.INFO,
        title: str = "",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
        request_id: str = "",
        ip_address: str | None = None,
        user_agent: str = "",
        publish_realtime: bool = True,
    ) -> ActivityEvent:
        """
        Record a structured activity event.

        Args:
            website: Tenant that owns the event.
            verb: Canonical activity verb.
            target: Primary object affected by the event.
            actor: User or system object that caused the event.
            subject: Optional supporting object involved in the event.
            actor_type: Category of actor responsible for the event.
            audiences: Audience codes allowed to view the event.
            severity: Operational severity of the event.
            title: Short display title.
            summary: Optional human readable display summary.
            metadata: Structured non sensitive metadata.
            request_id: Optional request correlation id.
            ip_address: Optional request IP address.
            user_agent: Optional request user agent.
            publish_realtime: Whether to publish the event after creation.

        Returns:
            The created ActivityEvent.
        """
        ActivityService._validate_verb(verb=verb)
        ActivityService._validate_choice(
            value=actor_type,
            allowed_values=ActivityActorType.values,
            field_name="actor_type",
        )
        ActivityService._validate_choice(
            value=severity,
            allowed_values=ActivitySeverity.values,
            field_name="severity",
        )

        safe_audiences = audiences or [ActivityAudience.INTERNAL]
        ActivityService._validate_audiences(audiences=safe_audiences)

        target_type = ContentType.objects.get_for_model(
            target,
            for_concrete_model=False,
        )

        actor_type_obj = None
        actor_object_id = ""
        if actor is not None:
            actor_type_obj = ContentType.objects.get_for_model(
                actor,
                for_concrete_model=False,
            )
            actor_object_id = str(actor.pk)

        subject_type_obj = None
        subject_object_id = ""
        if subject is not None:
            subject_type_obj = ContentType.objects.get_for_model(
                subject,
                for_concrete_model=False,
            )
            subject_object_id = str(subject.pk)

        event = ActivityEvent.objects.create(
            website=website,
            verb=verb,
            actor_type=actor_type,
            actor_content_type=actor_type_obj,
            actor_object_id=actor_object_id,
            target_content_type=target_type,
            target_object_id=str(target.pk),
            subject_content_type=subject_type_obj,
            subject_object_id=subject_object_id,
            severity=severity,
            audiences=safe_audiences,
            title=title,
            summary=summary,
            metadata=ActivityMetadataSanitizer.sanitize(metadata),
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if publish_realtime:
            ActivityRealtimePublisher.publish(event=event)

        ActivityNotificationOrchestrator.handle_event(event=event)

        task = cast(Task, dispatch_activity_notifications)
        task.delay(str(event.id))

        return event

    @staticmethod
    def record_system_event(
        *,
        website,
        verb: str,
        target: Model,
        subject: Model | None = None,
        audiences: list[str] | None = None,
        severity: str = ActivitySeverity.INFO,
        title: str = "",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
        publish_realtime: bool = True,
    ) -> ActivityEvent:
        """
        Record an event caused by the system.
        """
        return ActivityService.record_event(
            website=website,
            verb=verb,
            target=target,
            subject=subject,
            actor=None,
            actor_type=ActivityActorType.SYSTEM,
            audiences=audiences,
            severity=severity,
            title=title,
            summary=summary,
            metadata=metadata,
            publish_realtime=publish_realtime,
        )

    @staticmethod
    def _validate_verb(*, verb: str) -> None:
        """
        Validate an activity verb.
        """
        if verb not in ActivityVerb.values:
            raise InvalidActivityVerbError(
                f"Invalid activity verb: {verb}",
            )

    @staticmethod
    def _validate_choice(
        *,
        value: str,
        allowed_values: Sequence[str],
        field_name: str,
    ) -> None:
        """
        Validate that a value belongs to an allowed choices collection.
        """
        allowed = {str(item) for item in allowed_values}

        if value not in allowed:
            raise ValueError(f"Invalid activity {field_name}: {value}")

    @staticmethod
    def _validate_audiences(*, audiences: list[str]) -> None:
        """
        Validate activity audience values.
        """
        invalid = set(audiences) - set(ActivityAudience.values)

        if invalid:
            invalid_values = ", ".join(sorted(invalid))
            raise InvalidActivityAudienceError(
                f"Invalid activity audiences: {invalid_values}",
            )