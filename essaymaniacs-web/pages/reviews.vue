<script setup lang="ts">
import { ArrowRight, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Student Reviews — 9,400+ Verified Reviews | EssayManiacs',
  description: 'Read verified student reviews of EssayManiacs. 4.8/5 average from 9,400+ reviews. Real grades, real subjects, real writers who know your field.',
  ogTitle: 'EssayManiacs Student Reviews — 4.8/5',
  ogDescription: '9,400+ verified student reviews. Essays matched to subject specialists. Grade or money back.',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/reviews' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: 'EssayManiacs',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '9400', bestRating: '5' },
    }),
  }],
})

const platforms = [
  { name: 'Trustpilot', rating: '4.8', count: '5,800+' },
  { name: 'SiteJabber', rating: '4.7', count: '2,400+' },
  { name: 'Google',     rating: '4.9', count: '1,200+' },
]

const gradeBreakdown = [
  { grade: 'A+', pct: 38, color: 'bg-emerald-500' },
  { grade: 'A',  pct: 44, color: 'bg-brand-600'   },
  { grade: 'A−', pct: 12, color: 'bg-violet-500'  },
  { grade: 'B+', pct:  6, color: 'bg-slate-400'   },
]

const reviews = [
  { grade: 'A−', name: 'Jake M.',    subject: 'History',         level: 'Undergraduate',  date: 'May 2026',      quote: "Needed an argumentative essay on colonial African history with 24 hours notice. Got back something I actually learned from — solid sourcing, a real argument, not a generic overview." },
  { grade: 'A',  name: 'Amara L.',   subject: 'Psychology',      level: "Master's",        date: 'May 2026',      quote: "My thesis literature review was structurally broken. They rebuilt it completely — gaps I hadn't noticed, sources I'd missed. Worth every penny and more." },
  { grade: 'A+', name: 'Sophie C.',  subject: 'Literature',      level: 'Doctoral',        date: 'April 2026',    quote: "Surprised by how much the reflective essay sounded like me — only a sharper, more articulate version of me. Not generic. Not AI. Will absolutely use again." },
  { grade: 'A',  name: 'Kwame D.',   subject: 'Philosophy',      level: 'Undergraduate',   date: 'April 2026',    quote: "Asked for a Kantian analysis of contemporary bioethics. Came back with something my professor actually commented on positively in seminar. Genuinely impressed." },
  { grade: 'A',  name: 'Chloe N.',   subject: 'Sociology',       level: 'Undergraduate',   date: 'March 2026',    quote: "Three different services before this one. EssayManiacs is the only one where the writer understood what my professor was actually looking for, not just what the assignment sheet said." },
  { grade: 'A',  name: 'Riya P.',    subject: 'Law',             level: "Master's",        date: 'March 2026',    quote: "Contract law essay, two days, LLM level. The writer cited cases I hadn't considered and built a stronger argument than my own draft. Distinction." },
  { grade: 'A+', name: 'Liam F.',    subject: 'Media Studies',   level: 'Undergraduate',   date: 'February 2026', quote: "Critical discourse analysis of social media rhetoric. Genuinely analytical, not just descriptive. My tutor asked me to present it to the seminar group." },
  { grade: 'A−', name: 'Priya S.',   subject: 'Economics',       level: "Master's",        date: 'February 2026', quote: "Ordered a 3,000-word policy paper on quantitative easing at 11 pm. Delivered at 8 am. Clear, well-argued, every claim evidenced. Grade guarantee was never needed." },
  { grade: 'A',  name: 'Marcus T.',  subject: 'Political Science', level: 'Undergraduate',  date: 'January 2026',  quote: "IR theory essay on constructivism and state behaviour. The writer knew Wendt, knew Waltz, argued the distinction intelligently. Not a textbook summary — a real argument." },
  { grade: 'A',  name: 'Dana H.',    subject: 'English',         level: 'Undergraduate',   date: 'January 2026',  quote: "Close reading of Toni Morrison for my Victorian lit module (wrong subject, long story). The writer politely flagged the mismatch and still delivered something excellent." },
  { grade: 'A+', name: 'Fatima R.',  subject: 'Business',        level: "Master's",        date: 'December 2025', quote: "MBA case study on international market entry. Real analysis, real frameworks applied properly — not just labelled. My study group wanted to read it after I mentioned the grade." },
  { grade: 'A',  name: 'Owen B.',    subject: 'Environmental Science', level: 'Undergraduate', date: 'December 2025', quote: "Research essay on carbon pricing policy. Well-sourced, current (2024 data), structurally tight. First service that actually met my word count without padding." },
]

