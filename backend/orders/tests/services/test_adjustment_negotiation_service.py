from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast
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
        self.website = SimpleNamespace(pk=10)
        self.client_user = SimpleNamespace(pk=20, website_id=1)
        self.writer = SimpleNamespace(pk=20)
        self.staff = SimpleNamespace(pk=20, website_id=1)
        self.order = SimpleNamespace(
            pk=100,
            website=self.website,
            client=self.client,
            base_quantity=4,
            unit_type="page",
            currency="USD",
        )

    @patch(
        "orders.services.adjustment_negotiation_service."
        "OrderAdjustmentRequest.objects.create"
    )
    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._create_proposal"
    )
    def test_create_scope_increment_request(
        self,
        mock_create_proposal: Any,
        mock_create_request: Any,
    ) -> None:
        adjustment_request = SimpleNamespace(
            pk=1,
            website=self.website,
            order=self.order,
            current_proposal=None,
            save=lambda *args, **kwargs: None,
        )
        proposal = SimpleNamespace(pk=50)

        mock_create_request.return_value = adjustment_request
        mock_create_proposal.return_value = proposal

        result = AdjustmentNegotiationService.create_scope_increment_request(
            website=self.website,
            order=self.order,
            requested_by=self.writer,
            adjustment_type="page_increase",
            unit_type="page",
            requested_quantity=6,
            title="Need more pages",
            writer_justification="Rubric requires more depth.",
            pricing_result={
                "total_price": "60.00",
                "writer_compensation_amount": "30.00",
            },
        )

        self.assertEqual(result, adjustment_request)
        mock_create_request.assert_called_once()
        mock_create_proposal.assert_called_once()

    @patch(
        "orders.services.adjustment_negotiation_service."
        "OrderAdjustmentRequest.objects.create"
    )
    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._create_proposal"
    )
    def test_create_extra_service_request(
        self,
        mock_create_proposal: Any,
        mock_create_request: Any,
    ) -> None:
        adjustment_request = SimpleNamespace(
            pk=2,
            website=self.website,
            order=self.order,
            current_proposal=None,
            save=lambda *args, **kwargs: None,
        )
        mock_create_request.return_value = adjustment_request
        mock_create_proposal.return_value = SimpleNamespace(pk=60)

        result = AdjustmentNegotiationService.create_extra_service_request(
            website=self.website,
            order=self.order,
            requested_by=self.writer,
            extra_service_code="speaker_notes",
            title="Add speaker notes",
            pricing_result={
                "total_price": "25.00",
                "writer_compensation_amount": "10.00",
            },
        )

        self.assertEqual(result, adjustment_request)
        mock_create_request.assert_called_once()
        mock_create_proposal.assert_called_once()

    def test_create_extra_service_requires_code(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService.create_extra_service_request(
                website=self.website,
                order=self.order,
                requested_by=self.writer,
                extra_service_code="",
                title="Bad extra",
                pricing_result={"total_price": "10.00"},
            )

    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._lock_request"
    )
    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._deactivate_current_proposal"
    )
    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._create_proposal"
    )
    def test_client_counter_scope_increment(
        self,
        mock_create_proposal: Any,
        mock_deactivate: Any,
        mock_lock: Any,
    ) -> None:
        locked_request = SimpleNamespace(
            pk=1,
            website=self.website,
            order=self.order,
            adjustment_kind="scope_increment",
            status="pending_client_response",
            current_quantity=4,
            requested_quantity=6,
            unit_type="page",
            current_proposal=SimpleNamespace(pk=1),
            save=lambda *args, **kwargs: None,
        )
        mock_lock.return_value = locked_request
        mock_create_proposal.return_value = SimpleNamespace(pk=2)

        result = AdjustmentNegotiationService.client_counter_scope_increment(
            adjustment_request=cast(Any, SimpleNamespace(pk=1)),
            countered_quantity=5,
            countered_note="One page only.",
            pricing_result={
                "total_price": "30.00",
                "writer_compensation_amount": "15.00",
            },
            countered_by=self.client,
        )

        self.assertEqual(result.status, "client_countered")
        self.assertEqual(result.countered_quantity, 5)
        self.assertEqual(result.counter_total_amount, Decimal("30.00"))
        mock_deactivate.assert_called_once()
        mock_create_proposal.assert_called_once()

    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._lock_request"
    )
    def test_client_counter_rejects_extra_service(self, mock_lock: Any) -> None:
        mock_lock.return_value = SimpleNamespace(
            adjustment_kind="extra_service",
            status="pending_client_response",
        )

        with self.assertRaises(ValidationError):
            AdjustmentNegotiationService.client_counter_scope_increment(
                adjustment_request=cast(Any, SimpleNamespace(pk=1)),
                countered_quantity=5,
                countered_note="Nope",
                pricing_result={"total_price": "30.00"},
                countered_by=self.client,
            )

    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._lock_request"
    )
    def test_client_accept_extra_service(self, mock_lock: Any) -> None:
        locked_request = SimpleNamespace(
            adjustment_kind="extra_service",
            status="pending_client_response",
            current_proposal=SimpleNamespace(pk=11),
            save=lambda *args, **kwargs: None,
        )
        mock_lock.return_value = locked_request

        result = AdjustmentNegotiationService.client_accept_extra_service(
            adjustment_request=cast(Any, SimpleNamespace(pk=1)),
            accepted_by=self.client,
        )

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.accepted_proposal.pk, 11) # type: ignore

    @patch(
        "orders.services.adjustment_negotiation_service."
        "OrderReassignmentService.request_reassignment"
    )
    @patch(
        "orders.services.adjustment_negotiation_service."
        "AdjustmentNegotiationService._lock_request"
    )
    def test_writer_escalate_after_funded_counter(
        self,
        mock_lock: Any,
        mock_reassignment: Any,
    ) -> None:
        locked_request = SimpleNamespace(
            order=self.order,
            escalated_after_counter=False,
            escalation_reason="",
            save=lambda *args, **kwargs: None,
        )
        mock_lock.return_value = locked_request

        AdjustmentNegotiationService.writer_escalate_after_funded_counter(
            adjustment_request=cast(Any, SimpleNamespace(pk=1)),
            writer=self.writer,
            reason="Counter scope still too heavy.",
        )

        self.assertTrue(locked_request.escalated_after_counter)
        mock_reassignment.assert_called_once()

    def _make_order(self) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        return order

    # def _make_request(
    #     self,
    #     *,
    #     order,
    #     status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
    # ) -> MagicMock:
    #     req = MagicMock()
    #     req.pk = 200
    #     req.order = order
    #     req.website = order.website
    #     req.status = status
    #     req.save = MagicMock()
    #     return req

    # def _make_proposal(self, *, req) -> MagicMock:
    #     proposal = MagicMock()
    #     proposal.pk = 300
    #     proposal.adjustment_request = req
    #     return proposal

    # @patch.object(AdjustmentNegotiationService, "_create_proposal")
    # @patch.object(AdjustmentNegotiationService, "_create_event")
    # @patch.object(AdjustmentNegotiationService, "_lock_order")
    # @patch(
    #     "orders.services.adjustment_negotiation_service."
    #     "OrderAdjustmentRequest.objects.create"
    # )
    # def test_create_request_with_system_quote(
    #     self,
    #     mock_request_create,
    #     mock_lock_order,
    #     mock_create_event,
    #     mock_create_proposal,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_order.return_value = order
    #     mock_request_create.return_value = req

    #     result = AdjustmentNegotiationService.create_request_with_system_quote(
    #         order=order,
    #         requested_by=self.client_user,
    #         adjustment_type=ORDER_ADJUSTMENT_TYPE_PAID_REVISION,
    #         reason="Late revision",
    #         quoted_amount=Decimal("50.00"),
    #         scope_summary="Extra work",
    #     )

    #     self.assertEqual(result, req)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE)
    #     mock_create_proposal.assert_called_once()

    # @patch.object(AdjustmentNegotiationService, "_create_proposal")
    # @patch.object(AdjustmentNegotiationService, "_lock_request")
    # def test_client_counter_updates_status(
    #     self,
    #     mock_lock_request,
    #     mock_create_proposal,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_request.return_value = req
    #     proposal = self._make_proposal(req=req)
    #     mock_create_proposal.return_value = proposal

    #     result = AdjustmentNegotiationService.counter_by_client(
    #         adjustment_request=req,
    #         client=self.client_user,
    #         amount=Decimal("30.00"),
    #         notes="Too expensive",
    #     )

    #     self.assertEqual(result, proposal)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED)
    #     req.save.assert_called_once()

    # @patch.object(AdjustmentNegotiationService, "_create_proposal")
    # @patch.object(AdjustmentNegotiationService, "_lock_request")
    # def test_accept_request_sets_final_status(
    #     self,
    #     mock_lock_request,
    #     mock_create_proposal,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_request.return_value = req
    #     proposal = self._make_proposal(req=req)
    #     mock_create_proposal.return_value = proposal

    #     result = AdjustmentNegotiationService.accept_request(
    #         adjustment_request=req,
    #         accepted_by=self.client_user,
    #         final_amount=Decimal("40.00"),
    #     )

    #     self.assertEqual(result, proposal)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_ACCEPTED)
    #     req.save.assert_called_once()

    # @patch.object(AdjustmentNegotiationService, "_lock_request")
    # def test_decline_request_sets_status(
    #     self,
    #     mock_lock_request,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_request.return_value = req

    #     result = AdjustmentNegotiationService.decline_request(
    #         adjustment_request=req,
    #         declined_by=self.client_user,
    #         reason="Not needed",
    #     )

    #     self.assertEqual(result, req)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_DECLINED)

    # @patch.object(AdjustmentNegotiationService, "_lock_request")
    # def test_cancel_request_sets_status(
    #     self,
    #     mock_lock_request,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_request.return_value = req

    #     result = AdjustmentNegotiationService.cancel_request(
    #         adjustment_request=req,
    #         cancelled_by=self.client_user,
    #         reason="Client cancelled",
    #     )

    #     self.assertEqual(result, req)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_CANCELLED)

    # @patch.object(AdjustmentNegotiationService, "_lock_request")
    # def test_expire_request_sets_status(
    #     self,
    #     mock_lock_request,
    # ):
    #     order = self._make_order()
    #     req = self._make_request(order=order)

    #     mock_lock_request.return_value = req

    #     result = AdjustmentNegotiationService.expire_request(
    #         adjustment_request=req
    #     )

    #     self.assertEqual(result, req)
    #     self.assertEqual(req.status, ORDER_ADJUSTMENT_STATUS_EXPIRED)

    # def test_validate_amount_rejects_zero_or_negative(self):
    #     with self.assertRaises(ValidationError):
    #         AdjustmentNegotiationService._validate_amount(Decimal("0"))

    #     with self.assertRaises(ValidationError):
    #         AdjustmentNegotiationService._validate_amount(Decimal("-10"))

    # def test_ensure_request_open_for_negotiation_blocks_closed(self):
    #     order = self._make_order()
    #     req = self._make_request(
    #         order=order,
    #         status=ORDER_ADJUSTMENT_STATUS_ACCEPTED,
    #     )

    #     with self.assertRaises(ValidationError):
    #         AdjustmentNegotiationService._ensure_request_open_for_negotiation(req)

    # def test_validate_actor_website_blocks_cross_tenant(self):
    #     order = self._make_order()
    #     foreign_actor = SimpleNamespace(pk=99, website_id=999)

    #     with self.assertRaises(ValidationError):
    #         AdjustmentNegotiationService._validate_actor_website(
    #             actor=foreign_actor,
    #             order=order,
    #         )