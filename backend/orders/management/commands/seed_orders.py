from decimal import Decimal
from datetime import timedelta
from random import choice, randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from order_configs.models import (
    PaperType,
    AcademicLevel,
    FormattingandCitationStyle,
    Subject,
    TypeOfWork,
    EnglishType,
    WriterDeadlineConfig,
)
from orders.models import Order
from orders.order_enums import OrderStatus, SpacingOptions
from websites.models import Website


DEFAULT_COUNTRY = "Unknown"
DEFAULT_TIMEZONE = "UTC"


class Command(BaseCommand):
    help = "Seed demo orders with various statuses for testing and UI demonstration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded orders before creating new ones",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of orders to create (default: 50)",
        )

    def ensure_user(self, *, email, username, role, password, website, **extra_fields):
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User(
                email=email,
                username=username,
                role=role,
                website=website,
                **extra_fields,
            )
            user.detected_country = DEFAULT_COUNTRY
            user.detected_timezone = DEFAULT_TIMEZONE
            user.set_password(password)
        else:
            user.username = username
            user.role = role
            if website and (user.website_id != website.id):
                user.website = website
            if not user.detected_country:
                user.detected_country = DEFAULT_COUNTRY
            if not user.detected_timezone:
                user.detected_timezone = DEFAULT_TIMEZONE
            if extra_fields.get("is_staff"):
                user.is_staff = True
            if extra_fields.get("is_superuser"):
                user.is_superuser = True
        user.save()
        return user

    def handle(self, *args, **options):
        count = max(10, options["count"])
        clear_existing = options["clear"]

        User = get_user_model()

        website, _ = Website.objects.get_or_create(
            domain="https://demo.writingsystem.test",
            defaults={"name": "Demo Writing System", "contact_email": "support@demo.test"},
        )

        # Ensure admin user exists
        admin_user = self.ensure_user(
            email="admin.demo@example.com",
            username="admin_demo",
            role="superadmin",
            password="AdminDemo123!",
            website=website,
            is_staff=True,
            is_superuser=True,
        )

        # Ensure client user exists
        client_user = self.ensure_user(
            email="client.demo@example.com",
            username="client_demo",
            role="client",
            password="ClientDemo123!",
            website=website,
        )

        # Create or get writers
        demo_writers = []
        for index in range(1, 6):  # Create 5 writers
            email = f"writer{index}.demo@example.com"
            username = f"writer_demo_{index}"
            writer_user = self.ensure_user(
                email=email,
                username=username,
                role="writer",
                password="WriterDemo123!",
                website=website,
            )
            demo_writers.append(writer_user)

        # Get or create order configs
        # PaperType has unique constraint on name, so we need to check carefully
        paper_type = PaperType.objects.filter(website=website).first()
        if not paper_type:
            # Try to find any Essay paper type and reuse it, or create new one
            paper_type = PaperType.objects.filter(name__icontains="Essay").first()
            if not paper_type:
                # Create with unique name
                unique_name = f"Essay-{uuid.uuid4().hex[:8]}"
                paper_type = PaperType.objects.create(website=website, name=unique_name)
            else:
                # Use existing one but update website if needed
                if paper_type.website_id != website.id:
                    paper_type.website = website
                    paper_type.save(update_fields=['website'])

        # Get or create configs - handle unique constraints
        academic_level = AcademicLevel.objects.filter(website=website, name="University").first()
        if not academic_level:
            academic_level = AcademicLevel.objects.filter(name="University").first()
            if not academic_level:
                academic_level = AcademicLevel.objects.create(website=website, name="University")
            elif academic_level.website_id != website.id:
                academic_level.website = website
                academic_level.save(update_fields=['website'])
        
        formatting_style = FormattingandCitationStyle.objects.filter(website=website, name="APA").first()
        if not formatting_style:
            formatting_style = FormattingandCitationStyle.objects.filter(name="APA").first()
            if not formatting_style:
                formatting_style = FormattingandCitationStyle.objects.create(website=website, name="APA")
            elif formatting_style.website_id != website.id:
                formatting_style.website = website
                formatting_style.save(update_fields=['website'])

        subject = Subject.objects.filter(website=website, name="Business").first()
        if not subject:
            subject = Subject.objects.filter(name="Business").first()
            if not subject:
                subject = Subject.objects.create(website=website, name="Business")
            elif subject.website_id != website.id:
                subject.website = website
                subject.save(update_fields=['website'])

        type_of_work = TypeOfWork.objects.filter(website=website, name="Writing").first()
        if not type_of_work:
            type_of_work = TypeOfWork.objects.filter(name="Writing").first()
            if not type_of_work:
                type_of_work = TypeOfWork.objects.create(website=website, name="Writing")
            elif type_of_work.website_id != website.id:
                type_of_work.website = website
                type_of_work.save(update_fields=['website'])

        english_type = EnglishType.objects.filter(website=website, name="US English").first()
        if not english_type:
            english_type = EnglishType.objects.filter(name="US English").first()
            if not english_type:
                english_type = EnglishType.objects.create(website=website, name="US English", code="US")
            elif english_type.website_id != website.id:
                english_type.website = website
                english_type.save(update_fields=['website'])

        writer_deadline_cfg, _ = WriterDeadlineConfig.objects.get_or_create(
            website=website, writer_deadline_percentage=80
        )

        # Clear existing seeded orders if requested
        if clear_existing:
            deleted_count = Order.objects.filter(
                website=website,
                topic__startswith="Demo Order"
            ).delete()[0]
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} existing seeded orders."))

        # Define status distribution - create orders with various statuses
        # Using only statuses that exist in OrderStatus enum
        status_distribution = [
            # Initial states
            (OrderStatus.CREATED.value, 4),
            (OrderStatus.PENDING.value, 4),
            (OrderStatus.UNPAID.value, 4),
            
            # Assignment states
            (OrderStatus.AVAILABLE.value, 4),
            (OrderStatus.ASSIGNED.value, 3),
            
            # Active work states
            (OrderStatus.IN_PROGRESS.value, 6),
            (OrderStatus.ON_HOLD.value, 2),
            (OrderStatus.REASSIGNED.value, 2),
            
            # Submission and review states
            (OrderStatus.SUBMITTED.value, 3),
            (OrderStatus.UNDER_REVIEW.value, 2),
            (OrderStatus.REVIEWED.value, 2),
            (OrderStatus.RATED.value, 2),
            (OrderStatus.APPROVED.value, 2),
            
            # Revision states
            (OrderStatus.REVISION_REQUESTED.value, 2),
            (OrderStatus.ON_REVISION.value, 2),
            (OrderStatus.REVISED.value, 2),
            
            # Editing states
            (OrderStatus.UNDER_EDITING.value, 2),
            
            # Dispute states
            (OrderStatus.DISPUTED.value, 1),
            
            # Final states
            (OrderStatus.COMPLETED.value, 3),
            (OrderStatus.ARCHIVED.value, 2),
            (OrderStatus.CLOSED.value, 2),
            (OrderStatus.CANCELLED.value, 2),
            (OrderStatus.REFUNDED.value, 1),
            (OrderStatus.REOPENED.value, 1),
        ]

        # Create orders with various statuses
        created_orders = []
        original_disable_pricing = getattr(settings, "DISABLE_PRICE_RECALC_DURING_TESTS", False)
        settings.DISABLE_PRICE_RECALC_DURING_TESTS = True
        
        try:
            order_counter = 1
            for status, num_orders in status_distribution:
                for i in range(num_orders):
                    if order_counter > count:
                        break
                    
                    # Select a random writer for assigned orders
                    assigned_writer = None
                    if status in [
                        OrderStatus.ASSIGNED.value,
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REASSIGNED.value,
                        OrderStatus.SUBMITTED.value,
                        OrderStatus.UNDER_REVIEW.value,
                        OrderStatus.REVIEWED.value,
                        OrderStatus.RATED.value,
                        OrderStatus.APPROVED.value,
                        OrderStatus.REVISION_REQUESTED.value,
                        OrderStatus.ON_REVISION.value,
                        OrderStatus.REVISED.value,
                        OrderStatus.UNDER_EDITING.value,
                        OrderStatus.DISPUTED.value,
                        OrderStatus.COMPLETED.value,
                    ]:
                        assigned_writer = choice(demo_writers) if demo_writers else None
                    
                    # Determine payment status based on order status
                    is_paid = status in [
                        OrderStatus.AVAILABLE.value,
                        OrderStatus.ASSIGNED.value,
                        OrderStatus.IN_PROGRESS.value,
                        OrderStatus.ON_HOLD.value,
                        OrderStatus.REASSIGNED.value,
                        OrderStatus.SUBMITTED.value,
                        OrderStatus.UNDER_REVIEW.value,
                        OrderStatus.REVIEWED.value,
                        OrderStatus.RATED.value,
                        OrderStatus.APPROVED.value,
                        OrderStatus.REVISION_REQUESTED.value,
                        OrderStatus.ON_REVISION.value,
                        OrderStatus.REVISED.value,
                        OrderStatus.UNDER_EDITING.value,
                        OrderStatus.DISPUTED.value,
                        OrderStatus.COMPLETED.value,
                        OrderStatus.ARCHIVED.value,
                        OrderStatus.CLOSED.value,
                    ]
                    
                    # Set deadlines based on status
                    days_offset = randint(-30, 30)  # Random days in past or future
                    client_deadline = timezone.now() + timedelta(days=days_offset)
                    writer_deadline = client_deadline - timedelta(days=1) if assigned_writer else None
                    
                    # Create order
                    order = Order.objects.create(
                        website=website,
                        client=client_user,
                        assigned_writer=assigned_writer,
                        topic=f"Demo Order #{order_counter} - {status.replace('_', ' ').title()}",
                        paper_type=paper_type,
                        academic_level=academic_level,
                        formatting_style=formatting_style,
                        subject=subject,
                        type_of_work=type_of_work,
                        english_type=english_type,
                        number_of_pages=randint(5, 20),
                        number_of_slides=0,
                        number_of_refereces=randint(3, 10),
                        spacing=choice([SpacingOptions.SINGLE.value, SpacingOptions.DOUBLE.value]),
                        status=status,
                        client_deadline=client_deadline,
                        writer_deadline=writer_deadline,
                        writer_deadline_percentage=writer_deadline_cfg,
                        total_price=Decimal(str(randint(100, 500))),
                        writer_compensation=Decimal(str(randint(50, 300))),
                        is_paid=is_paid,
                        order_instructions=f"This is a demo order with status '{status}'. Created for testing purposes.",
                    )
                    
                    # Set additional fields for completed orders
                    if status == OrderStatus.COMPLETED.value and assigned_writer:
                        order.completed_by = assigned_writer
                        order.submitted_at = timezone.now() - timedelta(days=randint(1, 7))
                        order.save(update_fields=['completed_by', 'submitted_at'])
                    
                    created_orders.append(order)
                    order_counter += 1
                    
                    if order_counter > count:
                        break
                
                if order_counter > count:
                    break
                    
        finally:
            settings.DISABLE_PRICE_RECALC_DURING_TESTS = original_disable_pricing

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(created_orders)} demo orders with various statuses."
            )
        )
        
        # Print status summary
        from django.db.models import Count
        status_summary = Order.objects.filter(
            website=website,
            topic__startswith="Demo Order"
        ).values('status').annotate(count=Count('id')).order_by('status')
        
        self.stdout.write("\nStatus distribution:")
        for item in status_summary:
            self.stdout.write(f"  {item['status']}: {item['count']} orders")
        
        self.stdout.write(
            f"\nYou can view these orders at /orders in the frontend."
        )

