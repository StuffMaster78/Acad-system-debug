from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_SOURCE_REASSIGNMENT,
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_REASSIGNED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_CANCELLED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_REJECTED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_REQUESTED,
    ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
    ORDER_VISIBILITY_HIDDEN,
    ORDER_VISIBILITY_POOL,
    PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
    PREFERRED_WRITER_STATUS_NOT_REQUESTED,
)
from orders.models.orders.order_reassignment_request import (
    OrderReassignmentDecision,
    OrderReassignmentRequestStatus,
)
from orders.services.order_reassignment_service import (
    OrderReassignmentService,
)


class OrderReassignmentServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.writer = SimpleNamespace(pk=20, website_id=1)
        self.new_writer = SimpleNamespace(pk=21, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_IN_PROGRESS,
        preferred_writer=None,
        preferred_writer_status: str = PREFERRED_WRITER_STATUS_NOT_REQUESTED,
        visibility_mode: str = ORDER_VISIBILITY_HIDDEN,
    ) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.client = self.client_user
        order.status = status
        order.preferred_writer = preferred_writer
        order.preferred_writer_status = preferred_writer_status
        order.visibility_mode = visibility_mode
        order.save = MagicMock()
        return order

    def _make_assignment(self, *, writer=None) -> MagicMock:
        assignment = MagicMock()
        assignment.pk = 200
        assignment.writer = writer or self.writer
        assignment.status = ORDER_ASSIGNMENT_STATUS_ACTIVE
        assignment.is_current = True
        assignment.save = MagicMock()
        return assignment

    def _make_request(
        self,
        *,
        order,
        requested_by,
        current_assignment,
        status: str = OrderReassignmentRequestStatus.PENDING,
        decision: str = "",
    ) -> MagicMock:
        request = MagicMock()
        request.pk = 300
        request.order = order
        request.requested_by = requested_by
        request.current_assignment = current_assignment
        request.status = status
        request.reason = "Need reassignment"
        request.decision = decision
        request.internal_notes = ""
        request.save = MagicMock()
        return request

    @patch.object(OrderReassignmentService, "_create_timeline_event")
    @patch.object(OrderReassignmentService, "_get_current_assignment")
    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_no_pending_request")
    @patch.object(OrderReassignmentService, "_ensure_order_can_be_reassigned")
    @patch.object(OrderReassignmentService, "_lock_order")
    @patch(
        "orders.services.order_reassignment_service."
        "OrderReassignmentRequest.objects.create"
    )
    def test_request_reassignment_creates_request(
        self,
        mock_request_create,
        mock_lock_order,
        mock_ensure_order_can_be_reassigned,
        mock_ensure_no_pending_request,
        mock_validate_actor_website,
        mock_get_current_assignment,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order()
        assignment = self._make_assignment(writer=self.writer)
        request = self._make_request(
            order=order,
            requested_by=self.writer,
            current_assignment=assignment,
        )

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment
        mock_request_create.return_value = request

        result = OrderReassignmentService.request_reassignment(
            order=order,
            requested_by=self.writer,
            requester_role="writer",
            reason="Client is unresponsive",
            internal_notes="Need support review",
            triggered_by=self.writer,
        )

        self.assertEqual(result, request)
        mock_request_create.assert_called_once_with(
            website=order.website,
            order=order,
            requested_by=self.writer,
            requester_role="writer",
            current_assignment=assignment,
            status=OrderReassignmentRequestStatus.PENDING,
            reason="Client is unresponsive",
            internal_notes="Need support review",
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REASSIGNMENT_REQUESTED,
        )

    @patch.object(OrderReassignmentService, "_get_current_assignment")
    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_no_pending_request")
    @patch.object(OrderReassignmentService, "_ensure_order_can_be_reassigned")
    @patch.object(OrderReassignmentService, "_lock_order")
    def test_request_reassignment_fails_without_current_assignment(
        self,
        mock_lock_order,
        mock_ensure_order_can_be_reassigned,
        mock_ensure_no_pending_request,
        mock_validate_actor_website,
        mock_get_current_assignment,
    ) -> None:
        order = self._make_order()
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        with self.assertRaisesMessage(
            ValidationError,
            "A current assignment is required for reassignment.",
        ):
            OrderReassignmentService.request_reassignment(
                order=order,
                requested_by=self.writer,
                requester_role="writer",
                reason="Need out",
            )

    @patch.object(OrderReassignmentService, "_create_timeline_event")
    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_request")
    def test_reject_reassignment_updates_request(
        self,
        mock_lock_request,
        mock_ensure_pending_request,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order()
        assignment = self._make_assignment()
        request = self._make_request(
            order=order,
            requested_by=self.writer,
            current_assignment=assignment,
        )
        mock_lock_request.return_value = request

        result = OrderReassignmentService.reject_reassignment(
            reassignment_request=request,
            reviewed_by=self.staff_user,
            internal_notes="Request denied",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, request)
        self.assertEqual(
            request.status,
            OrderReassignmentRequestStatus.REJECTED,
        )
        request.save.assert_called_once()
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REASSIGNMENT_REJECTED,
        )

    @patch.object(OrderReassignmentService, "_create_timeline_event")
    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_request")
    def test_cancel_reassignment_request_updates_request(
        self,
        mock_lock_request,
        mock_ensure_pending_request,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order()
        assignment = self._make_assignment()
        request = self._make_request(
            order=order,
            requested_by=self.writer,
            current_assignment=assignment,
        )
        mock_lock_request.return_value = request

        result = OrderReassignmentService.cancel_reassignment_request(
            reassignment_request=request,
            cancelled_by=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, request)
        self.assertEqual(
            request.status,
            OrderReassignmentRequestStatus.CANCELLED,
        )
        request.save.assert_called_once()
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REASSIGNMENT_CANCELLED,
        )

    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_request")
    def test_cancel_reassignment_request_blocks_non_requester(
        self,
        mock_lock_request,
        mock_ensure_pending_request,
    ) -> None:
        order = self._make_order()
        assignment = self._make_assignment()
        request = self._make_request(
            order=order,
            requested_by=self.writer,
            current_assignment=assignment,
        )
        mock_lock_request.return_value = request

        with self.assertRaisesMessage(
            ValidationError,
            "Only the requester can cancel this reassignment request.",
        ):
            OrderReassignmentService.cancel_reassignment_request(
                reassignment_request=request,
                cancelled_by=self.staff_user,
            )

    @patch.object(OrderReassignmentService, "_create_timeline_event")
    @patch.object(OrderReassignmentService, "_get_current_assignment")
    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_order")
    @patch.object(OrderReassignmentService, "_lock_request")
    def test_approve_return_to_pool_releases_assignment_and_opens_pool(
        self,
        mock_lock_request,
        mock_lock_order,
        mock_ensure_pending_request,
        mock_validate_actor_website,
        mock_get_current_assignment,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(
            preferred_writer=self.writer,
            preferred_writer_status="accepted",
        )
        assignment = self._make_assignment(writer=self.writer)
        request = self._make_request(
            order=order,
            requested_by=self.client_user,
            current_assignment=assignment,
        )

        mock_lock_request.return_value = request
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        result = OrderReassignmentService.approve_return_to_pool(
            reassignment_request=request,
            reviewed_by=self.staff_user,
            internal_notes="Approved",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, order)
        self.assertEqual(assignment.status, ORDER_ASSIGNMENT_STATUS_RELEASED)
        self.assertFalse(assignment.is_current)
        self.assertEqual(
            request.status,
            OrderReassignmentRequestStatus.APPROVED,
        )
        self.assertEqual(
            request.decision,
            OrderReassignmentDecision.RETURN_TO_POOL,
        )
        self.assertEqual(order.status, ORDER_STATUS_READY_FOR_STAFFING)
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_POOL)
        self.assertEqual(
            order.preferred_writer_status,
            PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
        )
        self.assertEqual(mock_create_timeline_event.call_count, 2)
        first_event = mock_create_timeline_event.call_args_list[0]
        second_event = mock_create_timeline_event.call_args_list[1]
        self.assertEqual(
            first_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REASSIGNED,
        )
        self.assertEqual(
            second_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
        )

    @patch(
        "orders.services.order_reassignment_service."
        "OrderAssignment.objects.create"
    )
    @patch.object(OrderReassignmentService, "_create_timeline_event")
    @patch.object(OrderReassignmentService, "_get_current_assignment")
    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_order")
    @patch.object(OrderReassignmentService, "_lock_request")
    def test_approve_assign_specific_writer_releases_and_reassigns(
        self,
        mock_lock_request,
        mock_lock_order,
        mock_ensure_pending_request,
        mock_validate_actor_website,
        mock_get_current_assignment,
        mock_create_timeline_event,
        mock_assignment_create,
    ) -> None:
        order = self._make_order()
        current_assignment = self._make_assignment(writer=self.writer)
        replacement_assignment = self._make_assignment(writer=self.new_writer)
        replacement_assignment.pk = 201
        request = self._make_request(
            order=order,
            requested_by=self.client_user,
            current_assignment=current_assignment,
        )

        mock_lock_request.return_value = request
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = current_assignment
        mock_assignment_create.return_value = replacement_assignment

        result = OrderReassignmentService.approve_assign_specific_writer(
            reassignment_request=request,
            reviewed_by=self.staff_user,
            assign_to_writer=self.new_writer,
            internal_notes="Reassigned",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, replacement_assignment)
        self.assertEqual(
            current_assignment.status,
            ORDER_ASSIGNMENT_STATUS_RELEASED,
        )
        self.assertFalse(current_assignment.is_current)
        self.assertEqual(
            request.status,
            OrderReassignmentRequestStatus.APPROVED,
        )
        self.assertEqual(
            request.decision,
            OrderReassignmentDecision.ASSIGN_SPECIFIC_WRITER,
        )
        self.assertEqual(request.assign_to_writer, self.new_writer)
        self.assertEqual(order.status, ORDER_STATUS_IN_PROGRESS)
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_HIDDEN)
        mock_assignment_create.assert_called_once_with(
            website=order.website,
            order=order,
            writer=self.new_writer,
            assigned_by=self.staff_user,
            source=ORDER_ASSIGNMENT_SOURCE_REASSIGNMENT,
            status=ORDER_ASSIGNMENT_STATUS_ACTIVE,
            is_current=True,
            source_interest=None,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_REASSIGNED,
        )

    @patch.object(OrderReassignmentService, "_validate_actor_website")
    @patch.object(OrderReassignmentService, "_ensure_pending_request")
    @patch.object(OrderReassignmentService, "_lock_order")
    @patch.object(OrderReassignmentService, "_lock_request")
    @patch.object(OrderReassignmentService, "_get_current_assignment")
    def test_approve_assign_specific_writer_fails_without_current_assignment(
        self,
        mock_get_current_assignment,
        mock_lock_request,
        mock_lock_order,
        mock_ensure_pending_request,
        mock_validate_actor_website,
    ) -> None:
        order = self._make_order()
        request = self._make_request(
            order=order,
            requested_by=self.client_user,
            current_assignment=None,
        )

        mock_lock_request.return_value = request
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        with self.assertRaisesMessage(
            ValidationError,
            "A current assignment is required for reassignment.",
        ):
            OrderReassignmentService.approve_assign_specific_writer(
                reassignment_request=request,
                reviewed_by=self.staff_user,
                assign_to_writer=self.new_writer,
            )

    def test_ensure_order_can_be_reassigned_blocks_non_in_progress(self) -> None:
        order = self._make_order(status=ORDER_STATUS_READY_FOR_STAFFING)

        with self.assertRaisesMessage(
            ValidationError,
            "Only in progress orders can be reassigned.",
        ):
            OrderReassignmentService._ensure_order_can_be_reassigned(order)

    @patch(
        "orders.services.order_reassignment_service."
        "OrderReassignmentRequest.objects.select_for_update"
    )
    def test_ensure_no_pending_request_raises_when_pending_exists(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order()
        mock_select_for_update.return_value.filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has a pending reassignment request.",
        ):
            OrderReassignmentService._ensure_no_pending_request(order)

    def test_ensure_pending_request_raises_for_non_pending_request(self) -> None:
        order = self._make_order()
        assignment = self._make_assignment()
        request = self._make_request(
            order=order,
            requested_by=self.writer,
            current_assignment=assignment,
            status=OrderReassignmentRequestStatus.REJECTED,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only pending reassignment requests can be reviewed.",
        ):
            OrderReassignmentService._ensure_pending_request(request)

    def test_validate_actor_website_raises_for_cross_tenant_actor(self) -> None:
        order = self._make_order()
        foreign_actor = SimpleNamespace(pk=77, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            OrderReassignmentService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )