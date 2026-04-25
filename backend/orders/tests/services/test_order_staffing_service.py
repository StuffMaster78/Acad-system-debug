from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
    ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
    ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
    ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_INTEREST_STATUS_ACCEPTED,
    ORDER_INTEREST_STATUS_DECLINED,
    ORDER_INTEREST_STATUS_EXPIRED,
    ORDER_INTEREST_STATUS_PENDING,
    ORDER_INTEREST_STATUS_WITHDRAWN,
    ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
    ORDER_INTEREST_TYPE_REQUEST_TAKE,
    ORDER_INTEREST_TYPE_SHOW_INTEREST,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_ASSIGNED,
    ORDER_TIMELINE_EVENT_INTEREST_CREATED,
    ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
    ORDER_TIMELINE_EVENT_POOL_OPENED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
    ORDER_TIMELINE_EVENT_PREFERRED_WRITER_INVITED,
    ORDER_TIMELINE_EVENT_REASSIGNED,
    ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
    ORDER_VISIBILITY_HIDDEN,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
    PREFERRED_WRITER_STATUS_ACCEPTED,
    PREFERRED_WRITER_STATUS_DECLINED,
    PREFERRED_WRITER_STATUS_EXPIRED,
    PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
    PREFERRED_WRITER_STATUS_INVITED,
    PREFERRED_WRITER_STATUS_NOT_REQUESTED,
)
from orders.services.order_staffing_service import OrderStaffingService


