from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.drafts.draft_views import (
    ReviewDraftView,
    SubmitDraftView,
)


class FakeUser:
    def __init__(self, *, pk: int, website: Any, is_staff: bool = False) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.is_staff = is_staff
        self.is_authenticated = True


class FakeAssignmentsManager:
    def __init__(self, writer: Any | None) -> None:
        self.writer = writer

    def filter(self, **kwargs: Any) -> "FakeAssignmentsManager":
        return self

    def first(self) -> Any | None:
        if self.writer is None:
            return None
        return SimpleNamespace(writer=self.writer)


class DraftAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.writer = FakeUser(pk=1, website=self.website)
        self.staff = FakeUser(pk=2, website=self.website, is_staff=True)
        self.client_user = FakeUser(pk=3, website=self.website)

    def _post(self, *, path: str, user: FakeUser, data: dict[str, Any]) -> Request:
        request = self.factory.post(path, data, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @patch("orders.api.views.drafts.draft_views.DraftService.submit_draft")
    @patch("orders.api.views.drafts.draft_views.get_object_or_404")
    def test_writer_can_submit_draft(
        self,
        mock_get_object: Any,
        mock_submit: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            assignments=FakeAssignmentsManager(self.writer),
            preferred_writer=None,
        )
        draft = SimpleNamespace(pk=9, status="submitted")
        mock_get_object.return_value = order
        mock_submit.return_value = draft

        view = SubmitDraftView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    path="/orders/100/drafts/submit/",
                    user=self.writer,
                    data={"note": "Draft ready."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_submit.assert_called_once()

    @patch("orders.api.views.drafts.draft_views.get_object_or_404")
    def test_client_cannot_submit_draft(
        self,
        mock_get_object: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            assignments=FakeAssignmentsManager(self.writer),
            preferred_writer=None,
        )
        mock_get_object.return_value = order

        view = SubmitDraftView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    path="/orders/100/drafts/submit/",
                    user=self.client_user,
                    data={"note": "Trying."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("orders.api.views.drafts.draft_views.DraftService.review_draft")
    @patch("orders.api.views.drafts.draft_views.get_object_or_404")
    def test_staff_can_review_draft(
        self,
        mock_get_object: Any,
        mock_review: Any,
    ) -> None:
        draft = SimpleNamespace(pk=8, status="submitted")
        mock_get_object.return_value = draft
        mock_review.return_value = SimpleNamespace(pk=8, status="reviewed")

        view = ReviewDraftView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    path="/drafts/8/review/",
                    user=self.staff,
                    data={"approve": True},
                ),
                draft_id=8,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_review.assert_called_once()

    def test_review_draft_requires_approve_field(self) -> None:
        view = ReviewDraftView.as_view()

        response = cast(
            DRFResponse,
            view(
                self._post(
                    path="/drafts/8/review/",
                    user=self.staff,
                    data={},
                ),
                draft_id=8,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)