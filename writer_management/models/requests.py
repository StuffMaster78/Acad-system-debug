from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order
from django.core.exceptions import ValidationError
from writer_management.models.configs import WriterConfig

User = settings.AUTH_USER_MODEL




class WriterOrderRequest(models.Model):
    """
    Writers can request an order, expressing their interest.
    Admins must review and approve.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_requests_management"
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was made."
    )
    approved = models.BooleanField(
        default=False, help_text="Has the request been approved?"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="order_request_reviewer"
    )

    def __str__(self):
        return f"Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"

    def clean(self):
        """
        Enforce max request limit before saving.
        """
        config = WriterConfig.objects.first()
        if config:
            max_requests = config.max_requests_per_writer
            active_requests = WriterOrderRequest.objects.filter(writer=self.writer, approved=False).count()

            if active_requests >= max_requests:
                raise ValidationError(f"Writer {self.writer.user.username} has reached their max request limit.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class WriterOrderTake(models.Model):
    """
    Writers can take orders directly if admin allows.
    Writers can only take orders up to their max allowed limit.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="taken_orders"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_takes"
    )
    taken_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the order was taken."
    )

    def __str__(self):
        return f"Taken: {self.writer.user.username} - Order {self.order.id}"

    def clean(self):
        """
        Enforce writer take limit based on level & admin setting.
        """
        config = WriterConfig.objects.first()
        if not config or not config.takes_enabled:
            raise ValidationError("Order takes are currently disabled. Writers must request orders.")

        max_allowed_orders = self.writer.writer_level.max_orders if self.writer.writer_level else 0
        current_taken_orders = WriterOrderTake.objects.filter(writer=self.writer).count()

        if current_taken_orders >= max_allowed_orders:
            raise ValidationError(f"Writer {self.writer.user.username} has reached their max take limit.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)




class WriterOrderRequestReview(models.Model):
    """
    Admin reviews for writer order requests.
    """
    request = models.ForeignKey(
        WriterOrderRequest, on_delete=models.CASCADE,
        related_name="reviews"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="order_request_reviews"
    )
    review_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the review was made."
    )
    comments = models.TextField(
        blank=True, null=True,
        help_text="Admin comments on the request."
    )

    def __str__(self):
        return f"Review: {self.request.writer.user.username} for Order {self.request.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Request Review"
        verbose_name_plural = "Writer Order Request Reviews"
        ordering = ['-review_date'] 

class WriterOrderTakeReview(models.Model):
    """
    Admin reviews for writer order takes.
    """
    take = models.ForeignKey(
        WriterOrderTake, on_delete=models.CASCADE,
        related_name="reviews"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="order_take_reviews"
    )
    review_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the review was made."
    )
    comments = models.TextField(
        blank=True, null=True,
        help_text="Admin comments on the take."
    )

    def __str__(self):
        return f"Review: {self.take.writer.user.username} - Order {self.take.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Take Review"
        verbose_name_plural = "Writer Order Take Reviews"
        ordering = ['-review_date']


class WriterOrderRequestAdminReview(models.Model):
    """
    Admin reviews for writer order requests.
    """
    request = models.ForeignKey(
        WriterOrderRequest, on_delete=models.CASCADE,
        related_name="admin_reviews"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="order_request_admin_reviews"
    )
    review_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the review was made."
    )
    comments = models.TextField(
        blank=True, null=True,
        help_text="Admin comments on the request."
    )

    def __str__(self):
        return f"Admin Review: {self.request.writer.user.username} for Order {self.request.order.id}"
    
    class Meta:
        verbose_name = "Writer Order Request Admin Review"
        verbose_name_plural = "Writer Order Request Admin Reviews"
        ordering = ['-review_date']



class WriterDeadlineExtensionRequest(models.Model):
    """
    Writers can request a deadline extension for an order.
    Admin/Client approval required.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="writer_deadline_extension_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="order_deadline_extension_requests"
    )
    old_deadline = models.DateTimeField(
        help_text="Current order deadline."
    )
    requested_deadline = models.DateTimeField(
        help_text="New requested deadline."
    )
    reason = models.TextField(
        help_text="Reason for requesting a deadline extension."
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="deadline_reviews"
    )

    def __str__(self):
        return f"Deadline Extension Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"
    

class WriterOrderHoldRequest(models.Model):
    """
    Writers can request an order to be put on hold.
    This freezes the deadline count of the order until when put off hold.
    Admin approval is required.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="hold_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="hold_writer_requests"
    )
    reason = models.TextField(
        help_text="Reason for requesting hold."
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="hold_reviews"
    )

    def __str__(self):
        return f"Hold Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"
    

class WriterReassignmentRequest(models.Model):
    """
    Writers can request reassignment from an order.
    Admin approval is required.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_reassignment_request"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="writer_reassignment_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="reassignment_requests_by_writers"
    )
    reason = models.TextField(
        help_text="Reason for requesting reassignment."
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reassignment_reviews"
    )

    def __str__(self):
        return f"Reassignment Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"
    


class WriterOrderReopenRequest(models.Model):
    """
    Writers can request a completed order to be reopened.
    Admin must approve.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="reopen_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="reopen_requests"
    )
    reason = models.TextField(help_text="Reason for reopening the order.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reopen_reviews"
    )

    def __str__(self):
        return f"Reopen Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"
    

class WriterDemotionRequest(models.Model):
    """
    Editors or support staff can request an admin to demote a writer.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_demotion_request_website"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="demotion_requests"
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="demotion_requests_made_by"
    )
    reason = models.TextField(
        help_text="Reason for requesting writer demotion."
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        blank=True, related_name="demotion_reviews_by"
    )

    def __str__(self):
        return f"Demotion Request: {self.writer.user.username} (Approved: {self.approved})"


class WriterEarningsReviewRequest(models.Model):
    """
    Writers can request a review of their earnings.
    Admin must approve.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="earnings_review_requests"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="earnings_review_requests"
    )
    reason = models.TextField(help_text="Reason for requesting earnings review.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="earnings_review_reviews"
    )

    def __str__(self):
        return f"Earnings Review Request: {self.writer.user.username} (Approved: {self.approved})"