from django.apps import apps
from django.conf import settings

from django.db import models
from django.utils import timezone

from orders.order_enums import (
    OrderRequestStatus
)
from orders.models.orders import Order


User = settings.AUTH_USER_MODEL 

class OrderRequest(models.Model):
    """ 
    Represents a request made by a writer to work on an order. 
    This is used when a writer wants to take on an order that is not assigned to them.
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='requests'
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_orders'
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='order_requests'
    )
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=OrderRequestStatus.choices,
        default=OrderRequestStatus.PENDING,
    )
    rejection_feedback = models.TextField(blank=True, null=True)
  
    accepted_by_admin_at = models.DateTimeField(null=True, blank=True)
    writer_accepted_assignment_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()


    def __str__(self):
        return f"Writer {self.writer_id} requested Order {self.order_id}"
    
    def is_expired(self):
        """
        Checks if the order request has expired.
        """
        return (
            self.status == OrderRequestStatus.PENDING and
            timezone.now() > self.expires_at
        )

    def mark_expired(self):
        """
        Marks the order request as expired.
        It updates the status and adds feedback.
        """
        self.status = OrderRequestStatus.EXPIRED
        self.rejection_feedback = "Request expired due to no response."
        self.save(update_fields=["status", "rejection_feedback"])
    
    class Meta:
        unique_together = ('order', 'writer')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'expires_at']),
        ]

class WriterRequest(models.Model):
    """
    Model to track writer requests such as deadline extensions or page
    increases.
    """
    class RequestType(models.TextChoices):
        DEADLINE = 'deadline_extension', 'Deadline Extension'
        PAGES = 'page_increase', 'Page Increase'
        SLIDES = 'slide_increase', 'Slide Increase'

    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="writer_deadline_pages_request"
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name="writer_requests"
    )
    request_type = models.CharField(
        max_length=50,
        choices=RequestType.choices
    )
    requested_by_writer = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    new_deadline = models.DateTimeField(
        null=True, blank=True
    )
    additional_pages = models.PositiveIntegerField(null=True, blank=True)
    additional_slides = models.PositiveIntegerField(null=True, blank=True)
    request_reason = models.TextField()
    client_approval = models.BooleanField(default=False)
    admin_approval = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )
    
    # Counter offer fields
    client_counter_pages = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Client's counter offer for additional pages"
    )
    client_counter_slides = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Client's counter offer for additional slides"
    )
    client_counter_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Client's counter offer cost"
    )
    client_counter_reason = models.TextField(
        null=True, blank=True,
        help_text="Client's reason for counter offer"
    )
    has_counter_offer = models.BooleanField(
        default=False,
        help_text="Whether client has made a counter offer"
    )

    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Estimated cost of request"
    )

    final_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Final cost to be charged"
    )

    is_paid = models.BooleanField(default=False)
    requires_payment = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        """
        Return a string representation of the request.
        Returns:
            str: A summary of the request, including order ID and type.
        """
        return f"WriterRequest({self.id}) - {self.request_type} for Order #{self.order.id}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'request_type', 'status']),
        ]

class ReassignmentRequest(models.Model):
    """
    Handles reassignment requests by client or writer.
    Also handles force-reassign by admin.
    """
    REQUESTED_BY_CHOICES = (
        ('client', 'Client'),
        ('writer', 'Writer'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),    # e.g. admin approved but not reassigned yet
        ('rejected', 'Rejected'),
        ('reassigned', 'Reassigned'),  # actioned
    )

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='reassignment_requests'
    )

    requested_by = models.CharField(
        max_length=10,
        choices=REQUESTED_BY_CHOICES,
        help_text="Whether the client or writer requested this reassignment."
    )

    requester = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reassignment_requests_made',
        help_text="The actual user who made the request."
    )
    admin_initiated = models.BooleanField(
        default=False,
        help_text="Was this reassignment initiated by admin?"
    )
    reason = models.TextField(
        help_text="The reason for requesting reassignment."
    )

    preferred_writer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_reassignments',
        help_text="Optional preferred writer requested by the client."
    )

    fine_applied = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Fine applied to writer if they requested reassignment near deadline."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the reassignment request."
    )
    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reassignment_requests_processed',
        help_text="Admin or system user who processed this request."
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional field for system flags, debug info, auto-approved flags, etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag."
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ReassignmentRequest(Order #{self.order_id}, {self.requested_by}, {self.status})"

    def soft_delete_request(request_id):
        req = ReassignmentRequest.objects.get(id=request_id)
        req.is_deleted = True
        req.save()
    def is_fine_needed(self, threshold=0.8):
        from orders.services.reassignment import is_near_deadline
        return is_near_deadline(self.order, threshold)

    def apply_default_fine(self, percentage=0.10):
        from orders.services.reassignment import calculate_fine
        self.fine_applied = calculate_fine(self.order, percentage)
        self.save()

    def mark_resolved(self, status, fine=0.00, processed_by=None, metadata=None):
        self.status = status
        self.fine_applied = fine
        self.resolved_at = timezone.now()
        if processed_by:
            self.processed_by = processed_by
        if metadata:
            self.metadata = metadata
        self.save()

 class DraftRequest(models.Model):
    """
    Tracks requests for drafts to see order progress.
    Clients can request if they've paid for Progressive Delivery extra service.
    Admins can request drafts for any order.
    """
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='draft_requests'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='draft_requests'
    )
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='draft_requests_made',
        help_text="User who requested the draft (client or admin)"
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default='pending',
        help_text="Status of the draft request"
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Optional message from client about what they want to see"
    )
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Client's requested deadline for the draft"
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the draft was requested"
    )
    fulfilled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the writer uploaded the draft"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was cancelled"
    )

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['requested_by', 'status']),
        ]

    def can_request(self):
        """
        Check if a draft can be requested for this order.
        Returns (can_request: bool, reason: str or None)
        Admins can always request drafts.
        """
        # Admins can always request drafts
        if hasattr(self.requested_by, 'role') and self.requested_by.role in ['admin', 'superadmin', 'support']:
            return True, None
        
        # Check if order is in a valid status
        if self.order.status not in ['in_progress', 'under_editing', 'on_hold']:
            return False, f"Order status '{self.order.status}' does not allow draft requests"
        
        # Check if Progressive Delivery extra service is purchased
        # Check if the order has the Progressive Delivery extra service
        from django.db.models import Q
        has_progressive_delivery = self.order.extra_services.filter(
            Q(service_name__icontains='progressive') |
            Q(service_name__icontains='draft') |
            Q(slug__iexact='progressive-delivery')
        ).exists()
        
        if not has_progressive_delivery:
            return False, "Progressive Delivery extra service is required to request drafts"
        
        return True, None
    
    def fulfill(self, fulfilled_by):
        """Mark the draft request as fulfilled."""
        from django.utils import timezone
        self.status = 'fulfilled'
        self.fulfilled_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Draft Request #{self.id} - Order #{self.order.id} - {self.status}"
