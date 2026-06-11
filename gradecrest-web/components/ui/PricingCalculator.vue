<script setup lang="ts">
import { Minus, Plus } from '@lucide/vue'
import {
  ACADEMIC_LEVELS,
  DEADLINES,
  PAPER_TYPES,
  usePricing,
} from '~/composables/usePricing'

type EstimateResponse = {
  currency?: string
  source?: string
  total?: string | number | null
  estimated_min_price?: string | number | null
  estimated_max_price?: string | number | null
}

const app = useAppUrl()
const config = useRuntimeConfig()
const { calculate } = usePricing()

const levelKey = ref(ACADEMIC_LEVELS[1].key)
const deadlineKey = ref(DEADLINES[0].key)
const paperKey = ref(PAPER_TYPES[0].key)
const pages = ref(1)
const backendEstimate = ref<EstimateResponse | null>(null)
const isPricing = ref(false)
const hasBackendPricing = ref(false)

let pricingTimer: ReturnType<typeof setTimeout> | null = null

const deadlineHoursByKey: Record<string, number> = {
  '14d': 336,
  '7d': 168,
  '5d': 120,
  '3d': 72,
  '24h': 24,
  '12h': 12,
  '6h': 6,
}

const localPrice = computed(() =>
  calculate({
    levelKey: levelKey.value,
    deadlineKey: deadlineKey.value,
    pages: pages.value,
  }),
)

const localPerPage = computed(() =>
  calculate({
    levelKey: levelKey.value,
    deadlineKey: deadlineKey.value,
    pages: 1,
  }),
)

const backendTotal = computed(() => {
  const raw = backendEstimate.value?.total
    ?? backendEstimate.value?.estimated_min_price
  const parsed = Number(raw)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
})

const displayPrice = computed(() => backendTotal.value ?? localPrice.value)
const perPage = computed(() => displayPrice.value / pages.value)
const pricingLabel = computed(() =>
  hasBackendPricing.value ? 'Live price' : 'Estimate',
)

const orderUrl = computed(() => {
  const p = new URLSearchParams({
    level: levelKey.value,
    deadline: deadlineKey.value,
    type: paperKey.value,
    pages: String(pages.value),
  })
  return `${app.order}?${p.toString()}`
})

function incPages() {
  if (pages.value < 100) pages.value++
}

function decPages() {
  if (pages.value > 1) pages.value--
}

async function refreshBackendEstimate() {
  if (import.meta.server) return

  const apiBase = config.public.apiBase || ''
  if (!apiBase) {
    backendEstimate.value = null
    hasBackendPricing.value = false
    return
  }

  isPricing.value = true
  try {
    const estimate = await $fetch<EstimateResponse>(
      `${apiBase}/api/v1/pricing/public/estimate/`,
      {
        method: 'POST',
        body: {
          service_code: paperKey.value,
          paper_type_code: paperKey.value,
          academic_level_code: levelKey.value,
          pages: pages.value,
          deadline_hours: deadlineHoursByKey[deadlineKey.value] ?? 336,
          spacing: 'double',
        },
        credentials: 'include',
      },
    )
    backendEstimate.value = estimate
    hasBackendPricing.value = true
  } catch {
    backendEstimate.value = null
    hasBackendPricing.value = false
  } finally {
    isPricing.value = false
  }
}

function scheduleEstimate() {
  if (pricingTimer) clearTimeout(pricingTimer)
  pricingTimer = setTimeout(() => {
    void refreshBackendEstimate()
  }, 250)
}

onMounted(() => {
  void refreshBackendEstimate()
})

watch([levelKey, deadlineKey, paperKey, pages], scheduleEstimate)
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
    <div class="border-b border-slate-100 px-4 py-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-gc-600">
            Instant quote
          </p>
          <p class="mt-0.5 text-xs text-graphite">
            {{ pricingLabel }} for {{ pages * 275 }} words
          </p>
        </div>
        <div class="text-right">
          <p class="text-[11px] text-graphite">{{ isPricing ? 'Updating' : 'Total' }}</p>
          <p class="text-2xl font-extrabold tabular-nums text-ink">
            ${{ displayPrice.toFixed(2) }}
          </p>
        </div>
      </div>
    </div>

    <div class="space-y-3 px-4 py-4">
      <label class="block">
        <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">
          Work
        </span>
        <select
          v-model="paperKey"
          class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500"
        >
          <option v-for="pt in PAPER_TYPES" :key="pt.key" :value="pt.key">
            {{ pt.label }}
          </option>
        </select>
      </label>

      <div class="grid grid-cols-2 gap-2">
        <label class="block">
          <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">
            Level
          </span>
          <select
            v-model="levelKey"
            class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500"
          >
            <option v-for="lvl in ACADEMIC_LEVELS" :key="lvl.key" :value="lvl.key">
              {{ lvl.label }}
            </option>
          </select>
        </label>

        <label class="block">
          <span class="mb-1 block text-[11px] font-semibold uppercase tracking-widest text-graphite">
            Deadline
          </span>
          <select
            v-model="deadlineKey"
            class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500"
          >
            <option v-for="dl in DEADLINES" :key="dl.key" :value="dl.key">
              {{ dl.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="flex items-center gap-3 rounded-lg bg-slate-50 px-3 py-2">
        <span class="text-xs font-semibold uppercase tracking-widest text-graphite">
          Pages
        </span>
        <div class="ml-auto flex items-center gap-2">
          <button
            class="flex size-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40"
            :disabled="pages <= 1"
            type="button"
            @click="decPages"
          >
            <Minus class="size-4" />
          </button>
          <span class="w-8 text-center text-lg font-bold tabular-nums text-ink">
            {{ pages }}
          </span>
          <button
            class="flex size-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40"
            :disabled="pages >= 100"
            type="button"
            @click="incPages"
          >
            <Plus class="size-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="border-t border-slate-100 bg-slate-50 px-4 py-3">
      <div class="mb-3 flex items-center justify-between text-xs text-graphite">
        <span>${{ perPage.toFixed(2) }} / page</span>
      </div>
      <a
        :href="orderUrl"
        class="flex h-11 w-full items-center justify-center rounded-lg bg-gc-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-gc-700"
      >
        Place order
      </a>
    </div>
  </div>
</template>
