<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Nursing Paper Pricing — From $24/Page | NurseMyGrade',
  description: 'Transparent nursing paper prices. BSN-level work from $24/page. MSN and DNP writers available. Price by academic level, deadline, and writer tier. No hidden fees.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/pricing' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'PriceSpecification',
      price: '24.00',
      priceCurrency: 'USD',
      name: 'Nursing Paper Writing Service — Starting Price',
    }),
  }],
})

const levels = [
  { label: 'ADN / Associate Level',  from: 24, note: 'Associate Degree in Nursing coursework' },
  { label: 'BSN Undergraduate',      from: 26, note: 'Pre-licensure BSN programmes' },
  { label: 'RN-to-BSN Bridge',       from: 26, note: 'RN-to-BSN completion programmes' },
  { label: "MSN / Graduate",         from: 32, note: 'Master of Science in Nursing' },
  { label: 'DNP / Doctoral',         from: 40, note: 'Doctor of Nursing Practice & PhD' },
]

const deadlines = [
  { label: '14 days',   modifier: 'Standard',   badge: '' },
  { label: '7 days',    modifier: '+10%',        badge: '' },
  { label: '3 days',    modifier: '+20%',        badge: '' },
  { label: '24 hours',  modifier: '+35%',        badge: 'Rush' },
  { label: '12 hours',  modifier: '+50%',        badge: 'Urgent' },
  { label: '3–6 hours', modifier: '+65%',        badge: 'Emergency' },
]

const writerTiers = [
  {
    name: 'Registered Nurse',
    badge: '',
    credential: 'BSN, RN',
    modifier: 'Base price',
    modColor: 'text-green-600',
    features: [
      'BSN-qualified with active RN licence',
      'Verified clinical experience',
      '4.0–4.9 star rating',
      'Ideal for BSN and RN-to-BSN work',
    ],
    cta: 'Most popular',
    highlight: false,
  },
  {
    name: 'Advanced Nurse Writer',
    badge: 'Best value',
    credential: 'MSN, RN',
    modifier: '+10%',
    modColor: 'text-amber-600',
    features: [
      'MSN-qualified, top-rated writers',
      '4.8+ star rating, 200+ nursing papers',
      'Graduate-level theory & research',
      'Recommended for MSN capstones',
    ],
    cta: 'Recommended',
    highlight: true,
  },
  {
    name: 'Expert Nurse Scholar',
    badge: 'Premium',
    credential: 'DNP / PhD, RN',
    modifier: '+20%',
    modColor: 'text-brand-600',
    features: [
      'DNP or PhD-qualified nurse writers',
      '500+ doctoral nursing papers',
      'EBP, quality improvement, policy',
      'For DNP projects and dissertations',
    ],
    cta: 'For DNP / doctoral work',
    highlight: false,
  },
]

