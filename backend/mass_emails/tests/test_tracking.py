import pytest
from django.urls import reverse
from django.utils.timezone import now
from mass_emails.models import (
    EmailCampaign, EmailRecipient,
    EmailOpenTracker, EmailClickTracker, UnsubscribeLog
)
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEmailTrackingEndpoints:

    def setup_method(self):
        self.user = User.objects.create_user(
            username="client1", email="client1@example.com", password="pass"
        )
        self.campaign = EmailCampaign.objects.create(
            title="Spring Sale", subject="🌼 50% Off!", body="<p>Hello</p>",
            email_type="promos", created_by=self.user
        )
        self.recipient = EmailRecipient.objects.create(
            user=self.user,
            campaign=self.campaign,
            email=self.user.email,
            status="sent",
            sent_at=now()
        )

    def test_track_open_creates_tracker_once(self, client):
        url = reverse("email-track-open", args=[self.recipient.id])

        # Hit open pixel
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "image/gif"

        # DB check
        assert EmailOpenTracker.objects.filter(recipient=self.recipient).exists()

        # Hitting again does not duplicate
        client.get(url)
        assert EmailOpenTracker.objects.filter(recipient=self.recipient).count() == 1

        # Status should be updated to 'opened'
        self.recipient.refresh_from_db()
        assert self.recipient.status == "opened"
        assert self.recipient.opened_at is not None

    def test_track_click_creates_log_and_redirects(self, client):
        url = reverse("email-track-click", args=[self.recipient.id])
        destination = "https://example.com"

        response = client.get(f"{url}?url={destination}")
        assert response.status_code == 302
        assert response.url == destination

        click = EmailClickTracker.objects.filter(recipient=self.recipient).first()
        assert click is not None
        assert click.url == destination

    def test_click_missing_url_returns_400(self, client):
        url = reverse("email-track-click", args=[self.recipient.id])
        response = client.get(url)
        assert response.status_code == 400
        assert b"Missing 'url'" in response.content

    def test_unsubscribe_creates_log(self, client):
        url = reverse("email-unsubscribe", args=[self.recipient.id])
        response = client.get(url)

        assert response.status_code == 200
        assert b"unsubscribed" in response.content.lower()

        unsub = UnsubscribeLog.objects.filter(email=self.recipient.email).first()
        assert unsub is not None
        assert unsub.user == self.user

    def test_invalid_recipient_id_returns_404(self, client):
        for route_name in ["email-track-open", "email-track-click", "email-unsubscribe"]:
            url = reverse(route_name, args=[9999])
            response = client.get(url)
            assert response.status_code == 404