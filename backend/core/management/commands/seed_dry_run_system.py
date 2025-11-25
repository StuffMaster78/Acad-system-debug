"""
Django management command to seed the system for a complete dry run.
Creates 3 websites, 100 clients, configurations, writers, orders, and completes orders.
"""
from decimal import Decimal
from datetime import timedelta
from random import choice, randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import os
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save

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
from pricing_configs.models import PricingConfiguration, AcademicLevelPricing, WriterLevelOptionConfig
from wallet.models import Wallet
from writer_management.models.payout import WriterPayment

User = get_user_model()


class Command(BaseCommand):
    help = "Seed complete system for dry run: 3 websites, 100 clients, configurations, writers, orders, and completed orders"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded data before creating new ones",
        )

    def ensure_user(self, *, email, username, role, password, website, **extra_fields):
        """Ensure a user exists, create if not."""
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User(
                email=email,
                username=username,
                role=role,
                website=website,
                detected_country="Unknown",
                detected_timezone="UTC",
                **extra_fields,
            )
            user.set_password(password)
            # Disable auto-detection during save
            user._skip_auto_detection = True
            user.save()
        else:
            user.username = username
            user.role = role
            if website and (user.website_id != website.id):
                user.website = website
            if extra_fields.get("is_staff"):
                user.is_staff = True
            if extra_fields.get("is_superuser"):
                user.is_superuser = True
            user._skip_auto_detection = True
            user.save()
        return user

    def safe_get_or_create(self, model, name, website, **defaults):
        """Safely create a model instance, handling unique constraint on name."""
        existing = model.objects.filter(name=name, website=website).first()
        if existing:
            return existing, False
        # Check if one exists with same name but different website
        existing_other = model.objects.filter(name=name).exclude(website=website).first()
        if existing_other:
            # Create with website name suffix to avoid conflict
            unique_name = f"{name} ({website.name})"
            # Check if the unique name already exists
            existing_unique = model.objects.filter(name=unique_name, website=website).first()
            if existing_unique:
                return existing_unique, False
            return model.objects.create(name=unique_name, website=website, **defaults), True
        else:
            return model.objects.create(name=name, website=website, **defaults), True

    def create_website_configs(self, website):
        """Create all necessary configurations for a website."""
        self.stdout.write(f"  Creating configurations for {website.name}...")
        
        # Paper Types
        paper_types = [
            'Essay', 'Research Paper', 'Term Paper', 'Dissertation', 'Thesis',
            'Case Study', 'Article Review', 'Book Report', 'Literature Review',
            'Annotated Bibliography', 'Coursework', 'Lab Report', 'Presentation',
        ]
        for pt_name in paper_types:
            self.safe_get_or_create(PaperType, pt_name, website)
        
        # Formatting Styles
        formatting_styles = ['APA', 'MLA', 'Chicago', 'Turabian', 'Harvard', 'IEEE']
        for style_name in formatting_styles:
            self.safe_get_or_create(FormattingandCitationStyle, style_name, website)
        
        # Academic Levels
        academic_levels = [
            'High School', 'College', 'Undergraduate', 'Bachelor\'s', 'Master\'s',
            'Graduate', 'PhD', 'Doctorate',
        ]
        for level_name in academic_levels:
            AcademicLevel.objects.get_or_create(
                name=level_name,
                website=website,
                defaults={}
            )
        
        # Subjects
        subjects_data = [
            ('English', False), ('Literature', False), ('History', False),
            ('Psychology', False), ('Business', False), ('Economics', False),
            ('Biology', True), ('Chemistry', True), ('Physics', True),
            ('Mathematics', True), ('Computer Science', True), ('Engineering', True),
            ('Nursing', False), ('Medicine', True), ('Law', False),
        ]
        for subject_name, is_technical in subjects_data:
            self.safe_get_or_create(Subject, subject_name, website, is_technical=is_technical)
        
        # Types of Work
        types_of_work = ['Writing', 'Editing', 'Proofreading', 'Rewriting', 'Research']
        for work_type_name in types_of_work:
            self.safe_get_or_create(TypeOfWork, work_type_name, website)
        
        # English Types
        english_types = [
            ('US English', 'US'), ('UK English', 'UK'),
            ('Australian English', 'AU'), ('Canadian English', 'CA'),
        ]
        for eng_name, code in english_types:
            existing = EnglishType.objects.filter(name=eng_name, website=website).first()
            if existing:
                continue
            # Check if name already exists for another website
            existing_name = EnglishType.objects.filter(name=eng_name).exclude(website=website).first()
            # Check if code already exists
            existing_code = EnglishType.objects.filter(code=code).exclude(website=website).first()
            
            if existing_name or existing_code:
                # Use modified name and code to avoid conflicts
                unique_name = f"{eng_name} ({website.name})"
                unique_code = f"{code}_{website.slug[:3].upper()}"
                # Check if unique name already exists for this website
                existing_unique = EnglishType.objects.filter(name=unique_name, website=website).first()
                if existing_unique:
                    continue
                EnglishType.objects.create(name=unique_name, website=website, code=unique_code)
            else:
                EnglishType.objects.create(name=eng_name, website=website, code=code)
        
        # Writer Deadline Config
        WriterDeadlineConfig.objects.get_or_create(
            website=website,
            writer_deadline_percentage=80,
            defaults={}
        )
        
        # Pricing Configuration
        pricing_config, _ = PricingConfiguration.objects.get_or_create(
            website=website,
            defaults={
                'base_price_per_page': Decimal('10.00'),
                'base_price_per_slide': Decimal('5.00'),
                'technical_multiplier': Decimal('1.5'),
                'non_technical_order_multiplier': Decimal('1.0'),
            }
        )
        
        # Academic Level Pricing
        level_multipliers = {
            'High School': Decimal('0.8'),
            'College': Decimal('0.9'),
            'Undergraduate': Decimal('1.0'),
            'Bachelor\'s': Decimal('1.0'),
            'Master\'s': Decimal('1.3'),
            'Graduate': Decimal('1.3'),
            'PhD': Decimal('1.5'),
            'Doctorate': Decimal('1.5'),
        }
        for level_name, multiplier in level_multipliers.items():
            level = AcademicLevel.objects.filter(name=level_name, website=website).first()
            if level:
                base_slug = level_name.lower().replace(' ', '-').replace('\'', '')
                # Make slug unique by adding website identifier if needed
                existing_slug = AcademicLevelPricing.objects.filter(slug=base_slug).exclude(website=website).first()
                if existing_slug:
                    unique_slug = f"{base_slug}-{website.slug}"
                else:
                    unique_slug = base_slug
                
                AcademicLevelPricing.objects.get_or_create(
                    website=website,
                    academic_level=level,
                    defaults={
                        'multiplier': multiplier,
                        'level_name': level_name,
                        'slug': unique_slug,
                    }
                )
        
        # Writer Level Options
        writer_levels = [
            ('Standard', Decimal('0.00'), 'Standard quality writer'),
            ('Premium', Decimal('5.00'), 'Premium quality writer'),
            ('Top 10', Decimal('10.00'), 'Top 10 writers'),
        ]
        for name, value, desc in writer_levels:
            WriterLevelOptionConfig.objects.get_or_create(
                website=website,
                name=name,
                defaults={
                    'value': value,
                    'description': desc,
                    'active': True,
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f"  ✓ Configurations created for {website.name}"))

    def create_sample_writer_payments(self, writer_user):
        """Create historical writer payment data for the given writer."""
        try:
            profile = writer_user.writer_profile
        except Exception:
            self.stdout.write(self.style.WARNING(f"  ⚠ Could not find writer profile for {writer_user.email}, skipping payment seed."))
            return

        website = profile.website
        existing_payments = WriterPayment.objects.filter(writer=profile).count()
        if existing_payments >= 3:
            self.stdout.write(f"  Writer payments already exist for {writer_user.email}, skipping creation.")
            return

        payment_templates = [
            {
                "amount": Decimal("245.50"),
                "bonuses": Decimal("15.00"),
                "tips": Decimal("8.00"),
                "fines": Decimal("0.00"),
                "offset_days": 12,
                "description": "Fortnightly payout covering urgent orders and quality bonus.",
            },
            {
                "amount": Decimal("310.75"),
                "bonuses": Decimal("0.00"),
                "tips": Decimal("20.00"),
                "fines": Decimal("5.00"),
                "offset_days": 32,
                "description": "Monthly payout with client tips and minor late delivery deduction.",
            },
            {
                "amount": Decimal("198.25"),
                "bonuses": Decimal("10.00"),
                "tips": Decimal("0.00"),
                "fines": Decimal("0.00"),
                "offset_days": 55,
                "description": "Fortnightly payout with revision assistance bonus.",
            },
        ]

        self.stdout.write(f"  Creating sample writer payments for {writer_user.email}...")
        for template in payment_templates:
            WriterPayment.objects.create(
                website=website,
                writer=profile,
                amount=template["amount"],
                bonuses=template["bonuses"],
                fines=template["fines"],
                tips=template["tips"],
                description=template["description"],
                payment_date=timezone.now() - timedelta(days=template["offset_days"]),
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Seeded writer payments for {writer_user.email}"))

    def handle(self, *args, **options):
        # Temporarily disable cache operations that require Redis
        original_delete = cache.delete
        original_set = cache.set
        
        def safe_delete(*args, **kwargs):
            try:
                return original_delete(*args, **kwargs)
            except Exception:
                return None
        
        def safe_set(*args, **kwargs):
            try:
                return original_set(*args, **kwargs)
            except Exception:
                return None
        
        cache.delete = safe_delete
        cache.set = safe_set
        
        # Disable notification signals during seeding
        original_disable = getattr(settings, 'DISABLE_NOTIFICATION_SIGNALS', False)
        settings.DISABLE_NOTIFICATION_SIGNALS = True
        
        # Disable Celery
        original_enable_celery = os.environ.get('ENABLE_CELERY', '1')
        os.environ['ENABLE_CELERY'] = '0'
        
        # Disable auto-creation of WriterProfile
        original_disable_writer_profile = getattr(settings, 'DISABLE_AUTO_CREATE_WRITER_PROFILE', False)
        settings.DISABLE_AUTO_CREATE_WRITER_PROFILE = True
        
        try:
            self._handle(*args, **options)
        finally:
            cache.delete = original_delete
            cache.set = original_set
            settings.DISABLE_NOTIFICATION_SIGNALS = original_disable
            os.environ['ENABLE_CELERY'] = original_enable_celery
            settings.DISABLE_AUTO_CREATE_WRITER_PROFILE = original_disable_writer_profile
    
    def _handle(self, *args, **options):
        clear_existing = options["clear"]
        
        if clear_existing:
            self.stdout.write(self.style.WARNING("Clearing existing seeded data..."))
            # Clear seeded orders
            Order.objects.filter(topic__startswith="Dry Run Order").delete()
            # Clear seeded users (clients and writers)
            User.objects.filter(
                email__startswith="dryrun.client"
            ).delete()
            User.objects.filter(
                email__startswith="dryrun.writer"
            ).delete()
            self.stdout.write(self.style.SUCCESS("Cleared existing seeded data."))
        
        # Create 3 websites
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING WEBSITES")
        self.stdout.write("="*70)
        
        websites = []
        website_data = [
            ("Academic Writing Pro", "https://academicwritingpro.com", "academic-pro"),
            ("Essay Masters", "https://essaymasters.com", "essay-masters"),
            ("Paper Experts", "https://paperexperts.com", "paper-experts"),
        ]
        
        for name, domain, slug in website_data:
            website, created = Website.objects.get_or_create(
                domain=domain,
                defaults={
                    "name": name,
                    "slug": slug,
                    "is_active": True,
                    "contact_email": f"support@{slug}.com",
                }
            )
            websites.append(website)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Created website: {name}"))
            else:
                self.stdout.write(f"  Using existing website: {name}")
        
        # Create configurations for each website
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING CONFIGURATIONS")
        self.stdout.write("="*70)
        for website in websites:
            self.create_website_configs(website)
        
        # Create staff users (superadmins, admins, editors, support) for each website
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING STAFF USERS")
        self.stdout.write("="*70)
        superadmins = []
        admins = []
        editors = []
        support_staff = []
        
        for website in websites:
            # Superadmin (1 per website)
            superadmin = self.ensure_user(
                email=f"superadmin@{website.slug}.com",
                username=f"superadmin_{website.slug}",
                role="superadmin",
                password="SuperAdmin123!",
                website=website,
                is_staff=True,
                is_superuser=True,
            )
            superadmins.append(superadmin)
            # Ensure SuperadminProfile exists
            try:
                from superadmin_management.models import SuperadminProfile
                SuperadminProfile.objects.get_or_create(user=superadmin)
            except Exception:
                pass
            
            # Admin (2 per website)
            for i in range(2):
                admin = self.ensure_user(
                    email=f"admin{i+1}@{website.slug}.com",
                    username=f"admin_{website.slug}_{i+1}",
                    role="admin",
                    password="Admin123!",
                    website=website,
                    is_staff=True,
                )
                admins.append(admin)
                # Ensure AdminProfile exists
                try:
                    from admin_management.models import AdminProfile
                    AdminProfile.objects.get_or_create(user=admin)
                except Exception:
                    pass
            
            # Editor (3 per website)
            for i in range(3):
                editor = self.ensure_user(
                    email=f"editor{i+1}@{website.slug}.com",
                    username=f"editor_{website.slug}_{i+1}",
                    role="editor",
                    password="Editor123!",
                    website=website,
                    is_staff=True,
                )
                editors.append(editor)
                # Ensure EditorProfile exists
                try:
                    from editor_management.models import EditorProfile
                    import random
                    registration_id = f"Editor #{random.randint(10000, 99999)}"
                    while EditorProfile.objects.filter(registration_id=registration_id).exists():
                        registration_id = f"Editor #{random.randint(10000, 99999)}"
                    EditorProfile.objects.get_or_create(
                        user=editor,
                        defaults={
                            'name': editor.username,
                            'registration_id': registration_id,
                            'email': editor.email,
                            'website': website,
                        }
                    )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ⚠ Could not create EditorProfile for {editor.username}: {e}"))
            
            # Support (3 per website)
            for i in range(3):
                support = self.ensure_user(
                    email=f"support{i+1}@{website.slug}.com",
                    username=f"support_{website.slug}_{i+1}",
                    role="support",
                    password="Support123!",
                    website=website,
                    is_staff=True,
                )
                support_staff.append(support)
                # Ensure SupportProfile exists
                try:
                    from support_management.models import SupportProfile
                    SupportProfile.objects.get_or_create(
                        user=support,
                        defaults={
                            'name': support.username,
                            'registration_id': f"Support #{support.id:05d}",
                            'email': support.email,
                            'website': website,
                        }
                    )
                except Exception:
                    pass
            
            self.stdout.write(self.style.SUCCESS(f"✓ Created staff for {website.name}: 1 superadmin, 2 admins, 3 editors, 3 support"))
        
        # Create 100 clients distributed across websites
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING 100 CLIENTS")
        self.stdout.write("="*70)
        clients = []
        clients_per_website = [34, 33, 33]  # Distribute 100 clients
        
        for idx, website in enumerate(websites):
            count = clients_per_website[idx]
            for i in range(count):
                client_num = sum(clients_per_website[:idx]) + i + 1
                client = self.ensure_user(
                    email=f"dryrun.client{client_num}@{website.slug}.com",
                    username=f"client_{website.slug}_{client_num}",
                    role="client",
                    password="Client123!",
                    website=website,
                )
                # Wallet will be created automatically via signals if needed
                # But ensure it exists for dry run
                try:
                    Wallet.objects.get_or_create(
                        user=client,
                        website=website,
                        defaults={'balance': Decimal('0.00')}
                    )
                except Exception:
                    pass  # Wallet creation may fail, continue anyway
                clients.append(client)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {count} clients for {website.name}"))
        
        # Create writers for each website (10 per website)
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING WRITERS")
        self.stdout.write("="*70)
        all_writers = []
        for website in websites:
            website_writers = []
            for i in range(10):
                writer_num = len(all_writers) + 1
                writer = self.ensure_user(
                    email=f"dryrun.writer{writer_num}@{website.slug}.com",
                    username=f"writer_{website.slug}_{writer_num}",
                    role="writer",
                    password="Writer123!",
                    website=website,
                )
                # Manually create WriterProfile if it doesn't exist (signal is disabled)
                try:
                    from writer_management.models.profile import WriterProfile
                    from wallet.models import Wallet
                    if not hasattr(writer, 'writer_profile'):
                        wallet, _ = Wallet.objects.get_or_create(
                            user=writer,
                            website=website,
                            defaults={'balance': Decimal('0.00')}
                        )
                        import random
                        registration_id = f"Writer #{random.randint(10000, 99999)}"
                        while WriterProfile.objects.filter(registration_id=registration_id).exists():
                            registration_id = f"Writer #{random.randint(10000, 99999)}"
                        WriterProfile.objects.get_or_create(
                            user=writer,
                            website=website,
                            defaults={
                                'registration_id': registration_id,
                                'wallet': wallet,
                            }
                        )
                except Exception as e:
                    # If WriterProfile creation fails (e.g., schema mismatch), continue
                    self.stdout.write(self.style.WARNING(f"  ⚠ Could not create WriterProfile for {writer.username}: {e}"))
                website_writers.append(writer)
                all_writers.append(writer)
            self.stdout.write(self.style.SUCCESS(f"✓ Created 10 writers for {website.name}"))
        
        # Get configuration objects for each website
        self.stdout.write("\n" + "="*70)
        self.stdout.write("CREATING ORDERS")
        self.stdout.write("="*70)
        
        # Temporarily disable price recalculation
        original_disable_pricing = getattr(settings, "DISABLE_PRICE_RECALC_DURING_TESTS", False)
        settings.DISABLE_PRICE_RECALC_DURING_TESTS = True
        
        try:
            created_orders = []
            order_counter = 1
            
            # Create orders for each client
            for client in clients:
                website = client.website
                
                # Get configs for this website
                paper_type = PaperType.objects.filter(website=website).first()
                academic_level = AcademicLevel.objects.filter(website=website).first()
                formatting_style = FormattingandCitationStyle.objects.filter(website=website).first()
                subject = Subject.objects.filter(website=website).first()
                type_of_work = TypeOfWork.objects.filter(website=website).first()
                english_type = EnglishType.objects.filter(website=website).first()
                writer_deadline_cfg = WriterDeadlineConfig.objects.filter(website=website).first()
                
                if not all([paper_type, academic_level, formatting_style, subject, type_of_work, english_type]):
                    self.stdout.write(self.style.WARNING(f"  ⚠ Skipping client {client.id} - missing configs"))
                    continue
                
                # Create 2-5 orders per client for more comprehensive testing
                num_orders = randint(2, 5)
                for order_idx in range(num_orders):
                    # More diverse status distribution for end-to-end testing
                    status_weights = {
                        # Initial states
                        OrderStatus.CREATED.value: 3,
                        OrderStatus.PENDING.value: 3,
                        OrderStatus.UNPAID.value: 4,
                        # Payment and assignment states
                        OrderStatus.AVAILABLE.value: 5,
                        OrderStatus.ASSIGNED.value: 8,
                        # Active work states
                        OrderStatus.IN_PROGRESS.value: 12,
                        OrderStatus.ON_HOLD.value: 2,
                        OrderStatus.REASSIGNED.value: 2,
                        # Submission and review states
                        OrderStatus.SUBMITTED.value: 8,
                        OrderStatus.UNDER_REVIEW.value: 3,
                        OrderStatus.REVIEWED.value: 3,
                        OrderStatus.RATED.value: 2,
                        OrderStatus.APPROVED.value: 2,
                        # Revision states
                        OrderStatus.REVISION_REQUESTED.value: 3,
                        OrderStatus.ON_REVISION.value: 2,
                        OrderStatus.REVISED.value: 2,
                        # Editing states
                        OrderStatus.UNDER_EDITING.value: 4,
                        # Final states
                        OrderStatus.COMPLETED.value: 15,
                        OrderStatus.CLOSED.value: 8,
                        OrderStatus.CANCELLED.value: 3,
                        OrderStatus.REFUNDED.value: 2,
                        OrderStatus.DISPUTED.value: 2,
                    }
                    
                    # Weighted random selection
                    statuses = []
                    for status, weight in status_weights.items():
                        statuses.extend([status] * weight)
                    status = choice(statuses)
                    
                    # Determine if order should have writer assigned
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
                        OrderStatus.COMPLETED.value,
                        OrderStatus.CLOSED.value,
                        OrderStatus.DISPUTED.value,
                    ]:
                        # Assign a writer from the same website
                        website_writers = [w for w in all_writers if w.website_id == website.id]
                        if website_writers:
                            assigned_writer = choice(website_writers)
                    
                    # Determine payment status
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
                        OrderStatus.COMPLETED.value,
                        OrderStatus.CLOSED.value,
                        OrderStatus.DISPUTED.value,
                    ]
                    
                    # Set deadlines
                    days_offset = randint(-30, 30)
                    client_deadline = timezone.now() + timedelta(days=days_offset)
                    writer_deadline = None
                    if assigned_writer and writer_deadline_cfg:
                        writer_deadline = client_deadline - timedelta(days=1)
                    
                    # Create order
                    order = Order.objects.create(
                        website=website,
                        client=client,
                        assigned_writer=assigned_writer,
                        topic=f"Dry Run Order #{order_counter} - {status.replace('_', ' ').title()}",
                        paper_type=paper_type,
                        academic_level=academic_level,
                        formatting_style=formatting_style,
                        subject=subject,
                        type_of_work=type_of_work,
                        english_type=english_type,
                        number_of_pages=randint(5, 20),
                        number_of_slides=randint(0, 10),
                        number_of_refereces=randint(3, 15),
                        spacing=choice([SpacingOptions.SINGLE.value, SpacingOptions.DOUBLE.value]),
                        status=status,
                        client_deadline=client_deadline,
                        writer_deadline=writer_deadline,
                        writer_deadline_percentage=writer_deadline_cfg,
                        total_price=Decimal(str(randint(50, 500))),
                        writer_compensation=Decimal(str(randint(30, 300))),
                        is_paid=is_paid,
                        order_instructions=f"This is a dry run order with status '{status}'. Created for system testing.",
                    )
                    
                    # Set additional fields based on status
                    update_fields = []
                    if status == OrderStatus.COMPLETED.value and assigned_writer:
                        order.completed_by = assigned_writer
                        order.submitted_at = timezone.now() - timedelta(days=randint(1, 7))
                        update_fields.extend(['completed_by', 'submitted_at'])
                    
                    if status == OrderStatus.SUBMITTED.value and assigned_writer:
                        order.submitted_at = timezone.now() - timedelta(days=randint(0, 3))
                        update_fields.append('submitted_at')
                    
                    if status in [OrderStatus.REVISION_REQUESTED.value, OrderStatus.ON_REVISION.value, OrderStatus.REVISED.value]:
                        # Add some revision context
                        order.order_instructions += f"\n[Revision Status: {status}]"
                        update_fields.append('order_instructions')
                    
                    if status == OrderStatus.DISPUTED.value:
                        # Add dispute context
                        order.order_instructions += "\n[Dispute: Client requested revision or refund]"
                        update_fields.append('order_instructions')
                    
                    if update_fields:
                        order.save(update_fields=update_fields)
                    
                    created_orders.append(order)
                    order_counter += 1
                    
                    if order_counter % 20 == 0:
                        self.stdout.write(f"  Created {order_counter} orders...")
            
        finally:
            settings.DISABLE_PRICE_RECALC_DURING_TESTS = original_disable_pricing
        
        # Ensure sample writer payments exist for the main dry run writer
        sample_writer = User.objects.filter(email="dryrun.writer1@academic-pro.com").first()
        if sample_writer:
            self.create_sample_writer_payments(sample_writer)
        else:
            self.stdout.write(self.style.WARNING("  ⚠ Could not locate dryrun.writer1@academic-pro.com to seed writer payments."))
        
        # Summary
        self.stdout.write("\n" + "="*70)
        self.stdout.write("SUMMARY")
        self.stdout.write("="*70)
        self.stdout.write(f"✓ Websites: {len(websites)}")
        self.stdout.write(f"✓ Superadmins: {len(superadmins)}")
        self.stdout.write(f"✓ Admins: {len(admins)}")
        self.stdout.write(f"✓ Editors: {len(editors)}")
        self.stdout.write(f"✓ Support Staff: {len(support_staff)}")
        self.stdout.write(f"✓ Clients: {len(clients)}")
        self.stdout.write(f"✓ Writers: {len(all_writers)}")
        self.stdout.write(f"✓ Orders: {len(created_orders)}")
        
        # Status distribution
        from django.db.models import Count
        status_summary = Order.objects.filter(
            topic__startswith="Dry Run Order"
        ).values('status').annotate(count=Count('id')).order_by('status')
        
        self.stdout.write("\nOrder Status Distribution:")
        for item in status_summary:
            self.stdout.write(f"  {item['status']}: {item['count']} orders")
        
        # Website distribution
        website_summary = Order.objects.filter(
            topic__startswith="Dry Run Order"
        ).values('website__name').annotate(count=Count('id')).order_by('website__name')
        
        self.stdout.write("\nOrders by Website:")
        for item in website_summary:
            self.stdout.write(f"  {item['website__name']}: {item['count']} orders")
        
        self.stdout.write("\n" + self.style.SUCCESS("✅ Dry run system seeded successfully!"))
        self.stdout.write("="*70 + "\n")
        
        # Print login credentials
        self.stdout.write("\n" + "="*70)
        self.stdout.write("LOGIN CREDENTIALS")
        self.stdout.write("="*70)
        
        self.stdout.write("\nSuperadmins:")
        for website, superadmin in zip(websites, superadmins):
            self.stdout.write(f"  {website.name}: {superadmin.email} / SuperAdmin123!")
        
        self.stdout.write("\nAdmins (sample):")
        for admin in admins[:3]:
            self.stdout.write(f"  {admin.email} / Admin123!")
        
        self.stdout.write("\nEditors (sample):")
        for editor in editors[:3]:
            self.stdout.write(f"  {editor.email} / Editor123!")
        
        self.stdout.write("\nSupport Staff (sample):")
        for support in support_staff[:3]:
            self.stdout.write(f"  {support.email} / Support123!")
        
        self.stdout.write("\nSample Clients:")
        for client in clients[:5]:
            self.stdout.write(f"  {client.email} / Client123!")
        
        self.stdout.write("\nSample Writers:")
        for writer in all_writers[:5]:
            self.stdout.write(f"  {writer.email} / Writer123!")
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write("NOTE: All passwords follow the pattern: [Role]123!")
        self.stdout.write("="*70 + "\n")

