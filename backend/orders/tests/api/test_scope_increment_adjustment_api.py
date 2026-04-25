from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.adjustments.scope_increment_adjustment_views import (
    CreateScopeIncrementAdjustmentView,
)


class FakeUser:
    def __init__(self, *, pk: int, website: Any) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.is_authenticated = True


class ScopeIncrementAdjustmentAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.user = FakeUser(pk=1, website=self.website)

    def _request(self, data: dict[str, Any]) -> Request:
        request = self.factory.post(
            "/orders/100/adjustments/scope-increment/",
            data,
            format="json",
        )
        force_authenticate(request, user=cast(Any, self.user))
        return cast(Request, request)

    @patch(
        "orders.api.views.adjustments.scope_increment_adjustment_views."
        "AdjustmentNegotiationService.create_scope_increment_request"
    )
    @patch(
        "orders.api.views.adjustments.scope_increment_adjustment_views."
        "get_object_or_404"
    )
    def test_create_scope_increment_adjustment(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        order = SimpleNamespace(
            pk=100,
            website=self.website,
            base_quantity=4,
        )
        adjustment = SimpleNamespace(
            pk=5,
            status="pending_client_response",
            adjustment_kind="scope_increment",
            unit_type="page",
        )
        mock_get_object.return_value = order
        mock_service.return_value = adjustment

        view = CreateScopeIncrementAdjustmentView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._request(
                    {
                        "adjustment_type": "page_increase",
                        "unit_type": "page",
                        "requested_quantity": 6,
                        "title": "Need more pages",
                    }
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_service.assert_called_once()

    def test_create_scope_increment_rejects_extra_service_type(self) -> None:
        view = CreateScopeIncrementAdjustmentView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._request(
                    {
                        "adjustment_type": "extra_service",
                        "unit_type": "page",
                        "requested_quantity": 6,
                        "title": "Wrong path",
                    }
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)