from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from files_management.enums import (
    DeletionRequestScope,
    DeletionRequestStatus,
    FileLifecycleStatus,
    FilePurpose,
    FileVisibility,
)
from files_management.models import FileDeletionRequest
from files_management.services import (
    FileAttachmentService,
    FileDeletionService,
    FileUploadService,
)
from orders.models import Order
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileDeletionServiceTests(TestCase):
    """
    Tests for governed deletion workflows.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )
        self.client_user = user_model.objects.create_user(
            username="yeye",
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.staff = user_model.objects.create_user(
            username="Aasta",
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )
        self.order = Order.objects.create(
            website=self.website,
            client=self.client,
        )
        self.file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.client,
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
            managed_file=self.file,
            purpose=FilePurpose.ORDER_INSTRUCTION,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=self.client,
        )

    def test_client_can_request_deletion(self) -> None:
        request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client,
            attachment=self.attachment,
            reason="Wrong file.",
        )

        self.assertIsInstance(request, FileDeletionRequest)
        self.assertEqual(request.status, DeletionRequestStatus.PENDING)
        self.assertEqual(request.requested_by, self.client)

    def test_staff_can_approve_deletion_request(self) -> None:
        request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client,
            attachment=self.attachment,
            reason="Wrong file.",
        )

        approved = FileDeletionService.approve_request(
            deletion_request=request,
            reviewed_by=self.staff,
            admin_comment="Approved.",
        )

        self.assertEqual(approved.status, DeletionRequestStatus.APPROVED)

    def test_staff_can_complete_detach_only_request(self) -> None:
        request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client,
            attachment=self.attachment,
            reason="Wrong file.",
            scope=DeletionRequestScope.DETACH_ONLY,
        )
        FileDeletionService.approve_request(
            deletion_request=request,
            reviewed_by=self.staff,
        )

        completed = FileDeletionService.complete_request(
            deletion_request=request,
            completed_by=self.staff,
        )

        self.attachment.refresh_from_db()

        self.assertEqual(
            completed.status,
            DeletionRequestStatus.COMPLETED,
        )
        self.assertFalse(self.attachment.is_active)

    def test_staff_can_archive_file_from_request(self) -> None:
        request = FileDeletionService.request_deletion(
            website=self.website,
            requested_by=self.client,
            attachment=self.attachment,
            reason="Archive it.",
            scope=DeletionRequestScope.ARCHIVE_FILE,
        )
        FileDeletionService.approve_request(
            deletion_request=request,
            reviewed_by=self.staff,
        )

        FileDeletionService.complete_request(
            deletion_request=request,
            completed_by=self.staff,
        )

        self.file.refresh_from_db()

        self.assertEqual(
            self.file.lifecycle_status,
            FileLifecycleStatus.ARCHIVED,
        )