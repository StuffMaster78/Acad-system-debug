<script setup lang="ts">
const app = useAppUrl()

const heroStats = [
  { value: '9,800+', label: 'Nursing papers delivered' },
  { value: '500+',   label: 'BSN/MSN/DNP writers' },
  { value: '4.98/5', label: 'Average rating' },
  { value: '3 hrs',  label: 'Fastest turnaround' },
]

const vettingSteps = [
  {
    step: '01',
    title: 'Nursing licence & degree check',
    desc: 'Every applicant submits their nursing licence, degree certificate, and transcript. BSN is the minimum — unverified credentials are an automatic rejection.',
  },
  {
    step: '02',
    title: 'Clinical knowledge assessment',
    desc: 'A written test covering NANDA-I diagnoses, ADPIE, pharmacology, and clinical documentation. Only nurses with active or recent clinical experience pass.',
  },
  {
    step: '03',
    title: 'Sample nursing paper review',
    desc: 'Applicants submit an original care plan or SOAP note. Our senior editors check for clinical accuracy, NANDA alignment, and APA 7th citation.',
  },
  {
    step: '04',
    title: 'Supervised trial orders',
    desc: 'New writers complete their first 5 orders under editorial oversight. Only those who maintain clinical accuracy and client satisfaction stay on.',
  },
]

const values = [
  {
    icon: 'stethoscope',
    bg: 'bg-brand-100',
    fg: 'text-brand-600',
    title: 'Real nurses, real expertise',
    desc: 'Every writer holds an active nursing qualification. BSN is the floor — MSN and DNP writers handle graduate and doctoral work.',
  },
  {
    icon: 'users',
    bg: 'bg-amber-100',
    fg: 'text-amber-600',
    title: 'Academic integrity',
    desc: 'We provide model and reference papers for study. Every order includes an academic-use acknowledgement and a legal-use disclosure.',
  },
  {
    icon: 'lock',
    bg: 'bg-green-100',
    fg: 'text-green-600',
    title: 'Privacy by design',
    desc: "Your name, email, school, and order details are never sold or shared. We store only what's needed to fulfil your order.",
  },
  {
    icon: 'message-square',
    bg: 'bg-purple-100',
    fg: 'text-purple-600',
    title: 'Real human support',
    desc: 'Every query reaches a real person, 7 days a week. No bots, no scripted replies — just knowledgeable, direct support.',
  },
]

const milestones = [
  { year: '2020', label: 'Founded with 15 BSN-qualified nurse writers focused exclusively on nursing coursework' },
  { year: '2022', label: 'Crossed 1,000 completed nursing papers with a 4.95/5 average client rating' },
  { year: '2023', label: 'Added MSN and DNP writer tiers; launched Shadow Health and iHuman simulation help' },
  { year: '2024', label: 'Grew to 500+ nurse writers; launched full online class management service' },
  { year: '2025', label: '9,800+ nursing papers delivered; AI-zero guarantee and DNP capstone tier introduced' },
]

useSeoMeta({
  title: 'About NurseMyGrade — Nursing Papers Written by Real Nurses',
  description: 'NurseMyGrade is staffed entirely by BSN, MSN, and DNP nurses. Learn how we vet our writers, what we stand for, and why nursing students trust us.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/about' }],
})
</script>

