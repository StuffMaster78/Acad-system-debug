<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Pricing — From $15/Page',
  description: 'Transparent academic writing prices. Research papers from $15/page. Rates vary by academic level, deadline, and subject complexity.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://researchpapermate.com/pricing' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'PriceSpecification',
      price: '15.00',
      priceCurrency: 'USD',
      name: 'Research Paper Writing Service — Starting Price',
    }),
  }],
})

const levels = [
  { label: 'High School',          from: 15, note: 'Grades 9–12' },
  { label: 'Undergraduate (1–2)',  from: 18, note: 'Freshman & Sophomore' },
  { label: 'Undergraduate (3–4)',  from: 22, note: 'Junior & Senior' },
  { label: "Master's",             from: 28, note: 'Graduate level' },
  { label: 'PhD / Doctoral',       from: 36, note: 'Dissertation-level' },
]

const deadlines = [
  { label: '14 days',   modifier: 'Standard',   badge: '' },
  { label: '7 days',    modifier: '+10%',        badge: '' },
  { label: '3 days',    modifier: '+20%',        badge: '' },
  { label: '24 hours',  modifier: '+35%',        badge: 'Rush' },
  { label: '12 hours',  modifier: '+50%',        badge: 'Urgent' },
  { label: '2–6 hours', modifier: '+65%',        badge: 'Emergency' },
]

const writerTiers = [
  {
    name: 'Standard',
    badge: '',
    modifier: 'Base price',
    modColor: 'text-green-600',
    features: ['Master\'s degree or higher', 'Verified credentials', '4.0–4.9 star rating', 'Good for most orders'],
    cta: 'Most popular',
    highlight: false,
  },
  {
    name: 'Advanced',
    badge: 'Best value',
    modifier: '+10%',
    modColor: 'text-amber-600',
    features: ['Top-rated writers only', '4.8+ star rating', '500+ completed orders', 'Recommended for dissertations'],
    cta: 'Recommended',
    highlight: true,
  },
  {
    name: 'Expert',
    badge: 'Premium',
    modifier: '+20%',
    modColor: 'text-brand-600',
    features: ['PhD-level writers', 'Doctoral work specialists', '1,000+ completed orders', 'For PhD & publication-level work'],
    cta: 'For doctoral work',
    highlight: false,
  },
]

const faqs = [
  { q: 'How is the price calculated?',
    a: 'Price is based on academic level, deadline, and page count (1 page = 275 words, double-spaced). You\'ll see an exact quote before paying.' },
  { q: 'What counts as one page?',
    a: '275 words, double-spaced, 12pt Times New Roman or equivalent — the standard academic page.' },
  { q: 'Are there discounts?',
    a: 'Yes. You earn loyalty points with every order that convert to discounts. First-time customers also get an introductory offer.' },
  { q: 'What\'s the refund policy?',
    a: 'Grade or money back. If the completed work doesn\'t meet the stated requirements, we rewrite it for free or issue a refund.' },
  { q: 'Do rush orders cost more?',
    a: 'Yes — deadlines shorter than 7 days carry a surcharge. For the best price, order as early as possible.' },
  { q: 'Can I talk to the writer before paying?',
    a: 'You can message your assigned writer directly once the order is placed. Direct communication is included at no extra cost.' },
]
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Simple, Transparent Pricing</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-brand-100">
          Prices start at <strong>$15/page</strong> and depend on your academic level and deadline. No hidden fees.
        </p>
      </div>
    </section>

    <!-- Level pricing -->
    <section class="section">
      <h2 class="section-heading text-center">Price by academic level</h2>
      <p class="section-sub text-center">Standard 14-day deadline. Rush deadlines adjust the rate below.</p>
      <div class="mt-10 overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th class="px-6 py-4 text-left">Academic Level</th>
              <th class="px-6 py-4 text-left text-slate-400 font-normal">Typical for</th>
              <th class="px-6 py-4 text-right">From (per page)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="level in levels" :key="level.label" class="bg-white hover:bg-slate-50 transition-colors">
              <td class="px-6 py-4 font-medium text-slate-800">{{ level.label }}</td>
              <td class="px-6 py-4 text-slate-400">{{ level.note }}</td>
              <td class="px-6 py-4 text-right font-bold text-brand-700">${{ level.from }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="mt-4 text-center text-xs text-slate-400">
        Exact quote shown at checkout before any payment is taken.
      </p>
    </section>

    <!-- Writer tiers -->
    <section class="bg-slate-50">
      <div class="section">
        <h2 class="section-heading text-center">Choose your writer tier</h2>
        <p class="section-sub text-center">All tiers include the same guarantees. Higher tiers give access to more experienced writers.</p>
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
              <p class="mt-1 text-sm font-semibold" :class="tier.modColor">{{ tier.modifier }}</p>
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
          All writer tiers include: free revisions · plagiarism report · grade or money back · on-time guarantee
        </p>
      </div>
    </section>

    <!-- Deadline modifiers -->
    <section class="bg-slate-50">
      <div class="section">
        <h2 class="section-heading text-center">Deadline adjustments</h2>
        <p class="section-sub text-center">Order early for the best rate.</p>
        <div class="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="d in deadlines" :key="d.label"
            class="card flex items-center justify-between">
            <div>
              <span v-if="d.badge"
                class="mb-1 inline-block rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">
                {{ d.badge }}
              </span>
              <p class="font-semibold text-slate-900">{{ d.label }}</p>
            </div>
            <span class="text-sm font-medium" :class="d.modifier === 'Standard' ? 'text-green-600' : 'text-slate-500'">
              {{ d.modifier }}
            </span>
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
      <p class="section-sub text-center">Pick your level and deadline — see your total instantly.</p>
      <div class="mt-10">
        <ClientOnly>
          <OrderCalculator />
          <template #fallback><div class="h-72 animate-pulse rounded-2xl bg-slate-100" /></template>
        </ClientOnly>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-700 py-16 text-center">
      <h2 class="font-serif text-3xl font-bold text-white">Get your exact quote now</h2>
      <p class="mt-4 text-brand-200">Fill in your requirements — see a precise price before paying anything.</p>
      <NuxtLink to="/register"
        class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base">
        Place an order — from $15/page
      </NuxtLink>
      <p class="mt-4 text-sm text-brand-200">Grade or money back · Free revisions · 24/7 support</p>
    </section>
  </div>
</template>
