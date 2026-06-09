<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Write With Us — Apply as a Nurse Writer | NurseMyGrade',
  description: 'Join 500+ BSN, MSN, and DNP nurses earning up to $50/page on a flexible schedule. Turn your clinical expertise into income. Apply in minutes.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/apply' }],
})

const stats = [
  { value: '500+',   label: 'Active nurse writers' },
  { value: '$40',    label: 'Avg. per page (MSN tier)' },
  { value: '4.97★',  label: 'Writer satisfaction' },
  { value: '9,800+', label: 'Nursing papers delivered' },
]

const steps = [
  {
    number: '01',
    title: 'Submit your nursing application',
    desc: 'Fill in our online form in under 10 minutes. Tell us your nursing qualification, licence status, clinical specialties, and years of experience.',
  },
  {
    number: '02',
    title: 'Complete the clinical knowledge quiz',
    desc: 'A short written assessment covering NANDA-I, ADPIE, pharmacology, and clinical documentation. We review everything within 48 hours and give feedback either way.',
  },
  {
    number: '03',
    title: 'Start accepting nursing orders',
    desc: 'Once approved, browse the marketplace filtered to your specialty. Set your own schedule, pick orders that fit, and start earning. Payouts every Friday.',
  },
]

const perks = [
  {
    icon: '💰',
    title: 'Earn up to $50/page',
    desc: 'BSN writers start at $30/page. MSN writers earn $40+. DNP writers earn $50+ per page. Pay scales with your credential level and client ratings.',
  },
  {
    icon: '🕐',
    title: 'Work your own hours',
    desc: 'No fixed shifts. Accept orders that fit your schedule — between shifts, during breaks, or full-time. You control your availability.',
  },
  {
    icon: '🩺',
    title: 'Work in your specialty',
    desc: 'Only see orders in your clinical area. Med-Surg, ICU, Psych, OB, Paeds, FNP — orders are filtered to nurses who know the subject.',
  },
  {
    icon: '📈',
    title: 'Build your nursing reputation',
    desc: 'Every 5-star delivery builds your profile. Higher ratings unlock premium orders, higher base pay, and priority matching.',
  },
  {
    icon: '💳',
    title: 'Weekly payouts',
    desc: 'Earnings processed every Friday via M-Pesa, bank transfer, or PayPal. No hidden deductions, no waiting 30 days.',
  },
  {
    icon: '🛡️',
    title: 'Protected by escrow',
    desc: 'Payment is held in escrow from the moment a client places an order. You get paid even if the client goes quiet.',
  },
]

const requirements = [
  'Active nursing qualification — BSN minimum (MSN/DNP welcomed for advanced work)',
  'Active or recent RN, NP, or clinical nursing licence',
  'Clinical experience relevant to your stated specialty',
  'Strong academic English — ability to write at nursing programme level',
  'Knowledge of NANDA-I, NIC, NOC, ADPIE, SOAP, APA 7th edition',
  'Reliable internet access and ability to meet order deadlines',
]

const testimonials = [
  {
    name: 'Grace W.',
    role: 'MSN, RN — Senior Nurse Writer',
    quote: 'I work ICU nights and write for NurseMyGrade during slow shifts and days off. The orders are genuine nursing work — not the generic academic garbage you see on other platforms. My clinical background actually matters here.',
  },
  {
    name: 'Daniel O.',
    role: 'BSN, RN — Nurse Writer',
    quote: 'The vetting was thorough — they checked my licence and tested my NANDA knowledge, which I respected. It means the clients here are serious students and the pay reflects that. I made my monthly rent from my first 3 weeks.',
  },
]
</script>

