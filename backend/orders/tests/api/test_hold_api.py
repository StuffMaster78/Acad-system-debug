from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.holds.hold_views import (
    HoldActivateView,
    HoldCancelView,
    HoldReleaseView,
    HoldRequestView,
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


class HoldAPITests(SimpleTestCase):
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
                "status": "in_progress",
            },
        )()

        self.hold = type(
            "HoldStub",
            (),
            {
                "pk": 200,
                "website": self.website,
                "order": self.order,
                "requested_by": self.writer_user,
                "status": "pending",
                "remaining_seconds": None,
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
        "orders.api.views.holds.hold_views."
        "OrderHoldService.request_hold"
    )
    @patch.object(HoldRequestView, "_get_order_for_tenant")
    def test_hold_request(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        created_hold = type(
            "HoldStub",
            (),
            {
                "pk": 201,
                "status": "pending",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = created_hold

        view = HoldRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/holds/",
            user=self.writer_user,
            data={
                "reason": "Waiting for client clarification",
                "internal_notes": "Need instructions on section 3",
            },
        )

        with patch.object(
            HoldRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["hold_id"], 201)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "pending")
        mock_service.assert_called_once_with(
            order=self.order,
            requested_by=self.writer_user,
            reason="Waiting for client clarification",
            internal_notes="Need instructions on section 3",
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.holds.hold_views."
        "OrderHoldService.activate_hold"
    )
    @patch.object(HoldActivateView, "_get_hold_for_tenant")
    def test_hold_activate(
        self,
        mock_get_hold: Any,
        mock_service: Any,
    ) -> None:
        activated_hold = type(
            "HoldStub",
            (),
            {
                "pk": 200,
                "status": "active",
                "order": self.order,
                "remaining_seconds": 7200,
            },
        )()

        mock_get_hold.return_value = self.hold
        mock_service.return_value = activated_hold

        view = HoldActivateView.as_view()
        request = self._auth_post(
            path="/api/orders/holds/200/activate/",
            user=self.staff_user,
            data={
                "remaining_seconds": 7200,
                "internal_notes": "Approved temporary hold",
            },
        )

        with patch.object(
            HoldActivateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, hold_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["hold_id"], 200)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["remaining_seconds"], 7200)
        mock_service.assert_called_once_with(
            hold=self.hold,
            activated_by=self.staff_user,
            remaining_seconds=7200,
            internal_notes="Approved temporary hold",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.holds.hold_views."
        "OrderHoldService.release_hold"
    )
    @patch.object(HoldReleaseView, "_get_hold_for_tenant")
    def test_hold_release(
        self,
        mock_get_hold: Any,
        mock_service: Any,
    ) -> None:
        updated_order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "status": "in_progress",
            },
        )()

        mock_get_hold.return_value = self.hold
        mock_service.return_value = updated_order

        view = HoldReleaseView.as_view()
        request = self._auth_post(
            path="/api/orders/holds/200/release/",
            user=self.staff_user,
            data={
                "internal_notes": "Client responded, resume work",
            },
        )

        with patch.object(
            HoldReleaseView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, hold_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "in_progress")
        mock_service.assert_called_once_with(
            hold=self.hold,
            released_by=self.staff_user,
            internal_notes="Client responded, resume work",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.holds.hold_views."
        "OrderHoldService.cancel_hold_request"
    )
    @patch.object(HoldCancelView, "_get_hold_for_tenant")
    def test_hold_cancel(
        self,
        mock_get_hold: Any,
        mock_service: Any,
    ) -> None:
        cancelled_hold = type(
            "HoldStub",
            (),
            {
                "pk": 200,
                "status": "cancelled",
            },
        )()

        mock_get_hold.return_value = self.hold
        mock_service.return_value = cancelled_hold

        view = HoldCancelView.as_view()
        request = self._auth_post(
            path="/api/orders/holds/200/cancel/",
            user=self.writer_user,
            data={
                "internal_notes": "No longer needed",
            },
        )

        with patch.object(
            HoldCancelView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, hold_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["hold_id"], 200)
        self.assertEqual(data["status"], "cancelled")
        mock_service.assert_called_once_with(
            hold=self.hold,
            cancelled_by=self.writer_user,
            internal_notes="No longer needed",
            triggered_by=self.writer_user,
        )

    def test_hold_request_requires_reason(self) -> None:
        view = HoldRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/holds/",
            user=self.writer_user,
            data={},
        )

        with patch.object(
            HoldRequestView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            HoldRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_hold_activate_requires_remaining_seconds(self) -> None:
        view = HoldActivateView.as_view()
        request = self._auth_post(
            path="/api/orders/holds/200/activate/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            HoldActivateView,
            "_get_hold_for_tenant",
            return_value=self.hold,
        ), patch.object(
            HoldActivateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, hold_id=200))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("remaining_seconds", data)