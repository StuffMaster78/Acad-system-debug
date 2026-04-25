from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.tasks import order_adjustment_tasks


class FakeQuerySet:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def select_related(self, *args: Any, **kwargs: Any) -> "FakeQuerySet":
        return self

    def iterator(self, chunk_size: int = 200):
        return iter(self._items)


class OrderAdjustmentTaskTests(SimpleTestCase):
    def _adjustment_request(self, pk: int, *, client: Any | None) -> Any:
        req = SimpleNamespace(
            pk=pk,
            website=SimpleNamespace(pk=10),
            order=SimpleNamespace(pk=100 + pk, client=client),
            status="pending_client_response",
            save=lambda *args, **kwargs: None,
        )
        return cast(Any, req)

    def _funding(self, pk: int, *, client: Any | None) -> Any:
        funding = SimpleNamespace(
            pk=pk,
            website=SimpleNamespace(pk=10),
            adjustment_request=SimpleNamespace(
                pk=200 + pk,
                order=SimpleNamespace(pk=300 + pk, client=client),
            ),
        )
        return cast(Any, funding)

    @patch(
        "orders.tasks.order_adjustment_tasks.NotificationService.notify"
    )
    @patch(
        "orders.tasks.order_adjustment_tasks."
        "OrderAdjustmentRequest.objects.filter"
    )
    def test_send_pending_adjustment_response_reminders(
        self,
        mock_filter: Any,
        mock_notify: Any,
    ) -> None:
        requests = [
            self._adjustment_request(1, client=SimpleNamespace(pk=20)),
            self._adjustment_request(2, client=None),
            self._adjustment_request(3, client=SimpleNamespace(pk=21)),
        ]
        mock_filter.return_value = FakeQuerySet(requests)

        task = cast(
            Any,
            order_adjustment_tasks.send_pending_adjustment_response_reminders,
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
        self.assertEqual(mock_notify.call_count, 2)

    @patch("orders.tasks.order_adjustment_tasks.timezone")
    @patch(
        "orders.tasks.order_adjustment_tasks."
        "OrderAdjustmentRequest.objects.filter"
    )
    def test_expire_stale_adjustments(
        self,
        mock_filter: Any,
        mock_timezone: Any,
    ) -> None:
        mock_timezone.now.return_value = SimpleNamespace()
        req1 = self._adjustment_request(1, client=SimpleNamespace(pk=20))
        req2 = self._adjustment_request(2, client=SimpleNamespace(pk=21))
        mock_filter.return_value = FakeQuerySet([req1, req2])

        task = cast(
            Any,
            order_adjustment_tasks.expire_stale_adjustments,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "expired": 2,
                "failed": 0,
            },
        )
        self.assertEqual(req1.status, "expired")
        self.assertEqual(req2.status, "expired")

    @patch("orders.tasks.order_adjustment_tasks.timezone")
    @patch(
        "orders.tasks.order_adjustment_tasks."
        "OrderAdjustmentRequest.objects.filter"
    )
    def test_expire_stale_adjustments_continues_on_failure(
        self,
        mock_filter: Any,
        mock_timezone: Any,
    ) -> None:
        mock_timezone.now.return_value = SimpleNamespace()
        bad_req = self._adjustment_request(1, client=SimpleNamespace(pk=20))
        bad_req.save = lambda *args, **kwargs: (_ for _ in ()).throw(
            Exception("boom")
        )
        good_req = self._adjustment_request(2, client=SimpleNamespace(pk=21))
        mock_filter.return_value = FakeQuerySet([bad_req, good_req])

        task = cast(
            Any,
            order_adjustment_tasks.expire_stale_adjustments,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "expired": 1,
                "failed": 1,
            },
        )

    @patch(
        "orders.tasks.order_adjustment_tasks.NotificationService.notify"
    )
    @patch(
        "orders.tasks.order_adjustment_tasks."
        "OrderAdjustmentFunding.objects.filter"
    )
    def test_send_pending_adjustment_funding_reminders(
        self,
        mock_filter: Any,
        mock_notify: Any,
    ) -> None:
        fundings = [
            self._funding(1, client=SimpleNamespace(pk=20)),
            self._funding(2, client=None),
            self._funding(3, client=SimpleNamespace(pk=21)),
        ]
        mock_filter.return_value = FakeQuerySet(fundings)

        task = cast(
            Any,
            order_adjustment_tasks.send_pending_adjustment_funding_reminders,
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
        self.assertEqual(mock_notify.call_count, 2)