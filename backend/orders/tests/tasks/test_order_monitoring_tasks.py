from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.tasks import order_monitoring_tasks


class FakeAssignmentsManager:
    def __init__(self, current_assignment: Any | None) -> None:
        self._current_assignment = current_assignment

    def filter(self, **kwargs: Any) -> "FakeAssignmentsManager":
        return self

    def select_related(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> "FakeAssignmentsManager":
        return self

    def first(self) -> Any | None:
        return self._current_assignment


class FakeQuerySet:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def select_related(self, *args: Any, **kwargs: Any) -> "FakeQuerySet":
        return self

    def iterator(self, chunk_size: int = 200):
        return iter(self._items)


class OrderMonitoringTaskTests(SimpleTestCase):
    def _order(
        self,
        pk: int,
        *,
        current_assignment: Any | None,
    ) -> Any:
        order = SimpleNamespace(
            pk=pk,
            assignments=FakeAssignmentsManager(current_assignment),
        )
        return cast(Any, order)

    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderReminderService.send_writer_acknowledgement_reminder"
    )
    @patch("orders.tasks.order_monitoring_tasks.Order.objects.filter")
    def test_send_writer_acknowledgement_reminders(
        self,
        mock_filter: Any,
        mock_send: Any,
    ) -> None:
        assignment = SimpleNamespace(writer=SimpleNamespace(pk=20))
        orders = [
            self._order(1, current_assignment=assignment),
            self._order(2, current_assignment=None),
            self._order(3, current_assignment=assignment),
        ]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_send.side_effect = [True, False]

        task = cast(
            Any,
            order_monitoring_tasks.send_writer_acknowledgement_reminders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 3,
                "reminded": 1,
                "failed": 0,
            },
        )
        self.assertEqual(mock_send.call_count, 2)

    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderReminderService.send_writer_acknowledgement_reminder"
    )
    @patch("orders.tasks.order_monitoring_tasks.Order.objects.filter")
    def test_send_writer_acknowledgement_reminders_continues_on_failure(
        self,
        mock_filter: Any,
        mock_send: Any,
    ) -> None:
        assignment = SimpleNamespace(writer=SimpleNamespace(pk=20))
        orders = [
            self._order(1, current_assignment=assignment),
            self._order(2, current_assignment=assignment),
        ]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_send.side_effect = [Exception("boom"), True]

        task = cast(
            Any,
            order_monitoring_tasks.send_writer_acknowledgement_reminders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "reminded": 1,
                "failed": 1,
            },
        )

    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderReminderService.send_operational_writer_reminder"
    )
    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderMonitoringService.build_operational_state"
    )
    @patch("orders.tasks.order_monitoring_tasks.Order.objects.filter")
    def test_send_operational_writer_reminders(
        self,
        mock_filter: Any,
        mock_build_state: Any,
        mock_send: Any,
    ) -> None:
        assignment = SimpleNamespace(writer=SimpleNamespace(pk=20))
        orders = [
            self._order(1, current_assignment=assignment),
            self._order(2, current_assignment=None),
            self._order(3, current_assignment=assignment),
        ]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_build_state.side_effect = [
            SimpleNamespace(state_label="critical"),
            SimpleNamespace(state_label="late"),
            SimpleNamespace(state_label="normal"),
        ]
        mock_send.side_effect = [True]

        task = cast(
            Any,
            order_monitoring_tasks.send_operational_writer_reminders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 3,
                "reminded": 1,
                "failed": 0,
            },
        )
        mock_send.assert_called_once()

    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderReminderService.send_operational_writer_reminder"
    )
    @patch(
        "orders.tasks.order_monitoring_tasks."
        "OrderMonitoringService.build_operational_state"
    )
    @patch("orders.tasks.order_monitoring_tasks.Order.objects.filter")
    def test_send_operational_writer_reminders_continues_on_failure(
        self,
        mock_filter: Any,
        mock_build_state: Any,
        mock_send: Any,
    ) -> None:
        assignment = SimpleNamespace(writer=SimpleNamespace(pk=20))
        orders = [
            self._order(1, current_assignment=assignment),
            self._order(2, current_assignment=assignment),
        ]
        mock_filter.return_value = FakeQuerySet(orders)
        mock_build_state.side_effect = [
            SimpleNamespace(state_label="critical"),
            SimpleNamespace(state_label="late"),
        ]
        mock_send.side_effect = [Exception("boom"), True]

        task = cast(
            Any,
            order_monitoring_tasks.send_operational_writer_reminders,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "reminded": 1,
                "failed": 1,
            },
        )