from __future__ import annotations

from typing import cast, Any

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import (
    ClassWriterCompensationPermission,
)
from class_management.api.serializers.class_writer_compensation_serializers import (
    ClassWriterCompensationSerializer,
    SetWriterCompensationSerializer,
)
from class_management.selectors.class_order_selectors import (
    ClassOrderSelector,
)
from class_management.selectors.class_writer_compensation_selectors import (
    ClassWriterCompensationSelector,
)
from class_management.services.class_writer_compensation_service import (
    ClassWriterCompensationService,
)


class ClassWriterCompensationViewSet(viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated,
        ClassWriterCompensationPermission,
    ]

    def get_website(self):
        """Returns middleware-injected website."""
        return getattr(cast(Any, self.request), "website")
    
    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        compensation = ClassWriterCompensationSelector.for_order(
            class_order=class_order,
        )

        if compensation is None:
            return Response([], status=status.HTTP_200_OK)

        return Response(
            ClassWriterCompensationSerializer([compensation], many=True).data
        )

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = SetWriterCompensationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        UserModel = get_user_model()
        writer = UserModel.objects.get(pk=data["writer_id"])

        compensation = ClassWriterCompensationService.set_compensation(
            class_order=class_order,
            writer=writer,
            compensation_type=data["compensation_type"],
            percentage=data.get("percentage"),
            fixed_amount=data.get("fixed_amount"),
            admin_notes=data.get("admin_notes", ""),
            set_by=request.user,
        )

        return Response(
            ClassWriterCompensationSerializer(compensation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def approve(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        compensation = ClassWriterCompensationService.get_compensation(
            class_order=class_order,
        )

        updated = ClassWriterCompensationService.approve_compensation(
            compensation=compensation,
            approved_by=request.user,
        )

        return Response(ClassWriterCompensationSerializer(updated).data)

    @action(detail=False, methods=["post"])
    def mark_earned(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        updated = ClassWriterCompensationService.mark_earned(
            class_order=class_order,
            triggered_by=request.user,
        )

        return Response(ClassWriterCompensationSerializer(updated).data)

    @action(detail=False, methods=["post"])
    def post_to_wallet(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        compensation = ClassWriterCompensationService.get_compensation(
            class_order=class_order,
        )

        updated = ClassWriterCompensationService.post_to_writer_wallet(
            compensation=compensation,
            posted_by=request.user,
            metadata={
                "source": "class_management_api",
                "posted_by_user_id": request.user.id,
            },
        )

        return Response(ClassWriterCompensationSerializer(updated).data)