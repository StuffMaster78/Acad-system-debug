"""
Management command: seed_gradecrest_blog
=========================================

Seeds GradeCrest blog with sample posts, categories, and an author so
the blog section renders end-to-end without any Wagtail admin setup.

Idempotent — skips objects that already exist by slug/name.

Usage:
    python manage.py seed_gradecrest_blog
    python manage.py seed_gradecrest_blog --site gradecrest.com
"""

from django.core.management.base import BaseCommand, CommandParser

AUTHOR = {
    "name": "GradeCrest Editorial Team",
    "slug": "gradecrest-editorial",
    "credentials": "Academic Writing Specialists",
    "bio": (
        "The GradeCrest Editorial Team comprises subject-matter experts, "
        "PhD-level academics, and professional academic writers who review "
        "and produce content across all disciplines. Our editorial standards "
        "require every article to be fact-checked, cited correctly, and "
        "reviewed for academic accuracy before publication."
    ),
}

CATEGORIES = [
    {"name": "Essay Writing", "slug": "essay-writing", "display_order": 1, "is_featured": True},
    {"name": "Research & Dissertations", "slug": "research-dissertations", "display_order": 2, "is_featured": True},
    {"name": "Study Tips", "slug": "study-tips", "display_order": 3},
    {"name": "Academic Skills", "slug": "academic-skills", "display_order": 4},
    {"name": "Nursing & Healthcare", "slug": "nursing-healthcare", "display_order": 5},
]

