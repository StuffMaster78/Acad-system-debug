import pytest

from activity.constants import ActivityAudience
from activity.selectors.event_selectors import (
    ActivityEventSelector,
)

pytestmark = pytest.mark.django_db


def test_user_can_view_event(activity_event, user):
    activity_event.audiences = [ActivityAudience.CLIENT]
    activity_event.save()

    assert ActivityEventSelector.user_can_view(
        event=activity_event,
        user=user,
    )


def test_user_cannot_view_event(activity_event, user):
    activity_event.audiences = [ActivityAudience.STAFF]
    activity_event.save()

    assert not ActivityEventSelector.user_can_view(
        event=activity_event,
        user=user,
    )