<script setup lang="ts">
import { ArrowRight, CheckCircle2, Clock, DollarSign, Lock, MessageSquare, RefreshCw, Shield } from '@lucide/vue'
import { markRaw } from 'vue'

const app = useAppUrl()

useSeoMeta({
  title: 'How It Works — Place Your Order in 2 Minutes | GradeCrest',
  description: 'Learn how GradeCrest works. Fill your brief, pay securely, communicate with your writer, and download your paper. Grade or money back. From $13/page.',
})

useSeoBase('https://gradecrest.com/how-it-works')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'How It Works', url: 'https://gradecrest.com/how-it-works' },
])

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'HowTo',
      name: 'How to order from GradeCrest',
      description: 'Order a custom academic paper in four simple steps.',
      step: [
        { '@type': 'HowToStep', position: 1, name: 'Fill in your brief', text: 'Submit your topic, deadline, academic level, and any instructions or files.' },
        { '@type': 'HowToStep', position: 2, name: 'Pay securely', text: 'Your payment is held in escrow and only released when you approve the work.' },
        { '@type': 'HowToStep', position: 3, name: 'Communicate with your writer', text: 'Message your assigned expert directly at any time through the platform.' },
        { '@type': 'HowToStep', position: 4, name: 'Download and review', text: 'Receive your paper and request unlimited free revisions if needed.' },
      ],
    }),
  }],
})

const steps = [
  {
    n: '01', icon: markRaw(MessageSquare), color: 'bg-gc-50 text-gc-600',
    title: 'Fill in your brief',
    desc: 'Tell us what you need. Subject, paper type, academic level, deadline, word count, and any specific instructions, reading materials, or rubric files.',
    details: ['Takes less than 2 minutes', 'No account required to get a quote', 'Attach files, rubrics, and reading lists', 'Describe grade expectations in plain language'],
  },
  {
    n: '02', icon: markRaw(Lock), color: 'bg-emerald-50 text-emerald-600',
    title: 'Secure checkout',
    desc: 'Pay securely via card or PayPal. Your payment is held in escrow — it is only released to your writer after you approve the completed work.',
    details: ['Visa, Mastercard, American Express, PayPal', 'Payment held in escrow until you approve', '256-bit SSL encryption on all transactions', 'No charge if we cannot fulfil your order'],
  },
  {
    n: '03', icon: markRaw(MessageSquare), color: 'bg-amber-50 text-amber-600',
    title: 'Communicate with your writer',
    desc: 'A verified subject expert is assigned and begins work. Message them directly, share additional files, and check progress at any point in the process.',
    details: ['Direct writer messaging included free', 'Share additional instructions at any time', 'Request progress updates or early drafts', 'Your writer stays with your order through revisions'],
  },
  {
    n: '04', icon: markRaw(RefreshCw), color: 'bg-violet-50 text-violet-600',
    title: 'Review and download',
    desc: 'Receive your paper alongside a plagiarism report. Read it carefully and request any changes — revisions are free and unlimited within the revision window.',
    details: ['Plagiarism report included on delivery', 'AI-detection certificate on request', 'Unlimited free revisions within the window', 'Full refund if requirements are not met'],
  },
]

const guarantees = [
  { icon: markRaw(Shield),    title: 'Your payment is protected', desc: 'Funds are held in escrow until you approve the work. You are never charged for work that is not delivered.' },
  { icon: markRaw(Lock),      title: 'Complete confidentiality',  desc: 'Your identity, order details, and personal data are never shared with any third party under any circumstances.' },
  { icon: markRaw(DollarSign),title: 'Grade or money back',       desc: 'If the work does not meet your stated requirements, we rewrite it free of charge or issue a full refund.' },
  { icon: markRaw(Clock),     title: 'On-time delivery — always', desc: 'If your paper is delivered late, you are entitled to a partial or full refund depending on the delay.' },
]
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-navy-900 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">Simple process</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">How GradeCrest works</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">
          From brief to delivered in four steps. Place your order in under two minutes.
        </p>
      </div>
    </section>

    <!-- Steps -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 space-y-8">
        <div
          v-for="step in steps" :key="step.n"
          class="grid sm:grid-cols-[auto_1fr] gap-6 rounded-2xl border border-slate-200 bg-white p-7 shadow-card"
        >
          <div class="flex flex-col items-center gap-3 sm:items-start">
            <span class="text-5xl font-extrabold text-slate-100 leading-none select-none">{{ step.n }}</span>
            <div class="flex size-12 items-center justify-center rounded-xl" :class="step.color">
              <component :is="step.icon" class="size-6" />
            </div>
          </div>
          <div>
            <h2 class="text-xl font-bold text-ink">{{ step.title }}</h2>
            <p class="mt-2 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
            <ul class="mt-4 grid gap-2 sm:grid-cols-2">
              <li v-for="d in step.details" :key="d" class="flex items-center gap-2 text-sm text-ink">
                <CheckCircle2 class="size-4 text-gc-600 shrink-0" />
                {{ d }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="mt-10 text-center">
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order now <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

    <!-- Guarantees -->
    <section class="bg-mist py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-ink text-center mb-8">Your order is protected</h2>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="g in guarantees" :key="g.title" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <component :is="g.icon" class="size-7 text-gc-600 mb-3" />
            <h3 class="text-sm font-semibold text-ink">{{ g.title }}</h3>
            <p class="mt-1.5 text-xs text-graphite leading-relaxed">{{ g.desc }}</p>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>
