from __future__ import annotations

from celery import shared_task


@shared_task
def build_activity_digest_for_user(user_id: str) -> dict:
    """
    Build an activity digest for a user.

    This is intentionally a placeholder until digest rules are finalized.
    """
    return {
        "user_id": user_id,
        "events": [],
    }