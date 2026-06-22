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

const NURSING_TYPES = [
  { id: 'writing',      label: 'Write it for me' },
  { id: 'editing',      label: 'Edit my draft' },
  { id: 'proofreading', label: 'Proofread only' },
  { id: 'rewriting',    label: 'Rewrite from scratch' },
]

const NURSING_INCLUSIONS = [
  'NANDA-I diagnosis', 'APA 7th formatting', 'Care plan structure',
  'Reference list', 'Plagiarism-free report', 'Unlimited revisions',
]

type EstimateResponse = {
  total?: string | number | null
  estimated_min_price?: string | number | null
}

const app    = useAppUrl()
const config = useRuntimeConfig()

const { data: pricingConfig } = useLazyAsyncData('ng-pricing-config', fetchPricingConfig)

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
const spacing            = ref<'' | 'double' | 'single'>('')
const subjectName        = ref('')
const selectedAddonCodes = ref<string[]>([])

watch(levels,    (lvls) => { if (lvls.length > 1) levelCode.value = lvls[1].code }, { immediate: false })
watch(deadlines, (dls)  => { if (dls.length) deadlineHrs.value = dls[0].max_hours }, { immediate: false })

const selectedLevel    = computed(() => levels.value.find(l => l.code === levelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === deadlineHrs.value) ?? deadlines.value[0])
const effectiveSpacing = computed(() => spacing.value === 'single' ? 'single' : 'double')
const words            = computed(() => pages.value * (effectiveSpacing.value === 'single' ? 550 : 275))

const estimate     = ref<EstimateResponse | null>(null)
const isPricing    = ref(false)
const hasLivePrice = ref(false)
let   priceTimer: ReturnType<typeof setTimeout> | null = null

