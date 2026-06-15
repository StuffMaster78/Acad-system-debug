<script setup lang="ts">
import {
  ArrowLeft, ArrowRight, Bot, Check, CheckCircle2, Clock,
  FileText, GraduationCap, LayoutTemplate, Lock, MessageSquare,
  RefreshCw, ShieldCheck, Trophy, Zap,
} from '@lucide/vue'
import {
  fetchPricingConfig,
  FALLBACK_LEVELS, FALLBACK_DEADLINES, FALLBACK_PAPER_TYPES,
  type PricingLevel, type PricingDeadline, type PricingPaperType,
} from '~/composables/usePricingConfig'

definePageMeta({ ssr: false })

useHead({ title: 'Place Your Order | GradeCrest' })
useSeoMeta({
  title: 'Place Your Order | GradeCrest',
  description: 'Configure your academic paper order — type, level, deadline, and brief. Human-written by verified experts. Grade or money back.',
})

const app    = useAppUrl()
const config = useRuntimeConfig()

// ── Pricing config ─────────────────────────────────────────────────────────
const levels      = ref<PricingLevel[]>(FALLBACK_LEVELS)
const deadlines   = ref<PricingDeadline[]>(FALLBACK_DEADLINES)
const paperTypes  = ref<PricingPaperType[]>(FALLBACK_PAPER_TYPES)

onMounted(async () => {
  const cfg      = await fetchPricingConfig()
  levels.value   = cfg.academic_levels
  deadlines.value = cfg.deadlines
  paperTypes.value = cfg.paper_types
  levelCode.value    = cfg.academic_levels[1]?.code ?? cfg.academic_levels[0]?.code ?? 'undergrad'
  deadlineHrs.value  = cfg.deadlines[0]?.max_hours ?? 336
  paperCode.value    = cfg.paper_types[0]?.code ?? 'essay'
})

// ── Order types ────────────────────────────────────────────────────────────
const ORDER_TYPES = [
  { id: 'paper',   icon: FileText,       label: 'Paper & Essay',      desc: 'Essays, research papers, dissertations, case studies & coursework',   from: 13, color: 'brand' },
  { id: 'design',  icon: LayoutTemplate, label: 'Slides & Design',    desc: 'PowerPoint presentations, infographics, posters & visual assets',      from: 20, color: 'violet' },
  { id: 'diagram', icon: Zap,            label: 'Diagrams & Charts',  desc: 'Flowcharts, ER diagrams, mind maps, Gantt charts & org charts',        from: 25, color: 'teal' },
  { id: 'class',   icon: GraduationCap,  label: 'Full Class Support', desc: 'Assignments, quizzes, discussions & full-semester course management',   from: 0,  color: 'green', external: '/class-support' },
  { id: 'special', icon: MessageSquare,  label: 'Special Project',    desc: 'Custom work — nursing sims, coding assignments, shadow health & more', from: 0,  color: 'rose',  external: '/quote' },
]

const DESIGN_TYPES = [
  { id: 'powerpoint',  label: 'PowerPoint / Slides', unit: 'slides' },
  { id: 'infographic', label: 'Infographic',          unit: 'designs' },
  { id: 'poster',      label: 'Academic Poster',      unit: 'designs' },
  { id: 'report_layout', label: 'Report / PDF Design', unit: 'pages' },
  { id: 'other_design', label: 'Other Design',         unit: 'designs' },
]

const DIAGRAM_TYPES = [
  { id: 'flowchart',  label: 'Flowchart' },
  { id: 'er_diagram', label: 'ER Diagram' },
  { id: 'mind_map',   label: 'Mind Map' },
  { id: 'uml',        label: 'UML Diagram' },
  { id: 'gantt',      label: 'Gantt Chart' },
  { id: 'other_diag', label: 'Other Diagram' },
]

// ── Form state ─────────────────────────────────────────────────────────────
const step         = ref(0)
const orderTypeId  = ref('paper')
const paperCode    = ref(FALLBACK_PAPER_TYPES[0]?.code ?? 'essay')
const levelCode    = ref(FALLBACK_LEVELS[1]?.code ?? 'undergrad')
const deadlineHrs  = ref(FALLBACK_DEADLINES[0]?.max_hours ?? 336)
const units        = ref(1)          // pages or slides or designs
const designTypeId = ref(DESIGN_TYPES[0].id)
const diagramTypeId = ref(DIAGRAM_TYPES[0].id)
const topic        = ref('')
const instructions = ref('')

const orderType    = computed(() => ORDER_TYPES.find(t => t.id === orderTypeId.value) ?? ORDER_TYPES[0])
const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])
const unitLabel    = computed(() => {
  if (orderTypeId.value === 'design') return DESIGN_TYPES.find(d => d.id === designTypeId.value)?.unit ?? 'designs'
  if (orderTypeId.value === 'diagram') return 'diagrams'
  return 'pages'
})
const wordCount = computed(() => unitLabel.value === 'pages' ? units.value * 275 : null)

// ── Live price ─────────────────────────────────────────────────────────────
type EstimateResp = { total?: string | number | null; estimated_min_price?: string | number | null }
const estimate     = ref<EstimateResp | null>(null)
const isPricing    = ref(false)
const hasLivePrice = ref(false)
let priceTimer: ReturnType<typeof setTimeout> | null = null

const localPrice = computed(() => {
  if (orderTypeId.value !== 'paper') {
    const base = orderType.value.from || 25
    return Math.ceil(base * units.value * 100) / 100
  }
  const base = selectedLevel.value?.price_per_page ?? 15
  const mult = selectedDeadline.value?.multiplier ?? 1
  return Math.ceil(base * mult * units.value * 100) / 100
})

const livePrice = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})

const displayPrice = computed(() => livePrice.value ?? localPrice.value)
const perUnit      = computed(() => units.value > 0 ? displayPrice.value / units.value : 0)

