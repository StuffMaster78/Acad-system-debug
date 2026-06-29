"""
Body block content for NurseMyGrade service pages.

Imported by seed_nursemygrade_services._apply_fields.
Each key is a service slug; the value is a list of StreamField block dicts
compatible with SERVICE_PAGE_BLOCKS in cms_core/blocks.py.

Block format: {"type": "<block_type>", "value": <block_value>}

Blocks used here and their frontend rendering:
  heading        -> text, level (h2/h3), subtitle, accent
  paragraph      -> HTML string (v-html)
  stats_highlight-> {stats: [{value, label}], supporting_text}
  how_it_works   -> {heading, steps: [{step_number, title, description (HTML)}]}
  feature_grid   -> {heading, features: [{icon_name, title, description (plain text)}]}
  checklist      -> {title, items: [{text, detail}]}
  faq            -> {question, answer (HTML)}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _h(text, level="h2"):
    return {"type": "heading", "value": {"text": text, "level": level, "subtitle": "", "accent": "none"}}


def _p(html):
    return {"type": "paragraph", "value": html}


def _stats(*pairs):
    """pairs: ("value", "label") tuples"""
    return {
        "type": "stats_highlight",
        "value": {
            "stats": [{"value": v, "label": l} for v, l in pairs],
            "supporting_text": "",
        },
    }


def _hiw(heading, steps):
    """steps: [(title, description_html), ...]"""
    return {
        "type": "how_it_works",
        "value": {
            "heading": heading,
            "steps": [
                {"step_number": i + 1, "title": t, "description": d}
                for i, (t, d) in enumerate(steps)
            ],
        },
    }


def _fg(heading, features):
    """features: [(title, description_plain_text), ...]"""
    return {
        "type": "feature_grid",
        "value": {
            "heading": heading,
            "features": [{"icon_name": "", "title": t, "description": d} for t, d in features],
        },
    }


def _cl(title, items):
    """items: [(text, detail), ...]"""
    return {
        "type": "checklist",
        "value": {
            "title": title,
            "items": [{"text": t, "detail": d} for t, d in items],
        },
    }


def _faq(q, a_html):
    return {"type": "faq", "value": {"question": q, "answer": a_html}}


def _faq_heading():
    return _h("Frequently Asked Questions")


# ---------------------------------------------------------------------------
# Common how-it-works step 1 + step 4 (reused with variation)
# ---------------------------------------------------------------------------

STEP_SUBMIT = (
    "Submit Your Brief",
    "<p>Share your topic, word count, academic level, deadline, and rubric or marking criteria. "
    "The more detail you provide, the more precisely your writer can target the marks your faculty awards.</p>",
)

STEP_DELIVER = (
    "Delivery and Revision",
    "<p>Your completed work is delivered before your deadline. Review it against your rubric "
    "and request any changes within the revision window. Your original writer makes all amendments "
    "until the work meets your stated requirements.</p>",
)


# ---------------------------------------------------------------------------
# BODY_BLOCKS
# ---------------------------------------------------------------------------

BODY_BLOCKS = {

    # ── 1. Nursing Essay ────────────────────────────────────────────────────
    "online-nursing-essays-help": [
        _stats(
            ("BSN–DNP", "writer credentials"),
            ("3 hrs", "fastest turnaround"),
            ("APA 7th", "citation standard"),
            ("100%", "human-written"),
        ),
        _h("Why Nursing Students Trust NurseMyGrade for Essay Help"),
        _p(
            "<p>A nursing essay is evaluated differently from a general academic essay. "
            "The marker holds clinical credentials and expects you to demonstrate that you understand "
            "how evidence-based practice informs nursing decisions, not just that you can construct a paragraph. "
            "That distinction — from academic exercise to clinical reasoning on paper — is where most students lose marks.</p>"
            "<p>NurseMyGrade assigns nursing essay work exclusively to writers who hold BSN, MSN, or DNP credentials "
            "with current or recent clinical experience. When your essay requires a PICO question, your writer has "
            "formulated one in real EBP projects. When your assignment covers pain assessment, your writer has "
            "performed a numeric rating scale at the bedside. That clinical foundation produces essays that read "
            "— and are marked — differently from content produced by generalist writers.</p>"
        ),
        _hiw("How We Write Your Nursing Essay", [
            STEP_SUBMIT,
            (
                "Writer Matching",
                "<p>A writer with BSN, MSN, or DNP credentials and clinical experience relevant to your essay "
                "topic is assigned. For specialist topics such as mental health, paediatrics, or critical care, "
                "we match by clinical background, not just subject familiarity.</p>",
            ),
            (
                "Evidence-Based Drafting",
                "<p>Your essay is written from current peer-reviewed nursing journals (CINAHL, PubMed, Cochrane) "
                "with EBP frameworks applied where your rubric requires them. Every in-text citation and reference "
                "follows APA 7th edition unless you specify otherwise.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Makes Our Nursing Essays Different", [
            (
                "Clinical Reasoning Applied",
                "Arguments are structured using clinical reasoning frameworks—PICO, Orem’s Self-Care Model, "
                "or whichever EBP framework your rubric specifies. Not just a literature summary.",
            ),
            (
                "APA 7th Edition Built In",
                "In-text citations, reference lists, heading levels, DOI formatting, and student paper conventions "
                "are applied correctly throughout. No formatting errors to cost you marks.",
            ),
            (
                "Reflective Models Covered",
                "Gibbs, Johns, Driscoll, and the ERA cycle are all used regularly. Specify your programme’s "
                "model and your writer applies it structurally, not decoratively.",
            ),
        ]),
        _h("What Makes a Nursing Essay Score in the 70s"),
        _p(
            "<p>Most nursing essay rubrics award high marks across four dimensions: clinical knowledge, "
            "application of evidence, critical analysis, and academic writing quality. Generalist writing services "
            "can sometimes deliver the fourth. They routinely fail on the first three.</p>"
            "<p>Clinical knowledge shows in the precision of terminology. An examiner who has worked in ICU will "
            "notice when a student confuses nursing assessment with nursing diagnosis, or cites an intervention "
            "without grounding it in NANDA-I. That kind of error signals the writer lacks clinical background. "
            "Application of evidence means structuring your argument around what the evidence actually shows, "
            "acknowledging its limitations, and connecting it to practice outcomes. Your writer applies the Iowa "
            "Model or ACE Star structurally because that is how nurses apply evidence in clinical settings, not "
            "because it is a box to tick.</p>"
        ),
        _cl("NurseMyGrade Nursing Essay Quality Checklist", [
            ("Thesis or clinical question clearly stated in the introduction", ""),
            ("EBP framework identified and applied structurally throughout", "Iowa Model, ACE Star, or framework specified by your programme"),
            ("Peer-reviewed nursing journals from the last five years cited", "CINAHL, PubMed, Cochrane, and nursing-specific journals"),
            ("Clinical terminology (NANDA-I, NIC, NOC) used accurately", ""),
            ("APA 7th in-text citations and reference list consistent throughout", ""),
            ("Argument moves from evidence to clinical applicability, not just description", ""),
            ("Reflective model applied structurally for reflective essay types", "Gibbs, Johns, Driscoll, or ERA cycle"),
        ]),
        _faq_heading(),
        _faq("Who writes my nursing essay?",
             "<p>All NurseMyGrade writers hold at minimum a BSN with active or recent clinical experience. "
             "Many hold MSN or DNP credentials. For specialist topics, we match by clinical background—a mental "
             "health essay goes to a nurse with MH clinical experience, not a generalist writer.</p>"),
        _faq("What nursing essay types do you cover?",
             "<p>Reflective, argumentative, analytical, descriptive, SOAP-structured narrative essays, literature "
             "reviews, PICO-based papers, policy analyses, and any other format your programme requires.</p>"),
        _faq("Will my essay be in APA 7th edition?",
             "<p>Yes. APA 7th edition is applied throughout—title page, in-text citations, heading levels, "
             "reference list entries, and DOI formatting. If your institution has style deviations, note them in "
             "your brief and we will follow them.</p>"),
        _faq("Can you write a Gibbs reflective nursing essay?",
             "<p>Yes. Gibbs, Johns, Driscoll, and the ERA cycle are all used regularly. Specify your reflective "
             "framework and your writer structures the essay around it: description, feelings, evaluation, analysis, "
             "conclusion, action plan.</p>"),
        _faq("How do you ensure clinical accuracy?",
             "<p>Writer matching by clinical speciality is the primary mechanism. If your brief references a "
             "specific clinical scenario, protocol, or nursing theory, your writer addresses it accurately and "
             "specifically, not generically.</p>"),
        _faq("What if my essay needs revisions?",
             "<p>Unlimited free revisions are included within the revision window. Your original writer makes all "
             "amendments. If the essay still does not meet your stated requirements after revision rounds, "
             "you receive a full refund.</p>"),
        _faq("How fast can you deliver a nursing essay?",
             "<p>Rush delivery from 3 hours is available for short essays (1–2 pages). Standard turnaround for "
             "a 2,000-word nursing essay is 24–48 hours. Longer papers require more lead time—specify your "
             "deadline when ordering.</p>"),
        _faq("Do you include a reference list?",
             "<p>Yes. A complete APA 7th reference list is included with every essay. Every in-text citation has "
             "a corresponding reference entry and DOIs are hyperlinked where available.</p>"),
    ],

    # ── 2. Nursing Care Plan ─────────────────────────────────────────────────
    "nursing-care-plan-writing-services": [
        _stats(
            ("NANDA-I", "diagnostic taxonomy"),
            ("ADPIE", "care plan structure"),
            ("3 hrs", "fastest delivery"),
            ("BSN–DNP", "writer credentials"),
        ),
        _h("Why BSN Students Choose NurseMyGrade for Care Plan Help"),
        _p(
            "<p>A nursing care plan is not a fill-in-the-blanks exercise. Selecting the correct NANDA-I approved "
            "nursing diagnosis from a patient scenario, ranking diagnoses by clinical priority, writing measurable "
            "short- and long-term goals, and pairing each intervention with an evidence-based rationale—these "
            "are clinical judgment tasks that require real nursing knowledge. Students who submit care plans with "
            "generic interventions and vague goal statements consistently lose marks, regardless of how polished "
            "their formatting is.</p>"
            "<p>NurseMyGrade care plan writers hold active BSN or higher credentials and use NANDA-I, NIC, and NOC "
            "frameworks daily in their academic or clinical work. When you share a patient scenario, your writer "
            "applies the full ADPIE process: Assessment, Diagnosis, Planning, Implementation, and Evaluation. "
            "Goals are written in the SMART format your faculty expects. Interventions are cited from nursing "
            "literature, not drawn from memory.</p>"
        ),
        _hiw("How We Build Your Nursing Care Plan", [
            (
                "Share Your Patient Scenario",
                "<p>Provide the primary diagnosis, any comorbidities, relevant vitals, history, and your assignment "
                "requirements. The more clinical detail you share, the more accurate the care plan will be.</p>",
            ),
            (
                "Diagnosis and Priority Ranking",
                "<p>Your writer identifies NANDA-I approved nursing diagnoses for the patient scenario and ranks "
                "them by clinical priority using the ABCs (airway, breathing, circulation) and Maslow’s hierarchy "
                "of needs as the guiding frameworks.</p>",
            ),
            (
                "Goals, Interventions, and Rationale",
                "<p>Short- and long-term goal statements are written in measurable, time-bound format. Each "
                "NIC-aligned nursing intervention is paired with a cited evidence-based rationale from current "
                "nursing literature.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Care Plan Includes", [
            (
                "NANDA-I Approved Diagnoses",
                "Diagnoses are drawn directly from the current NANDA-I taxonomy, formatted with the three-part "
                "diagnostic statement: problem, etiology (related to), and defining characteristics (as evidenced by).",
            ),
            (
                "NIC Interventions with Rationale",
                "Every nursing intervention is NIC-aligned and paired with a cited evidence-based rationale. "
                "Your faculty can trace every recommendation back to peer-reviewed nursing literature.",
            ),
            (
                "NOC Measurable Outcomes",
                "Patient outcomes follow the NOC framework with specific, measurable indicators and a target "
                "rating scale so evaluation criteria are clearly defined and assessable.",
            ),
        ]),
        _h("The Clinical Difference Between a Passing and a High-Scoring Care Plan"),
        _p(
            "<p>A passing care plan lists a nursing diagnosis and some interventions. A high-scoring care plan "
            "demonstrates clinical judgment: it explains why this diagnosis takes priority over others, why this "
            "goal is realistic for this patient within this timeframe, and why this intervention is supported by "
            "current evidence. That explanatory layer—the rationale—is what separates a 60% from an 85%.</p>"
            "<p>NurseMyGrade writers understand that distinction because they build care plans as part of their "
            "nursing practice, not just their academic writing. Your writer will rank diagnoses using the ABCs "
            "and Maslow framework, write goals that are patient-centered and time-bound (not generic), and pair "
            "every intervention with a cited rationale from journals your faculty recognises. The evaluation "
            "section will define specific NOC indicators and expected ratings, giving you a complete, defensible "
            "care plan document.</p>"
        ),
        _cl("NurseMyGrade Care Plan Quality Checklist", [
            ("NANDA-I approved nursing diagnoses with three-part diagnostic statement", "Problem + related to (etiology) + as evidenced by (defining characteristics)"),
            ("Diagnoses ranked by clinical priority using ABCs and Maslow hierarchy", ""),
            ("SMART short- and long-term goal statements for each diagnosis", "Specific, Measurable, Achievable, Relevant, Time-bound"),
            ("NIC nursing interventions for each goal with at least one rationale", "Rationale cited from peer-reviewed nursing literature"),
            ("NOC measurable outcome criteria with target indicators", ""),
            ("ADPIE format followed throughout (Assessment to Evaluation)", ""),
            ("APA 7th formatted reference list for all cited rationale", ""),
        ]),
        _faq_heading(),
        _faq("Which nursing diagnosis framework do you use?",
             "<p>NANDA-I approved diagnoses as standard, formatted with the three-part diagnostic statement. "
             "We also support facility-specific formats and alternative diagnostic taxonomies if your programme "
             "or clinical site uses them—specify in your order brief.</p>"),
        _faq("Can you complete a care plan for a specific patient scenario I provide?",
             "<p>Yes. Share the patient case details—primary diagnosis, comorbidities, relevant vitals, history, "
             "and any clinical context—and your writer builds the care plan around that specific clinical picture.</p>"),
        _faq("How many nursing diagnoses will the care plan include?",
             "<p>This depends on your assignment requirements. Most BSN care plans include 2–3 priority diagnoses. "
             "Specify how many diagnoses your rubric requires and your writer will include exactly that number, "
             "ranked by clinical priority.</p>"),
        _faq("Do you cover ADPIE format?",
             "<p>Yes. Assessment, Diagnosis, Planning, Implementation, and Evaluation are all structured within "
             "the care plan. Each section is clearly labelled and follows the format your faculty expects.</p>"),
        _faq("What is the difference between NIC and NOC?",
             "<p>NIC (Nursing Interventions Classification) is the standardised taxonomy of nursing interventions. "
             "NOC (Nursing Outcomes Classification) is the standardised taxonomy of patient outcomes. Your care "
             "plan uses NIC to classify what the nurse does and NOC to classify what the patient achieves.</p>"),
        _faq("Can you write a care plan for mental health, paediatric, or maternity patients?",
             "<p>Yes. All nursing specialities are covered. Our writer pool includes nurses with clinical "
             "experience in mental health, paediatrics, maternity, medical-surgical, critical care, and community "
             "nursing settings.</p>"),
        _faq("How quickly can you deliver a nursing care plan?",
             "<p>Most care plans are delivered within 24 hours. Rush delivery from 3 hours is available for "
             "single-diagnosis care plans. Complex multi-diagnosis care plans may require additional time.</p>"),
        _faq("What if I need the care plan in a specific table format?",
             "<p>Share your programme’s template or preferred format (table, column layout, narrative format) "
             "and your writer will structure the care plan accordingly. If your institution has a specific form, "
             "attach it to your order.</p>"),
    ],

    # ── 3. SOAP Note ─────────────────────────────────────────────────────────
    "nursing-soap-note-writing-help": [
        _stats(
            ("S/O/A/P", "all four sections"),
            ("ICD-10", "coding awareness"),
            ("3 hrs", "fastest turnaround"),
            ("NP-ready", "clinical accuracy"),
        ),
        _h("Why NP Students and Advanced Practice Nurses Choose NurseMyGrade for SOAP Notes"),
        _p(
            "<p>A SOAP note is a clinical document, not an academic essay. The Subjective section must capture "
            "the chief complaint, HPI, past medical history, family history, social history, and a relevant review "
            "of systems in the concise clinical language that attending physicians and supervising NPs expect to read. "
            "The Objective section requires accurate physical exam documentation. The Assessment must include "
            "differential diagnoses ranked by likelihood. The Plan must be evidence-based, specific, and actionable. "
            "Most students get the structure right. Very few get the clinical depth right.</p>"
            "<p>NurseMyGrade SOAP note writers include practicing Family Nurse Practitioners (FNPs) and Advanced "
            "Practice Registered Nurses (APRNs) who write SOAP documentation in actual clinical settings. When your "
            "FNP programme requires a SOAP note for a hypertensive patient encounter, your writer has managed "
            "hypertension in primary care and knows exactly which differentials to list, which labs to order in "
            "the Plan, and how to document the HPI in the clinically standard format.</p>"
        ),
        _hiw("How We Write Your SOAP Note", [
            (
                "Share Your Patient Scenario",
                "<p>Provide the chief complaint, patient demographics, any vitals or clinical findings included "
                "in your assignment, and your course or clinical site requirements. The more clinical detail "
                "you share, the more accurate the SOAP note will be.</p>",
            ),
            (
                "Matched to a Clinically Experienced Writer",
                "<p>Your note is assigned to a writer with FNP or APRN experience in the relevant clinical "
                "area—primary care, acute care, or specialty. They review the scenario before writing "
                "the Subjective section.</p>",
            ),
            (
                "Full Four-Section Documentation",
                "<p>S: chief complaint, HPI, PMH, FH, SH, ROS. O: vital signs, physical exam findings. "
                "A: primary assessment with differential diagnoses. P: medications, labs, referrals, follow-up, "
                "and patient education—all documented to clinical standard.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your SOAP Note Includes", [
            (
                "Complete Subjective Section",
                "Chief complaint and HPI using the OLDCART framework. Past medical, surgical, family, and social "
                "history. Review of systems pertinent to the presenting complaint.",
            ),
            (
                "Clinically Accurate Assessment",
                "Primary assessment with ICD-10 code awareness. Differential diagnoses ranked by likelihood "
                "with supporting clinical evidence. Written by writers who produce assessments in clinical practice.",
            ),
            (
                "Evidence-Based Plan",
                "Medications with dose, route, and frequency. Diagnostic labs and imaging orders. Referrals, "
                "patient education, and follow-up timeline—all justified by current clinical guidelines.",
            ),
        ]),
        _h("The Difference Between a Textbook SOAP Note and a Clinical SOAP Note"),
        _p(
            "<p>Nursing programmes teach SOAP note structure. What they cannot fully replicate is the clinical "
            "judgment required to populate each section accurately. The Assessment section is where students most "
            "commonly lose marks: listing a single diagnosis without differentials, or listing differentials without "
            "ranking them by likelihood and providing supporting evidence for each. An FNP examiner reads the "
            "Assessment the way a supervising physician reads it—looking for clinical reasoning, not just "
            "a diagnosis name.</p>"
            "<p>The Plan section is equally challenging. Prescribing the correct medication at the correct dose "
            "for the correct duration, ordering the appropriate diagnostic workup, and scheduling the right "
            "follow-up interval—these decisions require clinical knowledge that textbooks outline but "
            "practice solidifies. Our FNP and APRN writers bring that practice knowledge to your SOAP note, "
            "producing a document that reads like it was written by someone who has seen the patient type "
            "before—because they have.</p>"
        ),
        _cl("NurseMyGrade SOAP Note Quality Checklist", [
            ("Chief complaint documented in the patient’s own words", ""),
            ("HPI follows OLDCART or similar structured framework", "Onset, Location, Duration, Characteristics, Aggravating/Alleviating, Radiation, Timing"),
            ("PMH, FH, SH, and ROS documented and pertinent", ""),
            ("Objective section includes vital signs and relevant physical exam findings", ""),
            ("Assessment includes primary diagnosis with ICD-10 and at least two differentials ranked by likelihood", ""),
            ("Plan includes medication (dose, route, frequency), labs, referrals, and follow-up", ""),
            ("Patient education documented in the Plan section", ""),
            ("Formatted to your course or clinical site requirements", ""),
        ]),
        _faq_heading(),
        _faq("Can you write SOAP notes for FNP programme cases?",
             "<p>Yes. Our writer pool includes practicing FNPs and APRNs who write SOAP documentation in "
             "primary care settings daily. FNP programme SOAP notes are one of our most requested assignment types.</p>"),
        _faq("Do you include the full HPI and ROS?",
             "<p>Yes. The Subjective section covers chief complaint (in patient’s words), HPI using OLDCART "
             "or your programme’s framework, past medical/surgical/family/social history, and review of "
             "systems as required by your case.</p>"),
        _faq("Can you match a specific patient scenario I provide?",
             "<p>Yes. Provide the chief complaint, patient demographics, any vitals or clinical findings in "
             "your assignment, and your writer builds a clinically realistic SOAP note around that specific scenario.</p>"),
        _faq("What format do you deliver SOAP notes in?",
             "<p>Standard SOAP format is delivered as a Word document. If your programme or clinical site uses "
             "a specific template, attach it and your writer will complete your template directly.</p>"),
        _faq("Do you write SBAR format as well?",
             "<p>Yes. SBAR (Situation, Background, Assessment, Recommendation), DAR (Data, Action, Response), "
             "and other clinical documentation formats are available. Specify your required format when ordering.</p>"),
        _faq("Will the Assessment include differential diagnoses?",
             "<p>Yes. The Assessment section includes the primary diagnosis with ICD-10 awareness and at least "
             "two differentials ranked by likelihood with brief supporting clinical rationale for each.</p>"),
        _faq("How fast can you deliver a SOAP note?",
             "<p>Same-day delivery is standard for most SOAP notes. Rush delivery from 3 hours is available "
             "for urgent deadlines. Complex multi-system cases may require more time.</p>"),
        _faq("Can you write SOAP notes for mental health NP programmes?",
             "<p>Yes. Psychiatric SOAP notes including mental status examination documentation, DSM-5 diagnostic "
             "criteria, psychotropic medication plans, and safety assessments are all covered by our PMHNP-experienced writers.</p>"),
    ],

    # ── 4. Nursing Capstone ──────────────────────────────────────────────────
    "nursing-capstone-project-writing-service": [
        _stats(
            ("PICOT", "question framework"),
            ("BSN–DNP", "all levels covered"),
            ("EBP models", "Iowa, ACE Star, PDSA"),
            ("14 days", "extended revision window"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Capstone Support"),
        _p(
            "<p>A nursing capstone project is the most demanding academic assignment in most BSN, MSN, and DNP "
            "programmes. It requires you to identify a clinical practice problem, formulate a researchable PICOT "
            "question, systematically search and critically appraise the nursing literature, develop an evidence-based "
            "implementation plan, and present your findings in a scholarly format your faculty committee can evaluate. "
            "This is not a long essay—it is a structured research project that unfolds across an entire semester.</p>"
            "<p>NurseMyGrade capstone writers hold MSN or DNP credentials and have completed capstone projects "
            "themselves. They understand the difference between a well-formed PICOT question and a vague clinical "
            "inquiry, between a systematic literature search and a convenient one, and between an evidence appraisal "
            "that uses validated tools and one that summarises abstracts. Whether you need support for the entire "
            "project from proposal to final submission or just for the chapter your committee has returned with "
            "feedback, your writer provides the scholarly depth your programme expects.</p>"
        ),
        _hiw("How We Support Your Nursing Capstone", [
            (
                "Define Your PICOT and Project Scope",
                "<p>Share your clinical practice problem, any feedback from your faculty advisor, and the EBP "
                "framework your programme uses. Your writer refines your PICOT question and outlines the project "
                "structure to match your programme’s capstone template.</p>",
            ),
            (
                "Systematic Literature Search and Appraisal",
                "<p>A structured database search (CINAHL, PubMed, Cochrane, MEDLINE) is conducted using your "
                "PICOT terms with clearly defined inclusion and exclusion criteria. Each included study is "
                "critically appraised using validated tools (CASP, JBI) and summarised in an evidence table.</p>",
            ),
            (
                "Implementation Plan and Evaluation Strategy",
                "<p>The practice change or quality improvement intervention is designed to fit your clinical "
                "setting, with barriers, facilitators, and stakeholders identified. An evaluation framework "
                "(PDSA, SMART outcomes) is built into the plan.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Capstone Project Includes", [
            (
                "PICOT Question Development",
                "A well-formed PICOT question that defines Population, Intervention, Comparison, Outcome, and Time. "
                "Reviewed against your faculty’s requirements before the literature search begins.",
            ),
            (
                "Evidence Appraisal with Validated Tools",
                "Each appraised study is evaluated using CASP checklists, JBI critical appraisal tools, or the "
                "GRADE framework. An evidence table summarises design, sample, findings, and level of evidence.",
            ),
            (
                "EBP Framework Applied",
                "ACE Star, Iowa Model, PDSA cycle, or the framework your programme specifies—applied "
                "structurally throughout the project, not just referenced in the introduction.",
            ),
        ]),
        _h("The Difference Between a BSN, MSN, and DNP Capstone"),
        _p(
            "<p>Each programme level sets a different standard for the capstone project. BSN capstones typically "
            "require a literature review and practice change proposal—demonstrating that the student can "
            "identify a clinical problem and find evidence to address it. MSN capstones require integration of "
            "nursing theory, advanced clinical reasoning, and a more rigorous evidence appraisal process. DNP "
            "scholarly projects require doctoral-level synthesis, a defined implementation plan, measurable "
            "outcomes, and IRB consideration.</p>"
            "<p>NurseMyGrade writers are matched to your programme level. A BSN capstone is not written with "
            "the same depth requirements as a DNP project, and a DNP project is not written with the same "
            "structural simplicity as a BSN literature review. Your writer understands the competency expectations "
            "at your level and calibrates every section—PICOT, literature review, evidence appraisal, "
            "implementation plan—to match what your committee will be looking for.</p>"
        ),
        _cl("NurseMyGrade Capstone Quality Checklist", [
            ("PICOT question clearly defines Population, Intervention, Comparison, Outcome, and Time", ""),
            ("Systematic literature search with defined inclusion and exclusion criteria", ""),
            ("Evidence appraised using validated tools (CASP, JBI, GRADE)", ""),
            ("Evidence table summarising study design, sample, findings, and level of evidence", ""),
            ("EBP framework applied structurally throughout (not just named)", "Iowa, ACE Star, PDSA, or framework specified by your programme"),
            ("Implementation plan includes barriers, facilitators, stakeholders, and timeline", ""),
            ("Evaluation framework with SMART outcomes defined", ""),
            ("APA 7th formatted throughout with complete reference list", ""),
        ]),
        _faq_heading(),
        _faq("Can you help with just the PICOT question and proposal?",
             "<p>Yes. We support individual sections—proposal, literature review, methodology, implementation "
             "plan—or the full capstone project from PICOT to final submission.</p>"),
        _faq("Which EBP frameworks do you use?",
             "<p>ACE Star Model, Iowa Model, PDSA cycle, Stetler Model, and others. We apply whichever framework "
             "your programme or faculty specifies. If your faculty has not specified one, your writer recommends "
             "the most appropriate framework for your clinical question.</p>"),
        _faq("Do you support DNP scholarly projects?",
             "<p>Yes. DNP scholarly projects including quality improvement initiatives, practice change proposals, "
             "evidence-based practice implementations, and program evaluations are all supported.</p>"),
        _faq("Can you incorporate my faculty advisor’s feedback?",
             "<p>Yes. Share your advisor’s written feedback or committee comments and your writer will "
             "revise the affected sections accordingly. This is one of the most common revision scenarios we handle.</p>"),
        _faq("What databases do you search for the literature review?",
             "<p>CINAHL, PubMed, Cochrane Library, MEDLINE, PsycINFO, and other databases relevant to your "
             "clinical topic. Search terms are documented for transparency and replication.</p>"),
        _faq("How do you handle IRB considerations for DNP projects?",
             "<p>Your writer identifies whether your project requires IRB review based on the intervention type "
             "and data collection method, and guides the IRB determination and exemption documentation sections "
             "of your proposal.</p>"),
        _faq("What is the revision window for capstone projects?",
             "<p>Extended 14-day revision window from delivery for most capstone projects. Additional revision "
             "time is available for larger doctoral projects on request.</p>"),
        _faq("Can you match the writing style of sections I have already written?",
             "<p>Yes. Share any sections you have already completed and your writer will match your academic "
             "voice and writing style throughout the project for consistency.</p>"),
    ],

    # ── 5. Nursing Research Paper ─────────────────────────────────────────────
    "best-online-nursing-research-paper-service": [
        _stats(
            ("CINAHL + PubMed", "primary databases"),
            ("APA / AMA", "any citation style"),
            ("6 hrs", "fastest turnaround"),
            ("BSN–DNP", "writer credentials"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Research Paper Help"),
        _p(
            "<p>A nursing research paper is graded on the quality of the evidence, not just the quality of the "
            "writing. Examiners look for a clearly stated research question or PICOT framework, a rigorous "
            "literature search from appropriate nursing and health databases, an accurate description of the "
            "methodology used in the studies you cite, and a synthesis that draws clinically relevant "
            "conclusions—not just a summary of what each paper found. Most students can write. Fewer can "
            "critically appraise quantitative and qualitative nursing research.</p>"
            "<p>NurseMyGrade research paper writers hold BSN, MSN, or DNP credentials and have produced research "
            "as part of their own academic programmes. They source from CINAHL, PubMed, the Cochrane Library, "
            "and nursing-specific journals. They understand the difference between a systematic review and a "
            "narrative review, between a level of evidence rating and a quality rating, and between a statistical "
            "result and a clinically significant finding. That methodological literacy is what makes the "
            "difference between a research paper that passes and one that scores in the 70s.</p>"
        ),
        _hiw("How We Write Your Nursing Research Paper", [
            (
                "Submit Your Brief and Research Question",
                "<p>Share your topic, research question or PICOT, required paper type (quantitative, qualitative, "
                "mixed methods, literature review), word count, deadline, and rubric. Include any required "
                "sources or databases your faculty specifies.</p>",
            ),
            (
                "Literature Search and Source Selection",
                "<p>Your writer conducts a structured search of CINAHL, PubMed, Cochrane, and relevant nursing "
                "databases. Sources are selected based on publication date (typically last 5 years unless seminal), "
                "study design, and relevance to your research question.</p>",
            ),
            (
                "Evidence-Based Writing",
                "<p>The paper is structured to your required format—IMRAD for empirical papers, thematic "
                "structure for literature reviews. Each claim is cited. Methodology sections describe the research "
                "design accurately. The discussion connects findings to nursing practice implications.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Research Paper Includes", [
            (
                "Current Peer-Reviewed Sources",
                "CINAHL, PubMed, Cochrane Library, PsycINFO, and nursing-specific journals. Most sources are "
                "within 5 years unless your topic requires seminal works. No grey literature without justification.",
            ),
            (
                "Methodological Accuracy",
                "Study designs are described correctly (RCT, cohort, systematic review, phenomenological, "
                "grounded theory). Statistical results are reported accurately. Level of evidence is cited "
                "where your rubric requires it.",
            ),
            (
                "Clinical Applicability Discussion",
                "The conclusion and discussion connect research findings to nursing practice implications. "
                "Your reader understands what the evidence means for clinical decision-making, not just what "
                "each study found.",
            ),
        ]),
        _h("Quantitative vs Qualitative Nursing Research Papers: What Your Writer Knows"),
        _p(
            "<p>Quantitative nursing research papers require accurate statistical literacy: understanding the "
            "difference between statistical significance (p-value) and clinical significance (effect size), "
            "describing randomisation and blinding correctly, and knowing when a systematic review or meta-analysis "
            "carries more weight than a single RCT. Your writer reports quantitative findings with the same "
            "precision that a research methods course teaches—because they have studied and applied those methods.</p>"
            "<p>Qualitative nursing research papers require a different kind of rigour: describing the "
            "epistemological approach (phenomenology, grounded theory, ethnography), explaining how themes were "
            "identified and how trustworthiness was established, and acknowledging the transferability limitations "
            "of qualitative findings. Most generalist writers describe qualitative research as if it just "
            "involves interviewing people. Our writers understand the methodological differences and write each "
            "type with appropriate precision.</p>"
        ),
        _cl("NurseMyGrade Research Paper Quality Checklist", [
            ("Research question or PICOT clearly stated in the introduction", ""),
            ("Literature search conducted in appropriate nursing and health databases", "CINAHL, PubMed, Cochrane, MEDLINE, or databases specified by your faculty"),
            ("Study designs and methodologies described accurately", "RCT, cohort, systematic review, phenomenological, grounded theory, etc."),
            ("Findings synthesised, not just summarised source by source", ""),
            ("Level of evidence cited where rubric requires it", ""),
            ("Discussion connects findings to nursing practice implications", ""),
            ("APA 7th or other required citation style applied consistently", ""),
            ("Reference list complete with DOIs where available", ""),
        ]),
        _faq_heading(),
        _faq("Can you write both quantitative and qualitative nursing research papers?",
             "<p>Yes. Quantitative, qualitative, and mixed-methods nursing research papers are all covered. "
             "Your writer has methodological experience with the design type your assignment requires.</p>"),
        _faq("What databases do your writers use?",
             "<p>CINAHL, PubMed, the Cochrane Library, MEDLINE, PsycINFO, and other nursing and health databases. "
             "The search is documented so your faculty can evaluate the search strategy.</p>"),
        _faq("Can I specify which sources to use?",
             "<p>Yes. Add required sources, textbooks, or specific journals to your order brief. Your writer "
             "incorporates them and supplements with additional peer-reviewed sources as needed.</p>"),
        _faq("Do you write systematic literature reviews?",
             "<p>Yes. Systematic reviews with defined search strategy, inclusion and exclusion criteria, evidence "
             "tables, and PRISMA flow diagram where required are all supported.</p>"),
        _faq("What citation styles do you use?",
             "<p>APA 7th edition as standard. AMA, MLA, Chicago/Turabian, Harvard, and Vancouver are also "
             "available. Specify your required style in your order brief.</p>"),
        _faq("Can you write a nursing research proposal?",
             "<p>Yes. Research proposals including background, PICOT or research question, methodology rationale, "
             "sample and setting description, and data collection plan are all supported.</p>"),
        _faq("How fast can you deliver a nursing research paper?",
             "<p>Short papers (5–7 pages) can be delivered in 6–12 hours. Longer papers (15+ pages) "
             "require 48–72 hours. Specify your deadline when ordering.</p>"),
        _faq("Do you include an annotated bibliography?",
             "<p>An annotated bibliography can be added to any research paper order at no additional cost. "
             "Each annotation summarises the source and evaluates its relevance to your research question.</p>"),
    ],

    # ── 6. Nursing Case Study ─────────────────────────────────────────────────
    "nursing-case-study-help": [
        _stats(
            ("ADPIE", "clinical reasoning structure"),
            ("NCSBN CJM", "clinical judgment model"),
            ("BSN–MSN", "writer credentials"),
            ("6 hrs", "fastest turnaround"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Case Study Help"),
        _p(
            "<p>Nursing case studies are designed to test clinical judgment, not just knowledge recall. "
            "You are given a patient scenario and expected to demonstrate that you can apply nursing theory and "
            "clinical reasoning to assess, diagnose, plan, implement, and evaluate care for a specific patient "
            "in a specific context. Examiners award high marks for clinical specificity—responses that "
            "address the details of the scenario—and deduct marks for generic interventions that could "
            "apply to any patient.</p>"
            "<p>NurseMyGrade case study writers are nurses who perform exactly this kind of clinical reasoning "
            "in their practice. When you share a patient scenario, your writer reads it as a clinician, not as "
            "a writer: identifying the priority nursing diagnoses, applying the appropriate clinical reasoning "
            "framework, selecting evidence-based interventions, and evaluating expected outcomes with the specificity "
            "your rubric requires. The result is a case study analysis that reads like it was written by someone "
            "who has cared for this type of patient—because they have.</p>"
        ),
        _hiw("How We Analyse Your Nursing Case Study", [
            (
                "Share Your Case Scenario and Rubric",
                "<p>Provide the full patient scenario, any specific questions or structured tasks your assignment "
                "requires, your rubric or marking criteria, and any clinical reasoning framework your programme "
                "expects you to apply.</p>",
            ),
            (
                "Clinical Assessment and Diagnosis",
                "<p>Your writer analyses the patient scenario clinically: identifying subjective and objective "
                "data, forming priority nursing diagnoses using NANDA-I taxonomy, and explaining the clinical "
                "rationale for diagnosis prioritisation using ABCs and clinical judgment frameworks.</p>",
            ),
            (
                "Evidence-Based Planning and Intervention",
                "<p>A patient-centred care plan is developed with SMART goals and NIC-aligned interventions, "
                "each with cited rationale from current nursing literature. Legal, ethical, and cultural "
                "considerations are integrated where your rubric requires them.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Case Study Analysis Includes", [
            (
                "Clinical Reasoning Framework Applied",
                "ADPIE, the NCSBN Clinical Judgment Measurement Model, Levett-Jones Clinical Reasoning Cycle, "
                "or the framework your programme specifies—applied to every stage of the analysis.",
            ),
            (
                "Legal, Ethical, and Cultural Considerations",
                "Patient autonomy, informed consent, culturally safe care, and mandatory reporting obligations "
                "are integrated where clinically relevant—not as a checkbox, but as part of the clinical "
                "reasoning.",
            ),
            (
                "Reflection Section Where Required",
                "Gibbs, Johns, or Driscoll reflective framework applied to the clinical scenario where your "
                "assignment requires a reflective component, structured to meet the exact requirements of "
                "your marking criteria.",
            ),
        ]),
        _h("The NCSBN Clinical Judgment Model and Why It Matters for Case Studies"),
        _p(
            "<p>The National Council of State Boards of Nursing (NCSBN) Clinical Judgment Measurement Model "
            "is now embedded in the NCLEX Next Generation format and increasingly present in nursing programme "
            "assessments. The model defines clinical judgment across six cognitive skills: recognise cues, "
            "analyse cues, prioritise hypotheses, generate solutions, take action, and evaluate outcomes. "
            "Case study assignments built around this model expect students to demonstrate each cognitive "
            "skill explicitly, not just describe what they would do.</p>"
            "<p>NurseMyGrade writers who work on case study assignments understand the NCSBN CJM framework "
            "and apply it when your rubric requires it. If your programme uses a different framework—the "
            "Levett-Jones Clinical Reasoning Cycle, the ADPIE process, or a facility-specific model—your "
            "writer applies that one instead. The framework is a tool for demonstrating clinical reasoning, and "
            "your writer chooses and applies the right tool for your specific assignment.</p>"
        ),
        _cl("NurseMyGrade Case Study Quality Checklist", [
            ("Patient scenario read clinically, not just summarised", "Subjective and objective data extracted and interpreted"),
            ("Priority nursing diagnoses identified using NANDA-I taxonomy", "Ranked by clinical priority with rationale"),
            ("Clinical reasoning framework applied explicitly", "ADPIE, NCSBN CJM, Levett-Jones, or framework specified by your programme"),
            ("SMART patient goals written for each priority diagnosis", "Specific, Measurable, Achievable, Relevant, Time-bound"),
            ("NIC-aligned interventions with cited evidence-based rationale", ""),
            ("Legal, ethical, and cultural considerations addressed", ""),
            ("Evaluation criteria defined using NOC outcomes where appropriate", ""),
            ("Reflection section included where required by rubric", "Gibbs, Johns, or Driscoll framework"),
        ]),
        _faq_heading(),
        _faq("Can you analyse a case study I have been given?",
             "<p>Yes. Share the case scenario, patient details, any specific questions or tasks, and your rubric. "
             "Your writer builds the complete analysis around the specific patient and scenario you provide.</p>"),
        _faq("Which clinical reasoning frameworks do you use?",
             "<p>ADPIE, NCSBN Clinical Judgment Measurement Model, Levett-Jones Clinical Reasoning Cycle, and "
             "others as required by your programme. Specify your framework in your brief.</p>"),
        _faq("Do you cover mental health nursing case studies?",
             "<p>Yes. Mental health, medical-surgical, paediatric, maternity, critical care, community health, "
             "and all other clinical areas are covered. Writer matching ensures the nurse assigned to your case "
             "has clinical experience in the relevant speciality area.</p>"),
        _faq("Can you include a reflection section?",
             "<p>Yes. Gibbs, Johns, Driscoll, or other reflective frameworks are added on request. Specify your "
             "required reflective model and the word count allocated to the reflection section.</p>"),
        _faq("Do you cover Next Generation NCLEX (NGN) case study formats?",
             "<p>Yes. NGN-style case studies requiring the NCSBN Clinical Judgment Measurement Model, clinical "
             "decision-making documentation, and matrix-style responses are supported.</p>"),
        _faq("Can you write a case study for a mental health patient with multiple comorbidities?",
             "<p>Yes. Complex cases with multiple nursing diagnoses and comorbidities are handled routinely. "
             "Priority diagnosis ranking and clinical reasoning for complexity is a core strength of our "
             "mental health nursing writers.</p>"),
        _faq("How quickly can you deliver a nursing case study?",
             "<p>Short case studies (1,000–2,000 words) can be delivered in 6–12 hours. Longer case "
             "study analyses (3,000–5,000 words) require 24–48 hours.</p>"),
        _faq("What if I need the case study formatted to my institution’s template?",
             "<p>Share your template or formatting guidelines and your writer will structure the case study "
             "analysis to match your institution’s requirements exactly.</p>"),
    ],

    # ── 7. Nursing Dissertation ───────────────────────────────────────────────
    "nursing-dissertation-writing-service": [
        _stats(
            ("DNP–PhD", "writer credentials"),
            ("21 days", "extended revision window"),
            ("PRISMA", "systematic review standard"),
            ("Chapter-by-chapter", "delivery available"),
        ),
        _h("Why MSN and DNP Students Choose NurseMyGrade for Dissertation Support"),
        _p(
            "<p>A nursing dissertation or doctoral scholarly project is the most sustained piece of academic "
            "work most nursing students will ever produce. It requires an original contribution to nursing "
            "knowledge, methodological rigour that can survive committee scrutiny, and scholarly writing that "
            "maintains doctoral-level precision across 60–200 pages. Most students who struggle with their "
            "dissertation do not struggle because they lack intelligence—they struggle because managing a "
            "dissertation alongside clinical practice, coursework, and professional responsibilities is genuinely "
            "difficult. And faculty feedback cycles, committee revisions, and IRB timelines add complexity that "
            "no course prepares you for.</p>"
            "<p>NurseMyGrade dissertation writers hold MSN, DNP, or PhD credentials and have completed doctoral-level "
            "nursing work themselves. They understand the committee dynamics, the IRB process, the chapter review "
            "cycles, and the difference between a concept paper that passes and one that the committee sends back "
            "three times. Whether you need support for a single chapter or the entire dissertation from proposal "
            "to defence, your writer brings doctoral-level nursing scholarship to every section.</p>"
        ),
        _hiw("How We Support Your Nursing Dissertation", [
            (
                "Initial Consultation and Scope Definition",
                "<p>Share your research question or practice problem, your programme’s dissertation "
                "template or guidelines, any faculty feedback you have received, and the specific chapters "
                "or sections you need support with. Your writer maps the scope before writing begins.</p>",
            ),
            (
                "Chapter-by-Chapter Writing with Review Cycles",
                "<p>Each chapter is delivered individually so you can review it and share faculty feedback "
                "before the next chapter begins. This chapter-by-chapter process mirrors the actual dissertation "
                "review cycle your programme uses.</p>",
            ),
            (
                "Faculty Feedback Integration",
                "<p>Share your committee’s written feedback or supervisor comments after each review. "
                "Your writer revises the affected sections, addresses each feedback point explicitly, and "
                "produces a tracked-changes version where your programme requires it.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Dissertation Support Includes", [
            (
                "All Chapter Types Covered",
                "Chapter 1 (Introduction), Chapter 2 (Literature Review), Chapter 3 (Methodology), "
                "Chapter 4 (Findings/Results), Chapter 5 (Discussion) and Appendices. Individual chapters "
                "or the complete dissertation.",
            ),
            (
                "PRISMA-Compliant Literature Reviews",
                "Systematic literature reviews with PRISMA flow diagram, documented search strategy, "
                "inclusion and exclusion criteria, evidence tables, and critical appraisal using validated "
                "tools (CASP, JBI, GRADE).",
            ),
            (
                "Methodology Design and Justification",
                "Qualitative, quantitative, and mixed-methods designs. Research paradigm, design rationale, "
                "sampling strategy, data collection instruments, and analysis plan—all written with "
                "doctoral-level methodological precision.",
            ),
        ]),
        _h("DNP Scholarly Projects vs MSN Theses: What Your Writer Understands"),
        _p(
            "<p>The DNP scholarly project is practice-focused: it identifies a clinical problem, implements "
            "an evidence-based intervention in a defined setting, and evaluates outcomes. The emphasis is on "
            "translational research—moving evidence into practice—rather than generating new knowledge. "
            "IRB considerations, stakeholder engagement, and implementation fidelity are central concerns. "
            "Your DNP writer understands this distinction and writes the project accordingly.</p>"
            "<p>The MSN thesis is more traditionally academic: it formulates a research question, conducts "
            "a literature review, and may involve original data collection or a secondary data analysis. "
            "The scholarly depth expectation is graduate-level synthesis and analysis. The PhD dissertation "
            "sits at the highest standard, requiring an original contribution to nursing knowledge with "
            "full methodological rigour and a findings chapter that can withstand peer review. "
            "NurseMyGrade matches your writer to your degree level and programme type, not just your subject area.</p>"
        ),
        _cl("NurseMyGrade Dissertation Quality Checklist", [
            ("Research question or practice problem clearly defined in Chapter 1", ""),
            ("PICOT or research question operationalised with conceptual/theoretical framework identified", ""),
            ("Literature review uses systematic search strategy with documented inclusion and exclusion criteria", ""),
            ("Studies critically appraised using validated tools (CASP, JBI, GRADE)", ""),
            ("Methodology chapter justifies research paradigm, design, sample, and data collection approach", ""),
            ("DNP project includes implementation plan, stakeholder analysis, and IRB determination", ""),
            ("Chapter 5 discussion connects findings to nursing practice implications", ""),
            ("APA 7th formatted throughout with PRISMA flow diagram where required", ""),
        ]),
        _faq_heading(),
        _faq("Can you help with just one chapter?",
             "<p>Yes. Individual chapters—literature review, methodology, findings, discussion, or any "
             "single section—are supported. You do not need to order the full dissertation.</p>"),
        _faq("Do you support DNP scholarly projects?",
             "<p>Yes. Quality improvement projects, practice change proposals, evidence-based implementation "
             "projects, and program evaluations at doctoral level are all supported by our DNP-credentialed writers.</p>"),
        _faq("Can you write a PRISMA-compliant systematic review?",
             "<p>Yes. PRISMA flow diagram, documented search strategy, inclusion and exclusion criteria, "
             "evidence tables with level of evidence ratings, and narrative synthesis are all included.</p>"),
        _faq("What is the revision window for dissertations?",
             "<p>Extended 21-day revision window from delivery. Additional revision time is available for "
             "larger doctoral projects on request. Committee-initiated revisions are also supported.</p>"),
        _faq("Can you incorporate supervisor or committee feedback?",
             "<p>Yes. Share your committee’s written feedback or supervisor comments. Your writer revises "
             "the affected sections, addresses each point explicitly, and returns a revised document.</p>"),
        _faq("How do you handle IRB considerations?",
             "<p>Your writer identifies whether your project requires IRB review or qualifies for exemption, "
             "documents the rationale, and drafts the IRB determination or exemption request if your programme "
             "requires formal submission.</p>"),
        _faq("Can you write the methodology chapter for a qualitative dissertation?",
             "<p>Yes. Phenomenology, grounded theory, ethnography, narrative inquiry, and case study methodology "
             "chapters are all supported. Research paradigm, design rationale, sampling, data collection, "
             "and trustworthiness criteria are written with doctoral-level methodological precision.</p>"),
        _faq("Do you write the defence presentation as well?",
             "<p>Yes. A PowerPoint presentation for the dissertation or DNP project defence can be created "
             "alongside the written document. Speaker notes timed to your defence slot are included.</p>"),
    ],

    # ── 8. Concept Map ───────────────────────────────────────────────────────
    "concept-map-writing-services": [
        _stats(
            ("Pathophysiology→Diagnosis", "clinical linkage"),
            ("BSN–MSN", "writer credentials"),
            ("3 hrs", "fastest turnaround"),
            ("All formats", "Word, PDF, PPT"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Concept Map Help"),
        _p(
            "<p>A nursing concept map is not a mind map. It is a structured clinical thinking tool that maps "
            "the relationships between a patient’s pathophysiology, their nursing diagnoses, the evidence-based "
            "interventions selected for each diagnosis, and the expected outcomes of those interventions. The "
            "connections between nodes are what your faculty evaluates—a concept map where the links are "
            "generic or incorrect loses marks even if the individual nodes are accurately named.</p>"
            "<p>NurseMyGrade concept map writers understand the clinical reasoning that underpins accurate "
            "concept mapping. When you provide a patient scenario for a patient with heart failure and chronic "
            "kidney disease, your writer maps the pathophysiological relationships between fluid overload, "
            "decreased cardiac output, and impaired renal perfusion—and connects those relationships to "
            "the priority NANDA-I diagnoses, ranked NIC interventions, and measurable NOC outcomes. Every "
            "connection on the map is clinically justified, not just visually arranged.</p>"
        ),
        _hiw("How We Build Your Nursing Concept Map", [
            (
                "Share Your Patient Scenario or Topic",
                "<p>Provide the primary diagnosis, any comorbidities, relevant clinical data, and your "
                "programme’s preferred concept map format. Include your rubric if specific components "
                "are required.</p>",
            ),
            (
                "Pathophysiology and Diagnosis Mapping",
                "<p>Your writer maps the pathophysiological processes relevant to the patient’s diagnosis, "
                "identifies priority NANDA-I nursing diagnoses, and establishes the clinical links between "
                "pathophysiology and each nursing diagnosis.</p>",
            ),
            (
                "Interventions, Outcomes, and Rationale",
                "<p>Evidence-based NIC interventions are mapped to each nursing diagnosis with cited rationale. "
                "NOC measurable outcomes are added. A written rationale document explains each connection "
                "for programmes that require written justification.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Concept Map Includes", [
            (
                "Pathophysiology to Diagnosis Linkage",
                "Disease processes connected to their clinical manifestations, and clinical manifestations "
                "connected to the NANDA-I nursing diagnoses they support. Relationships labelled and directed.",
            ),
            (
                "Priority Nursing Diagnoses Ranked",
                "Diagnoses ranked by clinical priority using ABCs and Maslow hierarchy, with each diagnosis "
                "connected to its defining characteristics from the patient scenario.",
            ),
            (
                "Written Rationale Where Required",
                "A written rationale document explaining each concept map link and intervention selection, "
                "formatted to your programme’s requirements for programmes that assess written justification "
                "separately.",
            ),
        ]),
        _h("Medication Concept Maps and Pharmacology Concept Maps"),
        _p(
            "<p>Many ADN and BSN programmes require pharmacology concept maps as a separate assignment from "
            "patient care concept maps. A medication concept map maps the drug class, mechanism of action, "
            "therapeutic indications, contraindications, adverse effects, nursing considerations (monitoring "
            "parameters, patient education, administration precautions), and drug interactions for one or more "
            "medications. This is a high-density information assignment that requires accurate pharmacological "
            "knowledge, not just the ability to fill in boxes.</p>"
            "<p>NurseMyGrade concept map writers draw on current pharmacological references—including the "
            "Davis Drug Guide for Nurses and clinical pharmacology databases—to ensure medication concept "
            "maps contain accurate, complete, and clinically current information. If your pharmacology concept "
            "map covers a high-alert medication (anticoagulants, insulin, digoxin), your writer includes the "
            "specific monitoring parameters and safety considerations that your faculty expects to see documented.</p>"
        ),
        _cl("NurseMyGrade Concept Map Quality Checklist", [
            ("Pathophysiology nodes accurately represent disease process", ""),
            ("Clinical manifestations (signs and symptoms) linked to pathophysiology with directed relationships", ""),
            ("NANDA-I nursing diagnoses correctly formatted with three-part statement where required", ""),
            ("Diagnoses ranked by clinical priority with rationale", "ABCs and Maslow hierarchy"),
            ("NIC interventions mapped to each diagnosis with cited evidence", ""),
            ("NOC measurable outcomes defined for each diagnosis", ""),
            ("Written rationale document included where required by rubric", ""),
            ("Format matches your programme’s requirements (table, diagram, or hybrid)", ""),
        ]),
        _faq_heading(),
        _faq("What format do you deliver concept maps in?",
             "<p>Word document (table or diagram format), PDF, or PowerPoint slide—specify your programme’s "
             "preference when ordering. If your programme uses a specific template, attach it and we will "
             "complete your template.</p>"),
        _faq("Can you build a concept map for a specific patient diagnosis?",
             "<p>Yes. Provide the primary diagnosis and any comorbidities. Your writer builds the full concept "
             "map from pathophysiology through nursing diagnoses, interventions, and outcomes for that specific "
             "clinical picture.</p>"),
        _faq("Do you cover pharmacology or medication concept maps?",
             "<p>Yes. Pharmacology concept maps linking drug class, mechanism of action, indications, "
             "contraindications, adverse effects, and nursing considerations are a common request. "
             "High-alert medications receive specific safety coverage.</p>"),
        _faq("Can you include a written rationale for each link?",
             "<p>Yes. A written rationale document explaining each concept map connection and intervention "
             "selection is included for programmes that assess written justification separately from the map.</p>"),
        _faq("How fast can you deliver a concept map?",
             "<p>Most concept maps are delivered within 24 hours. Rush delivery from 3 hours is available "
             "for single-diagnosis concept maps. Complex multi-diagnosis or multi-medication maps require "
             "more time.</p>"),
        _faq("Can you create concept maps for mental health diagnoses?",
             "<p>Yes. Mental health concept maps covering psychiatric diagnoses, DSM-5 criteria, "
             "psychopharmacology, therapeutic communication interventions, and safety planning are "
             "all supported by our mental health nursing writers.</p>"),
        _faq("Do you handle multi-system concept maps with multiple comorbidities?",
             "<p>Yes. Complex patients with heart failure and CKD, COPD and diabetes, or other comorbidity "
             "combinations are handled. Your writer maps the pathophysiological interactions between conditions "
             "and prioritises diagnoses accordingly.</p>"),
        _faq("What if I need a concept map for a simulation lab case?",
             "<p>Yes. Simulation lab concept maps are common requests. Provide the simulation scenario details "
             "and your lab’s assessment criteria and your writer builds the map to those requirements.</p>"),
    ],

    # ── 9. Nursing Coursework ─────────────────────────────────────────────────
    "nursing-coursework-help-online": [
        _stats(
            ("Same writer", "for your entire module"),
            ("3 hrs", "fastest turnaround"),
            ("APA 7th", "formatting standard"),
            ("All nursing subjects", "covered"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Weekly Coursework Help"),
        _p(
            "<p>BSN and MSN nursing programmes produce a relentless volume of weekly coursework: discussion board "
            "posts, peer responses, reflective journals, pharmacology assignments, pathophysiology questions, "
            "module quizzes, and short papers—all alongside clinical hours that leave minimal time for desk "
            "work. The volume is not designed to be managed by studying alone. Students who perform consistently "
            "well in nursing programmes have usually developed systems for managing their academic workload "
            "alongside their clinical and personal commitments.</p>"
            "<p>NurseMyGrade weekly coursework support connects you with a single qualified nurse writer who "
            "works with you across multiple modules or an entire semester. Your writer develops familiarity with "
            "your programme, your academic voice, your faculty’s expectations, and the subject matter of "
            "your course—so each submission builds on the last rather than starting from zero. Consistency "
            "of voice, style, and clinical reasoning across your weekly submissions is something only a dedicated "
            "writer who knows your work can deliver.</p>"
        ),
        _hiw("How Weekly Coursework Support Works", [
            (
                "Onboard Your Writer",
                "<p>Share your course outline, syllabus, your LMS login details if needed, and any specific "
                "faculty expectations or style preferences. Your writer reviews the full module before "
                "your first assignment begins.</p>",
            ),
            (
                "Submit Each Assignment as It Comes",
                "<p>Share the week’s discussion prompt, assignment brief, or assessment task with your "
                "deadline. Your writer completes it to your rubric, using evidence-based content and the "
                "appropriate citation format.</p>",
            ),
            (
                "Consistent Voice and Academic Quality",
                "<p>Because the same writer handles every submission, your academic voice stays consistent "
                "across the module. Your writer learns your course content and builds on previous submissions "
                "where the module is cumulative.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Weekly Coursework Support Covers", [
            (
                "Discussion Posts and Peer Responses",
                "Initial discussion board posts and peer response posts, formatted to your LMS requirements. "
                "Evidence-based content, APA 7th citations, and the word count your faculty specifies.",
            ),
            (
                "Pharmacology and Pathophysiology Assignments",
                "Drug classification, mechanism of action, nursing considerations, dosage calculations, "
                "disease process descriptions, clinical manifestations, and nursing management questions.",
            ),
            (
                "Reflective Practice Journals",
                "Gibbs, Johns, Driscoll, and ERA cycle reflective frameworks applied to your clinical "
                "experiences or course learning objectives, written to the length and format your module requires.",
            ),
        ]),
        _h("Discussion Board Posts That Earn Full Marks"),
        _p(
            "<p>Nursing discussion board posts are deceptively difficult to do well. The prompt is often open-ended, "
            "the word count is short (150–300 words), and the marking criteria reward clinical specificity "
            "and integration of course content—not just a general response that engages with the topic. "
            "Faculty who mark fifty responses in a week recognise the difference between a post that was "
            "genuinely thought about and one that restated the prompt in different words.</p>"
            "<p>NurseMyGrade discussion posts are written by nurses who understand the clinical content of your "
            "module. If your week 3 discussion asks about the nurse’s role in pain management using the "
            "multimodal analgesia approach, your writer addresses the specific pharmacological and non-pharmacological "
            "strategies that current evidence supports—with a peer-reviewed citation in APA 7th. If a peer "
            "response is required, it engages substantively with the original post, builds on it, and meets the "
            "word and citation requirements your faculty sets.</p>"
        ),
        _cl("NurseMyGrade Weekly Coursework Quality Checklist", [
            ("Discussion post addresses the specific prompt, not just the general topic", ""),
            ("Current peer-reviewed nursing sources cited (within 5 years where possible)", ""),
            ("APA 7th in-text citation and reference list included where required", ""),
            ("Word count meets or is within 10% of your module’s requirement", ""),
            ("Peer responses engage substantively with the original post", ""),
            ("Pharmacology assignments include dose, route, mechanism, and nursing considerations", ""),
            ("Reflective journal follows the specified reflective framework structurally", ""),
            ("Academic voice is consistent across submissions within the module", ""),
        ]),
        _faq_heading(),
        _faq("Can I use the same writer for all my module assignments?",
             "<p>Yes. We strongly recommend requesting the same writer for ongoing coursework so they build "
             "familiarity with your subject, your academic voice, and your faculty’s expectations "
             "across the module.</p>"),
        _faq("Do you write discussion board posts and peer responses?",
             "<p>Yes. Initial discussion posts and peer response posts are written to your LMS requirements "
             "and your module’s word count and citation specifications.</p>"),
        _faq("Can you help with pharmacology calculations and drug cards?",
             "<p>Yes. Dosage calculations, drug classification, mechanism of action, adverse effects, "
             "contraindications, and nursing considerations are all covered by our nursing coursework writers.</p>"),
        _faq("What reflective models do you use?",
             "<p>Gibbs, Johns, Driscoll, and the ERA cycle. Specify your module’s preferred reflective "
             "model and your writer applies it structurally throughout the journal entry.</p>"),
        _faq("Do you work with Canvas, Blackboard, and Moodle?",
             "<p>Yes. All major LMS platforms are supported. If your coursework involves submitting directly "
             "to your LMS, share your login details securely and your writer will handle submissions.</p>"),
        _faq("Can you write reflective journals about my clinical placements?",
             "<p>Yes. Share the clinical experience you want to reflect on (protecting patient confidentiality "
             "by removing identifying details) and your writer applies the specified reflective framework to "
             "produce a structured, academically appropriate journal entry.</p>"),
        _faq("How fast can you complete a weekly discussion post?",
             "<p>Short discussion posts (150–300 words) can be completed in 3–6 hours. Longer weekly "
             "assignments require more time depending on complexity and word count.</p>"),
        _faq("Can you handle entire nursing modules, not just individual assignments?",
             "<p>Yes. Full module management—including all weekly submissions, discussions, assignments, "
             "and assessments for a single module or multiple modules—is available through our online "
             "class help service.</p>"),
    ],

    # ── 10. Online Nursing Class ──────────────────────────────────────────────
    "nursing-class-help-online": [
        _stats(
            ("Full course", "or individual modules"),
            ("Canvas + Blackboard", "all LMS platforms"),
            ("BSN–MSN", "qualified nurse assigned"),
            ("Grade-focused", "rubric-driven approach"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Online Class Help"),
        _p(
            "<p>Managing multiple online nursing courses simultaneously while completing clinical rotations "
            "is a logistics problem that nursing programmes design without fully accounting for. A typical "
            "semester might include a pathophysiology module with weekly quizzes, a nursing theory course "
            "with daily discussion board requirements, a pharmacology module with timed assessments, and "
            "forty or more clinical hours—all overlapping. Students who are failing behind are often "
            "failing not because they lack the ability to pass, but because they do not have enough hours "
            "in the week to complete everything to an acceptable standard.</p>"
            "<p>NurseMyGrade online class help assigns a dedicated, qualified nurse to manage one or more "
            "of your online nursing courses. Your assigned nurse holds BSN or MSN credentials in the relevant "
            "subject area and approaches every submission with the grade criteria your faculty publishes. "
            "Discussions, quizzes, assignments, and exams are completed on time, to rubric, and with the "
            "clinical accuracy that nursing faculty expects from a practising nurse.</p>"
        ),
        _hiw("How Online Class Help Works", [
            (
                "Share Your Course Access",
                "<p>Share your LMS login details securely. Your assigned nurse reviews your entire course "
                "outline, all current and upcoming assignments, quiz schedules, and any faculty announcements "
                "before any submissions are made.</p>",
            ),
            (
                "Nurse Assignment and Course Review",
                "<p>A qualified nurse with subject-matter expertise in your course content is assigned. "
                "They review the syllabus, rubrics, and grading criteria before touching any submission. "
                "You receive a progress overview within 24 hours of assignment.</p>",
            ),
            (
                "All Weekly Submissions Handled",
                "<p>Discussion posts, peer responses, weekly assignments, module quizzes, and any graded "
                "activities are completed on time and to your rubric. Your nurse monitors the course for "
                "new posts, announcements, and instructor feedback.</p>",
            ),
            (
                "Progress Updates and Grade Reporting",
                "<p>You receive regular progress updates on submissions completed and grades received. "
                "If your instructor posts feedback, your nurse addresses it in subsequent submissions. "
                "All communication remains discreet and confidential.</p>",
            ),
        ]),
        _fg("What Online Class Help Covers", [
            (
                "All Nursing Subjects",
                "Pharmacology, pathophysiology, mental health nursing, community health, nursing theory, "
                "leadership, research methods, evidence-based practice, and all other nursing module types "
                "are covered by subject-specific nurse writers.",
            ),
            (
                "Timed Quizzes and Exams",
                "Unproctored timed quizzes and module exams completed within the allotted window. "
                "Your nurse is informed of the quiz schedule and available during the assessment window "
                "to complete timed assessments accurately.",
            ),
            (
                "Discussion Posts, Peer Responses, and Assignments",
                "All weekly participation requirements handled. Initial discussion posts, peer response "
                "posts, and weekly assignment submissions—all completed to your faculty’s "
                "grading rubric and posted on your behalf.",
            ),
        ]),
        _h("How We Ensure Grade Quality in Your Online Nursing Class"),
        _p(
            "<p>Every nursing course has a grading rubric. Your assigned nurse reads it before making any "
            "submission. For discussion boards, the rubric typically grades on: initial post substance "
            "and evidence, peer response engagement, word count, and citation format. Your nurse meets "
            "every criterion explicitly. For assignments, the rubric is followed point by point. For "
            "quizzes, the nurse applies their nursing knowledge accurately and within the time limit.</p>"
            "<p>Where your faculty posts feedback on a submission, your nurse adjusts subsequent submissions "
            "accordingly. Where an assignment receives a lower grade than expected, your nurse reviews the "
            "feedback and compensates in the next opportunity. The goal is not just to complete your course "
            "but to complete it with grades that reflect what a competent, practising nurse would achieve "
            "on the same assessments.</p>"
        ),
        _cl("NurseMyGrade Online Class Quality Checklist", [
            ("Assigned nurse holds BSN or MSN credentials relevant to your course subject", ""),
            ("Full course syllabus and rubrics reviewed before first submission", ""),
            ("All weekly deadlines tracked and submissions made on time", ""),
            ("Discussion posts meet word count, citation, and engagement requirements", ""),
            ("Timed quizzes completed within the assessment window", ""),
            ("Faculty feedback integrated into subsequent submissions", ""),
            ("Grade progress reported to you regularly", ""),
            ("All access credentials handled confidentially", ""),
        ]),
        _faq_heading(),
        _faq("Can you take over my entire online nursing course?",
             "<p>Yes. We handle all weekly submissions, discussions, quizzes, and assignments for one course "
             "or multiple courses simultaneously. Your assigned nurse manages the course from the current "
             "week through to the final assessment.</p>"),
        _faq("Which LMS platforms do you support?",
             "<p>Canvas, Blackboard, Moodle, Brightspace (D2L), and any other LMS your programme uses. "
             "Share your login details securely and your nurse accesses the course directly.</p>"),
        _faq("How do you ensure confidentiality?",
             "<p>All work is handled discreetly. We never share client information, never discuss client "
             "courses with third parties, and use secure communication throughout. Your login credentials "
             "are used only to access your course and are deleted after the engagement ends.</p>"),
        _faq("Can you handle timed quizzes and exams?",
             "<p>Yes. Share the quiz schedule and any constraints and your assigned nurse completes "
             "unproctored timed quizzes within the allotted window. For proctored exams, contact us "
             "to discuss your specific requirements.</p>"),
        _faq("What nursing subjects can you cover?",
             "<p>All nursing subjects: pharmacology, pathophysiology, nursing theory, mental health, "
             "community health, maternal-child nursing, critical care, nursing leadership, research "
             "methods, and evidence-based practice.</p>"),
        _faq("Can you start mid-semester?",
             "<p>Yes. We can take over a course at any point in the semester. Share your current grade "
             "standing and your nurse will review what has been submitted and calibrate the approach for "
             "the remaining assessments.</p>"),
        _faq("How do you handle instructor feedback on submissions?",
             "<p>When your instructor posts feedback on a submission, your nurse reviews it and adjusts "
             "subsequent submissions accordingly. You are notified of any feedback received.</p>"),
        _faq("What happens if a quiz question covers unfamiliar content?",
             "<p>Your assigned nurse is matched to your subject area and applies their clinical and "
             "academic knowledge to every quiz question. For speciality topics outside their primary "
             "area, they consult reference materials to ensure accurate responses.</p>"),
    ],

    # ── 11. Shadow Health ─────────────────────────────────────────────────────
    "shadow-health-help-online": [
        _stats(
            ("Tina, Brian, Danny+", "all patients covered"),
            ("Same-day", "standard completion"),
            ("3 hrs", "rush available"),
            ("Practicing nurses", "complete your DCEs"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Shadow Health DCE Help"),
        _p(
            "<p>Shadow Health Digital Clinical Experiences are time-intensive clinical simulation assignments "
            "that require nursing students to conduct a complete patient interview, perform a physical examination, "
            "document clinical findings, write a SOAP note or clinical summary, complete an education section, "
            "and submit a reflection—all within a single digital encounter. For a single Tina Jones "
            "Comprehensive Assessment, this process can take 4–6 hours if you are completing it carefully "
            "and accurately. For students managing multiple DCEs alongside clinical hours, coursework, and "
            "family responsibilities, this is simply not feasible every week.</p>"
            "<p>NurseMyGrade assigns Shadow Health DCE completion to practicing nurses who are familiar with "
            "the Shadow Health platform and its scoring criteria. They know which interview questions produce "
            "high assessment scores, how to document physical exam findings accurately, what the education "
            "section expects in terms of patient teaching documentation, and how to write the reflection "
            "sections in a way that meets your programme’s passing threshold.</p>"
        ),
        _hiw("How Shadow Health DCE Completion Works", [
            (
                "Share Your Login and DCE Details",
                "<p>Provide your Shadow Health credentials securely and specify which Digital Clinical "
                "Experience needs to be completed: Tina Jones, Brian Foster, Danny Rivera, or any other "
                "patient case. Share your programme’s passing threshold if known.</p>",
            ),
            (
                "Expert Nurse Logs In and Completes the DCE",
                "<p>A practicing nurse with Shadow Health experience accesses your account and completes "
                "the patient encounter from start to finish: interview, physical examination, SOAP or "
                "clinical summary documentation, education section, and reflection.</p>",
            ),
            (
                "Review and Access Recovery",
                "<p>The completed DCE is submitted. You are notified immediately. Change your Shadow Health "
                "password as soon as the DCE is done. We do not retain your credentials after completion.</p>",
            ),
            (
                "Follow-Up Support",
                "<p>If any section of the completed DCE requires revision within your platform’s "
                "revision window, contact us and your nurse will address it. If your programme has "
                "follow-up questions about the documentation, we provide support.</p>",
            ),
        ]),
        _fg("What Your Shadow Health DCE Completion Includes", [
            (
                "All DCE Sections Completed",
                "Patient interview (subjective history), physical exam documentation (objective), "
                "clinical assessment and reasoning (assessment), plan of care and patient education (plan), "
                "plus reflection and self-evaluation sections.",
            ),
            (
                "Scored to Your Passing Threshold",
                "Shadow Health scores each section. Your nurse is familiar with the scoring criteria "
                "and completes each section to a standard that meets or exceeds your programme’s "
                "required passing score.",
            ),
            (
                "All Patient Cases Covered",
                "Tina Jones (Comprehensive, Focused, Complex), Brian Foster, Danny Rivera, Esther Park, "
                "Alex Reyes, and all other Shadow Health patient encounters across every clinical speciality.",
            ),
        ]),
        _h("Shadow Health DCE Sections: What Your Nurse Completes"),
        _p(
            "<p>The Shadow Health Comprehensive Health Assessment with Tina Jones covers: health history "
            "(chief complaint, history of present illness, past medical history, family history, social "
            "history, review of systems), physical examination (vital signs, general survey, head-to-toe "
            "assessment), nursing diagnosis and priority setting, care plan with interventions and rationale, "
            "patient education documentation, and a scored reflection on clinical performance. Each section "
            "contributes to your overall encounter score.</p>"
            "<p>The Focused Assessment DCEs for specific body systems—cardiovascular, respiratory, "
            "neurological, musculoskeletal, and others—require the same documentation structure applied "
            "to a narrower clinical scope. Your nurse selects the appropriate interview questions and "
            "examination techniques for the specific body system being assessed, documents findings accurately, "
            "and completes the SBAR or clinical note in the format Shadow Health requires for that "
            "specific case type.</p>"
        ),
        _cl("NurseMyGrade Shadow Health DCE Checklist", [
            ("Subjective history complete: CC, HPI, PMH, FH, SH, ROS", ""),
            ("Physical exam findings documented accurately for all required body systems", ""),
            ("Assessment includes priority nursing diagnoses with clinical rationale", ""),
            ("Patient education section completed with appropriate health teaching content", ""),
            ("Reflection section completed to your programme’s scoring standard", ""),
            ("Overall encounter score meets your programme’s passing threshold", ""),
            ("Completed within your assignment deadline", ""),
        ]),
        _faq_heading(),
        _faq("Which Shadow Health patients do you cover?",
             "<p>All Shadow Health patients: Tina Jones, Brian Foster, Danny Rivera, Esther Park, Alex Reyes, "
             "and all other DCE cases across every clinical speciality. Specify which patient and encounter "
             "type when ordering.</p>"),
        _faq("Do you complete the reflection and education sections?",
             "<p>Yes. All DCE sections are completed: health history, physical exam, assessment, care plan, "
             "patient education, and reflection. The reflection section is written to meet your programme’s "
             "scoring criteria.</p>"),
        _faq("How do you access my Shadow Health account?",
             "<p>You share temporary credentials securely. We complete the DCE and notify you immediately. "
             "Change your password as soon as the encounter is submitted—we do not retain credentials.</p>"),
        _faq("How fast can you complete a Shadow Health DCE?",
             "<p>Same-day completion is standard for most DCEs. Rush delivery within 3 hours is available "
             "for urgent deadlines. Contact us before ordering to confirm same-day availability.</p>"),
        _faq("What if my DCE score is below the passing threshold?",
             "<p>If your Shadow Health encounter score does not meet your programme’s passing threshold, "
             "contact us immediately. We will review the scoring report and address any sections that "
             "contributed to a low score.</p>"),
        _faq("Do you complete Tina Jones Comprehensive Health Assessment?",
             "<p>Yes. The Tina Jones Comprehensive Health Assessment is one of our most requested DCEs. "
             "Your nurse completes the full encounter including all body systems in the physical exam "
             "and all documentation sections.</p>"),
        _faq("Can you complete Shadow Health DCEs for speciality assessments?",
             "<p>Yes. Mental health, women’s health, paediatric, and other speciality Shadow Health "
             "assessments are all covered. Your nurse is matched to the clinical speciality of your DCE.</p>"),
        _faq("Is using this service confidential?",
             "<p>Yes. We never share client information. Your login credentials are used only to complete "
             "the DCE and deleted immediately after. All communication is handled discreetly.</p>"),
    ],

    # ── 12. iHuman ───────────────────────────────────────────────────────────
    "ihuman-help": [
        _stats(
            ("All iHuman cases", "every speciality"),
            ("Clinical reasoning", "differential diagnoses"),
            ("3 hrs", "fastest turnaround"),
            ("Practicing clinicians", "assigned to your case"),
        ),
        _h("Why Nursing and NP Students Choose NurseMyGrade for iHuman Case Help"),
        _p(
            "<p>iHuman virtual patient encounters require a level of clinical reasoning sophistication that "
            "goes well beyond filling in a template. Each case involves taking a complete patient history "
            "through a branching interview structure, selecting the appropriate physical examination maneuvers, "
            "generating a differential diagnosis list ranked by clinical probability, justifying each "
            "differential with clinical evidence from the encounter, ordering diagnostic tests, interpreting "
            "results, and formulating a management plan. The iHuman scoring algorithm evaluates not just "
            "whether you got the right diagnosis, but whether your clinical reasoning process was sound.</p>"
            "<p>NurseMyGrade assigns iHuman cases to nurses and nurse practitioners who perform clinical "
            "reasoning in their actual practice. They know how to navigate the iHuman interview structure "
            "to extract the most clinically relevant information, how to prioritise examination maneuvers "
            "based on the presenting complaint, and how to rank differentials in the way the iHuman "
            "scoring algorithm rewards—with evidence-based justification for each ranked hypothesis.</p>"
        ),
        _hiw("How iHuman Case Completion Works", [
            (
                "Share Your iHuman Access and Case Details",
                "<p>Provide your iHuman login credentials securely and specify the patient case to be "
                "completed. Share your course rubric or any scoring criteria your faculty has provided. "
                "Indicate your programme’s minimum required score if known.</p>",
            ),
            (
                "Clinician Logs In and Completes the Encounter",
                "<p>A nurse or nurse practitioner with iHuman experience accesses your account. They "
                "navigate the patient interview, select and perform the physical examination, generate "
                "the differential list, order diagnostics, interpret results, and formulate the "
                "management plan.</p>",
            ),
            (
                "Documentation Sections Completed",
                "<p>The clinical reasoning narrative, differential diagnoses with evidence-based "
                "justification, diagnostic interpretation, and management/follow-up plan are all "
                "documented to your course’s standard.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your iHuman Case Completion Includes", [
            (
                "Complete Patient Encounter",
                "Full history taking, physical examination, assessment documentation, and clinical "
                "reasoning narrative. Every section of the iHuman encounter is completed, not just "
                "the final diagnosis.",
            ),
            (
                "Ranked Differential Diagnoses",
                "Differentials ranked from most to least likely based on clinical evidence from the "
                "encounter. Each differential is supported with evidence-based justification—the "
                "specific finding that supports or argues against each hypothesis.",
            ),
            (
                "Management Plan and Follow-Up",
                "Evidence-based treatment plan with specific medications, diagnostics, patient education, "
                "referrals, and follow-up timeline. Written in the clinical documentation format "
                "iHuman requires for your case type.",
            ),
        ]),
        _h("How iHuman Scores Clinical Reasoning—and How We Meet That Standard"),
        _p(
            "<p>The iHuman scoring system evaluates three core dimensions: information gathering (did you ask "
            "the right questions and perform the right examination maneuvers?), clinical problem solving "
            "(did you generate the right differentials, order the right tests, and interpret them correctly?), "
            "and communication (did you document your clinical reasoning clearly?). Students who know the "
            "right diagnosis but cannot demonstrate the reasoning process that leads to it lose significant "
            "marks on the problem-solving dimension.</p>"
            "<p>Our clinicians approach iHuman cases the way they approach real patient encounters: "
            "systematically, prioritising examination findings that will most differentiate between competing "
            "hypotheses, and documenting their reasoning explicitly. They have completed enough iHuman cases "
            "to understand the platform’s scoring priorities and the evidence threshold required for "
            "each differential. The result is not just a completed encounter—it is a completed encounter "
            "that scores where your programme requires it to score.</p>"
        ),
        _cl("NurseMyGrade iHuman Case Quality Checklist", [
            ("Complete patient history obtained using iHuman interview structure", ""),
            ("Physical examination maneuvers selected appropriately for presenting complaint", ""),
            ("Differential diagnoses ranked by clinical probability with evidence-based justification", ""),
            ("Diagnostic tests ordered and results interpreted accurately", ""),
            ("Clinical reasoning narrative clearly documented", ""),
            ("Management plan specific to diagnosis with medications, referrals, follow-up", ""),
            ("Patient education section completed where required", ""),
            ("Encounter score meets programme’s required minimum", ""),
        ]),
        _faq_heading(),
        _faq("Which iHuman cases do you cover?",
             "<p>All iHuman virtual patient cases across every speciality area: acute care, primary care, "
             "chronic disease management, paediatrics, women’s health, and mental health. Specify "
             "your case name and specialty when ordering.</p>"),
        _faq("Do you write the differential diagnoses and justifications?",
             "<p>Yes. Differentials are ranked by clinical probability with evidence-based clinical "
             "justification for each. The evidence comes from the patient encounter findings, not just "
             "from textbook knowledge.</p>"),
        _faq("How do you access my iHuman account?",
             "<p>You share temporary credentials securely. We complete the case and notify you immediately. "
             "Change your password as soon as the encounter is complete.</p>"),
        _faq("Can you help with iHuman assessment scoring?",
             "<p>Yes. Our clinicians are familiar with the iHuman scoring dimensions and aim to meet your "
             "programme’s required score on information gathering, clinical problem solving, and "
             "documentation.</p>"),
        _faq("How fast can you complete an iHuman case?",
             "<p>Same-day completion is standard for most iHuman cases. Rush delivery within 3 hours is "
             "available. Contact us before ordering to confirm same-day availability.</p>"),
        _faq("Do you handle iHuman cases for FNP programmes?",
             "<p>Yes. FNP programme iHuman cases, including primary care encounters, complex chronic disease "
             "management, and acute presentations, are commonly handled by our FNP and APRN writers.</p>"),
        _faq("What if the case requires a specific management plan format?",
             "<p>Share your course’s documentation requirements or any specific management plan format "
             "your faculty specifies. Your clinician will structure the plan accordingly.</p>"),
        _faq("Is my account information kept confidential?",
             "<p>Yes. Your login credentials are used only to complete the iHuman case and are not "
             "retained after completion. All engagement information is handled confidentially.</p>"),
    ],


    # ── 13. Buy Nursing Papers ────────────────────────────────────────────────
    "nursing-research-for-sale-online": [
        _stats(
            ("All paper types", "one service"),
            ("BSN–DNP", "writer credentials"),
            ("3 hrs", "fastest delivery"),
            ("Grade guarantee", "or money back"),
        ),
        _h("Why Students Buy Nursing Papers from NurseMyGrade"),
        _p(
            "<p>When nursing students buy papers online, the most common disappointment is receiving a "
            "paper that was clearly written by someone without nursing knowledge. Generic academic writers "
            "produce papers that use the right vocabulary and cite the right journals—but get the clinical "
            "detail wrong in ways that a nursing faculty member immediately recognises. A care plan that "
            "lists NANDA-I diagnoses without the three-part diagnostic statement, a SOAP note with a "
            "Plan section that omits follow-up documentation, a research paper that mischaracterises a "
            "qualitative study as quantitative—these are the errors that produce marks in the 50s.</p>"
            "<p>NurseMyGrade connects you with BSN, MSN, and DNP writers who have produced the same types "
            "of nursing papers you need as part of their own clinical education. They understand the "
            "marking rubrics, the clinical frameworks, and the institutional expectations that shape "
            "nursing faculty grading. Every paper is written from scratch to your specific brief and "
            "backed by a grade or money-back guarantee.</p>"
        ),
        _hiw("How to Buy a Nursing Paper from NurseMyGrade", [
            (
                "Submit Your Order Brief",
                "<p>Specify the paper type (essay, care plan, SOAP note, research paper, capstone, "
                "or any other), topic, word count, academic level, deadline, and rubric. The more "
                "specific your brief, the more targeted your writer's work will be.</p>",
            ),
            (
                "Writer Matching and Review",
                "<p>A BSN, MSN, or DNP writer with relevant clinical and academic experience is "
                "matched to your order. They review your brief and rubric before writing begins "
                "and confirm that they can meet your requirements.</p>",
            ),
            (
                "Original Paper Written to Your Brief",
                "<p>Your paper is written from scratch, never recycled from previous orders. "
                "Current peer-reviewed nursing literature is sourced. APA 7th edition formatting "
                "is applied. A free Turnitin plagiarism report is produced before delivery.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Every NurseMyGrade Paper Includes", [
            (
                "Written by Credentialed Nurses",
                "BSN minimum. MSN and DNP writers available for graduate and doctoral-level papers. "
                "Every writer is verified for nursing credentials before being allowed to accept orders.",
            ),
            (
                "Free Turnitin Plagiarism Report",
                "Every paper is checked for originality before delivery. The Turnitin report is included "
                "with your order at no extra charge. Papers are written from scratch, not repurposed.",
            ),
            (
                "Grade or Money-Back Guarantee",
                "Share your rubric and marking criteria. Your writer follows it precisely. If the paper "
                "does not meet your stated requirements after revision, you receive a full refund.",
            ),
        ]),
        _h("All Nursing Paper Types Available"),
        _p(
            "<p>NurseMyGrade covers every nursing paper type a BSN, MSN, or DNP programme produces. "
            "Nursing essays with EBP frameworks and APA 7th citations. Care plans with NANDA-I, NIC, "
            "and NOC frameworks and ADPIE structure. SOAP notes with complete S, O, A, and P sections "
            "written to clinical documentation standards. Research papers with systematic literature "
            "searches and methodological accuracy. Case study analyses with clinical reasoning frameworks. "
            "Capstone projects from PICOT through implementation plan. Dissertations chapter by chapter. "
            "Concept maps with pathophysiology linkages. Annotated bibliographies with critical evaluation. "
            "Presentations with speaker notes.</p>"
            "<p>Every paper type is handled by a writer who has produced that specific format as part "
            "of their own nursing education or practice. You are not ordering from a generic essay service "
            "that added nursing to its list of covered subjects—you are ordering from a platform built "
            "specifically for nursing students, staffed exclusively by nursing professionals.</p>"
        ),
        _cl("NurseMyGrade Paper Quality Checklist", [
            ("Paper type matches your assignment requirement exactly", "Essay, care plan, SOAP note, research paper, capstone, or other"),
            ("Writer holds credentials relevant to your paper's clinical content", ""),
            ("Rubric requirements followed point by point", ""),
            ("Current peer-reviewed nursing sources cited", "CINAHL, PubMed, Cochrane, nursing-specific journals"),
            ("APA 7th edition or required citation style applied consistently", ""),
            ("Free Turnitin plagiarism report included with delivery", ""),
            ("Grade or money-back guarantee applies to your order", ""),
        ]),
        _faq_heading(),
        _faq("What types of nursing papers can I buy?",
             "<p>Essays, care plans, SOAP notes, research papers, case studies, capstone projects, "
             "dissertations, concept maps, annotated bibliographies, presentations, and any other "
             "nursing paper type your programme requires.</p>"),
        _faq("Are the papers written from scratch?",
             "<p>Yes. Every paper is original, written to your specific brief, and never resold or reused. "
             "A free Turnitin plagiarism report is included with every order to confirm originality.</p>"),
        _faq("How do I know my paper will get a good grade?",
             "<p>Share your rubric and marking criteria. Your writer follows it precisely. We back every "
             "order with a grade or money-back guarantee. If the paper does not meet your stated requirements "
             "after revision, you receive a full refund.</p>"),
        _faq("Can I see the writer's credentials?",
             "<p>Yes. Writer profiles including credentials, clinical specialities, and academic backgrounds "
             "are available. You can request a specific credential level (BSN, MSN, or DNP) in your brief.</p>"),
        _faq("Will my paper contain AI-generated content?",
             "<p>No. All papers are written by human nursing professionals. We do not use AI writing "
             "tools. The paper you receive was written by a nurse, not generated by software.</p>"),
        _faq("Can I communicate with my writer?",
             "<p>Yes. Direct communication with your writer through our messaging system is available before, "
             "during, and after order completion. Share additional requirements or ask clinical questions directly.</p>"),
        _faq("How fast can I get a nursing paper?",
             "<p>Rush delivery from 3 hours is available for short papers. Most standard nursing papers "
             "(2,000–3,000 words) are delivered within 24–48 hours. Specify your deadline when ordering.</p>"),
        _faq("What if I am not satisfied with the paper?",
             "<p>Unlimited free revisions within the revision window. If your writer cannot meet your stated "
             "requirements after revision rounds, you receive a full refund. No conditions.</p>"),
    ],

    # ── 14. Nursing Report ────────────────────────────────────────────────────
    "nursing-report-writing-service": [
        _stats(
            ("SBAR + DAR", "all report formats"),
            ("BSN–MSN", "clinical documentation experience"),
            ("3 hrs", "fastest turnaround"),
            ("All report types", "incident to handover"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Report Writing Help"),
        _p(
            "<p>Clinical nursing reports are not essays. They are structured, functional documents that serve "
            "specific communication purposes in healthcare settings—and each type has conventions that differ "
            "meaningfully from academic writing. An incident report must be factual, non-inferential, and "
            "written in chronological sequence without attributing cause. An SBAR communication must be "
            "concise enough to deliver in 60–90 seconds but complete enough to prompt the receiving "
            "clinician to act. A patient progress note must document the nursing assessment and "
            "intervention in the format that the care team reads and the medical record requires.</p>"
            "<p>NurseMyGrade nursing report writers have produced these documents in clinical settings. "
            "They know what a charge nurse expects to read in a shift handover report, what information a "
            "risk manager requires in an incident report, and what an attending physician expects in an "
            "SBAR. That practical knowledge is what makes the difference between a report that fulfils "
            "its clinical communication purpose and one that gets the format right but the substance wrong.</p>"
        ),
        _hiw("How We Write Your Nursing Report", [
            (
                "Specify Report Type and Scenario",
                "<p>Provide the report type (incident report, SBAR, progress note, handover report, case "
                "report, or other), the clinical scenario details, and any specific format requirements "
                "your programme or institution uses.</p>",
            ),
            (
                "Matched to a Clinically Experienced Writer",
                "<p>A writer with clinical experience in the relevant report type and healthcare setting "
                "is assigned. Incident reports go to a writer experienced in quality and safety documentation; "
                "SBAR communications go to a writer experienced in acute care handovers.</p>",
            ),
            (
                "Report Written to Clinical Documentation Standards",
                "<p>Your report is written in the appropriate clinical language for the document type: "
                "factual and non-inferential for incident reports, concise and action-oriented for "
                "SBAR, structured and complete for progress notes and handovers.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("Nursing Report Types We Write", [
            (
                "Incident Reports and Near-Miss Documentation",
                "Factual, chronological incident reports that document what happened without inferring cause. "
                "Written in the objective clinical language that risk management and quality assurance "
                "departments require.",
            ),
            (
                "SBAR and Handover Communications",
                "SBAR (Situation, Background, Assessment, Recommendation) reports formatted for verbal or "
                "written handover. Shift handover summaries that give the incoming nurse the clinical "
                "picture they need to continue safe care.",
            ),
            (
                "Patient Progress Notes and Clinical Case Reports",
                "DAR (Data, Action, Response) and SOAP-format progress notes. Clinical case reports for "
                "academic submission documenting patient presentation, nursing care, and outcomes with "
                "appropriate clinical terminology.",
            ),
        ]),
        _h("What Nursing Faculty Look for in Clinical Report Assignments"),
        _p(
            "<p>When a nursing programme assigns a report-writing task, they are evaluating three things: "
            "clinical communication competency (can you identify and prioritise the information that "
            "matters?), documentation accuracy (is the clinical terminology correct?), and format "
            "adherence (does the report follow the conventions of the type?). Most marking rubrics "
            "award marks for each of these dimensions separately.</p>"
            "<p>The most common mark-losing errors in nursing report assignments are: including opinion or "
            "inference in an incident report (documented as fact), omitting the Assessment and Recommendation "
            "components in an SBAR (the most action-relevant parts), using vague non-clinical language "
            "in a progress note ('patient did not seem well' instead of 'patient reports 7/10 pain, "
            "BP 160/100, diaphoretic'), and failing to use the correct format template. "
            "NurseMyGrade writers avoid these errors because they have documented them correctly in "
            "actual clinical practice.</p>"
        ),
        _cl("NurseMyGrade Nursing Report Quality Checklist", [
            ("Report type correctly identified and formatted to its conventions", ""),
            ("Incident report: factual, chronological, non-inferential language throughout", ""),
            ("SBAR: all four components present (Situation, Background, Assessment, Recommendation)", ""),
            ("Progress note: clinical terminology accurate, patient status changes documented", ""),
            ("Handover report: incoming nurse has sufficient clinical picture to continue care safely", ""),
            ("Appropriate clinical terminology used throughout (not lay language)", ""),
            ("APA 7th formatted with references where academic submission requires it", ""),
        ]),
        _faq_heading(),
        _faq("What types of nursing reports do you write?",
             "<p>Incident reports, shift handover reports, patient progress notes, clinical case reports, "
             "SBAR communications, DAR notes, and academic clinical reports for portfolio or course submission.</p>"),
        _faq("Do you write reports for portfolio submissions?",
             "<p>Yes. Clinical portfolio entries, reflective reports, professional practice documentation, "
             "and competency evidence reports are all covered. Specify your portfolio's format requirements "
             "in your brief.</p>"),
        _faq("Can you write an SBAR for a simulation scenario?",
             "<p>Yes. Provide the patient scenario and your simulation case details and your writer "
             "produces a complete SBAR formatted to your programme's requirements.</p>"),
        _faq("Can you write an incident report for a hypothetical clinical scenario?",
             "<p>Yes. Academic incident report assignments based on a provided scenario are handled "
             "regularly. Your writer produces a factual, non-inferential report in the correct format.</p>"),
        _faq("How fast can you deliver a nursing report?",
             "<p>Most nursing reports are delivered within 24 hours. Rush delivery from 3 hours is "
             "available for short SBAR or progress note assignments.</p>"),
        _faq("Do you write clinical case reports for academic submission?",
             "<p>Yes. Clinical case reports documenting patient presentation, nursing assessment, "
             "interventions, and outcomes with current nursing literature citations and APA 7th "
             "formatting are a common request.</p>"),
        _faq("What format do you deliver nursing reports in?",
             "<p>Word document as standard. If your programme or clinical site uses a specific "
             "template form, attach it and your writer completes the form directly.</p>"),
        _faq("Can you write documentation for a patient deterioration scenario?",
             "<p>Yes. Documentation of patient deterioration including recognition of early warning signs, "
             "escalation procedures (SBAR to senior clinician), response actions, and outcome recording "
             "are all covered.</p>"),
    ],

    # ── 15. Nursing Presentation ──────────────────────────────────────────────
    "nursing-presentation-writing-service": [
        _stats(
            ("PPT + Google Slides", "formats covered"),
            ("Speaker notes", "timed to your slot"),
            ("BSN–DNP", "writer credentials"),
            ("6 hrs", "fastest turnaround"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Presentation Help"),
        _p(
            "<p>A nursing presentation does more than display information on slides. Whether it is a "
            "capstone project defence, a clinical rounds presentation, a journal club facilitation, "
            "or a seminar on evidence-based practice, the presentation must communicate clinical "
            "evidence clearly to an audience that will evaluate both the substance and the structure. "
            "Faculty who grade nursing presentations are looking for evidence of clinical reasoning, "
            "not just slide design competency. A visually polished presentation with weak clinical "
            "content scores lower than a plainly designed presentation with a well-constructed argument.</p>"
            "<p>NurseMyGrade presentation writers hold nursing credentials at BSN level or above and "
            "have built presentations for academic and professional clinical contexts. They know how to "
            "structure a capstone defence narrative from problem statement through evidence appraisal to "
            "implementation recommendation. They know the difference between a slide that summarises "
            "your argument and a slide that replaces it. And they write speaker notes that tell you "
            "what to say at each slide, timed to your allotted presentation slot, so your delivery "
            "is as strong as your content.</p>"
        ),
        _hiw("How We Build Your Nursing Presentation", [
            (
                "Share Your Brief and Content Requirements",
                "<p>Provide your presentation topic, slide count or time slot, academic level, target "
                "audience (faculty committee, clinical team, seminar group), and any rubric or scoring "
                "criteria. Include any written paper or report the presentation should be based on.</p>",
            ),
            (
                "Content Structure and Narrative Development",
                "<p>Your writer plans the presentation structure: problem statement, evidence review, "
                "clinical implications, recommendations, and conclusion—organised into a logical "
                "narrative that guides the audience from the clinical question to the answer.</p>",
            ),
            (
                "Slide Content and Speaker Notes",
                "<p>Each slide is populated with concise, evidence-based content. Speaker notes are "
                "written for every slide, timed to your slot (typically 1–2 slides per minute), "
                "with APA 7th cited evidence and clinical terminology your audience expects.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Your Nursing Presentation Includes", [
            (
                "Slide-by-Slide Content Development",
                "Problem statement, background, literature review summary, methodology (where applicable), "
                "findings, clinical implications, and recommendations—each occupying the appropriate "
                "number of slides for your time slot.",
            ),
            (
                "Speaker Notes for Every Slide",
                "Detailed speaker notes timed to your presentation slot, written to be spoken naturally "
                "rather than read. Notes cover what to say at each slide and how to transition "
                "between sections.",
            ),
            (
                "Evidence-Based Clinical Content",
                "Peer-reviewed nursing literature cited in APA 7th format on the reference slide "
                "and in speaker notes. Clinical statistics and evidence summarised accurately "
                "for a clinical audience.",
            ),
        ]),
        _h("Building a Capstone Defence Presentation That Passes Committee Scrutiny"),
        _p(
            "<p>A capstone or DNP project defence presentation is evaluated by a faculty committee that "
            "has read your written project. They are not evaluating whether you know the content—they "
            "already know you do. They are evaluating whether you can communicate your project's "
            "significance, your evidence appraisal process, your implementation rationale, and your "
            "outcome evaluation plan clearly and concisely within your allotted time. The most common "
            "committee feedback on defence presentations is that students spend too much time on "
            "background (which the committee already knows) and too little time on the clinical "
            "significance of their specific contribution.</p>"
            "<p>NurseMyGrade presentation writers who build capstone defence presentations calibrate "
            "the slide ratio accordingly: one or two slides on background, two to three slides on "
            "your literature review and evidence synthesis, two to three slides on your implementation "
            "plan, and one to two slides on your evaluation framework and expected outcomes. The "
            "clinical argument is the centrepiece, and the presentation structure reflects that.</p>"
        ),
        _cl("NurseMyGrade Presentation Quality Checklist", [
            ("Presentation structure matches presentation type (capstone defence, seminar, rounds, journal club)", ""),
            ("Slide count appropriate for the allotted time slot (1–2 slides per minute)", ""),
            ("Each slide contains one main point, not a paragraph", ""),
            ("Speaker notes timed to your presentation slot and written to be spoken naturally", ""),
            ("Evidence cited with APA 7th references on a dedicated reference slide", ""),
            ("Clinical terminology appropriate to your audience level", ""),
            ("Problem statement, evidence, implications, and recommendation all present", ""),
            ("Format delivered in PowerPoint (.pptx) or as specified", ""),
        ]),
        _faq_heading(),
        _faq("Do you write speaker notes as well as slides?",
             "<p>Yes. Speaker notes are included for every slide, timed to your allotted presentation "
             "slot. Notes are written to be spoken naturally, not read from a script.</p>"),
        _faq("Can you build a presentation for my capstone defence?",
             "<p>Yes. Capstone defence presentations are among our most common requests. Share your "
             "capstone paper and your defence time slot and your writer builds the presentation around it.</p>"),
        _faq("What software format do you deliver in?",
             "<p>PowerPoint (.pptx) as standard. Google Slides conversion is available on request. "
             "Specify your required format in your brief.</p>"),
        _faq("How many slides will the presentation be?",
             "<p>Typically 1–2 slides per minute of presentation time. For a 15-minute presentation, "
             "plan for 15–20 content slides plus a title and reference slide. Specify your time "
             "slot and we structure accordingly.</p>"),
        _faq("Can you build a journal club presentation?",
             "<p>Yes. Journal club presentations including article summary, methods appraisal, "
             "clinical implications, and facilitation questions are a standard request.</p>"),
        _faq("Can you include data visualisations and tables?",
             "<p>Yes. Summary tables, bar charts, and data visualisations are included where your "
             "content requires them. Clinical data is represented accurately and clearly.</p>"),
        _faq("Do you cover clinical rounds presentations?",
             "<p>Yes. Clinical case presentations for grand rounds, nursing rounds, and interdisciplinary "
             "team meetings—structured for a clinical audience with appropriate clinical terminology "
             "and evidence-based recommendations.</p>"),
        _faq("How fast can you deliver a nursing presentation?",
             "<p>Short presentations (10–15 slides) can be delivered in 6–12 hours. Longer "
             "capstone or seminar presentations require 24–48 hours depending on complexity.</p>"),
    ],

    # ── 16. BSN Writing ───────────────────────────────────────────────────────
    "reliable-and-cheap-bsn-writing-service": [
        _stats(
            ("All 4 years", "Year 1 to capstone"),
            ("BSN writers", "same programme experience"),
            ("APA 7th", "formatting standard"),
            ("3 hrs", "fastest turnaround"),
        ),
        _h("Why BSN Students Choose NurseMyGrade for Academic Writing Help"),
        _p(
            "<p>The BSN nursing curriculum is designed to be simultaneously demanding and cumulative. "
            "Year 1 foundations work introduces the nursing process, therapeutic communication, and "
            "health assessment. Year 2 adds pathophysiology, pharmacology, and clinical practicum. "
            "Year 3 brings medical-surgical nursing, mental health, maternity, and paediatrics—with "
            "corresponding clinical hours and a weekly academic submission requirement for each. "
            "Year 4 demands a capstone project that demonstrates integration of everything learned "
            "across the programme. Each year builds on the last, and falling behind in academic "
            "submissions has a compounding effect on your programme standing.</p>"
            "<p>NurseMyGrade BSN writing support is staffed by writers who hold BSN credentials from "
            "nursing programmes with exactly this curriculum structure. They know what a Year 1 "
            "fundamentals essay should demonstrate, what a Year 3 care plan needs to include to "
            "meet clinical practicum standards, and what a Year 4 capstone committee expects to read. "
            "That programme-level knowledge shapes every assignment they write for you.</p>"
        ),
        _hiw("How BSN Writing Support Works", [
            STEP_SUBMIT,
            (
                "Matched to a BSN-Credentialed Nurse Writer",
                "<p>A writer who holds a BSN from a nursing programme with curriculum similar to yours "
                "is assigned. For speciality assignments (mental health nursing, maternity, critical care), "
                "we match by clinical background as well as academic credential.</p>",
            ),
            (
                "Assignment Written to BSN Programme Standards",
                "<p>Your assignment is written to the competency level your programme year expects. "
                "Year 1 work demonstrates foundational nursing knowledge. Year 4 capstone work demonstrates "
                "integration, synthesis, and leadership. Your writer calibrates accordingly.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("BSN Assignment Types We Cover", [
            (
                "All Years of BSN Programme",
                "Year 1 fundamentals essays and health assessment papers. Year 2 pharmacology and "
                "pathophysiology assignments. Year 3 medical-surgical, mental health, maternity, and "
                "paediatric clinical papers. Year 4 capstone projects.",
            ),
            (
                "NANDA-I and ADPIE Applied Correctly",
                "Care plans using the NANDA-I diagnostic taxonomy, NIC interventions, NOC outcomes, "
                "and ADPIE process structure—applied correctly for BSN programme level, not just "
                "referenced by name.",
            ),
            (
                "Portfolio and Reflective Documentation",
                "Clinical portfolio entries, reflective journals (Gibbs, Johns, Driscoll), skills "
                "sign-off documentation, and competency evidence reports for BSN portfolio requirements.",
            ),
        ]),
        _h("What BSN Faculty Expect vs What Students Deliver"),
        _p(
            "<p>BSN programme faculty evaluate assignments against programme-level competency descriptors. "
            "In Year 1, the expectation is foundational understanding and correct use of nursing frameworks. "
            "By Year 3, the expectation is application—not just knowing what the ADPIE process is, but "
            "demonstrating it in the context of a specific patient scenario with specific clinical reasoning. "
            "By Year 4 capstone, the expectation is integration and leadership: synthesising evidence, "
            "proposing practice change, and communicating it at a scholarly level.</p>"
            "<p>The most common gap between what students submit and what faculty expect is the move from "
            "description to application. Describing what EBP is earns limited marks; demonstrating EBP by "
            "selecting, appraising, and applying specific evidence to a clinical question earns the marks "
            "in the upper range. NurseMyGrade BSN writers understand this distinction because they learned "
            "it in the same type of programme and have helped hundreds of BSN students navigate it.</p>"
        ),
        _cl("NurseMyGrade BSN Writing Quality Checklist", [
            ("Assignment calibrated to your programme year's competency expectations", ""),
            ("Nursing frameworks applied correctly (NANDA-I, NIC, NOC, ADPIE)", ""),
            ("Clinical reasoning demonstrated, not just described", ""),
            ("Current peer-reviewed nursing sources cited from appropriate databases", ""),
            ("APA 7th edition applied consistently throughout", ""),
            ("Reflective framework applied structurally (for reflective assignments)", ""),
            ("Portfolio entries formatted to your programme's portfolio requirements", ""),
            ("Grade or money-back guarantee applies", ""),
        ]),
        _faq_heading(),
        _faq("Do your writers understand BSN curriculum requirements?",
             "<p>Yes. All our BSN-focused writers hold BSN credentials from nursing programmes and have "
             "direct experience with BSN programme assignments, clinical competencies, and academic "
             "expectations at each year level.</p>"),
        _faq("Can you help from Year 1 fundamentals through Year 4 capstone?",
             "<p>Yes. All years of BSN programmes supported: fundamentals and health assessment in Year 1, "
             "pharmacology and pathophysiology in Year 2, clinical speciality papers in Year 3, "
             "and capstone projects in Year 4.</p>"),
        _faq("Do you apply NANDA-I and ADPIE correctly?",
             "<p>Yes. Nursing diagnoses follow the NANDA-I taxonomy with three-part diagnostic statements. "
             "ADPIE process is applied structurally: Assessment, Diagnosis, Planning, Implementation, "
             "and Evaluation are each addressed with clinical specificity.</p>"),
        _faq("Can you help with my nursing portfolio?",
             "<p>Yes. Portfolio entries, reflective journals, clinical logs, competency evidence "
             "documentation, and skills sign-off supporting materials are all covered.</p>"),
        _faq("Do you cover mental health nursing assignments?",
             "<p>Yes. Mental health nursing essays, care plans, case studies, and reflection journals "
             "are handled by writers with mental health clinical experience.</p>"),
        _faq("Can you write pharmacology assignments and drug cards?",
             "<p>Yes. Pharmacology assignments including drug class, mechanism of action, therapeutic "
             "indications, nursing considerations, dosage calculations, and drug interaction analysis "
             "are all supported.</p>"),
        _faq("How fast can you complete a BSN assignment?",
             "<p>Short assignments (500–1,000 words) can be delivered in 3–6 hours. "
             "Standard assignment lengths (1,500–3,000 words) in 24–48 hours.</p>"),
        _faq("What citation style do BSN programmes typically use?",
             "<p>APA 7th edition is the standard for most BSN programmes in the US. "
             "Some programmes use AMA or Harvard depending on institution. Specify your required "
             "style and we apply it consistently.</p>"),
    ],

    # ── 17. MSN Writing ───────────────────────────────────────────────────────
    "reliable-msn-writing-services": [
        _stats(
            ("Graduate-level", "scholarly rigour"),
            ("DNP–PhD", "writer credentials"),
            ("All MSN tracks", "NP, educator, leader"),
            ("12 hrs", "fastest turnaround"),
        ),
        _h("Why MSN Students Choose NurseMyGrade for Graduate Writing Help"),
        _p(
            "<p>Graduate-level nursing writing operates at a fundamentally different standard from "
            "undergraduate work. Where BSN assignments reward application of frameworks, MSN assignments "
            "reward synthesis—the ability to integrate multiple theoretical perspectives, critically "
            "evaluate conflicting evidence, and construct a scholarly argument that advances understanding "
            "rather than just demonstrating it. Faculty who grade MSN work are themselves graduate-educated "
            "clinicians and researchers, and they evaluate writing against that standard.</p>"
            "<p>NurseMyGrade MSN writing support draws on writers who hold DNP or PhD credentials "
            "and have produced the full range of MSN academic work: scholarly papers, policy analyses, "
            "NP clinical case presentations, SOAP notes for advanced practice, programme evaluations, "
            "and MSN capstone projects. They write at the level of synthesis and critical analysis that "
            "graduate nursing programmes require, because they have written at that level in their own "
            "doctoral education.</p>"
        ),
        _hiw("How MSN Writing Support Works", [
            (
                "Share Your Assignment and Graduate-Level Requirements",
                "<p>Provide your paper topic, assignment brief, word count, deadline, and rubric. "
                "Include the theoretical or conceptual framework your module expects you to apply, "
                "and any specific databases or sources your faculty requires.</p>",
            ),
            (
                "Matched to a DNP or PhD Nursing Writer",
                "<p>A writer who holds DNP or PhD credentials and has experience with your MSN track "
                "(NP, educator, leader, or clinical speciality) is assigned. Graduate-level writing "
                "requires graduate-level credentials.</p>",
            ),
            (
                "Scholarly Synthesis and Critical Analysis",
                "<p>Your paper is written with the depth of analysis your MSN programme expects: "
                "integration of multiple perspectives, critical evaluation of evidence quality, "
                "and a scholarly argument that draws implications for nursing practice or policy.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("MSN Writing Support Covers", [
            (
                "All MSN Speciality Tracks",
                "Clinical nurse specialist, nurse educator, nursing leadership and administration, "
                "family nurse practitioner, adult-gerontology primary care, psychiatric-mental health NP, "
                "and dual-degree MSN programmes.",
            ),
            (
                "NP Clinical Documentation",
                "SOAP notes for advanced practice, clinical encounter logs, patient case presentations, "
                "pharmacotherapy papers, prescriptive authority documentation, and clinical competency "
                "evidence for NP programmes.",
            ),
            (
                "Policy and Leadership Papers",
                "Healthcare policy analysis, health systems leadership papers, quality improvement "
                "initiatives, staffing model analyses, transformational leadership papers, and "
                "nursing administration case studies.",
            ),
        ]),
        _h("Graduate Nursing Writing: Description vs Synthesis vs Critical Analysis"),
        _p(
            "<p>The distinction between undergraduate and graduate nursing writing is most visible in "
            "the depth of analysis expected. An undergraduate essay describes what EBP is and identifies "
            "an example. A graduate paper synthesises competing EBP frameworks, evaluates their relative "
            "strengths for a specific clinical context, and constructs an argument for why one approach "
            "is more appropriate than another in your specific practice setting. The movement from "
            "description to synthesis to critical analysis is the defining trajectory of graduate "
            "nursing education.</p>"
            "<p>NurseMyGrade MSN writers understand this trajectory and calibrate every paper accordingly. "
            "They do not summarise what each study found—they synthesise what the body of evidence "
            "collectively shows, acknowledge where evidence is inconsistent or limited, and draw "
            "implications that are specific to your programme track. For NP students, that means "
            "implications for advanced practice decision-making. For nurse educator students, "
            "implications for curriculum design. For nurse leader students, implications for "
            "organisational policy and staffing.</p>"
        ),
        _cl("NurseMyGrade MSN Writing Quality Checklist", [
            ("Writing demonstrates synthesis, not just description of sources", ""),
            ("Theoretical or conceptual framework identified and applied consistently", ""),
            ("Evidence critically evaluated for quality, not just cited for support", ""),
            ("Graduate-level scholarly argument constructed throughout", ""),
            ("Track-specific implications (NP, educator, leader) integrated into the discussion", ""),
            ("APA 7th edition applied consistently at graduate standard", ""),
            ("Healthcare databases appropriate to your topic searched", ""),
            ("Extended revision window applied for complex graduate papers", ""),
        ]),
        _faq_heading(),
        _faq("Do you support all MSN speciality tracks?",
             "<p>Yes. Clinical nurse specialist, nurse educator, nurse leader, FNP, AGPCNP, PMHNP, "
             "and dual-degree MSN programmes are all supported.</p>"),
        _faq("Can you help with NP clinical log and case presentation requirements?",
             "<p>Yes. SOAP notes for advanced practice, clinical encounter logs, patient case presentations, "
             "and pharmacotherapy papers for NP programmes are all covered by our FNP and APRN writers.</p>"),
        _faq("What level of scholarly rigour do MSN papers require?",
             "<p>Graduate level: synthesis rather than description, integration of theory and evidence, "
             "critical evaluation of source quality, and scholarly argumentation that draws practice-specific "
             "implications. Your writer delivers at this standard.</p>"),
        _faq("Can you write healthcare policy analysis papers?",
             "<p>Yes. Healthcare policy, health systems leadership, quality improvement, nursing "
             "administration, and health equity papers are all covered by our graduate-level writers.</p>"),
        _faq("Can you help with a nurse educator curriculum design paper?",
             "<p>Yes. Curriculum development, educational theory application (Benner's Novice to Expert, "
             "adult learning theory), simulation design, and clinical teaching papers for nurse educator "
             "MSN tracks are supported.</p>"),
        _faq("What databases do you use for MSN literature reviews?",
             "<p>CINAHL, PubMed, Cochrane Library, MEDLINE, PsycINFO, HealthSource Nursing, and "
             "any other databases your faculty specifies. Search strategies are documented.</p>"),
        _faq("How fast can you deliver an MSN paper?",
             "<p>Short MSN papers (2,000–3,000 words) from 12 hours. Longer papers and literature "
             "reviews require 24–72 hours depending on complexity and word count.</p>"),
        _faq("Can you incorporate theoretical frameworks like Watson's Theory of Human Caring?",
             "<p>Yes. Major nursing theories (Watson, Benner, Roy, Orem, Rogers, Leininger) and "
             "conceptual models are applied correctly as frameworks in MSN-level nursing papers.</p>"),
    ],

    # ── 18. APA Format ────────────────────────────────────────────────────────
    "apa-format-nursing-paper-writing-service": [
        _stats(
            ("APA 7th", "7th edition standard"),
            ("All levels", "student to doctoral"),
            ("3 hrs", "fastest turnaround"),
            ("Every section", "title page to references"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for APA Formatting"),
        _p(
            "<p>APA 7th edition is the standard citation and formatting style for nursing papers in most "
            "US programmes. The 7th edition introduced meaningful changes from the 6th: the running head "
            "requirement was eliminated for student papers, the DOI format changed to a hyperlink rather "
            "than a label, the et al. rule changed from six or more authors to three or more, and "
            "new guidelines on bias-free language were introduced. Students who learned APA 6th edition "
            "in a previous degree programme or who were taught inconsistently are routinely penalised "
            "for applying 6th edition conventions to 7th edition assignments.</p>"
            "<p>NurseMyGrade APA nursing papers are formatted by writers who apply APA 7th edition "
            "as their daily citation standard. They know which elements differ between the student "
            "and professional paper formats, how to format a DOI correctly, when to use et al. "
            "and when to list all authors, how to format a paraphrased citation versus a direct "
            "quote, and how to apply the five levels of APA headings. Every paper we deliver "
            "meets the 7th edition standard your faculty expects.</p>"
        ),
        _hiw("How We Format Your Nursing Paper in APA 7th", [
            (
                "Submit Your Paper or Brief",
                "<p>Share your completed draft for formatting review, or submit your assignment brief "
                "for a fully written and formatted paper. Include your institution's specific "
                "requirements if they deviate from standard APA 7th.</p>",
            ),
            (
                "APA Audit or Full Formatting",
                "<p>For drafts: every citation, reference, heading, margin, font, and spacing element "
                "is reviewed against APA 7th and corrected. For new papers: formatting is applied "
                "from the first page as the paper is written.</p>",
            ),
            (
                "Reference List Verification",
                "<p>Every reference entry is verified: author format (last name, initials), "
                "publication year in parentheses, article title (sentence case), journal name "
                "(title case, italicised), volume and issue numbers, page range, and DOI hyperlink. "
                "Every in-text citation is cross-checked against the reference list.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("APA 7th Elements We Apply Correctly", [
            (
                "Title Page and Abstract",
                "Student title page format: title, author, institution, course number and name, "
                "instructor name, due date. Abstract (250 words or fewer) with keywords if required. "
                "No running head for student papers.",
            ),
            (
                "In-Text Citations and Reference List",
                "Author-date format for all in-text citations. Reference list entries formatted "
                "by source type (journal article, book, chapter, website, report). DOI "
                "hyperlinks formatted correctly (https://doi.org/...).",
            ),
            (
                "Headings and Page Formatting",
                "APA 7th heading levels 1–5 applied consistently. 1-inch margins. "
                "Times New Roman 12pt or Calibri 11pt. Double-spaced throughout. "
                "Page numbers in upper right header.",
            ),
        ]),
        _h("APA 7th Edition: What Changed from 6th Edition"),
        _p(
            "<p>The three most commonly misapplied APA 7th changes are the et al. rule, the DOI "
            "format, and the running head. In APA 7th, et al. is used for three or more authors "
            "in all in-text citations (not just six or more as in the 6th edition). DOIs are "
            "formatted as hyperlinks (https://doi.org/...) without the doi: label. Running "
            "heads are no longer required for student papers—only for manuscripts submitted "
            "for publication. Students who still include running heads are applying 6th "
            "edition formatting. Faculty who grade to the 7th edition will notice.</p>"
            "<p>Other important changes include: URLs for sources without DOIs no longer need "
            "'Retrieved from' prefixes; the 7th edition introduced singular 'they' as a "
            "gender-neutral singular pronoun; specific guidance was provided on bias-free "
            "language for race, ethnicity, age, disability, and gender identity; and "
            "the format for citing social media posts and podcast episodes was clarified. "
            "NurseMyGrade writers apply all 7th edition changes correctly and consistently.</p>"
        ),
        _cl("NurseMyGrade APA 7th Edition Checklist", [
            ("Title page follows student format (no running head)", ""),
            ("Abstract is 250 words or fewer with Keywords on the line below", ""),
            ("In-text citations use et al. for three or more authors from the first citation", ""),
            ("DOIs formatted as hyperlinks: https://doi.org/...", ""),
            ("Reference list entries formatted by source type", "Journal article, book chapter, website, report, etc."),
            ("APA heading levels 1–5 applied consistently", ""),
            ("Margins 1 inch, font Times New Roman 12pt or Calibri 11pt, double-spaced", ""),
            ("Tables and figures formatted with APA 7th captions and notes", ""),
        ]),
        _faq_heading(),
        _faq("What changed from APA 6th to APA 7th edition?",
             "<p>Key changes: running head eliminated for student papers; et al. now used for three or more "
             "authors (not six or more); DOIs formatted as hyperlinks without 'doi:' label; "
             "new bias-free language guidelines; URLs no longer need 'Retrieved from'. "
             "All applied correctly by your writer.</p>"),
        _faq("Can you format a paper I have already written?",
             "<p>Yes. Share your draft and we apply full APA 7th formatting: title page, abstract, "
             "headings, in-text citations, and reference list. Every element is reviewed and corrected.</p>"),
        _faq("Do you format tables and figures in APA 7th?",
             "<p>Yes. Tables formatted with APA 7th table notes, captions above the table, "
             "and source attribution. Figures formatted with captions below the figure "
             "and source attribution.</p>"),
        _faq("What if my institution has deviations from standard APA?",
             "<p>Share your institution's style guide or specific requirements and we apply those "
             "deviations instead of the standard APA 7th defaults.</p>"),
        _faq("Do you format the abstract and keywords correctly?",
             "<p>Yes. Abstract is 150–250 words, not indented, with the heading 'Abstract' in "
             "APA 7th format. 'Keywords' is indented and italicised on the line below the abstract.</p>"),
        _faq("Can you format a paper with multiple APA heading levels?",
             "<p>Yes. APA heading levels 1–5 are applied: Level 1 (bold, centred), Level 2 (bold, "
             "left-aligned), Level 3 (bold italic, left-aligned), Level 4 (bold, indented, ends with "
             "period), Level 5 (bold italic, indented, ends with period).</p>"),
        _faq("How fast can you format a nursing paper?",
             "<p>APA formatting of an existing draft (3,000–5,000 words) can be completed in "
             "3–6 hours. Full paper writing with formatting takes longer depending on length and complexity.</p>"),
        _faq("Do you apply APA 7th to direct quotes as well as paraphrases?",
             "<p>Yes. Direct quotes include page numbers (p. X) or paragraph numbers for non-paginated "
             "sources. Paraphrases use the author-date format without page numbers unless your "
             "instructor requires them.</p>"),
    ],

    # ── 19. Medical and Health Papers ─────────────────────────────────────────
    "health-and-medicine-paper-writing-service": [
        _stats(
            ("Nursing + medicine", "all health disciplines"),
            ("APA / AMA / Vancouver", "any citation style"),
            ("BSN–MD writers", "credentialed clinicians"),
            ("6 hrs", "fastest turnaround"),
        ),
        _h("Why Health Sciences Students Choose NurseMyGrade for Medical Paper Help"),
        _p(
            "<p>Medical and health sciences academic papers require clinical literacy that generalist "
            "academic writers cannot reliably provide. Whether the paper covers pharmacokinetics, "
            "epidemiological methodology, public health interventions, healthcare policy, "
            "social determinants of health, or clinical case reports, the examiner reading it "
            "holds clinical or research credentials in the field. Generic papers that use the "
            "right terminology without demonstrating understanding of clinical or methodological "
            "context are quickly identified and marked accordingly.</p>"
            "<p>NurseMyGrade health and medical paper writers include nurses, pharmacists, "
            "public health practitioners, and allied health professionals. Every writer is "
            "matched to the specific health discipline and paper type of your assignment. "
            "A pharmacokinetics paper goes to a writer with clinical pharmacy or pharmacology "
            "background. A social determinants of health paper goes to a writer with public "
            "health expertise. That matching discipline is what ensures your paper demonstrates "
            "the clinical or disciplinary literacy your faculty expects.</p>"
        ),
        _hiw("How We Write Your Medical or Health Sciences Paper", [
            STEP_SUBMIT,
            (
                "Matched by Health Discipline and Paper Type",
                "<p>Your writer is matched to your specific health discipline—not just to 'nursing' "
                "as a generic category. A pharmacology paper goes to a writer with pharmacological "
                "expertise; a public health paper to a writer with epidemiology or health promotion "
                "background.</p>",
            ),
            (
                "Clinically Accurate Writing with Appropriate Methodology",
                "<p>Your paper is written with the clinical or disciplinary accuracy your health "
                "sciences programme expects. Medical terminology is used precisely. Epidemiological "
                "methods are described correctly. Clinical evidence is cited from appropriate "
                "health databases.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("Health Disciplines We Cover", [
            (
                "Nursing and Allied Health",
                "Nursing theory, clinical nursing papers, public health nursing, community health, "
                "occupational therapy, physiotherapy, radiography, dietetics, and all other "
                "allied health disciplines.",
            ),
            (
                "Pharmacology and Pharmacy",
                "Pharmacokinetics, pharmacodynamics, drug classification papers, mechanism of action "
                "assignments, clinical pharmacology, drug interaction analysis, and pharmacy "
                "practice papers.",
            ),
            (
                "Public Health and Epidemiology",
                "Epidemiological study designs, health promotion papers, social determinants of health, "
                "health policy analysis, disease prevention, community health needs assessments, "
                "and global health papers.",
            ),
        ]),
        _h("Clinical Accuracy in Health Sciences Papers: Why It Matters"),
        _p(
            "<p>The difference between a health sciences paper that scores in the 60s and one that "
            "scores in the 80s is almost always clinical accuracy and disciplinary precision. "
            "A pharmacokinetics paper that confuses clearance with half-life, a public health paper "
            "that misapplies the Bradford Hill criteria for causation, a community health paper "
            "that describes an epidemiological design without specifying the comparison group—these "
            "are the errors that signal to a health sciences examiner that the writer does not "
            "have the clinical background to engage with the material at the required level.</p>"
            "<p>NurseMyGrade health and medical writers use the correct technical vocabulary for "
            "their discipline because they have studied and practised in it. Pharmacokinetic "
            "parameters (Vd, Cl, t½, AUC, Cmax) are reported correctly. Epidemiological study "
            "design terminology (incidence vs prevalence, relative risk vs odds ratio, "
            "confounding vs effect modification) is applied accurately. Clinical trial "
            "phases and their purposes are described correctly. This precision is not incidental "
            "to good health sciences writing—it is the mark of it.</p>"
        ),
        _cl("NurseMyGrade Health Sciences Paper Quality Checklist", [
            ("Writer matched to your specific health discipline, not just to health generally", ""),
            ("Clinical or disciplinary terminology used precisely and accurately", ""),
            ("Appropriate health databases searched for evidence", "PubMed, CINAHL, Cochrane, Embase, or discipline-specific database"),
            ("Epidemiological or methodological concepts described correctly", ""),
            ("Citation style applied correctly (APA, AMA, Vancouver, or other)", ""),
            ("Evidence from peer-reviewed clinical or health sciences journals", ""),
            ("Discussion connects evidence to practice or policy implications", ""),
        ]),
        _faq_heading(),
        _faq("Do you cover pharmacology and pharmacy assignments?",
             "<p>Yes. Pharmacokinetics, pharmacodynamics, drug classifications, mechanism of action, "
             "clinical pharmacology, and pharmacy practice papers are covered by writers with "
             "pharmacological expertise.</p>"),
        _faq("Can you write public health papers?",
             "<p>Yes. Epidemiology, health promotion, community health, social determinants of health, "
             "health policy, disease prevention, and global health papers are all supported.</p>"),
        _faq("Do you use AMA citation style?",
             "<p>Yes. APA, AMA, Vancouver, Chicago, Harvard, and any other citation style your "
             "programme requires. Specify your required style in your brief.</p>"),
        _faq("Are your writers clinically qualified?",
             "<p>Yes. All health and medical paper writers hold nursing, pharmacy, public health, "
             "or allied health credentials with active or recent clinical or professional experience.</p>"),
        _faq("Can you write papers for medicine or pre-medicine students?",
             "<p>Yes. Pre-clinical biomedical sciences papers, clinical case studies, evidence-based "
             "medicine papers, and clinical clerkship assignments are covered by our medically "
             "experienced writers.</p>"),
        _faq("Do you write systematic reviews for health sciences topics?",
             "<p>Yes. PRISMA-compliant systematic reviews with documented search strategy, evidence "
             "tables, and critical appraisal for health sciences topics across all disciplines.</p>"),
        _faq("Can you write a clinical case report for academic submission?",
             "<p>Yes. Clinical case reports following CARE (CAse REport) guidelines or your "
             "programme's required format—patient presentation, assessment, intervention, "
             "outcomes, discussion—are a common request.</p>"),
        _faq("How fast can you deliver a health sciences paper?",
             "<p>Short papers (5–7 pages) can be delivered in 6–12 hours. Longer papers "
             "and systematic reviews require 24–72 hours depending on complexity.</p>"),
    ],

    # ── 20. Nursing Homework ──────────────────────────────────────────────────
    "online-nursing-homework-help": [
        _stats(
            ("3 hrs", "fastest completion"),
            ("All subjects", "pharmacology to theory"),
            ("APA 7th", "citations included"),
            ("BSN–MSN", "qualified nurses"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Homework Help"),
        _p(
            "<p>Nursing homework is relentless. Discussion board posts due Tuesday. Pathophysiology "
            "questions due Wednesday. Drug card assignments due Thursday. A short reflection journal "
            "due Friday. And through all of it, clinical hours that start at 0600. The volume of "
            "weekly nursing homework is not designed to be manageable alongside full clinical "
            "schedules—it is designed to be completed by students who have significant study time, "
            "which most nursing students at the point of clinical rotations do not have.</p>"
            "<p>NurseMyGrade homework help assigns qualified BSN and MSN nurses to your weekly "
            "homework tasks. They complete short nursing assignments to your rubric using "
            "current clinical knowledge, evidence-based content, and the citation format "
            "your course requires. Whether it is a 200-word discussion post, a drug card "
            "for five medications, or a three-question pathophysiology problem set, "
            "your assignment is handled by someone who knows the content—not a generic "
            "tutor who looks it up.</p>"
        ),
        _hiw("How Nursing Homework Help Works", [
            (
                "Share Your Assignment",
                "<p>Paste the discussion prompt, attach the homework question sheet, or describe "
                "the assignment. Include your deadline, word count, and any specific instructions "
                "from your faculty or course rubric.</p>",
            ),
            (
                "Matched to a Nursing Subject Expert",
                "<p>Your assignment goes to a nurse with knowledge in the subject area: pharmacology "
                "questions to a nurse with pharmacology expertise, pathophysiology to a nurse who "
                "teaches or practises in the relevant clinical area, theory to a nurse with "
                "academic background in nursing theory.</p>",
            ),
            (
                "Assignment Completed to Your Rubric",
                "<p>Your nurse completes the homework using current, evidence-based clinical "
                "knowledge. Citations are included where required. Word count meets your "
                "assignment's specification. Format follows your course requirements.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("Nursing Homework Types We Handle", [
            (
                "Discussion Posts and Peer Responses",
                "Weekly discussion board posts written to your prompt, word count, and citation "
                "requirements. Peer response posts that engage substantively with the original "
                "post and add clinical depth.",
            ),
            (
                "Pharmacology and Drug Card Assignments",
                "Drug class, mechanism of action, therapeutic indications, contraindications, "
                "adverse effects, drug interactions, nursing considerations, and patient education "
                "for individual medications or a medication class.",
            ),
            (
                "Pathophysiology and Short Answer Questions",
                "Disease process descriptions, clinical manifestations, diagnostic criteria, "
                "nursing management, and complication prevention for any pathophysiology topic "
                "your module covers.",
            ),
        ]),
        _h("Drug Cards and Pharmacology Homework Done Right"),
        _p(
            "<p>Pharmacology homework is among the most time-consuming weekly assignments in BSN "
            "programmes—and one of the most frequently lost points. A complete drug card for a "
            "single medication typically covers: generic and trade name, drug class, mechanism of "
            "action, therapeutic indications (approved and off-label where relevant), "
            "contraindications (absolute and relative), adverse effects organised by system, "
            "drug-drug and drug-food interactions, nursing considerations (what to assess before "
            "giving, what to monitor after giving), and patient education (what to tell the patient). "
            "For a weekly assignment covering five medications, that is a substantial clinical "
            "knowledge demand.</p>"
            "<p>NurseMyGrade pharmacology homework help is completed by nurses who have administered "
            "and monitored the medications they write about. Your drug card for heparin will include "
            "the correct aPTT monitoring parameters. Your drug card for digoxin will include "
            "the correct toxicity symptoms and the Lanoxin brand name. Your drug card for "
            "metformin will note the correct contraindication for contrast dye administration. "
            "That clinical specificity is what your faculty is looking for—and what generic "
            "homework services miss.</p>"
        ),
        _cl("NurseMyGrade Nursing Homework Quality Checklist", [
            ("Discussion post directly addresses the specific prompt, not just the topic area", ""),
            ("Current peer-reviewed source cited where required (APA 7th in-text and reference list)", ""),
            ("Pharmacology drug card includes all required components", "Drug class, MOA, indications, contraindications, adverse effects, nursing considerations, patient education"),
            ("Pathophysiology answers include clinical manifestations, not just disease description", ""),
            ("Peer responses engage substantively with the original post", ""),
            ("Word count meets assignment specification", ""),
            ("Submitted before your deadline", ""),
        ]),
        _faq_heading(),
        _faq("Can you help with pharmacology drug cards?",
             "<p>Yes. Drug class, mechanism, indications, contraindications, side effects, drug "
             "interactions, and nursing considerations (monitoring parameters, patient education, "
             "administration precautions) for any medication or medication class.</p>"),
        _faq("Do you answer pathophysiology questions?",
             "<p>Yes. Disease processes, clinical manifestations, diagnostic criteria, nursing "
             "management, and complication prevention for any pathophysiology topic in your nursing module.</p>"),
        _faq("How fast can you complete short nursing homework?",
             "<p>Short discussion posts (150–300 words) can be completed in 3 hours. "
             "Drug card sets and short answer questions typically complete within 3–6 hours "
             "depending on the number of items.</p>"),
        _faq("Can you respond to my classmates' discussion posts?",
             "<p>Yes. Peer response posts written to your programme's requirements, engaging "
             "substantively with the original post and adding clinical or evidence-based content.</p>"),
        _faq("Do you help with concept map homework?",
             "<p>Yes. Short concept map assignments, including pathophysiology-to-diagnosis maps "
             "and medication concept maps, are handled as homework assignments.</p>"),
        _faq("Can you help with nursing calculation homework?",
             "<p>Yes. Dosage calculation, IV drip rate, medication administration, and "
             "fluid management calculations are covered with step-by-step working shown where required.</p>"),
        _faq("Do you write nursing theory reflection homework?",
             "<p>Yes. Short reflection assignments applying nursing theories (Orem, Roy, Watson, "
             "Benner, Leininger) to clinical practice or personal nursing philosophy are covered.</p>"),
        _faq("What if my homework is due tonight?",
             "<p>Rush delivery from 3 hours is standard for short nursing homework. "
             "Contact us as soon as you have the assignment and specify your exact deadline.</p>"),
    ],

    # ── 21. Postgraduate Nursing ──────────────────────────────────────────────
    "postgraduate-nursing-papers-assignments-help": [
        _stats(
            ("MSN–DNP–PhD", "all postgraduate levels"),
            ("Doctoral rigour", "synthesis and analysis"),
            ("DNP–PhD writers", "credentialed at your level"),
            ("Extended revision", "window available"),
        ),
        _h("Why Postgraduate Nursing Students Choose NurseMyGrade"),
        _p(
            "<p>Postgraduate nursing demands a level of scholarly performance that undergraduate "
            "nursing education does not fully prepare students for. The expectation shifts from "
            "application—demonstrating you can use frameworks correctly—to synthesis and "
            "critical analysis: constructing original arguments from multiple bodies of evidence, "
            "evaluating methodological rigour at a level that would survive peer review, and writing "
            "at the scholarly precision expected of a doctoral-level clinician or researcher. "
            "Most students who struggle at postgraduate level are not struggling because they "
            "lack intelligence or clinical knowledge—they are struggling because postgraduate "
            "academic writing is a distinct skill that requires development independent of "
            "clinical expertise.</p>"
            "<p>NurseMyGrade postgraduate support draws on writers who hold DNP or PhD credentials "
            "and have produced doctoral-level nursing scholarship. They write the PRISMA-compliant "
            "systematic reviews, the DNP quality improvement project proposals, the MSN policy "
            "analysis papers, and the PhD dissertation chapters that postgraduate programmes produce. "
            "More importantly, they write them at the standard of doctoral-level scholarly "
            "rigour that postgraduate nursing examiners apply when grading.</p>"
        ),
        _hiw("How Postgraduate Nursing Writing Support Works", [
            (
                "Share Your Assignment and Programme Level",
                "<p>Provide your paper topic, programme level (MSN, DNP, or PhD), assignment brief, "
                "required frameworks or theoretical models, word count, deadline, and any "
                "faculty feedback from previous submissions.</p>",
            ),
            (
                "Matched to a Doctoral-Level Nurse Writer",
                "<p>A writer who holds DNP or PhD credentials and has produced postgraduate "
                "nursing scholarship in your subject area is assigned. Postgraduate-level work "
                "requires postgraduate-level credentials in the writer.</p>",
            ),
            (
                "Doctoral-Level Scholarly Writing",
                "<p>Your paper is written with the synthesis, critical analysis, and scholarly "
                "argumentation that postgraduate nursing examiners expect. Evidence is appraised "
                "for methodological quality, not just cited. Arguments draw original implications "
                "for nursing practice, policy, or knowledge.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("Postgraduate Nursing Writing Covers", [
            (
                "MSN, DNP, and PhD-Level Papers",
                "MSN scholarly papers, policy analyses, and leadership papers. DNP project proposals, "
                "quality improvement papers, and evidence-based implementation projects. "
                "PhD dissertation chapters and research papers.",
            ),
            (
                "Quality Improvement Papers",
                "PDSA cycle documentation, Plan-Do-Study-Act frameworks, QI project proposals, "
                "outcome measurement plans, and implementation science papers for DNP and MSN "
                "quality improvement courses.",
            ),
            (
                "PRISMA-Compliant Systematic Reviews",
                "Systematic reviews with full PRISMA flow diagram, documented search strategy, "
                "inclusion and exclusion criteria applied across databases, evidence tables "
                "with critical appraisal ratings, and thematic synthesis.",
            ),
        ]),
        _h("The Standard Difference Between MSN and DNP Writing"),
        _p(
            "<p>MSN writing operates at graduate level: it synthesises theoretical frameworks, "
            "critically evaluates evidence, and draws practice-relevant conclusions. The "
            "expectation is that you can integrate multiple scholarly perspectives and argue "
            "for a position based on evidence quality, not just evidence presence. DNP writing "
            "moves further: it is practice-focused, translational, and explicitly tied to a "
            "defined clinical or organisational context. A DNP quality improvement paper is "
            "not just a literature review—it is a blueprint for implementing a practice "
            "change in a specific setting, with identified barriers, stakeholder engagement "
            "strategy, implementation timeline, and measurable outcome criteria.</p>"
            "<p>PhD nursing writing is the most rigorous: original contribution to nursing "
            "knowledge, epistemological justification for the chosen research paradigm, "
            "methodological choices justified against alternatives, and findings that advance "
            "the field rather than apply existing evidence. NurseMyGrade writers are matched "
            "to your programme level, not just your subject, because the writing standard "
            "varies as significantly as the content.</p>"
        ),
        _cl("NurseMyGrade Postgraduate Writing Quality Checklist", [
            ("Writing demonstrates doctoral-level synthesis, not undergraduate-level description", ""),
            ("Theoretical or conceptual framework applied throughout, not just named", ""),
            ("Evidence appraised for methodological quality, not just cited for support", ""),
            ("DNP projects include implementation plan, barriers, facilitators, and SMART outcomes", ""),
            ("Systematic reviews follow PRISMA guidelines with full documentation", ""),
            ("Scholarly argument draws original practice or policy implications", ""),
            ("APA 7th applied at doctoral standard throughout", ""),
            ("Extended revision window applies", ""),
        ]),
        _faq_heading(),
        _faq("What is the difference between MSN and DNP writing?",
             "<p>MSN writing is scholarly and graduate-level: synthesis of evidence and theory, "
             "critical evaluation, practice implications. DNP writing is practice-focused: "
             "evidence applied to a specific clinical problem with an implementation plan "
             "and measurable outcomes. Our writers understand both standards.</p>"),
        _faq("Can you help with quality improvement papers?",
             "<p>Yes. PDSA cycles, Plan-Do-Study-Act documentation, QI project proposals, "
             "outcome measurement plans, and implementation science papers for DNP and "
             "MSN programmes.</p>"),
        _faq("Do you support nursing leadership and administration papers?",
             "<p>Yes. Transformational leadership, nurse leader competencies, staffing model "
             "analyses, health systems management, and nursing administration papers at "
             "MSN and DNP level.</p>"),
        _faq("Can you write a PRISMA-compliant systematic review for a PhD?",
             "<p>Yes. Full search strategy documentation, PRISMA flow diagram, inclusion "
             "and exclusion criteria applied consistently, evidence tables with critical "
             "appraisal ratings, and narrative synthesis at doctoral scholarly standard.</p>"),
        _faq("Can you help with a DNP project implementation plan?",
             "<p>Yes. Implementation science frameworks (RE-AIM, CFIR, Grol and Grimshaw), "
             "stakeholder analysis, barrier and facilitator identification, implementation "
             "timeline, and fidelity assessment plan are all supported.</p>"),
        _faq("What theoretical frameworks do you use at postgraduate level?",
             "<p>Donabedian's Quality Framework, Lewin's Change Theory, Kotter's Change Model, "
             "Stetler Model, ACE Star, Iowa Model, RE-AIM, CFIR, and others. Specify your "
             "programme's required framework and we apply it.</p>"),
        _faq("How fast can you deliver a postgraduate nursing paper?",
             "<p>Short postgraduate papers (3,000–5,000 words) from 12 hours. "
             "Longer papers, systematic reviews, and project proposals require 48–72 hours "
             "depending on complexity.</p>"),
        _faq("Can you incorporate committee or faculty feedback at doctoral level?",
             "<p>Yes. Share committee feedback or faculty comments and your writer revises "
             "the affected sections with the scholarly precision doctoral committees expect.</p>"),
    ],

    # ── 22. Evidence-Based Practice ───────────────────────────────────────────
    "nursing-evidence-based-practice": [
        _stats(
            ("PICOT", "question framework"),
            ("CASP / JBI / GRADE", "appraisal tools"),
            ("Iowa + ACE Star", "EBP models"),
            ("BSN–DNP", "writer credentials"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for EBP Paper Help"),
        _p(
            "<p>Evidence-based practice papers are the academic version of the process nurses "
            "perform in clinical decision-making: identifying a practice problem, formulating "
            "a searchable question, locating and appraising the best available evidence, and "
            "translating that evidence into a practice recommendation. The academic paper "
            "must make this process transparent—showing not just the conclusion but the "
            "reasoning that led to it. Examiners evaluate the quality of your evidence "
            "appraisal as much as the quality of your recommendation.</p>"
            "<p>NurseMyGrade EBP paper writers hold BSN, MSN, or DNP credentials and apply "
            "evidence-based practice in their clinical and academic roles. They know the "
            "difference between a PICOT question that is too broad to search effectively "
            "and one that generates a manageable, relevant results set. They know how to "
            "use CASP checklists to evaluate an RCT vs a qualitative study. They know "
            "what level of evidence each study design represents in a hierarchy. That "
            "methodological knowledge is what EBP paper examiners are looking for.</p>"
        ),
        _hiw("How We Write Your EBP Nursing Paper", [
            (
                "PICOT Question Development",
                "<p>Share your clinical practice problem and your writer helps formulate a clear, "
                "searchable PICOT question: Population, Intervention, Comparison, Outcome, and Time. "
                "A well-formed PICOT drives the entire evidence search.</p>",
            ),
            (
                "Systematic Literature Search",
                "<p>A structured search of CINAHL, PubMed, Cochrane, and other relevant databases "
                "is conducted using your PICOT terms. Inclusion and exclusion criteria are defined "
                "and applied consistently. A search strategy table is documented.</p>",
            ),
            (
                "Critical Appraisal and Evidence Synthesis",
                "<p>Each included study is critically appraised using CASP checklists, JBI tools, "
                "or the GRADE framework as appropriate to the study design. An evidence synthesis "
                "table summarises design, sample, key findings, and level of evidence. Clinical "
                "applicability is evaluated explicitly.</p>",
            ),
            (
                "Practice Recommendations and Implementation Discussion",
                "<p>Based on the appraised evidence, specific, practice-change recommendations "
                "are drawn and connected to a named EBP framework (Iowa, ACE Star, Stetler). "
                "Implications for your specific practice setting are discussed.</p>",
            ),
        ]),
        _fg("What Your EBP Paper Includes", [
            (
                "PICOT Question and Search Strategy",
                "Formally stated PICOT question. Documented search strategy with database names, "
                "search terms, Boolean operators, and inclusion/exclusion criteria applied to "
                "each database.",
            ),
            (
                "Evidence Table with Critical Appraisal",
                "Synthesis table summarising each appraised study: author/year, design, sample, "
                "intervention, outcome, level of evidence, appraisal quality rating, and "
                "key findings relevant to your PICOT question.",
            ),
            (
                "EBP Framework Applied",
                "Iowa Model, ACE Star, Stetler Model, PDSA, or the framework your programme "
                "specifies—applied structurally to guide the evidence translation process, "
                "not just referenced in the introduction.",
            ),
        ]),
        _h("Critical Appraisal Tools: CASP, JBI, and GRADE"),
        _p(
            "<p>The Critical Appraisal Skills Programme (CASP) provides separate checklists for "
            "different study designs: systematic reviews, RCTs, cohort studies, case-control "
            "studies, qualitative research, and economic evaluations. Each checklist asks "
            "specific methodological questions relevant to the design type. A CASP appraisal "
            "of a qualitative study asks about the appropriateness of the research design, "
            "the rigour of the recruitment strategy, and the adequacy of data analysis—not "
            "the same questions you would apply to an RCT.</p>"
            "<p>The JBI (Joanna Briggs Institute) critical appraisal tools are particularly "
            "relevant for nursing EBP because JBI was founded specifically for healthcare "
            "evidence synthesis. The GRADE (Grading of Recommendations Assessment, Development "
            "and Evaluation) framework rates the certainty of a body of evidence across "
            "four levels: high, moderate, low, and very low. NurseMyGrade writers select "
            "the appropriate appraisal tool for each study design and apply it correctly, "
            "because applying a tool incorrectly is itself an evidence of insufficient "
            "methodological understanding.</p>"
        ),
        _cl("NurseMyGrade EBP Paper Quality Checklist", [
            ("PICOT question clearly defines Population, Intervention, Comparison, Outcome, and Time", ""),
            ("Literature search conducted in at least two appropriate health databases with documented strategy", ""),
            ("Inclusion and exclusion criteria defined and applied consistently", ""),
            ("Each study appraised using appropriate tool for its design (CASP, JBI, GRADE)", ""),
            ("Evidence table summarises all appraised studies with level of evidence ratings", ""),
            ("EBP framework applied structurally (not just named) to guide evidence translation", ""),
            ("Practice recommendations specific and grounded in appraised evidence", ""),
            ("Implications for practice setting discussed explicitly", ""),
        ]),
        _faq_heading(),
        _faq("What is a PICOT question and can you help develop one?",
             "<p>PICOT stands for Population, Intervention, Comparison, Outcome, and Time. "
             "Your writer helps formulate a clear, focused PICOT question appropriate to your "
             "clinical topic—specific enough to generate a manageable evidence set.</p>"),
        _faq("Which critical appraisal tools do you use?",
             "<p>CASP checklists (design-specific), JBI critical appraisal tools, and GRADE "
             "framework—whichever your programme or faculty requires. We apply the tool "
             "appropriate to each included study's design.</p>"),
        _faq("Can you write a full EBP project proposal?",
             "<p>Yes. PICOT through literature search, evidence appraisal, synthesis, implementation "
             "plan (with EBP framework), and evaluation strategy—all included in a full EBP "
             "project proposal.</p>"),
        _faq("Which EBP frameworks do you cover?",
             "<p>Iowa Model, ACE Star Model, Stetler Model, PDSA cycle, and others. Specify "
             "which your programme uses and your writer applies it structurally throughout.</p>"),
        _faq("Do you produce an evidence synthesis table?",
             "<p>Yes. An evidence table summarising each appraised study (author, year, design, "
             "sample, intervention, outcome, level of evidence, appraisal rating, key findings) "
             "is included with every EBP paper.</p>"),
        _faq("What level of evidence is each study design?",
             "<p>Systematic reviews and meta-analyses: Level I. RCTs: Level II. Quasi-experimental: "
             "Level III. Case-control/cohort: Level IV. Systematic reviews of qualitative evidence: "
             "Level V. Qualitative/descriptive: Level VI. Expert opinion: Level VII. "
             "Your writer assigns levels correctly.</p>"),
        _faq("Can you help with just the PICOT question and literature search sections?",
             "<p>Yes. Individual sections—PICOT development, search strategy, evidence appraisal, "
             "synthesis, or recommendations—are supported as standalone requests.</p>"),
        _faq("How fast can you deliver an EBP nursing paper?",
             "<p>Short EBP papers (2,000–3,000 words) can be delivered in 6–12 hours. "
             "Full EBP project proposals with evidence tables require 24–48 hours.</p>"),
    ],

    # ── 23. Annotated Bibliography ────────────────────────────────────────────
    "nursing-annotated-bibliography": [
        _stats(
            ("CINAHL + PubMed", "primary databases"),
            ("APA 7th", "citation standard"),
            ("150–300 words", "per annotation"),
            ("3 hrs", "fastest turnaround"),
        ),
        _h("Why Nursing Students Choose NurseMyGrade for Annotated Bibliography Help"),
        _p(
            "<p>A nursing annotated bibliography is not a list of sources with a summary attached. "
            "The annotation for each source must evaluate the source—assessing its methodology, "
            "the quality of its evidence, the relevance of its findings to your research question, "
            "and its limitations. Examiners who grade annotated bibliographies are looking for "
            "evidence that you can critically evaluate nursing literature, not just summarise it. "
            "An annotation that says 'this article discusses patient falls and prevention strategies' "
            "earns limited marks. An annotation that identifies the study design, evaluates the "
            "sample size, notes a potential bias, and explains why this evidence level is "
            "appropriate for your PICOT question earns the marks in the upper range.</p>"
            "<p>NurseMyGrade annotated bibliography writers hold nursing credentials and read "
            "clinical nursing literature regularly. They can identify whether a study is a "
            "systematic review or a literature review, whether a sample size is adequate for "
            "the research question, whether a qualitative methodology is appropriate for the "
            "type of knowledge being sought, and whether a nursing finding has clinical "
            "applicability beyond the study setting. That critical literacy is what annotation "
            "requires.</p>"
        ),
        _hiw("How We Write Your Nursing Annotated Bibliography", [
            (
                "Provide Your Topic and Source Requirements",
                "<p>Share your research topic or PICOT question, required source count, "
                "any specific sources you want to include, and your rubric or annotation length "
                "requirement. Indicate whether we should locate sources or annotate sources "
                "you provide.</p>",
            ),
            (
                "Literature Search (If Source Identification Required)",
                "<p>A structured search of CINAHL, PubMed, Cochrane, and other appropriate "
                "databases is conducted. Sources are selected based on relevance to your topic, "
                "publication date, and study design quality.</p>",
            ),
            (
                "Critical Annotation Writing",
                "<p>Each annotation is written to your required length (typically 150–300 words) "
                "and covers: source summary, methodological evaluation, identification of strengths "
                "and limitations, and commentary on relevance to your research question. "
                "APA 7th citation precedes each annotation.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("What Each Annotation Includes", [
            (
                "Summary of Purpose and Findings",
                "The source's research question or purpose, methodology, key findings, "
                "and conclusions—summarised concisely in clinical nursing language appropriate "
                "to your level.",
            ),
            (
                "Methodological Evaluation",
                "Study design identified and evaluated: sample size adequacy, research "
                "methodology appropriateness, potential biases, and level of evidence in the "
                "nursing evidence hierarchy. Not just 'this is a good source.'",
            ),
            (
                "Relevance Commentary",
                "Specific explanation of how this source relates to your research question "
                "or PICOT, including how it contributes to (or complicates) the body of evidence "
                "on your topic.",
            ),
        ]),
        _h("What Nursing Faculty Look for in Annotation Quality"),
        _p(
            "<p>The highest-scoring annotations demonstrate what evidence-based practice training "
            "is supposed to develop: the ability to read a nursing study and evaluate it, not just "
            "report it. Faculty who grade annotated bibliographies often apply a rubric that awards "
            "marks separately for summary accuracy, methodological critique, relevance assessment, "
            "and citation format. Students who lose marks almost always lose them on the "
            "methodological critique dimension—because writing a genuine critique of a nursing "
            "study requires enough methodological literacy to identify what could have been "
            "done differently, what the study's design cannot control for, and what its "
            "findings do and do not generalise.</p>"
            "<p>NurseMyGrade annotated bibliography writers approach each source as a nurse "
            "reading clinical literature for their own practice decisions. They identify "
            "when a study's sample is too small for the effect it claims, when a qualitative "
            "study's transferability is limited by its setting, and when a systematic review "
            "is based on studies with publication bias. That evaluative stance produces "
            "annotations that score marks in the section that most students find hardest "
            "to demonstrate.</p>"
        ),
        _cl("NurseMyGrade Annotated Bibliography Quality Checklist", [
            ("APA 7th citation correctly formatted before each annotation", ""),
            ("Annotation opens with a clear, accurate summary of the source's purpose and findings", ""),
            ("Study design identified and methodological quality evaluated", "RCT, cohort, qualitative, systematic review, etc."),
            ("Sample size adequacy and potential biases noted", ""),
            ("Level of evidence in nursing hierarchy indicated where rubric requires it", ""),
            ("Relevance to your specific research question or PICOT explained", ""),
            ("Annotation length meets rubric requirement (typically 150–300 words per source)", ""),
            ("Sources drawn from peer-reviewed nursing and health databases", ""),
        ]),
        _faq_heading(),
        _faq("How long is each annotation?",
             "<p>Typically 150–300 words per source unless your assignment specifies differently. "
             "Share your rubric and we match the annotation length exactly to your requirements.</p>"),
        _faq("Can you find the sources as well as annotate them?",
             "<p>Yes. If you need sources identified as well as annotated, provide your topic "
             "or PICOT question and required source count. We locate appropriate peer-reviewed "
             "literature and annotate each source.</p>"),
        _faq("Can I supply my own list of sources for annotation?",
             "<p>Yes. Provide your source list (or PDFs where available) and your writer "
             "produces annotations for each source you supply.</p>"),
        _faq("Do you annotate non-nursing sources?",
             "<p>Yes. Nursing research, medical journals, public health, psychology, and any "
             "other discipline your assignment requires. The annotation evaluates each source "
             "on its own methodological terms.</p>"),
        _faq("Do you include a PRISMA diagram for larger annotated bibliographies?",
             "<p>If your annotated bibliography is large enough to constitute a systematic "
             "search (typically 15+ sources from multiple databases), we can include a "
             "PRISMA flow diagram documenting the search and selection process.</p>"),
        _faq("Can you annotate sources for a capstone or dissertation literature review?",
             "<p>Yes. Annotated bibliographies that form the foundation of a capstone or "
             "dissertation literature review are a common request. Annotations are written "
             "at the scholarly level your programme requires.</p>"),
        _faq("What databases do you search?",
             "<p>CINAHL, PubMed, Cochrane Library, MEDLINE, PsycINFO, and any other databases "
             "your topic or faculty specification requires. Search terms and databases used "
             "are documented.</p>"),
        _faq("How fast can you deliver an annotated bibliography?",
             "<p>A 5-source annotated bibliography can typically be completed in 3–6 hours. "
             "Larger bibliographies (10–15 sources) require 12–24 hours depending on "
             "source availability and annotation length.</p>"),
    ],

    # ── 24. Medical Writers for Hire ──────────────────────────────────────────
    "hire-a-health-and-medical-writer": [
        _stats(
            ("Matched by speciality", "not just subject area"),
            ("BSN–DNP–PhD", "credential range"),
            ("All content types", "academic to educational"),
            ("6 hrs", "fastest turnaround"),
        ),
        _h("Why Clients Choose NurseMyGrade When Hiring Health and Medical Writers"),
        _p(
            "<p>The difference between a health writer and a health professional who writes is "
            "substantial—and immediately apparent to a clinical audience. A health writer can "
            "research and accurately paraphrase clinical information. A health professional who "
            "writes brings clinical experience, institutional knowledge, and professional "
            "judgment to the content they produce. When the content is being evaluated by "
            "nurses, physicians, health educators, or clinical examiners, that difference "
            "is what separates acceptable from authoritative.</p>"
            "<p>NurseMyGrade medical and health writers are nurses, advanced practice providers, "
            "and health educators who also write. They hold BSN, MSN, DNP, or PhD credentials "
            "and have been selected for writing quality as well as clinical competence. "
            "Matching is done by clinical speciality and content type: a paediatric nursing "
            "education resource goes to a paediatric nurse with education experience, not to "
            "a generalist health writer. That clinical-to-content alignment is what ensures "
            "the final product is credible to its clinical audience.</p>"
        ),
        _hiw("How We Match You with a Health or Medical Writer", [
            (
                "Share Your Content Requirements",
                "<p>Describe the content type (academic assignment, patient education material, "
                "clinical education resource, or other), the clinical topic, the target audience, "
                "word count, and any style or format requirements.</p>",
            ),
            (
                "Clinical Speciality Matching",
                "<p>Your writer is matched by clinical speciality and content type, not just "
                "subject area. A neonatal nursing case goes to a NICU nurse; an FNP clinical "
                "guide goes to a family nurse practitioner. Speciality knowledge produces "
                "clinically credible content.</p>",
            ),
            (
                "Content Created to Clinical Standard",
                "<p>Academic assignments are written to your programme's level and rubric. "
                "Patient education materials are written in plain language calibrated to health "
                "literacy guidelines. Clinical education content is written to professional "
                "practice standards.</p>",
            ),
            STEP_DELIVER,
        ]),
        _fg("Content Types Our Health Writers Produce", [
            (
                "Academic Nursing Assignments",
                "Essays, care plans, SOAP notes, research papers, capstone projects, dissertations, "
                "and any other nursing academic assignment at BSN through doctoral level. "
                "Written to your programme's standards and your faculty's rubric.",
            ),
            (
                "Patient Education Materials",
                "Discharge instructions, patient handouts, medication guides, health literacy-calibrated "
                "patient information sheets, and condition-specific education resources written "
                "at appropriate reading level (typically 6th–8th grade for patient materials).",
            ),
            (
                "Clinical Education Content",
                "Case scenarios for simulation debriefs, competency assessment tools, clinical "
                "teaching materials, nursing orientation content, and continuing education "
                "materials for nurse educators and clinical educators.",
            ),
        ]),
        _h("Clinical Speciality Matching: Why It Matters"),
        _p(
            "<p>Health writing that lacks clinical speciality grounding shows in the details. "
            "A NICU content piece written by a generalist health writer will use the right "
            "terminology but miss the specific clinical context: the nuance of developmental "
            "care positioning in a 28-weeker, the specific weight thresholds that govern "
            "feeding advancement decisions, the family communication approaches specific "
            "to NICU environments. A reader who has worked in NICU notices these omissions "
            "immediately.</p>"
            "<p>NurseMyGrade speciality matching means the writer assigned to your content "
            "has clinical experience in the area the content covers. This is particularly "
            "important for patient education materials, where clinical accuracy is a safety "
            "issue, and for simulation case scenarios, where clinical realism is required "
            "for the learning objective to work. We do not match by keyword or subject area—"
            "we match by the specific clinical environment and patient population your "
            "content addresses.</p>"
        ),
        _cl("NurseMyGrade Health Writer Quality Checklist", [
            ("Writer matched to your clinical speciality, not just to health generally", ""),
            ("Content type matches writer's production experience (academic, patient education, clinical teaching)", ""),
            ("Clinical terminology accurate and context-appropriate", ""),
            ("Patient education materials written at appropriate reading level (6th–8th grade)", ""),
            ("Academic assignments formatted to programme standards and rubric", ""),
            ("Evidence from peer-reviewed clinical sources where applicable", ""),
            ("Citation style applied correctly (APA, AMA, or other) for academic content", ""),
        ]),
        _faq_heading(),
        _faq("How do you match writers to assignments?",
             "<p>By clinical speciality—a NICU case goes to a neonatal nurse, an FNP SOAP note "
             "goes to a family nurse practitioner, an oncology nursing assignment goes to an "
             "oncology nurse. We match by clinical background, not just subject familiarity.</p>"),
        _faq("Can I view a writer's profile before committing?",
             "<p>Yes. Writer profiles including credentials, clinical specialities, and academic "
             "backgrounds are available. You can request a specific credential level or "
             "speciality in your brief.</p>"),
        _faq("Do you write patient education materials?",
             "<p>Yes. Discharge instructions, patient handouts, medication guides, and condition-specific "
             "patient information sheets written at appropriate health literacy level (typically "
             "6th–8th grade reading level for patient-facing materials).</p>"),
        _faq("Can you help with clinical education content for nurse educators?",
             "<p>Yes. Case scenarios, simulation debriefs, competency assessment tools, clinical "
             "teaching materials, and continuing education content for nurse educators and "
             "clinical education teams.</p>"),
        _faq("Do you write content for nursing orientation programmes?",
             "<p>Yes. New nurse orientation modules, clinical competency checklists, and "
             "skills validation materials for hospital nursing orientation programmes.</p>"),
        _faq("Can you write content across multiple nursing specialities?",
             "<p>Yes. Medical-surgical, critical care, emergency, paediatric, neonatal, "
             "maternal-child, mental health, oncology, community health, and all other "
             "nursing specialities are covered by our multi-speciality writer pool.</p>"),
        _faq("Do you write grant proposals or clinical research summaries?",
             "<p>Grant proposals for nursing research, clinical research summaries for "
             "lay audiences, and policy briefs translating clinical evidence for "
             "non-clinical stakeholders are all supported.</p>"),
        _faq("How fast can you deliver health and medical writing?",
             "<p>Short academic assignments from 6 hours. Patient education materials from "
             "6–12 hours depending on length. Clinical education modules and longer content "
             "require 24–48 hours depending on complexity.</p>"),
    ],

}  # end BODY_BLOCKS

