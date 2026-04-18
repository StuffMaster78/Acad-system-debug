from __future__ import annotations

from decimal import Decimal
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.adjustments.adjustment_funding_views import (
    AdjustmentApplyPaymentView,
    AdjustmentAttachPaymentIntentView,
    AdjustmentFundingCreateView,
    AdjustmentMarkPaymentRequestView,
)


class FakeUser:
    def __init__(
        self,
        *,
        pk: int,
        website: Any,
        is_staff: bool = False,
    ) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class AdjustmentFundingAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

        self.staff_user = FakeUser(
            pk=30,
            website=self.website,
            is_staff=True,
        )

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "status": "in_progress",
            },
        )()

        self.adjustment_request = type(
            "AdjustmentRequestStub",
            (),
            {
                "pk": 200,
                "website": self.website,
                "order": self.order,
                "status": "accepted",
                "adjustment_type": "paid_revision",
            },
        )()

        self.funding = type(
            "FundingStub",
            (),
            {
                "pk": 300,
                "website": self.website,
                "adjustment_request": self.adjustment_request,
                "status": "not_started",
                "amount_expected": Decimal("50.00"),
                "amount_paid": Decimal("0.00"),
                "payment_intent_reference": "",
                "payment_request_reference": "",
                "funded_at": None,
            },
        )()

    def _auth_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any] | None = None,
    ) -> Request:
        request = self.factory.post(path, data or {}, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @patch(
        "orders.api.views.adjustments.adjustment_funding_views."
        "AdjustmentFundingService.create_funding_record"
    )
    @patch.object(
        AdjustmentFundingCreateView,
        "_get_adjustment_for_tenant",
    )
    def test_adjustment_funding_create(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        created_funding = type(
            "FundingStub",
            (),
            {
                "pk": 301,
                "status": "not_started",
                "amount_expected": Decimal("50.00"),
                "amount_paid": Decimal("0.00"),
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = created_funding

        view = AdjustmentFundingCreateView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/funding/create/",
            user=self.staff_user,
            data={
                "amount_expected": "50.00",
                "payment_request_reference": "pr_123",
                "invoice_reference": "inv_123",
            },
        )

        with patch.object(
            AdjustmentFundingCreateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["funding_id"], 301)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "not_started")
        self.assertEqual(data["amount_expected"], Decimal("50.00"))
        self.assertEqual(data["amount_paid"], Decimal("0.00"))

        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            amount_expected=Decimal("50.00"),
            payment_request_reference="pr_123",
            invoice_reference="inv_123",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_funding_views."
        "AdjustmentFundingService.attach_payment_intent"
    )
    @patch.object(
        AdjustmentAttachPaymentIntentView,
        "_get_funding_for_tenant",
    )
    def test_attach_payment_intent(
        self,
        mock_get_funding: Any,
        mock_service: Any,
    ) -> None:
        updated_funding = type(
            "FundingStub",
            (),
            {
                "pk": 300,
                "status": "payment_intent_created",
                "payment_intent_reference": "pi_123",
            },
        )()

        mock_get_funding.return_value = self.funding
        mock_service.return_value = updated_funding

        view = AdjustmentAttachPaymentIntentView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/attach-payment-intent/",
            user=self.staff_user,
            data={
                "payment_intent_reference": "pi_123",
            },
        )

        with patch.object(
            AdjustmentAttachPaymentIntentView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["funding_id"], 300)
        self.assertEqual(data["status"], "payment_intent_created")
        self.assertEqual(data["payment_intent_reference"], "pi_123")

        mock_service.assert_called_once_with(
            funding=self.funding,
            payment_intent_reference="pi_123",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_funding_views."
        "AdjustmentFundingService.mark_payment_request_created"
    )
    @patch.object(
        AdjustmentMarkPaymentRequestView,
        "_get_funding_for_tenant",
    )
    def test_mark_payment_request_created(
        self,
        mock_get_funding: Any,
        mock_service: Any,
    ) -> None:
        updated_funding = type(
            "FundingStub",
            (),
            {
                "pk": 300,
                "status": "payment_request_created",
                "payment_request_reference": "pr_456",
            },
        )()

        mock_get_funding.return_value = self.funding
        mock_service.return_value = updated_funding

        view = AdjustmentMarkPaymentRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/mark-payment-request-created/",
            user=self.staff_user,
            data={
                "payment_request_reference": "pr_456",
            },
        )

        with patch.object(
            AdjustmentMarkPaymentRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["funding_id"], 300)
        self.assertEqual(data["status"], "payment_request_created")
        self.assertEqual(data["payment_request_reference"], "pr_456")

        mock_service.assert_called_once_with(
            funding=self.funding,
            payment_request_reference="pr_456",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_funding_views."
        "AdjustmentFundingService.apply_payment"
    )
    @patch.object(
        AdjustmentApplyPaymentView,
        "_get_funding_for_tenant",
    )
    def test_apply_payment(
        self,
        mock_get_funding: Any,
        mock_service: Any,
    ) -> None:
        updated_funding = type(
            "FundingStub",
            (),
            {
                "pk": 300,
                "status": "funded",
                "amount_expected": Decimal("50.00"),
                "amount_paid": Decimal("50.00"),
                "funded_at": "2026-04-16T10:30:00Z",
            },
        )()

        mock_get_funding.return_value = self.funding
        mock_service.return_value = updated_funding

        view = AdjustmentApplyPaymentView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/apply-payment/",
            user=self.staff_user,
            data={
                "amount": "50.00",
                "external_reference": "ext_789",
            },
        )

        with patch.object(
            AdjustmentApplyPaymentView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["funding_id"], 300)
        self.assertEqual(data["status"], "funded")
        self.assertEqual(data["amount_expected"], Decimal("50.00"))
        self.assertEqual(data["amount_paid"], Decimal("50.00"))
        self.assertEqual(data["funded_at"], "2026-04-16T10:30:00Z")

        mock_service.assert_called_once_with(
            funding=self.funding,
            amount=Decimal("50.00"),
            external_reference="ext_789",
            triggered_by=self.staff_user,
        )

    def test_adjustment_funding_create_requires_amount_expected(self) -> None:
        view = AdjustmentFundingCreateView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/funding/create/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            AdjustmentFundingCreateView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentFundingCreateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount_expected", data)

    def test_attach_payment_intent_requires_reference(self) -> None:
        view = AdjustmentAttachPaymentIntentView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/attach-payment-intent/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            AdjustmentAttachPaymentIntentView,
            "_get_funding_for_tenant",
            return_value=self.funding,
        ), patch.object(
            AdjustmentAttachPaymentIntentView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("payment_intent_reference", data)

    def test_mark_payment_request_created_requires_reference(self) -> None:
        view = AdjustmentMarkPaymentRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/mark-payment-request-created/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            AdjustmentMarkPaymentRequestView,
            "_get_funding_for_tenant",
            return_value=self.funding,
        ), patch.object(
            AdjustmentMarkPaymentRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("payment_request_reference", data)

    def test_apply_payment_requires_amount(self) -> None:
        view = AdjustmentApplyPaymentView.as_view()
        request = self._auth_post(
            path="/api/orders/funding/300/apply-payment/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            AdjustmentApplyPaymentView,
            "_get_funding_for_tenant",
            return_value=self.funding,
        ), patch.object(
            AdjustmentApplyPaymentView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, funding_id=300))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", data)