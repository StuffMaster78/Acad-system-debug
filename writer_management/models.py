from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from websites.models import Website
from orders.models import Order
from wallet.models import Wallet

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
        ratings = self.ratings.all()
        if ratings.exists():
            return round(ratings.aggregate(models.Avg("rating"))["rating__avg"], 2)
        return 0.0

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
    """
    name = models.CharField(max_length=50, unique=True, help_text="Name of the writer level (e.g., Beginner, Intermediate).")
    max_orders = models.PositiveIntegerField(default=10, help_text="Maximum number of orders the writer can take simultaneously.")
    base_pay_per_page = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base pay per page.")
    base_pay_per_slide = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base pay per slide.")
    tip_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tip percentage.")

    def __str__(self):
        return f"{self.name} (Max Orders: {self.max_orders}, Base Pay/Page: {self.base_pay_per_page})"


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
        related_name="education",
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