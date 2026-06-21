<script setup lang="ts">
import { Loader2, CheckCircle2 } from '@lucide/vue'
import {
  fetchPricingConfig,
  FALLBACK_LEVELS,
  FALLBACK_DEADLINES,
  FALLBACK_PAPER_TYPES,
  type PricingLevel,
  type PricingDeadline,
  type PricingPaperType,
} from '~/composables/usePricingConfig'

const props = withDefaults(defineProps<{
  preselectedPaper?: string | null
}>(), { preselectedPaper: null })

const runtimeConfig = useRuntimeConfig()

const { data: pricingConfig } = useLazyAsyncData('gc-pricing-config', fetchPricingConfig)

const levels     = computed<PricingLevel[]>(() => pricingConfig.value?.academic_levels ?? FALLBACK_LEVELS)
const deadlines  = computed<PricingDeadline[]>(() => pricingConfig.value?.deadlines ?? FALLBACK_DEADLINES)
const paperTypes = computed<PricingPaperType[]>(() => pricingConfig.value?.paper_types ?? FALLBACK_PAPER_TYPES)

// ── Form state ───────────────────────────────────────────────────────────────
const serviceType = ref<'writing' | 'editing' | 'rewriting'>('writing')
const paperCode   = ref<string | null>(props.preselectedPaper ?? null)
const levelCode   = ref<string>(FALLBACK_LEVELS[1]?.code ?? 'undergrad')
const deadlineHrs = ref<number>(FALLBACK_DEADLINES[0]?.max_hours ?? 336)
const pages       = ref(1)
const spacing     = ref<'double' | 'single'>('double')

watch(levels,    lvls => { if (lvls.length > 1) levelCode.value = lvls[1].code })
watch(deadlines, dls  => { if (dls.length) deadlineHrs.value = dls[0].max_hours })

const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])
const words            = computed(() => pages.value * (spacing.value === 'double' ? 275 : 550))

// ── Pricing ──────────────────────────────────────────────────────────────────
type EstimateResponse = { total?: string | number | null; estimated_min_price?: string | number | null }
const estimate     = ref<EstimateResponse | null>(null)
const isPricing    = ref(false)
const hasLivePrice = ref(false)
let   priceTimer: ReturnType<typeof setTimeout> | null = null

const spacingMult = computed(() =>
  spacing.value === 'single'
    ? (pricingConfig.value?.spacing_multipliers?.single ?? 2)
    : (pricingConfig.value?.spacing_multipliers?.double ?? 1)
)

const localPrice = computed(() => {
  const base = selectedLevel.value?.price_per_page ?? 13
  const mult = selectedDeadline.value?.multiplier ?? 1
  return Math.ceil(base * mult * spacingMult.value * pages.value * 100) / 100
})

const livePrice    = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})

const displayPrice = computed(() => livePrice.value ?? localPrice.value)
const pricePerPage = computed(() => (displayPrice.value / Math.max(pages.value, 1)).toFixed(2))

async function refreshEstimate() {
  if (import.meta.server) return
  const apiBase = runtimeConfig.public.apiBase || ''
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
          spacing:             spacing.value,
        },
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
  priceTimer = setTimeout(() => void refreshEstimate(), 300)
}

watch([serviceType, paperCode, levelCode, deadlineHrs, pages, spacing], scheduleEstimate)

// ── Order URL ────────────────────────────────────────────────────────────────
const orderUrl = computed(() => {
  const p = new URLSearchParams({ type: serviceType.value })
  if (levelCode.value)             p.set('level', levelCode.value)
  if (deadlineHrs.value)           p.set('deadline', String(deadlineHrs.value))
  if (pages.value > 1)             p.set('pages', String(pages.value))
  if (paperCode.value)             p.set('paper', paperCode.value)
  if (spacing.value === 'single')  p.set('spacing', 'single')
  return `/order?${p.toString()}`
})

// ── Step 1 data ──────────────────────────────────────────────────────────────
const SERVICE_TYPES = [
  { id: 'writing',   label: 'Writing'   },
  { id: 'editing',   label: 'Editing'   },
  { id: 'rewriting', label: 'Rewriting' },
] as const

// ── Step 3 data ──────────────────────────────────────────────────────────────
const FREE_INCLUSIONS = ['Cover page', 'Reference list', 'Plagiarism report', 'AI-detection cert']
</script>

