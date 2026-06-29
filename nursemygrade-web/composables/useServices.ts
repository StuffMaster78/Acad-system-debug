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
    slug: 'online-nursing-essays-help',
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
    relatedSlugs: ['best-online-nursing-research-paper-service', 'nursing-case-study-help', 'nursing-coursework-help-online'],
    meta: {
      title: 'Nursing Essay Writing Service — BSN, MSN & DNP Writers',
      description: 'Custom nursing essays written by qualified nurses. APA 7th, EBP-grounded, plagiarism-free. From $24/page.',
    },
  },
  {
    slug: 'nursing-care-plan-writing-services',
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
    relatedSlugs: ['nursing-soap-note-writing-help', 'nursing-case-study-help', 'online-nursing-essays-help'],
    meta: {
      title: 'Nursing Care Plan Writing Service — NANDA, NIC & NOC',
      description: 'Expert nursing care plan writing using NANDA diagnoses, NIC interventions, and NOC outcomes. Clinically accurate. From $26/page.',
    },
  },
  {
    slug: 'nursing-soap-note-writing-help',
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
    relatedSlugs: ['nursing-care-plan-writing-services', 'nursing-case-study-help', 'online-nursing-essays-help'],
    meta: {
      title: 'SOAP Note Writing Service — Clinical Documentation Help',
      description: 'Accurate SOAP notes written by clinical nursing professionals. All four sections, ICD-10 aware. From $28/page.',
    },
  },
  {
    slug: 'nursing-capstone-project-writing-service',
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
    relatedSlugs: ['nursing-dissertation-writing-service', 'best-online-nursing-research-paper-service', 'nursing-soap-note-writing-help'],
    meta: {
      title: 'Nursing Capstone Project Writing Service — BSN, MSN & DNP',
      description: 'Expert nursing capstone support from PICOT to final paper. BSN, MSN, and DNP levels. From $30/page.',
    },
  },
  {
    slug: 'best-online-nursing-research-paper-service',
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
    relatedSlugs: ['online-nursing-essays-help', 'nursing-capstone-project-writing-service', 'nursing-dissertation-writing-service'],
    meta: {
      title: 'Nursing Research Paper Writing Service — APA 7th Edition',
      description: 'Evidence-based nursing research papers written by qualified nurses. APA 7th, peer-reviewed sources, plagiarism-free. From $24/page.',
    },
  },
  {
    slug: 'nursing-case-study-help',
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
    relatedSlugs: ['nursing-care-plan-writing-services', 'nursing-soap-note-writing-help', 'online-nursing-essays-help'],
    meta: {
      title: 'Nursing Case Study Writing Service — Clinical Reasoning',
      description: 'Expert nursing case study analysis using ADPIE and clinical reasoning. Written by BSN/MSN nurses. From $26/page.',
    },
  },
  {
    slug: 'nursing-dissertation-writing-service',
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
    relatedSlugs: ['nursing-capstone-project-writing-service', 'best-online-nursing-research-paper-service', 'nursing-case-study-help'],
    meta: {
      title: 'Nursing Dissertation Writing Service — DNP & PhD Experts',
      description: 'Expert nursing dissertation writing from proposal to defence. DNP, MSN, and PhD levels. From $32/page.',
    },
  },
  {
    slug: 'concept-map-writing-services',
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
    relatedSlugs: ['nursing-care-plan-writing-services', 'nursing-case-study-help', 'online-nursing-essays-help'],
    meta: {
      title: 'Nursing Concept Map Writing Service — Clinical & Patient Care',
      description: 'Clinically accurate nursing concept maps linking pathophysiology, diagnoses, interventions, and outcomes. From $24/page.',
    },
  },
  {
    slug: 'nursing-coursework-help-online',
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
    relatedSlugs: ['online-nursing-essays-help', 'best-online-nursing-research-paper-service', 'nursing-case-study-help'],
    meta: {
      title: 'Nursing Coursework & Assignment Help from $24/Page',
      description: 'Reliable nursing coursework help — discussions, reflections, pharmacology, and more. From $24/page.',
    },
  },
  {
    slug: 'nursing-class-help-online',
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
    relatedSlugs: ['nursing-coursework-help-online', 'online-nursing-essays-help', 'best-online-nursing-research-paper-service'],
    meta: {
      title: 'Online Nursing Class Help — Full Course Management',
      description: 'Qualified nurses handle your online nursing classes — discussions, quizzes, assignments. Discreet, grade-focused. From $35/page.',
    },
  },
  {
    slug: 'shadow-health-help-online',
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
    relatedSlugs: ['ihuman-help', 'nursing-soap-note-writing-help', 'nursing-care-plan-writing-services'],
    meta: {
      title: 'Shadow Health DCE Help — Tina Jones & All Patients',
      description: 'Expert Shadow Health Digital Clinical Experience completion by practicing nurses. Tina Jones, Brian Foster, all patients. From $35.',
    },
  },
  {
    slug: 'ihuman-help',
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
    relatedSlugs: ['shadow-health-help-online', 'nursing-soap-note-writing-help', 'nursing-case-study-help'],
    meta: {
      title: 'iHuman Virtual Patient Case Help — Clinical Reasoning',
      description: 'Expert iHuman virtual patient case completion by practicing nurses. Clinical reasoning, differentials, treatment plans. From $35.',
    },
  },
  {
    slug: 'ihuman-patients',
    navLabel: 'iHuman Patients',
    icon: 'stethoscope',
    title: 'iHuman Virtual Patient Cases — Nursing Help',
    hero: {
      headline: 'iHuman Patient Cases Completed by Real Nurses',
      sub: 'History, physical exam, ranked differentials, and clinical reasoning for every iHuman virtual patient — handled by nurses who work with these cases clinically.',
    },
    includes: [
      'Patient history and physical examination documentation',
      'Ranked differential diagnoses with clinical rationale',
      'Diagnostic tests ordered with evidence-based justification',
      'Treatment plan and patient education sections',
      'All sections completed to your course rubric',
    ],
    delivers: [
      'Complete iHuman case submission-ready document',
      'Clinical reasoning narrative for each differential',
      'Management and follow-up plan',
      'Turnitin plagiarism report included',
    ],
    whoFor: 'Nursing and NP students working through iHuman virtual patient encounters who need clinically accurate case documentation, differential reasoning, and treatment planning support.',
    priceFrom: 35,
    relatedSlugs: ['ihuman-help', 'shadow-health-help-online', 'nursing-case-study-help'],
    meta: {
      title: 'iHuman Virtual Patient Cases — Nursing Help | NurseMyGrade',
      description: 'Expert iHuman virtual patient case completion. History, differentials, clinical reasoning, and treatment plans — by practicing nurses. From $35.',
    },
  },
  {
    slug: 'nursing-research-for-sale-online',
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
    relatedSlugs: ['online-nursing-essays-help', 'nursing-care-plan-writing-services', 'nursing-coursework-help-online'],
    meta: {
      title: 'Buy Nursing Papers Online — Written by BSN, MSN & DNP Nurses',
      description: 'Buy custom nursing papers written by qualified nurses. Care plans, essays, SOAP notes, capstone projects. Grade guaranteed. From $24/page.',
    },
  },
  {
    slug: 'nursing-report-writing-service',
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
    relatedSlugs: ['nursing-soap-note-writing-help', 'online-nursing-essays-help', 'nursing-case-study-help'],
    meta: {
      title: 'Nursing Report Writing Service — Clinical Documentation Help',
      description: 'Expert nursing report writing — incident reports, SBAR, progress notes, clinical case reports. From $24/page.',
    },
  },
  {
    slug: 'nursing-presentation-writing-service',
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
    relatedSlugs: ['nursing-capstone-project-writing-service', 'online-nursing-essays-help', 'best-online-nursing-research-paper-service'],
    meta: {
      title: 'Nursing Presentation Writing Service — PPT & Speaker Notes',
      description: 'Expert nursing PowerPoint presentations for capstone defence, seminars, and clinical rounds. Evidence-based, APA cited. From $26.',
    },
  },
  {
    slug: 'reliable-and-cheap-bsn-writing-service',
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
    relatedSlugs: ['online-nursing-essays-help', 'nursing-care-plan-writing-services', 'nursing-capstone-project-writing-service'],
    meta: {
      title: 'BSN Nursing Writing Services — Essays, Care Plans & Capstone',
      description: 'Comprehensive writing help for BSN nursing students. Essays, care plans, SOAP notes, capstone projects. From $24/page.',
    },
  },
  {
    slug: 'reliable-msn-writing-services',
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
    relatedSlugs: ['nursing-dissertation-writing-service', 'nursing-capstone-project-writing-service', 'best-online-nursing-research-paper-service'],
    meta: {
      title: 'MSN Nursing Writing Help — Graduate-Level Papers & Capstone',
      description: 'Expert writing support for MSN nursing students. Scholarly papers, NP coursework, policy analysis, capstone. From $32/page.',
    },
  },
  {
    slug: 'apa-format-nursing-paper-writing-service',
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
    relatedSlugs: ['online-nursing-essays-help', 'best-online-nursing-research-paper-service', 'nursing-coursework-help-online'],
    meta: {
      title: 'APA Nursing Paper Writing Service — 7th Edition Formatting',
      description: 'Nursing papers written and formatted in APA 7th edition. All citation types, heading levels, reference lists. From $24/page.',
    },
  },
  {
    slug: 'health-and-medicine-paper-writing-service',
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
    relatedSlugs: ['best-online-nursing-research-paper-service', 'nursing-case-study-help', 'online-nursing-essays-help'],
    meta: {
      title: 'Medical Paper Writing Service — Nursing, Medicine & Health Sciences',
      description: 'Expert medical and health sciences paper writing by clinicians. Nursing, medicine, public health, pharmacy. From $26/page.',
    },
  },
  {
    slug: 'online-nursing-homework-help',
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
    relatedSlugs: ['nursing-coursework-help-online', 'online-nursing-essays-help', 'nursing-case-study-help'],
    meta: {
      title: 'Nursing Homework Help Online — Weekly Assignments & Problems',
      description: 'Get your nursing homework done by a qualified nurse. Discussions, pharmacology, pathophysiology, short assignments. From $24/page.',
    },
  },
  {
    slug: 'postgraduate-nursing-papers-assignments-help',
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
    relatedSlugs: ['reliable-msn-writing-services', 'nursing-dissertation-writing-service', 'nursing-capstone-project-writing-service'],
    meta: {
      title: 'Postgraduate Nursing Writing Help — MSN, DNP & PhD Support',
      description: 'Expert postgraduate nursing writing help. MSN papers, DNP projects, PhD dissertations. Doctoral-level quality. From $32/page.',
    },
  },
  {
    slug: 'hire-a-health-and-medical-writer',
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
    relatedSlugs: ['online-nursing-essays-help', 'health-and-medicine-paper-writing-service', 'best-online-nursing-research-paper-service'],
    meta: {
      title: 'Health & Medical Writers — Credentialed Nursing Professionals',
      description: 'Hire credentialed health and medical writers for academic and educational content. BSN, MSN, DNP writers available. From $24/page.',
    },
  },
  {
    slug: 'nursing-evidence-based-practice',
    navLabel: 'EBP Papers',
    icon: 'search',
    title: 'Evidence-Based Practice (EBP) Nursing Paper Writing Service',
    hero: {
      headline: 'EBP Nursing Papers Built on Current Clinical Evidence',
      sub: 'PICOT-driven evidence-based practice papers, systematic appraisals, and EBP project proposals — written by nurses who apply evidence-based practice every clinical shift.',
    },
    includes: [
      'PICOT question development and refinement',
      'Systematic literature search with inclusion/exclusion criteria',
      'Critical appraisal using validated tools (CASP, JBI)',
      'Evidence synthesis and clinical applicability discussion',
      'APA 7th edition formatting throughout',
    ],
    delivers: [
      'Full EBP paper with PICOT, evidence appraisal, and clinical recommendations',
      'Synthesis table summarising appraised studies',
      'Implications for practice section',
      'Formatted reference list with DOIs',
    ],
    whoFor: 'BSN, MSN, and DNP nursing students who need rigorous EBP papers that demonstrate critical appraisal skills and application of current evidence to clinical practice.',
    priceFrom: 26,
    relatedSlugs: ['nursing-annotated-bibliography', 'best-online-nursing-research-paper-service', 'nursing-capstone-project-writing-service'],
    meta: {
      title: 'Evidence-Based Practice Nursing Paper Writing Service — EBP Help',
      description: 'Expert EBP nursing papers using PICOT, clinical appraisal, and synthesis of current evidence. Written by BSN/MSN nurses. From $26/page.',
    },
  },
  {
    slug: 'nursing-annotated-bibliography',
    navLabel: 'Annotated Bibliography',
    icon: 'book-open',
    title: 'Nursing Annotated Bibliography Writing Service',
    hero: {
      headline: 'Nursing Annotated Bibliographies — Critically Summarised, APA Formatted',
      sub: 'Source-by-source summaries with critical evaluation of relevance, methodology, and clinical applicability — properly formatted in APA 7th edition by nurses who read the literature daily.',
    },
    includes: [
      'Full APA 7th citation for each source',
      'Summary of the source\'s purpose, methodology, and key findings',
      'Critical evaluation of strengths, limitations, and relevance',
      'Commentary on how each source fits your research question',
      'Nursing sources from CINAHL, PubMed, Cochrane',
    ],
    delivers: [
      'Complete annotated bibliography to your required source count',
      'Annotations written in academic nursing language',
      'APA 7th formatted references and annotations',
      'Sources drawn from peer-reviewed nursing literature',
    ],
    whoFor: 'Nursing students who need an annotated bibliography for a research paper, capstone project, or literature review assignment — with genuine critical analysis of each source.',
    priceFrom: 24,
    relatedSlugs: ['nursing-evidence-based-practice', 'best-online-nursing-research-paper-service', 'nursing-capstone-project-writing-service'],
    meta: {
      title: 'Nursing Annotated Bibliography Writing Service — APA 7th Edition',
      description: 'Expert nursing annotated bibliographies with critical summaries and APA 7th citations. Written by qualified nurses. From $24/page.',
    },
  },
  {
    slug: 'online-nursing-papers-writing-service',
    navLabel: 'Nursing Papers',
    icon: 'file-text',
    title: 'Nursing Paper Writing Service',
    hero: {
      headline: 'Dependable Nursing Paper Help — Any Type, Any Deadline',
      sub: 'Essays, research papers, case studies, care plans, and more — written by BSN, MSN, and DNP nurses available 24/7 for urgent and standard deadlines.',
    },
    includes: [
      'Original nursing paper written to your exact brief and rubric',
      'Plagiarism-free with Turnitin report included',
      'APA 7th edition formatting as standard',
      'Editing and paraphrasing available on request',
      'Urgent delivery from 2 hours for qualifying assignments',
    ],
    delivers: [
      'Complete nursing paper to your required length and format',
      'Turnitin similarity report under 5%',
      'Title page, outline, and full reference list',
      'Unlimited free revisions within the revision window',
    ],
    whoFor: 'Nursing students at all academic levels — ADN, RN, BSN, MSN, DNP, PhD — who need reliable, plagiarism-free papers written by qualified nurses on any nursing topic or assignment type.',
    priceFrom: 15,
    relatedSlugs: ['online-nursing-essays-help', 'best-online-nursing-research-paper-service', 'nursing-coursework-help-online'],
    meta: {
      title: 'Nursing Paper Writing Service — Any Type, 24/7 Help',
      description: 'Professional nursing paper writing service. Essays, research papers, case studies, care plans and more — written by BSN/MSN/DNP nurses. From $15/page.',
    },
  },
  {
    slug: 'online-nursing-thesis-writing-helpers',
    navLabel: 'Thesis Help',
    icon: 'graduation-cap',
    title: 'Online Nursing Thesis Writing Service',
    hero: {
      headline: 'MSN & PhD Nursing Thesis Writing — Proposal to Final Chapter',
      sub: 'Structured thesis manuscripts written by masters- and doctoral-prepared nurses who understand graduate-level expectations, committee requirements, and PICOT-grounded research.',
    },
    includes: [
      'Thesis proposal development and problem statement',
      'Literature review with gap analysis and synthesis',
      'Methodology chapter (quantitative, qualitative, or mixed methods)',
      'Data analysis and discussion grounded in nursing theory',
      'APA 7th edition formatting throughout',
    ],
    delivers: [
      'Full thesis manuscript or individual chapters to your schedule',
      'Formatted reference list with DOIs',
      'Free revisions within agreed scope',
      'Turnitin plagiarism report',
    ],
    whoFor: 'MSN and PhD nursing students who need structured, rigorous thesis writing support — from the initial proposal through to final submission and defence preparation.',
    priceFrom: 26,
    relatedSlugs: ['nursing-dissertation-writing-service', 'nursing-capstone-project-writing-service', 'postgraduate-nursing-papers-assignments-help'],
    meta: {
      title: 'Online Nursing Thesis Writing Service — MSN & PhD',
      description: 'Expert nursing thesis writing for MSN and PhD students. Proposal, literature review, methodology, and full manuscripts. From $26/page.',
    },
  },
  {
    slug: 'reliable-nursing-assignment-help',
    navLabel: 'Assignment Help',
    icon: 'clipboard-list',
    title: 'Online Nursing Assignment Help',
    hero: {
      headline: 'Nursing Assignment Help — All Types, All Levels',
      sub: 'From short weekly assignments to complex semester projects — matched with a nurse writer who has completed the same coursework and understands your rubric.',
    },
    includes: [
      'Assignment completed to your exact brief, rubric, and word count',
      'BSN, MSN, or DNP writer matched to your academic level',
      'APA 7th or alternate referencing style on request',
      'Free revisions until all requirements are met',
      '24/7 order tracking and direct writer messaging',
    ],
    delivers: [
      'Completed nursing assignment to required length and format',
      'Full reference list formatted to your style guide',
      'Turnitin plagiarism report',
      'Grade guarantee — full refund if requirements are not met after revisions',
    ],
    whoFor: 'Nursing students at any level who need reliable help with weekly assignments, take-home tests, module papers, or complex coursework — especially those balancing clinicals, work, and study.',
    priceFrom: 15,
    relatedSlugs: ['nursing-coursework-help-online', 'online-nursing-homework-help', 'nursing-care-plan-writing-services'],
    meta: {
      title: 'Online Nursing Assignment Help — Reliable, Fast',
      description: 'Reliable nursing assignment help for all levels. Short assignments to full projects — written by BSN/MSN nurses to your exact rubric. From $15/page.',
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
  meta: { slug: string; type: string; html_url?: string }
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
    return cmsItems.filter(page => page?.meta?.slug).map(page => {
      const slug = page.meta.slug
      const local = staticServices.find(s => s.slug === slug)
      return {
        slug,
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
