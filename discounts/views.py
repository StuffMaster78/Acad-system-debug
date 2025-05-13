from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import Q
from .models import Discount, SeasonalEvent, DiscountUsage, DiscountStackingRule
from .serializers import (
    DiscountSerializer, SeasonalEventSerializer,
    SeasonalEventWithDiscountsSerializer,
    DiscountUsageSerializer,
    DiscountStackingRuleSerializer
)
from .services.engine import DiscountEngine
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.filters import SearchFilter, OrderingFilter

class SeasonalEventViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing seasonal events.
    Supports full CRUD operations.
    """
    queryset = SeasonalEvent.objects.all()
    serializer_class = SeasonalEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on whether the request
        is a list or detail view.
        """
        if self.action == 'list':
            return SeasonalEventSerializer
        return SeasonalEventWithDiscountsSerializer

    def perform_create(self, serializer):
        """
        Custom logic to assign website or other fields during create
        """
        serializer.save()

    def get_queryset(self):
        """
        Filter seasonal events based on active status and date.
        """
        return SeasonalEvent.objects.filter(is_active=True)
    

class DiscountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discounts.
    Supports full CRUD operations with optimized filtering and validation.
    """
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'is_active', 'discount_type', 'seasonal_event', 'assigned_to_client',
        'start_date', 'end_date'
    ]
    search_fields = ['code', 'description']
    ordering_fields = ['start_date', 'end_date', 'value', 'created_at']

    def get_queryset(self):
        """
        Optimize queries:
        - Filter active discounts
        - Exclude expired ones
        - Preload related data for seasonal event and assigned client
        """
        return Discount.objects.filter(
            is_active=True, end_date__gte=now() | Q(end_date__isnull=True)
        ).select_related("seasonal_event", "assigned_to_client")

    def perform_create(self, serializer):
        """
        Ensure discount is valid before saving, including discount type and date
        validations.
        """
        discount = serializer.save()
        self._validate_discount(discount)

    def perform_update(self, serializer):
        """
        Ensure discount remains valid on update, including date validations.
        """
        discount = serializer.save()
        self._validate_discount(discount)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: deactivate the discount instead of deleting it.
        """
        discount = self.get_object()
        discount.is_active = False
        discount.save(update_fields=["is_active"])
        return Response(
            {"detail": "Discount deactivated."}, status=status.HTTP_204_NO_CONTENT
        )

    def _validate_discount(self, discount):
        """
        Validate discount properties like type and date consistency.
        """
        # Validate percentage range
        if discount.discount_type == "percentage" and not (1 <= discount.value <= 100):
            raise ValidationError("Percentage discount must be between 1 and 100.")

        # Ensure end_date is after start_date
        if discount.end_date and discount.start_date >= discount.end_date:
            raise ValidationError("End date must be after start date.")

        # Auto-disable expired discount
        if discount.end_date and discount.end_date < now():
            discount.is_active = False
            discount.save(update_fields=["is_active"])

    @action(detail=False, methods=["post"], url_path="duplicate")
    def duplicate_selected(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "No discount IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discounts = self.get_queryset().filter(id__in=ids)
        DiscountEngine.duplicate_discounts(discounts)
        return Response(
            {"detail": f"{discounts.count()} discounts duplicated."}
        )

    @action(detail=False, methods=["post"], url_path="deactivate")
    def deactivate_selected(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "No discount IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        count = Discount.objects.filter(id__in=ids).update(is_active=False)
        return Response({"detail": f"{count} discount(s) deactivated."})

    @action(detail=True, methods=["patch"])
    def toggle_active(self, request, pk=None):
        discount = self.get_object()
        discount.is_active = not discount.is_active
        discount.save(update_fields=["is_active"])
        return Response(
            {"detail": f"Discount is now {'active' if discount.is_active else 'inactive'}."}
        )

    @action(detail=True, methods=["post"])
    def apply_discount(self, request, pk=None):
        order = self.get_object()
        codes = request.data.get("codes", [])
        if isinstance(codes, str):
            codes = [codes]

        # If only one code is entered, provide hint if stackable code exists
        if len(codes) == 1:
            hint = self.get_stackable_hint(codes[0])
            if hint:
                return Response({
                    "message": f"You can stack this discount with: {hint['code']}.",
                    "stackable_discount": hint
                })

        try:
            result = apply_discounts_to_order(order, codes, request.user)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=500,
            )

        return Response(result)

    def get_stackable_hint(self, code):
        """
        Returns a hint with the stackable discount code if applicable.
        """
        discount = Discount.objects.filter(code=code, is_active=True).first()
        if not discount:
            return None
        stackable_discount = discount.stackable_with.first()
        if stackable_discount:
            return {"code": stackable_discount.code}
        return None


class DiscountUsageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discount usage.

    Ensures that discounts are not overused and tracks usage by users.
    Provides CRUD operations for discount usage entries.
    """
    queryset = DiscountUsage.objects.all()
    serializer_class = DiscountUsageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get the list of DiscountUsage entries for the authenticated user.

        Optimizes the queryset by preloading related fields to reduce database
        queries, ensuring the user, discount, and stackable discount are fetched
        efficiently.
        """
        return DiscountUsage.objects.select_related(
            "user", "base_discount", "stackable_with"
        )

    def perform_create(self, serializer):
        """
        Validate and save a new DiscountUsage entry.

        Ensures that discount usage does not exceed the maximum usage limit
        and that stacking rules are followed.
        """
        discount_usage = serializer.save()
        self._validate_discount_usage(discount_usage)

    def perform_update(self, serializer):
        """
        Validate and save an updated DiscountUsage entry.

        Ensures that discount usage remains within valid limits, such as
        usage count and stacking rules.
        """
        discount_usage = serializer.save()
        self._validate_discount_usage(discount_usage)

    def _validate_discount_usage(self, discount_usage):
        """
        Validate that the discount usage does not violate any business rules.

        Checks:
        - The discount's maximum usage limit
        - The user's usage count for the discount
        - The stackable discount's usage rules
        """
        discount = discount_usage.base_discount

        # Ensure the discount can still be used
        if discount.max_uses and discount.used_count >= discount.max_uses:
            raise ValidationError("This discount has already reached its "
                                    "maximum usage.")

        # Ensure the user has not exceeded the max usage for this discount
        user_usage_count = DiscountUsage.objects.filter(
            user=discount_usage.user,
            base_discount=discount_usage.base_discount
        ).count()

        if user_usage_count >= discount.max_uses:
            raise ValidationError(
                f"You have already used this discount {discount.max_uses} "
                "times."
            )

        # Ensure stacking limits are respected
        if discount_usage.stackable_with:
            stackable_discount = discount_usage.stackable_with
            if not stackable_discount.stackable:
                raise ValidationError(
                    f"{stackable_discount.code} is not stackable with other "
                    "discounts."
                )

            user_stack_count = DiscountUsage.objects.filter(
                user=discount_usage.user,
                base_discount=discount_usage.base_discount,
                stackable_with=stackable_discount
            ).count()

            if user_stack_count >= stackable_discount.max_stackable_uses_per_customer:
                raise ValidationError(
                    f"You cannot stack {stackable_discount.code} more than "
                    f"{stackable_discount.max_stackable_uses_per_customer} "
                    "times."
                )

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete the discount usage entry.

        Instead of permanently deleting the record, this method will deactivate
        the discount usage by calling `delete()`, ensuring that historical data
        is retained.
        """
        discount_usage = self.get_object()
        discount_usage.delete()
        return Response({"detail": "Discount usage entry deleted."},
                        status=status.HTTP_204_NO_CONTENT)
    

class DiscountStackingRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discount stacking rules.

    Provides CRUD operations for defining rules that govern how different
    discounts can be combined (stacked) together on orders.
    """
    queryset = DiscountStackingRule.objects.all()
    serializer_class = DiscountStackingRuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get the list of all stacking rules for the authenticated user.

        The queryset is optimized with `select_related` to reduce database 
        queries by preloading the related discount fields.
        """
        return DiscountStackingRule.objects.select_related(
            "base_discount", "stackable_discount"
        )

    def perform_create(self, serializer):
        """
        Validate and save a new stacking rule.

        Ensures that the stacking rule does not create conflicting relationships
        between discounts.
        """
        stacking_rule = serializer.save()
        self._validate_stacking_rule(stacking_rule)

    def perform_update(self, serializer):
        """
        Validate and save an updated stacking rule.

        Ensures that the updated stacking rule does not create conflicting
        relationships between discounts.
        """
        stacking_rule = serializer.save()
        self._validate_stacking_rule(stacking_rule)

    def _validate_stacking_rule(self, stacking_rule):
        """
        Validate that the stacking rule does not violate business logic.

        Checks:
        - Ensures the base discount is not the same as the stackable discount
        - Prevents stacking of discounts that are already marked as non-stackable
        """
        base_discount = stacking_rule.base_discount
        stackable_discount = stacking_rule.stackable_discount

        # Ensure the discounts are not the same
        if base_discount == stackable_discount:
            raise ValidationError("A discount cannot be stacked with itself.")

        # Ensure the stackable discount is actually stackable
        if not stackable_discount.stackable:
            raise ValidationError(f"{stackable_discount.code} cannot be stacked "
                                    "with other discounts.")

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete the stacking rule entry.

        Instead of permanently deleting the record, this method will deactivate
        the stacking rule by calling `delete()`, ensuring that historical data
        is retained.
        """
        stacking_rule = self.get_object()
        stacking_rule.delete()
        return Response({"detail": "Discount stacking rule deleted."},
                        status=status.HTTP_204_NO_CONTENT)