from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from files_management.enums import (
    FileAccessAction,
    FileLifecycleStatus,
    FilePurpose,
    FileScanStatus,
    FileVisibility,
)
from files_management.models import FileAccessGrant
from files_management.services import (
    FileAccessService,
    FileAttachmentService,
    FileUploadService,
)
from orders.models import Order
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileAccessServiceTests(TestCase):
    """
    Tests for generic and policy-based file access decisions.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )
        self.client_user = user_model.objects.create_user(
            username="Tester",
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.writer = user_model.objects.create_user(
            username="Teri",
            email="writer@example.com",
            password="pass",
            website=self.website,
        )
        self.staff = user_model.objects.create_user(
            username="Toror",
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )
        self.order = Order.objects.create(
            website=self.website,
            client=self.client,
            writer=self.writer,
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

    def test_order_client_can_view_order_file(self) -> None:
        allowed = FileAccessService.can_access(
            user=self.client,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertTrue(allowed)

    def test_assigned_writer_can_view_order_file(self) -> None:
        allowed = FileAccessService.can_access(
            user=self.writer,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertTrue(allowed)

    def test_staff_can_view_order_file(self) -> None:
        allowed = FileAccessService.can_access(
            user=self.staff,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertTrue(allowed)

    def test_quarantined_file_cannot_be_accessed(self) -> None:
        self.file.lifecycle_status = FileLifecycleStatus.QUARANTINED
        self.file.save(update_fields=["lifecycle_status", "updated_at"])

        allowed = FileAccessService.can_access(
            user=self.client,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertFalse(allowed)

    def test_flagged_file_cannot_be_accessed(self) -> None:
        self.file.scan_status = FileScanStatus.FLAGGED
        self.file.save(update_fields=["scan_status", "updated_at"])

        allowed = FileAccessService.can_access(
            user=self.client,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertFalse(allowed)

    def test_explicit_grant_allows_access(self) -> None:
        outsider = get_user_model().objects.create_user(
            username="TestuserH",
            email="outsider@example.com",
            password="pass",
            website=self.website,
        )

        FileAccessGrant.objects.create(
            website=self.website,
            managed_file=self.file,
            attachment=self.attachment,
            grantee=outsider,
            granted_by=self.staff,
            action=FileAccessAction.VIEW,
        )

        allowed = FileAccessService.can_access(
            user=outsider,
            website=self.website,
            attachment=self.attachment,
            action=FileAccessAction.VIEW,
        )

        self.assertTrue(allowed)