async function refreshEstimate() {
  if (orderTypeId.value !== 'paper') { estimate.value = null; return }
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
        spacing:             'double',
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

watch([orderTypeId, paperCode, levelCode, deadlineHrs, units], scheduleEstimate)
onMounted(() => void refreshEstimate())

// ── Portal redirect URL ────────────────────────────────────────────────────
const portalUrl = computed(() => {
  const p: Record<string, string> = {
    order_type: orderTypeId.value,
    pages:      String(units.value),
    deadline:   String(deadlineHrs.value),
  }
  if (orderTypeId.value === 'paper') {
    p.type  = paperCode.value
    p.level = levelCode.value
  } else if (orderTypeId.value === 'design') {
    p.design_type = designTypeId.value
  } else if (orderTypeId.value === 'diagram') {
    p.diagram_type = diagramTypeId.value
  }
  if (topic.value.trim()) p.topic = topic.value.trim().slice(0, 200)
  return `${app.order}?${new URLSearchParams(p)}`
})

// ── Validation ─────────────────────────────────────────────────────────────
const step1Valid = computed(() => units.value >= 1 && deadlineHrs.value > 0)
const step2Valid = computed(() => topic.value.trim().length >= 3)

function selectType(id: string, external?: string) {
  if (external) { window.location.href = external; return }
  orderTypeId.value = id
  step.value = 1
}

const deadlineLabel = computed(() => {
  const dl = selectedDeadline.value
  if (!dl) return ''
  const d = Math.floor(dl.max_hours / 24)
  const h = dl.max_hours % 24
  if (d === 0) return `${h}h`
  if (h === 0) return `${d} day${d > 1 ? 's' : ''}`
  return `${d}d ${h}h`
})

const colorMap: Record<string, { pill: string; btn: string; bg: string; ring: string }> = {
  brand:  { pill: 'border-brand-200  bg-brand-50  text-brand-700',  btn: 'bg-brand-600  hover:bg-brand-700  text-white', bg: 'bg-brand-600',  ring: 'border-brand-500'  },
  violet: { pill: 'border-violet-200 bg-violet-50 text-violet-700', btn: 'bg-violet-600 hover:bg-violet-700 text-white', bg: 'bg-violet-600', ring: 'border-violet-500' },
  teal:   { pill: 'border-teal-200   bg-teal-50   text-teal-700',   btn: 'bg-teal-600   hover:bg-teal-700   text-white', bg: 'bg-teal-600',   ring: 'border-teal-500'   },
  green:  { pill: 'border-green-200  bg-green-50  text-green-700',  btn: 'bg-green-600  hover:bg-green-700  text-white', bg: 'bg-green-600',  ring: 'border-green-500'  },
  rose:   { pill: 'border-rose-200   bg-rose-50   text-rose-700',   btn: 'bg-rose-600   hover:bg-rose-700   text-white', bg: 'bg-rose-600',   ring: 'border-rose-500'   },
}
const colors = computed(() => colorMap[orderType.value.color] ?? colorMap.brand)
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20 pt-20">

    <!-- ── Step header ──────────────────────────────────────────────────── -->
    <div v-if="step > 0" class="sticky top-16 z-30 border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3 sm:px-6">
        <button class="flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors" @click="step > 1 ? step-- : (step = 0)">
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

      <!-- ── Step 0: Order type ──────────────────────────────────────────── -->
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
            <component :is="ot.icon" class="h-7 w-7" />
            <div>
              <p class="font-bold text-slate-900">{{ ot.label }}</p>
              <p class="mt-0.5 text-xs text-slate-500 leading-relaxed">{{ ot.desc }}</p>
            </div>
            <div v-if="ot.from" class="mt-auto text-xs font-semibold">from ${{ ot.from }}</div>
            <div class="mt-auto flex items-center gap-1 text-xs font-semibold transition-all group-hover:gap-2">
              <span>{{ ot.external ? 'Get a quote' : 'Start order' }}</span>
              <ArrowRight class="h-3 w-3" />
            </div>
          </button>
        </div>

        <!-- Trust strip -->
        <div class="mt-10 flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-slate-500">
          <span class="flex items-center gap-1.5"><Trophy class="h-4 w-4 text-amber-500" /> Grade or money back</span>
          <span class="flex items-center gap-1.5"><Bot class="h-4 w-4 text-blue-500" /> 100% human-written</span>
          <span class="flex items-center gap-1.5"><ShieldCheck class="h-4 w-4 text-green-500" /> Free plagiarism report</span>
          <span class="flex items-center gap-1.5"><Lock class="h-4 w-4 text-slate-400" /> Secure & confidential</span>
        </div>
      </div>

      <!-- ── Step 1: Configure ───────────────────────────────────────────── -->
      <div v-else-if="step === 1" class="py-8">
        <div class="mb-6">
          <span class="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold" :class="colors.pill">
            <component :is="orderType.icon" class="h-4 w-4" /> {{ orderType.label }}
          </span>
          <h2 class="mt-3 text-2xl font-extrabold text-slate-900">Configure your order</h2>
        </div>

        <div class="grid gap-6 lg:grid-cols-3">
          <div class="space-y-5 lg:col-span-2">

            <!-- Paper type (paper only) -->
            <div v-if="orderTypeId === 'paper'">
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Paper type</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="pt in paperTypes" :key="pt.code"
                  class="rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors"
                  :class="paperCode === pt.code ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-600 hover:border-brand-400'"
                  @click="paperCode = pt.code"
                >{{ pt.label }}</button>
              </div>
            </div>

            <!-- Design type (design only) -->
            <div v-if="orderTypeId === 'design'">
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Design type</p>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <button
                  v-for="dt in DESIGN_TYPES" :key="dt.id"
                  class="rounded-xl border px-3 py-2 text-sm text-left transition-colors"
                  :class="designTypeId === dt.id ? 'border-violet-600 bg-violet-50 font-semibold text-violet-700' : 'border-slate-200 text-slate-600 hover:border-violet-300'"
                  @click="designTypeId = dt.id"
                >{{ dt.label }}</button>
              </div>
            </div>

            <!-- Diagram type (diagram only) -->
            <div v-if="orderTypeId === 'diagram'">
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Diagram type</p>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <button
                  v-for="dt in DIAGRAM_TYPES" :key="dt.id"
                  class="rounded-xl border px-3 py-2 text-sm text-left transition-colors"
                  :class="diagramTypeId === dt.id ? 'border-teal-600 bg-teal-50 font-semibold text-teal-700' : 'border-slate-200 text-slate-600 hover:border-teal-300'"
                  @click="diagramTypeId = dt.id"
                >{{ dt.label }}</button>
              </div>
            </div>

            <!-- Academic level (paper only) -->
            <div v-if="orderTypeId === 'paper'">
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Academic level</p>
              <div class="space-y-1.5">
                <button
                  v-for="lvl in levels" :key="lvl.code"
                  class="flex w-full items-center justify-between rounded-xl border px-4 py-2.5 text-sm transition-colors text-left"
                  :class="levelCode === lvl.code ? 'border-brand-600 bg-brand-50 font-semibold text-brand-700' : 'border-slate-200 text-slate-600 hover:border-brand-300'"
                  @click="levelCode = lvl.code"
                >
                  <span>{{ lvl.label }}</span>
                  <span v-if="lvl.price_per_page" class="text-xs text-slate-400">from ${{ lvl.price_per_page }}/pg</span>
                </button>
              </div>
            </div>

            <!-- Deadline -->
            <div>
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Deadline</p>
              <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <button
                  v-for="dl in deadlines" :key="dl.max_hours"
                  class="flex flex-col items-start rounded-xl border px-3 py-2.5 text-sm transition-colors"
                  :class="deadlineHrs === dl.max_hours ? 'border-brand-600 bg-brand-50 font-semibold text-brand-700' : 'border-slate-200 text-slate-600 hover:border-brand-300'"
                  @click="deadlineHrs = dl.max_hours"
                >
                  <span>{{ dl.label }}</span>
                  <span v-if="dl.multiplier > 1" class="text-[10px] text-slate-400">+{{ Math.round((dl.multiplier - 1) * 100) }}%</span>
                </button>
              </div>
            </div>

            <!-- Units (pages / slides / designs) -->
            <div>
              <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                {{ unitLabel === 'pages' ? 'Pages' : unitLabel === 'slides' ? 'Slides' : 'Quantity' }}
                <span v-if="wordCount" class="ml-1 font-normal normal-case text-slate-400">({{ wordCount }} words)</span>
              </p>
              <div class="flex items-center gap-5">
                <button class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30" :disabled="units <= 1" @click="units--">−</button>
                <span class="w-10 text-center text-2xl font-bold tabular-nums text-slate-900">{{ units }}</span>
                <button class="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30" :disabled="units >= 200" @click="units++">+</button>
              </div>
            </div>
          </div>

          <!-- Sticky price card -->
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

        <!-- Footer CTA -->
        <div class="mt-8 flex items-center justify-between rounded-xl bg-brand-50 px-5 py-4">
          <div>
            <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimated price' }}</p>
            <p class="text-2xl font-extrabold tabular-nums text-brand-700">
              ${{ displayPrice.toFixed(2) }}
              <span v-if="isPricing" class="ml-1 animate-pulse text-xs font-normal text-brand-400">…</span>
            </p>
          </div>
          <button
            class="rounded-xl px-6 py-3 text-sm font-bold transition-colors"
            :class="step1Valid ? `${colors.btn}` : 'cursor-not-allowed bg-slate-200 text-slate-400'"
            :disabled="!step1Valid"
            @click="step = 2"
          >
            Next — Add brief <ArrowRight class="ml-1 inline h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- ── Step 2: Brief ───────────────────────────────────────────────── -->
      <div v-else-if="step === 2" class="py-8">
        <h2 class="mb-6 text-2xl font-extrabold text-slate-900">Add your brief</h2>

        <div class="space-y-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
              Title / topic <span class="text-brand-600">*</span>
            </label>
            <input
              v-model="topic"
              type="text"
              maxlength="200"
              placeholder="e.g. The impact of remote work on corporate productivity"
              class="h-11 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100 transition-colors"
            />
            <p v-if="topic.trim().length > 0 && topic.trim().length < 3" class="mt-1 text-xs text-rose-500">Please add a bit more detail.</p>
          </div>

          <div>
            <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
              Additional instructions
              <span class="ml-1 font-normal normal-case text-slate-400">(optional — you can add more after logging in)</span>
            </label>
            <textarea
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
            :class="step2Valid ? `${colors.btn}` : 'cursor-not-allowed bg-slate-200 text-slate-400'"
            :disabled="!step2Valid"
            @click="step = 3"
          >
            Review order <ArrowRight class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- ── Step 3: Review ──────────────────────────────────────────────── -->
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
              <div v-if="orderTypeId === 'paper'" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Paper type</dt>
                <dd class="font-medium text-slate-800">{{ paperTypes.find(p => p.code === paperCode)?.label ?? paperCode }}</dd>
              </div>
              <div v-if="orderTypeId === 'design'" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Design type</dt>
                <dd class="font-medium text-slate-800">{{ DESIGN_TYPES.find(d => d.id === designTypeId)?.label }}</dd>
              </div>
              <div v-if="orderTypeId === 'diagram'" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Diagram type</dt>
                <dd class="font-medium text-slate-800">{{ DIAGRAM_TYPES.find(d => d.id === diagramTypeId)?.label }}</dd>
              </div>
              <div v-if="orderTypeId === 'paper'" class="flex justify-between py-2.5">
                <dt class="text-slate-500">Academic level</dt>
                <dd class="font-medium text-slate-800">{{ selectedLevel?.label }}</dd>
              </div>
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">Deadline</dt>
                <dd class="font-medium text-slate-800">{{ deadlineLabel }}</dd>
              </div>
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">{{ unitLabel === 'pages' ? 'Pages' : unitLabel === 'slides' ? 'Slides' : 'Quantity' }}</dt>
                <dd class="font-medium text-slate-800">
                  {{ units }}{{ wordCount ? ` (${wordCount} words)` : '' }}
                </dd>
              </div>
              <div class="flex justify-between py-2.5">
                <dt class="text-slate-500">Topic</dt>
                <dd class="max-w-[60%] text-right font-medium leading-snug text-slate-800">{{ topic }}</dd>
              </div>
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
