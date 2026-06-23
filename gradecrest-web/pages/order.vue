<script setup lang="ts">
import { type Component } from 'vue'
import {
  ArrowLeft, ArrowRight, Bot, Check, CheckCircle2, ChevronDown, Clock,
  FileText, GraduationCap, Layers, LayoutTemplate, Lock, MessageSquare,
  RefreshCw, ShieldCheck, Trophy, Zap,
} from '@lucide/vue'
import {
  fetchPricingConfig,
  FALLBACK_LEVELS, FALLBACK_DEADLINES, FALLBACK_PAPER_TYPES,
  type CfgAddon, type PricingLevel, type PricingDeadline, type PricingPaperType,
} from '~/composables/usePricingConfig'

definePageMeta({ ssr: false })

useHead({ title: 'Place Your Order | GradeCrest' })
useSeoMeta({
  title: 'Place Your Order | GradeCrest',
  description: 'Configure your academic paper order — type, level, deadline, and brief. Human-written by verified experts. Grade or money back.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const app    = useAppUrl()
const config = useRuntimeConfig()
const route  = useRoute()

// ── Pricing config ──────────────────────────────────────────────────────────
const levels             = ref<PricingLevel[]>(FALLBACK_LEVELS)
const deadlines          = ref<PricingDeadline[]>(FALLBACK_DEADLINES)
const paperTypes         = ref<PricingPaperType[]>(FALLBACK_PAPER_TYPES)
const spacingMultipliers = ref({ double: 1, single: 2 })
const cfgSubjects        = ref<{ name: string; category: string }[]>([])
const cfgWorkTypes       = ref<{ name: string; description?: string | null }[]>([])
const cfgFormattingStyles = ref<{ name: string }[]>([])
const cfgEnglishTypes    = ref<{ name: string; code: string }[]>([])
const gcAddons           = ref<CfgAddon[]>([])

const GC_DRAFT_KEY = 'gc_order_draft'
const savedDraft = import.meta.client
  ? (() => { try { return JSON.parse(localStorage.getItem(GC_DRAFT_KEY) ?? 'null') } catch { return null } })()
  : null

const selectedAddonIds = ref<number[]>((savedDraft?.selectedAddonIds as number[]) ?? [])
const gcAddonTotal     = computed(() =>
  gcAddons.value
    .filter(a => selectedAddonIds.value.includes(a.id))
    .reduce((sum, a) => sum + Number(a.flat_amount), 0)
)

// ── Static fallbacks ────────────────────────────────────────────────────────
const STATIC_SUBJECTS = [
  { id: 'biology',     label: 'Biology',           category: 'Natural Sciences'       },
  { id: 'chemistry',   label: 'Chemistry',          category: 'Natural Sciences'       },
  { id: 'physics',     label: 'Physics',            category: 'Natural Sciences'       },
  { id: 'mathematics', label: 'Mathematics',        category: 'Mathematics & Statistics' },
  { id: 'statistics',  label: 'Statistics',         category: 'Mathematics & Statistics' },
  { id: 'cs',          label: 'Computer Science',   category: 'Computing & Technology' },
  { id: 'engineering', label: 'Engineering',        category: 'Computing & Technology' },
  { id: 'psychology',  label: 'Psychology',         category: 'Social Sciences'        },
  { id: 'sociology',   label: 'Sociology',          category: 'Social Sciences'        },
  { id: 'history',     label: 'History',            category: 'Humanities'             },
  { id: 'literature',  label: 'Literature / English', category: 'Humanities'           },
  { id: 'philosophy',  label: 'Philosophy',         category: 'Humanities'             },
  { id: 'business',    label: 'Business Admin.',    category: 'Business & Economics'   },
  { id: 'economics',   label: 'Economics',          category: 'Business & Economics'   },
  { id: 'marketing',   label: 'Marketing',          category: 'Business & Economics'   },
  { id: 'accounting',  label: 'Accounting / Finance', category: 'Business & Economics' },
  { id: 'nursing',     label: 'Nursing',            category: 'Healthcare'             },
  { id: 'medicine',    label: 'Medicine / Health',  category: 'Healthcare'             },
  { id: 'law',         label: 'Law',                category: 'Law & Education'        },
  { id: 'education',   label: 'Education',          category: 'Law & Education'        },
  { id: 'other',       label: 'Other',              category: 'General'                },
]
const STATIC_FORMATTING = [
  { id: 'apa7',      label: 'APA 7th'       },
  { id: 'mla9',      label: 'MLA 9th'       },
  { id: 'chicago17', label: 'Chicago 17th'  },
  { id: 'harvard',   label: 'Harvard'       },
  { id: 'ieee',      label: 'IEEE'          },
  { id: 'none',      label: 'Not required'  },
]
const STATIC_WORK_TYPES = [
  { id: 'writing',      label: 'Writing'      },
  { id: 'editing',      label: 'Editing'      },
  { id: 'rewriting',    label: 'Rewriting'    },
  { id: 'proofreading', label: 'Proofreading' },
]

const subjects = computed(() =>
  cfgSubjects.value.length
    ? cfgSubjects.value.map(s => ({ id: s.name, label: s.name, category: s.category }))
    : STATIC_SUBJECTS
)
const formattingStyles = computed(() =>
  cfgFormattingStyles.value.length
    ? cfgFormattingStyles.value.map(f => ({ id: f.name, label: f.name }))
    : STATIC_FORMATTING
)
const workTypes = computed(() =>
  cfgWorkTypes.value.length
    ? cfgWorkTypes.value.map(w => ({ id: w.name, label: w.name }))
    : STATIC_WORK_TYPES
)
const subjectGroups = computed(() => {
  const g: Record<string, { id: string; label: string }[]> = {}
  for (const s of subjects.value) (g[s.category] ??= []).push({ id: s.id, label: s.label })
  return Object.entries(g).sort(([a], [b]) => a.localeCompare(b))
})

onMounted(async () => {
  const cfg        = await fetchPricingConfig()
  levels.value     = cfg.academic_levels
  deadlines.value  = cfg.deadlines
  paperTypes.value = cfg.paper_types
  spacingMultipliers.value   = cfg.spacing_multipliers
  cfgSubjects.value          = cfg.subjects
  cfgWorkTypes.value         = cfg.work_types
  cfgFormattingStyles.value  = cfg.formatting_styles
  cfgEnglishTypes.value      = cfg.english_types
  gcAddons.value             = cfg.addons

  if (!savedDraft) {
    levelCode.value   = cfg.academic_levels[1]?.code ?? cfg.academic_levels[0]?.code ?? 'undergrad'
    deadlineHrs.value = cfg.deadlines[0]?.max_hours ?? 336
    paperCode.value   = cfg.paper_types[0]?.code ?? 'essay'
  }

  const q = route.query
  const serviceSlug = q.service as string | undefined
  if (serviceSlug) {
    const mappedCode = SERVICE_TO_PAPER[serviceSlug]
    if (mappedCode) paperCode.value = mappedCode
    orderTypeId.value = 'paper'
    step.value = 1
  }

  const qtype = String(q.type ?? '')
  if (qtype && !serviceSlug) {
    if (['writing', 'editing', 'proofreading', 'rewriting'].includes(qtype)) {
      orderTypeId.value = 'paper'
      workTypeId.value  = qtype
    } else if (qtype === 'design') {
      orderTypeId.value = 'design'
    } else if (qtype === 'diagram') {
      orderTypeId.value = 'diagram'
    } else if (qtype === 'combo') {
      orderTypeId.value = 'combo'
    }
    if (qtype) step.value = 1
  }

  if (q.level && cfg.academic_levels.some(l => l.code === String(q.level)))
    levelCode.value = String(q.level)
  if (q.deadline) {
    const hrs = Number(q.deadline)
    if (cfg.deadlines.some(d => d.max_hours === hrs)) deadlineHrs.value = hrs
  }
  if (q.pages) { const pg = Number(q.pages); if (pg >= 1 && pg <= 200) units.value = pg }
  if (q.slides) { const sl = Number(q.slides); if (sl >= 1 && sl <= 100) comboSlides.value = sl }
  if (q.paper && cfg.paper_types.some(p => p.code === String(q.paper))) paperCode.value = String(q.paper)
  if (q.subject) subjectId.value = String(q.subject)
  if (q.work_type && STATIC_WORK_TYPES.some(w => w.id === String(q.work_type))) workTypeId.value = String(q.work_type)
  if (q.spacing === 'single') spacing.value = 'single'
  if (q.format_style) formatStyleId.value = String(q.format_style)
  if (q.topic) topic.value = String(q.topic).trim().slice(0, 200)
  if (q.instructions) instructions.value = String(q.instructions).trim().slice(0, 2000)
  const addonCodes = q.addons ?? q.addon_codes
  if (addonCodes) {
    const codes = String(addonCodes).split(',').filter(Boolean)
    const ids = cfg.addons.filter(a => codes.includes(a.addon_code)).map(a => a.id)
    if (ids.length) selectedAddonIds.value.push(...ids)
  }
})

// ── Service slug → paper type pre-fill ─────────────────────────────────────
const SERVICE_TO_PAPER: Record<string, string> = {
  'essay-writing':        'essay',
  'research-papers':      'research_paper',
  'dissertations':        'dissertation',
  'thesis-writing':       'dissertation',
  'term-papers':          'term_paper',
  'case-studies':         'case_study',
  'literature-review':    'literature_review',
  'coursework':           'coursework',
  'nursing-essays':       'essay',
  'data-analysis':        'data_analysis',
  'capstone-projects':    'capstone',
  'admission-essays':     'admission_essay',
  'homework-help':        'essay',
  'editing-proofreading': 'essay',
}

// ── Order types ─────────────────────────────────────────────────────────────
const ORDER_TYPE_ICONS: Record<string, Component> = {
  FileText, LayoutTemplate, Zap, GraduationCap, MessageSquare, Layers,
}
const ORDER_TYPES = [
  { id: 'paper',   iconKey: 'FileText',       label: 'Paper & Essay',      desc: 'Essays, research papers, dissertations, case studies & coursework',        from: 13, color: 'brand'  },
  { id: 'combo',   iconKey: 'Layers',         label: 'Paper + Slides',     desc: 'Written paper and a matching slide presentation — one order, one expert',  from: 13, color: 'indigo' },
  { id: 'design',  iconKey: 'LayoutTemplate', label: 'Slides & Design',    desc: 'PowerPoint presentations, infographics, posters & visual assets',           from: 20, color: 'violet' },
  { id: 'diagram', iconKey: 'Zap',            label: 'Diagrams & Charts',  desc: 'Flowcharts, ER diagrams, mind maps, Gantt charts & org charts',             from: 25, color: 'teal'   },
  { id: 'class',   iconKey: 'GraduationCap',  label: 'Full Class Support', desc: 'Assignments, quizzes, discussions & full-semester course management',       from: 0,  color: 'green',  external: `${app.order}?order_type=class`   },
  { id: 'special', iconKey: 'MessageSquare',  label: 'Special Project',    desc: 'Custom work — nursing sims, coding assignments, shadow health & more',     from: 0,  color: 'rose',   external: `${app.order}?order_type=special` },
]

const DESIGN_TYPES = [
  { id: 'powerpoint',    label: 'PowerPoint / Slides',   unit: 'slides'  },
  { id: 'infographic',   label: 'Infographic',            unit: 'designs' },
  { id: 'poster',        label: 'Academic Poster',        unit: 'designs' },
  { id: 'report_layout', label: 'Report / PDF Design',    unit: 'pages'   },
  { id: 'other_design',  label: 'Other Design',           unit: 'designs' },
]

const DIAGRAM_TYPES = [
  { id: 'flowchart',  label: 'Flowchart'    },
  { id: 'er_diagram', label: 'ER Diagram'   },
  { id: 'mind_map',   label: 'Mind Map'     },
  { id: 'uml',        label: 'UML Diagram'  },
  { id: 'gantt',      label: 'Gantt Chart'  },
  { id: 'other_diag', label: 'Other'        },
]

// ── Form state ──────────────────────────────────────────────────────────────
const step          = ref(0)
const orderTypeId   = ref(savedDraft?.orderTypeId   ?? 'paper')
const paperCode     = ref(savedDraft?.paperCode     ?? FALLBACK_PAPER_TYPES[0]?.code ?? 'essay')
const levelCode     = ref(savedDraft?.levelCode     ?? FALLBACK_LEVELS[1]?.code ?? 'undergrad')
const deadlineHrs   = ref<number>(savedDraft?.deadlineHrs ?? FALLBACK_DEADLINES[0]?.max_hours ?? 336)
const units         = ref(savedDraft?.units         ?? 1)
const comboSlides   = ref(savedDraft?.comboSlides   ?? 5)
const spacing       = ref<'double' | 'single'>(savedDraft?.spacing ?? 'double')
const designTypeId  = ref(savedDraft?.designTypeId  ?? DESIGN_TYPES[0].id)
const diagramTypeId = ref(savedDraft?.diagramTypeId ?? DIAGRAM_TYPES[0].id)
const subjectId     = ref(savedDraft?.subjectId     ?? '')
const formatStyleId = ref(savedDraft?.formatStyleId ?? 'apa7')
const workTypeId    = ref(savedDraft?.workTypeId    ?? 'writing')
const topic         = ref(savedDraft?.topic         ?? '')
const instructions  = ref(savedDraft?.instructions  ?? '')

// Convenience flags
const isPaper        = computed(() => orderTypeId.value === 'paper')
const isCombo        = computed(() => orderTypeId.value === 'combo')
const isDesign       = computed(() => orderTypeId.value === 'design')
const isDiagram      = computed(() => orderTypeId.value === 'diagram')
const isWritingOrder = computed(() => isPaper.value || isCombo.value)

// Draft persistence
if (import.meta.client) {
  watch(
    () => ({
      orderTypeId: orderTypeId.value, paperCode: paperCode.value, levelCode: levelCode.value,
      deadlineHrs: deadlineHrs.value, units: units.value, comboSlides: comboSlides.value,
      spacing: spacing.value, designTypeId: designTypeId.value, diagramTypeId: diagramTypeId.value,
      subjectId: subjectId.value, formatStyleId: formatStyleId.value, workTypeId: workTypeId.value,
      topic: topic.value, instructions: instructions.value, selectedAddonIds: selectedAddonIds.value,
    }),
    (draft) => { try { localStorage.setItem(GC_DRAFT_KEY, JSON.stringify(draft)) } catch {} },
    { deep: true }
  )
}

const orderType        = computed(() => ORDER_TYPES.find(t => t.id === orderTypeId.value) ?? ORDER_TYPES[0])
const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])
const unitLabel        = computed(() => {
  if (isDesign.value) return DESIGN_TYPES.find(d => d.id === designTypeId.value)?.unit ?? 'designs'
  if (isDiagram.value) return 'diagrams'
  return 'pages'
})
const spacingMult = computed(() => spacing.value === 'single' ? spacingMultipliers.value.single : spacingMultipliers.value.double)
const wordCount   = computed(() => unitLabel.value === 'pages' ? units.value * (spacing.value === 'double' ? 275 : 550) : null)

// ── Live price ──────────────────────────────────────────────────────────────
type EstimateResp = { total?: string | number | null; estimated_min_price?: string | number | null }
const estimate     = ref<EstimateResp | null>(null)
const isPricing    = ref(false)
const hasLivePrice = ref(false)
let priceTimer: ReturnType<typeof setTimeout> | null = null

const localPrice = computed(() => {
  if (isDesign.value || isDiagram.value) {
    return Math.ceil((orderType.value.from || 25) * units.value * 100) / 100
  }
  const paperBase = (selectedLevel.value?.price_per_page ?? 15) * (selectedDeadline.value?.multiplier ?? 1) * spacingMult.value * units.value
  if (isCombo.value) {
    const slidesBase = 20 * comboSlides.value
    return Math.ceil((paperBase + slidesBase) * 100) / 100
  }
  return Math.ceil(paperBase * 100) / 100
})

const livePrice    = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})
const displayPrice = computed(() => (livePrice.value ?? localPrice.value) + gcAddonTotal.value)
const perUnit      = computed(() => units.value > 0 ? displayPrice.value / units.value : 0)

async function refreshEstimate() {
  if (!isWritingOrder.value) { estimate.value = null; return }
  const apiBase = config.public.apiBase || ''
  if (!apiBase) return
  isPricing.value = true
  try {
    estimate.value = await $fetch<EstimateResp>(`${apiBase}/api/v1/pricing/public/estimate/`, {
      method: 'POST',
      body: {
        paper_type_code:     paperCode.value,
        academic_level_code: levelCode.value,
        pages:               units.value,
        deadline_hours:      deadlineHrs.value,
        spacing:             spacing.value,
      },
      credentials: 'include',
    })
    hasLivePrice.value = true
  } catch {
    estimate.value = null; hasLivePrice.value = false
  } finally {
    isPricing.value = false
  }
}

