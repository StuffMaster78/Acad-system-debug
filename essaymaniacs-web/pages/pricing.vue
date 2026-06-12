<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Essay Writing Pricing — From $10/Page | EssayManiacs',
  description: 'Transparent academic writing prices. Essays from $10/page. No hidden fees. Grade or money back guarantee.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/pricing' }] })

const levels = [
  { label: 'High School',         from: 15, note: 'Grades 9–12',          color: 'bg-slate-50 border-slate-200' },
  { label: 'Undergraduate 1–2',   from: 18, note: 'Freshman & Sophomore', color: 'bg-brand-50 border-brand-100' },
  { label: 'Undergraduate 3–4',   from: 22, note: 'Junior & Senior',      color: 'bg-brand-50 border-brand-200' },
  { label: "Master's",            from: 28, note: 'Graduate level',       color: 'bg-brand-50 border-brand-300' },
  { label: 'PhD / Doctoral',      from: 36, note: 'Dissertation-level',   color: 'bg-brand-100 border-brand-400' },
]

const deadlines = [
  { label: '14 days',   hours: 336, surcharge: 0,    badge: 'Best price', badgeColor: 'bg-green-100 text-green-700' },
  { label: '10 days',   hours: 240, surcharge: 5,    badge: null, badgeColor: '' },
  { label: '7 days',    hours: 168, surcharge: 10,   badge: null, badgeColor: '' },
  { label: '5 days',    hours: 120, surcharge: 15,   badge: null, badgeColor: '' },
  { label: '3 days',    hours: 72,  surcharge: 20,   badge: null, badgeColor: '' },
  { label: '24 hours',  hours: 24,  surcharge: 35,   badge: 'Rush', badgeColor: 'bg-amber-100 text-amber-700' },
  { label: '12 hours',  hours: 12,  surcharge: 50,   badge: 'Urgent', badgeColor: 'bg-orange-100 text-orange-700' },
  { label: '6 hours',   hours: 6,   surcharge: 65,   badge: 'Emergency', badgeColor: 'bg-red-100 text-red-700' },
]

const writerTiers = [
  {
    name: 'Standard',
    emoji: '🎓',
    credential: "Master's degree",
    from: 'Base price',
    fromColor: 'text-slate-700',
    features: ['Master\'s degree or higher', 'Verified credentials', '4.0–4.9★ rating', 'Ideal for most assignments'],
    highlight: false,
    badge: null,
  },
  {
    name: 'Advanced',
    emoji: '⭐',
    credential: "Master's, top-rated",
    from: '+10%',
    fromColor: 'text-amber-600',
    features: ['Top-rated writers only', '4.8+★ rating', '500+ completed orders', 'Recommended for dissertations'],
    highlight: true,
    badge: 'Best value',
  },
  {
    name: 'Expert',
    emoji: '🔬',
    credential: 'PhD / Doctoral',
    from: '+20%',
    fromColor: 'text-brand-600',
    features: ['PhD-level specialists', 'Doctoral-level work', '1,000+ completed orders', 'For PhD & publication work'],
    highlight: false,
    badge: 'Premium',
  },
]

