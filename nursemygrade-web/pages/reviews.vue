<script setup lang="ts">
import { ArrowRight, CheckCircle2, Stethoscope } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Nursing Student Reviews — 9,800+ Verified | NurseMyGrade',
  description: 'Read verified reviews from nursing students across BSN, MSN, and DNP programmes. 4.98/5 average. Care plans, SOAP notes, capstone projects, dissertations.',
  ogTitle: 'NurseMyGrade Reviews — 4.98/5 from 9,800+ Nursing Students',
  ogDescription: 'BSN, MSN, and DNP students share their experience with NurseMyGrade. Clinically accurate, nurse-written work.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/reviews' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'NurseMyGrade',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.98', reviewCount: '9800', bestRating: '5' },
    }),
  }],
})

const featured = {
  quote: "I was three weeks from my DNP capstone submission and my PICOT question still wasn't landing with my committee. The writer didn't just fix the question — she rebuilt the entire literature review framework around it, flagged gaps my advisor hadn't caught, and delivered 36 hours early. Genuine doctoral-level thinking from someone who had clearly written at this level before.",
  name: 'Amina O.',
  program: 'DNP, Family Practice',
  university: 'Rush University',
  grade: 'A',
  specialty: 'Evidence-Based Practice',
}

const levels = [
  { label: 'ADN / LPN',   color: 'bg-slate-100 text-slate-700',   count: '1,200+' },
  { label: 'BSN',         color: 'bg-brand-100 text-brand-700',   count: '4,800+' },
  { label: 'MSN / NP',    color: 'bg-teal-100 text-teal-700',     count: '2,600+' },
  { label: 'DNP / PhD',   color: 'bg-violet-100 text-violet-700', count: '1,200+' },
]

const reviews = [
  {
    name: 'Sarah K.',    program: 'BSN Year 3',         specialty: 'Med-Surgical',       grade: 'A',  date: 'May 2026',
    quote: "My Med-Surg care plan had the wrong NANDA diagnoses. My writer identified every error, rebuilt it correctly in 6 hours, and explained her reasoning. She had clearly done this for real patients."
  },
  {
    name: 'Marcus T.',   program: 'MSN, Family NP',     specialty: 'Advanced Practice',  grade: 'A+', date: 'May 2026',
    quote: "SOAP notes for NP school are a different standard than undergrad. The writer nailed the clinical reasoning, the differential, and the pharmacological plan. I genuinely learned from it."
  },
  {
    name: 'Rosa C.',     program: 'BSN Year 4',         specialty: 'Psychiatric Nursing', grade: 'A', date: 'April 2026',
    quote: "Psychiatric nursing case study, 48 hours. The therapeutic communication framework and mental status exam were textbook-accurate but written with real clinical nuance. First A I've had on a psych assignment."
  },
  {
    name: 'David M.',    program: 'ADN',                specialty: 'Fundamentals',        grade: 'A', date: 'April 2026',
    quote: "First semester, fundamentals care plan. I was completely lost on ADPIE. The writer walked through each section and her document became my reference for the rest of the semester."
  },
  {
    name: 'Tricia L.',   program: 'MSN, Leadership',    specialty: 'Nursing Management',  grade: 'A−', date: 'March 2026',
    quote: "Leadership and management essay on nurse retention strategies. Well-researched, recent evidence, and a clear policy recommendation. My professor asked if I wanted to expand it for publication."
  },
  {
    name: 'Kenji B.',    program: 'BSN, RN-to-BSN',     specialty: 'Community Health',    grade: 'A', date: 'March 2026',
    quote: "Community health assessment for a rural population. The writer included proper epidemiological framing and social determinants of health analysis. Exactly what the rubric asked for."
  },
  {
    name: 'Yvette N.',   program: 'DNP, PMHNP',         specialty: 'Psychiatric NP',      grade: 'A+', date: 'February 2026',
    quote: "Prescribing guidelines essay for my PMHNP programme. The clinical pharmacology was accurate, the evidence was current, and every APA citation was perfect. Exactly the standard I needed."
  },
  {
    name: 'Jenna H.',    program: 'BSN Year 2',         specialty: 'Maternal Health',     grade: 'A', date: 'February 2026',
    quote: "OB nursing care plan for a postpartum patient. The interventions and rationale were clinically sound and written by someone who clearly understood the postpartum physiological changes."
  },
  {
    name: 'Samuel O.',   program: 'MSN, Educator',      specialty: 'Nursing Education',   grade: 'A', date: 'January 2026',
    quote: "Curriculum development paper for my MSN Education track. The writer understood constructive alignment and Bloom's taxonomy at the graduate level. Not a Wikipedia-level summary — actual scholarly engagement."
  },
  {
    name: 'Carmen D.',   program: 'BSN Year 3',         specialty: 'Critical Care',       grade: 'A', date: 'January 2026',
    quote: "ICU patient scenario care plan. Haemodynamic monitoring, ventilator management, priority diagnoses — all correct and detailed. I used it as my study guide for clinical the following week."
  },
  {
    name: 'Fatou B.',    program: 'DNP, Capstone',      specialty: 'Evidence-Based Practice', grade: 'A', date: 'December 2025',
    quote: "My DNP project implementation chapter was structurally weak. The writer reorganised it around the Iowa Model, tightened the evidence hierarchy section, and fixed my APA formatting throughout."
  },
  {
    name: 'Luke V.',     program: 'BSN Year 4',         specialty: 'Oncology',            grade: 'A+', date: 'December 2025',
    quote: "Oncology nursing essay on palliative care transitions. Compassionate, evidence-based, and technically accurate. My clinical instructor said it was one of the best she'd seen from an undergrad."
  },
]

