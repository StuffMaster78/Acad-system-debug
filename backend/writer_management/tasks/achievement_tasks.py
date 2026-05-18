from __future__ import annotations

import logging

from celery import shared_task

from writer_management.models.writer_profile import (
    WriterProfile,
)
from writer_management.services.achievement_service import (
    AchievementService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def evaluate_writer_achievements_task(
    self,
    *,
    writer_id: int,
) -> None:
    """
    Evaluate achievements for one writer.
    """

    writer = WriterProfile.objects.get(
        pk=writer_id,
    )

    AchievementService.evaluate_writer(
        writer=writer,
        website=website,
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def evaluate_all_writer_achievements_task(
    self,
) -> None:
    """
    Batch achievement evaluation.
    """

    writers = (
        WriterProfile.objects
        .filter(
            is_active=True,
        )
        .only("id")
    )

    for writer in writers:
        AchievementService.evaluate_writer(
            writer=writer,
            website=website,
        )

    logger.info(
        "Completed global achievement evaluation.",
    )