from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from typing import cast
from django.http import HttpRequest

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client(user, website):
    """
    API client with authenticated user and website injected.
    """
    client = APIClient()
    client.force_authenticate(user=user)

    # attach website via request hook
    original = client.request

    def request_with_website(*args, **kwargs):
        request = original(*args, **kwargs)

        req = cast(HttpRequest, request)
        setattr(req, "website", website)

        return req

    client.request = request_with_website # type: ignore[method-assign]

    return client


def test_feed_list(api_client, activity_event):
    response = api_client.get("/activity/feed/")

    assert response.status_code == 200
    assert isinstance(response.data, list)


def test_mark_read_endpoint(api_client, activity_event):
    response = api_client.post(
        f"/activity/feed/{activity_event.id}/mark-read/",
    )

    assert response.status_code == 204