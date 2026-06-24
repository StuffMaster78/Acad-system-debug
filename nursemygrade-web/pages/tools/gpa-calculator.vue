<script setup lang="ts">
useSeoMeta({
  title: 'GPA Calculator — Free College GPA Calculator',
  description: 'Calculate your semester GPA and cumulative GPA on a 4.0 scale. Add courses, credits, and letter grades for an instant result. No sign-up required.',
})

interface Course {
  id: number
  name: string
  credits: number
  grade: string
}

const GRADE_POINTS: Record<string, number> = {
  'A+': 4.0, 'A': 4.0, 'A-': 3.7,
  'B+': 3.3, 'B': 3.0, 'B-': 2.7,
  'C+': 2.3, 'C': 2.0, 'C-': 1.7,
  'D+': 1.3, 'D': 1.0, 'D-': 0.7,
  'F': 0.0,
}

const GRADES = Object.keys(GRADE_POINTS)

let nextId = 5
const courses = ref<Course[]>([
  { id: 1, name: '', credits: 3, grade: 'A' },
  { id: 2, name: '', credits: 3, grade: 'B+' },
  { id: 3, name: '', credits: 4, grade: 'A-' },
  { id: 4, name: '', credits: 3, grade: 'B' },
])

function addCourse() {
  courses.value.push({ id: nextId++, name: '', credits: 3, grade: 'B' })
}
function removeCourse(id: number) {
  if (courses.value.length > 1) courses.value = courses.value.filter(c => c.id !== id)
}

const semesterGPA = computed(() => {
  const validCourses = courses.value.filter(c => c.credits > 0 && c.grade in GRADE_POINTS)
  const totalCredits = validCourses.reduce((s, c) => s + c.credits, 0)
  if (totalCredits === 0) return null
  const totalPoints = validCourses.reduce((s, c) => s + c.credits * GRADE_POINTS[c.grade], 0)
  return Math.round((totalPoints / totalCredits) * 100) / 100
})

const gpaColor = computed(() => {
  if (semesterGPA.value === null) return ''
  if (semesterGPA.value >= 3.5) return 'text-green-600'
  if (semesterGPA.value >= 2.5) return 'text-amber-600'
  return 'text-red-600'
})

const gpaBgColor = computed(() => {
  if (semesterGPA.value === null) return 'bg-slate-50 border-slate-200'
  if (semesterGPA.value >= 3.5) return 'bg-green-50 border-green-200'
  if (semesterGPA.value >= 2.5) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
})

const semesterCredits = computed(() =>
  courses.value.filter(c => c.credits > 0 && c.grade in GRADE_POINTS).reduce((s, c) => s + c.credits, 0)
)

// Cumulative section
const showCumulative = ref(false)
const prevGPA = ref(3.0)
const prevCredits = ref(30)

const cumulativeGPA = computed(() => {
  if (semesterGPA.value === null || semesterCredits.value === 0) return null
  const prevPoints = prevGPA.value * prevCredits.value
  const semPoints = semesterGPA.value * semesterCredits.value
  const totalCred = prevCredits.value + semesterCredits.value
  if (totalCred === 0) return null
  return Math.round(((prevPoints + semPoints) / totalCred) * 100) / 100
})

