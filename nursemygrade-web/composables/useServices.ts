export interface ServiceData {
  slug: string
  navLabel: string
  icon: string
  title: string
  hero: { headline: string; sub: string }
  includes: string[]
  delivers: string[]
  whoFor: string
  priceFrom: number
  relatedSlugs: string[]
  meta: { title: string; description: string }
}

const services: ServiceData[] = [
  {
    slug: 'nursing-essays',
    navLabel: 'Nursing Essays',
    icon: 'pen-line',
    title: 'Nursing Essay Writing Service',
    hero: {
      headline: 'Nursing Essays Written by BSN, MSN & DNP Experts',
      sub: 'Reflective, argumentative, and analytical nursing essays grounded in evidence-based practice — APA 7th edition, plagiarism-free, any level.',
    },
    includes: [
      'Written by nurses with BSN, MSN, or DNP credentials',
      'Evidence-based practice (EBP) framework applied',
      'APA 7th edition formatting included',
      'Free Turnitin plagiarism report',
      'Unlimited revisions within review window',
    ],
    delivers: [
      'Strong clinical argument with PICO or NURS framework where relevant',
      'Current peer-reviewed nursing journals cited',
      'Introduction, body, conclusion, and references page',
      'Formatted to your institution\'s style guide',
    ],
    whoFor: 'Nursing students at ADN, BSN, MSN, and DNP level who need a well-argued, clinically grounded essay on any nursing topic.',
    priceFrom: 24,
    relatedSlugs: ['nursing-research-papers', 'nursing-case-studies', 'nursing-coursework'],
    meta: {
      title: 'Nursing Essay Writing Service — BSN, MSN & DNP Writers',
      description: 'Custom nursing essays written by qualified nurses. APA 7th, EBP-grounded, plagiarism-free. From $24/page.',
    },
  },
  {
    slug: 'care-plans',
    navLabel: 'Care Plans',
    icon: 'clipboard-list',
    title: 'Nursing Care Plan Writing Service',
    hero: {
      headline: 'Nursing Care Plans Built on NANDA, NIC & NOC',
      sub: 'Clinically accurate care plans with complete nursing diagnoses, patient goals, and evidence-based interventions — formatted to your programme\'s standards.',
    },
    includes: [
      'NANDA-I approved nursing diagnoses',
      'NIC nursing interventions with rationale',
      'NOC measurable patient outcomes',
      'Assessment, planning, implementation, evaluation (APIE) format',
      'Free revisions',
    ],
    delivers: [
      'Complete care plan for one or multiple nursing diagnoses',
      'Short- and long-term goal statements',
      'Evidence-based nursing interventions with cited rationale',
      'Evaluation criteria and expected outcomes',
    ],
    whoFor: 'BSN and ADN students who need a properly formatted, clinically sound care plan for clinical practicum, simulation labs, or academic submissions.',
    priceFrom: 26,
    relatedSlugs: ['soap-notes', 'nursing-case-studies', 'nursing-essays'],
    meta: {
      title: 'Nursing Care Plan Writing Service — NANDA, NIC & NOC',
      description: 'Expert nursing care plan writing using NANDA diagnoses, NIC interventions, and NOC outcomes. Clinically accurate. From $26/page.',
    },
  },
  {
    slug: 'soap-notes',
    navLabel: 'SOAP Notes',
    icon: 'stethoscope',
    title: 'SOAP Note Writing Service',
    hero: {
      headline: 'SOAP Notes That Meet Clinical Documentation Standards',
      sub: 'Subjective, Objective, Assessment, and Plan sections written by practicing nursing professionals — accurate, concise, and ready for clinical review.',
    },
    includes: [
      'All four SOAP sections: S, O, A, P',
      'Written by clinically experienced nursing writers',
      'ICD-10 coding awareness where applicable',
      'Chief complaint, HPI, ROS, and physical exam sections',
      'Free revisions',
    ],
    delivers: [
      'Complete SOAP note to your patient scenario',
      'Clinically accurate assessment and differential considerations',
      'Evidence-based plan with medication, referral, and follow-up notes',
      'Formatted to your course or clinical site requirements',
    ],
    whoFor: 'NP students, FNP programmes, and advanced practice nursing students who need clinically accurate SOAP notes for coursework or simulation scenarios.',
    priceFrom: 28,
    relatedSlugs: ['care-plans', 'nursing-case-studies', 'nursing-essays'],
    meta: {
      title: 'SOAP Note Writing Service — Clinical Documentation Help',
      description: 'Accurate SOAP notes written by clinical nursing professionals. All four sections, ICD-10 aware. From $28/page.',
    },
  },
  {
    slug: 'capstone-projects',
    navLabel: 'Capstone Projects',
    icon: 'graduation-cap',
    title: 'Nursing Capstone Project Writing Service',
    hero: {
      headline: 'Nursing Capstone Projects from Proposal to Final Submission',
      sub: 'End-to-end capstone support — PICOT question, literature review, evidence appraisal, implementation plan, and DNP or BSN project paper.',
    },
    includes: [
      'PICOT question development',
      'Systematic literature review and evidence appraisal',
      'Project implementation and evaluation plan',
      'DNP project, MSN capstone, and BSN capstone formats',
      'Extended 14-day revision window',
    ],
    delivers: [
      'Full capstone paper or individual chapters',
      'Evidence-based practice framework applied (ACE Star, Iowa, etc.)',
      'Properly formatted with APA 7th edition',
      'IRB and scholarly integrity guidance included',
    ],
    whoFor: 'BSN, MSN, and DNP students who need structured support for their nursing capstone from proposal development through final submission.',
    priceFrom: 30,
    relatedSlugs: ['nursing-dissertations', 'nursing-research-papers', 'soap-notes'],
    meta: {
      title: 'Nursing Capstone Project Writing Service — BSN, MSN & DNP',
      description: 'Expert nursing capstone support from PICOT to final paper. BSN, MSN, and DNP levels. From $30/page.',
    },
  },
  {
    slug: 'nursing-research-papers',
    navLabel: 'Research Papers',
    icon: 'microscope',
    title: 'Nursing Research Paper Writing Service',
    hero: {
      headline: 'Nursing Research Papers Grounded in Current Evidence',
      sub: 'Quantitative, qualitative, and mixed-methods nursing research papers — built on peer-reviewed journals, properly cited in APA 7th or other required styles.',
    },
    includes: [
      'Current peer-reviewed nursing and medical journals sourced',
      'Quantitative, qualitative, or mixed-methods approach',
      'APA 7th edition (or AMA, MLA, Chicago)',
      'Free Turnitin plagiarism report',
      'Unlimited revisions',
    ],
    delivers: [
      'Structured introduction, literature review, methodology, results, discussion',
      'PICOT or research question clearly stated',
      'Annotated bibliography available on request',
      'Full reference list and in-text citations',
    ],
    whoFor: 'Nursing students from ADN through DNP who need a well-structured, evidence-based research paper on any clinical or nursing theory topic.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'capstone-projects', 'nursing-dissertations'],
    meta: {
      title: 'Nursing Research Paper Writing Service — APA 7th Edition',
      description: 'Evidence-based nursing research papers written by qualified nurses. APA 7th, peer-reviewed sources, plagiarism-free. From $24/page.',
    },
  },
  {
    slug: 'nursing-case-studies',
    navLabel: 'Case Studies',
    icon: 'search',
    title: 'Nursing Case Study Writing Service',
    hero: {
      headline: 'Nursing Case Studies That Think Like a Clinician',
      sub: 'Patient scenario analysis with nursing diagnosis, clinical reasoning, evidence-based interventions, and outcome evaluation — written by nurses who\'ve been there.',
    },
    includes: [
      'Patient scenario analysis using clinical reasoning frameworks',
      'Nursing diagnoses and priority setting',
      'Evidence-based intervention with rationale',
      'Legal, ethical, and cultural considerations',
      'Free revisions',
    ],
    delivers: [
      'Full case study in your programme\'s required format',
      'Assessment, diagnosis, planning, implementation, evaluation (ADPIE)',
      'Cited evidence from current nursing literature',
      'Reflection section where required',
    ],
    whoFor: 'Nursing students who need rigorous clinical case study analysis that demonstrates critical thinking, clinical judgment, and evidence-based practice.',
    priceFrom: 26,
    relatedSlugs: ['care-plans', 'soap-notes', 'nursing-essays'],
    meta: {
      title: 'Nursing Case Study Writing Service — Clinical Reasoning',
      description: 'Expert nursing case study analysis using ADPIE and clinical reasoning. Written by BSN/MSN nurses. From $26/page.',
    },
  },
  {
    slug: 'nursing-dissertations',
    navLabel: 'Dissertations',
    icon: 'book-open',
    title: 'Nursing Dissertation & Thesis Writing Service',
    hero: {
      headline: 'Nursing Dissertations Written by DNP & PhD-Level Experts',
      sub: 'Chapter-by-chapter dissertation support — from proposal and PICOT to methodology, findings, and defence preparation.',
    },
    includes: [
      'DNP project, MSN thesis, and PhD dissertation support',
      'PICOT development and research design consultation',
      'Chapter-by-chapter delivery with review cycles',
      'Supervisor feedback integration',
      'Extended 21-day revision window',
    ],
    delivers: [
      'Full dissertation or individual chapters',
      'Properly designed methodology (qualitative, quantitative, mixed)',
      'Data analysis with interpretation',
      'APA 7th formatted bibliography',
    ],
    whoFor: 'MSN and DNP students who need expert-level support for their nursing dissertation or doctoral project — from concept through final submission.',
    priceFrom: 32,
    relatedSlugs: ['capstone-projects', 'nursing-research-papers', 'nursing-case-studies'],
    meta: {
      title: 'Nursing Dissertation Writing Service — DNP & PhD Experts',
      description: 'Expert nursing dissertation writing from proposal to defence. DNP, MSN, and PhD levels. From $32/page.',
    },
  },
  {
    slug: 'concept-maps',
    navLabel: 'Concept Maps',
    icon: 'network',
    title: 'Nursing Concept Map Writing Service',
    hero: {
      headline: 'Nursing Concept Maps That Connect the Clinical Picture',
      sub: 'Visually clear, clinically accurate concept maps linking pathophysiology, nursing diagnoses, interventions, and outcomes — for any patient scenario.',
    },
    includes: [
      'Pathophysiology to nursing diagnosis linkage',
      'Priority nursing diagnoses ranked',
      'Evidence-based interventions mapped',
      'Expected outcomes and evaluation criteria',
      'Free revisions',
    ],
    delivers: [
      'Completed concept map in your programme\'s preferred format',
      'Written rationale for each link and intervention',
      'Colour-coded or structured diagram as required',
      'Supporting reference list',
    ],
    whoFor: 'ADN and BSN students who need concept maps for clinical courses, simulation prep, or medication management assignments.',
    priceFrom: 24,
    relatedSlugs: ['care-plans', 'nursing-case-studies', 'nursing-essays'],
    meta: {
      title: 'Nursing Concept Map Writing Service — Clinical & Patient Care',
      description: 'Clinically accurate nursing concept maps linking pathophysiology, diagnoses, interventions, and outcomes. From $24/page.',
    },
  },
  {
    slug: 'nursing-coursework',
    navLabel: 'Coursework & Assignments',
    icon: 'briefcase',
    title: 'Nursing Coursework & Assignment Help',
    hero: {
      headline: 'Consistent Nursing Assignment Help, Every Week',
      sub: 'Weekly discussions, reflection journals, pharmacology assignments, and module work handled by the same nursing writer who knows your course.',
    },
    includes: [
      'Discussion board posts and responses',
      'Reflective practice journals (Gibbs, Johns, Driscoll)',
      'Pharmacology and pathophysiology assignments',
      'Short and extended nursing assignments',
      'Free revisions',
    ],
    delivers: [
      'Completed assignment to your brief and rubric',
      'Evidence-based content with current nursing sources',
      'APA 7th formatted references',
      'On-time delivery guaranteed',
    ],
    whoFor: 'Nursing students managing heavy coursework loads — ADN through DNP — who need reliable, expert weekly help across one or more modules.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'nursing-research-papers', 'nursing-case-studies'],
    meta: {
      title: 'Nursing Coursework & Assignment Help from $24/Page',
      description: 'Reliable nursing coursework help — discussions, reflections, pharmacology, and more. From $24/page.',
    },
  },
  {
    slug: 'online-nursing-classes',
    navLabel: 'Online Class Help',
    icon: 'laptop',
    title: 'Online Nursing Class Help',
    hero: {
      headline: 'Let a Nursing Expert Handle Your Online Classes',
      sub: 'Full online nursing course management — discussions, quizzes, exams, and assignments — handled by a qualified nurse so you can focus on clinical hours.',
    },
    includes: [
      'Full course or individual module management',
      'Discussion posts, peer responses, and weekly assignments',
      'Proctored and unproctored quiz/exam support',
      'Pharmacology, pathophysiology, mental health, and all nursing subjects',
      'Dedicated writer for the duration of the course',
    ],
    delivers: [
      'All weekly submissions completed on time',
      'Grade-conscious approach — your rubric is our standard',
      'Regular progress updates throughout the course',
      'Confidential and discreet handling',
    ],
    whoFor: 'Nursing students who are overwhelmed by multiple online courses and need a qualified nursing professional to manage coursework while they complete clinical rotations.',
    priceFrom: 35,
    relatedSlugs: ['nursing-coursework', 'nursing-essays', 'nursing-research-papers'],
    meta: {
      title: 'Online Nursing Class Help — Full Course Management',
      description: 'Qualified nurses handle your online nursing classes — discussions, quizzes, assignments. Discreet, grade-focused. From $35/page.',
    },
  },
  {
    slug: 'shadow-health',
    navLabel: 'Shadow Health DCEs',
    icon: 'monitor-play',
    title: 'Shadow Health Digital Clinical Experience Help',
    hero: {
      headline: 'Shadow Health DCEs Completed by Practicing Nurses',
      sub: 'Digital Clinical Experiences — Tina, Brian, Danny, and all Shadow Health patients — documented accurately and professionally by nurses who know the platform inside out.',
    },
    includes: [
      'All Shadow Health patient encounters: Tina Jones, Brian Foster, Danny Rivera, and more',
      'Subjective, Objective, Assessment, Plan documentation for each DCE',
      'Education section, reflection, and evidence-based rationale included',
      'Scored to meet your programme\'s passing threshold',
      'Completed within your deadline — usually same-day',
    ],
    delivers: [
      'Completed DCE documentation submitted on your behalf or as a reference',
      'Health history, physical exam, and clinical reasoning sections',
      'SBAR or clinical note format where required',
      'Full reflection and self-evaluation sections',
    ],
    whoFor: 'Nursing students enrolled in programmes using Shadow Health — ADN, BSN, MSN, and NP students struggling with DCE time demands or clinical reasoning documentation.',
    priceFrom: 35,
    relatedSlugs: ['ihuman-patients', 'soap-notes', 'care-plans'],
    meta: {
      title: 'Shadow Health DCE Help — Tina Jones & All Patients',
      description: 'Expert Shadow Health Digital Clinical Experience completion by practicing nurses. Tina Jones, Brian Foster, all patients. From $35.',
    },
  },
  {
    slug: 'ihuman-patients',
    navLabel: 'iHuman Virtual Patients',
    icon: 'activity',
    title: 'iHuman Virtual Patient Case Help',
    hero: {
      headline: 'iHuman Cases Completed by Clinical Nursing Experts',
      sub: 'Virtual patient encounters on iHuman require clinical reasoning, differential diagnosis, and evidence-based decision-making — our nurses have done hundreds of these.',
    },
    includes: [
      'Full iHuman patient case completion — history, physical, assessment',
      'Differential diagnosis with evidence-based rationale',
      'Diagnostic reasoning and clinical decision-making documentation',
      'Treatment plan and patient education sections',
      'Completed within your deadline',
    ],
    delivers: [
      'All iHuman case sections completed to your rubric',
      'Clinical reasoning narrative with supporting evidence',
      'Differential diagnoses ranked with rationale',
      'Follow-up and management plan',
    ],
    whoFor: 'Nursing and NP students using the iHuman platform for virtual patient encounters who need support with clinical reasoning documentation and case completion.',
    priceFrom: 35,
    relatedSlugs: ['shadow-health', 'soap-notes', 'nursing-case-studies'],
    meta: {
      title: 'iHuman Virtual Patient Case Help — Clinical Reasoning',
      description: 'Expert iHuman virtual patient case completion by practicing nurses. Clinical reasoning, differentials, treatment plans. From $35.',
    },
  },
  {
    slug: 'buy-nursing-papers',
    navLabel: 'Buy Nursing Papers',
    icon: 'file-text',
    title: 'Buy Nursing Papers Online — Written by Real Nurses',
    hero: {
      headline: 'Buy Nursing Papers Written by BSN, MSN & DNP Nurses',
      sub: 'Every nursing paper we write is original, clinically grounded, and delivered on time. From care plans to dissertations — all nursing paper types available.',
    },
    includes: [
      'All nursing paper types: essays, care plans, SOAP notes, capstone projects',
      'Written by credentialed nurses with active clinical experience',
      'APA 7th edition formatting as standard',
      'Free Turnitin plagiarism report included',
      'Grade or money-back guarantee on every order',
    ],
    delivers: [
      'Completed nursing paper written to your exact brief',
      'Clinically accurate content sourced from peer-reviewed nursing literature',
      'Free plagiarism report verifying originality',
      'On-time delivery guaranteed',
    ],
    whoFor: 'Nursing students at any level — ADN through DNP — who need a reliable, clinically grounded nursing paper written by a qualified nurse.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'care-plans', 'nursing-coursework'],
    meta: {
      title: 'Buy Nursing Papers Online — Written by BSN, MSN & DNP Nurses',
      description: 'Buy custom nursing papers written by qualified nurses. Care plans, essays, SOAP notes, capstone projects. Grade guaranteed. From $24/page.',
    },
  },
  {
    slug: 'nursing-report',
    navLabel: 'Nursing Reports',
    icon: 'file-text',
    title: 'Nursing Report Writing Service',
    hero: {
      headline: 'Nursing Reports Written to Clinical Documentation Standards',
      sub: 'Incident reports, shift handover reports, patient progress notes, and clinical case reports — written by experienced nurses who know how documentation works in practice.',
    },
    includes: [
      'Incident reports, progress notes, and shift summaries',
      'Clinical case reports and patient documentation',
      'SBAR-format reports and handover notes',
      'Written by BSN/MSN nurses with documentation experience',
      'Free revisions within review window',
    ],
    delivers: [
      'Complete nursing report to your brief and format',
      'Clear, concise clinical language throughout',
      'Properly structured sections per report type',
      'References cited in APA 7th where required',
    ],
    whoFor: 'Nursing students who need help writing clinical reports, incident documentation, or case reports for academic submission or portfolio development.',
    priceFrom: 24,
    relatedSlugs: ['soap-notes', 'nursing-essays', 'nursing-case-studies'],
    meta: {
      title: 'Nursing Report Writing Service — Clinical Documentation Help',
      description: 'Expert nursing report writing — incident reports, SBAR, progress notes, clinical case reports. From $24/page.',
    },
  },
  {
    slug: 'nursing-presentation',
    navLabel: 'Nursing Presentations',
    icon: 'monitor-play',
    title: 'Nursing Presentation (PPT) Writing Service',
    hero: {
      headline: 'Nursing Presentations That Communicate Clinical Evidence Clearly',
      sub: 'PowerPoint slides for nursing seminars, capstone defence, clinical case presentations, and journal club — structured, evidence-based, and professionally formatted.',
    },
    includes: [
      'Slide-by-slide content development',
      'Speaker notes for every slide',
      'Evidence-based clinical content with APA-cited sources',
      'Designed for capstone defence, seminar, or clinical rounds',
      'Free revisions',
    ],
    delivers: [
      'Complete PowerPoint presentation to your brief',
      'Structured narrative flow from problem to conclusion',
      'Data visualisations, tables, and clinical images guidance',
      'Speaker notes timed to your presentation slot',
    ],
    whoFor: 'Nursing students preparing for capstone defence presentations, clinical case rounds, seminar presentations, or journal club facilitation.',
    priceFrom: 26,
    relatedSlugs: ['capstone-projects', 'nursing-essays', 'nursing-research-papers'],
    meta: {
      title: 'Nursing Presentation Writing Service — PPT & Speaker Notes',
      description: 'Expert nursing PowerPoint presentations for capstone defence, seminars, and clinical rounds. Evidence-based, APA cited. From $26.',
    },
  },
  {
    slug: 'bsn-writing',
    navLabel: 'BSN Writing Services',
    icon: 'graduation-cap',
    title: 'BSN Nursing Writing Services',
    hero: {
      headline: 'Writing Services Built Specifically for BSN Students',
      sub: 'From first-year fundamentals essays to senior capstone projects — every BSN writing assignment handled by qualified nurses who understand what your programme expects.',
    },
    includes: [
      'All BSN-level assignments: essays, care plans, SOAP notes, capstone',
      'Writers who hold BSN credentials and understand programme expectations',
      'APA 7th edition formatting throughout',
      'NANDA, NIC, NOC, and ADPIE frameworks applied correctly',
      'Free Turnitin report and unlimited revisions',
    ],
    delivers: [
      'Complete assignment written to your rubric and programme level',
      'Clinically grounded content appropriate to BSN competency',
      'Properly cited peer-reviewed nursing sources',
      'Grade or money back guarantee',
    ],
    whoFor: 'BSN nursing students at any year who need reliable academic writing support — from fundamentals in Year 1 to capstone projects in Year 4.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'care-plans', 'capstone-projects'],
    meta: {
      title: 'BSN Nursing Writing Services — Essays, Care Plans & Capstone',
      description: 'Comprehensive writing help for BSN nursing students. Essays, care plans, SOAP notes, capstone projects. From $24/page.',
    },
  },
  {
    slug: 'msn-help',
    navLabel: 'MSN Writing Help',
    icon: 'book-open',
    title: 'MSN Nursing Writing Help',
    hero: {
      headline: 'Advanced Writing Support for MSN Students and NP Programmes',
      sub: 'Literature reviews, scholarly papers, policy analyses, clinical practicums, and MSN capstone projects — written by DNP and PhD-credentialed nursing faculty.',
    },
    includes: [
      'MSN-level scholarly papers and advanced clinical writing',
      'Literature reviews with systematic search strategy',
      'Policy analysis and healthcare leadership papers',
      'NP coursework: SOAP notes, clinical logs, case presentations',
      'Extended revision window for complex projects',
    ],
    delivers: [
      'Scholarly writing at graduate nursing level',
      'Synthesis of peer-reviewed nursing and healthcare literature',
      'APA 7th formatted with graduate-level academic rigour',
      'Original analysis and evidence-based argumentation',
    ],
    whoFor: 'MSN students in clinical speciality, nurse educator, nurse leader, or NP programmes who need expert-level writing support for graduate coursework and programme requirements.',
    priceFrom: 32,
    relatedSlugs: ['nursing-dissertations', 'capstone-projects', 'nursing-research-papers'],
    meta: {
      title: 'MSN Nursing Writing Help — Graduate-Level Papers & Capstone',
      description: 'Expert writing support for MSN nursing students. Scholarly papers, NP coursework, policy analysis, capstone. From $32/page.',
    },
  },
  {
    slug: 'apa-nursing-papers',
    navLabel: 'APA Nursing Papers',
    icon: 'clipboard-list',
    title: 'APA Nursing Paper Writing Service',
    hero: {
      headline: 'Nursing Papers Written and Formatted in APA 7th Edition',
      sub: 'Every nursing paper we write follows APA 7th edition — in-text citations, reference lists, headings, tables, and figures — all correctly formatted by writers who use it daily.',
    },
    includes: [
      'APA 7th edition formatting throughout — headings, margins, spacing',
      'In-text citations and reference list correctly formatted',
      'DOI hyperlinks, journal italics, and author formats correct',
      'Free plagiarism report confirming originality',
      'Free revisions for any APA formatting corrections',
    ],
    delivers: [
      'Fully APA 7th formatted nursing paper',
      'Title page, abstract (if required), and references page',
      'Correct running head (if required by your programme)',
      'Level 1–3 headings consistently applied',
    ],
    whoFor: 'Nursing students who need a properly APA-formatted paper — or who have written a draft that needs expert APA formatting review and correction.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'nursing-research-papers', 'nursing-coursework'],
    meta: {
      title: 'APA Nursing Paper Writing Service — 7th Edition Formatting',
      description: 'Nursing papers written and formatted in APA 7th edition. All citation types, heading levels, reference lists. From $24/page.',
    },
  },
  {
    slug: 'medical-paper-writing',
    navLabel: 'Medical Paper Writing',
    icon: 'microscope',
    title: 'Medical & Health Sciences Paper Writing Service',
    hero: {
      headline: 'Medical Papers Written by Healthcare Professionals',
      sub: 'Research papers, case studies, and academic assignments across medicine, public health, pharmacy, and allied health — written by clinically experienced professionals.',
    },
    includes: [
      'Medical research papers, case reports, and literature reviews',
      'Public health, pharmacology, and health sciences assignments',
      'APA, AMA, Vancouver, or Chicago citation as required',
      'Written by nurses, clinicians, and healthcare professionals',
      'Free plagiarism report included',
    ],
    delivers: [
      'Complete medical or health sciences paper to your brief',
      'Clinically accurate content with peer-reviewed medical sources',
      'Correctly formatted references and in-text citations',
      'Appropriate medical terminology and clinical reasoning',
    ],
    whoFor: 'Students in nursing, medicine, public health, pharmacy, and allied health disciplines who need expert clinical writing for academic assignments.',
    priceFrom: 26,
    relatedSlugs: ['nursing-research-papers', 'nursing-case-studies', 'nursing-essays'],
    meta: {
      title: 'Medical Paper Writing Service — Nursing, Medicine & Health Sciences',
      description: 'Expert medical and health sciences paper writing by clinicians. Nursing, medicine, public health, pharmacy. From $26/page.',
    },
  },
  {
    slug: 'nursing-homework',
    navLabel: 'Nursing Homework Help',
    icon: 'briefcase',
    title: 'Nursing Homework Help Online',
    hero: {
      headline: 'Nursing Homework Done by a Qualified Nurse Tonight',
      sub: 'Short weekly assignments, discussion posts, pathophysiology problems, pharmacology calculations, and any other nursing homework — handled by a BSN/MSN nurse who knows your subject.',
    },
    includes: [
      'Weekly discussion posts and peer responses',
      'Short nursing assignments and homework problems',
      'Pharmacology and pathophysiology questions',
      'Concept questions, quizzes, and worksheet assistance',
      'Fast turnaround — as little as 3 hours for short tasks',
    ],
    delivers: [
      'Completed homework to your rubric and brief',
      'Evidence-based answers with appropriate citations',
      'APA 7th formatted references where required',
      'Submitted within your deadline',
    ],
    whoFor: 'Nursing students who need reliable weekly homework help across any nursing subject — from fundamentals to advanced pathophysiology and pharmacology.',
    priceFrom: 24,
    relatedSlugs: ['nursing-coursework', 'nursing-essays', 'nursing-case-studies'],
    meta: {
      title: 'Nursing Homework Help Online — Weekly Assignments & Problems',
      description: 'Get your nursing homework done by a qualified nurse. Discussions, pharmacology, pathophysiology, short assignments. From $24/page.',
    },
  },
  {
    slug: 'postgrad-nursing',
    navLabel: 'Postgrad Nursing Help',
    icon: 'graduation-cap',
    title: 'Postgraduate Nursing Writing Help',
    hero: {
      headline: 'Expert Writing Support for MSN, DNP & PhD Nursing Students',
      sub: 'Postgraduate nursing demands graduate-level clinical reasoning and academic writing. Our DNP and PhD-credentialed writers provide the scholarly depth your programme expects.',
    },
    includes: [
      'MSN, DNP, and PhD-level nursing papers and projects',
      'Doctoral-level clinical reasoning and evidence synthesis',
      'Capstone projects, dissertations, and scholarly papers',
      'Policy analysis, quality improvement, and leadership papers',
      'Extended revision window for complex postgraduate work',
    ],
    delivers: [
      'Graduate or doctoral-level writing with appropriate rigour',
      'Synthesis of primary and secondary nursing literature',
      'Properly structured scholarly argument throughout',
      'APA 7th formatted with full reference list',
    ],
    whoFor: 'MSN, DNP, and PhD nursing students who need doctoral-calibre writing support — from coursework papers through dissertation chapters and scholarly projects.',
    priceFrom: 32,
    relatedSlugs: ['msn-help', 'nursing-dissertations', 'capstone-projects'],
    meta: {
      title: 'Postgraduate Nursing Writing Help — MSN, DNP & PhD Support',
      description: 'Expert postgraduate nursing writing help. MSN papers, DNP projects, PhD dissertations. Doctoral-level quality. From $32/page.',
    },
  },
  {
    slug: 'health-medical-writers',
    navLabel: 'Health & Medical Writers',
    icon: 'stethoscope',
    title: 'Health & Medical Writers for Hire',
    hero: {
      headline: 'Credentialed Health and Medical Writers Available Now',
      sub: 'BSN, MSN, DNP, and PhD-credentialed health professionals who write — for academic assignments, clinical education content, and health communications.',
    },
    includes: [
      'Nursing and medical academic writing at all levels',
      'Health communications, patient education, and clinical guides',
      'Public health, pharmacology, and health policy content',
      'Writers matched by clinical speciality — not just subject area',
      'Free revisions and plagiarism report with every assignment',
    ],
    delivers: [
      'Clinically accurate, professionally written content',
      'Evidence from peer-reviewed nursing and medical literature',
      'APA, AMA, or other required citation style',
      'Completed to your brief and submission deadline',
    ],
    whoFor: 'Students, healthcare educators, and professionals who need credentialed health and nursing writers for academic or educational content.',
    priceFrom: 24,
    relatedSlugs: ['nursing-essays', 'medical-paper-writing', 'nursing-research-papers'],
    meta: {
      title: 'Health & Medical Writers — Credentialed Nursing Professionals',
      description: 'Hire credentialed health and medical writers for academic and educational content. BSN, MSN, DNP writers available. From $24/page.',
    },
  },
]

