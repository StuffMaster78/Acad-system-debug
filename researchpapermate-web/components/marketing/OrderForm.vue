<script setup lang="ts">
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
  source?: string
}

const app    = useAppUrl()
const config = useRuntimeConfig()

const { data: pricingConfig } = await useAsyncData('rpm-pricing-config', fetchPricingConfig)

const levels     = computed<PricingLevel[]>(() => pricingConfig.value?.academic_levels ?? FALLBACK_LEVELS)
const deadlines  = computed<PricingDeadline[]>(() => pricingConfig.value?.deadlines ?? FALLBACK_DEADLINES)
const paperTypes = computed<PricingPaperType[]>(() => pricingConfig.value?.paper_types ?? FALLBACK_PAPER_TYPES)

// Selections
const levelCode   = ref(levels.value[1]?.code ?? levels.value[0]?.code ?? 'undergrad')
const deadlineHrs = ref(deadlines.value[0]?.max_hours ?? 336)
const paperCode   = ref(paperTypes.value[0]?.code ?? 'essay')
const pages       = ref(1)
const topic       = ref('')

// Pricing
const estimate    = ref<EstimateResponse | null>(null)
const isPricing   = ref(false)
const hasLivePrice = ref(false)
let priceTimer: ReturnType<typeof setTimeout> | null = null

const localPrice = computed(() => {
  const lvl = levels.value.find(l => l.code === levelCode.value) ?? levels.value[0]
  const dl  = deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0]
  if (!lvl || !dl) return 0
  const base = lvl.price_per_page ?? 15
  return Math.ceil(base * dl.multiplier * pages.value * 100) / 100
})

const livePrice = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})

const displayPrice  = computed(() => livePrice.value ?? localPrice.value)
const perPage       = computed(() => pages.value > 0 ? displayPrice.value / pages.value : 0)
const pricingLabel  = computed(() => hasLivePrice.value ? 'Live price' : 'Estimated price')
const words         = computed(() => pages.value * 275)

const orderUrl = computed(() => {
  const p = new URLSearchParams({
    type:     paperCode.value,
    level:    levelCode.value,
    deadline: String(deadlineHrs.value),
    pages:    String(pages.value),
  })
  if (topic.value.trim()) p.set('topic', topic.value.trim().slice(0, 200))
  return `${app.order}?${p.toString()}`
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
        body: { paper_type_code: paperCode.value, academic_level_code: levelCode.value, pages: pages.value, deadline_hours: deadlineHrs.value, spacing: 'double' },
        credentials: 'include',
      },
    )
    hasLivePrice.value = true
  } catch {
    estimate.value = null
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
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white shadow-xl overflow-hidden">

    <!-- Header -->
    <div class="bg-brand-700 px-6 py-4">
      <p class="text-xs font-bold uppercase tracking-widest text-brand-200">Instant order form</p>
      <p class="mt-0.5 text-sm text-white/80">Configure your order and see the price before paying anything</p>
    </div>

    <div class="p-6 space-y-5">

      <!-- Paper type -->
      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Paper type</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="pt in paperTypes"
            :key="pt.code"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors"
            :class="paperCode === pt.code
              ? 'border-brand-600 bg-brand-600 text-white'
              : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'"
            @click="paperCode = pt.code"
          >
            {{ pt.label }}
          </button>
        </div>
      </div>

      <!-- Level + Deadline side by side -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Academic level</p>
          <div class="flex flex-col gap-1.5">
            <button
              v-for="lvl in levels"
              :key="lvl.code"
              type="button"
              class="flex items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors text-left"
              :class="levelCode === lvl.code
                ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold'
                : 'border-slate-200 text-slate-600 hover:border-brand-300'"
              @click="levelCode = lvl.code"
            >
              <span>{{ lvl.label }}</span>
              <span v-if="lvl.price_per_page" class="text-xs text-slate-400">from ${{ lvl.price_per_page }}/pg</span>
            </button>
          </div>
        </div>

        <div>
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">Deadline</p>
          <div class="flex flex-col gap-1.5">
            <button
              v-for="dl in deadlines"
              :key="dl.max_hours"
              type="button"
              class="flex items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors text-left"
              :class="deadlineHrs === dl.max_hours
                ? 'border-brand-600 bg-brand-50 text-brand-700 font-semibold'
                : 'border-slate-200 text-slate-600 hover:border-brand-300'"
              @click="deadlineHrs = dl.max_hours"
            >
              <span>{{ dl.label }}</span>
              <span v-if="dl.multiplier > 1" class="text-xs text-slate-400">+{{ Math.round((dl.multiplier - 1) * 100) }}%</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Pages -->
      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
          Pages
          <span class="ml-1 font-normal normal-case text-slate-400">({{ words }} words, double-spaced)</span>
        </p>
        <div class="flex items-center gap-4">
          <button
            type="button"
            class="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30"
            :disabled="pages <= 1"
            @click="pages = Math.max(1, pages - 1)"
          >−</button>
          <span class="w-10 text-center text-xl font-bold text-slate-900 tabular-nums">{{ pages }}</span>
          <button
            type="button"
            class="flex size-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30"
            :disabled="pages >= 100"
            @click="pages = Math.min(100, pages + 1)"
          >+</button>
        </div>
      </div>

      <!-- Topic -->
      <div>
        <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
          Topic / title
          <span class="ml-1 font-normal normal-case text-slate-400">(optional — you can add it in the portal)</span>
        </p>
        <input
          v-model="topic"
          type="text"
          placeholder="e.g. The impact of social media on mental health in teenagers"
          maxlength="200"
          class="h-10 w-full rounded-xl border border-slate-200 px-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
        />
      </div>
    </div>

    <!-- Price + CTA -->
    <div class="border-t border-slate-100 bg-slate-50 px-6 py-4">
      <div class="mb-4 flex items-end justify-between">
        <div>
          <p class="text-xs text-slate-400">{{ pricingLabel }}</p>
          <div class="flex items-baseline gap-2">
            <p class="text-4xl font-extrabold tabular-nums text-brand-700">
              ${{ displayPrice.toFixed(2) }}
            </p>
            <span v-if="isPricing" class="text-xs text-slate-400 animate-pulse">Updating…</span>
          </div>
          <p class="mt-0.5 text-xs text-slate-400">${{ perPage.toFixed(2) }}/page · {{ words }} words</p>
        </div>
        <div class="text-right text-xs text-slate-400 space-y-0.5">
          <p>✓ Price confirmed before payment</p>
          <p>✓ Free revisions included</p>
          <p>✓ Money-back guarantee</p>
        </div>
      </div>

      <a
        :href="orderUrl"
        class="flex h-12 w-full items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand-700"
      >
        Start my order →
      </a>
      <p class="mt-2 text-center text-xs text-slate-400">
        No payment required to continue · Free account in 30 seconds
      </p>
    </div>

  </div>
</template>
