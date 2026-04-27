from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import cast, Any

from django.test import TestCase
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient

from billing.services.invoice_service import InvoiceService
from billing.services.payment_request_service import (
    PaymentRequestService,
)
from websites.models.websites import Website
from users.models import User


class ClientBillingViewsTests(TestCase):
    """
    Verify client-scoped invoice and payment-request summary endpoints.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.com",
        )
        self.client_one = User.objects.create_user(
            username="testuser",
            email="one@example.com",
            password="testpass123",
            website=self.website,
        )
        self.client_two = User.objects.create_user(
            username="testuserq",
            email="two@example.com",
            password="testpass123",
            website=self.website,
        )

        self.invoice_one = InvoiceService.create_invoice(
            website=self.website,
            title="Invoice one",
            amount=Decimal("500.00"),
            due_at=timezone.now() + timedelta(days=7),
            issued_by=self.client_one,
            purpose="special_order",
            client=self.client_one,
            recipient_email=self.client_one.email,
            recipient_name="Client One",
            currency="USD",
        )
        self.invoice_two = InvoiceService.create_invoice(
            website=self.website,
            title="Invoice two",
            amount=Decimal("700.00"),
            due_at=timezone.now() + timedelta(days=7),
            issued_by=self.client_two,
            purpose="special_order",
            client=self.client_two,
            recipient_email=self.client_two.email,
            recipient_name="Client Two",
            currency="USD",
        )

        self.payment_request_one = (
            PaymentRequestService.create_payment_request(
                website=self.website,
                title="Adjustment one",
                amount=Decimal("150.00"),
                requested_by=self.client_one,
                purpose="order_adjustment",
                client=self.client_one,
                recipient_email=self.client_one.email,
                recipient_name="Client One",
                due_at=timezone.now() + timedelta(days=4),
                currency="USD",
            )
        )
        self.payment_request_two = (
            PaymentRequestService.create_payment_request(
                website=self.website,
                title="Adjustment two",
                amount=Decimal("175.00"),
                requested_by=self.client_two,
                purpose="order_adjustment",
                client=self.client_two,
                recipient_email=self.client_two.email,
                recipient_name="Client Two",
                due_at=timezone.now() + timedelta(days=4),
                currency="USD",
            )
        )

        self.api_client = APIClient()

    def test_client_invoice_list_only_returns_own_invoices(self) -> None:
        self.api_client.force_authenticate(user=self.client_one)

        response = cast(
            Response,
            self.api_client.get("/billing/my/invoices/"),
        )

        data = cast(list[dict[str, Any]], response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["reference"],
            self.invoice_one.reference,
        )

    def test_client_payment_request_list_only_returns_own_requests(
        self,
    ) -> None:
        self.api_client.force_authenticate(user=self.client_one)

        response = cast(
            Response,
            self.api_client.get("/billing/my/payment-requests/"),
        )

        data = cast(list[dict[str, Any]], response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["reference"],
            self.payment_request_one.reference,
        )

    def test_client_cannot_access_another_clients_invoice(self) -> None:
        self.api_client.force_authenticate(user=self.client_one)

        response = cast(
            Response,
            self.api_client.get(
                f"/billing/my/invoices/{self.invoice_two.pk}/"
            ),
        )

        self.assertEqual(response.status_code, 404)

    def test_client_cannot_access_another_clients_payment_request(
        self,
    ) -> None:
        self.api_client.force_authenticate(user=self.client_one)

        response = cast(
            Response,
            self.api_client.get(
                f"/billing/my/payment-requests/"
                f"{self.payment_request_two.pk}/"
            ),
        )

        self.assertEqual(response.status_code, 404)