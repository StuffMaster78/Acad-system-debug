<script setup lang="ts">
import { Loader2 } from '@lucide/vue'
import {
  fetchPricingConfig,
  FALLBACK_LEVELS,
  FALLBACK_DEADLINES,
  FALLBACK_PAPER_TYPES,
  FALLBACK_SUBJECTS,
  type PricingLevel,
  type PricingDeadline,
  type PricingPaperType,
  type CfgSubject,
  type CfgAddon,
} from '~/composables/usePricingConfig'

const SERVICE_TYPES = [
  { id: 'writing',      label: 'Writing' },
  { id: 'editing',      label: 'Editing' },
  { id: 'proofreading', label: 'Proofreading' },
  { id: 'rewriting',    label: 'Rewriting' },
]

type EstimateResponse = {
  total?: string | number | null
  estimated_min_price?: string | number | null
}

const app    = useAppUrl()
const config = useRuntimeConfig()

// ── Live config ────────────────────────────────────────────────────────────
const { data: pricingConfig } = useLazyAsyncData('calc-pricing-config', fetchPricingConfig)

const levels     = computed<PricingLevel[]>(() => pricingConfig.value?.academic_levels ?? FALLBACK_LEVELS)
const deadlines  = computed<PricingDeadline[]>(() => pricingConfig.value?.deadlines ?? FALLBACK_DEADLINES)
const paperTypes = computed<PricingPaperType[]>(() => pricingConfig.value?.paper_types ?? FALLBACK_PAPER_TYPES)
const subjects   = computed<CfgSubject[]>(() => {
  const s = pricingConfig.value?.subjects
  return s?.length ? s : FALLBACK_SUBJECTS
})
const addons = computed<CfgAddon[]>(() => pricingConfig.value?.addons ?? [])

const subjectGroups = computed(() => {
  const groups: Record<string, string[]> = {}
  for (const s of subjects.value) {
    if (!groups[s.category]) groups[s.category] = []
    groups[s.category].push(s.name)
  }
  return groups
})

const standardDeadlines = computed(() => deadlines.value.filter(d => d.max_hours > 48))
const expressDeadlines  = computed(() => deadlines.value.filter(d => d.max_hours <= 48))

// ── Form state ─────────────────────────────────────────────────────────────
const serviceType        = ref('writing')
const paperCode          = ref<string | null>(null)
const levelCode          = ref(FALLBACK_LEVELS[1]?.code ?? FALLBACK_LEVELS[0]?.code ?? 'undergrad')
const deadlineHrs        = ref(FALLBACK_DEADLINES[0]?.max_hours ?? 336)
const pages              = ref(1)
const spacing            = ref<'double' | 'single'>('double')
const subjectName        = ref('')
const selectedAddonCodes = ref<string[]>([])

watch(levels,    (lvls) => { if (lvls.length > 1) levelCode.value = lvls[1].code }, { immediate: false })
watch(deadlines, (dls)  => { if (dls.length) deadlineHrs.value = dls[0].max_hours }, { immediate: false })

const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])
const words            = computed(() => pages.value * (spacing.value === 'double' ? 275 : 550))

// ── Live price ─────────────────────────────────────────────────────────────
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
  const base = selectedLevel.value?.price_per_page ?? 15
  const mult = selectedDeadline.value?.multiplier ?? 1
  return Math.ceil(base * mult * spacingMult.value * pages.value * 100) / 100
})

const livePrice = computed(() => {
  const n = Number(estimate.value?.total ?? estimate.value?.estimated_min_price)
  return Number.isFinite(n) && n > 0 ? n : null
})

const addonTotal = computed(() =>
  addons.value
    .filter(a => selectedAddonCodes.value.includes(a.addon_code))
    .reduce((sum, a) => sum + a.flat_amount, 0)
)

const displayPrice = computed(() => (livePrice.value ?? localPrice.value) + addonTotal.value)

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
          spacing:             spacing.value,
        },
        credentials: 'include',
      },
    )
    hasLivePrice.value = true
  } catch {
    estimate.value     = null
    hasLivePrice.value = false
  } finally {
    isPricing.value = false
  }
}

function scheduleEstimate() {
  if (priceTimer) clearTimeout(priceTimer)
  priceTimer = setTimeout(() => { void refreshEstimate() }, 350)
}

