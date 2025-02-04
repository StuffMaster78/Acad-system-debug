from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from websites.models import Website
from orders.models import Order
from wallet.models import Wallet
from django.core.exceptions import ValidationError

User = get_user_model()


class WriterProfile(models.Model):
    """
    Represents the profile of a writer.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="writer_profile",
        limit_choices_to={"role": "writer"},
        help_text="The user associated with this writer profile."
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique writer registration ID (e.g., Writer #12345)."
    )
    email = models.EmailField(unique=True, help_text="Writer's email address.")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Writer's phone number.")
    country = models.CharField(max_length=100, blank=True, null=True, help_text="Writer's country.")
    timezone = models.CharField(max_length=50, default="UTC", help_text="Writer's timezone.")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Last known IP address of the writer.")
    location_verified = models.BooleanField(default=False, help_text="Whether the writer's location has been verified.")
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writers",
        help_text="Website the writer is associated with."
    )
    joined = models.DateTimeField(default=now, help_text="Date when the writer joined.")
    last_logged_in = models.DateTimeField(blank=True, null=True, help_text="The last time the writer logged in.")
    writer_level = models.ForeignKey(
        "WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writers",
        help_text="The level of the writer."
    )
    completed_orders = models.PositiveIntegerField(default=0, help_text="Total completed orders by the writer.")
    number_of_takes = models.PositiveIntegerField(default=0, help_text="Total orders the writer has accepted.")
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total earnings by the writer."
    )
    verification_status = models.BooleanField(default=False, help_text="Indicates whether the writer has been verified.")
    verification_documents = models.JSONField(
        default=dict,
        blank=True,
        help_text="Uploaded documents for verification (e.g., ID, certificates)."
    )
    skills = models.TextField(blank=True, null=True, help_text="Skills and specialties of the writer.")
    subject_preferences = models.TextField(blank=True, null=True, help_text="Subjects or topics the writer prefers to handle.")
    education = models.JSONField(default=list, blank=True, help_text="List of schools attended and uploaded certificates.")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Average rating of the writer.")
    active_orders = models.PositiveIntegerField(default=0, help_text="Number of ongoing orders assigned to the writer.")

    def __str__(self):
        return f"Writer Profile: {self.user.username} ({self.registration_id})"

    @property
    def average_rating(self):
        """
        Calculate the average rating for the writer based on WriterRating objects.
        """
        avg_rating = self.ratings.aggregate(models.Avg("rating"))["rating__avg"]
        return round(avg_rating, 2) if avg_rating is not None else 0.0


    @property
    def total_ratings(self):
        """
        Count the total number of ratings the writer has received.
        """
        return self.ratings.count()

    @property
    def recent_feedback(self):
        """
        Retrieve the most recent feedback provided for the writer.
        """
        return self.ratings.order_by("-created_at").values("feedback", "rating", "created_at")[:5]

    @property
    def leave_status(self):
        """
        Check if the writer is currently on leave.
        """
        current_leaves = self.leaves.filter(
            start_date__lte=now(),
            end_date__gte=now(),
            approved=True
        )
        return current_leaves.exists()

    @property
    def wallet_balance(self):
        """
        Retrieve the writer's wallet balance.
        """
        wallet = Wallet.objects.filter(user=self.user).first()
        return wallet.balance if wallet else 0.00


class WriterLevel(models.Model):
    """
    Represents different levels or tiers of writers.
    Includes base pay rates, urgent order multipliers, and technical order adjustments.
    """
    name = models.CharField(max_length=50, unique=True, help_text="Name of the writer level (e.g., Beginner, Intermediate).")
    max_orders = models.PositiveIntegerField(default=10, help_text="Maximum number of orders the writer can take simultaneously.")
    
    # Base pay rates
    base_pay_per_page = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base pay per page.")
    base_pay_per_slide = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base pay per slide.")

    # Urgency-based multipliers
    urgency_percentage_increase = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Percentage increase for urgent orders."
    )
    urgency_deadline_limit = models.PositiveIntegerField(
        default=8, help_text="Maximum hours considered as 'urgent' (e.g., orders within 8 hours get extra pay)."
    )

    # Technical order adjustments
    technical_order_adjustment_per_page = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Extra pay per page for technical orders."
    )
    technical_order_adjustment_per_slide = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Extra pay per slide for technical orders."
    )

    tip_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Tip percentage."
    )

    def __str__(self):
        return f"{self.name} (Max Orders: {self.max_orders}, Base Pay/Page: {self.base_pay_per_page})"

    def calculate_order_payment(self, pages, slides, is_urgent, is_technical):
        """
        Calculate the writer's earnings based on the order details.
        """
        base_payment = (pages * self.base_pay_per_page) + (slides * self.base_pay_per_slide)

        # Apply urgency adjustment if the order is urgent
        if is_urgent:
            base_payment += (base_payment * (self.urgency_percentage_increase / 100))

        # Apply technical order adjustments
        if is_technical:
            base_payment += (pages * self.technical_order_adjustment_per_page) + (slides * self.technical_order_adjustment_per_slide)

        return round(base_payment, 2)


class WriterLeave(models.Model):
    """
    Tracks periods when a writer is unavailable for work.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="leaves",
        help_text="The writer who is unavailable."
    )
    start_date = models.DateTimeField(help_text="Start date of the leave period.")
    end_date = models.DateTimeField(help_text="End date of the leave period.")
    reason = models.TextField(blank=True, null=True, help_text="Reason for the leave (e.g., vacation, emergency).")
    approved = models.BooleanField(default=False, help_text="Whether the leave has been approved by an admin.")

    def __str__(self):
        return f"Leave: {self.writer.user.username} ({self.start_date} - {self.end_date})"


