from __future__ import annotations

from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIRequestFactory, force_authenticate

from orders.api.views.reassignments.reassignment_views import (
    ReassignmentApproveAssignWriterView,
    ReassignmentApproveReturnToPoolView,
    ReassignmentCancelView,
    ReassignmentRejectView,
    ReassignmentRequestView,
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


class ReassignmentAPITests(SimpleTestCase):
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
        self.writer_user = FakeUser(
            pk=20,
            website=self.website,
            is_staff=False,
        )
        self.staff_user = FakeUser(
            pk=30,
            website=self.website,
            is_staff=True,
        )
        self.new_writer_user = FakeUser(
            pk=21,
            website=self.website,
            is_staff=False,
        )

        self.order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "website": self.website,
                "client": self.client_user,
                "status": "in_progress",
                "visibility_mode": "hidden",
            },
        )()

        self.reassignment_request = type(
            "ReassignmentRequestStub",
            (),
            {
                "pk": 200,
                "website": self.website,
                "order": self.order,
                "requested_by": self.writer_user,
                "status": "pending",
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

    @patch(
        "orders.api.views.reassignments.reassignment_views."
        "OrderReassignmentService.request_reassignment"
    )
    @patch.object(ReassignmentRequestView, "_get_order_for_tenant")
    def test_request_reassignment(
        self,
        mock_get_order: Any,
        mock_service: Any,
    ) -> None:
        created_request = type(
            "ReassignmentRequestStub",
            (),
            {
                "pk": 201,
                "status": "pending",
            },
        )()

        mock_get_order.return_value = self.order
        mock_service.return_value = created_request

        view = ReassignmentRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/reassignments/",
            user=self.writer_user,
            data={
                "requester_role": "writer",
                "reason": "Client is unresponsive",
                "internal_notes": "Need reassignment quickly",
            },
        )

        with patch.object(
            ReassignmentRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data["reassignment_request_id"], 201)
        self.assertEqual(data["status"], "pending")
        mock_service.assert_called_once_with(
            order=self.order,
            requested_by=self.writer_user,
            requester_role="writer",
            reason="Client is unresponsive",
            internal_notes="Need reassignment quickly",
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.reassignments.reassignment_views."
        "OrderReassignmentService.reject_reassignment"
    )
    @patch.object(
        ReassignmentRejectView,
        "_get_reassignment_for_tenant",
    )
    def test_reject_reassignment(
        self,
        mock_get_reassignment: Any,
        mock_service: Any,
    ) -> None:
        updated_request = type(
            "ReassignmentRequestStub",
            (),
            {
                "pk": 200,
                "status": "rejected",
            },
        )()

        mock_get_reassignment.return_value = self.reassignment_request
        mock_service.return_value = updated_request

        view = ReassignmentRejectView.as_view()
        request = self._auth_post(
            path="/api/orders/reassignments/200/reject/",
            user=self.staff_user,
            data={"internal_notes": "Not justified"},
        )

        with patch.object(
            ReassignmentRejectView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, reassignment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["reassignment_request_id"], 200)
        self.assertEqual(data["status"], "rejected")
        mock_service.assert_called_once_with(
            reassignment_request=self.reassignment_request,
            reviewed_by=self.staff_user,
            internal_notes="Not justified",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.reassignments.reassignment_views."
        "OrderReassignmentService.cancel_reassignment_request"
    )
    @patch.object(
        ReassignmentCancelView,
        "_get_reassignment_for_tenant",
    )
    def test_cancel_reassignment(
        self,
        mock_get_reassignment: Any,
        mock_service: Any,
    ) -> None:
        updated_request = type(
            "ReassignmentRequestStub",
            (),
            {
                "pk": 200,
                "status": "cancelled",
            },
        )()

        mock_get_reassignment.return_value = self.reassignment_request
        mock_service.return_value = updated_request

        view = ReassignmentCancelView.as_view()
        request = self._auth_post(
            path="/api/orders/reassignments/200/cancel/",
            user=self.writer_user,
        )

        with patch.object(
            ReassignmentCancelView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, reassignment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["reassignment_request_id"], 200)
        self.assertEqual(data["status"], "cancelled")
        mock_service.assert_called_once_with(
            reassignment_request=self.reassignment_request,
            cancelled_by=self.writer_user,
            triggered_by=self.writer_user,
        )

    @patch(
        "orders.api.views.reassignments.reassignment_views."
        "OrderReassignmentService.approve_return_to_pool"
    )
    @patch.object(
        ReassignmentApproveReturnToPoolView,
        "_get_reassignment_for_tenant",
    )
    def test_approve_return_to_pool(
        self,
        mock_get_reassignment: Any,
        mock_service: Any,
    ) -> None:
        updated_order = type(
            "OrderStub",
            (),
            {
                "pk": 100,
                "status": "ready_for_staffing",
                "visibility_mode": "pool",
            },
        )()

        mock_get_reassignment.return_value = self.reassignment_request
        mock_service.return_value = updated_order

        view = ReassignmentApproveReturnToPoolView.as_view()
        request = self._auth_post(
            path="/api/orders/reassignments/200/approve-return-to-pool/",
            user=self.staff_user,
            data={"internal_notes": "Approved for pool"},
        )

        with patch.object(
            ReassignmentApproveReturnToPoolView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, reassignment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["status"], "ready_for_staffing")
        self.assertEqual(data["visibility_mode"], "pool")
        mock_service.assert_called_once_with(
            reassignment_request=self.reassignment_request,
            reviewed_by=self.staff_user,
            internal_notes="Approved for pool",
            triggered_by=self.staff_user,
        )

    @patch(
        "orders.api.views.reassignments.reassignment_views."
        "OrderReassignmentService.approve_assign_specific_writer"
    )
    @patch.object(
        ReassignmentApproveAssignWriterView,
        "_get_reassignment_for_tenant",
    )
    @patch.object(
        ReassignmentApproveAssignWriterView,
        "_get_writer_for_tenant",
    )
    def test_approve_assign_specific_writer(
        self,
        mock_get_writer: Any,
        mock_get_reassignment: Any,
        mock_service: Any,
    ) -> None:
        assignment = type(
            "AssignmentStub",
            (),
            {
                "pk": 300,
                "status": "active",
                "source": "reassignment",
                "order": self.order,
                "writer": self.new_writer_user,
            },
        )()

        mock_get_reassignment.return_value = self.reassignment_request
        mock_get_writer.return_value = self.new_writer_user
        mock_service.return_value = assignment

        view = ReassignmentApproveAssignWriterView.as_view()
        request = self._auth_post(
            path="/api/orders/reassignments/200/approve-assign-writer/",
            user=self.staff_user,
            data={
                "writer_id": 21,
                "internal_notes": "Assigning stronger writer",
            },
        )

        with patch.object(
            ReassignmentApproveAssignWriterView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, reassignment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["assignment_id"], 300)
        self.assertEqual(data["order_id"], 100)
        self.assertEqual(data["writer_id"], 21)
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["source"], "reassignment")
        mock_service.assert_called_once_with(
            reassignment_request=self.reassignment_request,
            reviewed_by=self.staff_user,
            assign_to_writer=self.new_writer_user,
            internal_notes="Assigning stronger writer",
            triggered_by=self.staff_user,
        )

    def test_reassignment_request_requires_reason(self) -> None:
        view = ReassignmentRequestView.as_view()
        request = self._auth_post(
            path="/api/orders/orders/100/reassignments/",
            user=self.writer_user,
            data={
                "requester_role": "writer",
            },
        )

        with patch.object(
            ReassignmentRequestView,
            "_get_order_for_tenant",
            return_value=self.order,
        ), patch.object(
            ReassignmentRequestView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(DRFResponse, view(request, order_id=100))

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reason", data)

    def test_approve_assign_specific_writer_requires_writer_id(self) -> None:
        view = ReassignmentApproveAssignWriterView.as_view()
        request = self._auth_post(
            path="/api/orders/reassignments/200/approve-assign-writer/",
            user=self.staff_user,
            data={},
        )

        with patch.object(
            ReassignmentApproveAssignWriterView,
            "_get_reassignment_for_tenant",
            return_value=self.reassignment_request,
        ), patch.object(
            ReassignmentApproveAssignWriterView,
            "check_object_permissions",
            return_value=None,
        ):
            response = cast(
                DRFResponse,
                view(request, reassignment_id=200),
            )

        data = self._data(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("writer_id", data)