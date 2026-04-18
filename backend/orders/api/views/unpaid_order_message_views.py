from __future__ import annotations

from typing import cast

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from orders.api.serializers.unpaid_order_message_serializer import (
    UnpaidOrderMessageSerializer,
)
from orders.models.legacy_models.unpaid_order_message import UnpaidOrderMessage
from users.models import User


class UnpaidOrderMessageListCreateView(generics.ListCreateAPIView):
    """
    List and create unpaid order reminder messages for the current
    tenant website.
    """

    serializer_class = UnpaidOrderMessageSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UnpaidOrderMessage.objects.none()

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Restrict reminder messages to the current user's website.
        """
        user = cast(User, self.request.user)

        return UnpaidOrderMessage.objects.filter(
            website=user.website,
        ).order_by("sequence_number", "interval_hours", "id")

    def perform_create(self, serializer) -> None:
        """
        Persist the reminder message under the current tenant website.
        """
        user = cast(User, self.request.user)

        serializer.save(
            website=user.website,
            created_by=user,
            updated_by=user,
        )


class UnpaidOrderMessageRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    Retrieve, update, or delete a single unpaid order reminder message.
    """

    serializer_class = UnpaidOrderMessageSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UnpaidOrderMessage.objects.none()

    def get_queryset(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Restrict access to reminder messages within the user's website.
        """
        user = cast(User, self.request.user)

        return UnpaidOrderMessage.objects.filter(
            website=user.website,
        )

    def perform_update(self, serializer) -> None:
        """
        Track the user that last updated the reminder message.
        """
        user = cast(User, self.request.user)
        serializer.save(updated_by=user)