class WriterActionLog(models.Model):
    """
    Logs actions taken on writers (e.g., warnings, probation, suspension).
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="action_logs",
        help_text="The writer this action applies to."
    )
    action = models.CharField(
        max_length=20,
        choices=(
            ("warning", "Warning"),
            ("probation", "Probation"),
            ("suspension", "Suspension"),
            ("deactivation", "Deactivation"),
        ),
        help_text="The type of action taken."
    )
    reason = models.TextField(blank=True, null=True, help_text="Reason for taking this action.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action: {self.action} for {self.writer.user.username}"


class WriterEducation(models.Model):
    """
    Tracks education history and uploaded certificates for verification.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="education_details",
        help_text="The writer whose education details are being tracked."
    )
    institution_name = models.CharField(max_length=255, help_text="Name of the educational institution.")
    degree = models.CharField(max_length=255, help_text="Degree or certification obtained.")
    graduation_year = models.PositiveIntegerField(null=True, blank=True, help_text="Year of graduation.")
    document = models.FileField(upload_to="education_certificates/", help_text="Upload proof of education (e.g., certificate).")
    is_verified = models.BooleanField(default=False, help_text="Indicates whether this education has been verified by the admin.")

    def __str__(self):
        return f"{self.degree} from {self.institution_name} ({self.writer.user.username})"


class PaymentHistory(models.Model):
    """
    Tracks payment history for writers, including bonuses, fines, and tips.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="payment_history",
        help_text="The writer receiving the payment."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total payment amount made to the writer."
    )
    bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Bonuses received by the writer."
    )
    fines = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Fines deducted from the writer."
    )
    tips = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Tips received by the writer."
    )
    payment_date = models.DateTimeField(auto_now_add=True, help_text="Date of the payment.")
    description = models.TextField(blank=True, null=True, help_text="Optional description for the payment.")

    def __str__(self):
        return f"Payment of ${self.amount} to {self.writer.user.username} on {self.payment_date}"



class WriterRewardCriteria(models.Model):
    """
    Admin-defined criteria for writer rewards (automated or manual).
    """
    name = models.CharField(max_length=200, help_text="Name of the reward criteria (e.g., 'Top Performer').")
    min_completed_orders = models.PositiveIntegerField(default=10, help_text="Minimum orders required.")
    min_rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5, help_text="Minimum rating required.")
    min_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=500.00, help_text="Minimum earnings required.")
    auto_reward_enabled = models.BooleanField(default=True, help_text="Enable automatic rewards.")

    def __str__(self):
        return f"Reward Criteria: {self.name} (Auto: {self.auto_reward_enabled})"

        
class WriterReward(models.Model):
    """
    Tracks rewards given to writers, including criteria, performance metrics, and prizes.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="rewards",
        help_text="The writer receiving this reward."
    )
    criteria = models.ForeignKey(WriterRewardCriteria, on_delete=models.SET_NULL, null=True, blank=True, related_name="rewards_given")
    title = models.CharField(max_length=200, help_text="Custom title for the reward (e.g., 'Top Performer').")
    performance_metric = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details of the performance metric used to determine the reward (e.g., ratings, urgent orders)."
    )
    awarded_date = models.DateTimeField(default=now, help_text="Date the reward was given.")
    prize = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Prize or benefit given to the writer (e.g., 'Bonus $50')."
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the reward.")

    def __str__(self):
        return f"{self.title} - {self.writer.user.username} ({self.awarded_date})"


class WriterDemotionRequest(models.Model):
    """
    Editors or support staff can request an admin to demote a writer.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="demotion_requests")
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="demotion_requests_made")
    reason = models.TextField(help_text="Reason for requesting writer demotion.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="demotion_reviews")

    def __str__(self):
        return f"Demotion Request: {self.writer.user.username} (Approved: {self.approved})"


class WriterPerformanceReport(models.Model):
    """
    Stores performance analytics for writers.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="performance_reports")
    period_start = models.DateTimeField(help_text="Start of performance tracking period.")
    period_end = models.DateTimeField(help_text="End of performance tracking period.")
    completed_orders = models.PositiveIntegerField(default=0, help_text="Total completed orders.")
    disputes = models.PositiveIntegerField(default=0, help_text="Total disputes.")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Average rating for the period.")

    def __str__(self):
        return f"Performance Report: {self.writer.user.username} ({self.period_start} - {self.period_end})"

class WriterRating(models.Model):
    """
    Tracks client ratings and feedback for writers.
    """
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="ratings",
        help_text="The writer being rated."
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings_given",
        limit_choices_to={"role": "client"},
        help_text="The client providing the rating."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="writer_ratings",
        help_text="The order associated with this rating."
    )
    rating = models.PositiveIntegerField(
        help_text="Rating given by the client (1 to 5).",
        choices=[(i, str(i)) for i in range(1, 6)]  # Ratings from 1 to 5
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Optional feedback provided by the client."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the rating was created.")

    def __str__(self):
        return f"Rating {self.rating} for {self.writer.user.username} by {self.client.username} (Order {self.order.id})"
    


class Probation(models.Model):
    """Tracks writers placed on probation."""
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="probation_records")
    placed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="probation_admins")
    reason = models.TextField(help_text="Reason for probation.")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(help_text="Date when probation ends.")
    is_active = models.BooleanField(default=True)

    def check_expiry(self):
        """Automatically deactivates probation if the end_date has passed."""
        if self.end_date < now():
            self.is_active = False
            self.save()

    def __str__(self):
        return f"Probation: {self.writer.user.username} (Active: {self.is_active})"



class WriterPenalty(models.Model):
    """
    Logs penalties and fines applied to writers.
    """
    PENALTY_REASONS = [
        ("Late Submission", "Late Submission"),
        ("Plagiarism", "Plagiarism"),
        ("Missed Deadline", "Missed Deadline"),
        ("Client Complaint", "Client Complaint"),
        ("Other", "Other"),
    ]

    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="penalties")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="penalties")
    reason = models.CharField(max_length=50, choices=PENALTY_REASONS, help_text="Reason for penalty.")
    amount_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fine deducted from earnings.")
    applied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="penalty_appliers")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes.")

    def __str__(self):
        return f"Penalty: {self.writer.user.username} - {self.reason} (${self.amount_deducted})"


class WriterSuspension(models.Model):
    """
    Tracks suspended writers.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="suspensions")
    reason = models.TextField(help_text="Reason for suspension.")
    suspended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspension_admins")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True, help_text="Optional end date for temporary suspensions.")
    is_active = models.BooleanField(default=True, help_text="If True, the writer is currently suspended.")

    def lift_suspension(self):
        """
        Admin can manually lift a suspension.
        """
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Suspension: {self.writer.user.username} (Active: {self.is_active})"



class WriterPayoutPreference(models.Model):
    """
    Stores writer payout preferences.
    """
    PAYMENT_METHOD_CHOICES = [
        ("Bank Transfer", "Bank Transfer"),
        ("PayPal", "PayPal"),
        ("Crypto", "Crypto"),
        ("Other", "Other"),
    ]

    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="payout_preferences")
    preferred_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="PayPal")
    payout_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=50.00, help_text="Minimum payout threshold.")
    account_details = models.JSONField(default=dict, blank=True, help_text="Payment account details (e.g., PayPal email, bank details).")

    def __str__(self):
        return f"Payout Preference: {self.writer.user.username} - {self.preferred_method}"


class WriterPayment(models.Model):
    """
    Tracks payment history for writers.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total payment amount.")
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Bonuses received.")
    fines = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Fines deducted.")
    tips = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Tips received.")
    payment_date = models.DateTimeField(auto_now_add=True, help_text="Date of payment.")
    description = models.TextField(blank=True, null=True, help_text="Payment description.")

    def __str__(self):
        return f"Payment of ${self.amount} to {self.writer.user.username} on {self.payment_date}"


class WriterEarningsHistory(models.Model):
    """
    Tracks the writer's total earnings over different time periods.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="earnings_history")
    period_start = models.DateTimeField(help_text="Start date of the earnings period.")
    period_end = models.DateTimeField(help_text="End date of the earnings period.")
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total earnings for the period.")
    orders_completed = models.PositiveIntegerField(default=0, help_text="Number of completed orders during this period.")

    def __str__(self):
        return f"Earnings for {self.writer.user.username}: {self.period_start} - {self.period_end}"


class WriterEarningsReviewRequest(models.Model):
    """
    Writers can request an admin to review earnings for a specific order.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="earnings_review_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="earnings_review_requests")
    reason = models.TextField(help_text="Reason for requesting earnings review.")
    requested_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True, help_text="Admin resolution notes.")

    def __str__(self):
        return f"Earnings Review Request: {self.writer.user.username} for Order {self.order.id} (Resolved: {self.resolved})"




class WriterReassignmentRequest(models.Model):
    """
    Writers can request reassignment from an order.
    Admin approval is required.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="reassignment_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reassignment_requests")
    reason = models.TextField(help_text="Reason for requesting reassignment.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reassignment_reviews")

    def __str__(self):
        return f"Reassignment Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"


class WriterOrderHoldRequest(models.Model):
    """
    Writers can request an order to be put on hold.
    Admin approval is required.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="hold_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="hold_requests")
    reason = models.TextField(help_text="Reason for requesting hold.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="hold_reviews")

    def __str__(self):
        return f"Hold Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"


class OrderDispute(models.Model):
    """
    Writers can dispute an order.
    Admins must resolve the dispute.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="disputes")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="writer_order_disputes")
    reason = models.TextField(help_text="Reason for disputing the order.")
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True, help_text="Admin notes on dispute resolution.")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispute_resolutions")

    def __str__(self):
        return f"Dispute: {self.writer.user.username} for Order {self.order.id} (Resolved: {self.resolved})"


class WriterOrderReopenRequest(models.Model):
    """
    Writers can request a completed order to be reopened.
    Admin must approve.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="reopen_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reopen_requests")
    reason = models.TextField(help_text="Reason for reopening the order.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reopen_reviews")

    def __str__(self):
        return f"Reopen Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"


