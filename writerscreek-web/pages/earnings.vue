<script setup lang="ts">
useSeoMeta({
  title: 'Earnings & Writer Rates | Writers Creek',
  description: 'See how much you can earn as a Writers Creek writer. Level-based rates from $18 to $45 per page with bi-weekly payouts.',
  ogImage:       'https://writerscreek.com/og-default.png',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const levels = [
  {
    name: 'Entry',
    rate: '$18–$22',
    rateMin: 18,
    rateMax: 22,
    color: 'border-slate-200 bg-slate-50',
    badge: 'bg-slate-100 text-slate-700',
    desc: 'New writers building their track record on the platform. All assignments are reviewed before delivery to the client.',
    requirements: [
      'Postgraduate degree or professional credential verified',
      'Pass the vetting grammar and subject quiz',
      'First 5 assignments reviewed by senior editor',
    ],
    promotion: 'Progress to Standard after 10 successful assignments with a 4.5+ rating.',
  },
  {
    name: 'Standard',
    rate: '$24–$28',
    rateMin: 24,
    rateMax: 28,
    color: 'border-brand-100 bg-brand-50/50',
    badge: 'bg-brand-100 text-brand-700',
    desc: 'Writers with a consistent quality track record. Higher assignment volume access across more subjects.',
    requirements: [
      'At least 10 completed assignments',
      'Rating of 4.5 or above',
      'No unresolved client disputes',
    ],
    promotion: 'Progress to Senior after 50 assignments with a 4.7+ average rating.',
  },
  {
    name: 'Senior',
    rate: '$30–$36',
    rateMin: 30,
    rateMax: 36,
    color: 'border-sky-200 bg-sky-50/50',
    badge: 'bg-sky-100 text-sky-700',
    desc: 'Proven writers with specialist subject depth. Priority matching for premium assignments and faster deadline slots.',
    requirements: [
      'At least 50 completed assignments',
      'Rating of 4.7 or above',
      'Demonstrated subject expertise in at least one specialism',
    ],
    promotion: 'Progress to Expert by invitation after sustained 4.9+ performance on complex work.',
  },
  {
    name: 'Expert',
    rate: '$38–$45',
    rateMin: 38,
    rateMax: 45,
    color: 'border-brand-400 bg-brand-900 text-white',
    badge: 'bg-brand-400/20 text-brand-300',
    desc: 'Top-tier writers handling dissertation-level and doctoral assignments. First pick of high-value, complex work.',
    requirements: [
      'Invitation-only — based on sustained performance',
      'Rating of 4.9 or above',
      'Doctoral-level or specialist clinical credentials',
    ],
    promotion: 'Expert status is maintained by continued quality delivery.',
  },
]

const payoutFaqs = [
  {
    q: 'When exactly do payouts happen?',
    a: 'Payouts are released every two weeks on a fixed schedule. You will know the exact dates when you join.',
  },
  {
    q: 'What payment methods are supported?',
    a: 'At onboarding you choose between direct bank transfer (SWIFT/SEPA) and PayPal. Both are supported globally.',
  },
  {
    q: 'Is there a minimum payout threshold?',
    a: 'There is a minimum payout of $20 to avoid excessive processing fees. Earnings below this threshold roll over to the next cycle.',
  },
  {
    q: 'How do I move from Entry to Standard?',
    a: 'Complete 10 assignments with a client-approved rating of 4.5 or above. No disputes on file. Your tier is upgraded automatically.',
  },
  {
    q: 'Can my level be demoted?',
    a: 'Yes. Sustained low ratings, missed deadlines, or quality issues can result in a level review. We communicate any changes clearly before they take effect.',
  },
]

const exampleMonths = [
  { scenario: 'Part-time, Entry level',   pages: 20, rate: 20, monthly: 400  },
  { scenario: 'Part-time, Standard level', pages: 20, rate: 26, monthly: 520  },
  { scenario: 'Full-time, Senior level',  pages: 80, rate: 33, monthly: 2640 },
  { scenario: 'Full-time, Expert level',  pages: 80, rate: 42, monthly: 3360 },
]
</script>

<template>
  <div class="bg-white">

    <!-- Hero -->
    <div class="bg-slate-900 px-4 py-16 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Earnings and writer rates</h1>
        <p class="mt-5 text-lg text-slate-300">
          Your rate grows with your performance. Start at $18/page and earn up to $45/page as you build your track record.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-6 text-center">
          <div>
            <p class="text-3xl font-bold text-brand-400">$18–$45</p>
            <p class="text-sm text-slate-400">per page range</p>
          </div>
          <div>
            <p class="text-3xl font-bold text-white">2×/month</p>
            <p class="text-sm text-slate-400">payout frequency</p>
          </div>
          <div>
            <p class="text-3xl font-bold text-white">4 levels</p>
            <p class="text-sm text-slate-400">performance-based</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Level cards -->
    <div class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <h2 class="mb-10 text-center text-2xl font-bold text-slate-900 sm:text-3xl">Writer level rates</h2>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="level in levels"
          :key="level.name"
          class="rounded-2xl border p-6"
          :class="level.color"
        >
          <div class="mb-3">
            <span class="rounded-full px-3 py-1 text-xs font-bold" :class="level.badge">{{ level.name }}</span>
          </div>
          <p class="text-3xl font-black" :class="level.name === 'Expert' ? 'text-white' : 'text-slate-900'">{{ level.rate }}</p>
          <p class="text-sm" :class="level.name === 'Expert' ? 'text-brand-300' : 'text-slate-500'">per page</p>
          <p class="mt-4 text-sm leading-relaxed" :class="level.name === 'Expert' ? 'text-slate-300' : 'text-slate-600'">{{ level.desc }}</p>
          <div class="mt-5 border-t pt-5" :class="level.name === 'Expert' ? 'border-white/10' : 'border-slate-200'">
            <p class="mb-2 text-[11px] font-bold uppercase tracking-wider" :class="level.name === 'Expert' ? 'text-brand-400' : 'text-slate-400'">Requirements</p>
            <ul class="space-y-1.5">
              <li
                v-for="req in level.requirements"
                :key="req"
                class="flex items-start gap-2 text-xs"
                :class="level.name === 'Expert' ? 'text-slate-300' : 'text-slate-600'"
              >
                <span class="mt-0.5 shrink-0" :class="level.name === 'Expert' ? 'text-brand-400' : 'text-brand-500'">✓</span>
                {{ req }}
              </li>
            </ul>
          </div>
          <p class="mt-4 text-[11px] italic" :class="level.name === 'Expert' ? 'text-slate-400' : 'text-slate-400'">{{ level.promotion }}</p>
        </div>
      </div>
    </div>

    <!-- Example monthly earnings -->
    <div class="bg-slate-50 py-16">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <h2 class="mb-3 text-2xl font-bold text-slate-900 sm:text-3xl">Example monthly earnings</h2>
        <p class="mb-10 text-slate-600">Based on approximate page output at illustrative mid-band rates. Actual earnings depend on volume and assignment mix.</p>
        <div class="overflow-hidden rounded-2xl border border-slate-100">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-100 bg-white text-left">
                <th class="px-5 py-3.5 font-semibold text-slate-700">Scenario</th>
                <th class="px-5 py-3.5 font-semibold text-slate-700">Pages/month</th>
                <th class="px-5 py-3.5 font-semibold text-slate-700">Rate/page</th>
                <th class="px-5 py-3.5 font-semibold text-brand-700">Monthly earnings</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr
                v-for="ex in exampleMonths"
                :key="ex.scenario"
                class="bg-white transition-colors hover:bg-slate-50"
              >
                <td class="px-5 py-4 font-medium text-slate-800">{{ ex.scenario }}</td>
                <td class="px-5 py-4 text-slate-600">{{ ex.pages }}</td>
                <td class="px-5 py-4 text-slate-600">${{ ex.rate }}</td>
                <td class="px-5 py-4 font-bold text-brand-700">${{ ex.monthly.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="mt-4 text-xs text-slate-400">Page count estimates assume 275 words per page. Rates shown are mid-band illustrative figures within each level range.</p>
      </div>
    </div>

    <!-- Payout FAQs -->
    <div class="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <h2 class="mb-8 text-2xl font-bold text-slate-900 sm:text-3xl">Payout questions</h2>
      <div class="divide-y divide-slate-100">
        <details
          v-for="faq in payoutFaqs"
          :key="faq.q"
          class="group py-5"
        >
          <summary class="flex cursor-pointer items-center justify-between gap-4 text-base font-semibold text-slate-900 marker:hidden [&::-webkit-details-marker]:hidden">
            {{ faq.q }}
            <svg class="h-5 w-5 shrink-0 text-slate-400 transition-transform group-open:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </summary>
          <p class="mt-3 text-sm leading-relaxed text-slate-600">{{ faq.a }}</p>
        </details>
      </div>
    </div>

    <!-- CTA -->
    <div class="bg-slate-900 py-14">
      <div class="mx-auto max-w-2xl px-4 text-center">
        <h2 class="text-2xl font-bold text-white">Start earning at Writers Creek</h2>
        <p class="mt-3 text-slate-400">Apply today. First assignment in your dashboard within 48 hours of approval.</p>
        <NuxtLink to="/apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-7 py-3.5 text-base font-bold text-white transition-colors hover:bg-brand-500">
          Apply to write →
        </NuxtLink>
      </div>
    </div>

  </div>
</template>
