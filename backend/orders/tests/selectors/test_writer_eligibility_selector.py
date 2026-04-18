from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_STATUS_SUBMITTED,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
)
from orders.selectors.writer_eligibility_selector import (
    WriterEligibilitySelector,
)


class WriterEligibilitySelectorTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.other_website = SimpleNamespace(pk=2)

        self.writer = SimpleNamespace(
            pk=10,
            website=self.website,
            website_id=1,
        )
        self.other_writer = SimpleNamespace(
            pk=11,
            website=self.website,
            website_id=1,
        )
        self.foreign_writer = SimpleNamespace(
            pk=12,
            website=self.other_website,
            website_id=2,
        )

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_READY_FOR_STAFFING,
        visibility_mode: str = ORDER_VISIBILITY_POOL,
        preferred_writer=None,
        website=None,
    ) -> MagicMock:
        website = website or self.website

        order = MagicMock()
        order.pk = 100
        order.website = website
        order.status = status
        order.visibility_mode = visibility_mode
        order.preferred_writer = preferred_writer
        return order

    def test_build_snapshot_pool_order_allows_bid_and_take(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertTrue(result.can_view_pool)
        self.assertTrue(result.can_bid)
        self.assertTrue(result.can_take)
        self.assertEqual(result.reason, "eligible_for_take")

    def test_build_snapshot_pool_order_blocks_take_when_disabled(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=False,
            bidding_enabled=True,
        )

        self.assertTrue(result.can_view_pool)
        self.assertTrue(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(result.reason, "eligible_for_bid")

    def test_build_snapshot_pool_order_blocks_bid_when_disabled(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=False,
        )

        self.assertTrue(result.can_view_pool)
        self.assertFalse(result.can_bid)
        self.assertTrue(result.can_take)
        self.assertEqual(result.reason, "eligible_for_take")

    def test_build_snapshot_pool_order_blocks_when_actions_disabled(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=False,
            bidding_enabled=False,
        )

        self.assertTrue(result.can_view_pool)
        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(result.reason, "writer_actions_disabled")

    def test_build_snapshot_preferred_writer_visible_allows_bid(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.writer,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertFalse(result.can_view_pool)
        self.assertTrue(result.can_view_preferred_invite)
        self.assertTrue(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(result.reason, "eligible_for_bid")

    def test_build_snapshot_preferred_writer_blocks_non_invited_writer(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.other_writer,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertFalse(result.can_view_pool)
        self.assertFalse(result.can_view_preferred_invite)
        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(result.reason, "preferred_writer_only")

    def test_build_snapshot_blocks_cross_tenant_writer(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.foreign_writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertFalse(result.is_same_tenant)
        self.assertEqual(result.reason, "cross_tenant_blocked")

    def test_build_snapshot_blocks_non_staffing_ready_order(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=1,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertFalse(result.is_order_staffing_ready)
        self.assertEqual(result.reason, "order_not_staffing_ready")

    def test_build_snapshot_blocks_when_writer_at_capacity(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=5,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
        )

        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertFalse(result.has_capacity)
        self.assertEqual(result.reason, "writer_at_capacity")

    def test_build_snapshot_allows_preferred_writer_capacity_override(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.writer,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=5,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
            ignore_capacity_for_preferred_writer=True,
        )

        self.assertFalse(result.has_capacity)
        self.assertTrue(result.can_view_preferred_invite)
        self.assertTrue(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(
            result.reason,
            "preferred_writer_capacity_override",
        )

    def test_build_snapshot_blocks_preferred_writer_without_override(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.writer,
        )

        result = WriterEligibilitySelector.build_snapshot(
            writer=self.writer,
            order=order,
            active_order_count=5,
            max_active_orders=5,
            takes_enabled=True,
            bidding_enabled=True,
            ignore_capacity_for_preferred_writer=False,
        )

        self.assertFalse(result.can_bid)
        self.assertFalse(result.can_take)
        self.assertEqual(result.reason, "writer_at_capacity")

    def test_is_same_tenant_returns_true(self) -> None:
        order = self._make_order()

        result = WriterEligibilitySelector._is_same_tenant(
            writer=self.writer,
            order=order,
        )

        self.assertTrue(result)

    def test_is_same_tenant_returns_false(self) -> None:
        order = self._make_order(website=self.website)

        result = WriterEligibilitySelector._is_same_tenant(
            writer=self.foreign_writer,
            order=order,
        )

        self.assertFalse(result)

    def test_is_preferred_writer_returns_true(self) -> None:
        order = self._make_order(preferred_writer=self.writer)

        result = WriterEligibilitySelector._is_preferred_writer(
            writer=self.writer,
            order=order,
        )

        self.assertTrue(result)

    def test_is_preferred_writer_returns_false(self) -> None:
        order = self._make_order(preferred_writer=self.other_writer)

        result = WriterEligibilitySelector._is_preferred_writer(
            writer=self.writer,
            order=order,
        )

        self.assertFalse(result)

    def test_active_work_statuses_are_expected(self) -> None:
        self.assertEqual(
            WriterEligibilitySelector.ACTIVE_WORK_STATUSES,
            frozenset({
                ORDER_STATUS_IN_PROGRESS,
                ORDER_STATUS_ON_HOLD,
                ORDER_STATUS_SUBMITTED,
            }),
        )