from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.selectors.order_adjustment_selector import OrderAdjustmentSelector


class OrderAdjustmentSelectorTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=10)

    @patch(
        "orders.selectors.order_adjustment_selector."
        "OrderAdjustmentRequest.objects.filter"
    )
    def test_base_queryset_scopes_by_website(self, mock_filter: Any) -> None:
        OrderAdjustmentSelector.base_queryset(website=self.website)

        mock_filter.assert_called_once_with(website=self.website)
        mock_filter.return_value.select_related.assert_called_once_with(
            "order",
            "requested_by",
            "reviewed_by",
            "current_proposal",
            "accepted_proposal",
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_pending_client_response(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.pending_client_response(
            website=self.website,
        )

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            status="pending_client_response",
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_client_countered(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.client_countered(website=self.website)

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            status="client_countered",
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_funding_pending(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.funding_pending(website=self.website)

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            status="funding_pending",
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_counter_funded_final(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.counter_funded_final(website=self.website)

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            status="counter_funded_final",
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_open_scope_increments(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.open_scope_increments(website=self.website)

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            adjustment_kind="scope_increment",
            applied_at__isnull=True,
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_open_extra_services(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.open_extra_services(website=self.website)

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            adjustment_kind="extra_service",
            applied_at__isnull=True,
        )

    @patch.object(OrderAdjustmentSelector, "base_queryset")
    def test_post_counter_escalations(self, mock_base: Any) -> None:
        OrderAdjustmentSelector.post_counter_escalations(
            website=self.website,
        )

        mock_base.assert_called_once_with(website=self.website)
        mock_base.return_value.filter.assert_called_once_with(
            escalated_after_counter=True,
            resolved_at__isnull=True,
        )