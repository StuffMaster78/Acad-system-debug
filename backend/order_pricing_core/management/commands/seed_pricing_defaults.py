"""
Market-calibrated pricing seed.

Replaces the placeholder defaults with values benchmarked against
8 competitors (July 2026): 99Papers, WritePaperFor.me, PaperHelp,
GradeMiners, SpeedyPaper, ExpertWriting, EduBirdie, CheapWritingService.

Positioning: quality-premium, transparent, mid-market entry, steeper
academic-level premium than most competitors.

Usage:
    python manage.py seed_pricing_defaults [website_domain]
    python manage.py seed_pricing_defaults              # defaults to localhost
    python manage.py seed_pricing_defaults --all-sites  # every active website
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.apps import apps

from order_pricing_core.constants import DesignPackageType
from order_pricing_core.constants import DesignProductType
from order_pricing_core.constants import DiagramType
from order_pricing_core.constants import PricingStrategy
from order_pricing_core.constants import PricingUnit
from order_pricing_core.constants import ServiceFamily


# ── Market-research anchors (July 2026) ─────────────────────────────────────
# Reference: 99Papers HS 14-day = $13.93  | Masters 3-day = $26.06
#            GradeMiners HS editing = $6.88/page
#            SpeedyPaper PhD max = $52/page
#            WritePaperFor.me urgency spread = 3.5× (cheapest → 4-hr)
#
# Our base $13.99/page (double-spaced, HS, 10-day standard) sits at the
# established mid-market (99Papers tier). PhD 3-day lands at $33.23 —
# above 99Papers ($28.19), below SpeedyPaper ($52), justified by
# quality positioning and expert-only PhD assignment policy.
# ─────────────────────────────────────────────────────────────────────────────

BASE_PER_PAGE     = Decimal("13.99")   # double-spaced, HS, standard deadline
BASE_PER_SLIDE    = Decimal("13.99")   # presentation slide (market parity)
BASE_PER_DIAGRAM  = Decimal("19.99")   # includes editable source file
MIN_PAPER_CHARGE  = Decimal("13.99")   # floor on any paper order
MIN_DESIGN_CHARGE = Decimal("20.99")   # 2-slide minimum effectively
MIN_DIAGRAM_CHARGE= Decimal("19.99")   # 1-diagram minimum
PREFERRED_WRITER_FEE = Decimal("4.99") # flat: return to a specific writer


class Command(BaseCommand):
    help = (
        "Seed market-calibrated pricing for a website. "
        "Pass a domain or --all-sites."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "website_domain",
            nargs="?",
            default="localhost",
            help="Website domain to seed (default: localhost).",
        )
        parser.add_argument(
            "--all-sites",
            action="store_true",
            help="Seed every active website (ignores website_domain).",
        )

    def handle(self, *args, **options):
        Website = apps.get_model("websites", "Website")

        if options["all_sites"]:
            sites = list(Website.objects.filter(is_active=True))
            if not sites:
                self.stderr.write(self.style.ERROR("No active websites found."))
                return
        else:
            domain = options["website_domain"]
            try:
                sites = [Website.objects.get(domain=domain)]
            except Website.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'No website with domain "{domain}"'))
                return

        for website in sites:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"\n{'═' * 62}\n  {website.name}  ({website.domain})\n{'═' * 62}"
                )
            )
            self._seed_website(website)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓  Pricing seeded for {len(sites)} site(s).\n"
            )
        )

    # ── Per-website orchestration ─────────────────────────────────────────────

    def _seed_website(self, website):
        WebsitePricingProfile      = apps.get_model("order_pricing_core", "WebsitePricingProfile")
        AcademicLevelRate          = apps.get_model("order_pricing_core", "AcademicLevelRate")
        PaperTypeRate              = apps.get_model("order_pricing_core", "PaperTypeRate")
        WorkTypeRate               = apps.get_model("order_pricing_core", "WorkTypeRate")
        DeadlineRate               = apps.get_model("order_pricing_core", "DeadlineRate")
        WriterLevelRate            = apps.get_model("order_pricing_core", "WriterLevelRate")
        SubjectCategory            = apps.get_model("order_pricing_core", "SubjectCategory")
        SubjectRate                = apps.get_model("order_pricing_core", "SubjectRate")
        AnalysisLevelRate          = apps.get_model("order_pricing_core", "AnalysisLevelRate")
        DiagramComplexityRate      = apps.get_model("order_pricing_core", "DiagramComplexityRate")
        ServiceCatalogItem         = apps.get_model("order_pricing_core", "ServiceCatalogItem")
        DesignOrderServiceConfig   = apps.get_model("order_pricing_core", "DesignOrderServiceConfig")
        DiagramOrderServiceConfig  = apps.get_model("order_pricing_core", "DiagramOrderServiceConfig")
        PaperType     = apps.get_model("order_configs", "PaperType")
        Subject       = apps.get_model("order_configs", "Subject")
        AcademicLevel = apps.get_model("order_configs", "AcademicLevel")
        TypeOfWork    = apps.get_model("order_configs", "TypeOfWork")

        self._seed_profile(website, WebsitePricingProfile)
        self._seed_academic_levels(website, AcademicLevelRate)
        self._seed_deadlines(website, DeadlineRate)
        self._seed_paper_type_rates(website, PaperTypeRate)
        self._seed_work_type_rates(website, WorkTypeRate)
        self._seed_writer_level_rates(website, WriterLevelRate)
        self._seed_subject_categories(website, SubjectCategory)
        self._seed_analysis_levels(website, AnalysisLevelRate)
        self._seed_diagram_complexity(website, DiagramComplexityRate)
        self._seed_services(
            website, ServiceCatalogItem,
            DesignOrderServiceConfig, DiagramOrderServiceConfig,
        )
        self._sync_from_order_configs(
            website,
            PaperTypeRate, WorkTypeRate, AcademicLevelRate, SubjectRate, SubjectCategory,
            PaperType, TypeOfWork, AcademicLevel, Subject,
        )
        self._print_summary(website)

    # ── Pricing profile ───────────────────────────────────────────────────────

    def _seed_profile(self, website, Model):
        self._section("PRICING PROFILE")
        _, created = Model.objects.update_or_create(
            website=website,
            defaults=dict(
                profile_name="Market-Calibrated Pricing Profile",
                currency="USD",
                base_price_per_page=BASE_PER_PAGE,
                base_price_per_slide=BASE_PER_SLIDE,
                base_price_per_diagram=BASE_PER_DIAGRAM,
                # Spacing: double = standard, single = 2× (industry norm)
                double_spacing_multiplier=Decimal("1.0000"),
                single_spacing_multiplier=Decimal("2.0000"),
                preferred_writer_fee=PREFERRED_WRITER_FEE,
                minimum_paper_order_charge=MIN_PAPER_CHARGE,
                minimum_design_order_charge=MIN_DESIGN_CHARGE,
                minimum_diagram_order_charge=MIN_DIAGRAM_CHARGE,
                max_pages_per_hour=1,
                extra_hour_per_extra_page=1,
                rush_recommendation_only=True,
                is_active=True,
                allow_customization=True,
            ),
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"  {verb}  ${BASE_PER_PAGE}/page · ${BASE_PER_SLIDE}/slide"
            f" · ${BASE_PER_DIAGRAM}/diagram"
        ))

    # ── Academic level multipliers ────────────────────────────────────────────
    # Benchmarked against 99Papers full grid:
    #   HS 30-day=$12.46  →  implied multiplier=1.00
    #   Masters 30-day=$20.98 → 20.98/12.46 = 1.683×  (we use 1.55 – conservative)
    #   PhD 30-day=$23.11 → 23.11/12.46 = 1.855×  (we use 1.90 – premium posture)

    def _seed_academic_levels(self, website, Model):
        self._section("ACADEMIC LEVEL MULTIPLIERS")
        levels = [
            # code, label, multiplier, sort_order
            # HS $13.99/page — market range $10–$14
            ("high_school",  "High School",         Decimal("1.0000"), 1),
            # College $15.39 — market range $12–$16
            ("college",      "College / Freshman",  Decimal("1.1000"), 2),
            # Undergrad $16.79 — market range $14–$18
            ("undergrad",    "Undergraduate",        Decimal("1.2000"), 3),
            # Bachelor's $17.49
            ("bachelors",    "Bachelor's",           Decimal("1.2500"), 4),
            # Graduate $20.29
            ("graduate",     "Graduate",             Decimal("1.4500"), 5),
            # Master's $21.69 — 99Papers Masters 30-day=$20.98 baseline
            ("masters",      "Master's",             Decimal("1.5500"), 6),
            # Professional $23.78 — MBA/JD/MD carry complexity premium
            ("professional", "Professional (MBA/JD/MD/DNP)",
                                                     Decimal("1.7000"), 7),
            # PhD $26.58 — 99Papers PhD 30-day=$23.11; our premium > them
            ("phd",          "PhD / Doctorate",      Decimal("1.9000"), 8),
        ]
        for code, label, mult, sort in levels:
            _, created = Model.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=mult, sort_order=sort, is_active=True),
            )
            price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{label:<32} ×{mult}  → ${price}/page"
            ))

    # ── Deadline tiers ────────────────────────────────────────────────────────
    # Urgency spread: cheapest (30-day) to fastest (3-hr) = 3.53×
    # Matches 99Papers spread of 2.92× at HS; we're slightly wider to
    # price rush work fairly and discourage last-minute abuse.
    #
    # Key verified market anchors (HS, writing):
    #   99Papers  HS 14-day=$13.93  ← our base (≈1.0× at 10-day)
    #   99Papers  HS 24-hr =$24.26  ← we use 1.75× → $24.48  ✓
    #   99Papers  HS 3-hr  =$33.44  ← we use 3.0× → $41.97  (premium)
    #   GradeMiners HS 24-hr=$28.95 ← our 24-hr $24.48 is below — competitive

    def _seed_deadlines(self, website, Model):
        self._section("DEADLINE TIERS")
        # Clear stale rows — deadline structure is versioned, not additive
        deleted, _ = Model.objects.filter(website=website).delete()
        if deleted:
            self.stdout.write(f"  Cleared {deleted} stale deadline row(s)")

        tiers = [
            # label, max_hours, multiplier, sort_order
            # 3-hr: 3.0× — HS = $41.97  (market: SpeedyPaper ~$26 HS 6-hr,
            #   ExpertWriting $40 HS 3-hr). We match ExpertWriting's 4× premium
            #   but at a higher base so absolute price is still justified.
            ("3 Hours",   3,   Decimal("3.0000"),  1),
            ("6 Hours",   6,   Decimal("2.5000"),  2),  # HS $34.98
            ("12 Hours",  12,  Decimal("2.0000"),  3),  # HS $27.98
            ("24 Hours",  24,  Decimal("1.7500"),  4),  # HS $24.48 vs 99P $24.26 ✓
            ("2 Days",    48,  Decimal("1.4500"),  5),  # HS $20.29
            ("3 Days",    72,  Decimal("1.2500"),  6),  # HS $17.49, Masters $33.23
            ("5 Days",    120, Decimal("1.1000"),  7),  # HS $15.39
            ("7 Days",    168, Decimal("1.0500"),  8),  # HS $14.69, Masters $22.76 ✓
            ("10 Days",   240, Decimal("1.0000"),  9),  # HS $13.99 — standard base
            ("14 Days",   336, Decimal("0.9500"), 10),  # HS $13.29 — discount for planning
            ("20 Days",   480, Decimal("0.9000"), 11),  # HS $12.59 vs GradeMiners $11.30
            ("30 Days",   720, Decimal("0.8500"), 12),  # HS $11.89 vs 99P 30-day $12.46
        ]
        for label, max_h, mult, sort in tiers:
            Model.objects.create(
                website=website, label=label, max_hours=max_h,
                multiplier=mult, sort_order=sort, is_active=True,
            )
            hs_price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  + {label:<10} ≤{max_h:>4}h  ×{mult}  HS→${hs_price}"
            ))

    # ── Paper type multipliers ────────────────────────────────────────────────

    def _seed_paper_type_rates(self, website, Model):
        self._section("PAPER TYPE RATES (canonical list)")
        types = [
            # code, label, multiplier, sort
            ("essay",           "Essay",                          Decimal("1.0000"),  1),
            ("research_paper",  "Research Paper",                 Decimal("1.1000"),  2),
            ("thesis",          "Thesis / Dissertation",          Decimal("1.4500"),  3),
            ("case_study",      "Case Study",                     Decimal("1.1000"),  4),
            ("lab_report",      "Lab Report",                     Decimal("1.2000"),  5),
            ("presentation",    "Presentation / Slides",          Decimal("1.0000"),  6),
            ("business",        "Business Writing",               Decimal("1.0500"),  7),
            ("creative",        "Creative Writing",               Decimal("0.9500"),  8),
            ("nursing",         "Nursing / Clinical",             Decimal("1.2500"),  9),
            ("legal",           "Legal Writing",                  Decimal("1.5500"), 10),
            ("technical",       "Technical / Engineering",        Decimal("1.3500"), 11),
            ("editing",         "Editing",                        Decimal("0.5500"), 12),
            ("proofreading",    "Proofreading",                   Decimal("0.4500"), 13),
            ("rewriting",       "Rewriting / Paraphrasing",       Decimal("0.7500"), 14),
            ("coding",          "Coding / Programming",           Decimal("1.6500"), 15),
            ("data_analysis",   "Data Analysis / Statistics",     Decimal("1.3000"), 16),
            ("annotated_bib",   "Annotated Bibliography",         Decimal("0.9000"), 17),
            ("lit_review",      "Literature Review",              Decimal("1.0500"), 18),
            ("article_review",  "Article / Book Review",          Decimal("0.9500"), 19),
            ("reflection",      "Reflection / Journal",           Decimal("0.8500"), 20),
            ("speech",          "Speech / Presentation Script",   Decimal("0.9000"), 21),
            ("cover_letter",    "Cover Letter / Personal Statement", Decimal("1.0000"), 22),
            ("admission_essay", "Admission Essay",                Decimal("1.1500"), 23),
            ("grant",           "Grant Proposal",                 Decimal("1.2500"), 24),
        ]
        for code, label, mult, sort in types:
            _, created = Model.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=mult, sort_order=sort, is_active=True),
            )
            price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{label:<40} ×{mult}  ${price}/page"
            ))

    # ── Work type multipliers ─────────────────────────────────────────────────
    # Editing: market $5–$8/page.  Our: $13.99 × 0.55 = $7.69 ✓
    # Proofreading: market $4–$6/page.  Our: $13.99 × 0.40 = $5.60 ✓
    # Data analysis: market premium ~1.3×. Ours: 1.35 ✓

    def _seed_work_type_rates(self, website, Model):
        self._section("WORK TYPE RATES")
        types = [
            ("writing",       "Writing from scratch",  Decimal("1.0000"),  1),
            ("editing",       "Editing",               Decimal("0.5500"),  2),
            ("proofreading",  "Proofreading",          Decimal("0.4000"),  3),
            ("rewriting",     "Rewriting",             Decimal("0.8000"),  4),
            ("paraphrasing",  "Paraphrasing",          Decimal("0.6500"),  5),
            ("research",      "Research only",         Decimal("1.0000"),  6),
            ("data_analysis", "Data Analysis",         Decimal("1.3500"),  7),
            ("programming",   "Programming / Coding",  Decimal("1.6500"),  8),
            ("formatting",    "Formatting / Citation", Decimal("0.3500"),  9),
            ("translation",   "Translation",           Decimal("1.1500"), 10),
            ("tutoring",      "Tutoring / Guidance",   Decimal("0.9000"), 11),
        ]
        for code, label, mult, sort in types:
            _, created = Model.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=mult, sort_order=sort, is_active=True),
            )
            price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{label:<35} ×{mult}  ${price}/page"
            ))

    # ── Writer level upsells (flat fee per page) ──────────────────────────────
    # Market benchmarks (flat-fee model, like GradeMiners):
    #   GradeMiners: Top writer +$6.29/page; Premium +$12.59/page
    #   Our tiers are slightly higher — justified by stricter curation.

    def _seed_writer_level_rates(self, website, Model):
        self._section("WRITER LEVEL UPSELLS (flat fee per page)")
        levels = [
            # code, label, amount, is_flat_fee, sort
            ("standard",  "Standard Writer",
             Decimal("0.00"), True, 1),   # included, no upsell
            ("advanced",  "Advanced Writer (+2 yrs experience, top-20%)",
             Decimal("4.99"), True, 2),   # market: GradeMiners +$6.29
            ("top",       "Top Writer (verified postgrad, top-10%)",
             Decimal("9.99"), True, 3),   # market: GradeMiners +$12.59
            ("expert",    "Expert Writer (PhD/verified specialist)",
             Decimal("13.99"), True, 4),  # reserved for PhD-level orders
        ]
        for code, label, amt, flat, sort in levels:
            _, created = Model.objects.update_or_create(
                website=website, code=code,
                defaults=dict(
                    label=label, amount=amt,
                    is_flat_fee=flat, sort_order=sort, is_active=True,
                ),
            )
            fee_str = f"+${amt}/page (flat)" if amt else "included"
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{label:<50} {fee_str}"
            ))

    # ── Subject categories ────────────────────────────────────────────────────
    # STEM and Law carry the steepest market premiums. Our multipliers
    # are conservative (not maximising margin) to stay competitive on volume.

    def _seed_subject_categories(self, website, Model):
        self._section("SUBJECT CATEGORIES")
        cats = [
            # code, label, multiplier, sort
            ("humanities",  "Humanities & Arts",        Decimal("1.0000"), 1),
            ("social_sci",  "Social Sciences",          Decimal("1.0000"), 2),
            ("business",    "Business & Economics",     Decimal("1.0500"), 3),
            ("nursing",     "Nursing & Health Sciences",Decimal("1.1500"), 4),
            ("stem",        "STEM (Science & Math)",    Decimal("1.2000"), 5),
            ("law",         "Law & Legal Studies",      Decimal("1.3500"), 6),
            ("technology",  "Technology & CS",          Decimal("1.4500"), 7),
        ]
        for code, label, mult, sort in cats:
            _, created = Model.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=mult, sort_order=sort, is_active=True),
            )
            price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{label:<35} ×{mult}  ${price}/page"
            ))

    # ── Analysis level rates ──────────────────────────────────────────────────

    def _seed_analysis_levels(self, website, Model):
        self._section("ANALYSIS LEVEL RATES")
        levels = [
            ("none",     Decimal("1.0000")),  # no quantitative component
            ("basic",    Decimal("1.2000")),  # descriptive stats, simple charts
            ("advanced", Decimal("1.5500")),  # SPSS/R/Excel modelling, regression
        ]
        for level, mult in levels:
            _, created = Model.objects.update_or_create(
                website=website, level=level,
                defaults=dict(multiplier=mult, is_active=True),
            )
            price = (BASE_PER_PAGE * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{level.capitalize():<12} ×{mult}  ${price}/page"
            ))

    # ── Diagram complexity ────────────────────────────────────────────────────

    def _seed_diagram_complexity(self, website, Model):
        self._section("DIAGRAM COMPLEXITY RATES")
        levels = [
            # complexity, multiplier
            ("simple",   Decimal("1.0000")),  # $19.99 — basic flowchart/org chart
            ("moderate", Decimal("1.3500")),  # $26.99 — UML, ERD with relationships
            ("complex",  Decimal("1.8000")),  # $35.98 — system architecture, multi-layer
        ]
        for complexity, mult in levels:
            _, created = Model.objects.update_or_create(
                website=website, complexity=complexity,
                defaults=dict(multiplier=mult, is_active=True),
            )
            price = (BASE_PER_DIAGRAM * mult).quantize(Decimal("0.01"))
            self.stdout.write(self.style.SUCCESS(
                f"  {'+ ' if created else '↻ '}{complexity.capitalize():<12} ×{mult}  ${price}/diagram"
            ))

    # ── Service catalog ───────────────────────────────────────────────────────

    def _seed_services(self, website, Catalog, DesignConfig, DiagramConfig):
        self._section("SERVICE CATALOG")
        p = self._seed_paper_services(website, Catalog)
        d = self._seed_design_services(website, Catalog, DesignConfig)
        g = self._seed_diagram_services(website, Catalog, DiagramConfig)
        self.stdout.write(self.style.SUCCESS(
            f"  {p} paper + {d} design + {g} diagram services"
        ))

    def _seed_paper_services(self, website, Catalog):
        services = [
            {
                "service_code": "academic_writing",
                "name": "Academic Writing",
                "description": (
                    "Essays, research papers, dissertations, and all standard academic paper types. "
                    "Price shown per double-spaced page at your chosen academic level and deadline."
                ),
                "sort_order": 10,
            },
            {
                "service_code": "nursing_writing",
                "name": "Nursing & Clinical Writing",
                "description": (
                    "SOAP notes, care plans, nursing assessments, clinical case studies, "
                    "and health-sciences papers. Handled by verified nursing graduates."
                ),
                "sort_order": 11,
            },
            {
                "service_code": "business_writing",
                "name": "Business & Professional Writing",
                "description": (
                    "Business reports, case studies, marketing plans, financial analyses, "
                    "MBA papers, and professional correspondence."
                ),
                "sort_order": 12,
            },
            {
                "service_code": "stem_writing",
                "name": "STEM & Technical Writing",
                "description": (
                    "Lab reports, technical documentation, engineering papers, "
                    "data-analysis write-ups, and science research papers."
                ),
                "sort_order": 13,
            },
            {
                "service_code": "editing_proofreading",
                "name": "Editing & Proofreading",
                "description": (
                    "Grammar, flow, structure, and citation editing. "
                    "Priced at 40–55% of the standard writing rate."
                ),
                "sort_order": 14,
            },
            {
                "service_code": "admission_writing",
                "name": "Admission & Personal Statement Writing",
                "description": (
                    "College application essays, personal statements, "
                    "statement of purpose, and scholarship essays."
                ),
                "sort_order": 15,
            },
        ]
        for data in services:
            Catalog.objects.update_or_create(
                website=website,
                service_code=data["service_code"],
                defaults={
                    **data,
                    "service_family": ServiceFamily.PAPER_ORDER,
                    "pricing_strategy": PricingStrategy.FORMULA,
                    "pricing_unit": PricingUnit.PAGE,
                    "base_amount": BASE_PER_PAGE,
                    "minimum_charge": MIN_PAPER_CHARGE,
                    "is_public": True,
                    "is_active": True,
                },
            )
        return len(services)

    def _seed_design_services(self, website, Catalog, DesignConfig):
        services = [
            {
                "service_code": "presentation_design",
                "name": "Presentation Design",
                "description": (
                    "Professional slide decks (PowerPoint, Google Slides, Keynote). "
                    f"From ${BASE_PER_SLIDE}/slide · minimum {MIN_DESIGN_CHARGE} (2 slides)."
                ),
                "pricing_unit": PricingUnit.SLIDE,
                "base_amount": BASE_PER_SLIDE,
                "minimum_charge": MIN_DESIGN_CHARGE,
                "sort_order": 50,
                "config": {
                    "design_product_type": DesignProductType.PRESENTATION,
                    "default_package_type": DesignPackageType.STANDARD,
                    "supports_slides": True,
                    "supports_quantity": False,
                },
            },
            {
                "service_code": "infographic_design",
                "name": "Infographic Design",
                "description": (
                    "Custom infographics, data visualisations, and statistical diagrams. "
                    "Delivered in PNG + editable source file."
                ),
                "pricing_unit": PricingUnit.ITEM,
                "base_amount": Decimal("49.99"),
                "minimum_charge": Decimal("49.99"),
                "sort_order": 51,
                "config": {
                    "design_product_type": DesignProductType.INFOGRAPHIC,
                    "default_package_type": DesignPackageType.STANDARD,
                    "supports_slides": False,
                    "supports_quantity": False,
                },
            },
            {
                "service_code": "poster_flyer_design",
                "name": "Poster / Flyer Design",
                "description": (
                    "Academic posters, conference posters, promotional flyers. "
                    "Delivered as high-resolution PDF + editable file."
                ),
                "pricing_unit": PricingUnit.ITEM,
                "base_amount": Decimal("39.99"),
                "minimum_charge": Decimal("39.99"),
                "sort_order": 52,
                "config": {
                    "design_product_type": DesignProductType.FLYER,
                    "default_package_type": DesignPackageType.STANDARD,
                    "supports_slides": False,
                    "supports_quantity": False,
                },
            },
        ]
        for data in services:
            config = data.pop("config")
            item, _ = Catalog.objects.update_or_create(
                website=website,
                service_code=data["service_code"],
                defaults={
                    **data,
                    "service_family": ServiceFamily.DESIGN_ORDER,
                    "pricing_strategy": PricingStrategy.FORMULA,
                    "is_public": True,
                    "is_active": True,
                },
            )
            DesignConfig.objects.update_or_create(
                service=item,
                defaults={
                    **config,
                    "supports_deadline": True,
                    "supports_files": True,
                    "supports_topic": True,
                    "supports_instructions": True,
                },
            )
        return len(services)

    def _seed_diagram_services(self, website, Catalog, DiagramConfig):
        services = [
            {
                "service_code": "flowchart_diagram",
                "name": "Flowchart Diagram",
                "description": (
                    "Process flows, decision trees, and workflow diagrams. "
                    "Delivered as PNG + editable Visio/Draw.io source."
                ),
                "diagram_type": DiagramType.FLOWCHART,
                "sort_order": 60,
            },
            {
                "service_code": "erd_diagram",
                "name": "Entity Relationship Diagram (ERD)",
                "description": (
                    "Database ERDs with entities, attributes, and relationships. "
                    "Suitable for database design coursework and documentation."
                ),
                "diagram_type": DiagramType.ERD,
                "sort_order": 61,
            },
            {
                "service_code": "uml_diagram",
                "name": "UML Diagram",
                "description": (
                    "Class diagrams, sequence diagrams, use-case diagrams, "
                    "and state machine diagrams."
                ),
                "diagram_type": DiagramType.UML,
                "sort_order": 62,
            },
            {
                "service_code": "system_diagram",
                "name": "System Architecture Diagram",
                "description": (
                    "Network topologies, system architecture, cloud infrastructure, "
                    "and component diagrams."
                ),
                "diagram_type": DiagramType.SYSTEM_DIAGRAM,
                "sort_order": 63,
            },
        ]
        for data in services:
            diagram_type = data.pop("diagram_type")
            item, _ = Catalog.objects.update_or_create(
                website=website,
                service_code=data["service_code"],
                defaults={
                    **data,
                    "service_family": ServiceFamily.DIAGRAM_ORDER,
                    "pricing_strategy": PricingStrategy.FORMULA,
                    "pricing_unit": PricingUnit.DIAGRAM,
                    "base_amount": BASE_PER_DIAGRAM,
                    "minimum_charge": MIN_DIAGRAM_CHARGE,
                    "is_public": True,
                    "is_active": True,
                },
            )
            DiagramConfig.objects.update_or_create(
                service=item,
                defaults={
                    "diagram_type": diagram_type,
                    "supports_quantity": True,
                    "supports_complexity": True,
                    "supports_deadline": True,
                    "supports_files": True,
                    "supports_topic": True,
                    "supports_instructions": True,
                },
            )
        return len(services)

    # ── Sync dynamic rates from order_configs ─────────────────────────────────
    # order_configs holds the full catalogue of paper types / subjects /
    # academic levels / types-of-work per site. We sync a PricingRate row
    # for every record so the quote engine never hits a missing-rate error.

    def _sync_from_order_configs(
        self, website,
        PaperTypeRate, WorkTypeRate, AcademicLevelRate, SubjectRate, SubjectCategory,
        PaperType, TypeOfWork, AcademicLevel, Subject,
    ):
        self._section("SYNC FROM order_configs")

        # Paper types
        pt_c = pt_u = 0
        for pt in PaperType.objects.filter(website=website):
            mult = self._paper_type_mult(pt.name)
            _, created = PaperTypeRate.objects.update_or_create(
                website=website, code=pt.name,
                defaults=dict(label=pt.name, multiplier=mult, sort_order=0, is_active=True),
            )
            if created: pt_c += 1
            else: pt_u += 1
        self.stdout.write(self.style.SUCCESS(
            f"  PaperTypeRate   +{pt_c} created  ↻{pt_u} updated"
        ))

        # Types of work
        wt_c = wt_u = 0
        for tow in TypeOfWork.objects.filter(website=website):
            mult = self._work_type_mult(tow.name)
            _, created = WorkTypeRate.objects.update_or_create(
                website=website, code=tow.name,
                defaults=dict(label=tow.name, multiplier=mult, sort_order=0, is_active=True),
            )
            if created: wt_c += 1
            else: wt_u += 1
        self.stdout.write(self.style.SUCCESS(
            f"  WorkTypeRate    +{wt_c} created  ↻{wt_u} updated"
        ))

        # Academic levels
        al_c = al_u = 0
        for al in AcademicLevel.objects.filter(website=website):
            mult = self._academic_level_mult(al.name)
            _, created = AcademicLevelRate.objects.update_or_create(
                website=website, code=al.name,
                defaults=dict(label=al.name, multiplier=mult, sort_order=0, is_active=True),
            )
            if created: al_c += 1
            else: al_u += 1
        self.stdout.write(self.style.SUCCESS(
            f"  AcademicLevelRate +{al_c} created  ↻{al_u} updated"
        ))

        # Subjects
        cat_map = {c.code: c for c in SubjectCategory.objects.filter(website=website)}
        default_cat = cat_map.get("humanities")
        if not default_cat:
            self.stdout.write(self.style.WARNING("  No subject categories — skipping SubjectRate sync"))
        else:
            sr_c = sr_u = 0
            for subj in Subject.objects.filter(website=website):
                cat = self._subject_category(subj.name, subj.is_technical, cat_map)
                _, created = SubjectRate.objects.update_or_create(
                    website=website, code=subj.name,
                    defaults=dict(label=subj.name, category=cat, sort_order=0, is_active=True),
                )
                if created: sr_c += 1
                else: sr_u += 1
            self.stdout.write(self.style.SUCCESS(
                f"  SubjectRate     +{sr_c} created  ↻{sr_u} updated"
            ))

    # ── Summary printout ──────────────────────────────────────────────────────

    def _print_summary(self, website):
        models = {
            "Pricing profile":    ("order_pricing_core", "WebsitePricingProfile"),
            "Academic level rates": ("order_pricing_core", "AcademicLevelRate"),
            "Deadline tiers":     ("order_pricing_core", "DeadlineRate"),
            "Paper type rates":   ("order_pricing_core", "PaperTypeRate"),
            "Work type rates":    ("order_pricing_core", "WorkTypeRate"),
            "Writer level rates": ("order_pricing_core", "WriterLevelRate"),
            "Subject categories": ("order_pricing_core", "SubjectCategory"),
            "Subject rates":      ("order_pricing_core", "SubjectRate"),
            "Analysis levels":    ("order_pricing_core", "AnalysisLevelRate"),
            "Diagram complexity": ("order_pricing_core", "DiagramComplexityRate"),
            "Service catalog":    ("order_pricing_core", "ServiceCatalogItem"),
        }
        self.stdout.write(f"\n{'─' * 62}")
        self.stdout.write(f"  SUMMARY — {website.name}")
        self.stdout.write(f"{'─' * 62}")
        for label, (app, model_name) in models.items():
            Model = apps.get_model(app, model_name)
            try:
                count = Model.objects.filter(website=website).count()
            except Exception:
                count = "—"
            self.stdout.write(f"  {label:<28} {count}")

        # Sample price grid
        self.stdout.write(f"\n  Sample prices (double-spaced, Writing, Essay):")
        self.stdout.write(f"  {'Deadline':<12} {'HS':>8} {'College':>10} {'Masters':>10} {'PhD':>10}")
        for label, dl_mult, al_pairs in [
            ("14 Days",  Decimal("0.9500"), [("HS", Decimal("1.0000")), ("College", Decimal("1.1000")), ("Masters", Decimal("1.5500")), ("PhD", Decimal("1.9000"))]),
            ("7 Days",   Decimal("1.0500"), [("HS", Decimal("1.0000")), ("College", Decimal("1.1000")), ("Masters", Decimal("1.5500")), ("PhD", Decimal("1.9000"))]),
            ("3 Days",   Decimal("1.2500"), [("HS", Decimal("1.0000")), ("College", Decimal("1.1000")), ("Masters", Decimal("1.5500")), ("PhD", Decimal("1.9000"))]),
            ("24 Hours", Decimal("1.7500"), [("HS", Decimal("1.0000")), ("College", Decimal("1.1000")), ("Masters", Decimal("1.5500")), ("PhD", Decimal("1.9000"))]),
            ("3 Hours",  Decimal("3.0000"), [("HS", Decimal("1.0000")), ("College", Decimal("1.1000")), ("Masters", Decimal("1.5500")), ("PhD", Decimal("1.9000"))]),
        ]:
            prices = [
                f"${(BASE_PER_PAGE * dl_mult * al_mult).quantize(Decimal('0.01'))}"
                for _, al_mult in al_pairs
            ]
            self.stdout.write(
                f"  {label:<12} {prices[0]:>8} {prices[1]:>10} {prices[2]:>10} {prices[3]:>10}"
            )
        self.stdout.write("")

    # ── Multiplier lookup helpers ─────────────────────────────────────────────

    def _academic_level_mult(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("phd", "doctorate", "doctoral")):
            return Decimal("1.9000")
        if any(k in n for k in ("professional", "md ", "jd ", "dds", "dvm", "edd ", "dpt", "pharmd", "dnp")):
            return Decimal("1.7000")
        if any(k in n for k in ("master", "mba", "msc", "meng", "graduate")):
            return Decimal("1.5500")
        if any(k in n for k in ("bachelor", "undergrad", "university")):
            return Decimal("1.2500")
        if any(k in n for k in ("college", "associate", "diploma", "certificate", "freshman")):
            return Decimal("1.1000")
        if any(k in n for k in ("high school", "secondary", "a-level", "ib ")):
            return Decimal("1.0000")
        return Decimal("1.2000")

    def _work_type_mult(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("programming", "coding", "algorithm", "software", "development", "api", "database design", "system design", "data structure")):
            return Decimal("1.6500")
        if any(k in n for k in ("data analysis", "statistical", "quantitative", "qualitative", "research analysis", "financial analysis", "market research")):
            return Decimal("1.3500")
        if any(k in n for k in ("translation", "localiz")):
            return Decimal("1.1500")
        if any(k in n for k in ("research", "literature review", "bibliography", "annotated", "annotation")):
            return Decimal("1.0000")
        if any(k in n for k in ("rewriting", "rewrite", "paraphras")):
            return Decimal("0.8000")
        if any(k in n for k in ("editing", "revision", "review")):
            return Decimal("0.5500")
        if any(k in n for k in ("proofreading", "formatting", "citation", "referencing")):
            return Decimal("0.4000")
        if any(k in n for k in ("tutoring", "consultation", "guidance", "coaching")):
            return Decimal("0.9000")
        return Decimal("1.0000")

    def _paper_type_mult(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("coding", "programming", "algorithm", "software design", "api doc", "code doc")):
            return Decimal("1.6500")
        if any(k in n for k in ("legal", "court", "brief", "motion", "law", "contract analysis", "bluebook", "oscola")):
            return Decimal("1.5500")
        if any(k in n for k in ("thesis", "dissertation", "doctoral", "phd", "prospectus", "qualifying exam")):
            return Decimal("1.4500")
        if any(k in n for k in ("technical", "engineering", "system design", "database design", "architecture", "requirements analysis", "test plan", "user manual", "technical manual", "technical spec")):
            return Decimal("1.3500")
        if any(k in n for k in ("data analysis", "statistical analysis", "meta-analysis", "systematic review")):
            return Decimal("1.3000")
        if any(k in n for k in ("nursing", "clinical", "soap note", "care plan", "nursing assessment", "nursing diagnosis", "discharge summary")):
            return Decimal("1.2500")
        if any(k in n for k in ("lab report",)):
            return Decimal("1.2000")
        if any(k in n for k in ("grant", "proposal", "scholarship", "funding")):
            return Decimal("1.2500")
        if any(k in n for k in ("admission", "personal statement", "statement of purpose")):
            return Decimal("1.1500")
        if any(k in n for k in ("research paper", "journal article", "conference paper", "scholarly", "academic paper", "research report")):
            return Decimal("1.1000")
        if any(k in n for k in ("case study", "feasibility", "market analysis", "swot", "cost-benefit", "risk analysis", "business case")):
            return Decimal("1.1000")
        if any(k in n for k in ("business", "marketing", "financial report", "management report")):
            return Decimal("1.0500")
        if any(k in n for k in ("literature review", "annotated bibliography")):
            return Decimal("1.0500")
        if any(k in n for k in ("proofreading", "formatting")):
            return Decimal("0.4500")
        if any(k in n for k in ("editing",)):
            return Decimal("0.5500")
        if any(k in n for k in ("paraphras", "rewriting", "rewrite")):
            return Decimal("0.7500")
        if any(k in n for k in ("creative", "fiction", "short story", "poetry", "poem", "screenplay", "script", "memoir", "novel")):
            return Decimal("0.9500")
        if any(k in n for k in ("reflection", "journal entry", "discussion post")):
            return Decimal("0.8500")
        if any(k in n for k in ("speech", "presentation script")):
            return Decimal("0.9000")
        return Decimal("1.0000")

    def _subject_category(self, name: str, is_technical: bool, cat_map: dict):
        n = name.lower()
        if any(k in n for k in ("programming", "software", "frontend", "backend", "full stack", "ios", "android", "sql", "devops", "data analytics", "big data", "deep learning", "natural language", "computer vision", "blockchain", "cryptography", "operating system", "computer architecture", "algorithms", "data structures", "information security", "health informatics", "web design", "machine learning", "artificial intelligence")):
            return cat_map.get("technology", cat_map.get("stem", list(cat_map.values())[0]))
        if any(k in n for k in ("nursing", "medicine", "medical", "health", "clinical", "pharmacology", "anatomy", "physiology", "pathology", "cardiology", "oncology", "neurology", "pediatric", "psychiatry", "dermatology", "orthopedic", "surgery", "dentistry", "dental", "audiology", "speech therapy", "veterinary", "biomedical", "epidemiology", "public health", "nutrition", "dietetics", "food science", "athletic training", "physical therapy", "occupational therapy")):
            return cat_map.get("nursing", cat_map.get("humanities", list(cat_map.values())[0]))
        if is_technical and any(k in n for k in ("engineering", "physics", "chemistry", "biology", "mathematics", "calculus", "algebra", "statistics", "probability", "geometry", "trigonometry", "biophysics", "biochemistry", "ecology", "marine", "oceanography", "astronomy", "aerospace", "aeronautic", "automotive", "petroleum", "nuclear")):
            return cat_map.get("stem", cat_map.get("humanities", list(cat_map.values())[0]))
        if any(k in n for k in ("law", "legal", "constitutional", "criminal", "civil law", "international law", "environmental law", "maritime law")):
            return cat_map.get("law", cat_map.get("humanities", list(cat_map.values())[0]))
        if any(k in n for k in ("business", "marketing", "finance", "accounting", "management", "economics", "entrepreneurship", "supply chain", "logistics", "hospitality", "hotel", "retail", "e-commerce", "investment", "auditing", "taxation")):
            return cat_map.get("business", cat_map.get("humanities", list(cat_map.values())[0]))
        if any(k in n for k in ("psychology", "sociology", "anthropology", "political", "geography", "communications", "journalism", "media", "social work", "education", "criminology", "gender studies", "women's studies", "african american", "asian american", "latin american", "middle eastern", "library science")):
            return cat_map.get("social_sci", cat_map.get("humanities", list(cat_map.values())[0]))
        return cat_map.get("humanities", list(cat_map.values())[0])

    def _section(self, title: str):
        self.stdout.write(f"\n{'─' * 62}")
        self.stdout.write(f"  {title}")
        self.stdout.write(f"{'─' * 62}")