const specialties = [
  'Med-Surgical', 'Critical Care', 'Psychiatric Nursing', 'Maternal Health',
  'Community Health', 'Paediatric Nursing', 'Family NP', 'DNP Capstone',
  'Pharmacology', 'Pathophysiology', 'Evidence-Based Practice', 'Leadership',
]

const guarantees = [
  'Every writer holds active BSN, MSN, or DNP credentials',
  'Free Turnitin report included — zero AI, zero plagiarism',
  'Grade or money back — no questions asked',
  'Unlimited free revisions within the revision window',
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-gradient-to-br from-brand-900 to-brand-700 pb-0 pt-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="relative mx-auto max-w-5xl px-4 pb-10 text-center sm:px-6">
        <div class="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-brand-200 backdrop-blur-sm">
          <Stethoscope class="h-4 w-4" />
          Written by real nurses. Reviewed by real nurses.
        </div>
        <h1 class="text-4xl font-extrabold text-white sm:text-5xl">
          9,800+ nursing students.<br class="hidden sm:block" /> One verdict.
        </h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-brand-200">
          4.98/5 average across BSN, MSN, and DNP programmes. Here's what they said.
        </p>
        <!-- Program level breakdown -->
        <div class="mt-10 flex flex-wrap justify-center gap-3">
          <div
            v-for="l in levels"
            :key="l.label"
            class="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-center backdrop-blur-sm"
          >
            <p class="text-xl font-extrabold text-white">{{ l.count }}</p>
            <span class="mt-1 inline-block rounded-full px-2.5 py-0.5 text-xs font-bold" :class="l.color">{{ l.label }}</span>
          </div>
        </div>
      </div>
      <!-- Wave divider -->
      <svg class="block w-full" viewBox="0 0 1440 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0 40L1440 40L1440 20C1200 0 960 40 720 20C480 0 240 40 0 20L0 40Z" fill="white"/>
      </svg>
    </section>

    <!-- ── Featured review ───────────────────────────────────────────────── -->
    <section class="bg-white px-4 pt-10 pb-4 sm:px-6">
      <div class="mx-auto max-w-4xl">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-600">Featured review</p>
        <div class="relative overflow-hidden rounded-2xl border border-brand-100 bg-brand-50 p-7">
          <div class="pointer-events-none absolute right-0 top-0 h-40 w-40 rounded-full bg-brand-200 opacity-20 blur-3xl" />
          <div class="flex items-start gap-2 mb-4">
            <span
              v-for="i in 5" :key="i"
              class="inline-block h-5 w-5 rounded-full bg-amber-400"
              style="clip-path: polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%)"
            />
          </div>
          <p class="text-base leading-relaxed text-slate-800 sm:text-lg">"{{ featured.quote }}"</p>
          <div class="mt-6 flex flex-wrap items-center justify-between gap-4">
            <div>
              <p class="font-bold text-slate-900">{{ featured.name }}</p>
              <p class="text-sm text-slate-500">{{ featured.program }} · {{ featured.university }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="rounded-full bg-violet-100 px-3 py-1 text-xs font-bold text-violet-700">{{ featured.specialty }}</span>
              <span class="rounded-full bg-brand-700 px-3 py-1 text-xs font-bold text-white">Grade: {{ featured.grade }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Specialty strip ───────────────────────────────────────────────── -->
    <div class="bg-white border-y border-slate-100 py-4">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap justify-center gap-2">
          <span
            v-for="s in specialties" :key="s"
            class="rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
          >{{ s }}</span>
        </div>
      </div>
    </div>

    <!-- ── Reviews grid ───────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-12">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="r in reviews"
            :key="r.name"
            class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div class="flex items-center justify-between gap-2 mb-3">
              <span class="rounded-full bg-brand-100 px-2.5 py-1 text-[11px] font-bold text-brand-700">{{ r.program }}</span>
              <div class="flex items-center gap-0.5">
                <span
                  v-for="i in 5" :key="i"
                  class="inline-block h-3 w-3 rounded-full bg-amber-400"
                  style="clip-path: polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%)"
                />
              </div>
            </div>
            <p class="flex-1 text-sm leading-relaxed text-slate-700">"{{ r.quote }}"</p>
            <div class="mt-4 border-t border-slate-100 pt-3 flex items-end justify-between gap-2">
              <div>
                <p class="text-xs font-bold text-slate-900">{{ r.name }}</p>
                <p class="text-xs text-slate-500">{{ r.specialty }}</p>
              </div>
              <div class="text-right shrink-0 space-y-1">
                <span class="block rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600">Grade: {{ r.grade }}</span>
                <span class="block text-[11px] text-slate-400">{{ r.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Guarantees ────────────────────────────────────────────────────── -->
    <section class="border-t border-brand-100 bg-brand-50 py-10">
      <div class="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <p class="mb-5 text-xs font-bold uppercase tracking-wider text-brand-600">What every order includes</p>
        <ul class="grid gap-3 text-sm sm:grid-cols-2">
          <li
            v-for="g in guarantees" :key="g"
            class="flex items-start gap-2.5 rounded-xl border border-brand-200 bg-white px-4 py-3 text-left text-slate-700"
          >
            <CheckCircle2 class="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />
            {{ g }}
          </li>
        </ul>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-brand-700 py-14 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-extrabold text-white">Ready to work with a real nurse writer?</h2>
        <p class="mt-2 text-brand-200">From $24/page · As fast as 3 hours · Grade or money back</p>
        <NuxtLink
          to="/order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Place your first order <ArrowRight class="h-4 w-4" />
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
