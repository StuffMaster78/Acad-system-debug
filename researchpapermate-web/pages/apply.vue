<script setup lang="ts">
import { markRaw } from 'vue'
import { Banknote, Clock, Target, TrendingUp, ShieldCheck, MessageSquare } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Write With Us — Apply as an Academic Researcher',
  description: 'Join 500+ expert writers earning competitive pay on a flexible schedule. Verified degree required. Apply in minutes.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/apply' }] })

const stats = [
  { value: '500+',     label: 'Active researchers',   sub: 'Across 100+ subjects' },
  { value: '$35',      label: 'Avg. per page',         sub: 'Expert tier earns more' },
  { value: '14,700+',  label: 'Orders delivered',      sub: 'And growing' },
  { value: 'Friday',   label: 'Weekly payout',         sub: 'No delays, no surprises' },
]

const perks = [
  { icon: markRaw(Banknote),     title: 'Earn up to $50/page', desc: 'Pay scales with your tier and performance. Expert writers earn 20% above base rate. No ceiling on your earnings.' },
  { icon: markRaw(Clock),        title: 'Work your own hours', desc: 'No fixed shifts. Accept orders that fit your timetable, decline anything that doesn\'t. Log in when you choose.' },
  { icon: markRaw(Target),       title: 'Only your subjects', desc: 'Browse 100+ subject categories. You only see orders in your declared disciplines — no irrelevant requests.' },
  { icon: markRaw(TrendingUp),   title: 'Grow your tier', desc: 'Standard → Advanced → Expert. Each tier unlocks higher-paying orders and better assignment access.' },
  { icon: markRaw(ShieldCheck),  title: 'Protected by escrow', desc: 'Your payment is in escrow the moment a client places the order. You get paid even if the client goes quiet.' },
  { icon: markRaw(MessageSquare), title: 'Direct client chat', desc: 'Communicate with clients directly through the platform — no third-party go-betweens or support ticket chains.' },
]

const steps = [
  { n: '01', title: 'Submit your application', desc: 'Fill in our form — takes under 10 minutes. Share your education background and subject specialisms.' },
  { n: '02', title: 'Complete the vetting quiz', desc: 'A brief subject assessment and a short writing sample. We review within 48 hours and give feedback either way.' },
  { n: '03', title: 'Accept your first order', desc: 'Once approved, browse the marketplace. Accept orders that interest you, set your schedule, earn from day one.' },
]

const requirements = [
  "Postgraduate degree (Master's or higher) in your subject area",
  'Academic-level written English with strong citation skills',
  'Ability to research, structure arguments, and cite correctly (APA, MLA, Harvard, Chicago…)',
  'Reliable internet access and ability to meet deadlines',
  'Willingness to communicate professionally with clients through the platform',
]

