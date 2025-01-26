from django.test import TestCase
from .models import Discount
from websites.models import Website

class DiscountModelTest(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Test Website", domain="https://test.com")
        self.discount = Discount.objects.create(
            code="TEST10",
            discount_type="fixed",
            value=10.00,
            website=self.website,
            max_uses=5,
            start_date="2025-01-01 00:00:00",
            end_date="2025-12-31 23:59:59",
        )

    def test_discount_creation(self):
        self.assertEqual(self.discount.code, "TEST10")
        self.assertTrue(self.discount.is_valid())

    def test_increment_usage(self):
        self.discount.increment_usage()
        self.assertEqual(self.discount.used_count, 1)