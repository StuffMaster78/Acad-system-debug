"""
Management command: seed pricing configuration for the four marketing websites.

Usage:
    python manage.py seed_marketing_pricing
    python manage.py seed_marketing_pricing --dry-run
"""
from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from order_pricing_core.constants import ServiceFamily
from order_pricing_core.models import (
    AcademicLevelRate,
    DeadlineRate,
    PaperTypeRate,
    ServiceCatalogItem,
    SubjectRate,
    WebsitePricingProfile,
    WorkTypeRate,
)
from order_pricing_core.models.pricing_dimensions import SubjectCategory
from websites.models.websites import Website


# ── Per-site configuration ────────────────────────────────────────────────────
#
# base_price_per_page: the "1× multiplier" anchor price.
#   The cheapest realistic quote a student sees is:
#     base × level_multiplier × deadline_multiplier
#   e.g. GradeCrest High School (1.0×) at 14 days (1.0×) = $13/page  →  base $13
#
SITE_CONFIGS = [
    {
        "domain":     "gradecrest.com",
        "name":       "GradeCrest",
        "base":       Decimal("13.00"),   # "from $13/page" headline
        "currency":   "USD",
        "niche":      "general_academic",
    },
    {
        "domain":     "nursemygrade.com",
        "name":       "NurseMyGrade",
        "base":       Decimal("24.00"),   # "from $24/page" — nursing-specialist premium
        "currency":   "USD",
        "niche":      "nursing",
    },
    {
        "domain":     "researchpapermate.com",
        "name":       "ResearchPaperMate",
        "base":       Decimal("15.00"),   # "from $15/page"
        "currency":   "USD",
        "niche":      "research",
    },
    {
        "domain":     "essaymaniacs.com",
        "name":       "EssayManiacs",
        "base":       Decimal("10.00"),   # "from $10/page" — student/essay focus
        "currency":   "USD",
        "niche":      "essays",
    },
]

# ── Academic levels (shared across all sites; base_price_per_page derived per site) ──
ACADEMIC_LEVELS = [
    {"code": "high_school", "label": "High School",         "multiplier": Decimal("1.0000"), "sort_order": 1},
    {"code": "undergrad",   "label": "Undergraduate",       "multiplier": Decimal("1.2000"), "sort_order": 2},
    {"code": "bachelors",   "label": "Bachelor's",          "multiplier": Decimal("1.2500"), "sort_order": 3},
    {"code": "masters",     "label": "Master's",            "multiplier": Decimal("1.5000"), "sort_order": 4},
    {"code": "graduate",    "label": "Graduate",            "multiplier": Decimal("1.4000"), "sort_order": 5},
    {"code": "phd",         "label": "PhD / Doctorate",     "multiplier": Decimal("1.8000"), "sort_order": 6},
    {"code": "professional","label": "Professional",        "multiplier": Decimal("1.6000"), "sort_order": 7},
]

# ── Deadlines ─────────────────────────────────────────────────────────────────
DEADLINES = [
    {"label": "3 Hours",   "max_hours": 3,   "multiplier": Decimal("3.0000"), "sort_order": 1},
    {"label": "6 Hours",   "max_hours": 6,   "multiplier": Decimal("2.5000"), "sort_order": 2},
    {"label": "12 Hours",  "max_hours": 12,  "multiplier": Decimal("2.0000"), "sort_order": 3},
    {"label": "24 Hours",  "max_hours": 24,  "multiplier": Decimal("1.7000"), "sort_order": 4},
    {"label": "2 Days",    "max_hours": 48,  "multiplier": Decimal("1.4000"), "sort_order": 5},
    {"label": "3 Days",    "max_hours": 72,  "multiplier": Decimal("1.2000"), "sort_order": 6},
    {"label": "5 Days",    "max_hours": 120, "multiplier": Decimal("1.1000"), "sort_order": 7},
    {"label": "7 Days",    "max_hours": 168, "multiplier": Decimal("1.0000"), "sort_order": 8},
    {"label": "10 Days",   "max_hours": 240, "multiplier": Decimal("0.9500"), "sort_order": 9},
    {"label": "14 Days",   "max_hours": 336, "multiplier": Decimal("1.0000"), "sort_order": 10},
    {"label": "20 Days",   "max_hours": 480, "multiplier": Decimal("0.9000"), "sort_order": 11},
    {"label": "30 Days",   "max_hours": 720, "multiplier": Decimal("0.8500"), "sort_order": 12},
]

