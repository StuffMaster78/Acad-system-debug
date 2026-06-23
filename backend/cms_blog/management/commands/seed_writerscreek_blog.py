"""
Management command: seed_writerscreek_blog
==========================================

Seeds the Writers Creek blog with writer-focused articles covering
writing quality, academic referencing, platform guidance, and career
advice for freelance academic writers.

Idempotent — skips posts that already exist by slug.

Usage:
    python manage.py seed_writerscreek_blog
    python manage.py seed_writerscreek_blog --site writerscreek.com --update
"""

from django.core.management.base import BaseCommand, CommandParser

AUTHOR = {
    "name": "Writers Creek Editorial Team",
    "slug": "writerscreek-editorial",
    "credentials": "Academic Writing Specialists",
    "bio": (
        "The Writers Creek Editorial Team is made up of experienced academic "
        "writers, editors, and writing coaches who share practical insights on "
        "craft, professional practice, and platform success. Every article is "
        "reviewed for accuracy and relevance to the writers on our network."
    ),
}

CATEGORIES = [
    {"name": "Writing Craft",       "slug": "writing-craft",       "display_order": 1, "is_featured": True},
    {"name": "Referencing & Style", "slug": "referencing-style",   "display_order": 2, "is_featured": True},
    {"name": "Platform Guides",     "slug": "platform-guides",     "display_order": 3},
    {"name": "Career & Workflow",   "slug": "career-workflow",     "display_order": 4},
    {"name": "Assignment Types",    "slug": "assignment-types",    "display_order": 5},
]

