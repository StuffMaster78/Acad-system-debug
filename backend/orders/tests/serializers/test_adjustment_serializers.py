from __future__ import annotations

from django.test import SimpleTestCase
from typing import cast
from orders.api.serializers.adjustments.client_accept_extra_service_serializer import (
    ClientAcceptExtraServiceSerializer,
)
from orders.api.serializers.adjustments.client_counter_scope_increment_serializer import (
    ClientCounterScopeIncrementSerializer,
)
from orders.api.serializers.adjustments.create_extra_service_adjustment_serializer import (
    CreateExtraServiceAdjustmentSerializer,
)
from orders.api.serializers.adjustments.create_scope_increment_adjustment_serializer import (
    CreateScopeIncrementAdjustmentSerializer,
)
from rest_framework.utils.serializer_helpers import ReturnDict


class AdjustmentSerializerTests(SimpleTestCase):
    def test_create_scope_increment_serializer_valid(self) -> None:
        serializer = CreateScopeIncrementAdjustmentSerializer(
            data={
                "adjustment_type": "page_increase",
                "unit_type": "page",
                "requested_quantity": 6,
                "title": "Need more pages",
                "description": "",
                "writer_justification": "Rubric needs more depth.",
                "client_visible_note": "More detail is required.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_scope_increment_serializer_rejects_invalid_type(self) -> None:
        serializer = CreateScopeIncrementAdjustmentSerializer(
            data={
                "adjustment_type": "extra_service",
                "unit_type": "page",
                "requested_quantity": 6,
                "title": "Wrong path",
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_create_extra_service_serializer_valid(self) -> None:
        serializer = CreateExtraServiceAdjustmentSerializer(
            data={
                "extra_service_code": "speaker_notes",
                "title": "Add speaker notes",
                "description": "Need notes for every slide.",
                "writer_justification": "",
                "client_visible_note": "Speaker notes are needed.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_client_counter_scope_serializer_valid(self) -> None:
        serializer = ClientCounterScopeIncrementSerializer(
            data={
                "countered_quantity": 5,
                "countered_note": "One extra page is enough.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_client_accept_extra_service_serializer_defaults_confirm_true(
        self,
    ) -> None:
        serializer = ClientAcceptExtraServiceSerializer(data={})
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid, serializer.errors)

        validated = cast(ReturnDict, serializer.validated_data)
        self.assertTrue(validated["confirm"])


    def test_create_extra_service_serializer_requires_milestones_for_progressive_delivery(
            self,
    ) -> None:
        serializer = CreateExtraServiceAdjustmentSerializer(
            data={
                "extra_service_code": "progressive_delivery",
                "title": "Add progressive delivery",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("milestones", serializer.errors)


    def test_create_extra_service_serializer_accepts_progressive_delivery_milestones(
            self,
    ) -> None:
        serializer = CreateExtraServiceAdjustmentSerializer(
            data={
                "extra_service_code": "progressive_delivery",
                "title": "Add progressive delivery",
                "milestones": [
                    {
                        "title": "50% draft",
                        "description": "Halfway checkpoint",
                        "due_at": "2026-05-01t12:00:00Z",
                        "percentage": 50,
                    }
                ],
            }
        )

        self.assertFalse(serializer.is_valid(), serializer.errors)