from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from mass_emails.models import EmailCampaign, EmailRecipient, UnsubscribeLog
from mass_emails.models import CampaignAttachment
from mass_emails.services import MassEmailCampaignService
from websites.models.websites import Website


User = get_user_model()


class MassEmailCampaignWorkflowTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="https://gradecrest.test",
            is_active=True,
            default_sender_name="Gradecrest",
            marketing_sender_email="offers@gradecrest.test",
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@test.local",
            password="pass",
            role="admin",
            website=self.website,
        )
        self.client_user = User.objects.create_user(
            username="client",
            email="client@test.local",
            password="pass",
            role="client",
            website=self.website,
            first_name="Client",
        )
        self.writer_user = User.objects.create_user(
            username="writer",
            email="writer@test.local",
            password="pass",
            role="writer",
            website=self.website,
        )
        self.editor = User.objects.create_user(
            username="editor",
            email="editor@test.local",
            password="pass",
            role="editor",
            website=self.website,
        )
        self.client = APIClient()

    def test_staff_can_create_campaign_for_clients_and_writers(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/mass-emails/campaigns/",
            {
                "website": self.website.id,
                "title": "May Promo",
                "subject": "A practical offer",
                "body": "Hello {{ first_name }}",
                "email_type": "promos",
                "target_roles": ["client", "writer"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        campaign = EmailCampaign.objects.get(title="May Promo")
        self.assertEqual(campaign.created_by, self.admin)
        self.assertEqual(campaign.target_roles, ["client", "writer"])

    def test_non_staff_cannot_create_campaign(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.post(
            "/api/v1/mass-emails/campaigns/",
            {
                "website": self.website.id,
                "title": "Nope",
                "subject": "Nope",
                "body": "Nope",
                "target_roles": ["client"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_campaign_rejects_non_customer_target_roles(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(
            "/api/v1/mass-emails/campaigns/",
            {
                "website": self.website.id,
                "title": "Bad Target",
                "subject": "Bad Target",
                "body": "Nope",
                "target_roles": ["admin"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sync_recipients_skips_unsubscribed_users(self):
        campaign = EmailCampaign.objects.create(
            website=self.website,
            title="Promo",
            subject="Promo",
            body="Hello {{ first_name }}",
            email_type="promos",
            target_roles=["client", "writer"],
            created_by=self.admin,
        )
        UnsubscribeLog.objects.create(
            email=self.writer_user.email,
            user=self.writer_user,
        )

        created = MassEmailCampaignService.sync_recipients(campaign)

        self.assertEqual(created, 1)
        self.assertTrue(
            EmailRecipient.objects.filter(
                campaign=campaign,
                user=self.client_user,
            ).exists()
        )
        self.assertFalse(
            EmailRecipient.objects.filter(
                campaign=campaign,
                user=self.writer_user,
            ).exists()
        )

    def test_preview_renders_template_context(self):
        campaign = EmailCampaign.objects.create(
            website=self.website,
            title="Promo",
            subject="Promo",
            body="Hello {{ first_name }} at {{ website.name }}",
            email_type="promos",
            target_roles=["client"],
            created_by=self.admin,
        )

        html = MassEmailCampaignService.render_body(
            campaign=campaign,
            user=self.client_user,
        )

        self.assertEqual(html, "Hello Client at Gradecrest")

    def test_campaign_attachment_uses_files_management(self):
        self.client.force_authenticate(user=self.admin)
        campaign = EmailCampaign.objects.create(
            website=self.website,
            title="Promo",
            subject="Promo",
            body="Hello",
            email_type="promos",
            target_roles=["client"],
            created_by=self.admin,
        )
        uploaded_file = SimpleUploadedFile(
            "promo.pdf",
            b"promo content",
            content_type="application/pdf",
        )

        response = self.client.post(
            "/api/v1/mass-emails/attachments/",
            {
                "campaign": campaign.id,
                "name": "Promo PDF",
                "uploaded_file": uploaded_file,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        campaign_attachment = CampaignAttachment.objects.get(
            campaign=campaign,
        )
        self.assertEqual(campaign_attachment.name, "Promo PDF")
        self.assertEqual(
            campaign_attachment.attachment.managed_file.original_name,
            "promo.pdf",
        )
        self.assertEqual(
            campaign_attachment.attachment.purpose,
            "mass_email_attachment",
        )
