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


# ── Milestone template CRUD ───────────────────────────────────────────────────

def _website_from_request(request):
    website = getattr(request, "website", None)
    if website:
        return website
    try:
        return request.user.account_profiles.order_by("pk").first().website
    except Exception:
        return None


class MilestoneTemplateListView(APIView):
    """GET /special-orders/milestone-templates/   POST create"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from special_orders.models.configs import SpecialOrderMilestoneTemplate
        from special_orders.api.serializers.config_serializers import SpecialOrderMilestoneTemplateSerializer
        website = _website_from_request(request)
        qs = SpecialOrderMilestoneTemplate.objects.filter(website=website).prefetch_related("items")
        return Response(SpecialOrderMilestoneTemplateSerializer(qs, many=True).data)

    def post(self, request):
        from special_orders.models.configs import SpecialOrderMilestoneTemplate
        from special_orders.api.serializers.config_serializers import SpecialOrderMilestoneTemplateSerializer
        website = _website_from_request(request)
        t = SpecialOrderMilestoneTemplate.objects.create(
            website=website,
            name=request.data.get("name", ""),
            description=request.data.get("description", ""),
            is_active=request.data.get("is_active", True),
        )
        return Response(SpecialOrderMilestoneTemplateSerializer(t).data, status=status.HTTP_201_CREATED)


class MilestoneTemplateDetailView(APIView):
    """PATCH/DELETE /special-orders/milestone-templates/<pk>/"""
    permission_classes = [IsAuthenticated]

    def _get(self, pk):
        from special_orders.models.configs import SpecialOrderMilestoneTemplate
        try:
            return SpecialOrderMilestoneTemplate.objects.prefetch_related("items").get(pk=pk)
        except SpecialOrderMilestoneTemplate.DoesNotExist:
            return None

    def patch(self, request, pk):
        from special_orders.api.serializers.config_serializers import SpecialOrderMilestoneTemplateSerializer
        t = self._get(pk)
        if not t:
            return Response({"detail": "Not found."}, status=404)
        for field in ("name", "description", "is_active"):
            if field in request.data:
                setattr(t, field, request.data[field])
        t.save()
        return Response(SpecialOrderMilestoneTemplateSerializer(t).data)

    def delete(self, request, pk):
        t = self._get(pk)
        if not t:
            return Response({"detail": "Not found."}, status=404)
        t.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MilestoneTemplateItemView(APIView):
    """
    POST  /special-orders/milestone-templates/<pk>/items/  add item
    PATCH /special-orders/milestone-template-items/<item_pk>/
    DELETE /special-orders/milestone-template-items/<item_pk>/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from special_orders.models.configs import SpecialOrderMilestoneTemplate, SpecialOrderMilestoneTemplateItem
        from special_orders.api.serializers.config_serializers import SpecialOrderMilestoneTemplateSerializer
        try:
            t = SpecialOrderMilestoneTemplate.objects.prefetch_related("items").get(pk=pk)
        except SpecialOrderMilestoneTemplate.DoesNotExist:
            return Response({"detail": "Template not found."}, status=404)
        item = SpecialOrderMilestoneTemplateItem.objects.create(
            template=t,
            sequence=request.data.get("sequence", t.items.count() + 1),
            label=request.data.get("label", ""),
            percentage=request.data.get("percentage", "0.00"),
            required_before_staffing=request.data.get("required_before_staffing", False),
            required_before_delivery=request.data.get("required_before_delivery", False),
        )
        t.refresh_from_db()
        return Response(SpecialOrderMilestoneTemplateSerializer(t).data, status=status.HTTP_201_CREATED)


class MilestoneTemplateItemDetailView(APIView):
    """PATCH/DELETE /special-orders/milestone-template-items/<pk>/"""
    permission_classes = [IsAuthenticated]

    def _get(self, pk):
        from special_orders.models.configs import SpecialOrderMilestoneTemplateItem
        try:
            return SpecialOrderMilestoneTemplateItem.objects.select_related("template").get(pk=pk)
        except SpecialOrderMilestoneTemplateItem.DoesNotExist:
            return None

    def patch(self, request, pk):
        from special_orders.api.serializers.config_serializers import SpecialOrderMilestoneTemplateItemSerializer
        item = self._get(pk)
        if not item:
            return Response({"detail": "Not found."}, status=404)
        for field in ("sequence", "label", "percentage", "required_before_staffing", "required_before_delivery"):
            if field in request.data:
                setattr(item, field, request.data[field])
        item.save()
        return Response(SpecialOrderMilestoneTemplateItemSerializer(item).data)

    def delete(self, request, pk):
        item = self._get(pk)
        if not item:
            return Response({"detail": "Not found."}, status=404)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Pricing rules CRUD (all scoped to a PredefinedSpecialOrderConfig) ─────────

class _RuleBaseView(APIView):
    """Base for list+create on per-preset pricing rules."""
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def _config(self, config_pk):
        try:
            return PredefinedSpecialOrderConfig.objects.get(pk=config_pk)
        except PredefinedSpecialOrderConfig.DoesNotExist:
            return None

    def get(self, request, config_pk):
        config = self._config(config_pk)
        if not config:
            return Response({"detail": "Config not found."}, status=404)
        from special_orders.api.serializers import config_serializers as cs
        qs = self.model.objects.filter(predefined_order=config)
        return Response(self.serializer_class(qs, many=True).data)

    def post(self, request, config_pk):
        config = self._config(config_pk)
        if not config:
            return Response({"detail": "Config not found."}, status=404)
        s = self.serializer_class(data=request.data)
        s.is_valid(raise_exception=True)
        obj = s.save(website=config.website, predefined_order=config)
        return Response(self.serializer_class(obj).data, status=status.HTTP_201_CREATED)


class _RuleDetailBaseView(APIView):
    """Base for patch+delete on a single pricing rule."""
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def _get(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def patch(self, request, pk):
        obj = self._get(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        s = self.serializer_class(obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)

    def delete(self, request, pk):
        obj = self._get(pk)
        if not obj:
            return Response({"detail": "Not found."}, status=404)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _make_rule_views(model_name, serial_name):
    """Factory — builds list+create and detail views for a pricing rule model."""
    from special_orders.models import configs as cfg_module
    from special_orders.api.serializers import config_serializers as cs_module

    class ListView(_RuleBaseView):
        model = getattr(cfg_module, model_name)
        serializer_class = getattr(cs_module, serial_name)

    class DetailView(_RuleDetailBaseView):
        model = getattr(cfg_module, model_name)
        serializer_class = getattr(cs_module, serial_name)

    return ListView, DetailView


RushRuleListView, RushRuleDetailView = _make_rule_views(
    "SpecialOrderRushSurchargeRule", "RushSurchargeRuleSerializer"
)
WriterLevelRuleListView, WriterLevelRuleDetailView = _make_rule_views(
    "SpecialOrderWriterLevelSurchargeRule", "WriterLevelSurchargeRuleSerializer"
)
ClientTierRuleListView, ClientTierRuleDetailView = _make_rule_views(
    "SpecialOrderClientTierDiscountRule", "ClientTierDiscountRuleSerializer"
)
DifficultyRuleListView, DifficultyRuleDetailView = _make_rule_views(
    "SpecialOrderPlatformDifficultyRule", "DifficultyRuleSerializer"
)
