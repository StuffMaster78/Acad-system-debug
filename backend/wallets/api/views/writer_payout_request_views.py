from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.request_context import get_request_website
from wallets.api.permissions.permissions import CanAdjustWallet, CanViewWallets
from wallets.api.serializers.writer_payout_request_serializer import (
    WriterPayoutRequestActionSerializer,
    WriterPayoutRequestCreateSerializer,
    WriterPayoutRequestSerializer,
)
from wallets.models import WalletHold
from wallets.services.writer_payout_request_service import WriterPayoutRequestService


class MyWriterPayoutRequestListCreateView(generics.ListCreateAPIView):
    """
    List or create payout requests for the authenticated writer.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WriterPayoutRequestCreateSerializer
        return WriterPayoutRequestSerializer

    def get_queryset(self):
        request = cast(Request, self.request)
        website = get_request_website(request)
        return WriterPayoutRequestService.get_writer_queryset(
            website=website,
            writer=request.user,
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        website = get_request_website(request)
        hold = WriterPayoutRequestService.request_payout(
            website=website,
            writer=request.user,
            amount=serializer.validated_data["amount"],
            reason=serializer.validated_data.get("reason", ""),
            created_by=request.user,
            currency=serializer.validated_data.get("currency", "USD"),
            metadata=serializer.validated_data.get("metadata", {}),
        )
        return Response(
            WriterPayoutRequestSerializer(hold).data,
            status=status.HTTP_201_CREATED,
        )


class AdminWriterPayoutRequestListView(generics.ListAPIView):
    """
    List writer payout requests for finance/admin users.
    """

    serializer_class = WriterPayoutRequestSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewWallets]

    def get_queryset(self):
        request = cast(Request, self.request)
        website = get_request_website(request)
        queryset = WriterPayoutRequestService.get_queryset(website=website)

        workflow_status = request.query_params.get("workflow_status")
        if workflow_status:
            queryset = queryset.filter(metadata__workflow_status=workflow_status)

        hold_status = request.query_params.get("status")
        if hold_status:
            queryset = queryset.filter(status=hold_status)

        writer_id = request.query_params.get("writer_id")
        if writer_id:
            queryset = queryset.filter(wallet__owner_user_id=writer_id)

        return queryset


class AdminWriterPayoutRequestActionMixin:
    permission_classes = [permissions.IsAuthenticated, CanAdjustWallet]

    def get_hold(self, request: Request, hold_id: int) -> WalletHold:
        website = get_request_website(request)
        return get_object_or_404(
            WalletHold,
            id=hold_id,
            website=website,
            reference_type=WriterPayoutRequestService.REFERENCE_TYPE,
        )

    def get_action_data(self, request: Request):
        serializer = WriterPayoutRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class AdminWriterPayoutRequestApproveView(
    AdminWriterPayoutRequestActionMixin,
    APIView,
):
    def post(self, request: Request, hold_id: int) -> Response:
        data = self.get_action_data(request)
        hold = WriterPayoutRequestService.approve_request(
            hold=self.get_hold(request, hold_id),
            reviewed_by=request.user,
            review_notes=data.get("review_notes", ""),
        )
        return Response(WriterPayoutRequestSerializer(hold).data)


class AdminWriterPayoutRequestRejectView(
    AdminWriterPayoutRequestActionMixin,
    APIView,
):
    def post(self, request: Request, hold_id: int) -> Response:
        data = self.get_action_data(request)
        hold = WriterPayoutRequestService.reject_request(
            hold=self.get_hold(request, hold_id),
            reviewed_by=request.user,
            review_notes=data.get("review_notes", ""),
        )
        return Response(WriterPayoutRequestSerializer(hold).data)


class AdminWriterPayoutRequestProcessView(
    AdminWriterPayoutRequestActionMixin,
    APIView,
):
    def post(self, request: Request, hold_id: int) -> Response:
        data = self.get_action_data(request)
        hold = WriterPayoutRequestService.process_request(
            hold=self.get_hold(request, hold_id),
            processed_by=request.user,
            external_reference=data.get("external_reference", ""),
            review_notes=data.get("review_notes", ""),
        )
        return Response(WriterPayoutRequestSerializer(hold).data)
