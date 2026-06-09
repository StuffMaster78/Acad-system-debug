export interface PaperTypeOption   { id: string; label: string; icon: string }
export interface LevelOption       { id: string; label: string; basePrice: number; note: string }
export interface DeadlineOption    { id: string; label: string; sublabel: string; multiplier: number; hours: number; badge?: string }
export interface SubjectOption     { id: string; label: string; category: string }
export interface FormatOption      { id: string; label: string }
export interface WorkTypeOption    { id: string; label: string; desc: string }
export interface OrderTypeOption   { id: string; label: string; desc: string; examples: string; priceFrom: number; color: string; external?: string }
export interface WriterTierOption  { id: string; label: string; desc: string; surcharge: number }

export const ORDER_TYPES: OrderTypeOption[] = [
  {
    id: 'paper',
    label: 'Nursing Paper',
    desc: 'Essays, care plans, SOAP notes, research papers, capstone projects & more',
    examples: 'Care Plan · SOAP Note · Nursing Essay · Research Paper · Dissertation',
    priceFrom: 24,
    color: 'text-brand-600 bg-brand-50 border-brand-200',
  },
  {
    id: 'class',
    label: 'Online Class Help',
    desc: 'Full course management — all assignments, discussions, quizzes & exams',
    examples: 'Full semester · Individual modules · Weekly discussions · Exams',
    priceFrom: 0,
    color: 'text-green-600 bg-green-50 border-green-200',
    external: '/class-support',
  },
  {
    id: 'simulation',
    label: 'Clinical Simulation',
    desc: 'Shadow Health DCEs, iHuman virtual patients & other simulation platforms',
    examples: 'Tina Jones · Brian Foster · iHuman cases · ATI · Kaplan',
    priceFrom: 35,
    color: 'text-rose-600 bg-rose-50 border-rose-200',
    external: '/quote',
  },
  {
    id: 'special',
    label: 'Special / Custom Project',
    desc: 'Unusual brief that needs a tailored quote — multi-part, custom scope',
    examples: 'Multi-part project · Admission essay · Portfolio · Custom research',
    priceFrom: 0,
    color: 'text-amber-600 bg-amber-50 border-amber-200',
    external: '/quote',
  },
]

export const PAPER_TYPES: PaperTypeOption[] = [
  { id: 'care_plan',      label: 'Care Plan',            icon: 'ClipboardList' },
  { id: 'soap_note',      label: 'SOAP Note',            icon: 'Stethoscope'   },
  { id: 'nursing_essay',  label: 'Nursing Essay',        icon: 'PenLine'       },
  { id: 'research_paper', label: 'Research Paper',       icon: 'Microscope'    },
  { id: 'capstone',       label: 'Capstone Project',     icon: 'GraduationCap' },
  { id: 'case_study',     label: 'Case Study',           icon: 'Search'        },
  { id: 'concept_map',    label: 'Concept Map',          icon: 'Network'       },
  { id: 'coursework',     label: 'Coursework',           icon: 'Briefcase'     },
  { id: 'dissertation',   label: 'Dissertation / Thesis',icon: 'BookOpen'      },
  { id: 'discussion',     label: 'Discussion Post',      icon: 'MessageSquare' },
  { id: 'reflection',     label: 'Reflective Journal',   icon: 'FileText'      },
  { id: 'lit_review',     label: 'Literature Review',    icon: 'BookOpen'      },
]

export const ACADEMIC_LEVELS: LevelOption[] = [
  { id: 'adn_lpn',      label: 'ADN / LPN',           basePrice: 24, note: 'Associate degree or practical nursing' },
  { id: 'bsn_1_2',      label: 'BSN Year 1–2',        basePrice: 26, note: 'Freshman / Sophomore nursing' },
  { id: 'bsn_3_4',      label: 'BSN Year 3–4',        basePrice: 28, note: 'Junior / Senior nursing' },
  { id: 'msn',          label: 'MSN / NP Program',    basePrice: 32, note: 'Graduate nursing level' },
  { id: 'dnp_phd',      label: 'DNP / PhD',           basePrice: 38, note: 'Doctoral nursing program' },
]

