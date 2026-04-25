from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY,
)
from orders.services.progressive_delivery_service import (
    ProgressiveDeliveryService,
)


class ProgressiveDeliveryAdjustmentIntegrationTests(SimpleTestCase):
    def _adjustment(self) -> Any:
        order = SimpleNamespace(
            pk=100,
            website=SimpleNamespace(pk=10),
            client=SimpleNamespace(pk=20),
            preferred_writer=None,
        )

        return cast(
            Any,
            SimpleNamespace(
                pk=5,
                order=order,
                extra_service_code=ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY,
                countered_quantity=None,
                request_pricing_payload={
                    "progressive_delivery": {
                        "milestones": [
                            {
                                "title": "50% draft",
                                "description": "Halfway checkpoint.",
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
                },
                counter_pricing_payload={},
            ),
        )

    @patch(
        "orders.services.progressive_delivery_service."
        "NotificationService.notify"
    )
    @patch(
        "orders.services.progressive_delivery_service."
        "OrderTimelineEvent.objects.create"
    )
    @patch(
        "orders.services.progressive_delivery_service."
        "OrderMilestone.objects.create"
    )
    @patch(
        "orders.services.progressive_delivery_service."
        "OrderProgressivePlan.objects.create"
    )
    def test_create_plan_from_adjustment_creates_plan_and_milestones(
        self,
        mock_plan_create: Any,
        mock_milestone_create: Any,
        mock_timeline_create: Any,
        mock_notify: Any,
    ) -> None:
        adjustment = self._adjustment()
        plan = SimpleNamespace(pk=30)
        mock_plan_create.return_value = plan

        result = ProgressiveDeliveryService.create_plan_from_adjustment(
            adjustment_request=adjustment,
            created_by=None,
        )

        self.assertEqual(result, plan)
        mock_plan_create.assert_called_once_with(
            website=adjustment.order.website,
            order=adjustment.order,
            is_required=True,
        )
        self.assertEqual(mock_milestone_create.call_count, 2)
        self.assertEqual(mock_timeline_create.call_count, 2)
        mock_notify.assert_called_once()

    def test_create_plan_from_adjustment_rejects_non_progressive_service(
        self,
    ) -> None:
        adjustment = self._adjustment()
        adjustment.extra_service_code = "speaker_notes"

        with self.assertRaises(ValueError):
            ProgressiveDeliveryService.create_plan_from_adjustment(
                adjustment_request=adjustment,
                created_by=None,
            )

    def test_create_plan_from_adjustment_requires_milestones(self) -> None:
        adjustment = self._adjustment()
        adjustment.request_pricing_payload = {}

        with self.assertRaises(ValueError):
            ProgressiveDeliveryService.create_plan_from_adjustment(
                adjustment_request=adjustment,
                created_by=None,
            )