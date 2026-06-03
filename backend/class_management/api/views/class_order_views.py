from __future__ import annotations

from typing import Any
from typing import cast

from django.db.models import QuerySet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
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
from class_management.models import ClassServiceConfig
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


    def get_queryset(self) -> QuerySet[ClassOrder]: # type: ignore[override]
        """
        Return tenant-scoped class orders based on user role.
        """
        website = self.get_website()
        user = self.request.user

        if user.is_superuser or getattr(user, 'role', None) == 'superadmin':
            return ClassOrder.objects.select_related(
                "website", "client", "assigned_writer"
            ).order_by("-created_at")

        if user.is_staff:
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

    def get_serializer_class(self): # type: ignore[override]
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
        website = self.get_website()
        if website is None:
            website = getattr(request.user, "website", None)

        class_config = None
        pricing_snapshot: dict[str, Any] = {}
        complexity_level = ""

        config_id = data.get("class_config_id")
        if config_id:
            class_config = ClassServiceConfig.objects.filter(
                id=int(config_id),
                website=website,
                is_active=True,
            ).first()
            if class_config is None:
                raise NotFound("Class service config not found.")
            pricing_snapshot = self._build_config_snapshot(
                class_config=class_config,
                duration_key=str(data.get("duration_key", "")),
                workload_key=str(data.get("workload_key", "")),
                selected_task_keys=list(data.get("selected_task_keys", [])),
                portal_access_enabled=bool(
                    data.get(
                        "portal_access_enabled",
                        class_config.requires_portal_access,
                    )
                ),
            )
            workload = pricing_snapshot.get("selected_workload") or {}
            complexity_level = str(workload.get("complexity", ""))

        class_order = ClassOrderService.create_draft(
            website=website,
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
        if class_config is not None:
            update_fields = [
                "class_config",
                "pricing_snapshot",
                "currency",
                "updated_at",
            ]
            class_order.class_config = class_config
            class_order.pricing_snapshot = pricing_snapshot
            class_order.currency = class_config.currency
            if complexity_level:
                class_order.complexity_level = complexity_level
                update_fields.append("complexity_level")
            class_order.save(update_fields=update_fields)

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

    @staticmethod
    def _find_option(options: list[Any], key: str) -> dict[str, Any] | None:
        for option in options:
            if isinstance(option, dict) and str(option.get("key", "")) == key:
                return option
        return None

    @staticmethod
    def _option_keys(options: list[Any]) -> set[str]:
        return {
            str(option.get("key", ""))
            for option in options
            if isinstance(option, dict) and option.get("key")
        }

    @classmethod
    def _build_config_snapshot(
        cls,
        *,
        class_config: ClassServiceConfig,
        duration_key: str,
        workload_key: str,
        selected_task_keys: list[str],
        portal_access_enabled: bool,
    ) -> dict[str, Any]:
        duration_options = list(class_config.duration_options or [])
        workload_options = list(class_config.workload_options or [])
        task_options = list(class_config.task_options or [])

        selected_task_key_set = {
            str(key)
            for key in selected_task_keys
            if str(key).strip()
        }
        required_task_keys = {
            str(option.get("key"))
            for option in task_options
            if isinstance(option, dict)
            and option.get("key")
            and bool(option.get("required", False))
        }
        selected_task_key_set.update(required_task_keys)

        if duration_options and not duration_key:
            raise ValidationError({"duration_key": "Select a valid class duration."})

        if workload_options and not workload_key:
            raise ValidationError({"workload_key": "Select a valid workload."})

        selected_duration = cls._find_option(
            duration_options,
            duration_key,
        )
        selected_workload = cls._find_option(
            workload_options,
            workload_key,
        )

        if duration_options and selected_duration is None:
            raise ValidationError({"duration_key": "Selected class duration is not available."})

        if workload_options and selected_workload is None:
            raise ValidationError({"workload_key": "Selected workload is not available."})

        valid_task_keys = cls._option_keys(task_options)
        invalid_task_keys = selected_task_key_set - valid_task_keys
        if invalid_task_keys:
            raise ValidationError(
                {
                    "selected_task_keys": (
                        "One or more selected tasks are not available for this class preset."
                    )
                }
            )

        selected_tasks = [
            option
            for option in task_options
            if isinstance(option, dict)
            and str(option.get("key", "")) in selected_task_key_set
        ]

        return {
            "source": "class_service_config",
            "config_id": class_config.pk,
            "config_name": class_config.name,
            "config_slug": class_config.slug,
            "service_type": class_config.service_type,
            "pricing_mode": class_config.pricing_mode,
            "base_price": str(class_config.base_price),
            "currency": class_config.currency,
            "payment_policy": {
                "allow_installments": class_config.allow_installments,
                "require_deposit_before_start": (
                    class_config.require_deposit_before_start
                ),
                "deposit_percentage": str(class_config.deposit_percentage),
                "quote_expiry_hours": class_config.quote_expiry_hours,
            },
            "selected_duration": selected_duration,
            "selected_workload": selected_workload,
            "selected_tasks": selected_tasks,
            "portal_access_enabled": portal_access_enabled,
        }
