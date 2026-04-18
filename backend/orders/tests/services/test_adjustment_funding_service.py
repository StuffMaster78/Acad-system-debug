from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
    ORDER_ADJUSTMENT_EVENT_COMPENSATION_CREATED,
    ORDER_ADJUSTMENT_EVENT_FUNDED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_FULLY_APPLIED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_INTENT_CREATED,
    ORDER_ADJUSTMENT_EVENT_PAYMENT_PARTIALLY_APPLIED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_FUNDED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_NOT_STARTED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PARTIALLY_FUNDED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_INTENT_CREATED,
    ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_REQUEST_CREATED,
    ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ORDER_ADJUSTMENT_STATUS_FUNDED,
    ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
    ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
)
from orders.services.adjustment_funding_service import (
    AdjustmentFundingService,
)


class AdjustmentFundingServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.staff_user = SimpleNamespace(pk=20, website_id=1)

    def _make_order(self) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        return order

    def _make_adjustment_request(
        self,
        *,
        status: str = ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ) -> MagicMock:
        order = self._make_order()
        request = MagicMock()
        request.pk = 200
        request.website = self.website
        request.order = order
        request.status = status
        request.adjustment_type = "paid_revision"
        request.save = MagicMock()
        return request

    def _make_funding(
        self,
        *,
        adjustment_request,
        status: str = ORDER_ADJUSTMENT_FUNDING_STATUS_NOT_STARTED,
        amount_expected: Decimal = Decimal("50.00"),
        amount_paid: Decimal = Decimal("0.00"),
    ) -> MagicMock:
        funding = MagicMock()
        funding.pk = 300
        funding.website = adjustment_request.website
        funding.adjustment_request = adjustment_request
        funding.status = status
        funding.amount_expected = amount_expected
        funding.amount_paid = amount_paid
        funding.payment_request_reference = ""
        funding.payment_intent_reference = ""
        funding.invoice_reference = ""
        funding.funded_at = None
        funding.save = MagicMock()
        return funding

    def _make_compensation(self) -> MagicMock:
        compensation = MagicMock()
        compensation.pk = 400
        return compensation

    @patch.object(AdjustmentFundingService, "_create_event")
    @patch.object(AdjustmentFundingService, "_get_funding_record")
    @patch.object(AdjustmentFundingService, "_lock_request")
    @patch(
        "orders.services.adjustment_funding_service."
        "OrderAdjustmentFunding.objects.create"
    )
    def test_create_funding_record_creates_record_and_updates_request(
        self,
        mock_funding_create,
        mock_lock_request,
        mock_get_funding_record,
        mock_create_event,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_request.return_value = adjustment_request
        mock_get_funding_record.return_value = None
        mock_funding_create.return_value = funding

        result = AdjustmentFundingService.create_funding_record(
            adjustment_request=adjustment_request,
            amount_expected=Decimal("50.00"),
            payment_request_reference="payreq_123",
            invoice_reference="inv_123",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, funding)
        mock_funding_create.assert_called_once_with(
            website=adjustment_request.website,
            adjustment_request=adjustment_request,
            status=ORDER_ADJUSTMENT_FUNDING_STATUS_NOT_STARTED,
            payment_request_reference="payreq_123",
            invoice_reference="inv_123",
            amount_expected=Decimal("50.00"),
            amount_paid=Decimal("0.00"),
            metadata={},
        )
        self.assertEqual(
            adjustment_request.status,
            ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
        )
        adjustment_request.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_event.call_args.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
        )

    @patch.object(AdjustmentFundingService, "_get_funding_record")
    @patch.object(AdjustmentFundingService, "_lock_request")
    def test_create_funding_record_rejects_duplicate_funding_record(
        self,
        mock_lock_request,
        mock_get_funding_record,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_request.return_value = adjustment_request
        mock_get_funding_record.return_value = funding

        with self.assertRaisesMessage(
            ValidationError,
            "Adjustment request already has a funding record.",
        ):
            AdjustmentFundingService.create_funding_record(
                adjustment_request=adjustment_request,
                amount_expected=Decimal("50.00"),
            )

    @patch.object(AdjustmentFundingService, "_create_event")
    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_attach_payment_intent_updates_reference_and_status(
        self,
        mock_lock_funding,
        mock_create_event,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_funding.return_value = funding

        result = AdjustmentFundingService.attach_payment_intent(
            funding=funding,
            payment_intent_reference="pi_123",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, funding)
        self.assertEqual(funding.payment_intent_reference, "pi_123")
        self.assertEqual(
            funding.status,
            ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_INTENT_CREATED,
        )
        funding.save.assert_called_once_with(
            update_fields=[
                "payment_intent_reference",
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_event.call_args.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_PAYMENT_INTENT_CREATED,
        )

    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_attach_payment_intent_requires_reference(
        self,
        mock_lock_funding,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_funding.return_value = funding

        with self.assertRaisesMessage(
            ValidationError,
            "payment_intent_reference is required.",
        ):
            AdjustmentFundingService.attach_payment_intent(
                funding=funding,
                payment_intent_reference="",
            )

    @patch.object(AdjustmentFundingService, "_create_event")
    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_mark_payment_request_created_updates_reference_and_status(
        self,
        mock_lock_funding,
        mock_create_event,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_funding.return_value = funding

        result = AdjustmentFundingService.mark_payment_request_created(
            funding=funding,
            payment_request_reference="payreq_456",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, funding)
        self.assertEqual(funding.payment_request_reference, "payreq_456")
        self.assertEqual(
            funding.status,
            ORDER_ADJUSTMENT_FUNDING_STATUS_PAYMENT_REQUEST_CREATED,
        )
        funding.save.assert_called_once_with(
            update_fields=[
                "payment_request_reference",
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_event.call_args.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_BILLING_CREATED,
        )

    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_mark_payment_request_created_requires_reference(
        self,
        mock_lock_funding,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
        )

        mock_lock_funding.return_value = funding

        with self.assertRaisesMessage(
            ValidationError,
            "payment_request_reference is required.",
        ):
            AdjustmentFundingService.mark_payment_request_created(
                funding=funding,
                payment_request_reference="",
            )

    @patch.object(AdjustmentFundingService, "_create_event")
    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_apply_payment_marks_partial_funding(
        self,
        mock_lock_funding,
        mock_create_event,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        funding = self._make_funding(
            adjustment_request=adjustment_request,
            amount_expected=Decimal("100.00"),
            amount_paid=Decimal("0.00"),
        )

        mock_lock_funding.return_value = funding

        result = AdjustmentFundingService.apply_payment(
            funding=funding,
            amount=Decimal("25.00"),
            external_reference="ext_123",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, funding)
        self.assertEqual(funding.amount_paid, Decimal("25.00"))
        self.assertEqual(
            funding.status,
            ORDER_ADJUSTMENT_FUNDING_STATUS_PARTIALLY_FUNDED,
        )
        funding.save.assert_called_once_with(
            update_fields=[
                "amount_paid",
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_event.call_args.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_PAYMENT_PARTIALLY_APPLIED,
        )

    @patch.object(
        AdjustmentFundingService,
        "_create_compensation_adjustment",
    )
    @patch.object(AdjustmentFundingService, "_create_event")
    @patch.object(AdjustmentFundingService, "_lock_request")
    @patch.object(AdjustmentFundingService, "_lock_funding")
    def test_apply_payment_marks_funded_and_creates_compensation(
        self,
        mock_lock_funding,
        mock_lock_request,
        mock_create_event,
        mock_create_compensation_adjustment,
    ) -> None:
        adjustment_request = self._make_adjustment_request(
            status=ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
        )
        funding = self._make_funding(
            adjustment_request=adjustment_request,
            amount_expected=Decimal("100.00"),
            amount_paid=Decimal("40.00"),
        )

        mock_lock_funding.return_value = funding
        mock_lock_request.return_value = adjustment_request

        result = AdjustmentFundingService.apply_payment(
            funding=funding,
            amount=Decimal("60.00"),
            external_reference="ext_456",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, funding)
        self.assertEqual(funding.amount_paid, Decimal("100.00"))
        self.assertEqual(
            funding.status,
            ORDER_ADJUSTMENT_FUNDING_STATUS_FUNDED,
        )
        self.assertIsNotNone(funding.funded_at)
        funding.save.assert_called_once_with(
            update_fields=[
                "amount_paid",
                "status",
                "funded_at",
                "updated_at",
            ]
        )
        self.assertEqual(
            adjustment_request.status,
            ORDER_ADJUSTMENT_STATUS_FUNDED,
        )
        adjustment_request.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(mock_create_event.call_count, 2)
        first_event = mock_create_event.call_args_list[0]
        second_event = mock_create_event.call_args_list[1]
        self.assertEqual(
            first_event.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_PAYMENT_FULLY_APPLIED,
        )
        self.assertEqual(
            second_event.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_FUNDED,
        )
        mock_create_compensation_adjustment.assert_called_once_with(
            adjustment_request=adjustment_request,
            amount=Decimal("100.00"),
            triggered_by=self.staff_user,
        )

    @patch.object(
        AdjustmentFundingService,
        "_create_event",
    )
    @patch(
        "orders.services.adjustment_funding_service."
        "OrderCompensationAdjustment.objects.create"
    )
    def test_create_compensation_adjustment_creates_placeholder(
        self,
        mock_compensation_create,
        mock_create_event,
    ) -> None:
        adjustment_request = self._make_adjustment_request()
        compensation = self._make_compensation()

        mock_compensation_create.return_value = compensation

        result = AdjustmentFundingService._create_compensation_adjustment(
            adjustment_request=adjustment_request,
            amount=Decimal("80.00"),
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, compensation)
        mock_compensation_create.assert_called_once_with(
            website=adjustment_request.website,
            order=adjustment_request.order,
            adjustment_request=adjustment_request,
            status=ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
            adjustment_type=adjustment_request.adjustment_type,
            amount=Decimal("80.00"),
            metadata={},
        )
        self.assertEqual(
            mock_create_event.call_args.kwargs["event_type"],
            ORDER_ADJUSTMENT_EVENT_COMPENSATION_CREATED,
        )

    def test_ensure_request_can_enter_funding_blocks_non_accepted_status(
        self,
    ) -> None:
        adjustment_request = self._make_adjustment_request(
            status=ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only accepted adjustment requests can enter funding.",
        ):
            AdjustmentFundingService._ensure_request_can_enter_funding(
                adjustment_request
            )

    def test_validate_amount_rejects_zero_or_negative(self) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "Amount must be greater than zero.",
        ):
            AdjustmentFundingService._validate_amount(Decimal("0.00"))

        with self.assertRaisesMessage(
            ValidationError,
            "Amount must be greater than zero.",
        ):
            AdjustmentFundingService._validate_amount(Decimal("-1.00"))