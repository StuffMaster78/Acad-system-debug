<script setup lang="ts">
useSeoMeta({
  title: 'Grade Calculator — What Grade Do I Need on My Final?',
  description: 'Calculate your current weighted grade and find out exactly what score you need on your final exam to reach your goal. Free, instant, no sign-up required.',
})

type Tab = 'current' | 'final'
const activeTab = ref<Tab>('current')

// ---- Tab 1: Current Grade ----
interface Category {
  id: number
  name: string
  weight: number
  earned: number
  possible: number
}

let nextId = 5
const categories = ref<Category[]>([
  { id: 1, name: 'Homework', weight: 20, earned: 85, possible: 100 },
  { id: 2, name: 'Midterm', weight: 30, earned: 74, possible: 100 },
  { id: 3, name: 'Quizzes', weight: 20, earned: 90, possible: 100 },
  { id: 4, name: 'Final Exam', weight: 30, earned: 0, possible: 100 },
])

function addCategory() {
  categories.value.push({ id: nextId++, name: '', weight: 0, earned: 0, possible: 100 })
}
function removeCategory(id: number) {
  if (categories.value.length > 1) categories.value = categories.value.filter(c => c.id !== id)
}

const totalWeight = computed(() => categories.value.reduce((s, c) => s + (c.weight || 0), 0))
const weightOk = computed(() => Math.abs(totalWeight.value - 100) < 0.01)

const weightedGrade = computed(() => {
  const valid = categories.value.filter(c => c.weight > 0 && c.possible > 0)
  const tw = valid.reduce((s, c) => s + c.weight, 0)
  if (tw === 0) return null
  const weighted = valid.reduce((s, c) => s + (c.earned / c.possible) * 100 * c.weight, 0)
  return Math.round((weighted / tw) * 10) / 10
})

function gradeLabel(pct: number | null): string {
  if (pct === null) return '—'
  if (pct >= 90) return 'A'
  if (pct >= 80) return 'B'
  if (pct >= 70) return 'C'
  if (pct >= 60) return 'D'
  return 'F'
}
function gradeColor(pct: number | null): string {
  if (pct === null) return 'text-slate-400'
  if (pct >= 80) return 'text-green-600'
  if (pct >= 70) return 'text-amber-600'
  return 'text-red-600'
}
function gradeBg(pct: number | null): string {
  if (pct === null) return 'bg-slate-50 border-slate-200'
  if (pct >= 80) return 'bg-green-50 border-green-200'
  if (pct >= 70) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}

// ---- Tab 2: Final Exam ----
const currentGrade = ref(78)
const finalWeight = ref(30)
const desiredGrade = ref(80)

const neededScore = computed(() => {
  const w = finalWeight.value / 100
  if (w <= 0 || w >= 1) return null
  return Math.round(((desiredGrade.value - currentGrade.value * (1 - w)) / w) * 10) / 10
})

const finalResultColor = computed(() => {
  const n = neededScore.value
  if (n === null) return 'bg-slate-50 border-slate-200 text-slate-700'
  if (n > 100) return 'bg-red-50 border-red-200 text-red-700'
  if (n >= 90) return 'bg-red-50 border-red-200 text-red-700'
  if (n >= 70) return 'bg-amber-50 border-amber-200 text-amber-700'
  return 'bg-green-50 border-green-200 text-green-700'
})

const finalResultMsg = computed(() => {
  const n = neededScore.value
  if (n === null) return ''
  if (n > 100) return `This goal is not achievable — you would need ${n}% on your final, which exceeds 100%.`
  if (n < 0) return `You have already reached ${desiredGrade.value}% — any score on the final will maintain it.`
  return `You need ${n}% on your final exam to finish with ${desiredGrade.value}%.`
})