const testimonials = [
  {
    name: 'Grace M.',
    role: 'MSc Nursing — Senior Writer',
    quote: "I've been writing here for two years. The flexibility is unmatched — I work around my kids and still earn more than at my previous full-time job.",
  },
  {
    name: 'Daniel O.',
    role: 'PhD Economics — Expert Writer',
    quote: "I pick the orders that interest me academically. I've published papers in my own name and still find the client work stimulating. The pay is genuinely competitive.",
  },
  {
    name: 'Amara N.',
    role: 'MSc Public Health — Advanced Writer',
    quote: "The escrow system was the thing that convinced me. I know I'll get paid — no chasing clients, no uncertainty. It's a proper platform.",
  },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-claret-950 py-24">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-parchment-1000 opacity-20 blur-[120px]" />
      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-amber-400">For researchers and writers</p>
        <h1 class="text-4xl font-bold leading-tight text-white sm:text-5xl">
          Turn your degree into<br class="hidden sm:block" /> flexible income.
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-claret-200">
          ResearchPaperMate connects verified academic specialists with students who need expert help. No shifts, no supervisors — work when and how much you choose.
        </p>
        <a :href="app.apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
          Apply now — it's free
          <svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
        </a>
      </div>
    </section>

    <!-- ── Stats ─────────────────────────────────────────────────────────── -->
    <section class="border-b border-slate-100 bg-white">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 divide-x divide-y divide-slate-100 md:grid-cols-4 md:divide-y-0">
          <div v-for="s in stats" :key="s.label" class="flex flex-col items-center py-8 text-center">
            <span class="text-3xl font-extrabold tabular-nums text-claret-700">{{ s.value }}</span>
            <span class="mt-1 text-sm font-semibold text-slate-800">{{ s.label }}</span>
            <span class="mt-0.5 text-xs text-slate-400">{{ s.sub }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Perks ──────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-amber-700">Why writers choose us</p>
          <h2 class="text-3xl font-bold text-slate-900">Work on your terms.</h2>
        </div>
        <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="p in perks" :key="p.title" class="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm transition-shadow hover:shadow-md">
            <div class="mb-4">
              <component :is="p.icon" class="h-8 w-8" />
            </div>
            <h3 class="font-bold text-slate-900">{{ p.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ p.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Process ────────────────────────────────────────────────────────── -->
    <section class="bg-parchment-100 py-20">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-amber-700">Getting started</p>
          <h2 class="text-3xl font-bold text-slate-900">Three steps to your first order.</h2>
        </div>
        <div class="space-y-5">
          <div v-for="step in steps" :key="step.n" class="flex gap-6 rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
            <div class="flex size-12 shrink-0 items-center justify-center rounded-xl border-2 border-claret-200 bg-parchment-100 text-sm font-extrabold text-claret-700">
              {{ step.n }}
            </div>
            <div>
              <h3 class="font-bold text-slate-900">{{ step.title }}</h3>
              <p class="mt-1.5 text-sm leading-relaxed text-slate-500">{{ step.desc }}</p>
            </div>
          </div>
        </div>
        <div class="mt-10 text-center">
          <a :href="app.apply" class="inline-flex items-center gap-2 rounded-xl bg-claret-900 px-8 py-3.5 text-sm font-bold text-white shadow transition-colors hover:bg-claret-900">
            Start your application
          </a>
        </div>
      </div>
    </section>

    <!-- ── Requirements ───────────────────────────────────────────────────── -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h2 class="mb-6 text-xl font-bold text-slate-900">What we're looking for</h2>
        <ul class="space-y-3">
          <li v-for="r in requirements" :key="r" class="flex items-start gap-3 text-sm text-slate-600">
            <span class="mt-0.5 text-amber-600 font-bold">✓</span>
            {{ r }}
          </li>
        </ul>
        <p class="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-5 py-3 text-sm text-amber-800">
          <strong>We do not accept undergraduates.</strong> All writers must hold at minimum a completed Bachelor's degree. Master's and PhD holders are preferred.
        </p>
      </div>
    </section>

    <!-- ── Testimonials ───────────────────────────────────────────────────── -->
    <section class="bg-parchment-100 py-16">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <p class="mb-8 text-center text-xs font-bold uppercase tracking-widest text-amber-700">From our writers</p>
        <div class="grid gap-6 md:grid-cols-3">
          <div v-for="t in testimonials" :key="t.name" class="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
            <blockquote class="text-sm italic leading-relaxed text-slate-700">"{{ t.quote }}"</blockquote>
            <div class="mt-5 flex items-center gap-3 border-t border-slate-100 pt-4">
              <div class="flex size-9 items-center justify-center rounded-full bg-amber-50 text-xs font-bold text-claret-700">{{ t.name.charAt(0) }}</div>
              <div>
                <p class="text-xs font-bold text-slate-800">{{ t.name }}</p>
                <p class="text-xs text-slate-400">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Final CTA ──────────────────────────────────────────────────────── -->
    <section class="bg-claret-950 py-16 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-bold text-white">Ready to apply?</h2>
        <p class="mt-3 text-claret-200">Takes under 10 minutes. We review within 48 hours and give feedback either way.</p>
        <a :href="app.apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
          Apply as a writer
        </a>
      </div>
    </section>

  </div>
</template>
