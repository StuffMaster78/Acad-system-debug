from __future__ import annotations

import logging

from celery import shared_task

from writer_management.services.achievement_service import (
    AchievementService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def evaluate_writer_achievements_task(
    self,
    *,
    writer: str,
    website=None,
) -> None:
    """
    Evaluate achievements for a writer.
    """

    logger.info(
        "Evaluating achievements for writer=%s",
        writer,
    )

    AchievementService.evaluate_writer(
        writer=writer,
        website=website,
    )

    logger.info(
        "Completed achievement evaluation "
        "for writer=%s",
        writer,
    )