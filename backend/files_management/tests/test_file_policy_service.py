from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from files_management.enums import FilePurpose
from files_management.exceptions import FileValidationError
from files_management.models import FilePolicy
from files_management.services import FilePolicyService
from websites.models import Website


class FilePolicyServiceTests(TestCase):
    """
    Tests for tenant and purpose based file validation.
    """

    def setUp(self) -> None:
        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )

    def test_uses_default_policy_when_no_policy_exists(self) -> None:
        allowed = FilePolicyService.get_allowed_extensions(
            website=self.website,
            purpose=FilePurpose.ORDER_INSTRUCTION,
        )

        self.assertIn(".docx", allowed)
        self.assertIn(".pdf", allowed)

    def test_validates_uploaded_file_against_custom_policy(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Order finals",
            purpose=FilePurpose.ORDER_FINAL,
            allowed_extensions=[".docx"],
            allowed_mime_types=[
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document",
            ],
            max_file_size_bytes=1024,
        )

        uploaded = SimpleUploadedFile(
            "paper.docx",
            b"hello",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        mime_type = FilePolicyService.validate_uploaded_file(
            website=self.website,
            purpose=FilePurpose.ORDER_FINAL,
            uploaded_file=uploaded,
        )

        self.assertEqual(
            mime_type,
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document",
        )

    def test_rejects_disallowed_extension(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Message attachments",
            purpose=FilePurpose.MESSAGE_ATTACHMENT,
            allowed_extensions=[".pdf"],
            allowed_mime_types=["application/pdf"],
            max_file_size_bytes=1024,
        )

        uploaded = SimpleUploadedFile(
            "script.exe",
            b"bad",
            content_type="application/octet-stream",
        )

        with self.assertRaises(FileValidationError):
            FilePolicyService.validate_uploaded_file(
                website=self.website,
                purpose=FilePurpose.MESSAGE_ATTACHMENT,
                uploaded_file=uploaded,
            )

    def test_rejects_file_above_size_limit(self) -> None:
        FilePolicy.objects.create(
            website=self.website,
            name="Small PDFs",
            purpose=FilePurpose.ORDER_REFERENCE,
            allowed_extensions=[".pdf"],
            allowed_mime_types=["application/pdf"],
            max_file_size_bytes=2,
        )

        uploaded = SimpleUploadedFile(
            "rubric.pdf",
            b"large",
            content_type="application/pdf",
        )

        with self.assertRaises(FileValidationError):
            FilePolicyService.validate_uploaded_file(
                website=self.website,
                purpose=FilePurpose.ORDER_REFERENCE,
                uploaded_file=uploaded,
            )