class OrderStaffingServiceTests(SimpleTestCase):
    """
    Unit tests for OrderStaffingService.

    These tests focus on service behavior and orchestration.
    They do not require a full database object graph.
    """

    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.writer = SimpleNamespace(pk=20, website_id=1)
        self.other_writer = SimpleNamespace(pk=21, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)

    def _make_order(
        self,
        *,
        preferred_writer=None,
        status: str = ORDER_STATUS_READY_FOR_STAFFING,
        visibility_mode: str = ORDER_VISIBILITY_POOL,
        preferred_writer_status: str = PREFERRED_WRITER_STATUS_NOT_REQUESTED,
    ) -> Any:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.client_user = self.client_user
        order.preferred_writer = preferred_writer
        order.status = status
        order.visibility_mode = visibility_mode
        order.preferred_writer_status = preferred_writer_status
        order.save = MagicMock()
        return cast(Any, order)

    def _make_interest(
        self,
        *,
        order,
        writer,
        interest_type: str = ORDER_INTEREST_TYPE_SHOW_INTEREST,
        status: str = ORDER_INTEREST_STATUS_PENDING,
    ) -> Any:
        interest = MagicMock()
        interest.pk = 200
        interest.order = order
        interest.writer = writer
        interest.interest_type = interest_type
        interest.status = status
        interest.save = MagicMock()
        return cast(Any, interest)

    def _make_assignment(
        self,
        *,
        writer=None,
        status: str = ORDER_ASSIGNMENT_STATUS_ACTIVE,
        is_current: bool = True,
    ) -> Any:
        assignment = MagicMock()
        assignment.pk = 300
        assignment.writer = writer or self.writer
        assignment.status = status
        assignment.is_current = is_current
        assignment.save = MagicMock()
        return cast(Any, assignment)

    @patch.object(OrderStaffingService, "_open_order_to_pool")
    @patch.object(OrderStaffingService, "_invite_preferred_writer")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    def test_route_order_to_staffing_invites_preferred_writer(
        self,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_no_current_assignment: Any,
        mock_invite_preferred_writer: Any,
        mock_open_order_to_pool: Any,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        mock_lock_order.return_value = order
        mock_invite_preferred_writer.return_value = order

        result = OrderStaffingService.route_order_to_staffing(
            order=order,
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, order)
        mock_invite_preferred_writer.assert_called_once_with(
            order=order,
            triggered_by=self.staff_user,
        )
        mock_open_order_to_pool.assert_not_called()

    @patch.object(OrderStaffingService, "_open_order_to_pool")
    @patch.object(OrderStaffingService, "_invite_preferred_writer")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    def test_route_order_to_staffing_opens_pool_when_no_preferred_writer(
        self,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_no_current_assignment: Any,
        mock_invite_preferred_writer: Any,
        mock_open_order_to_pool: Any,
    ) -> None:
        order = self._make_order(preferred_writer=None)
        mock_lock_order.return_value = order
        mock_open_order_to_pool.return_value = order

        result = OrderStaffingService.route_order_to_staffing(
            order=order,
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, order)
        mock_open_order_to_pool.assert_called_once_with(
            order=order,
            triggered_by=self.staff_user,
        )
        mock_invite_preferred_writer.assert_not_called()

    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.create"
    )
    @patch.object(OrderStaffingService, "_create_timeline_event")
    @patch.object(OrderStaffingService, "_validate_writer_website")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_visibility_mode")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.select_for_update"
    )
    def test_express_interest_creates_interest(
        self,
        mock_select_for_update: Any,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_visibility_mode: Any,
        mock_ensure_no_current_assignment: Any,
        mock_validate_writer_website: Any,
        mock_create_timeline_event: Any,
        mock_interest_create: Any,
    ) -> None:
        order = self._make_order()
        created_interest = self._make_interest(order=order, writer=self.writer)

        mock_lock_order.return_value = order
        mock_select_for_update.return_value.filter.return_value.first.return_value = None
        mock_interest_create.return_value = created_interest

        result = OrderStaffingService.express_interest(
            order=order,
            writer=self.writer,
            message="I can take this",
            triggered_by=self.writer,
        )

        self.assertEqual(result, created_interest)
        mock_interest_create.assert_called_once_with(
            website=order.website,
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_SHOW_INTEREST,
            status=ORDER_INTEREST_STATUS_PENDING,
            message="I can take this",
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_INTEREST_CREATED,
        )

    @patch.object(OrderStaffingService, "_validate_writer_website")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_visibility_mode")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.select_for_update"
    )
    def test_express_interest_blocks_duplicate_pending_interest(
        self,
        mock_select_for_update: Any,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_visibility_mode: Any,
        mock_ensure_no_current_assignment: Any,
        mock_validate_writer_website: Any,
    ) -> None:
        order = self._make_order()
        existing_interest = self._make_interest(order=order, writer=self.writer)

        mock_lock_order.return_value = order
        mock_select_for_update.return_value.filter.return_value.first.return_value = (
            existing_interest
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Writer already has a pending interest for this order.",
        ):
            OrderStaffingService.express_interest(
                order=order,
                writer=self.writer,
            )

    @patch.object(OrderStaffingService, "_create_timeline_event")
    @patch.object(OrderStaffingService, "_lock_interest")
    def test_withdraw_interest_updates_interest_and_logs_event(
        self,
        mock_lock_interest: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order()
        interest = self._make_interest(order=order, writer=self.writer)
        mock_lock_interest.return_value = interest

        result = OrderStaffingService.withdraw_interest(
            interest=interest,
            writer=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, interest)
        self.assertEqual(interest.status, ORDER_INTEREST_STATUS_WITHDRAWN)
        interest.save.assert_called_once()
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_INTEREST_WITHDRAWN,
        )

    @patch.object(OrderStaffingService, "_lock_interest")
    def test_withdraw_interest_blocks_non_owner(
        self,
        mock_lock_interest: Any,
    ) -> None:
        order = self._make_order()
        interest = self._make_interest(order=order, writer=self.other_writer)
        mock_lock_interest.return_value = interest

        with self.assertRaisesMessage(
            ValidationError,
            "Only the writer who created the interest can withdraw it.",
        ):
            OrderStaffingService.withdraw_interest(
                interest=interest,
                writer=self.writer,
            )

    @patch.object(OrderStaffingService, "_mark_order_in_progress")
    @patch.object(OrderStaffingService, "_close_other_open_interests")
    @patch.object(OrderStaffingService, "_create_assignment")
    @patch.object(OrderStaffingService, "_validate_writer_website")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_visibility_mode")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.select_for_update"
    )
    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.create"
    )
    def test_take_order_creates_assignment_and_marks_in_progress(
        self,
        mock_interest_create: Any,
        mock_select_for_update: Any,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_visibility_mode: Any,
        mock_ensure_no_current_assignment: Any,
        mock_validate_writer_website: Any,
        mock_create_assignment: Any,
        mock_close_other_open_interests: Any,
        mock_mark_order_in_progress: Any,
    ) -> None:
        order = self._make_order()
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_REQUEST_TAKE,
            status=ORDER_INTEREST_STATUS_ACCEPTED,
        )
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_order.return_value = order
        mock_select_for_update.return_value.filter.return_value.first.return_value = None
        mock_interest_create.return_value = interest
        mock_create_assignment.return_value = assignment

        result = OrderStaffingService.take_order(
            order=order,
            writer=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, assignment)
        mock_create_assignment.assert_called_once_with(
            order=order,
            writer=self.writer,
            assigned_by=self.writer,
            source=ORDER_ASSIGNMENT_SOURCE_SELF_TAKE,
            source_interest=interest,
        )
        mock_close_other_open_interests.assert_called_once_with(
            order=order,
            keep_interest=interest,
        )
        mock_mark_order_in_progress.assert_called_once()

    @patch.object(OrderStaffingService, "_mark_order_in_progress")
    @patch.object(OrderStaffingService, "_close_other_open_interests")
    @patch.object(OrderStaffingService, "_create_assignment")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    @patch.object(OrderStaffingService, "_lock_interest")
    def test_assign_from_interest_accepts_interest_and_creates_assignment(
        self,
        mock_lock_interest: Any,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_no_current_assignment: Any,
        mock_create_assignment: Any,
        mock_close_other_open_interests: Any,
        mock_mark_order_in_progress: Any,
    ) -> None:
        order = self._make_order()
        interest = self._make_interest(order=order, writer=self.writer)
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_interest.return_value = interest
        mock_lock_order.return_value = order
        mock_create_assignment.return_value = assignment

        result = OrderStaffingService.assign_from_interest(
            interest=interest,
            assigned_by=self.staff_user,
        )

        self.assertEqual(result, assignment)
        self.assertEqual(interest.status, ORDER_INTEREST_STATUS_ACCEPTED)
        interest.save.assert_called_once()
        mock_create_assignment.assert_called_once_with(
            order=order,
            writer=self.writer,
            assigned_by=self.staff_user,
            source=ORDER_ASSIGNMENT_SOURCE_ACCEPTED_INTEREST,
            source_interest=interest,
        )
        mock_close_other_open_interests.assert_called_once_with(
            order=order,
            keep_interest=interest,
        )
        mock_mark_order_in_progress.assert_called_once()

    @patch.object(OrderStaffingService, "_mark_order_in_progress")
    @patch.object(OrderStaffingService, "_close_other_open_interests")
    @patch.object(OrderStaffingService, "_create_assignment")
    @patch.object(OrderStaffingService, "_validate_writer_website")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    def test_assign_directly_creates_assignment(
        self,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_no_current_assignment: Any,
        mock_validate_writer_website: Any,
        mock_create_assignment: Any,
        mock_close_other_open_interests: Any,
        mock_mark_order_in_progress: Any,
    ) -> None:
        order = self._make_order()
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_order.return_value = order
        mock_create_assignment.return_value = assignment

        result = OrderStaffingService.assign_directly(
            order=order,
            writer=self.writer,
            assigned_by=self.staff_user,
        )

        self.assertEqual(result, assignment)
        mock_create_assignment.assert_called_once_with(
            order=order,
            writer=self.writer,
            assigned_by=self.staff_user,
            source=ORDER_ASSIGNMENT_SOURCE_STAFF_ASSIGNMENT,
            source_interest=None,
        )
        mock_close_other_open_interests.assert_called_once_with(order=order)
        mock_mark_order_in_progress.assert_called_once()

    @patch.object(
        OrderStaffingService,
        "_ensure_pending_preferred_invitation_for_writer",
    )
    @patch.object(OrderStaffingService, "_mark_order_in_progress")
    @patch.object(OrderStaffingService, "_close_other_open_interests")
    @patch.object(OrderStaffingService, "_create_assignment")
    @patch.object(OrderStaffingService, "_validate_writer_website")
    @patch.object(OrderStaffingService, "_ensure_no_current_assignment")
    @patch.object(OrderStaffingService, "_ensure_status")
    @patch.object(OrderStaffingService, "_lock_order")
    @patch.object(OrderStaffingService, "_lock_interest")
    def test_accept_preferred_writer_invitation_creates_assignment(
        self,
        mock_lock_interest: Any,
        mock_lock_order: Any,
        mock_ensure_status: Any,
        mock_ensure_no_current_assignment: Any,
        mock_validate_writer_website: Any,
        mock_create_assignment: Any,
        mock_close_other_open_interests: Any,
        mock_mark_order_in_progress: Any,
        mock_ensure_pending_preferred_invitation_for_writer: Any,
    ) -> None:
        order = self._make_order(
            preferred_writer=self.writer,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer_status=PREFERRED_WRITER_STATUS_INVITED,
        )
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
        )
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_interest.return_value = interest
        mock_lock_order.return_value = order
        mock_create_assignment.return_value = assignment

        result = OrderStaffingService.accept_preferred_writer_invitation(
            interest=interest,
            writer=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, assignment)
        mock_ensure_pending_preferred_invitation_for_writer.assert_called_once_with(
            interest=interest,
            writer=self.writer,
            action="accept",
        )
        self.assertEqual(interest.status, ORDER_INTEREST_STATUS_ACCEPTED)
        mock_create_assignment.assert_called_once_with(
            order=order,
            writer=self.writer,
            assigned_by=self.writer,
            source=ORDER_ASSIGNMENT_SOURCE_PREFERRED_WRITER_ACCEPTANCE,
            source_interest=interest,
        )
        mock_close_other_open_interests.assert_called_once_with(
            order=order,
            keep_interest=interest,
        )
        mock_mark_order_in_progress.assert_called_once()

    @patch.object(
        OrderStaffingService,
        "_ensure_pending_preferred_invitation_for_writer",
    )
    @patch.object(OrderStaffingService, "_lock_order")
    @patch.object(OrderStaffingService, "_lock_interest")
    @patch.object(OrderStaffingService, "_create_timeline_event")
    def test_decline_preferred_writer_invitation_opens_pool(
        self,
        mock_create_timeline_event: Any,
        mock_lock_interest: Any,
        mock_lock_order: Any,
        mock_ensure_pending_preferred_invitation_for_writer: Any,
    ) -> None:
        order = self._make_order(
            preferred_writer=self.writer,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer_status=PREFERRED_WRITER_STATUS_INVITED,
        )
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
        )

        mock_lock_interest.return_value = interest
        mock_lock_order.return_value = order

        result = OrderStaffingService.decline_preferred_writer_invitation(
            interest=interest,
            writer=self.writer,
            triggered_by=self.writer,
        )

        self.assertEqual(result, order)
        mock_ensure_pending_preferred_invitation_for_writer.assert_called_once_with(
            interest=interest,
            writer=self.writer,
            action="decline",
        )
        self.assertEqual(interest.status, ORDER_INTEREST_STATUS_DECLINED)
        self.assertEqual(
            order.preferred_writer_status,
            PREFERRED_WRITER_STATUS_DECLINED,
        )
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_POOL)
        self.assertEqual(mock_create_timeline_event.call_count, 2)
        first_event = mock_create_timeline_event.call_args_list[0]
        second_event = mock_create_timeline_event.call_args_list[1]
        self.assertEqual(
            first_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_PREFERRED_WRITER_DECLINED,
        )
        self.assertEqual(
            second_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_POOL_OPENED,
        )

    @patch.object(OrderStaffingService, "_lock_order")
    @patch.object(OrderStaffingService, "_lock_interest")
    @patch.object(OrderStaffingService, "_create_timeline_event")
    def test_expire_preferred_writer_invitation_opens_pool(
        self,
        mock_create_timeline_event: Any,
        mock_lock_interest: Any,
        mock_lock_order: Any,
    ) -> None:
        order = self._make_order(
            preferred_writer=self.writer,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer_status=PREFERRED_WRITER_STATUS_INVITED,
        )
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
        )

        mock_lock_interest.return_value = interest
        mock_lock_order.return_value = order

        result = OrderStaffingService.expire_preferred_writer_invitation(
            interest=interest,
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, order)
        self.assertEqual(interest.status, ORDER_INTEREST_STATUS_EXPIRED)
        self.assertEqual(
            order.preferred_writer_status,
            PREFERRED_WRITER_STATUS_EXPIRED,
        )
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_POOL)
        self.assertEqual(mock_create_timeline_event.call_count, 2)
        first_event = mock_create_timeline_event.call_args_list[0]
        second_event = mock_create_timeline_event.call_args_list[1]
        self.assertEqual(
            first_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_PREFERRED_WRITER_EXPIRED,
        )
        self.assertEqual(
            second_event.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_POOL_OPENED,
        )

    @patch(
        "orders.services.order_staffing_service.validate_status_transition"
    )
    @patch.object(OrderStaffingService, "_lock_order")
    @patch.object(OrderStaffingService, "_get_current_assignment")
    @patch.object(OrderStaffingService, "_create_timeline_event")
    def test_release_to_pool_releases_assignment_and_restores_visibility(
        self,
        mock_create_timeline_event: Any,
        mock_get_current_assignment: Any,
        mock_lock_order: Any,
        mock_validate_status_transition: Any,
    ) -> None:
        order = self._make_order(
            preferred_writer=self.writer,
            status=ORDER_STATUS_IN_PROGRESS,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer_status=PREFERRED_WRITER_STATUS_ACCEPTED,
        )
        assignment = self._make_assignment(writer=self.writer)

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        result = OrderStaffingService.release_to_pool(
            order=order,
            released_by=self.staff_user,
            reason="Client requested reassignment",
        )

        self.assertEqual(result, order)
        self.assertEqual(
            assignment.status,
            ORDER_ASSIGNMENT_STATUS_RELEASED,
        )
        self.assertFalse(assignment.is_current)
        self.assertEqual(order.status, ORDER_STATUS_READY_FOR_STAFFING)
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_POOL)
        self.assertEqual(
            order.preferred_writer_status,
            PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
        )
        mock_validate_status_transition.assert_called_once_with(
            from_status=ORDER_STATUS_IN_PROGRESS,
            to_status=ORDER_STATUS_READY_FOR_STAFFING,
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

    @patch.object(OrderStaffingService, "_get_current_assignment")
    def test_ensure_no_current_assignment_raises_when_active_assignment_exists(
        self,
        mock_get_current_assignment: Any,
    ) -> None:
        order = self._make_order()
        mock_get_current_assignment.return_value = self._make_assignment()

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has an active assignment.",
        ):
            OrderStaffingService._ensure_no_current_assignment(order)

    @patch.object(OrderStaffingService, "_get_current_assignment")
    def test_ensure_no_current_assignment_passes_when_no_active_assignment(
        self,
        mock_get_current_assignment: Any,
    ) -> None:
        order = self._make_order()
        mock_get_current_assignment.return_value = None

        OrderStaffingService._ensure_no_current_assignment(order)

    @patch(
        "orders.services.order_staffing_service.OrderInterest.objects.select_for_update"
    )
    def test_ensure_no_open_preferred_invitation_raises_when_pending_exists(
        self,
        mock_select_for_update: Any,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        mock_select_for_update.return_value.filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has an open preferred writer invitation.",
        ):
            OrderStaffingService._ensure_no_open_preferred_invitation(order)

    def test_validate_writer_website_raises_for_cross_tenant_writer(self) -> None:
        order = self._make_order()
        foreign_writer = SimpleNamespace(pk=55, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Writer website must match order website.",
        ):
            OrderStaffingService._validate_writer_website(
                writer=foreign_writer,
                order=order,
            )

    def test_validate_writer_website_allows_same_tenant_writer(self) -> None:
        order = self._make_order()

        OrderStaffingService._validate_writer_website(
            writer=self.writer,
            order=order,
        )

    @patch(
        "orders.services.order_staffing_service.validate_status_transition"
    )
    @patch.object(OrderStaffingService, "_create_timeline_event")
    def test_mark_order_in_progress_updates_status_and_logs_assignment(
        self,
        mock_create_timeline_event: Any,
        mock_validate_status_transition: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
            preferred_writer_status=PREFERRED_WRITER_STATUS_INVITED,
        )

        OrderStaffingService._mark_order_in_progress(
            order=order,
            actor=self.staff_user,
            metadata={"assignment_id": 300},
        )

        mock_validate_status_transition.assert_called_once_with(
            from_status=ORDER_STATUS_READY_FOR_STAFFING,
            to_status=ORDER_STATUS_IN_PROGRESS,
        )
        self.assertEqual(order.status, ORDER_STATUS_IN_PROGRESS)
        self.assertEqual(order.visibility_mode, ORDER_VISIBILITY_HIDDEN)
        self.assertEqual(
            order.preferred_writer_status,
            PREFERRED_WRITER_STATUS_ACCEPTED,
        )
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )
        mock_create_timeline_event.assert_called_once_with(
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNED,
            actor=self.staff_user,
            metadata={"assignment_id": 300},
        )

    def test_ensure_pending_preferred_invitation_for_writer_rejects_wrong_writer(
        self,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
            status=ORDER_INTEREST_STATUS_PENDING,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only the invited writer can accept this invitation.",
        ):
            OrderStaffingService._ensure_pending_preferred_invitation_for_writer(
                interest=interest,
                writer=self.other_writer,
                action="accept",
            )

    def test_ensure_pending_preferred_invitation_for_writer_rejects_wrong_type(
        self,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_SHOW_INTEREST,
            status=ORDER_INTEREST_STATUS_PENDING,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Interest is not a preferred writer invitation.",
        ):
            OrderStaffingService._ensure_pending_preferred_invitation_for_writer(
                interest=interest,
                writer=self.writer,
                action="accept",
            )

    def test_ensure_pending_preferred_invitation_for_writer_rejects_non_pending_status(
        self,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
            status=ORDER_INTEREST_STATUS_DECLINED,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only pending preferred writer invitations can be accepted.",
        ):
            OrderStaffingService._ensure_pending_preferred_invitation_for_writer(
                interest=interest,
                writer=self.writer,
                action="accept",
            )

    def test_ensure_pending_preferred_invitation_for_writer_passes_for_valid_interest(
        self,
    ) -> None:
        order = self._make_order(preferred_writer=self.writer)
        interest = self._make_interest(
            order=order,
            writer=self.writer,
            interest_type=ORDER_INTEREST_TYPE_PREFERRED_WRITER_INVITATION,
            status=ORDER_INTEREST_STATUS_PENDING,
        )

        OrderStaffingService._ensure_pending_preferred_invitation_for_writer(
            interest=interest,
            writer=self.writer,
            action="accept",
        )