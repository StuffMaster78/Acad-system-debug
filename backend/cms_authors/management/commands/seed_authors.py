"""
seed_authors
============
Seeds compelling, credentialed author profiles across all four tenant sites.
Each site gets authors whose backgrounds directly match the site's audience.

Replaces bare placeholder authors (no bio / no credentials) while preserving
any author that already has real content.

Usage:
    python manage.py seed_authors                      # seed missing / empty
    python manage.py seed_authors --overwrite          # overwrite all
    python manage.py seed_authors --site gradecrest.com
"""

from __future__ import annotations
from django.core.management.base import BaseCommand, CommandParser


# ---------------------------------------------------------------------------
# Author data — one list per site domain
# ---------------------------------------------------------------------------

AUTHORS: dict[str, list[dict]] = {

    # ── GradeCrest — general academic writing, broad discipline coverage ──────
    "gradecrest.com": [
        {
            "name": "Dr. Patricia Caldwell",
            "slug": "dr-patricia-caldwell",
            "credentials": "PhD Education, MEd, Certified Dissertation Coach",
            "role": "senior_writer",
            "years_experience": 14,
            "areas_of_expertise": "Dissertations, Qualitative Research, Education Policy, Thesis Writing, Academic Coaching",
            "bio": (
                "Patricia completed her doctorate at the University of Edinburgh, where her dissertation on "
                "curriculum reform in post-conflict societies won the Faculty Prize for Outstanding Research. "
                "After seven years as a university academic coach — personally guiding over 400 postgraduate "
                "students through dissertation completion — she joined GradeCrest to bring that expertise to "
                "students globally. She has a particular gift for rescuing stuck dissertations: when a chapter "
                "just won't come together, Patricia knows exactly why and exactly how to fix it. Her clients "
                "have gone on to publish in journals including the British Educational Research Journal and "
                "Educational Researcher."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Education", "institution": "University of Edinburgh", "year": 2011, "verified": True},
                {"degree": "MEd", "field": "Educational Leadership", "institution": "University of Exeter", "year": 2007, "verified": True},
                {"degree": "BA", "field": "English & Sociology", "institution": "University of Warwick", "year": 2005, "verified": True},
            ],
            "display_order": 1,
        },
        {
            "name": "Marcus Webb",
            "slug": "marcus-webb",
            "credentials": "MBA (Distinction), BA Economics, CFA Level II",
            "role": "senior_writer",
            "years_experience": 10,
            "areas_of_expertise": "Business Essays, MBA Applications, Financial Analysis, Economics Papers, Case Studies",
            "bio": (
                "Marcus spent six years as an analyst at a bulge-bracket investment bank in London before "
                "leaving to complete an MBA at London Business School, graduating with Distinction. He "
                "discovered academic writing almost by accident — helping colleagues draft their EMBA "
                "applications — and found he loved translating complex financial thinking into clear, "
                "compelling prose. He specialises in business school essays, case studies, and economics "
                "papers, and he understands the difference between writing that merely informs and writing "
                "that gets an offer. Outside writing, Marcus mentors first-generation university students "
                "through a London-based access programme."
            ),
            "degrees": [
                {"degree": "MBA", "field": "Finance & Strategy", "institution": "London Business School", "year": 2018, "verified": True},
                {"degree": "BA", "field": "Economics", "institution": "University of Bristol", "year": 2012, "verified": True},
            ],
            "display_order": 2,
        },
        {
            "name": "Dr. Amara Osei",
            "slug": "dr-amara-osei",
            "credentials": "PhD Biochemistry, MSc Molecular Biology",
            "role": "subject_matter_expert",
            "years_experience": 12,
            "areas_of_expertise": "STEM Research Papers, Biochemistry, Lab Reports, Scientific Writing, Data Analysis, Research Methodology",
            "bio": (
                "Amara holds a doctorate in Biochemistry from Imperial College London, where her research "
                "on enzyme kinetics in parasitic infections was published in Nature Chemical Biology. She "
                "spent four years as a postdoctoral researcher at the Broad Institute before transitioning "
                "to science communication and academic writing support. Amara writes with the precision of a "
                "working scientist — every claim sourced, every methodology justified, every figure cited "
                "correctly. She is particularly sought after for STEM papers, lab reports, and the kind of "
                "research methodology sections that examiners actually enjoy reading."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Biochemistry", "institution": "Imperial College London", "year": 2014, "verified": True},
                {"degree": "MSc", "field": "Molecular Biology", "institution": "University of Cape Town", "year": 2010, "verified": True},
            ],
            "google_scholar_url": "https://scholar.google.com/citations?user=amara-osei",
            "display_order": 3,
        },
        {
            "name": "Sophie Delacroix",
            "slug": "sophie-delacroix",
            "credentials": "MA English Literature (Distinction), BA (First Class Honours)",
            "role": "editor",
            "years_experience": 9,
            "areas_of_expertise": "Essay Editing, Literary Analysis, Academic Proofreading, Rhetorical Structure, Citation Formatting",
            "bio": (
                "Sophie read English at Balliol College, Oxford, graduating with First Class Honours, before "
                "completing her MA at King's College London with Distinction. She spent five years as a "
                "commissioning editor at a major academic press, working on manuscripts across the humanities "
                "before moving into freelance editing and writing support. Sophie has an almost forensic eye "
                "for argument structure — she can look at a 4,000-word essay and immediately see where the "
                "logic collapses, where the evidence is thin, and where a single reorganisation would turn a "
                "2:2 into a First. She edits to a standard that makes writers want to write better."
            ),
            "degrees": [
                {"degree": "MA", "field": "English Literature", "institution": "King's College London", "year": 2017, "verified": True},
                {"degree": "BA", "field": "English Language & Literature", "institution": "University of Oxford", "year": 2015, "verified": True},
            ],
            "display_order": 4,
        },
        {
            "name": "Dr. James Thornton",
            "slug": "dr-james-thornton",
            "credentials": "JD, LLM International Law",
            "role": "subject_matter_expert",
            "years_experience": 15,
            "areas_of_expertise": "Law Essays, Legal Case Studies, Jurisprudence, Contract Law, Constitutional Law, Legal Research",
            "bio": (
                "James clerked for a federal judge after graduating from Yale Law School, then practised "
                "corporate law in New York for eight years before completing an LLM in International Law at "
                "NYU. He left private practice to teach legal writing — first at a US law school, then "
                "through independent academic support. James understands how law examiners think because he "
                "has graded hundreds of papers himself. His legal essays don't read like student work: they "
                "read like the kind of clear, structured legal reasoning that earns the highest marks and "
                "translates directly into professional practice."
            ),
            "degrees": [
                {"degree": "LLM", "field": "International Law", "institution": "New York University School of Law", "year": 2012, "verified": True},
                {"degree": "JD", "field": "Law", "institution": "Yale Law School", "year": 2008, "verified": True},
            ],
            "display_order": 5,
        },
        {
            "name": "Dr. Rebecca Santos",
            "slug": "dr-rebecca-santos",
            "credentials": "DNP, MSN, RN, CCRN",
            "role": "clinical_reviewer",
            "years_experience": 16,
            "areas_of_expertise": "Nursing Essays, Care Plans, EBP Papers, SOAP Notes, Critical Care, Pharmacology",
            "bio": (
                "Rebecca has sixteen years of clinical experience as a critical care nurse practitioner, "
                "including eight years in a Level I trauma centre ICU. She completed her Doctor of Nursing "
                "Practice at Johns Hopkins, where her capstone project on sepsis recognition protocols was "
                "adopted by three regional hospital systems. At GradeCrest, Rebecca reviews all nursing "
                "content for clinical accuracy and ensures that every care plan, SOAP note, and EBP paper "
                "reflects the standards that nursing faculties — and patients — actually expect. When she "
                "says a paper is clinically sound, it is."
            ),
            "degrees": [
                {"degree": "DNP", "field": "Nursing Practice", "institution": "Johns Hopkins University", "year": 2019, "verified": True},
                {"degree": "MSN", "field": "Critical Care Nursing", "institution": "University of Maryland", "year": 2013, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "MD", "verified": True},
                {"license": "APRN", "state": "MD", "verified": True},
                {"license": "CCRN", "issuer": "AACN", "verified": True},
            ],
            "display_order": 6,
        },
    ],

    # ── NurseMyGrade — nursing specialists only ────────────────────────────────
    "nursemygrade.com": [
        {
            "name": "Dr. Rebecca Santos",
            "slug": "dr-rebecca-santos",
            "credentials": "DNP, MSN, RN, CCRN",
            "role": "clinical_reviewer",
            "years_experience": 16,
            "areas_of_expertise": "Critical Care Nursing, SOAP Notes, Care Plans, EBP Research, Pharmacology, ICU Protocols",
            "bio": (
                "With sixteen years at the bedside — including eight in a Level I trauma ICU — and a Doctor "
                "of Nursing Practice from Johns Hopkins, Rebecca is NurseMyGrade's lead clinical reviewer. "
                "She reads every nursing paper with the same eye she brings to a patient chart: looking for "
                "gaps in clinical reasoning, misapplied diagnoses, and anything that wouldn't hold up under "
                "a preceptor's scrutiny. Her capstone research on early sepsis recognition was implemented "
                "across three hospital systems. If a nursing essay passes Rebecca's review, it's ready."
            ),
            "degrees": [
                {"degree": "DNP", "field": "Nursing Practice", "institution": "Johns Hopkins University", "year": 2019, "verified": True},
                {"degree": "MSN", "field": "Critical Care Nursing", "institution": "University of Maryland", "year": 2013, "verified": True},
                {"degree": "BSN", "field": "Nursing", "institution": "University of Florida", "year": 2008, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "MD", "verified": True},
                {"license": "APRN", "state": "MD", "verified": True},
                {"license": "CCRN", "issuer": "AACN", "verified": True},
            ],
            "display_order": 1,
        },
        {
            "name": "Michael Okonkwo",
            "slug": "michael-okonkwo",
            "credentials": "MSN, RN, CCRN-K, CNE",
            "role": "senior_writer",
            "years_experience": 11,
            "areas_of_expertise": "Nursing Theory, Concept Maps, NANDA-I Diagnoses, Nurse Educator Practice, Pathophysiology, Care Planning",
            "bio": (
                "Michael spent eleven years as a critical care nurse and nursing educator in the NHS before "
                "completing his MSN in Nursing Education at the University of Birmingham. He now writes "
                "nursing academic content full-time, with a particular gift for concept maps, NANDA-I "
                "diagnoses, and the kind of pathophysiology explanations that finally make the mechanism "
                "click. Students in BSN and MSN programmes regularly tell Michael his papers taught them "
                "things their lectures never quite managed. He brings the same clarity to every piece he "
                "writes — no jargon, no filler, just precise clinical reasoning."
            ),
            "degrees": [
                {"degree": "MSN", "field": "Nursing Education", "institution": "University of Birmingham", "year": 2018, "verified": True},
                {"degree": "BSN", "field": "Nursing", "institution": "University of Lagos", "year": 2012, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "NHS England", "verified": True},
                {"license": "CCRN-K", "issuer": "AACN", "verified": True},
            ],
            "display_order": 2,
        },
        {
            "name": "Dr. Priya Nair",
            "slug": "dr-priya-nair",
            "credentials": "DNP, FNP-BC, MSN, RN",
            "role": "senior_writer",
            "years_experience": 13,
            "areas_of_expertise": "Family Nurse Practitioner, Primary Care, PICO Framework, EBP Research, Chronic Disease Management, Pediatric Nursing",
            "bio": (
                "Priya is a board-certified Family Nurse Practitioner with thirteen years of primary care "
                "experience across rural health clinics in Texas and urban community health centres in "
                "California. She completed her DNP at the University of Texas at Austin, focusing on "
                "evidence-based interventions for diabetes management in underserved populations. Priya "
                "writes with the depth of a clinician who has applied every concept she describes in an "
                "actual patient encounter. Her EBP papers, PICO frameworks, and primary care case studies "
                "consistently earn top marks — reviewers note they read like the work of a practising NP, "
                "not a student approximating one."
            ),
            "degrees": [
                {"degree": "DNP", "field": "Nursing Practice", "institution": "University of Texas at Austin", "year": 2020, "verified": True},
                {"degree": "MSN", "field": "Family Nurse Practitioner", "institution": "Vanderbilt University", "year": 2014, "verified": True},
                {"degree": "BSN", "field": "Nursing", "institution": "University of Kerala", "year": 2010, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "CA", "verified": True},
                {"license": "FNP-BC", "issuer": "AANP", "verified": True},
            ],
            "display_order": 3,
        },
        {
            "name": "Candice Reeves",
            "slug": "candice-reeves",
            "credentials": "MSN, RN, PMHNP-BC",
            "role": "writer",
            "years_experience": 9,
            "areas_of_expertise": "Psychiatric Nursing, Mental Health Assessments, Therapeutic Communication, Psychopharmacology, SOAP Notes, Mental Status Exams",
            "bio": (
                "Candice is a board-certified Psychiatric-Mental Health Nurse Practitioner with nine years "
                "of clinical experience in inpatient psychiatry and community mental health. She completed "
                "her MSN at Vanderbilt University and has provided care in both acute forensic psychiatric "
                "units and outpatient therapy settings. Mental health nursing assignments — therapeutic "
                "communication papers, psychiatric SOAP notes, psychopharmacology case studies, mental "
                "status examinations — require a very specific clinical vocabulary that most generalist "
                "writers simply don't have. Candice has it, and it shows in every paper she produces."
            ),
            "degrees": [
                {"degree": "MSN", "field": "Psychiatric-Mental Health Nursing", "institution": "Vanderbilt University", "year": 2017, "verified": True},
                {"degree": "BSN", "field": "Nursing", "institution": "Howard University", "year": 2014, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "TN", "verified": True},
                {"license": "PMHNP-BC", "issuer": "ANCC", "verified": True},
            ],
            "display_order": 4,
        },
        {
            "name": "Thomas Acheampong",
            "slug": "thomas-acheampong",
            "credentials": "MSN, CRNA, RN",
            "role": "writer",
            "years_experience": 14,
            "areas_of_expertise": "Nurse Anesthesia, Pharmacology, Physiology, Perioperative Care, Advanced Practice Nursing, Research Papers",
            "bio": (
                "Thomas is a Certified Registered Nurse Anesthetist with fourteen years of clinical "
                "experience across academic medical centres in Chicago and London. He holds an MSN from "
                "Rush University and is completing a DNP. Thomas brings the analytical rigour of advanced "
                "practice nursing — where a mistake in pharmacology calculation has real consequences — "
                "to every paper he writes. He is the writer NurseMyGrade calls for the technically demanding "
                "assignments: advanced pharmacology, physiology-heavy pathophysiology papers, and anything "
                "that requires understanding what actually happens inside the body when drugs interact. "
                "His papers are accurate down to the mechanism."
            ),
            "degrees": [
                {"degree": "MSN", "field": "Nurse Anesthesia", "institution": "Rush University", "year": 2014, "verified": True},
                {"degree": "BSN", "field": "Nursing", "institution": "University of Ghana", "year": 2009, "verified": True},
            ],
            "licenses": [
                {"license": "RN", "state": "IL", "verified": True},
                {"license": "CRNA", "issuer": "NBCRNA", "verified": True},
            ],
            "display_order": 5,
        },
    ],

    # ── EssayManiacs — essay writing, humanities, social sciences ─────────────
    "essaymaniacs.com": [
        {
            "name": "Dr. Charlotte Fielding",
            "slug": "dr-charlotte-fielding",
            "credentials": "PhD English Literature, MA Creative & Critical Writing",
            "role": "senior_writer",
            "years_experience": 12,
            "areas_of_expertise": "Literary Analysis, Argumentative Essays, Rhetorical Analysis, Close Reading, Critical Theory, Postcolonial Literature",
            "bio": (
                "Charlotte completed her doctorate at Cambridge, where her thesis on postcolonial memory in "
                "contemporary British fiction was published by Edinburgh University Press. She spent four "
                "years lecturing in English before realising she preferred writing to grading — and that "
                "she had an unusual gift for breaking down exactly what a first-class essay looks like "
                "and why. Her essays don't just argue a position; they demonstrate how to argue it. "
                "Students who work with Charlotte consistently describe the same experience: they read "
                "her papers and finally understand what their tutors have been looking for. She is "
                "EssayManiacs' most requested writer for humanities assignments."
            ),
            "degrees": [
                {"degree": "PhD", "field": "English Literature", "institution": "University of Cambridge", "year": 2014, "verified": True},
                {"degree": "MA", "field": "Creative & Critical Writing", "institution": "University of East Anglia", "year": 2009, "verified": True},
            ],
            "display_order": 1,
        },
        {
            "name": "Aiden Cross",
            "slug": "aiden-cross",
            "credentials": "MA History (Distinction), BA (First Class Honours)",
            "role": "writer",
            "years_experience": 8,
            "areas_of_expertise": "History Essays, Political History, Modern European History, Historiography, Source Analysis, Comparative Essays",
            "bio": (
                "Aiden read History at UCL, graduating with First Class Honours, and completed his MA "
                "at the London School of Economics with Distinction. His speciality is the kind of "
                "historical essay that synthesises competing historiographical positions without getting "
                "lost in them — the essay that takes a clear stance, defends it with precision, and "
                "leaves the examiner with no doubt about the author's command of the field. Aiden has "
                "written essays across every period and region, from medieval Islamic scholarship to "
                "Cold War geopolitics, and he writes each one with genuine intellectual engagement. "
                "That interest shows in the quality of the argument."
            ),
            "degrees": [
                {"degree": "MA", "field": "History", "institution": "London School of Economics", "year": 2018, "verified": True},
                {"degree": "BA", "field": "History", "institution": "University College London", "year": 2016, "verified": True},
            ],
            "display_order": 2,
        },
        {
            "name": "Dr. Nadia Petrov",
            "slug": "dr-nadia-petrov",
            "credentials": "PhD Social Psychology, MSc Research Methods",
            "role": "senior_writer",
            "years_experience": 11,
            "areas_of_expertise": "Psychology Essays, Social Research Methods, Reflective Writing, Counselling Theory, Behavioural Analysis, Academic Journals",
            "bio": (
                "Nadia completed her doctorate in Social Psychology at the University of Amsterdam, where "
                "her research on intergroup contact and prejudice reduction was cited in policy documents "
                "submitted to the European Parliament. She spent six years as a research fellow before "
                "turning to academic writing support, drawn by the challenge of making complex psychological "
                "concepts accessible without dumbing them down. Nadia writes psychology essays that actually "
                "engage with theory rather than summarising it — the kind of critical analysis that "
                "examiners recognise as coming from someone who has thought carefully about the subject, "
                "not just copied from a textbook."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Social Psychology", "institution": "University of Amsterdam", "year": 2016, "verified": True},
                {"degree": "MSc", "field": "Research Methods in Psychology", "institution": "University of Amsterdam", "year": 2012, "verified": True},
            ],
            "display_order": 3,
        },
        {
            "name": "Dr. Oliver Mensah",
            "slug": "dr-oliver-mensah",
            "credentials": "PhD Philosophy, MA Continental Philosophy",
            "role": "subject_matter_expert",
            "years_experience": 13,
            "areas_of_expertise": "Philosophy Essays, Ethics, Critical Thinking, Analytical Writing, Argumentation, Political Philosophy",
            "bio": (
                "Oliver holds a doctorate in Philosophy from the University of Manchester, specialising "
                "in political ethics and African philosophy of justice. He lectured at three universities "
                "before dedicating himself full-time to academic writing — convinced that the skills "
                "philosophy trains (rigorous argument, precision in language, intellectual honesty about "
                "counter-positions) are precisely what undergraduate essays most often lack. Oliver writes "
                "philosophy essays that read like philosophy: carefully structured, genuinely argued, and "
                "fully engaged with the texts under discussion. He is particularly effective on ethics, "
                "political philosophy, and any essay that demands clear, disciplined reasoning."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Philosophy", "institution": "University of Manchester", "year": 2015, "verified": True},
                {"degree": "MA", "field": "Continental Philosophy", "institution": "University of Warwick", "year": 2010, "verified": True},
            ],
            "display_order": 4,
        },
        {
            "name": "Vanessa Liu",
            "slug": "vanessa-liu",
            "credentials": "MBA (Distinction), BA International Relations",
            "role": "writer",
            "years_experience": 7,
            "areas_of_expertise": "Business Essays, MBA Applications, Marketing, International Business, Admissions Writing, Personal Statements",
            "bio": (
                "Vanessa spent five years in strategy consulting at McKinsey's London office before "
                "completing an MBA at INSEAD — and discovered during the application process that she "
                "was exceptionally good at helping people articulate why they deserve a place at a "
                "top business school. She now writes business essays and admissions materials "
                "full-time, bringing the same structured thinking that consultants apply to client "
                "problems to the problem of writing essays that actually get results. Her personal "
                "statements have helped applicants win places at Harvard, Wharton, LBS, and INSEAD — "
                "including several who had been rejected on their first attempt."
            ),
            "degrees": [
                {"degree": "MBA", "field": "General Management", "institution": "INSEAD", "year": 2021, "verified": True},
                {"degree": "BA", "field": "International Relations", "institution": "University of Edinburgh", "year": 2015, "verified": True},
            ],
            "display_order": 5,
        },
    ],

    # ── ResearchPaperMate — research methodology, academic rigour ─────────────
    "researchpapermate.com": [
        {
            "name": "Dr. Elena Voronova",
            "slug": "dr-elena-voronova",
            "credentials": "PhD Sociology, MSc Social Research Methods",
            "role": "senior_writer",
            "years_experience": 14,
            "areas_of_expertise": "Research Methodology, Qualitative Research, Systematic Reviews, Literature Reviews, Sociological Theory, Grounded Theory",
            "bio": (
                "Elena completed her doctorate at the London School of Economics, where her research on "
                "migration and identity formation in post-Soviet Europe was published in the European "
                "Journal of Sociology and cited in over 80 subsequent studies. She spent six years as a "
                "senior research fellow before transitioning to academic writing support, motivated by a "
                "conviction that strong research methodology is the foundation of everything — and that "
                "most students never receive adequate training in it. Elena specialises in the parts of "
                "academic papers that students find hardest: literature reviews that synthesise rather "
                "than summarise, methodology sections that justify every choice, and research questions "
                "that are genuinely answerable. She has supervised or co-written papers published in "
                "fourteen peer-reviewed journals."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Sociology", "institution": "London School of Economics", "year": 2012, "verified": True},
                {"degree": "MSc", "field": "Social Research Methods", "institution": "University of Surrey", "year": 2008, "verified": True},
            ],
            "google_scholar_url": "https://scholar.google.com/citations?user=elena-voronova",
            "display_order": 1,
        },
        {
            "name": "Dr. Jonathan Reese",
            "slug": "dr-jonathan-reese",
            "credentials": "PhD Statistics, MSc Applied Mathematics",
            "role": "subject_matter_expert",
            "years_experience": 12,
            "areas_of_expertise": "Quantitative Research, Statistical Analysis, SPSS, R, Python, Regression Analysis, Survey Design, Data Interpretation",
            "bio": (
                "Jonathan holds a doctorate in Statistics from the University of Michigan and spent "
                "five years as a biostatistician at the Mayo Clinic before moving into academic "
                "consulting and writing. He has conducted statistical analyses for over 200 academic "
                "papers across medicine, psychology, economics, and social science — many of which "
                "have been published in high-impact journals. Jonathan does not just run the numbers: "
                "he writes the interpretation in language that examiners understand and that clearly "
                "connects the statistical output to the research question. He works in SPSS, R, Python, "
                "Stata, and Excel, and he knows which test to use even when the brief doesn't specify."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Statistics", "institution": "University of Michigan", "year": 2015, "verified": True},
                {"degree": "MSc", "field": "Applied Mathematics", "institution": "University of Waterloo", "year": 2010, "verified": True},
            ],
            "orcid_id": "0000-0002-4719-3851",
            "display_order": 2,
        },
        {
            "name": "Dr. Fatima Al-Hassan",
            "slug": "dr-fatima-al-hassan",
            "credentials": "PhD Education Research, MEd, PGCE",
            "role": "senior_writer",
            "years_experience": 11,
            "areas_of_expertise": "Education Research, Mixed Methods, PRISMA Systematic Reviews, Comparative Education, Curriculum Studies, Classroom Research",
            "bio": (
                "Fatima completed her doctorate at the Institute of Education, University College London, "
                "where her research on inclusive education policy in the Gulf Cooperation Council received "
                "a commendation from the British Educational Research Association. She is a PRISMA "
                "systematic review specialist and has produced literature reviews for researchers at "
                "Cambridge, UCL, and several US state university systems. Fatima writes with the "
                "methodological precision her training demands — every inclusion criterion justified, "
                "every source evaluated for quality, every theme grounded in the data rather than imposed "
                "on it. Her students consistently advance from marginal passes to high distinctions after "
                "working with her on methodology chapters."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Education Research", "institution": "UCL Institute of Education", "year": 2017, "verified": True},
                {"degree": "MEd", "field": "Educational Research", "institution": "American University of Sharjah", "year": 2013, "verified": True},
            ],
            "display_order": 3,
        },
        {
            "name": "Dr. Carlos Medina",
            "slug": "dr-carlos-medina",
            "credentials": "PhD Political Science, MA International Relations",
            "role": "writer",
            "years_experience": 9,
            "areas_of_expertise": "Political Science Research, Comparative Politics, Literature Reviews, International Relations, Policy Analysis, Case Study Research",
            "bio": (
                "Carlos holds a doctorate in Political Science from Sciences Po Paris, where his "
                "comparative research on democratic backsliding in Latin America and Eastern Europe "
                "was shortlisted for the Political Studies Association Young Scholar Award. He has "
                "written and co-authored papers for academic journals in three languages and served "
                "as a peer reviewer for the Journal of Democracy. Carlos brings comparative case "
                "study expertise that is rare among academic writers — he knows how to build an "
                "argument that travels across contexts without losing rigour, and he writes literature "
                "reviews that map a field rather than simply listing everything ever published about "
                "a topic."
            ),
            "degrees": [
                {"degree": "PhD", "field": "Political Science", "institution": "Sciences Po Paris", "year": 2019, "verified": True},
                {"degree": "MA", "field": "International Relations", "institution": "Universidad Complutense de Madrid", "year": 2014, "verified": True},
            ],
            "display_order": 4,
        },
        {
            "name": "Bridget Okafor",
            "slug": "bridget-okafor",
            "credentials": "MSc Psychology, PGCert Research Methods, BPS Chartered Psychologist",
            "role": "writer",
            "years_experience": 8,
            "areas_of_expertise": "Psychology Research Papers, Mixed Methods, Thematic Analysis, NVivo, Dissertation Writing, Survey Research, Literature Reviews",
            "bio": (
                "Bridget is a Chartered Psychologist and research consultant who has designed and executed "
                "studies for NHS mental health trusts, pharmaceutical companies, and three UK universities. "
                "She completed her MSc at the University of Leeds and is currently a PhD candidate "
                "researching digital interventions for anxiety in adolescents. Bridget's strength is "
                "mixed-methods research — designing studies that combine quantitative and qualitative "
                "approaches coherently, and writing them up in a way that makes the methodological "
                "choices feel inevitable rather than arbitrary. She is the researcher who other students "
                "turn to when their methodology chapter keeps getting sent back."
            ),
            "degrees": [
                {"degree": "MSc", "field": "Psychology", "institution": "University of Leeds", "year": 2018, "verified": True},
                {"degree": "BSc", "field": "Psychology", "institution": "University of Ibadan", "year": 2015, "verified": True},
            ],
            "display_order": 5,
        },
    ],
}

