import pytest

from activity.api.filters import ActivityEventFilter

pytestmark = pytest.mark.django_db


def test_filter_by_time_range(activity_event, user, rf):
    request = rf.get("/activity/")
    request.user = user

    f = ActivityEventFilter(
        data={"time_range": "today"},
        queryset=type(activity_event).objects.all(),
        request=request,
    )

    qs = f.qs

    assert activity_event in qs