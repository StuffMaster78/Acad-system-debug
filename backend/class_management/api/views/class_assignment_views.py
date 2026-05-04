from __future__ import annotations

from typing import cast, Any

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import ClassAssignmentPermission
from class_management.api.serializers.class_assignment_serializers import (
    AssignWriterSerializer,
    ClassAssignmentSerializer,
    ReassignWriterSerializer,
    RemoveWriterSerializer,
)
from class_management.selectors.class_assignment_selectors import (
    ClassAssignmentSelector,
)
from class_management.selectors.class_order_selectors import (
    ClassOrderSelector,
)
from class_management.services.class_assignment_service import (
    ClassAssignmentService,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin

class ClassAssignmentViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ClassAssignmentPermission]


    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        assignments = ClassAssignmentSelector.assignments_for_order(
            class_order=class_order,
        )

        return Response(ClassAssignmentSerializer(assignments, many=True).data)

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = AssignWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        UserModel = get_user_model()
        writer = UserModel.objects.get(pk=data["writer_id"])

        assignment = ClassAssignmentService.assign_writer(
            class_order=class_order,
            writer=writer,
            assigned_by=request.user,
            assignment_notes=data.get("assignment_notes", ""),
            writer_visible_notes=data.get("writer_visible_notes", ""),
        )

        return Response(
            ClassAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def reassign(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = ReassignWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        UserModel = get_user_model()
        writer = UserModel.objects.get(pk=data["writer_id"])

        assignment = ClassAssignmentService.reassign_writer(
            class_order=class_order,
            new_writer=writer,
            reassigned_by=request.user,
            reason=data["reason"],
            assignment_notes=data.get("assignment_notes", ""),
        )

        return Response(ClassAssignmentSerializer(assignment).data)

    @action(detail=False, methods=["post"])
    def remove(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = RemoveWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        ClassAssignmentService.remove_writer(
            class_order=class_order,
            removed_by=request.user,
            reason=data["reason"],
        )

        return Response(status=status.HTTP_204_NO_CONTENT)