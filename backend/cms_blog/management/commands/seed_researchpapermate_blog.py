"""
Management command: seed_researchpapermate_blog
===============================================

Seeds ResearchPaperMate blog with sample posts, categories, and an author so
the blog section renders end-to-end without any Wagtail admin setup.

Idempotent — skips objects that already exist by slug/name.

Usage:
    python manage.py seed_researchpapermate_blog
    python manage.py seed_researchpapermate_blog --site researchpapermate.com
    python manage.py seed_researchpapermate_blog --update
"""

from django.core.management.base import BaseCommand, CommandParser

AUTHOR = {
    "name": "ResearchPaperMate Editorial Team",
    "slug": "researchpapermate-editorial",
    "credentials": "Research Methodology & Academic Writing Specialists",
    "bio": (
        "The ResearchPaperMate Editorial Team consists of postgraduate-qualified writers "
        "with expertise in research methodology, academic writing, and citation standards. "
        "Our contributors hold Master's and PhD degrees across natural sciences, social "
        "sciences, humanities, and engineering. Every article is peer-reviewed for "
        "methodological accuracy before publication."
    ),
}

CATEGORIES = [
    {"name": "Research Papers",    "slug": "research-papers",    "display_order": 1, "is_featured": True},
    {"name": "Citations & Style",  "slug": "citations-style",    "display_order": 2, "is_featured": True},
    {"name": "Literature Reviews", "slug": "literature-reviews", "display_order": 3},
    {"name": "Dissertations",      "slug": "dissertations",      "display_order": 4},
    {"name": "Study Tips",         "slug": "study-tips",         "display_order": 5},
]