<template>
  <div>
    <!-- Hero -->
    <div class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-3xl text-center">
          <span class="mb-6 inline-block rounded-full bg-white/10 px-4 py-1.5 text-sm font-semibold text-brand-200 ring-1 ring-white/20">
            Now accepting applications — BSN, MSN & DNP nurses
          </span>
          <h1 class="font-serif text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            Your nursing expertise<br class="hidden sm:block" /> is worth more
          </h1>
          <p class="mt-6 text-lg leading-relaxed text-brand-200 sm:text-xl">
            Join 500+ BSN, MSN, and DNP nurses earning up to $50 per page on a schedule
            that's entirely yours. Your clinical knowledge is exactly what nursing students need.
          </p>
          <a
            :href="app.apply"
            class="mt-10 inline-flex items-center gap-2 rounded-xl bg-white px-10 py-4 text-base font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
          >
            Start your application
            <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </a>
          <p class="mt-4 text-sm text-brand-300">Takes under 10 minutes · Decisions within 48 hours</p>
        </div>
      </div>
    </div>

    <!-- Stats strip -->
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

    <!-- How it works -->
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">How it works</h2>
        <p class="section-sub">Three steps from application to your first nursing paper payout.</p>
      </div>

      <div class="mt-14 grid gap-8 sm:grid-cols-3">
        <div v-for="step in steps" :key="step.number" class="relative">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-lg font-bold text-white">
            {{ step.number }}
          </div>
          <h3 class="text-lg font-semibold text-slate-900">{{ step.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ step.desc }}</p>
        </div>
      </div>
    </div>

    <!-- Perks -->
    <div class="bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="section-heading">Why nurses choose us</h2>
          <p class="section-sub">Built specifically for nursing professionals — not generic freelancers.</p>
        </div>

        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="perk in perks" :key="perk.title" class="card">
            <span class="text-3xl">{{ perk.icon }}</span>
            <h3 class="mt-4 font-semibold text-slate-900">{{ perk.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ perk.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Requirements -->
    <div class="section">
      <div class="mx-auto max-w-2xl">
        <h2 class="section-heading text-center">What we look for</h2>
        <p class="section-sub text-center">
          We accept nurses only — clinical expertise is non-negotiable. If you're a qualified nurse
          who can write at academic level, you're exactly who we're looking for.
        </p>

        <ul class="mt-10 space-y-4">
          <li v-for="req in requirements" :key="req" class="flex items-start gap-4">
            <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">✓</span>
            <span class="text-slate-700">{{ req }}</span>
          </li>
        </ul>

        <div class="mt-8 rounded-2xl border border-amber-100 bg-amber-50 p-5">
          <p class="text-sm font-semibold text-amber-800">Not a nurse?</p>
          <p class="mt-1 text-sm text-amber-700">
            NurseMyGrade is a nursing-only platform. We do not accept general academic writers,
            regardless of degree level. This is what makes our service different — and it's what
            nursing students are paying for.
          </p>
        </div>
      </div>
    </div>

    <!-- Testimonials -->
    <div class="bg-brand-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="section-heading text-center">Hear from our nurse writers</h2>

        <div class="mx-auto mt-12 grid max-w-3xl gap-8 sm:grid-cols-2">
          <div v-for="t in testimonials" :key="t.name" class="rounded-2xl border border-brand-100 bg-white p-7 shadow-sm">
            <p class="italic leading-relaxed text-slate-700">"{{ t.quote }}"</p>
            <div class="mt-5 flex items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                {{ t.name[0] }}
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ t.name }}</p>
                <p class="text-xs text-slate-500">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom CTA -->
    <div class="section text-center">
      <h2 class="font-serif text-3xl font-bold text-slate-900 sm:text-4xl">
        Ready to put your nursing degree to work?
      </h2>
      <p class="mx-auto mt-4 max-w-xl text-lg text-slate-600">
        Applications take under 10 minutes. We review every submission and send feedback within 48 hours
        — including constructive notes if you're not successful first time.
      </p>
      <a :href="app.apply" class="btn-primary mt-10 px-12 py-4 text-base">
        Apply now — it's free
      </a>
      <p class="mt-4 text-sm text-slate-400">No fees, no commitments. Accept orders on your own terms after approval.</p>
    </div>
  </div>
</template>
