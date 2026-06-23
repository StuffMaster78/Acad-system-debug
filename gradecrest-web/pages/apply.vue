<script setup lang="ts">
import {
  ArrowRight, BadgeCheck, Banknote, BookOpen, Briefcase,
  CheckCircle2, ChevronDown, Clock, GraduationCap,
  Star, Upload, Users, X,
} from '@lucide/vue'
import { markRaw } from 'vue'

const app = useAppUrl()

function selectResume(event: Event) {
  resumeFile.value = (event.target as HTMLInputElement).files?.[0] ?? null
}

function selectSample(event: Event) {
  sampleFile.value = (event.target as HTMLInputElement).files?.[0] ?? null
}

useSeoMeta({
  title: 'Become a GradeCrest Writer — Apply Today | Academic Writing Jobs',
  description: 'Join GradeCrest as a freelance academic writer. Competitive per-page rates, flexible hours, 100+ subjects. Apply with your postgraduate degree and writing sample.',
  ogTitle: 'Join the GradeCrest Writing Team',
  ogDescription: 'Earn competitive rates working from home as a freelance academic writer. Postgraduate degree required.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useSeoBase('https://gradecrest.com/apply')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Become a Writer', url: 'https://gradecrest.com/apply' },
])

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'JobPosting',
      title: 'Freelance Academic Writer',
      description: 'Write custom academic papers for university students. Flexible remote work. Postgraduate degree required.',
      hiringOrganization: { '@type': 'Organization', name: 'GradeCrest', sameAs: 'https://gradecrest.com' },
      jobLocationType: 'TELECOMMUTE',
      employmentType: 'CONTRACTOR',
      datePosted: '2024-01-01',
    }),
  }],
})

// ── Form state ────────────────────────────────────────────────────────────────

const form = reactive({
  full_name: '', email: '', phone: '', country: '',
  education_level: '', years_of_experience: 0,
  subjectInput: '', application_text: '',
})
const resumeFile  = ref<File | null>(null)
const sampleFile  = ref<File | null>(null)
const resumeInput = ref<HTMLInputElement | null>(null)
const sampleInput = ref<HTMLInputElement | null>(null)
const submitting  = ref(false)
const submitted   = ref(false)
const serverError = ref('')
const errors      = reactive<Record<string, string>>({})

function validate() {
  Object.keys(errors).forEach(k => delete (errors as Record<string, string>)[k])
  if (!form.full_name.trim())  errors.full_name = 'Required'
  if (!form.email.includes('@')) errors.email   = 'Valid email required'
  if (form.application_text.trim().length < 50) errors.application_text = 'Please write at least 50 characters'
  return Object.keys(errors).length === 0
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  serverError.value = ''
  try {
    const body = new FormData()
    Object.entries(form).forEach(([k, v]) => body.append(k, String(v)))
    form.subjectInput.split(',').map(s => s.trim()).filter(Boolean).forEach(s => body.append('subjects', s))
    if (resumeFile.value) body.append('resume', resumeFile.value)
    if (sampleFile.value) body.append('sample_work', sampleFile.value)
    const apiBase = useRuntimeConfig().public.apiBase
    await $fetch(`${apiBase}/api/v1/writer-management/applications/submit/`, { method: 'POST', body })
    submitted.value = true
  } catch (err: unknown) {
    serverError.value = (err as { data?: { detail?: string } })?.data?.detail ?? 'Submission failed. Please try again.'
  } finally {
    submitting.value = false
  }
}

// ── Page data ─────────────────────────────────────────────────────────────────

const heroStats = [
  { value: '600+',  label: 'Active writers'      },
  { value: '100+',  label: 'Subjects covered'     },
  { value: '4.9/5', label: 'Average writer rating' },
]

const perks = [
  { icon: markRaw(Banknote), title: 'Competitive rates',     desc: 'Tiered per-page rates that increase with your level and order performance.' },
  { icon: markRaw(Clock),    title: 'Fully flexible hours',  desc: 'Accept only the orders you want. Work mornings, evenings, weekends — your call.' },
  { icon: markRaw(BookOpen), title: '100+ subject areas',    desc: 'STEM, humanities, business, nursing, law — steady order flow across every discipline.' },
  { icon: markRaw(Users),    title: 'Direct client chat',    desc: 'Communicate with clients directly through the platform. No third-party go-betweens.' },
  { icon: markRaw(Banknote), title: 'Reliable payouts',      desc: 'Weekly or bi-weekly withdrawals. Multiple payout methods, no surprise deductions.' },
  { icon: markRaw(Star),     title: 'Grow your tier',        desc: 'Standard → Advanced → Expert. Higher tier means better rates and priority matching.' },
]