# ── Work types ───────────────────────────────────────────────────────────────
WORK_TYPES = [
    {"code": "writing",      "label": "Writing",      "multiplier": Decimal("1.0000"), "sort_order": 1},
    {"code": "editing",      "label": "Editing",      "multiplier": Decimal("0.6000"), "sort_order": 2},
    {"code": "proofreading", "label": "Proofreading", "multiplier": Decimal("0.5000"), "sort_order": 3},
    {"code": "rewriting",    "label": "Rewriting",    "multiplier": Decimal("0.8000"), "sort_order": 4},
    {"code": "paraphrasing", "label": "Paraphrasing", "multiplier": Decimal("0.7000"), "sort_order": 5},
]

# ── Subject categories ────────────────────────────────────────────────────────
SUBJECT_CATEGORIES = [
    {"code": "humanities",  "label": "Humanities",       "multiplier": Decimal("1.0000"), "sort_order": 1},
    {"code": "social_sci",  "label": "Social Sciences",  "multiplier": Decimal("1.0000"), "sort_order": 2},
    {"code": "business",    "label": "Business",         "multiplier": Decimal("1.0000"), "sort_order": 3},
    {"code": "stem",        "label": "STEM",             "multiplier": Decimal("1.2000"), "sort_order": 4},
    {"code": "health",      "label": "Nursing & Health", "multiplier": Decimal("1.1000"), "sort_order": 5},
    {"code": "law",         "label": "Law",              "multiplier": Decimal("1.2000"), "sort_order": 6},
    {"code": "general",     "label": "General",          "multiplier": Decimal("1.0000"), "sort_order": 7},
]

# ── Subject rates (linked to category; custom_multiplier = fine-tune per subject) ─
SUBJECT_RATES = [
    # General
    {"code": "general",          "label": "General",             "cat": "general",   "multiplier": Decimal("1.0000"), "sort_order": 1},
    # Humanities
    {"code": "history",          "label": "History",             "cat": "humanities","multiplier": Decimal("1.0000"), "sort_order": 10},
    {"code": "literature",       "label": "Literature / English","cat": "humanities","multiplier": Decimal("1.0000"), "sort_order": 11},
    {"code": "philosophy",       "label": "Philosophy",          "cat": "humanities","multiplier": Decimal("1.0000"), "sort_order": 12},
    # Social Sciences
    {"code": "psychology",       "label": "Psychology",          "cat": "social_sci","multiplier": Decimal("1.0000"), "sort_order": 20},
    {"code": "sociology",        "label": "Sociology",           "cat": "social_sci","multiplier": Decimal("1.0000"), "sort_order": 21},
    {"code": "political_sci",    "label": "Political Science",   "cat": "social_sci","multiplier": Decimal("1.0000"), "sort_order": 22},
    # Business
    {"code": "business",         "label": "Business",            "cat": "business",  "multiplier": Decimal("1.0000"), "sort_order": 30},
    {"code": "economics",        "label": "Economics",           "cat": "business",  "multiplier": Decimal("1.0000"), "sort_order": 31},
    {"code": "marketing",        "label": "Marketing",           "cat": "business",  "multiplier": Decimal("1.0000"), "sort_order": 32},
    # STEM
    {"code": "mathematics",      "label": "Mathematics",         "cat": "stem",      "multiplier": Decimal("1.1000"), "sort_order": 40},
    {"code": "biology",          "label": "Biology",             "cat": "stem",      "multiplier": Decimal("1.1000"), "sort_order": 41},
    {"code": "engineering",      "label": "Engineering",         "cat": "stem",      "multiplier": Decimal("1.2000"), "sort_order": 42},
    {"code": "computer_science", "label": "Computer Science",    "cat": "stem",      "multiplier": Decimal("1.2000"), "sort_order": 43},
    # Health & Nursing
    {"code": "nursing",          "label": "Nursing",             "cat": "health",    "multiplier": Decimal("1.1000"), "sort_order": 50},
    {"code": "medicine",         "label": "Medicine / Health",   "cat": "health",    "multiplier": Decimal("1.2000"), "sort_order": 51},
    {"code": "pharmacy",         "label": "Pharmacy",            "cat": "health",    "multiplier": Decimal("1.1000"), "sort_order": 52},
    # Law
    {"code": "law",              "label": "Law",                 "cat": "law",       "multiplier": Decimal("1.2000"), "sort_order": 60},
    # Education
    {"code": "education",        "label": "Education",           "cat": "social_sci","multiplier": Decimal("1.0000"), "sort_order": 70},
]