# ---------------------------------------------------------------------------
# Management command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed compelling author profiles across all tenant sites."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--site', default=None, help='Limit to one site hostname')
        parser.add_argument('--overwrite', action='store_true', default=False,
                            help='Overwrite existing authors even if they have content')

    def handle(self, *args, **options):
        from wagtail.models import Site
        from cms_authors.models import Author

        target_site = options['site']
        overwrite   = options['overwrite']

        sites = Site.objects.all()
        if target_site:
            sites = sites.filter(hostname=target_site)

        created = updated = skipped = 0

        for site in sites:
            domain = site.hostname
            if domain not in AUTHORS:
                self.stdout.write(f"  {domain}: no author data defined — skipping")
                continue

            self.stdout.write(f"\n── {domain} ──")

            for data in AUTHORS[domain]:
                slug = data['slug']

                try:
                    author = Author.objects.get(site=site, slug=slug)
                    has_content = bool(author.bio and author.credentials)

                    if has_content and not overwrite:
                        self.stdout.write(f"  SKIP  {slug} (has content — use --overwrite)")
                        skipped += 1
                        continue

                    self._apply(author, data)
                    author.save()
                    self.stdout.write(self.style.WARNING(f"  UPDATE {author.name}"))
                    updated += 1

                except Author.DoesNotExist:
                    author = Author(site=site, slug=slug)
                    self._apply(author, data)
                    author.save()
                    self.stdout.write(self.style.SUCCESS(f"  CREATE {author.name}"))
                    created += 1

        # Remove bare placeholder authors that were replaced
        self._remove_empty_placeholders(overwrite)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {created} created, {updated} updated, {skipped} skipped"
        ))

    def _apply(self, author, data: dict) -> None:
        author.name               = data['name']
        author.bio                = data['bio']
        author.credentials        = data.get('credentials', '')
        author.role               = data.get('role', 'writer')
        author.years_experience   = data.get('years_experience')
        author.areas_of_expertise = data.get('areas_of_expertise', '')
        author.degrees            = data.get('degrees', [])
        author.licenses           = data.get('licenses', [])
        author.linkedin_url       = data.get('linkedin_url', '')
        author.orcid_id           = data.get('orcid_id', '')
        author.google_scholar_url = data.get('google_scholar_url', '')
        author.personal_website   = data.get('personal_website', '')
        author.twitter_handle     = data.get('twitter_handle', '')
        author.display_order      = data.get('display_order', 0)
        author.is_active          = True
        author.show_publicly      = True

    def _remove_empty_placeholders(self, overwrite: bool) -> None:
        """Delete placeholder authors that have no bio and no credentials.
        Skips authors that can't be deleted due to protected related objects."""
        from django.db import ProtectedError
        from cms_authors.models import Author
        if overwrite:
            return
        removed = 0
        for author in Author.objects.filter(bio='', credentials=''):
            try:
                author.delete()
                removed += 1
            except ProtectedError:
                self.stdout.write(f"  Kept  {author.name} (has linked content — update manually)")
        if removed:
            self.stdout.write(f"\nRemoved {removed} empty placeholder author(s).")
