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

const selectedLevel = ref(levels[1])
const selectedDeadline = ref(deadlines[0])
const pages = ref(1)

const total = computed(() =>
  Math.ceil(selectedLevel.value.value * selectedDeadline.value.multiplier * pages.value)
)

const orderUrl = computed(() => {
  const params = new URLSearchParams({
    level: selectedLevel.value.label,
    deadline: selectedDeadline.value.label,
    pages: String(pages.value),
  })
  return `${app.register}?${params}`
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
            :key="l.label"
            class="rounded-lg border px-3 py-2 text-sm transition-colors"
            :class="selectedLevel === l
              ? 'border-brand-600 bg-brand-600 text-white font-semibold'
              : 'border-slate-200 text-slate-600 hover:border-brand-300'"
            @click="selectedLevel = l"
          >
            {{ l.label }}
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
            :key="d.label"
            class="rounded-lg border px-3 py-2 text-sm transition-colors"
            :class="selectedDeadline === d
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
          >
            −
          </button>
          <span class="w-8 text-center text-lg font-bold text-slate-900">{{ pages }}</span>
          <button
            class="flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600"
            @click="pages++"
          >
            +
          </button>
        </div>
      </div>
    </div>

    <!-- Result -->
    <div class="mt-6 flex items-center justify-between rounded-xl bg-brand-50 px-5 py-4">
      <div>
        <p class="text-xs text-brand-600 font-medium">Estimated total</p>
        <p class="text-3xl font-bold text-brand-700">${{ total }}</p>
      </div>
      <a :href="orderUrl" class="btn-primary px-6 py-3 text-sm">
        Order now
      </a>
    </div>
    <p class="mt-3 text-center text-xs text-slate-400">
      Final price confirmed at checkout · No payment required to place order
    </p>
  </div>
</template>
