from __future__ import annotations

from celery import shared_task

from writer_compensation.services.reward_event_router import (
    RewardEventRouter,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def process_reward_event_task(
    self,
    *,
    event_key: str,
    payload: dict,
) -> None:
    """
    Route reward-related domain event.
    """

    RewardEventRouter.route(
        event_key=event_key,
        event_type="",
        payload=payload,
    )