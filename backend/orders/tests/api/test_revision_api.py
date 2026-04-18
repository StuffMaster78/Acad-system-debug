from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.revisions.revision_views import (
    RevisionRequestView,
)


class FakeUser:
    def __init__(
        self,
        *,
        pk: int,
        website: Any,
        is_staff: bool = False,
    ) -> None:
        self.pk = pk
        self.id = pk
        self.website = website
        self.website_id = getattr(website, "pk", None)
        self.is_staff = is_staff
        self.is_authenticated = True


class RevisionAPITests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

        class Website:
            pk = 1

        self.website = Website()

        self.client_user = FakeUser(
            pk=10,
            website=self.website,
            is_staff=False,
        )
        self.staff_user = FakeUser(
            pk=20,
            website=self.website,
            is_staff=True,
        )

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "client": self.client_user,
                "status": "submitted",
            },
        )()

    def _auth_post(
        self,
        *,
        path: str,
        user: FakeUser,
        data: dict[str, Any] | None = None,
    ) -> Request:
        request = self.factory.post(path, data or {}, format="json")
        force_authenticate(request, user=cast(Any, user))
        return cast(Request, request)

    @staticmethod
    def _data(response: DRFResponse) -> dict[str, Any]:
        assert response.data is not None
        return cast(dict[str, Any], response.data)

    # =========================
    # FREE REVISION ROUTE
    # =========================
    @patch(
        "orders.api.views.revisions.revision_views."
        "RevisionOrchestrationService.create_revision_request"
    )
    @patch.object(RevisionRequestView, "_get_order_for_tenant")
    def test_revision_routes_to_free_revision(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        revision = type(
            "RevisionStub",
            (),
            {
                "pk": 300,
                "status": "pending",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = revision

        view = RevisionRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/revisions/",
            user=self.client_user,
            data={
                "reason": "Minor corrections needed",
                "scope_summary": "Fix grammar issues",
                "is_within_original_scope": True,
            },
        )

        with patch.object(
            RevisionRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["routing"], "free_revision")
        self.assertEqual(data["revision_request_id"], 300)
        self.assertEqual(data["status"], "pending")

        mock_service.assert_called_once_with(
            order=self.order,
            requested_by=self.client_user,
            reason="Minor corrections needed",
            scope_summary="Fix grammar issues",
            is_within_original_scope=True,
            triggered_by=self.client_user,
        )

    # =========================
    # PAID ADJUSTMENT ROUTE
    # =========================
    @patch(
        "orders.api.views.revisions.revision_views."
        "RevisionOrchestrationService.create_revision_request"
    )
    @patch.object(RevisionRequestView, "_get_order_for_tenant")
    def test_revision_routes_to_paid_adjustment(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        adjustment = type(
            "AdjustmentStub",
            (),
            {
                "pk": 400,
                "status": "pending",
                "adjustment_type": "extra_work",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = adjustment

        view = RevisionRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/revisions/",
            user=self.client_user,
            data={
                "reason": "Add new section",
                "scope_summary": "Add 2 pages",
                "is_within_original_scope": False,
            },
        )

        with patch.object(
            RevisionRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["routing"], "paid_adjustment")
        self.assertEqual(data["adjustment_request_id"], 400)
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["adjustment_type"], "extra_work")

    # =========================
    # VALIDATION
    # =========================
    def test_revision_requires_reason(self) -> None:
        view = RevisionRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/revisions/",
            user=self.client_user,
            data={
                "scope_summary": "Missing reason",
                "is_within_original_scope": True,
            },
        )

        with patch.object(
            RevisionRequestView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            RevisionRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_revision_requires_scope_summary(self) -> None:
        view = RevisionRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/revisions/",
            user=self.client_user,
            data={
                "reason": "Missing scope",
                "is_within_original_scope": True,
            },
        )

        with patch.object(
            RevisionRequestView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            RevisionRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("scope_summary", data)

    def test_revision_requires_scope_flag(self) -> None:
        view = RevisionRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/revisions/",
            user=self.client_user,
            data={
                "reason": "Missing flag",
                "scope_summary": "Some work",
            },
        )

        with patch.object(
            RevisionRequestView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            RevisionRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("is_within_original_scope", data)