<template>
  <div>
    <!-- Hero with stat overlay -->
    <section class="relative bg-gradient-to-br from-brand-900 to-brand-700 pb-0 pt-20">
      <div class="section py-0 text-center">
        <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-300">About us</p>
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">
          Nursing papers written<br class="hidden sm:block" /> by real nurses
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-lg text-brand-100 leading-relaxed">
          Every writer on our platform holds at minimum a BSN and active clinical experience.
          No generalists. No AI. Just nurses who understand your coursework because they've lived it.
        </p>
      </div>

      <!-- Stats bar -->
      <div class="mt-16 border-t border-white/10">
        <div class="section py-0">
          <div class="grid grid-cols-2 gap-0 md:grid-cols-4">
            <div
              v-for="(stat, i) in heroStats"
              :key="stat.label"
              class="border-r border-white/10 py-6 text-center last:border-r-0"
              :class="i % 2 === 0 ? 'border-r border-white/10' : ''"
            >
              <div class="text-3xl font-bold text-white">{{ stat.value }}</div>
              <div class="mt-1 text-sm text-brand-200">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mission -->
    <section class="bg-white">
      <div class="section">
        <div class="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600">Our mission</p>
            <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
              Nursing school is hard enough without fighting your assignments too
            </h2>
            <p class="mt-5 text-slate-600 leading-relaxed text-lg">
              NurseMyGrade was built by nurses for nursing students. Balancing theory, clinical
              rotations, simulation labs, and coursework is genuinely brutal — and generic writing
              services staffed by general academics cannot help you with NANDA diagnoses, ADPIE
              care plans, or Shadow Health cases.
            </p>
            <p class="mt-4 text-slate-600 leading-relaxed">
              We built a platform where every writer is a credentialed nurse — and where every paper
              is written by someone who's documented real patient care, not just read about it.
            </p>
            <NuxtLink to="/order" class="btn-primary mt-8 inline-flex">
              Place your first order
            </NuxtLink>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="v in values" :key="v.title" class="card">
              <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl" :class="v.bg">
                <Icon :name="v.icon" class="h-5 w-5" :class="v.fg" />
              </div>
              <h3 class="font-semibold text-slate-900">{{ v.title }}</h3>
              <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ v.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How we vet writers -->
    <section class="bg-slate-50">
      <div class="section">
        <div class="mx-auto max-w-3xl text-center">
          <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600">Writer vetting</p>
          <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
            Every writer is a verified, practising nurse
          </h2>
          <p class="section-sub">
            We reject over 95% of applicants. The nurses who make it through write papers that your
            clinical instructors can't fault.
          </p>
        </div>
        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="step in vettingSteps" :key="step.step" class="card relative">
            <div class="mb-4 font-mono text-4xl font-bold text-brand-100">{{ step.step }}</div>
            <h3 class="font-semibold text-slate-900">{{ step.title }}</h3>
            <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Milestones timeline -->
    <section class="bg-white">
      <div class="section">
        <div class="mx-auto max-w-3xl">
          <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-brand-600 text-center">Our story</p>
          <h2 class="font-serif text-3xl font-bold text-slate-900 text-center sm:text-4xl">
            Built by nurses, growing with every cohort
          </h2>
          <div class="mt-12 space-y-0">
            <div
              v-for="(m, i) in milestones"
              :key="m.year"
              class="relative flex gap-6 pb-10 last:pb-0"
            >
              <div class="flex flex-col items-center">
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white shadow-md">
                  {{ m.year.slice(2) }}'
                </div>
                <div v-if="i < milestones.length - 1" class="mt-2 h-full w-0.5 bg-brand-100" />
              </div>
              <div class="pt-1.5 pb-2">
                <p class="text-sm font-bold text-brand-700">{{ m.year }}</p>
                <p class="mt-1 text-slate-700 leading-relaxed">{{ m.label }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Commitments -->
    <section class="bg-brand-50 border-y border-brand-100">
      <div class="section">
        <div class="grid gap-6 sm:grid-cols-3 text-center">
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100">
              <Icon name="check-circle-2" class="h-6 w-6 text-green-600" />
            </div>
            <h3 class="font-semibold text-slate-900">Clinically accurate, original work</h3>
            <p class="mt-1 text-sm text-slate-500">Written from scratch by a nurse in your subject area. Plagiarism report included on every order.</p>
          </div>
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100">
              <Icon name="bot" class="h-6 w-6 text-blue-600" />
            </div>
            <h3 class="font-semibold text-slate-900">Zero AI — nurse-written only</h3>
            <p class="mt-1 text-sm text-slate-500">All work is 100% written by a real nurse. AI-detection report available on request, free of charge.</p>
          </div>
          <div>
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-100">
              <Icon name="lock" class="h-6 w-6 text-brand-600" />
            </div>
            <h3 class="font-semibold text-slate-900">Private by default</h3>
            <p class="mt-1 text-sm text-slate-500">Your identity, school, and order details are never disclosed. Payment handled by a regulated third party.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-700 py-20 text-center">
      <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">Ready to work with a real nurse writer?</h2>
      <p class="mt-4 text-brand-200 text-lg">
        9,800+ nursing students have trusted us with their coursework. Your paper is next.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <NuxtLink
          to="/order"
          class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base shadow-lg"
        >
          Place your first order — from $24/page
        </NuxtLink>
        <NuxtLink
          to="/contact"
          class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-4 text-base"
        >
          Talk to us first
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
