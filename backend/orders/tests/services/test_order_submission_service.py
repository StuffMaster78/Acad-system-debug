from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_STATUS_SUBMITTED,
    ORDER_TIMELINE_EVENT_COMPLETED,
    ORDER_TIMELINE_EVENT_REOPENED,
    ORDER_TIMELINE_EVENT_SUBMITTED,
)
from orders.services.order_submission_service import (
    OrderSubmissionService,
)


class OrderSubmissionServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.writer = SimpleNamespace(pk=20, website_id=1)
        self.other_writer = SimpleNamespace(pk=21, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)
        self.editor_user = SimpleNamespace(pk=31, website_id=1)

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_IN_PROGRESS,
    ) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.client = self.client_user
        order.status = status
        order.submitted_at = None
        order.completed_at = None
        order.approved_at = None
        order.save = MagicMock()
        return order

    def _make_assignment(self, *, writer=None) -> MagicMock:
        assignment = MagicMock()
        assignment.pk = 200
        assignment.writer = writer or self.writer
        assignment.is_current = True
        assignment.save = MagicMock()
        return assignment

    @patch.object(OrderSubmissionService, "_create_timeline_event")
    @patch.object(OrderSubmissionService, "_get_current_assignment")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_submit")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_submit_order_moves_order_to_submitted(
        self,
        mock_lock_order,
        mock_ensure_can_submit,
        mock_validate_actor_website,
        mock_get_current_assignment,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        result = OrderSubmissionService.submit_order(
            order=order,
            submitted_by=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_SUBMITTED)
        self.assertIsNotNone(order.submitted_at)
        self.assertIsNone(order.completed_at)
        self.assertIsNone(order.approved_at)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "submitted_at",
                "updated_at",
            ]
        )
        mock_ensure_can_submit.assert_called_once_with(order)
        mock_validate_actor_website.assert_called_once_with(
            actor=self.writer,
            order=order,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_SUBMITTED,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "submitted_by_id"
            ],
            self.writer.pk,
        )

    @patch.object(OrderSubmissionService, "_get_current_assignment")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_submit")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_submit_order_fails_without_current_assignment(
        self,
        mock_lock_order,
        mock_ensure_can_submit,
        mock_validate_actor_website,
        mock_get_current_assignment,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        with self.assertRaisesMessage(
            ValidationError,
            "A current assignment is required for submission.",
        ):
            OrderSubmissionService.submit_order(
                order=order,
                submitted_by=self.writer,
            )

    @patch.object(OrderSubmissionService, "_get_current_assignment")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_submit")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_submit_order_fails_for_non_current_writer(
        self,
        mock_lock_order,
        mock_ensure_can_submit,
        mock_validate_actor_website,
        mock_get_current_assignment,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)
        assignment = self._make_assignment(writer=self.other_writer)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        with self.assertRaisesMessage(
            ValidationError,
            "Only the current assigned writer can submit the order.",
        ):
            OrderSubmissionService.submit_order(
                order=order,
                submitted_by=self.writer,
            )

    @patch.object(OrderSubmissionService, "_create_timeline_event")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_complete")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_complete_order_moves_submitted_order_to_completed(
        self,
        mock_lock_order,
        mock_ensure_can_complete,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        mock_lock_order.return_value = order

        result = OrderSubmissionService.complete_order(
            order=order,
            completed_by=self.staff_user,
            triggered_by=self.staff_user,
            internal_reason="staff_close",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(order.completed_at)
        self.assertIsNone(order.approved_at)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )
        mock_ensure_can_complete.assert_called_once_with(order)
        mock_validate_actor_website.assert_called_once_with(
            actor=self.staff_user,
            order=order,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_COMPLETED,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "completed_by_id"
            ],
            self.staff_user.pk,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "internal_reason"
            ],
            "staff_close",
        )

    @patch.object(OrderSubmissionService, "_create_timeline_event")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_complete")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_complete_order_allows_client_completion(
        self,
        mock_lock_order,
        mock_ensure_can_complete,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        mock_lock_order.return_value = order

        result = OrderSubmissionService.complete_order(
            order=order,
            completed_by=self.client_user,
            triggered_by=self.client_user,
            internal_reason="client_acceptance",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(order.completed_at)
        self.assertIsNone(order.approved_at)
        mock_validate_actor_website.assert_called_once_with(
            actor=self.client_user,
            order=order,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "completed_by_id"
            ],
            self.client_user.pk,
        )

    @patch.object(OrderSubmissionService, "_create_timeline_event")
    @patch.object(OrderSubmissionService, "_ensure_can_complete")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_auto_complete_order_moves_submitted_order_to_completed(
        self,
        mock_lock_order,
        mock_ensure_can_complete,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        mock_lock_order.return_value = order

        result = OrderSubmissionService.auto_complete_order(
            order=order,
            internal_reason="auto_complete",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(order.completed_at)
        self.assertIsNone(order.approved_at)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "completed_at",
                "updated_at",
            ]
        )
        mock_ensure_can_complete.assert_called_once_with(order)
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_COMPLETED,
        )
        self.assertTrue(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "is_automatic"
            ]
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "internal_reason"
            ],
            "auto_complete",
        )

    @patch.object(OrderSubmissionService, "_create_timeline_event")
    @patch.object(OrderSubmissionService, "_get_current_assignment")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_reopen")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_reopen_order_moves_completed_order_to_in_progress(
        self,
        mock_lock_order,
        mock_ensure_can_reopen,
        mock_validate_actor_website,
        mock_get_current_assignment,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_COMPLETED)
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        result = OrderSubmissionService.reopen_order(
            order=order,
            reopened_by=self.editor_user,
            reason="Client needs fixes",
            triggered_by=self.editor_user,
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_IN_PROGRESS)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        mock_ensure_can_reopen.assert_called_once_with(order)
        mock_validate_actor_website.assert_called_once_with(
            actor=self.editor_user,
            order=order,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REOPENED,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"]["reason"],
            "Client needs fixes",
        )

    @patch.object(OrderSubmissionService, "_get_current_assignment")
    @patch.object(OrderSubmissionService, "_validate_actor_website")
    @patch.object(OrderSubmissionService, "_ensure_can_reopen")
    @patch.object(OrderSubmissionService, "_lock_order")
    def test_reopen_order_fails_without_current_assignment(
        self,
        mock_lock_order,
        mock_ensure_can_reopen,
        mock_validate_actor_website,
        mock_get_current_assignment,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_COMPLETED)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        with self.assertRaisesMessage(
            ValidationError,
            "A current assignment is required to reopen the order.",
        ):
            OrderSubmissionService.reopen_order(
                order=order,
                reopened_by=self.staff_user,
                reason="Need more work",
            )

    def test_ensure_can_submit_blocks_non_in_progress_order(self) -> None:
        order = self._make_order(status=ORDER_STATUS_READY_FOR_STAFFING)

        with self.assertRaisesMessage(
            ValidationError,
            "Only in progress orders can be submitted.",
        ):
            OrderSubmissionService._ensure_can_submit(order)

    def test_ensure_can_complete_blocks_non_submitted_order(self) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)

        with self.assertRaisesMessage(
            ValidationError,
            "Only submitted orders can be completed.",
        ):
            OrderSubmissionService._ensure_can_complete(order)

    def test_ensure_can_reopen_blocks_non_completed_order(self) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        with self.assertRaisesMessage(
            ValidationError,
            "Only completed orders can be reopened.",
        ):
            OrderSubmissionService._ensure_can_reopen(order)

    def test_validate_actor_website_raises_for_cross_tenant_actor(self) -> None:
        order = self._make_order()
        foreign_actor = SimpleNamespace(pk=77, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            OrderSubmissionService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )