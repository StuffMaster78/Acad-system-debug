from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import status, decorators, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import models
from decimal import Decimal

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.permissions import IsOrderOwnerOrSupport
from orders.services.order_deletion_service import (
    OrderDeletionService, ALLOWED_STAFF_ROLES
)
from orders.exceptions import InvalidTransitionError
from order_payments_management.models import OrderPayment


class LimitedPagination(PageNumberPagination):
    """Custom pagination class with safety limits to prevent performance issues."""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500  # Safety limit to prevent excessive data transfer
    
    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        from rest_framework.response import Response
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
        })


class OrderBaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Base viewset for orders. Supports list and retrieve operations.

    Attributes:
        queryset: QuerySet of Order objects.
        serializer_class: Serializer used for order objects.
        permission_classes: List of permission classes.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]
    pagination_class = LimitedPagination  # Paginated with safety limits

    def get_queryset(self):
        """
        Returns the filtered queryset for the current user.

        Returns:
            QuerySet: A queryset filtered based on user role.
        """
        user = self.request.user

        # Check if user is authenticated
        if not user or not user.is_authenticated:
            return Order.objects.none()

        # Optimize queryset with select_related and prefetch_related to prevent N+1 queries
        qs = Order.objects.all().select_related(
            'client',           # Used in serializer
            'website',          # Used in serializer
            'assigned_writer',  # Used in serializer (writer_username)
            'preferred_writer', # Used in serializer
            'paper_type',       # Used in serializer
            'academic_level',   # Used in serializer
            'formatting_style', # Used in serializer
            'type_of_work',     # Used in serializer
            'english_type',     # Used in serializer
            'subject',          # Used in serializer
            'previous_order',   # Used in serializer
            'discount',         # Used in serializer
        ).prefetch_related(
            'extra_services',   # ManyToMany field used in serializer
        )

        # Role-based scoping
        # Both superadmin and admin should see all orders (no website filtering)
        user_role = getattr(user, 'role', None)
        if user.is_superuser or user_role == 'superadmin':
            base_qs = qs
        elif user_role == 'client':
            base_qs = qs.filter(client=user)
        elif user_role == 'writer':
            # Writers see:
            # 1. Orders assigned to them (always visible, regardless of payment status)
            # 2. Paid orders that are available and not assigned to other writers
            # 3. Paid orders that are preferred for them (unless they declined)
            from orders.order_enums import OrderStatus
            from writer_management.models.profile import WriterProfile
            from orders.models import PreferredWriterResponse
            
            # Get writer's website from their profile - use select_related to avoid N+1
            writer_website = None
            try:
                # Use get() instead of hasattr to ensure we get the profile
                writer_profile = WriterProfile.objects.select_related('website').get(user=user)
                writer_website = writer_profile.website
            except WriterProfile.DoesNotExist:
                pass
            except Exception as e:
                # Log error but continue with fallback
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error getting writer profile for user {user.id}: {str(e)}")
            
            if writer_website:
                # Get orders where writer has declined (to exclude them)
                declined_order_ids = list(PreferredWriterResponse.objects.filter(
                    writer=user,
                    response='declined'
                ).values_list('order_id', flat=True))
                
                # Filter by website for available orders
                # Writers see:
                # 1. Orders assigned to them (always visible)
                # 2. Available paid orders that are:
                #    - Not assigned to anyone
                #    - In common pool (preferred_writer is None) OR preferred for this writer
                #    - Not declined by this writer
                base_qs = qs.filter(
                    models.Q(assigned_writer=user) |  # Orders assigned to them (always visible)
                    models.Q(
                        # Available paid orders not assigned to anyone
                        status=OrderStatus.AVAILABLE.value,
                        assigned_writer__isnull=True,
                        is_paid=True,  # Only paid orders
                        website=writer_website,
                    ) & (
                        # Either in common pool or preferred for this writer
                        models.Q(preferred_writer__isnull=True) | models.Q(preferred_writer=user)
                    )
                )
                
                # Only exclude declined orders if there are any
                if declined_order_ids:
                    base_qs = base_qs.exclude(id__in=declined_order_ids)
            else:
                # Fallback: only show assigned orders if no website
                base_qs = qs.filter(assigned_writer=user)
        elif user_role in ['admin', 'support', 'editor']:
            # Admins, support, and editors see all orders (no website filtering)
            base_qs = qs
        else:
            base_qs = qs.none()

        # Query param filters
        params = self.request.query_params
        unattributed = params.get('unattributed')
        if unattributed is not None:
            val = unattributed.lower() in ['1', 'true', 'yes']
            if val:
                base_qs = base_qs.filter(client__isnull=True).filter(
                    models.Q(external_contact_name__isnull=False) | models.Q(external_contact_email__isnull=False)
                )
            else:
                base_qs = base_qs.exclude(client__isnull=True)

        contact_search = params.get('contact')
        if contact_search:
            base_qs = base_qs.filter(
                models.Q(external_contact_name__icontains=contact_search) |
                models.Q(external_contact_email__icontains=contact_search) |
                models.Q(external_contact_phone__icontains=contact_search)
            )

        paid = params.get('is_paid')
        if paid is not None:
            base_qs = base_qs.filter(is_paid=(paid.lower() in ['1','true','yes']))

        # Filter by one or more statuses (comma-separated)
        statuses = params.get('status')
        if statuses:
            requested = [s.strip() for s in statuses.split(',') if s.strip()]
            if requested:
                base_qs = base_qs.filter(status__in=requested)

        # Order by most recent first
        base_qs = base_qs.order_by('-created_at', '-id')
        
        return base_qs
    
    def list(self, request, *args, **kwargs):
        """
        Override list to ensure queryset is not filtered by object permissions.
        DRF doesn't filter list results by object permissions by default,
        but we want to make sure our queryset filtering works correctly.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in OrderBaseViewSet.list: {str(e)}", exc_info=True)
            # Return empty result instead of 500 error
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': [],
                'total_pages': 0,
            })
    

    @decorators.action(detail=True, methods=["get"], url_path="payment-summary")
    def payment_summary(self, request, pk=None):
        """
        Provide payment and installment summary for the order owner or staff.
        """
        order = self.get_object()
        payments_qs = OrderPayment.objects.filter(order=order).order_by("-created_at")

        def _sum_amount(queryset):
            total = queryset.aggregate(total=models.Sum("amount")).get("total")
            return total or Decimal("0.00")

        completed_statuses = ["completed", "succeeded"]
        pending_statuses = ["pending", "processing", "under_review", "unpaid"]
        refunded_statuses = ["refunded", "partially_refunded", "fully_refunded"]

        amount_paid = _sum_amount(payments_qs.filter(status__in=completed_statuses))
        pending_amount = _sum_amount(payments_qs.filter(status__in=pending_statuses))
        refunded_amount = _sum_amount(payments_qs.filter(status__in=refunded_statuses))

        total_price = order.total_price or Decimal("0.00")
        balance_due = total_price - amount_paid
        if balance_due < Decimal("0.00"):
            balance_due = Decimal("0.00")

        def _format_decimal(value):
            return f"{(value or Decimal('0.00')).quantize(Decimal('0.01'))}"

        payments_payload = [
            {
                "id": payment.id,
                "amount": _format_decimal(payment.amount),
                "status": payment.status,
                "payment_method": payment.payment_method or "manual",
                "payment_type": payment.payment_type,
                "reference_id": payment.reference_id,
                "transaction_id": payment.transaction_id,
                "created_at": payment.created_at,
                "confirmed_at": payment.confirmed_at,
            }
            for payment in payments_qs
        ]

        summary = {
            "order_id": order.id,
            "currency": "USD",
            "order_total": _format_decimal(total_price),
            "amount_paid": _format_decimal(amount_paid),
            "pending_amount": _format_decimal(pending_amount),
            "refunded_amount": _format_decimal(refunded_amount),
            "balance_due": _format_decimal(balance_due),
            "is_fully_paid": balance_due == Decimal("0.00"),
            "last_payment_at": payments_qs.filter(status__in=completed_statuses).values_list("confirmed_at", flat=True).first(),
            "payments": payments_payload,
            "installments": [],
            "upcoming_installment": None,
        }

        return Response(summary, status=status.HTTP_200_OK)



    @decorators.action(detail=False, methods=["post"], url_path="create")
    def create_order(self, request):
        """
        Client creates a new order. Minimal required fields:
        - topic (str)
        - paper_type_id (int)
        - number_of_pages (int >=1)
        - client_deadline (datetime ISO)
        - order_instructions (str)
        Optional:
        - academic_level_id, formatting_style_id, subject_id, extra_services (list[int])
        """
        user = request.user
        if user.role != 'client' and not user.is_superuser:
            return Response({"detail": "Only clients can create orders."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data if isinstance(request.data, dict) else {}

        required = ["topic", "paper_type_id", "number_of_pages", "client_deadline", "order_instructions"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.create(
                website=getattr(user, 'website', None),
                client=user,
                topic=data["topic"],
                paper_type_id=int(data["paper_type_id"]),
                number_of_pages=int(data["number_of_pages"]),
                client_deadline=data["client_deadline"],
                order_instructions=data["order_instructions"],
                created_by_admin=False,
                is_paid=False,
            )

            # Optional fields
            if data.get("academic_level_id"):
                order.academic_level_id = int(data["academic_level_id"])
            if data.get("formatting_style_id"):
                order.formatting_style_id = int(data["formatting_style_id"])
            if data.get("subject_id"):
                order.subject_id = int(data["subject_id"])
            order.save()

            # Extra services many-to-many
            extra_services = data.get("extra_services") or []
            if isinstance(extra_services, list) and extra_services:
                order.extra_services.set(extra_services)

            return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["post"], url_path="quote")
    def quote(self, request):
        """
        Calculate price quote for a prospective order without saving it.
        Required fields mirror create_order. Returns detailed breakdown.
        """
        data = request.data if isinstance(request.data, dict) else {}
        try:
            from django.utils import timezone
            from datetime import datetime
            
            # Parse deadline
            deadline = data.get("client_deadline")
            if deadline:
                if isinstance(deadline, str):
                    deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            
            temp = Order(
                website=getattr(request.user, 'website', None),
                client=request.user if getattr(request.user, 'role', None) == 'client' else None,
                topic=data.get("topic", ""),
                paper_type_id=data.get("paper_type_id"),
                number_of_pages=int(data.get("number_of_pages", 1)),
                number_of_slides=int(data.get("number_of_slides", 0)),
                client_deadline=deadline,
                order_instructions=data.get("order_instructions", ""),
                created_at=timezone.now(),
            )
            # Optional fields
            if data.get("academic_level_id"):
                temp.academic_level_id = int(data["academic_level_id"])
            if data.get("formatting_style_id"):
                temp.formatting_style_id = int(data["formatting_style_id"])
            if data.get("subject_id"):
                temp.subject_id = int(data["subject_id"])
            if data.get("type_of_work_id"):
                temp.type_of_work_id = int(data["type_of_work_id"])
            if data.get("english_type_id"):
                temp.english_type_id = int(data["english_type_id"])
            if data.get("preferred_writer_id"):
                temp.preferred_writer_id = int(data["preferred_writer_id"])
            if data.get("writer_level_id"):
                from pricing_configs.models import WriterLevelOptionConfig
                try:
                    temp.writer_level = WriterLevelOptionConfig.objects.get(id=int(data["writer_level_id"]))
                except WriterLevelOptionConfig.DoesNotExist:
                    pass
            
            # Handle extra services - calculate price manually since we can't save M2M on unsaved order
            extra_services_price = Decimal("0.00")
            if data.get("extra_services"):
                from pricing_configs.models import AdditionalService
                service_ids = data["extra_services"]
                if isinstance(service_ids, list):
                    services = AdditionalService.objects.filter(id__in=service_ids, is_active=True)
                    extra_services_price = sum(Decimal(str(s.service_cost or 0)) for s in services)
            
            # Handle discount code
            if data.get("discount_code"):
                from discounts.models import Discount
                try:
                    discount = Discount.objects.get(
                        code=data["discount_code"],
                        website=temp.website,
                        is_active=True
                    )
                    temp.discount = discount
                except Discount.DoesNotExist:
                    pass

            # Use pricing calculator service
            from orders.services.pricing_calculator import PricingCalculatorService
            calculator = PricingCalculatorService(temp)
            breakdown = calculator.calculate_breakdown()
            total = calculator.calculate_total_price()
            
            # Get deadline multiplier for display
            deadline_multiplier = calculator.get_deadline_multiplier()
            
            # Calculate hours until deadline
            hours_until_deadline = None
            if deadline:
                hours_until_deadline = (deadline - timezone.now()).total_seconds() / 3600
            
            # Manually add extra services to total if they weren't included
            final_total = float(total)
            if extra_services_price > 0:
                final_total += float(extra_services_price)
            
            return Response({
                "total_price": final_total,
                "base_price": breakdown.get("base_price", 0),
                "slides_price": float(temp.number_of_slides * calculator.config.base_price_per_slide) if temp.number_of_slides > 0 else 0,
                "extra_services": float(extra_services_price),
                "writer_level": breakdown.get("writer_level", 0),
                "preferred_writer": breakdown.get("preferred_writer", 0),
                "discount_amount": breakdown.get("discount", 0),
                "deadline_multiplier": float(deadline_multiplier),
                "hours_until_deadline": hours_until_deadline,
                "breakdown": breakdown
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=["get"], url_path="preferred-writers")
    def get_preferred_writers(self, request):
        """
        Get list of writers the client has worked with before (for preferred writer selection).
        """
        from orders.services.preferred_writer_service import PreferredWriterService
        from users.serializers import UserSerializer
        
        if request.user.role != 'client':
            return Response(
                {"detail": "This endpoint is only available for clients."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        writer_ids = PreferredWriterService.get_last_five_writers_for_client(request.user)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        writers = User.objects.filter(id__in=writer_ids).select_related('writer_profile')
        
        # Get preferred writer costs
        from pricing_configs.models import PreferredWriterConfig
        website = getattr(request.user, 'website', None)
        writer_data = []
        for writer in writers:
            cost = Decimal("0.00")
            if website:
                try:
                    config = PreferredWriterConfig.objects.get(website=website)
                    if config.is_active:
                        cost = config.preferred_writer_cost
                except PreferredWriterConfig.DoesNotExist:
                    pass
            
            writer_data.append({
                'id': writer.id,
                'username': writer.username,
                'email': writer.email,
                'first_name': writer.first_name,
                'last_name': writer.last_name,
                'preferred_writer_cost': float(cost)
            })
        
        return Response(writer_data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="pay/wallet")
    def pay_with_wallet(self, request, pk=None):
        """
        Mark an order as paid using wallet (placeholder implementation).
        Requires client to own the order or staff privileges.
        """
        order = get_object_or_404(Order, pk=pk)
        user = request.user
        if not (user.is_superuser or user.role in ["admin", "support"] or order.client_id == user.id):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        if order.is_paid:
            return Response({"detail": "Order already paid."}, status=status.HTTP_200_OK)

        # TODO: integrate real wallet deduction here
        order.is_paid = True
        order.save(update_fields=["is_paid", "updated_at"])
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_200_OK)

    # ---------- soft delete (clients: only UNPAID; staff: any) ----------

    def destroy(self, request, pk=None):
        """
        Soft delete an order.
        - Clients: only their own UNPAID orders.
        - Staff (admin/support/superadmin): any order.
        Returns 204 if a transition happened, 200 if it was already deleted.
        """
        order = get_object_or_404(self.get_queryset().model,
                                  pk=pk, website_id=self.website.id)
        # use the raw manager to bypass deleted filter when needed
        # but we already got it via model; refetch guarded by tenant:
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)

        reason = request.data.get("reason", "") if isinstance(
            request.data, dict
        ) else ""

        result = self._svc().soft_delete(user=request.user,
                                         order=order,
                                         reason=reason)
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)

    # ---------- restore (client: own; staff: any) ----------

    @decorators.action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted order.
        - Clients: only their own.
        - Staff: any.
        Returns 200 on success.
        """
        # need to access even if currently deleted, so bypass filtered qs
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)
        self._svc().restore(user=request.user, order=order)
        return Response(status=status.HTTP_200_OK)

    # ---------- hard delete (irreversible; staff-only) ----------

    @decorators.action(detail=True, methods=["delete"], url_path="hard")
    def hard_delete(self, request, pk=None):
        """
        Irreversible delete (row removal).
        - Staff only: admin/support/superadmin (or superuser).
        Returns 204 if deleted, 200 if it was already gone.
        """
        if not self._is_staff_role(request.user):
            return Response({"detail": "Forbidden."},
                            status=status.HTTP_403_FORBIDDEN)

        result = self._svc().hard_delete_by_id(user=request.user,
                                               order_id=int(pk))
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)
    
    @decorators.action(detail=True, methods=["post"], url_path="transition")
    def transition_status(self, request, pk=None):
        """
        Transition order to a new status.
        
        Body:
        {
            "target_status": "in_progress",
            "reason": "Optional reason for transition",
            "skip_payment_check": false
        }
        """
        order = get_object_or_404(Order, pk=pk)
        target_status = request.data.get("target_status")
        reason = request.data.get("reason")
        skip_payment_check = request.data.get("skip_payment_check", False)
        
        if not target_status:
            return Response(
                {"detail": "target_status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has permission (admin/superadmin can skip checks)
        user_role = getattr(request.user, 'role', None)
        if user_role not in ['admin', 'superadmin']:
            skip_payment_check = False
        
        try:
            from orders.services.status_transition_service import StatusTransitionService
            service = StatusTransitionService(user=request.user)
            service.transition_order_to_status(
                order,
                target_status,
                reason=reason,
                skip_payment_check=skip_payment_check
            )
            
            return Response(
                {
                    "message": f"Order transitioned to {target_status}",
                    "order": OrderSerializer(order, context={"request": request}).data
                },
                status=status.HTTP_200_OK
            )
        except InvalidTransitionError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Transition failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @decorators.action(detail=True, methods=["get"], url_path="available-transitions")
    def get_available_transitions(self, request, pk=None):
        """
        Get list of available status transitions for an order.
        """
        order = get_object_or_404(Order, pk=pk)
        
        from orders.services.status_transition_service import StatusTransitionService
        service = StatusTransitionService(user=request.user)
        available = service.get_available_transitions(order)
        
        return Response(
            {
                "current_status": order.status,
                "available_transitions": available,
                "order_id": order.id
            },
            status=status.HTTP_200_OK
        )