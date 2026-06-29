<script setup lang="ts">
import { markRaw } from 'vue'
import { PenLine, Monitor, GraduationCap, ClipboardList, FileText, Hospital, Target, Microscope, Globe, Trophy, Bot, Stethoscope, Lock, RefreshCw, Zap } from '@lucide/vue'
import { STATIC_SUBJECTS } from '~/composables/useOrderForm'
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const app = useAppUrl()

// Fetch home_seo_body from TenantHomePage — editable in Wagtail admin
const _homeConfig = useRuntimeConfig()
const { data: _homeCms } = useFetch<{ items: { home_seo_body: unknown[] }[] }>(
  '/api/v2/pages/',
  {
    key: 'nmg-home-seo-body',
    baseURL: String(_homeConfig.public.apiBase || ''),
    query: { type: 'cms_core.TenantHomePage', fields: 'home_seo_body', limit: 1 },
    default: () => ({ items: [] }),
  },
)
const homeSeoBlocks = computed(
  () => (_homeCms.value?.items?.[0]?.home_seo_body ?? []) as { type: string; id: string; value: unknown }[]
)

const SCROLL_SUBJECTS = STATIC_SUBJECTS.filter(s => s.category !== 'Other')
const row1 = SCROLL_SUBJECTS.slice(0, Math.ceil(SCROLL_SUBJECTS.length / 2))
const row2 = SCROLL_SUBJECTS.slice(Math.ceil(SCROLL_SUBJECTS.length / 2))

useSeoMeta({
  title: 'Nursing Paper Writing Service — BSN, MSN & DNP Writers | NurseMyGrade',
  description: 'Expert nursing papers written by qualified BSN, MSN, and DNP nurses. Care plans, SOAP notes, capstone projects, dissertations. From $24/page. Grade or money back.',
  ogTitle: 'NurseMyGrade — Nursing Papers Written by Real Nurses',
  ogDescription: 'SOAP notes, care plans, capstone projects, nursing essays — written by BSN/MSN/DNP experts. Grade or money back. Free Turnitin report.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': 'https://nursemygrade.com/#org',
        name: 'NurseMyGrade',
        url: 'https://nursemygrade.com',
        logo: 'https://nursemygrade.com/favicon.svg',
        contactPoint: { '@type': 'ContactPoint', contactType: 'customer support', availableLanguage: 'English' },
        sameAs: ['https://www.trustpilot.com/review/nursemygrade.com'],
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': 'https://nursemygrade.com/#website',
        url: 'https://nursemygrade.com',
        name: 'NurseMyGrade',
        description: 'Nursing paper writing service by BSN, MSN and DNP specialists.',
        publisher: { '@id': 'https://nursemygrade.com/#org' },
        potentialAction: {
          '@type': 'SearchAction',
          target: { '@type': 'EntryPoint', urlTemplate: 'https://nursemygrade.com/services?q={search_term_string}' },
          'query-input': 'required name=search_term_string',
        },
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'ProfessionalService',
        '@id': 'https://nursemygrade.com/#service',
        name: 'NurseMyGrade',
        description: 'Nursing paper writing service by BSN, MSN and DNP specialists.',
        url: 'https://nursemygrade.com',
        priceRange: '$24–$60 per page',
        aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.98', reviewCount: '9800' },
      }),
    },
  ],
})

const stats = [
  { value: '9,800+',  label: 'Nursing papers delivered',  note: 'By credentialed nurses' },
  { value: '500+',    label: 'BSN/MSN/DNP writers',        note: 'Clinically verified' },
  { value: '4.98/5',  label: 'Average rating',             note: 'Highest in class' },
  { value: '3 hrs',   label: 'Fastest turnaround',         note: 'For urgent orders' },
]

const pillars = [
  {
    icon: markRaw(PenLine),
    title: 'Nursing Writing',
    headline: "Written by nurses who've done it.",
    body: 'Essays, care plans, SOAP notes, PICOT papers, capstone projects, dissertations — written from scratch by a credentialed nurse who knows the clinical context, the NANDA diagnoses, and what your faculty expects.',
    href: '/services',
  },
  {
    icon: markRaw(Monitor),
    title: 'Online Class Help',
    headline: 'We handle the coursework. You handle clinicals.',
    body: 'Discussions, quizzes, assignments, and full course management for online nursing programmes. Handled by BSN/MSN specialists who know the curriculum.',
    href: '/nursing-class-help-online',
  },
  {
    icon: markRaw(GraduationCap),
    title: 'Mentoring',
    headline: 'Into nursing school. Into your career.',
    body: 'Nursing school admission essays, career statement reviews, and programme-specific guidance from nurses who have navigated the process themselves.',
    href: '/contact',
  },
]