const gpaInterpretation = [
  { range: '4.00 – 3.70', standing: 'Summa Cum Laude', grade: 'A range', color: 'text-green-700 bg-green-50' },
  { range: '3.69 – 3.30', standing: 'Magna Cum Laude', grade: 'B+ range', color: 'text-green-600 bg-green-50' },
  { range: '3.29 – 3.00', standing: 'Cum Laude', grade: 'B range', color: 'text-blue-700 bg-blue-50' },
  { range: '2.99 – 2.00', standing: 'Satisfactory', grade: 'C range', color: 'text-amber-700 bg-amber-50' },
  { range: '< 2.00', standing: 'Academic Probation Risk', grade: 'Below C', color: 'text-red-700 bg-red-50' },
]
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">GPA Calculator</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">GPA Calculator</h1>
      <p class="text-slate-500 text-sm">Add your courses, credits, and grades to calculate your semester and cumulative GPA.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Semester GPA display -->
      <div :class="['rounded-2xl border shadow-sm p-6 text-center transition-colors', gpaBgColor]">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1">Semester GPA</p>
        <p :class="['text-6xl font-extrabold transition-colors', gpaColor]">
          {{ semesterGPA !== null ? semesterGPA.toFixed(2) : '—' }}
        </p>
        <p class="text-xs text-slate-400 mt-1">out of 4.00 · {{ semesterCredits }} credit{{ semesterCredits !== 1 ? 's' : '' }}</p>
      </div>

      <!-- Course rows -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Current Semester Courses</h2>

        <div class="space-y-3">
          <!-- Header -->
          <div class="hidden sm:grid grid-cols-12 gap-3 px-1">
            <span class="col-span-5 text-xs font-semibold text-slate-400 uppercase">Course Name</span>
            <span class="col-span-3 text-xs font-semibold text-slate-400 uppercase">Credits</span>
            <span class="col-span-3 text-xs font-semibold text-slate-400 uppercase">Grade</span>
            <span class="col-span-1" />
          </div>

          <div v-for="course in courses" :key="course.id" class="grid grid-cols-12 gap-3 items-center">
            <input
              v-model="course.name"
              type="text"
              placeholder="Course name (optional)"
              class="col-span-12 sm:col-span-5 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
            <input
              v-model.number="course.credits"
              type="number"
              min="1"
              max="6"
              class="col-span-4 sm:col-span-3 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
            <select
              v-model="course.grade"
              class="col-span-6 sm:col-span-3 rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            >
              <option v-for="g in GRADES" :key="g" :value="g">{{ g }} ({{ GRADE_POINTS[g].toFixed(1) }})</option>
            </select>
            <button
              type="button"
              @click="removeCourse(course.id)"
              :disabled="courses.length === 1"
              class="col-span-2 sm:col-span-1 flex items-center justify-center w-9 h-9 rounded-lg border border-slate-200 text-slate-400 hover:border-red-200 hover:text-red-500 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>

        <button type="button" @click="addCourse" class="mt-4 flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:border-brand-400 hover:text-brand-600 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
          Add course
        </button>
      </div>

      <!-- Cumulative GPA -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 overflow-hidden">
        <button
          type="button"
          @click="showCumulative = !showCumulative"
          class="w-full flex items-center justify-between px-6 py-4 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <span>Cumulative GPA (optional)</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-400 transition-transform" :class="{ 'rotate-180': showCumulative }" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5"/></svg>
        </button>
        <div v-if="showCumulative" class="px-6 pb-6 border-t border-slate-100 pt-5 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Previous Cumulative GPA</label>
              <input v-model.number="prevGPA" type="number" min="0" max="4" step="0.01"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Previous Total Credits</label>
              <input v-model.number="prevCredits" type="number" min="0"
                class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none" />
            </div>
          </div>
          <div v-if="cumulativeGPA !== null" class="rounded-xl bg-brand-50 border border-brand-100 p-4 text-center">
            <p class="text-xs text-slate-500 mb-1">New Cumulative GPA</p>
            <p class="text-4xl font-extrabold text-brand-600">{{ cumulativeGPA.toFixed(2) }}</p>
            <p class="text-xs text-slate-400 mt-1">over {{ prevCredits + semesterCredits }} total credits</p>
          </div>
        </div>
      </div>

      <!-- GPA interpretation table -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-700 mb-4">GPA Standing Reference</h2>
        <div class="space-y-2">
          <div
            v-for="row in gpaInterpretation"
            :key="row.range"
            :class="['flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm', row.color]"
          >
            <span class="font-bold w-24 flex-shrink-0">{{ row.range }}</span>
            <span class="font-semibold flex-1">{{ row.standing }}</span>
            <span class="text-xs opacity-70">{{ row.grade }}</span>
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
