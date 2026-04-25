from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from orders.models.orders.constants import (
    FREE_REVISION_WINDOW_DAYS,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
    ORDER_REVISION_EVENT_CREATED,
    ORDER_REVISION_STATUS_PENDING,
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_SUBMITTED,
)
from orders.services.revision_orchestration_service import (
    RevisionOrchestrationService,
)


class RevisionOrchestrationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.staff_user = SimpleNamespace(pk=20, website_id=1)

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_COMPLETED,
        completed_at=None,
        submitted_at=None,
        approved_at=None,
    ) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.status = status
        order.completed_at = completed_at
        order.submitted_at = submitted_at
        order.approved_at = approved_at
        return order

    def _make_revision_request(self, *, order) -> MagicMock:
        revision_request = MagicMock()
        revision_request.pk = 200
        revision_request.website = order.website
        revision_request.order = order
        return revision_request

    def _make_adjustment_request(self, *, order) -> MagicMock:
        adjustment_request = MagicMock()
        adjustment_request.pk = 300
        adjustment_request.website = order.website
        adjustment_request.order = order
        return adjustment_request

    @patch.object(
        RevisionOrchestrationService,
        "_create_free_revision_request",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_create_paid_revision_adjustment",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_ensure_order_can_accept_revision",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_lock_order",
    )
    def test_create_revision_request_routes_to_free_revision(
        self,
        mock_lock_order,
        mock_ensure_order_can_accept_revision,
        mock_validate_actor_website,
        mock_create_paid_revision_adjustment,
        mock_create_free_revision_request,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=2),
        )
        revision_request = self._make_revision_request(order=order)

        mock_lock_order.return_value = order
        mock_create_free_revision_request.return_value = revision_request

        result = RevisionOrchestrationService.create_revision_request(
            order=order,
            requested_by=self.client_user,
            reason="Please fix formatting",
            scope_summary="Formatting cleanup",
            is_within_original_scope=True,
            triggered_by=self.client_user,
        )

        self.assertEqual(result, revision_request)
        mock_create_free_revision_request.assert_called_once_with(
            order=order,
            requested_by=self.client_user,
            reason="Please fix formatting",
            scope_summary="Formatting cleanup",
            triggered_by=self.client_user,
        )
        mock_create_paid_revision_adjustment.assert_not_called()

    @patch.object(
        RevisionOrchestrationService,
        "_create_free_revision_request",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_create_paid_revision_adjustment",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_ensure_order_can_accept_revision",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_lock_order",
    )
    def test_create_revision_request_routes_to_paid_when_out_of_scope(
        self,
        mock_lock_order,
        mock_ensure_order_can_accept_revision,
        mock_validate_actor_website,
        mock_create_paid_revision_adjustment,
        mock_create_free_revision_request,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=2),
        )
        adjustment_request = self._make_adjustment_request(order=order)

        mock_lock_order.return_value = order
        mock_create_paid_revision_adjustment.return_value = adjustment_request

        result = RevisionOrchestrationService.create_revision_request(
            order=order,
            requested_by=self.client_user,
            reason="Add two more sections",
            scope_summary="New sections and examples",
            is_within_original_scope=False,
            triggered_by=self.client_user,
        )

        self.assertEqual(result, adjustment_request)
        mock_create_paid_revision_adjustment.assert_called_once_with(
            order=order,
            requested_by=self.client_user,
            reason="Add two more sections",
            scope_summary="New sections and examples",
            is_within_original_scope=False,
            triggered_by=self.client_user,
        )
        mock_create_free_revision_request.assert_not_called()

    @patch.object(
        RevisionOrchestrationService,
        "_create_free_revision_request",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_create_paid_revision_adjustment",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_validate_actor_website",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_ensure_order_can_accept_revision",
    )
    @patch.object(
        RevisionOrchestrationService,
        "_lock_order",
    )
    def test_create_revision_request_routes_to_paid_when_window_expired(
        self,
        mock_lock_order,
        mock_ensure_order_can_accept_revision,
        mock_validate_actor_website,
        mock_create_paid_revision_adjustment,
        mock_create_free_revision_request,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now()
            - timedelta(days=FREE_REVISION_WINDOW_DAYS + 1),
        )
        adjustment_request = self._make_adjustment_request(order=order)

        mock_lock_order.return_value = order
        mock_create_paid_revision_adjustment.return_value = adjustment_request

        result = RevisionOrchestrationService.create_revision_request(
            order=order,
            requested_by=self.client_user,
            reason="Late revision request",
            scope_summary="Minor updates",
            is_within_original_scope=True,
            triggered_by=self.client_user,
        )

        self.assertEqual(result, adjustment_request)
        mock_create_paid_revision_adjustment.assert_called_once()
        mock_create_free_revision_request.assert_not_called()

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderRevisionRequest.objects.create"
    )
    @patch.object(
        RevisionOrchestrationService,
        "_create_revision_event",
    )
    def test_create_free_revision_request_creates_request_and_event(
        self,
        mock_create_revision_event,
        mock_revision_request_create,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        revision_request = self._make_revision_request(order=order)

        mock_revision_request_create.return_value = revision_request

        result = RevisionOrchestrationService._create_free_revision_request(
            order=order,
            requested_by=self.client_user,
            reason="Fix citations",
            scope_summary="Citation formatting only",
            triggered_by=self.client_user,
        )

        self.assertEqual(result, revision_request)
        mock_revision_request_create.assert_called_once_with(
            website=order.website,
            order=order,
            requested_by=self.client_user,
            reason="Fix citations",
            scope_summary="Citation formatting only",
            status=ORDER_REVISION_STATUS_PENDING,
        )
        self.assertEqual(
            mock_create_revision_event.call_args.kwargs["event_type"],
            ORDER_REVISION_EVENT_CREATED,
        )

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderAdjustmentRequest.objects.create"
    )
    def test_create_paid_revision_adjustment_creates_adjustment_request(
        self,
        mock_adjustment_request_create,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        adjustment_request = self._make_adjustment_request(order=order)

        mock_adjustment_request_create.return_value = adjustment_request

        result = (
            RevisionOrchestrationService._create_paid_revision_adjustment(
                order=order,
                requested_by=self.client_user,
                reason="Add new analysis section",
                scope_summary="New analysis section",
                is_within_original_scope=False,
                triggered_by=self.client_user,
            )
        )

        self.assertEqual(result, adjustment_request)
        mock_adjustment_request_create.assert_called_once()
        kwargs = mock_adjustment_request_create.call_args.kwargs
        self.assertEqual(kwargs["website"], order.website)
        self.assertEqual(kwargs["order"], order)
        self.assertEqual(kwargs["requested_by"], self.client_user)
        self.assertEqual(
            kwargs["adjustment_type"],
            ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
        )
        self.assertEqual(
            kwargs["status"],
            ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
        )
        self.assertEqual(
            kwargs["metadata"]["reject_revision_reason"],
            "out_of_scope",
        )

    def test_is_free_revision_eligible_returns_true_within_scope_and_window_for_completed(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=2),
        )

        result = RevisionOrchestrationService._is_free_revision_eligible(
            order=order,
            is_within_original_scope=True,
        )

        self.assertTrue(result)

    def test_is_free_revision_eligible_returns_true_within_scope_and_window_for_submitted(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_SUBMITTED,
            completed_at=None,
            submitted_at=timezone.now() - timedelta(days=2),
        )

        result = RevisionOrchestrationService._is_free_revision_eligible(
            order=order,
            is_within_original_scope=True,
        )

        self.assertTrue(result)

    def test_is_free_revision_eligible_returns_false_when_out_of_scope(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=2),
        )

        result = RevisionOrchestrationService._is_free_revision_eligible(
            order=order,
            is_within_original_scope=False,
        )

        self.assertFalse(result)

    def test_is_free_revision_eligible_returns_false_when_window_expired(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now()
            - timedelta(days=FREE_REVISION_WINDOW_DAYS + 1),
        )

        result = RevisionOrchestrationService._is_free_revision_eligible(
            order=order,
            is_within_original_scope=True,
        )

        self.assertFalse(result)

    def test_is_free_revision_eligible_returns_false_when_reference_time_missing(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_SUBMITTED,
            completed_at=None,
            submitted_at=None,
        )

        result = RevisionOrchestrationService._is_free_revision_eligible(
            order=order,
            is_within_original_scope=True,
        )

        self.assertFalse(result)

    def test_build_paid_revision_reject_reason_returns_reference_time_missing(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_SUBMITTED,
            completed_at=None,
            submitted_at=None,
        )

        result = (
            RevisionOrchestrationService._build_paid_revision_reject_reason(
                order=order,
                is_within_original_scope=True,
            )
        )

        self.assertEqual(result, "revision_reference_time_missing")

    def test_build_paid_revision_reject_reason_returns_out_of_scope(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=2),
        )

        result = (
            RevisionOrchestrationService._build_paid_revision_reject_reason(
                order=order,
                is_within_original_scope=False,
            )
        )

        self.assertEqual(result, "out_of_scope")

    def test_build_paid_revision_reject_reason_returns_window_expired(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now()
            - timedelta(days=FREE_REVISION_WINDOW_DAYS + 1),
        )

        result = (
            RevisionOrchestrationService._build_paid_revision_reject_reason(
                order=order,
                is_within_original_scope=True,
            )
        )

        self.assertEqual(result, "free_revision_window_expired")

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderRevisionRequest.objects.select_for_update"
    )
    def test_ensure_order_can_accept_revision_rejects_invalid_status(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)

        mock_select_for_update.return_value.filter.return_value.exists.return_value = (
            False
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only submitted or completed orders can enter revision routing.",
        ):
            RevisionOrchestrationService._ensure_order_can_accept_revision(
                order
            )

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderRevisionRequest.objects.select_for_update"
    )
    def test_ensure_order_can_accept_revision_rejects_approved_order(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
            approved_at=timezone.now(),
        )

        mock_select_for_update.return_value.filter.return_value.exists.return_value = (
            False
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Approved orders cannot be revised.",
        ):
            RevisionOrchestrationService._ensure_order_can_accept_revision(
                order
            )

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderRevisionRequest.objects.select_for_update"
    )
    def test_ensure_order_can_accept_revision_rejects_duplicate_pending_revision(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )

        mock_select_for_update.return_value.filter.return_value.exists.return_value = (
            True
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has a pending revision request.",
        ):
            RevisionOrchestrationService._ensure_order_can_accept_revision(
                order
            )

    @patch(
        "orders.services.revision_orchestration_service."
        "OrderRevisionRequest.objects.select_for_update"
    )
    def test_ensure_order_can_accept_revision_rejects_missing_reference_time(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_SUBMITTED,
            completed_at=None,
            submitted_at=None,
        )

        mock_select_for_update.return_value.filter.return_value.exists.return_value = (
            False
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Submitted or completed orders must have a revision reference time.",
        ):
            RevisionOrchestrationService._ensure_order_can_accept_revision(
                order
            )

    def test_validate_actor_website_raises_for_cross_tenant_actor(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now(),
        )
        foreign_actor = SimpleNamespace(pk=99, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            RevisionOrchestrationService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )