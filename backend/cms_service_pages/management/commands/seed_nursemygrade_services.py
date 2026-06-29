"""
Management command: seed_nursemygrade_services
==============================================

Seeds all 22 NurseMyGrade service pages into Wagtail from the data
defined in nursemygrade-web/composables/useServices.ts.

Idempotent — skips pages whose slug already exists under the
ServiceIndexPage unless --update is passed.

Usage:
    python manage.py seed_nursemygrade_services
    python manage.py seed_nursemygrade_services --site nursemygrade.com
    python manage.py seed_nursemygrade_services --update
"""

from django.core.management.base import BaseCommand, CommandParser

SERVICE_DATA = [
    {
        "slug": "online-nursing-essays-help",
        "title": "Nursing Essay Writing Service",
        "seo_title": "Nursing Essay Writing Service — BSN, MSN & DNP Writers",
        "search_description": "Custom nursing essays written by qualified nurses. APA 7th, EBP-grounded, plagiarism-free. From $24/page.",
        "hero_headline": "Nursing Essays Written by BSN, MSN & DNP Experts",
        "hero_sub": "Reflective, argumentative, and analytical nursing essays grounded in evidence-based practice — APA 7th edition, plagiarism-free, any level.",
        "who_for": "Nursing students at ADN, BSN, MSN, and DNP level who need a well-argued, clinically grounded essay on any nursing topic.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Written by nurses with BSN, MSN, or DNP credentials",
            "Evidence-based practice (EBP) framework applied",
            "APA 7th edition formatting included",
            "Free Turnitin plagiarism report",
            "Unlimited revisions within review window",
        ],
        "delivers_items": [
            "Strong clinical argument with PICO or NURS framework where relevant",
            "Current peer-reviewed nursing journals cited",
            "Introduction, body, conclusion, and references page",
            "Formatted to your institution's style guide",
        ],
        "faqs": [
            {"q": "Who writes my nursing essay?", "a": "All NurseMyGrade writers hold at minimum a BSN with active or recent clinical experience. Many hold MSN or DNP credentials."},
            {"q": "What nursing essay types do you cover?", "a": "Reflective, argumentative, analytical, descriptive, SOAP-format narrative essays, and any other type required by your programme."},
            {"q": "Will my essay be APA 7th edition?", "a": "Yes — in-text citations, reference lists, headings, and page formatting all follow APA 7th edition unless you specify otherwise."},
            {"q": "What if I need changes after delivery?", "a": "Unlimited free revisions within the revision window. If we still cannot meet your requirements, you receive a full refund."},
        ],
    },
    {
        "slug": "nursing-care-plan-writing-services",
        "title": "Nursing Care Plan Writing Service",
        "seo_title": "Nursing Care Plan Writing Service — NANDA, NIC & NOC",
        "search_description": "Expert nursing care plan writing using NANDA diagnoses, NIC interventions, and NOC outcomes. Clinically accurate. From $26/page.",
        "hero_headline": "Nursing Care Plans Built on NANDA, NIC & NOC",
        "hero_sub": "Clinically accurate care plans with complete nursing diagnoses, patient goals, and evidence-based interventions — formatted to your programme's standards.",
        "who_for": "BSN and ADN students who need a properly formatted, clinically sound care plan for clinical practicum, simulation labs, or academic submissions.",
        "pricing_from": "26.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "NANDA-I approved nursing diagnoses",
            "NIC nursing interventions with rationale",
            "NOC measurable patient outcomes",
            "Assessment, planning, implementation, evaluation (APIE) format",
            "Free revisions",
        ],
        "delivers_items": [
            "Complete care plan for one or multiple nursing diagnoses",
            "Short- and long-term goal statements",
            "Evidence-based nursing interventions with cited rationale",
            "Evaluation criteria and expected outcomes",
        ],
        "faqs": [
            {"q": "Which nursing diagnosis framework do you use?", "a": "NANDA-I approved diagnoses as standard. We also support facility-specific formats and alternative diagnostic taxonomies on request."},
            {"q": "Can you complete a care plan for a specific patient scenario?", "a": "Yes. Share your patient case details (diagnosis, vitals, history) and your writer will build the care plan around that specific clinical picture."},
            {"q": "Do you cover ADPIE format?", "a": "Yes — Assessment, Diagnosis, Planning, Implementation, and Evaluation are all structured within the care plan."},
            {"q": "How quickly can you deliver a care plan?", "a": "Most care plans are delivered within 24 hours. Rush delivery from 3 hours is available."},
        ],
    },
    {
        "slug": "nursing-soap-note-writing-help",
        "title": "SOAP Note Writing Service",
        "seo_title": "SOAP Note Writing Service — Clinical Documentation Help",
        "search_description": "Accurate SOAP notes written by clinical nursing professionals. All four sections, ICD-10 aware. From $28/page.",
        "hero_headline": "SOAP Notes That Meet Clinical Documentation Standards",
        "hero_sub": "Subjective, Objective, Assessment, and Plan sections written by practicing nursing professionals — accurate, concise, and ready for clinical review.",
        "who_for": "NP students, FNP programmes, and advanced practice nursing students who need clinically accurate SOAP notes for coursework or simulation scenarios.",
        "pricing_from": "28.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 96,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "All four SOAP sections: S, O, A, P",
            "Written by clinically experienced nursing writers",
            "ICD-10 coding awareness where applicable",
            "Chief complaint, HPI, ROS, and physical exam sections",
            "Free revisions",
        ],
        "delivers_items": [
            "Complete SOAP note to your patient scenario",
            "Clinically accurate assessment and differential considerations",
            "Evidence-based plan with medication, referral, and follow-up notes",
            "Formatted to your course or clinical site requirements",
        ],
        "faqs": [
            {"q": "Can you write SOAP notes for NP programme cases?", "a": "Yes — our writers include practicing FNPs and NPs who write SOAP documentation daily in clinical settings."},
            {"q": "Do you include the full HPI and ROS?", "a": "Yes. The Subjective section covers chief complaint, HPI, past medical/surgical/family/social history, and review of systems as required."},
            {"q": "Can you match a specific patient scenario I provide?", "a": "Yes. Provide the scenario, chief complaint, and any specific parameters and your writer will build a clinically realistic SOAP note around it."},
            {"q": "What if I need SBAR format instead?", "a": "We write SOAP, SBAR, DAR, and other clinical documentation formats — specify your requirement when ordering."},
        ],
    },
    {
        "slug": "nursing-capstone-project-writing-service",
        "title": "Nursing Capstone Project Writing Service",
        "seo_title": "Nursing Capstone Project Writing Service — BSN, MSN & DNP",
        "search_description": "Expert nursing capstone support from PICOT to final paper. BSN, MSN, and DNP levels. From $30/page.",
        "hero_headline": "Nursing Capstone Projects from Proposal to Final Submission",
        "hero_sub": "End-to-end capstone support — PICOT question, literature review, evidence appraisal, implementation plan, and DNP or BSN project paper.",
        "who_for": "BSN, MSN, and DNP students who need structured support for their nursing capstone from proposal development through final submission.",
        "pricing_from": "30.00",
        "turnaround_hours_fastest": 24,
        "turnaround_hours_standard": 720,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "PICOT question development",
            "Systematic literature review and evidence appraisal",
            "Project implementation and evaluation plan",
            "DNP project, MSN capstone, and BSN capstone formats",
            "Extended 14-day revision window",
        ],
        "delivers_items": [
            "Full capstone paper or individual chapters",
            "Evidence-based practice framework applied (ACE Star, Iowa, etc.)",
            "Properly formatted with APA 7th edition",
            "IRB and scholarly integrity guidance included",
        ],
        "faqs": [
            {"q": "Can you help with just the PICOT question and proposal?", "a": "Yes — we support individual sections (proposal, literature review, methodology, implementation plan) or the full capstone project."},
            {"q": "Which EBP frameworks do you use?", "a": "ACE Star Model, Iowa Model, PDSA, and others. We apply whichever framework your programme or faculty specifies."},
            {"q": "Do you support DNP scholarly projects?", "a": "Yes — DNP projects including quality improvement initiatives, practice change proposals, and evidence-based practice implementations."},
            {"q": "What is the revision window for capstone projects?", "a": "Extended 14-day revision window from delivery, with additional time available for larger doctoral projects on request."},
        ],
    },
    {
        "slug": "best-online-nursing-research-paper-service",
        "title": "Nursing Research Paper Writing Service",
        "seo_title": "Nursing Research Paper Writing Service — APA 7th Edition",
        "search_description": "Evidence-based nursing research papers written by qualified nurses. APA 7th, peer-reviewed sources, plagiarism-free. From $24/page.",
        "hero_headline": "Nursing Research Papers Grounded in Current Evidence",
        "hero_sub": "Quantitative, qualitative, and mixed-methods nursing research papers — built on peer-reviewed journals, properly cited in APA 7th or other required styles.",
        "who_for": "Nursing students from ADN through DNP who need a well-structured, evidence-based research paper on any clinical or nursing theory topic.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Current peer-reviewed nursing and medical journals sourced",
            "Quantitative, qualitative, or mixed-methods approach",
            "APA 7th edition (or AMA, MLA, Chicago)",
            "Free Turnitin plagiarism report",
            "Unlimited revisions",
        ],
        "delivers_items": [
            "Structured introduction, literature review, methodology, results, discussion",
            "PICOT or research question clearly stated",
            "Annotated bibliography available on request",
            "Full reference list and in-text citations",
        ],
        "faqs": [
            {"q": "Can you write quantitative and qualitative research papers?", "a": "Yes — both methodological approaches covered, including mixed-methods designs."},
            {"q": "What databases do your writers use for sources?", "a": "PubMed, CINAHL, Cochrane Library, PsycINFO, and other nursing and health databases."},
            {"q": "Can I specify which journals or sources to use?", "a": "Yes — add required sources, textbooks, or databases to your order instructions."},
            {"q": "Do you include a methodology section?", "a": "Yes, for empirical papers. For theoretical or analytical papers, the structure follows your programme's requirements."},
        ],
    },
    {
        "slug": "nursing-case-study-help",
        "title": "Nursing Case Study Writing Service",
        "seo_title": "Nursing Case Study Writing Service — Clinical Reasoning",
        "search_description": "Expert nursing case study analysis using ADPIE and clinical reasoning. Written by BSN/MSN nurses. From $26/page.",
        "hero_headline": "Nursing Case Studies That Think Like a Clinician",
        "hero_sub": "Patient scenario analysis with nursing diagnosis, clinical reasoning, evidence-based interventions, and outcome evaluation — written by nurses who've been there.",
        "who_for": "Nursing students who need rigorous clinical case study analysis that demonstrates critical thinking, clinical judgment, and evidence-based practice.",
        "pricing_from": "26.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Patient scenario analysis using clinical reasoning frameworks",
            "Nursing diagnoses and priority setting",
            "Evidence-based intervention with rationale",
            "Legal, ethical, and cultural considerations",
            "Free revisions",
        ],
        "delivers_items": [
            "Full case study in your programme's required format",
            "Assessment, diagnosis, planning, implementation, evaluation (ADPIE)",
            "Cited evidence from current nursing literature",
            "Reflection section where required",
        ],
        "faqs": [
            {"q": "Can you analyse a case study I've been given?", "a": "Yes — share the case scenario, patient details, and any specific questions or rubric and your writer will build the analysis around it."},
            {"q": "Which clinical reasoning frameworks do you use?", "a": "ADPIE, clinical judgment model (NCSBN), clinical reasoning cycle, and others as required by your programme."},
            {"q": "Do you cover mental health nursing case studies?", "a": "Yes — mental health, medical-surgical, paediatric, maternity, critical care, and all other clinical areas covered."},
            {"q": "Can you include a reflection?", "a": "Yes — Gibbs, Johns, Driscoll, or other reflective frameworks added on request."},
        ],
    },
    {
        "slug": "nursing-dissertation-writing-service",
        "title": "Nursing Dissertation & Thesis Writing Service",
        "seo_title": "Nursing Dissertation Writing Service — DNP & PhD Experts",
        "search_description": "Expert nursing dissertation writing from proposal to defence. DNP, MSN, and PhD levels. From $32/page.",
        "hero_headline": "Nursing Dissertations Written by DNP & PhD-Level Experts",
        "hero_sub": "Chapter-by-chapter dissertation support — from proposal and PICOT to methodology, findings, and defence preparation.",
        "who_for": "MSN and DNP students who need expert-level support for their nursing dissertation or doctoral project — from concept through final submission.",
        "pricing_from": "32.00",
        "turnaround_hours_fastest": 24,
        "turnaround_hours_standard": 720,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "DNP project, MSN thesis, and PhD dissertation support",
            "PICOT development and research design consultation",
            "Chapter-by-chapter delivery with review cycles",
            "Supervisor feedback integration",
            "Extended 21-day revision window",
        ],
        "delivers_items": [
            "Full dissertation or individual chapters",
            "Properly designed methodology (qualitative, quantitative, mixed)",
            "Data analysis with interpretation",
            "APA 7th formatted bibliography",
        ],
        "faqs": [
            {"q": "Can you help with just one chapter?", "a": "Yes — individual chapters (literature review, methodology, findings, discussion) or the full dissertation."},
            {"q": "Do you support DNP scholarly projects?", "a": "Yes — quality improvement projects, practice change proposals, and evidence-based implementation projects at doctoral level."},
            {"q": "What is the revision window for dissertations?", "a": "Extended 21-day revision window. Additional revision time available for larger doctoral projects."},
            {"q": "Can you incorporate supervisor feedback?", "a": "Yes — share supervisor comments or committee feedback and your writer will revise accordingly."},
        ],
    },
    {
        "slug": "concept-map-writing-services",
        "title": "Nursing Concept Map Writing Service",
        "seo_title": "Nursing Concept Map Writing Service — Clinical & Patient Care",
        "search_description": "Clinically accurate nursing concept maps linking pathophysiology, diagnoses, interventions, and outcomes. From $24/page.",
        "hero_headline": "Nursing Concept Maps That Connect the Clinical Picture",
        "hero_sub": "Visually clear, clinically accurate concept maps linking pathophysiology, nursing diagnoses, interventions, and outcomes — for any patient scenario.",
        "who_for": "ADN and BSN students who need concept maps for clinical courses, simulation prep, or medication management assignments.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 96,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Pathophysiology to nursing diagnosis linkage",
            "Priority nursing diagnoses ranked",
            "Evidence-based interventions mapped",
            "Expected outcomes and evaluation criteria",
            "Free revisions",
        ],
        "delivers_items": [
            "Completed concept map in your programme's preferred format",
            "Written rationale for each link and intervention",
            "Colour-coded or structured diagram as required",
            "Supporting reference list",
        ],
        "faqs": [
            {"q": "What format do you deliver concept maps in?", "a": "Word document (table or diagram format), PDF, or a PowerPoint slide — specify your programme's preference when ordering."},
            {"q": "Can you build a concept map for a specific patient diagnosis?", "a": "Yes — provide the primary diagnosis and any comorbidities and your writer builds the full clinical picture."},
            {"q": "Do you cover medication concept maps?", "a": "Yes — pharmacology concept maps linking drug class, mechanism, indications, side effects, and nursing considerations."},
            {"q": "How fast can you deliver a concept map?", "a": "Most concept maps are delivered within 24 hours. Rush delivery from 3 hours is available."},
        ],
    },
    {
        "slug": "nursing-coursework-help-online",
        "title": "Nursing Coursework & Assignment Help",
        "seo_title": "Nursing Coursework & Assignment Help from $24/Page",
        "search_description": "Reliable nursing coursework help — discussions, reflections, pharmacology, and more. From $24/page.",
        "hero_headline": "Consistent Nursing Assignment Help, Every Week",
        "hero_sub": "Weekly discussions, reflection journals, pharmacology assignments, and module work handled by the same nursing writer who knows your course.",
        "who_for": "Nursing students managing heavy coursework loads — ADN through DNP — who need reliable, expert weekly help across one or more modules.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Discussion board posts and responses",
            "Reflective practice journals (Gibbs, Johns, Driscoll)",
            "Pharmacology and pathophysiology assignments",
            "Short and extended nursing assignments",
            "Free revisions",
        ],
        "delivers_items": [
            "Completed assignment to your brief and rubric",
            "Evidence-based content with current nursing sources",
            "APA 7th formatted references",
            "On-time delivery guaranteed",
        ],
        "faqs": [
            {"q": "Can I use the same writer for all my module assignments?", "a": "Yes — we strongly recommend requesting the same writer for ongoing coursework so they build familiarity with your subject and academic voice."},
            {"q": "Do you write discussion board posts and peer responses?", "a": "Yes — initial posts and peer response posts, formatted to your LMS requirements."},
            {"q": "Can you help with pharmacology calculations?", "a": "Yes — dosage calculations, drug classification, mechanism of action, and pharmacology assignment questions are all covered."},
            {"q": "What reflective models do you use?", "a": "Gibbs, Johns, Driscoll, and the ERA cycle — specify your module's preferred model when ordering."},
        ],
    },
    {
        "slug": "nursing-class-help-online",
        "title": "Online Nursing Class Help",
        "seo_title": "Online Nursing Class Help — Full Course Management",
        "search_description": "Qualified nurses handle your online nursing classes — discussions, quizzes, assignments. Discreet, grade-focused. From $35/page.",
        "hero_headline": "Let a Nursing Expert Handle Your Online Classes",
        "hero_sub": "Full online nursing course management — discussions, quizzes, exams, and assignments — handled by a qualified nurse so you can focus on clinical hours.",
        "who_for": "Nursing students who are overwhelmed by multiple online courses and need a qualified nursing professional to manage coursework while they complete clinical rotations.",
        "pricing_from": "35.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Full course or individual module management",
            "Discussion posts, peer responses, and weekly assignments",
            "Proctored and unproctored quiz/exam support",
            "Pharmacology, pathophysiology, mental health, and all nursing subjects",
            "Dedicated writer for the duration of the course",
        ],
        "delivers_items": [
            "All weekly submissions completed on time",
            "Grade-conscious approach — your rubric is our standard",
            "Regular progress updates throughout the course",
            "Confidential and discreet handling",
        ],
        "faqs": [
            {"q": "Can you take over my entire online nursing course?", "a": "Yes — we handle all weekly submissions, discussions, quizzes, and assignments for one course or multiple courses simultaneously."},
            {"q": "Which LMS platforms do you support?", "a": "Canvas, Blackboard, Moodle, and any other LMS your programme uses."},
            {"q": "How do you ensure confidentiality?", "a": "All work is handled discreetly. We never share client information and use secure communication throughout."},
            {"q": "Can you handle timed quizzes and exams?", "a": "Yes — let us know the quiz window and any constraints and your assigned nurse will complete it within the allotted time."},
        ],
    },
    {
        "slug": "shadow-health-help-online",
        "title": "Shadow Health Digital Clinical Experience Help",
        "seo_title": "Shadow Health DCE Help — Tina Jones & All Patients",
        "search_description": "Expert Shadow Health Digital Clinical Experience completion by practicing nurses. Tina Jones, Brian Foster, all patients. From $35.",
        "hero_headline": "Shadow Health DCEs Completed by Practicing Nurses",
        "hero_sub": "Digital Clinical Experiences — Tina, Brian, Danny, and all Shadow Health patients — documented accurately and professionally by nurses who know the platform inside out.",
        "who_for": "Nursing students enrolled in programmes using Shadow Health — ADN, BSN, MSN, and NP students struggling with DCE time demands or clinical reasoning documentation.",
        "pricing_from": "35.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 48,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "All Shadow Health patient encounters: Tina Jones, Brian Foster, Danny Rivera, and more",
            "Subjective, Objective, Assessment, Plan documentation for each DCE",
            "Education section, reflection, and evidence-based rationale included",
            "Scored to meet your programme's passing threshold",
            "Completed within your deadline — usually same-day",
        ],
        "delivers_items": [
            "Completed DCE documentation submitted on your behalf or as a reference",
            "Health history, physical exam, and clinical reasoning sections",
            "SBAR or clinical note format where required",
            "Full reflection and self-evaluation sections",
        ],
        "faqs": [
            {"q": "Which Shadow Health patients do you cover?", "a": "All Shadow Health patients — Tina Jones, Brian Foster, Danny Rivera, and all other DCE cases across every speciality."},
            {"q": "Do you complete the reflection and education sections?", "a": "Yes — all DCE sections including health history, physical exam, assessment, education, and reflection are completed."},
            {"q": "How do you access my Shadow Health account?", "a": "You share temporary credentials securely. We complete the DCE and you can update your password immediately after."},
            {"q": "How fast can you complete a Shadow Health DCE?", "a": "Same-day completion is standard. Rush delivery within 3 hours is available for urgent DCE deadlines."},
        ],
    },
    {
        "slug": "ihuman-help",
        "title": "iHuman Virtual Patient Case Help",
        "seo_title": "iHuman Virtual Patient Case Help — Clinical Reasoning",
        "search_description": "Expert iHuman virtual patient case completion by practicing nurses. Clinical reasoning, differentials, treatment plans. From $35.",
        "hero_headline": "iHuman Cases Completed by Clinical Nursing Experts",
        "hero_sub": "Virtual patient encounters on iHuman require clinical reasoning, differential diagnosis, and evidence-based decision-making — our nurses have done hundreds of these.",
        "who_for": "Nursing and NP students using the iHuman platform for virtual patient encounters who need support with clinical reasoning documentation and case completion.",
        "pricing_from": "35.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 48,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Full iHuman patient case completion — history, physical, assessment",
            "Differential diagnosis with evidence-based rationale",
            "Diagnostic reasoning and clinical decision-making documentation",
            "Treatment plan and patient education sections",
            "Completed within your deadline",
        ],
        "delivers_items": [
            "All iHuman case sections completed to your rubric",
            "Clinical reasoning narrative with supporting evidence",
            "Differential diagnoses ranked with rationale",
            "Follow-up and management plan",
        ],
        "faqs": [
            {"q": "Which iHuman cases do you cover?", "a": "All iHuman virtual patient cases across all speciality areas — acute care, primary care, chronic disease management, and more."},
            {"q": "Do you write the differential diagnoses?", "a": "Yes — differentials are ranked by likelihood with evidence-based clinical reasoning supporting each entry."},
            {"q": "How do you access my iHuman account?", "a": "You share temporary credentials securely. We complete the case and you can update your password immediately after."},
            {"q": "Can you help with iHuman assessment scoring?", "a": "Yes — our nurses are familiar with the iHuman scoring rubric and aim to meet your programme's required score."},
        ],
    },
    {
        "slug": "nursing-research-for-sale-online",
        "title": "Buy Nursing Papers Online — Written by Real Nurses",
        "seo_title": "Buy Nursing Papers Online — Written by BSN, MSN & DNP Nurses",
        "search_description": "Buy custom nursing papers written by qualified nurses. Care plans, essays, SOAP notes, capstone projects. Grade guaranteed. From $24/page.",
        "hero_headline": "Buy Nursing Papers Written by BSN, MSN & DNP Nurses",
        "hero_sub": "Every nursing paper we write is original, clinically grounded, and delivered on time. From care plans to dissertations — all nursing paper types available.",
        "who_for": "Nursing students at any level — ADN through DNP — who need a reliable, clinically grounded nursing paper written by a qualified nurse.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "All nursing paper types: essays, care plans, SOAP notes, capstone projects",
            "Written by credentialed nurses with active clinical experience",
            "APA 7th edition formatting as standard",
            "Free Turnitin plagiarism report included",
            "Grade or money-back guarantee on every order",
        ],
        "delivers_items": [
            "Completed nursing paper written to your exact brief",
            "Clinically accurate content sourced from peer-reviewed nursing literature",
            "Free plagiarism report verifying originality",
            "On-time delivery guaranteed",
        ],
        "faqs": [
            {"q": "What types of nursing papers can I buy?", "a": "Essays, care plans, SOAP notes, research papers, case studies, capstone projects, dissertations, concept maps, and more."},
            {"q": "Are the papers written from scratch?", "a": "Yes — every paper is original, written to your specific brief, and never resold or reused."},
            {"q": "How do I know my paper will get a good grade?", "a": "Share your rubric and marking criteria. Your writer follows it precisely. We back every order with a grade or money-back guarantee."},
            {"q": "Can I see the writer's credentials?", "a": "Yes — writer profiles are available. You can also message your writer before work begins."},
        ],
    },
    {
        "slug": "nursing-report-writing-service",
        "title": "Nursing Report Writing Service",
        "seo_title": "Nursing Report Writing Service — Clinical Documentation Help",
        "search_description": "Expert nursing report writing — incident reports, SBAR, progress notes, clinical case reports. From $24/page.",
        "hero_headline": "Nursing Reports Written to Clinical Documentation Standards",
        "hero_sub": "Incident reports, shift handover reports, patient progress notes, and clinical case reports — written by experienced nurses who know how documentation works in practice.",
        "who_for": "Nursing students who need help writing clinical reports, incident documentation, or case reports for academic submission or portfolio development.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 96,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Incident reports, progress notes, and shift summaries",
            "Clinical case reports and patient documentation",
            "SBAR-format reports and handover notes",
            "Written by BSN/MSN nurses with documentation experience",
            "Free revisions within review window",
        ],
        "delivers_items": [
            "Complete nursing report to your brief and format",
            "Clear, concise clinical language throughout",
            "Properly structured sections per report type",
            "References cited in APA 7th where required",
        ],
        "faqs": [
            {"q": "What types of nursing reports do you write?", "a": "Incident reports, shift handover reports, patient progress notes, clinical case reports, SBAR communications, and academic clinical reports."},
            {"q": "Do you write reports for portfolio submissions?", "a": "Yes — clinical portfolio entries, reflective reports, and professional practice documentation are all covered."},
            {"q": "Can you write an SBAR communication for a simulation scenario?", "a": "Yes — provide the patient scenario and we'll produce a complete SBAR formatted to your programme's standards."},
            {"q": "How fast can you deliver a nursing report?", "a": "Most reports are delivered within 24 hours. Rush delivery from 3 hours is available."},
        ],
    },
    {
        "slug": "nursing-presentation-writing-service",
        "title": "Nursing Presentation (PPT) Writing Service",
        "seo_title": "Nursing Presentation Writing Service — PPT & Speaker Notes",
        "search_description": "Expert nursing PowerPoint presentations for capstone defence, seminars, and clinical rounds. Evidence-based, APA cited. From $26.",
        "hero_headline": "Nursing Presentations That Communicate Clinical Evidence Clearly",
        "hero_sub": "PowerPoint slides for nursing seminars, capstone defence, clinical case presentations, and journal club — structured, evidence-based, and professionally formatted.",
        "who_for": "Nursing students preparing for capstone defence presentations, clinical case rounds, seminar presentations, or journal club facilitation.",
        "pricing_from": "26.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Slide-by-slide content development",
            "Speaker notes for every slide",
            "Evidence-based clinical content with APA-cited sources",
            "Designed for capstone defence, seminar, or clinical rounds",
            "Free revisions",
        ],
        "delivers_items": [
            "Complete PowerPoint presentation to your brief",
            "Structured narrative flow from problem to conclusion",
            "Data visualisations, tables, and clinical images guidance",
            "Speaker notes timed to your presentation slot",
        ],
        "faqs": [
            {"q": "Do you write the speaker notes as well as the slides?", "a": "Yes — speaker notes are included for every slide, timed to your allotted presentation slot where specified."},
            {"q": "Can you build a presentation for my capstone defence?", "a": "Yes — capstone defence presentations are one of our most common requests. Share your capstone paper and your writer will build the presentation around it."},
            {"q": "What software format do you deliver in?", "a": "PowerPoint (.pptx) as standard. Google Slides conversion available on request."},
            {"q": "How many slides will the presentation be?", "a": "Typically 1–2 slides per minute of presentation time. Specify your time slot and we'll structure accordingly."},
        ],
    },
    {
        "slug": "reliable-and-cheap-bsn-writing-service",
        "title": "BSN Nursing Writing Services",
        "seo_title": "BSN Nursing Writing Services — Essays, Care Plans & Capstone",
        "search_description": "Comprehensive writing help for BSN nursing students. Essays, care plans, SOAP notes, capstone projects. From $24/page.",
        "hero_headline": "Writing Services Built Specifically for BSN Students",
        "hero_sub": "From first-year fundamentals essays to senior capstone projects — every BSN writing assignment handled by qualified nurses who understand what your programme expects.",
        "who_for": "BSN nursing students at any year who need reliable academic writing support — from fundamentals in Year 1 to capstone projects in Year 4.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "All BSN-level assignments: essays, care plans, SOAP notes, capstone",
            "Writers who hold BSN credentials and understand programme expectations",
            "APA 7th edition formatting throughout",
            "NANDA, NIC, NOC, and ADPIE frameworks applied correctly",
            "Free Turnitin report and unlimited revisions",
        ],
        "delivers_items": [
            "Complete assignment written to your rubric and programme level",
            "Clinically grounded content appropriate to BSN competency",
            "Properly cited peer-reviewed nursing sources",
            "Grade or money back guarantee",
        ],
        "faqs": [
            {"q": "Do your writers understand BSN curriculum requirements?", "a": "Yes — all our writers hold BSN credentials and have direct experience with BSN programme assignments and clinical competencies."},
            {"q": "Can you help from Year 1 fundamentals through Year 4 capstone?", "a": "Yes — all years of BSN programmes supported, from nursing theory and fundamentals through capstone projects and clinical practice papers."},
            {"q": "Do you use NANDA and ADPIE correctly?", "a": "Yes — nursing diagnoses, interventions, outcomes, and care planning all follow NANDA-I, NIC, NOC, and ADPIE standards."},
            {"q": "Can I get help with my nursing portfolio?", "a": "Yes — portfolio entries, reflective journals, clinical logs, and skills sign-off documentation are all covered."},
        ],
    },
    {
        "slug": "reliable-msn-writing-services",
        "title": "MSN Nursing Writing Help",
        "seo_title": "MSN Nursing Writing Help — Graduate-Level Papers & Capstone",
        "search_description": "Expert writing support for MSN nursing students. Scholarly papers, NP coursework, policy analysis, capstone. From $32/page.",
        "hero_headline": "Advanced Writing Support for MSN Students and NP Programmes",
        "hero_sub": "Literature reviews, scholarly papers, policy analyses, clinical practicums, and MSN capstone projects — written by DNP and PhD-credentialed nursing faculty.",
        "who_for": "MSN students in clinical speciality, nurse educator, nurse leader, or NP programmes who need expert-level writing support for graduate coursework and programme requirements.",
        "pricing_from": "32.00",
        "turnaround_hours_fastest": 12,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "MSN-level scholarly papers and advanced clinical writing",
            "Literature reviews with systematic search strategy",
            "Policy analysis and healthcare leadership papers",
            "NP coursework: SOAP notes, clinical logs, case presentations",
            "Extended revision window for complex projects",
        ],
        "delivers_items": [
            "Scholarly writing at graduate nursing level",
            "Synthesis of peer-reviewed nursing and healthcare literature",
            "APA 7th formatted with graduate-level academic rigour",
            "Original analysis and evidence-based argumentation",
        ],
        "faqs": [
            {"q": "Do you support all MSN speciality tracks?", "a": "Yes — clinical speciality, nurse educator, nurse leader, NP tracks, and dual degree programmes."},
            {"q": "Can you help with NP clinical log and case presentation requirements?", "a": "Yes — SOAP notes, clinical encounter logs, patient case presentations, and pharmacotherapy papers for NP programmes."},
            {"q": "What level of academic rigour do MSN papers require?", "a": "Graduate level — synthesis rather than description, integration of theory and evidence, and scholarly argumentation throughout."},
            {"q": "Can you write healthcare policy analysis papers?", "a": "Yes — healthcare policy, health systems leadership, quality improvement, and nursing administration papers covered."},
        ],
    },
    {
        "slug": "apa-format-nursing-paper-writing-service",
        "title": "APA Nursing Paper Writing Service",
        "seo_title": "APA Nursing Paper Writing Service — 7th Edition Formatting",
        "search_description": "Nursing papers written and formatted in APA 7th edition. All citation types, heading levels, reference lists. From $24/page.",
        "hero_headline": "Nursing Papers Written and Formatted in APA 7th Edition",
        "hero_sub": "Every nursing paper we write follows APA 7th edition — in-text citations, reference lists, headings, tables, and figures — all correctly formatted by writers who use it daily.",
        "who_for": "Nursing students who need a properly APA-formatted paper — or who have written a draft that needs expert APA formatting review and correction.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "APA 7th edition formatting throughout — headings, margins, spacing",
            "In-text citations and reference list correctly formatted",
            "DOI hyperlinks, journal italics, and author formats correct",
            "Free plagiarism report confirming originality",
            "Free revisions for any APA formatting corrections",
        ],
        "delivers_items": [
            "Fully APA 7th formatted nursing paper",
            "Title page, abstract (if required), and references page",
            "Correct running head (if required by your programme)",
            "Level 1–3 headings consistently applied",
        ],
        "faqs": [
            {"q": "What APA 7th changes do I need to know about?", "a": "APA 7th removed the running head requirement for student papers, updated DOI formatting, changed et al. rules, and introduced new bias-free language guidelines — all applied correctly by your writer."},
            {"q": "Can you format a paper I've already written?", "a": "Yes — share your draft and we'll apply full APA 7th formatting: title page, abstract, headings, citations, and reference list."},
            {"q": "Do you format tables and figures in APA 7th?", "a": "Yes — tables and figures formatted with correct APA 7th captions, notes, and placement."},
            {"q": "What if my institution has deviations from standard APA?", "a": "Share your style guide or institution requirements and we'll apply those specific rules."},
        ],
    },
    {
        "slug": "health-and-medicine-paper-writing-service",
        "title": "Medical & Health Sciences Paper Writing Service",
        "seo_title": "Medical Paper Writing Service — Nursing, Medicine & Health Sciences",
        "search_description": "Expert medical and health sciences paper writing by clinicians. Nursing, medicine, public health, pharmacy. From $26/page.",
        "hero_headline": "Medical Papers Written by Healthcare Professionals",
        "hero_sub": "Research papers, case studies, and academic assignments across medicine, public health, pharmacy, and allied health — written by clinically experienced professionals.",
        "who_for": "Students in nursing, medicine, public health, pharmacy, and allied health disciplines who need expert clinical writing for academic assignments.",
        "pricing_from": "26.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Medical research papers, case reports, and literature reviews",
            "Public health, pharmacology, and health sciences assignments",
            "APA, AMA, Vancouver, or Chicago citation as required",
            "Written by nurses, clinicians, and healthcare professionals",
            "Free plagiarism report included",
        ],
        "delivers_items": [
            "Complete medical or health sciences paper to your brief",
            "Clinically accurate content with peer-reviewed medical sources",
            "Correctly formatted references and in-text citations",
            "Appropriate medical terminology and clinical reasoning",
        ],
        "faqs": [
            {"q": "Do you cover pharmacology and pharmacy assignments?", "a": "Yes — pharmacokinetics, pharmacodynamics, drug classifications, mechanism of action, and clinical pharmacology papers."},
            {"q": "Can you write public health papers?", "a": "Yes — epidemiology, health promotion, community health, social determinants of health, and health policy."},
            {"q": "Do you use AMA citation style?", "a": "Yes — APA, AMA, Vancouver, Chicago, and any other style your programme requires."},
            {"q": "Are your writers clinically qualified?", "a": "Yes — all writers have nursing or allied health credentials with active or recent clinical experience."},
        ],
    },
    {
        "slug": "online-nursing-homework-help",
        "title": "Nursing Homework Help Online",
        "seo_title": "Nursing Homework Help Online — Weekly Assignments & Problems",
        "search_description": "Get your nursing homework done by a qualified nurse. Discussions, pharmacology, pathophysiology, short assignments. From $24/page.",
        "hero_headline": "Nursing Homework Done by a Qualified Nurse Tonight",
        "hero_sub": "Short weekly assignments, discussion posts, pathophysiology problems, pharmacology calculations, and any other nursing homework — handled by a BSN/MSN nurse who knows your subject.",
        "who_for": "Nursing students who need reliable weekly homework help across any nursing subject — from fundamentals to advanced pathophysiology and pharmacology.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 48,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Weekly discussion posts and peer responses",
            "Short nursing assignments and homework problems",
            "Pharmacology and pathophysiology questions",
            "Concept questions, quizzes, and worksheet assistance",
            "Fast turnaround — as little as 3 hours for short tasks",
        ],
        "delivers_items": [
            "Completed homework to your rubric and brief",
            "Evidence-based answers with appropriate citations",
            "APA 7th formatted references where required",
            "Submitted within your deadline",
        ],
        "faqs": [
            {"q": "Can you help with pharmacology drug cards?", "a": "Yes — drug class, mechanism, indications, contraindications, side effects, and nursing considerations all covered."},
            {"q": "Do you answer pathophysiology questions?", "a": "Yes — disease processes, clinical manifestations, diagnostic criteria, and nursing management of any pathophysiology topic."},
            {"q": "How fast can you complete short nursing homework?", "a": "As fast as 3 hours for short assignments. Turnaround depends on complexity and length."},
            {"q": "Can you respond to my classmates' discussion posts?", "a": "Yes — peer response posts written to your programme's requirements, engaging substantively with the original post."},
        ],
    },
    {
        "slug": "postgraduate-nursing-papers-assignments-help",
        "title": "Postgraduate Nursing Writing Help",
        "seo_title": "Postgraduate Nursing Writing Help — MSN, DNP & PhD Support",
        "search_description": "Expert postgraduate nursing writing help. MSN papers, DNP projects, PhD dissertations. Doctoral-level quality. From $32/page.",
        "hero_headline": "Expert Writing Support for MSN, DNP & PhD Nursing Students",
        "hero_sub": "Postgraduate nursing demands graduate-level clinical reasoning and academic writing. Our DNP and PhD-credentialed writers provide the scholarly depth your programme expects.",
        "who_for": "MSN, DNP, and PhD nursing students who need doctoral-calibre writing support — from coursework papers through dissertation chapters and scholarly projects.",
        "pricing_from": "32.00",
        "turnaround_hours_fastest": 12,
        "turnaround_hours_standard": 336,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "MSN, DNP, and PhD-level nursing papers and projects",
            "Doctoral-level clinical reasoning and evidence synthesis",
            "Capstone projects, dissertations, and scholarly papers",
            "Policy analysis, quality improvement, and leadership papers",
            "Extended revision window for complex postgraduate work",
        ],
        "delivers_items": [
            "Graduate or doctoral-level writing with appropriate rigour",
            "Synthesis of primary and secondary nursing literature",
            "Properly structured scholarly argument throughout",
            "APA 7th formatted with full reference list",
        ],
        "faqs": [
            {"q": "What is the difference between MSN and DNP writing?", "a": "MSN writing is scholarly and graduate-level. DNP writing is practice-focused, applying evidence to clinical problems and quality improvement. Our writers understand both standards."},
            {"q": "Can you help with quality improvement papers?", "a": "Yes — PDSA cycles, Plan-Do-Study-Act frameworks, and QI project papers for DNP and MSN programmes."},
            {"q": "Do you support nursing leadership and administration papers?", "a": "Yes — transformational leadership, nurse leader competencies, staffing models, and health systems management papers."},
            {"q": "Can you write a systematic literature review for a PhD?", "a": "Yes — PRISMA-compliant systematic reviews with full search strategy, inclusion/exclusion criteria, and thematic synthesis."},
        ],
    },
    {
        "slug": "nursing-evidence-based-practice",
        "title": "Evidence-Based Practice (EBP) Nursing Paper Writing Service",
        "seo_title": "Evidence-Based Practice Nursing Paper Writing Service — EBP Help",
        "search_description": "Expert EBP nursing papers using PICOT, clinical appraisal, and synthesis of current evidence. Written by BSN/MSN nurses. From $26/page.",
        "hero_headline": "EBP Nursing Papers Built on Current Clinical Evidence",
        "hero_sub": "PICOT-driven evidence-based practice papers, systematic appraisals, and EBP project proposals — written by nurses who apply evidence-based practice every clinical shift.",
        "who_for": "BSN, MSN, and DNP nursing students who need rigorous EBP papers that demonstrate critical appraisal skills and application of current evidence to clinical practice.",
        "pricing_from": "26.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "PICOT question development and refinement",
            "Systematic literature search with inclusion/exclusion criteria",
            "Critical appraisal of primary research using validated tools (CASP, JBI)",
            "Evidence synthesis and clinical applicability discussion",
            "APA 7th edition formatting throughout",
            "Free plagiarism report",
        ],
        "delivers_items": [
            "Full EBP paper with PICOT, evidence appraisal, and clinical recommendations",
            "Synthesis table summarising appraised studies",
            "Implications for practice section",
            "Formatted reference list with DOIs",
        ],
        "faqs": [
            {"q": "What is a PICOT question and can you help develop one?", "a": "PICOT stands for Population, Intervention, Comparison, Outcome, and Time. Your writer helps you formulate a clear, focused PICOT question appropriate to your clinical topic."},
            {"q": "Which critical appraisal tools do you use?", "a": "CASP checklists, JBI critical appraisal tools, GRADE framework, and others — whichever your programme or faculty requires."},
            {"q": "Can you write a full EBP project proposal?", "a": "Yes — from PICOT through literature search, evidence appraisal, implementation plan, and evaluation strategy."},
            {"q": "Do you cover EBP frameworks?", "a": "Yes — Iowa Model, ACE Star Model, Stetler Model, PDSA, and others. Specify which your programme uses."},
        ],
    },
    {
        "slug": "nursing-annotated-bibliography",
        "title": "Nursing Annotated Bibliography Writing Service",
        "seo_title": "Nursing Annotated Bibliography Writing Service — APA 7th Edition",
        "search_description": "Expert nursing annotated bibliographies with critical summaries and APA 7th citations. Written by qualified nurses. From $24/page.",
        "hero_headline": "Nursing Annotated Bibliographies — Critically Summarised, APA Formatted",
        "hero_sub": "Source-by-source summaries with critical evaluation of relevance, methodology, and clinical applicability — properly formatted in APA 7th edition by nurses who read the literature daily.",
        "who_for": "Nursing students who need an annotated bibliography for a research paper, capstone project, or literature review assignment — with genuine critical analysis of each source.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 3,
        "turnaround_hours_standard": 96,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Full APA 7th citation for each source",
            "Summary of the source's purpose, methodology, and key findings",
            "Critical evaluation of strengths, limitations, and relevance to your topic",
            "Commentary on how each source fits your research question",
            "Nursing and health-specific sources from CINAHL, PubMed, Cochrane",
            "Free revisions",
        ],
        "delivers_items": [
            "Complete annotated bibliography to your required source count",
            "Annotations written in academic nursing language",
            "APA 7th formatted references and annotations",
            "Sources drawn from peer-reviewed nursing literature",
        ],
        "faqs": [
            {"q": "How long is each annotation?", "a": "Typically 150–300 words per source unless your assignment specifies a different length. Share your rubric and we'll match it exactly."},
            {"q": "Can you find the sources as well as annotate them?", "a": "Yes — if you need sources identified as well as annotated, provide your topic and we'll source and annotate appropriate peer-reviewed literature."},
            {"q": "Can I supply my own list of sources?", "a": "Yes — provide your source list (or PDFs) and your writer will produce annotations for each."},
            {"q": "Do you annotate non-nursing sources?", "a": "Yes — nursing research, medical journals, public health, psychology, and any other discipline your assignment requires."},
        ],
    },
    {
        "slug": "hire-a-health-and-medical-writer",
        "title": "Health & Medical Writers for Hire",
        "seo_title": "Health & Medical Writers — Credentialed Nursing Professionals",
        "search_description": "Hire credentialed health and medical writers for academic and educational content. BSN, MSN, DNP writers available. From $24/page.",
        "hero_headline": "Credentialed Health and Medical Writers Available Now",
        "hero_sub": "BSN, MSN, DNP, and PhD-credentialed health professionals who write — for academic assignments, clinical education content, and health communications.",
        "who_for": "Students, healthcare educators, and professionals who need credentialed health and nursing writers for academic or educational content.",
        "pricing_from": "24.00",
        "turnaround_hours_fastest": 6,
        "turnaround_hours_standard": 168,
        "primary_cta_text": "Order now",
        "primary_cta_url": "/order/",
        "includes_items": [
            "Nursing and medical academic writing at all levels",
            "Health communications, patient education, and clinical guides",
            "Public health, pharmacology, and health policy content",
            "Writers matched by clinical speciality — not just subject area",
            "Free revisions and plagiarism report with every assignment",
        ],
        "delivers_items": [
            "Clinically accurate, professionally written content",
            "Evidence from peer-reviewed nursing and medical literature",
            "APA, AMA, or other required citation style",
            "Completed to your brief and submission deadline",
        ],
        "faqs": [
            {"q": "How do you match writers to assignments?", "a": "By clinical speciality — a NICU case goes to a neonatal nurse, an FNP SOAP note goes to a family nurse practitioner."},
            {"q": "Can I view a writer's profile before committing?", "a": "Yes — writer profiles including credentials, specialities, and sample work are available before you confirm your order."},
            {"q": "Do you write patient education materials?", "a": "Yes — discharge instructions, patient handouts, medication guides, and health literacy-appropriate patient education content."},
            {"q": "Can you help with clinical education content for nurse educators?", "a": "Yes — case scenarios, simulation debriefs, competency assessment tools, and clinical teaching materials."},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed all 24 NurseMyGrade service pages into Wagtail"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--site",
            default="nursemygrade.com",
            help="Hostname of the target Wagtail site (default: nursemygrade.com)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing pages instead of skipping them",
        )

    def handle(self, *args, **options):
        from decimal import Decimal
        from wagtail.models import Site
        from cms_service_pages.models import ServiceIndexPage, ServicePage

        hostname = options["site"]
        do_update = options["update"]

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"No Wagtail site found for '{hostname}'. Run setup_tenants first."
                )
            )
            return

        try:
            svc_index = ServiceIndexPage.objects.child_of(site.root_page).get()
        except ServiceIndexPage.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    "No ServiceIndexPage found under this site's root. "
                    "Run setup_tenants first."
                )
            )
            return

        self.stdout.write(
            f"Seeding into: {hostname} → ServiceIndexPage id={svc_index.id}"
        )

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
                page = ServicePage(title=svc["title"], slug=slug, live=True)
                self._apply_fields(page, svc)
                svc_index.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  CREATE {slug}"))
                created += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} created, {updated} updated, {skipped} skipped"
            )
        )

    def _apply_fields(self, page, svc: dict):
        from decimal import Decimal
        from cms_service_pages.management.commands.nmg_body_blocks import BODY_BLOCKS

        page.title = svc["title"]
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

        page.includes_items = [
            {"type": "item", "value": item}
            for item in svc.get("includes_items", [])
        ]
        page.delivers_items = [
            {"type": "item", "value": item}
            for item in svc.get("delivers_items", [])
        ]

        slug = svc.get("slug", "")
        if slug in BODY_BLOCKS:
            page.body = BODY_BLOCKS[slug]
        else:
            page.body = [
                {
                    "type": "faq",
                    "value": {
                        "question": faq["q"],
                        "answer": f"<p>{faq['a']}</p>",
                    },
                }
                for faq in svc.get("faqs", [])
            ]
