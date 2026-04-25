from __future__ import annotations

from django.test import SimpleTestCase

from orders.api.serializers.drafts.draft_serializers import (
    ReviewDraftSerializer,
    SubmitDraftSerializer,
)


class DraftSerializerTests(SimpleTestCase):
    def test_submit_draft_serializer_allows_optional_milestone(self) -> None:
        serializer = SubmitDraftSerializer(
            data={
                "note": "Here is the 50% draft.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["note"], "Here is the 50% draft.")

    def test_submit_draft_serializer_accepts_milestone_id(self) -> None:
        serializer = SubmitDraftSerializer(
            data={
                "milestone_id": 10,
                "note": "Milestone draft.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["milestone_id"], 10)

    def test_review_draft_serializer_valid(self) -> None:
        serializer = ReviewDraftSerializer(data={"approve": True})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertTrue(serializer.validated_data["approve"])

    def test_review_draft_serializer_requires_approve(self) -> None:
        serializer = ReviewDraftSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("approve", serializer.errors)