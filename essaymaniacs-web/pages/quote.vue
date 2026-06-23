<script setup lang="ts">
definePageMeta({ ssr: false })

import {
  Sparkles, MessageSquare, Clock, DollarSign, FileText,
  ChevronRight, ArrowLeft, Loader2, Check,
} from '@lucide/vue'

const auth = useRpmAuthStore()

const SPECIAL_TYPES = [
  { id: 'shadow_health',  label: 'Shadow Health / iHuman', desc: 'Nursing simulation assignments', icon: 'hospital',     color: 'bg-rose-100 text-rose-600' },
  { id: 'coding_project', label: 'Coding / Programming',   desc: 'Scripts, apps, algorithms',      icon: 'terminal',     color: 'bg-slate-100 text-slate-700' },
  { id: 'nursing_sim',    label: 'Nursing Simulation',     desc: 'NCLEX-style scenario work',      icon: 'stethoscope',  color: 'bg-blue-100 text-blue-600' },
  { id: 'research_proj',  label: 'Research Project',       desc: 'Multi-part study or analysis',   icon: 'microscope',   color: 'bg-purple-100 text-purple-600' },
  { id: 'math_stats',     label: 'Maths / Statistics',     desc: 'Problem sets, SPSS, R work',     icon: 'calculator',   color: 'bg-amber-100 text-amber-600' },
  { id: 'custom_project', label: 'Other / Custom',         desc: 'Describe in the form below',     icon: 'sparkles',     color: 'bg-green-100 text-green-600' },
]

const BUDGET_RANGES = [
  { id: 'u50',    label: 'Under $50' },
  { id: '50_150', label: '$50 – $150' },
  { id: '150_300',label: '$150 – $300' },
  { id: '300_500',label: '$300 – $500' },
  { id: 'o500',   label: '$500+' },
  { id: 'unsure', label: "I'm not sure" },
]

const DEADLINES_SIMPLE = [
  { id: 'asap',    label: 'ASAP (< 24 hrs)' },
  { id: '3days',   label: '2–3 days' },
  { id: 'week',    label: '4–7 days' },
  { id: 'twoweek', label: '1–2 weeks' },
  { id: 'month',   label: '2–4 weeks' },
  { id: 'flexible',label: 'Flexible' },
]

const step      = ref(1)
const submitted = ref(false)
const submitting = ref(false)
const serverError = ref<string | null>(null)

const form = reactive({
  projectType:  SPECIAL_TYPES[0],
  title:        '',
  description:  '',
  deadline:     DEADLINES_SIMPLE[2],
  budget:       BUDGET_RANGES[1],
  level:        '',
  // Account
  firstName: '', lastName: '', email: '', password: '', agreeToTerms: false,
})

const step1Valid = computed(() => form.title.trim().length >= 3 && form.description.trim().length >= 20)
const step2Valid = computed(() => form.firstName.trim().length > 0 && form.email.includes('@') && form.password.length >= 8 && form.agreeToTerms)

function savePendingInquiry() {
  if (!import.meta.client) return
  localStorage.setItem('rpm_pending_inquiry', JSON.stringify({
    type: 'special_order',
    projectType: form.projectType.label,
    title: form.title,
    description: form.description,
    deadline: form.deadline.label,
    budget: form.budget.label,
    level: form.level,
    savedAt: new Date().toISOString(),
  }))
}

async function submit() {
  submitting.value = true; serverError.value = null
  try {
    savePendingInquiry()
    await auth.register({ email: form.email, password: form.password, first_name: form.firstName, last_name: form.lastName })
    submitted.value = true
  } catch { serverError.value = auth.error || 'Something went wrong. Please try again.' }
  finally { submitting.value = false }
}

