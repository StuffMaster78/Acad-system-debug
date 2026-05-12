import pytest

from activity.services.feed_state_service import (
    ActivityFeedStateService,
)

pytestmark = pytest.mark.django_db


def test_mark_read(activity_event, user):
    state = ActivityFeedStateService.mark_read(
        event=activity_event,
        user=user,
    )

    assert state.is_read is True
    assert state.read_at is not None


def test_dismiss(activity_event, user):
    state = ActivityFeedStateService.dismiss(
        event=activity_event,
        user=user,
    )

    assert state.is_dismissed is True