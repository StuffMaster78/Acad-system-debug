<script setup lang="ts">
import { Minus, Plus } from '@lucide/vue'
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
  currency?: string
  source?: string
  total?: string | number | null
  estimated_min_price?: string | number | null
  estimated_max_price?: string | number | null
}

const app    = useAppUrl()
const config = useRuntimeConfig()

// Fetch live config from backend; falls back to static constants if unavailable.
const { data: pricingConfig } = await useAsyncData('pricing-config', fetchPricingConfig)

const levels       = computed<PricingLevel[]>(() => pricingConfig.value?.academic_levels ?? FALLBACK_LEVELS)
const deadlines    = computed<PricingDeadline[]>(() => pricingConfig.value?.deadlines ?? FALLBACK_DEADLINES)
const paperTypes   = computed<PricingPaperType[]>(() => pricingConfig.value?.paper_types ?? FALLBACK_PAPER_TYPES)

// Selections — store codes + hours directly so orderUrl passes exact backend values.
const levelCode    = ref(levels.value[1]?.code ?? levels.value[0]?.code ?? 'high_school')
const deadlineHrs  = ref(deadlines.value[0]?.max_hours ?? 336)
const paperCode    = ref(paperTypes.value[0]?.code ?? 'essay')
const pages        = ref(1)

const backendEstimate = ref<EstimateResponse | null>(null)
const isPricing       = ref(false)
const hasBackendPrice = ref(false)

let pricingTimer: ReturnType<typeof setTimeout> | null = null

// Local fallback price from config data.
const localPrice = computed(() => {
  const lvl = levels.value.find(l => l.code === levelCode.value) ?? levels.value[0]
  const dl  = deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0]
  if (!lvl || !dl) return 0
  const base = lvl.price_per_page ?? 13
  return Math.ceil(base * dl.multiplier * pages.value * 100) / 100
})

const backendTotal = computed(() => {
  const raw = backendEstimate.value?.total ?? backendEstimate.value?.estimated_min_price
  const n = Number(raw)
  return Number.isFinite(n) && n > 0 ? n : null
})

const displayPrice  = computed(() => backendTotal.value ?? localPrice.value)
const perPage       = computed(() => pages.value > 0 ? displayPrice.value / pages.value : 0)
const pricingLabel  = computed(() => hasBackendPrice.value ? 'Live price' : 'Estimate')

// Pass exact backend codes and hours — no fuzzy name matching needed in the portal.
const orderUrl = computed(() => {
  const p = new URLSearchParams({
    level:    levelCode.value,
    type:     paperCode.value,
    deadline: String(deadlineHrs.value),
    pages:    String(pages.value),
  })
  return `${app.order}?${p.toString()}`
})

function incPages() { if (pages.value < 100) pages.value++ }
function decPages() { if (pages.value > 1)   pages.value-- }

async function refreshEstimate() {
  if (import.meta.server) return
  const apiBase = config.public.apiBase || ''
  if (!apiBase) { backendEstimate.value = null; hasBackendPrice.value = false; return }

  isPricing.value = true
  try {
    backendEstimate.value = await $fetch<EstimateResponse>(
      `${apiBase}/api/v1/pricing/public/estimate/`,
      {
        method: 'POST',
        body: {
          paper_type_code:       paperCode.value,
          academic_level_code:   levelCode.value,
          pages:                 pages.value,
          deadline_hours:        deadlineHrs.value,
          spacing:               'double',
        },
        credentials: 'include',
      },
    )
    hasBackendPrice.value = true
  } catch {
    backendEstimate.value = null
    hasBackendPrice.value = false
  } finally {
    isPricing.value = false
  }
}

function scheduleEstimate() {
  if (pricingTimer) clearTimeout(pricingTimer)
  pricingTimer = setTimeout(() => { void refreshEstimate() }, 250)
}

onMounted(() => { void refreshEstimate() })
watch([levelCode, deadlineHrs, paperCode, pages], scheduleEstimate)
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
    <div class="border-b border-slate-100 px-4 py-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600">Instant quote</p>
          <p class="mt-0.5 text-xs text-graphite">{{ pricingLabel }} for {{ pages * 275 }} words</p>
        </div>
        <div class="text-right">
          <p class="text-[11px] text-graphite">{{ isPricing ? 'Updating…' : 'Total' }}</p>
          <p class="text-2xl font-extrabold tabular-nums text-ink">${{ displayPrice.toFixed(2) }}</p>
        </div>
      </div>
    </div>

    <div class="space-y-3 px-4 py-4">
      <label class="block">
        <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">Work</span>
        <select v-model="paperCode" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500">
          <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
        </select>
      </label>

      <div class="grid grid-cols-2 gap-2">
        <label class="block">
          <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">Level</span>
          <select v-model="levelCode" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500">
            <option v-for="lvl in levels" :key="lvl.code" :value="lvl.code">{{ lvl.label }}</option>
          </select>
        </label>

        <label class="block">
          <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">Deadline</span>
          <select v-model="deadlineHrs" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500">
            <option v-for="dl in deadlines" :key="dl.max_hours" :value="dl.max_hours">{{ dl.label }}</option>
          </select>
        </label>
      </div>

      <div class="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Pages</span>
        <div class="ml-auto flex items-center gap-2">
          <button class="flex size-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40" :disabled="pages <= 1" type="button" @click="decPages">
            <Minus class="size-4" />
          </button>
          <span class="w-8 text-center text-lg font-bold tabular-nums text-ink">{{ pages }}</span>
          <button class="flex size-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40" :disabled="pages >= 100" type="button" @click="incPages">
            <Plus class="size-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="border-t border-slate-100 bg-slate-50 px-4 py-3">
      <div class="mb-3 flex items-center justify-between text-xs text-graphite">
        <span>${{ perPage.toFixed(2) }} / page</span>
      </div>
      <a :href="orderUrl" class="flex h-11 w-full items-center justify-center rounded-lg bg-gc-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-gc-700">
        Place order
      </a>
    </div>
  </div>
</template>
