from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


@override_settings(ROOT_URLCONF="orders.api.urls")
class OrderCancellationAPITests(APITestCase):
    def setUp(self) -> None:
        self.api_client = APIClient()

        self.website = SimpleNamespace(pk=1)

        self.client_user = SimpleNamespace(
            pk=10,
            website=SimpleNamespace(pk=1),
            website_id=1,
            is_authenticated=True,
            is_staff=False,
        )
        self.staff_user = SimpleNamespace(
            pk=20,
            website=SimpleNamespace(pk=1),
            website_id=1,
            is_authenticated=True,
            is_staff=True,
        )
        self.foreign_user = SimpleNamespace(
            pk=30,
            website=SimpleNamespace(pk=999),
            website_id=999,
            is_authenticated=True,
            is_staff=False,
        )

        self.order = SimpleNamespace(
            pk=100,
            website=SimpleNamespace(pk=1),
            status="completed",
            cancelled_at=None,
            client=self.client_user,
            client_user=self.client_user,
        )

    @patch("orders.api.views.cancellation.order_cancellation_views.get_object_or_404")
    @patch(
        "orders.api.views.cancellation.order_cancellation_views."
        "OrderCancellationService.cancel_order"
    )
    def test_cancel_order_returns_success_for_client_owner(
        self,
        mock_cancel_order: Any,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.client_user)
        mock_get_object_or_404.return_value = self.order

        cancelled_order = SimpleNamespace(
            pk=100,
            status="cancelled",
            cancelled_at=None,
        )
        mock_cancel_order.return_value = cancelled_order

        response = self.api_client.post(
            reverse("order-cancel", kwargs={"order_id": 100}),
            data={
                "reason": "Client requested cancellation",
                "refund_destination": "wallet",
                "notes": "No longer needed",
            },
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = cast(dict[str, Any], response.json())
        self.assertEqual(
            payload["detail"],
            "Order cancelled successfully.",
        )
        self.assertEqual(payload["order_id"], 100)
        self.assertEqual(payload["status"], "cancelled")
        self.assertEqual(payload["refund_destination"], "wallet")

        mock_cancel_order.assert_called_once_with(
            order=self.order,
            cancelled_by=self.client_user,
            reason="Client requested cancellation",
            refund_destination="wallet",
            notes="No longer needed",
            triggered_by=self.client_user,
        )

    @patch("orders.api.views.cancellation.order_cancellation_views.get_object_or_404")
    @patch(
        "orders.api.views.cancellation.order_cancellation_views."
        "OrderCancellationService.cancel_order"
    )
    def test_cancel_order_returns_success_for_staff(
        self,
        mock_cancel_order: Any,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.staff_user)
        mock_get_object_or_404.return_value = self.order

        cancelled_order = SimpleNamespace(
            pk=100,
            status="cancelled",
            cancelled_at=None,
        )
        mock_cancel_order.return_value = cancelled_order

        response = self.api_client.post(
            reverse("order-cancel", kwargs={"order_id": 100}),
            data={
                "reason": "Ops cancellation",
                "refund_destination": "external_gateway",
            },
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = cast(dict[str, Any], response.json())
        self.assertEqual(payload["status"], "cancelled")
        self.assertEqual(
            payload["refund_destination"],
            "external_gateway",
        )

    def test_cancel_order_requires_authentication(self) -> None:
        response = self.api_client.post(
            reverse("order-cancel", kwargs={"order_id": 100}),
            data={
                "reason": "Client requested cancellation",
                "refund_destination": "wallet",
            },
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch("orders.api.views.cancellation.order_cancellation_views.get_object_or_404")
    def test_cancel_order_rejects_invalid_payload(
        self,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.client_user)
        mock_get_object_or_404.return_value = self.order

        response = self.api_client.post(
            reverse("order-cancel", kwargs={"order_id": 100}),
            data={
                "reason": "",
                "refund_destination": "banana",
            },
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payload = cast(dict[str, Any], response.json())
        self.assertIn("reason", payload)
        self.assertIn("refund_destination", payload)

    @patch("orders.api.views.cancellation.order_cancellation_views.get_object_or_404")
    def test_cancel_order_blocks_user_without_object_permission(
        self,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.foreign_user)
        mock_get_object_or_404.return_value = self.order

        response = self.api_client.post(
            reverse("order-cancel", kwargs={"order_id": 100}),
            data={
                "reason": "Should fail",
                "refund_destination": "wallet",
            },
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )