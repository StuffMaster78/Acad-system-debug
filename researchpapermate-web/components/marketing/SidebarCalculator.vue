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
  <div class="rounded-2xl border border-parchment-300 bg-white p-5 shadow-sm">
    <h3 class="mb-4 font-serif text-base font-bold text-slate-900">Get an instant quote</h3>

    <div class="space-y-3">
      <!-- Level -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Academic level
        </label>
        <select
          class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-claret-500 focus:outline-none focus:ring-1 focus:ring-claret-200"
          :value="selectedLevel.code"
          @change="selectedLevel = levels.find(l => l.code === ($event.target as HTMLSelectElement).value) ?? levels[0]"
        >
          <option v-for="l in levels" :key="l.code" :value="l.code">
            {{ l.label }}{{ l.price_per_page ? ` — from $${l.price_per_page}/pg` : '' }}
          </option>
        </select>
      </div>

      <!-- Deadline -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Deadline
        </label>
        <select
          class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-claret-500 focus:outline-none focus:ring-1 focus:ring-claret-200"
          :value="selectedDeadline.max_hours"
          @change="selectedDeadline = deadlines.find(d => d.max_hours === Number(($event.target as HTMLSelectElement).value)) ?? deadlines[0]"
        >
          <option v-for="d in deadlines" :key="d.max_hours" :value="d.max_hours">{{ d.label }}</option>
        </select>
      </div>

      <!-- Pages -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Pages ({{ pages * 275 }} words)
        </label>
        <div class="flex items-center gap-3">
          <button
            class="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-amber-500 hover:text-amber-700 disabled:opacity-30"
            :disabled="pages <= 1"
            @click="pages = Math.max(1, pages - 1)"
          >−</button>
          <span class="w-6 text-center font-bold text-slate-900">{{ pages }}</span>
          <button
            class="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-amber-500 hover:text-amber-700"
            @click="pages++"
          >+</button>
        </div>
      </div>
    </div>

    <!-- Result -->
    <div class="mt-4 flex items-center justify-between rounded-xl bg-parchment-100 px-4 py-3">
      <div>
        <p class="text-xs font-medium text-amber-700">Estimated total</p>
        <p class="text-2xl font-bold text-claret-700">${{ total }}</p>
      </div>
      <a :href="orderUrl" class="btn-primary px-4 py-2 text-sm">Order now</a>
    </div>
    <p class="mt-2 text-center text-xs text-slate-400">No payment required to browse</p>
  </div>
</template>
