from decimal import Decimal
from datetime import timedelta
from uuid import uuid4
from calendar import monthrange

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
from wallet.models import Wallet
from websites.models import Website
from writer_management.models.profile import WriterProfile
from writer_wallet.models import (
    WriterWallet,
    PaymentSchedule,
    ScheduledWriterPayment,
    PaymentOrderRecord,
)


DEFAULT_COUNTRY = "Unknown"
DEFAULT_TIMEZONE = "UTC"


class Command(BaseCommand):
    help = "Seed demo writer payment data so the UI can show realistic tables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--writers",
            type=int,
            default=2,
            help="Number of demo writers to create",
        )
        parser.add_argument(
            "--periods",
            type=int,
            default=2,
            help="Number of payment periods (per type) to create",
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
        writers_count = max(1, options["writers"])
        periods_count = max(1, options["periods"])

        User = get_user_model()

        # Seed for all active websites, or create demo website if none exist
        websites = Website.objects.filter(is_active=True)
        if not websites.exists():
            website, _ = Website.objects.get_or_create(
                domain="https://demo.writingsystem.test",
                defaults={"name": "Demo Writing System", "contact_email": "support@demo.test", "is_active": True},
            )
            websites = Website.objects.filter(id=website.id)

        # Process each website
        total_schedules = 0
        total_payments = 0
        for website in websites:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"Processing website: {website.name} (ID: {website.id})")
            self.stdout.write(f"{'='*60}")

            admin_user = self.ensure_user(
                email=f"admin.demo@{website.id}.example.com",
                username=f"admin_demo_{website.id}",
                role="superadmin",
                password="AdminDemo123!",
                website=website,
                is_staff=True,
                is_superuser=True,
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.role = "superadmin"
            admin_user.save(update_fields=["is_staff", "is_superuser", "role", "website", "detected_country", "detected_timezone"])

            client_user = self.ensure_user(
                email=f"client.demo@{website.id}.example.com",
                username=f"client_demo_{website.id}",
                role="client",
                password="ClientDemo123!",
                website=website,
            )

            paper_type = PaperType.objects.filter(name="Essay", website=website).first()
            if paper_type is None:
                paper_type = PaperType.objects.create(website=website, name="Essay")

            academic_level, _ = AcademicLevel.objects.get_or_create(website=website, name="University")
            formatting_style = FormattingandCitationStyle.objects.filter(name="APA", website=website).first()
            if formatting_style is None:
                formatting_style = FormattingandCitationStyle.objects.create(website=website, name="APA")

            subject = Subject.objects.filter(name="Business", website=website).first()
            if subject is None:
                subject = Subject.objects.create(website=website, name="Business")

            type_of_work = TypeOfWork.objects.filter(name="Writing", website=website).first()
            if type_of_work is None:
                type_of_work = TypeOfWork.objects.create(website=website, name="Writing")

            english_type = EnglishType.objects.filter(name="US English", website=website).first()
            if english_type is None:
                english_type = EnglishType.objects.create(website=website, name="US English", code="US")

            writer_deadline_cfg, _ = WriterDeadlineConfig.objects.get_or_create(website=website, writer_deadline_percentage=80)

            demo_writers = []
            self.stdout.write(f"  Creating {writers_count} writers for {website.name}...")
            for index in range(1, writers_count + 1):
                email = f"writer{index}.demo@{website.id}.example.com"
                username = f"writer_demo_{website.id}_{index}"
                self.stdout.write(f"    Creating writer {index}/{writers_count}: {username}")
                writer_user = self.ensure_user(
                    email=email,
                    username=username,
                    role="writer",
                    password="WriterDemo123!",
                    website=website,
                )
                self.stdout.write(f"      ensure_user returned: user_id={writer_user.id if writer_user else 'None'}, username={writer_user.username if writer_user else 'None'}")

                wallet, _ = Wallet.objects.get_or_create(
                    user=writer_user,
                    defaults={"website": website, "balance": Decimal("0.00")},
                )
                if wallet.website_id is None:
                    wallet.website = website
                    wallet.save(update_fields=["website"])

                # Make registration_id unique by including website ID
                registration_id = f"WR-{website.id}-{index:03d}"
                # Alternate between bi-weekly and monthly payment schedules
                payment_schedule = "bi-weekly" if index % 2 == 1 else "monthly"
                payment_date_pref = "1,15" if payment_schedule == "bi-weekly" else "1"
                
                writer_profile, created = WriterProfile.objects.get_or_create(
                    user=writer_user,
                    defaults={
                        "website": website,
                        "wallet": wallet,
                        "registration_id": registration_id,
                        "pen_name": f"Writer Demo {index}",
                        "timezone": "UTC",
                        "payment_schedule": payment_schedule,
                        "payment_date_preference": payment_date_pref,
                    },
                )
                self.stdout.write(f"      WriterProfile: created={created}, profile_id={writer_profile.id if writer_profile else 'None'}")
                if created is False:
                    updates = {}
                    if writer_profile.wallet_id != wallet.id:
                        writer_profile.wallet = wallet
                        updates["wallet"] = wallet
                    # Only update registration_id if it's not set or if it doesn't match the expected pattern
                    if not writer_profile.registration_id or not writer_profile.registration_id.startswith(f"WR-{website.id}-"):
                        # Check if the new registration_id already exists
                        if not WriterProfile.objects.filter(registration_id=registration_id).exclude(id=writer_profile.id).exists():
                            writer_profile.registration_id = registration_id
                            updates["registration_id"] = registration_id
                    # Update payment preferences
                    writer_profile.payment_schedule = payment_schedule
                    writer_profile.payment_date_preference = payment_date_pref
                    updates["payment_schedule"] = payment_schedule
                    updates["payment_date_preference"] = payment_date_pref
                    if updates:
                        writer_profile.save(update_fields=list(updates.keys()))

                writer_wallet, _ = WriterWallet.objects.get_or_create(
                    writer=writer_user,
                    defaults={
                        "website": website,
                        "balance": Decimal("0.00"),
                        "total_earnings": Decimal("0.00"),
                    },
                )
                if writer_wallet.website_id is None:
                    writer_wallet.website = website
                    writer_wallet.save(update_fields=["website"])

                # Add writer to demo_writers list
                demo_writers.append({
                    "user": writer_user,
                    "profile": writer_profile,
                    "wallet": writer_wallet,
                })
                self.stdout.write(f"      ✓ Added writer {index} to demo_writers (user_id: {writer_user.id}, profile_id: {writer_profile.id if writer_profile else 'None'})")

        # Debug: Log how many writers we have
        self.stdout.write(f"  Created {len(demo_writers)} writers for {website.name}")

        # Store orders per writer
        writer_orders = {}
        spacing_choice = SpacingOptions.DOUBLE.value
        original_disable_pricing = getattr(settings, "DISABLE_PRICE_RECALC_DURING_TESTS", False)
        settings.DISABLE_PRICE_RECALC_DURING_TESTS = True
        try:
            for writer in demo_writers:
                writer_user = writer["user"]
                writer_orders[writer_user.id] = []
                # Create more orders to ensure we have enough for all payment periods
                # Create orders for each payment period plus some extras
                num_orders_per_writer = (periods_count * 2) + 10  # Enough for bi-weekly and monthly periods
                for order_index in range(1, num_orders_per_writer + 1):
                    order_topic = f"Sample Order {writer_user.username}-{order_index}"
                    order_defaults = {
                        "paper_type": paper_type,
                        "academic_level": academic_level,
                        "formatting_style": formatting_style,
                        "subject": subject,
                        "type_of_work": type_of_work,
                        "english_type": english_type,
                        "number_of_pages": 5 + order_index,
                        "number_of_slides": 0,
                        "number_of_refereces": 3,
                        "spacing": spacing_choice,
                        "status": OrderStatus.COMPLETED.value,
                        "client_deadline": timezone.now() - timedelta(days=7 - order_index),
                        "writer_deadline": timezone.now() - timedelta(days=8 - order_index),
                        "writer_deadline_percentage": writer_deadline_cfg,
                        "total_price": Decimal("200.00") + Decimal(order_index) * 10,
                        "writer_compensation": Decimal("120.00") + Decimal(order_index) * 5,
                        "is_paid": True,
                        "order_instructions": "Complete the assignment with the provided outline.",
                        "completed_by": writer_user,
                        "submitted_at": timezone.now() - timedelta(days=6 - order_index),
                    }
                    order = Order.objects.filter(
                        website=website,
                        client=client_user,
                        assigned_writer=writer_user,
                        topic=order_topic,
                    ).first()
                    if order is None:
                        order = Order.objects.create(
                            website=website,
                            client=client_user,
                            assigned_writer=writer_user,
                            topic=order_topic,
                            **order_defaults,
                        )
                    else:
                        for field, value in order_defaults.items():
                            setattr(order, field, value)
                        order.save()
                    writer_orders[writer_user.id].append(order)
        finally:
            settings.DISABLE_PRICE_RECALC_DURING_TESTS = original_disable_pricing

        # Debug: Log writer_orders summary
        total_orders_stored = sum(len(orders) for orders in writer_orders.values())
        writer_ids = list(writer_orders.keys())
        self.stdout.write(f"  Stored {total_orders_stored} orders for {len(writer_orders)} writers (IDs: {writer_ids[:5]})")

        # Delete existing payment data for this website
        PaymentSchedule.objects.filter(website=website).delete()
        # PaymentOrderRecord will be deleted via CASCADE when ScheduledWriterPayment is deleted
        ScheduledWriterPayment.objects.filter(website=website).delete()

        payment_periods = []
        today = timezone.now().date()
        
        # Create bi-weekly schedules: 1st and 15th of each month
        # Generate for 3 months back, current month, and 1 month forward
        biweekly_count = 0
        for months_offset in range(-3, 2):  # 3 months back to 1 month forward
            # Calculate target month
            target_month = today.month + months_offset
            target_year = today.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            while target_month > 12:
                target_month -= 12
                target_year += 1
            
            # Get last day of month to ensure day 15 is valid
            last_day = monthrange(target_year, target_month)[1]
            
            # Create payment schedule for 1st of month
            scheduled_date_1st = today.replace(year=target_year, month=target_month, day=1)
            is_past_1st = scheduled_date_1st < today
            
            biweekly_schedule_1st = PaymentSchedule.objects.create(
                website=website,
                schedule_type="Bi-Weekly",
                scheduled_date=scheduled_date_1st,
                processed_by=admin_user if is_past_1st else None,
                completed=is_past_1st,
                reference_code=f"BW{uuid4().hex[:8]}",
            )
            payment_periods.append(biweekly_schedule_1st)
            biweekly_count += 1
            
            # Create payment schedule for 15th of month
            scheduled_date_15th = today.replace(year=target_year, month=target_month, day=min(15, last_day))
            is_past_15th = scheduled_date_15th < today
            
            biweekly_schedule_15th = PaymentSchedule.objects.create(
                website=website,
                schedule_type="Bi-Weekly",
                scheduled_date=scheduled_date_15th,
                processed_by=admin_user if is_past_15th else None,
                completed=is_past_15th,
                reference_code=f"BW{uuid4().hex[:8]}",
            )
            payment_periods.append(biweekly_schedule_15th)
            biweekly_count += 1
        
        # Create monthly schedules: 1st of each month
        # Generate for 3 months back, current month, and 1 month forward
        monthly_count = 0
        for months_offset in range(-3, 2):  # 3 months back to 1 month forward
            # Calculate target month
            target_month = today.month + months_offset
            target_year = today.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            while target_month > 12:
                target_month -= 12
                target_year += 1
            
            # Create payment schedule for 1st of month
            scheduled_date = today.replace(year=target_year, month=target_month, day=1)
            is_past = scheduled_date < today
            
            monthly_schedule = PaymentSchedule.objects.create(
                website=website,
                schedule_type="Monthly",
                scheduled_date=scheduled_date,
                processed_by=admin_user if is_past else None,
                completed=is_past,
                reference_code=f"MO{uuid4().hex[:8]}",
            )
            payment_periods.append(monthly_schedule)
            monthly_count += 1

        payment_records_created = 0
        import random
        
        for schedule in payment_periods:
            for writer in demo_writers:
                writer_profile = writer["profile"]
                writer_user = writer["user"]
                # Create payments for all writers matching their schedule preference
                # For simplicity, create payments for all writers - can be filtered later if needed
                # The payment amounts and orders will be properly calculated below
                
                # Get orders for this writer - ensure we have the orders
                writer_order_list = writer_orders.get(writer_user.id, [])
                
                # Always link 1-2 orders per payment if orders are available
                # Allow orders to be reused across payments (realistic scenario)
                selected_orders = []
                if writer_order_list and len(writer_order_list) > 0:
                    # Link 1-2 orders per payment
                    num_orders = min(random.randint(1, 2), len(writer_order_list))
                    selected_orders = random.sample(writer_order_list, num_orders)
                # Note: If writer_order_list is empty, selected_orders will be empty
                # and payment will be created with random amount but no linked orders
                
                # Calculate amount from selected orders
                amount = Decimal("0.00")
                for order in selected_orders:
                    amount += order.writer_compensation or Decimal("0.00")
                
                # If no orders available, use a random base amount
                if amount == Decimal("0.00"):
                    amount = Decimal("150.00") + Decimal(str(random.randint(0, 65))) * Decimal("10.00")
                
                # Add some random tips (20% chance)
                tips_amount = Decimal("0.00")
                if random.random() < 0.2:
                    tips_amount = Decimal(str(random.randint(5, 50)))
                    amount += tips_amount
                
                # Add some random fines (10% chance)
                fines_amount = Decimal("0.00")
                if random.random() < 0.1:
                    fines_amount = Decimal(str(random.randint(10, 100)))
                    amount = max(Decimal("0.00"), amount - fines_amount)
                
                # Create payment with appropriate status
                payment = ScheduledWriterPayment.objects.create(
                    website=website,
                    batch=schedule,
                    writer_wallet=writer["wallet"],
                    amount=amount,
                    status="Paid" if schedule.completed else "Pending",
                    payment_date=timezone.now() - timedelta(days=random.randint(1, 30)) if schedule.completed else None,
                    reference_code=f"PW{uuid4().hex[:8]}",
                )

                # Link orders to payment - ensure we always link if orders are available
                orders_linked = 0
                if selected_orders:
                    for order in selected_orders:
                        try:
                            # Check if this order is already linked to this payment
                            existing = PaymentOrderRecord.objects.filter(
                                payment=payment,
                                order=order
                            ).first()
                            if not existing:
                                record = PaymentOrderRecord.objects.create(
                                    website=website,
                                    payment=payment,
                                    order=order,
                                    amount_paid=order.writer_compensation or Decimal("100.00"),
                                )
                                orders_linked += 1
                        except Exception as e:
                            # Log error but continue
                            self.stdout.write(self.style.WARNING(
                                f"Warning: Could not link order {order.id} to payment {payment.id}: {e}"
                            ))
                elif writer_order_list:
                    # Debug: log if we have orders but didn't select any
                    self.stdout.write(self.style.WARNING(
                        f"Warning: Writer {writer_user.username} has {len(writer_order_list)} orders but none were selected for payment {payment.id}"
                    ))

                payment_records_created += 1
            
            total_schedules += len(payment_periods)
            total_payments += payment_records_created
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {len(payment_periods)} payment schedules and "
                    f"{payment_records_created} scheduled payments for {website.name}"
                )
            )

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("Seeded demo writer payment data for all websites."))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(
            f"""\nSummary:
  - Total Payment Schedules: {total_schedules}
  - Total Scheduled Payments: {total_payments}
  - Websites Processed: {websites.count()}

Navigate to /admin/payments/writer-payments or /admin/payments/batched in the frontend as an admin to view the tables."""
        )
