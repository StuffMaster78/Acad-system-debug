"""
Seed WriterProfile and ClientProfile records for existing demo/smoke-test users.

Safe to run multiple times — uses get_or_create throughout.
"""
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Seed WriterProfile and ClientProfile records for demo users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing profiles before re-seeding (destructive).",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset()

        with transaction.atomic():
            writers_created = self._seed_writers()
            clients_created = self._seed_clients()

        self.stdout.write(self.style.SUCCESS(
            f"Done. Writers seeded: {writers_created}  Clients seeded: {clients_created}"
        ))

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset(self):
        from writer_management.models import WriterProfile
        from client_management.models import ClientProfile
        from accounts.models.account_profile import AccountProfile
        from django.contrib.auth import get_user_model
        User = get_user_model()

        writer_users = User.objects.filter(role="writer")
        ClientProfile.objects.filter(user__in=User.objects.filter(role="client")).delete()
        account_profiles = AccountProfile.objects.filter(user__in=writer_users)
        WriterProfile.objects.filter(account_profile__in=account_profiles).delete()
        account_profiles.filter(user__in=writer_users).delete()
        self.stdout.write("Reset complete.")

    # ------------------------------------------------------------------
    # Writers
    # ------------------------------------------------------------------

    def _seed_writers(self):
        from django.contrib.auth import get_user_model
        from writer_management.models import WriterProfile
        from writer_management.models.writer_level import WriterLevel
        from writer_management.models.writer_discipline_state import WriterDisciplineState
        from accounts.models.account_profile import AccountProfile

        User = get_user_model()
        writers = User.objects.filter(role="writer").select_related("website")

        # Map level name -> level obj (fall back to highest id if not found)
        level_map = {lv.name.lower(): lv for lv in WriterLevel.objects.all()}
        default_level = WriterLevel.objects.order_by("id").last()

        # Writer seed data: keyed by email suffix / fallback pen name logic
        writer_meta = {
            "writer1.demo@example.com":        ("Amina K.",   "Expert",       4, "A seasoned academic writer specialising in social sciences."),
            "writer2.demo@example.com":        ("Jon M.",     "Advanced",     6, "Technical writer with a background in STEM disciplines."),
            "writer3.demo@example.com":        ("Sera D.",    "Intermediate", 3, "Generalist writer covering humanities and business topics."),
            "writer4.demo@example.com":        ("Mira Draft", "Expert",       5, "Research-driven writer focused on graduate-level assignments."),
            "writer5.demo@example.com":        ("Leo B.",     "Advanced",     4, "Versatile writer with expertise in law and economics."),
            "smoke.writer@example.com":        ("Smoke W.",   "Intermediate", 2, "Smoke test writer account."),
            "smoke.wallet.writer@example.com": ("Wallet W.",  "Intermediate", 2, "Smoke wallet writer account."),
            "demo.writer.eli@example.com":     ("Eli Prose",  "Expert",       5, "Literature and philosophy specialist."),
            "demo.writer.zara@example.com":    ("Zara Reed",  "Advanced",     7, "Medical and nursing essay writer."),
            "demo.writer.kai@example.com":     ("Kai Strand", "Advanced",     4, "Engineering and computer science writer."),
        }

        created = 0
        for idx, user in enumerate(writers, start=1):
            meta = writer_meta.get(user.email)
            pen_name    = meta[0] if meta else f"Writer {idx}"
            level_name  = meta[1].lower() if meta else "intermediate"
            experience  = meta[2] if meta else 3
            bio         = meta[3] if meta else ""
            level       = level_map.get(level_name, default_level)
            reg_id      = f"WR-{idx:04d}"

            # AccountProfile (writer profiles use an account_profile intermediary)
            website = user.website
            ap, ap_created = AccountProfile.objects.get_or_create(
                user=user,
                defaults={
                    "website": website,
                    "status": "active",
                    "onboarding_status": "completed",
                    "is_primary": True,
                },
            )

            wp, wp_created = WriterProfile.objects.get_or_create(
                account_profile=ap,
                defaults={
                    "registration_id": reg_id,
                    "public_uuid": uuid.uuid4(),
                    "pen_name": pen_name,
                    "bio": bio,
                    "years_of_experience": experience,
                    "writer_level": level,
                    "is_verified": True,
                    "verification_status": "verified",
                    "onboarding_status": "completed",
                },
            )

            # Ensure discipline state exists (required by the writers view)
            WriterDisciplineState.objects.get_or_create(writer=wp)

            if wp_created:
                created += 1
                self.stdout.write(f"  [writer] Created {reg_id} — {pen_name} ({user.email})")
            else:
                self.stdout.write(f"  [writer] Exists  {wp.registration_id} — {wp.pen_name} ({user.email})")

        return created

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------

    def _seed_clients(self):
        from django.contrib.auth import get_user_model
        from client_management.models import ClientProfile
        from loyalty_management.models import LoyaltyTier
        from websites.models.websites import Website

        User = get_user_model()
        clients = User.objects.filter(role="client").select_related("website")

        # Ensure basic loyalty tiers exist per-website
        tier_cache: dict = {}

        def get_or_create_tier(website, name: str, threshold: int) -> "LoyaltyTier":
            if name not in tier_cache:
                tier, _ = LoyaltyTier.objects.get_or_create(
                    name=name,
                    defaults={"website": website, "threshold": threshold, "discount_percentage": Decimal("0.00"), "perks": {}},
                )
                tier_cache[name] = tier
            return tier_cache[name]

        client_meta = {
            "client.demo@example.com":          ("US", "America/New_York",  250,  Decimal("1250.00"), "Silver"),
            "smoke.client@example.com":          ("GB", "Europe/London",      0,  Decimal("0.00"),    "Bronze"),
            "smoke.wallet.client@example.com":   ("GB", "Europe/London",      0,  Decimal("0.00"),    "Bronze"),
            "demo.client.ada@example.com":       ("US", "America/Chicago",  500,  Decimal("3200.00"), "Gold"),
            "demo.client.noah@example.com":      ("CA", "America/Toronto",   80,  Decimal("480.00"),  "Bronze"),
            "demo.client.mira@example.com":      ("AU", "Australia/Sydney",  150, Decimal("950.00"),  "Silver"),
        }
        tier_thresholds = {"Bronze": 0, "Silver": 200, "Gold": 400}

        created = 0
        for idx, user in enumerate(clients, start=1):
            meta = client_meta.get(user.email)
            country      = meta[0] if meta else "US"
            timezone     = meta[1] if meta else "UTC"
            loyalty_pts  = meta[2] if meta else 0
            total_spent  = meta[3] if meta else Decimal("0.00")
            tier_name    = meta[4] if meta else "Bronze"
            reg_id       = f"CL-{idx:04d}"

            website = user.website
            tier_obj = get_or_create_tier(website, tier_name, tier_thresholds.get(tier_name, 0)) if website else None

            cp, cp_created = ClientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "website": website,
                    "country": country,
                    "timezone": timezone,
                    "registration_id": reg_id,
                    "loyalty_points": loyalty_pts,
                    "tier": tier_obj,
                    "total_spent": total_spent,
                    "is_active": True,
                    "is_guest": False,
                },
            )

            if cp_created:
                created += 1
                self.stdout.write(f"  [client] Created {reg_id} — {user.email}")
            else:
                self.stdout.write(f"  [client] Exists  {cp.registration_id} — {user.email}")

        return created
