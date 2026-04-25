from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.tasks import order_completion_tasks 


class FakeQuerySet:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def select_related(self, *args: Any, **kwargs: Any) -> "FakeQuerySet":
        return self

    def iterator(self, chunk_size: int = 200):
        return iter(self._items)


class OrderCompletionTaskTests(SimpleTestCase):
    def _order(self, pk: int) -> Any:
        return cast(Any, SimpleNamespace(pk=pk))

    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderApprovalService.can_auto_approve"
    )
    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderApprovalService.auto_approve_order"
    )
    @patch("orders.tasks.order_completion_tasks.Order.objects.filter")
    def test_auto_approve_eligible_orders(
        self,
        mock_filter: Any,
        mock_auto_approve: Any,
        mock_can_auto_approve: Any,
    ) -> None:
        orders = [self._order(1), self._order(2), self._order(3)]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_can_auto_approve.side_effect = [True, False, True]

        task = cast(
            Any,
            order_completion_tasks.auto_approve_eligible_orders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 3,
                "approved": 2,
                "failed": 0,
            },
        )
        self.assertEqual(mock_auto_approve.call_count, 2)

    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderApprovalService.can_auto_approve"
    )
    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderApprovalService.auto_approve_order"
    )
    @patch("orders.tasks.order_completion_tasks.Order.objects.filter")
    def test_auto_approve_eligible_orders_continues_on_failure(
        self,
        mock_filter: Any,
        mock_auto_approve: Any,
        mock_can_auto_approve: Any,
    ) -> None:
        orders = [self._order(1), self._order(2)]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_can_auto_approve.return_value = True
        mock_auto_approve.side_effect = [Exception("boom"), None]

        task = cast(
            Any,
            order_completion_tasks.auto_approve_eligible_orders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "approved": 1,
                "failed": 1,
            },
        )

    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderReminderService.send_approval_reminder"
    )
    @patch("orders.tasks.order_completion_tasks.Order.objects.filter")
    def test_send_completion_approval_reminders(
        self,
        mock_filter: Any,
        mock_send_reminder: Any,
    ) -> None:
        orders = [self._order(1), self._order(2), self._order(3)]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_send_reminder.side_effect = [True, False, True]

        task = cast(
            Any,
            order_completion_tasks.send_completion_approval_reminders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 3,
                "reminded": 2,
                "failed": 0,
            },
        )

    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderArchivalService.can_auto_archive"
    )
    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderArchivalService.auto_archive_order"
    )
    @patch("orders.tasks.order_completion_tasks.Order.objects.filter")
    def test_auto_archive_eligible_orders(
        self,
        mock_filter: Any,
        mock_auto_archive: Any,
        mock_can_auto_archive: Any,
    ) -> None:
        orders = [self._order(10), self._order(11)]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_can_auto_archive.side_effect = [True, False]

        task = cast(
            Any,
            order_completion_tasks.auto_archive_eligible_orders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "archived": 1,
                "failed": 0,
            },
        )
        mock_auto_archive.assert_called_once_with(
            order=orders[0],
            triggered_by=None,
        )

    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderArchivalService.can_auto_archive"
    )
    @patch(
        "orders.tasks.order_completion_tasks."
        "OrderArchivalService.auto_archive_order"
    )
    @patch("orders.tasks.order_completion_tasks.Order.objects.filter")
    def test_auto_archive_eligible_orders_continues_on_failure(
        self,
        mock_filter: Any,
        mock_auto_archive: Any,
        mock_can_auto_archive: Any,
    ) -> None:
        orders = [self._order(10), self._order(11)]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_can_auto_archive.return_value = True
        mock_auto_archive.side_effect = [Exception("boom"), None]

        task = cast(
            Any,
            order_completion_tasks.auto_archive_eligible_orders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "archived": 1,
                "failed": 1,
            },
        )