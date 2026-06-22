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
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-parchment-50 px-5 py-4">
      <p class="text-xs font-bold uppercase tracking-widest text-amber-700">Instant price estimate</p>
      <p class="mt-0.5 text-[11px] text-slate-400">Adjust options — price updates live</p>
    </div>

    <div class="space-y-4 p-5">

      <!-- ── Service type ──────────────────────────────────────────────────── -->
      <div>
        <label class="field-label">Service type</label>
        <select v-model="serviceType" class="sel">
          <option v-for="s in SERVICE_TYPES" :key="s.id" :value="s.id">{{ s.label }}</option>
        </select>
      </div>

      <!-- ── Paper type ────────────────────────────────────────────────────── -->
      <div>
        <label class="field-label">Paper type</label>
        <select v-model="paperCode" class="sel">
          <option :value="null">— Select paper type —</option>
          <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
        </select>
      </div>

      <!-- ── Academic level ────────────────────────────────────────────────── -->
      <div>
        <label class="field-label">Academic level</label>
        <select v-model="levelCode" class="sel">
          <option v-for="lvl in levels" :key="lvl.code" :value="lvl.code">
            {{ lvl.label }}{{ lvl.price_per_page ? ` — from $${lvl.price_per_page}/pg` : '' }}
          </option>
        </select>
      </div>

      <!-- ── Subject area ──────────────────────────────────────────────────── -->
      <div>
        <label class="field-label">Subject area <span class="text-slate-300 font-normal normal-case tracking-normal">(optional)</span></label>
        <select v-model="subjectName" class="sel">
          <option value="">— Any subject —</option>
          <optgroup v-for="(names, category) in subjectGroups" :key="category" :label="String(category)">
            <option v-for="name in names" :key="name" :value="name">{{ name }}</option>
          </optgroup>
        </select>
      </div>

      <!-- ── Deadline ──────────────────────────────────────────────────────── -->
      <div>
        <label class="field-label">Deadline</label>
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

      <!-- ── Pages + Spacing ──────────────────────────────────────────────── -->
      <div class="grid grid-cols-2 gap-3">
        <!-- Pages stepper -->
        <div>
          <label class="field-label">Pages</label>
          <div class="flex h-10 items-center justify-between gap-1 rounded-lg border border-slate-200 bg-white px-2.5">
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-base font-bold text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-30"
              :disabled="pages <= 1"
              @click="pages--"
            >−</button>
            <span class="flex-1 text-center text-sm font-bold tabular-nums text-slate-900">{{ pages }}</span>
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-base font-bold text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-30"
              :disabled="pages >= 100"
              @click="pages++"
            >+</button>
          </div>
          <p class="mt-1 text-center text-[11px] text-slate-400">≈ {{ words.toLocaleString() }} words</p>
        </div>

        <!-- Spacing dropdown -->
        <div>
          <label class="field-label">Spacing</label>
          <select v-model="spacing" class="sel">
            <option value="double">Double (275 w/pg)</option>
            <option value="single">Single (550 w/pg)</option>
          </select>
        </div>
      </div>

      <!-- ── Add-ons ───────────────────────────────────────────────────────── -->
      <div v-if="addons.length" class="space-y-2">
        <p class="field-label">Optional add-ons</p>
        <div class="space-y-1.5">
          <label
            v-for="addon in addons.slice(0, 4)"
            :key="addon.addon_code"
            class="flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors"
            :class="selectedAddonCodes.includes(addon.addon_code)
              ? 'border-amber-300 bg-amber-50'
              : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'"
          >
            <input
              type="checkbox"
              class="mt-0.5 h-4 w-4 shrink-0 rounded border-slate-300 accent-amber-600"
              :checked="selectedAddonCodes.includes(addon.addon_code)"
              @change="toggleAddon(addon.addon_code)"
            />
            <div class="min-w-0 flex-1">
              <p class="text-xs font-semibold leading-tight text-slate-800">{{ addon.name }}</p>
              <p class="mt-0.5 text-[11px] font-semibold text-amber-700">+${{ addon.flat_amount }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- ── Free inclusions (writing only) ───────────────────────────────── -->
      <Transition name="slide">
        <div v-if="serviceType === 'writing'" class="rounded-lg border border-emerald-100 bg-emerald-50 p-4">
          <p class="mb-2.5 text-[11px] font-bold uppercase tracking-widest text-emerald-700">Included free</p>
          <ul class="grid grid-cols-2 gap-x-3 gap-y-1.5">
            <li
              v-for="item in ['Cover page', 'Title page', 'Reference list', 'Appendix', 'Citation formatting', 'Plagiarism-free report']"
              :key="item"
              class="flex items-center gap-1.5 text-[11px] font-medium text-emerald-800"
            >
              <svg class="size-3 shrink-0 text-emerald-500" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="2 6 5 9 10 3"/>
              </svg>
              {{ item }}
            </li>
          </ul>
        </div>
      </Transition>

      <!-- ── Price + CTA ───────────────────────────────────────────────────── -->
      <div class="rounded-xl border border-amber-100 bg-parchment-50 p-4">

        <!-- Price row -->
        <div class="flex items-end justify-between gap-2">
          <div>
            <p class="flex items-center gap-1.5 text-[11px] font-semibold text-amber-700">
              {{ hasLivePrice ? 'Live price' : 'Est. price' }}
              <Loader2 v-if="isPricing" class="size-3 animate-spin" />
            </p>
            <p class="mt-0.5 text-3xl font-extrabold tabular-nums leading-none text-claret-700">
              ${{ displayPrice.toFixed(2) }}
            </p>
          </div>
          <div class="text-right text-[11px] leading-relaxed text-amber-700">
            <p>${{ (displayPrice / Math.max(pages, 1)).toFixed(2) }}/page</p>
            <p>{{ selectedDeadline?.label }}</p>
          </div>
        </div>

        <!-- Trust bullets -->
        <div class="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-amber-100 pt-3 text-[11px] text-slate-500">
          <span>✓ Pay after approval</span>
          <span>✓ Free revisions</span>
          <span>✓ Human-written</span>
        </div>

        <!-- CTA -->
        <a
          :href="orderUrl"
          class="mt-3 flex h-11 w-full items-center justify-center rounded-xl bg-amber-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-amber-500"
        >
          Start my order — {{ selectedLevel?.label }}
        </a>

        <p class="mt-2 text-center text-[11px] text-slate-400">
          Price confirmed at checkout · no card needed
        </p>
      </div>

      <!-- Custom quote -->
      <p class="text-center text-xs text-slate-400">
        Complex scope?
        <NuxtLink to="/quote" class="font-semibold text-amber-700 transition-colors hover:text-amber-600">Get a custom quote →</NuxtLink>
      </p>

    </div>
  </div>
</template>

<style scoped>
.field-label {
  @apply mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500;
}
.sel {
  @apply h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-800 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-100 transition-colors;
}
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
