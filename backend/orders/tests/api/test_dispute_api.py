from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.disputes.dispute_views import (
    DisputeCloseView,
    DisputeEscalateView,
    DisputeOpenView,
    DisputeResolveView,
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
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class DisputeAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

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

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "client": self.client_user,
                "status": "submitted",
            },
        )()

        self.dispute = type(
            "DisputeStub",
            (),
            {
                "pk": 200,
                "website": self.website,
                "order": self.order,
                "opened_by": self.client_user,
                "status": "open",
            },
        )()

    def _auth_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any] | None = None,
    ) -> Request:
        request = self.factory.post(path, data or {}, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.disputes.dispute_views."
        "DisputeOrchestrationService.open_dispute"
    )
    @patch.object(DisputeOpenView, "_get_order_for_tenant")
    def test_open_dispute(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        created_dispute = type(
            "DisputeStub",
            (),
            {
                "pk": 201,
                "status": "open",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = created_dispute

        view = DisputeOpenView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/disputes/",
            user=self.client_user,
            data={
                "reason": "wrong_file_uploaded",
                "summary": "The uploaded file is not mine.",
            },
        )

        with patch.object(
            DisputeOpenView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["dispute_id"], 201)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "open")
        mock_service.assert_called_once_with(
            order=self.order,
            opened_by=self.client_user,
            reason="wrong_file_uploaded",
            summary="The uploaded file is not mine.",
            triggered_by=self.client_user,
        )

    @patch(
        "orders.api.views.disputes.dispute_views."
        "DisputeOrchestrationService.escalate_dispute"
    )
    @patch.object(DisputeEscalateView, "_get_dispute_for_tenant")
    def test_escalate_dispute(
        self,
        mock_get_dispute: Any,
        mock_service: Any,
    ) -> None:
        escalated_dispute = type(
            "DisputeStub",
            (),
            {
                "pk": 200,
                "status": "escalated",
            },
        )()

        mock_get_dispute.return_value = self.dispute
        mock_service.return_value = escalated_dispute

        view = DisputeEscalateView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/escalate/",
            user=self.staff_user,
            data={
                "notes": "Escalating to senior support.",
            },
        )

        with patch.object(
            DisputeEscalateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["dispute_id"], 200)
        self.assertEqual(data["status"], "escalated")
        mock_service.assert_called_once_with(
            dispute=self.dispute,
            escalated_by=self.staff_user,
            notes="Escalating to senior support.",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.disputes.dispute_views."
        "DisputeOrchestrationService.resolve_dispute"
    )
    @patch.object(DisputeResolveView, "_get_dispute_for_tenant")
    def test_resolve_dispute(
        self,
        mock_get_dispute: Any,
        mock_service: Any,
    ) -> None:
        resolution = type(
            "ResolutionStub",
            (),
            {
                "pk": 300,
            },
        )()

        mock_get_dispute.return_value = self.dispute
        mock_service.return_value = resolution

        view = DisputeResolveView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/resolve/",
            user=self.staff_user,
            data={
                "outcome": "reopen_order",
                "resolution_summary": "Writer should correct and resubmit.",
                "internal_notes": "Valid complaint after review.",
            },
        )

        with patch.object(
            DisputeResolveView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["resolution_id"], 300)
        self.assertEqual(data["dispute_id"], 200)
        mock_service.assert_called_once_with(
            dispute=self.dispute,
            resolved_by=self.staff_user,
            outcome="reopen_order",
            resolution_summary="Writer should correct and resubmit.",
            internal_notes="Valid complaint after review.",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.disputes.dispute_views."
        "DisputeOrchestrationService.close_dispute"
    )
    @patch.object(DisputeCloseView, "_get_dispute_for_tenant")
    def test_close_dispute(
        self,
        mock_get_dispute: Any,
        mock_service: Any,
    ) -> None:
        closed_dispute = type(
            "DisputeStub",
            (),
            {
                "pk": 200,
                "status": "closed",
            },
        )()

        mock_get_dispute.return_value = self.dispute
        mock_service.return_value = closed_dispute

        view = DisputeCloseView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/close/",
            user=self.staff_user,
            data={
                "restore_order_status": "in_progress",
            },
        )

        with patch.object(
            DisputeCloseView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["dispute_id"], 200)
        self.assertEqual(data["status"], "closed")
        mock_service.assert_called_once_with(
            dispute=self.dispute,
            closed_by=self.staff_user,
            restore_order_status="in_progress",
            triggered_by=self.staff_user,
        )

    def test_open_dispute_requires_reason(self) -> None:
        view = DisputeOpenView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/disputes/",
            user=self.client_user,
            data={
                "summary": "Missing reason field.",
            },
        )

        with patch.object(
            DisputeOpenView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            DisputeOpenView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_open_dispute_requires_summary(self) -> None:
        view = DisputeOpenView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/disputes/",
            user=self.client_user,
            data={
                "reason": "wrong_file_uploaded",
            },
        )

        with patch.object(
            DisputeOpenView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            DisputeOpenView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("summary", data)

    def test_resolve_dispute_requires_outcome(self) -> None:
        view = DisputeResolveView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/resolve/",
            user=self.staff_user,
            data={
                "resolution_summary": "Missing outcome.",
            },
        )

        with patch.object(
            DisputeResolveView,
            "_get_dispute_for_tenant",
            return_value=self.dispute,
        ), patch.object(
            DisputeResolveView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("outcome", data)

    def test_resolve_dispute_requires_resolution_summary(self) -> None:
        view = DisputeResolveView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/resolve/",
            user=self.staff_user,
            data={
                "outcome": "reopen_order",
            },
        )

        with patch.object(
            DisputeResolveView,
            "_get_dispute_for_tenant",
            return_value=self.dispute,
        ), patch.object(
            DisputeResolveView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("resolution_summary", data)

    def test_close_dispute_requires_restore_order_status(self) -> None:
        view = DisputeCloseView.as_view()
        request = self._auth_post(
            path="/api/orders/disputes/200/close/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            DisputeCloseView,
            "_get_dispute_for_tenant",
            return_value=self.dispute,
        ), patch.object(
            DisputeCloseView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, dispute_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("restore_order_status", data)