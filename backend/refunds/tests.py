from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from ledger.constants import LedgerAccountType
from ledger.models import LedgerAccount
from payments_processor.enums import (
    PaymentIntentPurpose,
    PaymentIntentStatus,
    PaymentProvider,
)
from payments_processor.models import PaymentIntent, PaymentRefund
from refunds.models import Refund, RefundLog, RefundReceipt
from rest_framework import status
from rest_framework.test import APITestCase
from wallets.models import Wallet
from websites.models.websites import Website


User = get_user_model()


class RefundsAPITestCase(APITestCase):
    """Refund API and processing coverage."""

    def setUp(self):
        self.website = Website.objects.create(
            name="Refunds Site",
            domain="https://refunds.test",
        )
        self.client_user = User.objects.create_user(
            username="refund-client",
            email="refund-client@test.local",
            password="pass",
            role="client",
            website=self.website,
        )
        self.other_client = User.objects.create_user(
            username="refund-other",
            email="refund-other@test.local",
            password="pass",
            role="client",
            website=self.website,
        )
        self.staff_user = User.objects.create_user(
            username="refund-staff",
            email="refund-staff@test.local",
            password="pass",
            role="admin",
            website=self.website,
            is_staff=True,
        )
        self._create_ledger_accounts()
        self.payment = self._create_payment(
            reference="pi_refunds_001",
            client=self.client_user,
            amount=Decimal("100.00"),
        )
        self.refund_data = {
            "order_payment": self.payment.id,
            "wallet_amount": "50.00",
            "external_amount": "0.00",
            "reason": "Client cancellation",
        }

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_client_can_create_refund_request(self):
        self.authenticate(self.client_user)
        response = self.client.post(reverse("refund-list"), self.refund_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Refund.objects.count(), 1)

        refund = Refund.objects.get()
        self.assertEqual(refund.client, self.client_user)
        self.assertEqual(refund.website, self.website)
        self.assertEqual(refund.wallet_amount, Decimal("50.00"))
        self.assertEqual(refund.refund_method, Refund.METHOD_WALLET)
        self.assertEqual(refund.status, Refund.PENDING)

    def test_client_cannot_refund_another_clients_payment(self):
        self.authenticate(self.other_client)
        response = self.client.post(reverse("refund-list"), self.refund_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pending_refunds_reserve_refundable_balance(self):
        self.authenticate(self.client_user)
        self.client.post(reverse("refund-list"), self.refund_data)

        response = self.client.post(
            reverse("refund-list"),
            {
                "order_payment": self.payment.id,
                "wallet_amount": "60.00",
                "external_amount": "0.00",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_partial_refunds_are_allowed_up_to_paid_amount(self):
        self.authenticate(self.client_user)
        first = self.client.post(reverse("refund-list"), self.refund_data)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(
            reverse("refund-list"),
            {
                "order_payment": self.payment.id,
                "wallet_amount": "50.00",
                "external_amount": "0.00",
            },
        )

        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Refund.objects.count(), 2)

    def test_staff_processes_wallet_refund(self):
        refund = self._create_refund(wallet_amount=Decimal("50.00"))
        self.authenticate(self.staff_user)

        response = self.client.post(
            reverse("refund-process-refund", args=[refund.id]),
            {"reason": "Order canceled"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        refund.refresh_from_db()
        self.payment.refresh_from_db()

        wallet = Wallet.objects.get(owner_user=self.client_user)
        self.assertEqual(refund.status, Refund.PROCESSED)
        self.assertEqual(wallet.available_balance, Decimal("50.00"))
        self.assertEqual(self.payment.amount_refunded, Decimal("50.00"))
        self.assertEqual(
            self.payment.status,
            PaymentIntentStatus.PARTIALLY_REFUNDED,
        )
        self.assertTrue(RefundReceipt.objects.filter(refund=refund).exists())
        self.assertTrue(RefundLog.objects.filter(refund=refund).exists())

    def test_staff_processes_external_full_refund(self):
        refund = self._create_refund(
            wallet_amount=Decimal("0.00"),
            external_amount=Decimal("100.00"),
        )
        self.authenticate(self.staff_user)

        response = self.client.post(
            reverse("refund-process-refund", args=[refund.id]),
            {"reason": "Dispute resolved for client"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        refund.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(refund.status, Refund.PROCESSED)
        self.assertEqual(refund.refund_method, Refund.METHOD_EXTERNAL)
        self.assertEqual(PaymentRefund.objects.count(), 1)
        self.assertEqual(self.payment.amount_refunded, Decimal("100.00"))
        self.assertEqual(self.payment.status, PaymentIntentStatus.REFUNDED)

    def test_staff_processes_split_refund(self):
        refund = self._create_refund(
            wallet_amount=Decimal("30.00"),
            external_amount=Decimal("70.00"),
        )
        self.authenticate(self.staff_user)

        response = self.client.post(
            reverse("refund-process-refund", args=[refund.id]),
            {"reason": "Partial wallet credit requested"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )
        refund.refresh_from_db()
        self.payment.refresh_from_db()

        wallet = Wallet.objects.get(owner_user=self.client_user)
        self.assertEqual(refund.refund_method, Refund.METHOD_SPLIT)
        self.assertEqual(wallet.available_balance, Decimal("30.00"))
        self.assertEqual(PaymentRefund.objects.count(), 1)
        self.assertEqual(self.payment.amount_refunded, Decimal("100.00"))
        self.assertEqual(self.payment.status, PaymentIntentStatus.REFUNDED)

    def test_client_can_cancel_own_pending_refund(self):
        refund = self._create_refund(wallet_amount=Decimal("50.00"))
        self.authenticate(self.client_user)

        response = self.client.post(
            reverse("refund-cancel-refund", args=[refund.id]),
            {"reason": "Changed mind"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.REJECTED)

    def test_client_cannot_process_refund(self):
        refund = self._create_refund(wallet_amount=Decimal("50.00"))
        self.authenticate(self.client_user)

        response = self.client.post(
            reverse("refund-process-refund", args=[refund.id]),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_sees_all_refunds_and_client_sees_own_only(self):
        own = self._create_refund(wallet_amount=Decimal("10.00"))
        other_payment = self._create_payment(
            reference="pi_refunds_002",
            client=self.other_client,
            amount=Decimal("25.00"),
        )
        Refund.objects.create(
            order_payment=other_payment,
            wallet_amount=Decimal("25.00"),
            client=self.other_client,
            website=self.website,
        )

        self.authenticate(self.staff_user)
        staff_response = self.client.get(reverse("refund-list"))
        self.assertEqual(staff_response.data["count"], 2)

        self.authenticate(self.client_user)
        client_response = self.client.get(reverse("refund-list"))
        self.assertEqual(client_response.data["count"], 1)
        self.assertEqual(client_response.data["results"][0]["id"], own.id)

    def test_logs_and_receipts_are_read_only(self):
        refund = self._create_refund(wallet_amount=Decimal("50.00"))
        self.authenticate(self.staff_user)
        self.client.post(reverse("refund-process-refund", args=[refund.id]))

        self.authenticate(self.client_user)
        log_response = self.client.get(reverse("refund-log-list"))
        receipt_response = self.client.get(reverse("refund-receipt-list"))
        log_post = self.client.post(reverse("refund-log-list"), {})
        receipt_post = self.client.post(reverse("refund-receipt-list"), {})

        self.assertEqual(log_response.status_code, status.HTTP_200_OK)
        self.assertEqual(receipt_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            log_post.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            receipt_post.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_unauthenticated_access_is_rejected(self):
        response = self.client.get(reverse("refund-list"))
        self.assertIn(
            response.status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

    def _create_refund(
        self,
        *,
        wallet_amount: Decimal,
        external_amount: Decimal = Decimal("0.00"),
    ) -> Refund:
        return Refund.objects.create(
            order_payment=self.payment,
            wallet_amount=wallet_amount,
            external_amount=external_amount,
            client=self.client_user,
            website=self.website,
        )

    def _create_payment(
        self,
        *,
        reference: str,
        client,
        amount: Decimal,
    ) -> PaymentIntent:
        return PaymentIntent.objects.create(
            website=self.website,
            reference=reference,
            client=client,
            purpose=PaymentIntentPurpose.ORDER,
            provider=PaymentProvider.MOCK,
            status=PaymentIntentStatus.SUCCEEDED,
            amount=amount,
            currency="USD",
            provider_transaction_id=f"txn_{reference}",
        )

    def _create_ledger_accounts(self):
        accounts = [
            (
                "CLIENT_WALLET_LIABILITY",
                "Client Wallet Liability",
                LedgerAccountType.LIABILITY,
            ),
            (
                "REFUND_CLEARING",
                "Refund Clearing",
                LedgerAccountType.CLEARING,
            ),
        ]
        for code, name, account_type in accounts:
            LedgerAccount.objects.create(
                website=self.website,
                code=code,
                name=name,
                account_type=account_type,
                currency="USD",
                is_system_account=True,
            )
