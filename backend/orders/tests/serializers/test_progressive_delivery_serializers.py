from __future__ import annotations

from django.test import SimpleTestCase

from orders.api.serializers.progressive_delivery.progressive_delivery_serializers import (
    CreateProgressivePlanSerializer,
)


class ProgressiveDeliverySerializerTests(SimpleTestCase):
    def test_create_progressive_plan_serializer_valid(self) -> None:
        serializer = CreateProgressivePlanSerializer(
            data={
                "milestones": [
                    {
                        "title": "50% draft",
                        "description": "Halfway draft.",
                        "due_at": "2026-05-01T12:00:00Z",
                        "percentage": 50,
                    },
                    {
                        "title": "Final draft",
                        "description": "Full draft.",
                        "due_at": "2026-05-02T12:00:00Z",
                        "percentage": 100,
                    },
                ]
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(len(serializer.validated_data["milestones"]), 2)

    def test_create_progressive_plan_serializer_rejects_empty_milestones(self) -> None:
        serializer = CreateProgressivePlanSerializer(
            data={"milestones": []}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("milestones", serializer.errors)