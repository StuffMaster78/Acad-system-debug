from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DISPUTED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_SUBMITTED,
)
from orders.services.dispute_orchestration_service import (
    DisputeOrchestrationService,
)


class DisputeOrchestrationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.writer_user = SimpleNamespace(pk=20, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_IN_PROGRESS,
    ) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.status = status
        order.save = MagicMock()
        return order

    def _make_dispute(
        self,
        *,
        order,
        status: str = "open",
    ) -> MagicMock:
        dispute = MagicMock()
        dispute.pk = 200
        dispute.website = order.website
        dispute.order = order
        dispute.status = status
        dispute.reason = "quality_issue"
        dispute.summary = "Client unhappy"
        dispute.save = MagicMock()
        return dispute

    def _make_resolution(self) -> MagicMock:
        resolution = MagicMock()
        resolution.pk = 300
        resolution.resolved_at = None
        return resolution

    @patch.object(
        DisputeOrchestrationService,
        "_create_dispute_event",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_no_open_dispute",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_order_can_be_disputed",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_order",
    )
    @patch(
        "orders.services.dispute_orchestration_service."
        "OrderDispute.objects.create"
    )
    def test_open_dispute_creates_dispute_and_marks_order_disputed(
        self,
        mock_dispute_create,
        mock_lock_order,
        mock_ensure_order_can_be_disputed,
        mock_ensure_no_open_dispute,
        mock_validate_actor_website,
        mock_create_dispute_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)
        dispute = self._make_dispute(order=order, status="open")

        mock_lock_order.return_value = order
        mock_dispute_create.return_value = dispute

        result = DisputeOrchestrationService.open_dispute(
            order=order,
            opened_by=self.client_user,
            reason="quality_issue",
            summary="Wrong file uploaded",
            triggered_by=self.client_user,
        )

        self.assertEqual(result, dispute)
        mock_dispute_create.assert_called_once()
        self.assertEqual(order.status, ORDER_STATUS_DISPUTED)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_dispute_event.call_args.kwargs["event_type"],
            "dispute_opened",
        )

    @patch.object(
        DisputeOrchestrationService,
        "_create_dispute_event",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_dispute_open",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_dispute",
    )
    def test_escalate_dispute_updates_status(
        self,
        mock_lock_dispute,
        mock_ensure_dispute_open,
        mock_validate_actor_website,
        mock_create_dispute_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="open")
        mock_lock_dispute.return_value = dispute

        result = DisputeOrchestrationService.escalate_dispute(
            dispute=dispute,
            escalated_by=self.staff_user,
            notes="Needs admin review",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, dispute)
        self.assertEqual(dispute.status, "escalated")
        self.assertIsNotNone(dispute.escalated_at)
        dispute.save.assert_called_once()
        self.assertEqual(
            mock_create_dispute_event.call_args.kwargs["event_type"],
            "dispute_escalated",
        )

    @patch.object(
        DisputeOrchestrationService,
        "_create_dispute_event",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_dispute_resolvable",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_order",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_dispute",
    )
    @patch(
        "orders.services.dispute_orchestration_service."
        "OrderDisputeResolution.objects.create"
    )
    @patch(
        "orders.services.dispute_orchestration_service.timezone.now"
    )
    def test_resolve_dispute_creates_resolution_and_updates_dispute(
        self,
        mock_now,
        mock_resolution_create,
        mock_lock_dispute,
        mock_lock_order,
        mock_ensure_dispute_resolvable,
        mock_validate_actor_website,
        mock_create_dispute_event,
    ) -> None:
        resolved_at = SimpleNamespace()
        mock_now.return_value = resolved_at

        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="escalated")
        resolution = self._make_resolution()
        resolution.resolved_at = resolved_at

        mock_lock_dispute.return_value = dispute
        mock_lock_order.return_value = order
        mock_resolution_create.return_value = resolution

        result = DisputeOrchestrationService.resolve_dispute(
            dispute=dispute,
            resolved_by=self.staff_user,
            outcome="reopen_order",
            resolution_summary="Writer should revise",
            internal_notes="Valid complaint",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, resolution)
        self.assertEqual(dispute.status, "resolved")
        self.assertEqual(dispute.resolved_at, resolved_at)
        dispute.save.assert_called_once()
        self.assertEqual(
            mock_create_dispute_event.call_args.kwargs["event_type"],
            "dispute_resolved",
        )

    @patch.object(
        DisputeOrchestrationService,
        "_create_dispute_event",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_allowed_restore_status",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_ensure_dispute_closed_allowed",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_order",
    )
    @patch.object(
        DisputeOrchestrationService,
        "_lock_dispute",
    )
    def test_close_dispute_closes_and_restores_order_status(
        self,
        mock_lock_dispute,
        mock_lock_order,
        mock_ensure_dispute_closed_allowed,
        mock_validate_actor_website,
        mock_ensure_allowed_restore_status,
        mock_create_dispute_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="resolved")

        mock_lock_dispute.return_value = dispute
        mock_lock_order.return_value = order

        result = DisputeOrchestrationService.close_dispute(
            dispute=dispute,
            closed_by=self.staff_user,
            restore_order_status=ORDER_STATUS_IN_PROGRESS,
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, dispute)
        self.assertEqual(dispute.status, "closed")
        self.assertIsNotNone(dispute.closed_at)
        dispute.save.assert_called_once()
        self.assertEqual(order.status, ORDER_STATUS_IN_PROGRESS)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_dispute_event.call_args.kwargs["event_type"],
            "dispute_closed",
        )

    def test_ensure_order_can_be_disputed_allows_in_progress(self) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)
        DisputeOrchestrationService._ensure_order_can_be_disputed(order)

    def test_ensure_order_can_be_disputed_allows_submitted(self) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)
        DisputeOrchestrationService._ensure_order_can_be_disputed(order)

    def test_ensure_order_can_be_disputed_allows_completed(self) -> None:
        order = self._make_order(status=ORDER_STATUS_COMPLETED)
        DisputeOrchestrationService._ensure_order_can_be_disputed(order)

    def test_ensure_order_can_be_disputed_blocks_other_statuses(self) -> None:
        order = self._make_order(status="cancelled")

        with self.assertRaisesMessage(
            ValidationError,
            "Only in progress, submitted, or completed orders "
            "can be disputed.",
        ):
            DisputeOrchestrationService._ensure_order_can_be_disputed(
                order
            )

    @patch(
        "orders.services.dispute_orchestration_service."
        "OrderDispute.objects.select_for_update"
    )
    def test_ensure_no_open_dispute_raises_when_active_exists(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_COMPLETED)
        mock_select_for_update.return_value.filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has an active dispute.",
        ):
            DisputeOrchestrationService._ensure_no_open_dispute(order)

    def test_ensure_dispute_open_raises_when_not_open(self) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="escalated")

        with self.assertRaisesMessage(
            ValidationError,
            "Only open disputes can be escalated.",
        ):
            DisputeOrchestrationService._ensure_dispute_open(dispute)

    def test_ensure_dispute_resolvable_allows_open(self) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="open")
        DisputeOrchestrationService._ensure_dispute_resolvable(dispute)

    def test_ensure_dispute_resolvable_allows_escalated(self) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="escalated")
        DisputeOrchestrationService._ensure_dispute_resolvable(dispute)

    def test_ensure_dispute_resolvable_raises_otherwise(self) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="resolved")

        with self.assertRaisesMessage(
            ValidationError,
            "Only open or escalated disputes can be resolved.",
        ):
            DisputeOrchestrationService._ensure_dispute_resolvable(
                dispute
            )

    def test_ensure_dispute_closed_allowed_raises_when_not_resolved(
        self,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_DISPUTED)
        dispute = self._make_dispute(order=order, status="open")

        with self.assertRaisesMessage(
            ValidationError,
            "Only resolved disputes can be closed.",
        ):
            DisputeOrchestrationService._ensure_dispute_closed_allowed(
                dispute
            )

    def test_ensure_allowed_restore_status_allows_in_progress(self) -> None:
        DisputeOrchestrationService._ensure_allowed_restore_status(
            ORDER_STATUS_IN_PROGRESS
        )

    def test_ensure_allowed_restore_status_allows_submitted(self) -> None:
        DisputeOrchestrationService._ensure_allowed_restore_status(
            ORDER_STATUS_SUBMITTED
        )

    def test_ensure_allowed_restore_status_allows_completed(self) -> None:
        DisputeOrchestrationService._ensure_allowed_restore_status(
            ORDER_STATUS_COMPLETED
        )

    def test_ensure_allowed_restore_status_raises_for_invalid_status(
        self,
    ) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "Invalid restore order status after dispute closure.",
        ):
            DisputeOrchestrationService._ensure_allowed_restore_status(
                "cancelled"
            )

    def test_validate_actor_website_raises_for_cross_tenant_actor(
        self,
    ) -> None:
        order = self._make_order()
        foreign_actor = SimpleNamespace(pk=99, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            DisputeOrchestrationService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )