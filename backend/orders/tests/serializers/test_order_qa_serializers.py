from __future__ import annotations

from django.test import SimpleTestCase

from orders.api.serializers.qa.order_qa_serializers import (
    ApproveOrderForClientDeliverySerializer,
    ReturnOrderToWriterSerializer,
    SubmitOrderForQASerializer,
)


class OrderQASerializerTests(SimpleTestCase):
    def test_submit_order_for_qa_serializer_allows_blank_note(self) -> None:
        serializer = SubmitOrderForQASerializer(data={})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["note"], "")

    def test_approve_order_for_client_delivery_serializer_allows_blank_note(
        self,
    ) -> None:
        serializer = ApproveOrderForClientDeliverySerializer(data={})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["note"], "")

    def test_return_order_to_writer_serializer_requires_reason(self) -> None:
        serializer = ReturnOrderToWriterSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("reason", serializer.errors)

    def test_return_order_to_writer_serializer_valid(self) -> None:
        serializer = ReturnOrderToWriterSerializer(
            data={
                "reason": "Formatting is incomplete.",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["reason"],
            "Formatting is incomplete.",
        )