POSTS = [
    {
        "slug": "how-to-write-a-perfect-argumentative-essay",
        "title": "How to Write a Perfect Argumentative Essay: Structure, Examples & Tips",
        "seo_title": "How to Write an Argumentative Essay | Step-by-Step Guide | GradeCrest",
        "search_description": "Learn how to write a perfect argumentative essay with a clear thesis, strong evidence, and persuasive structure. Includes examples and a step-by-step guide.",
        "category_slug": "essay-writing",
        "excerpt": "An argumentative essay is one of the most common types of academic writing. This guide walks you through structure, evidence, counterarguments, and the exact formula top-scoring essays follow.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "An argumentative essay needs a clear, debatable thesis statement",
                    "Each body paragraph should make one claim, supported by evidence",
                    "Address counterarguments to strengthen your position",
                    "The conclusion should restate the thesis and synthesise — not summarise — your argument",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is an Argumentative Essay?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>An argumentative essay is a piece of academic writing in which you take a clear position on a debatable topic and defend that position using evidence, logic, and reasoning. Unlike a discursive essay — which presents multiple sides equally — an argumentative essay commits to one side and argues it persuasively.</p><p>It is one of the most commonly assigned essay types across all levels of university study, and mastering it will improve your performance in almost every written assessment you face.</p>"},
            {"type": "heading", "value": {"text": "The Classic 5-Paragraph Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most argumentative essays at undergraduate level follow a clear structure. While longer essays may expand on this, the logic remains the same.</p>"},
            {"type": "checklist", "value": {"heading": "Argumentative Essay Structure", "items": [
                {"text": "Introduction — hook, context, and a clear thesis statement"},
                {"text": "Body paragraph 1 — strongest claim with evidence and analysis"},
                {"text": "Body paragraph 2 — second claim with evidence and analysis"},
                {"text": "Body paragraph 3 — address the counterargument and refute it"},
                {"text": "Conclusion — restate thesis, synthesise arguments, broader implication"},
            ]}},
            {"type": "heading", "value": {"text": "Writing a Strong Thesis Statement", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The thesis statement is the most important sentence in your essay. It tells the reader exactly what you are arguing and why. A weak thesis makes a factual claim; a strong thesis makes a debatable argument.</p><p><strong>Weak:</strong> <em>Social media exists.</em><br><strong>Strong:</strong> <em>Social media platforms should be legally required to disclose algorithmic content curation to users because it directly affects political opinion formation and individual autonomy.</em></p><p>Your thesis should be specific, arguable, and reflect the full scope of your essay.</p>"},
            {"type": "heading", "value": {"text": "How to Use Evidence Correctly", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Evidence in an argumentative essay must come from credible, peer-reviewed sources. Each piece of evidence needs three elements: the evidence itself, a citation, and your analysis of why it supports your claim.</p><p>Avoid the common mistake of listing evidence without analysing it. Analysis is what earns marks — not the evidence itself.</p>"},
            {"type": "heading", "value": {"text": "Addressing Counterarguments", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A strong argumentative essay anticipates the strongest objection to its thesis and addresses it directly. This is not a sign of weakness — it demonstrates intellectual rigour and makes your argument more persuasive.</p><p>Use a concession-rebuttal structure: acknowledge the opposing view, then explain why your argument holds despite it.</p>"},
            {"type": "cta", "value": {
                "heading": "Need help with your argumentative essay?",
                "body": "GradeCrest connects you with expert writers who specialise in your subject. Every essay is written from scratch, cited correctly, and backed by our grade guarantee.",
                "button_text": "Get an essay written",
                "button_url": "/services/essay-writing",
                "style": "primary",
            }},
        ],
    },
    {
        "slug": "how-to-write-a-literature-review",
        "title": "How to Write a Literature Review: A Step-by-Step Guide for Students",
        "seo_title": "How to Write a Literature Review | Complete Guide | GradeCrest",
        "search_description": "A complete guide to writing a literature review: how to search for sources, synthesise findings, structure your review, and avoid the most common mistakes.",
        "category_slug": "research-dissertations",
        "excerpt": "A literature review is not a summary of sources — it is a critical synthesis of the field. This guide covers the structure, source selection, and synthesis techniques that distinguish good literature reviews from great ones.",
        "reading_time": 10,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A literature review synthesises sources — it does not just describe them",
                    "Organise thematically or methodologically, not chronologically by source",
                    "Every source included must be relevant to your research question",
                    "Identify gaps in the literature — this is where your research fits",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Literature Review?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A literature review is a critical, analytical survey of existing research on your topic. It identifies themes, debates, methodological approaches, and gaps in the literature — and positions your own research within that context.</p><p>Crucially, it is <strong>not</strong> an annotated bibliography. Listing sources one by one and describing them is the most common mistake students make. A real literature review weaves sources together into a coherent argument.</p>"},
            {"type": "heading", "value": {"text": "Types of Literature Review", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Before you begin, identify which type of review is appropriate for your assignment.</p>"},
            {"type": "checklist", "value": {"heading": "Literature Review Types", "items": [
                {"text": "Narrative review — synthesises a broad field; most common in humanities and social sciences"},
                {"text": "Systematic review — follows a strict protocol with PRISMA reporting; common in health sciences"},
                {"text": "Integrative review — combines quantitative and qualitative sources"},
                {"text": "Scoping review — maps the breadth of a topic rather than assessing quality"},
            ]}},
            {"type": "heading", "value": {"text": "How to Search for Sources", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Use academic databases rather than Google. The key databases are PubMed (health sciences), Scopus, Web of Science, JSTOR (humanities), and PsycINFO (psychology). Your institution's library portal usually provides access to all of these.</p><p>Define your search terms precisely. Use Boolean operators (AND, OR, NOT) to narrow or broaden results. Set date limits — most reviews prioritise sources from the last 10 years unless citing foundational or seminal work.</p>"},
            {"type": "heading", "value": {"text": "How to Structure Your Literature Review", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Organise thematically — group sources by the argument or finding they share, not by author or year. A typical structure:</p><ol><li>Introduction — state your research question and the scope of the review</li><li>Theme 1 — synthesise sources that address the first major strand of your topic</li><li>Theme 2 — a contrasting or complementary strand, with synthesis</li><li>Methodological considerations — note patterns in how research has been conducted</li><li>Gaps and your contribution — what the literature leaves unanswered</li></ol>"},
            {"type": "cta", "value": {
                "heading": "Need a literature review written by a subject expert?",
                "body": "Our writers hold postgraduate degrees and have conducted original research. Your literature review will be critically synthesised, correctly cited, and structured around your research question.",
                "button_text": "Order a literature review",
                "button_url": "/services/literature-review",
                "style": "primary",
            }},
        ],
    },
    {
        "slug": "dissertation-methodology-chapter-guide",
        "title": "How to Write the Methodology Chapter of Your Dissertation",
        "seo_title": "Dissertation Methodology Chapter — Complete Writing Guide | GradeCrest",
        "search_description": "How to write a dissertation methodology chapter: research design, data collection, analysis methods, ethical considerations, and what your supervisor is actually looking for.",
        "category_slug": "research-dissertations",
        "excerpt": "The methodology chapter is where your dissertation lives or dies. This guide covers research design, data collection methods, analysis approaches, and the critical detail most students miss.",
        "reading_time": 12,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "The methodology chapter explains how you conducted your research and why those choices were appropriate",
                    "Every methodological decision must be justified — not just described",
                    "Address limitations honestly — examiners expect them",
                    "Quantitative and qualitative methodologies have different conventions — know which applies to your study",
                ]
            }},
            {"type": "heading", "value": {"text": "What the Methodology Chapter Must Do", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The methodology chapter has one job: convince your examiner that your research design is appropriate for your research question, that you conducted the research rigorously, and that you understand the limitations of your approach.</p><p>Most students write their methodology as a description of what they did. That is necessary but not sufficient. Every section must include justification — why this research design, why these methods, why this sample size, why these analytical tools.</p>"},
            {"type": "heading", "value": {"text": "Research Philosophy and Paradigm", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most methodology chapters begin by situating the research within a philosophical paradigm. The two most common are positivism (reality is objective and measurable; typically associated with quantitative methods) and interpretivism (reality is socially constructed; typically associated with qualitative methods).</p><p>You do not need to write extensively about philosophy unless your examiner expects it — but you do need to show you understand which paradigm your study operates within and why.</p>"},
            {"type": "heading", "value": {"text": "Research Design", "level": "h2"}},
            {"type": "paragraph", "value": "<p>State your overall research design clearly: experimental, quasi-experimental, survey-based, case study, ethnographic, grounded theory, action research, or mixed methods. Each design choice should be justified in relation to your research question.</p>"},
            {"type": "heading", "value": {"text": "Data Collection Methods", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Describe precisely how you collected data. For quantitative studies: survey instruments, sampling method, sample size calculation, and data collection procedures. For qualitative studies: interview design, participant selection, data saturation rationale, and recording/transcription approach.</p><p>For both: include any pilot testing you conducted and what changes it resulted in.</p>"},
            {"type": "heading", "value": {"text": "Data Analysis", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Explain the analytical methods used and why they are appropriate. Quantitative studies should specify which statistical tests were used (with software), why those tests were selected given your data type, and how you checked assumptions. Qualitative studies should explain the analytical framework (thematic analysis, content analysis, grounded theory coding) and how themes were derived and verified.</p>"},
            {"type": "cta", "value": {
                "heading": "Struggling with your dissertation methodology?",
                "body": "Our PhD-qualified dissertation writers understand what examiners look for. We can write your methodology chapter from scratch or help you strengthen an existing draft.",
                "button_text": "Get dissertation help",
                "button_url": "/services/dissertations",
                "style": "primary",
            }},
        ],
    },
    {
        "slug": "how-to-write-a-nursing-care-plan",
        "title": "How to Write a Nursing Care Plan: NANDA Format, Examples & Tips",
        "seo_title": "How to Write a Nursing Care Plan | NANDA Format Guide | GradeCrest",
        "search_description": "Step-by-step guide to writing a nursing care plan using NANDA diagnoses, NOC outcomes, and NIC interventions. Includes examples and the exact format nursing schools require.",
        "category_slug": "nursing-healthcare",
        "excerpt": "A nursing care plan is a formal document that maps patient assessment to nursing diagnoses, outcomes, and interventions. This guide walks through the NANDA format with real examples.",
        "reading_time": 9,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A nursing care plan follows the NANDA-NOC-NIC framework in most programmes",
                    "Nursing diagnoses are not medical diagnoses — they address patient responses to health conditions",
                    "Each outcome must be measurable with a specific timeframe",
                    "Interventions must be evidence-based with rationale cited",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Nursing Care Plan?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A nursing care plan is a written document that organises a nurse's clinical thinking about a patient's needs. It connects the patient assessment to nursing diagnoses, desired outcomes, and specific evidence-based interventions.</p><p>In academic settings, care plans demonstrate your ability to apply clinical reasoning, use standardised nursing language (NANDA, NOC, NIC), and justify your clinical decisions with evidence.</p>"},
            {"type": "heading", "value": {"text": "The NANDA-NOC-NIC Framework", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most nursing programmes require care plans to use standardised taxonomies:</p><ul><li><strong>NANDA-I</strong> — North American Nursing Diagnosis Association International. Provides standardised nursing diagnoses (e.g., Impaired Gas Exchange, Risk for Falls)</li><li><strong>NOC</strong> — Nursing Outcomes Classification. Provides measurable patient outcomes linked to each diagnosis</li><li><strong>NIC</strong> — Nursing Interventions Classification. Provides standardised nursing actions to achieve each outcome</li></ul>"},
            {"type": "heading", "value": {"text": "Step 1: Patient Assessment", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Before writing a care plan, conduct a thorough patient assessment using a systematic framework such as head-to-toe or body systems. Document subjective data (what the patient reports) and objective data (what you observe and measure). Assessment data drives every subsequent component of the care plan.</p>"},
            {"type": "heading", "value": {"text": "Step 2: Formulate Nursing Diagnoses", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Select the 2–3 most important nursing diagnoses for your patient, prioritised using Maslow's hierarchy (physiological needs first). A nursing diagnosis is written in a three-part PES format: <strong>Problem</strong> (NANDA label) <strong>related to</strong> [Etiology] <strong>as evidenced by</strong> [Signs/Symptoms].</p><p>Example: <em>Impaired Gas Exchange related to alveolar-capillary membrane changes as evidenced by SpO₂ of 91%, confusion, and use of accessory muscles.</em></p>"},
            {"type": "cta", "value": {
                "heading": "Need your nursing care plan written by a registered nurse?",
                "body": "GradeCrest nursing writers are registered nurses with active clinical experience. They understand NANDA, NOC, NIC, and what your faculty expects.",
                "button_text": "Order nursing care plan",
                "button_url": "/services/nursing-essays",
                "style": "primary",
            }},
        ],
    },
    {
        "slug": "apa-7th-edition-citation-guide",
        "title": "APA 7th Edition Citation Guide: In-Text Citations, References & Examples",
        "seo_title": "APA 7th Edition Citation Guide — Complete Reference Examples | GradeCrest",
        "search_description": "Complete APA 7th edition guide with in-text citation formats, reference list examples for journals, books, websites, and the most common citation mistakes to avoid.",
        "category_slug": "academic-skills",
        "excerpt": "APA 7th edition is the most widely used citation style in psychology, education, nursing, and social sciences. This guide covers every format you need with real examples.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "APA 7th removed the publisher location from book references",
                    "DOIs are now formatted as hyperlinks (https://doi.org/...)",
                    "Use up to 20 authors in a reference list entry before using an ellipsis",
                    "Running heads are only required for manuscripts submitted for publication — not student papers",
                ]
            }},
            {"type": "heading", "value": {"text": "In-Text Citations", "level": "h2"}},
            {"type": "paragraph", "value": "<p>APA uses an author-date citation system. In-text citations include the author's surname and the publication year, separated by a comma.</p><p><strong>One author:</strong> (Smith, 2021)<br><strong>Two authors:</strong> (Smith &amp; Jones, 2021)<br><strong>Three or more:</strong> (Smith et al., 2021)<br><strong>Direct quote:</strong> (Smith, 2021, p. 45)</p>"},
            {"type": "heading", "value": {"text": "Journal Article References", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Author, A. A., &amp; Author, B. B. (Year). Title of article. <em>Journal Name</em>, <em>Volume</em>(Issue), page–page. https://doi.org/xxxxx</p><p><strong>Example:</strong><br>Nguyen, T., &amp; Williams, R. (2022). Academic self-efficacy and student outcomes in online learning environments. <em>Journal of Educational Psychology</em>, <em>114</em>(3), 412–428. https://doi.org/10.1037/edu0000683</p>"},
            {"type": "heading", "value": {"text": "Book References", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Author, A. A. (Year). <em>Title of work: Capital letter also for subtitle</em>. Publisher.</p><p><strong>Example:</strong><br>Brown, C. (2020). <em>The gilded age of academic writing: A critical history</em>. Oxford University Press.</p><p>Note: APA 7th no longer requires the publisher's city and state.</p>"},
            {"type": "heading", "value": {"text": "Website References", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Author, A. A. (Year, Month Day). <em>Title of page</em>. Site Name. URL</p><p><strong>Example:</strong><br>National Health Service. (2023, March 14). <em>Mental health statistics for England</em>. NHS. https://www.nhs.uk/mental-health/...</p><p>If there is no individual author, use the organisation name. If there is no date, write (n.d.) in place of the year.</p>"},
            {"type": "heading", "value": {"text": "Most Common APA 7th Mistakes", "level": "h2"}},
            {"type": "checklist", "value": {"heading": "Errors to avoid", "items": [
                {"text": "Using '&' in narrative text instead of 'and' (& is only used inside parentheses)"},
                {"text": "Missing DOI when one is available — always include it"},
                {"text": "Capitalising every word in an article title (only the first word and proper nouns are capitalised)"},
                {"text": "Using 'Retrieved from' before a URL — this was removed in APA 7th"},
                {"text": "Including the database name instead of the DOI"},
            ]}},
            {"type": "cta", "value": {
                "heading": "Need your paper formatted in APA 7th?",
                "body": "Every GradeCrest paper is formatted in your required citation style at no extra charge. Our editors check every reference before delivery.",
                "button_text": "Order an essay",
                "button_url": "/services/essay-writing",
                "style": "primary",
            }},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed GradeCrest blog with sample posts, categories, and an author"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="gradecrest.com")
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
        if created:
            self.stdout.write(self.style.SUCCESS(f"  CREATE author: {author.name}"))
        else:
            self.stdout.write(f"  EXISTS author: {author.name}")

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
            status = "CREATE" if created else "EXISTS"
            self.stdout.write(f"  {status}  category: {cat.name}")

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
        page.body = data.get("body", [])
