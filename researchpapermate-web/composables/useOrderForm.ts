import type { Ref } from 'vue'
import type { PublicPricingConfig, CfgAddon } from './usePricingConfig'

// ── Static shape types ────────────────────────────────────────────────────────

export interface PaperTypeOption    { id: string; label: string; icon: string }
export interface LevelOption        { id: string; label: string; basePrice: number; note: string }
export interface DeadlineOption     { id: string; label: string; sublabel: string; multiplier: number; hours: number; badge?: string }
export interface SubjectOption      { id: string; label: string; category: string }
export interface FormatOption       { id: string; label: string }
export interface WorkTypeOption     { id: string; label: string; desc: string }
export interface OrderTypeOption    { id: string; label: string; desc: string; examples: string; priceFrom: number; color: string; external?: string }
export interface DesignTypeOption   { id: string; label: string; desc: string; unit: string }
export interface DiagramTypeOption  { id: string; label: string; desc: string }

// ── Static fallback data ──────────────────────────────────────────────────────

export const ORDER_TYPES: OrderTypeOption[] = [
  { id: 'paper',   label: 'Paper & Essay',      desc: 'Research papers, essays, dissertations & more', examples: 'Research paper · Essay · Dissertation · Case study · Lab report', priceFrom: 15, color: 'text-brand-600 bg-brand-50 border-brand-200' },
  { id: 'design',  label: 'Design',             desc: 'Slides, infographics, posters & visual assets',  examples: 'PowerPoint · Infographic · Poster · Social media', priceFrom: 20, color: 'text-purple-600 bg-purple-50 border-purple-200' },
  { id: 'diagram', label: 'Diagrams & Charts',  desc: 'Flowcharts, ER diagrams, mind maps & more',      examples: 'Flowchart · ER diagram · Mind map · Org chart', priceFrom: 25, color: 'text-teal-600 bg-teal-50 border-teal-200' },
  { id: 'combo',   label: 'Combo Order',        desc: 'Paper + slides or diagram components together',  examples: 'Report + infographic · Essay + presentation', priceFrom: 15, color: 'text-amber-600 bg-amber-50 border-amber-200' },
  { id: 'special', label: 'Special Project',    desc: 'Custom work — nursing sims, coding, shadow health', examples: 'Shadow Health · iHuman · Coding project · Custom research', priceFrom: 0, color: 'text-rose-600 bg-rose-50 border-rose-200', external: '/quote' },
  { id: 'class',   label: 'Full Class Support', desc: 'We handle your entire course — all assignments', examples: 'Weekly assignments · Exams · Discussions · Full semester', priceFrom: 0, color: 'text-green-600 bg-green-50 border-green-200', external: '/class-support' },
]

export const DESIGN_TYPES: DesignTypeOption[] = [
  { id: 'powerpoint',    label: 'PowerPoint / Slides',   desc: 'Academic & professional presentations',   unit: 'slides' },
  { id: 'infographic',   label: 'Infographic',            desc: 'Visual data story or explainer',          unit: 'designs' },
  { id: 'poster',        label: 'Academic Poster',        desc: 'Research or conference poster',           unit: 'designs' },
  { id: 'social_media',  label: 'Social Media Graphics',  desc: 'Branded graphics for digital channels',   unit: 'designs' },
  { id: 'report_design', label: 'Report / PDF Design',    desc: 'Professionally designed document layout', unit: 'pages' },
  { id: 'other_design',  label: 'Other Design',           desc: 'Describe your needs in requirements',     unit: 'designs' },
]

export const DIAGRAM_TYPES: DiagramTypeOption[] = [
  { id: 'flowchart',  label: 'Flowchart',      desc: 'Process or decision flow' },
  { id: 'er_diagram', label: 'ER Diagram',      desc: 'Entity-relationship / database schema' },
  { id: 'mind_map',   label: 'Mind Map',        desc: 'Concept map or knowledge tree' },
  { id: 'org_chart',  label: 'Org Chart',       desc: 'Organisational structure' },
  { id: 'uml',        label: 'UML Diagram',     desc: 'Class, sequence, use-case diagrams' },
  { id: 'gantt',      label: 'Gantt Chart',     desc: 'Project timeline and schedule' },
  { id: 'network',    label: 'Network Diagram', desc: 'IT or architecture network map' },
  { id: 'other_diag', label: 'Other Diagram',   desc: 'Describe in requirements' },
]

