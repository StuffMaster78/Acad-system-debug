from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    ORDER_ADJUSTMENT_STATUS_CANCELLED,
    ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_STATUS_DECLINED,
    ORDER_ADJUSTMENT_STATUS_EXPIRED,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
)
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)


class AdjustmentNegotiationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.staff = SimpleNamespace(pk=20, website_id=1)

    def _make_order(self) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        return order

    def _make_request(
        self,
        *,
        order,
        status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    ) -> MagicMock:
        req = MagicMock()
        req.pk = 200
        req.order = order
        req.website = order.website
        req.status = status
        req.save = MagicMock()
        return req

    def _make_proposal(self, *, req) -> MagicMock:
        proposal = MagicMock()
        proposal.pk = 300
        proposal.adjustment_request = req
        return proposal

    @patch.object(AdjustmentNegotiationService, "_create_proposal")
    @patch.object(AdjustmentNegotiationService, "_create_event")
    @patch.object(AdjustmentNegotiationService, "_lock_order")
    @patch(
        "orders.services.adjustment_negotiation_service."
        "OrderAdjustmentRequest.objects.create"
    )
    def test_create_request_with_system_quote(
        self,
        mock_request_create,
        mock_lock_order,
        mock_create_event,
        mock_create_proposal,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_order.return_value = order
        mock_request_create.return_value = req

        result = AdjustmentNegotiationService.create_request_with_system_quote(
            order=order,
            requested_by=self.client_user,
            adjustment_type=ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
            reason="Late revision",
            quoted_amount=Decimal("50.00"),
            scope_summary="Extra work",
        )

        self.assertEqual(result, req)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE)
        mock_create_proposal.assert_called_once()

    @patch.object(AdjustmentNegotiationService, "_create_proposal")
    @patch.object(AdjustmentNegotiationService, "_lock_request")
    def test_client_counter_updates_status(
        self,
        mock_lock_request,
        mock_create_proposal,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_request.return_value = req
        proposal = self._make_proposal(req=req)
        mock_create_proposal.return_value = proposal

        result = AdjustmentNegotiationService.counter_by_client(
            adjustment_request=req,
            client=self.client_user,
            amount=Decimal("30.00"),
            notes="Too expensive",
        )

        self.assertEqual(result, proposal)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED)
        req.save.assert_called_once()

    @patch.object(AdjustmentNegotiationService, "_create_proposal")
    @patch.object(AdjustmentNegotiationService, "_lock_request")
    def test_accept_request_sets_final_status(
        self,
        mock_lock_request,
        mock_create_proposal,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_request.return_value = req
        proposal = self._make_proposal(req=req)
        mock_create_proposal.return_value = proposal

        result = AdjustmentNegotiationService.accept_request(
            adjustment_request=req,
            accepted_by=self.client_user,
            final_amount=Decimal("40.00"),
        )

        self.assertEqual(result, proposal)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_ACCEPTED)
        req.save.assert_called_once()

    @patch.object(AdjustmentNegotiationService, "_lock_request")
    def test_decline_request_sets_status(
        self,
        mock_lock_request,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_request.return_value = req

        result = AdjustmentNegotiationService.decline_request(
            adjustment_request=req,
            declined_by=self.client_user,
            reason="Not needed",
        )

        self.assertEqual(result, req)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_DECLINED)

    @patch.object(AdjustmentNegotiationService, "_lock_request")
    def test_cancel_request_sets_status(
        self,
        mock_lock_request,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_request.return_value = req

        result = AdjustmentNegotiationService.cancel_request(
            adjustment_request=req,
            cancelled_by=self.client_user,
            reason="Client cancelled",
        )

        self.assertEqual(result, req)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_CANCELLED)

    @patch.object(AdjustmentNegotiationService, "_lock_request")
    def test_expire_request_sets_status(
        self,
        mock_lock_request,
    ):
        order = self._make_order()
        req = self._make_request(order=order)

        mock_lock_request.return_value = req

        result = AdjustmentNegotiationService.expire_request(
            adjustment_request=req
        )

        self.assertEqual(result, req)
        self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_EXPIRED)

    def test_validate_amount_rejects_zero_or_negative(self):
        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService._validate_amount(Decimal("0"))

        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService._validate_amount(Decimal("-10"))

    def test_ensure_request_open_for_negotiation_blocks_closed(self):
        order = self._make_order()
        req = self._make_request(
            order=order,
            status=ORDER_ADJUSTMENT_STATUS_ACCEPTED,
        )

        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService._ensure_request_open_for_negotiation(req)

    def test_validate_actor_website_blocks_cross_tenant(self):
        order = self._make_order()
        foreign_actor = SimpleNamespace(pk=99, website_id=999)

        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )