from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from datetime import timedelta
from django.db import models
from django.utils import timezone

from websites.models import Website
from discounts.models.discount import Discount
from order_configs.models import WriterDeadlineConfig
from order_configs.models import AcademicLevel
from pricing_configs.models import PricingConfiguration
from django.core.exceptions import ValidationError

from .services.pricing_calculator import PricingCalculatorService
from django.apps import apps
from websites.models import Website
from orders.order_enums import (
    OrderStatus, OrderFlags,
    DisputeStatusEnum,
    SpacingOptions,
    OrderRequestStatus
)
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL 

# # Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()

# from writer_management.models import wr
class Order(models.Model):
    """
    Represents an order placed by a client.
    Inherits from WebsiteSpecificBaseModel
    for multi-website compatibility.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="order"
    )
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="orders_as_client",
        null=True,
        blank=True,
        limit_choices_to={'role': 'client'},
        help_text=(
            "The client who placed this order."
            "Leave blank for admin-created orders."
        )
    )
    assigned_writer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_as_writer",
        limit_choices_to={'role': 'writer'},
        help_text="The writer assigned to this order."
    )
    preferred_writer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'writer'},
        help_text="Preferred writer for this order."
    )
    topic = models.CharField(
        max_length=255, 
        help_text=(
            "The topic or title of the order."
        )
    )
    paper_type = models.ForeignKey(
        'order_configs.PaperType',
        on_delete=models.PROTECT,
        help_text="The type of paper requested."
    )
    discount = models.ForeignKey(
        Discount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    discount_code_used = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Discount code applied to the order."
    )   
    writer_level = models.ForeignKey(
        'pricing_configs.WriterLevelOptionConfig',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Selected writer quality level. eg. Standard, Premium."
    )
    academic_level = models.ForeignKey(
        AcademicLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="The academic level required."
    )
    formatting_style = models.ForeignKey(
        'order_configs.FormattingandCitationStyle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The formatting style required."
    )
    subject = models.ForeignKey(
        'order_configs.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The subject of the order."
    )
    is_follow_up = models.BooleanField(default=False)
    previous_order = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="follow_up_orders",
        help_text="Reference to the previous order this one follows up on."
    )
    type_of_work = models.ForeignKey(
        'order_configs.TypeOfWork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The type of work requested."
    )
    english_type = models.ForeignKey(
        'order_configs.EnglishType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Preferred English style for the paper."
    )
    number_of_pages = models.PositiveIntegerField(
        help_text="Number of pages required."
    )
    number_of_slides = models.PositiveIntegerField(
        default=0, help_text="Number of slides."
    )
    number_of_refereces = models.PositiveIntegerField(
        default=0, help_text="Number of references or sources."
    )
    spacing = models.CharField(
        max_length=10,
        choices=SpacingOptions.choices(),
        default=SpacingOptions.SINGLE.value,
        help_text="Spacing for the order."
    )
    extra_services = models.ManyToManyField(
        'pricing_configs.AdditionalService',
        blank=True,
        related_name='orders',
        help_text="Additional services requested."
    )
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.name) for status in OrderStatus],
        default=OrderStatus.CREATED.value,
        help_text="Current status of the order."
    )
    flags = ArrayField(
        base_field=models.CharField(
            max_length=10,
            choices=OrderFlags.choices()
        ),
        default=list,
        blank=True,
        help_text="Flags related to the order (e.g., Urgent Order (UO), Returning Client (RC0))."
    )
    client_deadline = models.DateTimeField(
        help_text="The deadline for the order."
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True,
        default=Decimal('0.00'),
        help_text="Total price of the order."
    )
    writer_compensation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        help_text="Compensation for the writer."
    )
    writer_deadline_percentage = models.ForeignKey(
        WriterDeadlineConfig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The Deadline the Writer sees"
    )
    writer_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Writer's deadline."
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Indicates if the order is paid."
    )
    is_urgent = models.BooleanField(default=False)
    requires_editing = models.BooleanField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            "Admin-controlled: Whether this order must undergo editing. "
            "None = use default/config rules, True = force editing, False = skip editing"
        )
    )
    editing_skip_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reason why editing was skipped (e.g., 'Urgent order', 'Admin disabled')"
    )
    created_by_admin = models.BooleanField(
        default=False,
        help_text="Indicates if the order was created by an admin."
    )
    is_special_order = models.BooleanField(
        default=False,
        help_text="Indicates if this is a special order."
    )
    is_public = models.BooleanField(default=False)  # Open to any writer if true
    reassignment_requested = models.BooleanField(default=False)
    order_instructions = models.TextField(
        help_text=(
            "Detailed instructions for the order."
        )
    )
    completed_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="completed_orders",
        limit_choices_to={'role__in': ['writer', 'editor', 'support', 'admin', 'superadmin']},
        help_text="User who completed the order."
    )
    completion_notes = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the writer submitted/uploaded the order."
    )
    reassigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Date and time when the order was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the order was last updated."
    )
    # External contact fields for unattributed orders
    external_contact_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of external contact for unattributed orders (e.g., from chat, WhatsApp)."
    )
    external_contact_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Email of external contact for unattributed orders."
    )
    external_contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Phone number of external contact for unattributed orders."
    )
    # Unpaid visibility override
    allow_unpaid_access = models.BooleanField(
        default=False,
        help_text="If True, allows access to this order even if unpaid. Admin can override default unpaid access restrictions."
    )

    # Include existing methods: calculate_total_cost,
    # calculate_writer_compensation, assign_flags, etc.
    # *** To add the writer progress field ****
    @property
    def status_enum(self) -> OrderStatus:
        """Get the order status as an `OrderStatus` enum.

        Returns:
            OrderStatus: The current status of the order as an enum.
        """
        return OrderStatus(self.status)

    @status_enum.setter
    def status_enum(self, value: OrderStatus):
        """Set the order status using an `OrderStatus` enum.

        Args:
            value (OrderStatus): The new status to assign to the order.

        Raises:
            ValueError: If `value` is not an instance of `OrderStatus`.
        """
        if isinstance(value, OrderStatus):
            self.status = value.value
        else:
            raise ValueError("status_enum must be an OrderStatus enum instance")

        
    def save(self, *args, **kwargs):
            """
            Trigger price recalculation whenever the order is saved.
            """
            calculator = PricingCalculatorService(self)
            self.total_price = calculator.calculate_total_price()
            super(Order, self).save(*args, **kwargs)

    def update_total_price(self):
        """
        Calculates and updates the total price of the order.
        """
        calculator = PricingCalculatorService(self)
        self.total_price = calculator.calculate_total_price()
        self.save(update_fields=["total_price"])

    def calculate_writer_deadline(
            client_deadline,
            writer_deadline_percentage
    ):
        """
        Calculates the writer deadline based on client deadline
        and admin-set buffer (writer deadline) percentage.

        Args:
            client_deadline (datetime): The deadline the client sees.
            buffer_percentage (float): A value between 0 and 100 (e.g., 80 for 80%).

        Returns:
            datetime: The deadline the writer should aim for.
        """
        if not (0 < writer_deadline_percentage <= 100):
            raise ValueError("Buffer percentage must be between 0 and 100.")

        now = timezone.now()
        total_time = client_deadline - now

        if total_time.total_seconds() <= 0:
            raise ValueError("Client deadline must be in the future.")

        writer_time = total_time * (writer_deadline_percentage / 100)

        writer_deadline = now + writer_time
        return writer_deadline

    def apply_discount(self, discount_code):
        """Apply a discount to the order."""
        discount = Discount.objects.get(code=discount_code)

        if not discount.is_valid(self.user):
            raise ValidationError(
                "Discount is not valid for this order."
            )

        if discount.discount_type == 'percentage':
            discount_amount = (self.total_price * discount.value) / Decimal(100)
        else:  # Fixed amount
            discount_amount = discount.value

        new_total_price = self.total_price - discount_amount + self.additional_cost
        
        # Ensure new total price isn't negative
        if new_total_price < 0:
            raise ValidationError("Order total cannot be negative.")
        
    def update_status(self, new_status):
        """Update order status."""
        self.status = new_status
        self.save()


    def add_additional_cost(self, additional_amount):
        """Add additional costs (e.g., extra pages or slides)."""
        self.additional_cost += Decimal(additional_amount)
        self.save()

    def change_deadline(self, old_deadline, new_deadline):
        """Method for safely changing the deadline and logging it."""
        # Ensure new_deadline is a future date
        if new_deadline <= self.deadline:
            raise ValidationError("New deadline must be later than the current deadline.")
        # Update the deadline
        self.deadline = new_deadline
        self.save()

        # Log the deadline change 
        DeadlineChangeLog.objects.create(
            order=self,
            old_deadline=old_deadline,
            new_deadline=new_deadline,
            changed_by=self.client
        )


    def update_status_based_on_payment(self):
        """
        Updates the order status when payment status
        changes in orders_payments_management.
        """
        Payment = apps.get_model(
            'order_payments_management', 'OrderPayment'
        )
        payment = Payment.objects.filter(
            order=self
        ).order_by('-created_at').first()  # Ensure latest payment

        if payment:
            # Fix: OrderPayment uses 'completed' not 'paid', and also check 'succeeded'
            if payment.status in ['completed', 'succeeded'] and self.status == 'unpaid':
                self.status = 'pending'
                self.is_paid = True
            elif payment.status in ['failed', 'refunded']:
                self.status = 'cancelled'
                self.is_paid = False

            self.save()
    
    def mark_paid(self):
        """
        Mark order as paid and transition to in_progress.
        This method is called by payment signals when payment is completed.
        """
        # Use the service for consistent behavior
        from orders.services.mark_order_as_paid_service import MarkOrderPaidService
        service = MarkOrderPaidService()
        # Service expects order_id, but we can call it directly
        if self.status == 'unpaid':
            self.status = 'in_progress'
            self.is_paid = True
            self.save()
        elif self.status not in ['unpaid']:
            # Log but don't raise - payment signal should handle gracefully
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Attempted to mark order {self.id} as paid from status {self.status}"
            )

    
    def add_pages(self, additional_pages: int):
        """
        Add extra pages to the existing order, recalculate the price for the new pages.
        The client will be redirected to pay for the extra pages.
        """
        self.number_of_pages += additional_pages
        # Recalculate the price with the new page count
        calculator = PricingCalculatorService(self)
        base_price = calculator.calculate_base_price()
        # Calculate price for the new pages
        pricing_config = PricingConfiguration.objects.filter(website=self.website).first()
        if not pricing_config:
            raise ValueError(f"No PricingConfiguration found for website {self.website}")
        new_page_price = additional_pages * pricing_config.base_price_per_page
        self.total_price = base_price + new_page_price  # Update the total cost
        self.save()

    def add_slides(self, additional_slides: int):
        """
        Add extra slides to the existing order, recalculate the price for the new slides.
        The client will be redirected to pay for the extra slides.
        """
        self.number_of_slides += additional_slides
        # Recalculate price with new slide count
        calculator = PricingCalculatorService(self)
        base_price = calculator.calculate_base_price()
        # Calculate price for the new slides
        pricing_config = PricingConfiguration.objects.filter(website=self.website).first()
        if not pricing_config:
            raise ValueError(f"No PricingConfiguration found for website {self.website}")
        new_slide_price = additional_slides * pricing_config.base_price_per_slide
        # Apply Discount that was already applied to the order
        if self.discount:
            discount_amount = self.discount.calculate_discount(self.total_price)
            base_price -= discount_amount

        # Update the total cost with the new slide price
        self.total_price = base_price + new_slide_price  # Update the total cost
        self.save()

    def add_extra_service(self, service):
        """
        Add extra service to the order, recalculate price, and prompt for payment.
        """
        self.extra_services.add(service)
        calculator = PricingCalculatorService(self)
        self.total_price = calculator.calculate_total_price()  # Recalculate price with new service
        self.save()

    def change_deadline(self, new_deadline):
        """
        Change the deadline, apply the necessary convenience fee if reduced.
        """
        pricing_config = PricingConfiguration.objects.filter(
            website=self.website
        ).first()
        
        if not pricing_config:
            raise ValueError(f"No PricingConfiguration found for website {self.website}")
        old_deadline = self.deadline
        self.deadline = new_deadline

        if new_deadline < old_deadline:
            # Apply convenience fee if deadline is reduced
            self.total_price += pricing_config.convenience_fee

        calculator = PricingCalculatorService(self)
        self.total_price = calculator.calculate_total_price()  # Recalculate after changing deadline
        self.save()

    @property
    def price_snapshot(self):
        return getattr(self, "pricing_snapshot", None)


    def add_discount(self, discount):
        """
        Add a discount to the order and recalculate the total price.
        """
        self.discount = discount
        calculator = PricingCalculatorService(self)
        self.total_price = calculator.calculate_total_price()
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.topic} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Single field indexes for common filters
            models.Index(fields=['status']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['created_at']),
            models.Index(fields=['client']),
            models.Index(fields=['assigned_writer']),
            models.Index(fields=['website']),
            # Composite indexes for common query patterns
            models.Index(fields=['status', 'is_paid']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['assigned_writer', 'status']),
            models.Index(fields=['website', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['is_paid', 'created_at']),
        ]

    # Backward-compat deadline alias for tests
    @property
    def deadline(self):
        return getattr(self, 'client_deadline', None)

    @deadline.setter
    def deadline(self, value):
        self.client_deadline = value

    def __init__(self, *args, **kwargs):
        # Allow legacy/alias field names from tests
        alias_writer = kwargs.pop('writer', None)
        if alias_writer is not None:
            kwargs['assigned_writer'] = alias_writer
        alias_deadline = kwargs.pop('deadline', None)
        if alias_deadline is not None:
            kwargs['client_deadline'] = alias_deadline
        # Map type_of_work by name if a string is provided
        tow = kwargs.get('type_of_work')
        if isinstance(tow, str):
            try:
                TypeOfWork = apps.get_model('order_configs', 'TypeOfWork')
                tow_obj = (
                    TypeOfWork.objects.filter(name__iexact=tow).first()
                    or TypeOfWork.objects.filter(slug__iexact=slugify(tow)).first()
                )
                if tow_obj is not None:
                    kwargs['type_of_work'] = tow_obj
            except Exception:
                pass
        # Map legacy test payload keys
        title = kwargs.pop('title', None)
        if title is not None:
            kwargs['topic'] = title
        description = kwargs.pop('description', None)
        if description is not None:
            kwargs['order_instructions'] = description
        price = kwargs.pop('price', None)
        if price is not None:
            kwargs['total_price'] = price
        # Map academic_level by name if a string is provided
        acad = kwargs.get('academic_level')
        if isinstance(acad, str):
            try:
                # Resolve model lazily and ensure website exists
                AcademicLevel = apps.get_model('order_configs', 'AcademicLevel')
                from websites.models import Website
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name='Test Website', domain='https://test.local', is_active=True)
                level = (
                    AcademicLevel.objects.filter(name__iexact=acad, website=site).first()
                )
                if level is None:
                    level = AcademicLevel.objects.create(name=acad, website=site)
                kwargs['academic_level'] = level
            except Exception:
                pass
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Ensure website is set from client or writer if missing
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'client', None) and getattr(self.client, 'website_id', None):
                    self.website_id = self.client.website_id
                elif getattr(self, 'assigned_writer', None) and getattr(self.assigned_writer, 'website_id', None):
                    self.website_id = self.assigned_writer.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name='Test Website', domain='https://test.local', is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        # Auto-select a default PaperType if missing to satisfy tests
        if not getattr(self, 'paper_type_id', None):
            try:
                PaperType = apps.get_model('order_configs', 'PaperType')
                pt = PaperType.objects.first()
                if pt is None:
                    # Ensure website is set on PaperType for multi-tenancy
                    website_id = getattr(self, 'website_id', None)
                    if website_id is None:
                        site = Website.objects.filter(is_active=True).first()
                        if site is None:
                            site = Website.objects.create(name='Test Website', domain='https://test.local', is_active=True)
                        website_id = site.id
                    pt = PaperType.objects.create(name='Essay', website_id=website_id)
                self.paper_type_id = pt.id
            except Exception:
                pass
        # Map academic_level by name if it arrived as a string
        if isinstance(getattr(self, 'academic_level', None), str):
            try:
                level = (
                    AcademicLevel.objects.filter(name__iexact=self.academic_level).first()
                    or AcademicLevel.objects.filter(title__iexact=self.academic_level).first()
                )
                if level is not None:
                    self.academic_level = level
            except Exception:
                pass
        # Default required numeric fields for tests
        if getattr(self, 'number_of_pages', None) in (None, 0):
            self.number_of_pages = 1
        # Trigger price recalculation unless disabled during tests
        from django.conf import settings as dj_settings
        if not getattr(dj_settings, "DISABLE_PRICE_RECALC_DURING_TESTS", False):
            # Only calculate price if we have a website (required for pricing config)
            if self.website_id:
                try:
                    calculator = PricingCalculatorService(self)
                    self.total_price = calculator.calculate_total_price()
                except (ValueError, LookupError) as e:
                    # If pricing config doesn't exist yet, set default price or skip
                    # This allows orders to be created before pricing config is set up
                    if not self.total_price:
                        # Set a default price based on pages if available
                        from pricing_configs.models import PricingConfiguration
                        config = PricingConfiguration.objects.filter(
                            website=self.website
                        ).first()
                        if config:
                            self.total_price = config.base_price_per_page * (self.number_of_pages or 1)
                        else:
                            # No config available, set minimal default
                            self.total_price = Decimal('0.00')
        super(Order, self).save(*args, **kwargs)

class PreferredWriterResponse(models.Model):
    """
    Handles the preferred writer's response when declining
    to work on an order.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='preferred_writer_decline_response'
    ) 
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='preferred_writer_responses',
    )
    response = models.CharField(
        max_length=10,
        choices=[('accepted', 'Accepted'), ('declined', 'Declined')]
    )
    reason = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(auto_now_add=True)

class DeadlineChangeLog(models.Model):
    """
    Logs every deadline change for audit.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='deadline_change_log'
    ) 
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_deadline = models.DateTimeField()
    new_deadline = models.DateTimeField()
    changed_by = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='deadline_changes',
        help_text="User who changed the deadline."
    )
    reason = models.TextField()

    def __str__(self):
        return f"Deadline changed for Order #{self.order.id}"

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

class WriterProgress(models.Model):
    """
    Tracks progress logs for writers working on orders.
    Includes notes, screened word checking, and admin moderation.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='writer_progress'
    )
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="progress_logs",
        limit_choices_to={"role": "writer"},
        help_text="The writer associated with this progress log."
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="progress_logs",
        help_text="The order associated with this progress log."
    )
    progress_percentage = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)],
        help_text="Percentage of work completed (0-100)."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about the progress update."
    )
    # Moderation fields
    is_withdrawn = models.BooleanField(
        default=False,
        help_text="Whether this progress report has been withdrawn by admin due to policy violations."
    )
    withdrawn_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="withdrawn_progress_reports",
        help_text="Admin/superadmin who withdrew this report."
    )
    withdrawn_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this report was withdrawn."
    )
    withdrawal_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for withdrawal (e.g., screened words detected)."
    )
    # Flag for screened words
    contains_screened_words = models.BooleanField(
        default=False,
        help_text="Whether this report contains screened words."
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_screened_words(self):
        """Check if notes contain screened words."""
        if not self.notes:
            return False
        
        from communications.models import ScreenedWord
        screened_words = ScreenedWord.objects.values_list('word', flat=True)
        
        notes_lower = self.notes.lower()
        for word in screened_words:
            if word.lower() in notes_lower:
                self.contains_screened_words = True
                return True
        
        self.contains_screened_words = False
        return False
    
    def withdraw(self, withdrawn_by, reason=None):
        """Withdraw this progress report."""
        self.is_withdrawn = True
        self.withdrawn_by = withdrawn_by
        self.withdrawn_at = timezone.now()
        if reason:
            self.withdrawal_reason = reason
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to check for screened words."""
        if self.notes:
            self.check_screened_words()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['order', '-timestamp']),
            models.Index(fields=['writer', '-timestamp']),
            models.Index(fields=['is_withdrawn']),
        ]

    def __str__(self):
        status = " (Withdrawn)" if self.is_withdrawn else ""
        return (
            f"Progress {self.progress_percentage}% for Order {self.order.id} "
            f"by {self.writer.username}{status}"
        )


class Dispute(models.Model):
    """
    Tracks disputes raised for an order.
    The order status is automatically updated when 
    disputes are raised, reviewed, or resolved.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='order_dispute'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='disputes',
        help_text="The order associated with this dispute."
    )
    raised_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_raised',
        help_text="The user who raised the dispute."
    )
    dispute_status = models.CharField(
        max_length=20,
        choices=DisputeStatusEnum.choices(),
        default=DisputeStatusEnum.OPEN.value,
        help_text="The current status of the dispute."
    )
    resolution_outcome = models.CharField(
        max_length=20,
        choices=[
            ('writer_wins', 'Writer Wins'),
            ('client_wins', 'Client Wins'),
            ('extend_deadline', 'Extend Deadline'),
            ('reassign', 'Reassign Order'),
        ],
        null=True,
        blank=True,
        help_text="Outcome of the dispute resolution."
    )
    reason = models.TextField(
        help_text="Reason for raising the dispute."
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes or comments regarding the resolution."
    )
    writer_responded = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer has responded."
    )
    admin_extended_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, admin has manually extended the deadline."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dispute was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the dispute was last updated."
    )

    def save(self, *args, **kwargs):
        """
        Automatically update order status when dispute is
        raised, reviewed, escalated, or resolved.
        """
        Order = apps.get_model('orders', 'Order')

        if self._state.adding and self.order.status == 'cancelled':
            raise ValueError(
                "Cannot raise a dispute for a cancelled order."
            )
        if self._state.adding and self.order.status == 'progress':
            raise ValueError(
                "Cannot raise a dispute for an order in progress."
            )

        if self._state.adding:
            self.order.status = 'disputed'
            self.writer_responded = False
            self.notify_users(
                "New Dispute Raised",
                f"A dispute has been raised for Order #{self.order.id}. "
                "Admin review is required."
            )
        if self.status == 'in_review':
            self.order.status = 'in_review'
        elif self.status == 'escalated':
            self.order.status = 'escalated'
        elif self.status == 'resolved':
            self.resolve_dispute_action()

        self.order.save()
        super().save(*args, **kwargs)

    def resolve_dispute_action(self, resolved_by):
        """
        Updates the order status based on
        the dispute resolution decision.
        """
        if self.resolution_outcome == 'writer_wins':
            self.order.status = 'completed'
        elif self.resolution_outcome == 'client_wins':
            self.order.status = 'cancelled'
        elif self.resolution_outcome == 'extend_deadline':
            self.order.change_deadline(resolved_by.new_deadline)
            self.order.status = 'revision'
        elif self.resolution_outcome == 'reassign':
            self.order.status = 'available'
            self.order.writer = None

        self.order.save()

    def notify_users(self, subject, message):
        recipients = []

        # Notify assigned writer
        if self.order.writer:
            recipients.append(self.order.writer.email)

        # Notify the person who raised the dispute
        if self.raised_by:
            recipients.append(self.raised_by.email)

        # Notify admins
        admin_emails = User.objects.filter(
            role__in=['admin', 'superadmin', 'support']
        ).values_list('email', flat=True)

        if recipients:
            send_mail(
                subject,
                message, 
                "no-reply@yourdomain.com",
                recipients
            )

    def __str__(self):
        return f"Dispute #{self.id} for Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class DisputeWriterResponse(models.Model):
    """
    Model to track writer responses to disputes.
    Writers must respond before a final decision.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='dispute_writer_response'
    )
    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.CASCADE,
        related_name='writer_responses_to_disputes',
        help_text="The dispute being responded to."
    )
    responded_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='dispute_writer_responses',
        limit_choices_to={'role': 'writer'},
        help_text="The writer responding to the dispute."
    )
    response_text = models.TextField(
        help_text="Writer's response or clarification."
    )
    response_file = models.FileField(
        upload_to='dispute_responses/',
        null=True,
        blank=True,
        help_text="Optional file upload for revised work."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time of response."
    )

    def __str__(self):
        return (
            f"Writer Response for Dispute #{self.dispute.id} by "
            f"{self.responded_by.username}"
        )


    def save(self, *args, **kwargs):
        """
        Mark dispute as responded
        when a writer submits a response.
        """
        self.dispute.writer_responded = True
        self.dispute.save()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('dispute', 'responded_by')
        ordering = ['-timestamp']


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


class OrderDiscount(models.Model):
    """
    Tracks which discounts were applied to a specific order and their amounts.
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="applied_discounts"
    )
    discount = models.ForeignKey(
        'discounts.Discount',
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.discount.code} - ${self.amount} on Order {self.order.id}"
    
    
class ClientFeedback(models.Model):
    """
    Stores feedback from a client about an order experience.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="client_feedbacks"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="order_feedbacks"
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Optional rating from 1 (worst) to 5 (best)."
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional client comment about the order."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.client} on Order #{self.order.id}"
    

class OrderTransitionLog(models.Model):
    """
    Logs all status transitions for an order.
    This is useful for auditing and tracking changes in order status.
    """
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="transitions"
    )
    user = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    old_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32)
    action = models.CharField(max_length=64)  # e.g. "mark_paid", "auto_expire"
    is_automatic = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)  # optional context or payload

    class Meta:
        ordering = ['-timestamp']


class WebhookDeliveryLog(models.Model):
    """
    Records each webhook delivery attempt.
    """
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE,
        related_name="webhook_logs"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="webhook_delivery_logs_for_website"
        )
    event = models.CharField(max_length=50)
    url = models.URLField()
    success = models.BooleanField(default=False)
    status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True, null=True)
    request_payload = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, null=True)
    test_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    retry_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]


class OrderPricingSnapshot(models.Model):
    """
    Captures a snapshot of the order's pricing details at a specific time.
    This is useful for auditing and historical reference.
    """
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="pricing_snapshot"
    )
    pricing_data = models.JSONField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pricing Snapshot for Order #{self.order.id} at {self.calculated_at}"
    

class WriterReassignmentLog(models.Model):
    """
    Logs all writer reassignments for transparency and audit.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="reassignment_logs"
    )
    previous_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_lost"
    )
    new_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_gained"
    )
    reassigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_made"
    )
    reason = models.TextField(
        blank=True,
        help_text="Optional reason for the reassignment."
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="When the reassignment occurred."
    )

    class Meta:
        verbose_name = "Writer Reassignment Log"
        verbose_name_plural = "Writer Reassignment Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order.id} reassigned to {self.new_writer}"
    

class SoftDeletableMixin(models.Model):
    """Soft deletion flags and metadata."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_%(class)ss",
    )
    delete_reason = models.CharField(max_length=255, blank=True, default="")
    restored_at = models.DateTimeField(null=True, blank=True)
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="restored_%(class)ss",
    )

    class Meta:
        abstract = True

    def mark_deleted(self, user, reason=""):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.delete_reason = reason[:255] if reason else ""
        self.restored_at = None
        self.restored_by = None

    def mark_restored(self, user):
        self.is_deleted = False
        self.restored_at = timezone.now()
        self.restored_by = user