import pytest
from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework.test import APIClient
from mass_emails.models import (
    EmailCampaign, EmailRecipient,
    EmailOpenTracker, EmailClickTracker, UnsubscribeLog
)
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestCampaignAnalytics:

    def setup_method(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="pass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.campaign = EmailCampaign.objects.create(
            title="March Blast",
            subject="🔥 New Promo",
            body="<p>Body</p>",
            email_type="marketing",
            sent_time=now() - timedelta(days=2),
            created_by=self.admin
        )

        self.recipients = []
        for i in range(5):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@test.com"
            )
            r = EmailRecipient.objects.create(
                user=user, email=user.email,
                campaign=self.campaign,
                sent_at=now() - timedelta(days=2)
            )
            self.recipients.append(r)

        # simulate some opens and clicks
        EmailOpenTracker.objects.create(recipient=self.recipients[0])
        EmailOpenTracker.objects.create(recipient=self.recipients[1])
        EmailClickTracker.objects.create(recipient=self.recipients[0], url="https://link.com")

        UnsubscribeLog.objects.create(email=self.recipients[4].email)

    def test_summary_dashboard(self):
        url = reverse("campaign-analytics")
        response = self.client.get(url)
        assert response.status_code == 200

        data = response.json()["results"]
        assert len(data) >= 1

        campaign = data[0]
        assert campaign["title"] == self.campaign.title
        assert campaign["opens"] == 2
        assert campaign["clicks"] == 1
        assert campaign["unsubscribes"] == 1

    def test_summary_with_date_filter(self):
        url = reverse("campaign-analytics")
        response = self.client.get(url + "?start=2025-03-01&end=2025-03-31")
        assert response.status_code == 200
        assert "results" in response.json()

    def test_trending_data(self):
        url = reverse("campaign-trending")
        response = self.client.get(url)
        assert response.status_code == 200
        data = response.json()

        assert "labels" in data
        assert "opens" in data
        assert "clicks" in data
        assert "unsubscribes" in data
        assert len(data["labels"]) == 7