"""
Service layer for handling reassignment requests for orders.

This module contains logic for creating, resolving, and managing reassignment 
requests. It also includes utilities for calculating fines, checking deadlines, 
and retrieving top-rated previous writers for clients.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Avg
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from orders.models import ReassignmentRequest, Order

User = get_user_model()


class OrderReassignmentService:
    """
    Service class for order reassignment operations.
    """

    @staticmethod
    @transaction.atomic
    def create_reassignment_request(
        order,
        requester,
        reason,
        requested_by,
        preferred_writer=None
    ):
        """
        Creates a reassignment request for an order.

        Args:
            order (Order): Order to be reassigned.
            requester (User): Client or writer making the request.
            reason (str): Reason for reassignment.
            requested_by (str): 'client' or 'writer'.
            preferred_writer (User, optional): Preferred writer for reassignment.

        Returns:
            ReassignmentRequest: The new request object.

        Raises:
            ValueError: Invalid request source.
            Exception: If a request already exists.
        """
        if requested_by not in ["client", "writer"]:
            raise ValueError("requested_by must be 'client' or 'writer'")

        if ReassignmentRequest.objects.filter(
            order=order, status="pending"
        ).exists():
            raise Exception("A pending reassignment request already exists.")

        return ReassignmentRequest.objects.create(
            order=order,
            requester=requester,
            requested_by=requested_by,
            reason=reason,
            preferred_writer=preferred_writer
        )

    @staticmethod
    @transaction.atomic
    def resolve_reassignment_request(
        request_id=None,
        order_id=None,
        status='reassigned',
        processed_by=None,
        fine=0.00,
        metadata=None
    ):
        """
        Resolves a reassignment request and updates the order.

        Args:
            request_id (int): Optional request ID.
            order_id (int): Optional order ID.
            status (str): New status for the request.
            processed_by (User): Admin resolving the request.
            fine (float): Fine amount for the writer.
            metadata (dict): Extra metadata, e.g., assigned writer.

        Returns:
            Order: The updated order instance.
        """
        if not (order_id or request_id):
            raise ValueError("Either order_id or request_id is required.")

        if request_id:
            request = ReassignmentRequest.objects.get(id=request_id)
            order = request.order
        else:
            order = Order.objects.get(id=order_id)
            request = None

        if request:
            request.status = status
            request.fine_applied = fine
            request.processed_by = processed_by
            request.metadata = metadata or {}
            request.resolved_at = timezone.now()
            request.save()

        if status == 'reassigned' and processed_by and processed_by.is_staff:
            from orders.services.transition_helper import OrderTransitionHelper
            from orders.services.status_transition_service import VALID_TRANSITIONS
            
            assigned_writer = metadata.get('assigned_writer') if metadata else None
            order.assigned_writer = assigned_writer
            
            # Determine target status based on current status and valid transitions
            current_status = order.status
            preferred_target = "in_progress" if assigned_writer else "available"
            
            # Check if preferred target is valid from current status
            allowed_transitions = VALID_TRANSITIONS.get(current_status, [])
            
            if preferred_target in allowed_transitions:
                target_status = preferred_target
            else:
                # Try alternative transitions
                if assigned_writer:
                    # Try to get to in_progress via intermediate states
                    if 'reassigned' in allowed_transitions:
                        target_status = "reassigned"
                    elif 'on_hold' in allowed_transitions:
                        target_status = "on_hold"
                    else:
                        raise ValueError(
                            f"Cannot reassign order from '{current_status}' to '{preferred_target}'. "
                            f"Allowed transitions: {', '.join(allowed_transitions)}. "
                            f"Please transition order to a valid state first."
                        )
                else:
                    # Try to get to available
                    if 'available' not in allowed_transitions:
                        if 'reassigned' in allowed_transitions:
                            target_status = "reassigned"
                        elif 'on_hold' in allowed_transitions:
                            target_status = "on_hold"
                        else:
                            raise ValueError(
                                f"Cannot reassign order from '{current_status}' to 'available'. "
                                f"Allowed transitions: {', '.join(allowed_transitions)}. "
                                f"Please transition order to a valid state first."
                            )
                    else:
                        target_status = "available"
            
            OrderTransitionHelper.transition_order(
                order=order,
                target_status=target_status,
                user=processed_by,
                reason=f"Order reassigned{' to new writer' if assigned_writer else ' - available for assignment'}",
                action="resolve_reassignment",
                is_automatic=False,
                metadata={
                    "reassignment_request_id": request.id if request else None,
                    "assigned_writer_id": assigned_writer.id if assigned_writer else None,
                    "fine_applied": float(fine),
                    **(metadata or {})
                }
            )
            order.save(update_fields=["assigned_writer"])

        return order

    @staticmethod
    def get_available_writers(order, limit=5, exclude_writer=None):
        """
        Returns available writers excluding the current one.

        Args:
            order (Order): The order in question.
            limit (int): Max writers to fetch.
            exclude_writer (User): Writer to exclude.

        Returns:
            QuerySet: Available writers.
        """
        writers = User.objects.filter(
            is_active=True,
            is_staff=False,
            role='writer'
        )

        if exclude_writer:
            writers = writers.exclude(id=exclude_writer.id)

        return writers.order_by('-last_login')[:limit]

    @staticmethod
    def get_previous_writers_for_client(order, limit=5):
        """
        Gets top-rated previous writers used by the client.

        Args:
            order (Order): Order belonging to the client.
            limit (int): Number of writers to fetch.

        Returns:
            QuerySet: Writers ranked by rating.
        """
        client_orders = Order.objects.filter(
            client=order.client, status='completed'
        )

        return User.objects.filter(
            orders__in=client_orders,
            role='writer',
            is_active=True
        ).distinct().order_by('-rating')[:limit]

    @staticmethod
    def get_top_previous_writers(client, limit=5):
        """
        Gets most reliable past writers based on rating.

        Args:
            client (User): The client user.
            limit (int): Number to return.

        Returns:
            QuerySet: Writers sorted by average rating and count.
        """
        stats = (
            Order.objects.filter(
                client=client,
                writer__isnull=False,
                rating__gte=4
            )
            .values('writer')
            .annotate(total=Count('id'), avg_rating=Avg('rating'))
            .order_by('-avg_rating', '-total')[:limit]
        )

        ids = [entry['writer'] for entry in stats]
        return User.objects.filter(id__in=ids)

    @staticmethod
    def is_near_deadline(order, threshold_percent=0.8):
        """
        Determines if deadline is approaching.

        Args:
            order (Order): Order to check.
            threshold_percent (float): 0.0–1.0 of deadline duration.

        Returns:
            bool: Whether deadline is near.
        """
        total = (order.deadline - order.created_at).total_seconds()
        elapsed = (timezone.now() - order.created_at).total_seconds()

        return elapsed >= (threshold_percent * total)

    @staticmethod
    def calculate_fine(order, fine_percentage=0.10):
        """
        Computes fine from writer's pay.

        Args:
            order (Order): The target order.
            fine_percentage (float): Fraction to fine.

        Returns:
            Decimal: Fine value.
        """
        if hasattr(order, 'writer_payment') and order.writer_payment:
            return order.writer_payment * Decimal(str(fine_percentage))
        return Decimal('0.00')

    @staticmethod
    def force_reassign_order(order_id, writer_id=None):
        """
        Admin-level forced reassignment.

        Args:
            order_id (int): Target order ID.
            writer_id (int): New writer ID (optional).

        Returns:
            Order: Updated order instance.

        Raises:
            ObjectDoesNotExist: If order not found.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ObjectDoesNotExist(f"Order ID {order_id} not found.")

        metadata = {
            'admin_initiated': True,
            'assigned_writer': writer_id
        }

        return OrderReassignmentService.resolve_reassignment_request(
            order_id=order_id,
            status='reassigned',
            processed_by=None,
            fine=Decimal('0.00'),
            metadata=metadata
        )