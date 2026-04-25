from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.services.draft_service import DraftService


class DraftServiceTests(SimpleTestCase):
    def _order(self) -> Any:
        return cast(
            Any,
            SimpleNamespace(
                pk=100,
                website=SimpleNamespace(pk=10),
            ),
        )

    @patch("orders.services.draft_service.OrderDraft.objects.create")
    def test_submit_draft_creates_draft(self, mock_create: Any) -> None:
        order = self._order()
        draft = SimpleNamespace(pk=1, status="submitted")
        mock_create.return_value = draft

        result = DraftService.submit_draft(
            order=order,
            submitted_by=SimpleNamespace(pk=20),
            milestone=None,
            note="Draft submitted.",
        )

        self.assertEqual(result, draft)
        mock_create.assert_called_once()

    @patch("orders.services.draft_service.timezone")
    def test_review_draft_approves_and_completes_milestone(
        self,
        mock_timezone: Any,
    ) -> None:
        now = SimpleNamespace()
        mock_timezone.now.return_value = now

        milestone = SimpleNamespace(
            is_completed=False,
            save=lambda *args, **kwargs: None,
        )
        draft = SimpleNamespace(
            status="submitted",
            milestone=milestone,
            reviewed_at=None,
            save=lambda *args, **kwargs: None,
        )

        result = DraftService.review_draft(
            draft=draft,
            reviewed_by=SimpleNamespace(pk=30),
            approve=True,
        )

        self.assertEqual(result.status, "reviewed")
        self.assertEqual(result.reviewed_at, now)
        self.assertTrue(milestone.is_completed)

    @patch("orders.services.draft_service.timezone")
    def test_review_draft_requests_revision(
        self,
        mock_timezone: Any,
    ) -> None:
        now = SimpleNamespace()
        mock_timezone.now.return_value = now

        draft = SimpleNamespace(
            status="submitted",
            milestone=None,
            reviewed_at=None,
            save=lambda *args, **kwargs: None,
        )

        result = DraftService.review_draft(
            draft=draft,
            reviewed_by=SimpleNamespace(pk=30),
            approve=False,
        )

        self.assertEqual(result.status, "revision_requested")
        self.assertEqual(result.reviewed_at, now)