# ── Paper types ───────────────────────────────────────────────────────────────
PAPER_TYPES = [
    # Essays
    {"code": "essay",              "label": "Essay",                   "multiplier": Decimal("1.0000"), "sort_order": 1},
    {"code": "argumentative_essay","label": "Argumentative Essay",    "multiplier": Decimal("1.0000"), "sort_order": 2},
    {"code": "analytical_essay",   "label": "Analytical Essay",       "multiplier": Decimal("1.0000"), "sort_order": 3},
    {"code": "persuasive_essay",   "label": "Persuasive Essay",       "multiplier": Decimal("1.0000"), "sort_order": 4},
    {"code": "expository_essay",   "label": "Expository Essay",       "multiplier": Decimal("1.0000"), "sort_order": 5},
    {"code": "reflective_essay",   "label": "Reflective Essay",       "multiplier": Decimal("1.0000"), "sort_order": 6},
    {"code": "narrative_essay",    "label": "Narrative Essay",        "multiplier": Decimal("1.0000"), "sort_order": 7},
    {"code": "descriptive_essay",  "label": "Descriptive Essay",      "multiplier": Decimal("1.0000"), "sort_order": 8},
    # Research & Papers
    {"code": "research_paper",     "label": "Research Paper",          "multiplier": Decimal("1.1000"), "sort_order": 10},
    {"code": "term_paper",         "label": "Term Paper",              "multiplier": Decimal("1.0000"), "sort_order": 11},
    {"code": "literature_review",  "label": "Literature Review",       "multiplier": Decimal("1.1000"), "sort_order": 12},
    {"code": "annotated_bibliography","label": "Annotated Bibliography","multiplier": Decimal("1.0000"), "sort_order": 13},
    {"code": "case_study",         "label": "Case Study",              "multiplier": Decimal("1.1000"), "sort_order": 14},
    # Advanced
    {"code": "thesis",             "label": "Thesis",                  "multiplier": Decimal("1.3000"), "sort_order": 20},
    {"code": "dissertation",       "label": "Dissertation",            "multiplier": Decimal("1.5000"), "sort_order": 21},
    {"code": "capstone_project",   "label": "Capstone Project",        "multiplier": Decimal("1.3000"), "sort_order": 22},
    # Specialised
    {"code": "research_proposal",  "label": "Research Proposal",       "multiplier": Decimal("1.1000"), "sort_order": 30},
    {"code": "book_report",        "label": "Book Report / Review",    "multiplier": Decimal("1.0000"), "sort_order": 31},
    {"code": "article_review",     "label": "Article Review",          "multiplier": Decimal("1.0000"), "sort_order": 32},
    {"code": "coursework",         "label": "Coursework",              "multiplier": Decimal("1.0000"), "sort_order": 33},
    {"code": "homework",           "label": "Homework Assignment",     "multiplier": Decimal("1.0000"), "sort_order": 34},
    {"code": "presentation",       "label": "Presentation / Slides",   "multiplier": Decimal("1.0000"), "sort_order": 35},
    {"code": "speech",             "label": "Speech / Talk",           "multiplier": Decimal("1.0000"), "sort_order": 36},
    {"code": "lab_report",         "label": "Lab Report",              "multiplier": Decimal("1.1000"), "sort_order": 37},
    {"code": "admission_essay",    "label": "Admission Essay",         "multiplier": Decimal("1.0000"), "sort_order": 38},
    # Nursing-specific
    {"code": "care_plan",          "label": "Care Plan",               "multiplier": Decimal("1.1000"), "sort_order": 40},
    {"code": "soap_note",          "label": "SOAP Note",               "multiplier": Decimal("1.0000"), "sort_order": 41},
    {"code": "nursing_essay",      "label": "Nursing Essay",           "multiplier": Decimal("1.0000"), "sort_order": 42},
    {"code": "nursing_report",     "label": "Nursing Report",          "multiplier": Decimal("1.1000"), "sort_order": 43},
    # Editing
    {"code": "editing",            "label": "Editing",                 "multiplier": Decimal("0.6000"), "sort_order": 50},
    {"code": "proofreading",       "label": "Proofreading",            "multiplier": Decimal("0.4000"), "sort_order": 51},
    {"code": "rewriting",          "label": "Rewriting",               "multiplier": Decimal("0.7000"), "sort_order": 52},
]


