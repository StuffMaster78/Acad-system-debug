<script setup lang="ts">
const app = useAppUrl()

// Live-feeling order counter — seed realistic, increment occasionally
const ordersToday = ref(147)
onMounted(() => {
  const tick = () => {
    if (Math.random() > 0.7) ordersToday.value++
    setTimeout(tick, 8000 + Math.random() * 12000)
  }
  setTimeout(tick, 5000)
})

useSeoMeta({
  title: 'Essay Writing Service from $10/Page | EssayManiacs',
  description: 'Essays written by subject-obsessed specialists — not AI, not generalists. From $10/page. Zero AI. Grade or money back. 20,000+ essays delivered.',
  ogTitle: 'EssayManiacs — Essays Written by People Who Love the Subject',
  ogDescription: 'Expert essays across every subject and level. From $10/page. Zero AI. Grade or money back.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/' }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Organization',
        '@id': 'https://essaymaniacs.com/#org',
        name: 'EssayManiacs',
        url: 'https://essaymaniacs.com',
        logo: 'https://essaymaniacs.com/favicon.svg',
        contactPoint: { '@type': 'ContactPoint', contactType: 'customer support', availableLanguage: 'English' },
        sameAs: ['https://www.trustpilot.com/review/essaymaniacs.com'],
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': 'https://essaymaniacs.com/#website',
        url: 'https://essaymaniacs.com',
        name: 'EssayManiacs',
        description: 'Academic essay writing service staffed by subject-specialist writers.',
        publisher: { '@id': 'https://essaymaniacs.com/#org' },
        potentialAction: {
          '@type': 'SearchAction',
          target: { '@type': 'EntryPoint', urlTemplate: 'https://essaymaniacs.com/services?q={search_term_string}' },
          'query-input': 'required name=search_term_string',
        },
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'ProfessionalService',
        '@id': 'https://essaymaniacs.com/#service',
        name: 'EssayManiacs',
        description: 'Academic essay writing service staffed by subject-specialist writers.',
        url: 'https://essaymaniacs.com',
        priceRange: '$10–$50 per page',
        aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '20000' },
      }),
    },
  ],
})

const stats = [
  { value: '20,000+', label: 'Essays delivered',       note: 'Across 100+ subjects' },
  { value: '500+',    label: 'Subject specialists',     note: 'Each hired for their field' },
  { value: '4.8/5',   label: 'Average rating',          note: 'Based on 9,400+ reviews' },
  { value: '2 hrs',   label: 'Fastest turnaround',      note: 'For urgent essays' },
]

const whyUs = [
  {
    emoji: '🎯',
    headline: 'Matched to your exact subject.',
    body: "We don't assign essays randomly. Your order goes to a writer with a degree in your discipline — someone who has actually written at this level before and knows what tutors look for.",
  },
  {
    emoji: '🤖',
    headline: 'Written by a human who cares.',
    body: "AI writes sentences. It doesn't have opinions about your subject, can't read your rubric's nuance, and doesn't care about your grade. Our writers do. That difference shows.",
  },
  {
    emoji: '📐',
    headline: 'Every essay type. Every level.',
    body: 'Argumentative, reflective, analytical, personal statement, case study, literature review — plus proofreading and editing. One platform, 20+ types, all subjects, high school to doctoral.',
  },
]

const services = [
  { emoji: '✍️', title: 'Essays',              href: '/services/essays',           badge: 'Most popular', desc: 'Argumentative, analytical, reflective, narrative — any type, any level, any subject.' },
  { emoji: '📄', title: 'Research Papers',      href: '/services/research-papers',  badge: null,          desc: 'Original research from peer-reviewed sources, any citation style.' },
  { emoji: '🎓', title: 'Dissertations',        href: '/services/dissertations',    badge: null,          desc: 'Proposal through final chapter, with supervisor feedback integration.' },
  { emoji: '💼', title: 'Case Studies',         href: '/services/case-studies',     badge: null,          desc: 'Problem-solution-evaluation structure with real supporting evidence.' },
  { emoji: '🏫', title: 'Admission Essays',     href: '/services/admission-essays', badge: 'High impact', desc: 'Personal statements and scholarship essays tailored to each school.' },
  { emoji: '✅', title: 'Proofreading',         href: '/services/proofreading',     badge: null,          desc: 'Grammar, argument, structure, and citation accuracy — all checked.' },
]