const faqs = [
  {
    q: 'How is the price calculated?',
    a: 'Price depends on your nursing programme level, deadline, and page count (1 page = 275 words, double-spaced, APA 7th). You see an exact quote before paying — no surprises.',
  },
  {
    q: 'What counts as one page?',
    a: '275 words, double-spaced, 12pt Times New Roman — the standard academic page. Care plans and SOAP notes are priced by the full document, not per page.',
  },
  {
    q: 'Are there discounts?',
    a: 'Yes. Return clients earn loyalty points that convert to discounts. New clients also receive an introductory code — check the announcement bar at the top of the site.',
  },
  {
    q: 'What\'s the refund policy?',
    a: 'Grade or money back. If the completed paper doesn\'t meet your stated requirements and rubric, we rewrite it free or issue a full refund.',
  },
  {
    q: 'Do urgent nursing orders cost more?',
    a: 'Yes — deadlines under 7 days carry a rush surcharge. For the best price on a care plan or dissertation, place your order as early as possible.',
  },
  {
    q: 'Can I communicate with my nurse writer?',
    a: 'Yes. You message your assigned writer directly through the dashboard from the moment they accept your order. Share your rubric, notes, and clinical scenario details at no extra cost.',
  },
]
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Simple, Transparent Pricing</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-brand-100">
          Nursing papers start at <strong class="text-white">$24/page</strong> — written by a BSN, MSN,
          or DNP nurse matched to your subject. No hidden fees. Exact price shown before you pay.
        </p>
      </div>
    </section>

    <!-- Level pricing table -->
    <section class="section">
      <h2 class="section-heading text-center">Price by nursing programme level</h2>
      <p class="section-sub text-center">Standard 14-day deadline. Rush deadlines add a surcharge — see below.</p>
      <div class="mt-10 overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th class="px-6 py-4 text-left">Nursing Level</th>
              <th class="px-6 py-4 text-left font-normal text-slate-400">Typical for</th>
              <th class="px-6 py-4 text-right">From (per page)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="level in levels" :key="level.label" class="bg-white transition-colors hover:bg-slate-50">
              <td class="px-6 py-4 font-medium text-slate-800">{{ level.label }}</td>
              <td class="px-6 py-4 text-slate-400">{{ level.note }}</td>
              <td class="px-6 py-4 text-right font-bold text-brand-700">${{ level.from }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="mt-4 text-center text-xs text-slate-400">
        Care plans, SOAP notes, and simulations priced per document — exact quote shown at checkout.
      </p>
    </section>

    <!-- Writer tiers -->
    <section class="bg-slate-50">
      <div class="section">
        <h2 class="section-heading text-center">Choose your nurse writer tier</h2>
        <p class="section-sub text-center">
          All tiers carry the same guarantees. Higher tiers give access to more experienced nurses with advanced degrees.
        </p>
        <div class="mt-10 grid gap-6 md:grid-cols-3">
          <div
            v-for="tier in writerTiers"
            :key="tier.name"
            class="card relative flex flex-col"
            :class="tier.highlight ? 'ring-2 ring-brand-600 shadow-lg' : ''"
          >
            <div v-if="tier.badge" class="absolute -top-3 left-1/2 -translate-x-1/2">
              <span class="rounded-full bg-brand-600 px-3 py-1 text-xs font-bold text-white shadow">{{ tier.badge }}</span>
            </div>
            <div class="mb-4">
              <h3 class="text-lg font-bold text-slate-900">{{ tier.name }}</h3>
              <p class="mt-0.5 text-xs font-semibold text-slate-400 uppercase tracking-wide">{{ tier.credential }}</p>
              <p class="mt-1.5 text-sm font-semibold" :class="tier.modColor">{{ tier.modifier }}</p>
            </div>
            <ul class="flex-1 space-y-2 text-sm text-slate-600">
              <li v-for="f in tier.features" :key="f" class="flex items-start gap-2">
                <span class="mt-0.5 font-bold text-brand-500">✓</span>{{ f }}
              </li>
            </ul>
            <NuxtLink
              to="/register"
              class="mt-6 block rounded-lg py-2.5 text-center text-sm font-semibold transition-colors"
              :class="tier.highlight
                ? 'bg-brand-600 text-white hover:bg-brand-700'
                : 'border border-brand-200 text-brand-700 hover:bg-brand-600 hover:border-brand-600 hover:text-white'"
            >
              {{ tier.cta }}
            </NuxtLink>
          </div>
        </div>
        <p class="mt-6 text-center text-xs text-slate-400">
          All tiers include: free revisions · Turnitin report · AI-detection report · grade or money back · on-time guarantee
        </p>
      </div>
    </section>

    <!-- Deadline modifiers -->
    <section class="bg-white">
      <div class="section">
        <h2 class="section-heading text-center">Deadline adjustments</h2>
        <p class="section-sub text-center">Plan ahead for the best rate. Rush orders are always available.</p>
        <div class="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="d in deadlines"
            :key="d.label"
            class="card flex items-center justify-between"
          >
            <div>
              <span
                v-if="d.badge"
                class="mb-1 inline-block rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700"
              >{{ d.badge }}</span>
              <p class="font-semibold text-slate-900">{{ d.label }}</p>
            </div>
            <span
              class="text-sm font-medium"
              :class="d.modifier === 'Standard' ? 'text-green-600' : 'text-slate-500'"
            >{{ d.modifier }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section>
      <div class="section">
        <h2 class="section-heading text-center">Pricing FAQ</h2>
        <dl class="mt-10 grid gap-6 md:grid-cols-2">
          <div v-for="faq in faqs" :key="faq.q" class="card">
            <dt class="font-semibold text-slate-900">{{ faq.q }}</dt>
            <dd class="mt-2 text-sm text-slate-600 leading-relaxed">{{ faq.a }}</dd>
          </div>
        </dl>
      </div>
    </section>

    <!-- Calculator -->
    <section class="section max-w-2xl">
      <h2 class="section-heading text-center">Try the price calculator</h2>
      <p class="section-sub text-center">Pick your nursing level and deadline — see your exact price instantly.</p>
      <div class="mt-10">
        <ClientOnly>
          <OrderCalculator />
          <template #fallback><div class="h-72 animate-pulse rounded-2xl bg-slate-100" /></template>
        </ClientOnly>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-700 py-16 text-center">
      <h2 class="font-serif text-3xl font-bold text-white">Get your exact nursing paper quote</h2>
      <p class="mt-4 text-brand-200">Enter your requirements — see a precise price before paying anything.</p>
      <NuxtLink
        to="/register"
        class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base"
      >
        Place an order — from $24/page
      </NuxtLink>
      <p class="mt-4 text-sm text-brand-200">Grade or money back · Free revisions · Written by real nurses · 24/7 support</p>
    </section>
  </div>
</template>
