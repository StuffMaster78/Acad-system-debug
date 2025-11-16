from decimal import Decimal
from datetime import timedelta
from uuid import uuid4

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

        website, _ = Website.objects.get_or_create(
            domain="https://demo.writingsystem.test",
            defaults={"name": "Demo Writing System", "contact_email": "support@demo.test"},
        )

        admin_user = self.ensure_user(
            email="admin.demo@example.com",
            username="admin_demo",
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
            email="client.demo@example.com",
            username="client_demo",
            role="client",
            password="ClientDemo123!",
            website=website,
        )

        paper_type = PaperType.objects.filter(name="Essay").first()
        if paper_type is None:
            paper_type = PaperType.objects.create(website=website, name="Essay")

        academic_level, _ = AcademicLevel.objects.get_or_create(website=website, name="University")
        formatting_style = FormattingandCitationStyle.objects.filter(name="APA").first()
        if formatting_style is None:
            formatting_style = FormattingandCitationStyle.objects.create(website=website, name="APA")

        subject = Subject.objects.filter(name="Business").first()
        if subject is None:
            subject = Subject.objects.create(website=website, name="Business")

        type_of_work = TypeOfWork.objects.filter(name="Writing").first()
        if type_of_work is None:
            type_of_work = TypeOfWork.objects.create(website=website, name="Writing")

        english_type = EnglishType.objects.filter(name="US English").first()
        if english_type is None:
            english_type = EnglishType.objects.create(website=website, name="US English", code="US")

        writer_deadline_cfg, _ = WriterDeadlineConfig.objects.get_or_create(website=website, writer_deadline_percentage=80)

        demo_writers = []
        for index in range(1, writers_count + 1):
            email = f"writer{index}.demo@example.com"
            username = f"writer_demo_{index}"
            writer_user = self.ensure_user(
                email=email,
                username=username,
                role="writer",
                password="WriterDemo123!",
                website=website,
            )

            wallet, _ = Wallet.objects.get_or_create(
                user=writer_user,
                defaults={"website": website, "balance": Decimal("0.00")},
            )
            if wallet.website_id is None:
                wallet.website = website
                wallet.save(update_fields=["website"])

            registration_id = f"WR-{index:03d}"
            writer_profile, created = WriterProfile.objects.get_or_create(
                user=writer_user,
                defaults={
                    "website": website,
                    "wallet": wallet,
                    "registration_id": registration_id,
                    "pen_name": f"Writer Demo {index}",
                    "timezone": "UTC",
                },
            )
            if created is False:
                updates = {}
                if writer_profile.wallet_id != wallet.id:
                    writer_profile.wallet = wallet
                    updates["wallet"] = wallet
                if not writer_profile.registration_id:
                    writer_profile.registration_id = registration_id
                    updates["registration_id"] = registration_id
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

            demo_writers.append({
                "user": writer_user,
                "profile": writer_profile,
                "wallet": writer_wallet,
            })

        created_orders = []
        spacing_choice = SpacingOptions.DOUBLE.value
        original_disable_pricing = getattr(settings, "DISABLE_PRICE_RECALC_DURING_TESTS", False)
        settings.DISABLE_PRICE_RECALC_DURING_TESTS = True
        try:
            for writer in demo_writers:
                writer_user = writer["user"]
                for order_index in range(1, periods_count + 2):
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
                    created_orders.append(order)
        finally:
            settings.DISABLE_PRICE_RECALC_DURING_TESTS = original_disable_pricing

        PaymentSchedule.objects.filter(website=website).delete()
        ScheduledWriterPayment.objects.filter(website=website).delete()

        payment_periods = []
        today = timezone.now().date()
        for offset in range(periods_count):
            scheduled_date = today - timedelta(days=14 * offset)
            biweekly_schedule = PaymentSchedule.objects.create(
                website=website,
                schedule_type="Bi-Weekly",
                scheduled_date=scheduled_date,
                processed_by=admin_user,
                completed=offset == 0,
                reference_code=f"PB{uuid4().hex[:8]}",
            )
            payment_periods.append(biweekly_schedule)

            month_start = (today.replace(day=1) - timedelta(days=30 * offset))
            monthly_schedule = PaymentSchedule.objects.create(
                website=website,
                schedule_type="Monthly",
                scheduled_date=month_start,
                processed_by=admin_user,
                completed=offset == 0,
                reference_code=f"PB{uuid4().hex[:8]}",
            )
            payment_periods.append(monthly_schedule)

        payment_records_created = 0
        for schedule in payment_periods:
            for writer in demo_writers:
                amount = Decimal("250.00") + Decimal(payment_records_created % 3) * Decimal("25.00")
                payment = ScheduledWriterPayment.objects.create(
                    website=website,
                    batch=schedule,
                    writer_wallet=writer["wallet"],
                    amount=amount,
                    status="Paid" if schedule.completed else "Pending",
                    payment_date=timezone.now() - timedelta(days=1) if schedule.completed else None,
                    reference_code=f"PW{uuid4().hex[:8]}",
                )

                for order in created_orders[:2]:
                    PaymentOrderRecord.objects.create(
                        website=website,
                        payment=payment,
                        order=order,
                        amount_paid=order.writer_compensation or Decimal("100.00"),
                    )

                payment_records_created += 1

        self.stdout.write(self.style.SUCCESS("Seeded demo writer payment data."))
        self.stdout.write(
            """Created/updated demo users:
  Admin: admin.demo@example.com / AdminDemo123!
  Client: client.demo@example.com / ClientDemo123!
  Writers: writerX.demo@example.com / WriterDemo123! (X = 1..n)
Navigate to /admin/writer-payments or /admin/batched-writer-payments in the frontend as an admin to view the tables."""
        )