export function useServices() {
  function getAll() {
    return services
  }

  function getBySlug(slug: string) {
    return services.find(s => s.slug === slug) ?? null
  }

  function getRelated(slugs: string[]) {
    return services.filter(s => slugs.includes(s.slug))
  }

  return { getAll, getBySlug, getRelated }
}

export interface CmsServiceSummary {
  id: number
  title: string
  slug: string
  service_category?: { name: string; slug: string } | null
  pricing_from?: string | null
  turnaround_hours_fastest?: number | null
}

export function useCmsServiceList() {
  const config = useRuntimeConfig()
  const { data } = useFetch<{ items: CmsServiceSummary[] }>('/api/v2/pages/', {
    key: 'cms-service-list',
    baseURL: String(config.public.apiBase || ''),
    query: {
      type: 'cms_service_pages.ServicePage',
      live: true,
      order: 'title',
      fields: 'title,slug,service_category,pricing_from,turnaround_hours_fastest',
      limit: 50,
    },
    default: () => ({ items: [] }),
  })

  const staticServices = services

  const merged = computed(() => {
    const cmsItems = data.value?.items ?? []
    if (!cmsItems.length) {
      return staticServices.map(s => ({
        slug: s.slug,
        title: s.title,
        navLabel: s.navLabel,
        icon: s.icon,
        heroSub: s.hero.sub,
        priceFrom: s.priceFrom,
        category: null as string | null,
      }))
    }
    return cmsItems.map(page => {
      const local = staticServices.find(s => s.slug === page.slug)
      return {
        slug: page.slug,
        title: page.title,
        navLabel: local?.navLabel ?? page.title,
        icon: local?.icon ?? 'file-text',
        heroSub: local?.hero.sub ?? '',
        priceFrom: page.pricing_from ? parseFloat(page.pricing_from) : (local?.priceFrom ?? 24),
        category: page.service_category?.name ?? null,
      }
    })
  })

  return merged
}
