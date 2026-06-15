<script setup lang="ts">
import {
  fetchPricingConfig, FALLBACK_LEVELS, FALLBACK_DEADLINES,
  type PricingLevel, type PricingDeadline,
} from '~/composables/usePricingConfig'

const app = useAppUrl()

const levels    = ref<PricingLevel[]>(FALLBACK_LEVELS)
const deadlines = ref<PricingDeadline[]>(FALLBACK_DEADLINES)

const selectedLevel    = ref<PricingLevel>(FALLBACK_LEVELS[1])
const selectedDeadline = ref<PricingDeadline>(FALLBACK_DEADLINES[0])
const pages            = ref(1)

onMounted(async () => {
  const cfg       = await fetchPricingConfig()
  levels.value    = cfg.academic_levels
  deadlines.value = cfg.deadlines
  selectedLevel.value    = cfg.academic_levels[1] ?? cfg.academic_levels[0]
  selectedDeadline.value = cfg.deadlines[0]
})

const total = computed(() => {
  const base = selectedLevel.value.price_per_page ?? 15
  const mult = selectedDeadline.value.multiplier  ?? 1
  return (Math.ceil(base * mult * pages.value * 100) / 100).toFixed(2)
})

const orderUrl = computed(() => {
  const p = new URLSearchParams({
    level:    selectedLevel.value.code,
    deadline: String(selectedDeadline.value.max_hours),
    pages:    String(pages.value),
  })
  return `/order?${p}`
})
</script>

<template>
  <div class="rounded-2xl border border-brand-100 bg-white p-6 shadow-lg">
    <h3 class="mb-6 font-serif text-xl font-bold text-slate-900">Get an instant quote</h3>

    <div class="space-y-4">
      <!-- Level -->
      <div>
        <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Academic level
        </label>
        <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
          <button
            v-for="l in levels"
            :key="l.code"
            class="rounded-lg border px-3 py-2 text-sm transition-colors"
            :class="selectedLevel.code === l.code
              ? 'border-brand-600 bg-brand-600 text-white font-semibold'
              : 'border-slate-200 text-slate-600 hover:border-brand-300'"
            @click="selectedLevel = l"
          >
            {{ l.label }}
            <span v-if="l.price_per_page" class="block text-[10px] opacity-70">from ${{ l.price_per_page }}/pg</span>
          </button>
        </div>
      </div>

      <!-- Deadline -->
      <div>
        <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Deadline
        </label>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="d in deadlines"
            :key="d.max_hours"
            class="rounded-lg border px-3 py-2 text-sm transition-colors"
            :class="selectedDeadline.max_hours === d.max_hours
              ? 'border-brand-600 bg-brand-600 text-white font-semibold'
              : 'border-slate-200 text-slate-600 hover:border-brand-300'"
            @click="selectedDeadline = d"
          >
            {{ d.label }}
          </button>
        </div>
      </div>

      <!-- Pages -->
      <div>
        <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Pages ({{ pages * 275 }} words)
        </label>
        <div class="flex items-center gap-4">
          <button
            class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30"
            :disabled="pages <= 1"
            @click="pages = Math.max(1, pages - 1)"
          >−</button>
          <span class="w-8 text-center text-lg font-bold text-slate-900">{{ pages }}</span>
          <button
            class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600"
            @click="pages++"
          >+</button>
        </div>
      </div>
    </div>

    <!-- Result -->
    <div class="mt-6 flex items-center justify-between rounded-xl bg-brand-50 px-5 py-4">
      <div>
        <p class="text-xs font-medium text-brand-600">Estimated total</p>
        <p class="text-3xl font-bold text-brand-700">${{ total }}</p>
      </div>
      <a :href="orderUrl" class="btn-primary px-6 py-3 text-sm">Order now</a>
    </div>
    <p class="mt-3 text-center text-xs text-slate-400">
      Final price confirmed at checkout · No payment required to place order
    </p>
  </div>
</template>
