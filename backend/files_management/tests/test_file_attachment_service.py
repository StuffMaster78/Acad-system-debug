from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.services import (
    FileAttachmentService,
    FileUploadService,
)
from orders.models import Order
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileAttachmentServiceTests(TestCase):
    """
    Tests for attaching managed files to domain objects.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )
        self.user = user_model.objects.create_user(
            username="TestUser"
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.order = Order.objects.create(
            website=self.website,
            client=self.user,
        )
        uploaded = SimpleUploadedFile(
            "instructions.pdf",
            b"content",
            content_type="application/pdf",
        )
        self.managed_file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.user,
            uploaded_file=uploaded,
            purpose=FilePurpose.ORDER_INSTRUCTION,
        )

    def test_attach_managed_file_to_order(self) -> None:
        attachment = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=self.managed_file,
            purpose=FilePurpose.ORDER_INSTRUCTION,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=self.user,
        )

        self.assertIsInstance(attachment, FileAttachment)
        self.assertEqual(attachment.website, self.website)
        self.assertEqual(attachment.managed_file, self.managed_file)
        self.assertEqual(attachment.content_object, self.order)
        self.assertEqual(
            attachment.purpose,
            FilePurpose.ORDER_INSTRUCTION,
        )

    def test_primary_attachment_clears_previous_primary(self) -> None:
        first = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=self.managed_file,
            purpose=FilePurpose.ORDER_FINAL,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
            attached_by=self.user,
            is_primary=True,
        )

        second_file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.user,
            uploaded_file=SimpleUploadedFile(
                "final.docx",
                b"new",
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            purpose=FilePurpose.ORDER_FINAL,
        )

        second = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=second_file,
            purpose=FilePurpose.ORDER_FINAL,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
            attached_by=self.user,
            is_primary=True,
        )

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)

    def test_deactivate_attachment_soft_detaches(self) -> None:
        attachment = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=self.managed_file,
            purpose=FilePurpose.ORDER_INSTRUCTION,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=self.user,
        )

        FileAttachmentService.deactivate_attachment(
            attachment=attachment,
            deactivated_by=self.user,
            reason="Wrong file.",
        )

        attachment.refresh_from_db()

        self.assertFalse(attachment.is_active)
        self.assertEqual(
            attachment.metadata["deactivation_reason"],
            "Wrong file.",
        )