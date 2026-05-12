from __future__ import annotations

import pytest

from activity.permissions import CanViewActivityEvent

pytestmark = pytest.mark.django_db


def test_permission_allows_authenticated(user):
    """
    Authenticated users should pass has_permission.
    """
    perm = CanViewActivityEvent()

    class DummyReq:
        def __init__(self, user):
            self.user = user

    request = DummyReq(user)

    assert perm.has_permission(request, None)


def test_object_permission_blocks_wrong_website(
    activity_event,
    user,
):
    """
    Event should not be visible if website does not match.
    """
    perm = CanViewActivityEvent()

    class Req:
        def __init__(self, user):
            self.user = user
            self.website = type("W", (), {"id": "wrong"})()

    request = Req(user)

    assert not perm.has_object_permission(
        request,
        None,
        activity_event,
    )