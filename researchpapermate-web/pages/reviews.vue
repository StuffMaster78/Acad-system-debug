<script setup lang="ts">
import { ArrowRight, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Student Reviews — 8,200+ Verified Reviews | ResearchPaperMate',
  description: 'Verified reviews from 8,200+ research paper orders. 4.8/5 average. Read what students from top universities say about ResearchPaperMate.',
  ogTitle: 'ResearchPaperMate Reviews — 4.8/5 from 8,200+ Students',
  ogDescription: 'Verified student reviews across 100+ subject areas. Human-written research papers from $15/page.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://researchpapermate.com/reviews' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'ResearchPaperMate',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '8200', bestRating: '5' },
    }),
  }],
})

const platforms = [
  { name: 'Trustpilot', rating: 4.8, count: '4,900+', bar: 96 },
  { name: 'SiteJabber', rating: 4.7, count: '2,200+', bar: 94 },
  { name: 'Google',     rating: 4.9, count: '1,100+', bar: 98 },
]

const reviews = [
  {
    name: 'Marcus L.',   university: 'University of Edinburgh', subject: 'Business Strategy (MBA)',        level: 'Postgraduate', grade: 'A',  date: 'May 2026', stars: 5,
    quote: "My writer clearly understood Porter's Five Forces at a graduate level — not just described them but applied them to a specific market entry scenario with real insight. Distinction."
  },
  {
    name: 'Priya T.',    university: "King's College London",   subject: 'Nursing Literature Review',     level: 'MSN',          grade: 'A+', date: 'May 2026', stars: 5,
    quote: "Systematic literature review in APA 7 for my nursing dissertation. The writer found sources I hadn't come across and synthesised them methodologically. Asked for one minor revision and it was returned in under 3 hours."
  },
  {
    name: 'Daniel O.',   university: 'Northumbria University',  subject: 'Quantitative Data Analysis',    level: 'Undergraduate', grade: 'B+', date: 'April 2026', stars: 5,
    quote: "SPSS output interpreted correctly and written up in the required format with statistical notation I hadn't learned yet. The writer also explained what each result meant, which actually helped me understand it."
  },
  {
    name: 'Lena V.',     university: 'LSE',                    subject: 'Political Economy Dissertation', level: 'PhD',           grade: 'A',  date: 'April 2026', stars: 5,
    quote: "Second opinion on my dissertation's theoretical framework. The feedback was specific, direct, and identified a gap my supervisor had been circling around without naming. That conversation changed my whole methodology chapter."
  },
  {
    name: 'Arjun S.',    university: 'University of Toronto',   subject: 'Environmental Law',             level: "Master's",     grade: 'A',  date: 'March 2026', stars: 5,
    quote: "Case analysis on transboundary pollution law. The writer cited international precedents I hadn't considered and structured the argument clearly. My professor said the analysis was 'unusually sophisticated for the level.'"
  },
  {
    name: 'Elin R.',     university: 'Uppsala University',      subject: 'Molecular Biology',             level: 'PhD',           grade: 'A',  date: 'March 2026', stars: 5,
    quote: "Literature review section of my PhD thesis on CRISPR applications. Technically rigorous, up-to-date citations from 2023–2024, and consistent with the methodological stance I'd established in earlier chapters."
  },
  {
    name: 'James C.',    university: 'Georgetown University',    subject: 'International Relations',       level: 'Undergraduate', grade: 'A',  date: 'February 2026', stars: 5,
    quote: "Security studies essay on nuclear deterrence theory. The writer engaged with Waltz and Sagan properly — not just cited them but argued between their positions. My prof asked if I wanted to extend it for the department journal."
  },
  {
    name: 'Yuki T.',     university: 'University of Tokyo',     subject: 'Economics Research Paper',      level: "Master's",     grade: 'A',  date: 'February 2026', stars: 5,
    quote: "Macroeconomics paper on Japanese monetary policy. The writer understood the institutional context and cited Bank of Japan working papers alongside mainstream academic sources. Exactly the depth my programme expects."
  },
  {
    name: 'Chioma A.',   university: 'University of Cape Town', subject: 'Public Health Dissertation',    level: 'MPH',           grade: 'A+', date: 'January 2026', stars: 5,
    quote: "Dissertation chapter on HIV treatment access in sub-Saharan Africa. The writer integrated WHO policy data, peer-reviewed clinical evidence, and qualitative community studies. My supervisor approved it on first submission."
  },
  {
    name: 'Finn L.',     university: 'TU Delft',                subject: 'Engineering Ethics',            level: 'Undergraduate', grade: 'A',  date: 'January 2026', stars: 5,
    quote: "Applied ethics essay for my civil engineering programme. The writer handled the technical context accurately and applied the relevant ethical frameworks without oversimplifying the engineering constraints."
  },
  {
    name: 'Isabelle P.', university: 'Sciences Po',             subject: 'EU Policy Analysis',            level: "Master's",     grade: 'A',  date: 'December 2025', stars: 5,
    quote: "Policy memo on EU digital regulation. The writer knew the GDPR, DSA, and DMA landscape well and produced a document that read like it was written by someone working in Brussels. Exactly the register my programme requires."
  },
  {
    name: 'Kwame A.',    university: 'University of Ghana',     subject: 'African Development Economics', level: 'PhD',           grade: 'A',  date: 'December 2025', stars: 5,
    quote: "Chapter on structural adjustment and agricultural productivity in West Africa. The writer engaged with heterodox development economics, not just mainstream models — which is exactly the theoretical position my thesis takes."
  },
]