const subjects = [
  'History', 'Psychology', 'Sociology', 'Business', 'Law', 'Economics',
  'Literature', 'Philosophy', 'Political Science', 'Marketing', 'Nursing',
  'Biology', 'Chemistry', 'Engineering', 'Statistics', 'Finance', 'Education', 'Media Studies',
]

const steps = [
  { n: '01', color: 'bg-brand-700 text-white', title: 'Fill in your brief',        desc: 'Essay type, subject, level, deadline, word count, and any rubric or instructions.' },
  { n: '02', color: 'bg-violet-600 text-white', title: 'Meet your matched writer', desc: 'We assign a specialist with the right subject background — not a random generalist.' },
  { n: '03', color: 'bg-purple-600 text-white', title: 'Chat directly',            desc: 'Message your writer, share files, follow progress. No ticket queue, no delays.' },
  { n: '04', color: 'bg-fuchsia-600 text-white',title: 'Download + revise free',   desc: 'Receive your essay with a free plagiarism report. Unlimited revisions included.' },
]

const guarantees = [
  { emoji: '🏆', title: 'Grade or money back',        desc: "If the work doesn't meet your stated requirements, we rewrite it or refund you. No questions asked." },
  { emoji: '🎯', title: 'Subject-matched writer',     desc: "Your essay goes to someone with a degree in your discipline. Not a generalist who dabbles." },
  { emoji: '🤖', title: 'Zero AI content',            desc: 'Human-written by a subject enthusiast. Free AI-detection report on request if you need proof.' },
  { emoji: '🔒', title: 'Complete confidentiality',   desc: 'Your identity, school, and order details are never shared with any third party.' },
  { emoji: '🔁', title: 'Unlimited free revisions',   desc: 'As many changes as you need within the revision window — always at zero extra cost.' },
  { emoji: '⚡', title: 'As fast as 2 hours',         desc: 'Urgent essay due tonight? Most essays up to 4 pages delivered in 2 hours.' },
]

const testimonials = [
  {
    initials: 'JM', name: 'Jake M.', subject: 'History, undergraduate', orders: 8,
    grade: 'A−',
    quote: 'Needed an argumentative essay on colonial African history in 24 hours. Got back something I actually learned from. Solid sourcing, strong argument.',
  },
  {
    initials: 'AL', name: 'Amara L.', subject: "Psychology, Master's", orders: 12,
    grade: 'A',
    quote: 'My thesis literature review was a mess. They restructured it completely — gaps I missed, sources I hadn\'t found. Worth every cent.',
  },
  {
    initials: 'SC', name: 'Sophie C.', subject: 'Literature, doctoral', orders: 3,
    grade: 'A+',
    quote: "Surprised by the quality of a reflective essay. It sounded like me — better than me, actually. Will use again.",
  },
]
</script>

