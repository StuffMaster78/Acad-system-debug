import type { Ref } from 'vue'
import type { PublicPricingConfig, CfgAddon } from './usePricingConfig'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface PaperTypeOption    { id: string; label: string; icon: string }
export interface LevelOption        { id: string; label: string; basePrice: number; note: string }
export interface DeadlineOption     { id: string; label: string; sublabel: string; multiplier: number; hours: number; badge?: string }
export interface SubjectOption      { id: string; label: string; category: string }
export interface FormatOption       { id: string; label: string }
export interface WorkTypeOption     { id: string; label: string; desc: string }
export interface OrderTypeOption    { id: string; label: string; desc: string; examples: string; priceFrom: number; color: string; external?: string }
export interface WriterTierOption   { id: string; label: string; desc: string; surcharge: number }
export interface DesignTypeOption   { id: string; label: string; unit: string; basePrice: number }
export interface DiagramTypeOption  { id: string; label: string; desc: string; basePrice: number }

// ── Static / nursing-specific data ───────────────────────────────────────────

export const ORDER_TYPES: OrderTypeOption[] = [
  { id: 'paper',      label: 'Nursing Paper',          desc: 'Essays, care plans, SOAP notes, research papers, capstone projects & more', examples: 'Care Plan · SOAP Note · Nursing Essay · Research Paper · Dissertation', priceFrom: 24, color: 'text-brand-600 bg-brand-50 border-brand-200' },
  { id: 'design',     label: 'Slides & Visuals',       desc: 'Clinical presentations, care pathway visuals, patient-education posters & handouts', examples: 'Case presentation · Care pathway · Infographic · Conference poster', priceFrom: 20, color: 'text-violet-600 bg-violet-50 border-violet-200' },
  { id: 'diagram',    label: 'Diagrams & Maps',        desc: 'Concept maps, pathophysiology diagrams, genograms, ecomaps & flowcharts', examples: 'Concept map · Pathophysiology · Genogram · Ecomap · Process flowchart', priceFrom: 30, color: 'text-teal-600 bg-teal-50 border-teal-200' },
  { id: 'class',      label: 'Online Class Help',      desc: 'Full course management — all assignments, discussions, quizzes & exams', examples: 'Full semester · Individual modules · Weekly discussions · Exams', priceFrom: 0, color: 'text-green-600 bg-green-50 border-green-200', external: '/class-support' },
  { id: 'simulation', label: 'Clinical Simulation',    desc: 'Shadow Health DCEs, iHuman virtual patients & other simulation platforms', examples: 'Tina Jones · Brian Foster · iHuman cases · ATI · Kaplan', priceFrom: 35, color: 'text-rose-600 bg-rose-50 border-rose-200', external: '/quote' },
  { id: 'special',    label: 'Special / Custom Project', desc: 'Unusual brief that needs a tailored quote — multi-part, custom scope', examples: 'Multi-part project · Admission essay · Portfolio · Custom research', priceFrom: 0, color: 'text-amber-600 bg-amber-50 border-amber-200', external: '/quote' },
]

// Nursing design types carry per-type base prices
export const DESIGN_TYPES: DesignTypeOption[] = [
  { id: 'clinical_slides',  label: 'Clinical Presentation',       unit: 'slides',  basePrice: 20 },
  { id: 'care_pathway',     label: 'Care Pathway / Journey Map',  unit: 'designs', basePrice: 35 },
  { id: 'nursing_poster',   label: 'Research / Conference Poster',unit: 'designs', basePrice: 45 },
  { id: 'infographic',      label: 'Nursing Infographic',         unit: 'designs', basePrice: 35 },
  { id: 'patient_handout',  label: 'Patient Education Handout',   unit: 'pages',   basePrice: 20 },
  { id: 'other_design',     label: 'Other (describe in brief)',   unit: 'designs', basePrice: 30 },
]

