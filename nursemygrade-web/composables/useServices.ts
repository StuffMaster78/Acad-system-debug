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
    icon: '✍️',
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
    icon: '🩺',
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
    icon: '📋',
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
    icon: '🎓',
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
    icon: '📄',
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
    icon: '🔬',
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
    icon: '📚',
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
    icon: '🗺️',
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
    icon: '📓',
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
    icon: '💻',
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
  const { data } = useFetch<{ items: CmsServiceSummary[] }>('/api/v2/pages/', {
    key: 'cms-service-list',
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
