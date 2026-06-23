<script setup lang="ts">
const appUrl = useAppUrl()

useSeoMeta({
  title: 'Writers Creek — A Selective Academic Writing Network',
  description: 'Join 2,000+ credentialed writers earning $18–$45 per page. Flexible assignments, bi-weekly payouts, and work matched to your exact academic discipline.',
  ogTitle: 'Writers Creek — Write at the Highest Standard',
  ogDescription: 'Competitive per-page rates, flexible assignments, and reliable bi-weekly payouts for writers who take their craft seriously.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const stats = [
  { value: '2,000+',  label: 'Active writers',       note: 'Across 100+ subjects'       },
  { value: '$18–$45', label: 'Per page earned',       note: 'Level-based rates'          },
  { value: '2×/month', label: 'Payout schedule',     note: 'Reliable, on time'           },
  { value: '4.8/5',  label: 'Writer satisfaction',   note: 'Based on internal surveys'   },
]

const benefits = [
  {
    icon: '💰',
    title: 'Competitive per-page rates',
    desc: 'Entry writers start at $18/page. Senior and Expert writers earn $35–$45/page. Rates increase as you build your reputation on the platform.',
  },
  {
    icon: '📅',
    title: 'Flexible, on your schedule',
    desc: 'Choose assignments that match your availability. No minimum hours, no lock-in. Write one paper a week or twenty — entirely your call.',
  },
  {
    icon: '🎓',
    title: 'Work in your exact discipline',
    desc: 'We match assignments to your subject background. A nursing MSN handles nursing papers. A finance PhD handles quantitative analysis.',
  },
  {
    icon: '💳',
    title: 'Bi-weekly payouts, every time',
    desc: 'Earnings are released every two weeks without fail. Direct bank transfer or PayPal — your choice at onboarding.',
  },
]

const levels = [
  {
    name: 'Entry',
    rate: '$18–$22',
    desc: 'New writers building their track record. All assignments reviewed before client delivery.',
  },
  {
    name: 'Standard',
    rate: '$24–$28',
    desc: 'Consistent quality, positive client feedback. Higher-volume assignment access.',
  },
  {
    name: 'Senior',
    rate: '$30–$36',
    desc: 'Proven track record, specialist subject depth. Premium assignments, priority matching.',
  },
  {
    name: 'Expert',
    rate: '$38–$45',
    desc: 'Top-tier writers. Dissertation-level, doctoral work. Highest pay and first pick of assignments.',
  },
]

const steps = [
  {
    n: '01',
    title: 'Submit your application',
    desc: 'Share your academic background, subject specialisms, and a writing sample. Takes about 10 minutes.',
  },
  {
    n: '02',
    title: 'Complete the vetting quiz',
    desc: 'A short grammar and subject-knowledge assessment. Pass rate is intentional — we are selective for good reason.',
  },
  {
    n: '03',
    title: 'Get your first assignment',
    desc: 'Once approved, assignments matching your subject profile are available immediately. Pick what suits you.',
  },
  {
    n: '04',
    title: 'Deliver and get paid',
    desc: 'Submit your work, client approves, earnings are released. Bi-weekly payouts hit your account without chasing.',
  },
]

const testimonials = [
  {
    initials: 'AK',
    name: 'Dr. A. Kamau',
    subject: 'PhD · Business & Finance',
    quote: 'I have been writing here for two years. The assignments are genuinely academic — not filler content. The pay is fair and the team respects the work.',
    orders: 312,
    rating: 5.0,
  },
  {
    initials: 'MO',
    name: 'Maria O., RN',
    subject: 'MSN · Nursing',
    quote: 'Nursing assignments match my clinical background exactly. I have never been asked to write outside my lane, and the rates reflect the expertise required.',
    orders: 198,
    rating: 5.0,
  },
  {
    initials: 'LT',
    name: 'Dr. L. Thomson',
    subject: 'PhD · Literature',
    quote: 'The vetting kept the quality bar high. I write alongside people who actually know their subjects. It makes a difference in the calibre of work expected.',
    orders: 441,
    rating: 4.9,
  },
]

const subjects = [
  'Nursing', 'Business', 'Psychology', 'Law', 'History', 'Literature',
  'Finance', 'Statistics', 'Biology', 'Chemistry', 'Sociology', 'Philosophy',
  'Engineering', 'Education', 'Public Health', 'Political Science', 'Economics', 'Marketing',
]

const faqs = [
  {
    q: 'How do I qualify to write?',
    a: "You need a postgraduate degree (Master's or PhD) or active clinical credentials in your subject area. We verify credentials before approving any writer.",
  },
  {
    q: 'How much can I earn?',
    a: 'Entry writers earn $18–$22 per page. As you complete assignments and build your rating, you progress through Standard ($24–28), Senior ($30–36), and Expert ($38–45) tiers.',
  },
  {
    q: 'When do I get paid?',
    a: 'Bi-weekly, without fail. Payments are released every two weeks once the client has approved the work. You choose between direct bank transfer and PayPal at sign-up.',
  },
  {
    q: 'How many assignments can I take?',
    a: 'There is no minimum or maximum. Take as many or as few as you want. The platform does not penalise writers for low volume — quality is what matters.',
  },
  {
    q: 'What happens if a client requests revisions?',
    a: 'Revisions within the stated brief are part of the job. If a client requests something outside the original scope, that is flagged and handled separately — you will not be asked to do unlimited unpaid rework.',
  },
  {
    q: 'Is my personal information kept private?',
    a: 'Yes. Your full name, credentials, and contact details are never shared with clients. You interact through the platform under your writer profile name only.',
  },
]
</script>

<template>
  <div>

    <!-- ── HERO ────────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-slate-900 bg-hero-grid bg-grid-28">
      <div class="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28 2xl:max-w-screen-xl 2xl:px-12">
        <div class="grid items-center gap-14 lg:grid-cols-2">

          <!-- Left: Copy -->
          <div>
            <div class="mb-5 inline-flex items-center gap-2 rounded-full border border-brand-400/30 bg-brand-400/10 px-4 py-1.5 text-sm font-medium text-brand-300">
              <span class="inline-block h-1.5 w-1.5 rounded-full bg-brand-400"></span>
              Now accepting applications
            </div>

            <h1 class="text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
              Write at the<br>
              <span class="text-brand-400">highest standard.</span>
            </h1>

            <p class="mt-6 max-w-lg text-lg leading-relaxed text-slate-300">
              Competitive per-page rates, flexible assignments, and reliable bi-weekly payouts — for writers who take their craft seriously.
            </p>

            <!-- Mini stat row -->
            <div class="mt-8 flex flex-wrap gap-6">
              <div class="text-sm">
                <span class="block text-2xl font-bold text-white">2,000+</span>
                <span class="text-slate-400">active writers</span>
              </div>
              <div class="text-sm">
                <span class="block text-2xl font-bold text-brand-400">$18–$45</span>
                <span class="text-slate-400">per page</span>
              </div>
              <div class="text-sm">
                <span class="block text-2xl font-bold text-white">2×/month</span>
                <span class="text-slate-400">payouts</span>
              </div>
            </div>

            <!-- CTAs -->
            <div class="mt-10 flex flex-wrap gap-3">
              <NuxtLink
                to="/apply"
                class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-7 py-3.5 text-base font-bold text-white shadow-lg shadow-brand-900/50 transition-all hover:bg-brand-500 hover:shadow-xl hover:shadow-brand-900/60"
              >
                Apply to write
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
              </NuxtLink>
              <NuxtLink
                to="/earnings"
                class="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/5 px-6 py-3.5 text-base font-semibold text-white transition-colors hover:bg-white/10"
              >
                See earnings →
              </NuxtLink>
            </div>
          </div>

          <!-- Right: Writer credential cards -->
          <div class="flex flex-col gap-4">
            <div
              v-for="t in testimonials"
              :key="t.name"
              class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm"
            >
              <div class="flex items-start gap-4">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                  {{ t.initials }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <div>
                      <p class="text-sm font-semibold text-white">{{ t.name }}</p>
                      <p class="text-xs text-slate-400">{{ t.subject }}</p>
                    </div>
                    <div class="text-right text-xs">
                      <p class="font-bold text-brand-400">{{ t.orders }} orders</p>
                      <p class="text-slate-500">{{ t.rating }}★</p>
                    </div>
                  </div>
                  <p class="mt-3 text-sm italic leading-relaxed text-slate-300">"{{ t.quote }}"</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── STATS BAR ───────────────────────────────────────────────────────── -->
    <section class="border-y border-slate-100 bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="grid grid-cols-2 gap-6 py-10 sm:grid-cols-4">
          <div v-for="stat in stats" :key="stat.label" class="text-center">
            <p class="text-3xl font-bold text-slate-900 sm:text-4xl">{{ stat.value }}</p>
            <p class="mt-1 text-sm font-semibold text-slate-700">{{ stat.label }}</p>
            <p class="mt-0.5 text-xs text-slate-400">{{ stat.note }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── BENEFITS ────────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Why writers choose Writers Creek</h2>
          <p class="mt-4 text-lg text-slate-600">Built for academics and professionals who want to write seriously and be paid fairly.</p>
        </div>
        <div class="mt-14 grid gap-6 sm:grid-cols-2">
          <div
            v-for="b in benefits"
            :key="b.title"
            class="rounded-2xl border border-slate-100 bg-white p-7 shadow-sm"
          >
            <div class="mb-4 text-3xl">{{ b.icon }}</div>
            <h3 class="text-lg font-bold text-slate-900">{{ b.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ b.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS ────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">From application to first payout</h2>
          <p class="mt-4 text-lg text-slate-600">Four steps. Most writers receive their first assignment within 48 hours of approval.</p>
        </div>
        <div class="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="step in steps" :key="step.n" class="relative">
            <div class="mb-4 text-5xl font-black text-brand-400/20">{{ step.n }}</div>
            <h3 class="text-base font-bold text-slate-900">{{ step.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ step.desc }}</p>
            <!-- Connector line -->
            <div
              v-if="step.n !== '04'"
              class="absolute right-0 top-6 hidden h-px w-6 bg-brand-200 lg:block"
            />
          </div>
        </div>
        <div class="mt-12 text-center">
          <NuxtLink to="/apply" class="btn-primary">
            Start your application
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── EARNINGS / LEVELS ───────────────────────────────────────────────── -->
    <section class="bg-slate-900 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Level-based earning rates</h2>
          <p class="mt-4 text-lg text-slate-400">Your rate grows as you deliver quality. Progression is based on performance, not tenure.</p>
        </div>
        <div class="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="level in levels"
            :key="level.name"
            class="rounded-2xl border p-7 transition-all"
            :class="level.name === 'Expert'
              ? 'border-brand-400 bg-white/5 ring-2 ring-brand-400/50'
              : 'border-white/10 bg-white/5 hover:border-white/20'"
          >
            <div class="mb-1 flex items-center justify-between">
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-bold"
                :class="level.name === 'Expert'
                  ? 'bg-brand-400/20 text-brand-300'
                  : 'bg-white/10 text-slate-300'"
              >{{ level.name }}</span>
              <span v-if="level.name === 'Expert'" class="text-xs font-semibold text-brand-400">Top tier</span>
            </div>
            <p class="mt-4 text-3xl font-black text-white">{{ level.rate }}</p>
            <p class="text-sm text-slate-400">per page</p>
            <p class="mt-4 text-sm leading-relaxed text-slate-400">{{ level.desc }}</p>
          </div>
        </div>
        <div class="mt-12 text-center">
          <NuxtLink to="/earnings" class="inline-flex items-center gap-2 rounded-xl border border-brand-400/40 bg-brand-400/10 px-6 py-3 text-sm font-semibold text-brand-300 transition-colors hover:bg-brand-400/20">
            Full earnings breakdown →
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- ── SUBJECTS CLOUD ─────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">We need writers in these subjects</h2>
          <p class="mt-4 text-lg text-slate-600">Demand is high across disciplines. If your subject is on this list, we almost certainly have work for you.</p>
        </div>
        <div class="mt-10 flex flex-wrap justify-center gap-3">
          <span
            v-for="subject in subjects"
            :key="subject"
            class="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700"
          >
            {{ subject }}
          </span>
        </div>
        <p class="mt-8 text-center text-sm text-slate-400">Don't see your subject? Apply anyway — we review all applications.</p>
      </div>
    </section>

    <!-- ── TESTIMONIALS ────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">What our writers say</h2>
          <p class="mt-4 text-lg text-slate-600">From their own words — not marketing copy.</p>
        </div>
        <div class="mt-14 grid gap-6 sm:grid-cols-3">
          <div
            v-for="t in testimonials"
            :key="t.name"
            class="rounded-2xl border border-slate-100 bg-white p-7 shadow-sm"
          >
            <div class="mb-5 flex items-center gap-0.5">
              <svg v-for="i in Math.floor(t.rating)" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <p class="text-sm italic leading-relaxed text-slate-600">"{{ t.quote }}"</p>
            <div class="mt-5 flex items-center gap-3">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
                {{ t.initials }}
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ t.name }}</p>
                <p class="text-xs text-slate-500">{{ t.subject }} · {{ t.orders }} assignments</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── FAQ ────────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Common questions</h2>
          <p class="mt-4 text-lg text-slate-600">Everything you need to know before applying.</p>
        </div>
        <div class="mt-12 divide-y divide-slate-100">
          <details
            v-for="faq in faqs"
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
        <p class="mt-8 text-center text-sm text-slate-400">
          More questions?
          <NuxtLink to="/faq" class="font-medium text-brand-600 hover:underline">See the full FAQ →</NuxtLink>
        </p>
      </div>
    </section>

    <!-- ── FINAL CTA ───────────────────────────────────────────────────────── -->
    <section class="bg-slate-900 py-24">
      <div class="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-400">Ready to start?</p>
        <h2 class="mt-4 text-4xl font-bold text-white sm:text-5xl">
          Ready to join Writers Creek?
        </h2>
        <p class="mt-5 text-lg text-slate-400">
          Join a platform built on quality, not volume. Apply in 10 minutes — decisions within 48 hours.
        </p>
        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <NuxtLink
            to="/apply"
            class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-base font-bold text-white shadow-lg shadow-brand-900/50 transition-all hover:bg-brand-500"
          >
            Apply now — it's free
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
          </NuxtLink>
          <NuxtLink
            to="/how-it-works"
            class="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/5 px-6 py-4 text-base font-semibold text-white transition-colors hover:bg-white/10"
          >
            How it works
          </NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>
