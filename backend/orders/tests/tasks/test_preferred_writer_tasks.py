from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.tasks import preferred_writer_tasks


class FakeQuerySet:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def select_related(self, *args: Any, **kwargs: Any) -> "FakeQuerySet":
        return self

    def iterator(self, chunk_size: int = 200):
        return iter(self._items)


class PreferredWriterTaskTests(SimpleTestCase):
    def _interest(
        self,
        pk: int,
        *,
        writer: Any | None = None,
    ) -> Any:
        interest = SimpleNamespace(
            pk=pk,
            website=SimpleNamespace(pk=10),
            writer=writer,
            order=SimpleNamespace(
                pk=100 + pk,
                writer_deadline=None,
                preferred_writer_status="invited",
                save=lambda *args, **kwargs: None,
            ),
            status="pending",
            reviewed_at=None,
            save=lambda *args, **kwargs: None,
        )
        return cast(Any, interest)

    def _order(self, pk: int) -> Any:
        order = SimpleNamespace(
            pk=pk,
            website=SimpleNamespace(pk=10),
            client=SimpleNamespace(pk=20),
            preferred_writer=SimpleNamespace(pk=30),
            visibility_mode="preferred_writer_only",
            preferred_writer_status="expired",
            save=lambda *args, **kwargs: None,
        )
        return cast(Any, order)

    @patch(
        "orders.tasks.preferred_writer_tasks.NotificationService.notify"
    )
    @patch("orders.tasks.preferred_writer_tasks.OrderInterest.objects.filter")
    def test_send_pending_preferred_writer_reminders(
        self,
        mock_filter: Any,
        mock_notify: Any,
    ) -> None:
        interests = [
            self._interest(1, writer=SimpleNamespace(pk=50)),
            self._interest(2, writer=None),
            self._interest(3, writer=SimpleNamespace(pk=51)),
        ]
        mock_filter.return_value = FakeQuerySet(interests)

        task = cast(
            Any,
            preferred_writer_tasks.send_pending_preferred_writer_reminders,
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

    @patch("orders.tasks.preferred_writer_tasks.timezone")
    @patch("orders.tasks.preferred_writer_tasks.OrderInterest.objects.filter")
    def test_expire_preferred_writer_invitations(
        self,
        mock_filter: Any,
        mock_timezone: Any,
    ) -> None:
        mock_timezone.now.return_value = SimpleNamespace()
        interests = [
            self._interest(1, writer=SimpleNamespace(pk=50)),
            self._interest(2, writer=SimpleNamespace(pk=51)),
        ]
        mock_filter.return_value = FakeQuerySet(interests)

        task = cast(
            Any,
            preferred_writer_tasks.expire_preferred_writer_invitations,
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
        self.assertEqual(interests[0].status, "expired")
        self.assertEqual(interests[1].order.preferred_writer_status, "expired")

    @patch("orders.tasks.preferred_writer_tasks.timezone")
    @patch("orders.tasks.preferred_writer_tasks.OrderInterest.objects.filter")
    def test_expire_preferred_writer_invitations_continues_on_failure(
        self,
        mock_filter: Any,
        mock_timezone: Any,
    ) -> None:
        mock_timezone.now.return_value = SimpleNamespace()
        bad_interest = self._interest(1, writer=SimpleNamespace(pk=50))
        bad_interest.save = lambda *args, **kwargs: (_ for _ in ()).throw(
            Exception("boom")
        )
        good_interest = self._interest(2, writer=SimpleNamespace(pk=51))
        mock_filter.return_value = FakeQuerySet([bad_interest, good_interest])

        task = cast(
            Any,
            preferred_writer_tasks.expire_preferred_writer_invitations,
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
        "orders.tasks.preferred_writer_tasks.NotificationService.notify"
    )
    @patch("orders.tasks.preferred_writer_tasks.Order.objects.filter")
    def test_fallback_expired_preferred_writer_orders_to_pool(
        self,
        mock_filter: Any,
        mock_notify: Any,
    ) -> None:
        orders = [self._order(1), self._order(2)]
        mock_filter.return_value = FakeQuerySet(orders)

        task = cast(
            Any,
            preferred_writer_tasks.fallback_expired_preferred_writer_orders_to_pool,
        )
        result = task.run()

        self.assertEqual(
            result,
            {
                "scanned": 2,
                "moved": 2,
                "failed": 0,
            },
        )
        self.assertEqual(orders[0].visibility_mode, "pool")
        self.assertEqual(mock_notify.call_count, 2)