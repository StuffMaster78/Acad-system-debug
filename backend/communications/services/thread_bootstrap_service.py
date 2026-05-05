from __future__ import annotations

from django.db import transaction

from communications.constants import CommunicationThreadKind
from communications.models.thread import CommunicationThread
from communications.services.thread_service import CommunicationThreadService


class CommunicationThreadBootstrapService:
    """
    Creates default communication threads for domain objects.
    """

    DEFAULT_THREAD_KINDS = (
        CommunicationThreadKind.CLIENT_SUPPORT,
        CommunicationThreadKind.CLIENT_WRITER,
        CommunicationThreadKind.WRITER_SUPPORT,
    )

    @staticmethod
    @transaction.atomic
    def bootstrap_for_target(
        *,
        target,
        created_by,
        website=None,
        thread_kinds: tuple[str, ...] | None = None,
    ) -> list[CommunicationThread]:
        """
        Create missing default threads for a target object.
        """
        kinds = thread_kinds or CommunicationThreadBootstrapService.DEFAULT_THREAD_KINDS
        threads: list[CommunicationThread] = []

        for thread_kind in kinds:
            thread = CommunicationThreadService.get_or_create_thread(
                target=target,
                thread_kind=thread_kind,
                created_by=created_by,
                website=website,
            )
            threads.append(thread)

        return threads

    @staticmethod
    def bootstrap_for_order(*, order, created_by) -> list[CommunicationThread]:
        """
        Create default order communication threads.
        """
        return CommunicationThreadBootstrapService.bootstrap_for_target(
            target=order,
            created_by=created_by,
            website=order.website,
            thread_kinds=(
                CommunicationThreadKind.CLIENT_SUPPORT,
                CommunicationThreadKind.CLIENT_WRITER,
                CommunicationThreadKind.WRITER_SUPPORT,
            ),
        )

    @staticmethod
    def bootstrap_for_class_order(
        *,
        class_order,
        created_by,
    ) -> list[CommunicationThread]:
        """
        Create default class communication threads.
        """
        return CommunicationThreadBootstrapService.bootstrap_for_target(
            target=class_order,
            created_by=created_by,
            website=class_order.website,
            thread_kinds=(
                CommunicationThreadKind.CLIENT_SUPPORT,
                CommunicationThreadKind.CLIENT_WRITER,
                CommunicationThreadKind.WRITER_SUPPORT,
                CommunicationThreadKind.SENSITIVE_COORDINATION,
            ),
        )

    @staticmethod
    def bootstrap_for_special_order(
        *,
        special_order,
        created_by,
    ) -> list[CommunicationThread]:
        """
        Create default special order communication threads.
        """
        return CommunicationThreadBootstrapService.bootstrap_for_target(
            target=special_order,
            created_by=created_by,
            website=special_order.website,
            thread_kinds=(
                CommunicationThreadKind.CLIENT_SUPPORT,
                CommunicationThreadKind.CLIENT_WRITER,
                CommunicationThreadKind.WRITER_SUPPORT,
                CommunicationThreadKind.SENSITIVE_COORDINATION,
            ),
        )