<script setup lang="ts">
const { promo, visible, init } = usePromoDisplay()
onMounted(init)

useSeoMeta({
  title: 'Nursing Paper Discounts & Promo Codes | NurseMyGrade',
  description: 'Save on expert nursing papers. First-order discounts, loyalty rewards, referral credits, and seasonal promos — all in one place. See current deals and how to earn more.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://nursemygrade.com/discounts' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Does NurseMyGrade offer first-order discounts?',
          acceptedAnswer: { '@type': 'Answer', text: 'Yes. New clients receive a first-order discount automatically at checkout — no code needed. The discount is applied when you place your first nursing paper order.' },
        },
        {
          '@type': 'Question',
          name: 'How do loyalty rewards work?',
          acceptedAnswer: { '@type': 'Answer', text: 'Every completed order earns loyalty points. Points can be redeemed for discount codes, which are delivered to your account and can be used on future orders.' },
        },
        {
          '@type': 'Question',
          name: 'Is there a referral discount?',
          acceptedAnswer: { '@type': 'Answer', text: 'Yes. Refer a classmate and both of you receive a discount code when they complete their first order. Share your referral link from your account dashboard.' },
        },
      ],
    }),
  }],
})

const ways = [
  {
    icon: '🎓',
    title: 'First-Order Discount',
    badge: 'Auto-applied',
    desc: 'New to NurseMyGrade? Your first order discount is applied automatically at checkout — nothing to enter.',
    cta: 'Place first order',
    href: '/order',
  },
  {
    icon: '⭐',
    title: 'Loyalty Rewards',
    badge: 'Earn with every order',
    desc: 'Every completed paper earns you loyalty points. Redeem them for discount codes through your account dashboard.',
    cta: 'View my rewards',
    href: '/login',
  },
  {
    icon: '👥',
    title: 'Refer a Classmate',
    badge: 'Both of you save',
    desc: "Share your unique referral link. When your classmate completes their first order, you both receive a discount code.",
    cta: 'Get referral link',
    href: '/login',
  },
  {
    icon: '📅',
    title: 'Seasonal Promos',
    badge: 'Check the strip above',
    desc: 'Holiday and exam-season deals run throughout the year. Follow us on social or check back here for active codes.',
    cta: 'Browse services',
    href: '/services',
  },
  {
    icon: '💰',
    title: 'Spend-Tier Rewards',
    badge: 'Returning clients',
    desc: 'Hit a lifetime spend milestone and unlock a standing discount code — the more you order, the more you save.',
    cta: 'See pricing',
    href: '/pricing',
  },
]

const faqs = [
  { q: 'Can I stack two discount codes?', a: 'Stacking depends on your account tier and the specific codes. Most promotional codes cannot be combined, but a loyalty reward can sometimes stack with a spend-tier code. The checkout page will show you the best available deal.' },
  { q: 'Do discount codes expire?', a: 'Seasonal and promotional codes have a listed expiry. Loyalty reward codes are valid for 90 days after issue. Your portal dashboard shows the expiry date for each personal code.' },
  { q: 'Does a discount apply to urgent orders?', a: 'Yes — discounts apply to the base price before rush modifiers. So a 10% off code on a 12-hour urgent order saves 10% of the base rate.' },
  { q: 'What if my promo code is not working?', a: 'Make sure the code is entered in capitals with no extra spaces. Check whether it has expired or has already been used. If the issue persists, contact support and we will look into it for you.' },
]
</script>

