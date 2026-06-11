"""
Management command: seed_gradecrest_services
=============================================

Seeds GradeCrest service pages into Wagtail from the hardcoded SERVICE_MAP
that lives in gradecrest-web/pages/services/[slug].vue.

Idempotent — skips pages whose slug already exists under the ServiceIndexPage.

Usage:
    python manage.py seed_gradecrest_services
    python manage.py seed_gradecrest_services --site gradecrest.com
    python manage.py seed_gradecrest_services --update   # overwrite existing
"""

from django.core.management.base import BaseCommand, CommandParser

# Full SERVICE_MAP mirrored from gradecrest-web/pages/services/[slug].vue
# Each entry becomes one live ServicePage in Wagtail.
SERVICE_DATA = [
    {
        "slug": "essay-writing",
        "title": "Essay Writing Service",
        "template_key": "essay_service",
        "search_description": "Get a custom essay written by a human expert from $13/page. Argumentative, analytical, descriptive essays. Grade or money back. Zero AI content.",
        "seo_title": "Essay Writing Service from $13/Page | GradeCrest",
        "hero_headline": "Essay Writing Service",
        "hero_sub": "Any type. Any subject. Any level.",
        "pricing_from": "13.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Whether you need a 500-word argumentative essay or a 5,000-word analytical piece, GradeCrest connects you with a subject-specialist writer who understands your assignment and your institution's expectations.",
        "includes_items": [
            "All essay types: argumentative, analytical, descriptive, reflective, compare-and-contrast",
            "Matched to your exact subject — over 100 disciplines covered",
            "Correct referencing style (APA, MLA, Chicago, Harvard, Turabian)",
            "Full plagiarism report included at no extra cost",
            "AI-detection certificate included on request",
            "Unlimited revisions within the revision window",
        ],
        "delivers_items": [
            "Custom essay written from scratch by a subject specialist",
            "Plagiarism report",
            "AI-detection certificate (on request)",
            "Formatted reference list",
        ],
        "faqs": [
            {"q": "Can you write essays on any topic?", "a": "Yes. We cover 100+ academic subjects from nursing to philosophy to engineering. If you can name the topic, we have a writer for it."},
            {"q": "Will my essay be plagiarism-free?", "a": "Every essay is written from scratch and checked against plagiarism databases. Your report is included free of charge."},
            {"q": "Will my essay contain AI content?", "a": "No. Every essay is written by a verified human expert. We offer a free AI-detection certificate on request."},
            {"q": "What if I need changes?", "a": "Unlimited free revisions within 14 days of delivery. If we still cannot meet your requirements, you receive a full refund."},
        ],
    },
    {
        "slug": "research-papers",
        "title": "Research Paper Writing Service",
        "template_key": "standard_service",
        "search_description": "Custom research papers written by human experts. Full methodology, proper citations, plagiarism-free. From $15/page. Grade or money back.",
        "seo_title": "Research Paper Writing Service from $15/Page | GradeCrest",
        "hero_headline": "Research Paper Writing Service",
        "hero_sub": "Original. Citation-rich. Properly structured.",
        "pricing_from": "15.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A well-structured research paper requires more than writing ability — it demands domain knowledge, sound methodology, and mastery of academic conventions. GradeCrest writers hold postgraduate degrees in your subject and have produced research at the level your assignment demands.",
        "includes_items": [
            "Original research papers written from scratch by subject specialists",
            "Correct citation format: APA, MLA, Chicago, Harvard, Vancouver",
            "Full methodology section with justified research design",
            "Literature review integrated into the paper",
            "Statistical analysis support (SPSS, R, Python) where required",
            "Full plagiarism and AI-detection reports included",
        ],
        "delivers_items": [
            "Custom research paper written from scratch",
            "Full methodology and literature review",
            "Plagiarism report",
            "Formatted reference list",
        ],
        "faqs": [
            {"q": "Can you write a research paper in my subject?", "a": "Yes. We cover STEM, humanities, business, social sciences, health sciences, law, and 100+ other disciplines."},
            {"q": "Do you provide sources and citations?", "a": "Yes. Your writer will source appropriate peer-reviewed references and cite them correctly in your chosen style."},
            {"q": "Can I see a draft before final delivery?", "a": "Yes. You can request a progress update or partial draft from your writer at any time."},
            {"q": "What if the paper does not meet my grade?", "a": "We rewrite it free of charge. If still unsatisfied after revision, you receive a full refund."},
        ],
    },
    {
        "slug": "dissertations",
        "title": "Dissertation & Thesis Writing Service",
        "template_key": "standard_service",
        "search_description": "Expert dissertation support from proposal to final chapter. Master's and PhD level. Methodology, data analysis, literature review, discussion. Grade guaranteed.",
        "seo_title": "Dissertation Writing Service | Full Thesis Support | GradeCrest",
        "hero_headline": "Dissertation & Thesis Writing Service",
        "hero_sub": "Full support from proposal to final submission.",
        "pricing_from": "22.00",
        "turnaround_hours_fastest": 24,
        "turnaround_hours_standard": 720,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A dissertation is the most significant piece of academic writing most students ever produce. GradeCrest assigns PhD-qualified experts who have completed dissertations at the same level you're working at — so they understand the depth, rigour, and structure your committee expects.",
        "includes_items": [
            "Full dissertation support or individual chapters",
            "Proposal, literature review, methodology, findings, discussion, conclusion",
            "Quantitative, qualitative, and mixed-methods expertise",
            "Statistical analysis (SPSS, R, NVivo, Python)",
            "APA, Harvard, Chicago, Vancouver formatting",
            "Plagiarism report and AI certificate included",
            "Up to 30-day revision window for dissertations",
        ],
        "delivers_items": [
            "Complete dissertation or individual chapters",
            "All analysis files and outputs",
            "Plagiarism report",
            "AI-detection certificate",
        ],
        "faqs": [
            {"q": "Can you help with just one chapter?", "a": "Yes. You can order a single chapter, section, or the full dissertation — your choice."},
            {"q": "How do I ensure the writer knows my field?", "a": "We match by discipline, methodology, and academic level. You can also review your writer's profile and message them before work begins."},
            {"q": "Will the methodology be original?", "a": "Yes. Your writer designs a methodology appropriate to your research question, not a recycled template."},
            {"q": "What is the revision period for dissertations?", "a": "Up to 30 days from delivery. We revise until the work meets your specifications."},
        ],
    },
    {
        "slug": "nursing-essays",
        "title": "Nursing Essay Writing Service",
        "template_key": "healthcare_service",
        "search_description": "Nursing essays, SOAP notes, care plans, and EBP papers written by registered nurses. From $15/page. NMC, ANA, APA compliant. Grade or money back.",
        "seo_title": "Nursing Essay Writing Service | SOAP Notes, Care Plans | GradeCrest",
        "hero_headline": "Nursing Essay Writing Service",
        "hero_sub": "Written by registered nursing professionals.",
        "pricing_from": "15.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Nursing assignments demand clinical knowledge that generalist writers simply do not have. Our nursing writers are registered nurses and nursing academics — they understand patient care frameworks, clinical terminology, evidence-based practice, and the expectations of nursing faculties.",
        "includes_items": [
            "SOAP notes, DAR notes, and clinical documentation",
            "Care plans with nursing diagnoses and interventions",
            "Evidence-based practice (EBP) and PICO papers",
            "Pharmacology assignments and drug calculations",
            "Case studies with clinical reasoning frameworks",
            "NMC, ANA, NANDA-aligned content",
            "APA 7th edition formatting as standard",
        ],
        "delivers_items": [
            "Nursing essay, care plan, or clinical document written by a registered nurse",
            "Plagiarism report",
            "APA 7th edition formatting",
        ],
        "faqs": [
            {"q": "Are your nursing writers actually nurses?", "a": "Yes. Our nursing writers hold nursing degrees and most have active clinical experience. Credentials are verified before assignment."},
            {"q": "Can you write SOAP notes?", "a": "Yes — SOAP, DAR, SBAR, and other clinical documentation formats."},
            {"q": "Do you cover BSN, MSN, and DNP levels?", "a": "Yes. From undergraduate BSN through doctoral DNP and PhD nursing programmes."},
            {"q": "Will the content be evidence-based?", "a": "Yes. All claims are supported by current peer-reviewed sources and referenced in APA 7th edition."},
        ],
    },
    {
        "slug": "editing-proofreading",
        "title": "Editing & Proofreading Service",
        "template_key": "editing_service",
        "search_description": "Professional academic editing and proofreading from $8/page. Grammar, structure, flow, citations, and formatting. Returned within your deadline.",
        "seo_title": "Academic Editing & Proofreading Service | GradeCrest",
        "hero_headline": "Editing & Proofreading Service",
        "hero_sub": "Professional academic editing by expert editors.",
        "pricing_from": "8.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 120,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Even excellent research can be let down by unclear writing, grammatical errors, or inconsistent formatting. Our editors are academic writing specialists — they improve your work without changing your ideas or voice.",
        "includes_items": [
            "Grammar, spelling, punctuation, and syntax correction",
            "Sentence clarity, flow, and paragraph structure",
            "Academic tone and register consistency",
            "Citation checking and reference list formatting",
            "Formatting to APA, MLA, Chicago, Harvard, or your institution's style guide",
            "Track-changes version provided so you can see every edit",
        ],
        "delivers_items": [
            "Edited document with tracked changes",
            "Clean final copy",
            "Citation and reference list corrections",
        ],
        "faqs": [
            {"q": "Will my ideas and arguments be changed?", "a": "No. Editing improves how your ideas are expressed — it never changes what you are arguing."},
            {"q": "Do you check citations and references?", "a": "Yes. We verify citation format consistency and reference list accuracy in your chosen style."},
            {"q": "How fast can you edit a document?", "a": "Standard turnaround is 3–5 days. Rush editing from 24 hours is available at a surcharge."},
            {"q": "What file formats do you accept?", "a": "DOCX, DOC, PDF, RTF, and Google Docs (shared link). DOCX is preferred for track changes."},
        ],
    },
    {
        "slug": "admission-essays",
        "title": "Admission Essay Writing Service",
        "template_key": "admissions_service",
        "search_description": "Expert admission essay and personal statement writing. College, university, and graduate school applications. Stand out with a compelling, authentic narrative.",
        "seo_title": "Admission Essay Writing Service | Personal Statement Help | GradeCrest",
        "hero_headline": "Admission Essay Writing Service",
        "hero_sub": "Stand out from thousands of applicants.",
        "pricing_from": "15.00",
        "turnaround_hours_fastest": 12,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Admission committees read thousands of essays. A great personal statement is specific, authentic, and shows — not tells — who you are and why you belong at that institution. Our admissions writers have worked at top universities and know exactly what makes an application stand out.",
        "includes_items": [
            "College and university personal statements",
            "Graduate school and MBA admissions essays",
            "Medical, law, and nursing school applications",
            "Scholarship essays and grant applications",
            "Statement of purpose (SOP)",
            "Letter of intent (LOI)",
            "Completely original — built around your story and achievements",
        ],
        "delivers_items": [
            "Custom admission essay built around your story",
            "Multiple revision rounds",
            "Plagiarism-free guarantee",
        ],
        "faqs": [
            {"q": "Will the essay sound like me?", "a": "Yes. We build the essay around your experiences and voice. You provide the story; we craft the narrative."},
            {"q": "Can you help with multiple applications?", "a": "Yes. We can write multiple versions tailored to different institutions."},
            {"q": "Do you handle graduate school SOPs?", "a": "Yes — statement of purpose, personal statement, letter of intent, and research proposals."},
            {"q": "Is the essay plagiarism-free?", "a": "Every essay is written from scratch and is unique to you. It is never resold or reused."},
        ],
    },
    {
        "slug": "term-papers",
        "title": "Term Paper Writing Service",
        "template_key": "standard_service",
        "search_description": "Custom term papers written by human experts. Well-structured arguments, full citations, on-time delivery. From $14/page. Grade or money back.",
        "seo_title": "Term Paper Writing Service from $14/Page | GradeCrest",
        "hero_headline": "Term Paper Writing Service",
        "hero_sub": "Well-argued semester papers, delivered on time.",
        "pricing_from": "14.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A term paper is a substantial piece of writing that contributes to your module grade — it needs a clear thesis, well-organised arguments, and proper academic sourcing. GradeCrest writers hold postgraduate degrees in your subject and know exactly what your faculty expects.",
        "includes_items": [
            "Original term papers written from scratch by subject specialists",
            "Clear thesis with structured argumentation throughout",
            "Peer-reviewed sources researched and cited correctly",
            "APA, MLA, Chicago, Harvard, or any other citation style",
            "Full plagiarism report included at no extra cost",
            "Unlimited free revisions within the revision window",
        ],
        "delivers_items": [
            "Custom term paper written from scratch",
            "Plagiarism report",
            "Formatted reference list",
        ],
        "faqs": [
            {"q": "Can you write a term paper on any subject?", "a": "Yes. We cover 100+ academic subjects from STEM to humanities, business, and social sciences."},
            {"q": "Will you follow my professor's instructions?", "a": "Yes. Share your rubric, marking criteria, or any specific requirements and your writer will follow them precisely."},
            {"q": "Will the paper be plagiarism-free?", "a": "Every paper is written from scratch and comes with a plagiarism report at no extra charge."},
            {"q": "What if the grade requirement is not met?", "a": "We rewrite it free of charge. If still unsatisfied after revision, you receive a full refund."},
        ],
    },
    {
        "slug": "case-studies",
        "title": "Case Study Writing Service",
        "template_key": "standard_service",
        "search_description": "Expert case study writing for business, law, nursing, and any subject. In-depth analysis, structured arguments, plagiarism-free. From $15/page.",
        "seo_title": "Case Study Writing Service from $15/Page | GradeCrest",
        "hero_headline": "Case Study Writing Service",
        "hero_sub": "In-depth analysis with evidence-backed conclusions.",
        "pricing_from": "15.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A strong case study requires more than summarising facts — it demands analytical depth, a clear framework, and the ability to draw credible conclusions from evidence. GradeCrest writers hold postgraduate qualifications and have hands-on experience with case analysis in their fields.",
        "includes_items": [
            "Business, law, nursing, psychology, and social science case studies",
            "Analysis structured around recognised academic frameworks",
            "Evidence-based conclusions with cited supporting sources",
            "SWOT, PESTLE, Porter's Five Forces, and other models applied correctly",
            "APA, Harvard, Chicago, MLA formatting",
            "Plagiarism report included at no extra cost",
        ],
        "delivers_items": [
            "Custom case study written from scratch",
            "Framework-based analysis",
            "Plagiarism report",
        ],
        "faqs": [
            {"q": "Can you write business and law case studies?", "a": "Yes. We cover business, law, nursing, psychology, social science, and any other discipline."},
            {"q": "Will you apply a specific framework?", "a": "Yes — SWOT, PESTLE, Porter's Five Forces, legal case analysis, clinical frameworks, and others. Specify in your instructions."},
            {"q": "Can I include specific source requirements?", "a": "Yes. Add required readings, textbooks, or databases to your instructions and your writer will incorporate them."},
            {"q": "What if I need revisions?", "a": "Unlimited free revisions within 14 days of delivery. Full refund if requirements are not met."},
        ],
    },
    {
        "slug": "coursework",
        "title": "Coursework Help",
        "template_key": "online_class_service",
        "search_description": "Expert coursework help for any module or subject. Dedicated writer, consistent quality across every assignment. From $14/page. Grade or money back.",
        "seo_title": "Coursework Help from $14/Page | Ongoing Assignment Support | GradeCrest",
        "hero_headline": "Coursework Help",
        "hero_sub": "Consistent support throughout your module.",
        "pricing_from": "14.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Coursework spans an entire module — and inconsistent support from different writers shows. GradeCrest lets you work with the same writer throughout your course, building familiarity with your subject, your voice, and your institution's expectations over time.",
        "includes_items": [
            "Same writer for every assignment across your module",
            "Consistent academic voice and argument style throughout",
            "Covers essays, reports, reflections, presentations, and more",
            "Any subject, undergraduate through postgraduate",
            "All citation styles formatted correctly",
            "Plagiarism report on every submission",
        ],
        "delivers_items": [
            "Each assignment written from scratch",
            "Plagiarism report per submission",
            "Consistent writer across the module",
        ],
        "faqs": [
            {"q": "Can I keep the same writer for my whole course?", "a": "Yes. We strongly recommend this for coursework — request your writer by name when placing each new order."},
            {"q": "What types of coursework do you cover?", "a": "Essays, reports, reflective journals, lab reports, portfolios, presentations, and more."},
            {"q": "What if I have feedback from my tutor to incorporate?", "a": "Share tutor feedback with your writer before the next assignment and they will adjust their approach accordingly."},
            {"q": "Is the work plagiarism-free?", "a": "Yes. Every assignment is written from scratch with a full plagiarism report included."},
        ],
    },
    {
        "slug": "literature-review",
        "title": "Literature Review Writing Service",
        "template_key": "standard_service",
        "search_description": "Expert literature reviews written by human academics. Critically synthesised, thematically structured, fully cited. From $16/page. Grade or money back.",
        "seo_title": "Literature Review Writing Service from $16/Page | GradeCrest",
        "hero_headline": "Literature Review Writing Service",
        "hero_sub": "Comprehensive, critically synthesised scholarly reviews.",
        "pricing_from": "16.00",
        "turnaround_hours_fastest": 12,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A literature review is not a summary — it is a critical synthesis of the field, identifying themes, debates, gaps, and methodological trends. Our writers hold postgraduate degrees and have conducted original research, giving them the depth to produce literature reviews that meet doctoral-level expectations.",
        "includes_items": [
            "Systematic, narrative, and integrative review formats",
            "Critical synthesis — not just description — of source material",
            "Thematic structure developed around your research question",
            "Appropriate primary and secondary sources identified and included",
            "PRISMA-compliant systematic reviews upon request",
            "APA, Harvard, Chicago, Vancouver, and all major citation styles",
            "Plagiarism report included at no extra cost",
        ],
        "delivers_items": [
            "Critically synthesised literature review",
            "Thematic structure and gap analysis",
            "Plagiarism report",
            "Formatted reference list",
        ],
        "faqs": [
            {"q": "Can you conduct the source search for me?", "a": "Yes. Your writer identifies appropriate sources from databases such as PubMed, JSTOR, Scopus, and Google Scholar."},
            {"q": "Can I supply my own list of sources?", "a": "Yes. Add any required sources in your instructions and your writer will incorporate and synthesise them."},
            {"q": "Do you write PRISMA-compliant reviews?", "a": "Yes. Specify systematic review and PRISMA framework in your instructions."},
            {"q": "What if I need a literature review as part of a larger dissertation?", "a": "Absolutely. We can write individual chapters or the full dissertation — your choice."},
        ],
    },
    {
        "slug": "thesis-writing",
        "title": "Thesis Writing Service",
        "template_key": "standard_service",
        "search_description": "Expert thesis writing support at Master's and PhD level. Proposal through submission. Methodology, data, discussion. Grade guaranteed.",
        "seo_title": "Thesis Writing Service | Master's & PhD Thesis Help | GradeCrest",
        "hero_headline": "Thesis Writing Service",
        "hero_sub": "Graduate-level thesis support from proposal to submission.",
        "pricing_from": "22.00",
        "turnaround_hours_fastest": 24,
        "turnaround_hours_standard": 720,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "A thesis is the most rigorous piece of academic writing in your programme. It requires original argumentation, sound methodology, and mastery of your discipline's scholarly conventions. GradeCrest assigns writers who hold the same qualification you're working towards — so they understand the standard from the inside.",
        "includes_items": [
            "Full thesis support or individual chapters — Master's and PhD",
            "Research proposal and research question development",
            "Literature review, theoretical framework, and methodology",
            "Data collection planning and analysis (SPSS, R, NVivo, Python)",
            "Findings, discussion, and conclusion chapters",
            "Abstract, acknowledgements, and reference list",
            "Up to 30-day revision window",
        ],
        "delivers_items": [
            "Complete thesis or individual chapters",
            "All analysis files",
            "Plagiarism report",
            "AI-detection certificate",
        ],
        "faqs": [
            {"q": "Can you help with just the methodology chapter?", "a": "Yes. You can order any individual chapter, section, or the full thesis."},
            {"q": "How do you ensure the writer knows my field?", "a": "We match by discipline, methodology type, and academic level. You can review your writer's credentials before work begins."},
            {"q": "Will my supervisor see something generic?", "a": "No. Every thesis is built around your specific research question, theoretical framework, and existing literature."},
            {"q": "What is the revision period for a thesis?", "a": "Up to 30 days from delivery. We revise until the work meets your specifications."},
        ],
    },
    {
        "slug": "data-analysis",
        "title": "Data Analysis Service",
        "template_key": "technical_service",
        "search_description": "Academic data analysis by expert statisticians. SPSS, R, Python, Excel, NVivo. Quantitative and qualitative analysis with written interpretation. Grade guaranteed.",
        "seo_title": "Data Analysis Service for Academic Research | SPSS, R, Python | GradeCrest",
        "hero_headline": "Data Analysis Service",
        "hero_sub": "SPSS, R, Python, and Excel — results and written interpretation.",
        "pricing_from": "20.00",
        "turnaround_hours_fastest": 12,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Data analysis is the most technically demanding part of academic research — and errors in your methodology or interpretation can undermine an otherwise strong dissertation. Our analysts hold postgraduate degrees in statistics, research methods, or your specific subject, and work with the exact software your programme requires.",
        "includes_items": [
            "Quantitative: descriptive stats, regression, ANOVA, t-tests, chi-square, factor analysis",
            "Qualitative: thematic analysis, discourse analysis, content analysis (NVivo)",
            "Mixed-methods research designs",
            "SPSS, R, Python (pandas/scipy), Stata, and Excel",
            "Written interpretation of results in academic language",
            "Charts, tables, and figures formatted to your style guide",
            "Methodology section and results chapter written if required",
        ],
        "delivers_items": [
            "Statistical analysis output files",
            "Written interpretation of results",
            "Charts and tables formatted to your style guide",
        ],
        "faqs": [
            {"q": "Can you analyse my existing dataset?", "a": "Yes. Share your dataset (Excel, CSV, SPSS .sav, etc.) along with your research questions and methodology."},
            {"q": "Do you provide the SPSS/R output files?", "a": "Yes. You receive both the raw output files and a clean written interpretation of the results."},
            {"q": "Can you help if I don't know which test to use?", "a": "Yes. Our analysts can recommend the appropriate statistical tests based on your research design and data type."},
            {"q": "Do you cover qualitative methods?", "a": "Yes — thematic analysis, content analysis, grounded theory coding, and NVivo-supported analysis."},
        ],
    },
    {
        "slug": "online-class-help",
        "title": "Online Class Help",
        "template_key": "online_class_service",
        "search_description": "Expert help with online course assignments. Essays, discussion posts, quizzes, and coursework completed by verified subject specialists. From $14/page.",
        "seo_title": "Online Class Help | Assignment Support for Online Courses | GradeCrest",
        "hero_headline": "Online Class Help",
        "hero_sub": "Consistent assignment completion throughout your online course.",
        "pricing_from": "14.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Fully online courses demand the same academic rigour as campus programmes — but without the in-person support structure. GradeCrest provides consistent, subject-expert help across your entire online module, so every submission reflects the quality your grade requires.",
        "includes_items": [
            "Essays, reports, and written assignments",
            "Discussion board posts and response threads",
            "Quiz and short-answer question support",
            "Weekly and module-long coursework",
            "Any LMS platform — Canvas, Blackboard, Moodle",
            "Any subject, any level, undergraduate through postgraduate",
            "Plagiarism report included on written work",
        ],
        "delivers_items": [
            "Each assignment completed before the due date",
            "Plagiarism report on written work",
            "Discussion posts and responses",
        ],
        "faqs": [
            {"q": "Can you help with my entire online course?", "a": "Yes. We can provide ongoing support throughout your module for every type of assignment."},
            {"q": "Do you cover discussion board posts?", "a": "Yes — initial discussion posts and response posts to peers."},
            {"q": "What subjects do you cover?", "a": "All subjects offered in online programmes — nursing, business, education, IT, social sciences, psychology, and more."},
            {"q": "Is the work plagiarism-free?", "a": "Yes. Every written submission is original and comes with a plagiarism report."},
        ],
    },
    {
        "slug": "homework-help",
        "title": "Homework Help",
        "template_key": "standard_service",
        "search_description": "Expert homework help for any subject, any level. Same-day support available. Human-written, plagiarism-free. From $13/page. Grade or money back.",
        "seo_title": "Homework Help from $13/Page | Any Subject, Any Level | GradeCrest",
        "hero_headline": "Homework Help",
        "hero_sub": "Day-to-day assignment support across any subject.",
        "pricing_from": "13.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "who_for": "Whether it is a single assignment due tomorrow or a weekly flow of tasks across a difficult module, GradeCrest connects you with a subject specialist who can handle the work to the standard your course demands.",
        "includes_items": [
            "Any assignment type: essays, reports, problems, short answers, reflections",
            "Any subject: STEM, humanities, business, nursing, law, and more",
            "Any level: high school, undergraduate, and postgraduate",
            "Same-day and 6-hour rush turnaround available",
            "Correct citation style and formatting included",
            "Plagiarism report on every written submission",
        ],
        "delivers_items": [
            "Completed assignment written from scratch",
            "Plagiarism report",
            "Correct citation formatting",
        ],
        "faqs": [
            {"q": "How fast can you complete homework?", "a": "We offer turnarounds from 6 hours for short assignments. Complexity and length affect the minimum deadline."},
            {"q": "Can you help with maths and STEM assignments?", "a": "Yes. We have specialists in mathematics, physics, chemistry, engineering, statistics, and computer science."},
            {"q": "What if I only need help understanding, not a full answer?", "a": "We can provide worked examples, explanations, or model answers — whatever is most useful for your situation."},
            {"q": "Is the work original?", "a": "Yes. Every answer is written specifically for your assignment and never reused."},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed GradeCrest service pages into Wagtail from the hardcoded SERVICE_MAP"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--site",
            default="gradecrest.com",
            help="Hostname of the target Wagtail site (default: gradecrest.com)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing pages instead of skipping them",
        )

    def handle(self, *args, **options):
        from decimal import Decimal
        from wagtail.models import Site
        from wagtail.blocks import StreamValue
        from cms_service_pages.models import ServiceIndexPage, ServicePage

        hostname = options["site"]
        do_update = options["update"]

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"No Wagtail site found for hostname '{hostname}'. Run setup_tenants first."))
            return

        try:
            svc_index = ServiceIndexPage.objects.child_of(site.root_page).get()
        except ServiceIndexPage.DoesNotExist:
            self.stderr.write(self.style.ERROR("No ServiceIndexPage found under this site's root. Run setup_tenants first."))
            return

        self.stdout.write(f"Seeding into: {hostname} → ServiceIndexPage id={svc_index.id}")

        existing_slugs = set(
            ServicePage.objects.child_of(svc_index).values_list("slug", flat=True)
        )

        created = updated = skipped = 0

        for svc in SERVICE_DATA:
            slug = svc["slug"]

            if slug in existing_slugs:
                if not do_update:
                    self.stdout.write(f"  SKIP  {slug}")
                    skipped += 1
                    continue

                page = ServicePage.objects.child_of(svc_index).get(slug=slug)
                self._apply_fields(page, svc)
                page.save_revision().publish()
                self.stdout.write(self.style.WARNING(f"  UPDATE {slug}"))
                updated += 1
            else:
                page = ServicePage(
                    title=svc["title"],
                    slug=slug,
                    live=True,
                )
                self._apply_fields(page, svc)
                svc_index.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  CREATE {slug}"))
                created += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {updated} updated, {skipped} skipped"
        ))

    def _apply_fields(self, page: "ServicePage", svc: dict):
        from decimal import Decimal
        from wagtail.rich_text import RichText

        page.title = svc["title"]
        page.template_key = svc.get("template_key", "standard_service")
        page.seo_title = svc.get("seo_title", "")
        page.search_description = svc.get("search_description", "")
        page.hero_headline = svc.get("hero_headline", "")
        page.hero_sub = svc.get("hero_sub", "")
        page.who_for = svc.get("who_for", "")
        page.primary_cta_text = svc.get("primary_cta_text", "Order Now")
        page.primary_cta_url = svc.get("primary_cta_url", "/order/")
        page.show_aggregate_rating = True

        if svc.get("pricing_from"):
            page.pricing_from = Decimal(svc["pricing_from"])
        if svc.get("turnaround_hours_fastest"):
            page.turnaround_hours_fastest = svc["turnaround_hours_fastest"]
        if svc.get("turnaround_hours_standard"):
            page.turnaround_hours_standard = svc["turnaround_hours_standard"]

        # includes_items StreamField — each item is a CharBlock named "item"
        page.includes_items = [
            {"type": "item", "value": item}
            for item in svc.get("includes_items", [])
        ]

        # delivers_items StreamField
        page.delivers_items = [
            {"type": "item", "value": item}
            for item in svc.get("delivers_items", [])
        ]

        # body — inject FAQs as faq blocks
        body_blocks = []
        for faq in svc.get("faqs", []):
            body_blocks.append({
                "type": "faq",
                "value": {
                    "question": faq["q"],
                    "answer": f"<p>{faq['a']}</p>",
                },
            })
        page.body = body_blocks
