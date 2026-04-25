from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from orders.models.orders.constants import (
    ORDER_STATUS_ARCHIVED,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
)
from orders.services.order_archival_service import (
    OrderArchivalService,
)


class OrderArchivalServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.staff_user = SimpleNamespace(pk=10, website_id=1)
        self.foreign_user = SimpleNamespace(pk=99, website_id=999)

    def _make_order(
        self,
        *,
        pk: int = 100,
        status: str = ORDER_STATUS_COMPLETED,
        completed_at=None,
        archived_at=None,
    ) -> Any:
        order = MagicMock()
        order.pk = pk
        order.website = self.website
        order.status = status
        order.completed_at = completed_at
        order.archived_at = archived_at
        order.save = MagicMock()
        return cast(Any, order)

    @patch(
        "orders.services.order_archival_service.OrderDispute.objects.filter"
    )
    @patch(
        "orders.services.order_archival_service.OrderRevisionRequest.objects.filter"
    )
    @patch(
        "orders.services.order_archival_service.OrderAdjustmentRequest.objects.filter"
    )
    def test_can_auto_archive_returns_true_when_eligible(
        self,
        mock_adjustment_filter: Any,
        mock_revision_filter: Any,
        mock_dispute_filter: Any,
    ) -> None:
        completed_at = timezone.now() - timedelta(days=40)
        order = self._make_order(
            completed_at=completed_at,
            archived_at=None,
        )

        mock_dispute_filter.return_value.exists.return_value = False
        mock_revision_filter.return_value.exists.return_value = False
        mock_adjustment_filter.return_value.exists.return_value = False

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertTrue(result)

    def test_can_auto_archive_returns_false_when_not_completed(self) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    def test_can_auto_archive_returns_false_when_already_archived(self) -> None:
        order = self._make_order(
            completed_at=timezone.now() - timedelta(days=40),
            archived_at=timezone.now(),
        )

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    def test_can_auto_archive_returns_false_when_completed_at_missing(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=None,
            archived_at=None,
        )

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    @patch(
        "orders.services.order_archival_service.OrderDispute.objects.filter"
    )
    def test_can_auto_archive_returns_false_with_active_dispute(
        self,
        mock_dispute_filter: Any,
    ) -> None:
        order = self._make_order(
            completed_at=timezone.now() - timedelta(days=40),
            archived_at=None,
        )

        mock_dispute_filter.return_value.exists.return_value = True

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    @patch(
        "orders.services.order_archival_service.OrderDispute.objects.filter"
    )
    @patch(
        "orders.services.order_archival_service.OrderRevisionRequest.objects.filter"
    )
    def test_can_auto_archive_returns_false_with_pending_revision(
        self,
        mock_revision_filter: Any,
        mock_dispute_filter: Any,
    ) -> None:
        order = self._make_order(
            completed_at=timezone.now() - timedelta(days=40),
            archived_at=None,
        )

        mock_dispute_filter.return_value.exists.return_value = False
        mock_revision_filter.return_value.exists.return_value = True

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    @patch(
        "orders.services.order_archival_service.OrderDispute.objects.filter"
    )
    @patch(
        "orders.services.order_archival_service.OrderRevisionRequest.objects.filter"
    )
    @patch(
        "orders.services.order_archival_service.OrderAdjustmentRequest.objects.filter"
    )
    def test_can_auto_archive_returns_false_with_pending_paid_revision_adjustment(
        self,
        mock_adjustment_filter: Any,
        mock_revision_filter: Any,
        mock_dispute_filter: Any,
    ) -> None:
        order = self._make_order(
            completed_at=timezone.now() - timedelta(days=40),
            archived_at=None,
        )

        mock_dispute_filter.return_value.exists.return_value = False
        mock_revision_filter.return_value.exists.return_value = False
        mock_adjustment_filter.return_value.exists.return_value = True

        result = OrderArchivalService.can_auto_archive(order=order)

        self.assertFalse(result)

    def test_auto_archive_raises_when_not_eligible(self) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)

        with self.assertRaisesMessage(
            ValidationError,
            "Order is not eligible for automatic archival.",
        ):
            OrderArchivalService.auto_archive_order(order=order)

    @patch(
        "orders.services.order_archival_service.validate_status_transition"
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_active_dispute",
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_pending_revision",
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_pending_paid_revision_adjustment",
    )
    @patch.object(
        OrderArchivalService,
        "_create_timeline_event",
    )
    @patch.object(
        OrderArchivalService,
        "_lock_order",
    )
    def test_auto_archive_success(
        self,
        mock_lock: Any,
        mock_timeline: Any,
        mock_pending_adjustment: Any,
        mock_pending_revision: Any,
        mock_active_dispute: Any,
        mock_validate_transition: Any,
    ) -> None:
        completed_at = timezone.now() - timedelta(days=40)
        order = self._make_order(completed_at=completed_at)
        mock_lock.return_value = order

        result = OrderArchivalService.auto_archive_order(order=order)

        self.assertIsNotNone(result.archived_at)
        self.assertEqual(result.status, ORDER_STATUS_ARCHIVED)
        order.save.assert_called_once_with(
            update_fields=[
                "archived_at",
                "status",
                "updated_at",
            ]
        )
        mock_validate_transition.assert_called_once_with(
            from_status=ORDER_STATUS_COMPLETED,
            to_status=ORDER_STATUS_ARCHIVED,
        )
        mock_active_dispute.assert_called_once_with(order=order)
        mock_pending_revision.assert_called_once_with(order=order)
        mock_pending_adjustment.assert_called_once_with(order=order)
        mock_timeline.assert_called_once()

    @patch(
        "orders.services.order_archival_service.validate_status_transition"
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_active_dispute",
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_pending_revision",
    )
    @patch.object(
        OrderArchivalService,
        "_ensure_no_pending_paid_revision_adjustment",
    )
    @patch.object(
        OrderArchivalService,
        "_create_timeline_event",
    )
    @patch.object(
        OrderArchivalService,
        "_lock_order",
    )
    def test_archive_order_success(
        self,
        mock_lock: Any,
        mock_timeline: Any,
        mock_pending_adjustment: Any,
        mock_pending_revision: Any,
        mock_active_dispute: Any,
        mock_validate_transition: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=10),
            archived_at=None,
        )
        mock_lock.return_value = order

        result = OrderArchivalService.archive_order(
            order=order,
            archived_by=self.staff_user,
            triggered_by=self.staff_user,
            reason="Retention cleanup",
        )

        self.assertIsNotNone(result.archived_at)
        self.assertEqual(result.status, ORDER_STATUS_ARCHIVED)
        order.save.assert_called_once_with(
            update_fields=[
                "archived_at",
                "status",
                "updated_at",
            ]
        )
        mock_validate_transition.assert_called_once_with(
            from_status=ORDER_STATUS_COMPLETED,
            to_status=ORDER_STATUS_ARCHIVED,
        )
        mock_active_dispute.assert_called_once_with(order=order)
        mock_pending_revision.assert_called_once_with(order=order)
        mock_pending_adjustment.assert_called_once_with(order=order)
        mock_timeline.assert_called_once()

    def test_archive_order_raises_when_already_archived(self) -> None:
        order = self._make_order(
            archived_at=timezone.now(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Order has already been archived.",
        ):
            OrderArchivalService._ensure_can_archive(order)

    def test_archive_order_raises_when_not_completed(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_IN_PROGRESS,
            completed_at=timezone.now(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only completed orders can be archived.",
        ):
            OrderArchivalService._ensure_can_archive(order)

    def test_archive_order_raises_when_completed_at_missing(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=None,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Completed orders must have completed_at.",
        ):
            OrderArchivalService._ensure_can_archive(order)

    def test_validate_actor_website_raises_for_cross_tenant_actor(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            OrderArchivalService._validate_actor_website(
                actor=self.foreign_user,
                order=order,
            )

    @patch(
        "orders.services.order_archival_service.OrderDispute.objects.filter"
    )
    def test_ensure_no_active_dispute_raises_when_dispute_exists(
        self,
        mock_dispute_filter: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        mock_dispute_filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Cannot archive order with active dispute.",
        ):
            OrderArchivalService._ensure_no_active_dispute(order=order)

    @patch(
        "orders.services.order_archival_service.OrderRevisionRequest.objects.filter"
    )
    def test_ensure_no_pending_revision_raises_when_pending_revision_exists(
        self,
        mock_revision_filter: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        mock_revision_filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Cannot archive order with pending revision.",
        ):
            OrderArchivalService._ensure_no_pending_revision(order=order)

    @patch(
        "orders.services.order_archival_service.OrderAdjustmentRequest.objects.filter"
    )
    def test_ensure_no_pending_paid_revision_adjustment_raises_when_pending_adjustment_exists(
        self,
        mock_adjustment_filter: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        mock_adjustment_filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Cannot archive order with pending paid revision adjustment.",
        ):
            OrderArchivalService._ensure_no_pending_paid_revision_adjustment(
                order=order
            )