<template>
  <!-- ─── Hero ─────────────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-brand-900 py-20 sm:py-28">
    <!-- Grid overlay -->
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
    <!-- Purple orb blobs -->
    <div class="pointer-events-none absolute -top-32 right-0 h-[500px] w-[500px] rounded-full bg-brand-500 opacity-20 blur-[120px]" />
    <div class="pointer-events-none absolute bottom-0 -left-20 h-64 w-64 rounded-full bg-violet-400 opacity-15 blur-3xl" />

    <div class="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: copy -->
        <div class="max-w-xl">
          <!-- Live counter -->
          <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm text-brand-200 backdrop-blur-sm">
            <span class="h-1.5 w-1.5 animate-pulse rounded-full bg-green-400" />
            <span><strong class="text-white">{{ ordersToday }}</strong> essays ordered today · from <strong class="text-white">$10/page</strong></span>
          </div>

          <h1 class="text-4xl font-bold leading-tight text-white sm:text-5xl lg:text-[3.25rem]">
            Essays written by people<br class="hidden sm:block" />
            <span class="text-brand-300">who love the subject.</span>
          </h1>

          <p class="mt-6 text-lg leading-relaxed text-brand-200">
            Not AI. Not a generalist who dabbles in everything. A subject-obsessed specialist who has a degree in your field and actually cares about your grade.
          </p>

          <!-- Discount code nudge -->
          <div class="mt-5 flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white backdrop-blur-sm">
            <span class="text-brand-300">🎁</span>
            <span>First order? Use <strong class="rounded bg-white/15 px-1.5 py-0.5 font-mono tracking-wider">FIRST15</strong> for 15% off</span>
          </div>

          <div class="mt-3 flex items-center gap-3 text-sm text-brand-300">
            <span>✦ From $10/page</span>
            <span class="text-brand-700">·</span>
            <span>✦ Grade or money back</span>
            <span class="text-brand-700">·</span>
            <span>✦ Zero AI</span>
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

          <div class="mt-7 pt-5 border-t border-white/10">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: order form -->
        <div>
          <MultiStepOrderForm />
        </div>

      </div>
    </div>
  </section>

  <!-- ─── Stats bar ─────────────────────────────────────────────────────────── -->
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

  <!-- ─── Why EssayManiacs ──────────────────────────────────────────────────── -->
  <section class="bg-brand-50 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-14 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Why students choose us</p>
        <h2 class="text-3xl font-bold text-slate-900 sm:text-4xl">There's a difference between knowing<br class="hidden sm:block" /> how to write and knowing the subject.</h2>
      </div>
      <div class="grid gap-8 md:grid-cols-3">
        <div
          v-for="w in whyUs" :key="w.headline"
          class="group relative overflow-hidden rounded-2xl border border-brand-100 bg-white p-8 shadow-sm transition-shadow hover:shadow-md"
        >
          <div class="mb-5 text-4xl">{{ w.emoji }}</div>
          <h3 class="text-lg font-bold leading-snug text-slate-900">{{ w.headline }}</h3>
          <p class="mt-3 text-sm leading-relaxed text-slate-500">{{ w.body }}</p>
          <div class="pointer-events-none absolute -bottom-10 -right-10 h-32 w-32 rounded-full bg-brand-50 transition-transform group-hover:scale-150" />
        </div>
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
          <p class="mb-2 text-xs font-bold uppercase tracking-widest text-brand-600">20 essay types · 100+ subjects</p>
          <h2 class="text-3xl font-bold text-slate-900">Every essay type. Every subject.</h2>
        </div>
        <a href="/services" class="hidden text-sm font-semibold text-brand-600 hover:underline sm:block">All services →</a>
      </div>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <a
          v-for="svc in services" :key="svc.title" :href="svc.href"
          class="group relative flex flex-col rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md"
        >
          <div v-if="svc.badge" class="absolute right-4 top-4 rounded-full bg-brand-100 px-2.5 py-0.5 text-[11px] font-bold text-brand-700">{{ svc.badge }}</div>
          <div class="mb-3 text-2xl">{{ svc.emoji }}</div>
          <h3 class="font-bold text-slate-900 transition-colors group-hover:text-brand-700">{{ svc.title }}</h3>
          <p class="mt-2 flex-1 text-sm leading-relaxed text-slate-500">{{ svc.desc }}</p>
          <span class="mt-4 text-xs font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Learn more →</span>
        </a>
      </div>
      <div class="mt-10 flex flex-wrap gap-2">
        <span v-for="sub in subjects" :key="sub" class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700 transition-colors hover:bg-brand-100">{{ sub }}</span>
        <span class="rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs text-slate-400">+80 more</span>
      </div>
    </div>
  </section>

  <!-- ─── How it works ──────────────────────────────────────────────────────── -->
  <section class="bg-slate-50 py-20">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-14 text-center">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Simple process</p>
        <h2 class="text-3xl font-bold text-slate-900 sm:text-4xl">From brief to finished essay in four steps.</h2>
      </div>

      <!-- Desktop: horizontal timeline -->
      <div class="hidden md:block">
        <div class="relative grid grid-cols-4">
          <div class="absolute top-7 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-brand-300 via-violet-400 to-fuchsia-400" />
          <div v-for="step in steps" :key="step.n" class="flex flex-col items-center px-4 text-center">
            <div class="relative z-10 mb-6 flex size-14 items-center justify-center rounded-full border-4 border-brand-100 bg-white shadow-md">
              <span class="text-lg font-extrabold text-brand-700">{{ step.n }}</span>
            </div>
            <h3 class="text-sm font-bold text-slate-900">{{ step.title }}</h3>
            <p class="mt-2 text-xs leading-relaxed text-slate-500">{{ step.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Mobile: colored step cards -->
      <div class="space-y-4 md:hidden">
        <div v-for="step in steps" :key="step.n" class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-5">
          <div class="flex size-11 shrink-0 items-center justify-center rounded-xl text-sm font-extrabold" :class="step.color">{{ step.n }}</div>
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
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Every order, every time</p>
        <h2 class="text-3xl font-bold text-white sm:text-4xl">What we promise — and keep.</h2>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="g in guarantees" :key="g.title" class="flex gap-4 rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 transition-colors hover:bg-white/10">
          <div class="text-2xl">{{ g.emoji }}</div>
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
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Real students, real essays</p>
        <h2 class="text-3xl font-bold text-slate-900">What happens when your writer loves your subject.</h2>
      </div>
      <div class="grid gap-6 md:grid-cols-3">
        <div v-for="t in testimonials" :key="t.name" class="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-7">
          <!-- Grade badge -->
          <div class="absolute right-5 top-5 flex size-12 items-center justify-center rounded-full border-2 border-brand-300 bg-brand-50 text-xl font-extrabold text-brand-700">
            {{ t.grade }}
          </div>
          <!-- Stars -->
          <div class="mb-4 flex gap-0.5">
            <svg v-for="i in 5" :key="i" class="size-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <p class="text-xs font-semibold text-brand-600">{{ t.subject }}</p>
          <blockquote class="mt-3 pr-12 text-sm italic leading-relaxed text-slate-700">"{{ t.quote }}"</blockquote>
          <div class="mt-5 flex items-center gap-3 border-t border-slate-200 pt-4">
            <div class="flex size-8 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">{{ t.initials }}</div>
            <div class="flex-1">
              <p class="text-xs font-bold text-slate-800">{{ t.name }}</p>
              <p class="text-xs text-slate-400">{{ t.orders }} orders placed</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── FAQ ─────────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── Final CTA ───────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-gradient-to-br from-brand-800 to-brand-900 py-20">
    <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px]" />
    <div class="pointer-events-none absolute -top-20 right-0 h-64 w-64 rounded-full bg-brand-500 opacity-20 blur-[80px]" />
    <div class="relative z-10 mx-auto max-w-3xl px-4 text-center sm:px-6">
      <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">
        <span class="mr-2 h-1.5 w-1.5 inline-block animate-pulse rounded-full bg-green-400" />
        {{ ordersToday }} essays ordered today
      </p>
      <h2 class="text-3xl font-bold text-white sm:text-4xl">Your deadline isn't moving.<br class="hidden sm:block" /> Your writer is ready.</h2>
      <p class="mt-5 text-lg text-brand-200">Tell us what you need. A subject-obsessed specialist will be on it.</p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
          Place my order — from $10/page
          <svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
        </a>
        <a href="/contact" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-4 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
          Talk to us first
        </a>
      </div>
      <div class="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-2 text-xs text-brand-300">
        <span>✓ No payment until you approve</span>
        <span>✓ Free revisions</span>
        <span>✓ Grade or full refund</span>
        <span>✓ 24/7 support</span>
      </div>
    </div>
  </section>
</template>
