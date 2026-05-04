from __future__ import annotations

from typing import cast, Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions.class_scope_permissions import (
    ClassScopePermission,
)
from class_management.api.serializers.class_portal_work_serializers import (
    ClassPortalWorkLogSerializer,
    CreateClassPortalWorkLogSerializer,
    ReviewClassPortalWorkLogSerializer,
)
from class_management.models.class_portal_work import (
    ClassPortalWorkLog,
 )
from class_management.models.class_scope import (
    ClassTask,
)
from class_management.selectors.class_order_selectors import (
    ClassOrderSelector,
)
from class_management.selectors.class_portal_work_selectors import (
    ClassPortalWorkLogSelector,
)

from class_management.services.class_portal_work_log_service import (
    ClassPortalWorkLogService,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin

class ClassPortalWorkLogViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    """
    API endpoints for writer portal work logs.
    """

    permission_classes = [IsAuthenticated, ClassScopePermission]


    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    def get_work_log(self) -> ClassPortalWorkLog:
        class_order = self.get_class_order()
        work_log = ClassPortalWorkLog.objects.get(
            pk=self.kwargs["pk"],
            class_order=class_order,
        )
        self.check_object_permissions(self.request, work_log)
        return work_log

    def list(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        if (
            class_order.client.id == request.user.id
            and not request.user.is_staff
        ):
            logs = ClassPortalWorkLogSelector.visible_to_client(
                class_order=class_order,
            )
        else:
            logs = ClassPortalWorkLogSelector.for_order(
                class_order=class_order,
            )

        return Response(ClassPortalWorkLogSerializer(logs, many=True).data)

    def create(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = CreateClassPortalWorkLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        task = None
        task_id = data.get("task_id")

        if task_id:
            task = ClassTask.objects.get(
                pk=task_id,
                class_order=class_order,
            )

        work_log = ClassPortalWorkLogService.log_activity(
            class_order=class_order,
            writer=request.user,
            task=task,
            activity_type=data["activity_type"],
            title=data["title"],
            description=data.get("description", ""),
            portal_reference=data.get("portal_reference", ""),
            occurred_at=data["occurred_at"],
            visible_to_client=data.get("visible_to_client", True),
            post_to_thread=data.get("post_to_thread", True),
            metadata={
                "source": "class_portal_work_api",
                "logged_by_user_id": request.user.id,
            },
        )

        return Response(
            ClassPortalWorkLogSerializer(work_log).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None, *args, **kwargs):
        work_log = self.get_work_log()

        serializer = ReviewClassPortalWorkLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassPortalWorkLogService.verify_log(
            work_log=work_log,
            verified_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(ClassPortalWorkLogSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None, *args, **kwargs):
        work_log = self.get_work_log()

        serializer = ReviewClassPortalWorkLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        updated = ClassPortalWorkLogService.reject_log(
            work_log=work_log,
            rejected_by=request.user,
            notes=data.get("notes", ""),
        )

        return Response(ClassPortalWorkLogSerializer(updated).data)