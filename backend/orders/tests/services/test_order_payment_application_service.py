from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.services.order_payment_application_service import (
    OrderPaymentApplicationService,
)


class OrderPaymentApplicationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=10)
        self.order_client_user = SimpleNamespace(pk=20)

    def _make_order(
        self,
        *,
        pk: int = 100,
        total_price: Decimal = Decimal("120.00"),
        amount_paid: Decimal = Decimal("0.00"),
        payment_status: str = "unpaid",
        status: str = "pending_payment",
        archived_at: Any = None,
    ) -> Any:
        order = SimpleNamespace(
            pk=pk,
            website=self.website,
            client=self.order_client_user,
            total_price=total_price,
            amount_paid=amount_paid,
            payment_status=payment_status,
            status=status,
            archived_at=archived_at,
            currency="USD",
            service_family="writing",
            service_code="essay",
            save=lambda *args, **kwargs: None,
        )
        return cast(Any, order)

    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._create_timeline_event"
    )
    @patch(
        "orders.services.order_payment_application_service."
        "PaymentIntentService.create_intent"
    )
    def test_start_checkout_creates_payment_intent(
        self,
        mock_create_intent: Any,
        mock_timeline: Any,
    ) -> None:
        payment_intent = SimpleNamespace(
            pk=501,
            reference="pi_123",
            amount=Decimal("120.00"),
            currency="USD",
            provider="stripe",
        )
        mock_create_intent.return_value = payment_intent

        order = self._make_order()

        result = OrderPaymentApplicationService.start_checkout(
            order=order,
            provider="stripe",
            purpose="order_payment",
            triggered_by=self.order_client_user,
            payment_method_code="card",
        )

        self.assertEqual(result, payment_intent)
        mock_create_intent.assert_called_once()
        mock_timeline.assert_called_once()

    def test_start_checkout_raises_when_total_price_is_zero(self) -> None:
        order = self._make_order(total_price=Decimal("0.00"))

        with self.assertRaises(ValidationError):
            OrderPaymentApplicationService.start_checkout(
                order=order,
                provider="stripe",
            )

    def test_start_checkout_raises_for_archived_order(self) -> None:
        order = self._make_order(
            archived_at=SimpleNamespace(),
        )

        with self.assertRaises(ValidationError):
            OrderPaymentApplicationService.start_checkout(
                order=order,
                provider="stripe",
            )

    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._create_timeline_event"
    )
    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._lock_order"
    )
    def test_apply_confirmed_payment_marks_partially_paid(
        self,
        mock_lock_order: Any,
        mock_timeline: Any,
    ) -> None:
        order = self._make_order(
            total_price=Decimal("120.00"),
            amount_paid=Decimal("0.00"),
            payment_status="unpaid",
            status="pending_payment",
        )
        mock_lock_order.return_value = order

        result = OrderPaymentApplicationService.apply_confirmed_payment(
            order=order,
            amount=Decimal("50.00"),
            payment_reference="pay_001",
            triggered_by=self.order_client_user,
        )

        self.assertEqual(result.amount_paid, Decimal("50.00"))
        self.assertEqual(result.payment_status, "partially_paid")
        self.assertEqual(result.status, "pending_payment")
        self.assertEqual(mock_timeline.call_count, 1)

    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._create_timeline_event"
    )
    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._lock_order"
    )
    def test_apply_confirmed_payment_marks_fully_paid_and_ready_for_staffing(
        self,
        mock_lock_order: Any,
        mock_timeline: Any,
    ) -> None:
        order = self._make_order(
            total_price=Decimal("120.00"),
            amount_paid=Decimal("20.00"),
            payment_status="partially_paid",
            status="pending_payment",
        )
        mock_lock_order.return_value = order

        result = OrderPaymentApplicationService.apply_confirmed_payment(
            order=order,
            amount=Decimal("100.00"),
            payment_reference="pay_002",
            triggered_by=self.order_client_user,
        )

        self.assertEqual(result.amount_paid, Decimal("120.00"))
        self.assertEqual(result.payment_status, "fully_paid")
        self.assertEqual(result.status, "ready_for_staffing")
        self.assertEqual(mock_timeline.call_count, 2)

    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService._lock_order"
    )
    def test_apply_confirmed_payment_raises_for_overfunding(
        self,
        mock_lock_order: Any,
    ) -> None:
        order = self._make_order(
            total_price=Decimal("120.00"),
            amount_paid=Decimal("100.00"),
        )
        mock_lock_order.return_value = order

        with self.assertRaises(ValidationError):
            OrderPaymentApplicationService.apply_confirmed_payment(
                order=order,
                amount=Decimal("30.00"),
                payment_reference="pay_003",
            )

    def test_apply_confirmed_payment_raises_for_non_positive_amount(
        self,
    ) -> None:
        order = self._make_order()

        with self.assertRaises(ValidationError):
            OrderPaymentApplicationService.apply_confirmed_payment(
                order=order,
                amount=Decimal("0.00"),
                payment_reference="pay_004",
            )

    @patch(
        "orders.services.order_payment_application_service."
        "OrderPaymentApplicationService.apply_confirmed_payment"
    )
    def test_apply_split_payment_summary_combines_amounts(
        self,
        mock_apply_confirmed_payment: Any,
    ) -> None:
        order = self._make_order()
        mock_apply_confirmed_payment.return_value = order

        result = (
            OrderPaymentApplicationService.apply_split_payment_summary(
                order=order,
                wallet_amount=Decimal("20.00"),
                external_amount=Decimal("100.00"),
                payment_reference="pay_005",
                triggered_by=self.order_client_user,
                payment_intent_reference="pi_123",
            )
        )

        self.assertEqual(result, order)
        mock_apply_confirmed_payment.assert_called_once_with(
            order=order,
            amount=Decimal("120.00"),
            payment_reference="pay_005",
            triggered_by=self.order_client_user,
            payment_intent_reference="pi_123",
            source="split",
            metadata={
                "wallet_amount": "20.00",
                "external_amount": "100.00",
            },
        )

    def test_apply_split_payment_summary_raises_for_negative_amounts(
        self,
    ) -> None:
        order = self._make_order()

        with self.assertRaises(ValidationError):
            OrderPaymentApplicationService.apply_split_payment_summary(
                order=order,
                wallet_amount=Decimal("-1.00"),
                external_amount=Decimal("10.00"),
                payment_reference="pay_006",
            )

    def test_get_outstanding_amount_returns_remaining_balance(self) -> None:
        order = self._make_order(
            total_price=Decimal("120.00"),
            amount_paid=Decimal("50.00"),
        )

        result = OrderPaymentApplicationService.get_outstanding_amount(
            order=order
        )

        self.assertEqual(result, Decimal("70.00"))

    def test_get_outstanding_amount_never_returns_negative(self) -> None:
        order = self._make_order(
            total_price=Decimal("120.00"),
            amount_paid=Decimal("150.00"),
        )

        result = OrderPaymentApplicationService.get_outstanding_amount(
            order=order
        )

        self.assertEqual(result, Decimal("0.00"))