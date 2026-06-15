"""
Management command: seed_essaymaniacs_blog
==========================================

Seeds EssayManiacs blog with sample posts, categories, and an author so
the blog section renders end-to-end without any Wagtail admin setup.

Idempotent — skips objects that already exist by slug/name.

Usage:
    python manage.py seed_essaymaniacs_blog
    python manage.py seed_essaymaniacs_blog --site essaymaniacs.com
    python manage.py seed_essaymaniacs_blog --update
"""

from django.core.management.base import BaseCommand, CommandParser

AUTHOR = {
    "name": "EssayManiacs Editorial Team",
    "slug": "essaymaniacs-editorial",
    "credentials": "Academic Writing Specialists",
    "bio": (
        "The EssayManiacs Editorial Team is made up of subject-specialist writers, "
        "editors with postgraduate degrees, and academic coaches who have produced "
        "thousands of essays, research papers, and dissertations across every "
        "discipline. Every article is fact-checked and reviewed for academic accuracy "
        "before publication."
    ),
}

CATEGORIES = [
    {"name": "Essays",         "slug": "essays",          "display_order": 1, "is_featured": True},
    {"name": "Research Papers","slug": "research-papers", "display_order": 2, "is_featured": True},
    {"name": "Dissertations",  "slug": "dissertations",   "display_order": 3},
    {"name": "Academic Tips",  "slug": "academic-tips",   "display_order": 4},
]

