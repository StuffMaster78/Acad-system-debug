<script setup lang="ts">
/**
 * Multi-step public order form.
 *
 * Step 1 — Configure: paper type · academic level · deadline · pages
 * Step 2 — Brief: topic · instructions
 * Step 3 — Review: price summary · redirect to portal
 *
 * Options come from the backend /api/v1/pricing/public/config/ endpoint so
 * they stay in sync with whatever the admin has configured. Falls back to
 * static constants when the API is unavailable.
 */
import {
  fetchPricingConfig,
  FALLBACK_LEVELS,
  FALLBACK_DEADLINES,
  FALLBACK_PAPER_TYPES,
  type PricingLevel,
  type PricingDeadline,
  type PricingPaperType,
} from '~/composables/usePricingConfig'

type EstimateResponse = {
  total?: string | number | null
  estimated_min_price?: string | number | null
  currency?: string
}

const app    = useAppUrl()
const config = useRuntimeConfig()

// ── Live config from backend ───────────────────────────────────────────────
const { data: pricingConfig } = await useAsyncData('em-pricing-config', fetchPricingConfig)

const levels     = computed<PricingLevel[]>(() => pricingConfig.value?.academic_levels ?? FALLBACK_LEVELS)
const deadlines  = computed<PricingDeadline[]>(() => pricingConfig.value?.deadlines ?? FALLBACK_DEADLINES)
const paperTypes = computed<PricingPaperType[]>(() => pricingConfig.value?.paper_types ?? FALLBACK_PAPER_TYPES)

// ── Form state ─────────────────────────────────────────────────────────────
const step         = ref<1 | 2 | 3>(1)
const paperCode    = ref(paperTypes.value[0]?.code ?? 'essay')
const levelCode    = ref(levels.value[1]?.code ?? levels.value[0]?.code ?? 'undergrad')
const deadlineHrs  = ref(deadlines.value[0]?.max_hours ?? 336)
const pages        = ref(1)
const topic        = ref('')
const instructions = ref('')

// ── Pricing ────────────────────────────────────────────────────────────────
const estimate     = ref<EstimateResponse | null>(null)
const isPricing    = ref(false)
const hasLivePrice = ref(false)
let   priceTimer: ReturnType<typeof setTimeout> | null = null

const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])

const localPrice = computed(() => {
  const base = selectedLevel.value?.price_per_page ?? 15
  const mult = selectedDeadline.value?.multiplier ?? 1
  return Math.ceil(base * mult * pages.value * 100) / 100
})

const livePrice = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})

const displayPrice = computed(() => livePrice.value ?? localPrice.value)
const perPage      = computed(() => pages.value > 0 ? displayPrice.value / pages.value : 0)
const words        = computed(() => pages.value * 275)

const deadlineLabel = computed(() => {
  const dl = selectedDeadline.value
  if (!dl) return ''
  const d = Math.floor(dl.max_hours / 24)
  const h = dl.max_hours % 24
  if (d === 0) return `${h}h deadline`
  if (h === 0) return `${d}-day deadline`
  return `${d}d ${h}h deadline`
})

async function refreshEstimate() {
  if (import.meta.server) return
  const apiBase = config.public.apiBase || ''
  if (!apiBase) return
  isPricing.value = true
  try {
    estimate.value = await $fetch<EstimateResponse>(
      `${apiBase}/api/v1/pricing/public/estimate/`,
      {
        method: 'POST',
        body: {
          paper_type_code:     paperCode.value,
          academic_level_code: levelCode.value,
          pages:               pages.value,
          deadline_hours:      deadlineHrs.value,
          spacing:             'double',
        },
        credentials: 'include',
      },
    )
    hasLivePrice.value = true
  } catch {
    estimate.value    = null
    hasLivePrice.value = false
  } finally {
    isPricing.value = false
  }
}

function scheduleEstimate() {
  if (priceTimer) clearTimeout(priceTimer)
  priceTimer = setTimeout(() => { void refreshEstimate() }, 300)
}

onMounted(() => { void refreshEstimate() })
watch([paperCode, levelCode, deadlineHrs, pages], scheduleEstimate)

