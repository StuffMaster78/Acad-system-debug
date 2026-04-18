from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.submissions.submission_views import (
    CompleteOrderView,
    ReopenOrderView,
    SubmitOrderView,
)


class FakeUser:
    """
    Lightweight authenticated user test double.

    This is only for API view unit tests where we mock the underlying
    service layer and do not need a database-backed Django user model.
    """

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
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class SubmissionAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        self.website = SimpleNamespace(pk=1)

        self.client_user = FakeUser(
            pk=10,
            website=self.website,
            is_staff=False,
        )
        self.writer_user = FakeUser(
            pk=20,
            website=self.website,
            is_staff=False,
        )
        self.staff_user = FakeUser(
            pk=30,
            website=self.website,
            is_staff=True,
        )

        self.order = SimpleNamespace(
            pk=100,
            website=self.website,
            client=self.client_user,
            status="in_progress",
            submitted_at=None,
            completed_at=None,
        )

    def _authenticated_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any] | None = None,
    ) -> Request:
        """
        Build an authenticated DRF request for unit testing.
        """
        request = self.factory.post(
            path,
            data or {},
            format="json",
        )
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _response_data(response: DRFResponse) -> dict[str, Any]:
        """
        Return typed response data for assertions.
        """
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.submissions.submission_views."
        "OrderSubmissionService.submit_order"
    )
    @patch.object(SubmitOrderView, "_get_order_for_tenant")
    def test_submit_order_view_returns_200(
        self,
        mock_get_order: Any,
        mock_submit_order: Any,
    ) -> None:
        updated_order = SimpleNamespace(
            pk=100,
            status="submitted",
            submitted_at="2026-04-16T10:00:00Z",
        )
        mock_get_order.return_value = self.order
        mock_submit_order.return_value = updated_order

        view = SubmitOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/submit/",
            user=self.writer_user,
        )

        with patch.object(
            SubmitOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data["message"],
            "Order submitted successfully.",
        )
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "submitted")

        mock_submit_order.assert_called_once_with(
            order=self.order,
            submitted_by=self.writer_user,
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.submissions.submission_views."
        "OrderSubmissionService.complete_order"
    )
    @patch.object(CompleteOrderView, "_get_order_for_tenant")
    def test_complete_order_view_returns_200(
        self,
        mock_get_order: Any,
        mock_complete_order: Any,
    ) -> None:
        updated_order = SimpleNamespace(
            pk=100,
            status="completed",
            completed_at="2026-04-16T10:30:00Z",
        )
        mock_get_order.return_value = self.order
        mock_complete_order.return_value = updated_order

        view = CompleteOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/complete/",
            user=self.client_user,
            data={
                "internal_reason": "client_accepted",
            },
        )

        with patch.object(
            CompleteOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data["message"],
            "Order completed successfully.",
        )
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "completed")

        mock_complete_order.assert_called_once_with(
            order=self.order,
            completed_by=self.client_user,
            triggered_by=self.client_user,
            internal_reason="client_accepted",
        )

    @patch(
        "orders.api.views.submissions.submission_views."
        "OrderSubmissionService.reopen_order"
    )
    @patch.object(ReopenOrderView, "_get_order_for_tenant")
    def test_reopen_order_view_returns_200(
        self,
        mock_get_order: Any,
        mock_reopen_order: Any,
    ) -> None:
        updated_order = SimpleNamespace(
            pk=100,
            status="in_progress",
        )
        mock_get_order.return_value = self.order
        mock_reopen_order.return_value = updated_order

        view = ReopenOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/reopen/",
            user=self.staff_user,
            data={
                "reason": "Client identified issues",
            },
        )

        with patch.object(
            ReopenOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data["message"],
            "Order reopened successfully.",
        )
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "in_progress")

        mock_reopen_order.assert_called_once_with(
            order=self.order,
            reopened_by=self.staff_user,
            reason="Client identified issues",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.submissions.submission_views."
        "OrderSubmissionService.submit_order"
    )
    @patch.object(SubmitOrderView, "_get_order_for_tenant")
    def test_submit_order_view_allows_empty_payload(
        self,
        mock_get_order: Any,
        mock_submit_order: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_submit_order.return_value = SimpleNamespace(
            pk=100,
            status="submitted",
            submitted_at="2026-04-16T10:00:00Z",
        )

        view = SubmitOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/submit/",
            user=self.writer_user,
        )

        with patch.object(
            SubmitOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_submit_order.assert_called_once()

    @patch(
        "orders.api.views.submissions.submission_views."
        "OrderSubmissionService.complete_order"
    )
    @patch.object(CompleteOrderView, "_get_order_for_tenant")
    def test_complete_order_view_allows_empty_internal_reason(
        self,
        mock_get_order: Any,
        mock_complete_order: Any,
    ) -> None:
        mock_get_order.return_value = self.order
        mock_complete_order.return_value = SimpleNamespace(
            pk=100,
            status="completed",
            completed_at="2026-04-16T10:30:00Z",
        )

        view = CompleteOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/complete/",
            user=self.client_user,
        )

        with patch.object(
            CompleteOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_complete_order.assert_called_once_with(
            order=self.order,
            completed_by=self.client_user,
            triggered_by=self.client_user,
            internal_reason="",
        )

    def test_reopen_order_view_rejects_missing_reason(self) -> None:
        view = ReopenOrderView.as_view()
        request = self._authenticated_post(
            path="/api/orders/orders/100/reopen/",
            user=self.staff_user,
        )

        response = cast(DRFResponse, view(request, order_id=100))
        data = self._response_data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)