class WriterActivityLog(models.Model):
    """
    Tracks every action performed by a writer.
    """
    ACTION_TYPES = [
        ("Order Accepted", "Order Accepted"),
        ("Order Submitted", "Order Submitted"),
        ("File Uploaded", "File Uploaded"),
        ("Message Sent", "Message Sent"),
        ("Request Made", "Request Made"),
        ("Reopened Order", "Reopened Order"),
        ("Deadline Extension Requested", "Deadline Extension Requested"),
        ("Reassignment Requested", "Reassignment Requested"),
    ]

    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="activity_logs")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, help_text="Type of action performed.")
    description = models.TextField(blank=True, null=True, help_text="Additional details about the action.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Time the action was recorded.")

    def __str__(self):
        return f"Activity: {self.writer.user.username} - {self.action_type} ({self.timestamp})"

# class WriterActivityLog(models.Model):
#     """
#     Tracks every action performed by a writer.
#     """
#     ACTION_TYPES = [
#         ("Order Accepted", "Order Accepted"),
#         ("Order Submitted", "Order Submitted"),
#         ("File Uploaded", "File Uploaded"),
#         ("Message Sent", "Message Sent"),
#         ("Request Made", "Request Made"),
#         ("Reopened Order", "Reopened Order"),
#         ("Deadline Extension Requested", "Deadline Extension Requested"),
#         ("Reassignment Requested", "Reassignment Requested"),
#     ]

#     writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="activity_logs")
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
#     action_type = models.CharField(max_length=50, choices=ACTION_TYPES, help_text="Type of action performed.")
#     description = models.TextField(blank=True, null=True, help_text="Additional details about the action.")
#     timestamp = models.DateTimeField(auto_now_add=True, help_text="Time the action was recorded.")

#     def __str__(self):
#         return f"Activity: {self.writer.user.username} - {self.action_type} ({self.timestamp})"


class WriterMessageThread(models.Model):
    """
    A thread for writer messages.
    Each order has a writer-client and/or writer-admin thread.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="message_threads")
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="message_threads")
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writer_participant_threads",
                                    help_text="The client or admin participating in the thread.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message Thread for Order {self.order.id} - {self.writer.user.username} & {self.participant.username}"
    

class WriterMessage(models.Model):
    """
    Messages exchanged between a writer and a client/admin in an order thread.
    """
    thread = models.ForeignKey(WriterMessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_writer_messages")
    content = models.TextField(help_text="Message content.")
    attachment = models.FileField(upload_to="writer_messages/", blank=True, null=True, help_text="Optional message attachment.")
    timestamp = models.DateTimeField(auto_now_add=True)
    flagged = models.BooleanField(default=False, help_text="Flagged for admin moderation.")

    def __str__(self):
        return f"Message from {self.sender.username} in Thread {self.thread.id} (Flagged: {self.flagged})"


class WriterMessageModeration(models.Model):
    """
    Stores flagged messages for admin review.
    """
    message = models.ForeignKey(WriterMessage, on_delete=models.CASCADE, related_name="moderation")
    flagged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="moderated_messages")
    reason = models.TextField(help_text="Reason for flagging the message.")
    reviewed = models.BooleanField(default=False, help_text="Has the admin reviewed this message?")
    action_taken = models.CharField(max_length=50, choices=[
        ("Delete", "Delete"),
        ("Warn Writer", "Warn Writer"),
        ("No Action", "No Action"),
    ], blank=True, null=True)

    def __str__(self):
        return f"Moderation - {self.message.id} (Reviewed: {self.reviewed})"


class WriterSupportTicket(models.Model):
    """
    Writers can submit tickets for support.
    """
    CATEGORY_CHOICES = [
        ("Order Issue", "Order Issue"),
        ("Payment Issue", "Payment Issue"),
        ("Technical Support", "Technical Support"),
        ("Other", "Other"),
    ]

    STATUS_CHOICES = [
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ]

    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="support_tickets")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(help_text="Details of the issue.")
    attachment = models.FileField(upload_to="writer_tickets/", blank=True, null=True, help_text="Optional attachment.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_writer_tickets")

    def __str__(self):
        return f"Ticket {self.id} - {self.writer.user.username} ({self.status})"

class WriterDeadlineExtensionRequest(models.Model):
    """
    Writers can request a deadline extension for an order.
    Admin/Client approval required.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="deadline_extension_requests")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="deadline_extension_requests")
    old_deadline = models.DateTimeField(help_text="Current order deadline.")
    requested_deadline = models.DateTimeField(help_text="New requested deadline.")
    reason = models.TextField(help_text="Reason for requesting a deadline extension.")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deadline_reviews")

    def __str__(self):
        return f"Deadline Extension Request: {self.writer.user.username} for Order {self.order.id} (Approved: {self.approved})"


