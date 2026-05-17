"""
Celery tasks for user state events.
"""

from celery import shared_task
from django.contrib.auth import get_user_model

from users_state.resolvers.user_state_resolver import UserStateResolver

from users_state.tasks.notifications import handle_notification_event
from users_state.tasks.audit import handle_audit_event
from users_state.tasks.analytics import handle_analytics_event

User = get_user_model()


@shared_task
def process_user_state_event(event_payload: dict):
    """
    Central async handler for all state events.

    This is the event bus entry point.
    """

    event_type = event_payload.get("type")
    user_id = event_payload.get("user_id")
    website = event_payload.get("website")
    reason = event_payload.get("reason")

    if event_type == "UserSuspended":
        _handle_user_suspended(user_id, website, reason)

    elif event_type == "UserBlacklisted":
        _handle_user_blacklisted(user_id, website, reason)

    elif event_type == "UserProbationStarted":
        _handle_user_probation(user_id, website, reason)

    # async side effects (NOW FIXED)
    handle_notification_event.delay(event_payload)
    handle_audit_event.delay(event_payload)
    handle_analytics_event.delay(event_payload)


def _handle_user_suspended(user_id, website_id, reason):
    user = User.objects.get(pk=user_id)

    UserStateResolver.get(user=user, website=website_id)

    print(f"SUSPENDED EVENT: {user_id} {reason}")


def _handle_user_blacklisted(user_id, website_id, reason):
    user = User.objects.get(pk=user_id)

    UserStateResolver.get(user=user, website=website_id)

    print(f"BLACKLIST EVENT: {user_id} {reason}")


def _handle_user_probation(user_id, website_id, reason):
    user = User.objects.get(pk=user_id)

    UserStateResolver.get(user=user, website=website_id)

    print(f"PROBATION EVENT: {user_id} {reason}")