const disciplines = [
  { name: 'Business & Economics', count: '1,800+', color: 'bg-blue-50 border-blue-100 text-blue-700' },
  { name: 'Life & Medical Sciences', count: '1,200+', color: 'bg-green-50 border-green-100 text-green-700' },
  { name: 'Law & Politics', count: '1,100+', color: 'bg-purple-50 border-purple-100 text-purple-700' },
  { name: 'Social Sciences', count: '980+', color: 'bg-amber-50 border-amber-100 text-amber-700' },
  { name: 'STEM & Engineering', count: '870+', color: 'bg-rose-50 border-rose-100 text-rose-700' },
  { name: 'Arts & Humanities', count: '750+', color: 'bg-teal-50 border-teal-100 text-teal-700' },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-claret-950 py-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-claret-600 opacity-20 blur-[120px]" />

      <div class="relative mx-auto max-w-5xl px-4 sm:px-6">
        <div class="text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-claret-300">Verified student reviews</p>
          <h1 class="font-serif text-4xl font-extrabold text-white sm:text-5xl">
            8,200+ orders reviewed.<br class="hidden sm:block" /> Across 100+ universities.
          </h1>
          <p class="mx-auto mt-4 max-w-xl text-lg text-claret-200">
            Real researchers. Real grades. Real feedback from students who have handed work in.
          </p>
        </div>

        <!-- Platform cards -->
        <div class="mt-12 grid gap-4 sm:grid-cols-3">
          <div
            v-for="p in platforms" :key="p.name"
            class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm"
          >
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm font-bold text-white">{{ p.name }}</p>
              <p class="text-xl font-extrabold text-white">{{ p.rating }}</p>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-white/10">
              <div class="h-full rounded-full bg-amber-400" :style="`width:${p.bar}%`" />
            </div>
            <div class="mt-2 flex items-center justify-between">
              <div class="flex gap-0.5">
                <Star v-for="i in 5" :key="i" class="h-3 w-3 fill-amber-400 text-amber-400" />
              </div>
              <p class="text-xs text-claret-300">{{ p.count }} reviews</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Discipline breakdown ───────────────────────────────────────────── -->
    <section class="border-b border-slate-100 bg-white py-10">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <p class="mb-5 text-center text-xs font-bold uppercase tracking-wider text-slate-400">Orders by subject area</p>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="d in disciplines" :key="d.name"
            class="flex items-center justify-between rounded-xl border px-4 py-3"
            :class="d.color"
          >
            <p class="text-sm font-semibold">{{ d.name }}</p>
            <p class="text-sm font-bold">{{ d.count }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Masonry reviews ────────────────────────────────────────────────── -->
    <section class="bg-parchment-100 py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="columns-1 gap-5 sm:columns-2 lg:columns-3 [column-fill:balance]">
          <div
            v-for="r in reviews"
            :key="r.name"
            class="mb-5 break-inside-avoid overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
          >
            <!-- University band -->
            <div class="border-b border-slate-100 bg-slate-50 px-4 py-2 text-[11px] font-semibold text-slate-500">
              {{ r.university }}
            </div>
            <div class="p-5">
              <div class="mb-3 flex items-center justify-between gap-2">
                <div class="flex gap-0.5">
                  <Star v-for="i in r.stars" :key="i" class="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                </div>
                <span class="rounded-full bg-slate-900 px-2.5 py-0.5 text-[11px] font-bold text-white">{{ r.grade }}</span>
              </div>
              <p class="text-sm leading-relaxed text-slate-700">"{{ r.quote }}"</p>
              <div class="mt-4 border-t border-slate-100 pt-3 flex items-end justify-between gap-2">
                <div>
                  <p class="text-xs font-bold text-slate-900">{{ r.name }}</p>
                  <p class="text-xs text-slate-500">{{ r.subject }}</p>
                </div>
                <div class="text-right shrink-0">
                  <span class="block rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">{{ r.level }}</span>
                  <span class="block mt-1 text-[11px] text-slate-400">{{ r.date }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-claret-950 py-16 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="font-serif text-2xl font-extrabold text-white">Work with a real researcher.</h2>
        <p class="mt-3 text-claret-200">Research papers from $15/page. Grade or money back.</p>
        <a
          :href="app.order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-900 shadow-lg transition-colors hover:bg-parchment-100"
        >
          Start my order <ArrowRight class="h-4 w-4" />
        </a>
      </div>
    </section>

  </div>
</template>