const faqs = [
  { q: 'How is the price calculated?',
    a: 'Price is based on your academic level, deadline, and page count (1 page = 275 words, double-spaced). Your exact total is shown at checkout before any payment is taken.' },
  { q: 'What counts as one page?',
    a: '275 words, double-spaced, 12pt Times New Roman or equivalent — the standard academic page count used across most universities.' },
  { q: 'Are there any hidden fees?',
    a: 'No. The price you see in the calculator is the price you pay. Plagiarism report, AI-detection certificate and revisions are included free.' },
  { q: 'What\'s the refund policy?',
    a: 'Grade or money back. If the completed work doesn\'t meet your stated requirements, we rewrite it free or issue a full refund.' },
  { q: 'Do rush orders cost more?',
    a: 'Yes — deadlines shorter than 7 days carry a surcharge to prioritise your order. For the best price, order with as much lead time as possible.' },
  { q: 'Can I negotiate with my writer?',
    a: 'Pricing is set via the platform to protect both parties. You can message your writer directly once the order is placed.' },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">Transparent pricing</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">
          From <span class="text-amber-400">$15/page.</span><br class="hidden sm:block" />
          No surprises. No hidden fees.
        </h1>
        <p class="mx-auto mt-5 max-w-xl text-lg text-brand-200">
          Your exact price is confirmed at checkout before any payment is taken. Use the calculator below to see your total instantly.
        </p>
        <div class="mt-4 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-brand-300">
          <span>✓ Plagiarism report included free</span>
          <span>✓ Revisions included free</span>
          <span>✓ Grade or money back</span>
        </div>
      </div>
    </section>

    <!-- ── Live calculator ────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-16">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-6 text-center text-xs font-bold uppercase tracking-widest text-brand-600">Get your instant quote</p>
        <MultiStepOrderForm />
      </div>
    </section>

    <!-- ── Price by level ─────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Starting prices</p>
          <h2 class="text-3xl font-bold text-slate-900">Price by academic level</h2>
          <p class="mt-2 text-slate-500">Standard 14-day deadline. Deadline surcharges shown below.</p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <div
            v-for="level in levels"
            :key="level.label"
            class="flex flex-col items-center rounded-2xl border p-6 text-center"
            :class="level.color"
          >
            <p class="text-xs font-semibold text-slate-500">{{ level.note }}</p>
            <p class="mt-2 text-base font-bold text-slate-900">{{ level.label }}</p>
            <p class="mt-3 text-3xl font-extrabold tabular-nums text-brand-700">${{ level.from }}</p>
            <p class="text-xs text-slate-400">per page</p>
          </div>
        </div>
        <p class="mt-5 text-center text-xs text-slate-400">1 page = 275 words, double-spaced. Exact total at checkout.</p>
      </div>
    </section>

    <!-- ── Writer tiers ───────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="mb-12 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Writer tiers</p>
          <h2 class="text-3xl font-bold text-slate-900">Choose your level of expertise</h2>
          <p class="mt-2 text-slate-500">All tiers include the same guarantees. Higher tiers unlock more experienced specialists.</p>
        </div>

        <div class="grid gap-6 md:grid-cols-3">
          <div
            v-for="tier in writerTiers"
            :key="tier.name"
            class="relative flex flex-col rounded-2xl border bg-white p-8 shadow-sm"
            :class="tier.highlight ? 'border-brand-400 ring-2 ring-brand-400 ring-offset-2' : 'border-slate-200'"
          >
            <div v-if="tier.badge" class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-600 px-4 py-1 text-xs font-bold text-white shadow">
              {{ tier.badge }}
            </div>
            <div class="mb-4 text-4xl">{{ tier.emoji }}</div>
            <h3 class="text-xl font-bold text-slate-900">{{ tier.name }}</h3>
            <p class="text-sm text-slate-500">{{ tier.credential }}</p>
            <p class="mt-3 text-2xl font-extrabold" :class="tier.fromColor">{{ tier.from }}</p>
            <ul class="mt-5 flex-1 space-y-2">
              <li v-for="f in tier.features" :key="f" class="flex items-start gap-2 text-sm text-slate-600">
                <span class="mt-0.5 text-brand-500">✓</span>{{ f }}
              </li>
            </ul>
            <a :href="app.order" class="mt-6 block rounded-xl py-2.5 text-center text-sm font-bold transition-colors" :class="tier.highlight ? 'bg-brand-600 text-white hover:bg-brand-700' : 'border border-brand-200 text-brand-600 hover:bg-brand-50'">
              Order with {{ tier.name }}
            </a>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Deadline surcharges ────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="mb-10 text-center">
          <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-600">Deadline pricing</p>
          <h2 class="text-3xl font-bold text-slate-900">Rush vs. standard deadlines</h2>
          <p class="mt-2 text-slate-500">Ordering early gets you the best price — and the best writer selection.</p>
        </div>

        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="grid grid-cols-3 border-b border-slate-100 bg-slate-50 px-5 py-3 text-xs font-bold uppercase tracking-wider text-slate-400">
            <span>Deadline</span>
            <span class="text-center">Surcharge</span>
            <span class="text-right">Type</span>
          </div>
          <div v-for="dl in deadlines" :key="dl.label" class="grid grid-cols-3 items-center border-b border-slate-100 px-5 py-3.5 last:border-0 hover:bg-slate-50 transition-colors">
            <span class="text-sm font-semibold text-slate-800">{{ dl.label }}</span>
            <span class="text-center text-sm font-bold" :class="dl.surcharge === 0 ? 'text-green-600' : 'text-slate-700'">
              {{ dl.surcharge === 0 ? 'Standard' : `+${dl.surcharge}%` }}
            </span>
            <span class="flex justify-end">
              <span v-if="dl.badge" class="rounded-full px-2.5 py-0.5 text-[11px] font-bold" :class="dl.badgeColor">{{ dl.badge }}</span>
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── FAQ ────────────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="mb-10 text-center">
          <h2 class="text-3xl font-bold text-slate-900">Pricing questions answered</h2>
        </div>
        <div class="space-y-4">
          <details v-for="faq in faqs" :key="faq.q" class="group rounded-2xl border border-slate-200 bg-white">
            <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-slate-800">
              {{ faq.q }}
              <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-400 transition-transform group-open:rotate-45">+</span>
            </summary>
            <p class="px-6 pb-5 text-sm leading-relaxed text-slate-500">{{ faq.a }}</p>
          </details>
        </div>
      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-16 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-bold text-white">Ready to get an exact quote?</h2>
        <p class="mt-3 text-brand-200">Fill in your brief above — your total is confirmed before you pay anything.</p>
        <a :href="app.order" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow transition-colors hover:bg-brand-50">
          Start my order — from $10/page
        </a>
      </div>
    </section>

  </div>
</template>
