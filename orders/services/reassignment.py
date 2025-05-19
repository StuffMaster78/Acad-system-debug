"""
Service layer for handling reassignment requests for orders.

This module contains functions to create, resolve, and manage reassignment 
requests. It also includes utility functions for calculating fines, checking 
deadlines, and retrieving the top previous writers for clients.
"""

from django.db import transaction
from django.utils import timezone
from orders.models import ReassignmentRequest, Order
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from decimal import Decimal

User = get_user_model()

class OrderReassignmentService:
    """
    Service class for handling order reassignment requests and operations.
    All methods are static and designed to be stateless.
    """
    @transaction.atomic
    def create_reassignment_request(order, requester, reason, requested_by,
                                    preferred_writer=None):
        """
        Creates a reassignment request from a client or writer.

        Args:
            order (Order): The order for which reassignment is requested.
            requester (User): The user making the request (client or writer).
            reason (str): The reason for the reassignment request.
            requested_by (str): Who made the request ('client' or 'writer').
            preferred_writer (User, optional): A preferred writer for reassignment.

        Returns:
            ReassignmentRequest: The created reassignment request.

        Raises:
            ValueError: If the `requested_by` is not 'client' or 'writer'.
            Exception: If there is already a pending reassignment request for the 
                    order.
        """
        if requested_by not in ["client", "writer"]:
            raise ValueError("requested_by must be either 'client' or 'writer'")

        if ReassignmentRequest.objects.filter(order=order, status="pending").exists():
            raise Exception("There is already a pending reassignment request for "
                            "this order.")

        request = ReassignmentRequest.objects.create(
            order=order,
            requester=requester,
            requested_by=requested_by,
            reason=reason,
            preferred_writer=preferred_writer
        )
        return request


    def resolve_reassignment_request(
        request_id=None,
        order_id=None,
        status='reassigned',
        processed_by=None,
        fine=0.00,
        metadata=None,
    ):
        """
        Resolves a reassignment request, either initiated by
        the client, writer, or admin.
        This function updates the reassignment request
        and the associated order.
        
        Args:
            request_id (int): The reassignment request ID (if provided).
            order_id (int): The order ID to be reassigned.
            status (str): The new status of the reassignment request.
            processed_by (User): The admin user who processes this reassignment.
            fine (float): The fine to apply to the writer (if applicable).
            metadata (dict): Optional metadata for additional processing.
        
        Returns:
            Order: The updated order after reassignment.
        """
        if not (order_id or request_id):
            raise ValueError("Either order_id or request_id must be provided.")

        # Get the order to be reassigned
        if order_id:
            order = Order.objects.get(id=order_id)
        else:
            # If request_id is provided, fetch the reassignment request first
            reassignment_request = ReassignmentRequest.objects.get(id=request_id)
            order = reassignment_request.order

        # Start a database transaction to ensure atomicity
        with transaction.atomic():
            # Mark the reassignment request status
            if request_id:
                reassignment_request = ReassignmentRequest.objects.get(id=request_id)
                reassignment_request.status = status
                reassignment_request.fine_applied = fine
                reassignment_request.processed_by = processed_by
                reassignment_request.metadata = metadata
                reassignment_request.resolved_at = timezone.now()
                reassignment_request.save()

            # Handle force reassignment by admin
            if status == 'reassigned':
                if processed_by and processed_by.is_staff:
                    # Admin initiated reassignment logic
                    if 'assigned_writer' in metadata and metadata['assigned_writer']:
                        # Assign to a specific writer
                        assigned_writer = metadata['assigned_writer']
                        order.assigned_writer = assigned_writer
                    else:
                        # Send to the public pool (no specific writer assigned)
                        order.assigned_writer = None

                    order.status = "in_progress" if assigned_writer else "available"
                    order.save()

        return order


    def get_available_writers(order, limit=5, exclude_writer=None):
        """
        Fetches a list of writers who can be assigned the order.
        This can either be writers from the public pool or
        based on the client's preferences.
        
        Args:
            order (Order): The order to reassign.
            limit (int): The maximum number of writers to return.
            exclude_writer (User, optional): A writer to exclude from the list
            (for example, the current assigned writer).
        
        Returns:
            QuerySet: A queryset of available writers.
        """
        # Fetch writers who are available (based on custom filters you might have)
        writers = User.objects.filter(
            is_staff=False,  # Ensure we get non-admin users
            is_active=True,  # Only active writers
            role='writer'  # Filter writers based on their role
        )
        
        if exclude_writer:
            # Exclude the current writer if any
            writers = writers.exclude(id=exclude_writer.id)
        
        # Optionally, we can sort by custom criteria. For example, client ratings.
        # You can extend this to add more filters based on your app’s requirements
        writers = writers.order_by('-last_login')  # Example: prioritize writers who are more active

        return writers[:limit]  # Limit the results to 'limit' writers

    def get_previous_writers_for_client(order, limit=5):
        """
        Fetches a list of the top-rated previous writers
        the client has worked with.
        
        Args:
            order (Order): The current order for which
                        the reassignment is being requested.
            limit (int): The maximum number of writers to return.
        
        Returns:
            QuerySet: A queryset of the top-rated previous writers for this client.
        """
        # Fetch the client's previous orders
        client_orders = Order.objects.filter(
            client=order.client,
            status='completed'
        )
        
        # Get the writers associated with those previous orders
        previous_writers = User.objects.filter(
            orders__in=client_orders,
            role='writer',
            is_active=True
        ).distinct()
        
        # Optionally, filter by ratings or other factors
        previous_writers = previous_writers.order_by('-rating')  # Assuming you have a rating field

        return previous_writers[:limit]  # Limit the results to the top 'limit' writers


    def get_top_previous_writers(client, limit=5):
        """
        Retrieves the top previous writers the client has worked with and rated 
        well.

        Args:
            client (User): The client for whom to find previous writers.
            limit (int, optional): The number of writers to retrieve. Defaults to 5.

        Returns:
            QuerySet: A QuerySet of the top `limit` writers based on client ratings.
        """
        writer_stats = (
            Order.objects.filter(client=client, writer__isnull=False, rating__gte=4)
            .values('writer')
            .annotate(total=Count('id'), avg_rating=Avg('rating'))
            .order_by('-avg_rating', '-total')[:limit]
        )

        writer_ids = [entry['writer'] for entry in writer_stats]
        return User.objects.filter(id__in=writer_ids)


    def is_near_deadline(order, threshold_percent=0.8):
        """
        Checks if an order's deadline is near based on a threshold percentage of 
        the total time.

        Args:
            order (Order): The order to check for the deadline.
            threshold_percent (float, optional): The percentage threshold to check 
                                                (e.g., 0.8 for 80%). Defaults to 0.8.

        Returns:
            bool: True if the deadline is near, otherwise False.
        """
        total_duration = (order.deadline - order.created_at).total_seconds()
        elapsed_duration = (timezone.now() - order.created_at).total_seconds()

        return elapsed_duration >= (threshold_percent * total_duration)


    def calculate_fine(order, fine_percentage=0.10):
        """
        Calculates a fine for a writer based on their payment, if any.

        Args:
            order (Order): The order to calculate the fine for.
            fine_percentage (float, optional): The percentage of the writer's 
                                                payment to be deducted as a fine. 
                                                Defaults to 0.10 (10%).

        Returns:
            Decimal: The calculated fine.
        """
        if hasattr(order, 'writer_payment'):
            return order.writer_payment * fine_percentage
        return 0.00


    def force_reassign_order(order_id, writer_id=None):
        """
        Force reassign an order, either to a specific writer or back to the public pool.
        This is typically used for admin-initiated reassignments.
        
        Args:
            order_id (int): The order ID to reassign.
            writer_id (int, optional): The ID of the writer to reassign the order to. 
                                    If None, sends the order back to the public pool.
        
        Returns:
            Order: The reassigned order.
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise ObjectDoesNotExist(f"Order with ID {order_id} does not exist.")
        
        metadata = {
            'admin_initiated': True,
            'assigned_writer': writer_id,
        }

        # Start a database transaction to ensure atomicity
        with transaction.atomic():
            # Call resolve_reassignment_request to process the reassignment
            return OrderReassignmentService.resolve_reassignment_request(
                order_id=order_id,
                status='reassigned',
                processed_by=None,  # No specific admin needed for force reassign
                fine=0.00,  # No fine in force reassignment
                metadata=metadata,
            )