function scheduleEstimate() {
  if (priceTimer) clearTimeout(priceTimer)
  priceTimer = setTimeout(() => void refreshEstimate(), 400)
}

watch([orderTypeId, paperCode, levelCode, deadlineHrs, units, spacing], scheduleEstimate)
onMounted(() => { void refreshEstimate() })

// ── Portal URL ──────────────────────────────────────────────────────────────
const portalUrl = computed(() => {
  const p: Record<string, string> = {
    order_type: orderTypeId.value,
    deadline:   String(deadlineHrs.value),
  }
  if (isWritingOrder.value) {
    p.type      = paperCode.value
    p.level     = levelCode.value
    p.work_type = workTypeId.value
    p.spacing   = spacing.value
    p.pages     = String(units.value)
    if (subjectId.value)     p.subject      = subjectId.value
    if (formatStyleId.value) p.format_style = formatStyleId.value
  }
  if (isCombo.value)   p.slides       = String(comboSlides.value)
  if (isDesign.value)  { p.design_type = designTypeId.value;  p.quantity = String(units.value) }
  if (isDiagram.value) { p.diagram_type = diagramTypeId.value; p.quantity = String(units.value) }
  if (topic.value.trim())        p.topic        = topic.value.trim().slice(0, 200)
  if (instructions.value.trim()) p.instructions = instructions.value.trim().slice(0, 2000)
  if (selectedAddonIds.value.length) {
    const codes = gcAddons.value.filter(a => selectedAddonIds.value.includes(a.id)).map(a => a.addon_code)
    if (codes.length) p.addon_codes = codes.join(',')
  }
  return `${app.order}?${new URLSearchParams(p)}`
})

// ── Validation ──────────────────────────────────────────────────────────────
const step1Valid = computed(() =>
  units.value >= 1 &&
  deadlineHrs.value > 0 &&
  (!isCombo.value || comboSlides.value >= 1)
)
const step2Valid = computed(() => topic.value.trim().length >= 3)

const deadlineLabel = computed(() => {
  const dl = selectedDeadline.value
  if (!dl) return ''
  const d = Math.floor(dl.max_hours / 24)
  const h = dl.max_hours % 24
  if (d === 0) return `${h}h`
  if (h === 0) return `${d} day${d > 1 ? 's' : ''}`
  return `${d}d ${h}h`
})

// ── Colors ──────────────────────────────────────────────────────────────────
const colorMap: Record<string, { pill: string; btn: string; bg: string; ring: string }> = {
  brand:  { pill: 'border-brand-200  bg-brand-50  text-brand-700',  btn: 'bg-brand-600  hover:bg-brand-700  text-white', bg: 'bg-brand-600',  ring: 'border-brand-500'  },
  indigo: { pill: 'border-indigo-200 bg-indigo-50 text-indigo-700', btn: 'bg-indigo-600 hover:bg-indigo-700 text-white', bg: 'bg-indigo-600', ring: 'border-indigo-500' },
  violet: { pill: 'border-violet-200 bg-violet-50 text-violet-700', btn: 'bg-violet-600 hover:bg-violet-700 text-white', bg: 'bg-violet-600', ring: 'border-violet-500' },
  teal:   { pill: 'border-teal-200   bg-teal-50   text-teal-700',   btn: 'bg-teal-600   hover:bg-teal-700   text-white', bg: 'bg-teal-600',   ring: 'border-teal-500'   },
  green:  { pill: 'border-green-200  bg-green-50  text-green-700',  btn: 'bg-green-600  hover:bg-green-700  text-white', bg: 'bg-green-600',  ring: 'border-green-500'  },
  rose:   { pill: 'border-rose-200   bg-rose-50   text-rose-700',   btn: 'bg-rose-600   hover:bg-rose-700   text-white', bg: 'bg-rose-600',   ring: 'border-rose-500'   },
}
const colors = computed(() => colorMap[orderType.value.color] ?? colorMap.brand)

function selectType(id: string, external?: string) {
  if (external) { window.location.href = external; return }
  orderTypeId.value = id
  step.value = 1
}

