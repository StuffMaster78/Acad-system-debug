from __future__ import annotations

from dataclasses import asdict
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.dashboard.order_ops_dashboard_views import (
    OrderOpsDashboardSummaryView,
    OrderOpsQueueView,
)
from orders.selectors.order_ops_selector import OrderOpsDashboardCounts


class FakeUser:
    def __init__(
        self,
        *,
        pk: int,
        website: Any,
        is_staff: bool,
    ) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class OrderOpsDashboardAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.staff_user = FakeUser(
            pk=1,
            website=self.website,
            is_staff=True,
        )
        self.non_staff_user = FakeUser(
            pk=2,
            website=self.website,
            is_staff=False,
        )

    def _auth_get(
        self,
        *,
        path: str,
        user: FakeUser,
    ) -> Request:
        request = self.factory.get(path)
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.monitoring.order_ops_dashboard_views."
        "OrderOpsSelector.dashboard_counts"
    )
    def test_summary_view_returns_counts_for_staff(
        self,
        mock_dashboard_counts: Any,
    ) -> None:
        counts = OrderOpsDashboardCounts(
            late_orders=3,
            critical_orders=5,
            awaiting_approval=2,
            awaiting_acknowledgement=4,
            pending_staffing=6,
            preferred_writer_pending=1,
            eligible_for_archive=7,
        )
        mock_dashboard_counts.return_value = counts

        view = OrderOpsDashboardSummaryView.as_view()
        request = self._auth_get(
            path="/orders/ops/summary/",
            user=self.staff_user,
        )

        response = cast(DRFResponse, view(request))
        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, asdict(counts))
        mock_dashboard_counts.assert_called_once_with(
            website=self.website,
        )

    def test_summary_view_denies_non_staff(self) -> None:
        view = OrderOpsDashboardSummaryView.as_view()
        request = self._auth_get(
            path="/orders/ops/summary/",
            user=self.non_staff_user,
        )

        response = cast(DRFResponse, view(request))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch(
        "orders.api.views.monitoring.order_ops_dashboard_views."
        "OrderOpsQueueView._resolve_queue"
    )
    def test_queue_view_returns_serialized_rows_for_staff(
        self,
        mock_resolve_queue: Any,
    ) -> None:
        order_1 = SimpleNamespace(
            pk=100,
            topic="Order A",
            status="in_progress",
            payment_status="unpaid",
            total_price="120.00",
            amount_paid="0.00",
            client_deadline="2026-05-01T12:00:00Z",
            writer_deadline="2026-04-30T12:00:00Z",
            preferred_writer_status="invited",
            client=SimpleNamespace(pk=50),
            preferred_writer=SimpleNamespace(pk=60),
        )
        order_2 = SimpleNamespace(
            pk=101,
            topic="Order B",
            status="submitted",
            payment_status="partially_paid",
            total_price="200.00",
            amount_paid="100.00",
            client_deadline="2026-05-02T12:00:00Z",
            writer_deadline="2026-05-01T12:00:00Z",
            preferred_writer_status="not_requested",
            client=SimpleNamespace(pk=51),
            preferred_writer=None,
        )
        mock_resolve_queue.return_value = [order_1, order_2]

        view = OrderOpsQueueView.as_view()
        request = self._auth_get(
            path="/orders/ops/queues/late/",
            user=self.staff_user,
        )

        response = cast(DRFResponse, view(request, queue_key="late"))
        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["queue_key"], "late")
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["id"], 100)
        self.assertEqual(data["results"][1]["id"], 101)

        mock_resolve_queue.assert_called_once_with(
            website=self.website,
            queue_key="late",
        )

    def test_queue_view_denies_non_staff(self) -> None:
        view = OrderOpsQueueView.as_view()
        request = self._auth_get(
            path="/orders/ops/queues/late/",
            user=self.non_staff_user,
        )

        response = cast(DRFResponse, view(request, queue_key="late"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_queue_serializer_includes_expected_fields(self) -> None:
        order = SimpleNamespace(
            pk=200,
            topic="Order C",
            status="completed",
            payment_status="fully_paid",
            total_price="300.00",
            amount_paid="300.00",
            client_deadline="2026-05-03T12:00:00Z",
            writer_deadline="2026-05-02T12:00:00Z",
            preferred_writer_status="expired",
            client=SimpleNamespace(pk=70),
            preferred_writer=SimpleNamespace(pk=80),
        )

        row = OrderOpsQueueView._serialize_order(order=order)

        self.assertEqual(
            row,
            {
                "id": 200,
                "topic": "Order C",
                "status": "completed",
                "payment_status": "fully_paid",
                "total_price": "300.00",
                "amount_paid": "300.00",
                "client_deadline": "2026-05-03T12:00:00Z",
                "writer_deadline": "2026-05-02T12:00:00Z",
                "preferred_writer_status": "expired",
                "client_id": 70,
                "preferred_writer_id": 80,
            },
        )