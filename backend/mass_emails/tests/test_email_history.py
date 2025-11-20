import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.test import APIClient
from mass_emails.models import EmailCampaign, EmailRecipient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestEmailHistoryViews:

    def setup_method(self):
        self.user = User.objects.create_user(
            username="john", email="john@example.com", password="pass"
        )
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )

        self.campaign1 = EmailCampaign.objects.create(
            title="Welcome",
            subject="👋 Hello!",
            email_type="communication",
            body="<p>Welcome</p>",
            created_by=self.admin
        )

        self.campaign2 = EmailCampaign.objects.create(
            title="Promo",
            subject="🎉 Big Sale!",
            email_type="promos",
            body="<p>Sale</p>",
            created_by=self.admin
        )

        self.rec1 = EmailRecipient.objects.create(
            user=self.user,
            email=self.user.email,
            campaign=self.campaign1,
            status="sent",
            sent_at=now()
        )
        self.rec2 = EmailRecipient.objects.create(
            user=self.user,
            email=self.user.email,
            campaign=self.campaign2,
            status="opened",
            sent_at=now()
        )

    def test_user_history_requires_auth(self):
        url = reverse("user-email-history")
        client = APIClient()
        response = client.get(url)
        assert response.status_code == 401

    def test_user_history_returns_their_campaigns(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user-email-history")
        response = client.get(url)
        assert response.status_code == 200

        results = response.json()
        assert isinstance(results, list)
        assert len(results) == 2

        titles = [r["campaign"]["title"] for r in results]
        assert "Welcome" in titles
        assert "Promo" in titles

    def test_user_history_filters_work(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("user-email-history")
        response = client.get(url + "?status=opened")
        results = response.json()
        assert len(results) == 1
        assert results[0]["status"] == "opened"

    def test_admin_history_requires_admin(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        url = reverse("admin-email-history")
        response = client.get(url + "?user_id=" + str(self.user.id))
        assert response.status_code == 403

    def test_admin_can_view_any_user(self):
        client = APIClient()
        client.force_authenticate(user=self.admin)

        url = reverse("admin-email-history")
        response = client.get(url + f"?user_id={self.user.id}")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 2

    def test_admin_view_filters_work(self):
        client = APIClient()
        client.force_authenticate(user=self.admin)

        url = reverse("admin-email-history")
        response = client.get(url + f"?user_id={self.user.id}&email_type=promos")
        results = response.json()
        assert len(results) == 1
        assert results[0]["campaign"]["email_type"] == "promos"