export const DIAGRAM_TYPES: DiagramTypeOption[] = [
  { id: 'concept_map',     label: 'Concept Map',               desc: 'Nursing diagnosis concept linkages',     basePrice: 30 },
  { id: 'care_map',        label: 'Care Map',                   desc: 'Patient-centered care relationship map', basePrice: 35 },
  { id: 'pathophysiology', label: 'Pathophysiology Diagram',    desc: 'Disease process & system involvement',   basePrice: 40 },
  { id: 'genogram',        label: 'Genogram',                   desc: 'Family health history diagram',          basePrice: 30 },
  { id: 'ecomap',          label: 'Ecomap',                     desc: 'Patient-environment relationship map',   basePrice: 30 },
  { id: 'flowchart',       label: 'Clinical Flowchart',         desc: 'Decision or process flow diagram',       basePrice: 35 },
  { id: 'other_diagram',   label: 'Other (describe in brief)',  desc: 'Custom diagram — specify in brief',      basePrice: 30 },
]

export const DIAGRAM_SOFTWARE = [
  { id: 'any',        label: "Writer's choice (best tool for the job)" },
  { id: 'powerpoint', label: 'PowerPoint / Word' },
  { id: 'draw_io',    label: 'Draw.io / Diagrams.net' },
  { id: 'lucidchart', label: 'Lucidchart' },
  { id: 'hand_drawn', label: 'Hand-drawn & scanned' },
]

export const STATIC_PAPER_TYPES: PaperTypeOption[] = [
  { id: 'care_plan',      label: 'Care Plan',             icon: 'ClipboardList' },
  { id: 'soap_note',      label: 'SOAP Note',             icon: 'Stethoscope'   },
  { id: 'nursing_essay',  label: 'Nursing Essay',         icon: 'PenLine'       },
  { id: 'research_paper', label: 'Research Paper',        icon: 'Microscope'    },
  { id: 'capstone',       label: 'Capstone Project',      icon: 'GraduationCap' },
  { id: 'case_study',     label: 'Case Study',            icon: 'Search'        },
  { id: 'concept_map',    label: 'Concept Map',           icon: 'Network'       },
  { id: 'coursework',     label: 'Coursework',            icon: 'Briefcase'     },
  { id: 'dissertation',   label: 'Dissertation / Thesis', icon: 'BookOpen'      },
  { id: 'discussion',     label: 'Discussion Post',       icon: 'MessageSquare' },
  { id: 'reflection',     label: 'Reflective Journal',    icon: 'FileText'      },
  { id: 'lit_review',     label: 'Literature Review',     icon: 'BookOpen'      },
]
export const PAPER_TYPES = STATIC_PAPER_TYPES

export const STATIC_LEVELS: LevelOption[] = [
  { id: 'adn_lpn',  label: 'ADN / LPN',        basePrice: 24, note: 'Associate degree or practical nursing' },
  { id: 'bsn_1_2',  label: 'BSN Year 1–2',     basePrice: 26, note: 'Freshman / Sophomore nursing' },
  { id: 'bsn_3_4',  label: 'BSN Year 3–4',     basePrice: 28, note: 'Junior / Senior nursing' },
  { id: 'msn',      label: 'MSN / NP Program', basePrice: 32, note: 'Graduate nursing level' },
  { id: 'dnp_phd',  label: 'DNP / PhD',        basePrice: 38, note: 'Doctoral nursing program' },
]
export const ACADEMIC_LEVELS = STATIC_LEVELS

