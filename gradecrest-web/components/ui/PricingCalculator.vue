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

const FREE_INCLUSIONS = [
  'Cover page', 'Title page', 'Reference list',
  'Appendix', 'Citation formatting', 'Plagiarism-free report',
]

type EstimateResponse = {
  total?: string | number | null
  estimated_min_price?: string | number | null
}

const app    = useAppUrl()
const config = useRuntimeConfig()

const { data: pricingConfig } = useLazyAsyncData('gc-pricing-config', fetchPricingConfig)

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
  const base = selectedLevel.value?.price_per_page ?? 13
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
  if (levelCode.value)   p.set('level', levelCode.value)
  if (deadlineHrs.value) p.set('deadline', String(deadlineHrs.value))
  if (pages.value > 1)   p.set('pages', String(pages.value))
  if (paperCode.value)   p.set('paper', paperCode.value)
  if (spacing.value === 'single') p.set('spacing', 'single')
  if (subjectName.value) p.set('subject', subjectName.value)
  if (selectedAddonCodes.value.length) p.set('addons', selectedAddonCodes.value.join(','))
  return `/order?${p.toString()}`
})
</script>

<template>
  <div class="overflow-hidden rounded-2xl bg-forest-950 shadow-[0_8px_32px_rgba(0,0,0,0.4)] ring-1 ring-white/10">

    <!-- Header -->
    <div class="border-b border-white/10 px-5 py-4">
      <p class="text-xs font-bold uppercase tracking-widest text-gold-400">Instant price estimate</p>
      <p class="mt-0.5 text-[11px] text-white/45">Adjust options — price updates live</p>
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
        <label class="field-label">Subject area <span class="text-white/30 font-normal normal-case tracking-normal">(optional)</span></label>
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
          <optgroup v-if="expressDeadlines.length" label="Express">
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
          <div class="flex h-10 items-center justify-between gap-2 rounded-lg border border-white/15 bg-forest-900 px-3">
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-base font-bold text-white/50 transition-colors hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-25"
              :disabled="pages <= 1"
              @click="pages--"
            >−</button>
            <span class="flex-1 text-center text-sm font-bold tabular-nums text-white">{{ pages }}</span>
            <button
              type="button"
              class="flex size-6 shrink-0 items-center justify-center rounded text-base font-bold text-white/50 transition-colors hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-25"
              :disabled="pages >= 100"
              @click="pages++"
            >+</button>
          </div>
          <p class="mt-1 text-center text-[11px] text-white/40">≈ {{ words.toLocaleString() }} words</p>
        </div>

        <!-- Spacing -->
        <div>
          <label class="field-label">Spacing</label>
          <select v-model="spacing" class="sel" :class="!spacing ? 'text-white/40' : ''">
            <option value="" disabled>— Choose spacing —</option>
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
            v-for="addon in addons"
            :key="addon.addon_code"
            class="flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors"
            :class="selectedAddonCodes.includes(addon.addon_code)
              ? 'border-gold-600/40 bg-gold-900/20'
              : 'border-white/10 hover:border-white/20 hover:bg-white/5'"
          >
            <input
              type="checkbox"
              class="mt-0.5 h-4 w-4 shrink-0 rounded border-white/30 accent-gold-400"
              :checked="selectedAddonCodes.includes(addon.addon_code)"
              @change="toggleAddon(addon.addon_code)"
            />
            <div class="min-w-0 flex-1">
              <p class="text-xs font-semibold leading-tight text-white/90">{{ addon.name }}</p>
              <p class="mt-0.5 text-[11px] text-gold-400">+${{ addon.flat_amount.toFixed(2) }}</p>
            </div>
          </label>
        </div>
      </div>

      <!-- ── Free inclusions (writing only) ───────────────────────────────── -->
      <Transition name="slide">
        <div v-if="serviceType === 'writing'" class="rounded-lg border border-gold-700/30 bg-gold-500/10 p-4">
          <p class="mb-2.5 text-[11px] font-bold uppercase tracking-widest text-gold-400">Included free</p>
          <ul class="grid grid-cols-2 gap-x-3 gap-y-1.5">
            <li
              v-for="item in FREE_INCLUSIONS" :key="item"
              class="flex items-center gap-1.5 text-[11px] text-gold-200/80"
            >
              <svg class="size-3 shrink-0 text-gold-500" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="2 6 5 9 10 3"/>
              </svg>
              {{ item }}
            </li>
          </ul>
        </div>
      </Transition>

      <!-- ── Price + CTA ───────────────────────────────────────────────────── -->
      <div class="rounded-xl border border-white/10 bg-forest-900 p-4">

        <!-- Price row -->
        <div class="flex items-end justify-between gap-2">
          <div>
            <p class="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/45">
              {{ hasLivePrice ? 'Live price' : 'Est. price' }}
              <Loader2 v-if="isPricing" class="size-3 animate-spin text-gold-400" />
            </p>
            <p class="mt-0.5 text-3xl font-extrabold tabular-nums leading-none text-gold-300">
              ${{ displayPrice.toFixed(2) }}
            </p>
          </div>
          <div class="text-right text-[11px] leading-relaxed text-white/45">
            <p>${{ (displayPrice / Math.max(pages, 1)).toFixed(2) }}/page</p>
            <p>{{ selectedDeadline?.label }}</p>
          </div>
        </div>

        <!-- Trust bullets -->
        <div class="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-white/10 pt-3 text-[11px] text-white/40">
          <span>✓ Pay after approval</span>
          <span>✓ Free revisions</span>
          <span>✓ No AI content</span>
        </div>

        <!-- CTA -->
        <a
          :href="orderUrl"
          class="mt-3 flex h-11 w-full items-center justify-center rounded-xl bg-gc-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-gc-500"
        >
          Order now — {{ selectedLevel?.label }}
        </a>

        <p class="mt-2 text-center text-[11px] text-white/30">
          Exact price confirmed at checkout · no card needed
        </p>
      </div>

      <!-- Custom quote link -->
      <p class="text-center text-xs text-white/30">
        Complex scope?
        <NuxtLink to="/contact" class="font-semibold text-gold-400/70 transition-colors hover:text-gold-300">Request a custom quote →</NuxtLink>
      </p>

    </div>
  </div>
</template>

<style scoped>
.field-label {
  @apply mb-1.5 block text-xs font-semibold uppercase tracking-wide text-white/55;
}
.sel {
  @apply h-10 w-full rounded-lg border border-white/15 bg-forest-900 px-3 text-sm text-white focus:border-gold-500/50 focus:outline-none focus:ring-1 focus:ring-gold-500/30 transition-colors;
}
.sel option,
.sel optgroup { background: #052e16; color: #f1f5f9; }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
