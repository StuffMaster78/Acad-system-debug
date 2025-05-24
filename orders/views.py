from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Order, Dispute
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    DisputeSerializer
)
from notifications_system.models import send_notification
from superadmin_management.models import SuperadminLog
from .permissions import IsSuperadminOnly
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import WriterRequest, Order
from .serializers import WriterRequestSerializer
from order_payments_management.models import RequestPayment
from order_payments_management.serializers import RequestPaymentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.services.order_service import OrderService
from django.db import transaction
from users.models import User
from django_fsm import TransitionNotAllowed # type: ignore
from django.core.exceptions import ObjectDoesNotExist
from orders.permissions import (
    IsSupportOrAdmin,
    IsAssignedWriter,
    IsClientWhoOwnsOrder
)
from orders.services.disputes import (
    DisputeService,
    DisputeWriterResponseService
)
from orders.serializers import (
    AssignOrderSerializer,
    ReassignmentRequestSerializer,
    ResolveReassignmentSerializer,
    PreferredWriterResponseSerializer
)
from services import reassignment, assignment
from orders.actions.registry import OrderActionRegistry
from orders.actions.dispatcher import OrderActionDispatcher
from orders.actions.registry import all_actions
from orders.serializers import OrderActionSerializer

User = get_user_model()

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Orders.
    """
    queryset = Order.objects.all().select_related(
        'client', 'writer', 'preferred_writer',
        'discount_code', 'website'
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Return the queryset based on the user's role:
        - Admins and support see all orders.
        - Writers see all orders they can express interest in.
        - Assigned writers only see their orders.
        - Clients see only their orders.
        """
        user = self.request.user
        if user.is_staff:  # Admin or support
            return Order.objects.all()
        elif hasattr(user, 'is_writer') and user.is_writer:
            return Order.objects.filter(writer__isnull=True) | Order.objects.filter(writer=user)
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        """Automatically assign the authenticated user as the client when creating an order."""
        order = serializer.save(client=self.request.user)
        order.update_total_price()

    def perform_update(self, serializer):
        """Additional logic during order updates (if required)."""
        order = serializer.save()
        order.update_total_price()

    @action(detail=True, methods=["post"], url_path="action/(?P<action_name>[^/.]+)")
    def perform_order_action(self, request, pk=None, action_name=None):
        order = self.get_object()
        action_class = OrderActionRegistry.get(action_name)

        if not action_class:
            return Response({"error": f"Unknown action: {action_name}"}, status=400)

        try:
            handler = action_class(order=order, user=request.user, data=request.data)
            result = handler.handle()
            return Response(result, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=True, methods=['post'], url_path='dispute')
    def raise_dispute(self, request, pk=None):
        """
        Client raises a dispute on an order.
        """
        order = self.get_object()
        reason = request.data.get('reason')
        website = request.user.website

        try:
            dispute = DisputeService.raise_dispute(
                order=order,
                raised_by=request.user,
                reason=reason,
                website=website
            )
            return Response(DisputeSerializer(dispute).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def bring_back_in_progress(self, request, pk=None):
        """Superadmin brings back a completed, canceled, or disputed order to 'In Progress'."""
        order = self.get_object()
        if order.bring_back_in_progress(request.user):
            SuperadminLog.objects.create(
                superadmin=request.user,
                action_type="order_reopened",
                action_details=f"Brought back order #{order.id} to 'In Progress'."
            )
            send_notification(order.client, "Order Reopened", f"Your order #{order.id} is now in progress.")
            return Response({"message": "Order is now in progress."}, status=status.HTTP_200_OK)
        return Response({"error": "Order cannot be reopened."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])

    @action(detail=True, methods=["post"], url_path="assign")
    def assign_writer(self, request, pk=None):
        serializer = AssignOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        writer_id = serializer.validated_data["writer_id"]
        order = self.get_object()

        # You should have assignment.assign_writer(order, writer_id) in services
        updated_order = assignment.assign_writer(order, writer_id)

        return Response({"message": "Writer assigned successfully."}, status=status.HTTP_200_OK)
    
    # @action(detail=True, methods=["post"], url_path="request-reassignment")
    # def request_reassignment(self, request, pk=None):
    #     serializer = ReassignmentRequestSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     order = self.get_object()
    #     preferred_writer_id = serializer.validated_data.get("preferred_writer_id")
    #     preferred_writer = None

    #     if preferred_writer_id:
    #         preferred_writer = get_object_or_404(User, id=preferred_writer_id)

    #     request_obj = reassignment.create_reassignment_request(
    #         order=order,
    #         requester=request.user,
    #         reason=serializer.validated_data["reason"],
    #         requested_by=serializer.validated_data["requested_by"],
    #         preferred_writer=preferred_writer
    #     )

    #     return Response({"message": "Reassignment request submitted."}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='request-reassignment')
    def request_reassignment(self, request, pk=None):
        """
        Endpoint to request a reassignment of an order.

        Expects:
        - reason (str)
        - requested_by ('client' or 'writer')
        - preferred_writer_id (optional)
        """
        serializer = ReassignmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_object()
        requester = request.user
        data = serializer.validated_data

        preferred_writer = None
        if data.get("preferred_writer_id"):
            preferred_writer = User.objects.get(id=data["preferred_writer_id"])

        reassignment = create_reassignment_request(
            order=order,
            requester=requester,
            reason=data["reason"],
            requested_by=data["requested_by"],
            preferred_writer=preferred_writer,
        )

        return Response(
            {"message": "Reassignment request submitted.", "request_id": reassignment.id},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=["post"], url_path="resolve-reassignment")
    def resolve_reassignment(self, request, pk=None):
        serializer = ResolveReassignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assigned_writer_id = serializer.validated_data.get("assigned_writer_id")
        assigned_writer = None
        if assigned_writer_id:
            assigned_writer = get_object_or_404(User, id=assigned_writer_id)

        metadata = {
            "assigned_writer": assigned_writer,
        }

        order = reassignment.resolve_reassignment_request(
            order_id=pk,
            status=serializer.validated_data["status"],
            processed_by=request.user,
            fine=serializer.validated_data.get("fine", 0.00),
            metadata=metadata
        )

        return Response({"message": "Reassignment resolved."}, status=status.HTTP_200_OK)
    def reassign_writer(self, request, pk=None):
        """Superadmin reassigns an order to a different writer."""
        order = self.get_object()
        new_writer = User.objects.filter(pk=request.data.get("writer_id")).first()
        if not new_writer:
            return Response({"error": "Writer not found."}, status=status.HTTP_404_NOT_FOUND)

        order.reassign_writer(request.user, new_writer)
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="order_reassigned",
            action_details=f"Reassigned order #{order.id} to {new_writer.username}."
        )
        send_notification(order.client, "Order Reassigned", f"Your order #{order.id} has been reassigned to a new writer.")
        send_notification(new_writer, "New Assignment", f"You have been assigned order #{order.id}.")
        return Response({"message": "Order reassigned successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def edit_order(self, request, pk=None):
        """Superadmin edits order details."""
        order = self.get_object()
        order.edit_order_details(request.user, request.data)
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="order_edited",
            action_details=f"Edited details of order #{order.id}."
        )
        return Response({"message": "Order details updated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def update_deadline(self, request, pk=None):
        """Superadmin updates the order deadline."""
        order = self.get_object()
        order.update_deadline(request.user, request.data.get("deadline"))
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="deadline_updated",
            action_details=f"Updated deadline of order #{order.id}."
        )
        return Response({"message": "Deadline updated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def cancel_order(self, request, pk=None):
        """Superadmin cancels an order."""
        order = self.get_object()
        if order.cancel_order(request.user):
            SuperadminLog.objects.create(
                superadmin=request.user,
                action_type="order_canceled",
                action_details=f"Canceled order #{order.id}."
            )
            send_notification(order.client, "Order Canceled", f"Your order #{order.id} has been canceled.")
            return Response({"message": "Order canceled."}, status=status.HTTP_200_OK)
        return Response({"error": "Order cannot be canceled."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        """Allows Admins, Editors, and Support to mark an order as completed."""
        order = get_object_or_404(Order, pk=pk)
        if order.mark_as_completed(request.user):
            return Response({"message": "Order marked as completed!"})
        return Response({"error": "You do not have permission to complete this order."}, status=403)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def express_interest(self, request, pk=None):
        """
        Allows a writer to express interest in an order.
        """
        order = self.get_object()
        user = request.user

        if not hasattr(user, 'is_writer') or not user.is_writer:
            return Response({"error": "Only writers can express interest in orders."}, status=status.HTTP_403_FORBIDDEN)

        if order.writer:
            return Response({"error": "Order already has an assigned writer."}, status=status.HTTP_400_BAD_REQUEST)

        order.expressed_interest.add(user)
        send_notification(order.client, "Writer Interest", f"A writer has expressed interest in your order #{order.id}.")
        return Response({"message": "Interest expressed successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["post"], url_path="preferred-writer/respond")
    def respond_to_preferred(self, request, pk=None):
        """
        Allows a preferred writer to accept or decline an order.
        """
        serializer = PreferredWriterResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self.get_object()
        writer = request.user
        data = serializer.validated_data

        order = respond_to_preferred_order(
            writer=writer,
            order_id=order.id,
            response=data["response"],
            reason=data.get("reason")
        )

        return Response(
            {"message": f"You have {data['response']} this order."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def assign_writer(self, request, pk=None):
        """
        Allows an admin to assign a writer to an order.
        """
        order = self.get_object()
        writer_id = request.data.get("writer_id")
        writer = User.objects.filter(pk=writer_id, is_writer=True).first()

        if not writer:
            return Response(
                {"error": "Writer not found or not eligible."},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.writer:
            return Response(
                {"error": "Order already assigned to a writer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.writer = writer
        order.save()

        send_notification(
            writer,
            "New Order Assigned",
            f"You have been assigned to Order #{order.id}."
        )
        send_notification(
            order.client,
            "Writer Assigned",
            f"A writer has been assigned to your order #{order.id}."
        )
        return Response(
            {"message": "Writer assigned successfully."},
            status=status.HTTP_200_OK
        )
    

class DisputeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Disputes.
    """
    queryset = Dispute.objects.all().select_related('order', 'raised_by')
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter disputes based on user role:
        - Superadmins/Admins see all disputes.
        - Users only see disputes they raised.
        """
        user = self.request.user
        if user.is_staff:
            return Dispute.objects.all()
        return Dispute.objects.filter(raised_by=user)

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the dispute raiser.
        """
        serializer.save(raised_by=self.request.user)

    @action(
            detail=True, methods=["post"],
            permission_classes=[IsSuperadminOnly]
    )
    def resolve_dispute(self, request, pk=None):
        """
        Superadmins resolve a dispute by adding resolution notes and updating the status.
        """
        dispute = get_object_or_404(Dispute, pk=pk)
        resolution_outcome = request.data.get('resolution_outcome')
        resolution_notes = request.data.get("resolution_notes", "")
        extended_deadline = request.data.get('extended_deadline')

        service = DisputeService(dispute)

        try:
            dispute = service.resolve_dispute(
                resolution_outcome=resolution_outcome,
                resolved_by=request.user,
                resolution_notes=resolution_notes,
                extended_deadline=extended_deadline
            )
            return Response(DisputeSerializer(dispute).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], url_path='writer-response')
    def writer_response(self, request, pk=None):
        """
        Writer submits a response to a dispute.
        """
        dispute = self.get_object()
        response_text = request.data.get('response_text')
        response_file = request.data.get('response_file')

        service = DisputeWriterResponseService(dispute, request.user)

        try:
            response = service.submit_response(
                response_text, response_file
            )
            return Response(
                DisputeWriterResponseSerializer(response).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        """
        if not resolution_notes:
            return Response({"error": "Resolution notes are required."}, status=status.HTTP_400_BAD_REQUEST)

        dispute.status = "resolved"
        dispute.resolution_notes = resolution_notes
        dispute.save()

        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="dispute_resolved",
            action_details=f"Resolved dispute #{dispute.id} on order #{dispute.order.id}."
        )

        send_notification(
            dispute.raised_by, 
            "Dispute Resolved", 
            f"Your dispute on order #{dispute.order.id} has been resolved."
        )

        return Response({"message": "Dispute resolved successfully."}, status=status.HTTP_200_OK)
    """
        
    @action(
            detail=True, methods=["post"],
            url_path="actions/(?P<action_name>[^/.]+)"
    )
    def execute_action(self, request, pk=None, action_name=None):
        """
        Dynamically execute a registered order action via:
        /orders/{id}/actions/{action_name}/
        """
        order = self.get_object()
        action_cls = OrderActionRegistry.get(action_name)

        if not action_cls:
            return Response(
                {"detail": f"Action '{action_name}' is not supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if isinstance(action_cls, type):
                action_instance = action_cls(order, **request.data)
            else:
                # Just in case a functional handler is used
                return Response({"error": "Unsupported action handler type."}, status=500)

            result = action_instance.execute()

            return Response({"message": str(result)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WriterRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling writer requests such as deadline extensions or page
    increases.
    """
    queryset = WriterRequest.objects.all()
    serializer_class = WriterRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit_request(self, request, pk=None):
        """
        Submit a writer's request for changes to the order.

        Args:
            request (Request): The HTTP request object.
            pk (str): The primary key of the order.

        Returns:
            Response: A response confirming the submission.
        """
        order = Order.objects.get(id=pk)
        request_type = request.data.get("request_type")
        reason = request.data.get("request_reason")

        if request_type == "deadline_extension":
            new_deadline = request.data.get("new_deadline")
            writer_request = WriterRequest.objects.create(
                order=order,
                request_type=request_type,
                requested_by_writer=request.user,
                new_deadline=new_deadline,
                request_reason=reason
            )
        elif request_type in ["page_increase", "slide_increase"]:
            additional_pages = request.data.get("additional_pages")
            additional_slides = request.data.get("additional_slides")
            writer_request = WriterRequest.objects.create(
                order=order,
                request_type=request_type,
                requested_by_writer=request.user,
                additional_pages=additional_pages,
                additional_slides=additional_slides,
                request_reason=reason
            )
        return Response({"message": "Writer request submitted successfully."},
                        status=201)

    @action(detail=True, methods=['post'])
    def approve_request(self, request, pk=None):
        """
        Approve or decline a writer's request for changes to the order.

        Args:
            request (Request): The HTTP request object.
            pk (str): The primary key of the order.

        Returns:
            Response: A response indicating the approval status.
        """
        order = self.get_object()
        writer_request_id = request.data.get("writer_request_id")
        writer_request = WriterRequest.objects.get(id=writer_request_id,
                                                   order=order)

        client_response = request.data.get("response")

        if client_response == "approve":
            writer_request.status = "accepted"
            writer_request.save()

            # Handle payment for page/slide increase
            if writer_request.request_type in ["page_increase", "slide_increase"]:
                additional_cost = calculate_additional_cost(writer_request)
                payment = RequestPayment.objects.create(
                    order=order,
                    payment_method="wallet",  # Assuming wallet for now
                    additional_cost=additional_cost,
                    payment_for=writer_request.request_type
                )
                order.total_cost += additional_cost
                order.save()

            return Response({"message": "Request approved successfully."}, status=200)
        
        elif client_response == "decline":
            writer_request.status = "declined"
            writer_request.save()
            return Response({"message": "Request declined."}, status=200)

        return Response({"message": "Invalid response."}, status=400)


class OrderActionViewSet(viewsets.ViewSet):
    """
    A ViewSet for dispatching dynamic order actions.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="dispatch")
    def dispatch_action(self, request):
        serializer = OrderActionSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data["action"]
        order_id = serializer.validated_data["order_id"]

        # Remove known fields to forward the rest as dynamic kwargs
        params = {
            key: value for key, value in request.data.items()
            if key not in ("action", "order_id")
        }

        try:
            result = OrderActionDispatcher.dispatch(action, order_id, **params)
            return Response({
                "success": True,
                "action": action,
                "order_id": order_id,
                "result": result
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["get"], url_path="list")
    def list_actions(self, request):
        """
        Return all registered action names and their class names.
        """
        actions = all_actions()
        return Response([
            {
                "action": name,
                "class": cls.__name__,
                "doc": cls.__doc__ or "No description available"
            }
            for name, cls in actions.items()
        ])