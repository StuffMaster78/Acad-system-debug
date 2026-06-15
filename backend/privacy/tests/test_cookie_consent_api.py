from __future__ import annotations

from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from privacy.models import CookieConsentRecord
from websites.models.websites import Website


@override_settings(ALLOWED_HOSTS=["testserver", "nursemygrade.com"])
class CookieConsentApiTests(APITestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="NurseMyGrade",
            domain="https://nursemygrade.com",
            google_analytics_id="G-NURSE123",
        )
        self.host = "nursemygrade.com"

    def test_cookie_config_resolves_website_and_ga4(self):
        response = self.client.get(
            reverse("privacy:cookie-config"),
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["website"]["id"], self.website.id)
        self.assertEqual(
            response.data["integrations"]["ga4_measurement_id"],
            "G-NURSE123",
        )
        categories = {item["key"]: item for item in response.data["categories"]}
        self.assertTrue(categories["necessary"]["required"])
        self.assertFalse(categories["analytics"]["default"])

    def test_current_returns_empty_before_consent(self):
        response = self.client.get(
            reverse("privacy:cookie-consent-current"),
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["has_consent"])
        self.assertIsNone(response.data["consent"])

    def test_records_cookie_consent_for_resolved_website(self):
        response = self.client.post(
            reverse("privacy:cookie-consent"),
            {
                "preferences": True,
                "analytics": True,
                "marketing": False,
                "source": "banner",
            },
            format="json",
            HTTP_HOST=self.host,
            HTTP_USER_AGENT="Consent Test Browser",
            REMOTE_ADDR="203.0.113.10",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("writing_system.cookie_consent_id", response.cookies)

        record = CookieConsentRecord.objects.get()
        self.assertEqual(record.website, self.website)
        self.assertTrue(record.necessary)
        self.assertTrue(record.preferences)
        self.assertTrue(record.analytics)
        self.assertFalse(record.marketing)
        self.assertEqual(record.source_host, self.host)
        self.assertEqual(len(record.ip_hash), 64)
        self.assertEqual(len(record.user_agent_hash), 64)

    def test_current_uses_consent_cookie(self):
        created = self.client.post(
            reverse("privacy:cookie-consent"),
            {"preferences": False, "analytics": True, "marketing": False},
            format="json",
            HTTP_HOST=self.host,
        )
        consent_id = created.data["anonymous_id"]

        response = self.client.get(
            reverse("privacy:cookie-consent-current"),
            HTTP_HOST=self.host,
            HTTP_X_CONSENT_ID=consent_id,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["has_consent"])
        self.assertTrue(response.data["consent"]["analytics"])
        self.assertEqual(response.data["anonymous_id"], consent_id)

    def test_revoke_marks_existing_records_and_creates_rejection_record(self):
        created = self.client.post(
            reverse("privacy:cookie-consent"),
            {"preferences": True, "analytics": True, "marketing": True},
            format="json",
            HTTP_HOST=self.host,
        )
        consent_id = created.data["anonymous_id"]

        response = self.client.post(
            reverse("privacy:cookie-consent-revoke"),
            {},
            format="json",
            HTTP_HOST=self.host,
            HTTP_X_CONSENT_ID=consent_id,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["revoked"], 1)
        self.assertFalse(response.data["consent"]["preferences"])
        self.assertFalse(response.data["consent"]["analytics"])
        self.assertFalse(response.data["consent"]["marketing"])
        self.assertEqual(CookieConsentRecord.objects.count(), 2)
        self.assertEqual(CookieConsentRecord.objects.filter(revoked_at__isnull=False).count(), 1)
