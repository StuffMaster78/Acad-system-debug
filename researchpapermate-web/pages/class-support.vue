<script setup lang="ts">
definePageMeta({ ssr: false })

import {
  School, Calendar, BookOpen, GraduationCap,
  ChevronRight, ArrowLeft, Loader2, Check, Star, Shield,
} from '@lucide/vue'

const auth = useRpmAuthStore()

const COMPLEXITY = [
  { id: 'light',    label: 'Light',    desc: 'Mostly discussions, simple assignments' },
  { id: 'moderate', label: 'Moderate', desc: 'Mix of assignments, quizzes, exams' },
  { id: 'heavy',    label: 'Heavy',    desc: 'Labs, clinical hours, heavy writing load' },
]

const WEEKLY_LOAD = [
  { id: '1_2',  label: '1–2 tasks/week' },
  { id: '3_5',  label: '3–5 tasks/week' },
  { id: '6_10', label: '6–10 tasks/week' },
  { id: '10p',  label: '10+ tasks/week' },
]

const CLASS_DURATION = [
  { id: '4wk',  label: '4 weeks' },
  { id: '6wk',  label: '6 weeks' },
  { id: '8wk',  label: '8 weeks' },
  { id: '10wk', label: '10 weeks' },
  { id: '12wk', label: '12 weeks (semester)' },
  { id: 'other',label: 'Other' },
]

const BUDGET_RANGES = [
  { id: 'u300',    label: 'Under $300' },
  { id: '300_600', label: '$300 – $600' },
  { id: '600_1k',  label: '$600 – $1,000' },
  { id: '1k_2k',   label: '$1,000 – $2,000' },
  { id: 'o2k',     label: '$2,000+' },
  { id: 'unsure',  label: "I'm not sure" },
]

const step       = ref(1)
const submitted  = ref(false)
const submitting = ref(false)
const serverError = ref<string | null>(null)

const form = reactive({
  institution: '', className: '', classCode: '', classSubject: '',
  academicLevel: '', starts: '', ends: '',
  duration: CLASS_DURATION[4], complexity: COMPLEXITY[1],
  weeklyLoad: WEEKLY_LOAD[1], budget: BUDGET_RANGES[2],
  specialRequirements: '',
  // Account
  firstName: '', lastName: '', email: '', password: '', agreeToTerms: false,
})

const step1Valid = computed(() => form.className.trim().length >= 2 && form.classSubject.trim().length >= 2)
const step2Valid = computed(() => form.firstName.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && form.agreeToTerms)

function savePendingClass() {
  if (!import.meta.client) return
  localStorage.setItem('rpm_pending_class_order', JSON.stringify({
    type: 'class_order',
    institution: form.institution, className: form.className,
    classCode: form.classCode, classSubject: form.classSubject,
    academicLevel: form.academicLevel, starts: form.starts, ends: form.ends,
    duration: form.duration.label, complexity: form.complexity.label,
    weeklyLoad: form.weeklyLoad.label, budget: form.budget.label,
    specialRequirements: form.specialRequirements,
    savedAt: new Date().toISOString(),
  }))
}

async function submit() {
  submitting.value = true; serverError.value = null
  try {
    savePendingClass()
    await auth.register({ email: form.email, password: form.password, first_name: form.firstName, last_name: form.lastName })
    submitted.value = true
  } catch { serverError.value = auth.error || 'Something went wrong. Please try again.' }
  finally { submitting.value = false }
}