export const DIAGRAM_SOFTWARE = [
  { id: 'any',        label: 'Any (you choose)' },
  { id: 'draw_io',    label: 'Draw.io / Diagrams.net' },
  { id: 'powerpoint', label: 'PowerPoint / Word' },
  { id: 'lucidchart', label: 'Lucidchart' },
  { id: 'visio',      label: 'Microsoft Visio' },
  { id: 'mermaid',    label: 'Mermaid (code)' },
]

export const STATIC_PAPER_TYPES: PaperTypeOption[] = [
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
// Keep PAPER_TYPES as alias for backwards-compat with template imports
export const PAPER_TYPES = STATIC_PAPER_TYPES

export const STATIC_LEVELS: LevelOption[] = [
  { id: 'high_school',   label: 'High School',         basePrice: 15, note: 'Grades 9–12' },
  { id: 'undergrad_1_2', label: 'Undergraduate 1–2',   basePrice: 18, note: 'Freshman / Sophomore' },
  { id: 'undergrad_3_4', label: 'Undergraduate 3–4',   basePrice: 22, note: 'Junior / Senior' },
  { id: 'masters',       label: "Master's",            basePrice: 28, note: 'Graduate level' },
  { id: 'phd',           label: 'PhD / Doctoral',      basePrice: 36, note: 'Dissertation-level' },
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
  { id: 'biology',       label: 'Biology',             category: 'Natural Sciences' },
  { id: 'chemistry',     label: 'Chemistry',           category: 'Natural Sciences' },
  { id: 'physics',       label: 'Physics',             category: 'Natural Sciences' },
  { id: 'mathematics',   label: 'Mathematics',         category: 'Mathematics & Statistics' },
  { id: 'statistics',    label: 'Statistics',          category: 'Mathematics & Statistics' },
  { id: 'engineering',   label: 'Engineering',         category: 'Engineering' },
  { id: 'cs',            label: 'Computer Science',    category: 'Computing & Technology' },
  { id: 'env_science',   label: 'Environmental Sci.',  category: 'Environment & Earth Sciences' },
  { id: 'accounting',    label: 'Accounting',          category: 'Business & Economics' },
  { id: 'finance',       label: 'Finance',             category: 'Business & Economics' },
  { id: 'marketing',     label: 'Marketing',           category: 'Business & Economics' },
  { id: 'economics',     label: 'Economics',           category: 'Business & Economics' },
  { id: 'management',    label: 'Management',          category: 'Business & Economics' },
  { id: 'business_law',  label: 'Business Law',        category: 'Business & Economics' },
  { id: 'nursing',       label: 'Nursing',             category: 'Nursing & Healthcare' },
  { id: 'public_health', label: 'Public Health',       category: 'Health Sciences' },
  { id: 'psychology',    label: 'Psychology',          category: 'Health Sciences' },
  { id: 'pharmacology',  label: 'Pharmacology',        category: 'Health Sciences' },
  { id: 'social_work',   label: 'Social Work',         category: 'Social Sciences' },
  { id: 'history',       label: 'History',             category: 'Humanities & Arts' },
  { id: 'literature',    label: 'Literature',          category: 'Humanities & Arts' },
  { id: 'philosophy',    label: 'Philosophy',          category: 'Humanities & Arts' },
  { id: 'law',           label: 'Law',                 category: 'Law & Legal Studies' },
  { id: 'political_sci', label: 'Political Science',   category: 'Social Sciences' },
  { id: 'education',     label: 'Education',           category: 'Education' },
  { id: 'sociology',     label: 'Sociology',           category: 'Social Sciences' },
]
export const SUBJECTS = STATIC_SUBJECTS

export const STATIC_FORMATTING: FormatOption[] = [
  { id: 'apa7',      label: 'APA 7th Edition' },
  { id: 'mla9',      label: 'MLA 9th Edition' },
  { id: 'chicago17', label: 'Chicago 17th Edition' },
  { id: 'harvard',   label: 'Harvard' },
  { id: 'vancouver', label: 'Vancouver' },
  { id: 'none',      label: 'Not required' },
]
export const FORMATTING_STYLES = STATIC_FORMATTING

export const STATIC_WORK_TYPES: WorkTypeOption[] = [
  { id: 'writing',      label: 'Writing',       desc: 'New paper from scratch' },
  { id: 'editing',      label: 'Editing',       desc: 'Improve an existing draft' },
  { id: 'rewriting',    label: 'Rewriting',     desc: 'Rewrite existing content' },
  { id: 'proofreading', label: 'Proofreading',  desc: 'Fix grammar and formatting' },
]
export const WORK_TYPES = STATIC_WORK_TYPES

export const STATIC_ENGLISH: Array<{ id: string; label: string }> = [
  { id: 'us', label: 'US English' },
  { id: 'uk', label: 'UK English' },
  { id: 'au', label: 'Australian English' },
]
export const ENGLISH_TYPES = STATIC_ENGLISH

export const WRITER_TIERS = [
  { id: 'standard', label: 'Standard', desc: "Verified Master's writer",  surcharge: 0    },
  { id: 'advanced', label: 'Advanced', desc: 'Top-rated, 500+ orders',    surcharge: 0.10 },
  { id: 'expert',   label: 'Expert',   desc: 'PhD-level specialist',      surcharge: 0.20 },
]

// Default base prices (overridden by backend config when available)
const DEFAULT_DESIGN_BASE   = 20
const DEFAULT_DIAGRAM_BASE  = 25

// ── Draft persistence ─────────────────────────────────────────────────────────
const DRAFT_KEY = 'rpm_order_draft'

// ── Composable ────────────────────────────────────────────────────────────────

export function useOrderForm(cfg?: Ref<PublicPricingConfig | null>) {

  // ── Dynamic option arrays (backend → normalized, else static fallback) ──────

  const levels = computed<LevelOption[]>(() => {
    const display = cfg?.value?.academic_levels_display
    const pricing = cfg?.value?.academic_levels
    if (display?.length) {
      return display.map((d, i) => {
        const pricingMatch = pricing?.find(p => p.label.toLowerCase() === d.name.toLowerCase())
          ?? pricing?.[i]
        return {
          id:        d.name,
          label:     d.name,
          basePrice: pricingMatch?.price_per_page ?? STATIC_LEVELS[i]?.basePrice ?? 18,
          note:      d.description ?? '',
        }
      })
    }
    if (pricing?.length) {
      return pricing.map((p, i) => ({
        id:        p.code,
        label:     p.label,
        basePrice: p.price_per_page ?? STATIC_LEVELS[i]?.basePrice ?? 18,
        note:      '',
      }))
    }
    return STATIC_LEVELS
  })

  const paperTypes = computed<PaperTypeOption[]>(() => {
    const display = cfg?.value?.paper_types_display
    if (display?.length) {
      return display.map((d, i) => ({
        id:    d.name,
        label: d.name,
        icon:  STATIC_PAPER_TYPES[i]?.icon ?? 'FileText',
      }))
    }
    return STATIC_PAPER_TYPES
  })

  const deadlines = computed<DeadlineOption[]>(() => {
    const raw = cfg?.value?.deadlines
    if (raw?.length) {
      return raw.map((d, i) => {
        const staticMatch = STATIC_DEADLINES.find(s => s.hours === d.max_hours) ?? STATIC_DEADLINES[i]
        return {
          id:        String(d.max_hours),
          label:     d.label,
          sublabel:  staticMatch?.sublabel ?? '',
          multiplier: d.multiplier,
          hours:     d.max_hours,
          badge:     staticMatch?.badge,
        }
      })
    }
    return STATIC_DEADLINES
  })

  const subjects = computed<SubjectOption[]>(() => {
    const raw = cfg?.value?.subjects
    if (raw?.length) {
      return raw.map(s => ({ id: s.name, label: s.name, category: s.category }))
    }
    return STATIC_SUBJECTS
  })

  const workTypes = computed<WorkTypeOption[]>(() => {
    const raw = cfg?.value?.work_types
    if (raw?.length) {
      return raw.map(w => ({ id: w.name, label: w.name, desc: w.description ?? '' }))
    }
    return STATIC_WORK_TYPES
  })

  const formattingStyles = computed<FormatOption[]>(() => {
    const raw = cfg?.value?.formatting_styles
    if (raw?.length) {
      return raw.map(f => ({ id: f.name, label: f.name }))
    }
    return STATIC_FORMATTING
  })

  const englishTypes = computed<Array<{ id: string; label: string }>>(() => {
    const raw = cfg?.value?.english_types
    if (raw?.length) {
      return raw.map(e => ({ id: e.code || e.name, label: e.name }))
    }
    return STATIC_ENGLISH
  })

  // Available add-ons from backend config
  const addons = computed<CfgAddon[]>(() => cfg?.value?.addons ?? [])

  // Base prices from config (with static fallback)
  const basePricePerSlide   = computed(() => cfg?.value?.base_price_per_slide   ?? DEFAULT_DESIGN_BASE)
  const basePricePerDiagram = computed(() => cfg?.value?.base_price_per_diagram ?? DEFAULT_DIAGRAM_BASE)

  // Spacing multipliers from config
  const spacingMult = computed(() =>
    form.spacing === 'single'
      ? (cfg?.value?.spacing_multipliers?.single ?? 2)
      : (cfg?.value?.spacing_multipliers?.double ?? 1)
  )

  // ── Form state ───────────────────────────────────────────────────────────────

  // Load draft from localStorage
  const savedDraft = import.meta.client
    ? (() => { try { return JSON.parse(localStorage.getItem(DRAFT_KEY) ?? 'null') } catch { return null } })()
    : null

  const form = reactive({
    orderType:          ORDER_TYPES.find(t => t.id === savedDraft?.orderType) ?? ORDER_TYPES[0],
    paperType:          STATIC_PAPER_TYPES[0],
    level:              STATIC_LEVELS[1],
    pages:              savedDraft?.pages ?? 1,
    spacing:            (savedDraft?.spacing as 'double' | 'single') ?? 'double',
    designType:         DESIGN_TYPES[0],
    designUnits:        savedDraft?.designUnits ?? 1,
    designStyle:        savedDraft?.designStyle ?? '',
    diagramType:        DIAGRAM_TYPES[0],
    diagramCount:       savedDraft?.diagramCount ?? 1,
    diagramSoftware:    DIAGRAM_SOFTWARE[0],
    diagramComplexity:  (savedDraft?.diagramComplexity as 'simple' | 'standard' | 'complex') ?? 'standard',
    comboComponent:     (savedDraft?.comboComponent as 'design' | 'diagram') ?? 'design',
    deadline:           STATIC_DEADLINES[0],
    subject:            STATIC_SUBJECTS[0],
    writerTier:         WRITER_TIERS[0],
    topic:              savedDraft?.topic ?? '',
    instructions:       savedDraft?.instructions ?? '',
    workType:           STATIC_WORK_TYPES[0],
    formatStyle:        STATIC_FORMATTING[0],
    references:         savedDraft?.references ?? 0,
    englishType:        STATIC_ENGLISH[0],
    discountCode:       savedDraft?.discountCode ?? '',
    selectedAddonIds:   (savedDraft?.selectedAddonIds as number[]) ?? [],
    firstName:          '',
    lastName:           '',
    email:              '',
    password:           '',
    agreeToTerms:       false,
  })

  // Re-match selections when dynamic arrays load so selected item is from the live list
  watch(levels, (newLevels) => {
    const match = newLevels.find(l => l.id === form.level.id || l.label === form.level.label)
    if (match) form.level = match
    else if (newLevels.length) form.level = newLevels[Math.min(1, newLevels.length - 1)]
  }, { immediate: false })

  watch(paperTypes, (newTypes) => {
    const match = newTypes.find(p => p.id === form.paperType.id || p.label === form.paperType.label)
    if (match) form.paperType = match
    else if (newTypes.length) form.paperType = newTypes[0]
  }, { immediate: false })

  watch(deadlines, (newDeadlines) => {
    const match = newDeadlines.find(d => d.hours === form.deadline.hours)
    if (match) form.deadline = match
    else if (newDeadlines.length) form.deadline = newDeadlines[0]
  }, { immediate: false })

  watch(subjects, (newSubjects) => {
    if (!newSubjects.find(s => s.id === form.subject.id || s.label === form.subject.label) && newSubjects.length) {
      form.subject = newSubjects[0]
    }
  }, { immediate: false })

  // ── Pricing ──────────────────────────────────────────────────────────────────

  const paperBasePrice = computed(() => {
    // price_per_page already incorporates level × base from backend;
    // spacing multiplier is then applied on top
    const levelPrice = form.level.basePrice
    return levelPrice * form.deadline.multiplier * (1 + form.writerTier.surcharge) * spacingMult.value
  })

  const designBasePrice = computed(() =>
    basePricePerSlide.value * form.deadline.multiplier * (1 + form.writerTier.surcharge)
  )

  const diagramBasePrice = computed(() =>
    basePricePerDiagram.value * form.deadline.multiplier * (1 + form.writerTier.surcharge)
  )

  const basePrice = computed(() => {
    if (form.orderType.id === 'design')  return designBasePrice.value
    if (form.orderType.id === 'diagram') return diagramBasePrice.value
    return paperBasePrice.value
  })

  // Combo: paper cost + chosen add-on cost
  const comboPlusPrice = computed(() => {
    if (form.orderType.id !== 'combo') return 0
    if (form.comboComponent === 'design')  return designBasePrice.value  * form.designUnits
    return diagramBasePrice.value * form.diagramCount
  })

  const unitCount = computed(() => {
    if (form.orderType.id === 'design')  return form.designUnits
    if (form.orderType.id === 'diagram') return form.diagramCount
    return form.pages
  })

  const unitLabel = computed(() => {
    if (form.orderType.id === 'design')  return form.designType.unit
    if (form.orderType.id === 'diagram') return 'diagrams'
    return 'pages'
  })

  const addonTotal = computed(() =>
    addons.value
      .filter(a => form.selectedAddonIds.includes(a.id))
      .reduce((sum, a) => sum + a.flat_amount, 0)
  )

  const localTotal    = computed(() => Math.ceil(basePrice.value * unitCount.value + comboPlusPrice.value + addonTotal.value))

  // ── Live price from estimate endpoint ────────────────────────────────────────
  const liveTotal     = ref<number | null>(null)
  const isPricing     = ref(false)
  let _priceTimer: ReturnType<typeof setTimeout> | undefined

  async function _fetchEstimate() {
    if (form.orderType.id !== 'paper' && form.orderType.id !== 'combo') {
      liveTotal.value = null; return
    }
    const apiBase = import.meta.client
      ? (useRuntimeConfig().public.apiBase || '')
      : ''
    if (!apiBase) return
    isPricing.value = true
    try {
      type EstResp = { total?: string | number | null; estimated_min_price?: string | number | null }
      const resp = await $fetch<EstResp>(`${apiBase}/api/v1/pricing/public/estimate/`, {
        method: 'POST',
        credentials: 'include',
        body: {
          paper_type_code:     form.paperType.id,
          academic_level_code: form.level.id,
          pages:               form.pages,
          deadline_hours:      form.deadline.hours,
          spacing:             form.spacing,
        },
      })
      const n = Number(resp?.total ?? resp?.estimated_min_price)
      liveTotal.value = Number.isFinite(n) && n > 0 ? Math.ceil(n) : null
    } catch {
      liveTotal.value = null
    } finally {
      isPricing.value = false
    }
  }

  function _scheduleEstimate() {
    if (_priceTimer) clearTimeout(_priceTimer)
    _priceTimer = setTimeout(() => void _fetchEstimate(), 400)
  }

  if (import.meta.client) {
    watch(
      () => [form.paperType.id, form.level.id, form.deadline.hours, form.pages, form.spacing, form.orderType.id],
      _scheduleEstimate
    )
  }

  const totalPrice    = computed(() => liveTotal.value ?? localTotal.value)
  const pricePerUnit  = computed(() => Math.ceil(totalPrice.value / Math.max(unitCount.value, 1)))

  const wordCount = computed(() =>
    (form.orderType.id === 'paper' || form.orderType.id === 'combo')
      ? form.pages * (form.spacing === 'double' ? 275 : 550)
      : 0
  )

  const deadlineDate = computed(() => {
    const d = new Date()
    d.setHours(d.getHours() + form.deadline.hours)
    return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  })

  // ── Persistence ───────────────────────────────────────────────────────────────

  if (import.meta.client) {
    watch(
      () => ({
        orderType:         form.orderType.id,
        pages:             form.pages,
        spacing:           form.spacing,
        designUnits:       form.designUnits,
        designStyle:       form.designStyle,
        diagramCount:      form.diagramCount,
        diagramComplexity: form.diagramComplexity,
        comboComponent:    form.comboComponent,
        topic:             form.topic,
        instructions:      form.instructions,
        references:        form.references,
        discountCode:      form.discountCode,
        levelId:           form.level.id,
        paperTypeId:       form.paperType.id,
        deadlineHours:     form.deadline.hours,
        subjectId:         form.subject.id,
        workTypeId:        form.workType.id,
        formatStyleId:     form.formatStyle.id,
        englishTypeId:     form.englishType.id,
        writerTierId:      form.writerTier.id,
        selectedAddonIds:  form.selectedAddonIds,
      }),
      (draft) => { try { localStorage.setItem(DRAFT_KEY, JSON.stringify(draft)) } catch {} },
      { deep: true }
    )
  }

  // ── Submit payload builder ────────────────────────────────────────────────────

  function savePendingOrder() {
    const payload = {
      orderType:       form.orderType.id,
      paperType:       form.paperType.label,
      designType:      form.designType.label,
      diagramType:     form.diagramType.label,
      level:           form.level.label,
      pages:           form.pages,
      designUnits:     form.designUnits,
      diagramCount:    form.diagramCount,
      comboComponent:  form.comboComponent,
      spacing:         form.spacing,
      deadline:        form.deadline.label,
      deadlineHours:   form.deadline.hours,
      subject:         form.subject.label,
      writerTier:      form.writerTier.id,
      topic:           form.topic,
      instructions:    form.instructions,
      workType:        form.workType.label,
      formatStyle:     form.formatStyle.label,
      references:      form.references,
      englishType:     form.englishType.label,
      discountCode:    form.discountCode,
      estimatedPrice:  totalPrice.value,
      savedAt:         new Date().toISOString(),
    }
    if (import.meta.client) {
      localStorage.setItem('rpm_pending_order', JSON.stringify(payload))
    }
  }

  // ── Validation ────────────────────────────────────────────────────────────────

  const step1Valid = computed(() => {
    if (form.orderType.id === 'design')  return !!form.designType && form.designUnits >= 1 && !!form.deadline
    if (form.orderType.id === 'diagram') return !!form.diagramType && form.diagramCount >= 1 && !!form.deadline
    if (form.orderType.id === 'combo') {
      const paperOk = !!form.paperType && !!form.level && form.pages >= 1 && !!form.subject
      const plusOk  = form.comboComponent === 'design'
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
    form,
    // dynamic option arrays
    levels, paperTypes, deadlines, subjects, workTypes, formattingStyles, englishTypes, addons,
    // price outputs
    totalPrice, pricePerUnit, unitLabel, unitCount, wordCount, deadlineDate, isPricing, addonTotal,
    // validation
    step1Valid, step2Valid, step3Valid,
    // actions
    savePendingOrder,
  }
}
