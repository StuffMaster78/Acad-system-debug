from django.test import TestCase
from users.models import User
from .models import ClientProfile, LoyaltyTransaction


class ClientProfileTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="test_client", email="client@test.com", password="password123", role="client"
        )
        self.writer_user = User.objects.create_user(
            username="test_writer", email="writer@test.com", password="password123", role="writer"
        )

    def test_client_profile_creation(self):
        client_profile = ClientProfile.objects.get(client=self.client_user)
        self.assertEqual(client_profile.loyalty_points, 0)
        self.assertEqual(client_profile.total_spent, 0.00)

    def test_loyalty_transaction(self):
        client_profile = ClientProfile.objects.get(client=self.client_user)
        LoyaltyTransaction.objects.create(client=client_profile, points=50, transaction_type="add")
        self.assertEqual(client_profile.loyalty_transactions.count(), 1)