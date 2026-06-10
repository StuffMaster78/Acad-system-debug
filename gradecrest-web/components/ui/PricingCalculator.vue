<script setup lang="ts">
import { Minus, Plus } from '@lucide/vue'
import {
  ACADEMIC_LEVELS, DEADLINES, PAPER_TYPES,
  usePricing,
} from '~/composables/usePricing'

const app   = useAppUrl()
const { calculate } = usePricing()

const levelKey    = ref(ACADEMIC_LEVELS[1].key)
const deadlineKey = ref(DEADLINES[0].key)
const paperKey    = ref(PAPER_TYPES[0].key)
const pages       = ref(1)

const price = computed(() => calculate({ levelKey: levelKey.value, deadlineKey: deadlineKey.value, pages: pages.value }))
const perPage = computed(() => calculate({ levelKey: levelKey.value, deadlineKey: deadlineKey.value, pages: 1 }))

function incPages() { if (pages.value < 100) pages.value++ }
function decPages() { if (pages.value >   1) pages.value-- }

// Build order URL with pre-filled params
const orderUrl = computed(() => {
  const p = new URLSearchParams({
    level:    levelKey.value,
    deadline: deadlineKey.value,
    type:     paperKey.value,
    pages:    String(pages.value),
  })
  return `${app.order}?${p.toString()}`
})
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white shadow-lift overflow-hidden">

    <!-- Paper type -->
    <div class="border-b border-slate-100 px-5 pt-5 pb-4">
      <label class="block text-xs font-semibold uppercase tracking-widest text-graphite mb-2">Type of work</label>
      <select
        v-model="paperKey"
        class="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500"
      >
        <option v-for="pt in PAPER_TYPES" :key="pt.key" :value="pt.key">{{ pt.label }}</option>
      </select>
    </div>

    <!-- Academic level -->
    <div class="border-b border-slate-100 px-5 py-4">
      <label class="block text-xs font-semibold uppercase tracking-widest text-graphite mb-2">Academic level</label>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="lvl in ACADEMIC_LEVELS"
          :key="lvl.key"
          class="rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="levelKey === lvl.key
            ? 'bg-gc-600 border-gc-600 text-white'
            : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
          @click="levelKey = lvl.key"
        >
          {{ lvl.label }}
        </button>
      </div>
    </div>

    <!-- Deadline -->
    <div class="border-b border-slate-100 px-5 py-4">
      <label class="block text-xs font-semibold uppercase tracking-widest text-graphite mb-2">Deadline</label>
      <select
        v-model="deadlineKey"
        class="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-gc-500"
      >
        <option v-for="dl in DEADLINES" :key="dl.key" :value="dl.key">
          {{ dl.label }}{{ dl.urgent ? ' — Rush' : '' }}
        </option>
      </select>
    </div>

    <!-- Pages -->
    <div class="border-b border-slate-100 px-5 py-4">
      <div class="flex items-center justify-between">
        <label class="text-xs font-semibold uppercase tracking-widest text-graphite">Pages</label>
        <span class="text-xs text-graphite">{{ pages * 275 }} words</span>
      </div>
      <div class="mt-2 flex items-center gap-3">
        <button
          class="flex size-9 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:bg-slate-50 disabled:opacity-40 transition-colors"
          :disabled="pages <= 1"
          @click="decPages"
        >
          <Minus class="size-4" />
        </button>
        <span class="w-8 text-center text-xl font-semibold text-ink tabular-nums">{{ pages }}</span>
        <button
          class="flex size-9 items-center justify-center rounded-lg border border-slate-200 text-graphite hover:bg-slate-50 disabled:opacity-40 transition-colors"
          :disabled="pages >= 100"
          @click="incPages"
        >
          <Plus class="size-4" />
        </button>
        <span class="ml-auto text-xs text-graphite">${{ perPage.toFixed(2) }} / page</span>
      </div>
    </div>

    <!-- Price + CTA -->
    <div class="bg-slate-50 px-5 py-4 space-y-3">
      <div class="flex items-end justify-between">
        <div>
          <p class="text-xs text-graphite">Total</p>
          <p class="text-3xl font-bold text-ink tabular-nums">${{ price.toFixed(2) }}</p>
        </div>
        <p class="text-xs text-graphite text-right leading-relaxed">
          Title page, references<br />& plagiarism report free
        </p>
      </div>
      <a
        :href="orderUrl"
        class="flex h-12 w-full items-center justify-center rounded-xl bg-gc-600 text-sm font-bold text-white shadow-sm transition-colors hover:bg-gc-700"
      >
        Place order
      </a>
      <p class="text-center text-xs text-graphite">Secure checkout · Grade or money back</p>
    </div>

  </div>
</template>