const services = [
  { icon: markRaw(ClipboardList), title: 'Care Plans',        href: '/nursing-care-plan-writing-services',      badge: 'Most requested', desc: 'NANDA-I diagnoses, NIC interventions, NOC outcomes — ADPIE formatted and clinically grounded.' },
  { icon: markRaw(FileText),      title: 'SOAP Notes',        href: '/nursing-soap-note-writing-help',          badge: null,             desc: 'Accurate S-O-A-P documentation for NP and advanced practice programmes.' },
  { icon: markRaw(Hospital),      title: 'Nursing Essays',    href: '/online-nursing-essays-help',              badge: null,             desc: 'Reflective, argumentative, and EBP essays grounded in current nursing science.' },
  { icon: markRaw(Target),        title: 'Capstone Projects', href: '/nursing-capstone-project-writing-service', badge: 'Full support',   desc: 'PICOT to final paper — BSN, MSN, and DNP capstone support from start to submission.' },
  { icon: markRaw(Microscope),    title: 'Research Papers',   href: '/best-online-nursing-research-paper-service', badge: null,          desc: 'Evidence-based nursing research, APA 7th, peer-reviewed nursing journals.' },
  { icon: markRaw(Globe),         title: 'Concept Maps',      href: '/concept-map-writing-services',            badge: null,             desc: 'Pathophysiology to nursing diagnosis — clinical linkages clearly mapped.' },
]

const nursingAreas = [
  'Med-Surgical', 'Psychiatric Nursing', 'Pediatric Nursing', 'OB & Maternal Health',
  'Critical Care / ICU', 'Community Health', 'Pharmacology', 'Pathophysiology',
  'Family Nurse Practice', 'Nursing Informatics', 'Evidence-Based Practice',
  'Health Assessment', 'Nursing Leadership', 'Geriatric Nursing', 'Oncology',
  'Emergency Nursing', 'Public Health', 'Perioperative Care',
]

const steps = [
  { n: '01', title: 'Submit your nursing brief',    desc: 'Assignment type, course level, deadline, rubric, clinical scenario — the more detail, the better the match.' },
  { n: '02', title: 'Matched with your nurse',      desc: 'Your order goes to a writer whose clinical background fits your subject — not a random academic.' },
  { n: '03', title: 'Communicate directly',         desc: 'Message your writer, share additional files, and track progress. Direct access, no ticket queue.' },
  { n: '04', title: 'Download + free revisions',    desc: 'Receive your paper with a free Turnitin report. Unlimited free revisions until you are satisfied.' },
]

const guarantees = [
  { icon: markRaw(Trophy),      title: 'Grade or money back',           desc: "If the work doesn't meet your stated requirements, we'll rewrite or refund — no questions asked." },
  { icon: markRaw(Bot),         title: 'Zero AI — human nurses only',   desc: 'Every paper is written by a real nurse. We provide a free AI-detection report on request.' },
  { icon: markRaw(Stethoscope), title: 'Clinically accurate content',   desc: 'NANDA, NIC, NOC, ADPIE, APA 7th — written by practitioners who use these frameworks in their work.' },
  { icon: markRaw(Lock),        title: 'Your privacy protected',        desc: 'Your name, order details, and school are never shared with any third party.' },
  { icon: markRaw(RefreshCw),   title: 'Unlimited free revisions',      desc: 'Within the revision window, as many changes as you need at zero extra cost.' },
  { icon: markRaw(Zap),         title: 'As fast as 3 hours',            desc: 'Need it tonight? We can deliver most nursing papers within 3 hours for urgent orders.' },
]

const testimonials = [
  {
    initials: 'SK', name: 'Sarah K.', program: 'BSN, 3rd year', grade: 'A',
    quote: "My Med-Surg care plan was wrong from the start — wrong NANDA diagnoses, wrong interventions. My writer rebuilt the whole thing in 6 hours. She clearly knew what she was doing.",
  },
  {
    initials: 'MT', name: 'Marcus T.', program: 'MSN, Family NP', grade: 'A+',
    quote: "SOAP notes for NP school are a completely different level. The writer nailed the clinical reasoning and pharmacological plan. I learned from reading it back.",
  },
  {
    initials: 'AO', name: 'Amina O.', program: 'DNP capstone', grade: 'A',
    quote: "I was stuck on my PICOT question for three weeks. They turned it into a full literature review framework in 48 hours. Genuine DNP-level thinking.",
  },
]