const gradeScale = [
  { grade: 'A', range: '90–100%', color: 'text-green-700 bg-green-50' },
  { grade: 'B', range: '80–89%', color: 'text-blue-700 bg-blue-50' },
  { grade: 'C', range: '70–79%', color: 'text-amber-700 bg-amber-50' },
  { grade: 'D', range: '60–69%', color: 'text-orange-700 bg-orange-50' },
  { grade: 'F', range: '< 60%', color: 'text-red-700 bg-red-50' },
]
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Grade Calculator</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Grade Calculator</h1>
      <p class="text-slate-500 text-sm">Calculate your current weighted grade or find out what you need on your final exam.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Tabs -->
      <div class="flex gap-0 border border-slate-200 rounded-2xl bg-white shadow-sm overflow-hidden w-fit">
        <button
          type="button"
          @click="activeTab = 'current'"
          :class="['px-6 py-3 text-sm font-bold transition-all', activeTab === 'current' ? 'bg-brand-600 text-white' : 'text-slate-600 hover:text-brand-600']"
        >Current Grade</button>
        <button
          type="button"
          @click="activeTab = 'final'"
          :class="['px-6 py-3 text-sm font-bold transition-all', activeTab === 'final' ? 'bg-brand-600 text-white' : 'text-slate-600 hover:text-brand-600']"
        >Final Exam — What do I need?</button>
      </div>

      <!-- Tab 1: Current Grade -->
      <template v-if="activeTab === 'current'">
        <!-- Result -->
        <div :class="['rounded-2xl border shadow-sm p-6 text-center transition-colors', gradeBg(weightedGrade)]">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Current Weighted Grade</p>
          <p :class="['text-6xl font-extrabold', gradeColor(weightedGrade)]">
            {{ weightedGrade !== null ? weightedGrade + '%' : '—' }}
          </p>
          <p :class="['text-2xl font-bold mt-1', gradeColor(weightedGrade)]">{{ gradeLabel(weightedGrade) }}</p>
          <p v-if="!weightOk" class="text-amber-600 text-xs mt-2 font-semibold">⚠ Weights sum to {{ totalWeight }}% — adjust to 100% for accurate results</p>
        </div>

        <!-- Category rows -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Grade Categories</h2>

          <div class="space-y-3">
            <div class="hidden sm:grid grid-cols-12 gap-3 px-1">
              <span class="col-span-4 text-xs font-semibold text-slate-400 uppercase">Category</span>
              <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase">Weight %</span>
              <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase">Earned</span>
              <span class="col-span-2 text-xs font-semibold text-slate-400 uppercase">Possible</span>
              <span class="col-span-1 text-xs font-semibold text-slate-400 uppercase">Score</span>
              <span class="col-span-1" />
            </div>

            <div v-for="cat in categories" :key="cat.id" class="grid grid-cols-12 gap-2 sm:gap-3 items-center">
              <input v-model="cat.name" type="text" placeholder="Category name"
                class="col-span-12 sm:col-span-4 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
              <input v-model.number="cat.weight" type="number" min="0" max="100" placeholder="Weight"
                class="col-span-4 sm:col-span-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
              <input v-model.number="cat.earned" type="number" min="0" placeholder="Earned"
                class="col-span-4 sm:col-span-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
              <input v-model.number="cat.possible" type="number" min="1" placeholder="Possible"
                class="col-span-4 sm:col-span-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
              <div class="col-span-10 sm:col-span-1 flex items-center">
                <span :class="['text-sm font-bold', gradeColor(cat.possible > 0 ? Math.round((cat.earned / cat.possible) * 1000) / 10 : null)]">
                  {{ cat.possible > 0 ? Math.round((cat.earned / cat.possible) * 1000) / 10 + '%' : '—' }}
                </span>
              </div>
              <button type="button" @click="removeCategory(cat.id)" :disabled="categories.length === 1"
                class="col-span-2 sm:col-span-1 flex items-center justify-center w-9 h-9 rounded-lg border border-slate-200 text-slate-400 hover:border-red-200 hover:text-red-500 transition-colors disabled:opacity-30 disabled:cursor-not-allowed">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between mt-4 flex-wrap gap-3">
            <button type="button" @click="addCategory" class="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
              Add category
            </button>
            <span :class="['text-xs font-bold', weightOk ? 'text-green-600' : 'text-amber-600']">
              Total weight: {{ totalWeight }}% {{ weightOk ? '✓' : '(should equal 100%)' }}
            </span>
          </div>
        </div>
      </template>

      <!-- Tab 2: Final Exam -->
      <template v-if="activeTab === 'final'">
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Current Grade (%)</label>
              <input v-model.number="currentGrade" type="number" min="0" max="100"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Final Exam Weight (%)</label>
              <input v-model.number="finalWeight" type="number" min="1" max="100"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Desired Final Grade (%)</label>
              <input v-model.number="desiredGrade" type="number" min="0" max="100"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
            </div>
          </div>

          <div v-if="neededScore !== null" :class="['rounded-2xl border p-6 text-center', finalResultColor]">
            <p class="text-5xl font-extrabold mb-2">{{ neededScore > 100 ? '> 100%' : neededScore < 0 ? '0%' : neededScore + '%' }}</p>
            <p class="text-sm font-semibold">{{ finalResultMsg }}</p>
          </div>
        </div>
      </template>

      <!-- Grade scale (always visible) -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-700 mb-3">Grade Scale Reference</h2>
        <div class="flex flex-wrap gap-2">
          <div v-for="row in gradeScale" :key="row.grade" :class="['flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold', row.color]">
            <span class="font-extrabold text-base">{{ row.grade }}</span>
            <span class="opacity-80">{{ row.range }}</span>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full essay written by experts? We deliver custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
