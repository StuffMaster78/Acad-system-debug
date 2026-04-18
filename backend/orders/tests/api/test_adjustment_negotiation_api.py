from __future__ import annotations

from decimal import Decimal
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.adjustments.adjustment_negotiation_views import (
    AdjustmentAcceptView,
    AdjustmentCancelView,
    AdjustmentCounterView,
    AdjustmentCreateView,
    AdjustmentDeclineView,
    AdjustmentStaffOverrideView,
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


class AdjustmentNegotiationAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

        self.client_user = FakeUser(
            pk=10,
            website=self.website,
            is_staff=False,
        )
        self.writer_user = FakeUser(
            pk=20,
            website=self.website,
            is_staff=False,
        )
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
                "client": self.client_user,
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
                "requested_by": self.writer_user,
                "status": "pending_client_response",
                "adjustment_type": "paid_revision",
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
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.create_request_with_system_quote"
    )
    @patch.object(AdjustmentCreateView, "_get_order_for_tenant")
    def test_adjustment_create(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        created_request = type(
            "AdjustmentRequestStub",
            (),
            {
                "pk": 201,
                "status": "pending_client_response",
                "adjustment_type": "paid_revision",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = created_request

        view = AdjustmentCreateView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/adjustments/",
            user=self.writer_user,
            data={
                "adjustment_type": "paid_revision",
                "reason": "Late revision request",
                "quoted_amount": "50.00",
                "scope_summary": "Revision requested after free window",
            },
        )

        with patch.object(
            AdjustmentCreateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["adjustment_request_id"], 201)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "pending_client_response")
        self.assertEqual(data["adjustment_type"], "paid_revision")
        mock_service.assert_called_once_with(
            order=self.order,
            requested_by=self.writer_user,
            adjustment_type="paid_revision",
            reason="Late revision request",
            quoted_amount=Decimal("50.00"),
            scope_summary="Revision requested after free window",
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.counter_by_client"
    )
    @patch.object(AdjustmentCounterView, "_get_adjustment_for_tenant")
    def test_adjustment_counter(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        proposal = type(
            "ProposalStub",
            (),
            {
                "pk": 300,
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = proposal

        view = AdjustmentCounterView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/counter/",
            user=self.client_user,
            data={
                "amount": "35.00",
                "notes": "Too high, reduce a bit",
            },
        )

        with patch.object(
            AdjustmentCounterView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["proposal_id"], 300)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "pending_client_response")
        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            client=self.client_user,
            amount=Decimal("35.00"),
            notes="Too high, reduce a bit",
            triggered_by=self.client_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.accept_request"
    )
    @patch.object(AdjustmentAcceptView, "_get_adjustment_for_tenant")
    def test_adjustment_accept(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        proposal = type(
            "ProposalStub",
            (),
            {
                "pk": 301,
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = proposal

        view = AdjustmentAcceptView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/accept/",
            user=self.client_user,
            data={
                "final_amount": "40.00",
                "notes": "Accepted",
            },
        )

        with patch.object(
            AdjustmentAcceptView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["proposal_id"], 301)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "pending_client_response")
        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            accepted_by=self.client_user,
            final_amount=Decimal("40.00"),
            notes="Accepted",
            triggered_by=self.client_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.decline_request"
    )
    @patch.object(AdjustmentDeclineView, "_get_adjustment_for_tenant")
    def test_adjustment_decline(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        updated_request = type(
            "AdjustmentRequestStub",
            (),
            {
                "pk": 200,
                "status": "declined",
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = updated_request

        view = AdjustmentDeclineView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/decline/",
            user=self.client_user,
            data={
                "reason": "No longer needed",
            },
        )

        with patch.object(
            AdjustmentDeclineView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "declined")
        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            declined_by=self.client_user,
            reason="No longer needed",
            triggered_by=self.client_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.cancel_request"
    )
    @patch.object(AdjustmentCancelView, "_get_adjustment_for_tenant")
    def test_adjustment_cancel(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        updated_request = type(
            "AdjustmentRequestStub",
            (),
            {
                "pk": 200,
                "status": "cancelled",
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = updated_request

        view = AdjustmentCancelView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/cancel/",
            user=self.writer_user,
            data={
                "reason": "Created by mistake",
            },
        )

        with patch.object(
            AdjustmentCancelView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "cancelled")
        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            cancelled_by=self.writer_user,
            reason="Created by mistake",
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.adjustments.adjustment_negotiation_views."
        "AdjustmentNegotiationService.create_staff_override_proposal"
    )
    @patch.object(
        AdjustmentStaffOverrideView,
        "_get_adjustment_for_tenant",
    )
    def test_adjustment_staff_override(
        self,
        mock_get_adjustment: Any,
        mock_service: Any,
    ) -> None:
        proposal = type(
            "ProposalStub",
            (),
            {
                "pk": 302,
            },
        )()

        mock_get_adjustment.return_value = self.adjustment_request
        mock_service.return_value = proposal

        view = AdjustmentStaffOverrideView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/staff-override/",
            user=self.staff_user,
            data={
                "amount": "25.00",
                "notes": "Support-approved override",
            },
        )

        with patch.object(
            AdjustmentStaffOverrideView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["proposal_id"], 302)
        self.assertEqual(data["adjustment_request_id"], 200)
        self.assertEqual(data["status"], "pending_client_response")
        mock_service.assert_called_once_with(
            adjustment_request=self.adjustment_request,
            proposed_by=self.staff_user,
            amount=Decimal("25.00"),
            notes="Support-approved override",
            triggered_by=self.staff_user,
        )

    def test_adjustment_create_requires_adjustment_type(self) -> None:
        view = AdjustmentCreateView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/adjustments/",
            user=self.writer_user,
            data={
                "reason": "Late revision request",
                "quoted_amount": "50.00",
                "scope_summary": "Revision requested after free window",
            },
        )

        with patch.object(
            AdjustmentCreateView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            AdjustmentCreateView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("adjustment_type", data)

    def test_adjustment_counter_requires_amount(self) -> None:
        view = AdjustmentCounterView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/counter/",
            user=self.client_user,
            data={},
        )

        with patch.object(
            AdjustmentCounterView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentCounterView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", data)

    def test_adjustment_accept_requires_final_amount(self) -> None:
        view = AdjustmentAcceptView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/accept/",
            user=self.client_user,
            data={},
        )

        with patch.object(
            AdjustmentAcceptView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentAcceptView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("final_amount", data)

    def test_adjustment_decline_requires_reason(self) -> None:
        view = AdjustmentDeclineView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/decline/",
            user=self.client_user,
            data={},
        )

        with patch.object(
            AdjustmentDeclineView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentDeclineView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_adjustment_cancel_requires_reason(self) -> None:
        view = AdjustmentCancelView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/cancel/",
            user=self.writer_user,
            data={},
        )

        with patch.object(
            AdjustmentCancelView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentCancelView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_adjustment_staff_override_requires_notes(self) -> None:
        view = AdjustmentStaffOverrideView.as_view()
        request = self._auth_post(
            path="/api/orders/adjustments/200/staff-override/",
            user=self.staff_user,
            data={
                "amount": "25.00",
            },
        )

        with patch.object(
            AdjustmentStaffOverrideView,
            "_get_adjustment_for_tenant",
            return_value=self.adjustment_request,
        ), patch.object(
            AdjustmentStaffOverrideView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, adjustment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notes", data)