export const DEADLINES: DeadlineOption[] = [
  { id: 'd_14',  label: '14 days',  sublabel: 'Best price',  multiplier: 1.00, hours: 336 },
  { id: 'd_10',  label: '10 days',  sublabel: '+5%',         multiplier: 1.05, hours: 240 },
  { id: 'd_7',   label: '7 days',   sublabel: '+10%',        multiplier: 1.10, hours: 168 },
  { id: 'd_5',   label: '5 days',   sublabel: '+15%',        multiplier: 1.15, hours: 120 },
  { id: 'd_3',   label: '3 days',   sublabel: '+20%',        multiplier: 1.20, hours: 72  },
  { id: 'd_48',  label: '48 hours', sublabel: '+30%',        multiplier: 1.30, hours: 48  },
  { id: 'd_24',  label: '24 hours', sublabel: '+35%',        multiplier: 1.35, hours: 24, badge: 'Rush' },
  { id: 'd_12',  label: '12 hours', sublabel: '+50%',        multiplier: 1.50, hours: 12, badge: 'Urgent' },
  { id: 'd_6',   label: '6 hours',  sublabel: '+65%',        multiplier: 1.65, hours: 6,  badge: 'Emergency' },
  { id: 'd_3h',  label: '3 hours',  sublabel: '+80%',        multiplier: 1.80, hours: 3,  badge: 'Emergency' },
]

export const SUBJECTS: SubjectOption[] = [
  // Nursing — primary subjects (shown first)
  { id: 'med_surg',        label: 'Medical-Surgical Nursing',      category: 'Nursing' },
  { id: 'pathophysiology', label: 'Pathophysiology',               category: 'Nursing' },
  { id: 'pharmacology',    label: 'Pharmacology',                  category: 'Nursing' },
  { id: 'health_assess',   label: 'Health Assessment',             category: 'Nursing' },
  { id: 'psych_nursing',   label: 'Psychiatric / Mental Health',   category: 'Nursing' },
  { id: 'maternal_child',  label: 'Maternal & Child Health',       category: 'Nursing' },
  { id: 'pediatric',       label: 'Pediatric Nursing',             category: 'Nursing' },
  { id: 'community',       label: 'Community Health Nursing',      category: 'Nursing' },
  { id: 'critical_care',   label: 'Critical Care / ICU',           category: 'Nursing' },
  { id: 'emergency',       label: 'Emergency Nursing',             category: 'Nursing' },
  { id: 'periop',          label: 'Perioperative Nursing',         category: 'Nursing' },
  { id: 'geriatric',       label: 'Geriatric Nursing',             category: 'Nursing' },
  { id: 'oncology',        label: 'Oncology Nursing',              category: 'Nursing' },
  { id: 'leadership',      label: 'Nursing Leadership / Mgmt',     category: 'Nursing' },
  { id: 'informatics',     label: 'Nursing Informatics',           category: 'Nursing' },
  { id: 'ebp',             label: 'Evidence-Based Practice',       category: 'Nursing' },
  { id: 'fundamentals',    label: 'Fundamentals of Nursing',       category: 'Nursing' },
  // Advanced Practice
  { id: 'fnp',             label: 'Family Nurse Practice (FNP)',   category: 'Advanced Practice' },
  { id: 'np_adult',        label: 'Adult-Gero NP',                 category: 'Advanced Practice' },
  { id: 'pmhnp',           label: 'Psychiatric-Mental Health NP',  category: 'Advanced Practice' },
  { id: 'crna',            label: 'CRNA / Anesthesia Nursing',     category: 'Advanced Practice' },
  { id: 'midwifery',       label: 'Nurse Midwifery / CNM',         category: 'Advanced Practice' },
  { id: 'dnp_practice',    label: 'DNP Clinical Practice',         category: 'Advanced Practice' },
  // Allied Health
  { id: 'public_health',   label: 'Public Health',                 category: 'Allied Health' },
  { id: 'nutrition',       label: 'Nutrition / Dietetics',         category: 'Allied Health' },
  { id: 'social_work',     label: 'Social Work',                   category: 'Allied Health' },
  { id: 'psychology',      label: 'Psychology',                    category: 'Allied Health' },
  { id: 'biology',         label: 'Biology / Anatomy',             category: 'Allied Health' },
  { id: 'microbiology',    label: 'Microbiology',                  category: 'Allied Health' },
  // Other Academic
  { id: 'research_methods',label: 'Research Methodology',          category: 'Other' },
  { id: 'statistics',      label: 'Statistics / Biostatistics',    category: 'Other' },
  { id: 'english',         label: 'English / Communications',      category: 'Other' },
  { id: 'other',           label: 'Other (specify in topic)',       category: 'Other' },
]

