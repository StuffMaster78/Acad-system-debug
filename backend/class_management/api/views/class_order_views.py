from __future__ import annotations

from typing import Any
from typing import cast

from django.db.models import QuerySet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions.class_order_permissions import (
    ClassOrderPermission,
)
from class_management.api.serializers.class_order_public_serializers import (
    ClientClassOrderDetailSerializer,
    WriterClassOrderDetailSerializer,
)
from class_management.api.serializers.class_order_serializers import (
    ClassOrderActionSerializer,
    ClassOrderCancelSerializer,
    ClassOrderCreateSerializer,
    ClassOrderDetailSerializer,
    ClassOrderListSerializer,
)
from class_management.models.class_order import ClassOrder
from class_management.selectors import ClassOrderSelector
from class_management.services.class_order_service import (
    ClassOrderService,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin


class ClassOrderViewSet(ClassTenantViewMixin, viewsets.ModelViewSet):
    """
    API endpoints for class orders.
    """

    permission_classes = [IsAuthenticated, ClassOrderPermission]


    def get_queryset(self) -> QuerySet[ClassOrder]:  # type: ignore[override]
        """
        Return tenant-scoped class orders based on user role.
        """
        website = self.get_website()
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return ClassOrderSelector.for_website(website=website)

        writer_qs = ClassOrderSelector.for_writer(
            website=website,
            writer=user,
        )
        client_qs = ClassOrderSelector.for_client(
            website=website,
            client=user,
        )

        return writer_qs | client_qs

    def get_serializer_class(self):  # type: ignore[override]
        """
        Return serializer class for the current action and actor.
        """
        if self.action == "list":
            return ClassOrderListSerializer

        if self.action == "create":
            return ClassOrderCreateSerializer

        user = self.request.user
        obj = getattr(self, "_current_object", None)

        if obj is not None and not user.is_staff:
            user_pk = self._get_pk(user)

            if self._get_related_pk(obj=obj, field_name="client") == user_pk:
                return ClientClassOrderDetailSerializer

            assigned_writer_pk = self._get_related_pk(
                obj=obj,
                field_name="assigned_writer",
            )

            if assigned_writer_pk == user_pk:
                return WriterClassOrderDetailSerializer

        return ClassOrderDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a draft class order.
        """
        serializer = ClassOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        class_order = ClassOrderService.create_draft(
            website=self.get_website(),
            client=request.user,
            created_by=request.user,
            title=data["title"],
            institution_name=data.get("institution_name", ""),
            institution_state=data.get("institution_state", ""),
            class_name=data.get("class_name", ""),
            class_code=data.get("class_code", ""),
            class_subject=data.get("class_subject", ""),
            academic_level=data.get("academic_level", ""),
            starts_on=data.get("starts_on"),
            ends_on=data.get("ends_on"),
            initial_client_notes=data.get("initial_client_notes", ""),
        )

        output = ClassOrderDetailSerializer(class_order)

        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a class order.
        """
        instance = self.get_object()
        self._current_object = instance
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """
        Submit a draft class order.
        """
        class_order = self.get_object()

        updated = ClassOrderService.submit(
            class_order=class_order,
            submitted_by=request.user,
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def start_review(self, request, pk=None):
        """
        Start admin review.
        """
        class_order = self.get_object()

        serializer = ClassOrderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict[str, Any], serializer.validated_data)

        updated = ClassOrderService.start_review(
            class_order=class_order,
            reviewed_by=request.user,
            admin_internal_notes=data.get("notes", ""),
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def start_work(self, request, pk=None):
        """
        Start class work.
        """
        class_order = self.get_object()

        updated = ClassOrderService.start_work(
            class_order=class_order,
            started_by=request.user,
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """
        Complete a class order.
        """
        class_order = self.get_object()

        serializer = ClassOrderActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict[str, Any], serializer.validated_data)

        updated = ClassOrderService.complete(
            class_order=class_order,
            completed_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        Cancel a class order.
        """
        class_order = self.get_object()

        serializer = ClassOrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict[str, Any], serializer.validated_data)

        updated = ClassOrderService.cancel(
            class_order=class_order,
            cancelled_by=request.user,
            reason=data["reason"],
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """
        Archive a class order.
        """
        class_order = self.get_object()

        updated = ClassOrderService.archive(
            class_order=class_order,
            archived_by=request.user,
        )

        return Response(ClassOrderDetailSerializer(updated).data)

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return object primary key safely.
        """
        return getattr(obj, "pk", None)

    @staticmethod
    def _get_related_pk(*, obj: Any, field_name: str) -> Any:
        """
        Return related object primary key safely.
        """
        related_obj = getattr(obj, field_name, None)
        return getattr(related_obj, "pk", None)