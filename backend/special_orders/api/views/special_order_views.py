from __future__ import annotations
from rest_framework.permissions import IsAuthenticated

from typing import Any, cast

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanCreateSpecialOrder,
    CanViewSpecialOrder,
)
from special_orders.api.serializers import (
    CreateFixedSpecialOrderSerializer,
    CreateQuotedSpecialOrderSerializer,
    SpecialOrderDetailSerializer,
    SpecialOrderListSerializer,
)
from special_orders.api.serializers.config_serializers import (
    EstimatedSpecialOrderSettingsSerializer,
    PredefinedSpecialOrderConfigSerializer,
    SpecialOrderMilestoneTemplateSerializer,
)
from special_orders.selectors import (
    SpecialOrderConfigSelector,
    SpecialOrderSelector,
)
from special_orders.models import PredefinedSpecialOrderConfig
from special_orders.services.new_services.special_order_creation_service import (
    SpecialOrderCreationService,
)
from websites.models.websites import Website


class ListPredefinedSpecialOrderConfigsView(APIView):
    """
    List active predefined special order configs for the current website.
    Used by clients to browse fixed-price express order options.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _website(self, request):
        requested_website_id = request.query_params.get("website_id")
        role = getattr(request.user, "role", None)
        if requested_website_id and (
            request.user.is_superuser or role == "superadmin"
        ):
            website = Website.objects.filter(pk=requested_website_id).first()
            if website is None:
                raise NotFound("Website not found.")
            return website
        return getattr(request, "website", None) or request.user.website

    def get(self, request):
        website = self._website(request)
        configs = SpecialOrderConfigSelector.list_predefined_configs(
            website=website,
            active_only=True,
        )
        serializer = PredefinedSpecialOrderConfigSerializer(configs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        website = self._website(request)
        serializer = PredefinedSpecialOrderConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = serializer.save(website=website, created_by=request.user)
        self._sync_durations(
            website=website,
            config=config,
            durations=request.data.get("durations", []),
        )
        config.refresh_from_db()
        return Response(
            PredefinedSpecialOrderConfigSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _sync_durations(*, website, config, durations):
        if not isinstance(durations, list):
            return
        from special_orders.models import PredefinedSpecialOrderDuration

        seen: set[int] = set()
        for row in durations:
            if not isinstance(row, dict):
                continue
            duration_id = row.get("id")
            payload = {
                "duration_days": int(row.get("duration_days") or 1),
                "price": row.get("price") or "0.00",
                "is_active": bool(row.get("is_active", True)),
            }
            if duration_id:
                duration = PredefinedSpecialOrderDuration.objects.filter(
                    id=duration_id,
                    predefined_order=config,
                    website=website,
                ).first()
                if duration:
                    for key, value in payload.items():
                        setattr(duration, key, value)
                    duration.save(update_fields=[*payload.keys(), "updated_at"])
                    seen.add(duration.pk)
            else:
                duration, _created = PredefinedSpecialOrderDuration.objects.update_or_create(
                    predefined_order=config,
                    website=website,
                    duration_days=payload["duration_days"],
                    defaults=payload,
                )
                seen.add(duration.pk)

        if seen:
            PredefinedSpecialOrderDuration.objects.filter(
                predefined_order=config,
                website=website,
            ).exclude(pk__in=seen).update(is_active=False)


class PredefinedSpecialOrderConfigDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _website(self, request):
        requested_website_id = request.query_params.get("website_id")
        role = getattr(request.user, "role", None)
        if requested_website_id and (
            request.user.is_superuser or role == "superadmin"
        ):
            website = Website.objects.filter(pk=requested_website_id).first()
            if website is None:
                raise NotFound("Website not found.")
            return website
        return getattr(request, "website", None) or request.user.website

    def _get_config(self, request, pk: int):
        website = self._website(request)
        queryset = PredefinedSpecialOrderConfig.objects.filter(pk=pk)
        if not (request.user.is_superuser or getattr(request.user, "role", None) == "superadmin"):
            queryset = queryset.filter(website=website)
        return queryset.first()

    def get(self, request, pk: int):
        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(PredefinedSpecialOrderConfigSerializer(config).data)

    def patch(self, request, pk: int):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        config = self._get_config(request, pk)
        if config is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PredefinedSpecialOrderConfigSerializer(
            config,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ListPredefinedSpecialOrderConfigsView._sync_durations(
            website=config.website,
            config=config,
            durations=request.data.get("durations", []),
        )
        config.refresh_from_db()
        return Response(PredefinedSpecialOrderConfigSerializer(config).data)


class SpecialOrderQuoteConfigView(APIView):
    """
    Return tenant-scoped quote settings for custom special order intake.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def _can_manage(user) -> bool:
        role = getattr(user, "role", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or role in {"superadmin", "admin"})
        )

    def _website(self, request):
        requested_website_id = request.query_params.get("website_id")
        role = getattr(request.user, "role", None)
        if requested_website_id and (
            request.user.is_superuser or role == "superadmin"
        ):
            website = Website.objects.filter(pk=requested_website_id).first()
            if website is None:
                raise NotFound("Website not found.")
            return website
        return getattr(request, "website", None) or request.user.website

    def get(self, request):
        website = self._website(request)
        settings = SpecialOrderConfigSelector.get_estimated_settings(
            website=website,
        )
        templates = SpecialOrderConfigSelector.list_milestone_templates(
            website=website,
            active_only=True,
        )
        return Response(
            {
                "settings": EstimatedSpecialOrderSettingsSerializer(
                    settings,
                ).data,
                "milestone_templates": SpecialOrderMilestoneTemplateSerializer(
                    templates,
                    many=True,
                ).data,
            }
        )

    def patch(self, request):
        if not self._can_manage(request.user):
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        website = self._website(request)
        settings = SpecialOrderConfigSelector.get_estimated_settings(
            website=website,
        )
        serializer = EstimatedSpecialOrderSettingsSerializer(
            settings,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get(request)


class SpecialOrderListView(APIView):
    """
    List special orders for the current portal user.
    """

    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def get(self, request):
        user = request.user
        website = getattr(request, "website", None) or user.website
        role = getattr(user, "role", "")

        if role == "writer":
            queryset = SpecialOrderSelector.list_for_writer(
                website=website,
                writer=user,
            )
        elif role == "client":
            queryset = SpecialOrderSelector.list_for_client(
                website=website,
                client=user,
            )
        elif user.is_superuser or role == "superadmin":
            # Superadmin sees all special orders across all websites
            from special_orders.models import SpecialOrder
            queryset = SpecialOrder.objects.select_related(
                "website", "client", "writer"
            ).order_by("-created_at")
        else:
            queryset = SpecialOrderSelector.list_for_staff(
                website=website,
            )

        serializer = SpecialOrderListSerializer(queryset, many=True)
        return Response(serializer.data)


class SpecialOrderDetailView(APIView):
    """
    Retrieve one tenant-scoped special order.
    """

    permission_classes = [CanViewSpecialOrder]

    def get(self, request, special_order_id: int):
        user = request.user
        if user.is_superuser or getattr(user, "role", None) == "superadmin":
            from special_orders.models import SpecialOrder
            try:
                special_order = SpecialOrder.objects.select_related(
                    "website", "client", "writer"
                ).get(pk=special_order_id)
            except SpecialOrder.DoesNotExist:
                from rest_framework.exceptions import NotFound
                raise NotFound("Special order not found.")
        else:
            special_order = SpecialOrderSelector.get_by_id(
                website=user.website,
                special_order_id=special_order_id,
            )

        self.check_object_permissions(request, special_order)

        serializer = SpecialOrderDetailSerializer(special_order)
        return Response(serializer.data)


class CreateQuotedSpecialOrderView(APIView):
    """
    Create an estimated or quoted special order inquiry.
    """

    permission_classes = [IsAuthenticated, CanCreateSpecialOrder]

    def post(self, request):
        serializer = CreateQuotedSpecialOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderCreationService.create_quoted_order(
            website=request.user.website,
            client=request.user,
            title=str(data["title"]),
            inquiry_details=str(data.get("inquiry_details", "")),
            budget=data.get("budget"),
            duration_days=data.get("duration_days"),
            currency=str(data.get("currency", "USD")),
            created_by=request.user,
        )

        response_serializer = SpecialOrderDetailSerializer(special_order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CreateFixedSpecialOrderView(APIView):
    """
    Create a fixed special order from predefined config and duration.
    """

    permission_classes = [IsAuthenticated, CanCreateSpecialOrder]

    def post(self, request):
        serializer = CreateFixedSpecialOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        try:
            predefined_config = SpecialOrderConfigSelector.get_predefined_config(
                website=request.user.website,
                config_id=int(data["predefined_config_id"]),
            )
            predefined_duration = SpecialOrderConfigSelector.get_duration(
                website=request.user.website,
                duration_id=int(data["predefined_duration_id"]),
            )
        except ObjectDoesNotExist as exc:
            raise NotFound("Special order config or duration not found.") from exc

        try:
            special_order = SpecialOrderCreationService.create_fixed_order(
                website=request.user.website,
                client=request.user,
                predefined_config=predefined_config,
                predefined_duration=predefined_duration,
                title=str(data.get("title", "")) or None,
                inquiry_details=str(data.get("inquiry_details", "")),
                currency=str(data.get("currency", "USD")),
                platform=str(data.get("platform", "")),
                writer_level=str(data.get("writer_level", "")),
                coupon_code=str(data.get("coupon_code", "")),
                created_by=request.user,
            )
        except ValueError as exc:
            raise ValidationError({"detail": str(exc)}) from exc

        response_serializer = SpecialOrderDetailSerializer(special_order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
