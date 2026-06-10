export interface PaperTypeOption   { id: string; label: string; icon: string }
export interface LevelOption       { id: string; label: string; basePrice: number; note: string }
export interface DeadlineOption    { id: string; label: string; sublabel: string; multiplier: number; hours: number; badge?: string }
export interface SubjectOption     { id: string; label: string; category: string }
export interface FormatOption      { id: string; label: string }
export interface WorkTypeOption    { id: string; label: string; desc: string }
export interface OrderTypeOption   { id: string; label: string; desc: string; examples: string; priceFrom: number; color: string; external?: string }
export interface DesignTypeOption  { id: string; label: string; desc: string; unit: string }
export interface DiagramTypeOption { id: string; label: string; desc: string }

export const ORDER_TYPES: OrderTypeOption[] = [
  { id: 'paper',   label: 'Paper & Essay',      desc: 'Research papers, essays, dissertations & more', examples: 'Research paper · Essay · Dissertation · Case study · Lab report', priceFrom: 15, color: 'text-brand-600 bg-brand-50 border-brand-200' },
  { id: 'design',  label: 'Design',             desc: 'Slides, infographics, posters & visual assets',  examples: 'PowerPoint · Infographic · Poster · Social media', priceFrom: 20, color: 'text-purple-600 bg-purple-50 border-purple-200' },
  { id: 'diagram', label: 'Diagrams & Charts',  desc: 'Flowcharts, ER diagrams, mind maps & more',      examples: 'Flowchart · ER diagram · Mind map · Org chart', priceFrom: 25, color: 'text-teal-600 bg-teal-50 border-teal-200' },
  { id: 'combo',   label: 'Combo Order',        desc: 'Paper + slides or diagram components together',  examples: 'Report + infographic · Essay + presentation', priceFrom: 15, color: 'text-amber-600 bg-amber-50 border-amber-200' },
  { id: 'special', label: 'Special Project',    desc: 'Custom work — nursing sims, coding, shadow health', examples: 'Shadow Health · iHuman · Coding project · Custom research', priceFrom: 0, color: 'text-rose-600 bg-rose-50 border-rose-200', external: '/quote' },
  { id: 'class',   label: 'Full Class Support', desc: 'We handle your entire course — all assignments', examples: 'Weekly assignments · Exams · Discussions · Full semester', priceFrom: 0, color: 'text-green-600 bg-green-50 border-green-200', external: '/class-support' },
]

export const DESIGN_TYPES: DesignTypeOption[] = [
  { id: 'powerpoint',   label: 'PowerPoint / Slides',  desc: 'Academic & professional presentations',   unit: 'slides' },
  { id: 'infographic',  label: 'Infographic',           desc: 'Visual data story or explainer',          unit: 'designs' },
  { id: 'poster',       label: 'Academic Poster',       desc: 'Research or conference poster',           unit: 'designs' },
  { id: 'social_media', label: 'Social Media Graphics', desc: 'Branded graphics for digital channels',   unit: 'designs' },
  { id: 'report_design',label: 'Report / PDF Design',   desc: 'Professionally designed document layout', unit: 'pages' },
  { id: 'other_design', label: 'Other Design',          desc: 'Describe your needs in requirements',     unit: 'designs' },
]

export const DIAGRAM_TYPES: DiagramTypeOption[] = [
  { id: 'flowchart',   label: 'Flowchart',         desc: 'Process or decision flow' },
  { id: 'er_diagram',  label: 'ER Diagram',         desc: 'Entity-relationship / database schema' },
  { id: 'mind_map',    label: 'Mind Map',           desc: 'Concept map or knowledge tree' },
  { id: 'org_chart',   label: 'Org Chart',          desc: 'Organisational structure' },
  { id: 'uml',         label: 'UML Diagram',        desc: 'Class, sequence, use-case diagrams' },
  { id: 'gantt',       label: 'Gantt Chart',        desc: 'Project timeline and schedule' },
  { id: 'network',     label: 'Network Diagram',    desc: 'IT or architecture network map' },
  { id: 'other_diag',  label: 'Other Diagram',      desc: 'Describe in requirements' },
]

export const DIAGRAM_SOFTWARE = [
  { id: 'any',       label: 'Any (you choose)' },
  { id: 'draw_io',   label: 'Draw.io / Diagrams.net' },
  { id: 'powerpoint',label: 'PowerPoint / Word' },
  { id: 'lucidchart',label: 'Lucidchart' },
  { id: 'visio',     label: 'Microsoft Visio' },
  { id: 'mermaid',   label: 'Mermaid (code)' },
]

