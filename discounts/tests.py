from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Discount, SeasonalEvent

User = get_user_model()

class SeasonalEventTests(APITestCase):
    """Test cases for the SeasonalEvent API."""

    def setUp(self):
        """Set up test data."""
        self.event = SeasonalEvent.objects.create(
            name="Black Friday",
            description="Huge discounts for Black Friday!",
            start_date=now(),
            end_date=now() + timedelta(days=2),
            is_active=True,
        )

    def test_create_seasonal_event(self):
        """Ensure we can create a new promotional campaigns."""
        data = {
            "name": "Cyber Monday",
            "description": "Cyber Monday sale!",
            "start_date": now(),
            "end_date": now() + timedelta(days=1),
        }
        response = self.client.post("/api/seasonal-events/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Cyber Monday")

    def test_retrieve_seasonal_event(self):
        """Ensure we can retrieve an event."""
        response = self.client.get(f"/api/seasonal-events/{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.event.name)

    def test_update_seasonal_event(self):
        """Ensure we can update an event."""
        response = self.client.patch(f"/api/seasonal-events/{self.event.id}/", {"description": "Updated description"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, "Updated description")

    def test_delete_seasonal_event(self):
        """Ensure we can delete an event."""
        response = self.client.delete(f"/api/seasonal-events/{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SeasonalEvent.objects.filter(id=self.event.id).exists())


class DiscountTests(APITestCase):
    """Test cases for the Discount API."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.discount = Discount.objects.create(
            code="TEST10",
            discount_type="percentage",
            value=10,
            max_uses=5,
            used_count=0,
            start_date=now(),
            end_date=now() + timedelta(days=2),
            is_general=True,
            is_active=True,
        )

    def test_create_discount(self):
        """Ensure we can create a discount."""
        data = {
            "code": "NEWYEAR20",
            "discount_type": "fixed",
            "value": 20.00,
            "max_uses": 10,
            "start_date": now(),
            "end_date": now() + timedelta(days=3),
            "is_general": True,
        }
        response = self.client.post("/api/discounts/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "NEWYEAR20")

    def test_retrieve_discount(self):
        """Ensure we can retrieve a discount."""
        response = self.client.get(f"/api/discounts/{self.discount.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], self.discount.code)

    def test_update_discount(self):
        """Ensure we can update a discount."""
        response = self.client.patch(f"/api/discounts/{self.discount.id}/", {"value": 15})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.discount.refresh_from_db()
        self.assertEqual(self.discount.value, 15)

    def test_delete_discount(self):
        """Ensure we can delete a discount."""
        response = self.client.delete(f"/api/discounts/{self.discount.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Discount.objects.filter(id=self.discount.id).exists())

    def test_discount_usage_limit(self):
        """Ensure discount cannot be used beyond max_uses."""
        self.discount.used_count = 5
        self.discount.save()
        response = self.client.patch(f"/api/discounts/{self.discount.id}/", {"used_count": 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This discount code has reached its maximum usage.", str(response.data))

    def test_expired_discount(self):
        """Ensure expired discount is marked inactive."""
        self.discount.end_date = now() - timedelta(days=1)  # Set expiry date in the past
        self.discount.save()
        response = self.client.get(f"/api/discounts/{self.discount.id}/")
        self.assertEqual(response.data["is_active"], False)