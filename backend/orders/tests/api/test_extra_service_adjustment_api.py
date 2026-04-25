from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.adjustments.extra_service_adjustment_views import (
    ClientAcceptExtraServiceView,
    CreateExtraServiceAdjustmentView,
)


class FakeUser:
    def __init__(self, *, pk: int, website: Any) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.is_authenticated = True


class ExtraServiceAdjustmentAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.website = SimpleNamespace(pk=10)
        self.user = FakeUser(pk=1, website=self.website)

    def _post(self, path: str, data: dict[str, Any]) -> Request:
        request = self.factory.post(path, data, format="json")
        force_authenticate(request, user=cast(Any, self.user))
        return cast(Request, request)

    @patch(
        "orders.api.views.adjustments.extra_service_adjustment_views."
        "AdjustmentNegotiationService.create_extra_service_request"
    )
    @patch(
        "orders.api.views.adjustments.extra_service_adjustment_views."
        "get_object_or_404"
    )
    def test_create_extra_service_adjustment(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        order = SimpleNamespace(pk=100, website=self.website)
        adjustment = SimpleNamespace(
            pk=9,
            status="pending_client_response",
            adjustment_kind="extra_service",
            extra_service_code="speaker_notes",
        )
        mock_get_object.return_value = order
        mock_service.return_value = adjustment

        view = CreateExtraServiceAdjustmentView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    "/orders/100/adjustments/extra-service/",
                    {
                        "extra_service_code": "speaker_notes",
                        "title": "Add speaker notes",
                    },
                ),
                order_id=100,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_service.assert_called_once()

    @patch(
        "orders.api.views.adjustments.extra_service_adjustment_views."
        "AdjustmentNegotiationService.client_accept_extra_service"
    )
    @patch(
        "orders.api.views.adjustments.extra_service_adjustment_views."
        "get_object_or_404"
    )
    def test_client_accept_extra_service(
        self,
        mock_get_object: Any,
        mock_service: Any,
    ) -> None:
        adjustment = SimpleNamespace(
            pk=9,
            order=SimpleNamespace(client=self.user),
            status="pending_client_response",
        )
        mock_get_object.return_value = adjustment
        mock_service.return_value = SimpleNamespace(pk=9, status="accepted")

        view = ClientAcceptExtraServiceView.as_view()
        response = cast(
            DRFResponse,
            view(
                self._post(
                    "/orders/adjustments/9/accept-extra-service/",
                    {},
                ),
                adjustment_id=9,
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_service.assert_called_once()