class Command(BaseCommand):
    help = "Seed pricing configuration for the four marketing websites."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print what would be created without touching the database.",
        )

    def handle(self, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written.\n"))

        for cfg in SITE_CONFIGS:
            self._seed_site(cfg, dry_run=dry_run)

        self.stdout.write(self.style.SUCCESS("\nDone."))

    @transaction.atomic
    def _seed_site(self, cfg: dict, *, dry_run: bool) -> None:
        domain = cfg["domain"]
        name   = cfg["name"]
        base   = cfg["base"]

        self.stdout.write(f"\n── {name} ({domain}) ──")

        # 1. Website — look up by name (most stable) or any domain form
        from django.db.models import Q
        website = Website.objects.filter(
            Q(domain__iexact=domain) |
            Q(domain__iexact=f"https://{domain}") |
            Q(domain__iexact=f"http://{domain}") |
            Q(name__iexact=name),
            is_active=True,
            is_deleted=False,
        ).first()

        if not website:
            website = Website.objects.create(
                domain=domain,
                name=name,
                is_active=True,
                is_deleted=False,
            )
            action = "created"
        else:
            action = f"exists (domain='{website.domain}')"
        self.stdout.write(f"  Website: {action} (id={website.pk})")

        if dry_run:
            self.stdout.write(f"  [dry-run] Would create profile base=${base}, {len(ACADEMIC_LEVELS)} levels, {len(DEADLINES)} deadlines, {len(PAPER_TYPES)} paper types, {len(WORK_TYPES)} work types, {len(SUBJECT_RATES)} subject rates, 1 service")
            return

        # 2. Pricing profile
        profile, created = WebsitePricingProfile.objects.update_or_create(
            website=website,
            defaults={
                "profile_name":             f"{name} Default",
                "base_price_per_page":      base,
                "base_price_per_slide":     (base * Decimal("0.5")).quantize(Decimal("0.01")),
                "base_price_per_diagram":   (base * Decimal("0.75")).quantize(Decimal("0.01")),
                "double_spacing_multiplier": Decimal("1.0000"),
                "single_spacing_multiplier": Decimal("2.0000"),
                "currency":                 cfg["currency"],
                "is_active":                True,
            },
        )
        self.stdout.write(f"  Profile: {'created' if created else 'updated'} — base=${profile.base_price_per_page}/pg")

        # 3. Academic levels
        for lvl in ACADEMIC_LEVELS:
            AcademicLevelRate.objects.update_or_create(
                website=website,
                code=lvl["code"],
                defaults={
                    "label":      lvl["label"],
                    "multiplier": lvl["multiplier"],
                    "sort_order": lvl["sort_order"],
                    "is_active":  True,
                },
            )
        self.stdout.write(f"  Academic levels: {len(ACADEMIC_LEVELS)} upserted")

        # 4. Deadlines
        for dl in DEADLINES:
            DeadlineRate.objects.update_or_create(
                website=website,
                max_hours=dl["max_hours"],
                defaults={
                    "label":      dl["label"],
                    "multiplier": dl["multiplier"],
                    "sort_order": dl["sort_order"],
                    "is_active":  True,
                },
            )
        self.stdout.write(f"  Deadlines: {len(DEADLINES)} upserted")

        # 5. Paper types
        for pt in PAPER_TYPES:
            PaperTypeRate.objects.update_or_create(
                website=website,
                code=pt["code"],
                defaults={
                    "label":      pt["label"],
                    "multiplier": pt["multiplier"],
                    "sort_order": pt["sort_order"],
                    "is_active":  True,
                },
            )
        self.stdout.write(f"  Paper types: {len(PAPER_TYPES)} upserted")

        # 6. Work types
        for wt in WORK_TYPES:
            WorkTypeRate.objects.update_or_create(
                website=website,
                code=wt["code"],
                defaults={
                    "label":      wt["label"],
                    "multiplier": wt["multiplier"],
                    "sort_order": wt["sort_order"],
                    "is_active":  True,
                },
            )
        self.stdout.write(f"  Work types: {len(WORK_TYPES)} upserted")

        # 7. Subject categories + subject rates
        cat_objs: dict[str, SubjectCategory] = {}
        for sc in SUBJECT_CATEGORIES:
            obj, _ = SubjectCategory.objects.update_or_create(
                website=website,
                code=sc["code"],
                defaults={
                    "label":      sc["label"],
                    "multiplier": sc["multiplier"],
                    "sort_order": sc["sort_order"],
                    "is_active":  True,
                },
            )
            cat_objs[sc["code"]] = obj
        self.stdout.write(f"  Subject categories: {len(SUBJECT_CATEGORIES)} upserted")

        for sr in SUBJECT_RATES:
            SubjectRate.objects.update_or_create(
                website=website,
                code=sr["code"],
                defaults={
                    "label":             sr["label"],
                    "category":          cat_objs[sr["cat"]],
                    "custom_multiplier": sr["multiplier"],
                    "sort_order":        sr["sort_order"],
                    "is_active":         True,
                },
            )
        self.stdout.write(f"  Subject rates: {len(SUBJECT_RATES)} upserted")

        # 8. Service catalog item (required by estimate endpoint)
        ServiceCatalogItem.objects.update_or_create(
            website=website,
            service_code="writing",
            defaults={
                "name":             "Academic Writing",
                "description":      "Original academic papers written from scratch.",
                "service_family":   ServiceFamily.PAPER_ORDER,
                "pricing_strategy": "per_page",
                "pricing_unit":     "page",
                "base_amount":      base,
                "minimum_charge":   base,
                "is_public":        True,
                "is_active":        True,
                "sort_order":       1,
            },
        )
        self.stdout.write(f"  Service catalog: 1 upserted (writing)")