function toggleAddon(id: number) {
  const idx = selectedAddonIds.value.indexOf(id)
  if (idx >= 0) selectedAddonIds.value.splice(idx, 1)
  else selectedAddonIds.value.push(id)
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20 pt-20">

    <!-- ── Step header (steps 1-3) ────────────────────────────────────────── -->
    <div v-if="step > 0" class="sticky top-16 z-30 border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3 sm:px-6">
        <button
          class="flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
          @click="step > 1 ? step-- : (step = 0)"
        >
          <ArrowLeft class="h-4 w-4" />
          {{ step === 1 ? 'Order types' : 'Back' }}
        </button>
        <div class="flex items-center gap-1">
          <div
            v-for="s in [1, 2, 3]"
            :key="s"
            class="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold transition-colors"
            :class="step > s ? 'bg-brand-600 text-white' : step === s ? 'bg-brand-600 text-white' : 'bg-slate-200 text-slate-400'"
          >
            <Check v-if="step > s" class="h-3 w-3" />
            <span v-else>{{ s }}</span>
          </div>
        </div>
        <div class="flex items-center gap-1.5 rounded-full bg-brand-700 px-3 py-1 text-xs font-bold text-white">
          ${{ displayPrice.toFixed(2) }}
          <span v-if="isPricing" class="animate-pulse">…</span>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-3xl px-4 sm:px-6">

      <!-- ════════════════════════════════════════════════════════════════════
           Step 0 — Order type selection
           ════════════════════════════════════════════════════════════════════ -->
      <div v-if="step === 0" class="py-10">
        <div class="mb-8 text-center">
          <h1 class="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">What do you need?</h1>
          <p class="mt-2 text-slate-500">Select your order type to get started</p>
        </div>

        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <button
            v-for="ot in ORDER_TYPES"
            :key="ot.id"
            class="group flex flex-col items-start gap-2 rounded-2xl border-2 p-5 text-left transition-all hover:-translate-y-0.5 hover:shadow-md"
            :class="colorMap[ot.color].pill"
            @click="selectType(ot.id, ot.external)"
          >
            <component :is="ORDER_TYPE_ICONS[ot.iconKey]" class="h-7 w-7" />
            <div>
              <p class="font-bold text-slate-900">{{ ot.label }}</p>
              <p class="mt-0.5 text-xs text-slate-500 leading-relaxed">{{ ot.desc }}</p>
            </div>
            <div v-if="ot.from" class="mt-auto text-xs font-semibold">from ${{ ot.from }}/page</div>
            <div class="mt-auto flex items-center gap-1 text-xs font-semibold transition-all group-hover:gap-2">
              <span>{{ ot.external ? 'Continue →' : 'Start order' }}</span>
              <ArrowRight class="h-3 w-3" />
            </div>
          </button>
        </div>

        <div class="mt-10 flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-slate-500">
          <span class="flex items-center gap-1.5"><Trophy class="h-4 w-4 text-amber-500" /> Grade or money back</span>
          <span class="flex items-center gap-1.5"><Bot class="h-4 w-4 text-blue-500" /> 100% human-written</span>
          <span class="flex items-center gap-1.5"><ShieldCheck class="h-4 w-4 text-green-500" /> Free plagiarism report</span>
          <span class="flex items-center gap-1.5"><Lock class="h-4 w-4 text-slate-400" /> Secure & confidential</span>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════════════
           Step 1 — Configure
           ════════════════════════════════════════════════════════════════════ -->
      <div v-else-if="step === 1" class="py-8">

        <!-- Order type badge -->
        <div class="mb-5">
          <span class="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold" :class="colors.pill">
            <component :is="ORDER_TYPE_ICONS[orderType.iconKey]" class="h-4 w-4" />
            {{ orderType.label }}
          </span>
          <h2 class="mt-3 text-2xl font-extrabold text-slate-900">Configure your order</h2>
        </div>

        <div class="grid gap-6 lg:grid-cols-3">

          <!-- Left: all config fields -->
          <div class="space-y-4 lg:col-span-2">

            <!-- ── Select grid ─────────────────────────────────────────── -->
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">

              <!-- Work type (paper + combo) -->
              <div v-if="isWritingOrder">
                <label for="gc-order-work-type" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Work type</label>
                <div class="relative">
                  <select
                    id="gc-order-work-type"
                    v-model="workTypeId"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option v-for="wt in workTypes" :key="wt.id" :value="wt.id">{{ wt.label }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Paper type (paper + combo) -->
              <div v-if="isWritingOrder">
                <label for="gc-order-paper-type" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Paper type</label>
                <div class="relative">
                  <select
                    id="gc-order-paper-type"
                    v-model="paperCode"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Design type (design) -->
              <div v-if="isDesign">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Design type</label>
                <div class="relative">
                  <select
                    v-model="designTypeId"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-100"
                  >
                    <option v-for="dt in DESIGN_TYPES" :key="dt.id" :value="dt.id">{{ dt.label }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Diagram type (diagram) -->
              <div v-if="isDiagram">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Diagram type</label>
                <div class="relative">
                  <select
                    v-model="diagramTypeId"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-teal-400 focus:outline-none focus:ring-2 focus:ring-teal-100"
                  >
                    <option v-for="dt in DIAGRAM_TYPES" :key="dt.id" :value="dt.id">{{ dt.label }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Academic level (paper + combo) -->
              <div v-if="isWritingOrder">
                <label for="gc-order-level" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Academic level</label>
                <div class="relative">
                  <select
                    id="gc-order-level"
                    v-model="levelCode"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option v-for="lvl in levels" :key="lvl.code" :value="lvl.code">
                      {{ lvl.label }}{{ lvl.price_per_page ? ` — from $${lvl.price_per_page}/pg` : '' }}
                    </option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Deadline (all types) -->
              <div>
                <label for="gc-order-deadline" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Deadline</label>
                <div class="relative">
                  <select
                    id="gc-order-deadline"
                    v-model.number="deadlineHrs"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option v-for="dl in deadlines" :key="dl.max_hours" :value="dl.max_hours">
                      {{ dl.label }}{{ dl.multiplier > 1 ? ` (+${Math.round((dl.multiplier - 1) * 100)}%)` : '' }}
                    </option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Subject (paper + combo, optional) -->
              <div v-if="isWritingOrder">
                <label for="gc-order-subject" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">
                  Subject <span class="font-normal normal-case text-slate-400">(optional)</span>
                </label>
                <div class="relative">
                  <select
                    id="gc-order-subject"
                    v-model="subjectId"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option value="">Any / not listed</option>
                    <optgroup v-for="[cat, items] in subjectGroups" :key="cat" :label="cat">
                      <option v-for="s in items" :key="s.id" :value="s.id">{{ s.label }}</option>
                    </optgroup>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <!-- Formatting style (paper + combo) -->
              <div v-if="isWritingOrder">
                <label for="gc-order-format" class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Formatting style</label>
                <div class="relative">
                  <select
                    id="gc-order-format"
                    v-model="formatStyleId"
                    class="w-full appearance-none rounded-xl border border-slate-200 bg-white px-3 py-2.5 pr-8 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
                  >
                    <option v-for="f in formattingStyles" :key="f.id" :value="f.id">{{ f.label }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

            </div>
            <!-- /select grid -->

            <!-- ── Quantity row ────────────────────────────────────────── -->
            <div class="flex flex-wrap items-end gap-6">

              <!-- Pages stepper (paper + combo + diagram) -->
              <div v-if="isWritingOrder || isDiagram">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">
                  Pages
                  <span v-if="wordCount" class="ml-1 font-normal normal-case text-slate-400">({{ wordCount }} words)</span>
                </label>
                <div class="flex items-center gap-3">
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-brand-400 hover:text-brand-600 disabled:opacity-30 transition-colors" :disabled="units <= 1" @click="units > 1 && units--">−</button>
                  <span class="w-8 text-center text-xl font-bold tabular-nums text-slate-900">{{ units }}</span>
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-brand-400 hover:text-brand-600 disabled:opacity-30 transition-colors" :disabled="units >= 200" @click="units < 200 && units++">+</button>
                </div>
              </div>

              <!-- Slides stepper (combo — additional to pages) -->
              <div v-if="isCombo">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Slides</label>
                <div class="flex items-center gap-3">
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-indigo-400 hover:text-indigo-600 disabled:opacity-30 transition-colors" :disabled="comboSlides <= 1" @click="comboSlides > 1 && comboSlides--">−</button>
                  <span class="w-8 text-center text-xl font-bold tabular-nums text-slate-900">{{ comboSlides }}</span>
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-indigo-400 hover:text-indigo-600 disabled:opacity-30 transition-colors" :disabled="comboSlides >= 100" @click="comboSlides < 100 && comboSlides++">+</button>
                </div>
              </div>

              <!-- Slides / Designs stepper (design only) -->
              <div v-if="isDesign">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">
                  {{ DESIGN_TYPES.find(d => d.id === designTypeId)?.unit === 'slides' ? 'Slides' : unitLabel === 'pages' ? 'Pages' : 'Designs' }}
                </label>
                <div class="flex items-center gap-3">
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-violet-400 hover:text-violet-600 disabled:opacity-30 transition-colors" :disabled="units <= 1" @click="units > 1 && units--">−</button>
                  <span class="w-8 text-center text-xl font-bold tabular-nums text-slate-900">{{ units }}</span>
                  <button class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:border-violet-400 hover:text-violet-600 disabled:opacity-30 transition-colors" :disabled="units >= 200" @click="units < 200 && units++">+</button>
                </div>
              </div>

              <!-- Spacing toggle (paper + combo) -->
              <div v-if="isWritingOrder">
                <label class="mb-1.5 block text-xs font-bold uppercase tracking-widest text-slate-400">Spacing</label>
                <div class="flex gap-2">
                  <button
                    v-for="sp in [{ id: 'double', label: 'Double', sub: '275 w/pg' }, { id: 'single', label: 'Single', sub: '550 w/pg' }]"
                    :key="sp.id"
                    type="button"
                    class="rounded-xl border px-3 py-2 text-xs transition-all"
                    :class="spacing === sp.id ? 'border-brand-500 bg-brand-50 font-semibold text-brand-800' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
                    @click="spacing = sp.id as any"
                  >
                    <span class="block font-medium">{{ sp.label }}</span>
                    <span class="block text-[11px] opacity-60">{{ sp.sub }}</span>
                  </button>
                </div>
              </div>

            </div>
            <!-- /quantity row -->

            <!-- ── Add-ons ─────────────────────────────────────────────── -->
            <div v-if="gcAddons.length">
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                Add-ons <span class="font-normal normal-case text-slate-400">(optional)</span>
              </p>
              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <label
                  v-for="addon in gcAddons"
                  :key="addon.id"
                  class="flex cursor-pointer items-start gap-3 rounded-xl border bg-white p-3 transition-colors"
                  :class="selectedAddonIds.includes(addon.id) ? 'border-gc-500 bg-gc-50' : 'border-slate-200 hover:border-slate-300'"
                >
                  <input
                    type="checkbox"
                    class="mt-0.5 h-4 w-4 shrink-0 rounded border-slate-300 text-gc-600"
                    :checked="selectedAddonIds.includes(addon.id)"
                    @change="toggleAddon(addon.id)"
                  />
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-slate-900">{{ addon.name }}</p>
                    <p v-if="addon.description" class="mt-0.5 text-xs text-slate-500">{{ addon.description }}</p>
                  </div>
                  <span class="shrink-0 text-sm font-semibold text-gc-700">+${{ addon.flat_amount }}</span>
                </label>
              </div>
            </div>

          </div>
          <!-- /left column -->

          <!-- Right: sticky price card -->
          <div class="hidden lg:block">
            <div class="sticky top-28 rounded-2xl border border-brand-100 bg-white p-5 shadow-sm">
              <h3 class="mb-3 text-xs font-bold uppercase tracking-wider text-slate-400">Price estimate</h3>
              <div class="rounded-xl bg-brand-50 px-4 py-3">
                <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimate' }}</p>
                <p class="text-3xl font-extrabold tabular-nums text-brand-700">
                  ${{ displayPrice.toFixed(2) }}
                  <span v-if="isPricing" class="ml-1 animate-pulse text-xs font-normal text-brand-400">…</span>
                </p>
                <p class="text-xs text-brand-500">${{ perUnit.toFixed(2) }}/{{ unitLabel.replace(/s$/, '') }}</p>
              </div>
              <ul v-if="gcAddonTotal > 0" class="mt-3 space-y-1 border-t border-brand-100 pt-3 text-xs text-slate-500">
                <li v-for="addon in gcAddons.filter(a => selectedAddonIds.includes(a.id))" :key="addon.id" class="flex justify-between">
                  <span>+ {{ addon.name }}</span>
                  <span class="font-semibold text-slate-700">+${{ addon.flat_amount }}</span>
                </li>
              </ul>
              <ul class="mt-4 space-y-2 text-xs text-slate-500">
                <li class="flex items-center gap-2"><Trophy class="h-3.5 w-3.5 shrink-0 text-amber-500" /> Grade or money back</li>
                <li class="flex items-center gap-2"><Bot class="h-3.5 w-3.5 shrink-0 text-blue-500" /> 100% human-written</li>
                <li class="flex items-center gap-2"><ShieldCheck class="h-3.5 w-3.5 shrink-0 text-green-500" /> Free plagiarism report</li>
                <li class="flex items-center gap-2"><RefreshCw class="h-3.5 w-3.5 shrink-0 text-purple-500" /> Unlimited revisions</li>
                <li class="flex items-center gap-2"><Clock class="h-3.5 w-3.5 shrink-0 text-brand-400" /> On-time delivery</li>
              </ul>
            </div>
          </div>

        </div>
        <!-- /grid -->

        <!-- Footer CTA -->
        <div class="mt-6 flex items-center justify-between rounded-xl bg-brand-50 px-5 py-4">
          <div>
            <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimated price' }}</p>
            <p class="text-2xl font-extrabold tabular-nums text-brand-700">
              ${{ displayPrice.toFixed(2) }}
              <span v-if="isPricing" class="ml-1 animate-pulse text-xs font-normal text-brand-400">…</span>
            </p>
          </div>
          <button
            class="rounded-xl px-6 py-3 text-sm font-bold transition-colors"
            :class="step1Valid ? colors.btn : 'cursor-not-allowed bg-slate-200 text-slate-400'"
            :disabled="!step1Valid"
            @click="step = 2"
          >
            Next — Add brief <ArrowRight class="ml-1 inline h-4 w-4" />
          </button>
        </div>

      </div>

      <!-- ════════════════════════════════════════════════════════════════════
           Step 2 — Brief
           ════════════════════════════════════════════════════════════════════ -->
      <div v-else-if="step === 2" class="py-8">
        <h2 class="mb-6 text-2xl font-extrabold text-slate-900">Add your brief</h2>

        <div class="space-y-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <label for="gc-order-topic" class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
              Title / topic <span class="text-brand-600">*</span>
            </label>
            <input
              id="gc-order-topic"
              v-model="topic"
              type="text"
              maxlength="200"
              placeholder="e.g. The impact of remote work on corporate productivity"
              class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100 transition-colors"
            />
            <p v-if="topic.trim().length > 0 && topic.trim().length < 3" class="mt-1 text-xs text-rose-500">Please add a bit more detail.</p>
          </div>

          <div>
            <label for="gc-order-instructions" class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
              Additional instructions
              <span class="ml-1 font-normal normal-case text-slate-400">(optional — you can add more after logging in)</span>
            </label>
            <textarea
              id="gc-order-instructions"
              v-model="instructions"
              rows="5"
              placeholder="Rubric requirements, formatting style, specific sources to include, grading criteria, special notes…"
              class="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100 transition-colors"
            />
          </div>

          <div class="rounded-xl border border-brand-100 bg-brand-50 px-4 py-3 text-xs text-brand-700">
            <strong>Tip:</strong> The more detail you add here, the better your writer match. You can still add files, rubrics, and feedback after placing the order.
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button class="flex items-center gap-2 rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors" @click="step = 1">
            <ArrowLeft class="h-4 w-4" /> Back
          </button>
          <button
            class="flex flex-1 items-center justify-center gap-2 rounded-xl py-3 text-sm font-bold transition-colors"
            :class="step2Valid ? colors.btn : 'cursor-not-allowed bg-slate-200 text-slate-400'"
            :disabled="!step2Valid"
            @click="step = 3"
          >
            Review order <ArrowRight class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- ════════════════════════════════════════════════════════════════════
           Step 3 — Review
           ════════════════════════════════════════════════════════════════════ -->
      <div v-else-if="step === 3" class="py-8">
        <h2 class="mb-6 text-2xl font-extrabold text-slate-900">Review your order</h2>

        <div class="space-y-4">
          <!-- Summary card -->
          <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 class="mb-4 text-sm font-bold uppercase tracking-wider text-slate-400">Order summary</h3>
            <dl class="divide-y divide-slate-100 text-sm">
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">Order type</dt>
                <dd class="font-medium text-slate-800">{{ orderType.label }}</dd>
              </div>
              <div v-if="isWritingOrder" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Work type</dt>
                <dd class="font-medium text-slate-800">{{ workTypes.find(w => w.id === workTypeId)?.label ?? workTypeId }}</dd>
              </div>
              <div v-if="isWritingOrder" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Paper type</dt>
                <dd class="font-medium text-slate-800">{{ paperTypes.find(p => p.code === paperCode)?.label ?? paperCode }}</dd>
              </div>
              <div v-if="isDesign" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Design type</dt>
                <dd class="font-medium text-slate-800">{{ DESIGN_TYPES.find(d => d.id === designTypeId)?.label }}</dd>
              </div>
              <div v-if="isDiagram" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Diagram type</dt>
                <dd class="font-medium text-slate-800">{{ DIAGRAM_TYPES.find(d => d.id === diagramTypeId)?.label }}</dd>
              </div>
              <div v-if="isWritingOrder" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Academic level</dt>
                <dd class="font-medium text-slate-800">{{ selectedLevel?.label }}</dd>
              </div>
              <div v-if="isWritingOrder && subjectId" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Subject</dt>
                <dd class="font-medium text-slate-800">{{ subjects.find(s => s.id === subjectId)?.label ?? subjectId }}</dd>
              </div>
              <div v-if="isWritingOrder" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Formatting</dt>
                <dd class="font-medium text-slate-800">{{ formattingStyles.find(f => f.id === formatStyleId)?.label ?? formatStyleId }}</dd>
              </div>
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">Deadline</dt>
                <dd class="font-medium text-slate-800">{{ deadlineLabel }}</dd>
              </div>
              <div v-if="isWritingOrder || isDiagram" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Pages</dt>
                <dd class="font-medium text-slate-800">{{ units }}{{ wordCount ? ` (${wordCount} words)` : '' }}</dd>
              </div>
              <div v-if="isCombo" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Slides</dt>
                <dd class="font-medium text-slate-800">{{ comboSlides }}</dd>
              </div>
              <div v-if="isDesign" class="flex justify-between py-2.5">
                <dt class="text-slate-500">{{ DESIGN_TYPES.find(d => d.id === designTypeId)?.unit === 'slides' ? 'Slides' : 'Quantity' }}</dt>
                <dd class="font-medium text-slate-800">{{ units }}</dd>
              </div>
              <div v-if="isWritingOrder" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Spacing</dt>
                <dd class="font-medium text-slate-800">{{ spacing === 'double' ? 'Double spaced' : 'Single spaced' }}</dd>
              </div>
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">Topic</dt>
                <dd class="max-w-[60%] text-right font-medium leading-snug text-slate-800">{{ topic }}</dd>
              </div>
              <template v-if="gcAddons.filter(a => selectedAddonIds.includes(a.id)).length">
                <div
                  v-for="addon in gcAddons.filter(a => selectedAddonIds.includes(a.id))"
                  :key="addon.id"
                  class="flex justify-between py-2.5"
                >
                  <dt class="text-slate-500">Add-on</dt>
                  <dd class="font-medium text-slate-800">{{ addon.name }} <span class="text-gc-600">(+${{ addon.flat_amount }})</span></dd>
                </div>
              </template>
            </dl>
          </div>

          <!-- Price card -->
          <div class="flex items-center justify-between rounded-2xl bg-brand-50 px-6 py-4">
            <div>
              <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimated price' }}</p>
              <p class="text-4xl font-extrabold tabular-nums text-brand-700">${{ displayPrice.toFixed(2) }}</p>
              <p class="text-xs text-brand-500">${{ perUnit.toFixed(2) }}/{{ unitLabel.replace(/s$/, '') }}</p>
            </div>
            <div class="text-right text-xs text-brand-600 space-y-1">
              <p class="flex items-center justify-end gap-1"><CheckCircle2 class="h-3.5 w-3.5" /> Price locked at checkout</p>
              <p class="flex items-center justify-end gap-1"><CheckCircle2 class="h-3.5 w-3.5" /> Free revisions included</p>
              <p class="flex items-center justify-end gap-1"><CheckCircle2 class="h-3.5 w-3.5" /> Grade or money back</p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3">
            <button class="flex items-center gap-2 rounded-xl border border-slate-200 px-5 py-3.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors" @click="step = 2">
              <ArrowLeft class="h-4 w-4" /> Edit
            </button>
            <a
              :href="portalUrl"
              class="flex flex-1 h-14 items-center justify-center gap-2 rounded-xl text-sm font-bold shadow-sm transition-colors"
              :class="colors.btn"
            >
              Place my order <ArrowRight class="h-4 w-4" />
            </a>
          </div>
          <p class="text-center text-xs text-slate-400">No payment until you approve your paper · Free account in 30 seconds</p>
        </div>

      </div>

    </div>
  </div>
</template>
