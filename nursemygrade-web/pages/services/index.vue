<script setup lang="ts">
const services = useCmsServiceList()
const { getBySlug } = useServices()

const simulations = [
  {
    slug: 'shadow-health',
    icon: 'monitor-play',
    name: 'Shadow Health DCEs',
    tagline: 'Tina Jones, Brian Foster, Danny Rivera & all patients',
    desc: 'Digital Clinical Experiences completed accurately by nurses who use Shadow Health every day — history, physical exam, assessment, education, and reflection sections all covered.',
    badges: ['Tina Jones', 'Brian Foster', 'Danny Rivera', 'All patients'],
    price: 35,
  },
  {
    slug: 'ihuman-patients',
    icon: 'activity',
    name: 'iHuman Virtual Patients',
    tagline: 'Clinical reasoning & differential diagnosis',
    desc: 'Full iHuman case completion — patient history, physical exam, ranked differential diagnoses with rationale, and evidence-based treatment plans written by practicing nurses.',
    badges: ['History & Physical', 'Differentials', 'Clinical reasoning', 'Treatment plan'],
    price: 35,
  },
]

const nursingAreas = [
  { area: 'Core Nursing',           subjects: ['Med-Surgical Nursing', 'Fundamentals of Nursing', 'Pathophysiology', 'Pharmacology', 'Health Assessment', 'Nursing Theory'] },
  { area: 'Advanced Practice',      subjects: ['Family Nurse Practice', 'Adult-Gero NP', 'Psychiatric-Mental Health NP', 'Pediatric NP', 'Women\'s Health NP', 'CRNA'] },
  { area: 'Speciality Areas',       subjects: ['Critical Care / ICU', 'Emergency Nursing', 'Perioperative Care', 'Oncology Nursing', 'Cardiac Nursing', 'Neonatal / NICU'] },
  { area: 'Community & Leadership', subjects: ['Community Health', 'Public Health Nursing', 'Nursing Leadership', 'Nursing Informatics', 'Geriatric Nursing', 'Case Management'] },
]

const usps = [
  { icon: 'stethoscope',  title: 'Nurses writing for nurses',     desc: 'Every writer holds at minimum a BSN with active clinical experience. You\'re not getting generic academic writers — you\'re getting nurses.' },
  { icon: 'shield-check', title: 'Free Turnitin report',           desc: 'Every paper is checked for plagiarism before delivery. A free Turnitin-style report is included with every order.' },
  { icon: 'zap',          title: 'As fast as 3 hours',             desc: 'Urgent deadline? We can deliver most nursing papers — care plans, essays, SOAP notes — in as little as 3 hours.' },
  { icon: 'trophy',       title: 'Grade or money back',            desc: 'If the work doesn\'t meet your stated requirements, we\'ll rewrite or refund. No questions, no delays.' },
  { icon: 'bot',          title: 'Zero AI — 100% human-written',   desc: 'Every word is written by a qualified nurse. We provide a free AI-detection report on request.' },
  { icon: 'refresh-cw',  title: 'Unlimited free revisions',       desc: 'Within the revision window, request as many revisions as you need — all free, all handled by your original writer.' },
]

useSeoMeta({
  title: 'Nursing Writing Services — Care Plans, SOAP Notes, Capstone & More | NurseMyGrade',
  description: 'Expert nursing paper writing by BSN, MSN, and DNP nurses. Care plans, SOAP notes, capstone projects, Shadow Health DCEs, iHuman cases, essays, dissertations. From $24/page.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://nursemygrade.com/services' }] })

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Nursing Writing Services',
      itemListElement: services.value.map((s, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        name: s.title,
        url: `https://nursemygrade.com/services/${s.slug}`,
      })),
    }),
  }],
})
</script>

