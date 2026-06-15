"""
Management command: seed_nursemygrade_blog
==========================================

Seeds NurseMyGrade blog with sample posts, categories, and an author so
the blog section renders end-to-end without any Wagtail admin setup.

Idempotent — skips objects that already exist by slug/name.

Usage:
    python manage.py seed_nursemygrade_blog
    python manage.py seed_nursemygrade_blog --site nursemygrade.com
    python manage.py seed_nursemygrade_blog --update
"""

from django.core.management.base import BaseCommand, CommandParser

AUTHOR = {
    "name": "NurseMyGrade Editorial Team",
    "slug": "nursemygrade-editorial",
    "credentials": "BSN · MSN · DNP Nurse Writers",
    "bio": (
        "The NurseMyGrade Editorial Team comprises registered nurses with active "
        "clinical experience across medical-surgical, critical care, mental health, "
        "and community nursing settings. All content is written and reviewed by "
        "nurses with BSN, MSN, or DNP qualifications. Every article meets NANDA, "
        "NOC, NIC, and APA 7th edition standards before publication."
    ),
}

CATEGORIES = [
    {"name": "Nursing Papers",       "slug": "nursing-papers",       "display_order": 1, "is_featured": True},
    {"name": "Capstone & Research",  "slug": "capstone-research",    "display_order": 2, "is_featured": True},
    {"name": "Citation & Format",    "slug": "citation-format",      "display_order": 3},
    {"name": "Clinical Simulations", "slug": "clinical-simulations", "display_order": 4},
    {"name": "Nursing School",       "slug": "nursing-school",       "display_order": 5},
]