// ── Order URL (final step) ─────────────────────────────────────────────────
const orderUrl = computed(() => {
  const p = new URLSearchParams({
    type:     paperCode.value,
    level:    levelCode.value,
    deadline: String(deadlineHrs.value),
    pages:    String(pages.value),
  })
  if (topic.value.trim())        p.set('topic', topic.value.trim().slice(0, 200))
  return `${app.order}?${p.toString()}`
})

// ── Step validation ────────────────────────────────────────────────────────
const step1Valid = computed(() => !!paperCode.value && !!levelCode.value && deadlineHrs.value > 0 && pages.value >= 1)
const step2Valid = computed(() => topic.value.trim().length >= 3)

function next() {
  if (step.value === 1 && step1Valid.value) step.value = 2
  else if (step.value === 2 && step2Valid.value) step.value = 3
}
function back() {
  if (step.value > 1) step.value = (step.value - 1) as 1 | 2 | 3
}
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">

    <!-- Step indicator -->
    <div class="flex border-b border-slate-100 bg-slate-50">
      <div
        v-for="(label, i) in ['Configure', 'Your brief', 'Review & order']"
        :key="i"
        class="flex flex-1 items-center justify-center gap-1.5 py-3 text-xs font-semibold transition-colors"
        :class="step === i + 1 ? 'text-brand-700 border-b-2 border-brand-600 bg-white' : step > i + 1 ? 'text-brand-500' : 'text-slate-400'"
      >
        <span
          class="flex size-5 items-center justify-center rounded-full text-[10px] font-bold"
          :class="step > i + 1 ? 'bg-brand-600 text-white' : step === i + 1 ? 'bg-brand-600 text-white' : 'bg-slate-200 text-slate-500'"
        >{{ step > i + 1 ? '✓' : i + 1 }}</span>
        <span class="hidden sm:inline">{{ label }}</span>
      </div>
    </div>

    <!-- ── Step 1: Configure ─────────────────────────────────────────────── -->
    <div v-if="step === 1" class="p-6 space-y-5">

      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Paper type</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="pt in paperTypes" :key="pt.code"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors"
            :class="paperCode === pt.code ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'"
            @click="paperCode = pt.code"
          >{{ pt.label }}</button>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Academic level</p>
          <div class="space-y-1.5">
            <button
              v-for="lvl in levels" :key="lvl.code"
              type="button"
              class="flex w-full items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors text-left"
              :class="levelCode === lvl.code ? 'border-brand-600 bg-brand-50 font-semibold text-brand-700' : 'border-slate-200 text-slate-600 hover:border-brand-300'"
              @click="levelCode = lvl.code"
            >
              <span>{{ lvl.label }}</span>
              <span v-if="lvl.price_per_page" class="text-xs text-slate-400">from ${{ lvl.price_per_page }}/pg</span>
            </button>
          </div>
        </div>

        <div>
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Deadline</p>
          <div class="space-y-1.5 max-h-64 overflow-y-auto pr-1">
            <button
              v-for="dl in deadlines" :key="dl.max_hours"
              type="button"
              class="flex w-full items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors text-left"
              :class="deadlineHrs === dl.max_hours ? 'border-brand-600 bg-brand-50 font-semibold text-brand-700' : 'border-slate-200 text-slate-600 hover:border-brand-300'"
              @click="deadlineHrs = dl.max_hours"
            >
              <span>{{ dl.label }}</span>
              <span v-if="dl.multiplier > 1" class="text-xs text-slate-400">+{{ Math.round((dl.multiplier - 1) * 100) }}%</span>
            </button>
          </div>
        </div>
      </div>

      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
          Pages
          <span class="ml-1 font-normal normal-case text-slate-400">({{ words }} words, double-spaced)</span>
        </p>
        <div class="flex items-center gap-4">
          <button type="button" class="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30" :disabled="pages <= 1" @click="pages--">−</button>
          <span class="w-10 text-center text-xl font-bold tabular-nums text-slate-900">{{ pages }}</span>
          <button type="button" class="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30" :disabled="pages >= 100" @click="pages++">+</button>
        </div>
      </div>

      <!-- Running price footer -->
      <div class="flex items-center justify-between rounded-xl bg-brand-50 px-5 py-3">
        <div>
          <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimated price' }}</p>
          <p class="text-2xl font-extrabold tabular-nums text-brand-700">
            ${{ displayPrice.toFixed(2) }}
            <span v-if="isPricing" class="ml-1 animate-pulse text-xs font-normal text-brand-400">…</span>
          </p>
        </div>
        <button
          class="rounded-xl px-5 py-2.5 text-sm font-bold transition-colors"
          :class="step1Valid ? 'bg-brand-600 text-white hover:bg-brand-700' : 'cursor-not-allowed bg-slate-200 text-slate-400'"
          :disabled="!step1Valid"
          type="button"
          @click="next"
        >
          Next →
        </button>
      </div>
    </div>

    <!-- ── Step 2: Brief ─────────────────────────────────────────────────── -->
    <div v-else-if="step === 2" class="p-6 space-y-5">
      <div>
        <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
          Paper title / topic <span class="text-brand-600">*</span>
        </label>
        <input
          v-model="topic"
          type="text"
          placeholder="e.g. The impact of social media on adolescent mental health"
          maxlength="200"
          class="h-10 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
        <p v-if="topic.trim().length > 0 && topic.trim().length < 3" class="mt-1 text-xs text-red-500">Please add a bit more detail.</p>
      </div>

      <div>
        <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-400">
          Additional instructions
          <span class="ml-1 font-normal normal-case text-slate-400">(optional — you can add more in the portal)</span>
        </label>
        <textarea
          v-model="instructions"
          rows="4"
          placeholder="Specific requirements, formatting style, sources to include, grading rubric details…"
          class="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100 resize-none"
        />
      </div>

      <div class="flex gap-3">
        <button type="button" class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors" @click="back">← Back</button>
        <button
          type="button"
          class="flex-1 rounded-xl py-2.5 text-sm font-bold transition-colors"
          :class="step2Valid ? 'bg-brand-600 text-white hover:bg-brand-700' : 'cursor-not-allowed bg-slate-200 text-slate-400'"
          :disabled="!step2Valid"
          @click="next"
        >Review order →</button>
      </div>
    </div>

    <!-- ── Step 3: Review ────────────────────────────────────────────────── -->
    <div v-else class="p-6 space-y-4">
      <h3 class="text-base font-bold text-slate-900">Order summary</h3>

      <dl class="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-slate-50 text-sm">
        <div class="flex justify-between px-4 py-2.5">
          <dt class="text-slate-500">Paper type</dt>
          <dd class="font-medium text-slate-800">{{ paperTypes.find(p => p.code === paperCode)?.label ?? paperCode }}</dd>
        </div>
        <div class="flex justify-between px-4 py-2.5">
          <dt class="text-slate-500">Academic level</dt>
          <dd class="font-medium text-slate-800">{{ selectedLevel?.label }}</dd>
        </div>
        <div class="flex justify-between px-4 py-2.5">
          <dt class="text-slate-500">Deadline</dt>
          <dd class="font-medium text-slate-800">{{ deadlineLabel }}</dd>
        </div>
        <div class="flex justify-between px-4 py-2.5">
          <dt class="text-slate-500">Length</dt>
          <dd class="font-medium text-slate-800">{{ pages }} page{{ pages > 1 ? 's' : '' }} ({{ words }} words)</dd>
        </div>
        <div v-if="topic.trim()" class="flex justify-between px-4 py-2.5">
          <dt class="text-slate-500">Topic</dt>
          <dd class="font-medium text-slate-800 text-right max-w-[60%] leading-snug">{{ topic }}</dd>
        </div>
      </dl>

      <div class="flex items-center justify-between rounded-xl bg-brand-50 px-5 py-3">
        <div>
          <p class="text-xs text-brand-600">{{ hasLivePrice ? 'Live price' : 'Estimated price' }}</p>
          <p class="text-3xl font-extrabold tabular-nums text-brand-700">${{ displayPrice.toFixed(2) }}</p>
          <p class="text-xs text-brand-500">${{ perPage.toFixed(2) }}/page</p>
        </div>
        <div class="text-right text-xs text-brand-600 space-y-0.5">
          <p>✓ Price locked at checkout</p>
          <p>✓ Free revisions</p>
        </div>
      </div>

      <div class="flex gap-3">
        <button type="button" class="rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors" @click="back">← Edit</button>
        <a
          :href="orderUrl"
          class="flex flex-1 h-12 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand-700"
        >
          Place my order →
        </a>
      </div>
      <p class="text-center text-xs text-slate-400">No payment until you approve · Free account in 30 seconds</p>
    </div>

  </div>
</template>
