from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.services.adjustment_scope_application_service import (
    AdjustmentScopeApplicationService,
)


class AdjustmentScopeApplicationServiceTests(SimpleTestCase):
    def _order(self) -> Any:
        return cast(
            Any,
            SimpleNamespace(
                pk=100,
                website=SimpleNamespace(pk=10),
                base_quantity=4,
                total_price=Decimal("120.00"),
                writer_compensation=Decimal("60.00"),
                currency="USD",
                service_family="writing",
                service_code="essay",
                pricing_snapshot=None,
                preferred_writer=SimpleNamespace(pk=20),
                save=lambda *args, **kwargs: None,
            ),
        )

    def _scope_adjustment(self) -> Any:
        order = self._order()
        return cast(
            Any,
            SimpleNamespace(
                pk=1,
                website=order.website,
                order=order,
                adjustment_kind="scope_increment",
                adjustment_type="page_increase",
                unit_type="page",
                current_quantity=4,
                requested_quantity=6,
                countered_quantity=5,
                request_total_amount=Decimal("60.00"),
                counter_total_amount=Decimal("30.00"),
                request_writer_compensation_amount=Decimal("30.00"),
                counter_writer_compensation_amount=Decimal("15.00"),
                request_pricing_payload={"total_price": "60.00"},
                counter_pricing_payload={"total_price": "30.00"},
                source_pricing_snapshot=None,
                counter_pricing_snapshot=None,
                applied_at=None,
                is_counter_final=False,
                save=lambda *args, **kwargs: None,
            ),
        )

    def _extra_service_adjustment(self) -> Any:
        order = self._order()
        return cast(
            Any,
            SimpleNamespace(
                pk=2,
                website=order.website,
                order=order,
                adjustment_kind="extra_service",
                adjustment_type="extra_service",
                unit_type="other",
                extra_service_code="speaker_notes",
                requested_quantity=1,
                countered_quantity=None,
                request_total_amount=Decimal("25.00"),
                counter_total_amount=Decimal("0.00"),
                request_writer_compensation_amount=Decimal("10.00"),
                counter_writer_compensation_amount=Decimal("0.00"),
                request_pricing_payload={"total_price": "25.00"},
                counter_pricing_payload={},
                source_pricing_snapshot=None,
                counter_pricing_snapshot=None,
                applied_at=None,
                is_counter_final=False,
                save=lambda *args, **kwargs: None,
            ),
        )

    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderCompensationAdjustment.objects.create"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderPricingSnapshotService.record_current_snapshot"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderItem.objects.create"
    )
    def test_apply_funded_scope_increment_updates_order_and_creates_line_item(
        self,
        mock_item_create: Any,
        mock_snapshot: Any,
        mock_compensation: Any,
    ) -> None:
        adjustment = self._scope_adjustment()

        result = AdjustmentScopeApplicationService.apply_funded_scope_increment(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        self.assertEqual(result.base_quantity, 5)
        self.assertEqual(result.total_price, Decimal("150.00"))
        self.assertEqual(result.writer_compensation, Decimal("75.00"))
        self.assertTrue(adjustment.is_counter_final)
        mock_item_create.assert_called_once()
        mock_snapshot.assert_called_once()
        mock_compensation.assert_called_once()

        item_kwargs = mock_item_create.call_args.kwargs
        self.assertEqual(item_kwargs["item_kind"], "scope_unit")
        self.assertEqual(item_kwargs["unit_type"], "page")
        self.assertEqual(item_kwargs["quantity"], 1)
        self.assertEqual(item_kwargs["total_price"], Decimal("30.00"))

    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderCompensationAdjustment.objects.create"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderPricingSnapshotService.record_current_snapshot"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderItem.objects.create"
    )
    def test_apply_funded_extra_service_does_not_change_base_quantity(
        self,
        mock_item_create: Any,
        mock_snapshot: Any,
        mock_compensation: Any,
    ) -> None:
        adjustment = self._extra_service_adjustment()

        result = AdjustmentScopeApplicationService.apply_funded_extra_service(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        self.assertEqual(result.base_quantity, 4)
        self.assertEqual(result.total_price, Decimal("145.00"))
        self.assertEqual(result.writer_compensation, Decimal("70.00"))
        mock_item_create.assert_called_once()
        mock_snapshot.assert_called_once()
        mock_compensation.assert_called_once()

        item_kwargs = mock_item_create.call_args.kwargs
        self.assertEqual(item_kwargs["item_kind"], "extra_service")
        self.assertEqual(item_kwargs["service_code"], "speaker_notes")
        self.assertEqual(item_kwargs["quantity"], 1)
        self.assertEqual(item_kwargs["total_price"], Decimal("25.00"))

    @patch.object(
        AdjustmentScopeApplicationService,
        "apply_funded_scope_increment",
    )
    def test_apply_funded_adjustment_dispatches_scope_increment(
        self,
        mock_apply_scope: Any,
    ) -> None:
        adjustment = self._scope_adjustment()

        AdjustmentScopeApplicationService.apply_funded_adjustment(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        mock_apply_scope.assert_called_once_with(
            adjustment_request=adjustment,
            triggered_by=None,
        )

    @patch.object(
        AdjustmentScopeApplicationService,
        "apply_funded_extra_service",
    )
    def test_apply_funded_adjustment_dispatches_extra_service(
        self,
        mock_apply_extra: Any,
    ) -> None:
        adjustment = self._extra_service_adjustment()

        AdjustmentScopeApplicationService.apply_funded_adjustment(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        mock_apply_extra.assert_called_once_with(
            adjustment_request=adjustment,
            triggered_by=None,
        )

    def test_apply_funded_adjustment_is_idempotent_if_already_applied(
        self,
    ) -> None:
        adjustment = self._scope_adjustment()
        adjustment.applied_at = object()

        result = AdjustmentScopeApplicationService.apply_funded_adjustment(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        self.assertEqual(result, adjustment.order)


    @patch(
        "orders.services.adjustment_scope_application_service."
        "ProgressiveDeliveryService.create_plan_from_adjustment"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderCompensationAdjustment.objects.create"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderPricingSnapshotService.record_current_snapshot"
    )
    @patch(
        "orders.services.adjustment_scope_application_service."
        "OrderItem.objects.create"
    )
    def test_apply_funded_extra_service_creates_progressive_plan_when_needed(
        self,
        mock_item_create: Any,
        mock_snapshot: Any,
        mock_compensation: Any,
        mock_create_plan: Any,
    ) -> None:
        adjustment = self._extra_service_adjustment()
        adjustment.extra_service_code = "progressive_delivery"
        adjustment.request_pricing_payload = {
            "progressive_delivery": {
                "milestones": [
                    {
                        "title": "50% draft",
                        "due_at": "2026-05-01T12:00:00Z",
                        "percentage": 50,
                    }
                ]
            }
        }

        AdjustmentScopeApplicationService.apply_funded_extra_service(
            adjustment_request=adjustment,
            triggered_by=None,
        )

        mock_create_plan.assert_called_once_with(
            adjustment_request=adjustment,
            created_by=None,
        )