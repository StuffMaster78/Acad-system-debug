<script setup lang="ts">
import {
  fetchPricingConfig,
  FALLBACK_LEVELS,
  FALLBACK_DEADLINES,
  type PricingLevel,
  type PricingDeadline,
} from '~/composables/usePricingConfig'

const app = useAppUrl()

const levels    = ref<PricingLevel[]>(FALLBACK_LEVELS)
const deadlines = ref<PricingDeadline[]>(FALLBACK_DEADLINES)
const level     = ref<PricingLevel>(FALLBACK_LEVELS[1] ?? FALLBACK_LEVELS[0])
const deadline  = ref<PricingDeadline>(FALLBACK_DEADLINES[0])
const pages     = ref(1)

onMounted(async () => {
  const cfg = await fetchPricingConfig()
  levels.value    = cfg.academic_levels.length  ? cfg.academic_levels  : FALLBACK_LEVELS
  deadlines.value = cfg.deadlines.length        ? cfg.deadlines        : FALLBACK_DEADLINES
  level.value     = levels.value[1]    ?? levels.value[0]
  deadline.value  = deadlines.value[0]
})

const price = computed(() => {
  const base = level.value.price_per_page ?? 15
  const mult = deadline.value.multiplier  ?? 1
  return (Math.ceil(base * mult * pages.value * 100) / 100).toFixed(2)
})

const orderUrl = computed(() => {
  const p = new URLSearchParams({
    type:     'writing',
    level:    level.value.code,
    deadline: String(deadline.value.max_hours),
    pages:    String(pages.value),
  })
  return `${app.order}?${p}`
})
</script>

<template>
  <div class="bg-white shadow-[0_1px_0_0_#e2e8f0,0_4px_12px_-2px_rgba(0,0,0,0.07)]">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex flex-wrap items-center gap-3 py-3">

        <p class="shrink-0 text-xs font-bold uppercase tracking-widest text-slate-400">
          Get your price:
        </p>

        <!-- Academic level -->
        <select
          class="h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none"
          :value="level.code"
          @change="level = levels.find(l => l.code === ($event.target as HTMLSelectElement).value) ?? levels[0]"
        >
          <option v-for="l in levels" :key="l.code" :value="l.code">{{ l.label }}</option>
        </select>

        <!-- Deadline -->
        <select
          class="h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 focus:border-brand-500 focus:outline-none"
          :value="deadline.max_hours"
          @change="deadline = deadlines.find(d => d.max_hours === Number(($event.target as HTMLSelectElement).value)) ?? deadlines[0]"
        >
          <option v-for="d in deadlines" :key="d.max_hours" :value="d.max_hours">{{ d.label }}</option>
        </select>

        <!-- Pages stepper -->
        <div class="flex h-9 items-center gap-1.5 rounded-lg border border-slate-200 px-2.5">
          <button
            type="button"
            class="flex h-5 w-5 items-center justify-center rounded text-slate-500 hover:bg-slate-100 disabled:opacity-30 text-base leading-none"
            :disabled="pages <= 1"
            @click="pages--"
          >−</button>
          <span class="w-5 text-center text-sm font-bold tabular-nums text-slate-900">{{ pages }}</span>
          <button
            type="button"
            class="flex h-5 w-5 items-center justify-center rounded text-slate-500 hover:bg-slate-100 disabled:opacity-30 text-base leading-none"
            :disabled="pages >= 50"
            @click="pages++"
          >+</button>
          <span class="ml-1 text-xs text-slate-400">pg{{ pages > 1 ? 's' : '' }}</span>
        </div>

        <!-- Live price -->
        <div class="flex items-baseline gap-1">
          <span class="text-[11px] text-slate-400">from</span>
          <span class="text-xl font-extrabold tabular-nums text-brand-700">${{ price }}</span>
        </div>

        <!-- CTA -->
        <a
          :href="orderUrl"
          class="ml-auto inline-flex h-9 items-center gap-1.5 rounded-xl bg-brand-600 px-5 text-sm font-bold text-white shadow-sm transition-colors hover:bg-brand-700 shrink-0"
        >
          Order now
          <svg class="size-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </a>

      </div>
    </div>
  </div>
</template>