const spacingMult = computed(() =>
  effectiveSpacing.value === 'single'
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
          spacing:             effectiveSpacing.value,
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
  <div class="overflow-hidden rounded-2xl bg-brand-900 shadow-[0_8px_32px_rgba(13,148,136,0.25)] ring-1 ring-brand-700">

    <!-- ── Clinical header ───────────────────────────────────────────────── -->
    <div class="relative overflow-hidden px-5 py-5">
      <!-- Subtle dot-grid background -->
      <div class="pointer-events-none absolute inset-0 opacity-10"
        style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 20px 20px;" />
      <div class="relative">
        <!-- Live availability pulse -->
        <div class="mb-3 flex items-center gap-2">
          <span class="relative flex size-2.5">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span class="relative inline-flex size-2.5 rounded-full bg-emerald-400" />
          </span>
          <span class="text-[11px] font-semibold text-emerald-300 uppercase tracking-wider">Nurse writers available now</span>
        </div>
        <h3 class="text-lg font-bold text-white leading-snug">Get your nursing paper<br>written by a real nurse</h3>
        <div class="mt-2 flex flex-wrap gap-2">
          <span class="rounded-full bg-brand-800 px-2.5 py-0.5 text-[10px] font-semibold text-brand-200">🎓 BSN · MSN · DNP</span>
          <span class="rounded-full bg-brand-800 px-2.5 py-0.5 text-[10px] font-semibold text-brand-200">✓ Grade guaranteed</span>
          <span class="rounded-full bg-brand-800 px-2.5 py-0.5 text-[10px] font-semibold text-brand-200">⚡ As fast as 3 hrs</span>
        </div>
      </div>
    </div>

    <!-- ── Form fields ────────────────────────────────────────────────────── -->
    <div class="border-t border-brand-800 space-y-4 p-5">

      <!-- What do you need? -->
      <div>
        <label class="field-label">What do you need?</label>
        <select v-model="serviceType" class="sel">
          <option v-for="s in NURSING_TYPES" :key="s.id" :value="s.id">{{ s.label }}</option>
        </select>
      </div>

      <!-- Paper / assignment type -->
      <div>
        <label class="field-label">Assignment type</label>
        <select v-model="paperCode" class="sel">
          <option :value="null">— Select assignment type —</option>
          <option v-for="pt in paperTypes" :key="pt.code" :value="pt.code">{{ pt.label }}</option>
        </select>
      </div>

      <!-- Nursing level -->
      <div>
        <label class="field-label">Program level</label>
        <select v-model="levelCode" class="sel">
          <option v-for="lvl in levels" :key="lvl.code" :value="lvl.code">
            {{ lvl.label }}{{ lvl.price_per_page ? ` — from $${lvl.price_per_page}/pg` : '' }}
          </option>
        </select>
      </div>

      <!-- Subject / specialty area -->
      <div>
        <label class="field-label">Nursing specialty <span class="text-brand-500 font-normal normal-case tracking-normal">(optional)</span></label>
        <select v-model="subjectName" class="sel">
          <option value="">— Any specialty —</option>
          <optgroup v-for="(names, category) in subjectGroups" :key="category" :label="String(category)">
            <option v-for="name in names" :key="name" :value="name">{{ name }}</option>
          </optgroup>
        </select>
      </div>

      <!-- Deadline -->
      <div>
        <label class="field-label">When do you need it?</label>
        <select v-model.number="deadlineHrs" class="sel">
          <optgroup v-if="standardDeadlines.length" label="Standard">
            <option v-for="dl in standardDeadlines" :key="dl.max_hours" :value="dl.max_hours">
              {{ dl.label }}{{ dl.multiplier === 1 ? ' — best price' : ` (+${Math.round((dl.multiplier - 1) * 100)}%)` }}
            </option>
          </optgroup>
          <optgroup v-if="expressDeadlines.length" label="Rush order">
            <option v-for="dl in expressDeadlines" :key="dl.max_hours" :value="dl.max_hours">
              {{ dl.label }} (+{{ Math.round((dl.multiplier - 1) * 100) }}%)
            </option>
          </optgroup>
        </select>
      </div>

      <!-- Pages + Spacing -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="field-label">Pages</label>
          <div class="flex h-10 items-center justify-between gap-1 rounded-lg border border-brand-700 bg-brand-800 px-3">
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-lg font-bold text-brand-400 transition-colors hover:bg-brand-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
              :disabled="pages <= 1"
              @click="pages--"
            >−</button>
            <span class="flex-1 text-center text-sm font-bold tabular-nums text-white">{{ pages }}</span>
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-lg font-bold text-brand-400 transition-colors hover:bg-brand-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
              :disabled="pages >= 100"
              @click="pages++"
            >+</button>
          </div>
          <p class="mt-1 text-center text-[11px] text-brand-400">≈ {{ words.toLocaleString() }} words</p>
        </div>
        <div>
          <label class="field-label">Spacing</label>
          <select v-model="spacing" class="sel" :class="!spacing ? 'text-brand-500' : ''">
            <option value="" disabled>— Choose spacing —</option>
            <option value="double">Double (275 w/pg)</option>
            <option value="single">Single (550 w/pg)</option>
          </select>
        </div>
      </div>

      <!-- Add-ons -->
      <div v-if="addons.length" class="space-y-1.5">
        <p class="field-label">Optional extras</p>
        <label
          v-for="addon in addons.slice(0, 4)"
          :key="addon.addon_code"
          class="flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors"
          :class="selectedAddonCodes.includes(addon.addon_code)
            ? 'border-emerald-500/40 bg-emerald-900/30'
            : 'border-brand-700 hover:border-brand-600 hover:bg-brand-800/60'"
        >
          <input
            type="checkbox"
            class="mt-0.5 h-4 w-4 shrink-0 rounded border-brand-600 accent-emerald-500"
            :checked="selectedAddonCodes.includes(addon.addon_code)"
            @change="toggleAddon(addon.addon_code)"
          />
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold text-brand-100">{{ addon.name }}</p>
            <p class="mt-0.5 text-[11px] font-semibold text-emerald-400">+${{ addon.flat_amount }}</p>
          </div>
        </label>
      </div>

      <!-- Nursing-specific free inclusions (writing only) -->
      <Transition name="slide">
        <div v-if="serviceType === 'writing'" class="rounded-lg border border-brand-700 bg-brand-800/60 p-4">
          <p class="mb-2.5 text-[11px] font-bold uppercase tracking-widest text-emerald-400">Included free with every order</p>
          <ul class="grid grid-cols-2 gap-x-3 gap-y-1.5">
            <li
              v-for="item in NURSING_INCLUSIONS" :key="item"
              class="flex items-center gap-1.5 text-[11px] text-brand-200"
            >
              <svg class="size-3 shrink-0 text-emerald-500" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="2 6 5 9 10 3"/>
              </svg>
              {{ item }}
            </li>
          </ul>
        </div>
      </Transition>

      <!-- ── Price + CTA ─────────────────────────────────────────────────── -->
      <div class="overflow-hidden rounded-xl border border-brand-700 bg-brand-800">

        <!-- Price row -->
        <div class="flex items-end justify-between gap-2 px-4 pt-4 pb-3">
          <div>
            <p class="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-brand-300">
              {{ hasLivePrice ? 'Live price' : 'Est. price' }}
              <Loader2 v-if="isPricing" class="size-3 animate-spin text-emerald-400" />
            </p>
            <p class="mt-0.5 text-3xl font-extrabold tabular-nums leading-none text-white">
              ${{ displayPrice.toFixed(2) }}
            </p>
          </div>
          <div class="text-right text-[11px] leading-relaxed text-brand-300">
            <p>${{ (displayPrice / Math.max(pages, 1)).toFixed(2) }}/page</p>
            <p>{{ selectedDeadline?.label }}</p>
          </div>
        </div>

        <!-- Trust row -->
        <div class="flex flex-wrap gap-x-3 gap-y-1 border-t border-brand-700 px-4 py-2.5 text-[11px] text-brand-400">
          <span>✓ Pay after approval</span>
          <span>✓ Free revisions</span>
          <span>✓ NANDA approved</span>
        </div>

        <!-- CTA -->
        <div class="px-4 pb-4 pt-1">
          <a
            :href="orderUrl"
            class="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 text-sm font-bold text-white shadow-md transition-all hover:bg-emerald-400 hover:shadow-lg active:scale-[0.98]"
          >
            Get my nurse writer now
            <svg class="size-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </a>
          <!-- Social proof under CTA -->
          <div class="mt-3 flex items-center justify-center gap-1.5 text-[11px] text-brand-400">
            <div class="flex -space-x-1">
              <div v-for="i in 4" :key="i"
                class="flex size-5 items-center justify-center rounded-full border border-brand-700 bg-brand-700 text-[8px] font-bold text-brand-200">
                {{ ['BSN','MSN','DNP','RN'][i-1] }}
              </div>
            </div>
            <span>9,800+ nursing papers delivered</span>
          </div>
          <p class="mt-1.5 text-center text-[11px] text-brand-500">
            Price confirmed at checkout · no card needed
          </p>
        </div>
      </div>

      <!-- Custom quote -->
      <p class="text-center text-xs text-brand-500">
        Capstone or complex brief?
        <NuxtLink to="/quote" class="font-semibold text-brand-300 transition-colors hover:text-white">Request a custom quote →</NuxtLink>
      </p>

    </div>
  </div>
</template>

<style scoped>
.field-label {
  @apply mb-1.5 block text-xs font-semibold uppercase tracking-wide text-brand-300;
}
.sel {
  @apply h-10 w-full rounded-lg border border-brand-700 bg-brand-800 px-3 text-sm text-white
         focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-colors;
}
.sel option,
.sel optgroup { background: #134e4a; color: #e0f2f1; }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
