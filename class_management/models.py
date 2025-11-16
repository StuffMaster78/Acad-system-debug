"""
Models for managing class bundles, purchases, durations, and related
client interactions such as messages, tickets, and wallet transactions.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings
from django.utils import timezone
from communications.models import CommunicationThread
from tickets.models import Ticket
from wallet.models import Wallet
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


class ClassBundleFile(models.Model):
    """
    File attachments for class bundles.
    Can be uploaded by clients, writers, admins, editors, superadmins.
    """
    class_bundle = models.ForeignKey(
        'ClassBundle',
        on_delete=models.CASCADE,
        related_name='files',
        help_text="Class bundle this file belongs to"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='class_bundle_files',
        help_text="User who uploaded the file"
    )
    file = models.FileField(
        upload_to='class_bundles/files/',
        help_text="Uploaded file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the file"
    )
    is_visible_to_client = models.BooleanField(
        default=True,
        help_text="Whether file is visible to client"
    )
    is_visible_to_writer = models.BooleanField(
        default=True,
        help_text="Whether file is visible to writer"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.class_bundle} - {self.uploaded_by}"


class ClassBundle(models.Model):
    """
    Represents a bundle of classes purchased by a client.
    Can be created from a config bundle OR manually by admin with custom pricing.
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
    
    PRICING_SOURCE_CHOICES = [
        ('config', 'From Bundle Config'),
        ('manual', 'Admin Manual Entry'),
    ]
    
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Client who bought the bundle"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="class_bundles",
        help_text="Website this bundle belongs to"
    )
    assigned_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_class_bundles',
        limit_choices_to={'role': 'writer'},
        help_text="Writer assigned to this class bundle"
    )
    config = models.ForeignKey(
        ClassBundleConfig,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Base pricing config used (if from config)"
    )
    pricing_source = models.CharField(
        max_length=20,
        choices=PRICING_SOURCE_CHOICES,
        default='config',
        help_text="Whether pricing came from config or manual admin entry"
    )
    duration = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Duration copied from config or manually set"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='in_progress',
        help_text="The status of the class bundle."
    )
    level = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Level copied from config or manually set"
    )
    bundle_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of classes in this bundle"
    )
    price_per_class = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price per class in this bundle"
    )
    number_of_classes = models.PositiveIntegerField(
        help_text="Actual number of classes client needs done"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Class start date (date A)"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Class end date (date B)"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total price of the bundle (from config or manually set, before discount)"
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price before discount (if discount applied)"
    )
    discount = models.ForeignKey(
        'discounts.Discount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_bundles',
        help_text="Applied discount (set by admin)"
    )
    deposit_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Deposit amount required before starting classes (set by admin, after discount)"
    )
    deposit_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Amount of deposit already paid"
    )
    balance_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Remaining balance after payments (excluding deposit)"
    )
    installments_enabled = models.BooleanField(
        default=False,
        help_text="Whether installments are enabled for this bundle"
    )
    installment_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of installments (set by admin)"
    )
    created_by_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_class_bundles",
        help_text="Admin who created this bundle (if manual)"
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
            f"{self.get_level_display() if self.level else 'Class'} | {self.duration or 'N/A'} | "
            f"{self.bundle_size or self.number_of_classes} class bundle"
        )

    def save(self, *args, **kwargs):
        """
        Autofill class details from config during first save, or use manual values.
        """
        if not self.pk:
            if self.config and self.pricing_source == 'config':
                # Fill from config
                self.duration = self.config.duration.class_code
                self.level = self.config.level
                self.bundle_size = self.config.bundle_size
                self.price_per_class = self.config.price_per_class
                if not self.total_price:
                    self.total_price = self.bundle_size * self.price_per_class
            # Calculate balance remaining (total - deposit paid - payments made)
            if not self.balance_remaining:
                self.balance_remaining = self.total_price - self.deposit_required
        
        super().save(*args, **kwargs)
    
    def update_balance(self):
        """Update balance_remaining based on payments."""
        total_paid = self.installments.filter(is_paid=True).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Balance = total_price - deposit_required - installments_paid
        # (deposit is separate, not counted in balance)
        self.balance_remaining = max(
            Decimal('0'),
            self.total_price - self.deposit_required - Decimal(str(total_paid))
        )
        self.save(update_fields=['balance_remaining'])
    
    @property
    def has_deposit_paid(self):
        """Check if deposit is fully paid."""
        return self.deposit_paid >= self.deposit_required
    
    @property
    def is_fully_paid(self):
        """Check if bundle is fully paid (deposit + installments)."""
        total_paid = self.installments.filter(is_paid=True).aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return (self.has_deposit_paid and 
                Decimal(str(total_paid)) >= (self.total_price - self.deposit_required))

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
    Represents a payment record for a class bundle deposit.
    NOTE: Installment payments are tracked via ClassInstallment.payment_record
    linking to OrderPayment. This model is mainly for deposit payments.
    
    For unified payment workflow, use OrderPayment with payment_type='class_payment'.
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
        related_name="purchases",
        help_text="Target class bundle"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="class_purchases",
        help_text="Website this purchase belongs to"
    )
    payment_record = models.ForeignKey(
        'order_payments_management.OrderPayment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_purchases',
        help_text="The actual payment transaction record (for unified payment workflow)"
    )
    payment_type = models.CharField(
        max_length=20,
        default='deposit',
        choices=[
            ('deposit', 'Deposit Payment'),
            ('full', 'Full Payment'),
            ('installment', 'Installment Payment'),
        ],
        help_text="Type of payment"
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
        return f"{self.client} - {self.bundle} - {self.payment_type} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Lock the price at the time of payment.
        """
        if not self.price_locked:
            if self.payment_type == 'deposit':
                self.price_locked = self.bundle.deposit_required
            else:
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
    Supports scheduled installments with due dates and payment tracking.
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
        help_text="Amount due for this installment"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this installment is due"
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether this installment has been paid"
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this installment was paid"
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made the payment"
    )
    payment_record = models.ForeignKey(
        'order_payments_management.OrderPayment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_installments',
        help_text="The actual payment transaction record for this installment"
    )
    installment_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Sequence number of this installment (1, 2, 3, ...)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['installment_number', 'due_date']
    
    def __str__(self):
        status = "Paid" if self.is_paid else "Pending"
        return f"Installment #{self.installment_number} of ${self.amount} for {self.class_bundle} - {status}"
    
    def mark_paid(self, payment_record=None, paid_by=None):
        """Mark installment as paid and link payment record."""
        self.is_paid = True
        self.paid_at = timezone.now()
        if payment_record:
            self.payment_record = payment_record
        if paid_by:
            self.paid_by = paid_by
        self.save()
        # Update bundle balance
        self.class_bundle.update_balance()


class ExpressClass(models.Model):
    """
    Represents a single express class request (different from class bundles).
    Client submits inquiry, admin reviews scope, sets price, assigns writer.
    """
    INQUIRY = "inquiry"
    SCOPE_REVIEW = "scope_review"
    PRICED = "priced"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    STATUS_CHOICES = [
        (INQUIRY, "Inquiry"),
        (SCOPE_REVIEW, "Scope Review"),
        (PRICED, "Priced"),
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]
    
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="express_classes",
        help_text="Client booking the express class"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="express_classes",
        help_text="Website this express class belongs to"
    )
    assigned_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_express_classes",
        limit_choices_to={'role': 'writer'},
        help_text="Writer assigned to this express class"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=INQUIRY,
        help_text="Current status of the express class"
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
        default=0,
        help_text="Number of discussion posts required"
    )
    number_of_discussion_posts_replies = models.PositiveIntegerField(
        default=0,
        help_text="Number of discussion post replies required"
    )
    number_of_assignments = models.PositiveIntegerField(
        default=0,
        help_text="Number of assignments required"
    )
    number_of_exams = models.PositiveIntegerField(
        default=0,
        help_text="Number of exams required"
    )
    number_of_quizzes = models.PositiveIntegerField(
        default=0,
        help_text="Number of quizzes required"
    )
    number_of_projects = models.PositiveIntegerField(
        default=0,
        help_text="Number of projects required"
    )
    number_of_presentations = models.PositiveIntegerField(
        default=0,
        help_text="Number of presentations required"
    )
    number_of_papers = models.PositiveIntegerField(
        default=0,
        help_text="Number of papers required"
    )
    total_workload_in_pages = models.CharField(
        max_length=100,
        blank=True,
        help_text="Workload e.g., 'number of pages total'"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price for the express class (set by admin after scope review)"
    )
    price_approved = models.BooleanField(
        default=False,
        help_text="Whether the price has been approved by admin"
    )
    installments_needed = models.PositiveIntegerField(
        default=0,
        help_text="Number of installments needed (0 = full payment)"
    )
    instructions = models.TextField(
        blank=True,
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
    # School login credentials
    school_login_link = models.URLField(
        blank=True,
        help_text="Link to school login portal"
    )
    school_login_username = models.CharField(
        max_length=255,
        blank=True,
        help_text="School login username"
    )
    school_login_password = models.CharField(
        max_length=255,
        blank=True,
        help_text="School login password (encrypted/stored securely)"
    )
    # Admin review fields
    scope_review_notes = models.TextField(
        blank=True,
        help_text="Admin notes from scope review"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="General admin notes"
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_express_classes",
        limit_choices_to={'role__in': ['admin', 'superadmin', 'support']},
        help_text="Admin who reviewed the scope"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the scope was reviewed"
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
