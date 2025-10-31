"""
Models for managing class bundles, purchases, durations, and related
client interactions such as messages, tickets, and wallet transactions.
"""
import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
# from websites.models import Website
from communications.models import CommunicationThread
from tickets.models import Ticket
from wallet.models import Wallet
from django.apps import apps

from websites.models import Website

# Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()
User = settings.AUTH_USER_MODEL

class ClassDurationOption(models.Model):
    """
    Represents selectable duration options for classes per website.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="duration_options",
        help_text="Website-specific duration choice"
    )
    class_code = models.CharField(
        max_length=10,
        help_text="Short identifier e.g., '15-16'"
    )
    label = models.CharField(
        max_length=50,
        help_text="Human-readable label e.g., '15–16 weeks'"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("website", "class_code")

    def __str__(self):
        return f"{self.website.name} - {self.label}"


class ClassBundleConfig(models.Model):
    """
    Configurable class bundle pricing and metadata per website.
    """
    UNDERGRAD = "undergrad"
    GRAD = "grad"
    LEVEL_CHOICES = [
        (UNDERGRAD, "Undergraduate"),
        (GRAD, "Graduate"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="class_configs",
        help_text="Website this config applies to"
    )
    duration = models.ForeignKey(
        ClassDurationOption,
        on_delete=models.PROTECT,
        help_text="Target class duration option"
    )
    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        help_text="Academic level"
    )
    bundle_size = models.PositiveIntegerField(
        help_text="Number of classes in bundle"
    )
    price_per_class = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per individual class"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("duration", "level", "bundle_size")

    def __str__(self):
        return (
            f"{self.get_level_display()} | {self.duration} | "
            f"{self.bundle_size} classes"
        )

    @property
    def total_price(self):
        """
        Calculates total price for the full bundle.
        """
        return self.bundle_size * self.price_per_class


class ClassBundle(models.Model):
    """
    Represents a bundle of classes purchased by a client.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    EXHAUSTED = "exhausted"
    COMPLETED = "completed"

    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (EXHAUSTED, "Exhausted"),
        (COMPLETED, "Completed"),
    ]
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Client who bought the bundle"
    )
    config = models.ForeignKey(
        ClassBundleConfig,
        on_delete=models.PROTECT,
        help_text="Base pricing config used"
    )
    duration = models.CharField(
        max_length=10,
        help_text="Duration copied from config"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='in_progress',
        help_text="The status of the class bundle."
    )
    level = models.CharField(
        max_length=10,
        help_text="Level copied from config"
    )
    bundle_size = models.PositiveIntegerField(
        help_text="Number of classes in this bundle"
    )
    price_per_class = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per class in this bundle"
    )
    number_of_classes = models.PositiveIntegerField(
        help_text="Actual number of classes client needs done"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated full price of the bundle"
    )
    balance_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Remaining balance after payments"
    )
    message_threads = GenericRelation(CommunicationThread)
    support_tickets = GenericRelation(Ticket)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Metadata for the ClassBundle model."""
        verbose_name = "Class Bundle"
        verbose_name_plural = "Class Bundles"
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.get_level_display()} | {self.duration} | "
            f"{self.bundle_size} class bundle"
        )

    def save(self, *args, **kwargs):
        """
        Autofill class details from config during first save.
        """
        if not self.pk and self.config:
            self.duration = self.config.duration.code
            self.level = self.config.level
            self.bundle_size = self.config.bundle_size
            self.price_per_class = self.config.price_per_class
            self.total_price = self.bundle_size * self.price_per_class
            self.balance_remaining = self.total_price
        super().save(*args, **kwargs)

    def mark_as_exhausted(self):
        """
        Mark the class bundle as 'exhausted'. This is typically done once all 
        classes within the bundle have been completed.

        Returns:
            None
        """
        self.status = 'exhausted'
        self.save()

    def mark_as_completed(self):
        """
        Mark the class bundle as 'completed'. This is done when all classes 
        have been completed and the bundle is finished.

        Returns:
            None
        """
        self.status = 'completed'
        self.save()


class ClassPurchase(models.Model):
    """
    Represents a payment made for a class bundle.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Purchasing user"
    )
    bundle = models.ForeignKey(
        ClassBundle,
        on_delete=models.PROTECT,
        help_text="Target class bundle"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current payment status"
    )
    price_locked = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Locked price at time of payment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    reference_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Payment processor ref (e.g. Stripe)"
    )

    def __str__(self):
        return f"{self.client} - {self.bundle} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Lock the price at the time of payment.
        """
        if not self.price_locked:
            self.price_locked = self.bundle.total_price
        super().save(*args, **kwargs)


class WalletTransaction(models.Model):
    """
    Transaction record tied to a class purchase.
    """
    WALLET_TYPES = [
        ('deposit', 'Deposit'),
        ('deduction', 'Deduction'),
        ('refund', 'Refund'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="User wallet",
        related_name="class_management_wallet_transactions"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPES,
        help_text="Type of transaction"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Transaction amount"
    )
    related_purchase = models.ForeignKey(
        ClassPurchase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Purchase tied to this transaction"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)


class ClassInstallment(models.Model):
    """
    Represents a single installment toward a class bundle.
    """
    class_bundle = models.ForeignKey(
        ClassBundle,
        on_delete=models.CASCADE,
        related_name="installments",
        help_text="Target class bundle"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount paid"
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who made the payment"
    )

    def __str__(self):
        return f"Installment of ${self.amount} for {self.class_bundle}"


class ExpressClass(models.Model):
    """
    Represents a class that does not fit into the bundle model.
    """
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Client booking the express class"
    )
    start_date = models.DateField(
        help_text="Start date for the express class"
    )
    end_date = models.DateField(
        help_text="End date for the express class"
    )
    discipline = models.CharField(
        max_length=100,
        help_text="Discipline of the express class e.g., Math, Nursing"
    )
    number_of_discussion_posts = models.PositiveIntegerField(
        help_text="Number of discussion posts required"
    )
    number_of_discussion_posts_replies = models.PositiveIntegerField(
        help_text="Number of discussion post replies required"
    )
    number_of_assignments = models.PositiveIntegerField(
        help_text="Number of assignments required"
    )
    number_of_exams = models.PositiveIntegerField(
        help_text="Number of exams required"
    )
    number_of_quizzes = models.PositiveIntegerField(
        help_text="Number of quizzes required"
    )
    number_of_projects = models.PositiveIntegerField(
        help_text="Number of projects required"
    )
    number_of_presentations = models.PositiveIntegerField(
        help_text="Number of presentations required"
    )
    number_of_papers = models.PositiveIntegerField(
        help_text="Number of papers required"
    )
    total_workload_in_pages = models.CharField(
        max_length=100,
        help_text="Workload e.g., 'number of pages total'"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price for the express class"
    )
    installments_needed = models.PositiveIntegerField(
        help_text="Number of installments needed"
    )
    instructions = models.TextField(
        help_text="Special instructions for the express class"
    )
    institution = models.CharField(
        max_length=255,
        help_text="Client's institution"
    )
    course = models.CharField(
        max_length=255,
        help_text="Course name or code"
    )
    academic_level = models.CharField(
        max_length=50,
        help_text="Academic level e.g., Undergraduate, Graduate"
    )
    message_threads = GenericRelation(CommunicationThread)
    support_tickets = GenericRelation(Ticket)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Express Class"
        verbose_name_plural = "Express Classes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Express Class for {self.client} from {self.start_date} to {self.end_date}"