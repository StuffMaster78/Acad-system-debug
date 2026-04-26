from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from files_management.enums import FilePurpose, FileVisibility
from files_management.services import (
    FileAttachmentService,
    FileUploadService,
)
from orders.models import Order
from orders.services.order_file_download_service import (
    OrderFileDownloadService,
)
from websites.models import Website


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class OrderFileDownloadServiceTests(TestCase):
    """
    Tests for order-specific file download gates.
    """

    def setUp(self) -> None:
        user_model = get_user_model()

        self.website = Website.objects.create(
            name="Gradecrest",
            domain="gradecrest.test",
        )

        self.client_user = user_model.objects.create_user(
            username="Lulhaa",
            email="client@example.com",
            password="pass",
            website=self.website,
        )
        self.writer = user_model.objects.create_user(
            username="kenyaha",
            email="writer@example.com",
            password="pass",
            website=self.website,
        )
        self.staff = user_model.objects.create_user(
            username="Duntad",
            email="staff@example.com",
            password="pass",
            website=self.website,
            is_staff=True,
        )

        self.order = Order.objects.create(
            website=self.website,
            client=self.client,
            writer=self.writer,
            payment_status="pending",
        )

    def _make_attachment(self, *, purpose: str):
        managed_file = FileUploadService.upload_file(
            website=self.website,
            uploaded_by=self.writer,
            uploaded_file=SimpleUploadedFile(
                "paper.docx",
                b"content",
                content_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            ),
            purpose=purpose,
        )

        return FileAttachmentService.attach_managed_file(
            website=self.website,
            obj=self.order,
            managed_file=managed_file,
            purpose=purpose,
            visibility=FileVisibility.CLIENT_WRITER_STAFF,
            attached_by=self.writer,
        )

    def test_writer_can_download_order_file(self) -> None:
        attachment = self._make_attachment(
            purpose=FilePurpose.ORDER_DRAFT,
        )

        url = OrderFileDownloadService.get_download_url(
            order=self.order,
            user=self.writer,
            attachment=attachment,
        )

        self.assertTrue(url)

    def test_staff_can_download_order_file(self) -> None:
        attachment = self._make_attachment(
            purpose=FilePurpose.ORDER_FINAL,
        )

        url = OrderFileDownloadService.get_download_url(
            order=self.order,
            user=self.staff,
            attachment=attachment,
        )

        self.assertTrue(url)

    def test_client_cannot_download_final_when_unpaid(self) -> None:
        attachment = self._make_attachment(
            purpose=FilePurpose.ORDER_FINAL,
        )

        with self.assertRaises(PermissionDenied):
            OrderFileDownloadService.get_download_url(
                order=self.order,
                user=self.client,
                attachment=attachment,
            )

    def test_client_can_download_final_when_paid(self) -> None:
        attachment = self._make_attachment(
            purpose=FilePurpose.ORDER_FINAL,
        )

        self.order.payment_status = "paid"
        self.order.save(update_fields=["payment_status"])

        url = OrderFileDownloadService.get_download_url(
            order=self.order,
            user=self.client,
            attachment=attachment,
        )

        self.assertTrue(url)

    def test_cross_tenant_user_cannot_download(self) -> None:
        other_website = Website.objects.create(
            name="Other",
            domain="other.test",
        )
        other_user = get_user_model().objects.create_user(
            username="Doooduh",
            email="other@example.com",
            password="pass",
            website=other_website,
        )
        attachment = self._make_attachment(
            purpose=FilePurpose.ORDER_DRAFT,
        )

        with self.assertRaises(PermissionDenied):
            OrderFileDownloadService.get_download_url(
                order=self.order,
                user=other_user,
                attachment=attachment,
            )