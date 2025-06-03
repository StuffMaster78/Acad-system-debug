from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from fines.models import Fine, FineAppeal
from fines.serializers import FineSerializer, FineAppealSerializer
from actions.dispatcher import dispatch_action


class FineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fines. Supports CRUD and custom actions like
    waive and void, with user-context and permissions handled.
    """
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Customize access filtering here (e.g., per user or role).
        return Fine.objects.all()

    def perform_create(self, serializer):
        # Automatically set the fine issuer as the current user.
        serializer.save(issued_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="waive")
    def waive(self, request, pk=None):
        """
        Custom action to waive a fine via dispatcher.
        """
        fine = get_object_or_404(Fine, pk=pk)
        waived = dispatch_action(
            name="waivefine",
            actor=request.user,
            fine=fine,
            waived_by=request.user,
            reason=request.data.get("reason"),
        )
        return Response(self.get_serializer(waived).data)

    @action(detail=True, methods=["post"], url_path="void")
    def void(self, request, pk=None):
        """
        Custom action to void a fine via dispatcher.
        """
        fine = get_object_or_404(Fine, pk=pk)
        voided = dispatch_action(
            name="voidfine",
            actor=request.user,
            fine=fine,
            voided_by=request.user,
            reason=request.data.get("reason"),
        )
        return Response(self.get_serializer(voided).data)


class FineAppealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling fine appeals. Supports creation and admin
    review workflows with smart permissioning and audit trails.
    """
    queryset = FineAppeal.objects.all()
    serializer_class = FineAppealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Customize filtering (e.g., show only user's appeals).
        return FineAppeal.objects.all()

    def perform_create(self, serializer):
        # Set the current user as the appellant.
        serializer.save(appealed_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        """
        Admin action to review a submitted appeal.
        """
        appeal = get_object_or_404(FineAppeal, pk=pk)
        reviewed = dispatch_action(
            name="reviewfineappeal",
            actor=request.user,
            appeal=appeal,
            reviewed_by=request.user,
            accept=request.data.get("accept"),
            review_notes=request.data.get("review_notes"),
        )
        return Response(self.get_serializer(reviewed).data)