const requirements = [
  {
    icon: markRaw(GraduationCap),
    title: 'Postgraduate degree',
    desc: "Master's or PhD (or equivalent professional qualification). You must be able to upload your degree certificate during the onboarding process.",
  },
  {
    icon: markRaw(BadgeCheck),
    title: 'Demonstrated writing ability',
    desc: 'We review a writing sample and administer a short skills assessment. Strong grammar, clear argumentation, and correct citation style are essential.',
  },
  {
    icon: markRaw(Briefcase),
    title: 'Professionalism & reliability',
    desc: 'We look for writers who meet deadlines, communicate proactively, and maintain the quality standards that keep clients returning.',
  },
]

const steps = [
  { n: '01', title: 'Submit your application',  desc: 'Fill in the form below with your credentials, subjects, and a short introduction. Attach your CV and a writing sample.' },
  { n: '02', title: 'Editorial review',          desc: 'Our team reviews every application within 3–5 business days. We check your background, credentials, and writing quality.' },
  { n: '03', title: 'Skills assessment',         desc: 'Shortlisted applicants complete a brief grammar test and subject-knowledge quiz. No prep needed — just demonstrate what you know.' },
  { n: '04', title: 'Onboard and start earning', desc: 'Approved writers complete a short orientation, set up their payout method, and start bidding on available orders immediately.' },
]

const faqs = [
  { q: 'How much can I earn?',                   a: 'Rates depend on your tier (Standard, Advanced, Expert), the academic level of the order, and the deadline. Expert-tier writers consistently earn more per page. We share the full rate table during onboarding.' },
  { q: 'How many hours do I need to work?',       a: 'None are mandatory. You accept only the orders that fit your schedule. Some writers work full-time; others take one or two orders a week alongside other commitments.' },
  { q: 'What subjects do you need most?',         a: 'Nursing, Business/MBA, STEM fields, and Law are in consistently high demand. However, we match every order to a specialist, so strong writers in any subject are welcome.' },
  { q: 'How quickly will I hear back?',           a: 'We review every application and aim to respond within 3–5 business days. Due to application volume, we are unable to provide individual feedback on unsuccessful applications.' },
  { q: 'Can I apply from outside the UK or US?',  a: 'Yes. We work with writers globally. The only requirements are a postgraduate degree, strong English writing ability, and access to a supported payout method.' },
  { q: 'Is the work exclusively academic writing?', a: 'Yes. GradeCrest provides custom academic model papers for university-level students. If selected, you will write essays, research papers, dissertations, case studies, and similar assignments.' },
]

const openFaq = ref<number | null>(null)
function toggleFaq(i: number) { openFaq.value = openFaq.value === i ? null : i }

