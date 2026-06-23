<script setup lang="ts">
import {
  fetchPricingConfig, FALLBACK_LEVELS, FALLBACK_DEADLINES,
  type PricingLevel, type PricingDeadline, type CfgAddon,
} from '~/composables/usePricingConfig'

const app = useAppUrl()

const levels    = ref<PricingLevel[]>(FALLBACK_LEVELS)
const deadlines = ref<PricingDeadline[]>(FALLBACK_DEADLINES)
const addons    = ref<CfgAddon[]>([])

const selectedLevelCode    = ref(FALLBACK_LEVELS[1]?.code ?? FALLBACK_LEVELS[0]?.code)
const selectedDeadlineHrs  = ref(FALLBACK_DEADLINES[0]?.max_hours ?? 336)
const pages                = ref(1)
const spacing              = ref<'double' | 'single'>('double')
const selectedAddonCodes   = ref<string[]>([])

onMounted(async () => {
  const cfg           = await fetchPricingConfig()
  levels.value        = cfg.academic_levels
  deadlines.value     = cfg.deadlines
  addons.value        = cfg.addons
  selectedLevelCode.value   = cfg.academic_levels[1]?.code ?? cfg.academic_levels[0]?.code
  selectedDeadlineHrs.value = cfg.deadlines[0]?.max_hours
})

function toggleAddon(code: string) {
  const idx = selectedAddonCodes.value.indexOf(code)
  if (idx >= 0) selectedAddonCodes.value.splice(idx, 1)
  else selectedAddonCodes.value.push(code)
}

const standardDeadlines = computed(() => deadlines.value.filter(d => d.max_hours > 48))
const expressDeadlines  = computed(() => deadlines.value.filter(d => d.max_hours <= 48))

const selectedLevel    = computed(() => levels.value.find(l => l.code === selectedLevelCode.value) ?? levels.value[0])
const selectedDeadline = computed(() => deadlines.value.find(d => d.max_hours === selectedDeadlineHrs.value) ?? deadlines.value[0])

const spacingMultiplier = computed(() => spacing.value === 'single' ? 2 : 1)
const wordsPerPage      = computed(() => spacing.value === 'double' ? 275 : 550)
const words             = computed(() => pages.value * wordsPerPage.value)

const addonTotal = computed(() =>
  addons.value
    .filter(a => selectedAddonCodes.value.includes(a.addon_code))
    .reduce((sum, a) => sum + a.flat_amount, 0)
)

const baseTotal = computed(() => {
  const base = selectedLevel.value?.price_per_page ?? 15
  const mult = selectedDeadline.value?.multiplier  ?? 1
  return Math.ceil(base * mult * spacingMultiplier.value * pages.value * 100) / 100
})

const total = computed(() => (baseTotal.value + addonTotal.value).toFixed(2))

const orderUrl = computed(() => {
  const p = new URLSearchParams({
    level:    selectedLevelCode.value ?? '',
    deadline: String(selectedDeadlineHrs.value),
    pages:    String(pages.value),
  })
  if (spacing.value === 'single') p.set('spacing', 'single')
  if (selectedAddonCodes.value.length) p.set('addons', selectedAddonCodes.value.join(','))
  return `/order?${p}`
})
</script>

