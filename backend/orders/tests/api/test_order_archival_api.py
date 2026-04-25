from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


@override_settings(ROOT_URLCONF="orders.api.urls")
class OrderArchivalAPITests(APITestCase):
    def setUp(self) -> None:
        self.api_client = APIClient()

        self.staff_user = SimpleNamespace(
            pk=20,
            website=SimpleNamespace(pk=1),
            website_id=1,
            is_authenticated=True,
            is_staff=True,
        )
        self.client_user = SimpleNamespace(
            pk=10,
            website=SimpleNamespace(pk=1),
            website_id=1,
            is_authenticated=True,
            is_staff=False,
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
            archived_at=None,
            client=self.client_user,
            client_user=self.client_user,
        )

    @patch("orders.api.views.archival.order_archival_views.get_object_or_404")
    @patch(
        "orders.api.views.archival.order_archival_views."
        "OrderArchivalService.archive_order"
    )
    def test_archive_order_returns_success_for_staff(
        self,
        mock_archive_order: Any,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.staff_user)
        mock_get_object_or_404.return_value = self.order

        archived_order = SimpleNamespace(
            pk=100,
            status="archived",
            archived_at=None,
        )
        mock_archive_order.return_value = archived_order

        response = self.api_client.post(
            reverse("order-archive", kwargs={"order_id": 100}),
            data={"reason": "Retention cleanup"},
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payload = cast(dict[str, Any], response.json())
        self.assertEqual(
            payload["detail"],
            "Order archived successfully.",
        )
        self.assertEqual(payload["order_id"], 100)
        self.assertEqual(payload["status"], "archived")

        mock_archive_order.assert_called_once_with(
            order=self.order,
            archived_by=self.staff_user,
            triggered_by=self.staff_user,
            reason="Retention cleanup",
        )

    def test_archive_order_requires_authentication(self) -> None:
        response = self.api_client.post(
            reverse("order-archive", kwargs={"order_id": 100}),
            data={"reason": "Retention cleanup"},
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch("orders.api.views.archival.order_archival_views.get_object_or_404")
    def test_archive_order_blocks_non_staff_user(
        self,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.client_user)
        mock_get_object_or_404.return_value = self.order

        response = self.api_client.post(
            reverse("order-archive", kwargs={"order_id": 100}),
            data={"reason": "Should fail"},
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    @patch("orders.api.views.archival.order_archival_views.get_object_or_404")
    def test_archive_order_blocks_cross_tenant_user(
        self,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.foreign_user)
        mock_get_object_or_404.return_value = self.order

        response = self.api_client.post(
            reverse("order-archive", kwargs={"order_id": 100}),
            data={"reason": "Should fail"},
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    @patch("orders.api.views.archival.order_archival_views.get_object_or_404")
    @patch(
        "orders.api.views.archival.order_archival_views."
        "OrderArchivalService.archive_order"
    )
    def test_archive_order_allows_empty_reason(
        self,
        mock_archive_order: Any,
        mock_get_object_or_404: Any,
    ) -> None:
        self.api_client.force_authenticate(user=self.staff_user)
        mock_get_object_or_404.return_value = self.order

        archived_order = SimpleNamespace(
            pk=100,
            status="archived",
            archived_at=None,
        )
        mock_archive_order.return_value = archived_order

        response = self.api_client.post(
            reverse("order-archive", kwargs={"order_id": 100}),
            data={},
            format="json",
        )
        response = cast(Any, response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_archive_order.assert_called_once_with(
            order=self.order,
            archived_by=self.staff_user,
            triggered_by=self.staff_user,
            reason="",
        )