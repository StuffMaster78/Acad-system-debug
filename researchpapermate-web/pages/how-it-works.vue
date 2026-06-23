<script setup lang="ts">
import { markRaw } from 'vue'
import { Banknote, GraduationCap, Bot, RefreshCw } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'How It Works | ResearchPaperMate',
  description: 'How ResearchPaperMate works: submit your brief, pay securely, get matched with a subject expert, communicate directly, and download your paper.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/how-it-works' }] })

const steps = [
  {
    n: '01',
    title: 'Fill in your brief',
    sub: 'Takes 2 minutes',
    desc: 'Tell us your assignment type, academic level, deadline, word count, and any rubric or reading list. The more detail you provide upfront, the better the match.',
    bullets: [
      'Paper type — essay, research paper, dissertation, case study, lab report',
      'Academic level — high school through PhD',
      'Deadline — as fast as 3 hours or up to 14 days',
      'Citation style — APA, MLA, Harvard, Chicago, Vancouver',
      'Attach rubrics, reading lists, or grading criteria',
    ],
  },
  {
    n: '02',
    title: 'Pay into secure escrow',
    sub: 'Your payment is protected',
    desc: 'Pay via card or PayPal. Your money is held in escrow — it is only released to your writer after you have approved the completed paper. You pay nothing if we cannot fulfil your order.',
    bullets: [
      'Visa, Mastercard, PayPal accepted',
      'Payment held in escrow until you approve',
      '256-bit SSL encryption on all transactions',
      'Full refund if we cannot find a matching writer',
    ],
  },
  {
    n: '03',
    title: 'Your expert gets to work',
    sub: 'Direct communication throughout',
    desc: 'We match your order with a verified specialist whose degree and subject background align with your requirements. Message them directly, share files, track progress — no support tickets.',
    bullets: [
      'Matched by subject area, not just academic level',
      "Master's writers for undergraduate assignments",
      'PhD writers for dissertations and doctoral work',
      'Direct messaging — no third-party intermediaries',
      'Writer can share drafts and flag questions proactively',
    ],
  },
  {
    n: '04',
    title: 'Review, revise, download',
    sub: 'Unlimited free revisions included',
    desc: 'Download your completed paper in Word or PDF. Your plagiarism report is included free. Request as many revisions as you need within the revision window. Grade guarantee applies from day one.',
    bullets: [
      'Download via your dashboard (Word, PDF)',
      'Free Turnitin plagiarism report included',
      'Free AI-detection certificate on request',
      'Unlimited free revisions within the revision window',
      'Grade guarantee — rewrite or full refund if target missed',
    ],
  },
]

const guarantees = [
  { icon: markRaw(Banknote), title: 'Escrow protection', desc: 'Your money only moves to your writer when you approve the work.' },
  { icon: markRaw(GraduationCap), title: 'Grade guarantee', desc: "Miss your grade target? We rewrite free or refund completely." },
  { icon: markRaw(Bot), title: 'Zero AI', desc: 'Every paper is human-written. AI-detection report available free.' },
  { icon: markRaw(RefreshCw), title: 'Free revisions', desc: 'Unlimited revisions within the revision window — always free.' },
]
</script>

<template>
  <div>

    <!-- ── Page masthead — slim, typographic ─────────────────────────────── -->
    <section class="bg-claret-950 pt-16 pb-0">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <p class="text-[11px] font-bold uppercase tracking-widest text-amber-500">The process</p>
        <h1 class="mt-3 font-serif text-5xl text-white sm:text-6xl">How it works.</h1>
        <p class="mt-4 max-w-xl text-lg text-claret-200">From brief to finished paper. Four steps, clear as a research methodology.</p>
        <!-- Amber rule divider -->
        <div class="mt-10 h-px w-full bg-gradient-to-r from-amber-500 via-amber-400/40 to-transparent"/>
      </div>
    </section>

    <!-- ── Steps — continuous timeline, left-anchored ─────────────────────── -->
    <section class="bg-parchment-100 py-0">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="relative">
          <!-- Vertical timeline thread -->
          <div class="absolute left-[31px] top-0 bottom-0 w-px bg-amber-200 sm:left-[39px]"/>

          <div v-for="(step, i) in steps" :key="step.n" class="relative grid gap-8 py-14 sm:grid-cols-[80px_1fr] border-b border-parchment-300 last:border-0">
            <!-- Step number bubble -->
            <div class="relative z-10 flex size-16 shrink-0 flex-col items-center justify-center rounded-2xl bg-claret-900 text-center shadow-lg">
              <span class="text-[10px] font-bold uppercase tracking-widest text-amber-400">Step</span>
              <span class="text-xl font-extrabold leading-none text-white">{{ step.n }}</span>
            </div>

            <!-- Content -->
            <div class="pt-2">
              <p class="text-[11px] font-bold uppercase tracking-widest text-amber-700">{{ step.sub }}</p>
              <h2 class="mt-1.5 font-serif text-3xl text-ink-DEFAULT">{{ step.title }}</h2>
              <p class="mt-4 max-w-xl leading-relaxed text-ink-secondary">{{ step.desc }}</p>
              <ul class="mt-5 grid gap-2 sm:grid-cols-2">
                <li v-for="b in step.bullets" :key="b" class="flex items-start gap-2 text-sm text-ink-secondary">
                  <span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500"/>
                  {{ b }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Guarantees — white with amber accents ──────────────────────────── -->
    <section class="bg-white py-16 border-y border-parchment-300">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <p class="mb-8 text-center text-[11px] font-bold uppercase tracking-widest text-amber-700">What's always included</p>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="g in guarantees" :key="g.title" class="rounded-2xl border border-parchment-300 bg-parchment-50 p-6 text-center">
            <div class="mb-3 flex justify-center">
              <component :is="g.icon" class="h-8 w-8 text-slate-600" />
            </div>
            <h3 class="font-bold text-ink-DEFAULT">{{ g.title }}</h3>
            <p class="mt-2 text-xs leading-relaxed text-ink-secondary">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA — split layout ─────────────────────────────────────────────── -->
    <section class="bg-claret-900">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid items-center gap-8 py-16 lg:grid-cols-2">
          <div>
            <h2 class="font-serif text-4xl text-white">Ready to get started?</h2>
            <p class="mt-4 text-claret-200">Takes 2 minutes to fill in your brief. Free quote before you pay anything. No account required.</p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row lg:justify-end">
            <a :href="app.order" class="inline-flex items-center justify-center gap-2 rounded-xl bg-amber-600 px-7 py-3.5 text-sm font-bold text-white shadow transition-colors hover:bg-amber-500">
              Start my order — from $15/page
            </a>
            <a href="/pricing" class="inline-flex items-center justify-center rounded-xl border border-claret-700 px-7 py-3.5 text-sm font-semibold text-white transition-colors hover:border-claret-500 hover:bg-claret-800">
              See pricing →
            </a>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>
