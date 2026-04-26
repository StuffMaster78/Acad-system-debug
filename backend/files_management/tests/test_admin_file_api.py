from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from files_management.enums import (
    DeletionRequestScope,
    ExternalFileReviewStatus,
    FileAccessAction,
    FileLifecycleStatus,
    FilePurpose,
    FileScanStatus,
    FileVisibility,
)
from files_management.models import FilePolicy
from files_management.services import (
    ExternalFileLinkService,
    FileAttachmentService,
    FileDeletionService,
    FileScanService,
    FileUploadService,
)
from orders.models import Order
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class AdminFileApiTests(TestCase):
    """
    Tests for staff-facing file management API endpoints.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.client_api = APIClient()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )

        self.staff = user_model.objects.create_user(
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )
        self.client_user = user_model.objects.create_user(
            email="client@example.com",
            password="pass",
            website=self.website,
        )

        self.order = Order.objects.create(
            website=self.website,
            client=self.client_user,
        )

        self.managed_file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.client_user,
            uploaded_file=SimpleUploadedFile(
                "instructions.pdf",
                b"content",
                content_type="application/pdf",
            ),
            purpose=FilePurpose.ORDER_INSTRUCTION,
        )

        self.attachment = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=self.managed_file,
            purpose=FilePurpose.ORDER_INSTRUCTION,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=self.client_user,
        )

        self.client_api.force_authenticate(user=self.staff)

    def test_staff_can_create_file_policy(self) -> None:
        url = reverse("admin-file-policy-list-create")

        response = self.client_api.post(
            url,
            {
                "name": "Message files",
                "purpose": FilePurpose.MESSAGE_ATTACHMENT,
                "allowed_mime_types": ["application/pdf"],
                "allowed_extensions": [".pdf"],
                "max_file_size_bytes": 1024,
                "allow_external_links": False,
                "external_links_require_review": True,
                "allowed_external_providers": [],
                "require_scan_before_download": False,
                "require_review_before_download": False,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            FilePolicy.objects.filter(
                website=self.website,
                purpose=FilePurpose.MESSAGE_ATTACHMENT,
            ).exists()
        )

    def test_staff_can_list_files(self) -> None:
        url = reverse("admin-file-list")

        response = self.client_api.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_staff_can_approve_external_link(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Order references",
            purpose=FilePurpose.ORDER_REFERENCE,
            allow_external_links=True,
            external_links_require_review=True,
        )

        link = ExternalFileLinkService.submit_link(
            website=self.website,
            submitted_by=self.client_user,
            url="https://docs.google.com/document/d/abc",
            purpose=FilePurpose.ORDER_REFERENCE,
        )

        url = reverse(
            "admin-external-link-approve",
            kwargs={"link_id": link.id},
        )

        response = self.client_api.post(
            url,
            {"review_note": "Looks safe."},
            format="json",
        )

        link.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            link.review_status,
            ExternalFileReviewStatus.APPROVED,
        )

    def test_staff_can_reject_external_link(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Order references",
            purpose=FilePurpose.ORDER_REFERENCE,
            allow_external_links=True,
            external_links_require_review=True,
        )

        link = ExternalFileLinkService.submit_link(
            website=self.website,
            submitted_by=self.client_user,
            url="https://docs.google.com/document/d/abc",
            purpose=FilePurpose.ORDER_REFERENCE,
        )

        url = reverse(
            "admin-external-link-reject",
            kwargs={"link_id": link.id},
        )

        response = self.client_api.post(
            url,
            {"review_note": "Wrong document."},
            format="json",
        )

        link.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            link.review_status,
            ExternalFileReviewStatus.REJECTED,
        )
        self.assertFalse(link.is_active)

    def test_staff_can_approve_deletion_request(self) -> None:
        deletion_request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client_user,
            attachment=self.attachment,
            reason="Wrong file.",
            scope=DeletionRequestScope.DETACH_ONLY,
        )

        url = reverse(
            "admin-file-deletion-request-approve",
            kwargs={"request_id": deletion_request.id},
        )

        response = self.client_api.post(
            url,
            {"admin_comment": "Approved."},
            format="json",
        )

        deletion_request.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(deletion_request.status, "approved")

    def test_staff_can_complete_deletion_request(self) -> None:
        deletion_request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client_user,
            attachment=self.attachment,
            reason="Wrong file.",
            scope=DeletionRequestScope.DETACH_ONLY,
        )

        FileDeletionService.approve_request(
            deletion_request=deletion_request,
            reviewed_by=self.staff,
            admin_comment="Approved.",
        )

        url = reverse(
            "admin-file-deletion-request-complete",
            kwargs={"request_id": deletion_request.id},
        )

        response = self.client_api.post(
            url,
            {"admin_comment": "Completed."},
            format="json",
        )

        self.attachment.refresh_from_db()
        deletion_request.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(deletion_request.status, "completed")
        self.assertFalse(self.attachment.is_active)

    def test_staff_can_grant_access(self) -> None:
        url = reverse("admin-file-access-grant-create")

        response = self.client_api.post(
            url,
            {
                "managed_file_id": self.managed_file.id,
                "attachment_id": self.attachment.id,
                "grantee_id": self.client_user.id,
                "action": FileAccessAction.DOWNLOAD,
                "reason": "Support exception.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["action"], FileAccessAction.DOWNLOAD)

    def test_staff_can_release_quarantined_file(self) -> None:
        FileScanService.mark_flagged(
            managed_file=self.managed_file,
            scan_type="moderation",
            summary="Needs review.",
        )

        self.managed_file.refresh_from_db()

        self.assertEqual(
            self.managed_file.lifecycle_status,
            FileLifecycleStatus.QUARANTINED,
        )
        self.assertEqual(
            self.managed_file.scan_status,
            FileScanStatus.FLAGGED,
        )

        url = reverse(
            "admin-file-release-quarantine",
            kwargs={"file_id": self.managed_file.id},
        )

        response = self.client_api.post(
            url,
            {"summary": "Reviewed manually."},
            format="json",
        )

        self.managed_file.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.managed_file.lifecycle_status,
            FileLifecycleStatus.ACTIVE,
        )
        self.assertEqual(self.managed_file.scan_status, FileScanStatus.PASSED)