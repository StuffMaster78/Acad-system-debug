<script setup lang="ts">
import { ArrowRight, CheckCircle2, HelpCircle } from '@lucide/vue'
import PricingCalculator from '~/components/ui/PricingCalculator.vue'
import { ACADEMIC_LEVELS, DEADLINES, WRITER_TIERS } from '~/composables/usePricing'

const app = useAppUrl()

useSeoMeta({
  title: 'Pricing — Academic Writing Service from $13/Page | GradeCrest',
  description: 'Transparent academic writing prices. Essays from $13/page. Price depends on academic level, deadline, and page count. No hidden fees. Grade or money back.',
  ogTitle: 'GradeCrest Pricing — From $13/Page',
  ogDescription: 'Simple, transparent academic writing prices. No hidden fees. Grade or money back guarantee.',
})

useSeoBase('https://gradecrest.com/pricing')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Pricing', url: 'https://gradecrest.com/pricing' },
])
useFaqLd([
  { q: 'How is the price calculated?', a: 'Price depends on your academic level, deadline, and number of pages. You see the exact total before paying.' },
  { q: 'What counts as one page?', a: '275 words, double-spaced — the standard academic page.' },
  { q: 'Are there any hidden fees?', a: 'No. Title page, references, plagiarism report, and formatting are all included free.' },
  { q: 'Can I get a discount?', a: 'Yes. First-order discount available. Loyalty points earned on every order convert to future discounts.' },
])

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'PriceSpecification',
      price: '13.00',
      minPrice: '13.00',
      maxPrice: '65.00',
      priceCurrency: 'USD',
      description: 'Academic writing service pricing — price depends on level, deadline, and page count.',
    }),
  }],
})

const included = [
  'Title page', 'Reference list', 'Plagiarism report',
  'AI-detection certificate (on request)', 'Formatting (APA, MLA, Chicago, Harvard…)',
  'Unlimited revisions within revision window', 'Direct writer communication',
]

const faqs = [
  { q: 'How is the price calculated?',        a: 'Three variables: your academic level, your deadline, and the number of pages (1 page = 275 words). You see the exact total before you pay.' },
  { q: 'What counts as one page?',             a: '275 words double-spaced in 12pt Times New Roman — the academic standard. Single-spaced counts as two pages.' },
  { q: 'Are there any hidden fees?',           a: 'None. Title page, references, plagiarism report, and standard formatting are all included. What the calculator shows is what you pay.' },
  { q: 'Can I get a discount?',                a: 'Yes. New customers receive an introductory offer. Returning customers earn loyalty points on every order that convert to discounts.' },
  { q: 'Why do rush orders cost more?',        a: 'Short deadlines mean a writer must prioritise your order above others. The surcharge compensates them for working under time pressure.' },
  { q: 'What is the revision policy?',         a: 'Unlimited free revisions within 14 days of delivery (longer for dissertations). If the work does not meet your stated requirements, we refund in full.' },
]
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-forest-950 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gold-400 mb-3">Transparent pricing</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Simple, honest pricing</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">
          From $13/page. What you see is what you pay. No hidden fees, ever.
        </p>
      </div>
    </section>

    <!-- Calculator + included -->
    <section class="bg-mist py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-10 items-start">
          <div>
            <h2 class="text-2xl font-bold text-ink mb-6">Get an instant quote</h2>
            <PricingCalculator />
          </div>
          <div class="space-y-6">
            <div>
              <h2 class="text-2xl font-bold text-ink mb-1">What's included — always free</h2>
              <p class="text-sm text-graphite mb-4">Every order includes these at no extra charge.</p>
              <ul class="space-y-2.5">
                <li v-for="item in included" :key="item" class="flex items-center gap-3 text-sm text-ink">
                  <CheckCircle2 class="size-4 text-gc-600 shrink-0" />
                  {{ item }}
                </li>
              </ul>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
              <p class="text-sm font-semibold text-ink mb-1">Grade or money back</p>
              <p class="text-sm text-graphite leading-relaxed">If the completed work does not meet your stated grade requirement, we rewrite it for free. If still unsatisfied, we refund in full — no questions asked.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Level × deadline table -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-ink mb-2">Pricing by level & deadline</h2>
        <p class="text-sm text-graphite mb-8">Prices shown per page (275 words) for Standard writer tier.</p>
        <div class="overflow-x-auto rounded-2xl border border-slate-200 shadow-card">
          <table class="min-w-full text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-graphite">Academic Level</th>
                <th v-for="dl in DEADLINES" :key="dl.key" class="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wide text-graphite whitespace-nowrap">
                  {{ dl.label }}
                  <span v-if="dl.urgent" class="ml-1 rounded-full bg-rose-100 px-1.5 text-[10px] font-bold text-rose-600">Rush</span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="lvl in ACADEMIC_LEVELS" :key="lvl.key" class="hover:bg-mist transition-colors">
                <td class="px-5 py-3 font-medium text-ink">{{ lvl.label }}</td>
                <td v-for="dl in DEADLINES" :key="dl.key" class="px-4 py-3 text-center tabular-nums text-graphite">
                  ${{ (lvl.base * dl.multiplier).toFixed(0) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Writer tiers -->
    <section class="bg-mist py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-ink mb-2 text-center">Writer tiers</h2>
        <p class="text-sm text-graphite text-center mb-10">All tiers are verified experts. Choose based on seniority and complexity of your work.</p>
        <div class="grid gap-5 sm:grid-cols-3">
          <div
            v-for="tier in WRITER_TIERS" :key="tier.key"
            class="rounded-2xl border bg-white p-6 shadow-card"
            :class="tier.key === 'advanced' ? 'border-gc-300 ring-1 ring-gc-300' : 'border-slate-200'"
          >
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-base font-bold text-ink">{{ tier.label }}</h3>
              <span v-if="tier.badge" class="rounded-full bg-gc-50 px-2.5 py-0.5 text-xs font-bold text-gc-700">{{ tier.badge }}</span>
            </div>
            <p class="text-sm text-graphite mb-4">{{ tier.desc }}</p>
            <p class="text-sm font-semibold text-ink">
              {{ tier.multiplier === 1 ? 'Base price' : `+${Math.round((tier.multiplier - 1) * 100)}% on base` }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-3xl px-4 sm:px-6">
        <h2 class="text-2xl font-bold text-ink text-center mb-10">Pricing questions answered</h2>
        <div class="space-y-3">
          <details v-for="faq in faqs" :key="faq.q" class="group rounded-2xl border border-slate-200 bg-white shadow-card">
            <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
              {{ faq.q }}
              <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45">+</span>
            </summary>
            <p class="px-6 pb-5 text-sm text-graphite leading-relaxed">{{ faq.a }}</p>
          </details>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-forest-950 py-14 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-xl px-4 space-y-5">
        <h2 class="text-2xl font-bold text-white">Ready to place your order?</h2>
        <p class="text-slate-300 text-sm">The calculator shows your exact price. No surprises at checkout.</p>
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
