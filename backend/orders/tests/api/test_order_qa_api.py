from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.qa.order_qa_views import (
    ApproveOrderForClientDeliveryView,
    ReturnOrderToWriterView,
    SubmitOrderForQAView,
)


class FakeUser:
    def __init__(
        self,
        *,
        pk: int,
        website: Any,
        is_staff: bool = False,
    ) -> None:
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


class OrderQAAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.writer = FakeUser(pk=1, website=self.website)
        self.staff = FakeUser(
            pk=2,
            website=self.website,
            is_staff=True,
        )
        self.client_user = FakeUser(pk=3, website=self.website)

    def _auth_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any],
    ) -> Request:
        request = self.factory.post(path, data, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _response_data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.qa.order_qa_views."
        "OrderQAReviewService.submit_for_qa"
    )
    @patch("orders.api.views.qa.order_qa_views.get_object_or_404")
    def test_writer_can_submit_order_for_qa(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            status="in_progress",
            assignments=FakeAssignmentsManager(self.writer),
            preferred_writer=None,
        )
        mock_get_object.return_value = order
        mock_service.return_value = SimpleNamespace(
            pk=100,
            status="qa_review",
        )

        view = SubmitOrderForQAView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._auth_post(
                    path="/orders/100/qa/submit/",
                    user=self.writer,
                    data={"note": "Ready for QA."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self._response_data(response)
        self.assertEqual(data["status"], "qa_review")
        mock_service.assert_called_once()

    @patch("orders.api.views.qa.order_qa_views.get_object_or_404")
    def test_client_cannot_submit_order_for_qa(
        self,
        mock_get_object: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            status="in_progress",
            assignments=FakeAssignmentsManager(self.writer),
            preferred_writer=None,
        )
        mock_get_object.return_value = order

        view = SubmitOrderForQAView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._auth_post(
                    path="/orders/100/qa/submit/",
                    user=self.client_user,
                    data={"note": "Trying."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "orders.api.views.qa.order_qa_views."
        "OrderQAReviewService.approve_for_client_delivery"
    )
    @patch("orders.api.views.qa.order_qa_views.get_object_or_404")
    def test_staff_can_approve_order_for_client_delivery(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            status="qa_review",
        )
        mock_get_object.return_value = order
        mock_service.return_value = SimpleNamespace(
            pk=100,
            status="submitted",
        )

        view = ApproveOrderForClientDeliveryView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._auth_post(
                    path="/orders/100/qa/approve/",
                    user=self.staff,
                    data={"note": "Approved."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self._response_data(response)
        self.assertEqual(data["status"], "submitted")
        mock_service.assert_called_once()

    @patch("orders.api.views.qa.order_qa_views.get_object_or_404")
    def test_non_staff_cannot_approve_order_for_client_delivery(
        self,
        mock_get_object: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            status="qa_review",
        )
        mock_get_object.return_value = order

        view = ApproveOrderForClientDeliveryView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._auth_post(
                    path="/orders/100/qa/approve/",
                    user=self.writer,
                    data={"note": "Approved."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "orders.api.views.qa.order_qa_views."
        "OrderQAReviewService.return_to_writer"
    )
    @patch("orders.api.views.qa.order_qa_views.get_object_or_404")
    def test_staff_can_return_order_to_writer(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            status="qa_review",
        )
        mock_get_object.return_value = order
        mock_service.return_value = SimpleNamespace(
            pk=100,
            status="in_progress",
        )

        view = ReturnOrderToWriterView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._auth_post(
                    path="/orders/100/qa/return/",
                    user=self.staff,
                    data={"reason": "Fix formatting."},
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self._response_data(response)
        self.assertEqual(data["status"], "in_progress")
        mock_service.assert_called_once()

    def test_return_order_to_writer_requires_reason(self) -> None:
        view = ReturnOrderToWriterView.as_view()

        with patch(
            "orders.api.views.qa.order_qa_views.get_object_or_404"
        ) as mock_get_object:
            mock_get_object.return_value = SimpleNamespace(
                pk=100,
                website=self.website,
                status="qa_review",
            )

            response = cast(
                DRFResponse,
                view(
                    self._auth_post(
                        path="/orders/100/qa/return/",
                        user=self.staff,
                        data={},
                    ),
                    order_id=100,
                ),
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)