<script setup lang="ts">
const portal = usePortalStore()

const stats = [
  { value: '9,800+', label: 'Nursing papers delivered' },
  { value: '500+',   label: 'BSN/MSN/DNP writers' },
  { value: '4.98/5', label: 'Average rating' },
  { value: '3 hrs',  label: 'Fastest turnaround' },
]

// Three differentiating pillars
const pillars = [
  {
    icon: '✍️',
    title: 'Writing',
    desc: 'Essays, care plans, SOAP notes, capstone projects, dissertations — written from scratch by a credentialed nurse who knows the clinical context.',
    href: '/services',
  },
  {
    icon: '🖥️',
    title: 'Tutoring',
    desc: 'Online nursing class help — discussions, quizzes, assignments, and full course management so you can focus on your clinical rotations.',
    href: '/services/online-nursing-classes',
  },
  {
    icon: '🎓',
    title: 'Mentoring',
    desc: 'Nursing school admission essays, career statement reviews, and programme-specific guidance from nurses who\'ve been through the process.',
    href: '/contact',
  },
]

const services = [
  { icon: '✍️', title: 'Nursing Essays',       href: '/services/nursing-essays',         desc: 'Reflective, argumentative, and analytical essays grounded in evidence-based practice.' },
  { icon: '🩺', title: 'Care Plans',            href: '/services/care-plans',             desc: 'NANDA-I diagnoses, NIC interventions, NOC outcomes — APIE formatted.' },
  { icon: '📋', title: 'SOAP Notes',            href: '/services/soap-notes',             desc: 'Clinically accurate S-O-A-P documentation for NP and advanced practice programmes.' },
  { icon: '🎓', title: 'Capstone Projects',     href: '/services/capstone-projects',      desc: 'PICOT to final paper — BSN, MSN, and DNP capstone support.' },
  { icon: '📄', title: 'Research Papers',       href: '/services/nursing-research-papers', desc: 'Evidence-based nursing research, APA 7th, peer-reviewed sources.' },
  { icon: '🗺️', title: 'Concept Maps',          href: '/services/concept-maps',           desc: 'Pathophysiology to nursing diagnosis — clinical linkages clearly mapped.' },
]

const nursingSubjects = [
  'Med-Surgical Nursing', 'Psychiatric Nursing', 'Pediatric Nursing',
  'OB & Maternal Health', 'Critical Care / ICU', 'Community Health',
  'Pharmacology', 'Pathophysiology', 'Family Nurse Practice',
  'Nursing Informatics', 'Evidence-Based Practice', 'Health Assessment',
  'Nursing Leadership', 'Public Health Nursing', 'Geriatric Nursing',
  'Oncology Nursing', 'Emergency Nursing', 'Perioperative Care',
]

const steps = [
  { title: 'Submit your nursing brief',     desc: 'Share your assignment type, course level, deadline, and any rubric or clinical scenario details.' },
  { title: 'Matched with a nurse expert',   desc: 'We assign a writer whose clinical background fits your specific subject — not a generic writer.' },
  { title: 'Track progress & communicate',  desc: 'Message your writer directly, share files, and follow progress in your dashboard.' },
  { title: 'Download & request revisions',  desc: 'Receive your paper with a free Turnitin report. Request unlimited free revisions until satisfied.' },
]

const guarantees = [
  { icon: '🏆', title: 'Grade or money back',         desc: "If the work doesn't meet your stated requirements, we'll rewrite or refund — no questions asked." },
  { icon: '🔬', title: 'Zero AI — human nurses only', desc: 'Every paper is written by a real nurse. We provide a free AI-detection report on request.' },
  { icon: '📋', title: 'Clinically accurate content',  desc: 'NANDA, NIC, NOC, ADPIE, APA 7th — written by people who use these frameworks in practice.' },
  { icon: '🔒', title: 'Your privacy protected',       desc: 'We never share your name, order details, or school with any third party.' },
  { icon: '🔄', title: 'Unlimited free revisions',     desc: 'Within the revision window, request as many changes as you need at zero extra cost.' },
  { icon: '⚡', title: 'As fast as 3 hours',           desc: 'Need it tonight? We can deliver most nursing papers within 3 hours for urgent orders.' },
]

useSeoMeta({
  title: 'Nursing Paper Writing Service — BSN, MSN & DNP Writers | NurseMyGrade',
  description: 'Expert nursing papers written by qualified BSN, MSN, and DNP nurses. Care plans, SOAP notes, capstone projects, dissertations. From $24/page. Grade or money back.',
  ogTitle: 'NurseMyGrade — Nursing Papers Written by Real Nurses',
  ogDescription: 'SOAP notes, care plans, capstone projects, nursing essays — written by BSN/MSN/DNP experts. Grade or money back. Free Turnitin report.',
})

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ProfessionalService',
      name: 'NurseMyGrade',
      description: 'Nursing paper writing service with BSN, MSN, and DNP qualified writers.',
      url: 'https://nursemygrade.com',
      priceRange: '$24–$50 per page',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.98', reviewCount: '9800' },
    }),
  }],
})
</script>

