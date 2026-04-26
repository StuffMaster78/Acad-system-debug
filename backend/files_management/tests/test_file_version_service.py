from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileVersion
from files_management.services import (
    FileAttachmentService,
    FileUploadService,
    FileVersionService,
)
from orders.models import Order
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileVersionServiceTests(TestCase):
    """
    Tests for file replacement and version history.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )
        self.client = user_model.objects.create_user(
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.staff = user_model.objects.create_user(
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )
        self.order = Order.objects.create(
            website=self.website,
            client=self.client,
        )
        self.old_file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.client,
            uploaded_file=SimpleUploadedFile(
                "draft.docx",
                b"old",
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            purpose=FilePurpose.ORDER_DRAFT,
        )
        self.attachment = FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=self.old_file,
            purpose=FilePurpose.ORDER_DRAFT,
            visibility=FileVisibility.ORDER_PARTICIPANTS,
            attached_by=self.client,
        )

    def test_replace_attachment_file_creates_version(self) -> None:
        updated_attachment = FileVersionService.replace_attachment_file(
            website=self.website,
            replaced_by=self.staff,
            attachment=self.attachment,
            uploaded_file=SimpleUploadedFile(
                "draft-v2.docx",
                b"new",
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            notes="Corrected draft.",
        )

        version = FileVersion.objects.get(
            file=updated_attachment.managed_file,
        )

        self.assertEqual(version.version_number, 2)
        self.assertEqual(version.replaced_file, self.old_file)
        self.assertEqual(version.created_by, self.staff)
        self.assertEqual(version.notes, "Corrected draft.")
        self.assertNotEqual(
            updated_attachment.managed_file.pk,
            self.old_file.pk,
        )