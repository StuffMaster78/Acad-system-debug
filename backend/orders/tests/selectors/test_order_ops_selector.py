from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.selectors.order_ops_selector import (
    OrderOpsDashboardCounts,
    OrderOpsSelector,
)


class OrderOpsSelectorTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=10)

    @patch("orders.selectors.order_ops_selector.timezone")
    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_late_orders(
        self,
        mock_filter: Any,
        mock_timezone: Any,
    ) -> None:
        now = SimpleNamespace()
        mock_timezone.now.return_value = now

        OrderOpsSelector.late_orders(website=self.website)

        mock_filter.assert_called_once_with(
            website=self.website,
            status="in_progress",
            writer_deadline__lt=now,
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
            "preferred_writer",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_critical_orders(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.critical_orders(website=self.website)

        mock_filter.assert_called_once_with(
            website=self.website,
            status="in_progress",
            is_urgent=True,
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
            "preferred_writer",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_awaiting_approval(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.awaiting_approval(website=self.website)

        mock_filter.assert_called_once_with(
            website=self.website,
            status="submitted",
            approved_at__isnull=True,
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_awaiting_acknowledgement(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.awaiting_acknowledgement(
            website=self.website
        )

        mock_filter.assert_called_once_with(
            website=self.website,
            status="in_progress",
            last_writer_acknowledged_at__isnull=True,
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
            "preferred_writer",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_pending_staffing(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.pending_staffing(website=self.website)

        mock_filter.assert_called_once_with(
            website=self.website,
            status="ready_for_staffing",
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
            "preferred_writer",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_preferred_writer_pending(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.preferred_writer_pending(
            website=self.website
        )

        mock_filter.assert_called_once_with(
            website=self.website,
            status="ready_for_staffing",
            preferred_writer_status="invited",
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
            "preferred_writer",
        )

    @patch("orders.selectors.order_ops_selector.Order.objects.filter")
    def test_eligible_for_archive(
        self,
        mock_filter: Any,
    ) -> None:
        OrderOpsSelector.eligible_for_archive(website=self.website)

        mock_filter.assert_called_once_with(
            website=self.website,
            status="completed",
            archived_at__isnull=True,
        )
        mock_filter.return_value.select_related.assert_called_once_with(
            "client",
        )

    @patch.object(OrderOpsSelector, "late_orders")
    @patch.object(OrderOpsSelector, "critical_orders")
    @patch.object(OrderOpsSelector, "awaiting_approval")
    @patch.object(OrderOpsSelector, "awaiting_acknowledgement")
    @patch.object(OrderOpsSelector, "pending_staffing")
    @patch.object(OrderOpsSelector, "preferred_writer_pending")
    @patch.object(OrderOpsSelector, "eligible_for_archive")
    def test_dashboard_counts(
        self,
        mock_eligible_for_archive: Any,
        mock_preferred_writer_pending: Any,
        mock_pending_staffing: Any,
        mock_awaiting_acknowledgement: Any,
        mock_awaiting_approval: Any,
        mock_critical_orders: Any,
        mock_late_orders: Any,
    ) -> None:
        mock_late_orders.return_value.count.return_value = 3
        mock_critical_orders.return_value.count.return_value = 5
        mock_awaiting_approval.return_value.count.return_value = 2
        mock_awaiting_acknowledgement.return_value.count.return_value = 4
        mock_pending_staffing.return_value.count.return_value = 6
        mock_preferred_writer_pending.return_value.count.return_value = 1
        mock_eligible_for_archive.return_value.count.return_value = 7

        result = OrderOpsSelector.dashboard_counts(
            website=self.website
        )

        self.assertEqual(
            result,
            OrderOpsDashboardCounts(
                late_orders=3,
                critical_orders=5,
                awaiting_approval=2,
                awaiting_acknowledgement=4,
                pending_staffing=6,
                preferred_writer_pending=1,
                eligible_for_archive=7,
            ),
        )

        mock_late_orders.assert_called_once_with(website=self.website)
        mock_critical_orders.assert_called_once_with(website=self.website)
        mock_awaiting_approval.assert_called_once_with(
            website=self.website
        )
        mock_awaiting_acknowledgement.assert_called_once_with(
            website=self.website
        )
        mock_pending_staffing.assert_called_once_with(
            website=self.website
        )
        mock_preferred_writer_pending.assert_called_once_with(
            website=self.website
        )
        mock_eligible_for_archive.assert_called_once_with(
            website=self.website
        )