useSeoMeta({
  title: 'Full Class Support — ResearchPaperMate',
  description: 'We handle your entire course — all assignments, discussions, quizzes, and exams. Dedicated expert for the full semester.',
  robots: 'noindex',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/class-support' }] })
</script>

<template>
  <!-- Success -->
  <div v-if="submitted" class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-16">
    <div class="w-full max-w-lg text-center">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
        <Check class="h-10 w-10 text-emerald-600" />
      </div>
      <h1 class="font-serif text-3xl font-bold text-slate-900">Class support request received!</h1>
      <p class="mt-4 text-slate-600 leading-relaxed">
        We've sent a confirmation link to <strong>{{ form.email }}</strong>.
        Our class support team will review your course details and reach out within 4 hours with a personalised plan and pricing.
      </p>
    </div>
  </div>

  <!-- Form -->
  <div v-else class="min-h-[calc(100vh-4rem)] bg-parchment-100">

    <!-- Header -->
    <div class="bg-gradient-to-br from-green-900 to-green-700 py-12 text-center">
      <div class="section py-0">
        <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10">
          <School class="h-7 w-7 text-white" />
        </div>
        <h1 class="font-serif text-3xl font-bold text-white sm:text-4xl">Full Class Support</h1>
        <p class="mx-auto mt-3 max-w-xl text-green-100">
          One dedicated expert handles your entire course — every assignment, discussion, quiz, and exam — for the full semester.
        </p>
        <div class="mt-5 flex flex-wrap justify-center gap-6 text-sm text-green-200">
          <span class="flex items-center gap-1.5"><Star class="h-4 w-4" /> Dedicated writer, whole semester</span>
          <span class="flex items-center gap-1.5"><Shield class="h-4 w-4" /> Fully confidential</span>
          <span class="flex items-center gap-1.5"><Calendar class="h-4 w-4" /> Instalment-friendly payments</span>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-2xl px-4 py-10 sm:px-6">

      <!-- Step indicator -->
      <div class="mb-8 flex items-center gap-3">
        <div v-for="(s, i) in [{ n: 1, label: 'Class details' }, { n: 2, label: 'Your account' }]" :key="s.n" class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
            :class="step === s.n ? 'bg-green-700 text-white' : step > s.n ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'">
            <Check v-if="step > s.n" class="h-3.5 w-3.5" />
            <span v-else>{{ s.n }}</span>
          </div>
          <span class="text-sm" :class="step === s.n ? 'font-semibold text-slate-900' : 'text-slate-400'">{{ s.label }}</span>
          <div v-if="i === 0" class="h-px w-8 bg-slate-200" />
        </div>
      </div>

      <!-- Step 1 -->
      <div v-if="step === 1" class="space-y-5">

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="form-label">Institution name <span class="text-xs font-normal text-slate-400 ml-1">optional</span></label>
            <input v-model="form.institution" type="text" class="form-input mt-1.5" placeholder="e.g. University of Florida" />
          </div>
          <div>
            <label class="form-label">Academic level</label>
            <input v-model="form.academicLevel" type="text" class="form-input mt-1.5" placeholder="e.g. BSN Year 2, MBA" />
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="form-label">Class / course name <span class="text-rose-500">*</span></label>
            <input v-model="form.className" type="text" class="form-input mt-1.5" placeholder="e.g. Pathophysiology" />
          </div>
          <div>
            <label class="form-label">Course code <span class="text-xs font-normal text-slate-400 ml-1">optional</span></label>
            <input v-model="form.classCode" type="text" class="form-input mt-1.5" placeholder="e.g. NUR 3210" />
          </div>
        </div>

        <div>
          <label class="form-label">Subject area <span class="text-rose-500">*</span></label>
          <input v-model="form.classSubject" type="text" class="form-input mt-1.5" placeholder="e.g. Nursing, Business Management, Criminal Justice" />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="form-label"><Calendar class="inline h-3.5 w-3.5 mr-1" />Start date</label>
            <input v-model="form.starts" type="date" class="form-input mt-1.5" />
          </div>
          <div>
            <label class="form-label"><Calendar class="inline h-3.5 w-3.5 mr-1" />End date</label>
            <input v-model="form.ends" type="date" class="form-input mt-1.5" />
          </div>
        </div>

        <div>
          <label class="form-label">Duration (if no fixed dates)</label>
          <div class="mt-2 flex flex-wrap gap-2">
            <button v-for="d in CLASS_DURATION" :key="d.id" type="button"
              class="rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="form.duration.id === d.id ? 'border-green-700 bg-green-700 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-green-300'"
              @click="form.duration = d"
            >{{ d.label }}</button>
          </div>
        </div>

        <div>
          <label class="form-label">Workload complexity</label>
          <div class="mt-2 grid grid-cols-3 gap-3">
            <button v-for="c in COMPLEXITY" :key="c.id" type="button"
              class="rounded-xl border p-3 text-left transition-all"
              :class="form.complexity.id === c.id ? 'border-green-700 bg-green-700 text-white ring-1 ring-green-700' : 'border-slate-200 bg-white hover:border-green-300'"
              @click="form.complexity = c"
            >
              <p class="text-sm font-semibold">{{ c.label }}</p>
              <p class="mt-0.5 text-xs" :class="form.complexity.id === c.id ? 'text-green-200' : 'text-slate-400'">{{ c.desc }}</p>
            </button>
          </div>
        </div>

        <div>
          <label class="form-label">Estimated weekly tasks</label>
          <div class="mt-2 flex flex-wrap gap-2">
            <button v-for="w in WEEKLY_LOAD" :key="w.id" type="button"
              class="rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="form.weeklyLoad.id === w.id ? 'border-green-700 bg-green-700 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-green-300'"
              @click="form.weeklyLoad = w"
            >{{ w.label }}</button>
          </div>
        </div>

        <div>
          <label class="form-label">Budget range</label>
          <div class="mt-2 flex flex-wrap gap-2">
            <button v-for="b in BUDGET_RANGES" :key="b.id" type="button"
              class="rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="form.budget.id === b.id ? 'border-green-700 bg-green-700 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-green-300'"
              @click="form.budget = b"
            >{{ b.label }}</button>
          </div>
        </div>

        <div>
          <label class="form-label">Special requirements <span class="text-xs font-normal text-slate-400 ml-1">optional</span></label>
          <textarea v-model="form.specialRequirements" class="form-input mt-1.5 min-h-[100px] resize-y"
            placeholder="Specific platforms (Blackboard, Canvas), login details process, grading rubrics, anything else we should know…" />
        </div>

        <div class="flex justify-end">
          <button type="button"
            class="inline-flex items-center gap-2 rounded-xl bg-green-700 px-8 py-3 font-semibold text-white shadow hover:bg-green-800 disabled:opacity-50 transition-colors"
            :disabled="!step1Valid" @click="step = 2"
          >
            Continue <ChevronRight class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- Step 2 -->
      <div v-else class="space-y-6">
        <p class="text-slate-600">Create a free account to submit your class support request. We'll send you a full proposal and pricing within 4 hours.</p>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div><label class="form-label">First name</label><input v-model="form.firstName" type="text" class="form-input mt-1" placeholder="Jane" /></div>
            <div><label class="form-label">Last name</label><input v-model="form.lastName" type="text" class="form-input mt-1" placeholder="Smith" /></div>
          </div>
          <div><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-input mt-1" placeholder="you@example.com" /></div>
          <div><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-input mt-1" placeholder="At least 8 characters" minlength="8" /></div>
          <div v-if="serverError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ serverError }}</div>
          <label class="flex cursor-pointer items-start gap-3">
            <input v-model="form.agreeToTerms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-green-600" />
            <span class="text-xs text-slate-500 leading-relaxed">I agree to the <NuxtLink to="/terms" target="_blank" class="text-green-700 underline">Terms</NuxtLink> and <NuxtLink to="/privacy" target="_blank" class="text-green-700 underline">Privacy Policy</NuxtLink>.</span>
          </label>
        </div>

        <div class="flex justify-between">
          <button type="button" class="btn-outline flex items-center gap-2 px-6 py-2.5" @click="step = 1"><ArrowLeft class="h-4 w-4" /> Back</button>
          <button type="button"
            class="inline-flex items-center gap-2 rounded-xl bg-green-700 px-8 py-3 font-semibold text-white shadow hover:bg-green-800 disabled:opacity-50 transition-colors"
            :disabled="!step2Valid || submitting" @click="submit"
          >
            <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
            {{ submitting ? 'Submitting…' : 'Submit request & create account' }}
          </button>
        </div>
        <p class="text-center text-sm text-slate-400">Already have an account? <NuxtLink to="/login" class="text-green-700 hover:underline font-medium">Sign in</NuxtLink></p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.form-label { @apply block text-sm font-semibold text-slate-700; }
.form-input { @apply w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-200; }
</style>
