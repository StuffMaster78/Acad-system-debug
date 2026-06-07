"""
Seed sensible default pricing config for a website.

Usage:
    python manage.py seed_pricing_defaults [website_domain]
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


class Command(BaseCommand):
    help = "Seed default pricing profile, rates, and deadline tiers for a website"

    def add_arguments(self, parser):
        parser.add_argument("website_domain", nargs="?", default="localhost")

    def handle(self, *args, **options):
        Website = apps.get_model("websites", "Website")
        WebsitePricingProfile = apps.get_model("order_pricing_core", "WebsitePricingProfile")
        AcademicLevelRate = apps.get_model("order_pricing_core", "AcademicLevelRate")
        PaperTypeRate = apps.get_model("order_pricing_core", "PaperTypeRate")
        WorkTypeRate = apps.get_model("order_pricing_core", "WorkTypeRate")
        DeadlineRate = apps.get_model("order_pricing_core", "DeadlineRate")
        WriterLevelRate = apps.get_model("order_pricing_core", "WriterLevelRate")
        SubjectCategory = apps.get_model("order_pricing_core", "SubjectCategory")
        AnalysisLevelRate = apps.get_model("order_pricing_core", "AnalysisLevelRate")
        DiagramComplexityRate = apps.get_model("order_pricing_core", "DiagramComplexityRate")
        ServiceCatalogItem = apps.get_model("order_pricing_core", "ServiceCatalogItem")
        DesignOrderServiceConfig = apps.get_model("order_pricing_core", "DesignOrderServiceConfig")
        DiagramOrderServiceConfig = apps.get_model("order_pricing_core", "DiagramOrderServiceConfig")

        domain = options["website_domain"]
        try:
            website = Website.objects.get(domain=domain)
        except Website.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'No website with domain "{domain}"'))
            return

        self.stdout.write(f"\nSeeding pricing defaults for: {website.name} ({domain})\n")

        # ── Pricing profile ───────────────────────────────────────────────────
        self._section("PRICING PROFILE")
        profile, created = WebsitePricingProfile.objects.update_or_create(
            website=website,
            defaults=dict(
                profile_name="Default Pricing Profile",
                currency="USD",
                base_price_per_page=Decimal("14.00"),
                base_price_per_slide=Decimal("12.00"),
                base_price_per_diagram=Decimal("18.00"),
                double_spacing_multiplier=Decimal("1.0000"),
                single_spacing_multiplier=Decimal("2.0000"),
                preferred_writer_fee=Decimal("5.00"),
                minimum_paper_order_charge=Decimal("10.00"),
                minimum_design_order_charge=Decimal("15.00"),
                minimum_diagram_order_charge=Decimal("15.00"),
                max_pages_per_hour=1,
                extra_hour_per_extra_page=1,
                rush_recommendation_only=True,
                is_active=True,
            ),
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f" {verb} profile — $14/page · $12/slide · $18/diagram"
        ))

        # ── Academic level multipliers ─────────────────────────────────────────
        self._section("ACADEMIC LEVEL RATES")
        academic_levels = [
            ("high_school", "High School", Decimal("1.0000"), 1),
            ("college", "College", Decimal("1.1000"), 2),
            ("undergrad", "Undergraduate", Decimal("1.2000"), 3),
            ("bachelors", "Bachelor's", Decimal("1.2500"), 4),
            ("masters", "Master's", Decimal("1.5000"), 5),
            ("graduate", "Graduate", Decimal("1.4000"), 6),
            ("phd", "PhD / Doctorate", Decimal("1.8000"), 7),
            ("professional", "Professional", Decimal("1.6000"), 8),
        ]
        for code, label, multiplier, sort_order in academic_levels:
            _, created = AcademicLevelRate.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=multiplier, sort_order=sort_order),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {label} × {multiplier}"
            ))

        # ── Deadline tiers ─────────────────────────────────────────────────────
        self._section("DEADLINE TIERS")
        deadline_tiers = [
            ("3 Hours", 3, Decimal("3.0000"), 1),
            ("6 Hours", 6, Decimal("2.5000"), 2),
            ("12 Hours", 12, Decimal("2.0000"), 3),
            ("24 Hours", 24, Decimal("1.7000"), 4),
            ("2 Days", 48, Decimal("1.4000"), 5),
            ("3 Days", 72, Decimal("1.2000"), 6),
            ("5 Days", 120, Decimal("1.1000"), 7),
            ("7 Days", 168, Decimal("1.0000"), 8),
            ("10 Days", 240, Decimal("0.9500"), 9),
            ("14 Days", 336, Decimal("0.9000"), 10),
            ("20 Days", 480, Decimal("0.8500"), 11),
            ("30 Days", 720, Decimal("0.8000"), 12),
        ]
        # Clear existing deadline rates for a clean seed
        deleted, _ = DeadlineRate.objects.filter(website=website).delete()
        if deleted:
            self.stdout.write(f" Cleared {deleted} existing deadline tiers")
        for label, max_hours, multiplier, sort_order in deadline_tiers:
            DeadlineRate.objects.create(
                website=website,
                label=label,
                max_hours=max_hours,
                multiplier=multiplier,
                sort_order=sort_order,
            )
            self.stdout.write(self.style.SUCCESS(f" {label} (≤{max_hours}h) × {multiplier}"))

        # ── Paper type rates ───────────────────────────────────────────────────
        self._section("PAPER TYPE RATES (sample groups)")
        paper_type_rates = [
            ("essay", "Essay", Decimal("1.0000"), 1),
            ("research_paper", "Research Paper", Decimal("1.1000"), 2),
            ("thesis", "Thesis / Dissertation", Decimal("1.4000"), 3),
            ("case_study", "Case Study", Decimal("1.1000"), 4),
            ("lab_report", "Lab Report", Decimal("1.2000"), 5),
            ("presentation", "Presentation / Slides", Decimal("1.0000"), 6),
            ("business", "Business Writing", Decimal("1.0000"), 7),
            ("creative", "Creative Writing", Decimal("0.9000"), 8),
            ("nursing", "Nursing / Clinical", Decimal("1.2000"), 9),
            ("legal", "Legal Writing", Decimal("1.5000"), 10),
            ("technical", "Technical / Engineering", Decimal("1.3000"), 11),
            ("editing", "Editing / Proofreading", Decimal("0.7000"), 12),
            ("coding", "Coding / Programming", Decimal("1.6000"), 13),
        ]
        for code, label, multiplier, sort_order in paper_type_rates:
            _, created = PaperTypeRate.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=multiplier, sort_order=sort_order),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {label} × {multiplier}"
            ))

        # ── Work type rates ────────────────────────────────────────────────────
        self._section("WORK TYPE RATES")
        work_type_rates = [
            ("writing", "Writing", Decimal("1.0000"), 1),
            ("editing", "Editing", Decimal("0.6000"), 2),
            ("proofreading", "Proofreading", Decimal("0.5000"), 3),
            ("rewriting", "Rewriting", Decimal("0.8000"), 4),
            ("paraphrasing", "Paraphrasing", Decimal("0.7000"), 5),
            ("research", "Research", Decimal("1.0000"), 6),
            ("data_analysis", "Data Analysis", Decimal("1.3000"), 7),
            ("programming", "Programming", Decimal("1.6000"), 8),
            ("formatting", "Formatting", Decimal("0.4000"), 9),
            ("translation", "Translation", Decimal("1.1000"), 10),
        ]
        for code, label, multiplier, sort_order in work_type_rates:
            _, created = WorkTypeRate.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=multiplier, sort_order=sort_order),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {label} × {multiplier}"
            ))

        # ── Writer level rates (flat fee upsells) ─────────────────────────────
        self._section("WRITER LEVEL RATES")
        writer_levels = [
            ("standard", "Standard Writer", Decimal("0.00"), True, 1),
            ("advanced", "Advanced Writer", Decimal("5.00"), True, 2),
            ("top", "Top Writer", Decimal("10.00"), True, 3),
            ("expert", "Expert Writer", Decimal("15.00"), True, 4),
        ]
        for code, label, amount, is_flat_fee, sort_order in writer_levels:
            _, created = WriterLevelRate.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, amount=amount, is_flat_fee=is_flat_fee, sort_order=sort_order),
            )
            fee_str = f"+${amount}/page" if not is_flat_fee else f"+${amount} flat"
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {label} ({fee_str})"
            ))

        # ── Subject categories ─────────────────────────────────────────────────
        self._section("SUBJECT CATEGORIES")
        subject_categories = [
            ("humanities", "Humanities", Decimal("1.0000"), 1),
            ("social_sci", "Social Sciences", Decimal("1.0000"), 2),
            ("business", "Business", Decimal("1.0000"), 3),
            ("stem", "STEM", Decimal("1.2000"), 4),
            ("nursing", "Nursing & Health", Decimal("1.1000"), 5),
            ("law", "Law", Decimal("1.3000"), 6),
            ("technology", "Technology & CS", Decimal("1.4000"), 7),
        ]
        for code, label, multiplier, sort_order in subject_categories:
            _, created = SubjectCategory.objects.update_or_create(
                website=website, code=code,
                defaults=dict(label=label, multiplier=multiplier, sort_order=sort_order),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {label} × {multiplier}"
            ))

        # ── Analysis level rates ───────────────────────────────────────────────
        self._section("ANALYSIS LEVEL RATES")
        analysis_levels = [
            ("none", Decimal("1.0000")),
            ("basic", Decimal("1.2000")),
            ("advanced", Decimal("1.5000")),
        ]
        for level, multiplier in analysis_levels:
            _, created = AnalysisLevelRate.objects.update_or_create(
                website=website, level=level,
                defaults=dict(multiplier=multiplier),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {level.capitalize()} analysis × {multiplier}"
            ))

        # ── Diagram complexity rates ───────────────────────────────────────────
        self._section("DIAGRAM COMPLEXITY RATES")
        diagram_complexities = [
            ("simple", Decimal("1.0000")),
            ("moderate", Decimal("1.3000")),
            ("complex", Decimal("1.7000")),
        ]
        for complexity, multiplier in diagram_complexities:
            _, created = DiagramComplexityRate.objects.update_or_create(
                website=website, complexity=complexity,
                defaults=dict(multiplier=multiplier),
            )
            self.stdout.write(self.style.SUCCESS(
                f" {'' if created else '↻ '} {complexity.capitalize()} diagram × {multiplier}"
            ))

        # ── Service catalog defaults ──────────────────────────────────────────
        self._section("SERVICE CATALOG DEFAULTS")
        paper_count = self._seed_paper_services(
            website=website,
            ServiceCatalogItem=ServiceCatalogItem,
        )
        design_count = self._seed_design_services(
            website=website,
            ServiceCatalogItem=ServiceCatalogItem,
            DesignOrderServiceConfig=DesignOrderServiceConfig,
        )
        diagram_count = self._seed_diagram_services(
            website=website,
            ServiceCatalogItem=ServiceCatalogItem,
            DiagramOrderServiceConfig=DiagramOrderServiceConfig,
        )
        self.stdout.write(self.style.SUCCESS(
            f" {paper_count} paper, {design_count} design, {diagram_count} diagram services ready"
        ))

        # ── Paper type rates from order_configs ────────────────────────────────
        SubjectRate = apps.get_model("order_pricing_core", "SubjectRate")
        PaperType = apps.get_model("order_configs", "PaperType")
        Subject = apps.get_model("order_configs", "Subject")
        AcademicLevel = apps.get_model("order_configs", "AcademicLevel")
        TypeOfWork = apps.get_model("order_configs", "TypeOfWork")

        self._section("PAPER TYPE RATES (from order_configs)")
        pt_created = pt_updated = 0
        for pt in PaperType.objects.filter(website=website):
            multiplier = self._paper_type_multiplier(pt.name)
            _, created = PaperTypeRate.objects.update_or_create(
                website=website,
                code=pt.name,
                defaults=dict(label=pt.name, multiplier=multiplier, sort_order=0),
            )
            if created:
                pt_created += 1
            else:
                pt_updated += 1
        self.stdout.write(self.style.SUCCESS(
            f" {pt_created} created, {pt_updated} updated across {PaperType.objects.filter(website=website).count()} paper types"
        ))

        # ── Subject rates from order_configs ───────────────────────────────────
        self._section("SUBJECT RATES (from order_configs)")

        # Build category lookup by code
        cat_map = {c.code: c for c in SubjectCategory.objects.filter(website=website)}
        default_cat = cat_map.get("humanities")
        if not default_cat:
            self.stdout.write(self.style.WARNING(" No subject categories found — run seed without --skip-categories first"))
        else:
            sr_created = sr_updated = 0
            for subj in Subject.objects.filter(website=website):
                cat = self._subject_category(subj.name, subj.is_technical, cat_map)
                _, created = SubjectRate.objects.update_or_create(
                    website=website,
                    code=subj.name,
                    defaults=dict(label=subj.name, category=cat, sort_order=0),
                )
                if created:
                    sr_created += 1
                else:
                    sr_updated += 1
            self.stdout.write(self.style.SUCCESS(
                f" {sr_created} created, {sr_updated} updated across {Subject.objects.filter(website=website).count()} subjects"
            ))

        # ── Academic level rates from order_configs ────────────────────────────
        # The calculator looks up AcademicLevelRate by code=AcademicLevel.name
        # (via optionCode fallback). Seed one rate row per real AcademicLevel so
        # the quote engine never hits DoesNotExist for any valid selection.
        self._section("ACADEMIC LEVEL RATES (from order_configs)")
        al_created = al_updated = 0
        for al in AcademicLevel.objects.filter(website=website):
            multiplier = self._academic_level_multiplier(al.name)
            _, created = AcademicLevelRate.objects.update_or_create(
                website=website,
                code=al.name,
                defaults=dict(label=al.name, multiplier=multiplier, sort_order=0),
            )
            if created:
                al_created += 1
            else:
                al_updated += 1
        self.stdout.write(self.style.SUCCESS(
            f" {al_created} created, {al_updated} updated across {AcademicLevel.objects.filter(website=website).count()} academic levels"
        ))

        # ── Work type rates from order_configs ─────────────────────────────────
        # The calculator looks up WorkTypeRate by code=TypeOfWork.name.
        # Seed one rate row per real TypeOfWork so every valid selection resolves.
        self._section("WORK TYPE RATES (from order_configs)")
        wt_created = wt_updated = 0
        for tow in TypeOfWork.objects.filter(website=website):
            multiplier = self._work_type_multiplier(tow.name)
            _, created = WorkTypeRate.objects.update_or_create(
                website=website,
                code=tow.name,
                defaults=dict(label=tow.name, multiplier=multiplier, sort_order=0),
            )
            if created:
                wt_created += 1
            else:
                wt_updated += 1
        self.stdout.write(self.style.SUCCESS(
            f" {wt_created} created, {wt_updated} updated across {TypeOfWork.objects.filter(website=website).count()} work types"
        ))

        # ── Summary ────────────────────────────────────────────────────────────
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SUMMARY"))
        self.stdout.write("=" * 60)
        self.stdout.write(f" Pricing profile : 1")
        self.stdout.write(f" Academic levels : {AcademicLevelRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Deadline tiers : {DeadlineRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Paper type rates : {PaperTypeRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Work type rates : {WorkTypeRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Writer levels : {WriterLevelRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Subject categories: {SubjectCategory.objects.filter(website=website).count()}")
        self.stdout.write(f" Subject rates : {SubjectRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Analysis levels : {AnalysisLevelRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Diagram complexity: {DiagramComplexityRate.objects.filter(website=website).count()}")
        self.stdout.write(f" Paper services  : {ServiceCatalogItem.objects.filter(website=website, service_family=ServiceFamily.PAPER_ORDER).count()}")
        self.stdout.write(f" Design services : {ServiceCatalogItem.objects.filter(website=website, service_family=ServiceFamily.DESIGN_ORDER).count()}")
        self.stdout.write(f" Diagram services : {ServiceCatalogItem.objects.filter(website=website, service_family=ServiceFamily.DIAGRAM_ORDER).count()}")
        self.stdout.write(self.style.SUCCESS("\n Pricing defaults seeded successfully!\n"))

    def _seed_design_services(
        self,
        *,
        website,
        ServiceCatalogItem,
        DesignOrderServiceConfig,
    ) -> int:
        services = [
            {
                "service_code": "presentation_design",
                "name": "Presentation Design",
                "description": "Slide deck design priced per slide.",
                "pricing_unit": PricingUnit.SLIDE,
                "base_amount": Decimal("12.00"),
                "minimum_charge": Decimal("15.00"),
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
                "description": "Custom infographic design priced per item.",
                "pricing_unit": PricingUnit.ITEM,
                "base_amount": Decimal("45.00"),
                "minimum_charge": Decimal("45.00"),
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
                "description": "Poster, flyer, or one-page visual design.",
                "pricing_unit": PricingUnit.ITEM,
                "base_amount": Decimal("35.00"),
                "minimum_charge": Decimal("35.00"),
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
            item, _ = ServiceCatalogItem.objects.update_or_create(
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
            DesignOrderServiceConfig.objects.update_or_create(
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

    def _seed_diagram_services(
        self,
        *,
        website,
        ServiceCatalogItem,
        DiagramOrderServiceConfig,
    ) -> int:
        services = [
            {
                "service_code": "flowchart_diagram",
                "name": "Flowchart Diagram",
                "description": "Process, decision, or workflow diagram.",
                "diagram_type": DiagramType.FLOWCHART,
                "sort_order": 60,
            },
            {
                "service_code": "erd_diagram",
                "name": "Entity Relationship Diagram",
                "description": "Database ERD for entities and relationships.",
                "diagram_type": DiagramType.ERD,
                "sort_order": 61,
            },
            {
                "service_code": "uml_diagram",
                "name": "UML Diagram",
                "description": "UML-style class, sequence, or system diagram.",
                "diagram_type": DiagramType.UML,
                "sort_order": 62,
            },
            {
                "service_code": "system_diagram",
                "name": "System Architecture Diagram",
                "description": "Technical system or architecture diagram.",
                "diagram_type": DiagramType.SYSTEM_DIAGRAM,
                "sort_order": 63,
            },
        ]

        for data in services:
            diagram_type = data.pop("diagram_type")
            item, _ = ServiceCatalogItem.objects.update_or_create(
                website=website,
                service_code=data["service_code"],
                defaults={
                    **data,
                    "service_family": ServiceFamily.DIAGRAM_ORDER,
                    "pricing_strategy": PricingStrategy.FORMULA,
                    "pricing_unit": PricingUnit.DIAGRAM,
                    "base_amount": Decimal("18.00"),
                    "minimum_charge": Decimal("15.00"),
                    "is_public": True,
                    "is_active": True,
                },
            )
            DiagramOrderServiceConfig.objects.update_or_create(
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

    def _seed_paper_services(
        self,
        *,
        website,
        ServiceCatalogItem,
    ) -> int:
        services = [
            {
                "service_code": "academic_writing",
                "name": "Academic Writing",
                "description": "Standard academic paper, essay, or research writing service.",
                "sort_order": 10,
            },
            {
                "service_code": "standard_paper",
                "name": "Standard Paper",
                "description": "General paper writing priced per page.",
                "sort_order": 11,
            },
        ]
        for data in services:
            ServiceCatalogItem.objects.update_or_create(
                website=website,
                service_code=data["service_code"],
                defaults={
                    **data,
                    "service_family": ServiceFamily.PAPER_ORDER,
                    "pricing_strategy": PricingStrategy.FORMULA,
                    "pricing_unit": PricingUnit.PAGE,
                    "base_amount": Decimal("14.00"),
                    "minimum_charge": Decimal("10.00"),
                    "is_public": True,
                    "is_active": True,
                },
            )
        return len(services)

    def _academic_level_multiplier(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("phd", "doctorate", "doctoral")):
            return Decimal("1.8000")
        if any(k in n for k in ("professional", "md", "jd", "dds", "dvm", "edd", "dpt", "pharmd")):
            return Decimal("1.6000")
        if any(k in n for k in ("master", "graduate", "mba", "msc", "meng")):
            return Decimal("1.5000")
        if any(k in n for k in ("bachelor", "undergrad", "university")):
            return Decimal("1.2000")
        if any(k in n for k in ("college", "associate", "diploma", "certificate")):
            return Decimal("1.1000")
        if any(k in n for k in ("high school", "secondary", "a-level", "ib ")):
            return Decimal("1.0000")
        return Decimal("1.2000")

    def _work_type_multiplier(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("programming", "coding", "algorithm", "software", "development", "api", "database design", "system design", "data structure")):
            return Decimal("1.6000")
        if any(k in n for k in ("data analysis", "statistical", "quantitative", "qualitative", "research analysis", "financial analysis", "market research")):
            return Decimal("1.3000")
        if any(k in n for k in ("translation", "localiz")):
            return Decimal("1.1000")
        if any(k in n for k in ("research", "literature review", "bibliography", "annotated", "annotation")):
            return Decimal("1.0000")
        if any(k in n for k in ("rewriting", "rewrite", "paraphras")):
            return Decimal("0.8000")
        if any(k in n for k in ("editing", "revision", "review")):
            return Decimal("0.6000")
        if any(k in n for k in ("proofreading", "formatting", "citation", "referencing")):
            return Decimal("0.5000")
        if any(k in n for k in ("tutoring", "consultation", "guidance", "coaching")):
            return Decimal("0.9000")
        return Decimal("1.0000")

    def _paper_type_multiplier(self, name: str) -> Decimal:
        n = name.lower()
        if any(k in n for k in ("coding", "programming", "algorithm", "software design", "api doc", "code doc")):
            return Decimal("1.6000")
        if any(k in n for k in ("legal", "court", "brief", "motion", "law", "contract analysis", "bluebook", "oscola")):
            return Decimal("1.5000")
        if any(k in n for k in ("thesis", "dissertation", "doctoral", "phd", "prospectus", "qualifying exam", "preliminary exam")):
            return Decimal("1.4000")
        if any(k in n for k in ("technical", "engineering", "system design", "database design", "architecture", "requirements analysis", "test plan", "test report", "user manual", "technical manual", "technical spec")):
            return Decimal("1.3000")
        if any(k in n for k in ("nursing", "clinical", "soap note", "care plan", "nursing assessment", "nursing diagnosis", "discharge summary", "patient")):
            return Decimal("1.2000")
        if any(k in n for k in ("lab report", "data analysis", "statistical analysis", "qualitative analysis", "quantitative analysis", "meta-analysis", "systematic review")):
            return Decimal("1.2000")
        if any(k in n for k in ("research paper", "journal article", "conference paper", "scholarly", "academic paper", "research report")):
            return Decimal("1.1000")
        if any(k in n for k in ("case study", "feasibility", "market analysis", "swot", "cost-benefit", "risk analysis", "business case", "grant", "proposal")):
            return Decimal("1.1000")
        if any(k in n for k in ("proofreading", "formatting")):
            return Decimal("0.5000")
        if any(k in n for k in ("editing",)):
            return Decimal("0.6000")
        if any(k in n for k in ("paraphras", "rewriting", "rewrite")):
            return Decimal("0.7000")
        if any(k in n for k in ("creative", "fiction", "short story", "poetry", "poem", "screenplay", "script", "memoir", "novel")):
            return Decimal("0.9000")
        return Decimal("1.0000")

    def _subject_category(self, name: str, is_technical: bool, cat_map: dict):
        n = name.lower()
        # Technology & CS
        if any(k in n for k in ("programming", "software", "frontend", "backend", "full stack", "ios", "android",
                                 "sql", "devops", "data analytics", "big data", "deep learning", "natural language",
                                 "computer vision", "blockchain", "cryptography", "operating system", "computer architecture",
                                 "algorithms", "data structures", "information security", "health informatics", "web design")):
            return cat_map.get("technology", cat_map.get("stem", list(cat_map.values())[0]))
        # STEM (science & engineering, non-health)
        if is_technical and any(k in n for k in ("engineering", "physics", "chemistry", "biology", "mathematics",
                                                   "calculus", "algebra", "statistics", "probability", "geometry",
                                                   "trigonometry", "number theory", "topology", "biophysics",
                                                   "biochemistry", "ecology", "marine", "oceanography", "astronomy",
                                                   "aerospace", "aeronautic", "automotive", "petroleum", "nuclear")):
            return cat_map.get("stem", cat_map.get("humanities", list(cat_map.values())[0]))
        # Nursing & Health
        if any(k in n for k in ("nursing", "medicine", "medical", "health", "clinical", "pharmacology",
                                 "anatomy", "physiology", "pathology", "cardiology", "oncology", "neurology",
                                 "pediatric", "psychiatry", "dermatology", "orthopedic", "surgery", "dentistry",
                                 "dental", "audiology", "speech therapy", "veterinary", "biomedical",
                                 "epidemiology", "public health", "nutrition", "dietetics", "food science",
                                 "athletic training", "physical therapy", "occupational therapy")):
            return cat_map.get("nursing", cat_map.get("humanities", list(cat_map.values())[0]))
        # Law
        if any(k in n for k in ("law", "legal", "constitutional", "criminal", "civil law", "international law",
                                 "environmental law", "maritime law")):
            return cat_map.get("law", cat_map.get("humanities", list(cat_map.values())[0]))
        # Business
        if any(k in n for k in ("business", "marketing", "finance", "accounting", "management", "economics",
                                 "entrepreneurship", "supply chain", "logistics", "hospitality", "hotel",
                                 "retail", "e-commerce", "investment", "auditing", "taxation")):
            return cat_map.get("business", cat_map.get("humanities", list(cat_map.values())[0]))
        # Social Sciences
        if any(k in n for k in ("psychology", "sociology", "anthropology", "political", "geography",
                                 "communications", "journalism", "media", "social work", "education",
                                 "criminology", "gender studies", "women's studies", "african american",
                                 "asian american", "latin american", "middle eastern", "library science")):
            return cat_map.get("social_sci", cat_map.get("humanities", list(cat_map.values())[0]))
        # Humanities (default)
        return cat_map.get("humanities", list(cat_map.values())[0])

    def _section(self, title):
        self.stdout.write(f"\n{'─' * 60}")
        self.stdout.write(f" {title}")
        self.stdout.write(f"{'─' * 60}")