<template>
  <div>

    <!-- Active promo banner -->
    <Transition name="slide-down">
      <div v-if="visible && promo" class="relative bg-brand-700 px-4 py-3 text-center text-sm font-medium text-white">
        <span v-if="promo.badge_text" class="mr-2 rounded-full bg-white/20 px-2 py-0.5 text-xs font-bold uppercase tracking-wide">{{ promo.badge_text }}</span>
        <span>{{ promo.headline }}</span>
        <span v-if="promo.subtext" class="ml-2 opacity-80">{{ promo.subtext }}</span>
        <code v-if="promo.discount_code" class="ml-2 rounded bg-white/20 px-2 py-0.5 font-mono text-xs tracking-widest">{{ promo.discount_code }}</code>
        <NuxtLink v-if="promo.cta_label && promo.cta_url" :to="promo.cta_url" class="ml-3 underline underline-offset-2 hover:no-underline">{{ promo.cta_label }}</NuxtLink>
      </div>
    </Transition>

    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-900 via-brand-800 to-teal-900 px-4 py-20 text-center text-white">
      <div class="mx-auto max-w-3xl">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Savings &amp; Promotions</p>
        <h1 class="font-serif text-4xl font-bold leading-tight sm:text-5xl">Nursing paper discounts<br>you actually earn</h1>
        <p class="mt-5 text-lg text-brand-100 leading-relaxed">First-order deals, loyalty points, referral credits, and seasonal promos — every way to save on expert nursing papers, all in one place.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-3">
          <NuxtLink to="/order" class="rounded-xl bg-white px-6 py-3 text-sm font-bold text-brand-800 shadow transition hover:bg-brand-50">Place an order</NuxtLink>
          <NuxtLink to="/login" class="rounded-xl border border-white/30 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Sign in to redeem</NuxtLink>
        </div>
      </div>
    </section>

    <!-- Ways to save -->
    <section class="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <h2 class="mb-3 text-center font-serif text-2xl font-bold text-slate-900">Ways to save</h2>
      <p class="mb-10 text-center text-slate-500">Five earning paths — combine them to stack savings across every order.</p>
      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="w in ways" :key="w.title" class="flex flex-col rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <div class="mb-4 flex items-start justify-between gap-3">
            <span class="text-3xl">{{ w.icon }}</span>
            <span class="rounded-full bg-brand-50 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-brand-700">{{ w.badge }}</span>
          </div>
          <h3 class="mb-2 text-base font-bold text-slate-900">{{ w.title }}</h3>
          <p class="mb-5 flex-1 text-sm leading-relaxed text-slate-500">{{ w.desc }}</p>
          <NuxtLink :to="w.href" class="text-sm font-semibold text-brand-700 hover:text-brand-800">{{ w.cta }} →</NuxtLink>
        </div>
      </div>
    </section>

    <!-- How it works strip -->
    <section class="border-y border-slate-100 bg-slate-50 px-4 py-14">
      <div class="mx-auto max-w-4xl text-center">
        <h2 class="mb-10 font-serif text-2xl font-bold text-slate-900">How to redeem a discount code</h2>
        <div class="grid gap-6 sm:grid-cols-3">
          <div v-for="(step, i) in [
            { n: 1, title: 'Start your order', text: 'Go to the order page and configure your nursing paper — academic level, deadline, and subject.' },
            { n: 2, title: 'Enter your code', text: 'Expand the "Have a discount code?" field on the order form and type or paste your code.' },
            { n: 3, title: 'See the saving', text: 'The discount is applied instantly to your total. Confirm and pay the reduced amount.' },
          ]" :key="i" class="flex flex-col items-center">
            <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-brand-700 text-sm font-bold text-white">{{ step.n }}</div>
            <h3 class="mb-1.5 text-sm font-bold text-slate-900">{{ step.title }}</h3>
            <p class="text-sm text-slate-500 leading-relaxed">{{ step.text }}</p>
          </div>
        </div>
        <NuxtLink to="/order" class="mt-10 inline-flex items-center gap-2 rounded-xl bg-brand-700 px-6 py-3 text-sm font-bold text-white shadow transition hover:bg-brand-800">Place an order →</NuxtLink>
      </div>
    </section>

    <!-- FAQ -->
    <section class="mx-auto max-w-3xl px-4 py-16 sm:px-6">
      <h2 class="mb-8 font-serif text-2xl font-bold text-slate-900">Discount FAQs</h2>
      <div class="divide-y divide-slate-100 rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
        <details v-for="faq in faqs" :key="faq.q" class="group px-5 py-4">
          <summary class="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-slate-900">
            {{ faq.q }}
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 transition-transform group-open:rotate-45 text-xs font-bold">+</span>
          </summary>
          <p class="mt-3 text-sm text-slate-500 leading-relaxed">{{ faq.a }}</p>
        </details>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-800 px-4 py-16 text-center text-white">
      <div class="mx-auto max-w-xl">
        <h2 class="font-serif text-2xl font-bold">Ready to place your order?</h2>
        <p class="mt-3 text-brand-200 text-sm">Expert BSN, MSN, and DNP nurses. Grade or money back.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-3">
          <NuxtLink to="/order" class="rounded-xl bg-white px-6 py-3 text-sm font-bold text-brand-800 shadow transition hover:bg-brand-50">Start my order</NuxtLink>
          <NuxtLink to="/pricing" class="rounded-xl border border-white/30 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10">View pricing</NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from,
.slide-down-leave-to { opacity: 0; transform: translateY(-100%); }
</style>