function toggleAddon(code: string) {
  const idx = selectedAddonCodes.value.indexOf(code)
  if (idx >= 0) selectedAddonCodes.value.splice(idx, 1)
  else selectedAddonCodes.value.push(code)
}

onMounted(() => { void refreshEstimate() })
watch([serviceType, paperCode, levelCode, deadlineHrs, pages, spacing], scheduleEstimate)

// ── Order URL ──────────────────────────────────────────────────────────────
const orderUrl = computed(() => {
  const p = new URLSearchParams({ type: serviceType.value })
  if (levelCode.value) p.set('level', levelCode.value)
  if (deadlineHrs.value) p.set('deadline', String(deadlineHrs.value))
  if (pages.value > 1) p.set('pages', String(pages.value))
  if (paperCode.value) p.set('paper', paperCode.value)
  if (spacing.value === 'single') p.set('spacing', 'single')
  if (subjectName.value) p.set('subject', subjectName.value)
  if (selectedAddonCodes.value.length) p.set('addons', selectedAddonCodes.value.join(','))
  return `${app.order}?${p.toString()}`
})
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-5 py-3.5">
      <p class="text-xs font-bold uppercase tracking-widest text-slate-400">Get your instant price</p>
    </div>

    <div class="space-y-4 p-5">

      <!-- Row 1: Service + Paper type -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Service</label>
          <select v-model="serviceType" class="sel">
            <option v-for="s in SERVICE_TYPES" :key="s.id" :value="s.id">{{ s.label }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Paper type</label>
          <select v-model="paperCode" class="sel">
            <option :value="null">Any type</option>
            <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
          </select>
        </div>
      </div>

      <!-- Subject area -->
      <div>
        <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Subject area</label>
        <select v-model="subjectName" class="sel">
          <option value="">— Any subject —</option>
          <optgroup v-for="(names, category) in subjectGroups" :key="category" :label="String(category)">
            <option v-for="name in names" :key="name" :value="name">{{ name }}</option>
          </optgroup>
        </select>
      </div>

      <!-- Academic level -->
      <div>
        <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Academic level</label>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="lvl in levels"
            :key="lvl.code"
            type="button"
            class="rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition-colors"
            :class="levelCode === lvl.code
              ? 'border-amber-600 bg-amber-600 text-white'
              : 'border-slate-200 text-slate-600 hover:border-claret-300 hover:text-claret-700'"
            @click="levelCode = lvl.code"
          >
            {{ lvl.label }}
          </button>
        </div>
      </div>

      <!-- Deadline + Pages + Spacing -->
      <div class="grid grid-cols-[1fr_auto_auto] items-end gap-3">
        <div>
          <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Deadline</label>
          <select v-model.number="deadlineHrs" class="sel">
            <optgroup v-if="standardDeadlines.length" label="Standard">
              <option v-for="dl in standardDeadlines" :key="dl.max_hours" :value="dl.max_hours">
                {{ dl.label }}{{ dl.multiplier === 1 ? ' — best price' : ` (+${Math.round((dl.multiplier - 1) * 100)}%)` }}
              </option>
            </optgroup>
            <optgroup v-if="expressDeadlines.length" label="Express (rush rates)">
              <option v-for="dl in expressDeadlines" :key="dl.max_hours" :value="dl.max_hours">
                {{ dl.label }} (+{{ Math.round((dl.multiplier - 1) * 100) }}%)
              </option>
            </optgroup>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Pages</label>
          <div class="flex h-10 items-center gap-1.5 rounded-lg border border-slate-200 px-2">
            <button
              type="button"
              class="flex h-6 w-6 items-center justify-center rounded text-slate-500 hover:bg-slate-100 disabled:opacity-30"
              :disabled="pages <= 1"
              @click="pages--"
            >−</button>
            <span class="w-6 text-center text-sm font-bold tabular-nums text-slate-900">{{ pages }}</span>
            <button
              type="button"
              class="flex h-6 w-6 items-center justify-center rounded text-slate-500 hover:bg-slate-100 disabled:opacity-30"
              :disabled="pages >= 100"
              @click="pages++"
            >+</button>
          </div>
          <p class="mt-0.5 text-center text-[10px] text-slate-400">{{ words.toLocaleString() }} words</p>
        </div>

        <div>
          <label class="mb-1.5 block text-[11px] font-bold uppercase tracking-widest text-slate-400">Spacing</label>
          <div class="flex h-10 overflow-hidden rounded-lg border border-slate-200">
            <button
              type="button"
              class="flex-1 px-2.5 text-xs font-semibold transition-colors"
              :class="spacing === 'double' ? 'bg-amber-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'"
              @click="spacing = 'double'"
            >Dbl</button>
            <button
              type="button"
              class="flex-1 border-l border-slate-200 px-2.5 text-xs font-semibold transition-colors"
              :class="spacing === 'single' ? 'border-amber-600 bg-amber-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'"
              @click="spacing = 'single'"
            >Sgl</button>
          </div>
        </div>
      </div>

      <!-- Add-ons (only shown when backend returns them) -->
      <div v-if="addons.length" class="rounded-lg border border-slate-100 bg-slate-50 p-3">
        <p class="mb-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">Optional add-ons</p>
        <div class="grid grid-cols-2 gap-2">
          <label
            v-for="addon in addons.slice(0, 4)"
            :key="addon.addon_code"
            class="flex cursor-pointer items-start gap-2 rounded-lg border bg-white p-2 transition-colors"
            :class="selectedAddonCodes.includes(addon.addon_code) ? 'border-amber-400 bg-amber-50' : 'border-slate-200 hover:border-slate-300'"
          >
            <input
              type="checkbox"
              class="mt-0.5 h-3.5 w-3.5 shrink-0 rounded border-slate-300 text-amber-600"
              :checked="selectedAddonCodes.includes(addon.addon_code)"
              @change="toggleAddon(addon.addon_code)"
            />
            <div class="min-w-0">
              <p class="text-xs font-medium leading-tight text-slate-900">{{ addon.name }}</p>
              <p class="text-[11px] font-semibold text-amber-700">+${{ addon.flat_amount }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Free inclusions — writing only -->
      <Transition name="slide">
        <div v-if="serviceType === 'writing'" class="rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3">
          <div class="mb-2.5 flex items-center gap-2">
            <svg class="h-5 w-5 shrink-0 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <line x1="10" y1="9" x2="8" y2="9"/>
            </svg>
            <p class="text-[11px] font-bold uppercase tracking-widest text-emerald-700">Free with every writing order</p>
          </div>
          <div class="grid grid-cols-2 gap-x-4 gap-y-1.5">
            <p
              v-for="item in ['Cover page', 'Title page', 'Reference list', 'Appendix', 'Citation formatting', 'Plagiarism-free report']"
              :key="item"
              class="flex items-center gap-1.5 text-[11px] font-medium text-emerald-800"
            >
              <svg class="h-3 w-3 shrink-0 text-emerald-500" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="2 6 5 9 10 3"/></svg>
              {{ item }}
            </p>
          </div>
        </div>
      </Transition>

      <!-- Price + CTA -->
      <div class="rounded-xl bg-parchment-100 px-4 py-3.5">
        <div class="mb-3 flex items-end justify-between">
          <div>
            <p class="flex items-center gap-1.5 text-[11px] font-semibold text-amber-700">
              {{ hasLivePrice ? 'Live price' : 'Estimated price' }}
              <Loader2 v-if="isPricing" class="size-3 animate-spin" />
            </p>
            <p class="text-3xl font-extrabold tabular-nums leading-none text-claret-700">
              ${{ displayPrice.toFixed(2) }}
            </p>
            <p class="mt-0.5 text-xs text-amber-600">
              ${{ (displayPrice / Math.max(pages, 1)).toFixed(2) }}/page · {{ selectedLevel?.label }} · {{ selectedDeadline?.label }}
            </p>
          </div>
          <div class="text-right text-[11px] leading-relaxed text-amber-700">
            <p>✓ No payment until you approve</p>
            <p>✓ Free revisions included</p>
          </div>
        </div>
        <a
          :href="orderUrl"
          class="flex h-11 w-full items-center justify-center rounded-xl bg-amber-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-500"
        >
          Start my order →
        </a>
        <p class="mt-2 text-center text-[11px] text-slate-400">
          Price confirmed at checkout — no card needed to place
        </p>
      </div>

      <!-- Express / quote CTA -->
      <p class="text-center text-[11px] text-slate-400">
        Complex scope or express delivery?
        <NuxtLink to="/quote" class="font-semibold text-amber-700 hover:underline">Get a custom quote →</NuxtLink>
      </p>

    </div>
  </div>
</template>

<style scoped>
.sel {
  @apply h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-800 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100;
}
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
