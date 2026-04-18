from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from orders.services.order_archival_service import (
    OrderArchivalService,
)


class OrderArchivalServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)

    def _make_order(
        self,
        *,
        pk: int = 100,
        status: str = "completed",
        completed_at=None,
        archived_at=None,
    ) -> Any:
        order = MagicMock()
        order.pk = pk
        order.website = self.website
        order.status = status
        order.completed_at = completed_at
        order.archived_at = archived_at
        return cast(Any, order)

    def test_can_auto_archive_returns_true_when_eligible(self) -> None:
        completed_at = timezone.now() - timedelta(days=40)
        order = self._make_order(
            completed_at=completed_at,
            archived_at=None,
        )

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertTrue(result)

    def test_can_auto_archive_returns_false_when_not_completed(self) -> None:
        order = self._make_order(status="in_progress")

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    def test_can_auto_archive_returns_false_when_already_archived(self) -> None:
        order = self._make_order(
            completed_at=timezone.now() - timedelta(days=40),
            archived_at=timezone.now(),
        )

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    def test_auto_archive_raises_when_not_eligible(self) -> None:
        order = self._make_order(status="in_progress")

        with self.assertRaises(ValidationError):
            OrderArchivalService.auto_archive_order(order=order)

    @patch(
        "orders.services.order_archival_service."
        "OrderArchivalService._create_timeline_event"
    )
    @patch(
        "orders.services.order_archival_service."
        "OrderArchivalService._lock_order"
    )
    def test_auto_archive_success(
        self,
        mock_lock: Any,
        mock_timeline: Any,
    ) -> None:
        completed_at = timezone.now() - timedelta(days=40)
        order = self._make_order(
            completed_at=completed_at,
        )
        mock_lock.return_value = order

        result = OrderArchivalService.auto_archive_order(order=order)

        self.assertIsNotNone(result.archived_at)
        self.assertEqual(result.status, "archived")
        mock_timeline.assert_called_once()

    @patch(
        "orders.services.order_archival_service."
        "OrderArchivalService._create_timeline_event"
    )
    @patch(
        "orders.services.order_archival_service."
        "OrderArchivalService._lock_order"
    )
    def test_archive_order_success(
        self,
        mock_lock: Any,
        mock_timeline: Any,
    ) -> None:
        order = self._make_order(
            status="completed",
            completed_at=timezone.now() - timedelta(days=10),
            archived_at=None,
        )
        mock_lock.return_value = order

        result = OrderArchivalService.archive_order(order=order)

        self.assertIsNotNone(result.archived_at)
        self.assertEqual(result.status, "archived")
        mock_timeline.assert_called_once()

    def test_archive_order_raises_when_already_archived(self) -> None:
        order = self._make_order(
            archived_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            OrderArchivalService.archive_order(order=order)