export const STATIC_DEADLINES: DeadlineOption[] = [
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
export const DEADLINES = STATIC_DEADLINES

export const STATIC_SUBJECTS: SubjectOption[] = [
  { id: 'med_surg',        label: 'Medical-Surgical Nursing',     category: 'Nursing' },
  { id: 'pathophysiology', label: 'Pathophysiology',              category: 'Nursing' },
  { id: 'pharmacology',    label: 'Pharmacology',                 category: 'Nursing' },
  { id: 'health_assess',   label: 'Health Assessment',            category: 'Nursing' },
  { id: 'psych_nursing',   label: 'Psychiatric / Mental Health',  category: 'Nursing' },
  { id: 'maternal_child',  label: 'Maternal & Child Health',      category: 'Nursing' },
  { id: 'pediatric',       label: 'Pediatric Nursing',            category: 'Nursing' },
  { id: 'community',       label: 'Community Health Nursing',     category: 'Nursing' },
  { id: 'critical_care',   label: 'Critical Care / ICU',          category: 'Nursing' },
  { id: 'emergency',       label: 'Emergency Nursing',            category: 'Nursing' },
  { id: 'periop',          label: 'Perioperative Nursing',        category: 'Nursing' },
  { id: 'geriatric',       label: 'Geriatric Nursing',            category: 'Nursing' },
  { id: 'oncology',        label: 'Oncology Nursing',             category: 'Nursing' },
  { id: 'leadership',      label: 'Nursing Leadership / Mgmt',    category: 'Nursing' },
  { id: 'informatics',     label: 'Nursing Informatics',          category: 'Nursing' },
  { id: 'ebp',             label: 'Evidence-Based Practice',      category: 'Nursing' },
  { id: 'fundamentals',    label: 'Fundamentals of Nursing',      category: 'Nursing' },
  { id: 'fnp',             label: 'Family Nurse Practice (FNP)',  category: 'Advanced Practice' },
  { id: 'np_adult',        label: 'Adult-Gero NP',                category: 'Advanced Practice' },
  { id: 'pmhnp',           label: 'Psychiatric-Mental Health NP', category: 'Advanced Practice' },
  { id: 'crna',            label: 'CRNA / Anesthesia Nursing',    category: 'Advanced Practice' },
  { id: 'midwifery',       label: 'Nurse Midwifery / CNM',        category: 'Advanced Practice' },
  { id: 'dnp_practice',    label: 'DNP Clinical Practice',        category: 'Advanced Practice' },
  { id: 'public_health',   label: 'Public Health',                category: 'Allied Health' },
  { id: 'nutrition',       label: 'Nutrition / Dietetics',        category: 'Allied Health' },
  { id: 'social_work',     label: 'Social Work',                  category: 'Allied Health' },
  { id: 'psychology',      label: 'Psychology',                   category: 'Allied Health' },
  { id: 'biology',         label: 'Biology / Anatomy',            category: 'Allied Health' },
  { id: 'microbiology',    label: 'Microbiology',                 category: 'Allied Health' },
  { id: 'research_methods',label: 'Research Methodology',         category: 'Other' },
  { id: 'statistics',      label: 'Statistics / Biostatistics',   category: 'Other' },
  { id: 'english',         label: 'English / Communications',     category: 'Other' },
  { id: 'other',           label: 'Other (specify in topic)',      category: 'Other' },
]
export const SUBJECTS = STATIC_SUBJECTS

export const STATIC_FORMATTING: FormatOption[] = [
  { id: 'apa7',      label: 'APA 7th Edition (nursing standard)' },
  { id: 'ama',       label: 'AMA (medical journals)' },
  { id: 'mla9',      label: 'MLA 9th Edition' },
  { id: 'chicago17', label: 'Chicago 17th Edition' },
  { id: 'harvard',   label: 'Harvard' },
  { id: 'vancouver', label: 'Vancouver' },
  { id: 'none',      label: 'Not required / as instructed' },
]
export const FORMATTING_STYLES = STATIC_FORMATTING

export const STATIC_WORK_TYPES: WorkTypeOption[] = [
  { id: 'writing',      label: 'Writing',       desc: 'New paper from scratch' },
  { id: 'editing',      label: 'Editing',       desc: 'Improve an existing draft' },
  { id: 'rewriting',    label: 'Rewriting',     desc: 'Rewrite existing content' },
  { id: 'proofreading', label: 'Proofreading',  desc: 'Fix grammar and formatting' },
]
export const WORK_TYPES = STATIC_WORK_TYPES

export const STATIC_ENGLISH = [
  { id: 'us', label: 'US English' },
  { id: 'uk', label: 'UK English' },
]
export const ENGLISH_TYPES = STATIC_ENGLISH

export const WRITER_TIERS: WriterTierOption[] = [
  { id: 'bsn',     label: 'BSN Writer', desc: 'Verified BSN with clinical experience',   surcharge: 0    },
  { id: 'msn',     label: 'MSN Writer', desc: "Master's-level nurse, 3+ years writing",  surcharge: 0.10 },
  { id: 'dnp_phd', label: 'DNP / PhD',  desc: 'Doctoral-level nursing expert',           surcharge: 0.20 },
]

const DRAFT_KEY = 'nmg_order_draft'

// ── Composable ────────────────────────────────────────────────────────────────

export function useOrderForm(cfg?: Ref<PublicPricingConfig | null>) {

  // ── Dynamic option arrays ─────────────────────────────────────────────────

  const levels = computed<LevelOption[]>(() => {
    const display = cfg?.value?.academic_levels_display
    const pricing = cfg?.value?.academic_levels
    if (display?.length) {
      return display.map((d, i) => {
        const pricingMatch = pricing?.find(p => p.label.toLowerCase() === d.name.toLowerCase()) ?? pricing?.[i]
        return { id: d.name, label: d.name, basePrice: pricingMatch?.price_per_page ?? STATIC_LEVELS[i]?.basePrice ?? 24, note: d.description ?? '' }
      })
    }
    if (pricing?.length) {
      return pricing.map((p, i) => ({ id: p.code, label: p.label, basePrice: p.price_per_page ?? STATIC_LEVELS[i]?.basePrice ?? 24, note: '' }))
    }
    return STATIC_LEVELS
  })

  const paperTypes = computed<PaperTypeOption[]>(() => {
    const display = cfg?.value?.paper_types_display
    if (display?.length) {
      return display.map((d, i) => ({ id: d.name, label: d.name, icon: STATIC_PAPER_TYPES[i]?.icon ?? 'FileText' }))
    }
    return STATIC_PAPER_TYPES
  })

  const deadlines = computed<DeadlineOption[]>(() => {
    const raw = cfg?.value?.deadlines
    if (raw?.length) {
      return raw.map((d, i) => {
        const staticMatch = STATIC_DEADLINES.find(s => s.hours === d.max_hours) ?? STATIC_DEADLINES[i]
        return { id: String(d.max_hours), label: d.label, sublabel: staticMatch?.sublabel ?? '', multiplier: d.multiplier, hours: d.max_hours, badge: staticMatch?.badge }
      })
    }
    return STATIC_DEADLINES
  })

  const subjects = computed<SubjectOption[]>(() => {
    const raw = cfg?.value?.subjects
    if (raw?.length) return raw.map(s => ({ id: s.name, label: s.name, category: s.category }))
    return STATIC_SUBJECTS
  })

  const workTypes = computed<WorkTypeOption[]>(() => {
    const raw = cfg?.value?.work_types
    if (raw?.length) return raw.map(w => ({ id: w.name, label: w.name, desc: w.description ?? '' }))
    return STATIC_WORK_TYPES
  })

  const formattingStyles = computed<FormatOption[]>(() => {
    const raw = cfg?.value?.formatting_styles
    if (raw?.length) return raw.map(f => ({ id: f.name, label: f.name }))
    return STATIC_FORMATTING
  })

  const englishTypes = computed<Array<{ id: string; label: string }>>(() => {
    const raw = cfg?.value?.english_types
    if (raw?.length) return raw.map(e => ({ id: e.code || e.name, label: e.name }))
    return STATIC_ENGLISH
  })

  const addons = computed<CfgAddon[]>(() => cfg?.value?.addons ?? [])

  const spacingMult = computed(() =>
    form.spacing === 'single'
      ? (cfg?.value?.spacing_multipliers?.single ?? 2)
      : (cfg?.value?.spacing_multipliers?.double ?? 1)
  )

  // ── Form state ────────────────────────────────────────────────────────────

  const savedDraft = import.meta.client
    ? (() => { try { return JSON.parse(localStorage.getItem(DRAFT_KEY) ?? 'null') } catch { return null } })()
    : null

  const form = reactive({
    orderType:         ORDER_TYPES.find(t => t.id === savedDraft?.orderType) ?? ORDER_TYPES[0],
    paperType:         STATIC_PAPER_TYPES[0],
    level:             STATIC_LEVELS[1],
    pages:             savedDraft?.pages ?? 1,
    spacing:           (savedDraft?.spacing as 'double' | 'single') ?? 'double',
    subject:           STATIC_SUBJECTS[0],
    writerTier:        WRITER_TIERS[0],
    designType:        DESIGN_TYPES[0],
    designUnits:       savedDraft?.designUnits ?? 1,
    diagramType:       DIAGRAM_TYPES[0],
    diagramSoftware:   DIAGRAM_SOFTWARE[0],
    diagramCount:      savedDraft?.diagramCount ?? 1,
    deadline:          STATIC_DEADLINES[0],
    topic:             savedDraft?.topic ?? '',
    instructions:      savedDraft?.instructions ?? '',
    workType:          STATIC_WORK_TYPES[0],
    formatStyle:       STATIC_FORMATTING[0],
    references:        savedDraft?.references ?? 0,
    englishType:       STATIC_ENGLISH[0],
    discountCode:      savedDraft?.discountCode ?? '',
    selectedAddonIds:  (savedDraft?.selectedAddonIds as number[]) ?? [],
    firstName:         '',
    lastName:          '',
    email:             '',
    password:          '',
    agreeToTerms:      false,
  })

  // Re-match when dynamic arrays load
  watch(levels, (newLevels) => {
    const match = newLevels.find(l => l.id === form.level.id || l.label === form.level.label)
    if (match) form.level = match
    else if (newLevels.length) form.level = newLevels[Math.min(1, newLevels.length - 1)]
  })

  watch(paperTypes, (newTypes) => {
    const match = newTypes.find(p => p.id === form.paperType.id || p.label === form.paperType.label)
    if (match) form.paperType = match
    else if (newTypes.length) form.paperType = newTypes[0]
  })

  watch(deadlines, (newDeadlines) => {
    const match = newDeadlines.find(d => d.hours === form.deadline.hours)
    if (match) form.deadline = match
    else if (newDeadlines.length) form.deadline = newDeadlines[0]
  })

  watch(subjects, (newSubjects) => {
    if (!newSubjects.find(s => s.id === form.subject.id || s.label === form.subject.label) && newSubjects.length) {
      form.subject = newSubjects[0]
    }
  })

  // ── Pricing ───────────────────────────────────────────────────────────────

  const isDesign  = computed(() => form.orderType.id === 'design')
  const isDiagram = computed(() => form.orderType.id === 'diagram')

  const unitLabel = computed(() => {
    if (isDesign.value)  return form.designType.unit
    if (isDiagram.value) return 'diagrams'
    return 'pages'
  })
  const unitCount = computed(() => {
    if (isDesign.value)  return form.designUnits
    if (isDiagram.value) return form.diagramCount
    return form.pages
  })

  // NMG: design/diagram use per-type base prices; paper uses level price × spacing
  const basePrice = computed(() => {
    const deadlineMult = form.deadline.multiplier
    const tierMult     = 1 + form.writerTier.surcharge
    if (isDesign.value)  return form.designType.basePrice  * deadlineMult * tierMult
    if (isDiagram.value) return form.diagramType.basePrice * deadlineMult * tierMult
    return form.level.basePrice * deadlineMult * tierMult * spacingMult.value
  })

  const addonTotal = computed(() =>
    addons.value
      .filter(a => form.selectedAddonIds.includes(a.id))
      .reduce((sum, a) => sum + a.flat_amount, 0)
  )

  const localTotal    = computed(() => Math.ceil(basePrice.value * unitCount.value + addonTotal.value))

  // ── Live price from estimate endpoint (paper only) ─────────────────────────
  const liveTotal  = ref<number | null>(null)
  const isPricing  = ref(false)
  let _priceTimer: ReturnType<typeof setTimeout> | undefined

  async function _fetchEstimate() {
    if (form.orderType.id !== 'paper') { liveTotal.value = null; return }
    const apiBase = import.meta.client ? (useRuntimeConfig().public.apiBase || '') : ''
    if (!apiBase) return
    isPricing.value = true
    try {
      type EstResp = { total?: string | number | null; estimated_min_price?: string | number | null }
      const resp = await $fetch<EstResp>(`${apiBase}/api/v1/pricing/public/estimate/`, {
        method: 'POST', credentials: 'include',
        body: { paper_type_code: form.paperType.id, academic_level_code: form.level.id, pages: form.pages, deadline_hours: form.deadline.hours, spacing: form.spacing },
      })
      const n = Number(resp?.total ?? resp?.estimated_min_price)
      liveTotal.value = Number.isFinite(n) && n > 0 ? Math.ceil(n) : null
    } catch { liveTotal.value = null }
    finally { isPricing.value = false }
  }

  if (import.meta.client) {
    watch(
      () => [form.paperType.id, form.level.id, form.deadline.hours, form.pages, form.spacing, form.orderType.id],
      () => { if (_priceTimer) clearTimeout(_priceTimer); _priceTimer = setTimeout(() => void _fetchEstimate(), 400) }
    )
  }

  const totalPrice    = computed(() => liveTotal.value ?? localTotal.value)
  const pricePerUnit  = computed(() => Math.ceil(totalPrice.value / Math.max(unitCount.value, 1)))
  const wordCount     = computed(() => form.pages * (form.spacing === 'double' ? 275 : 550))

  const deadlineDate = computed(() => {
    const d = new Date()
    d.setHours(d.getHours() + form.deadline.hours)
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  })

  // ── Persistence ───────────────────────────────────────────────────────────

  if (import.meta.client) {
    watch(
      () => ({
        orderType: form.orderType.id, pages: form.pages, spacing: form.spacing,
        designUnits: form.designUnits, diagramCount: form.diagramCount,
        topic: form.topic, instructions: form.instructions, references: form.references,
        discountCode: form.discountCode, levelId: form.level.id,
        paperTypeId: form.paperType.id, deadlineHours: form.deadline.hours,
        subjectId: form.subject.id, workTypeId: form.workType.id,
        formatStyleId: form.formatStyle.id, englishTypeId: form.englishType.id,
        writerTierId: form.writerTier.id,
        selectedAddonIds: form.selectedAddonIds,
      }),
      (draft) => { try { localStorage.setItem(DRAFT_KEY, JSON.stringify(draft)) } catch {} },
      { deep: true }
    )
  }

  // ── Submit payload builder ────────────────────────────────────────────────

  function savePendingOrder() {
    if (!import.meta.client) return
    localStorage.setItem('nmg_pending_order', JSON.stringify({
      orderType: form.orderType.id, paperType: form.paperType.label,
      level: form.level.label, pages: form.pages, spacing: form.spacing,
      deadline: form.deadline.label, deadlineHours: form.deadline.hours,
      subject: form.subject.label, writerTier: form.writerTier.id,
      designType: form.designType.label, designUnits: form.designUnits,
      diagramType: form.diagramType.label, diagramSoftware: form.diagramSoftware.label,
      diagramCount: form.diagramCount, topic: form.topic, instructions: form.instructions,
      workType: form.workType.label, formatStyle: form.formatStyle.label,
      references: form.references, discountCode: form.discountCode,
      estimatedPrice: totalPrice.value, savedAt: new Date().toISOString(),
    }))
  }

  // ── Validation ────────────────────────────────────────────────────────────

  const step1Valid = computed(() => {
    if (isDesign.value)  return form.designUnits >= 1  && !!form.deadline
    if (isDiagram.value) return form.diagramCount >= 1 && !!form.deadline
    return !!form.paperType && !!form.level && form.pages >= 1 && !!form.deadline && !!form.subject
  })
  const step2Valid = computed(() =>
    form.topic.trim().length >= 3 && form.instructions.trim().length >= 10
  )
  const step3Valid = computed(() =>
    form.firstName.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && form.agreeToTerms
  )

  return {
    form,
    levels, paperTypes, deadlines, subjects, workTypes, formattingStyles, englishTypes, addons,
    totalPrice, pricePerUnit, unitLabel, unitCount, wordCount, deadlineDate, isPricing, addonTotal,
    step1Valid, step2Valid, step3Valid,
    savePendingOrder,
  }
}
