"""
python manage.py seed_dev_data

Seeds the minimum viable dev environment so the platform works
end-to-end on localhost without manual DB setup.

What it creates (idempotent — safe to re-run):
  1. Superadmin user            admin@dev.local / admin1234
  2. Website                    localhost  (so request.website is set)
  3. WebsiteBranding            branding + payment disclosure
  4. PortalDefinitions          internal_admin / writer_portal / client_portal
                                all pointing to localhost so request.portal
                                is resolved correctly in dev
  5. WriterLevels × 4           Entry → Standard → Senior → Expert
     WriterLevelSettings        pay rates, capacity, urgency
  6. WriterConfig               site-level writer assignment settings
  7. TipPolicy                  default split (writer 90 / platform 10)
  8. LoyaltyTiers × 4          Bronze → Silver → Gold → Platinum
  9. ClassOrder balance backfill  refreshes balance_amount on any order
                                where the stored value is stale (e.g. from
                                seeder scripts that bypass the payment flow)

Run order matters — Website must exist before anything website-scoped.
"""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seed minimum dev environment — idempotent, safe to re-run."

    # ----------------------------------------------------------------
    # Data catalogue
    # ----------------------------------------------------------------

    WEBSITE = {
        "name": "Dev Site",
        "domain": "localhost",
        "slug": "dev-site",
        "is_active": True,
        "contact_email": "support@dev.local",
    }

    BRANDING = {
        "brand_name": "WritePro Dev",
        "tagline": "Expert writing assistance across every subject.",
        "primary_color": "#4f46e5",
        "secondary_color": "#0f172a",
        "accent_color": "#14b8a6",
        "homepage_headline": "Academic writing services",
        "homepage_subheadline": "Professional assistance from verified writers.",
        "payment_processor_name": "DevPay",
        "payment_statement_descriptor": "DEVPAY PAYMENTS",
        "is_public": True,
    }

    PORTALS = [
        {"code": "internal_admin", "name": "Admin Portal",  "domain": "localhost"},
        {"code": "writer_portal",  "name": "Writer Portal", "domain": "localhost"},
        {"code": "client_portal",  "name": "Client Portal", "domain": "localhost"},
    ]

    WRITER_LEVELS = [
        {
            "name": "Entry",
            "description": "New writers completing onboarding.",
            "display_order": 3,
            "is_default": True,
            "settings": {
                "base_pay_per_page":  Decimal("2.00"),
                "base_pay_per_slide": Decimal("1.50"),
                "base_pay_per_chart": Decimal("1.00"),
                "tip_percentage":     Decimal("90.00"),
                "max_active_orders":  3,
                "max_manual_takes":   2,
                "max_pending_assignments": 2,
                "urgent_time_threshold_hours": 6,
                "urgent_order_surcharge":  Decimal("1.00"),
                "urgent_multiplier":       Decimal("1.10"),
                "min_completed_orders": 0,
                "min_rating": Decimal("0.00"),
            },
        },
        {
            "name": "Standard",
            "description": "Established writers with a track record.",
            "display_order": 2,
            "is_default": False,
            "settings": {
                "base_pay_per_page":  Decimal("3.50"),
                "base_pay_per_slide": Decimal("2.50"),
                "base_pay_per_chart": Decimal("2.00"),
                "tip_percentage":     Decimal("90.00"),
                "max_active_orders":  6,
                "max_manual_takes":   4,
                "max_pending_assignments": 4,
                "urgent_time_threshold_hours": 6,
                "urgent_order_surcharge":  Decimal("2.00"),
                "urgent_multiplier":       Decimal("1.15"),
                "min_completed_orders": 10,
                "min_rating": Decimal("7.00"),
            },
        },
        {
            "name": "Senior",
            "description": "High-performing writers with consistent quality.",
            "display_order": 1,
            "is_default": False,
            "settings": {
                "base_pay_per_page":  Decimal("5.00"),
                "base_pay_per_slide": Decimal("3.50"),
                "base_pay_per_chart": Decimal("3.00"),
                "tip_percentage":     Decimal("92.00"),
                "max_active_orders":  10,
                "max_manual_takes":   6,
                "max_pending_assignments": 6,
                "urgent_time_threshold_hours": 4,
                "urgent_order_surcharge":  Decimal("3.00"),
                "urgent_multiplier":       Decimal("1.20"),
                "min_completed_orders": 50,
                "min_rating": Decimal("8.00"),
            },
        },
        {
            "name": "Expert",
            "description": "Elite writers — top tier.",
            "display_order": 0,
            "is_default": False,
            "settings": {
                "base_pay_per_page":  Decimal("7.00"),
                "base_pay_per_slide": Decimal("5.00"),
                "base_pay_per_chart": Decimal("4.00"),
                "tip_percentage":     Decimal("95.00"),
                "max_active_orders":  15,
                "max_manual_takes":   10,
                "max_pending_assignments": 10,
                "urgent_time_threshold_hours": 3,
                "urgent_order_surcharge":  Decimal("5.00"),
                "urgent_multiplier":       Decimal("1.25"),
                "min_completed_orders": 150,
                "min_rating": Decimal("9.00"),
            },
        },
    ]

    LOYALTY_TIERS = [
        {"name": "Bronze",   "threshold": 0,    "discount_percentage": Decimal("0.00"),  "perks": "Access to the platform."},
        {"name": "Silver",   "threshold": 500,  "discount_percentage": Decimal("3.00"),  "perks": "3% discount on all orders."},
        {"name": "Gold",     "threshold": 1500, "discount_percentage": Decimal("7.00"),  "perks": "7% discount, priority support."},
        {"name": "Platinum", "threshold": 5000, "discount_percentage": Decimal("12.00"), "perks": "12% discount, dedicated support."},
    ]

    DEMO_WRITERS = [
        {
            "email": "writer1@dev.local",
            "username": "dev_writer1",
            "first_name": "Alice",
            "last_name": "Nkosi",
            "password": "writer1234",
            "pen_name": "A. Nkosi",
            "bio": "Experienced academic writer specialising in STEM and social sciences.",
            "years_of_experience": 5,
        },
        {
            "email": "writer2@dev.local",
            "username": "dev_writer2",
            "first_name": "Brian",
            "last_name": "Omondi",
            "password": "writer1234",
            "pen_name": "B. Omondi",
            "bio": "Business and finance writer with a background in MBA studies.",
            "years_of_experience": 8,
        },
        {
            "email": "writer3@dev.local",
            "username": "dev_writer3",
            "first_name": "Chloe",
            "last_name": "Waweru",
            "password": "writer1234",
            "pen_name": "C. Waweru",
            "bio": "Creative and academic writer with expertise in humanities.",
            "years_of_experience": 3,
        },
    ]

    DEMO_CLIENTS = [
        {
            "email": "client1@dev.local",
            "username": "dev_client1",
            "first_name": "David",
            "last_name": "Smith",
            "password": "client1234",
        },
        {
            "email": "client2@dev.local",
            "username": "dev_client2",
            "first_name": "Eva",
            "last_name": "Mwangi",
            "password": "client1234",
        },
        {
            "email": "client3@dev.local",
            "username": "dev_client3",
            "first_name": "Frank",
            "last_name": "Ochieng",
            "password": "client1234",
        },
    ]

    PAYMENT_REMINDER_CONFIGS = [
        {
            "name": "Early Reminder",
            "deadline_percentage": Decimal("30.00"),
            "message": "Just a heads-up — your order payment is still pending. Complete it before the deadline to avoid cancellation.",
            "email_subject": "Reminder: Your order payment is pending",
            "display_order": 0,
        },
        {
            "name": "Mid Reminder",
            "deadline_percentage": Decimal("60.00"),
            "message": "More than half your payment window has passed. Please complete your payment soon.",
            "email_subject": "Action required: Complete your order payment",
            "display_order": 1,
        },
        {
            "name": "Final Warning",
            "deadline_percentage": Decimal("90.00"),
            "message": "Your order payment is about to expire. Complete payment now to prevent cancellation.",
            "email_subject": "URGENT: Your order payment is expiring",
            "display_order": 2,
        },
    ]

    # Named test accounts — one per role, idempotent.
    # Passwords are set on first create only (never overwritten on re-run).
    TEST_ACCOUNTS = [
        # Personal superadmin — always has a known dev password
        {
            "email": "rickawino@gmail.com",
            "username": "rickawino",
            "first_name": "Erick",
            "last_name": "Awino",
            "role": "superadmin",
            "is_staff": True,
            "is_superuser": True,
            "password": "admin1234",
        },
        {
            "email": "admin@test.local",
            "username": "test_admin",
            "first_name": "Test",
            "last_name": "Admin",
            "role": "admin",
            "is_staff": True,
            "is_superuser": False,
            "password": "admin1234",
        },
        {
            "email": "editor@test.local",
            "username": "test_editor",
            "first_name": "Test",
            "last_name": "Editor",
            "role": "editor",
            "is_staff": False,
            "is_superuser": False,
            "password": "test1234",
        },
        {
            "email": "support@test.local",
            "username": "test_support",
            "first_name": "Test",
            "last_name": "Support",
            "role": "support",
            "is_staff": False,
            "is_superuser": False,
            "password": "test1234",
        },
        {
            "email": "writer@test.local",
            "username": "test_writer",
            "first_name": "Test",
            "last_name": "Writer",
            "role": "writer",
            "is_staff": False,
            "is_superuser": False,
            "password": "test1234",
        },
        {
            "email": "client@test.local",
            "username": "test_client",
            "first_name": "Test",
            "last_name": "Client",
            "role": "client",
            "is_staff": False,
            "is_superuser": False,
            "password": "test1234",
        },
    ]

    TIP_POLICY = {
        "name": "Default Policy",
        "slug": "default",
        "description": "Platform default: writers keep 90%, platform retains 10%.",
        "writer_percentage": Decimal("90.00"),
        "platform_percentage": Decimal("10.00"),
        "minimum_tip_amount": Decimal("1.00"),
        "risk_review_threshold": Decimal("500.00"),
        "allow_wallet_tips": True,
        "allow_external_tips": True,
        "require_manual_review": False,
        "maximum_tip_frequency_per_day": 10,
        "is_active": True,
    }

    # ----------------------------------------------------------------
    # Entry point
    # ----------------------------------------------------------------

    def handle(self, *args, **options):
        self.stdout.write("\n=== seed_dev_data ===\n")

        with transaction.atomic():
            website = self._seed_website()
            self._seed_branding(website)
            self._seed_portals()
            self._seed_superadmin(website)
            self._seed_writer_levels(website)
            self._seed_writer_config(website)
            self._seed_tip_policy()
            self._seed_loyalty_tiers(website)
            self._seed_demo_writers(website)
            self._seed_demo_clients(website)
            self._seed_payment_reminder_configs(website)
            self._seed_test_accounts(website)

        self._backfill_class_balances()

        self.stdout.write(self.style.SUCCESS("\nDone! Dev environment is ready.\n"))
        self.stdout.write("  Login:    http://localhost:8000/api/v1/auth/login/")
        self.stdout.write("  Email:    admin@dev.local")
        self.stdout.write("  Password: admin1234\n")

    # ----------------------------------------------------------------
    # Seeders
    # ----------------------------------------------------------------

    def _seed_website(self):
        from websites.models.websites import Website

        website, created = Website.objects.update_or_create(
            domain=self.WEBSITE["domain"],
            defaults=self.WEBSITE,
        )
        self._log("Website", website.name, created)
        return website

    def _seed_branding(self, website):
        from websites.models.website_branding import WebsiteBranding

        branding, created = WebsiteBranding.objects.update_or_create(
            website=website,
            defaults=self.BRANDING,
        )
        self._log("WebsiteBranding", branding.brand_name, created)

    def _seed_portals(self):
        from accounts.models.portal_definition import PortalDefinition

        for data in self.PORTALS:
            portal, created = PortalDefinition.objects.update_or_create(
                code=data["code"],
                defaults={"name": data["name"], "domain": data["domain"], "is_active": True},
            )
            self._log("PortalDefinition", portal.code, created)

    def _seed_superadmin(self, website):
        from accounts.models import AccountProfile
        from accounts.enums import AccountStatus

        email    = "admin@dev.local"
        username = "devadmin"

        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                "username": username,
                "first_name": "Dev",
                "last_name": "Admin",
                "role": "superadmin",
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password("admin1234")
            user.save(update_fields=["password"])

        AccountProfile.objects.get_or_create(
            user=user,
            website=website,
            defaults={
                "status": AccountStatus.ACTIVE,
                "is_primary": True,
            },
        )

        self._log("Superadmin", email, created)
        if not created:
            self.stdout.write("  (password unchanged — change manually if needed)")

    def _seed_writer_levels(self, website):
        from writer_management.models.writer_level import WriterLevel
        from writer_management.models.writer_level_settings import WriterLevelSettings

        for data in self.WRITER_LEVELS:
            settings_data = data.pop("settings")

            level, created = WriterLevel.objects.update_or_create(
                website=website,
                name=data["name"],
                defaults={**data},
            )
            self._log("WriterLevel", level.name, created)

            # Restore for idempotency
            data["settings"] = settings_data

            _, s_created = WriterLevelSettings.objects.update_or_create(
                writer_level=level,
                defaults=settings_data,
            )
            self._log("  WriterLevelSettings", level.name, s_created)

    def _seed_writer_config(self, website):
        from writer_management.models.configs import WriterConfig

        config, created = WriterConfig.objects.update_or_create(
            website=website,
            defaults={
                "takes_enabled": True,
                "max_requests_per_writer": 3,
                "max_takes_per_writer": 5,
            },
        )
        self._log("WriterConfig", f"website={website.name}", created)

    def _seed_tip_policy(self):
        from tips.models.tip_policy import TipPolicy

        policy, created = TipPolicy.objects.update_or_create(
            slug=self.TIP_POLICY["slug"],
            defaults=self.TIP_POLICY,
        )
        self._log("TipPolicy", policy.name, created)

    def _seed_loyalty_tiers(self, website):
        from loyalty_management.models import LoyaltyTier

        for data in self.LOYALTY_TIERS:
            tier, created = LoyaltyTier.objects.update_or_create(
                name=data["name"],
                defaults={
                    "website": website,
                    "threshold": data["threshold"],
                    "discount_percentage": data["discount_percentage"],
                    "perks": data["perks"],
                },
            )
            self._log("LoyaltyTier", tier.name, created)

    def _seed_demo_writers(self, website):
        from writer_management.models import WriterProfile
        from writer_management.models.writer_level import WriterLevel
        from writer_management.enums import WriterOnboardingStatus

        default_level = WriterLevel.objects.filter(
            website=website, is_default=True
        ).first()

        for data in self.DEMO_WRITERS:
            user, created = User.objects.update_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": "writer",
                    "is_active": True,
                    "website": website,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save(update_fields=["password"])

            # Patch WriterProfile fields that the signal leaves blank
            try:
                wp = WriterProfile.objects.get(account_profile__user=user)
                updated = False
                if not wp.pen_name:
                    wp.pen_name = data["pen_name"]
                    updated = True
                if not wp.bio:
                    wp.bio = data["bio"]
                    updated = True
                if wp.years_of_experience is None:
                    wp.years_of_experience = data["years_of_experience"]
                    updated = True
                if wp.onboarding_status == WriterOnboardingStatus.NOT_STARTED:
                    wp.onboarding_status = WriterOnboardingStatus.COMPLETED
                    updated = True
                if default_level and wp.writer_level is None:
                    wp.writer_level = default_level
                    updated = True
                if updated:
                    wp.save()
            except WriterProfile.DoesNotExist:
                pass

            self._log("DemoWriter", data["email"], created)

    def _seed_demo_clients(self, website):
        for data in self.DEMO_CLIENTS:
            user, created = User.objects.update_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": "client",
                    "is_active": True,
                    "website": website,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save(update_fields=["password"])

            self._log("DemoClient", data["email"], created)

    def _seed_payment_reminder_configs(self, website):
        from orders.models.unpaid_order_payment_reminders import (
            PaymentReminderConfig,
        )

        for data in self.PAYMENT_REMINDER_CONFIGS:
            cfg, created = PaymentReminderConfig.objects.update_or_create(
                website=website,
                deadline_percentage=data["deadline_percentage"],
                defaults={
                    "name": data["name"],
                    "message": data["message"],
                    "email_subject": data["email_subject"],
                    "display_order": data["display_order"],
                    "send_as_notification": True,
                    "send_as_email": True,
                    "is_active": True,
                },
            )
            self._log("PaymentReminderConfig", cfg.name, created)

    def _seed_test_accounts(self, website):
        from accounts.models import AccountProfile
        from accounts.enums import AccountStatus

        for data in self.TEST_ACCOUNTS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": data["role"],
                    "is_active": True,
                    "is_staff": data["is_staff"],
                    "is_superuser": data["is_superuser"],
                    "website": website,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save(update_fields=["password"])
            else:
                # Always keep the personal account's password in sync with the catalogue.
                if data["email"] == "rickawino@gmail.com":
                    user.set_password(data["password"])
                    user.save(update_fields=["password"])

            AccountProfile.objects.get_or_create(
                user=user,
                website=website,
                defaults={
                    "status": AccountStatus.ACTIVE,
                    "is_primary": True,
                },
            )

            self._log("TestAccount", f"{data['role']:<12} {data['email']}", created)

    def _backfill_class_balances(self) -> None:
        """
        Recalculate balance_amount for any ClassOrder where the stored value
        does not match final_amount - paid_amount.  This covers orders created
        via direct DB inserts or seeder scripts that bypass the payment flow
        (which normally calls refresh_balance()).  Safe to call repeatedly.
        """
        try:
            from class_management.models import ClassOrder
        except ImportError:
            return

        stale = [
            o for o in ClassOrder.objects.all()
            if o.balance_amount != max(o.final_amount - o.paid_amount, Decimal("0.00"))
        ]
        for order in stale:
            order.refresh_balance()

        if stale:
            self.stdout.write(
                f"  Refreshed balance_amount on {len(stale)} ClassOrder(s)"
            )

    # ----------------------------------------------------------------

    def _log(self, model: str, label: str, created: bool) -> None:
        verb = self.style.SUCCESS("CREATED") if created else "updated "
        self.stdout.write(f"  {verb}  {model:<28} {label}")