POSTS = [
    # ── 1. Writing craft ──────────────────────────────────────────────────────
    {
        "slug": "how-to-write-a-first-class-essay",
        "title": "How to Write a First-Class Essay: Techniques That Earn Top Marks",
        "seo_title": "How to Write a First-Class Essay | Academic Writing Techniques | Writers Creek",
        "search_description": "Learn the techniques that consistently earn first-class marks: strong thesis construction, evidence integration, critical analysis, and the difference between good and excellent academic writing.",
        "category_slug": "writing-craft",
        "tags": ["essay writing", "academic writing", "first class", "critical analysis", "thesis statement"],
        "excerpt": "The difference between a 2:1 and a first-class essay is rarely about knowledge — it's about how ideas are constructed, evidenced, and argued. This guide covers the exact techniques that move work from competent to distinction-level.",
        "reading_time": 10,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "First-class essays argue — they don't just describe or summarise",
                "Every paragraph should advance the overall argument, not just cover a topic",
                "Critical analysis means evaluating the strength of evidence, not just presenting it",
                "Examiners reward conceptual precision — vague generalisations lose marks",
                "Excellent conclusions synthesise and extend the argument; they don't just repeat it",
            ]}},
            {"type": "heading", "value": {"text": "What Separates First-Class Work", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Examiners often describe the difference between a solid 2:1 and a first-class essay in one word: <strong>argument</strong>. A 2:1 essay covers the topic correctly. A first-class essay <em>argues something</em> about it.</p><p>This means your thesis must be genuinely debatable — not merely a statement of what you will discuss. It means each paragraph must make a claim, not just present information. And it means your conclusion must add something, not simply restate what you've already said.</p>"},
            {"type": "heading", "value": {"text": "Constructing a Strong Thesis", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A first-class thesis is specific, arguable, and scoped. It tells the reader exactly what you are claiming and implies a line of reasoning rather than a list of topics.</p><p><strong>Weak:</strong> <em>This essay will examine the causes of the 2008 financial crisis.</em><br><strong>Strong:</strong> <em>The 2008 financial crisis was primarily caused by the deregulation of mortgage-backed securities in the 1990s, which created the structural conditions for systemic leverage failure when housing prices fell.</em></p><p>The strong version commits to a specific causal claim that another essay could argue against. That's what makes it an argument.</p>"},
            {"type": "heading", "value": {"text": "Integrating Evidence at the Right Depth", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Evidence serves your argument — it does not make the argument for you. After every piece of evidence, three things must follow: acknowledgement of what the source shows, critical evaluation of its strength or limitations, and explicit connection to your thesis.</p><p>Many writers make the mistake of quoting generously and then moving on. Examiners are not impressed by a long list of sources. They are impressed by precise, critical engagement with a smaller number of carefully chosen ones.</p>"},
            {"type": "heading", "value": {"text": "Paragraph Structure That Builds Argument", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Each body paragraph should do one thing: advance your overall argument with a distinct sub-claim. The PEEL structure (Point, Evidence, Explanation, Link) works well as a baseline, but the most important element is the link — the sentence at the end that connects your paragraph's sub-claim back to the thesis.</p><p>If you can delete a paragraph without weakening your argument, the paragraph doesn't belong in the essay.</p>"},
            {"type": "heading", "value": {"text": "Writing a Conclusion That Adds Value", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A first-class conclusion does three things: restates the thesis in light of the evidence presented (not just repeats it), synthesises the key lines of argument rather than summarising each paragraph, and briefly addresses the broader implications or limitations of the argument.</p><p>This last element — moving the reader from the specific argument to its broader significance — is what distinguishes a truly excellent conclusion from a competent one.</p>"},
            {"type": "cta", "value": {
                "heading": "Ready to write at this level on our platform?",
                "body": "Writers Creek connects academically trained writers with clients who need first-class work. Apply to join our writer network and start taking assignments that match your expertise.",
                "button_text": "Apply to Writers Creek",
                "button_url": "/apply",
                "style": "primary",
            }},
        ],
    },

    # ── 2. Referencing & Style ────────────────────────────────────────────────
    {
        "slug": "academic-referencing-styles-guide",
        "title": "APA, MLA, Harvard, and Chicago: A Writer's Quick-Reference Guide",
        "seo_title": "Academic Referencing Styles: APA, MLA, Harvard, Chicago | Writers Creek",
        "search_description": "A quick-reference guide to the four main academic referencing styles. Understand when each is used, how in-text citations differ, and the key formatting rules for reference lists.",
        "category_slug": "referencing-style",
        "tags": ["referencing", "APA", "MLA", "Harvard", "Chicago", "citations", "bibliography"],
        "excerpt": "Getting citations right is non-negotiable in academic writing. This guide compares APA 7th, MLA 9th, Harvard, and Chicago 17th side by side so you can format any assignment correctly and quickly.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "APA is standard in psychology, education, and social sciences",
                "MLA is standard in literature, arts, and humanities",
                "Harvard (author-date) is widely used in business, science, and UK universities",
                "Chicago has two systems: author-date (sciences) and notes-bibliography (humanities)",
                "Always check the client's specific style guide — style variants exist within each system",
            ]}},
            {"type": "heading", "value": {"text": "Why Referencing Style Matters", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Referencing is not just about avoiding plagiarism — it's a signal to the reader about where knowledge comes from and how to verify it. Different academic disciplines have converged on different conventions, so knowing which style applies to an assignment is the first task of every citation job.</p><p>Most clients will specify which style they need. If not, use the discipline as your guide: psychology → APA; English literature → MLA; business or UK university → Harvard; history → Chicago notes-bibliography.</p>"},
            {"type": "heading", "value": {"text": "APA 7th Edition", "level": "h2"}},
            {"type": "paragraph", "value": "<p>APA uses author-date in-text citations: <em>(Smith, 2022, p. 45)</em> for direct quotes, <em>(Smith, 2022)</em> for paraphrases. The reference list is alphabetical by author surname. For books: Author, A. A. (Year). <em>Title of work: Capital letter also for subtitle</em>. Publisher. For journal articles: Author, A. A., &amp; Author, B. B. (Year). Article title. <em>Journal Name, Volume</em>(Issue), pp–pp. https://doi.org/xxxxx</p><p>Key APA 7th changes: publisher location is no longer required; DOIs are formatted as hyperlinks; up to 20 authors are listed in full.</p>"},
            {"type": "heading", "value": {"text": "MLA 9th Edition", "level": "h2"}},
            {"type": "paragraph", "value": "<p>MLA uses in-text page references: <em>(Smith 45)</em> for a direct quote. The works cited list uses the container model: core elements in a fixed order, separated by commas and ending with a period. For a journal article: Author Last, First. \"Article Title.\" <em>Journal Name</em>, vol. 12, no. 3, Year, pp. 45–67.</p><p>MLA 9th introduced the concept of <em>containers</em> — the larger works (journals, websites, anthologies) in which a source appears. A source accessed through a database has two containers.</p>"},
            {"type": "heading", "value": {"text": "Harvard (Author-Date)", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Harvard is not a single standardised system — there are dozens of institutional variants. The common pattern is author-date in-text: <em>(Smith, 2022: 45)</em> or <em>(Smith, 2022, p. 45)</em> for quotes. The reference list is alphabetical. For books: Smith, A. (2022) <em>Title of Work</em>. City: Publisher.</p><p>When a client specifies Harvard, ask which institution's version, or check their provided reference examples. Oxford Harvard, Leeds Harvard, and APA can look almost identical at a distance but differ in details.</p>"},
            {"type": "heading", "value": {"text": "Chicago 17th Edition", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Chicago has two distinct systems. <strong>Notes-bibliography</strong> (humanities): footnotes or endnotes with full citations on first mention, shortened on subsequent mentions; a bibliography at the end. <strong>Author-date</strong> (sciences): in-text citations like APA, with a reference list.</p><p>Notes-bibliography footnote example: <sup>1</sup>John Smith, <em>Title of Work</em> (City: Publisher, 2022), 45. Second mention: Smith, <em>Title</em>, 47. (Or use Ibid. for consecutive citations of the same source.)</p>"},
            {"type": "cta", "value": {
                "heading": "Referencing precision is a Writers Creek standard",
                "body": "Every assignment on our platform is checked for correct, consistent citation formatting. Join our network and demonstrate your academic referencing skills.",
                "button_text": "Apply to Writers Creek",
                "button_url": "/apply",
                "style": "primary",
            }},
        ],
    },

    # ── 3. Platform guides ────────────────────────────────────────────────────
    {
        "slug": "how-to-handle-revision-requests-professionally",
        "title": "How to Handle Revision Requests Professionally and Protect Your Rating",
        "seo_title": "How to Handle Revision Requests | Writers Creek Platform Guide",
        "search_description": "Learn how to respond to revision requests professionally, understand what clients actually want, fix issues efficiently, and protect your writer rating on the Writers Creek platform.",
        "category_slug": "platform-guides",
        "tags": ["revision requests", "writer rating", "client communication", "platform guide", "quality"],
        "excerpt": "Revision requests are a normal part of academic writing work. How you handle them determines your rating and long-term earnings far more than the quality of your first draft. This guide explains how to turn revisions into a professional advantage.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Read the revision request carefully before responding — understand the specific issue",
                "Never argue with the client; acknowledge and resolve, then ask if there's anything else",
                "Most revision requests are caused by misunderstanding the instructions, not poor writing",
                "Revisions handled quickly and graciously lead to positive reviews and repeat clients",
                "If a request asks for something outside the original scope, use the ticket system",
            ]}},
            {"type": "heading", "value": {"text": "Revisions Are Part of the Job", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Even excellent writers receive revision requests. Academic writing is inherently collaborative, and clients often have specific expectations that aren't fully captured in the original instructions. Your ability to handle revisions gracefully and efficiently is one of the strongest signals of professional quality.</p><p>Writers who resist revisions, argue with clients, or take a long time to respond consistently receive lower ratings than writers who handle revisions quickly and positively — even when the first-draft quality is comparable.</p>"},
            {"type": "heading", "value": {"text": "Step 1: Read and Understand Before Responding", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Before you do anything, read the revision request in full. Identify the specific issues the client is raising. Is it a formatting change? A structural issue? A concern about the argument? A citation error? Different issues require different fixes, and rushing to revise before understanding the problem leads to secondary revision requests.</p><p>If the request is vague — for example, 'this doesn't meet my expectations' — ask one clear clarifying question. Something like: 'Thank you for the feedback. Could you point me to the specific sections that need adjustment so I can address them precisely?'</p>"},
            {"type": "heading", "value": {"text": "Step 2: Fix the Actual Issue", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Once you understand the issue, fix it completely. Don't just address the sentence or paragraph mentioned — check whether the same issue exists elsewhere in the paper. If a client flags an inconsistent citation style in one footnote, review all footnotes. If they flag a structural issue in the introduction, consider whether the same weakness affects the conclusion.</p><p>Submitting a revised draft that only fixes the specific examples mentioned — and leaves the same issue elsewhere — is one of the fastest ways to generate a second revision request and damage your rating.</p>"},
            {"type": "heading", "value": {"text": "Step 3: Communicate Clearly When You Submit", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When you return the revised draft, write a brief message explaining what you changed and why. This reassures the client that you took their feedback seriously and helps them know where to look. For example: 'I've restructured the introduction to lead with the thesis statement as requested, and I've also strengthened the counterargument section in paragraph 4 which felt underdeveloped. Please let me know if there's anything else you'd like adjusted.'</p><p>This approach consistently generates positive feedback because it demonstrates professionalism, not just compliance.</p>"},
            {"type": "heading", "value": {"text": "When a Revision Crosses Into New Scope", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Sometimes a revision request asks for work that wasn't in the original instructions — a new chapter, a different topic, or significantly expanded length. These are scope changes, not revisions. Use the support ticket system to flag the issue rather than simply refusing or completing the extra work for free.</p><p>The platform support team can mediate and ensure the compensation reflects the actual work completed.</p>"},
            {"type": "cta", "value": {
                "heading": "Earn more by delivering quality from draft one",
                "body": "Writers Creek's rating system rewards writers who consistently deliver accurate, well-cited, well-argued work. Apply to join and start building your reputation.",
                "button_text": "Apply to Writers Creek",
                "button_url": "/apply",
                "style": "primary",
            }},
        ],
    },

    # ── 4. Career & Workflow ──────────────────────────────────────────────────
    {
        "slug": "managing-multiple-deadlines-as-a-freelance-writer",
        "title": "Managing Multiple Deadlines as a Freelance Academic Writer",
        "seo_title": "Managing Multiple Deadlines | Freelance Academic Writing | Writers Creek",
        "search_description": "Practical strategies for managing multiple simultaneous writing deadlines, avoiding quality drop-off when busy, and knowing when to stop taking new assignments.",
        "category_slug": "career-workflow",
        "tags": ["time management", "deadlines", "freelance writing", "productivity", "workload"],
        "excerpt": "Accepting too many assignments is the most common mistake new freelance academic writers make. This guide covers the systems that experienced writers use to manage heavy workloads without sacrificing quality or missing deadlines.",
        "reading_time": 9,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Track all deadlines in one place — never rely on memory for more than one assignment",
                "Build in a quality buffer: finish 4–6 hours before the stated deadline",
                "Long deadlines are traps — front-load research and leave writing to a fixed window",
                "Know your maximum sustainable output per day and do not exceed it",
                "When over capacity, decline early — a rejected bid costs nothing; a missed deadline costs everything",
            ]}},
            {"type": "heading", "value": {"text": "The Overcommitment Trap", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most common reason writers damage their ratings is not poor writing — it's poor workload management. When you accept more assignments than you can handle at your normal quality level, something always suffers: either the quality of the work, or the deadline, or your sleep. Usually all three.</p><p>Experienced freelance academic writers are ruthless about capacity. They know their daily output ceiling — the maximum number of pages they can write while maintaining first-class quality — and they do not take assignments that would push past it.</p>"},
            {"type": "heading", "value": {"text": "Build a Single Source of Truth for Your Deadlines", "level": "h2"}},
            {"type": "paragraph", "value": "<p>If you have more than two active assignments, you need a system. A shared document, spreadsheet, or dedicated task manager with every assignment logged by: client deadline, your internal deadline (4–6 hours before the client deadline), word count, subject, and status (research, drafting, editing, submitted) is the baseline.</p><p>Many writers use a colour system: red for due within 24 hours, amber for due within 48, green for due within a week. Whatever system you use, it must be visible every time you open your computer.</p>"},
            {"type": "heading", "value": {"text": "The Long-Deadline Problem", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A 14-day deadline feels like luxury. In practice, most writers spend the first 10 days doing other assignments and then scramble to complete the 14-day job in the last 4 days at reduced quality. This is called the planning fallacy, and it affects almost everyone.</p><p>The fix is to schedule every assignment as if it has a 5-day deadline regardless of the actual deadline. Do the research in the first day or two, outline on day three, draft on days three and four, and edit on day five. Then you have a full week as a buffer — and the work is substantially better.</p>"},
            {"type": "heading", "value": {"text": "Know When to Stop Accepting", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most profitable freelance writers are not the ones who accept the most assignments. They are the ones who maintain the highest ratings — because ratings determine access to higher-paying work, preferred writer relationships, and platform bonuses.</p><p>Before accepting a new assignment, ask: can I complete this to first-class standard by my internal deadline without working more than 8 hours today? If not, decline. A rejected bid costs you nothing. A late or substandard submission costs you your rating.</p>"},
            {"type": "cta", "value": {
                "heading": "Writers Creek rewards consistent quality",
                "body": "Our rating system and payout tiers are designed to reward writers who deliver excellent work reliably. Level up your earnings by building a reputation for quality and reliability.",
                "button_text": "Apply to Writers Creek",
                "button_url": "/apply",
                "style": "primary",
            }},
        ],
    },

    # ── 5. Assignment Types ───────────────────────────────────────────────────
    {
        "slug": "academic-essay-types-guide-for-writers",
        "title": "Academic Essay Types: A Writer's Guide to Argumentative, Analytical, Reflective, and Discursive Essays",
        "seo_title": "Academic Essay Types Guide | Argumentative, Analytical, Reflective | Writers Creek",
        "search_description": "A writer's guide to the key academic essay types: argumentative, analytical, reflective, discursive, and compare-and-contrast. Understand what each requires and how to structure them correctly.",
        "category_slug": "assignment-types",
        "tags": ["essay types", "argumentative essay", "reflective writing", "analytical essay", "academic writing"],
        "excerpt": "Not all academic essays are the same. Applying an argumentative structure to a reflective brief — or a descriptive approach to an analytical question — is a reliable route to a poor grade. This guide maps out what each essay type actually requires.",
        "reading_time": 11,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "The essay type determines structure, stance, and voice — read the brief before assuming",
                "Argumentative essays commit to one position; discursive essays present balanced perspectives",
                "Reflective essays use first person and focus on learning — not just description of events",
                "Analytical essays break a text, data set, or case into components and evaluate each",
                "Compare-and-contrast essays need a clear evaluative framework — not just a list of similarities and differences",
            ]}},
            {"type": "heading", "value": {"text": "Why Essay Type Matters", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When you receive an assignment brief, the first thing to identify is the essay type — because it determines everything that follows: the structure, the stance, the voice, and the kind of evidence required. A writer who applies argumentative essay conventions to a reflective brief will produce work that misses the mark entirely, regardless of how well it is written.</p><p>Many briefs don't explicitly state the essay type. You need to infer it from the instruction verb: 'argue', 'evaluate', 'compare', 'reflect', 'analyse', 'discuss'. Each signals a different type.</p>"},
            {"type": "heading", "value": {"text": "The Argumentative Essay", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Signal words: argue, persuade, justify, defend. The argumentative essay takes a clear stance on a debatable topic and defends it with evidence and reasoning. The thesis must be a specific, arguable claim. Counterarguments must be acknowledged and refuted. Third-person voice is standard.</p><p>Common mistake: treating it as a balanced discussion. An argumentative essay is deliberately one-sided. Balance belongs in a discursive essay.</p>"},
            {"type": "heading", "value": {"text": "The Analytical Essay", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Signal words: analyse, examine, investigate, explore. The analytical essay breaks its subject — a text, a policy, a case study, a data set — into components and evaluates each systematically. It requires close reading, specific evidence, and critical judgement.</p><p>Unlike the argumentative essay, the analytical essay doesn't necessarily advocate for a position. It illuminates — but the best analytical essays still build toward a cumulative insight rather than remaining purely descriptive.</p>"},
            {"type": "heading", "value": {"text": "The Discursive Essay", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Signal words: discuss, consider, to what extent, examine both sides. The discursive essay presents multiple perspectives on a question without necessarily committing to one. It requires balance, fairness to opposing views, and a conclusion that weighs the evidence rather than asserting a firm position.</p><p>Examiners reward discursive essays that acknowledge nuance and complexity. A conclusion that simply states 'there are pros and cons on both sides' without weighing them is not a strong discursive essay — it's an avoidance of analysis.</p>"},
            {"type": "heading", "value": {"text": "The Reflective Essay", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Signal words: reflect, explore your experience, critically reflect. The reflective essay is personal, uses first person, and focuses on learning — not just the description of an experience. The standard framework is a reflective cycle: describe the experience, analyse what happened and why, evaluate what you learned, and explain how it will influence future practice.</p><p>The most common mistake is spending too long on description and not enough on the analytical and evaluative stages. Markers are looking for evidence of learning, not a retelling of events.</p>"},
            {"type": "heading", "value": {"text": "Compare-and-Contrast Essays", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Signal words: compare, contrast, compare and contrast, similarities and differences. The compare-and-contrast essay needs an evaluative framework to organise the comparison — not just a list of attributes. The point-by-point structure (compare both subjects on each criterion in turn) is usually more analytical than the block structure (all of subject A, then all of subject B).</p><p>The strongest compare-and-contrast essays build toward a conclusion that explains the significance of the similarities and differences identified — not just catalogues them.</p>"},
            {"type": "cta", "value": {
                "heading": "Master every essay type on our platform",
                "body": "Writers Creek assigns work across all academic disciplines and essay types. Apply to join and take assignments that match your subject expertise and writing strengths.",
                "button_text": "Apply to Writers Creek",
                "button_url": "/apply",
                "style": "primary",
            }},
        ],
    },
    # ── 6. Platform earnings strategy ────────────────────────────────────────
    {
        "slug": "how-to-maximise-earnings-academic-writing-platform",
        "title": "How to Maximise Your Earnings on an Academic Writing Platform",
        "seo_title": "How to Earn More as a Freelance Academic Writer | Platform Strategy | Writers Creek",
        "search_description": "The writers earning the most on academic writing platforms are not necessarily the fastest. They are the most strategic. This guide covers bid selection, tier advancement, and the habits that compound income over time.",
        "category_slug": "platform-guides",
        "tags": ["freelance academic writer income", "academic writing platform", "writer earnings", "writer tier", "freelance writing strategy"],
        "excerpt": "Most writers on academic platforms earn well below their potential — not because of a lack of skill, but because of how they select assignments, manage their time, and position themselves for tier advancement. This guide changes that.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Specialise in 2–3 high-demand, high-pay subjects rather than accepting everything",
                "On-time delivery rate and quality rating are the two metrics that unlock higher-earning tiers",
                "Reject low-fit assignments — a revision on a poorly matched paper costs more than the job paid",
                "Your effective hourly rate matters more than your per-page rate — track it",
                "Writers who deliver early and communicate proactively get offered more assignments directly",
            ]}},
            {"type": "heading", "value": {"text": "Track Your Effective Hourly Rate", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Per-page rate is the wrong number to optimise. What matters is how much you earn per hour of actual work. A $28/page assignment that takes 90 minutes per page pays $18.67/hour. A $22/page assignment in a subject you know deeply that takes 40 minutes per page pays $33/hour. The lower-rated assignment pays more.</p><p>Track your time per assignment for 2–3 months. You will quickly identify which subject areas and paper types give you the best effective hourly rate. Shift your acceptance decisions towards those assignments.</p>"},
            {"type": "heading", "value": {"text": "Selective Acceptance Is an Earnings Strategy", "level": "h2"}},
            {"type": "paragraph", "value": "<p>New writers make the mistake of accepting every available assignment to maximise volume. Experienced writers are selective. Here is why: a revision request on a badly matched assignment consumes 1–3 hours of unpaid revision time and damages your quality rating. A dispute or low rating carries a penalty that reduces assignment access for weeks. The cost of a poor match is far higher than the earnings from one assignment.</p><p>Decline assignments where: the subject is outside your demonstrated expertise, the deadline is tighter than your realistic time-per-page baseline allows, or the brief is ambiguous and the client has not responded to a clarification request.</p>"},
            {"type": "heading", "value": {"text": "How Tier Advancement Changes Your Earnings", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The compounding effect of tier advancement is the most underappreciated earnings lever on academic writing platforms. Moving from Entry ($18–22/page) to Standard ($24–28/page) is a 25–33% income increase on the same volume. Moving from Standard to Senior ($30–36/page) is another 20–30%. The quality habits that drive tier advancement are the same habits that produce the best per-hour earnings regardless of tier. They compound in both directions.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek and grow your income", "url": "/apply"}},
        ],
    },
    # ── 7. Research efficiency ────────────────────────────────────────────────
    {
        "slug": "how-to-research-academic-papers-efficiently",
        "title": "How to Research Academic Papers Efficiently: A Freelance Writer's Workflow",
        "seo_title": "How to Research Academic Papers Fast | Freelance Writer Workflow | Writers Creek",
        "search_description": "Research is the most time-consuming phase of academic writing. This guide covers the search strategies, database tools, and source-evaluation habits that cut research time without cutting quality.",
        "category_slug": "writing-craft",
        "tags": ["academic research", "academic databases", "Google Scholar", "peer-reviewed sources", "freelance writing workflow"],
        "excerpt": "Most writers spend too long on research — not because they are thorough, but because they search without a strategy. A structured research workflow cuts this phase by 30–40% without reducing source quality.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Define exactly what you are looking for before you open any database",
                "Google Scholar, PubMed, JSTOR, and CINAHL cover 95% of academic writing needs",
                "Use Boolean operators (AND, OR, NOT) to narrow searches immediately",
                "Check the reference lists of strong sources — this is faster than broad searching",
                "Distinguish between sources you will cite and sources that give you background understanding",
            ]}},
            {"type": "heading", "value": {"text": "Define Your Research Questions Before Searching", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most common cause of slow, inefficient research is starting a database search without knowing exactly what you are looking for. Before opening Google Scholar or PubMed, write down: the specific claim or section of the paper that needs a source, the type of source required (systematic review, RCT, qualitative study, theoretical framework), and the date range (last 5 years unless the assignment specifies otherwise).</p><p>With these three parameters clear, you can construct a precise search string immediately rather than browsing broadly and reading abstracts that turn out to be irrelevant.</p>"},
            {"type": "heading", "value": {"text": "The Four Databases That Cover Most Assignments", "level": "h2"}},
            {"type": "paragraph", "value": "<p><strong>Google Scholar</strong> — the starting point for most subjects. Use the 'Cited by' feature to find more recent papers that build on a foundational source. Use the date filter (custom range) to restrict to recent publications. Check for free PDF links (look for [PDF] tags on the right side).</p><p><strong>PubMed</strong> — essential for nursing, medicine, pharmacology, and public health. Free access to all abstracts and many full-text articles through PubMed Central. Use MeSH terms for precise searches.</p><p><strong>JSTOR</strong> — best for humanities, social sciences, history, and economics. Strong for foundational papers and theoretical frameworks.</p><p><strong>CINAHL (via institution or library access)</strong> — the definitive database for nursing and allied health literature. If your assignment platform provides academic database access, CINAHL should be your first stop for nursing papers.</p>"},
            {"type": "heading", "value": {"text": "Mining Reference Lists for Sources", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When you find one high-quality, directly relevant source, read its reference list. Papers cite the most important prior work in the field. A strong 2023 systematic review will have already done part of your literature search for you — its references are a curated list of relevant prior studies. This technique is faster and more targeted than running new database searches.</p><p>Apply the same technique in reverse using 'Cited by' in Google Scholar: find papers that have cited your source since it was published. This identifies the most current work building on the same foundation.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
    # ── 8. Client communication ───────────────────────────────────────────────
    {
        "slug": "client-communication-academic-writing-platform",
        "title": "Client Communication on Academic Writing Platforms: How to Get It Right",
        "seo_title": "Client Communication for Academic Writers | Platform Best Practices | Writers Creek",
        "search_description": "Clear, professional client communication reduces revision rates, builds long-term client relationships, and protects your quality rating. Here is how experienced platform writers handle it.",
        "category_slug": "platform-guides",
        "tags": ["client communication", "academic writing platform", "freelance writer tips", "revision prevention", "writer-client relationship"],
        "excerpt": "Most revision requests are preventable. The majority trace back to a single source: insufficient communication before writing begins. This guide covers what to ask, when to ask it, and how to set client expectations that protect your rating.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Clarify ambiguities before you start — not when you are halfway through",
                "Confirm source count, citation style, and required sections in every first message",
                "Set a mid-point check-in for longer assignments — it prevents major structural rework",
                "Respond to client messages within 2 hours during active assignments",
                "Document all client instructions in writing — verbal agreements cannot be referenced later",
            ]}},
            {"type": "heading", "value": {"text": "The Pre-Assignment Clarification Message", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When you accept an assignment, send a brief confirmation message that covers three things: your understanding of the scope (paper type, length, citation style), any specific questions about the brief (ambiguous requirements, missing information), and your expected delivery timeline.</p><p>This message does three things: it confirms that you have read the brief, it gives the client an opportunity to correct any misunderstandings before you write, and it establishes a documented record of the assignment terms. Most revision requests that are not your fault — where the client changes requirements after submission — are much easier to dispute when you have a clear message thread establishing the original scope.</p>"},
            {"type": "heading", "value": {"text": "What to Ask Before Every Assignment", "level": "h2"}},
            {"type": "checklist", "value": {"title": "Pre-Writing Clarification Checklist", "items": [
                {"text": "Is the word count a minimum, maximum, or exact target?", "detail": ""},
                {"text": "Which citation style is required — and is it the 7th edition (APA), 9th edition (MLA), or 17th (Chicago)?", "detail": ""},
                {"text": "How many sources are required, and must they be peer-reviewed?", "detail": ""},
                {"text": "Are there specific required sections (abstract, methodology, executive summary)?", "detail": ""},
                {"text": "Is there a rubric or marking criteria attached that should guide the structure?", "detail": ""},
                {"text": "Are there any sources the client specifically wants included or excluded?", "detail": ""},
            ]}},
            {"type": "heading", "value": {"text": "Managing Revision Requests Professionally", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When a revision request arrives, read it completely before responding or making changes. Understand exactly what is being asked and why. Acknowledge receipt professionally: 'Thank you for the feedback. I will address [specific points] and return the revised paper by [time]. Please let me know if you have any additional notes.'</p><p>Do not argue with revision feedback, even when you believe the original submission was correct. If a client requests a change that contradicts the original brief, note this politely: 'I have made the changes you requested. I note this differs from the original brief, which specified [X] — please confirm the updated requirement so I can apply it consistently.' This creates a documented record without being combative.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed Writers Creek blog with writer-focused articles"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--site", default="writerscreek.com")
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
            self.stderr.write(self.style.ERROR(
                f"No Wagtail site for '{hostname}'. Run setup_tenants first."
            ))
            return

        blog_index = BlogIndexPage.objects.child_of(site.root_page).first()
        if not blog_index:
            self.stderr.write(self.style.ERROR(
                "No BlogIndexPage under this site's root. Run setup_tenants first."
            ))
            return

        # Author
        author, created = Author.objects.get_or_create(
            site=site,
            slug=AUTHOR["slug"],
            defaults={"name": AUTHOR["name"], "credentials": AUTHOR["credentials"], "bio": AUTHOR["bio"]},
        )
        self.stdout.write(f"  {'CREATE' if created else 'EXISTS '}  author: {author.name}")

        # Categories
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
            self.stdout.write(f"  {'CREATE' if created else 'EXISTS '}  category: {cat.name}")

        # Posts
        existing_slugs = set(
            BlogPostPage.objects.child_of(blog_index).values_list("slug", flat=True)
        )
        created_count = updated = skipped = 0

        for post_data in POSTS:
            slug = post_data["slug"]
            category = cat_map.get(post_data["category_slug"])

            if slug in existing_slugs:
                if not do_update:
                    self.stdout.write(f"  SKIP   post: {slug}")
                    skipped += 1
                    continue
                page = BlogPostPage.objects.child_of(blog_index).get(slug=slug)
                self._apply_fields(page, post_data, author, category)
                page.save_revision().publish()
                self._apply_tags(page, post_data, site)
                self.stdout.write(self.style.WARNING(f"  UPDATE post: {slug}"))
                updated += 1
            else:
                page = BlogPostPage(title=post_data["title"], slug=slug, live=True, primary_author=author)
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
        page.tags.clear()
        for name in data.get("tags", []):
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
