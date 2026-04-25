from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from orders.services.order_creation_service import (
    OrderCreationService,
)


class OrderCreationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=10)
        self.order_client_user = SimpleNamespace(pk=20)
        self.paper_type = SimpleNamespace(pk=1)

    def _order_payload(self) -> dict[str, Any]:
        return {
            "topic": "Comparative healthcare systems",
            "paper_type": self.paper_type,
            "academic_level": None,
            "formatting_style": None,
            "subject": None,
            "type_of_work": None,
            "english_type": None,
            "writer_level": None,
            "discount": None,
            "discount_code_used": "",
            "is_follow_up": False,
            "previous_order": None,
            "preferred_writer": None,
            "flags": ["urgent"],
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "is_urgent": True,
            "requires_editing": True,
            "editing_skip_reason": "",
            "created_by_admin": False,
            "order_instructions": "Use peer reviewed sources.",
            "external_contact_name": "",
            "external_contact_email": "",
            "external_contact_phone": "",
            "allow_unpaid_access": False,
            "service_family": "writing",
            "service_code": "essay",
        }

    def _pricing_result(self) -> dict[str, Any]:
        return {
            "total_price": "120.00",
            "subtotal_amount": "120.00",
            "discount_amount": "0.00",
            "writer_compensation_amount": "60.00",
            "currency": "USD",
            "service_family": "writing",
            "service_code": "essay",
            "is_composite": True,
            "pricing_policy_version": "v1",
            "preferred_writer_fee_amount": "0.00",
            "items": [
                {
                    "service_family": "writing",
                    "service_code": "essay",
                    "topic": "Main paper",
                    "quantity": 1,
                    "subtotal": "120.00",
                    "discount_amount": "0.00",
                    "total_price": "120.00",
                    "metadata": {"pages": 4},
                }
            ],
        }

    @patch(
        "orders.services.order_creation_service."
        "OrderPricingSnapshotService.record_current_snapshot"
    )
    @patch(
        "orders.services.order_creation_service."
        "OrderTimelineEvent.objects.create"
    )
    @patch(
        "orders.services.order_creation_service."
        "OrderItem.objects.create"
    )
    @patch(
        "orders.services.order_creation_service."
        "Order.objects.create"
    )
    def test_create_order_creates_aggregate_and_items(
        self,
        mock_order_create: Any,
        mock_item_create: Any,
        mock_timeline_create: Any,
        mock_record_snapshot: Any,
    ) -> None:
        order_stub = SimpleNamespace(
            pk=100,
            website=self.website,
            total_price=Decimal("120.00"),
            service_family="writing",
            service_code="essay",
            payment_status="unpaid",
            currency="USD",
        )
        mock_order_create.return_value = order_stub

        result = OrderCreationService.create_order(
            website=self.website,
            client=self.order_client_user,
            order_payload=self._order_payload(),
            pricing_result=self._pricing_result(),
            source_pricing_snapshot=SimpleNamespace(pk=11),
            triggered_by=self.order_client_user,
        )

        self.assertEqual(result, order_stub)
        mock_order_create.assert_called_once()
        mock_item_create.assert_called_once()
        mock_record_snapshot.assert_called_once()
        mock_timeline_create.assert_called_once()

        order_create_kwargs = mock_order_create.call_args.kwargs
        self.assertEqual(
            order_create_kwargs["total_price"],
            Decimal("120.00"),
        )
        self.assertEqual(
            order_create_kwargs["amount_paid"],
            Decimal("0.00"),
        )
        self.assertEqual(order_create_kwargs["service_family"], "writing")
        self.assertEqual(order_create_kwargs["service_code"], "essay")
        self.assertEqual(
            order_create_kwargs["status"],
            "pending_payment",
        )

    def test_validate_payload_raises_for_missing_fields(self) -> None:
        with self.assertRaises(Exception):
            OrderCreationService._validate_payload(
                order_payload={"topic": "A"}
            )

    def test_extract_items_from_dict_result(self) -> None:
        items = OrderCreationService._extract_items(
            pricing_result=self._pricing_result()
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["service_code"], "essay")