POSTS = [
    {
        "slug": "how-to-write-a-perfect-essay-introduction",
        "title": "How to Write an Essay Introduction That Hooks Your Reader",
        "seo_title": "How to Write an Essay Introduction | Hook, Context & Thesis | EssayManiacs",
        "search_description": "Learn how to write a compelling essay introduction with a strong hook, background context, and a clear thesis statement. Includes examples and common mistakes to avoid.",
        "category_slug": "essays",
        "tags": ["essay introduction", "thesis statement", "essay writing", "academic writing"],
        "excerpt": "Your introduction sets the tone for your entire essay. This guide covers the three-part structure every strong introduction needs — and the mistakes that cost students marks.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A strong introduction has three parts: a hook, background context, and a thesis statement",
                    "Your thesis statement must be specific, debatable, and preview your essay's argument",
                    "Never start with a dictionary definition or a sweeping generalisation",
                    "The introduction should be 10–15% of the total essay word count",
                ]
            }},
            {"type": "heading", "value": {"text": "The Three-Part Introduction Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Every effective essay introduction has three components that flow into each other: the hook, the contextual background, and the thesis statement. Skipping or weakening any of them damages the rest of the essay before the reader has even reached your first argument.</p>"},
            {"type": "heading", "value": {"text": "1. The Hook", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The hook is the opening sentence (or two) that earns the reader's attention. It can be a startling statistic, a provocative question, a brief anecdote, or a counterintuitive claim. The hook must be directly relevant to your essay topic — never generic.</p><p><strong>Weak hook:</strong> <em>Since the beginning of time, humans have argued about justice.</em><br><strong>Strong hook:</strong> <em>In 2023, UK courts overturned 89 wrongful convictions — each one a product of the very justice system designed to prevent them.</em></p>"},
            {"type": "heading", "value": {"text": "2. Background Context", "level": "h2"}},
            {"type": "paragraph", "value": "<p>After the hook, provide 2–3 sentences of background that establish the topic's significance and narrow the reader's focus toward your specific argument. This is not the place for your full argument — just enough context to make your thesis make sense.</p>"},
            {"type": "heading", "value": {"text": "3. The Thesis Statement", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Your thesis statement is the final sentence of the introduction and the most important sentence in the essay. It states your main argument, not just your topic. A thesis about climate change is not <em>\"Climate change is a serious problem.\"</em> A thesis is <em>\"Carbon pricing, not voluntary corporate pledges, is the only policy mechanism with a proven track record of reducing industrial emissions at scale.\"</em></p>"},
            {"type": "checklist", "value": {"heading": "Thesis Checklist", "items": [
                {"text": "Is it a complete sentence (not a question)?"},
                {"text": "Does it make a specific, arguable claim — not a statement of fact?"},
                {"text": "Does it preview the structure or key arguments of the essay?"},
                {"text": "Does it appear as the final sentence of the introduction?"},
            ]}},
            {"type": "cta", "value": {
                "text": "Get your essay written by a specialist",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "essay-structure-complete-guide",
        "title": "Essay Structure: A Complete Guide to Body Paragraphs and Flow",
        "seo_title": "Essay Structure Guide — Body Paragraphs, Transitions & Flow | EssayManiacs",
        "search_description": "How to structure body paragraphs using the PEEL method, create smooth transitions between arguments, and maintain logical flow throughout your essay.",
        "category_slug": "essays",
        "tags": ["essay structure", "PEEL", "body paragraphs", "academic writing"],
        "excerpt": "Good essay structure is what separates a high mark from a pass. This guide explains the PEEL paragraph method, transitions, and how to build an essay that reads as a coherent argument rather than a list of ideas.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "Each body paragraph should make exactly one main claim and support it fully before moving on",
                    "The PEEL structure (Point, Evidence, Explain, Link) gives every paragraph a logical shape",
                    "Transitions between paragraphs show how ideas connect — they are not optional",
                    "The final paragraph before the conclusion should be your strongest argument",
                ]
            }},
            {"type": "heading", "value": {"text": "The PEEL Paragraph Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>PEEL is the most widely taught paragraph structure in UK universities, and for good reason: it forces you to complete each component before moving on. Many students write paragraphs that are 80% evidence and 10% explanation — PEEL prevents this.</p>"},
            {"type": "checklist", "value": {"heading": "PEEL Method", "items": [
                {"text": "Point — state the single claim this paragraph makes (topic sentence)"},
                {"text": "Evidence — provide 1–2 pieces of cited evidence that support the claim"},
                {"text": "Explain — analyse why the evidence supports your point (this is where the marks are)"},
                {"text": "Link — connect back to the thesis or forward to the next paragraph"},
            ]}},
            {"type": "heading", "value": {"text": "How Long Should a Body Paragraph Be?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A body paragraph should typically be 150–250 words in a 1,500–2,000 word essay. In longer essays (3,000+), paragraphs can extend to 300–400 words if the argument demands it. Paragraphs shorter than 100 words usually indicate underdeveloped analysis. Paragraphs longer than 400 words usually need splitting.</p>"},
            {"type": "heading", "value": {"text": "Writing Effective Transitions", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Transitions show the logical relationship between paragraphs. They are not decorative — they are part of the argument. Avoid lazy transitions like <em>\"Furthermore,\"</em> at the start of every paragraph. Instead, write transitions that explicitly show how the new paragraph relates to the one before it.</p><p><strong>Weak:</strong> <em>Furthermore, social media affects mental health.</em><br><strong>Strong:</strong> <em>While social media's effect on attention spans is well-documented, its impact on self-reported wellbeing is more contested — and the evidence suggests the relationship is bidirectional rather than causal.</em></p>"},
            {"type": "cta", "value": {
                "text": "Have a specialist write your essay",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "how-to-write-a-research-paper",
        "title": "How to Write a Research Paper: Structure, Sources & Submission",
        "seo_title": "How to Write a Research Paper — Step-by-Step Guide | EssayManiacs",
        "search_description": "A complete guide to writing a research paper: choosing a topic, finding credible sources, structuring your argument, citing correctly, and polishing for submission.",
        "category_slug": "research-papers",
        "tags": ["research paper", "academic research", "citation", "essay writing"],
        "excerpt": "A research paper is more formal and source-intensive than a standard essay. This guide walks through every stage — from choosing a topic to final submission — with practical techniques at each step.",
        "reading_time": 11,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A research paper requires primary and secondary sources, not just one or two citations",
                    "Begin with a focused research question — not a broad topic",
                    "Every claim that is not common knowledge must be cited",
                    "Structure follows IMRaD (Introduction, Methods, Results, Discussion) in sciences; thematic in humanities",
                ]
            }},
            {"type": "heading", "value": {"text": "Choosing and Narrowing Your Topic", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The single most common mistake in research papers is starting with a topic that is too broad. <em>\"Climate change\"</em> is a subject area, not a research topic. <em>\"The effectiveness of carbon pricing mechanisms in reducing industrial CO₂ emissions in EU member states, 2015–2023\"</em> is a research topic: it is specific, measurable, and bounded in scope.</p><p>A useful test: if your research question could fill a whole textbook, it needs narrowing. You should be able to fully address your question in the word count you have.</p>"},
            {"type": "heading", "value": {"text": "Finding and Evaluating Sources", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Use academic databases: Google Scholar, JSTOR, PubMed, Scopus, Web of Science. Your institution's library portal provides access to most. Avoid Wikipedia as a source — but do use its reference list to find primary sources.</p><p>Evaluate each source using the CRAAP test: Currency (when was it published?), Relevance (does it address your question?), Authority (who wrote it? what are their credentials?), Accuracy (is it peer-reviewed?), Purpose (why was it written?).</p>"},
            {"type": "heading", "value": {"text": "Research Paper Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Sciences follow IMRaD: Introduction (why this question matters and what is already known), Methods (how the research was conducted), Results (what was found), and Discussion (what it means). Humanities and social sciences typically use a thematic structure: introduction, themed argument sections, and conclusion.</p><p>Check your assignment brief and any sample papers your lecturer has provided — they will confirm which format is expected.</p>"},
            {"type": "heading", "value": {"text": "Citing Sources Correctly", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Every factual claim you make that is not common knowledge needs a citation. This includes statistics, research findings, definitions from specific sources, and any idea that originated with another author. Most research papers use APA 7th, MLA 9th, or Harvard — check your assignment brief.</p><p>Use a reference manager (Zotero is free and excellent) to keep track of sources as you read. Trying to reconstruct references at the end of the writing process wastes hours and introduces errors.</p>"},
            {"type": "cta", "value": {
                "text": "Get your research paper written",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "dissertation-proposal-guide",
        "title": "How to Write a Dissertation Proposal That Gets Approved",
        "seo_title": "Dissertation Proposal Guide — Structure, Tips & Examples | EssayManiacs",
        "search_description": "How to write a dissertation proposal: what to include, how to justify your research, what supervisors look for, and how to avoid the most common rejection reasons.",
        "category_slug": "dissertations",
        "tags": ["dissertation proposal", "dissertation", "research proposal", "academic writing"],
        "excerpt": "A dissertation proposal is your case for why your research matters and how you plan to conduct it. This guide covers structure, common rejection reasons, and what supervisors are actually looking for.",
        "reading_time": 9,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A dissertation proposal typically includes: background, research question(s), literature overview, methodology, and timeline",
                    "The most common rejection reason is a research question that is too broad or unfocused",
                    "Show that there is a genuine gap in the literature — your research must add something new",
                    "A realistic timeline with specific milestones shows your supervisor you are organised",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Dissertation Proposal?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A dissertation proposal is a formal document you submit before beginning your dissertation. It makes the case for your research: what you plan to study, why it matters, what the existing literature says, how you will conduct the research, and how long it will take.</p><p>Most proposals are 1,000–3,000 words. The exact requirements vary significantly by institution and discipline, so check your programme handbook before writing.</p>"},
            {"type": "heading", "value": {"text": "The Research Question", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Your research question is the foundation of the proposal. It should be specific (not 'What is the impact of social media?' but 'How has Instagram's algorithmic feed design affected self-reported body satisfaction in women aged 18–24 in the UK between 2018 and 2023?'), feasible within your timeframe and resources, and clearly connected to a gap in the existing literature.</p><p>Write your research question first. If you cannot write it in a single sentence, you have not yet defined it clearly enough.</p>"},
            {"type": "heading", "value": {"text": "Literature Overview", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The proposal is not the place for a full literature review, but you need to demonstrate familiarity with the key debates in your field. Aim for a focused overview (300–500 words) that: identifies the major schools of thought or research strands, notes where there is consensus, identifies the gap your research will address, and positions your research within that gap.</p>"},
            {"type": "heading", "value": {"text": "Methodology Section", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Describe your research design, data collection methods, and analytical approach. You do not need the full detail of the methodology chapter itself — but you do need to show that you have thought through how your research will actually be conducted and that your methods are appropriate for your research question.</p><p>If your research involves human participants, mention your plan for ethical approval — supervisors will flag this if absent.</p>"},
            {"type": "cta", "value": {
                "text": "Get help with your dissertation",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "academic-writing-style-guide",
        "title": "Academic Writing Style: Tone, Voice, and Formality in University Essays",
        "seo_title": "Academic Writing Style Guide — Tone, Voice & Formality | EssayManiacs",
        "search_description": "How to write in the correct academic style: formal register, hedging language, avoiding personal pronouns, and the specific conventions that differ by discipline.",
        "category_slug": "academic-tips",
        "tags": ["academic writing", "writing style", "academic tone", "university essays"],
        "excerpt": "Academic writing has a specific register, tone, and set of conventions that differ from other forms of writing. This guide covers what makes writing 'academic' — and how to achieve it without sacrificing clarity.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "Academic writing is formal, precise, and evidence-based — but it should still be clear",
                    "Avoid first person in most disciplines unless your lecturer specifically permits it",
                    "Hedging language ('suggests', 'may indicate', 'appears to') is standard in academic writing — not weakness",
                    "Never use contractions, colloquialisms, or rhetorical questions in formal academic writing",
                ]
            }},
            {"type": "heading", "value": {"text": "What Makes Writing 'Academic'?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Academic writing differs from other writing in four key ways: it is formal (no slang, contractions, or colloquialisms), precise (exact language rather than approximations), evidenced (claims are supported by cited research), and critical (it does not merely describe — it analyses and evaluates).</p><p>Note that formal does not mean unnecessarily complex. Examiners are not impressed by long sentences with multiple subordinate clauses when a short, clear sentence would work better. Clarity is always valued.</p>"},
            {"type": "heading", "value": {"text": "First Person vs. Third Person", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most undergraduate disciplines expect third person ('The research demonstrates...', 'This essay argues...') rather than first person ('I think...', 'In my opinion...'). However, this varies significantly by discipline and by lecturer preference. Sciences and social sciences often strictly prohibit first person; reflective writing in education or nursing may require it. Always check your assignment brief and any provided marking criteria.</p>"},
            {"type": "heading", "value": {"text": "Hedging Language", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Hedging is the use of language that qualifies certainty appropriately. Academic writers hedge because almost all research has limitations and findings are rarely absolute. Common hedging devices: modal verbs (<em>may, might, could, would</em>), hedging adverbs (<em>apparently, seemingly, arguably</em>), reporting verbs with nuance (<em>suggests, indicates, implies, appears to</em>).</p><p><strong>Overstated:</strong> <em>Social media causes depression in teenagers.</em><br><strong>Appropriately hedged:</strong> <em>Evidence suggests that heavy social media use is associated with increased depressive symptoms in adolescents, though causality has not been established.</em></p>"},
            {"type": "heading", "value": {"text": "Common Mistakes to Avoid", "level": "h2"}},
            {"type": "checklist", "value": {"heading": "Academic Style — What to Avoid", "items": [
                {"text": "Contractions: don't, can't, it's → do not, cannot, it is"},
                {"text": "Rhetorical questions: 'But is this really the case?' → state your position directly"},
                {"text": "Colloquialisms: 'a lot of', 'pretty significant', 'kind of' → precise alternatives"},
                {"text": "Padding phrases: 'It is important to note that', 'In today's modern society'"},
                {"text": "Unsupported generalisations: any claim that needs evidence must have a citation"},
            ]}},
            {"type": "cta", "value": {
                "text": "Get your essay written by a specialist",
                "url": "/order",
            }},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed EssayManiacs blog with sample posts, categories, and an author"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="essaymaniacs.com")
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
