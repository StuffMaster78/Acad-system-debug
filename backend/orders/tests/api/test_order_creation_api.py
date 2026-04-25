from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.order_creation.order_creation_views import (
    CreateOrderView,
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


class OrderCreationAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.other_website = SimpleNamespace(pk=99)

        self.user = FakeUser(
            pk=1,
            website=self.website,
            is_staff=False,
        )
        self.staff_user = FakeUser(
            pk=2,
            website=self.website,
            is_staff=True,
        )

    def _payload(self) -> dict[str, Any]:
        return {
            "topic": "Healthcare policy analysis",
            "paper_type_id": 1,
            "pricing_snapshot_id": 11,
            "client_deadline": (
                timezone.now() + timedelta(days=2)
            ).isoformat(),
            "writer_deadline": (
                timezone.now() + timedelta(days=1)
            ).isoformat(),
            "order_instructions": "Use APA 7th edition.",
            "payment_provider": "stripe",
            "payment_method_code": "card",
        }

    def _auth_post(
        self,
        *,
        user: FakeUser,
        data: dict[str, Any],
    ) -> Request:
        request = self.factory.post(
            "/orders/create/",
            data,
            format="json",
        )
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    @staticmethod
    def _order_stub(
        *,
        pk: int = 100,
        is_fully_paid: bool = False,
        total_price: str = "120.00",
        amount_paid: str = "0.00",
        remaining_balance: str = "120.00",
        status: str = "pending_payment",
        payment_status: str = "unpaid",
    ) -> Any:
        return SimpleNamespace(
            pk=pk,
            topic="Healthcare policy analysis",
            status=status,
            payment_status=payment_status,
            total_price=total_price,
            amount_paid=amount_paid,
            remaining_balance=remaining_balance,
            currency="USD",
            service_family="writing",
            service_code="essay",
            is_composite=False,
            client_deadline=timezone.now() + timedelta(days=2),
            writer_deadline=timezone.now() + timedelta(days=1),
            pricing_snapshot=SimpleNamespace(pk=11),
            is_fully_paid=is_fully_paid,
        )

    @staticmethod
    def _payment_intent_stub() -> Any:
        return SimpleNamespace(
            pk=501,
            reference="pi_123",
            status="pending",
            amount="120.00",
            currency="USD",
            provider="stripe",
            client_secret="secret_123",
            checkout_url="https://checkout.example.com",
        )

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderPaymentApplicationService.start_checkout"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_create_order_starts_checkout_for_unpaid_order(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
        mock_start_checkout: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        order_stub = self._order_stub(is_fully_paid=False)
        mock_create_order.return_value = order_stub
        mock_start_checkout.return_value = self._payment_intent_stub()

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.user, data=self._payload())

        response = cast(DRFResponse, view(request))
        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["message"], "Order created successfully.")
        self.assertTrue(data["checkout_started"])
        self.assertEqual(data["order"]["id"], 100)
        self.assertEqual(data["payment_intent"]["reference"], "pi_123")

        mock_create_order.assert_called_once()
        mock_start_checkout.assert_called_once_with(
            order=order_stub,
            provider="stripe",
            payment_method_code="card",
            triggered_by=self.user,
            metadata={
                "source": "order_creation_api",
            },
        )

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderPaymentApplicationService.start_checkout"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_create_order_skips_checkout_for_fully_paid_order(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
        mock_start_checkout: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        order_stub = self._order_stub(
            pk=101,
            is_fully_paid=True,
            total_price="0.00",
            amount_paid="0.00",
            remaining_balance="0.00",
            status="ready_for_staffing",
            payment_status="fully_paid",
        )
        mock_create_order.return_value = order_stub

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.user, data=self._payload())

        response = cast(DRFResponse, view(request))
        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(data["checkout_started"])
        self.assertIsNone(data["payment_intent"])
        mock_start_checkout.assert_not_called()

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderPaymentApplicationService.start_checkout"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_create_order_skips_checkout_when_provider_omitted(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
        mock_start_checkout: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        order_stub = self._order_stub(is_fully_paid=False)
        mock_create_order.return_value = order_stub

        payload = self._payload()
        payload.pop("payment_provider", None)

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.user, data=payload)

        response = cast(DRFResponse, view(request))
        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(data["checkout_started"])
        self.assertIsNone(data["payment_intent"])
        mock_start_checkout.assert_not_called()

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer._get_user_model"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_staff_can_create_for_another_client_same_tenant(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
        mock_get_user_model: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        client_stub = SimpleNamespace(pk=55, website_id=10)
        mock_get_user_model.return_value.objects.get.return_value = client_stub

        order_stub = self._order_stub(pk=102, is_fully_paid=True)
        mock_create_order.return_value = order_stub

        payload = self._payload()
        payload["client_id"] = 55

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.staff_user, data=payload)

        response = cast(DRFResponse, view(request))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        create_kwargs = mock_create_order.call_args.kwargs
        self.assertEqual(create_kwargs["client"], client_stub)

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer._get_user_model"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_staff_cannot_create_for_client_in_other_tenant(
        self,
        mock_serializer_class: Any,
        mock_get_user_model: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        cross_tenant_client = SimpleNamespace(pk=77, website_id=99)
        mock_get_user_model.return_value.objects.get.return_value = (
            cross_tenant_client
        )

        payload = self._payload()
        payload["client_id"] = 77

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.staff_user, data=payload)

        with self.assertRaises(Exception):
            view(request)

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderPaymentApplicationService.start_checkout"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_create_order_serializes_expected_order_fields(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
        mock_start_checkout: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        order_stub = self._order_stub(is_fully_paid=False)
        mock_create_order.return_value = order_stub
        mock_start_checkout.return_value = self._payment_intent_stub()

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.user, data=self._payload())

        response = cast(DRFResponse, view(request))
        data = self._data(response)
        order_data = cast(dict[str, Any], data["order"])

        self.assertEqual(order_data["topic"], "Healthcare policy analysis")
        self.assertEqual(order_data["status"], "pending_payment")
        self.assertEqual(order_data["payment_status"], "unpaid")
        self.assertEqual(order_data["total_price"], "120.00")
        self.assertEqual(order_data["amount_paid"], "0.00")
        self.assertEqual(order_data["remaining_balance"], "120.00")
        self.assertEqual(order_data["currency"], "USD")
        self.assertEqual(order_data["service_family"], "writing")
        self.assertEqual(order_data["service_code"], "essay")
        self.assertEqual(order_data["pricing_snapshot_id"], 11)

    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "OrderCreationService.create_order"
    )
    @patch(
        "orders.api.views.order_creation.order_creation_views."
        "CreateOrderSerializer"
    )
    def test_non_staff_client_id_is_ignored_and_request_user_is_used(
        self,
        mock_serializer_class: Any,
        mock_create_order: Any,
    ) -> None:
        serializer_instance = mock_serializer_class.return_value
        serializer_instance.is_valid.return_value = True
        serializer_instance.validated_data = {
            "pricing_snapshot": SimpleNamespace(pk=11),
        }
        serializer_instance.to_order_payload.return_value = {
            "topic": "Healthcare policy analysis",
            "paper_type": SimpleNamespace(pk=1),
            "client_deadline": timezone.now() + timedelta(days=2),
            "writer_deadline": timezone.now() + timedelta(days=1),
            "order_instructions": "Use APA 7th edition.",
        }

        order_stub = self._order_stub(pk=103, is_fully_paid=True)
        mock_create_order.return_value = order_stub

        payload = self._payload()
        payload["client_id"] = 999

        view = CreateOrderView.as_view()
        request = self._auth_post(user=self.user, data=payload)

        response = cast(DRFResponse, view(request))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        create_kwargs = mock_create_order.call_args.kwargs
        self.assertEqual(create_kwargs["client"], self.user)