POSTS = [
    {
        "slug": "how-to-write-a-nursing-care-plan-nanda",
        "title": "How to Write a Nursing Care Plan: NANDA, NOC & NIC Framework Explained",
        "seo_title": "How to Write a Nursing Care Plan | NANDA-NOC-NIC Guide | NurseMyGrade",
        "search_description": "Step-by-step guide to writing a nursing care plan using NANDA diagnoses, NOC outcomes, and NIC interventions — with examples and the exact format nursing programmes require.",
        "category_slug": "nursing-papers",
        "tags": ["nursing care plan", "NANDA", "NOC", "NIC", "nursing essay"],
        "excerpt": "A nursing care plan bridges patient assessment and clinical action. This guide walks through the NANDA-NOC-NIC framework, PES format for nursing diagnoses, and how to write measurable outcomes with confidence.",
        "reading_time": 10,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A nursing care plan follows the NANDA-I, NOC, NIC taxonomy in most nursing programmes",
                    "Nursing diagnoses are NOT medical diagnoses — they address patient responses to health problems",
                    "Use the PES format: Problem, Etiology, Signs/Symptoms (or Risk-Factor format for risk diagnoses)",
                    "Outcomes must be measurable and include a specific timeframe",
                    "Every intervention must be supported by evidence and include a rationale",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Nursing Care Plan?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A nursing care plan (NCP) is a formal written document that organises the nurse's clinical reasoning about a patient's needs. It maps patient assessment data to nursing diagnoses, desired patient outcomes, and evidence-based nursing interventions.</p><p>In academic settings, care plans demonstrate your ability to apply the nursing process (Assess, Diagnose, Plan, Implement, Evaluate — ADPIE), use standardised nursing language, and justify clinical decisions with peer-reviewed evidence.</p>"},
            {"type": "heading", "value": {"text": "The Three Core Taxonomies", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most nursing programmes require care plans to use three standardised classification systems:</p><ul><li><strong>NANDA-I</strong> (North American Nursing Diagnosis Association International) — provides approved nursing diagnosis labels, e.g., <em>Impaired Gas Exchange</em>, <em>Acute Pain</em>, <em>Risk for Falls</em></li><li><strong>NOC</strong> (Nursing Outcomes Classification) — provides measurable patient outcomes linked to each NANDA diagnosis</li><li><strong>NIC</strong> (Nursing Interventions Classification) — provides evidence-based nursing actions to achieve each NOC outcome</li></ul>"},
            {"type": "heading", "value": {"text": "Writing the Nursing Diagnosis (PES Format)", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The NANDA nursing diagnosis follows the PES three-part statement: <strong>P</strong>roblem (NANDA label) <strong>related to</strong> [Etiology/related factor] <strong>as evidenced by</strong> [Signs and symptoms from your assessment].</p><p><strong>Example — actual diagnosis:</strong><br><em>Impaired Gas Exchange related to alveolar-capillary membrane changes as evidenced by SpO₂ of 91% on room air, accessory muscle use, and patient-reported shortness of breath at rest.</em></p><p>For <strong>risk diagnoses</strong> (no signs/symptoms yet), use a two-part statement: <em>Risk for Falls related to impaired gait and confusion secondary to post-operative delirium.</em></p>"},
            {"type": "heading", "value": {"text": "Setting Measurable Outcomes", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Each outcome must meet SMART criteria within nursing: Specific (which patient behaviour?), Measurable (what number or observation confirms it?), Achievable (realistic for this patient?), Relevant (linked to the nursing diagnosis?), and Time-bound (by when?).</p><p><strong>Poor outcome:</strong> <em>Patient will breathe better.</em><br><strong>SMART outcome:</strong> <em>Patient will maintain SpO₂ ≥ 95% on 2L/min nasal cannula and report dyspnoea ≤ 2/10 within 48 hours of intervention.</em></p>"},
            {"type": "heading", "value": {"text": "Evidence-Based Interventions", "level": "h2"}},
            {"type": "paragraph", "value": "<p>For each NOC outcome, you need at least 3–5 NIC interventions with rationale. Rationale must be evidence-based — cite a peer-reviewed source or clinical guideline for each intervention. Do not write interventions without rationale; this is one of the most common reasons care plans lose marks.</p>"},
            {"type": "cta", "value": {
                "text": "Get your care plan written by a registered nurse",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "how-to-write-a-soap-note",
        "title": "How to Write a SOAP Note: Structure, Examples & Clinical Tips",
        "seo_title": "How to Write a SOAP Note | Nursing Format Guide | NurseMyGrade",
        "search_description": "A step-by-step guide to writing SOAP notes in nursing: Subjective, Objective, Assessment, and Plan — with clinical examples and tips to avoid common documentation errors.",
        "category_slug": "nursing-papers",
        "tags": ["SOAP note", "nursing documentation", "clinical writing", "nursing school"],
        "excerpt": "SOAP notes are the standard format for clinical documentation across nursing, medicine, and allied health. This guide explains each section, what to include, and the errors that undermine clinical credibility.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "SOAP stands for Subjective, Objective, Assessment, Plan",
                    "Subjective = what the patient tells you; Objective = what you observe and measure",
                    "The Assessment section requires clinical reasoning — not just a list of symptoms",
                    "The Plan must be specific: who does what, by when",
                ]
            }},
            {"type": "heading", "value": {"text": "S — Subjective", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The Subjective section records what the patient (or their carer) reports in their own words. Include the chief complaint, history of present illness, relevant past medical/surgical history, medications, allergies, and review of systems as reported by the patient.</p><p>Use direct quotes where the patient's exact words are clinically relevant: <em>\"The pain is like a burning in my chest, it started about two hours ago, 8/10.\"</em> Do not interpret or analyse here — that comes in the Assessment.</p>"},
            {"type": "heading", "value": {"text": "O — Objective", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The Objective section records all measurable, observable clinical data: vital signs, physical examination findings, laboratory results, imaging findings, and any other objective assessment data. This section should be factual and precise.</p><p><strong>Example:</strong> <em>BP 158/96 mmHg, HR 92 bpm regular, RR 22 breaths/min, T 37.2°C, SpO₂ 93% on room air. Chest auscultation: crackles bilateral bases. Peripheral oedema +2 bilateral lower extremities. BNP 1,240 pg/mL.</em></p>"},
            {"type": "heading", "value": {"text": "A — Assessment", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The Assessment is your clinical interpretation of the subjective and objective data. In nursing SOAP notes, this translates to your nursing diagnoses (using NANDA-I labels where required) prioritised by Maslow's hierarchy of needs.</p><p>This is the most intellectually demanding part of the note. You are not listing problems — you are synthesising data into a clinical picture and identifying the patient's priority nursing needs.</p>"},
            {"type": "heading", "value": {"text": "P — Plan", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The Plan outlines your nursing interventions, patient education, referrals, and follow-up. Each plan item should be actionable, with timeframes and responsible parties where appropriate. Include patient education topics and any referrals (dietitian, physiotherapy, social work).</p><p>The Plan should directly address each nursing diagnosis listed in the Assessment — if a problem is in the Assessment, there must be a corresponding plan.</p>"},
            {"type": "cta", "value": {
                "text": "Get your SOAP note written by a nurse",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "nursing-capstone-project-guide",
        "title": "How to Write a Nursing Capstone Project: From Topic to Submission",
        "seo_title": "Nursing Capstone Project Guide — Topic, Structure & Tips | NurseMyGrade",
        "search_description": "A complete guide to writing a nursing capstone project: choosing a clinical problem, using evidence-based practice frameworks, structuring your paper, and meeting programme requirements.",
        "category_slug": "capstone-research",
        "tags": ["nursing capstone", "evidence-based practice", "EBP", "nursing research", "BSN capstone"],
        "excerpt": "A nursing capstone is a comprehensive evidence-based project that integrates clinical knowledge and research skills. This guide covers topic selection, the PICOT question framework, and how to structure your capstone for maximum marks.",
        "reading_time": 12,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A nursing capstone project applies evidence-based practice to a real clinical problem",
                    "The PICOT question framework structures your research question: Population, Intervention, Comparison, Outcome, Time",
                    "A literature search of at least 5–10 peer-reviewed sources published within the last 5 years is typically required",
                    "Many programmes require an implementation plan — not just a literature review",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Nursing Capstone Project?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A nursing capstone project is the culminating academic requirement of most BSN and MSN programmes. It demonstrates your ability to identify a clinical practice problem, search and appraise the evidence, synthesise research findings, and propose (or implement) an evidence-based solution.</p><p>Capstone formats vary: some programmes require a written paper, others a poster, a quality improvement project, or a practice change proposal. Check your programme handbook for the exact format and marking criteria.</p>"},
            {"type": "heading", "value": {"text": "Choosing a Capstone Topic", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Choose a topic grounded in a genuine clinical problem you have observed in practice. The best capstone topics: are specific (not 'nurse burnout' but 'the effect of mindfulness-based interventions on burnout scores in ICU nurses in medium-sized UK hospitals'), have a sufficient evidence base, and are relevant to your clinical area or speciality.</p><p>Avoid topics so broad they cannot be addressed in your word count, or so narrow that there is insufficient published research to draw on.</p>"},
            {"type": "heading", "value": {"text": "Formulating the PICOT Question", "level": "h2"}},
            {"type": "paragraph", "value": "<p>PICOT structures your research question so it can drive a systematic literature search:</p><ul><li><strong>P — Population:</strong> Which patients or clinical group? Be specific about age, condition, setting.</li><li><strong>I — Intervention:</strong> What nursing intervention or practice change are you investigating?</li><li><strong>C — Comparison:</strong> What is the current practice or an alternative intervention?</li><li><strong>O — Outcome:</strong> What measurable outcome are you trying to achieve or improve?</li><li><strong>T — Time:</strong> Over what time frame would the outcome be measured?</li></ul><p><strong>Example PICOT:</strong> <em>In adult patients on mechanical ventilation in ICU settings (P), does implementation of a structured oral hygiene protocol using chlorhexidine gluconate (I) compared to standard mouth swabs (C) reduce the incidence of ventilator-associated pneumonia (O) within a 30-day post-intubation period (T)?</em></p>"},
            {"type": "heading", "value": {"text": "Searching and Appraising the Literature", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Use CINAHL, PubMed, Cochrane Library, and MEDLINE for nursing research. Set date limits (typically 5 years) unless citing foundational studies. Use Boolean operators (AND, OR) with your PICOT terms as search keywords.</p><p>Appraise each source using an appropriate tool: CASP checklists for different study designs (RCT, cohort, qualitative), or the Johns Hopkins Nursing Evidence-Based Practice appraisal tools.</p>"},
            {"type": "cta", "value": {
                "text": "Get your nursing capstone written by an MSN/DNP nurse",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "apa-7th-edition-nursing-referencing",
        "title": "APA 7th Edition for Nursing Students: In-Text Citations and Reference List",
        "seo_title": "APA 7th Edition Nursing Guide — Citations & Reference List | NurseMyGrade",
        "search_description": "APA 7th edition referencing guide for nursing students: in-text citation formats, reference list examples for journals, clinical guidelines, and government health websites.",
        "category_slug": "citation-format",
        "tags": ["APA 7th edition", "nursing citation", "referencing", "nursing essay"],
        "excerpt": "APA 7th edition is the standard citation format for nursing in the UK, US, and Australia. This guide covers the exact formats for journal articles, clinical guidelines, NHS sources, and the most common mistakes nursing students make.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "APA 7th uses author-date in-text citations: (Author, Year) or (Author, Year, p. page)",
                    "Journal articles must include the DOI formatted as a URL: https://doi.org/...",
                    "Clinical guidelines (NICE, WHO, NMC) are cited as organisational authors",
                    "Running heads are NOT required in student papers — only in manuscripts submitted for publication",
                ]
            }},
            {"type": "heading", "value": {"text": "In-Text Citations in Nursing Papers", "level": "h2"}},
            {"type": "paragraph", "value": "<p>APA 7th uses an author-date system. Every in-text citation includes the author's surname and year of publication:</p><ul><li><strong>Paraphrase:</strong> (Smith, 2022)</li><li><strong>Direct quote:</strong> (Smith, 2022, p. 45)</li><li><strong>Two authors:</strong> (Smith &amp; Jones, 2022)</li><li><strong>Three or more:</strong> (Smith et al., 2022)</li><li><strong>Organisation:</strong> (National Institute for Health and Care Excellence [NICE], 2023) — abbreviate to (NICE, 2023) on subsequent citations</li></ul>"},
            {"type": "heading", "value": {"text": "Journal Article References", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Author, A. A., &amp; Author, B. B. (Year). Article title in sentence case. <em>Journal Name in Title Case and Italic</em>, <em>Volume</em>(Issue), start page–end page. https://doi.org/xxxxx</p><p><strong>Example:</strong><br>McGowan, J., &amp; Clarke, S. (2021). Nurse-led early warning score interventions and patient outcomes: A systematic review. <em>Journal of Advanced Nursing</em>, <em>77</em>(4), 1820–1834. https://doi.org/10.1111/jan.14748</p>"},
            {"type": "heading", "value": {"text": "Clinical Guideline References (NICE, WHO)", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Organisation Name. (Year). <em>Title of guideline</em> (Guideline identifier if applicable). Publisher. URL</p><p><strong>NICE example:</strong><br>National Institute for Health and Care Excellence. (2023). <em>Sepsis: Recognition, diagnosis and early management</em> (NICE guideline NG51). NICE. https://www.nice.org.uk/guidance/ng51</p><p><strong>WHO example:</strong><br>World Health Organization. (2022). <em>Global patient safety action plan 2021–2030</em>. WHO. https://www.who.int/publications/i/item/9789240032705</p>"},
            {"type": "heading", "value": {"text": "Common APA Mistakes in Nursing Papers", "level": "h2"}},
            {"type": "checklist", "value": {"heading": "Errors to avoid", "items": [
                {"text": "Using 'Retrieved from' before a URL — removed in APA 7th edition"},
                {"text": "Missing the DOI — always include it if one exists"},
                {"text": "Capitalising every word in an article title — only the first word and proper nouns"},
                {"text": "Adding the database name (CINAHL, PubMed) instead of the DOI"},
                {"text": "Using '&' in narrative text — '&' is only used inside parentheses"},
            ]}},
            {"type": "cta", "value": {
                "text": "Get your nursing paper formatted correctly",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "nursing-school-time-management",
        "title": "Time Management for Nursing Students: How to Survive (and Thrive) in BSN",
        "seo_title": "Time Management for Nursing Students | BSN Study Guide | NurseMyGrade",
        "search_description": "Practical time management strategies for nursing students juggling clinical placements, coursework, and exams — including study schedules, exam preparation, and how to avoid burnout.",
        "category_slug": "nursing-school",
        "tags": ["nursing school", "time management", "BSN tips", "nursing student", "study tips"],
        "excerpt": "Nursing school is relentless — clinical placements, written assignments, OSCEs, and exams all run simultaneously. This guide covers the time management systems that actually work for BSN and MSN students.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "Block scheduling (fixed study blocks) works better than flexible 'study when I can' approaches",
                    "Prioritise active recall and spaced repetition over re-reading for pharmacology and pathophysiology",
                    "Build non-negotiable rest into your schedule — fatigue causes clinical errors, not just academic ones",
                    "Assignment writing and clinical preparation require different cognitive modes — do not mix them",
                ]
            }},
            {"type": "heading", "value": {"text": "Why Nursing School Time Management Is Different", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most university students manage lectures, assignments, and exams. Nursing students manage all of that plus clinical placements that can run 12-hour shifts, mandatory supernumerary time requirements, skills sign-offs, NMC proficiency standards, reflective practice portfolios, and OSCEs. The volume is not comparable to most other undergraduate programmes.</p><p>Generic student time management advice rarely accounts for this. What follows is specific to nursing students.</p>"},
            {"type": "heading", "value": {"text": "Block Scheduling for Clinical and Academic Weeks", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most effective approach is to treat your week as two distinct types: clinical weeks (placement) and academic weeks (university). In clinical weeks, your primary obligation is placement. Use mornings before shifts and evenings after (when you have energy) for 30–45 minute review of that day's clinical encounters. In academic weeks, use block scheduling: fixed 2–3 hour deep-work blocks in the morning for assignments and new learning, with revision and lighter tasks in the afternoon.</p>"},
            {"type": "heading", "value": {"text": "Studying Pharmacology and Pathophysiology", "level": "h2"}},
            {"type": "paragraph", "value": "<p>These two subjects require retention, not comprehension. Re-reading notes does not build retention — active recall does. Use Anki (free flashcard software with spaced repetition) for drug classes, mechanisms, side effects, and nursing considerations. 20 minutes of Anki daily during clinical placement keeps content fresh without requiring long study sessions.</p><p>For pathophysiology, build concept maps that connect aetiology → pathophysiology → clinical presentation → nursing assessment → nursing diagnoses. Seeing the connections helps retention far more than linear notes.</p>"},
            {"type": "heading", "value": {"text": "Managing Assignment Deadlines During Placement", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Never leave assignment writing until after placement ends. You will be too fatigued. Instead: outline your assignment and complete the literature search before placement begins, write 300–400 words per day on non-shift days during placement (even on placement days, 15 minutes of writing maintains momentum), and leave the final week before the deadline for editing, not first draft writing.</p>"},
            {"type": "cta", "value": {
                "text": "Need nursing coursework written by a nurse?",
                "url": "/order",
            }},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed NurseMyGrade blog with sample posts, categories, and an author"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="nursemygrade.com")
        parser.add_argument("--update", action="store_true", help="Update existing posts")

    def handle(self, *args, **options):
        from wagtail.models import Site
        from cms_core.models import BlogCategory
        from cms_authors.models import Author
        from cms_blog.models import BlogIndexPage, BlogPostPage

        hostname = options["site"]
        do_update = options["update"]

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No site for '{hostname}'. Run setup_tenants first."))
            return

        blog_index = BlogIndexPage.objects.child_of(site.root_page).first()
        if not blog_index:
            self.stderr.write(self.style.ERROR("No BlogIndexPage found. Run setup_tenants first."))
            return

        # 1 — Author
        author, created = Author.objects.get_or_create(
            site=site,
            slug=AUTHOR["slug"],
            defaults={
                "name": AUTHOR["name"],
                "credentials": AUTHOR["credentials"],
                "bio": AUTHOR["bio"],
            },
        )
        self.stdout.write(self.style.SUCCESS(f"  {'CREATE' if created else 'EXISTS'} author: {author.name}"))

        # 2 — Categories
        cat_map: dict[str, BlogCategory] = {}
        for cat_data in CATEGORIES:
            cat, created = BlogCategory.objects.get_or_create(
                site=site,
                slug=cat_data["slug"],
                defaults={
                    "name": cat_data["name"],
                    "display_order": cat_data.get("display_order", 0),
                    "is_featured": cat_data.get("is_featured", False),
                },
            )
            cat_map[cat_data["slug"]] = cat
            self.stdout.write(f"  {'CREATE' if created else 'EXISTS'}  category: {cat.name}")

        # 3 — Posts
        existing_slugs = set(
            BlogPostPage.objects.child_of(blog_index).values_list("slug", flat=True)
        )
        created_count = updated = skipped = 0

        for post_data in POSTS:
            slug = post_data["slug"]
            category = cat_map.get(post_data["category_slug"])

            if slug in existing_slugs:
                if not do_update:
                    self.stdout.write(f"  SKIP  post: {slug}")
                    skipped += 1
                    continue
                page = BlogPostPage.objects.child_of(blog_index).get(slug=slug)
                self._apply_fields(page, post_data, author, category)
                page.save_revision().publish()
                self._apply_tags(page, post_data, site)
                self.stdout.write(self.style.WARNING(f"  UPDATE post: {slug}"))
                updated += 1
            else:
                page = BlogPostPage(
                    title=post_data["title"],
                    slug=slug,
                    live=True,
                    primary_author=author,
                )
                self._apply_fields(page, post_data, author, category)
                blog_index.add_child(instance=page)
                page.save_revision().publish()
                self._apply_tags(page, post_data, site)
                self.stdout.write(self.style.SUCCESS(f"  CREATE post: {slug}"))
                created_count += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done — {created_count} created, {updated} updated, {skipped} skipped"
        ))

    def _apply_fields(self, page, data, author, category):
        page.title = data["title"]
        page.seo_title = data.get("seo_title", "")
        page.search_description = data.get("search_description", "")
        page.excerpt = data.get("excerpt", "")
        page.primary_author = author
        page.category = category
        page.citation_mode = "sources_list"
        page.body = [self._normalize_block(b) for b in data.get("body", [])]

    @staticmethod
    def _apply_tags(page, data, site):
        from cms_core.models import BlogTag
        from django.utils.text import slugify
        tag_names = data.get("tags", [])
        if not tag_names:
            return
        page.tags.clear()
        for name in tag_names:
            tag, _ = BlogTag.objects.get_or_create(
                site=site, slug=slugify(name), defaults={"name": name}
            )
            page.tags.add(tag)

    @staticmethod
    def _normalize_block(block: dict) -> dict:
        t = block.get("type")
        raw = block.get("value")

        if not isinstance(raw, dict):
            return {"type": t, "value": raw}

        v = dict(raw)

        if t == "checklist":
            if "heading" in v and "title" not in v:
                v["title"] = v.pop("heading")
            v["items"] = [
                item if isinstance(item, dict) and "detail" in item
                else {"text": item.get("text", item) if isinstance(item, dict) else item, "detail": ""}
                for item in v.get("items", [])
            ]

        elif t == "cta":
            if "button_text" in v:
                v["text"] = v.pop("button_text")
            if "button_url" in v:
                v["url"] = v.pop("button_url")
            v = {k: v[k] for k in ("text", "url", "style") if k in v}

        return {"type": t, "value": v}
