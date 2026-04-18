from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_STATUS_SUBMITTED,
    ORDER_VISIBILITY_POOL,
    ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
)
from orders.selectors.order_visibility_selector import (
    OrderVisibilitySelector,
)


class OrderVisibilitySelectorTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.other_website = SimpleNamespace(pk=2)

        self.client_user = SimpleNamespace(
            pk=10,
            website=self.website,
            website_id=1,
        )
        self.writer_user = SimpleNamespace(
            pk=20,
            website=self.website,
            website_id=1,
        )
        self.other_writer = SimpleNamespace(
            pk=21,
            website=self.website,
            website_id=1,
        )
        self.staff_user = SimpleNamespace(
            pk=30,
            website=self.website,
            website_id=1,
        )
        self.foreign_writer = SimpleNamespace(
            pk=40,
            website=self.other_website,
            website_id=2,
        )

    def _make_assignments_manager(self, *, exists_result: bool) -> MagicMock:
        manager = MagicMock()
        manager.filter.return_value.exists.return_value = exists_result
        return manager

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_READY_FOR_STAFFING,
        visibility_mode: str = ORDER_VISIBILITY_POOL,
        preferred_writer=None,
        client=None,
        website=None,
        assignments_exists: bool = False,
    ) -> MagicMock:
        website = website or self.website
        client = client or self.client_user

        order = MagicMock()
        order.pk = 100
        order.website = website
        order.status = status
        order.visibility_mode = visibility_mode
        order.preferred_writer = preferred_writer
        order.client = client
        order.assignments = self._make_assignments_manager(
            exists_result=assignments_exists
        )
        return order

    def test_can_writer_view_order_returns_pool_visible(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = OrderVisibilitySelector.can_writer_view_order(
            writer=self.writer_user,
            order=order,
        )

        self.assertTrue(result.can_view)
        self.assertEqual(result.visibility_reason, "pool_visible")
        self.assertTrue(result.is_pool_visible)
        self.assertFalse(result.is_preferred_writer_visible)
        self.assertFalse(result.is_current_assignment_visible)

    def test_can_writer_view_order_returns_preferred_writer_visible(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.writer_user,
        )

        result = OrderVisibilitySelector.can_writer_view_order(
            writer=self.writer_user,
            order=order,
        )

        self.assertTrue(result.can_view)
        self.assertEqual(
            result.visibility_reason,
            "preferred_writer_invitation",
        )
        self.assertFalse(result.is_pool_visible)
        self.assertTrue(result.is_preferred_writer_visible)
        self.assertFalse(result.is_current_assignment_visible)

    def test_can_writer_view_order_returns_current_assignment_visible(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_IN_PROGRESS,
            visibility_mode=ORDER_VISIBILITY_POOL,
            assignments_exists=True,
        )

        result = OrderVisibilitySelector.can_writer_view_order(
            writer=self.writer_user,
            order=order,
        )

        self.assertTrue(result.can_view)
        self.assertEqual(result.visibility_reason, "current_assignment")
        self.assertFalse(result.is_pool_visible)
        self.assertFalse(result.is_preferred_writer_visible)
        self.assertTrue(result.is_current_assignment_visible)

    def test_can_writer_view_order_blocks_cross_tenant(self) -> None:
        order = self._make_order(website=self.website)

        result = OrderVisibilitySelector.can_writer_view_order(
            writer=self.foreign_writer,
            order=order,
        )

        self.assertFalse(result.can_view)
        self.assertEqual(result.visibility_reason, "cross_tenant_blocked")

    def test_can_writer_view_order_returns_not_visible(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.other_writer,
        )

        result = OrderVisibilitySelector.can_writer_view_order(
            writer=self.writer_user,
            order=order,
        )

        self.assertFalse(result.can_view)
        self.assertEqual(result.visibility_reason, "not_visible")

    def test_can_client_view_order_returns_order_owner(self) -> None:
        order = self._make_order(client=self.client_user)

        result = OrderVisibilitySelector.can_client_view_order(
            client=self.client_user,
            order=order,
        )

        self.assertTrue(result.can_view)
        self.assertEqual(result.visibility_reason, "order_owner")
        self.assertTrue(result.is_client_visible)

    def test_can_client_view_order_blocks_non_owner(self) -> None:
        other_client = SimpleNamespace(
            pk=999,
            website=self.website,
            website_id=1,
        )
        order = self._make_order(client=self.client_user)

        result = OrderVisibilitySelector.can_client_view_order(
            client=other_client,
            order=order,
        )

        self.assertFalse(result.can_view)
        self.assertEqual(result.visibility_reason, "not_order_owner")

    def test_can_staff_view_order_allows_same_tenant(self) -> None:
        order = self._make_order(website=self.website)

        result = OrderVisibilitySelector.can_staff_view_order(
            staff_user=self.staff_user,
            order=order,
        )

        self.assertTrue(result.can_view)
        self.assertEqual(result.visibility_reason, "tenant_staff_access")
        self.assertTrue(result.is_staff_visible)

    def test_can_staff_view_order_blocks_cross_tenant(self) -> None:
        foreign_staff = SimpleNamespace(
            pk=77,
            website=self.other_website,
            website_id=2,
        )
        order = self._make_order(website=self.website)

        result = OrderVisibilitySelector.can_staff_view_order(
            staff_user=foreign_staff,
            order=order,
        )

        self.assertFalse(result.can_view)
        self.assertEqual(result.visibility_reason, "cross_tenant_blocked")

    def test_is_pool_visible_to_writer_true(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_POOL,
        )

        result = OrderVisibilitySelector._is_pool_visible_to_writer(
            writer=self.writer_user,
            order=order,
        )

        self.assertTrue(result)

    def test_is_preferred_writer_visible_to_writer_true(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_READY_FOR_STAFFING,
            visibility_mode=ORDER_VISIBILITY_PREFERRED_WRITER_ONLY,
            preferred_writer=self.writer_user,
        )

        result = (
            OrderVisibilitySelector._is_preferred_writer_visible_to_writer(
                writer=self.writer_user,
                order=order,
            )
        )

        self.assertTrue(result)

    def test_is_current_assignment_visible_to_writer_true(self) -> None:
        for status in (
            ORDER_STATUS_IN_PROGRESS,
            ORDER_STATUS_ON_HOLD,
            ORDER_STATUS_SUBMITTED,
        ):
            order = self._make_order(
                status=status,
                assignments_exists=True,
            )

            result = (
                OrderVisibilitySelector
                ._is_current_assignment_visible_to_writer(
                    writer=self.writer_user,
                    order=order,
                )
            )

            self.assertTrue(result)

    def test_is_current_assignment_visible_to_writer_false_without_match(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_IN_PROGRESS,
            assignments_exists=False,
        )

        result = (
            OrderVisibilitySelector
            ._is_current_assignment_visible_to_writer(
                writer=self.writer_user,
                order=order,
            )
        )

        self.assertFalse(result)