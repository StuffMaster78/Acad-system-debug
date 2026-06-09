<script setup lang="ts">
const app = useAppUrl()

const levels = [
  { label: 'High School',         value: 15 },
  { label: 'Undergraduate 1–2',   value: 18 },
  { label: 'Undergraduate 3–4',   value: 22 },
  { label: "Master's",            value: 28 },
  { label: 'PhD / Doctoral',      value: 36 },
]

const deadlines = [
  { label: '14 days',   multiplier: 1.0 },
  { label: '7 days',    multiplier: 1.1 },
  { label: '3 days',    multiplier: 1.2 },
  { label: '24 hours',  multiplier: 1.35 },
  { label: '12 hours',  multiplier: 1.5 },
  { label: '6 hours',   multiplier: 1.65 },
]

const selectedLevel    = ref(levels[1])
const selectedDeadline = ref(deadlines[0])
const pages            = ref(1)

const total = computed(() =>
  Math.ceil(selectedLevel.value.value * selectedDeadline.value.multiplier * pages.value)
)

const orderUrl = computed(() => {
  const params = new URLSearchParams({
    level:    selectedLevel.value.label,
    deadline: selectedDeadline.value.label,
    pages:    String(pages.value),
  })
  return `/order?${params}`
})
</script>

<template>
  <div class="rounded-2xl border border-brand-100 bg-white p-5 shadow-sm">
    <h3 class="mb-4 font-serif text-base font-bold text-slate-900">Get an instant quote</h3>

    <div class="space-y-3">
      <!-- Level -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Academic level
        </label>
        <select
          v-model="selectedLevel"
          class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option v-for="l in levels" :key="l.label" :value="l">{{ l.label }}</option>
        </select>
      </div>

      <!-- Deadline -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Deadline
        </label>
        <select
          v-model="selectedDeadline"
          class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        >
          <option v-for="d in deadlines" :key="d.label" :value="d">{{ d.label }}</option>
        </select>
      </div>

      <!-- Pages -->
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wider text-slate-400">
          Pages ({{ pages * 275 }} words)
        </label>
        <div class="flex items-center gap-3">
          <button
            class="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:opacity-30"
            :disabled="pages <= 1"
            @click="pages = Math.max(1, pages - 1)"
          >
            −
          </button>
          <span class="w-6 text-center font-bold text-slate-900">{{ pages }}</span>
          <button
            class="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600"
            @click="pages++"
          >
            +
          </button>
        </div>
      </div>
    </div>

    <!-- Result -->
    <div class="mt-4 flex items-center justify-between rounded-xl bg-brand-50 px-4 py-3">
      <div>
        <p class="text-xs text-brand-600 font-medium">Estimated total</p>
        <p class="text-2xl font-bold text-brand-700">${{ total }}</p>
      </div>
      <a :href="orderUrl" class="btn-primary px-4 py-2 text-sm">
        Order now
      </a>
    </div>
    <p class="mt-2 text-center text-xs text-slate-400">No payment required to browse</p>
  </div>
</template>