export const PAPER_TYPES: PaperTypeOption[] = [
  { id: 'research_paper',    label: 'Research Paper',        icon: 'FileText' },
  { id: 'essay',             label: 'Essay',                 icon: 'PenLine' },
  { id: 'dissertation',      label: 'Dissertation',          icon: 'GraduationCap' },
  { id: 'case_study',        label: 'Case Study',            icon: 'Briefcase' },
  { id: 'literature_review', label: 'Literature Review',     icon: 'Search' },
  { id: 'lab_report',        label: 'Lab Report',            icon: 'FlaskConical' },
  { id: 'coursework',        label: 'Coursework',            icon: 'BookOpen' },
  { id: 'data_analysis',     label: 'Data Analysis',         icon: 'BarChart3' },
  { id: 'presentation',      label: 'Presentation Notes',    icon: 'MonitorPlay' },
]

export const ACADEMIC_LEVELS: LevelOption[] = [
  { id: 'high_school',   label: 'High School',          basePrice: 15, note: 'Grades 9–12' },
  { id: 'undergrad_1_2', label: 'Undergraduate 1–2',    basePrice: 18, note: 'Freshman / Sophomore' },
  { id: 'undergrad_3_4', label: 'Undergraduate 3–4',    basePrice: 22, note: 'Junior / Senior' },
  { id: 'masters',       label: "Master's",             basePrice: 28, note: 'Graduate level' },
  { id: 'phd',           label: 'PhD / Doctoral',       basePrice: 36, note: 'Dissertation-level' },
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
  { id: 'biology',       label: 'Biology',            category: 'STEM' },
  { id: 'chemistry',     label: 'Chemistry',          category: 'STEM' },
  { id: 'physics',       label: 'Physics',            category: 'STEM' },
  { id: 'mathematics',   label: 'Mathematics',        category: 'STEM' },
  { id: 'statistics',    label: 'Statistics',         category: 'STEM' },
  { id: 'engineering',   label: 'Engineering',        category: 'STEM' },
  { id: 'cs',            label: 'Computer Science',   category: 'STEM' },
  { id: 'env_science',   label: 'Environmental Sci.', category: 'STEM' },
  { id: 'accounting',    label: 'Accounting',         category: 'Business & Finance' },
  { id: 'finance',       label: 'Finance',            category: 'Business & Finance' },
  { id: 'marketing',     label: 'Marketing',          category: 'Business & Finance' },
  { id: 'economics',     label: 'Economics',          category: 'Business & Finance' },
  { id: 'management',    label: 'Management',         category: 'Business & Finance' },
  { id: 'business_law',  label: 'Business Law',       category: 'Business & Finance' },
  { id: 'nursing',       label: 'Nursing',            category: 'Healthcare' },
  { id: 'public_health', label: 'Public Health',      category: 'Healthcare' },
  { id: 'psychology',    label: 'Psychology',         category: 'Healthcare' },
  { id: 'pharmacology',  label: 'Pharmacology',       category: 'Healthcare' },
  { id: 'social_work',   label: 'Social Work',        category: 'Healthcare' },
  { id: 'history',       label: 'History',            category: 'Humanities & Law' },
  { id: 'literature',    label: 'Literature',         category: 'Humanities & Law' },
  { id: 'philosophy',    label: 'Philosophy',         category: 'Humanities & Law' },
  { id: 'law',           label: 'Law',                category: 'Humanities & Law' },
  { id: 'political_sci', label: 'Political Science',  category: 'Humanities & Law' },
  { id: 'education',     label: 'Education',          category: 'Humanities & Law' },
  { id: 'sociology',     label: 'Sociology',          category: 'Humanities & Law' },
]

export const FORMATTING_STYLES: FormatOption[] = [
  { id: 'apa7',      label: 'APA 7th Edition' },
  { id: 'mla9',      label: 'MLA 9th Edition' },
  { id: 'chicago17', label: 'Chicago 17th Edition' },
  { id: 'harvard',   label: 'Harvard' },
  { id: 'vancouver', label: 'Vancouver' },
  { id: 'none',      label: 'Not required' },
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
  { id: 'au', label: 'Australian English' },
]

export const WRITER_TIERS = [
  { id: 'standard', label: 'Standard', desc: "Verified Master's writer",  surcharge: 0    },
  { id: 'advanced', label: 'Advanced', desc: 'Top-rated, 500+ orders',    surcharge: 0.10 },
  { id: 'expert',   label: 'Expert',   desc: 'PhD-level specialist',      surcharge: 0.20 },
]

export const DESIGN_BASE_PRICE = 20
export const DIAGRAM_BASE_PRICE = 25