<template>
  <div class="rounded-2xl border border-brand-100 bg-white p-6 shadow-lg">
    <h3 class="mb-5 font-serif text-xl font-bold text-slate-900">Get an instant quote</h3>

    <div class="space-y-5">

      <!-- Academic level — dropdown -->
      <div>
        <label class="field-label">Academic level</label>
        <select v-model="selectedLevelCode" class="sel">
          <option v-for="l in levels" :key="l.code" :value="l.code">
            {{ l.label }}{{ l.price_per_page ? ` — from $${l.price_per_page}/page` : '' }}
          </option>
        </select>
      </div>

      <!-- Deadline — dropdown (10 options don't fit as buttons) -->
      <div>
        <label class="field-label">Deadline</label>
        <select v-model.number="selectedDeadlineHrs" class="sel">
          <optgroup v-if="standardDeadlines.length" label="Standard delivery">
            <option v-for="d in standardDeadlines" :key="d.max_hours" :value="d.max_hours">
              {{ d.label }}{{ d.multiplier === 1 ? ' — best price' : ` (+${Math.round((d.multiplier - 1) * 100)}%)` }}
            </option>
          </optgroup>
          <optgroup v-if="expressDeadlines.length" label="Express (rush rates)">
            <option v-for="d in expressDeadlines" :key="d.max_hours" :value="d.max_hours">
              {{ d.label }} (+{{ Math.round((d.multiplier - 1) * 100) }}%)
            </option>
          </optgroup>
        </select>
      </div>

      <!-- Pages + spacing -->
      <div>
        <div class="mb-1.5 flex items-end justify-between">
          <label class="field-label mb-0">Pages</label>
          <span class="text-[11px] text-slate-400">≈ {{ words.toLocaleString() }} words</span>
        </div>
        <!-- Stepper -->
        <div class="flex h-11 items-stretch overflow-hidden rounded-lg border border-slate-200">
          <button
            type="button"
            class="flex w-12 shrink-0 items-center justify-center text-xl font-light text-slate-500 transition-colors hover:bg-slate-100 disabled:opacity-30"
            :disabled="pages <= 1"
            @click="pages = Math.max(1, pages - 1)"
          >−</button>
          <input
            type="number"
            v-model.number="pages"
            min="1"
            max="100"
            class="min-w-0 flex-1 border-x border-slate-200 bg-white text-center text-lg font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-300"
          />
          <button
            type="button"
            class="flex w-12 shrink-0 items-center justify-center text-xl font-light text-slate-500 transition-colors hover:bg-slate-100"
            @click="pages++"
          >+</button>
        </div>
        <!-- Spacing -->
        <div class="mt-2">
          <select v-model="spacing" class="sel">
            <option value="double">Double spaced (275 words/page)</option>
            <option value="single">Single spaced (550 words/page)</option>
          </select>
        </div>
      </div>
      <!-- Add-ons -->
      <div v-if="addons.length" class="space-y-1.5">
        <p class="field-label">Optional add-ons</p>
        <label
          v-for="addon in addons.slice(0, 4)" :key="addon.addon_code"
          class="flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-colors"
          :class="selectedAddonCodes.includes(addon.addon_code)
            ? 'border-brand-300 bg-brand-50'
            : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'"
        >
          <input
            type="checkbox"
            class="mt-0.5 h-4 w-4 shrink-0 rounded border-slate-300 accent-brand-600"
            :checked="selectedAddonCodes.includes(addon.addon_code)"
            @change="toggleAddon(addon.addon_code)"
          />
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold leading-tight text-slate-800">{{ addon.name }}</p>
            <p class="mt-0.5 text-[11px] font-semibold text-brand-700">+${{ addon.flat_amount }}</p>
          </div>
        </label>
      </div>

    </div>

    <!-- Result -->
    <div class="mt-6 flex items-center justify-between rounded-xl bg-brand-50 px-5 py-4">
      <div>
        <p class="text-xs font-medium text-brand-600">Estimated total</p>
        <p class="text-3xl font-bold tabular-nums text-brand-700">${{ total }}</p>
        <p class="mt-0.5 text-xs text-brand-500">
          ${{ (baseTotal / Math.max(pages, 1)).toFixed(2) }}/page · {{ selectedLevel?.label }}
        </p>
      </div>
      <a :href="orderUrl" class="btn-primary px-6 py-3 text-sm">Order now</a>
    </div>
    <p class="mt-3 text-center text-xs text-slate-400">
      Final price confirmed at checkout · No payment required to place order
    </p>
  </div>
</template>

<style scoped>
.sel {
  @apply h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100;
}
.field-label {
  @apply mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400;
}
</style>