class WriterAutoRanking(models.Model):
    """
    Auto-Promotion & Auto-Demotion based on writer performance.
    Admins can override.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="auto_ranking")
    promoted = models.BooleanField(default=False, help_text="Has the writer been auto-promoted?")
    demoted = models.BooleanField(default=False, help_text="Has the writer been auto-demoted?")
    reason = models.TextField(help_text="Reason for auto-promotion/demotion.")
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ranking_reviews")

    def __str__(self):
        return f"Auto-Ranking: {self.writer.user.username} (Promoted: {self.promoted}, Demoted: {self.demoted})"


class WriterActivityTracking(models.Model):
    """
    Tracks when a writer was last active.
    Helps admins monitor writer activity.
    """
    writer = models.OneToOneField(WriterProfile, on_delete=models.CASCADE, related_name="activity_tracking")
    last_login = models.DateTimeField(blank=True, null=True, help_text="Last time the writer logged in.")
    last_seen = models.DateTimeField(blank=True, null=True, help_text="Last time the writer was active.")

    def update_last_seen(self):
        self.last_seen = now()
        self.save()

    def __str__(self):
        return f"Activity Tracking: {self.writer.user.username} (Last Seen: {self.last_seen})"


class WriterIPLog(models.Model):
    """
    Logs multiple IP addresses used by a writer.
    Helps detect account sharing or fraud.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="ip_logs")
    ip_address = models.GenericIPAddressField(help_text="IP address used by the writer.")
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"IP Log: {self.writer.user.username} - {self.ip_address} ({self.logged_at})"


class WriterRatingCooldown(models.Model):
    """
    Prevents clients from rating a writer until the order is fully completed.
    Cooldown period prevents rating abuse.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="rating_cooldown")
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="rating_cooldowns")
    cooldown_until = models.DateTimeField(help_text="Time until the client can submit a rating.")
    rating_allowed = models.BooleanField(default=False, help_text="Has the cooldown expired?")

    def __str__(self):
        return f"Rating Cooldown for {self.writer.user.username} (Expires: {self.cooldown_until})"


class WriterFileDownloadLog(models.Model):
    """
    Logs when a writer downloads order files.
    Helps with tracking and accountability.
    """
    writer = models.ForeignKey(WriterProfile, on_delete=models.CASCADE, related_name="file_download_logs")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="writer_file_download_logs")
    file_name = models.CharField(max_length=255, help_text="Name of the downloaded file.")
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Download: {self.writer.user.username} - {self.file_name} ({self.downloaded_at})"

class WriterConfig(models.Model):
    """
    Admin-controlled settings for writers.
    This allows admins to enable/disable order takes.
    """
    takes_enabled = models.BooleanField(
        default=True,
        help_text="If True, writers can take orders directly. If False, writers must request orders."
    )
    max_requests_per_writer = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of order requests a writer can have at once."
    )

    def __str__(self):
        return f"Writer Config - Takes Enabled: {self.takes_enabled}"


class WriterOrderRequest(models.Model):
    """
    Writers can request an order, expressing their interest.
    Admins must review and approve.
    """
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE, related_name="order_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="writer_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True, help_text="When the request was made.")
    approved = models.BooleanField(default=False, help_text="Has the request been approved?")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_request_reviews"
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
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE, related_name="taken_orders"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="writer_takes"
    )
    taken_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the order was taken.")

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