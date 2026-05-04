from __future__ import annotations

from typing import cast, Any

from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import ClassOrderPermission
from class_management.api.serializers import (
    ClassPriceCounterOfferSerializer,
    ClassPriceProposalSerializer,
    CreateCounterOfferSerializer,
    CreatePriceProposalSerializer,
    RejectProposalSerializer,
)
from class_management.models import ClassOrder, ClassPriceProposal
from class_management.selectors import (
    ClassOrderSelector,
    ClassPricingSelector,
)
from class_management.services.class_pricing_service import (
    ClassPricingService,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin

class ClassPriceProposalViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    """
    API endpoints for class price proposals and negotiation.

    Discount integration happens through:
        ClassPricingService.create_discounted_proposal(...)
    """

    permission_classes = [IsAuthenticated, ClassOrderPermission]

    def get_queryset(self) -> QuerySet[ClassOrder]: # type: ignore[override]
        """
        Return tenant scoped class orders.
        """
        request = self.request
        website = self.get_website()
        user = request.user

        if user.is_superuser or user.is_staff:
            return ClassOrderSelector.for_website(website=website)

        return ClassOrderSelector.for_client(
            website=website,
            client=user,
        )

    def get_class_order(self) -> ClassOrder:
        """
        Return the tenant scoped class order from URL kwargs.
        """
        class_order_id = self.kwargs["class_order_pk"]

        class_order = self.get_queryset().get(pk=class_order_id)
        self.check_object_permissions(self.request, class_order)

        return class_order

    def list(self, request, *args, **kwargs):
        """
        List price proposals for a class order.
        """
        class_order = self.get_class_order()

        proposals = ClassPricingSelector.proposals_for_order(
            class_order=class_order,
        )

        serializer = ClassPriceProposalSerializer(proposals, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a price proposal.

        Supports optional discount_code.
        """
        class_order = self.get_class_order()

        serializer = CreatePriceProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        proposal = ClassPricingService.create_discounted_proposal(
            class_order=class_order,
            amount=data["amount"],
            proposed_by=request.user,
            client=class_order.client,
            discount_code=data.get("discount_code", ""),
            message_to_client=data.get("message_to_client", ""),
            internal_notes=data.get("internal_notes", ""),
            expires_at=data.get("expires_at"),
            send_now=data.get("send_now", False),
            metadata={
                "requested_by_user_id": request.user.id,
                "source": "class_management_api",
            },
        )

        output = ClassPriceProposalSerializer(proposal)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None, *args, **kwargs):
        """
        Send a draft proposal to the client.
        """
        proposal = self.get_proposal()

        updated = ClassPricingService.send_proposal(
            proposal=proposal,
            sent_by=request.user,
        )

        return Response(ClassPriceProposalSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None, *args, **kwargs):
        """
        Accept a price proposal.
        """
        proposal = self.get_proposal()

        updated = ClassPricingService.accept_proposal(
            proposal=proposal,
            accepted_by=request.user,
        )

        return Response(ClassPriceProposalSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None, *args, **kwargs):
        """
        Reject a price proposal.
        """
        proposal = self.get_proposal()

        serializer = RejectProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassPricingService.reject_proposal(
            proposal=proposal,
            rejected_by=request.user,
            reason=data.get("reason", ""),
        )

        return Response(ClassPriceProposalSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def counter(self, request, pk=None, *args, **kwargs):
        """
        Create a counter offer for a proposal.
        """
        proposal = self.get_proposal()

        serializer = CreateCounterOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        counter_offer = ClassPricingService.create_counter_offer(
            proposal=proposal,
            offered_amount=data["offered_amount"],
            created_by=request.user,
            message=data.get("message", ""),
        )

        output = ClassPriceCounterOfferSerializer(counter_offer)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def get_proposal(self) -> ClassPriceProposal:
        """
        Return tenant scoped proposal.
        """
        class_order = self.get_class_order()

        proposal = ClassPriceProposal.objects.select_related(
            "class_order",
            "proposed_by",
            "accepted_by",
        ).get(
            pk=self.kwargs["pk"],
            class_order=class_order,
        )

        return proposal