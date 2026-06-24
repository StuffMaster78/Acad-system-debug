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


POSTS += [
    # ── Writing Craft (3 new) ──────────────────────────────────────────────────
    {
        "slug": "writing-compelling-introductions-and-conclusions",
        "title": "Writing Introductions and Conclusions That Impress Markers",
        "seo_title": "How to Write Academic Introductions and Conclusions | Writers Creek",
        "search_description": "The introduction and conclusion are the most-read sections of any essay. Here is how to write both so they frame and reinforce a first-class argument.",
        "category_slug": "writing-craft",
        "tags": ["academic writing", "essay introductions", "conclusions", "thesis statement", "writing craft"],
        "excerpt": "Markers read introductions first and conclusions last — these are the two sections that form the strongest impression. A weak introduction or trailing conclusion can undermine an otherwise strong essay.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "An introduction should state the argument, not just the topic",
                "Context, thesis, and roadmap: these are the three elements every introduction needs",
                "Conclusions must add synthesis — they cannot simply summarise what was already said",
                "The final sentence should leave the marker with a clear sense of the essay's significance",
                "Avoid starting conclusions with 'In conclusion' — it signals a weak ending",
            ]}},
            {"type": "heading", "value": {"text": "What a Strong Introduction Actually Does", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A common misconception is that an introduction is just background. It is not. An introduction performs three jobs: it establishes context (why this topic matters), states the thesis (the specific argument the essay will make), and maps the structure (briefly, in one or two sentences, how the essay will proceed).</p><p>Context should be minimal — two to three sentences at most. The majority of the introduction should be devoted to the thesis. A thesis like <em>'This essay will examine climate change policy'</em> is not a thesis — it is a topic sentence. A real thesis commits to an argument: <em>'Current climate policy frameworks fail because they prioritise emissions reduction targets over adaptation infrastructure, leaving the most vulnerable populations inadequately protected.'</em></p>"},
            {"type": "heading", "value": {"text": "Structuring the Roadmap", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A roadmap sentence tells the marker how the argument will be structured. For a 2,000-word essay, one roadmap sentence is enough. For a dissertation chapter, two or three sentences are appropriate. The roadmap should reflect the actual structure — if you add or remove sections during writing, update the introduction accordingly before submission.</p><p>Avoid listing everything the essay will cover. Instead, state the logical sequence of your argument: <em>'The essay first establishes the theoretical framework, then analyses three case studies, and concludes by evaluating whether the framework holds across different contexts.'</em></p>"},
            {"type": "heading", "value": {"text": "Writing a Conclusion That Adds Value", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The conclusion's job is synthesis and significance — not summary. Repeating the points made in the body is the most common conclusion error. Instead, show how those points combine to support the thesis in a new way, or what the thesis implies beyond the specific argument of the essay.</p><p>A strong conclusion often moves from the specific (the essay's argument) to the general (its broader implication): what does this argument suggest about the field, the policy, or the problem at large? This gives the marker a sense of intellectual scope that distinguishes high-quality work.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "integrating-evidence-and-sources-academic-writing",
        "title": "How to Integrate Sources and Evidence in Academic Writing",
        "seo_title": "Integrating Evidence in Academic Writing | Source Integration Guide | Writers Creek",
        "search_description": "Poor source integration is one of the most common reasons for mark deductions. This guide covers direct quotation, paraphrase, and synthesis — and when to use each.",
        "category_slug": "writing-craft",
        "tags": ["academic writing", "source integration", "quoting", "paraphrasing", "evidence"],
        "excerpt": "Evidence does not speak for itself. Every source you include needs to be introduced, presented, and analysed. Writers who drop quotations without commentary lose marks even when their sources are excellent.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Direct quotation should be used sparingly — paraphrase is preferred in most academic work",
                "Every piece of evidence needs three elements: introduction, evidence, analysis",
                "Synthesis is higher-order than paraphrase — it combines multiple sources into your own argument",
                "Never end a paragraph with a quotation or citation — always follow with your own analysis",
                "The 'quote sandwich' technique prevents dropped quotations and lost marks",
            ]}},
            {"type": "heading", "value": {"text": "The Quote Sandwich Technique", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Every piece of evidence should be presented using a three-part structure: introduce the source (who says this and in what context), present the evidence (the quotation or paraphrase), then analyse it (what this means for your argument). This is sometimes called the 'quote sandwich'.</p><p>Example: <em>Smith (2021) identifies a systematic failure in post-2008 regulatory frameworks, noting that 'capital requirements remained structurally inadequate for the leverage levels that major institutions had accumulated' (p. 47). This directly supports the argument that regulatory capture — not market complexity — was the primary failure mode of the crisis.</em></p><p>Notice that the quotation is introduced with the author's name and context, and immediately followed by analytical commentary that connects it to the essay's argument.</p>"},
            {"type": "heading", "value": {"text": "When to Quote and When to Paraphrase", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Use a direct quotation when the exact wording is significant — for instance, when analysing a specific claim, a legal definition, or a phrase from a primary source. Use paraphrase for everything else. In most academic work, a ratio of roughly one direct quotation per 300–400 words is appropriate. Heavy quoting signals a lack of analytical engagement.</p><p>Paraphrase is not just changing a few words — it is restating the idea in your own language with your own sentence structure. A paraphrase that merely substitutes synonyms while preserving the original sentence structure is not a true paraphrase, and risks plagiarism detection even when cited.</p>"},
            {"type": "heading", "value": {"text": "Synthesising Multiple Sources", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Synthesis — combining multiple sources to build a new point — is the highest-order evidence skill in academic writing. Instead of presenting Smith, then Jones, then Brown sequentially, you weave them together: <em>'Both Smith (2021) and Jones (2019) identify regulatory capture as a primary cause, though they disagree on its mechanism — Smith emphasises legislative lobbying while Jones focuses on the revolving door between regulators and the institutions they oversaw.'</em></p><p>Synthesis shows the marker that you have read across the literature and are making independent analytical judgements about how sources relate to each other.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "writing-at-undergraduate-masters-phd-level",
        "title": "Writing at Undergraduate, Master's, and PhD Level: What Changes",
        "seo_title": "Academic Writing at Different Levels | Undergraduate vs Masters vs PhD | Writers Creek",
        "search_description": "The expectations for academic writing shift significantly between undergraduate, postgraduate, and doctoral work. Understanding these differences helps writers deliver work that matches the right standard.",
        "category_slug": "writing-craft",
        "tags": ["academic writing levels", "undergraduate writing", "masters writing", "PhD writing", "academic standards"],
        "excerpt": "A well-written 2:1 undergraduate essay is not the same as a well-written Master's essay. The expectations for argument depth, source engagement, originality, and critical analysis all shift as level increases. Writers who know these differences can calibrate their work precisely.",
        "reading_time": 9,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Undergraduate: demonstrate knowledge and apply theoretical frameworks competently",
                "Master's: critically evaluate frameworks and show awareness of their limitations",
                "PhD: make an original contribution — synthesise, challenge, or extend existing knowledge",
                "The language of argument becomes more hedged and precise at higher levels",
                "Source depth and recency expectations increase significantly at postgraduate level",
            ]}},
            {"type": "heading", "value": {"text": "Undergraduate Writing: Competent Application", "level": "h2"}},
            {"type": "paragraph", "value": "<p>At undergraduate level, the primary expectation is knowledge demonstration and competent application. An undergraduate essay should show that the student understands the key theories, debates, and evidence in the field, and can apply them to the question at hand.</p><p>First-class undergraduate work goes further: it selects among competing frameworks rather than simply listing them, and it makes clear analytical judgements rather than presenting evidence neutrally. But the originality expected is limited — undergraduate work is generally not expected to develop new theory.</p>"},
            {"type": "heading", "value": {"text": "Master's Writing: Critical Evaluation", "level": "h2"}},
            {"type": "paragraph", "value": "<p>At Master's level, the expectation shifts from application to critical evaluation. It is no longer enough to apply a framework — you must evaluate its assumptions, identify its limitations, and compare it against alternatives. A Master's student is expected to engage with methodological debates, not just conclusions.</p><p>Source expectations also change. At undergraduate level, five to ten sources per thousand words is typical. At Master's level, the literature review component alone may require 30–50 sources, and sources should generally be from the last five years unless citing foundational work. Older sources require explicit justification.</p>"},
            {"type": "heading", "value": {"text": "Doctoral Writing: Original Contribution", "level": "h2"}},
            {"type": "paragraph", "value": "<p>PhD-level writing is distinguished by the requirement for original contribution. This does not mean starting from scratch — it means locating a gap in the existing literature and making a specific, defensible claim about how your work addresses that gap.</p><p>The language of doctoral writing is typically more hedged and precise than lower-level work. Claims are qualified ('the evidence suggests' rather than 'it is clear'), scope is explicitly acknowledged ('within the limitations of this study'), and the discussion of methodology is proportionally larger. Writers working at doctoral level should expect to engage deeply with epistemological and methodological framing that would be out of place at undergraduate level.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
    # ── Referencing & Style (3 new) ────────────────────────────────────────────
    {
        "slug": "vancouver-ieee-citation-guide-for-writers",
        "title": "Vancouver and IEEE Citation Styles: A Practical Guide for Writers",
        "seo_title": "Vancouver and IEEE Citation Guide | Academic Referencing for Writers | Writers Creek",
        "search_description": "Vancouver and IEEE are the citation styles used in medicine, nursing, engineering, and computer science. This guide covers the numbering system, in-text citations, and reference list format for both.",
        "category_slug": "referencing-style",
        "tags": ["Vancouver citation", "IEEE citation", "academic referencing", "nursing citation", "engineering referencing"],
        "excerpt": "Vancouver and IEEE are numbered citation systems used across medicine, nursing, and engineering. Unlike author-date styles, they use superscript numbers or bracketed numbers in-text, with a reference list in citation order. Getting the format right is straightforward once you understand the logic.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Both Vancouver and IEEE use numbers in-text, not author-date pairs",
                "References are listed in the order they appear in the text, not alphabetically",
                "Vancouver uses superscript numbers; IEEE uses bracketed numbers [1]",
                "The same source always keeps the same number throughout the paper",
                "Journal article titles are not italicised in Vancouver; journal names are abbreviated",
            ]}},
            {"type": "heading", "value": {"text": "How Numbered Systems Work", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Vancouver and IEEE are both numbered citation systems. Instead of (Author, Year) in-text, you insert a number — either superscript<sup>1</sup> (Vancouver) or in square brackets [1] (IEEE). The reference list at the end is organised by the order in which sources first appear in the text, not alphabetically.</p><p>The key rule: once a source is assigned a number, it keeps that number for the entire paper. If you cite the same source five times, the same number appears each time. This makes the system efficient but means that adding a new source early in the document requires renumbering everything that follows.</p>"},
            {"type": "heading", "value": {"text": "Vancouver Format: Journal Articles", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A Vancouver reference for a journal article follows this structure: Author(s). Article title. <em>Abbreviated Journal Name</em>. Year;Volume(Issue):Pages.</p><p>Example: <code>Smith J, Brown K. Antibiotic stewardship in secondary care. <em>BMJ</em>. 2022;378:e071124.</code></p><p>Note: journal names are abbreviated according to the National Library of Medicine catalogue. Article titles use sentence case (only the first word and proper nouns are capitalised). Author surnames are listed with initials — no full first names. When there are more than six authors, list the first six then add 'et al.'</p>"},
            {"type": "heading", "value": {"text": "IEEE Format: Key Differences", "level": "h2"}},
            {"type": "paragraph", "value": "<p>IEEE references follow a similar structure but with key differences: author initials precede the surname (J. Smith rather than Smith J), article titles appear in quotation marks rather than plain text, journal names are italicised and not abbreviated, and the volume and issue format differs.</p><p>Example: <code>J. Smith and K. Brown, \"Antibiotic stewardship in secondary care,\" <em>British Medical Journal</em>, vol. 378, p. e071124, 2022.</code></p><p>IEEE is the dominant style for computer science, electrical engineering, and technology assignments. If the assignment specifies IEEE, confirm whether the client wants IEEE style for all referencing or only for technical sources — some assignments use IEEE only for citations of standards and patents.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "avoiding-common-referencing-mistakes",
        "title": "The Most Common Referencing Mistakes Writers Make (and How to Avoid Them)",
        "seo_title": "Common Referencing Mistakes to Avoid | Academic Citation Errors | Writers Creek",
        "search_description": "Referencing errors are one of the most preventable causes of mark deductions. This guide covers the mistakes that appear most frequently in academic work and how to eliminate them.",
        "category_slug": "referencing-style",
        "tags": ["referencing mistakes", "citation errors", "APA mistakes", "Harvard referencing", "academic writing quality"],
        "excerpt": "A technically strong essay with poor referencing can lose significant marks. Most referencing errors are not random — they follow predictable patterns. Knowing the ten most common mistakes lets you eliminate them systematically.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Mismatched in-text citations and reference list entries are the most penalised error",
                "Page numbers are required for direct quotations in APA and Harvard — never omit them",
                "Secondary citations (citing a source you found in another source) should be minimised",
                "DOIs are now required for all journal articles in APA 7th edition",
                "Website citations must include access dates — this is often forgotten",
            ]}},
            {"type": "heading", "value": {"text": "Mismatch Between In-Text and Reference List", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The single most penalised referencing error is a mismatch between in-text citations and the reference list. This means citing (Johnson, 2021) in the text but having Johnson listed as 2019 in the reference list, or having the reference list include sources not cited in the body. Markers check this systematically.</p><p>Always build your reference list as you write rather than retrospectively. Add each new source to the list the moment you cite it, and do a final cross-check before submission: every in-text citation should have a matching reference list entry, and every reference list entry should correspond to an in-text citation.</p>"},
            {"type": "heading", "value": {"text": "Page Numbers for Direct Quotations", "level": "h2"}},
            {"type": "paragraph", "value": "<p>In APA 7th edition and Harvard, page numbers are mandatory for all direct quotations. Writing (Smith, 2021) after a quotation is incomplete — it must be (Smith, 2021, p. 47) or (Smith, 2021, pp. 47–48). Many writers omit page numbers assuming they are optional. They are not, and their absence is marked as an error.</p><p>For sources without traditional page numbers (websites, ebooks), use paragraph numbers (para. 3) or section headings (under 'Methodology' heading) instead. If no location information is available, state that explicitly in a note.</p>"},
            {"type": "heading", "value": {"text": "Secondary Citations and Why to Avoid Them", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A secondary citation occurs when you cite a source that you found cited in another source, without reading the original. In APA: 'as cited in Smith (2021)'. Secondary citations are technically acceptable but signal that you have not engaged with the primary literature. Most marking rubrics penalise heavy use of secondary citations.</p><p>If a source is important enough to cite, locate and read the original. University library database access, Google Scholar, and ResearchGate can usually provide the original within minutes. If the original is genuinely inaccessible, limit secondary citations to one or two per assignment and use them only for historical or foundational sources.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "turabian-oscola-referencing-guide",
        "title": "Turabian and OSCOLA: Referencing Styles for History and Law Writers",
        "seo_title": "Turabian and OSCOLA Citation Guide | History and Law Referencing | Writers Creek",
        "search_description": "Turabian is the student version of Chicago style used in history and the humanities. OSCOLA is the standard legal citation style in UK law schools. This guide covers both for academic writers.",
        "category_slug": "referencing-style",
        "tags": ["Turabian", "OSCOLA", "Chicago referencing", "legal citation", "history referencing"],
        "excerpt": "History and humanities assignments typically use Turabian (the student version of Chicago), while UK law assignments require OSCOLA. Both have distinct conventions around footnotes, bibliography format, and how to cite primary sources — conventions that differ significantly from author-date styles.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Turabian uses footnotes for citations, not in-text author-date pairs",
                "First footnote citations are full; subsequent citations use shortened form (ibid. or Author, shortened title)",
                "OSCOLA uses footnotes only — there is no bibliography requirement in most UK law assessments",
                "Case names in OSCOLA are italicised; legislation is not",
                "Both styles require careful distinction between primary and secondary sources",
            ]}},
            {"type": "heading", "value": {"text": "Turabian: Footnote-Based Citation for the Humanities", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Turabian (formally the <em>Manual for Writers of Research Papers, Theses, and Dissertations</em>) is the student edition of Chicago style. It is used primarily in history, the classics, art history, music, and some social science disciplines. Unlike APA or Harvard, Turabian places citations in footnotes rather than in-text.</p><p>The first citation of a source gives the full details: Author First Surname, <em>Title of Work</em> (Place: Publisher, Year), page number. Example: <code>John Smith, <em>The Industrial Revolution in Britain</em> (London: Routledge, 2019), 142.</code> Subsequent citations of the same source use a shortened form: Smith, <em>Industrial Revolution</em>, 145. If citing the same source immediately after, 'ibid.' is used with a new page number: Ibid., 147.</p>"},
            {"type": "heading", "value": {"text": "OSCOLA: Legal Citations in UK Law", "level": "h2"}},
            {"type": "paragraph", "value": "<p>OSCOLA (Oxford University Standard for the Citation of Legal Authorities) is the standard for UK law school assessments. Like Turabian, it uses footnotes rather than in-text citations, but the format is specific to legal sources.</p><p>Case citations use the format: <em>Donoghue v Stevenson</em> [1932] AC 562 (HL). Note the case name is italicised, the year and report series are in brackets, and the court is abbreviated in parentheses. Legislation is <strong>not</strong> italicised: Misrepresentation Act 1967, s 2(1). Journal articles follow: Author, 'Title' (Year) Volume Journal Abbreviation Start Page, Pinpoint.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    # ── Platform Guides (3 new) ────────────────────────────────────────────────
    {
        "slug": "how-to-bid-on-orders-and-win-more-work",
        "title": "How to Bid on Orders and Win More Work on Writing Platforms",
        "seo_title": "How to Bid on Writing Platform Orders | Win More Assignments | Writers Creek",
        "search_description": "Most writers on academic platforms submit generic bids and wonder why their conversion rate is low. This guide covers what clients look for in a bid and how to write one that stands out.",
        "category_slug": "platform-guides",
        "tags": ["bidding on orders", "academic writing platform", "freelance academic writer", "winning bids", "writers creek tips"],
        "excerpt": "A generic bid gets ignored. A bid that shows you have read the brief, understood the requirements, and can deliver exactly what the client needs wins the order. The difference is two minutes of careful reading and one specific sentence.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Read the full brief before bidding — never bid blind",
                "Reference one specific detail from the brief to show you have read it",
                "State your relevant experience concisely — one sentence, not a paragraph",
                "Offer a clear confirmation of what you will deliver and by when",
                "Do not compete on price alone — compete on relevance and reliability",
            ]}},
            {"type": "heading", "value": {"text": "What Clients Actually Look For in a Bid", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Clients receive multiple bids for most orders. They are scanning for two things: evidence that the writer has read the brief, and confidence that the writer can deliver what they need. Generic opening sentences like 'I am an experienced academic writer with expertise in many subjects' provide neither.</p><p>The most effective bids are short (3–5 sentences), specific (reference something from the actual brief), and confident (tell the client what you will deliver, not what you think you might be able to do). Clients are busy. They will not read a long bid — they will skim for relevance.</p>"},
            {"type": "heading", "value": {"text": "The One Sentence That Wins Orders", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The single most effective sentence in any bid is one that references a specific element of the brief: <em>'I can see you need this in APA 7th using a minimum of 12 peer-reviewed sources from the last five years — I work with this requirement regularly and will include a reference list in that format.'</em></p><p>This sentence is specific enough to prove you read the brief and experienced enough to show you know what you are talking about. It costs nothing to write but dramatically increases bid conversion rates.</p>"},
            {"type": "heading", "value": {"text": "Pricing Your Bid Competitively Without a Race to the Bottom", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Competing solely on price is a short-term strategy with long-term costs. The lowest bid rarely builds the kind of client relationship that leads to repeat orders and platform reputation growth. Instead, price at the rate you need to deliver high-quality work, and justify that rate with your specific qualifications or experience relevant to the brief.</p><p>If the client's budget is lower than your minimum rate, do not adjust your quality expectations to fit. Either decline and move to the next order, or explain briefly why your rate reflects the quality they need. Writers who undercharge and then rush to make up time are the writers who accumulate revisions and poor ratings.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "understanding-assignment-briefs-and-rubrics",
        "title": "How to Read Assignment Briefs and Marking Rubrics Like a Pro",
        "seo_title": "Understanding Assignment Briefs and Rubrics | Academic Writers Guide | Writers Creek",
        "search_description": "Misreading a brief is the leading cause of avoidable revisions. This guide walks through how to extract every requirement from a brief and translate a marking rubric into a writing plan.",
        "category_slug": "platform-guides",
        "tags": ["assignment brief", "marking rubric", "academic writing", "order requirements", "revision prevention"],
        "excerpt": "Most avoidable revisions trace back to misreading the brief. A client who asked for a 'critical analysis' wanted something different from a 'discussion', and the writer who knows the difference avoids a revision request. Brief-reading is a skill, not just a habit.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Extract every constraint from the brief before you begin: word count, sources, style, structure, deadline",
                "Identify the command word — 'analyse', 'evaluate', and 'discuss' require different responses",
                "A marking rubric is a blueprint — map each criterion to a section of your outline",
                "If anything in the brief is ambiguous, clarify with the client before starting",
                "Read the brief again when you finish — check you have addressed every requirement",
            ]}},
            {"type": "heading", "value": {"text": "The Brief Extraction Checklist", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Before writing a single word, read the brief and extract the following: word count (and whether this includes or excludes references and appendices), citation style and edition, minimum and maximum source count, source type requirements (peer-reviewed journals only? Primary sources?), required structure (is there a mandatory section format?), and the specific question or task to be addressed.</p><p>Any ambiguity in any of these areas should be clarified with the client immediately. A brief that says 'use Harvard referencing' without specifying which Harvard variant (Anglia Ruskin, Leeds, Cite Them Right) can result in a revision if the client's institution uses a specific version.</p>"},
            {"type": "heading", "value": {"text": "Decoding Command Words", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The command word in a question tells you what kind of response is expected. The most commonly confused pairs are <strong>discuss</strong> (present multiple perspectives on an issue without necessarily concluding) versus <strong>evaluate</strong> (make a judgement about the relative merits of positions or evidence), and <strong>describe</strong> (provide factual detail) versus <strong>analyse</strong> (break down and examine components, causes, or implications).</p><p>A 'critically evaluate' question requires the highest level of engagement: you must identify the evidence for and against a position, assess the quality of that evidence, and reach a justified conclusion. Writing a description or discussion in response to this instruction will result in a revision request regardless of the quality of the writing itself.</p>"},
            {"type": "heading", "value": {"text": "Using the Rubric as a Writing Plan", "level": "h2"}},
            {"type": "paragraph", "value": "<p>When a marking rubric is provided, use it as the structure for your planning. Each criterion on the rubric represents marks. Map each criterion to a section of your outline and allocate proportional space: if 'critical analysis' is worth 40% of the marks, roughly 40% of the content should be analytical rather than descriptive.</p><p>In your final check before submission, read each rubric criterion and ask: does this paper clearly address this requirement? Markers are reading against the rubric — your paper should make it easy for them to award the marks available.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "building-your-writer-profile-and-reputation",
        "title": "Building Your Writer Profile and Reputation on an Academic Platform",
        "seo_title": "Build Your Academic Writer Profile | Platform Reputation Guide | Writers Creek",
        "search_description": "Your profile and rating are your primary sales tools on an academic writing platform. This guide covers how to build a profile that wins orders and how to protect and grow your reputation over time.",
        "category_slug": "platform-guides",
        "tags": ["writer profile", "academic writing platform", "reputation management", "writer rating", "platform success"],
        "excerpt": "A strong profile converts browsers into clients. A strong rating keeps existing clients coming back and attracts new ones. Both require deliberate attention — neither happens automatically, and both are far easier to build than to repair.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Specialise early — a focused profile converts better than a broad one",
                "Your first five ratings are disproportionately important — deliver exceptional work on early orders",
                "Respond to messages promptly — response time is a visible metric on most platforms",
                "Never accept an order you cannot complete to a high standard by the deadline",
                "A single strong long-term client relationship is worth more than many one-off orders",
            ]}},
            {"type": "heading", "value": {"text": "Specialising Your Profile for Better Conversion", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Writers who claim expertise in 'all subjects' are trusted by clients for none of them. A profile that specifies a clear area of expertise — nursing and healthcare, business and management, law and criminology — attracts clients in that area who are more likely to return and more likely to be satisfied because the writer's actual skills match their subject.</p><p>Identify your strongest two or three subject areas, your experience with specific assignment types (dissertations, systematic reviews, case studies), and the citation styles you are most proficient in. Lead with these in your profile and in your bids.</p>"},
            {"type": "heading", "value": {"text": "Protecting Your Rating", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Your rating is the most valuable asset you have on a writing platform. It takes time to build and can be damaged quickly. The primary protection is simple: never accept an order you cannot complete to a genuinely high standard within the deadline. Accepting work outside your expertise or agreeing to unrealistic timelines are the two most common causes of rating damage.</p><p>When a revision is requested, treat it as a priority. Fast, professional responses to revisions — even when you believe the original work was correct — protect the client relationship and your platform standing. Responding defensively to revision requests is one of the most reliably career-limiting habits on any writing platform.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    # ── Career & Workflow (3 new) ──────────────────────────────────────────────
    {
        "slug": "avoiding-burnout-as-a-freelance-academic-writer",
        "title": "Avoiding Burnout as a Freelance Academic Writer",
        "seo_title": "Avoiding Writer Burnout | Freelance Academic Writing Wellbeing | Writers Creek",
        "search_description": "Freelance academic writing burnout is real and more common than writers admit. This guide covers the warning signs, the structural causes, and the practical steps that prevent it.",
        "category_slug": "career-workflow",
        "tags": ["writer burnout", "freelance wellbeing", "academic writing career", "sustainable writing", "freelance workflow"],
        "excerpt": "Freelance writing burnout rarely arrives suddenly. It builds through a pattern of overcommitment, missed recovery time, and declining quality that the writer notices but cannot stop. The time to address it is before it becomes visible in your work.",
        "reading_time": 7,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Burnout is cumulative — it builds from sustained overcommitment, not single overloads",
                "The first sign is usually declining interest in quality, not declining output",
                "Set a weekly word-count ceiling and hold to it, even when more orders are available",
                "Scheduled non-writing time is not a luxury — it is a productivity investment",
                "Taking on a difficult order when already overloaded is almost always a false economy",
            ]}},
            {"type": "heading", "value": {"text": "Recognising the Warning Signs Early", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The first sign of academic writing burnout is rarely a sudden inability to write — it is a gradual decline in the care you take. You start accepting that your analysis is shallower than it could be. You stop checking references as carefully. You find yourself reaching for the first adequate phrase rather than the right one. These are warning signs that you are operating at above-sustainable capacity.</p><p>The second sign is deadline dread — not the productive tension of a challenging order, but a generalised anxiety about the work queue that persists even after orders are submitted. If every completed order immediately triggers anxiety about the next, the underlying issue is structural, not motivational.</p>"},
            {"type": "heading", "value": {"text": "The Weekly Ceiling: A Practical Protection", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most effective structural protection against burnout is a weekly word-count ceiling — a maximum you commit to not exceeding regardless of what is available. This ceiling should be calculated based on the quality of work you can sustain, not the maximum you can physically produce in a week. For most writers, this is significantly lower than their peak output under pressure.</p><p>The ceiling also protects your rating. The marginal revenue from taking one more order when you are already near capacity is almost always less valuable than the rating protection of delivering your existing commitments to a genuinely high standard.</p>"},
            {"type": "heading", "value": {"text": "Scheduling Recovery", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Writing is cognitively demanding work. Recovery is not laziness — it is the biological mechanism that makes tomorrow's work possible. Schedule at least one full day off from all writing per week, and protect it. Writers who work seven days a week consistently produce lower-quality work than those who work five or six days with genuine rest days.</p><p>Within working days, take a complete break from screens for at least 30 minutes in the middle of the session. Evidence from cognitive science is consistent on this point: sustained attention degrades faster than writers typically acknowledge, and the quality difference between work produced in a fresh versus depleted state is measurable.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "time-management-techniques-for-academic-writers",
        "title": "Time Management Techniques That Actually Work for Academic Writers",
        "seo_title": "Time Management for Freelance Academic Writers | Productivity Techniques | Writers Creek",
        "search_description": "Generic productivity advice rarely accounts for the specific demands of academic writing. This guide covers techniques that work for deadline-driven, research-intensive, long-form writing work.",
        "category_slug": "career-workflow",
        "tags": ["time management", "academic writing productivity", "freelance workflow", "deadline management", "writer productivity"],
        "excerpt": "Academic writing is not like other freelance work. Research, drafting, referencing, and revision each require different types of attention. Productivity techniques designed for other work often fail because they do not account for this cognitive variety.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Separate research sessions from writing sessions — context-switching between them destroys both",
                "Estimate time for academic work in three stages: research, draft, polish",
                "Block your most cognitively demanding work for your peak focus hours",
                "Use time-boxing for research phases to prevent scope creep",
                "Build buffer time into every deadline estimate — academic work expands predictably",
            ]}},
            {"type": "heading", "value": {"text": "Separating Research and Writing Sessions", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most common time-management failure in academic writing is attempting to research and write simultaneously — searching for a source, writing a sentence, searching for another source, writing the next paragraph. This context-switching destroys concentration and makes both the research and the writing worse.</p><p>Research and writing are different cognitive tasks. Research is analytical and evaluative — you are assessing relevance and quality. Writing is generative and constructive — you are building an argument. Mixing them forces constant mental gear-changes that increase cognitive load and reduce quality in both activities.</p><p>A more effective approach: complete all primary research before writing begins. Build a source document with brief notes on how each source will be used. Then close your browser and write.</p>"},
            {"type": "heading", "value": {"text": "The Three-Stage Time Estimate", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Most writers underestimate time because they estimate for writing only, forgetting research and revision. A realistic estimate for a 1,500-word assignment with 10 sources looks like this: research and reading (2–3 hours), outline and first draft (2–3 hours), revision and reference check (1 hour). Total: 5–7 hours, not 2–3 hours of 'writing time'.</p><p>Build your workload capacity on realistic three-stage estimates, not optimistic draft-only estimates. The difference between the two is the most common source of overcommitment on academic writing platforms.</p>"},
            {"type": "heading", "value": {"text": "Time-Boxing Research to Prevent Scope Creep", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Academic research has no natural stopping point — there is always another source, another angle, another paper worth reading. Time-boxing sets a fixed boundary: allocate a specific time period for research and stop when it ends, not when you feel you have found everything.</p><p>A practical approach: allocate 45 minutes for initial database searches, 30 minutes for selecting and downloading relevant sources, and 60 minutes for reading and note-taking. When the allocated time for each phase is up, move to the next — even if your source list feels incomplete. You can flag gaps for a brief second research pass after the first draft if necessary.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "setting-up-a-home-writing-environment-for-productivity",
        "title": "Setting Up a Home Writing Environment That Supports Deep Work",
        "seo_title": "Home Writing Environment Setup | Academic Writer Workspace Guide | Writers Creek",
        "search_description": "Where you write affects how well you write. This practical guide covers the physical and digital environment choices that support focused, high-quality academic work over sustained periods.",
        "category_slug": "career-workflow",
        "tags": ["home office setup", "writer workspace", "deep work", "academic writing environment", "freelance setup"],
        "excerpt": "Academic writing requires sustained concentration — the kind of focus that is fragile to interruption and difficult to re-establish quickly. Your physical and digital environment either supports this state or constantly erodes it.",
        "reading_time": 6,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Dedicated physical space for writing creates a cognitive association that makes focus easier",
                "Notifications are the single largest destroyer of deep work — disable them during writing sessions",
                "A second monitor significantly reduces context-switching between sources and draft",
                "Background noise affects different writers differently — test white noise, music, and silence",
                "Your reference management tool is as important as your writing software",
            ]}},
            {"type": "heading", "value": {"text": "The Physical Environment", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most important physical principle is dedicated space. Working at the same desk, in the same chair, at the same time of day creates a conditioned association — your brain begins to associate that location with focused work, which makes entering a state of concentration faster and more reliable. Writers who work at the kitchen table, on the sofa, and in bed in rotation are constantly fighting this conditioning rather than benefiting from it.</p><p>If a dedicated room is not possible, a dedicated corner with consistent lighting and setup is sufficient. The goal is environmental consistency that signals 'this is writing time' as clearly as possible.</p>"},
            {"type": "heading", "value": {"text": "The Digital Environment", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Notifications are the most reliably productivity-destroying element of the digital environment. Every notification — email, message, social media alert — breaks concentration and requires time to re-establish focus. Research on attention restoration suggests it takes an average of 23 minutes to return to full concentration after an interruption. For academic writing, this is catastrophic at scale.</p><p>During writing sessions, disable all notifications. This includes email, platform messages, and social media. Set a specific time — at the end of each writing session — to check and respond to messages. Most clients understand that writers are not available for instant responses during working hours.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    # ── Assignment Types (4 new) ───────────────────────────────────────────────
    {
        "slug": "how-to-write-dissertation-chapters",
        "title": "How to Write the Main Dissertation Chapters: Literature Review, Methodology, Results",
        "seo_title": "Writing Dissertation Chapters | Literature Review, Methodology, Results | Writers Creek",
        "search_description": "Dissertation chapters have distinct conventions that differ from standard essay writing. This guide covers the structural and stylistic requirements for literature reviews, methodology chapters, and results sections.",
        "category_slug": "assignment-types",
        "tags": ["dissertation writing", "literature review", "methodology chapter", "results chapter", "academic writing"],
        "excerpt": "Each dissertation chapter performs a specific function. A literature review is not a summary of sources — it is a critical synthesis that identifies gaps. A methodology chapter is not a description of what you did — it is a justification of why you chose to do it that way.",
        "reading_time": 10,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "The literature review must identify a gap that justifies the research — it is not a summary",
                "Methodology chapters justify choices, not just describe procedures",
                "Results sections present findings objectively — analysis belongs in the discussion",
                "Each chapter must connect logically to the chapters before and after it",
                "Tense consistency matters: literature review uses present tense; methodology typically past tense",
            ]}},
            {"type": "heading", "value": {"text": "The Literature Review: Synthesis, Not Summary", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The most common mistake in dissertation literature reviews is treating them as annotated bibliographies — a series of summaries: 'Smith (2021) found that... Jones (2019) argued that... Brown (2020) suggested that...' This is not a literature review. It is a list.</p><p>A literature review synthesises — it identifies themes, contradictions, gaps, and trajectories in the existing literature. The goal is to arrive at a specific gap or question that your research addresses. The structure should be thematic rather than chronological: organise by concept or debate, not by the order in which papers were published.</p><p>End the literature review with a clear statement of what the existing research does not address and how your study will fill that gap. This is the direct justification for your research questions.</p>"},
            {"type": "heading", "value": {"text": "The Methodology Chapter: Justify, Don't Just Describe", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The methodology chapter tells the reader not only what was done but <em>why</em> those choices were made. A methodology that reads as a lab report — 'participants were recruited by... data were collected using... analysis was conducted with...' — is descriptively complete but analytically weak.</p><p>Every methodological choice should be defended by reference to the research questions and the alternatives that were considered. Why qualitative rather than quantitative? Why semi-structured interviews rather than surveys? Why thematic analysis rather than grounded theory? The justification for each choice, with reference to the methodological literature, is what distinguishes a good methodology chapter from a procedure list.</p>"},
            {"type": "heading", "value": {"text": "Results and Discussion: Keeping Them Separate", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Many dissertations blur the line between results and discussion, presenting findings already interpreted in the results section. Most dissertation formats require a clear separation: results present data objectively, discussion interprets it in relation to the literature and research questions.</p><p>In the results chapter, use precise language: 'the data show', 'participants reported', 'the analysis identified'. Save evaluative language — 'this suggests', 'these findings are consistent with', 'a possible explanation is' — for the discussion chapter. Keeping this distinction clean makes the dissertation easier to read and signals to the examiner that you understand the difference between observation and interpretation.</p>"},
            {"type": "cta", "value": {"text": "Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "writing-case-studies-and-professional-reports",
        "title": "Writing Case Studies and Professional Reports: A Practical Guide",
        "seo_title": "How to Write Case Studies and Reports | Academic Writing Guide | Writers Creek",
        "search_description": "Case studies and professional reports are common assignment types in business, healthcare, law, and social work. This guide covers structure, analysis method, and the key conventions for each.",
        "category_slug": "assignment-types",
        "tags": ["case study writing", "professional reports", "business writing", "healthcare case study", "report structure"],
        "excerpt": "Case studies and reports follow specific structural conventions that differ from standard essay format. Understanding these conventions — executive summary, SWOT, PESTLE, recommendations — allows writers to deliver exactly what the assignment requires.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Case studies require analysis of a specific situation — description alone is insufficient",
                "Professional reports use headings, numbered sections, and executive summaries",
                "SWOT and PESTLE analyses must be applied, not just defined",
                "Recommendations should be specific, justified, and practically actionable",
                "Formal reports use third-person passive voice; reflective case studies may use first person",
            ]}},
            {"type": "heading", "value": {"text": "Case Study Analysis: Beyond Description", "level": "h2"}},
            {"type": "paragraph", "value": "<p>A case study assignment asks you to analyse a specific real or hypothetical situation by applying theoretical frameworks to it. Describing what happened is a starting point, not a sufficient response. The analytical requirement — applying frameworks, identifying causes, evaluating decisions — is where the marks are.</p><p>Common frameworks applied in case study assignments include SWOT (strengths, weaknesses, opportunities, threats), PESTLE (political, economic, social, technological, legal, environmental), and stakeholder analysis. The key error is defining these frameworks rather than applying them. 'SWOT analysis examines strengths, weaknesses...' wastes words. 'The organisation's strengths include... which could be leveraged against...' is the application that earns marks.</p>"},
            {"type": "heading", "value": {"text": "Professional Report Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Professional reports follow a more rigid structure than essays. The standard format includes: title page, executive summary, table of contents, introduction, main body (with numbered sections and subheadings), conclusions, recommendations, and references. The executive summary is not an introduction — it is a standalone précis of the entire report, written last, that should make sense to a reader who reads nothing else.</p><p>Recommendations are the most frequently underdeveloped section. Vague recommendations — 'the organisation should improve its communication strategy' — are not recommendations, they are observations. Effective recommendations specify what should be done, by whom, by when, and with what resources: 'The marketing team should implement a quarterly review process for digital campaigns, beginning in Q1, using the existing analytics dashboard.'</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "writing-reflective-essays-and-journals",
        "title": "How to Write Reflective Essays and Reflective Journals in Academic Settings",
        "seo_title": "Writing Reflective Essays and Journals | Academic Reflection Guide | Writers Creek",
        "search_description": "Reflective writing is a distinct academic form that many writers find challenging precisely because it uses first person and personal experience while still requiring theoretical framework application. This guide covers Gibbs, Kolb, and Driscoll reflection models.",
        "category_slug": "assignment-types",
        "tags": ["reflective writing", "Gibbs reflective cycle", "academic reflection", "nursing reflection", "reflective journal"],
        "excerpt": "Reflective writing is not personal diary writing — it is structured self-analysis using theoretical frameworks. The challenge is applying academic rigour to personal experience without losing authenticity, and using first person confidently within a formal academic context.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "Reflective writing uses first person — this is expected and required, not informal",
                "Gibbs, Kolb, and Driscoll are the three most commonly required reflection frameworks",
                "The analysis stage is where marks are made — description is just the starting point",
                "Theory must be integrated — cite frameworks to support your reflective analysis",
                "Reflective writing concludes with an action plan, not a summary",
            ]}},
            {"type": "heading", "value": {"text": "Understanding the Three Reflection Frameworks", "level": "h2"}},
            {"type": "paragraph", "value": "<p><strong>Gibbs' Reflective Cycle</strong> (1988) is the most widely used framework in healthcare and education. It has six stages: Description (what happened), Feelings (what were you thinking and feeling), Evaluation (what was good and bad about the experience), Analysis (what sense can you make of the situation), Conclusion (what else could you have done), and Action Plan (if it happened again, what would you do). The analysis stage — drawing on theory to understand the experience — is where the academic work lies.</p><p><strong>Kolb's Experiential Learning Cycle</strong> has four stages: Concrete Experience, Reflective Observation, Abstract Conceptualisation (the theory stage), and Active Experimentation. It is commonly used in business and management contexts.</p><p><strong>Driscoll's 'What?' Model</strong> uses three prompts: What? (describe the event), So What? (analyse the significance), Now What? (plan future action). It is simpler than Gibbs and is often used for shorter reflective pieces or journals.</p>"},
            {"type": "heading", "value": {"text": "Using Theory Within Reflection", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The distinguishing feature of academic reflection is the integration of theoretical frameworks into the analysis stage. A description of feeling anxious during a clinical procedure becomes academically rigorous when it is analysed through, for example, the theory of emotional regulation or Benner's stages of clinical competence. The personal experience is the starting point; the theory is the analytical lens.</p><p>Citations in reflective writing follow the same rules as in essays: author, date, page number for direct quotations. The first-person voice and the academic citation system coexist without contradiction — 'I noticed that my initial response aligned with what Smith (2020) describes as...' is both personal and academically grounded.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
        ],
    },
    {
        "slug": "technical-writing-for-stem-assignments",
        "title": "Technical Writing for STEM Assignments: Lab Reports, Research Papers, and Proposals",
        "seo_title": "Technical Writing for STEM | Lab Reports, Research Papers | Writers Creek",
        "search_description": "STEM academic writing follows specific conventions that differ from humanities writing: passive voice, precise numerical reporting, methodology transparency, and strict structure. This guide covers the key conventions across lab reports, research papers, and project proposals.",
        "category_slug": "assignment-types",
        "tags": ["STEM writing", "lab report", "research proposal", "scientific writing", "technical writing"],
        "excerpt": "STEM writing is not difficult — but it is different. It prioritises precision, reproducibility, and objectivity over argument and rhetorical structure. Writers from humanities backgrounds often over-write STEM work; writers already experienced in STEM sometimes under-cite. Both errors cost marks.",
        "reading_time": 8,
        "body": [
            {"type": "key_takeaways", "value": {"items": [
                "STEM writing uses passive voice in methods sections — this is correct, not an error",
                "All numerical data must include units, significant figures, and uncertainty where applicable",
                "The IMRaD structure (Introduction, Methods, Results, Discussion) governs most STEM papers",
                "Figures and tables must be numbered, captioned, and explicitly referenced in the text",
                "STEM assignments often require IEEE or Vancouver citation — check the brief carefully",
            ]}},
            {"type": "heading", "value": {"text": "The IMRaD Structure", "level": "h2"}},
            {"type": "paragraph", "value": "<p>The vast majority of scientific and technical papers follow the IMRaD structure: Introduction, Methods, Results, and Discussion. Each section has a distinct function. The Introduction establishes context and the specific research question. The Methods section describes the procedure in enough detail for it to be reproduced. The Results section presents data without interpretation. The Discussion interprets the results, connects them to the existing literature, and addresses limitations.</p><p>One common error in STEM writing is allowing interpretive language into the Results section: 'surprisingly', 'interestingly', 'it appears that'. These belong in the Discussion. The Results section reports what was observed, not what it means.</p>"},
            {"type": "heading", "value": {"text": "Passive Voice in Methods: Why It Is Correct", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Writers with a strong humanities background often instinctively correct passive voice in scientific writing — replacing 'samples were incubated' with 'we incubated samples'. In STEM methods sections, the passive voice is correct and preferred. The scientific convention emphasises the procedure rather than the researchers performing it, reflecting the principle that results should be reproducible by any competent researcher following the same method.</p><p>Many institutions and journals are moving towards first-person active voice in STEM writing as a readability improvement. Check the assignment requirements or journal style guide before defaulting to either convention.</p>"},
            {"type": "heading", "value": {"text": "Reporting Data: Precision and Units", "level": "h2"}},
            {"type": "paragraph", "value": "<p>Numerical data in STEM writing must be presented precisely: all values should include appropriate units (g, mL, °C, Hz), a consistent number of significant figures, and — where applicable — a measure of uncertainty or variance (mean ± standard deviation). Writing '25 degrees' instead of '25 °C ± 0.5 °C' is an error that signals lack of scientific rigour.</p><p>Figures and tables must each carry a number and a descriptive caption, and they must be explicitly referenced in the text before they appear: 'as shown in Figure 2...' or 'Table 3 summarises the results of...'. A figure that appears in a document without being referenced in the text is effectively invisible to the marker.</p>"},
            {"type": "cta", "value": {"text": "Apply to Join Writers Creek", "url": "/apply"}},
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
