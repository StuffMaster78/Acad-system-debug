from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from orders.services.writer_order_fit_service import (
    WriterOrderFitDecision,
    WriterOrderFitService,
)


class WriterOrderFitServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)

    def _make_order(
        self,
        *,
        total_price=50,
        pages=5,
        hot_flag_exists=False,
        hvo_flag_exists=False,
        writer_deadline=None,
    ) -> MagicMock:
        order = MagicMock()
        order.website = self.website
        order.total_price = total_price
        order.pages = pages
        order.writer_deadline = writer_deadline

        flags_manager = MagicMock()
        filter_result = MagicMock()
        flags_manager.filter.return_value = filter_result

        def filter_side_effect(**kwargs):
            result = MagicMock()
            flag_key = kwargs.get("flag_key")
            if flag_key == "hvo":
                result.exists.return_value = hvo_flag_exists
            elif flag_key == "hot":
                result.exists.return_value = hot_flag_exists
            else:
                result.exists.return_value = False
            return result

        flags_manager.filter.side_effect = filter_side_effect
        order.flags = flags_manager
        return order

    def _make_writer(
        self,
        *,
        level: int | None = None,
        profile_level: int | None = None,
    ) -> MagicMock:
        writer = MagicMock()
        if level is not None:
            writer.level = level
        else:
            if hasattr(writer, "level"):
                del writer.level

        if profile_level is not None:
            writer.writer_profile = SimpleNamespace(level=profile_level)
        else:
            writer.writer_profile = None
        return writer

    def test_get_fit_decision_returns_sufficient_when_level_matches(self) -> None:
        order = self._make_order(total_price=40, pages=3)
        writer = self._make_writer(level=2)

        result = WriterOrderFitService.get_fit_decision(
            writer=writer,
            order=order,
        )

        self.assertIsInstance(result, WriterOrderFitDecision)
        self.assertTrue(result.can_handle)
        self.assertEqual(result.required_level, 1)
        self.assertEqual(result.writer_level, 2)
        self.assertEqual(result.reason, "writer_level_sufficient")
        self.assertFalse(result.is_high_value_order)
        self.assertFalse(result.is_hot_order)

    def test_get_fit_decision_returns_insufficient_when_level_too_low(self) -> None:
        order = self._make_order(total_price=250, pages=3)
        writer = self._make_writer(level=1)

        result = WriterOrderFitService.get_fit_decision(
            writer=writer,
            order=order,
        )

        self.assertFalse(result.can_handle)
        self.assertEqual(result.required_level, 3)
        self.assertEqual(result.writer_level, 1)
        self.assertEqual(result.reason, "writer_level_insufficient")
        self.assertTrue(result.is_high_value_order)

    def test_can_writer_handle_order_returns_true(self) -> None:
        order = self._make_order(total_price=40, pages=3)
        writer = self._make_writer(level=1)

        result = WriterOrderFitService.can_writer_handle_order(
            writer=writer,
            order=order,
        )

        self.assertTrue(result)

    def test_can_writer_handle_order_returns_false(self) -> None:
        order = self._make_order(total_price=300, pages=20)
        writer = self._make_writer(level=1)

        result = WriterOrderFitService.can_writer_handle_order(
            writer=writer,
            order=order,
        )

        self.assertFalse(result)

    def test_validate_writer_assignment_raises_when_insufficient(self) -> None:
        order = self._make_order(total_price=300, pages=20)
        writer = self._make_writer(level=1)

        with self.assertRaisesMessage(
            Exception,
            "Writer level is insufficient for this order.",
        ):
            WriterOrderFitService.validate_writer_assignment(
                writer=writer,
                order=order,
            )

    def test_validate_writer_assignment_passes_when_sufficient(self) -> None:
        order = self._make_order(total_price=300, pages=20)
        writer = self._make_writer(level=3)

        WriterOrderFitService.validate_writer_assignment(
            writer=writer,
            order=order,
        )

    def test_get_required_level_defaults_to_base_level(self) -> None:
        order = self._make_order(total_price=50, pages=5)

        result = WriterOrderFitService.get_required_level(order=order)

        self.assertEqual(result, 1)

    def test_get_required_level_uses_hvo_level(self) -> None:
        order = self._make_order(total_price=250, pages=5)

        result = WriterOrderFitService.get_required_level(order=order)

        self.assertEqual(result, 3)

    def test_get_required_level_uses_hot_level(self) -> None:
        order = self._make_order(total_price=50, pages=5, hot_flag_exists=True)

        result = WriterOrderFitService.get_required_level(order=order)

        self.assertEqual(result, 2)

    def test_get_required_level_uses_large_page_count_level(self) -> None:
        order = self._make_order(total_price=50, pages=15)

        result = WriterOrderFitService.get_required_level(order=order)

        self.assertEqual(result, 2)

    def test_get_required_level_uses_max_of_conditions(self) -> None:
        order = self._make_order(total_price=300, pages=20, hot_flag_exists=True)

        result = WriterOrderFitService.get_required_level(order=order)

        self.assertEqual(result, 3)

    def test_is_high_value_order_uses_active_flags_when_present(self) -> None:
        order = self._make_order(
            total_price=10,
            pages=1,
            hvo_flag_exists=True,
        )

        result = WriterOrderFitService._is_high_value_order(order=order)

        self.assertTrue(result)

    def test_is_high_value_order_falls_back_to_total_price_or_pages(self) -> None:
        order = self._make_order(total_price=250, pages=1)

        result = WriterOrderFitService._is_high_value_order(order=order)

        self.assertTrue(result)

    def test_is_hot_order_uses_active_flags_when_present(self) -> None:
        order = self._make_order(
            total_price=10,
            pages=1,
            hot_flag_exists=True,
        )

        result = WriterOrderFitService._is_hot_order(order=order)

        self.assertTrue(result)

    def test_get_writer_level_uses_direct_writer_level(self) -> None:
        writer = self._make_writer(level=4)

        result = WriterOrderFitService._get_writer_level(writer=writer)

        self.assertEqual(result, 4)

    def test_get_writer_level_uses_profile_level_when_direct_missing(self) -> None:
        writer = self._make_writer(level=None, profile_level=3)

        result = WriterOrderFitService._get_writer_level(writer=writer)

        self.assertEqual(result, 3)

    def test_get_writer_level_defaults_to_one(self) -> None:
        writer = self._make_writer(level=None, profile_level=None)

        result = WriterOrderFitService._get_writer_level(writer=writer)

        self.assertEqual(result, 1)