<template>
  <div>
    <!-- ── Hero ──────────────────────────────────────────────────────── -->
    <section class="bg-gradient-to-br from-brand-900 via-brand-800 to-brand-600 py-20 text-center">
      <div class="section py-0">
        <div class="mx-auto max-w-3xl">
          <span class="inline-block rounded-full bg-white/10 px-4 py-1.5 text-sm font-semibold text-brand-200 ring-1 ring-white/20 mb-6">
            10 nursing services · Shadow Health · iHuman
          </span>
          <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">
            Every nursing paper type,<br class="hidden sm:block" /> covered by real nurses
          </h1>
          <p class="mx-auto mt-5 max-w-2xl text-lg text-brand-100 leading-relaxed">
            From first-year care plans to DNP dissertations — written by BSN, MSN, and DNP nurses who know the clinical context, not generic academic writers.
          </p>
          <div class="mt-8 flex flex-wrap justify-center gap-4">
            <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base shadow-lg">
              Place an order — from $24/page
            </NuxtLink>
            <NuxtLink to="/pricing" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-3.5 text-base">
              See pricing
            </NuxtLink>
          </div>
          <ul class="mt-6 flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-brand-200">
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Grade or money back</li>
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> Free Turnitin report</li>
            <li class="flex items-center gap-1.5"><span class="text-green-400">✓</span> 3-hour minimum turnaround</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ── Scrollable service cards ──────────────────────────────────── -->
    <section class="py-16 bg-white" id="paper-types">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-8 flex items-end justify-between gap-4">
          <div>
            <h2 class="section-heading">Nursing paper types we handle</h2>
            <p class="mt-2 text-slate-500">Each service has a dedicated team of nurses with matching credentials.</p>
          </div>
          <NuxtLink href="/order" class="hidden shrink-0 text-sm font-semibold text-brand-600 hover:underline sm:block">
            Place order →
          </NuxtLink>
        </div>

        <!-- Horizontal scroll on mobile / grid on lg -->
        <div class="-mx-4 sm:-mx-6 lg:mx-0">
          <!-- Mobile + tablet: horizontal scroll with snap -->
          <div class="flex gap-5 overflow-x-auto scroll-smooth snap-x snap-mandatory px-4 pb-4 sm:px-6 lg:hidden"
               style="scrollbar-width: none;">
            <NuxtLink
              v-for="s in services"
              :key="s.slug"
              :href="`/services/${s.slug}`"
              class="group snap-start w-72 shrink-0 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition-shadow hover:shadow-md hover:border-brand-200 flex flex-col"
            >
              <div class="mb-4 flex items-center gap-3">
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
                  <Icon :name="s.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
                </div>
                <h3 class="font-semibold text-slate-900 group-hover:text-brand-700 transition-colors leading-tight">
                  {{ s.navLabel }}
                </h3>
              </div>
              <p v-if="s.heroSub" class="flex-1 text-sm text-slate-500 leading-relaxed line-clamp-3">{{ s.heroSub }}</p>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <span class="text-sm font-bold text-brand-700">From ${{ s.priceFrom }}/page</span>
                <span class="text-xs font-medium text-brand-600 group-hover:underline">Details →</span>
              </div>
            </NuxtLink>
          </div>

          <!-- Desktop: 3-col grid -->
          <div class="hidden lg:grid grid-cols-3 gap-6">
            <NuxtLink
              v-for="s in services"
              :key="s.slug"
              :href="`/services/${s.slug}`"
              class="group rounded-2xl border border-slate-100 bg-white p-6 shadow-sm transition-shadow hover:shadow-md hover:border-brand-200 flex flex-col"
            >
              <div class="mb-4 flex items-center gap-3">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
                  <Icon :name="s.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
                </div>
                <h3 class="text-lg font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">
                  {{ s.navLabel }}
                </h3>
              </div>
              <p v-if="s.heroSub" class="flex-1 text-sm text-slate-600 leading-relaxed">{{ s.heroSub }}</p>
              <ul v-if="getBySlug(s.slug)?.includes?.length" class="mt-4 space-y-1.5">
                <li v-for="b in getBySlug(s.slug)!.includes.slice(0, 3)" :key="b"
                    class="flex items-start gap-2 text-sm text-slate-500">
                  <Icon name="check" class="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-500" />
                  {{ b }}
                </li>
              </ul>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
                <span class="text-sm font-bold text-brand-700">From ${{ s.priceFrom }}/page</span>
                <span class="text-xs font-medium text-brand-600 group-hover:underline">Learn more →</span>
              </div>
            </NuxtLink>
          </div>
        </div>

        <!-- Scroll hint for mobile -->
        <p class="mt-4 text-center text-xs text-slate-400 lg:hidden">← Scroll to see all services →</p>
      </div>
    </section>

    <!-- ── Clinical Simulations (Shadow Health + iHuman) ──────────────── -->
    <section class="bg-brand-50 py-16" id="simulations">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-10 text-center">
          <span class="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-700 mb-4">
            Clinical Simulations
          </span>
          <h2 class="section-heading">Shadow Health &amp; iHuman help</h2>
          <p class="section-sub mx-auto max-w-2xl">
            Virtual patient platforms require real clinical reasoning. Our nurses have completed hundreds of DCEs and iHuman cases — we know exactly what your rubric expects.
          </p>
        </div>

        <div class="grid gap-8 md:grid-cols-2">
          <NuxtLink
            v-for="sim in simulations"
            :key="sim.slug"
            :href="`/services/${sim.slug}`"
            class="group relative overflow-hidden rounded-2xl border border-brand-200 bg-white p-7 shadow-sm transition-shadow hover:shadow-lg hover:border-brand-400"
          >
            <!-- Accent bar -->
            <div class="absolute left-0 top-0 h-1 w-full bg-gradient-to-r from-brand-600 to-brand-400 rounded-t-2xl" />

            <div class="flex items-start gap-4">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-100 group-hover:bg-brand-600 transition-colors">
                <Icon :name="sim.icon" class="h-6 w-6 text-brand-600 group-hover:text-white transition-colors" />
              </div>
              <div class="min-w-0">
                <h3 class="text-lg font-bold text-slate-900 group-hover:text-brand-700 transition-colors">{{ sim.name }}</h3>
                <p class="text-sm font-medium text-brand-600">{{ sim.tagline }}</p>
              </div>
            </div>

            <p class="mt-4 text-sm leading-relaxed text-slate-600">{{ sim.desc }}</p>

            <div class="mt-5 flex flex-wrap gap-2">
              <span
                v-for="badge in sim.badges"
                :key="badge"
                class="rounded-full bg-brand-50 border border-brand-100 px-3 py-1 text-xs font-medium text-brand-700"
              >{{ badge }}</span>
            </div>

            <div class="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
              <span class="text-base font-bold text-brand-700">From ${{ sim.price }}</span>
              <span class="flex items-center gap-1 text-sm font-semibold text-brand-600 group-hover:underline">
                Get help <Icon name="arrow-right" class="h-4 w-4" />
              </span>
            </div>
          </NuxtLink>
        </div>

        <div class="mt-8 rounded-2xl bg-brand-900 p-6 text-center">
          <p class="text-base font-semibold text-white">Using a different simulation platform?</p>
          <p class="mt-1 text-sm text-brand-300">We also help with ATI, Kaplan, Lippincott, and other nursing simulation platforms. Contact us with your brief.</p>
          <NuxtLink to="/contact" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-2.5 text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors">
            Ask about your platform
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── Nursing subjects ───────────────────────────────────────────── -->
    <section class="bg-white py-16" id="subjects">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="section-heading">50+ nursing subjects covered</h2>
          <p class="section-sub">Writers hired for clinical expertise, not just writing ability. Every writer has worked in their area.</p>
        </div>
        <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="group in nursingAreas" :key="group.area">
            <div class="mb-4 flex items-center gap-2">
              <div class="h-1 w-6 rounded-full bg-brand-600" />
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">{{ group.area }}</h3>
            </div>
            <ul class="space-y-2">
              <li v-for="sub in group.subjects" :key="sub"
                class="flex items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700 hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700 transition-colors cursor-default">
                <Icon name="check" class="h-3 w-3 shrink-0 text-brand-500" />
                {{ sub }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Why NurseMyGrade ───────────────────────────────────────────── -->
    <section class="bg-slate-50 py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="section-heading">Why NurseMyGrade?</h2>
          <p class="section-sub">Built specifically for nursing students — by people who've been through nursing school.</p>
        </div>
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="usp in usps" :key="usp.title" class="flex gap-4">
            <div class="mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-100">
              <Icon :name="usp.icon" class="h-5 w-5 text-brand-600" />
            </div>
            <div>
              <h3 class="font-semibold text-slate-900">{{ usp.title }}</h3>
              <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ usp.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Calculator ─────────────────────────────────────────────────── -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <h2 class="section-heading text-center">Get your instant quote</h2>
        <p class="section-sub text-center">Pick your level and deadline — see your nursing paper price in seconds.</p>
        <div class="mt-10">
          <ClientOnly>
            <OrderCalculator />
            <template #fallback><div class="h-72 animate-pulse rounded-2xl bg-slate-100" /></template>
          </ClientOnly>
        </div>
      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────── -->
    <section class="bg-brand-700 py-16 text-center">
      <div class="mx-auto max-w-2xl px-4">
        <h2 class="font-serif text-3xl font-bold text-white">Not sure what you need?</h2>
        <p class="mt-4 text-brand-200 text-lg">Describe your assignment and we'll match you with the right nursing expert in minutes.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base shadow-lg">
            Start your order — from $24/page
          </NuxtLink>
          <NuxtLink to="/contact" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-4 text-base">
            Ask us first
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