<template>
  <!-- ─── Hero ─────────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-gradient-to-br from-brand-900 via-brand-800 to-brand-600 py-20 sm:py-28">
    <div class="section relative z-10">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: copy -->
        <div>
          <div class="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm text-white ring-1 ring-white/20">
            <span class="inline-block h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
            <span><strong>38 nursing writers</strong> online now · From <strong>$24/page</strong></span>
          </div>

          <h1 class="font-serif text-4xl font-bold leading-tight text-white sm:text-5xl">
            Nursing papers written by<br class="hidden sm:block" />
            <span class="text-brand-300">BSN, MSN &amp; DNP experts</span>
          </h1>
          <p class="mt-5 text-lg text-brand-100 leading-relaxed">
            Care plans, SOAP notes, capstone projects, nursing essays — written by nurses who know the clinical context. Not generic writers. Real nurses.
          </p>

          <div class="mt-8 flex flex-wrap gap-4">
            <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base shadow-lg">
              Place your order
            </NuxtLink>
            <NuxtLink href="/pricing" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-3.5 text-base">
              See pricing
            </NuxtLink>
          </div>

          <div class="mt-8">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: calculator -->
        <div class="lg:pl-8">
          <ClientOnly>
            <OrderCalculator />
            <template #fallback>
              <div class="h-72 animate-pulse rounded-2xl bg-white/10" />
            </template>
          </ClientOnly>
        </div>

      </div>
    </div>
    <div class="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-brand-400 opacity-20 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-teal-200 opacity-10 blur-3xl pointer-events-none" />
  </section>

  <!-- ─── Stats ─────────────────────────────────────────────────────────── -->
  <section class="border-b border-slate-100 bg-white py-10">
    <div class="section py-0">
      <div class="grid grid-cols-2 gap-6 text-center md:grid-cols-4">
        <div v-for="stat in stats" :key="stat.label">
          <div class="text-3xl font-bold text-brand-700">{{ stat.value }}</div>
          <div class="mt-1 text-sm text-slate-500">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Three Pillars ────────────────────────────────────────────────── -->
  <section class="bg-brand-50 py-20">
    <div class="section py-0">
      <div class="text-center">
        <h2 class="section-heading">Writing. Tutoring. Mentoring.</h2>
        <p class="section-sub">Three ways we help nursing students succeed — pick what fits your situation.</p>
      </div>
      <div class="mt-12 grid gap-8 md:grid-cols-3">
        <NuxtLink
          v-for="p in pillars"
          :key="p.title"
          :href="p.href"
          class="card group flex flex-col transition-shadow hover:shadow-lg hover:border-brand-300"
        >
          <span class="text-4xl">{{ p.icon }}</span>
          <h3 class="mt-4 text-xl font-bold text-brand-700 group-hover:text-brand-900 transition-colors">{{ p.title }}</h3>
          <p class="mt-3 flex-1 text-sm leading-relaxed text-slate-600">{{ p.desc }}</p>
          <span class="mt-4 text-xs font-semibold text-brand-600 group-hover:underline">Learn more →</span>
        </NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Writer Showcase ───────────────────────────────────────────────── -->
  <WriterShowcase />

  <!-- ─── Nursing Services Grid ───────────────────────────────────────── -->
  <section class="bg-slate-50">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Every nursing paper type covered</h2>
        <p class="section-sub">From first-year essays to DNP dissertations — we've got the right nurse for the job.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="svc in services"
          :key="svc.title"
          :href="svc.href"
          class="card group flex flex-col transition-shadow hover:shadow-md hover:border-brand-200"
        >
          <span class="text-3xl">{{ svc.icon }}</span>
          <h3 class="mt-4 font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">{{ svc.title }}</h3>
          <p class="mt-2 flex-1 text-sm text-slate-500 leading-relaxed">{{ svc.desc }}</p>
          <span class="mt-3 text-xs font-medium text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Order now →</span>
        </NuxtLink>
      </div>

      <!-- Nursing subjects pill cloud -->
      <div class="mt-10 flex flex-wrap justify-center gap-2">
        <span
          v-for="sub in nursingSubjects"
          :key="sub"
          class="rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
        >{{ sub }}</span>
        <span class="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-500">+30 more</span>
      </div>
      <div class="mt-10 text-center">
        <NuxtLink href="/services" class="btn-outline">View all nursing services</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── How it works ──────────────────────────────────────────────────── -->
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">How it works</h2>
        <p class="section-sub">From brief to finished nursing paper — in four simple steps.</p>
      </div>
      <ol class="mt-12 grid gap-8 md:grid-cols-4">
        <li v-for="(step, i) in steps" :key="step.title" class="flex flex-col items-center text-center">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-700 text-lg font-bold text-white shadow-md">
            {{ i + 1 }}
          </div>
          <h3 class="font-semibold text-slate-900">{{ step.title }}</h3>
          <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ step.desc }}</p>
        </li>
      </ol>
      <div class="mt-12 text-center">
        <NuxtLink to="/order" class="btn-primary">Start your order now</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Guarantees ────────────────────────────────────────────────────── -->
  <section class="bg-brand-900">
    <div class="section">
      <div class="text-center">
        <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">Our guarantees</h2>
        <p class="mt-4 text-brand-200">We put our reputation behind every nursing order.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="g in guarantees" :key="g.title" class="rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 transition-colors hover:bg-white/10">
          <span class="text-2xl">{{ g.icon }}</span>
          <h3 class="mt-3 font-semibold text-white">{{ g.title }}</h3>
          <p class="mt-2 text-sm text-brand-200 leading-relaxed">{{ g.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Testimonials ──────────────────────────────────────────────────── -->
  <TestimonialsSection />

  <!-- ─── FAQ ───────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── Final CTA ─────────────────────────────────────────────────────── -->
  <section class="bg-brand-600 py-20">
    <div class="section py-0 text-center">
      <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">
        Your deadline is waiting. Let's nurse your grade.
      </h2>
      <p class="mt-4 text-brand-100 text-lg">
        Tell us what you need. We'll match you with the right nurse expert in minutes.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base shadow-lg">
          Place your order — from $24/page
        </NuxtLink>
        <NuxtLink href="/contact" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-4 text-base">
          Talk to us first
        </NuxtLink>
      </div>
      <p class="mt-6 text-sm text-brand-200">
        24/7 support · 3-hour minimum turnaround · Free Turnitin report · Grade or money back
      </p>
    </div>
  </section>
</template>
