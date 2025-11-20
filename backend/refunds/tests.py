from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from refunds.models import Refund, RefundLog, RefundReceipt
from order_payments_management.models import OrderPayment
from django.utils import timezone

User = get_user_model()

class RefundsAPITestCase(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username="client", password="pass")
        self.staff_user = User.objects.create_user(username="staff", password="pass", is_staff=True)
        self.order_payment = OrderPayment.objects.create(
            # Fill with required fields for your OrderPayment model
            client=self.client_user,
            discounted_amount=100,
        )
        self.refund_data = {
            "order_payment": self.order_payment.id,
            "wallet_amount": 50,
            "external_amount": 0,
            "refund_method": "wallet",
        }

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_client_can_create_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Refund.objects.count(), 1)
        refund = Refund.objects.first()
        self.assertEqual(refund.client, self.client_user)
        self.assertEqual(refund.wallet_amount, 50)

    def test_client_cannot_update_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        update_url = reverse("refund-detail", args=[refund_id])
        response = self.client.put(update_url, {"wallet_amount": 80})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_client_cannot_delete_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        delete_url = reverse("refund-detail", args=[refund_id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_staff_can_retry_rejected_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        refund = Refund.objects.get(id=refund_id)
        refund.status = Refund.REJECTED
        refund.save()

        self.authenticate(self.staff_user)
        retry_url = reverse("refund-retry-refund", args=[refund_id])
        response = self.client.post(retry_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refund.refresh_from_db()
        self.assertEqual(refund.status, Refund.PROCESSED)

    def test_client_cannot_retry_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        refund = Refund.objects.get(id=refund_id)
        refund.status = Refund.REJECTED
        refund.save()
        retry_url = reverse("refund-retry-refund", args=[refund_id])
        response = self.client.post(retry_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_client_can_cancel_pending_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        cancel_url = reverse("refund-cancel-refund", args=[refund_id])
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refund = Refund.objects.get(id=refund_id)
        self.assertEqual(refund.status, Refund.REJECTED)

    def test_cannot_cancel_non_pending_refund(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]
        refund = Refund.objects.get(id=refund_id)
        refund.status = Refund.PROCESSED
        refund.save()
        cancel_url = reverse("refund-cancel-refund", args=[refund_id])
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_log_and_receipt_readonly(self):
        self.authenticate(self.client_user)
        # Create a refund to generate logs/receipts
        url = reverse("refund-list")
        response = self.client.post(url, self.refund_data)
        refund_id = response.data["id"]

        # Refund logs
        log_url = reverse("refund-log-list")
        response = self.client.get(log_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refund receipts
        receipt_url = reverse("refund-receipt-list")
        response = self.client.get(receipt_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to POST to logs/receipts (should fail)
        response = self.client.post(log_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(receipt_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_negative_refund_amount(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        data = self.refund_data.copy()
        data["wallet_amount"] = -10
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_refund_amounts(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        data = self.refund_data.copy()
        data["wallet_amount"] = 0
        data["external_amount"] = 0
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refund_exceeds_paid_amount(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        data = self.refund_data.copy()
        data["wallet_amount"] = 200  # More than discounted_amount
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        url = reverse("refund-list")
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_sees_all_refunds(self):
        # Create refund as client
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        self.client.post(url, self.refund_data)
        # Create another refund as staff for another client
        other_client = User.objects.create_user(username="other", password="pass")
        self.authenticate(self.staff_user)
        data = self.refund_data.copy()
        data["client"] = other_client.id
        data["order_payment"] = self.order_payment.id
        Refund.objects.create(client=other_client, order_payment=self.order_payment, wallet_amount=10, external_amount=0, refund_method="wallet")
        response = self.client.get(url)
        self.assertTrue(len(response.data) >= 2)

    def test_client_sees_only_own_refunds(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        self.client.post(url, self.refund_data)
        other_client = User.objects.create_user(username="other", password="pass")
        self.authenticate(other_client)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

    
    def test_client_only_sees_own_logs_and_receipts(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        self.client.post(url, self.refund_data)
        log_url = reverse("refund-log-list")
        receipt_url = reverse("refund-receipt-list")
        response = self.client.get(log_url)
        self.assertTrue(all(log["client"] == self.client_user.id for log in response.data))
        response = self.client.get(receipt_url)
        # If client field is present in receipt, check ownership
        if response.data and "client" in response.data[0]:
            self.assertTrue(all(r["client"] == self.client_user.id for r in response.data))

    def test_cannot_refund_twice(self):
        self.authenticate(self.client_user)
        url = reverse("refund-list")
        self.client.post(url, self.refund_data)
        response = self.client.post(url, self.refund_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)