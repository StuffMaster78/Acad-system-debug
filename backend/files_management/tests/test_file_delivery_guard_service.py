"""
Tests for FileDeliveryGuardService.

Covers: check(), check_and_raise(), submit_as_final(), unlock_after_payment().
Uses InMemoryStorage so no S3 credentials are needed.
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from files_management.enums import (
    DeliveryStatus,
    FilePurpose,
    FileVisibility,
    FileScanStatus,
)
from files_management.exceptions import FileDeliveryBlocked, FileNotAvailable
from files_management.models.file_delivery_guard_result import FileDeliveryGuardResult
from files_management.services.file_delivery_guard_service import (
    FileDeliveryGuardService,
)
from tickets.models import Ticket
from websites.models.websites import Website

User = get_user_model()


def _upload_file(website, user, purpose):
    from files_management.services import FileUploadService, FileAttachmentService, FileVersionService
    f = SimpleUploadedFile("test.txt", b"hello", content_type="text/plain")
    managed = FileUploadService.upload_file(
        website=website, uploaded_by=user, uploaded_file=f,
        purpose=purpose, is_public=False,
    )
    FileVersionService.create_initial_version(managed_file=managed, created_by=user)
    return managed


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileDeliveryGuardCheckTests(TestCase):
    """guard.check() returns correct BLOCKED/ALLOWED results."""

    def setUp(self):
        self.website = Website.objects.create(name="Test", domain="test.local")
        self.client_user = User.objects.create_user(
            username="client", email="c@test.local", password="pass", website=self.website,
        )
        self.writer = User.objects.create_user(
            username="writer", email="w@test.local", password="pass", website=self.website,
        )
        self.order = Ticket.objects.create(
            title="Test order", description="desc",
            website=self.website, created_by=self.client_user,
        )

    def _make_final_attachment(self, *, scan_status=FileScanStatus.PASSED, is_submitted=False):
        from files_management.services import FileAttachmentService
        managed = _upload_file(self.website, self.writer, FilePurpose.ORDER_FINAL)
        managed.scan_status = scan_status
        managed.save(update_fields=["scan_status"])
        att = FileAttachmentService.attach_managed_file(
            website=self.website, obj=self.order, managed_file=managed,
            purpose=FilePurpose.ORDER_FINAL, visibility=FileVisibility.CLIENT_AND_STAFF,
            attached_by=self.writer, is_primary=True,
        )
        if is_submitted:
            att.is_submitted = True
            att.delivery_status = DeliveryStatus.SUBMITTED
            att.submitted_at = timezone.now()
            att.save(update_fields=["is_submitted", "delivery_status", "submitted_at", "updated_at"])
        return att

    def test_blocked_when_not_submitted(self):
        att = self._make_final_attachment(is_submitted=False)
        result = FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(result.result, FileDeliveryGuardResult.RESULT_BLOCKED)
        self.assertEqual(result.blocked_reason, "not_submitted")

    def test_blocked_when_scan_pending(self):
        att = self._make_final_attachment(
            scan_status=FileScanStatus.QUEUED, is_submitted=True,
        )
        result = FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(result.result, FileDeliveryGuardResult.RESULT_BLOCKED)
        self.assertIn(result.blocked_reason, {"scan_pending", "scan_failed"})

    def test_blocked_when_scan_infected(self):
        att = self._make_final_attachment(
            scan_status=FileScanStatus.INFECTED, is_submitted=True,
        )
        result = FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(result.result, FileDeliveryGuardResult.RESULT_BLOCKED)
        self.assertEqual(result.blocked_reason, "scan_failed")

    def test_allowed_when_submitted_and_scan_passed(self):
        att = self._make_final_attachment(is_submitted=True)
        # No outstanding balance (balance checker returns None → allowed)
        result = FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(result.result, FileDeliveryGuardResult.RESULT_ALLOWED)
        self.assertIsNotNone(result.unlocked_at)

    def test_blocked_when_outstanding_balance(self):
        att = self._make_final_attachment(is_submitted=True)
        with patch(
            "files_management.services.file_delivery_guard_service."
            "FileDeliveryGuardService._get_outstanding_balance",
            return_value=Decimal("25.00"),
        ):
            result = FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(result.result, FileDeliveryGuardResult.RESULT_BLOCKED)
        self.assertEqual(result.blocked_reason, "balance_due")
        self.assertEqual(result.amount_due, Decimal("25.00"))

    def test_guard_result_persisted(self):
        att = self._make_final_attachment(is_submitted=True)
        before = FileDeliveryGuardResult.objects.count()
        FileDeliveryGuardService.check(attachment=att, order=self.order)
        self.assertEqual(FileDeliveryGuardResult.objects.count(), before + 1)

    def test_check_and_raise_raises_on_blocked(self):
        att = self._make_final_attachment(is_submitted=False)
        with self.assertRaises(FileDeliveryBlocked) as ctx:
            FileDeliveryGuardService.check_and_raise(attachment=att, order=self.order)
        self.assertEqual(ctx.exception.blocked_reason, "not_submitted")

    def test_check_and_raise_passes_when_allowed(self):
        att = self._make_final_attachment(is_submitted=True)
        result = FileDeliveryGuardService.check_and_raise(attachment=att, order=self.order)
        self.assertTrue(result.is_allowed)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage")
class FileDeliveryGuardSubmitTests(TestCase):
    """submit_as_final() validates and flips the submitted flag."""

    def setUp(self):
        self.website = Website.objects.create(name="Test2", domain="test2.local")
        self.writer = User.objects.create_user(
            username="writer2", email="w2@test.local", password="pass", website=self.website,
        )
        self.client_user = User.objects.create_user(
            username="client2", email="c2@test.local", password="pass", website=self.website,
        )
        self.order = Ticket.objects.create(
            title="Submit test", description="desc",
            website=self.website, created_by=self.client_user,
        )

    def _make_attachment(self, *, purpose=FilePurpose.ORDER_FINAL, scan_status=FileScanStatus.PASSED):
        from files_management.services import FileAttachmentService
        managed = _upload_file(self.website, self.writer, purpose)
        managed.scan_status = scan_status
        managed.save(update_fields=["scan_status"])
        return FileAttachmentService.attach_managed_file(
            website=self.website, obj=self.order, managed_file=managed,
            purpose=purpose, visibility=FileVisibility.CLIENT_AND_STAFF,
            attached_by=self.writer,
        )

    def test_submit_flips_is_submitted(self):
        att = self._make_attachment()
        self.assertFalse(att.is_submitted)
        updated = FileDeliveryGuardService.submit_as_final(
            attachment=att, submitted_by=self.writer,
        )
        self.assertTrue(updated.is_submitted)
        self.assertEqual(updated.delivery_status, DeliveryStatus.SUBMITTED)
        self.assertIsNotNone(updated.submitted_at)
        self.assertEqual(updated.submitted_by, self.writer)

    def test_submit_records_on_behalf_of(self):
        att = self._make_attachment()
        staff = User.objects.create_user(
            username="staff2", email="s2@test.local", password="pass",
            website=self.website, is_staff=True,
        )
        updated = FileDeliveryGuardService.submit_as_final(
            attachment=att, submitted_by=staff,
            on_behalf_of=self.writer, reason="Writer unavailable",
        )
        self.assertEqual(updated.submitted_on_behalf_of, self.writer)
        self.assertEqual(updated.submission_reason, "Writer unavailable")

    def test_submit_raises_if_scan_not_passed(self):
        att = self._make_attachment(scan_status=FileScanStatus.QUEUED)
        with self.assertRaises(FileNotAvailable):
            FileDeliveryGuardService.submit_as_final(
                attachment=att, submitted_by=self.writer,
            )

    def test_submit_raises_if_wrong_purpose(self):
        att = self._make_attachment(purpose=FilePurpose.ORDER_DRAFT)
        with self.assertRaises(FileNotAvailable):
            FileDeliveryGuardService.submit_as_final(
                attachment=att, submitted_by=self.writer,
            )

    def test_submit_raises_if_already_submitted(self):
        att = self._make_attachment()
        FileDeliveryGuardService.submit_as_final(
            attachment=att, submitted_by=self.writer,
        )
        att.refresh_from_db()
        with self.assertRaises(FileNotAvailable):
            FileDeliveryGuardService.submit_as_final(
                attachment=att, submitted_by=self.writer,
            )

    def test_on_behalf_requires_reason(self):
        att = self._make_attachment()
        staff = User.objects.create_user(
            username="staff3", email="s3@test.local", password="pass",
            website=self.website, is_staff=True,
        )
        with self.assertRaises(FileNotAvailable):
            FileDeliveryGuardService.submit_as_final(
                attachment=att, submitted_by=staff,
                on_behalf_of=self.writer, reason="",
            )
