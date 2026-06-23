<script setup lang="ts">
import { Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Student Reviews — 8,200+ Verified Reviews | ResearchPaperMate',
  description: 'Verified reviews from 8,200+ research paper orders. 4.8/5 average. Read what students from top universities say about ResearchPaperMate.',
  ogTitle: 'ResearchPaperMate Reviews — 4.8/5 from 8,200+ Students',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
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

// Grade distribution
const gradeBreakdown = [
  { grade: 'A+', pct: 34, count: '2,788', color: 'bg-amber-500' },
  { grade: 'A',  pct: 47, count: '3,854', color: 'bg-claret-700' },
  { grade: 'B+', pct: 13, count: '1,066', color: 'bg-claret-500' },
  { grade: 'B',  pct: 4,  count: '328',   color: 'bg-claret-300' },
  { grade: 'C+', pct: 2,  count: '164',   color: 'bg-parchment-400' },
]

const platforms = [
  { name: 'Trustpilot', rating: 4.8, count: '4,900+', bar: 96 },
  { name: 'SiteJabber', rating: 4.7, count: '2,200+', bar: 94 },
  { name: 'Google',     rating: 4.9, count: '1,100+', bar: 98 },
]

const reviews = [
  { name: 'Marcus L.',   university: 'University of Edinburgh', subject: 'Business Strategy (MBA)',        level: 'Postgraduate', grade: 'A',  date: 'May 2026',      stars: 5,
    quote: "My writer clearly understood Porter's Five Forces at a graduate level — not just described them but applied them to a specific market entry scenario with real insight. Distinction." },
  { name: 'Priya T.',    university: "King's College London",   subject: 'Nursing Literature Review',     level: 'MSN',          grade: 'A+', date: 'May 2026',      stars: 5,
    quote: "Systematic literature review in APA 7 for my nursing dissertation. Found sources I hadn't come across and synthesised them methodologically. One minor revision, returned in under 3 hours." },
  { name: 'Daniel O.',   university: 'Northumbria University',  subject: 'Quantitative Data Analysis',    level: 'Undergraduate', grade: 'B+', date: 'April 2026',    stars: 5,
    quote: "SPSS output interpreted correctly and written up in the required format with statistical notation I hadn't learned yet. The writer explained every result, which actually helped me understand it." },
  { name: 'Lena V.',     university: 'LSE',                    subject: 'Political Economy Dissertation', level: 'PhD',           grade: 'A',  date: 'April 2026',    stars: 5,
    quote: "Second opinion on my dissertation's theoretical framework. The feedback was specific, direct, and identified a gap my supervisor had been circling around without naming. Changed my whole methodology chapter." },
  { name: 'Arjun S.',    university: 'University of Toronto',   subject: 'Environmental Law',             level: "Master's",      grade: 'A',  date: 'March 2026',    stars: 5,
    quote: "Case analysis on transboundary pollution law. Cited international precedents I hadn't considered. My professor said the analysis was 'unusually sophisticated for the level.'" },
  { name: 'Elin R.',     university: 'Uppsala University',      subject: 'Molecular Biology',             level: 'PhD',           grade: 'A',  date: 'March 2026',    stars: 5,
    quote: "Literature review section of my PhD thesis on CRISPR applications. Technically rigorous, up-to-date citations from 2023–2024, consistent with the methodological stance in my earlier chapters." },
  { name: 'James C.',    university: 'Georgetown University',   subject: 'International Relations',       level: 'Undergraduate', grade: 'A',  date: 'February 2026', stars: 5,
    quote: "Security studies essay on nuclear deterrence theory. Engaged with Waltz and Sagan properly — argued between their positions. My prof asked if I wanted to extend it for the department journal." },
  { name: 'Yuki T.',     university: 'University of Tokyo',     subject: 'Economics Research Paper',      level: "Master's",      grade: 'A',  date: 'February 2026', stars: 5,
    quote: "Macroeconomics paper on Japanese monetary policy. Cited Bank of Japan working papers alongside mainstream academic sources. Exactly the depth my programme expects." },
  { name: 'Chioma A.',   university: 'University of Cape Town', subject: 'Public Health Dissertation',    level: 'MPH',           grade: 'A+', date: 'January 2026',  stars: 5,
    quote: "Dissertation chapter on HIV treatment access in sub-Saharan Africa. Integrated WHO policy data, peer-reviewed clinical evidence, and qualitative community studies. Approved on first submission." },
  { name: 'Finn L.',     university: 'TU Delft',               subject: 'Engineering Ethics',            level: 'Undergraduate', grade: 'A',  date: 'January 2026',  stars: 5,
    quote: "Applied ethics for civil engineering. Handled the technical context accurately and applied the relevant ethical frameworks without oversimplifying the engineering constraints." },
  { name: 'Isabelle P.', university: 'Sciences Po',            subject: 'EU Policy Analysis',            level: "Master's",      grade: 'A',  date: 'December 2025', stars: 5,
    quote: "Policy memo on EU digital regulation. Knew the GDPR, DSA, and DMA landscape well. Read like it was written by someone working in Brussels — exactly the register my programme requires." },
  { name: 'Kwame A.',    university: 'University of Ghana',    subject: 'African Development Economics', level: 'PhD',           grade: 'A',  date: 'December 2025', stars: 5,
    quote: "Chapter on structural adjustment and agricultural productivity in West Africa. Engaged with heterodox development economics, not just mainstream models — which is my thesis's theoretical position." },
]

const disciplines = [
  { name: 'Business & Economics', count: '1,800+' },
  { name: 'Life & Medical Sciences', count: '1,200+' },
  { name: 'Law & Politics', count: '1,100+' },
  { name: 'Social Sciences', count: '980+' },
  { name: 'STEM & Engineering', count: '870+' },
  { name: 'Arts & Humanities', count: '750+' },
]
</script>

<template>
  <div>

    <!-- ── Masthead — editorial, left-aligned ──────────────────────────────── -->
    <section class="bg-claret-950 pt-16 pb-0">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-end gap-8 lg:grid-cols-2">
          <div>
            <p class="text-[11px] font-bold uppercase tracking-widest text-amber-500">Verified student reviews</p>
            <h1 class="mt-3 font-serif text-5xl text-white sm:text-6xl">8,200+<br />reviews.</h1>
            <p class="mt-4 max-w-md text-lg text-claret-200">
              From PhD students in Uppsala to nursing students in London. Real researchers, real grades, real feedback.
            </p>
          </div>
          <!-- Platform ratings -->
          <div class="grid gap-3 sm:grid-cols-3 lg:pb-0">
            <div v-for="p in platforms" :key="p.name" class="rounded-2xl border border-claret-800 bg-claret-900/60 p-4 backdrop-blur-sm">
              <p class="text-xs font-bold text-white">{{ p.name }}</p>
              <p class="mt-1 text-2xl font-extrabold text-amber-400">{{ p.rating }}</p>
              <div class="mt-2 h-1 overflow-hidden rounded-full bg-claret-800">
                <div class="h-full rounded-full bg-amber-400 transition-all" :style="`width:${p.bar}%`"/>
              </div>
              <p class="mt-1.5 text-[10px] text-claret-400">{{ p.count }} reviews</p>
            </div>
          </div>
        </div>
        <div class="mt-10 h-px w-full bg-gradient-to-r from-amber-500 via-amber-400/40 to-transparent"/>
      </div>
    </section>

    <!-- ── Grade distribution — unique data visualisation ─────────────────── -->
    <section class="bg-parchment-100 border-b border-parchment-300 py-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-8 lg:grid-cols-[1fr_auto]">
          <div>
            <p class="mb-5 text-[11px] font-bold uppercase tracking-widest text-amber-700">Grade outcomes — all 8,200+ orders</p>
            <div class="space-y-2.5">
              <div v-for="g in gradeBreakdown" :key="g.grade" class="flex items-center gap-4">
                <span class="w-8 shrink-0 text-right text-sm font-extrabold text-ink-DEFAULT">{{ g.grade }}</span>
                <div class="relative h-7 flex-1 overflow-hidden rounded-full bg-parchment-300">
                  <div
                    class="absolute inset-y-0 left-0 rounded-full transition-all"
                    :class="g.color"
                    :style="`width:${g.pct}%`"
                  />
                  <span class="absolute inset-y-0 left-3 flex items-center text-xs font-bold text-white mix-blend-luminosity">{{ g.pct }}%</span>
                </div>
                <span class="w-16 shrink-0 text-xs text-ink-muted">{{ g.count }}</span>
              </div>
            </div>
          </div>
          <!-- Subject breakdown -->
          <div class="lg:w-60">
            <p class="mb-4 text-[11px] font-bold uppercase tracking-widest text-amber-700">By subject area</p>
            <ul class="space-y-2">
              <li v-for="d in disciplines" :key="d.name" class="flex items-center justify-between gap-3 text-sm">
                <span class="text-ink-secondary">{{ d.name }}</span>
                <span class="font-bold text-ink-DEFAULT">{{ d.count }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Reviews — editorial masonry ───────────────────────────────────── -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="columns-1 gap-5 sm:columns-2 lg:columns-3 [column-fill:balance]">
          <div
            v-for="r in reviews"
            :key="r.name"
            class="mb-5 break-inside-avoid overflow-hidden rounded-2xl border border-parchment-300 bg-white shadow-sm"
          >
            <!-- University header band -->
            <div class="border-b border-parchment-300 bg-parchment-100 px-4 py-2 text-[11px] font-semibold text-ink-muted">
              {{ r.university }}
            </div>
            <div class="p-5">
              <!-- Stars + grade badge -->
              <div class="mb-3 flex items-center justify-between gap-2">
                <div class="flex gap-0.5">
                  <Star v-for="i in r.stars" :key="i" class="h-3.5 w-3.5 fill-amber-400 text-amber-400"/>
                </div>
                <div class="flex size-10 flex-col items-center justify-center rounded-xl bg-claret-900 shadow">
                  <span class="text-sm font-extrabold leading-none text-amber-400">{{ r.grade }}</span>
                </div>
              </div>
              <!-- Quote -->
              <p class="text-sm leading-relaxed text-ink-secondary">"{{ r.quote }}"</p>
              <!-- Byline -->
              <div class="mt-4 flex items-end justify-between gap-2 border-t border-parchment-300 pt-3">
                <div>
                  <p class="text-xs font-bold text-ink-DEFAULT">{{ r.name }}</p>
                  <p class="text-xs text-ink-muted">{{ r.subject }}</p>
                </div>
                <div class="text-right">
                  <span class="block rounded-full border border-parchment-300 bg-parchment-100 px-2 py-0.5 text-[10px] font-medium text-ink-secondary">{{ r.level }}</span>
                  <span class="mt-1 block text-[11px] text-ink-muted">{{ r.date }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA — left-aligned on claret ──────────────────────────────────── -->
    <section class="bg-claret-950">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-8 py-16 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-4xl text-white">Work with a researcher<br />who has done this before.</h2>
            <p class="mt-4 text-claret-200">Research papers from $15/page. Grade or money back. Human-written, always.</p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row lg:justify-end">
            <a :href="app.order" class="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-600 px-7 py-3.5 text-sm font-bold text-white shadow transition-colors hover:bg-amber-500">
              Start my order
            </a>
            <a href="/pricing" class="inline-flex items-center justify-center rounded-xl border border-claret-700 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:border-claret-500">
              See pricing →
            </a>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>
