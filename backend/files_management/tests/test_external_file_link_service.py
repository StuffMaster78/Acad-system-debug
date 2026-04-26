from django.contrib.auth import get_user_model
from django.test import TestCase

from files_management.enums import (
    ExternalFileProvider,
    ExternalFileReviewStatus,
    FilePurpose,
)
from files_management.exceptions import ExternalFileLinkError
from files_management.models import FilePolicy
from files_management.services import ExternalFileLinkService
from websites.models import Website


class ExternalFileLinkServiceTests(TestCase):
    """
    Tests for external link submission and review.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )
        self.user = user_model.objects.create_user(
            username="Testuser2"
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.staff = user_model.objects.create_user(
            username="Testusero"
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )

    def test_rejects_external_link_when_policy_disallows_it(self) -> None:
        with self.assertRaises(ExternalFileLinkError):
            ExternalFileLinkService.submit_link(
                website=self.website,
                submitted_by=self.user,
                url="https://docs.google.com/document/d/abc",
                purpose=FilePurpose.ORDER_INSTRUCTION,
            )

    def test_submits_pending_external_link_when_review_required(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Order references",
            purpose=FilePurpose.ORDER_REFERENCE,
            allow_external_links=True,
            external_links_require_review=True,
        )

        link = ExternalFileLinkService.submit_link(
            website=self.website,
            submitted_by=self.user,
            url="https://docs.google.com/document/d/abc",
            purpose=FilePurpose.ORDER_REFERENCE,
            title="Google Doc",
        )

        self.assertEqual(link.review_status, ExternalFileReviewStatus.PENDING)
        self.assertEqual(link.provider, ExternalFileProvider.GOOGLE_DOCS)

    def test_approve_external_link(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Order references",
            purpose=FilePurpose.ORDER_REFERENCE,
            allow_external_links=True,
            external_links_require_review=True,
        )
        link = ExternalFileLinkService.submit_link(
            website=self.website,
            submitted_by=self.user,
            url="https://drive.google.com/file/d/abc",
            purpose=FilePurpose.ORDER_REFERENCE,
        )

        approved = ExternalFileLinkService.approve_link(
            external_link=link,
            reviewed_by=self.staff,
            review_note="Safe.",
        )

        self.assertEqual(
            approved.review_status,
            ExternalFileReviewStatus.APPROVED,
        )
        self.assertEqual(approved.reviewed_by, self.staff)