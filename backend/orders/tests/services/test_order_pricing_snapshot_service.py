from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.services.order_pricing_snapshot_service import (
    OrderPricingSnapshotService,
)


class OrderPricingSnapshotServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=10)
        self.order = cast(
            Any,
            SimpleNamespace(
                pk=100,
                website=self.website,
                currency="USD",
            ),
        )
        self.created_by = cast(Any, SimpleNamespace(pk=20))
        self.source_pricing_snapshot = cast(
            Any,
            SimpleNamespace(pk=11),
        )

    @patch(
        "orders.services.order_pricing_snapshot_service."
        "OrderPricingSnapshot.objects.create"
    )
    @patch(
        "orders.services.order_pricing_snapshot_service."
        "OrderPricingSnapshot.objects.filter"
    )
    def test_record_current_snapshot_marks_old_snapshots_not_current_and_creates_new(
        self,
        mock_filter: Any,
        mock_create: Any,
    ) -> None:
        created_snapshot = cast(
            Any,
            SimpleNamespace(pk=501, is_current=True),
        )
        mock_create.return_value = created_snapshot

        result = OrderPricingSnapshotService.record_current_snapshot(
            order=self.order,
            source_pricing_snapshot=self.source_pricing_snapshot,
            subtotal_amount=Decimal("120.00"),
            discount_amount=Decimal("10.00"),
            total_amount=Decimal("110.00"),
            writer_compensation_amount=Decimal("55.00"),
            pricing_payload={
                "service_family": "writing",
                "service_code": "essay",
            },
            created_by=self.created_by,
            currency="USD",
            pricing_policy_version="v1",
        )

        self.assertEqual(result, created_snapshot)

        mock_filter.assert_called_once_with(
            order=self.order,
            is_current=True,
        )
        mock_filter.return_value.update.assert_called_once_with(
            is_current=False
        )

        mock_create.assert_called_once_with(
            website=self.order.website,
            order=self.order,
            source_pricing_snapshot=self.source_pricing_snapshot,
            is_current=True,
            currency="USD",
            pricing_policy_version="v1",
            subtotal_amount=Decimal("120.00"),
            discount_amount=Decimal("10.00"),
            total_amount=Decimal("110.00"),
            writer_compensation_amount=Decimal("55.00"),
            pricing_payload={
                "service_family": "writing",
                "service_code": "essay",
            },
            created_by=self.created_by,
        )

    @patch(
        "orders.services.order_pricing_snapshot_service."
        "OrderPricingSnapshot.objects.create"
    )
    @patch(
        "orders.services.order_pricing_snapshot_service."
        "OrderPricingSnapshot.objects.filter"
    )
    def test_record_current_snapshot_falls_back_to_order_currency(
        self,
        mock_filter: Any,
        mock_create: Any,
    ) -> None:
        created_snapshot = cast(
            Any,
            SimpleNamespace(pk=502, is_current=True),
        )
        mock_create.return_value = created_snapshot

        OrderPricingSnapshotService.record_current_snapshot(
            order=self.order,
            source_pricing_snapshot=None,
            subtotal_amount=Decimal("50.00"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("50.00"),
            writer_compensation_amount=Decimal("25.00"),
            pricing_payload={"service_family": "editing"},
            created_by=None,
            currency="",
            pricing_policy_version="",
        )

        create_kwargs = mock_create.call_args.kwargs
        self.assertEqual(create_kwargs["currency"], "USD")
        self.assertIsNone(create_kwargs["source_pricing_snapshot"])
        self.assertEqual(
            create_kwargs["pricing_payload"],
            {"service_family": "editing"},
        )