POSTS = [
    {
        "slug": "how-to-write-a-research-paper-introduction",
        "title": "How to Write a Research Paper Introduction That Sets Up Your Argument",
        "seo_title": "Research Paper Introduction — How to Write It | ResearchPaperMate",
        "search_description": "How to write a compelling research paper introduction: background context, the research gap, your thesis or research question, and the structure signpost — with examples.",
        "category_slug": "research-papers",
        "tags": ["research paper", "academic writing", "introduction", "thesis statement"],
        "excerpt": "The introduction of a research paper must do more than introduce your topic — it must justify why your specific research question matters. This guide covers every component and the logic that connects them.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A research paper introduction moves from broad to narrow: background → gap → your question",
                    "The research gap is the most important component — it justifies the paper's existence",
                    "End with a clear thesis statement (humanities) or research question/objectives (sciences)",
                    "The introduction should be approximately 10–15% of total word count",
                ]
            }},
            {"type": "heading", "value": {"text": "The Four-Component Introduction", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A research paper introduction is not simply a general overview of your topic. It has a specific argumentative function: to convince the reader that your research question needs to be investigated. The best introductions follow a funnel structure, moving from broad context to the specific gap your paper addresses.</p>"},
            {"type": "checklist", "value": {"heading": "Introduction Components", "items": [
                {"text": "Background — establish the broader context and significance of the research area"},
                {"text": "Literature overview — briefly summarise what is already known"},
                {"text": "The gap — identify what is missing, contested, or unresolved in the literature"},
                {"text": "Your contribution — state your research question, thesis, or objectives"},
            ]}},
            {"type": "heading", "value": {"text": "How to Identify and State the Research Gap", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The research gap is the most intellectually demanding part of the introduction to write — but it is the one that most justifies your paper. A gap is not just 'nobody has studied this.' It can also be: conflicting findings in the existing literature that need resolution; a theoretical model that has not been empirically tested in a specific context; a population, geography, or time period not yet studied; or a methodological weakness in previous research that your study addresses.</p><p>State the gap explicitly: <em>\"Despite extensive research into X, relatively little attention has been paid to Y in the context of Z.\"</em></p>"},
            {"type": "heading", "value": {"text": "Thesis Statement vs. Research Questions", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Humanities papers typically end the introduction with a thesis statement: a single sentence that states your main argument. Sciences and social sciences often end with formal research questions or a list of objectives. Both function as a contract with the reader — the rest of the paper must deliver on what the introduction promises.</p>"},
            {"type": "cta", "value": {
                "text": "Get your research paper written by a specialist",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "mla-9th-edition-citation-guide",
        "title": "MLA 9th Edition Citation Guide: Works Cited, In-Text Citations & Examples",
        "seo_title": "MLA 9th Edition Citation Guide — Complete Examples | ResearchPaperMate",
        "search_description": "Complete MLA 9th edition guide with in-text citation format, Works Cited examples for books, journals, websites, films, and the key changes from MLA 8th edition.",
        "category_slug": "citations-style",
        "tags": ["MLA 9th edition", "MLA citation", "Works Cited", "academic writing"],
        "excerpt": "MLA 9th edition is the standard citation format for humanities: literature, languages, film, and cultural studies. This guide covers in-text citations, Works Cited formatting, and the key differences from MLA 8th.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "MLA 9th uses a universal format for all source types: Author. Title. Container, Contributor, Version, Number, Publisher, Date, Location.",
                    "In-text citations use (Author Page) format: (Smith 47) — no comma between author and page",
                    "MLA 9th restored the comma after the author's first name in Works Cited entries",
                    "Websites and online articles require an access date only if the content may change",
                ]
            }},
            {"type": "heading", "value": {"text": "In-Text Citations in MLA 9th", "level": "h2"}},
            {"type": "paragraph", "value": "<p>MLA uses parenthetical citations that include the author's last name and the page number (no comma between them). The citation appears after the quoted or paraphrased material, before the final punctuation.</p><ul><li><strong>One author:</strong> (Smith 47)</li><li><strong>Two authors:</strong> (Smith and Jones 112)</li><li><strong>Three or more:</strong> (Smith et al. 38)</li><li><strong>No page number (website):</strong> (Smith)</li><li><strong>No author:</strong> (\"Article Title\" 23) — use a shortened version of the title</li></ul>"},
            {"type": "heading", "value": {"text": "Works Cited: Book", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Last Name, First Name. <em>Title of Book in Italics</em>. Publisher, Year.</p><p><strong>Example:</strong><br>Morrison, Toni. <em>Beloved</em>. Alfred A. Knopf, 1987.</p><p>For an edited book: Editor Last Name, First Name, editor. <em>Title</em>. Publisher, Year.</p>"},
            {"type": "heading", "value": {"text": "Works Cited: Journal Article", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Last Name, First Name. \"Article Title.\" <em>Journal Name</em>, vol. X, no. X, Month Year, pp. X–X. DOI or URL.</p><p><strong>Example:</strong><br>Ahmad, Rasha, and Samantha Clarke. \"Decolonising the Curriculum: Student Perspectives on Representation in Higher Education.\" <em>Higher Education Research &amp; Development</em>, vol. 41, no. 3, 2022, pp. 678–693. https://doi.org/10.1080/07294360.2021.1929832.</p>"},
            {"type": "heading", "value": {"text": "Works Cited: Website", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Format: Last Name, First Name. \"Page Title.\" <em>Website Name</em>, Date Published, URL. Accessed Day Month Year.</p><p><strong>Example:</strong><br>Williams, Joanna. \"The Unreliable Narrator in Victorian Fiction.\" <em>Literary Hub</em>, 14 Mar. 2023, lithub.com/the-unreliable-narrator-in-victorian-fiction. Accessed 2 Sept. 2023.</p><p>Only include the access date if the page is likely to change or has no publication date.</p>"},
            {"type": "heading", "value": {"text": "Key Changes from MLA 8th to 9th Edition", "level": "h2"}},
            {"type": "checklist", "value": {"heading": "What changed in MLA 9th", "items": [
                {"text": "Comma restored after author's first name in Works Cited: 'Last, First,' (MLA 8th had removed it)"},
                {"text": "URLs should no longer include angle brackets < >"},
                {"text": "Inclusive language guidance expanded — use the language a person uses to describe themselves"},
                {"text": "New guidance on citing social media, podcasts, and streaming content"},
            ]}},
            {"type": "cta", "value": {
                "text": "Get your paper formatted in MLA 9th",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "how-to-write-a-literature-review-research-paper",
        "title": "How to Write a Literature Review for a Research Paper",
        "seo_title": "How to Write a Literature Review for a Research Paper | ResearchPaperMate",
        "search_description": "A step-by-step guide to writing a literature review for a research paper: database searching, source selection, synthesis techniques, structure, and the most common mistakes.",
        "category_slug": "literature-reviews",
        "tags": ["literature review", "academic research", "database search", "synthesis"],
        "excerpt": "A literature review is not a summary of sources — it is a critical synthesis of the field. This guide covers how to search systematically, evaluate what you find, and write a review that positions your own research meaningfully.",
        "reading_time": 10,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "A literature review synthesises sources — it does not describe them one by one",
                    "Organise thematically (by argument or finding), not chronologically (by publication date)",
                    "Every source must be directly relevant to your research question",
                    "Explicitly identify gaps in the literature — this is where your research fits",
                ]
            }},
            {"type": "heading", "value": {"text": "What Is a Literature Review for a Research Paper?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A literature review for a research paper has a different purpose from a standalone literature review. It is not an exhaustive survey — it is a focused review of the literature most directly relevant to your research question, designed to: demonstrate that you understand the field, show that there is a genuine gap or unresolved debate your paper addresses, and provide the theoretical or empirical foundation your own analysis builds on.</p>"},
            {"type": "heading", "value": {"text": "Searching the Literature Systematically", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Use academic databases, not general search engines. The most important databases by field:</p><ul><li><strong>Natural sciences, medicine:</strong> PubMed, Web of Science, Scopus</li><li><strong>Social sciences, education:</strong> ERIC, PsycINFO, Scopus</li><li><strong>Humanities:</strong> JSTOR, MLA International Bibliography, Project MUSE</li><li><strong>Business, economics:</strong> Business Source Complete, EconLit</li></ul><p>Define your search terms using your research question's key concepts. Use Boolean operators: AND (narrows results), OR (broadens), NOT (excludes). Set date filters — typically the last 10 years unless citing seminal foundational work.</p>"},
            {"type": "heading", "value": {"text": "The Most Common Literature Review Mistake", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The single most common mistake is writing an annotated bibliography disguised as a literature review. It looks like this: <em>\"Smith (2020) found that X. Jones (2021) argued that Y. Williams (2022) suggested that Z.\"</em></p><p>This is source description, not synthesis. A synthesised literature review groups sources by what they argue, not by who wrote them: <em>\"Several studies have found a positive correlation between X and Y (Smith, 2020; Jones, 2021; Williams, 2022), though the magnitude of the effect varies significantly by context, and no study has yet examined...\"</em></p>"},
            {"type": "heading", "value": {"text": "Thematic Organisation", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Organise your literature review by themes, debates, or methodological approaches — not by publication date or author. Identify 3–5 main themes in the literature and dedicate a paragraph or section to each. Within each section, synthesise sources across multiple studies rather than describing each one individually.</p><p>End the literature review by explicitly stating the gap your research addresses: <em>\"Despite extensive investigation into A and B, the relationship between X and Y in the context of Z remains underexplored.\"</em></p>"},
            {"type": "cta", "value": {
                "text": "Get your literature review written by a PhD researcher",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "research-paper-methodology-section",
        "title": "How to Write the Methodology Section of a Research Paper",
        "seo_title": "Research Paper Methodology Section Guide | ResearchPaperMate",
        "search_description": "How to write the methodology section of a research paper: research design, data collection, sampling, analysis methods, and how to justify every methodological choice.",
        "category_slug": "dissertations",
        "tags": ["methodology", "research design", "qualitative", "quantitative", "data analysis"],
        "excerpt": "The methodology section justifies every research decision you made. This guide covers research design, data collection, sampling, analysis methods, and the critical element most students miss: explicit justification for every choice.",
        "reading_time": 11,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "Every methodological choice must be justified — not just described",
                    "Research paradigm (positivism vs. interpretivism) determines your overall approach",
                    "Sample size justification is required for quantitative studies — and so is power calculation",
                    "Limitations must be addressed honestly — examiners expect them and will mark you down for omitting them",
                ]
            }},
            {"type": "heading", "value": {"text": "What the Methodology Section Must Do", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The methodology section has one purpose: convince the reader that your research design is appropriate for your research question, that you conducted the research rigorously, and that you understand its limitations. Most students write it as a description of what they did. That is necessary — but insufficient. Every decision needs justification: why this design, why these methods, why this sample, why these analytical tools.</p>"},
            {"type": "heading", "value": {"text": "Research Design", "level": "h2"}},
            {"type": "paragraph", "value": "<p>State your overall research design clearly — experimental, quasi-experimental, survey-based, case study, ethnographic, grounded theory, or mixed methods — and justify it in relation to your research question. A descriptive survey is appropriate for exploring a previously unstudied phenomenon; a randomised controlled trial is appropriate for testing a causal claim. The design should match the question.</p>"},
            {"type": "heading", "value": {"text": "Data Collection Methods", "level": "h2"}},
            {"type": "paragraph", "value": "<p><strong>Quantitative studies:</strong> Describe your survey instrument or experimental protocol, sampling method (random, stratified, convenience), sample size and how it was determined (power calculation for experimental studies), and data collection procedures. Specify any pilot testing and what changes resulted.</p><p><strong>Qualitative studies:</strong> Describe interview design (semi-structured, structured, unstructured), participant selection and rationale, how many participants and why (data saturation justification), and how interviews were recorded and transcribed.</p>"},
            {"type": "heading", "value": {"text": "Data Analysis", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Specify your analytical approach and justify it. Quantitative: which statistical tests, which software (SPSS, R, Stata), and why those tests are appropriate for your data type and research question. Qualitative: which analytical framework (thematic analysis, content analysis, grounded theory coding, IPA), how themes were derived, and how you ensured rigour (member checking, peer debriefing, reflexivity).</p>"},
            {"type": "heading", "value": {"text": "Limitations", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Address limitations explicitly — this is not a sign of weakness but of methodological rigour. Common limitations to address: sample size and representativeness; self-report bias in survey data; the specific context or population studied and whether findings may transfer; time limitations if longitudinal data would have been more appropriate. For each limitation, briefly note what steps (if any) were taken to mitigate it.</p>"},
            {"type": "cta", "value": {
                "text": "Get your methodology written by a research specialist",
                "url": "/order",
            }},
        ],
    },
    {
        "slug": "how-to-avoid-plagiarism-research-paper",
        "title": "How to Avoid Plagiarism in Research Papers: Paraphrasing, Quoting & Citations",
        "seo_title": "How to Avoid Plagiarism in Research Papers | Paraphrasing Guide | ResearchPaperMate",
        "search_description": "How to avoid plagiarism in research papers: effective paraphrasing technique, when to use direct quotes, how to cite correctly, and the self-plagiarism rules most students don't know about.",
        "category_slug": "study-tips",
        "tags": ["plagiarism", "paraphrasing", "citation", "academic integrity", "research paper"],
        "excerpt": "Plagiarism can end a university career. This guide covers the real techniques for paraphrasing effectively (not just swapping words), when to use direct quotes, how to cite everything that needs citing, and the self-plagiarism rules many students are unaware of.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {
                "items": [
                    "Plagiarism includes unintentional plagiarism — not knowing is not an excuse",
                    "Effective paraphrasing requires understanding, not word-swapping with a thesaurus",
                    "Direct quotes should be used sparingly — paraphrase and cite whenever possible",
                    "Self-plagiarism (reusing your own previous work without disclosure) is treated as academic misconduct in most institutions",
                ]
            }},
            {"type": "heading", "value": {"text": "What Counts as Plagiarism?", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Plagiarism is using someone else's ideas, words, data, or structure without proper attribution — regardless of whether it was intentional. The forms that catch students off guard:</p><ul><li><strong>Patchwork plagiarism</strong> — copying and rearranging sentences from multiple sources, sometimes with minor word changes</li><li><strong>Mosaic plagiarism</strong> — mixing your own writing with unattributed copied phrases</li><li><strong>Paraphrase plagiarism</strong> — restating an author's ideas in your own words without citing them</li><li><strong>Self-plagiarism</strong> — submitting work you wrote for a previous assignment without disclosing it</li></ul>"},
            {"type": "heading", "value": {"text": "How to Paraphrase Correctly", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Effective paraphrasing requires genuine comprehension, not word substitution. The process:</p><ol><li>Read the passage carefully until you fully understand it</li><li>Put the source away — do not look at it</li><li>Write the idea in your own words, using your own sentence structure</li><li>Check against the original to ensure you have not accidentally replicated phrasing</li><li>Add the citation — paraphrased material always requires a citation</li></ol><p>If you use a thesaurus to swap individual words while keeping the same sentence structure, that is still plagiarism. The structure must change, not just the vocabulary.</p>"},
            {"type": "heading", "value": {"text": "When to Use Direct Quotes", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Direct quotes should be used sparingly in academic research papers — typically only when the exact wording is important (a legal definition, a key theoretical term introduced by the author, or a particularly well-phrased argument that would lose something in paraphrase). Most examiners prefer to see evidence that you can engage with ideas intellectually, not just copy them accurately. Aim for no more than 10–15% of your paper to be direct quotation.</p>"},
            {"type": "heading", "value": {"text": "What Always Needs a Citation", "level": "h2"}},
            {"type": "checklist", "value": {"heading": "Always cite these", "items": [
                {"text": "Any direct quotation from any source"},
                {"text": "Any paraphrased idea, argument, or theory from another author"},
                {"text": "Statistics, data, and research findings — even if you are paraphrasing them"},
                {"text": "Diagrams, figures, or tables from another source"},
                {"text": "Your own previously submitted work (cite it explicitly if you reference it)"},
            ]}},
            {"type": "heading", "value": {"text": "What Does Not Need a Citation", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Common knowledge does not need a citation: <em>\"The First World War began in 1914\"</em> requires no citation. However, <em>\"Approximately 17 million people died as a direct result of World War I\"</em> does — that is a contested specific figure derived from research. If in doubt, cite. Over-citation is far preferable to under-citation.</p>"},
            {"type": "cta", "value": {
                "text": "Get your research paper written — plagiarism-free",
                "url": "/order",
            }},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed ResearchPaperMate blog with sample posts, categories, and an author"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="researchpapermate.com")
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
