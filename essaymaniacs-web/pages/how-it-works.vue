<script setup lang="ts">
import { markRaw } from 'vue'
import { ClipboardList, Lock, MessageSquare, Download, Banknote, GraduationCap, Bot, RefreshCw } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'How It Works | EssayManiacs',
  description: 'How EssayManiacs works: submit your brief, pay securely, get matched with a subject expert, communicate directly, and download your paper.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/how-it-works' }] })

const steps = [
  {
    n: '01',
    icon: markRaw(ClipboardList),
    title: 'Fill in your brief',
    sub: 'Takes 2 minutes',
    desc: 'Tell us your assignment type, academic level, deadline, word count, and any rubric or reading list. The more you share upfront, the better your match.',
    bullets: [
      'Paper type — essay, research paper, dissertation, case study, lab report…',
      'Academic level — high school through PhD',
      'Deadline — as fast as 3 hours or up to 14 days',
      'Citation style — APA, MLA, Harvard, Chicago, Vancouver…',
      'Attach rubrics, reading lists, or grading criteria',
    ],
    color: 'border-brand-200 bg-brand-50',
    numColor: 'bg-brand-700 text-white',
  },
  {
    n: '02',
    icon: markRaw(Lock),
    title: 'Pay — your money is held safely',
    sub: 'Your payment is in escrow',
    desc: 'Pay via card or PayPal. Your payment is held in escrow by our billing partner — it is only released to your writer after you have approved the completed work.',
    bullets: [
      'Visa, Mastercard, PayPal accepted',
      'Payment held in escrow until you approve',
      '256-bit SSL encryption on all transactions',
      'No charge if we cannot fulfil your order',
    ],
    color: 'border-green-200 bg-green-50',
    numColor: 'bg-green-700 text-white',
  },
  {
    n: '03',
    icon: markRaw(MessageSquare),
    title: 'Your writer gets matched and starts',
    sub: 'Direct communication included',
    desc: 'We match your order to a verified specialist whose degree and subject background align with your requirements. Message them directly, share files, and track progress.',
    bullets: [
      'Matched by subject area, not just academic level',
      "Master's writers for undergraduate work",
      'PhD writers for dissertations and doctoral papers',
      'Direct messaging — no support ticket middlemen',
      'Writer can flag questions and share drafts proactively',
    ],
    color: 'border-amber-200 bg-amber-50',
    numColor: 'bg-amber-600 text-white',
  },
  {
    n: '04',
    icon: markRaw(Download),
    title: 'Download, review, and request revisions',
    sub: 'Free revisions included',
    desc: 'Your writer uploads the completed paper. Download in Word or PDF. Your plagiarism report is included free. Request as many revisions as you need within the revision window.',
    bullets: [
      'Download via your dashboard (Word, PDF)',
      'Free Turnitin plagiarism report included',
      'Free AI-detection certificate available on request',
      'Unlimited free revisions within revision window',
      'Grade guarantee — rewrite or full refund if grade target missed',
    ],
    color: 'border-purple-200 bg-purple-50',
    numColor: 'bg-purple-700 text-white',
  },
]

const guarantees = [
  { icon: markRaw(Banknote), title: 'Escrow payment protection', desc: 'Your money only moves to the writer when you approve the work.' },
  { icon: markRaw(GraduationCap), title: 'Grade or money back', desc: "State your grade target. If we miss it, we rewrite or refund." },
  { icon: markRaw(Bot), title: 'Zero AI content', desc: 'Every paper is human-written. Free AI-detection report on request.' },
  { icon: markRaw(RefreshCw), title: 'Unlimited free revisions', desc: 'Within the revision window, revisions are always free.' },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="relative mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">The process</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">
          From brief to finished paper<br class="hidden sm:block" /> in four steps.
        </h1>
        <p class="mx-auto mt-5 max-w-xl text-lg text-brand-200">
          No account needed to get a quote. No payment until you're matched with a writer. Revisions included throughout.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-brand-300">
          <span>✓ Minimum 3-hour turnaround</span>
          <span>✓ Grade or money back</span>
          <span>✓ Direct writer access</span>
        </div>
      </div>
    </section>

    <!-- ── Steps ─────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-4xl space-y-6 px-4 sm:px-6 lg:px-8">
        <div
          v-for="step in steps"
          :key="step.n"
          class="overflow-hidden rounded-2xl border"
          :class="step.color"
        >
          <div class="flex items-start gap-6 p-8">
            <!-- Step number -->
            <div class="flex size-14 shrink-0 items-center justify-center rounded-2xl text-xl font-extrabold shadow-sm" :class="step.numColor">
              {{ step.n }}
            </div>
            <!-- Content -->
            <div class="flex-1">
              <p class="text-xs font-bold uppercase tracking-wider text-slate-400">{{ step.sub }}</p>
              <h2 class="mt-1 flex items-center gap-2 text-xl font-bold text-slate-900">
                <component :is="step.icon" class="h-5 w-5 shrink-0" />
                {{ step.title }}
              </h2>
              <p class="mt-3 leading-relaxed text-slate-600">{{ step.desc }}</p>
              <ul class="mt-5 grid gap-2 sm:grid-cols-2">
                <li v-for="b in step.bullets" :key="b" class="flex items-start gap-2 text-sm text-slate-600">
                  <span class="mt-0.5 font-bold text-slate-400">—</span>
                  {{ b }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Guarantees ─────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-16">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <p class="mb-8 text-center text-xs font-bold uppercase tracking-widest text-brand-600">What's always included</p>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="g in guarantees" :key="g.title" class="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
            <div class="mb-3 flex justify-center">
              <component :is="g.icon" class="h-8 w-8 text-slate-600" />
            </div>
            <h3 class="font-bold text-slate-900">{{ g.title }}</h3>
            <p class="mt-2 text-xs leading-relaxed text-slate-500">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-20 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-3xl font-bold text-white">Ready to get started?</h2>
        <p class="mt-4 text-brand-200">Takes 2 minutes to fill in your brief. Free quote before you pay anything.</p>
        <a :href="app.order" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
          Start my order — from $10/page
        </a>
        <p class="mt-4 text-xs text-brand-300">No payment until you approve · Free revisions · Grade or money back</p>
      </div>
    </section>

  </div>
</template>
