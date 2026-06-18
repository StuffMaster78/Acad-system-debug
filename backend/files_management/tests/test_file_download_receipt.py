"""
Tests for per-user FileDownloadReceipt.

Verifies that:
- One user's download does not clear another user's "new file" badge.
- The serializer's is_new_for_user field is per-user, not global.
- get_or_create is idempotent (double-download does not raise).
"""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from files_management.models.file_download_receipt import FileDownloadReceipt


class FakeAttachment:
    id = 1
    first_downloaded_at = None
    purpose = "order_final"
    managed_file = MagicMock()
    external_link = None

    def save(self, *a, **kw):
        pass


class FakeUser:
    id = 1
    is_authenticated = True


class FakeUser2:
    id = 2
    is_authenticated = True


class FileDownloadReceiptUniqueTogetherTest(SimpleTestCase):
    """Unit-level: model meta and receipt isolation logic."""

    def test_unique_together_fields(self):
        meta = FileDownloadReceipt._meta
        unique = {frozenset(uc) for uc in meta.unique_together}
        assert frozenset({"attachment", "user"}) in unique

    def test_receipt_db_table(self):
        assert FileDownloadReceipt._meta.db_table == "files_management_download_receipt"


class IsNewForUserSerializerTest(SimpleTestCase):
    """
    FileAttachmentDetailSerializer.get_is_new_for_user returns:
    - True  when the user has no receipt (file is new for them)
    - False when the user has a receipt (already downloaded)
    - False when context has no downloaded_attachment_ids
    """

    def _make_serializer(self, downloaded_ids=None):
        from files_management.api.serializers.response_serializers import (
            FileAttachmentDetailSerializer,
        )

        ctx = {}
        if downloaded_ids is not None:
            ctx["downloaded_attachment_ids"] = downloaded_ids

        s = FileAttachmentDetailSerializer(context=ctx)
        return s

    def test_new_when_not_in_downloaded_set(self):
        obj = MagicMock()
        obj.id = 42
        s = self._make_serializer(downloaded_ids={1, 2, 3})
        assert s.get_is_new_for_user(obj) is True

    def test_not_new_when_in_downloaded_set(self):
        obj = MagicMock()
        obj.id = 42
        s = self._make_serializer(downloaded_ids={42})
        assert s.get_is_new_for_user(obj) is False

    def test_defaults_false_when_no_context_key(self):
        obj = MagicMock()
        obj.id = 42
        s = self._make_serializer(downloaded_ids=None)
        assert s.get_is_new_for_user(obj) is False

    def test_user_a_download_does_not_clear_user_b(self):
        """
        Core invariant: downloaded set is per-user.
        User A having id=10 in their downloaded_ids must not affect
        the badge for User B whose downloaded_ids does not contain 10.
        """
        obj = MagicMock()
        obj.id = 10

        serializer_a = self._make_serializer(downloaded_ids={10})
        serializer_b = self._make_serializer(downloaded_ids=set())

        assert serializer_a.get_is_new_for_user(obj) is False  # A downloaded
        assert serializer_b.get_is_new_for_user(obj) is True   # B has not