<template>
  <div class="overflow-hidden rounded-2xl bg-forest-950 shadow-[0_16px_48px_rgba(0,0,0,0.5)] ring-1 ring-white/10 select-none">

    <!-- Header -->
    <div class="border-b border-white/10 px-5 py-3.5">
      <p class="text-[10px] font-bold uppercase tracking-widest text-gold-400">Instant price calculator</p>
    </div>

    <div class="space-y-4 p-5">

      <!-- Service type -->
      <div class="flex gap-1 rounded-xl border border-white/10 bg-forest-900/50 p-1">
        <button
          v-for="s in SERVICE_TYPES"
          :key="s.id"
          type="button"
          class="flex-1 rounded-lg py-2 text-xs font-bold uppercase tracking-widest transition-all"
          :class="serviceType === s.id ? 'bg-gc-600 text-white shadow-sm' : 'text-white/40 hover:text-white/70'"
          @click="serviceType = s.id"
        >{{ s.label }}</button>
      </div>

      <!-- Paper type + Level -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="lbl">Paper type</label>
          <select v-model="paperCode" class="sel">
            <option :value="null">— Any type —</option>
            <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
          </select>
        </div>
        <div>
          <label class="lbl">Academic level</label>
          <select v-model="levelCode" class="sel">
            <option v-for="lvl in levels" :key="lvl.code" :value="lvl.code">
              {{ lvl.label }}{{ lvl.price_per_page ? ` · $${lvl.price_per_page}/pg` : '' }}
            </option>
          </select>
        </div>
      </div>

      <!-- Deadline -->
      <div>
        <label class="lbl">Deadline</label>
        <select v-model.number="deadlineHrs" class="sel">
          <option v-for="dl in deadlines" :key="dl.max_hours" :value="dl.max_hours">
            {{ dl.label }}{{ dl.multiplier === 1 ? ' — best price' : ` (+${Math.round((dl.multiplier - 1) * 100)}%)` }}
          </option>
        </select>
      </div>

      <!-- Pages + Spacing -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="lbl">Pages</label>
          <div class="flex h-10 items-center justify-between rounded-lg border border-white/10 bg-forest-900/60 px-3">
            <button type="button" class="flex size-6 items-center justify-center rounded text-lg font-bold text-white/40 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-20" :disabled="pages <= 1" @click="pages--">−</button>
            <div class="text-center">
              <span class="text-sm font-extrabold tabular-nums text-white">{{ pages }}</span>
              <span class="ml-1 text-xs text-white/30">pg</span>
            </div>
            <button type="button" class="flex size-6 items-center justify-center rounded text-lg font-bold text-white/40 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-20" :disabled="pages >= 100" @click="pages++">+</button>
          </div>
          <p class="mt-0.5 text-center text-[9px] text-white/25">{{ words.toLocaleString() }} words</p>
        </div>
        <div>
          <label class="lbl">Spacing</label>
          <select v-model="spacing" class="sel">
            <option value="double">Double · 275 w/pg</option>
            <option value="single">Single · 550 w/pg</option>
          </select>
        </div>
      </div>

      <!-- Free inclusions (writing only) -->
      <Transition name="slide">
        <div v-if="serviceType === 'writing'" class="rounded-xl border border-gold-700/30 bg-gold-500/8 px-4 py-3">
          <p class="mb-2 text-[10px] font-bold uppercase tracking-widest text-gold-400/80">Included free</p>
          <div class="grid grid-cols-2 gap-x-3 gap-y-1">
            <p v-for="item in FREE_INCLUSIONS" :key="item" class="flex items-center gap-1.5 text-[10px] font-medium text-gold-200/60">
              <CheckCircle2 class="size-2.5 shrink-0 text-gold-500/70" />
              {{ item }}
            </p>
          </div>
        </div>
      </Transition>

      <!-- Price + CTA -->
      <div class="rounded-xl border border-white/10 bg-forest-900/70 px-4 py-4">
        <div class="mb-3 flex items-end justify-between">
          <div>
            <p class="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-white/35">
              {{ hasLivePrice ? 'Live price' : 'Estimated' }}
              <Loader2 v-if="isPricing" class="size-3 animate-spin text-gold-400" />
            </p>
            <p class="text-3xl font-extrabold tabular-nums leading-none text-gold-300">${{ displayPrice.toFixed(2) }}</p>
            <p class="mt-1 text-[10px] text-white/35">
              ${{ pricePerPage }}/page · {{ selectedLevel?.label }} · {{ selectedDeadline?.label }}
            </p>
          </div>
          <div class="text-right text-[10px] leading-relaxed text-white/30">
            <p>✓ Free revisions</p>
            <p>✓ Grade guarantee</p>
            <p>✓ No payment now</p>
          </div>
        </div>
        <a :href="orderUrl" class="flex h-11 w-full items-center justify-center rounded-xl bg-gc-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-gc-700">
          Place my order — ${{ displayPrice.toFixed(2) }} →
        </a>
        <p class="mt-2 text-center text-[10px] text-white/25">Price confirmed at checkout · No card needed now</p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.lbl { @apply mb-1.5 block text-[10px] font-bold uppercase tracking-widest text-white/35; }
.sel {
  @apply h-10 w-full rounded-lg border border-white/10 bg-forest-900/60 px-3 text-sm text-white/80 focus:border-gold-500/50 focus:outline-none focus:ring-1 focus:ring-gold-500/30;
}
.sel option { background: #052e16; color: white; }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
