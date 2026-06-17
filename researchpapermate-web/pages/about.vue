<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'About ResearchPaperMate — Our Researchers, Our Standards',
  description: 'ResearchPaperMate connects students with verified PhD and Master\'s researchers since 2019. Only 2 in 100 applicants pass our vetting process.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/about' }] })

const stats = [
  { value: '14,700+', label: 'Papers delivered',  sub: 'Across 100+ subjects' },
  { value: '2/100',   label: 'Acceptance rate',    sub: 'Writer applications' },
  { value: '4.8/5',   label: 'Average rating',     sub: 'Based on 8,200+ reviews' },
  { value: '2019',    label: 'Founded',             sub: 'Still human-only' },
]

const vettingSteps = [
  {
    n: '01',
    title: 'Degree certificate verification',
    desc: 'Every application requires certified degree documents. We verify directly with the issuing institution. No unverifiable claims make it through.',
  },
  {
    n: '02',
    title: 'Subject-specific knowledge test',
    desc: 'A written test in the applicant\'s declared subject area. Designed to surface actual domain knowledge — not general writing ability.',
  },
  {
    n: '03',
    title: 'Original sample paper review',
    desc: 'Our editorial team reviews an original academic sample against our quality rubric: argument structure, citation accuracy, and disciplinary conventions.',
  },
  {
    n: '04',
    title: 'Supervised trial period',
    desc: 'New writers complete their first five orders under editorial oversight. Only those who sustain our quality standard earn their full writer status.',
  },
]

const values = [
  { emoji: '🏆', title: 'Quality over volume', desc: 'We turn away 98% of applicants. Every paper is reviewed by a senior editor before delivery.' },
  { emoji: '🤝', title: 'Academic integrity', desc: 'We provide model and reference papers. We never encourage misrepresentation and include a legal-use disclosure on every order.' },
  { emoji: '🔒', title: 'Privacy by design', desc: 'Your identity and order details are never sold, shared, or stored beyond what\'s required to deliver your paper.' },
  { emoji: '💬', title: 'Real human support', desc: 'Every query reaches a real person. No chatbots, no queues, no scripted replies — direct and knowledgeable.' },
]

const milestones = [
  { year: '2019', event: 'Founded with 20 core writers across 12 subject areas.' },
  { year: '2021', event: 'Reached 1,000 completed orders — 4.7/5 average rating at scale.' },
  { year: '2022', event: 'Dissertation tier launched with dedicated PhD-level specialists.' },
  { year: '2023', event: 'Expanded to 100+ subject areas and 150+ active expert writers.' },
  { year: '2024', event: '200+ writers, 10,000+ papers delivered, data analysis division added.' },
  { year: '2025', event: 'AI-detection guarantee introduced. 14,700+ orders and counting.' },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-claret-950 py-24">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-brand-600 opacity-20 blur-[120px]" />
      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-claret-300">Our story</p>
        <h1 class="font-serif text-4xl font-bold leading-tight text-white sm:text-5xl">
          We built the research paper service<br class="hidden sm:block" />
          we wished existed.
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-claret-200">
          Since 2019, ResearchPaperMate has connected students with verified, degree-holding researchers who write original papers from scratch — no AI, no templates, no shortcuts.
        </p>
      </div>
    </section>

    <!-- ── Stats ─────────────────────────────────────────────────────────── -->
    <section class="border-b border-slate-100 bg-white">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 divide-x divide-y divide-slate-100 md:grid-cols-4 md:divide-y-0">
          <div v-for="stat in stats" :key="stat.label" class="flex flex-col items-center py-10 px-6 text-center">
            <span class="text-3xl font-extrabold tabular-nums text-claret-700">{{ stat.value }}</span>
            <span class="mt-1 text-sm font-semibold text-slate-800">{{ stat.label }}</span>
            <span class="mt-0.5 text-xs text-slate-400">{{ stat.sub }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Mission ───────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-16 lg:grid-cols-2">
          <div>
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-amber-700">What we believe</p>
            <h2 class="font-serif text-3xl font-bold leading-snug text-slate-900 sm:text-4xl">
              Good research takes a real researcher — not a language model.
            </h2>
            <p class="mt-5 text-base leading-relaxed text-slate-500">
              AI can write sentences. It cannot read your university's rubric, anticipate what your supervisor values, or know that your subject has a convention that the textbook doesn't mention. That's what a specialist knows — and it's what makes the difference between a pass and a distinction.
            </p>
            <p class="mt-4 text-base leading-relaxed text-slate-500">
              Every writer on ResearchPaperMate holds a verified postgraduate degree in their subject. They've written at this level before. They know the literature. They know the expectations. That's the only standard we work to.
            </p>
          </div>
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="v in values" :key="v.title" class="rounded-2xl border border-slate-200 bg-parchment-100 p-6">
              <div class="mb-3 text-3xl">{{ v.emoji }}</div>
              <h3 class="font-bold text-slate-900">{{ v.title }}</h3>
              <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ v.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Writer vetting ─────────────────────────────────────────────────── -->
    <section class="bg-parchment-100 py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-16 lg:grid-cols-2">
          <div>
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-amber-700">Our vetting process</p>
            <h2 class="text-3xl font-bold text-slate-900">
              Only 2 in 100 applicants<br class="hidden sm:block" /> make the cut.
            </h2>
            <p class="mt-5 text-base leading-relaxed text-slate-500">
              Generous acceptance rates might look good as a headline. We don't think they serve students. The writers on this platform have cleared four independent checkpoints — and they stay only as long as they maintain the standard.
            </p>
          </div>
          <div class="space-y-5">
            <div v-for="step in vettingSteps" :key="step.n" class="flex gap-5">
              <div class="flex size-10 shrink-0 items-center justify-center rounded-xl border-2 border-claret-200 bg-white text-sm font-extrabold text-claret-700">
                {{ step.n }}
              </div>
              <div>
                <h3 class="font-bold text-slate-900">{{ step.title }}</h3>
                <p class="mt-1 text-sm leading-relaxed text-slate-500">{{ step.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Timeline ───────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-amber-700">Our journey</p>
          <h2 class="text-3xl font-bold text-slate-900">How we got here.</h2>
        </div>
        <div class="relative space-y-0">
          <!-- Vertical line -->
          <div class="absolute left-[39px] top-4 bottom-4 w-px bg-amber-100" />
          <div v-for="m in milestones" :key="m.year" class="relative flex gap-6 pb-8 last:pb-0">
            <div class="flex size-[42px] shrink-0 items-center justify-center rounded-full border-2 border-claret-200 bg-white text-xs font-extrabold text-claret-700 shadow-sm z-10">
              {{ m.year.slice(2) }}'
            </div>
            <div class="pt-2">
              <p class="text-xs font-bold text-amber-700">{{ m.year }}</p>
              <p class="mt-0.5 text-sm leading-relaxed text-slate-600">{{ m.event }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────────── -->
    <section class="bg-claret-950 py-20 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-3xl font-bold text-white">Work with a real researcher.</h2>
        <p class="mt-4 text-lg text-claret-200">
          Tell us your subject, level, and deadline. We'll match you with the right specialist within minutes.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
            Start my order — from $15/page
          </a>
          <a href="/how-it-works" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10">
            How it works →
          </a>
        </div>
      </div>
    </section>

  </div>
</template>
