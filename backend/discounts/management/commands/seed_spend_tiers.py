"""
Seed creative spend-tier discount milestones for every active website.

Tiers unlock a % discount coupon automatically once a client's lifetime
spend crosses the threshold. Idempotent — safe to re-run.

Usage:
    python manage.py seed_spend_tiers
    python manage.py seed_spend_tiers --website-id 1
    python manage.py seed_spend_tiers --clear     # wipe existing tiers first
"""
from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from discounts.constants import DiscountOrigin, DiscountType
from discounts.models import Discount, DiscountSpendTier
from websites.models.websites import Website


# ── Tier catalogue ────────────────────────────────────────────────────────────
#
# Each tier gets:
#   name            – shown in the admin and on receipts
#   emoji           – prepended in the discount code hint
#   min_spend       – lifetime USD threshold to unlock
#   pct_off         – percentage discount value
#   code_suffix     – appended to website slug to form the discount code
#   description     – shown on the client dashboard

SPEND_TIERS: list[dict] = [
    {
        "name": "Inkwell Initiate",
        "emoji": "🖊",
        "min_spend": Decimal("100.00"),
        "pct_off": Decimal("3.00"),
        "code_suffix": "INK3",
        "description": "Your journey begins. 3% off every order once you've spent $100+.",
    },
    {
        "name": "Parchment Scholar",
        "emoji": "📜",
        "min_spend": Decimal("250.00"),
        "pct_off": Decimal("5.00"),
        "code_suffix": "PARCH5",
        "description": "The scroll unfurls. 5% off for clients who've crossed $250 in total orders.",
    },
    {
        "name": "Quill Artisan",
        "emoji": "🪶",
        "min_spend": Decimal("500.00"),
        "pct_off": Decimal("7.00"),
        "code_suffix": "QUILL7",
        "description": "Craft meets loyalty. 7% off when your lifetime spend hits $500.",
    },
    {
        "name": "Thesis Architect",
        "emoji": "🏛",
        "min_spend": Decimal("1000.00"),
        "pct_off": Decimal("10.00"),
        "code_suffix": "ARCH10",
        "description": "You build arguments like blueprints. 10% off at $1,000+ lifetime spend.",
    },
    {
        "name": "Lexicon Patron",
        "emoji": "📚",
        "min_spend": Decimal("2000.00"),
        "pct_off": Decimal("12.00"),
        "code_suffix": "LEXI12",
        "description": "A true steward of words. 12% off for $2,000+ in lifetime orders.",
    },
    {
        "name": "Manuscript Maven",
        "emoji": "📖",
        "min_spend": Decimal("3500.00"),
        "pct_off": Decimal("15.00"),
        "code_suffix": "MAVEN15",
        "description": "Elite status, beautifully earned. 15% off at $3,500+ lifetime spend.",
    },
    {
        "name": "Sovereign Scribe",
        "emoji": "👑",
        "min_spend": Decimal("5000.00"),
        "pct_off": Decimal("18.00"),
        "code_suffix": "SOVEREIGN18",
        "description": "The highest order of loyalty. 18% off every order for $5,000+ clients.",
    },
]


class Command(BaseCommand):
    help = "Seed creative spend-tier discounts for all active websites."

    def add_arguments(self, parser):
        parser.add_argument(
            "--website-id",
            type=int,
            dest="website_id",
            help="Seed only for a specific website ID.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing spend tiers before seeding.",
        )

    def handle(self, *args, **options):
        website_id = options.get("website_id")
        clear = options.get("clear", False)

        qs = Website.objects.filter(is_active=True, is_deleted=False)
        if website_id:
            qs = qs.filter(pk=website_id)

        websites = list(qs)
        if not websites:
            self.stdout.write(self.style.WARNING("No matching active websites found."))
            return

        if clear:
            deleted, _ = DiscountSpendTier.objects.filter(
                website__in=websites,
            ).delete()
            self.stdout.write(f"  Cleared {deleted} existing spend tier(s).")

        total_created = 0
        total_skipped = 0

        for website in websites:
            slug = (website.domain or website.name or "site").lower()
            slug = "".join(c for c in slug if c.isalnum() or c == "-")[:12].strip("-")

            self.stdout.write(f"\n🌐  {website.name} (id={website.pk})")

            for tier in SPEND_TIERS:
                code = f"{slug.upper()}-{tier['code_suffix']}"

                # Find or create the underlying Discount
                discount, d_created = Discount.objects.get_or_create(
                    website=website,
                    discount_code=code,
                    defaults={
                        "name": f"{tier['emoji']} {tier['name']} Reward",
                        "description": tier["description"],
                        "discount_type": DiscountType.PERCENTAGE,
                        "discount_value": tier["pct_off"],
                        "is_active": True,
                        "is_campaign_managed": False,
                        "origin": DiscountOrigin.MANUAL,
                    },
                )

                # Find or create the SpendTier
                spend_tier, st_created = DiscountSpendTier.objects.get_or_create(
                    website=website,
                    discount=discount,
                    defaults={
                        "name": f"{tier['emoji']} {tier['name']}",
                        "minimum_lifetime_spend": tier["min_spend"],
                        "is_active": True,
                    },
                )

                if st_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    ✓ Created  {tier['emoji']} {tier['name']}"
                            f"  (${tier['min_spend']}+ → {tier['pct_off']}%  code: {code})"
                        )
                    )
                    total_created += 1
                else:
                    self.stdout.write(
                        f"    – Exists   {tier['emoji']} {tier['name']}  (skipped)"
                    )
                    total_skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅  Done — {total_created} tier(s) created, {total_skipped} already existed."
            )
        )