export const FORMATTING_STYLES: FormatOption[] = [
  { id: 'apa7',      label: 'APA 7th Edition (nursing standard)' },
  { id: 'ama',       label: 'AMA (medical journals)' },
  { id: 'mla9',      label: 'MLA 9th Edition' },
  { id: 'chicago17', label: 'Chicago 17th Edition' },
  { id: 'harvard',   label: 'Harvard' },
  { id: 'vancouver', label: 'Vancouver' },
  { id: 'none',      label: 'Not required / as instructed' },
]

export const WORK_TYPES: WorkTypeOption[] = [
  { id: 'writing',      label: 'Writing',       desc: 'New paper from scratch' },
  { id: 'editing',      label: 'Editing',       desc: 'Improve an existing draft' },
  { id: 'rewriting',    label: 'Rewriting',     desc: 'Rewrite existing content' },
  { id: 'proofreading', label: 'Proofreading',  desc: 'Fix grammar and formatting' },
]

export const ENGLISH_TYPES = [
  { id: 'us', label: 'US English' },
  { id: 'uk', label: 'UK English' },
]

export const WRITER_TIERS: WriterTierOption[] = [
  { id: 'bsn',      label: 'BSN Writer',    desc: 'Verified BSN with clinical experience',    surcharge: 0    },
  { id: 'msn',      label: 'MSN Writer',    desc: 'Master\'s-level nurse, 3+ years writing',  surcharge: 0.10 },
  { id: 'dnp_phd',  label: 'DNP / PhD',     desc: 'Doctoral-level nursing expert',            surcharge: 0.20 },
]

export function useOrderForm() {
  const form = reactive({
    orderType:     ORDER_TYPES[0],
    paperType:     PAPER_TYPES[0],
    level:         ACADEMIC_LEVELS[1],
    pages:         1,
    spacing:       'double' as 'double' | 'single',
    deadline:      DEADLINES[0],
    subject:       SUBJECTS[0],
    writerTier:    WRITER_TIERS[0],
    topic:         '',
    instructions:  '',
    workType:      WORK_TYPES[0],
    formatStyle:   FORMATTING_STYLES[0],
    references:    0,
    englishType:   ENGLISH_TYPES[0],
    discountCode:  '',
    firstName:     '',
    lastName:      '',
    email:         '',
    password:      '',
    agreeToTerms:  false,
  })

  const basePrice = computed(() => form.level.basePrice * form.deadline.multiplier * (1 + form.writerTier.surcharge))
  const unitCount = computed(() => form.pages)
  const unitLabel = computed(() => 'pages')
  const totalPrice = computed(() => Math.ceil(basePrice.value * form.pages))
  const pricePerUnit = computed(() => Math.ceil(basePrice.value))

  const wordCount = computed(() => form.pages * (form.spacing === 'double' ? 275 : 550))

  const deadlineDate = computed(() => {
    const d = new Date()
    d.setHours(d.getHours() + form.deadline.hours)
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  })

  function savePendingOrder() {
    if (!import.meta.client) return
    localStorage.setItem('nmg_pending_order', JSON.stringify({
      orderType:      form.orderType.id,
      paperType:      form.paperType.label,
      level:          form.level.label,
      pages:          form.pages,
      spacing:        form.spacing,
      deadline:       form.deadline.label,
      deadlineHours:  form.deadline.hours,
      subject:        form.subject.label,
      writerTier:     form.writerTier.id,
      topic:          form.topic,
      instructions:   form.instructions,
      workType:       form.workType.label,
      formatStyle:    form.formatStyle.label,
      references:     form.references,
      discountCode:   form.discountCode,
      estimatedPrice: totalPrice.value,
      savedAt:        new Date().toISOString(),
    }))
  }

  const step1Valid = computed(() =>
    !!form.paperType && !!form.level && form.pages >= 1 && !!form.deadline && !!form.subject
  )
  const step2Valid = computed(() =>
    form.topic.trim().length >= 3 && form.instructions.trim().length >= 10
  )
  const step3Valid = computed(() =>
    form.firstName.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && form.agreeToTerms
  )

  return {
    form, totalPrice, pricePerUnit, unitLabel, unitCount,
    wordCount, deadlineDate, step1Valid, step2Valid, step3Valid,
    savePendingOrder,
  }
}