const nurses = [
  {
    initials: 'KO', name: 'Dr. K. Osei', credential: 'DNP, APRN · Family NP',
    specialty: 'SOAP Notes · Capstone Projects · PICOT',
    notes: 1240, rating: 4.98,
    soapLine: 'A: Ineffective tissue perfusion r/t altered cardiac output AEB BP 158/94, bilateral ankle oedema — ADPIE documented.',
  },
  {
    initials: 'AW', name: 'Amara W.', credential: 'MSN, RN · Critical Care',
    specialty: 'Care Plans · Nursing Essays · EBP',
    notes: 870, rating: 5.0,
    soapLine: 'P: Lisinopril 10mg PO daily · Monitor BP q4h · Na⁺ restriction < 2g/day · Educate re: fluid retention signs.',
  },
  {
    initials: 'JM', name: 'Janet M.', credential: 'BSN, RN · Pediatric Nursing',
    specialty: 'Nursing Essays · Concept Maps · Reflections',
    notes: 560, rating: 4.96,
    soapLine: 'S: Patient c/o chest tightness onset yesterday evening, mild dyspnoea on exertion, denies fever or productive cough.',
  },
]
</script>

<template>
  <!-- ─── Hero ─────────────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-brand-900 py-20 sm:py-28">
    <div class="pointer-events-none absolute inset-0 bg-[repeating-linear-gradient(45deg,rgba(255,255,255,0.03),rgba(255,255,255,0.03)_1px,transparent_1px,transparent_18px)]" />
    <div class="pointer-events-none absolute -top-32 right-0 h-[500px] w-[500px] rounded-full bg-brand-600 opacity-15 blur-[130px]" />
    <div class="pointer-events-none absolute bottom-0 -left-20 h-64 w-64 rounded-full bg-teal-400 opacity-10 blur-3xl" />

    <div class="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: clinical positioning -->
        <div class="max-w-xl">
          <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-brand-200 backdrop-blur-sm">
            <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-green-400" />
            <span>38 nursing writers online now · from <strong class="text-white">$24/page</strong></span>
          </div>

          <h1 class="text-4xl font-bold leading-tight text-white sm:text-5xl lg:text-[3.25rem]">
            Nursing papers written<br class="hidden sm:block" />
            <span class="text-brand-300">by real nurses.</span>
          </h1>

          <p class="mt-6 text-lg leading-relaxed text-brand-200">
            Care plans, SOAP notes, PICOT papers, capstone projects, nursing essays — written by BSN, MSN, and DNP specialists who know the clinical context. Not generic writers. Real nurses.
          </p>

          <div class="mt-4 flex flex-wrap gap-3 text-sm text-brand-300">
            <span class="flex items-center gap-1.5"><span class="text-brand-400">🩺</span> NANDA/ADPIE accurate</span>
            <span class="text-brand-700">·</span>
            <span>✦ From $24/page</span>
            <span class="text-brand-700">·</span>
            <span>✦ Grade or money back</span>
          </div>

          <div class="mt-7 flex flex-wrap gap-3">
            <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
              Place my order
              <svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </a>
            <a href="/pricing" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-7 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
              See pricing
            </a>
          </div>

          <div class="mt-7 border-t border-white/10 pt-5">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: nurse credential cards with SOAP snippets -->
        <div class="space-y-3">
          <p class="text-xs font-bold uppercase tracking-widest text-brand-400 mb-4">Some of our nursing writers</p>
          <div
            v-for="n in nurses" :key="n.name"
            class="group rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm hover:bg-white/10 transition-all"
          >
            <div class="flex items-start gap-4">
              <!-- Credential avatar -->
              <div class="relative shrink-0">
                <div class="flex size-12 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white">
                  {{ n.initials }}
                </div>
                <div class="absolute -bottom-1 -right-1 flex h-5 min-w-[20px] items-center justify-center rounded-full bg-teal-400 px-1 text-[8px] font-extrabold leading-none text-brand-900 shadow">
                  RN
                </div>
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-2">
                  <p class="text-sm font-bold text-white">{{ n.name }}</p>
                  <div class="flex items-center gap-1 text-xs">
                    <span class="text-amber-400">★</span>
                    <span class="font-semibold text-white">{{ n.rating }}</span>
                    <span class="text-brand-300">· {{ n.notes.toLocaleString() }} notes</span>
                  </div>
                </div>
                <p class="text-xs text-brand-300 font-medium mt-0.5">{{ n.credential }}</p>
                <p class="text-xs text-brand-400 mt-1">{{ n.specialty }}</p>
                <!-- SOAP note snippet -->
                <div class="mt-2.5 rounded-lg border border-white/10 bg-black/20 px-3 py-2">
                  <p class="mb-1 text-[10px] font-bold uppercase tracking-wider text-brand-300">SOAP excerpt</p>
                  <p class="font-mono text-xs leading-relaxed text-brand-100">{{ n.soapLine }}</p>
                </div>
              </div>
            </div>
          </div>

          <a href="/writers" class="block text-center text-xs font-semibold text-brand-300 hover:text-white transition-colors pt-1">
            View all 500+ nursing writers →
          </a>
        </div>

      </div>
    </div>
  </section>

  <!-- ─── Quick order bar ─────────────────────────────────────────────────── -->
  <ClientOnly>
    <QuickOrderBar />
  </ClientOnly>

  <!-- ─── Stats ─────────────────────────────────────────────────────────────── -->
  <section class="border-y border-slate-100 bg-white">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-2 divide-x divide-y divide-slate-100 md:grid-cols-4 md:divide-y-0">
        <div v-for="stat in stats" :key="stat.label" class="flex flex-col items-center py-8 px-6 text-center">
          <span class="text-3xl font-extrabold tabular-nums text-brand-700">{{ stat.value }}</span>
          <span class="mt-1 text-sm font-semibold text-slate-800">{{ stat.label }}</span>
          <span class="mt-0.5 text-xs text-slate-400">{{ stat.note }}</span>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Subjects scroll strip ───────────────────────────────────────────── -->
  <section class="overflow-hidden border-t border-brand-800 bg-brand-900 py-10">
    <div class="mb-6 flex items-center justify-center gap-4 px-4">
      <div class="h-px max-w-[60px] flex-1 bg-brand-700" />
      <p class="text-center text-[11px] font-bold uppercase tracking-widest text-brand-400">
        {{ SCROLL_SUBJECTS.length }}+ nursing subjects · one expert service
      </p>
      <div class="h-px max-w-[60px] flex-1 bg-brand-700" />
    </div>

    <!-- Row 1 — scrolls left -->
    <div class="relative flex overflow-hidden mb-3">
      <div class="flex shrink-0 gap-3 whitespace-nowrap animate-scroll pr-3">
        <a
          v-for="(subj, i) in [...row1, ...row1]"
          :key="`r1-${i}-${subj.id}`"
          :href="`/order?type=writing&subject=${encodeURIComponent(subj.label)}`"
          class="inline-flex items-center gap-1.5 rounded-full border border-brand-700 bg-brand-800/60 px-4 py-2 text-sm font-medium text-brand-200 backdrop-blur-sm transition-all hover:border-teal-400 hover:bg-teal-400/10 hover:text-teal-200"
        >
          <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-teal-400/70" />
          {{ subj.label }}
        </a>
      </div>
    </div>

    <!-- Row 2 — scrolls right -->
    <div class="relative flex overflow-hidden">
      <div class="flex shrink-0 gap-3 whitespace-nowrap animate-scroll-reverse pr-3">
        <a
          v-for="(subj, i) in [...row2, ...row2]"
          :key="`r2-${i}-${subj.id}`"
          :href="`/order?type=writing&subject=${encodeURIComponent(subj.label)}`"
          class="inline-flex items-center gap-1.5 rounded-full border border-brand-700 bg-brand-800/60 px-4 py-2 text-sm font-medium text-brand-200 backdrop-blur-sm transition-all hover:border-amber-400 hover:bg-amber-400/10 hover:text-amber-200"
        >
          <span class="h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400/70" />
          {{ subj.label }}
        </a>
      </div>
    </div>

    <div class="mt-6 text-center">
      <NuxtLink to="/services" class="text-sm font-semibold text-brand-300 transition-colors hover:text-teal-300">
        Browse all nursing services →
      </NuxtLink>
    </div>
  </section>

  <!-- ─── Three pillars ─────────────────────────────────────────────────────── -->
  <section class="bg-brand-50 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-14 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Everything you need to pass</p>
        <h2 class="text-3xl font-bold text-slate-900 sm:text-4xl">Nursing school is hard enough.<br class="hidden sm:block" /> Your assignments don't have to be.</h2>
      </div>
      <div class="grid gap-8 md:grid-cols-3">
        <a
          v-for="p in pillars" :key="p.title" :href="p.href"
          class="group relative overflow-hidden rounded-2xl border border-brand-100 bg-white p-8 shadow-sm transition-shadow hover:shadow-md"
        >
          <div class="mb-4"><component :is="p.icon" class="h-10 w-10 text-brand-700" /></div>
          <p class="text-xs font-bold uppercase tracking-widest text-brand-600">{{ p.title }}</p>
          <h3 class="mt-2 text-lg font-bold text-slate-900">{{ p.headline }}</h3>
          <p class="mt-3 text-sm leading-relaxed text-slate-500">{{ p.body }}</p>
          <span class="mt-5 block text-xs font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Learn more →</span>
          <div class="pointer-events-none absolute -bottom-10 -right-10 h-32 w-32 rounded-full bg-brand-50 transition-transform group-hover:scale-150" />
        </a>
      </div>
    </div>
  </section>

  <!-- ─── Writer showcase ───────────────────────────────────────────────────── -->
  <WriterShowcase />

  <!-- ─── Services ─────────────────────────────────────────────────────────── -->
  <section class="bg-white py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 flex items-end justify-between">
        <div>
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-brand-600">Every nursing assignment type</p>
          <h2 class="text-3xl font-bold text-slate-900">What we write.</h2>
        </div>
        <a href="/services" class="hidden text-sm font-semibold text-brand-600 hover:underline sm:block">All services →</a>
      </div>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <a
          v-for="svc in services" :key="svc.title" :href="svc.href"
          class="group relative flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md"
        >
          <div v-if="svc.badge" class="absolute right-4 top-4 rounded-full bg-brand-100 px-2.5 py-0.5 text-[11px] font-bold text-brand-700">{{ svc.badge }}</div>
          <div class="mb-3"><component :is="svc.icon" class="h-7 w-7 text-brand-700" /></div>
          <h3 class="font-bold text-slate-900 transition-colors group-hover:text-brand-700">{{ svc.title }}</h3>
          <p class="mt-2 flex-1 text-sm leading-relaxed text-slate-500">{{ svc.desc }}</p>
          <span class="mt-4 text-xs font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Learn more →</span>
        </a>
      </div>
      <div class="mt-10 flex flex-wrap gap-2">
        <span v-for="area in nursingAreas" :key="area" class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700 transition-colors hover:bg-brand-100">{{ area }}</span>
        <span class="rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs text-slate-400">+ all specialisms</span>
      </div>
    </div>
  </section>

  <!-- ─── How it works ──────────────────────────────────────────────────────── -->
  <section class="bg-slate-50 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-14 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Simple process</p>
        <h2 class="text-3xl font-bold text-slate-900 sm:text-4xl">Submit your brief. Receive your paper. Pass.</h2>
      </div>
      <div class="hidden md:block">
        <div class="relative grid grid-cols-4">
          <div class="absolute top-7 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-brand-300 via-brand-500 to-brand-300" />
          <div v-for="step in steps" :key="step.n" class="flex flex-col items-center px-4 text-center">
            <div class="relative z-10 mb-6 flex size-14 items-center justify-center rounded-full border-4 border-brand-100 bg-white shadow-md">
              <span class="text-lg font-extrabold text-brand-700">{{ step.n }}</span>
            </div>
            <h3 class="text-sm font-bold text-slate-900">{{ step.title }}</h3>
            <p class="mt-2 text-xs leading-relaxed text-slate-500">{{ step.desc }}</p>
          </div>
        </div>
      </div>
      <div class="space-y-4 md:hidden">
        <div v-for="step in steps" :key="step.n" class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-5">
          <div class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-sm font-extrabold text-brand-700">{{ step.n }}</div>
          <div>
            <h3 class="text-sm font-bold text-slate-900">{{ step.title }}</h3>
            <p class="mt-1 text-sm text-slate-500">{{ step.desc }}</p>
          </div>
        </div>
      </div>
      <div class="mt-12 text-center">
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-brand-700 px-8 py-3.5 text-sm font-bold text-white shadow transition-colors hover:bg-brand-800">
          Start my order now
        </a>
      </div>
    </div>
  </section>

  <!-- ─── Guarantees ────────────────────────────────────────────────────────── -->
  <section class="bg-brand-900 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Every nursing order</p>
        <h2 class="text-3xl font-bold text-white sm:text-4xl">What every paper includes.</h2>
        <p class="mt-3 text-brand-300">Not extras. Standard.</p>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="g in guarantees" :key="g.title" class="flex gap-4 rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 transition-colors hover:bg-white/10">
          <component :is="g.icon" class="h-7 w-7 text-brand-700" />
          <div>
            <h3 class="font-semibold text-white">{{ g.title }}</h3>
            <p class="mt-1.5 text-sm leading-relaxed text-brand-200">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Testimonials ──────────────────────────────────────────────────────── -->
  <section class="bg-white py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-12 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Clinical results</p>
        <h2 class="text-3xl font-bold text-slate-900">Nurses writing for nursing students.</h2>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <div v-for="t in testimonials" :key="t.name" class="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-7">
          <div class="absolute right-5 top-5 flex size-12 items-center justify-center rounded-full border-2 border-brand-300 bg-brand-50 text-xl font-extrabold text-brand-700">{{ t.grade }}</div>
          <p class="text-xs font-bold text-brand-600">{{ t.program }}</p>
          <blockquote class="mt-3 pr-14 text-sm italic leading-relaxed text-slate-700">"{{ t.quote }}"</blockquote>
          <div class="mt-5 flex items-center gap-3 border-t border-slate-200 pt-4">
            <div class="flex size-8 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">{{ t.initials }}</div>
            <p class="text-xs font-bold text-slate-800">{{ t.name }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── SEO content — mirrors the live NMG long-form authority section ─── -->
  <section class="bg-slate-50 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

      <!-- Heading -->
      <div class="mx-auto max-w-3xl text-center mb-14">
        <span class="inline-block rounded-full bg-brand-100 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-700 mb-4">Trusted by nursing students</span>
        <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
          The Leading Nursing Paper Writing Service
        </h2>
        <p class="mt-5 text-lg text-slate-600 leading-relaxed">
          NurseMyGrade is staffed exclusively by credentialed nurses — BSN, MSN, and DNP — who write the same papers their clients are submitting. 4.98★ across 9,800+ nursing orders.
        </p>
      </div>

      <!-- Why choose us — 3-col grid -->
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-16">
        <div v-for="r in [
          { icon: 'stethoscope',   title: 'Qualified nursing writers',        desc: 'Every writer holds at minimum a BSN with verified clinical experience. MSN and DNP writers available for advanced work.' },
          { icon: 'shield-check',  title: '100% plagiarism-free',             desc: 'Every paper is scanned with Turnitin before delivery. Similarity kept below 5%. Report included at no extra charge.' },
          { icon: 'refresh-cw',   title: 'Unlimited free revisions',          desc: 'Within the revision window, request as many changes as needed — always handled by your original nurse writer.' },
          { icon: 'message-circle', title: 'Direct writer communication',     desc: 'Message your assigned nurse through the order portal. Most writers respond within an hour during active work.' },
          { icon: 'book-open',    title: 'APA, AMA, and Harvard formatting',  desc: 'All major citation styles applied correctly. Reference lists, in-text citations, headings, and running heads — all formatted to spec.' },
          { icon: 'zap',          title: 'As fast as 3 hours',                desc: 'Urgent deadline? Most care plans, SOAP notes, and essays can be delivered in as little as 3 hours.' },
          { icon: 'globe',        title: 'Country-specific references',        desc: 'UK, Australian, Canadian, and US nursing guidelines applied correctly depending on your programme\'s region.' },
          { icon: 'trophy',       title: 'Grade or money back',               desc: 'If the completed paper does not meet your stated requirements after revisions, you qualify for a full refund. No conditions.' },
          { icon: 'lock',         title: '100% confidential',                 desc: 'Your identity, order details, and any login credentials shared for platform-based assignments are never stored or shared.' },
        ]" :key="r.title"
          class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100">
            <Icon :name="r.icon" class="h-5 w-5 text-brand-600" />
          </div>
          <div>
            <h3 class="font-semibold text-slate-900">{{ r.title }}</h3>
            <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ r.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Horizontal scroll — service category highlights -->
      <div class="mb-2">
        <h3 class="font-serif text-xl font-bold text-slate-900 mb-1">Every nursing assignment type, covered</h3>
        <p class="text-sm text-slate-500 mb-6">Scroll to explore what we write — each category is handled by nurses with matching clinical experience.</p>
      </div>
      <div class="flex gap-5 overflow-x-auto scroll-smooth snap-x snap-mandatory pb-4" style="scrollbar-width: none;">
        <div v-for="cat in [
          {
            icon: 'clipboard-list', label: 'Care Plans & SOAP Notes',
            items: ['NANDA-I diagnoses with PES format', 'NIC interventions and NOC outcomes', 'ADPIE-structured clinical reasoning', 'SOAP notes for NP and advanced practice'],
          },
          {
            icon: 'graduation-cap', label: 'Capstone & Research',
            items: ['BSN, MSN, and DNP capstone projects', 'PICOT question development', 'Evidence-based practice papers', 'Systematic literature reviews'],
          },
          {
            icon: 'monitor',        label: 'Clinical Simulations',
            items: ['Shadow Health DCE completion', 'iHuman virtual patient cases', 'Tina Jones, Brian Foster & all patients', 'Differential diagnosis and clinical reasoning'],
          },
          {
            icon: 'book-open',      label: 'Online Class Help',
            items: ['Full course or individual module support', 'Weekly discussion posts and responses', 'Quizzes and take-home tests', 'Assignment submission management'],
          },
          {
            icon: 'search',         label: 'Research & Evidence',
            items: ['APA 7th nursing research papers', 'Annotated bibliographies', 'CINAHL and PubMed literature search', 'Quantitative and qualitative designs'],
          },
          {
            icon: 'file-text',      label: 'Advanced Degrees',
            items: ['MSN scholarly papers', 'DNP practice-focused projects', 'PhD nursing research', 'Thesis chapters on demand'],
          },
        ]" :key="cat.label"
          class="snap-start w-72 shrink-0 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100">
              <Icon :name="cat.icon" class="h-5 w-5 text-brand-600" />
            </div>
            <h4 class="font-semibold text-slate-900 leading-tight">{{ cat.label }}</h4>
          </div>
          <ul class="space-y-2">
            <li v-for="item in cat.items" :key="item" class="flex items-start gap-2 text-sm text-slate-500">
              <Icon name="check" class="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-500" />
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
      <p class="mt-3 text-center text-xs text-slate-400 sm:hidden">← Scroll to explore →</p>

    </div>
  </section>

  <!-- ─── Wagtail-editable long-form SEO content ────────────────────────── -->
  <section v-if="homeSeoBlocks.length" class="bg-white py-20">
    <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
      <div class="prose prose-slate prose-lg max-w-none
                  prose-headings:font-serif prose-headings:font-bold prose-headings:text-slate-900
                  prose-a:text-brand-600 prose-a:underline
                  prose-strong:text-slate-900">
        <BlockRenderer :blocks="homeSeoBlocks" link-context="service" />
      </div>
    </div>
  </section>

  <!-- ─── FAQ ─────────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── Final CTA ───────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-gradient-to-br from-brand-800 to-brand-900 py-20">
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />
    <div class="pointer-events-none absolute -top-20 right-0 h-64 w-64 rounded-full bg-brand-500 opacity-15 blur-[80px]" />
    <div class="relative z-10 mx-auto max-w-3xl px-4 text-center sm:px-6">
      <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">Nurses ready to help</p>
      <h2 class="text-3xl font-bold text-white sm:text-4xl">Your next assignment deserves a nurse who's been there.</h2>
      <p class="mt-5 text-lg text-brand-200">Submit your brief. We'll match you with the right clinical specialist in minutes.</p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
          Place my order — from $24/page
          <svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
        </a>
        <a href="/contact" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-4 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
          Talk to us first
        </a>
      </div>
      <div class="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-2 text-xs text-brand-300">
        <span>✓ BSN/MSN/DNP verified writers</span>
        <span>✓ NANDA/ADPIE accurate</span>
        <span>✓ Grade or full refund</span>
        <span>✓ Free Turnitin report</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
@keyframes scroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
@keyframes scroll-reverse {
  from { transform: translateX(-50%); }
  to   { transform: translateX(0); }
}
.animate-scroll         { animation: scroll         35s linear infinite; }
.animate-scroll-reverse { animation: scroll-reverse 35s linear infinite; }
.animate-scroll:hover,
.animate-scroll-reverse:hover { animation-play-state: paused; }
</style>