useSeoMeta({
  title: 'Request a Custom Quote — EssayManiacs',
  description: 'Get a custom quote for special academic projects — nursing simulations, coding, Shadow Health, multi-part research, and more.',
  robots: 'noindex',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/quote' }] })
</script>

<template>
  <!-- Success -->
  <div v-if="submitted" class="grid min-h-[calc(100vh-4rem)] place-items-center px-4 py-16">
    <div class="w-full max-w-lg text-center">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
        <Check class="h-10 w-10 text-emerald-600" />
      </div>
      <h1 class="font-serif text-3xl font-bold text-slate-900">Inquiry received!</h1>
      <p class="mt-4 text-slate-600 leading-relaxed">
        We've sent a confirmation link to <strong>{{ form.email }}</strong>.
        Once you verify your email, our team will review your inquiry and send a personalised quote — usually within 2 hours.
      </p>
      <div class="mt-8 rounded-2xl border border-rose-100 bg-rose-50 p-6 text-left">
        <h2 class="mb-3 font-semibold text-rose-800">Your inquiry summary</h2>
        <dl class="space-y-1.5 text-sm">
          <div class="flex justify-between"><dt class="text-slate-500">Type</dt><dd class="font-medium">{{ form.projectType.label }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Project</dt><dd class="font-medium">{{ form.title }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Deadline</dt><dd class="font-medium">{{ form.deadline.label }}</dd></div>
          <div class="flex justify-between"><dt class="text-slate-500">Budget range</dt><dd class="font-medium">{{ form.budget.label }}</dd></div>
        </dl>
      </div>
    </div>
  </div>

  <!-- Form -->
  <div v-else class="min-h-[calc(100vh-4rem)] bg-slate-50">

    <!-- Header -->
    <div class="bg-gradient-to-br from-rose-900 to-rose-700 py-12 text-center">
      <div class="section py-0">
        <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10">
          <Sparkles class="h-7 w-7 text-white" />
        </div>
        <h1 class="font-serif text-3xl font-bold text-white sm:text-4xl">Request a Custom Quote</h1>
        <p class="mx-auto mt-3 max-w-xl text-rose-100">
          For special projects that need a tailored price — nursing simulations, coding assignments, multi-part research, and more.
        </p>
        <div class="mt-4 flex flex-wrap justify-center gap-4 text-sm text-rose-200">
          <span class="flex items-center gap-1.5"><MessageSquare class="h-4 w-4" /> Quote within 2 hours</span>
          <span class="flex items-center gap-1.5"><DollarSign class="h-4 w-4" /> No obligation</span>
          <span class="flex items-center gap-1.5"><Clock class="h-4 w-4" /> 24/7 response</span>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-2xl px-4 py-10 sm:px-6">

      <!-- Step indicator -->
      <div class="mb-8 flex items-center gap-3">
        <div v-for="(s, i) in [{ n: 1, label: 'Project details' }, { n: 2, label: 'Your account' }]" :key="s.n" class="flex items-center gap-2">
          <div class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
            :class="step === s.n ? 'bg-rose-700 text-white' : step > s.n ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-400'">
            <Check v-if="step > s.n" class="h-3.5 w-3.5" />
            <span v-else>{{ s.n }}</span>
          </div>
          <span class="text-sm" :class="step === s.n ? 'font-semibold text-slate-900' : 'text-slate-400'">{{ s.label }}</span>
          <div v-if="i === 0" class="h-px w-8 bg-slate-200" />
        </div>
      </div>

      <!-- Step 1 -->
      <div v-if="step === 1" class="space-y-6">
        <div>
          <label class="form-label">Project type</label>
          <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-3">
            <button v-for="pt in SPECIAL_TYPES" :key="pt.id" type="button"
              class="rounded-xl border p-3 text-left transition-all hover:-translate-y-0.5"
              :class="form.projectType.id === pt.id ? 'border-rose-600 bg-rose-600 text-white shadow-sm' : 'border-slate-200 bg-white hover:border-rose-300'"
              @click="form.projectType = pt"
            >
              <div class="mb-2 flex h-9 w-9 items-center justify-center rounded-lg"
                :class="form.projectType.id === pt.id ? 'bg-white/20' : pt.color.split(' ')[0]">
                <Icon :name="pt.icon" class="h-4.5 w-4.5"
                  :class="form.projectType.id === pt.id ? 'text-white' : pt.color.split(' ')[1]" />
              </div>
              <p class="text-sm font-semibold">{{ pt.label }}</p>
              <p class="text-xs mt-0.5" :class="form.projectType.id === pt.id ? 'text-rose-200' : 'text-slate-400'">{{ pt.desc }}</p>
            </button>
          </div>
        </div>

        <div>
          <label class="form-label" for="title">Project title / brief summary <span class="text-rose-500">*</span></label>
          <input id="title" v-model="form.title" type="text" class="form-input mt-2" placeholder="e.g. Shadow Health Tina Jones musculoskeletal assessment" />
        </div>

        <div>
          <label class="form-label" for="desc">Full description <span class="text-rose-500">*</span>
            <span class="ml-1 text-xs font-normal text-slate-400">include all requirements, attachments will be uploaded after account creation</span>
          </label>
          <textarea id="desc" v-model="form.description" class="form-input mt-2 min-h-[140px] resize-y"
            placeholder="Describe your project in detail: what's required, any platform specifics, grading criteria, expected output format, etc." />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="form-label">Deadline</label>
            <div class="mt-2 flex flex-col gap-2">
              <button v-for="d in DEADLINES_SIMPLE" :key="d.id" type="button"
                class="rounded-lg border px-3 py-2 text-sm font-medium transition-colors text-left"
                :class="form.deadline.id === d.id ? 'border-rose-600 bg-rose-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-rose-300'"
                @click="form.deadline = d"
              >{{ d.label }}</button>
            </div>
          </div>
          <div>
            <div>
              <label class="form-label">Budget range</label>
              <div class="mt-2 flex flex-col gap-2">
                <button v-for="b in BUDGET_RANGES" :key="b.id" type="button"
                  class="rounded-lg border px-3 py-2 text-sm font-medium transition-colors text-left"
                  :class="form.budget.id === b.id ? 'border-rose-600 bg-rose-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-rose-300'"
                  @click="form.budget = b"
                >{{ b.label }}</button>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="form-label" for="level">Academic level <span class="text-xs font-normal text-slate-400 ml-1">(optional)</span></label>
          <input id="level" v-model="form.level" type="text" class="form-input mt-2" placeholder="e.g. BSN Nursing Year 2, MBA, High School AP" />
        </div>

        <div class="flex justify-end">
          <button type="button" class="inline-flex items-center gap-2 rounded-xl bg-rose-700 px-8 py-3 font-semibold text-white shadow hover:bg-rose-800 disabled:opacity-50 transition-colors" :disabled="!step1Valid" @click="step = 2">
            Continue <ChevronRight class="h-4 w-4" />
          </button>
        </div>
      </div>

      <!-- Step 2 -->
      <div v-else class="space-y-6">
        <p class="text-slate-600">Create a free account to submit your inquiry and receive your personalised quote by email.</p>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <div class="grid grid-cols-2 gap-3">
            <div><label class="form-label">First name</label><input v-model="form.firstName" type="text" class="form-input mt-1" placeholder="Jane" /></div>
            <div><label class="form-label">Last name</label><input v-model="form.lastName" type="text" class="form-input mt-1" placeholder="Smith" /></div>
          </div>
          <div><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-input mt-1" placeholder="you@example.com" /></div>
          <div><label class="form-label">Password</label><input v-model="form.password" type="password" class="form-input mt-1" placeholder="At least 8 characters" minlength="8" /></div>
          <div v-if="serverError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{{ serverError }}</div>
          <label class="flex cursor-pointer items-start gap-3">
            <input v-model="form.agreeToTerms" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-rose-600" />
            <span class="text-xs text-slate-500 leading-relaxed">I agree to the <NuxtLink to="/terms" target="_blank" class="text-rose-600 underline">Terms</NuxtLink> and <NuxtLink to="/privacy" target="_blank" class="text-rose-600 underline">Privacy Policy</NuxtLink>.</span>
          </label>
        </div>

        <div class="flex justify-between">
          <button type="button" class="btn-outline flex items-center gap-2 px-6 py-2.5" @click="step = 1"><ArrowLeft class="h-4 w-4" /> Back</button>
          <button type="button"
            class="inline-flex items-center gap-2 rounded-xl bg-rose-700 px-8 py-3 font-semibold text-white shadow hover:bg-rose-800 disabled:opacity-50 transition-colors"
            :disabled="!step2Valid || submitting" @click="submit"
          >
            <Loader2 v-if="submitting" class="h-4 w-4 animate-spin" />
            {{ submitting ? 'Submitting…' : 'Submit inquiry & create account' }}
          </button>
        </div>
        <p class="text-center text-sm text-slate-400">Already have an account? <NuxtLink to="/login" class="text-rose-600 hover:underline font-medium">Sign in</NuxtLink></p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.form-label { @apply block text-sm font-semibold text-slate-700; }
.form-input { @apply w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 transition-colors hover:border-slate-300 focus:border-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-200; }
</style>
