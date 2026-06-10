<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Write With Us — Apply as an Academic Writer',
  description: 'Join 500+ expert writers earning competitive pay on a flexible schedule. Apply in minutes.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/apply' }] })

const stats = [
  { value: '500+',  label: 'Active writers' },
  { value: '$35',   label: 'Avg. per page' },
  { value: '4.9★',  label: 'Writer satisfaction' },
  { value: '14,700+', label: 'Orders delivered' },
]

const steps = [
  {
    number: '01',
    title: 'Submit your application',
    desc: 'Fill in our online form — it takes less than 10 minutes. Tell us your education background and areas of expertise.',
  },
  {
    number: '02',
    title: 'Complete a short vetting quiz',
    desc: 'A brief subject quiz and a sample writing task. We review everything within 48 hours and give feedback either way.',
  },
  {
    number: '03',
    title: 'Start accepting orders',
    desc: 'Once approved, browse the order marketplace, set your own schedule, and start earning. Payouts processed every Friday.',
  },
]

const perks = [
  { icon: 'dollar-sign',  title: 'Earn up to $50/page',  desc: 'Pay scales with your level and performance. Advanced and Expert writers earn 10–20% more per order.' },
  { icon: 'clock',        title: 'Work your own hours',  desc: 'No fixed shifts. Accept orders that fit your timetable and decline anything that doesn\'t.' },
  { icon: 'trending-up',  title: 'Grow your reputation', desc: 'Build ratings with every delivery. Higher ratings unlock access to premium, better-paying orders.' },
  { icon: 'credit-card',  title: 'Weekly payouts',       desc: 'Earnings are processed every Friday via M-Pesa, bank transfer, or PayPal. No hidden deductions.' },
  { icon: 'target',       title: 'Pick your subjects',   desc: 'Only see orders in your field. 100+ subject categories — from law to engineering to social sciences.' },
  { icon: 'shield-check', title: 'Protected by escrow',  desc: 'Your payment is held in escrow from the moment a client places an order. You get paid even if the client goes quiet.' },
]

const requirements = [
  'University degree or higher (undergraduate, Masters, PhD)',
  'Fluent written English at academic level',
  'Ability to research, write, and cite correctly (APA, MLA, Chicago, etc.)',
  'Reliable internet access and ability to meet deadlines',
  'Availability to communicate with clients through the platform',
]

const testimonials = [
  {
    name: 'Grace M.',
    role: 'MSc Nursing — Senior Writer',
    quote: 'I\'ve been writing here for two years. The flexibility is unmatched — I work around my kids and still earn more than at my previous full-time job.',
  },
  {
    name: 'Daniel O.',
    role: 'PhD Economics — Expert Writer',
    quote: 'The vetting process was thorough, which I actually liked — it means the clients here are serious and the competition is fair.',
  },
]
</script>

<template>
  <div>
    <!-- ── Hero ──────────────────────────────────────────────────── -->
    <div class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-3xl text-center">
          <span class="inline-block rounded-full bg-white/10 px-4 py-1.5 text-sm font-semibold text-brand-200 ring-1 ring-white/20 mb-6">
            Now accepting applications
          </span>
          <h1 class="font-serif text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            Turn your expertise<br class="hidden sm:block" /> into income
          </h1>
          <p class="mt-6 text-lg leading-relaxed text-brand-200 sm:text-xl">
            Join 500+ academic writers earning up to $50 per page on a schedule that's entirely yours.
            No commute. No fixed hours. Just your knowledge and a laptop.
          </p>
          <a :href="app.apply" class="mt-10 inline-flex items-center gap-2 rounded-xl bg-white px-10 py-4 text-base font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
            Start your application
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </a>
          <p class="mt-4 text-sm text-brand-300">Takes less than 10 minutes · Decisions within 48 hours</p>
        </div>
      </div>
    </div>

    <!-- ── Stats strip ────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 bg-white py-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div v-for="s in stats" :key="s.label" class="text-center">
            <p class="font-serif text-3xl font-bold text-brand-700">{{ s.value }}</p>
            <p class="mt-1 text-sm text-slate-500">{{ s.label }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── How it works ───────────────────────────────────────────── -->
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">How it works</h2>
        <p class="section-sub">Three steps from application to your first payout.</p>
      </div>

      <div class="mt-14 grid gap-8 sm:grid-cols-3">
        <div v-for="step in steps" :key="step.number" class="relative">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 font-bold text-white text-lg">
            {{ step.number }}
          </div>
          <h3 class="text-lg font-semibold text-slate-900">{{ step.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ step.desc }}</p>
        </div>
      </div>
    </div>

    <!-- ── Perks ──────────────────────────────────────────────────── -->
    <div class="bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="section-heading">Why writers choose us</h2>
          <p class="section-sub">Everything we've built with our writers in mind.</p>
        </div>

        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="perk in perks" :key="perk.title" class="card">
            <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100">
              <Icon :name="perk.icon" class="h-5 w-5 text-brand-700" />
            </div>
            <h3 class="mt-4 font-semibold text-slate-900">{{ perk.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ perk.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Requirements ───────────────────────────────────────────── -->
    <div class="section">
      <div class="mx-auto max-w-2xl">
        <h2 class="section-heading text-center">What we look for</h2>
        <p class="section-sub text-center">You don't need a PhD — but you do need to be serious about quality.</p>

        <ul class="mt-10 space-y-4">
          <li v-for="req in requirements" :key="req" class="flex items-start gap-4">
            <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700 text-xs font-bold">✓</span>
            <span class="text-slate-700">{{ req }}</span>
          </li>
        </ul>

        <div class="mt-8 rounded-2xl border border-amber-100 bg-amber-50 p-5">
          <p class="text-sm font-semibold text-amber-800">Not a degree holder?</p>
          <p class="mt-1 text-sm text-amber-700">
            ResearchPaperMate requires at minimum an undergraduate degree. We do not accept applicants without verifiable academic credentials, regardless of writing ability — this is what our clients are paying for.
          </p>
        </div>
      </div>
    </div>

    <!-- ── Testimonials ───────────────────────────────────────────── -->
    <div class="bg-brand-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="section-heading text-center">Hear from our writers</h2>

        <div class="mt-12 grid gap-8 sm:grid-cols-2 max-w-3xl mx-auto">
          <div v-for="t in testimonials" :key="t.name" class="rounded-2xl bg-white p-7 shadow-sm border border-brand-100">
            <p class="text-slate-700 leading-relaxed italic">"{{ t.quote }}"</p>
            <div class="mt-5 flex items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {{ t.name[0] }}
              </div>
              <div>
                <p class="font-semibold text-slate-900 text-sm">{{ t.name }}</p>
                <p class="text-xs text-slate-500">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Bottom CTA ─────────────────────────────────────────────── -->
    <div class="section text-center">
      <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">Ready to start earning?</h2>
      <p class="mt-4 text-lg text-slate-600 max-w-xl mx-auto">
        Applications take less than 10 minutes. Our team reviews every submission and sends feedback within 48 hours.
      </p>
      <a :href="app.apply" class="btn-primary mt-10 px-12 py-4 text-base">
        Apply now — it's free
      </a>
      <p class="mt-4 text-sm text-slate-400">No fees, no commitments. Cancel anytime after joining.</p>
    </div>
  </div>
</template>
