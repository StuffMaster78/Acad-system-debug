from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.approval.order_approval_views import (
    ApproveOrderView,
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


class OrderApprovalAPITests(SimpleTestCase):
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
        self.staff_user = FakeUser(
            pk=20,
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
                "approved_at": None,
                "completed_at": None,
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
        "orders.api.views.approval.order_approval_views."
        "OrderApprovalService.approve_order"
    )
    @patch.object(ApproveOrderView, "_get_order_for_tenant")
    def test_client_can_approve_order(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        updated_order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "status": "completed",
                "approved_at": "2026-04-17T09:00:00Z",
                "completed_at": "2026-04-17T09:00:00Z",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = updated_order

        view = ApproveOrderView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/approve/",
            user=self.client_user,
        )

        with patch.object(
            ApproveOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["message"], "Order approved successfully.")
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["approved_at"], "2026-04-17T09:00:00Z")
        self.assertEqual(data["completed_at"], "2026-04-17T09:00:00Z")

        mock_service.assert_called_once_with(
            order=self.order,
            approved_by=self.client_user,
            triggered_by=self.client_user,
        )

    @patch(
        "orders.api.views.approval.order_approval_views."
        "OrderApprovalService.approve_order"
    )
    @patch.object(ApproveOrderView, "_get_order_for_tenant")
    def test_staff_can_approve_order(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        updated_order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "status": "completed",
                "approved_at": "2026-04-17T10:00:00Z",
                "completed_at": "2026-04-17T10:00:00Z",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = updated_order

        view = ApproveOrderView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/approve/",
            user=self.staff_user,
        )

        with patch.object(
            ApproveOrderView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "completed")

        mock_service.assert_called_once_with(
            order=self.order,
            approved_by=self.staff_user,
            triggered_by=self.staff_user,
        )

    @patch.object(ApproveOrderView, "_get_order_for_tenant")
    def test_approve_order_with_empty_payload_is_valid(
        self,
        mock_get_order: Any,
    ) -> None:
        updated_order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "status": "completed",
                "approved_at": "2026-04-17T11:00:00Z",
                "completed_at": "2026-04-17T11:00:00Z",
            },
        )()

        mock_get_order.return_value = self.order

        view = ApproveOrderView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/approve/",
            user=self.client_user,
            data={},
        )

        with patch.object(
            ApproveOrderView,
            "check_object_permissions",
            return_value=None,
        ), patch(
            "orders.api.views.approval.order_approval_views."
            "OrderApprovalService.approve_order",
            return_value=updated_order,
        ) as mock_service:
            response = cast(DRFResponse, view(request, order_id=100))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once()

    @patch.object(ApproveOrderView, "_get_order_for_tenant")
    def test_approve_order_denies_when_object_permissions_fail(
        self,
        mock_get_order: Any,
    ) -> None:
        mock_get_order.return_value = self.order

        view = ApproveOrderView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/approve/",
            user=self.client_user,
        )

        with patch.object(
            ApproveOrderView,
            "check_object_permissions",
            side_effect=PermissionError("forbidden"),
        ):
            with self.assertRaises(PermissionError):
                view(request, order_id=100)