const subjects = [
  'History', 'Psychology', 'Literature', 'Philosophy', 'Sociology', 'Law',
  'Economics', 'Political Science', 'Media Studies', 'Business', 'Biology',
  'Chemistry', 'Engineering', 'Statistics', 'Finance', 'Education', 'Nursing',
  'Environmental Science', 'Marketing', 'Criminal Justice',
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute -top-32 right-0 h-[500px] w-[500px] rounded-full bg-brand-500 opacity-20 blur-[120px]" />

      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Verified reviews</p>
        <h1 class="text-4xl font-extrabold text-white sm:text-5xl">Grades speak for themselves.</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-brand-200">
          9,400+ students have trusted us with their essays. Here's what they got back.
        </p>

        <!-- Platform ratings -->
        <div class="mt-10 flex flex-wrap justify-center gap-6">
          <div v-for="p in platforms" :key="p.name" class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <div class="flex items-center justify-center gap-0.5 mb-1">
              <Star v-for="i in 5" :key="i" class="h-4 w-4 fill-amber-400 text-amber-400" />
            </div>
            <p class="text-xl font-extrabold text-white">{{ p.rating }}</p>
            <p class="text-xs text-brand-300">{{ p.name }} · {{ p.count }}</p>
          </div>
        </div>

        <!-- Grade breakdown -->
        <div class="mx-auto mt-10 max-w-lg rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm text-left">
          <p class="mb-3 text-xs font-bold uppercase tracking-wider text-brand-300">Grade outcomes on submitted work</p>
          <div class="space-y-2">
            <div v-for="g in gradeBreakdown" :key="g.grade" class="flex items-center gap-3">
              <span class="w-8 text-right text-sm font-bold text-white">{{ g.grade }}</span>
              <div class="flex-1 overflow-hidden rounded-full bg-white/10">
                <div class="h-2.5 rounded-full transition-all" :class="g.color" :style="`width:${g.pct}%`" />
              </div>
              <span class="w-8 text-xs text-brand-300">{{ g.pct }}%</span>
            </div>
          </div>
          <p class="mt-3 text-[11px] text-brand-400">Based on self-reported outcomes from 4,200+ students who shared their marked paper.</p>
        </div>
      </div>
    </section>

    <!-- ── Subject strip ──────────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 bg-slate-50 py-4">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap gap-2 justify-center">
          <span
            v-for="s in subjects" :key="s"
            class="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600"
          >{{ s }}</span>
        </div>
      </div>
    </div>

    <!-- ── Reviews grid ───────────────────────────────────────────────────── -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="columns-1 gap-5 sm:columns-2 lg:columns-3 [column-fill:balance]">
          <div
            v-for="r in reviews"
            :key="r.name"
            class="group mb-5 break-inside-avoid rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
          >
            <!-- Stars + grade badge -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-0.5">
                <Star v-for="i in 5" :key="i" class="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
              </div>
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-900 text-sm font-extrabold text-white shadow-sm">
                {{ r.grade }}
              </div>
            </div>

            <p class="mt-3 text-sm leading-relaxed text-slate-700">"{{ r.quote }}"</p>

            <div class="mt-4 flex items-end justify-between gap-2 border-t border-slate-100 pt-3">
              <div>
                <p class="text-xs font-bold text-slate-900">{{ r.name }}</p>
                <p class="text-xs text-slate-500">{{ r.subject }} · {{ r.level }}</p>
              </div>
              <span class="text-[11px] text-slate-400 shrink-0">{{ r.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-16 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-extrabold text-white">Your essay. Your subject. Your grade.</h2>
        <p class="mt-3 text-brand-200">Subject specialists in 100+ fields. Essays from $10/page.</p>
        <a
          :href="app.order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Start my essay <ArrowRight class="h-4 w-4" />
        </a>
      </div>
    </section>

  </div>
</template>