const formSection = ref<HTMLElement | null>(null)
function scrollToForm() { formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-forest-950 py-20 relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-4xl px-4 sm:px-6 text-center space-y-6">
        <span class="inline-flex items-center gap-1.5 rounded-full bg-gc-500/20 px-3 py-1 text-xs font-semibold text-gc-300 ring-1 ring-gc-500/30">
          Now hiring
        </span>
        <h1 class="text-4xl font-bold text-white sm:text-5xl lg:text-6xl leading-tight">
          Turn your expertise<br class="hidden sm:block" /> into income
        </h1>
        <p class="text-lg text-slate-300 leading-relaxed max-w-xl mx-auto">
          Join 600+ freelance academic writers earning competitive rates on a schedule that fits around your life. Postgraduate degree required.
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <button
            class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-6 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors"
            @click="scrollToForm"
          >
            Apply now <ArrowRight class="size-4" />
          </button>
          <NuxtLink
            to="/writers"
            class="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-6 py-3 text-sm font-semibold text-white hover:bg-white/20 transition-colors"
          >
            Meet the team
          </NuxtLink>
        </div>
        <!-- Stats bar -->
        <div class="pt-6 grid grid-cols-3 gap-4 max-w-lg mx-auto border-t border-white/10">
          <div v-for="s in heroStats" :key="s.label" class="text-center">
            <p class="text-2xl font-bold text-white">{{ s.value }}</p>
            <p class="mt-0.5 text-xs text-slate-400">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Perks -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <h2 class="text-2xl font-bold text-ink">Why writers choose GradeCrest</h2>
          <p class="mt-2 text-graphite max-w-lg mx-auto">We are built around making freelance academic writing sustainable — not just a side gig.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="p in perks" :key="p.title" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-card hover:shadow-lift transition-shadow">
            <div class="flex size-10 items-center justify-center rounded-xl bg-gc-50 mb-4">
              <component :is="p.icon" class="size-5 text-gc-600" />
            </div>
            <h3 class="text-sm font-semibold text-ink">{{ p.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ p.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Requirements -->
    <section class="bg-mist py-16">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <h2 class="text-2xl font-bold text-ink">What we look for</h2>
          <p class="mt-2 text-graphite max-w-lg mx-auto">We maintain high standards to protect our clients and our writers' reputations.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-3">
          <div v-for="r in requirements" :key="r.title" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
            <component :is="r.icon" class="size-6 text-gc-600 mb-3" />
            <h3 class="text-sm font-semibold text-ink">{{ r.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ r.desc }}</p>
          </div>
        </div>
        <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
          <p class="text-xs font-semibold uppercase tracking-widest text-graphite mb-3">Nice to have</p>
          <ul class="grid sm:grid-cols-2 gap-2">
            <li v-for="item in ['Native or near-native English speaker', 'Experience with APA, MLA, Harvard, Chicago', 'Previous academic or professional writing portfolio', 'Familiarity with Turnitin or plagiarism tools']" :key="item" class="flex items-start gap-2 text-sm text-graphite">
              <CheckCircle2 class="size-4 text-gc-400 shrink-0 mt-0.5" />
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Application process -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <h2 class="text-2xl font-bold text-ink">How the process works</h2>
          <p class="mt-2 text-graphite">From application to first order in as little as one week.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="step in steps" :key="step.n" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <span class="text-3xl font-extrabold text-slate-100 select-none leading-none">{{ step.n }}</span>
            <h3 class="mt-2 text-sm font-semibold text-ink">{{ step.title }}</h3>
            <p class="mt-1.5 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Application form -->
    <section ref="formSection" class="bg-mist py-16" id="apply-form">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <h2 class="text-2xl font-bold text-ink">Apply now</h2>
          <p class="mt-2 text-graphite">Applications reviewed within 3–5 business days. All submissions are confidential.</p>
        </div>

        <div class="rounded-2xl bg-white p-8 shadow-lift">
          <!-- Success state -->
          <div v-if="submitted" class="text-center py-8 space-y-4">
            <div class="flex size-16 items-center justify-center rounded-full bg-emerald-100 mx-auto">
              <CheckCircle2 class="size-8 text-emerald-600" />
            </div>
            <h3 class="text-xl font-bold text-ink">Application received!</h3>
            <p class="text-sm text-graphite max-w-xs mx-auto">
              Thank you. We review every application and will contact you at <strong>{{ form.email }}</strong> within 3–5 business days.
            </p>
          </div>

          <!-- Form -->
          <form v-else class="space-y-5" @submit.prevent="submit">
            <p v-if="serverError" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-3 text-sm text-rose-700">{{ serverError }}</p>

            <!-- Name + email -->
            <div class="grid sm:grid-cols-2 gap-4">
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Full name *</span>
                <input
                  v-model="form.full_name" type="text" placeholder="Your full name"
                  class="h-11 w-full rounded-xl border px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500"
                  :class="errors.full_name ? 'border-rose-400' : 'border-slate-200'"
                />
                <span v-if="errors.full_name" class="text-xs text-rose-600">{{ errors.full_name }}</span>
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Email address *</span>
                <input
                  v-model="form.email" type="email" placeholder="you@example.com"
                  class="h-11 w-full rounded-xl border px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500"
                  :class="errors.email ? 'border-rose-400' : 'border-slate-200'"
                />
                <span v-if="errors.email" class="text-xs text-rose-600">{{ errors.email }}</span>
              </label>
            </div>

            <!-- Phone + country -->
            <div class="grid sm:grid-cols-2 gap-4">
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Phone number</span>
                <input v-model="form.phone" type="tel" placeholder="+1 555 000 0000" class="h-11 w-full rounded-xl border border-slate-200 px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Country</span>
                <input v-model="form.country" type="text" placeholder="United Kingdom" class="h-11 w-full rounded-xl border border-slate-200 px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
              </label>
            </div>

            <!-- Education + experience -->
            <div class="grid sm:grid-cols-2 gap-4">
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Highest qualification</span>
                <select v-model="form.education_level" class="h-11 w-full rounded-xl border border-slate-200 bg-white px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500">
                  <option value="">— select —</option>
                  <option>Bachelor's Degree</option>
                  <option>Master's Degree</option>
                  <option>PhD / Doctorate</option>
                  <option>Professional Degree</option>
                </select>
              </label>
              <label class="block space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Years of writing experience</span>
                <input v-model.number="form.years_of_experience" type="number" min="0" max="40" class="h-11 w-full rounded-xl border border-slate-200 px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
              </label>
            </div>

            <!-- Subjects -->
            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Subjects you can cover <span class="normal-case font-normal text-slate-400">(comma-separated)</span></span>
              <input v-model="form.subjectInput" type="text" placeholder="Nursing, Business, Statistics, Psychology…" class="h-11 w-full rounded-xl border border-slate-200 px-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500" />
            </label>

            <!-- Intro -->
            <label class="block space-y-1.5">
              <span class="text-xs font-semibold uppercase tracking-widest text-graphite">Tell us about yourself *</span>
              <textarea
                v-model="form.application_text" rows="5"
                placeholder="Your background, subject specialisms, academic writing experience, and why you'd be a great fit. Minimum 50 characters."
                class="w-full rounded-xl border px-3.5 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gc-500 resize-none"
                :class="errors.application_text ? 'border-rose-400' : 'border-slate-200'"
              />
              <span v-if="errors.application_text" class="text-xs text-rose-600">{{ errors.application_text }}</span>
            </label>

            <!-- File uploads -->
            <input ref="resumeInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="selectResume" />
            <input ref="sampleInput" type="file" accept=".pdf,.doc,.docx" class="hidden" @change="selectSample" />

            <div class="grid sm:grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite block">Resume / CV</span>
                <div v-if="resumeFile" class="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-xs">
                  <CheckCircle2 class="size-3.5 text-emerald-500 shrink-0" />
                  <span class="truncate text-emerald-800 flex-1">{{ resumeFile.name }}</span>
                  <button type="button" class="ml-auto" @click="resumeFile = null"><X class="size-3.5 text-emerald-500" /></button>
                </div>
                <button v-else type="button" class="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 py-3 text-xs text-graphite hover:border-gc-400 hover:text-gc-600 transition-colors" @click="resumeInput?.click()">
                  <Upload class="size-3.5" /> Upload CV (PDF, DOC)
                </button>
              </div>
              <div class="space-y-1.5">
                <span class="text-xs font-semibold uppercase tracking-widest text-graphite block">Writing sample</span>
                <div v-if="sampleFile" class="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-xs">
                  <CheckCircle2 class="size-3.5 text-emerald-500 shrink-0" />
                  <span class="truncate text-emerald-800 flex-1">{{ sampleFile.name }}</span>
                  <button type="button" class="ml-auto" @click="sampleFile = null"><X class="size-3.5 text-emerald-500" /></button>
                </div>
                <button v-else type="button" class="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 py-3 text-xs text-graphite hover:border-gc-400 hover:text-gc-600 transition-colors" @click="sampleInput?.click()">
                  <Upload class="size-3.5" /> Upload sample (PDF, DOC)
                </button>
              </div>
            </div>

            <button
              type="submit" :disabled="submitting"
              class="w-full rounded-xl bg-gc-600 py-3.5 text-sm font-bold text-white hover:bg-gc-700 disabled:opacity-60 transition-colors flex items-center justify-center gap-2"
            >
              <span>{{ submitting ? 'Submitting…' : 'Submit application' }}</span>
              <ArrowRight v-if="!submitting" class="size-4" />
            </button>

            <p class="text-center text-xs text-slate-400">
              We review every application within 3–5 business days. Your information is kept confidential.
            </p>
          </form>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-ink text-center mb-8">Frequently asked questions</h2>
        <div class="divide-y divide-slate-200 rounded-2xl border border-slate-200 overflow-hidden">
          <div v-for="(faq, i) in faqs" :key="faq.q">
            <button
              type="button"
              class="flex w-full items-start justify-between gap-4 px-6 py-4 text-left hover:bg-mist transition-colors"
              @click="toggleFaq(i)"
            >
              <span class="text-sm font-semibold text-ink">{{ faq.q }}</span>
              <ChevronDown class="size-4 text-graphite shrink-0 mt-0.5 transition-transform" :class="openFaq === i ? 'rotate-180' : ''" />
            </button>
            <div v-show="openFaq === i" class="px-6 pb-4">
              <p class="text-sm text-graphite leading-relaxed">{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>