export function useOrderForm() {
  const form = reactive({
    // Order type
    orderType:     ORDER_TYPES[0],
    // Paper
    paperType:     PAPER_TYPES[0],
    level:         ACADEMIC_LEVELS[1],
    pages:         1,
    spacing:       'double' as 'double' | 'single',
    // Design
    designType:    DESIGN_TYPES[0],
    designUnits:   1,   // slides / designs / pages
    designStyle:   '',  // brief style notes
    // Diagram
    diagramType:   DIAGRAM_TYPES[0],
    diagramCount:  1,
    diagramSoftware: DIAGRAM_SOFTWARE[0],
    diagramComplexity: 'standard' as 'simple' | 'standard' | 'complex',
    comboComponent: 'design' as 'design' | 'diagram',
    // Shared
    deadline:      DEADLINES[0],
    subject:       SUBJECTS[0],
    writerTier:    WRITER_TIERS[0],
    // Step 2
    topic:         '',
    instructions:  '',
    workType:      WORK_TYPES[0],
    formatStyle:   FORMATTING_STYLES[0],
    references:    0,
    englishType:   ENGLISH_TYPES[0],
    discountCode:  '',
    // Step 3
    firstName:     '',
    lastName:      '',
    email:         '',
    password:      '',
    agreeToTerms:  false,
  })

  const basePrice = computed(() => {
    let base: number
    if (form.orderType.id === 'design')       base = DESIGN_BASE_PRICE
    else if (form.orderType.id === 'diagram') base = DIAGRAM_BASE_PRICE
    else                                       base = form.level.basePrice
    return base * form.deadline.multiplier * (1 + form.writerTier.surcharge)
  })

  // For combo: paper cost + design/diagram cost
  const comboPlusPrice = computed(() => {
    if (form.orderType.id !== 'combo') return 0
    const mult = form.deadline.multiplier * (1 + form.writerTier.surcharge)
    if (form.comboComponent === 'design')  return DESIGN_BASE_PRICE * mult * form.designUnits
    return DIAGRAM_BASE_PRICE * mult * form.diagramCount
  })

  const unitCount = computed(() => {
    if (form.orderType.id === 'design')       return form.designUnits
    if (form.orderType.id === 'diagram')      return form.diagramCount
    return form.pages
  })

  const unitLabel = computed(() => {
    if (form.orderType.id === 'design')       return form.designType.unit
    if (form.orderType.id === 'diagram')      return 'diagrams'
    return 'pages'
  })

  const totalPrice = computed(() => Math.ceil(basePrice.value * unitCount.value + comboPlusPrice.value))
  const pricePerUnit = computed(() => Math.ceil(basePrice.value))

  const wordCount = computed(() =>
    form.orderType.id === 'paper' || form.orderType.id === 'combo'
      ? form.pages * (form.spacing === 'double' ? 275 : 550)
      : 0
  )

  const deadlineDate = computed(() => {
    const d = new Date()
    d.setHours(d.getHours() + form.deadline.hours)
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  })

  function savePendingOrder() {
    const payload = {
      orderType:    form.orderType.id,
      paperType:    form.paperType.label,
      designType:   form.designType.label,
      diagramType:  form.diagramType.label,
      level:        form.level.label,
      pages:        form.pages,
      designUnits:  form.designUnits,
      diagramCount: form.diagramCount,
      comboComponent: form.comboComponent,
      spacing:      form.spacing,
      deadline:     form.deadline.label,
      deadlineHours: form.deadline.hours,
      subject:      form.subject.label,
      writerTier:   form.writerTier.id,
      topic:        form.topic,
      instructions: form.instructions,
      workType:     form.workType.label,
      formatStyle:  form.formatStyle.label,
      references:   form.references,
      englishType:  form.englishType.label,
      discountCode: form.discountCode,
      estimatedPrice: totalPrice.value,
      savedAt:      new Date().toISOString(),
    }
    if (import.meta.client) {
      localStorage.setItem('rpm_pending_order', JSON.stringify(payload))
    }
  }

  const step1Valid = computed(() => {
    if (form.orderType.id === 'design')  return !!form.designType && form.designUnits >= 1 && !!form.deadline
    if (form.orderType.id === 'diagram') return !!form.diagramType && form.diagramCount >= 1 && !!form.deadline
    if (form.orderType.id === 'combo') {
      const paperOk = !!form.paperType && !!form.level && form.pages >= 1 && !!form.subject
      const plusOk = form.comboComponent === 'design'
        ? !!form.designType && form.designUnits >= 1
        : !!form.diagramType && form.diagramCount >= 1
      return paperOk && plusOk && !!form.deadline
    }
    return !!form.paperType && !!form.level && form.pages >= 1 && !!form.deadline && !!form.subject
  })

  const step2Valid = computed(() =>
    form.topic.trim().length >= 3 && form.instructions.trim().length >= 10
  )

  const step3Valid = computed(() =>
    form.firstName.trim().length > 0
    && form.email.includes('@')
    && form.password.length >= 8
    && form.agreeToTerms
  )

  return {
    form, totalPrice, pricePerUnit, unitLabel, unitCount,
    wordCount, deadlineDate, step1Valid, step2Valid, step3Valid,
    savePendingOrder,
  }
}
