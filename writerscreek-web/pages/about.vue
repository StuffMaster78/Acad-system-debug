<script setup lang="ts">
useSeoMeta({
  title: 'About Writers Creek',
  description: 'Writers Creek is a selective academic writing network connecting credential-verified writers with quality academic assignments. Learn who we are and how we work.',
  ogTitle: 'About Writers Creek — A Selective Academic Writing Network',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const values = [
  {
    icon: '🎓',
    title: 'Credential-first selectivity',
    desc: 'Every writer on the platform holds a postgraduate degree or active professional credential in their subject area. We verify this before any writer is approved.',
  },
  {
    icon: '⚖️',
    title: 'Fair, transparent pay',
    desc: 'Rates are set per page and published openly. Writers know exactly what they earn before accepting any assignment. No hidden deductions, no ambiguous bonus schemes.',
  },
  {
    icon: '🔒',
    title: 'Writer privacy',
    desc: 'Your full name, credentials, and contact details are never shared with clients. You interact with the platform — the platform manages the client relationship.',
  },
  {
    icon: '📐',
    title: 'Quality over volume',
    desc: 'We have no minimum assignment quotas. We would rather have 2,000 writers producing consistently excellent work than 20,000 producing variable output.',
  },
  {
    icon: '💳',
    title: 'Reliable payouts',
    desc: 'Earnings are released bi-weekly, every time. You should never have to chase a payment or wonder when you will be paid.',
  },
  {
    icon: '🤝',
    title: 'Respect for the craft',
    desc: 'Academic writing is skilled, specialist work. We design the platform to reflect that — in the rates, the vetting process, and how we handle disputes.',
  },
]

const stats = [
  { value: '2,000+',  label: 'Credentialed writers' },
  { value: '100+',    label: 'Academic disciplines' },
  { value: '$18–$45', label: 'Per-page rate range'  },
  { value: '4.8/5',   label: 'Writer satisfaction'  },
]

const qualityStandards = [
  {
    step: '01',
    title: 'Credential verification',
    desc: 'Applicants submit proof of their highest qualification or professional credential. We verify independently before proceeding.',
  },
  {
    step: '02',
    title: 'Vetting quiz',
    desc: 'A timed grammar and subject-knowledge assessment. Pass rates are intentionally selective — the bar reflects the work we deliver.',
  },
  {
    step: '03',
    title: 'Trial assignment review',
    desc: "New writers' first five assignments are reviewed by a senior editor before client delivery. This protects quality during the onboarding window.",
  },
  {
    step: '04',
    title: 'Ongoing performance tracking',
    desc: 'Client satisfaction ratings, revision rates, and deadline adherence are tracked continuously. Tier progressions and assignment access are tied directly to performance.',
  },
]

const disciplines = [
  'Nursing & Healthcare', 'Business & Finance', 'Psychology', 'Law & Legal Studies',
  'Literature & English', 'History', 'Sociology', 'Philosophy',
  'Statistics & Data', 'Biology & Life Sciences', 'Chemistry & Physical Sciences',
  'Education & Teaching', 'Public Health & Epidemiology', 'Political Science',
  'Economics & Econometrics', 'Marketing & Management', 'Engineering', 'Architecture',
]
</script>

<template>
  <div>

    <!-- ── HERO ────────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-slate-900">
      <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(rgba(56,189,248,0.07)_1.5px,transparent_1.5px)] [background-size:28px_28px]" />
      <div class="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28 2xl:max-w-screen-xl 2xl:px-12">
        <div class="grid items-center gap-14 lg:grid-cols-2">

          <div>
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-400">About</p>
            <h1 class="text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl lg:text-6xl">
              A network built on<br>
              <span class="text-brand-400">academic rigour.</span>
            </h1>
            <p class="mt-6 max-w-lg text-lg leading-relaxed text-slate-300">
              Writers Creek is a selective academic writing network. We connect credential-verified writers — PhD holders, clinicians, and subject specialists — with assignments that match their exact expertise.
            </p>
            <p class="mt-4 max-w-lg text-lg leading-relaxed text-slate-400">
              We are not a content mill. We are a platform for writers who take academic work seriously, and who want to be compensated fairly for that expertise.
            </p>
            <div class="mt-10">
              <NuxtLink to="/apply" class="btn-primary px-8 py-4 text-base">
                Apply to write →
              </NuxtLink>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 gap-4">
            <div
              v-for="stat in stats"
              :key="stat.label"
              class="rounded-2xl border border-white/10 bg-white/5 p-7 text-center"
            >
              <p class="text-3xl font-black text-brand-400 sm:text-4xl">{{ stat.value }}</p>
              <p class="mt-2 text-sm font-medium text-slate-300">{{ stat.label }}</p>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── MISSION ─────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Our mission</h2>
        <div class="mt-6 space-y-5 text-lg leading-relaxed text-slate-600">
          <p>
            Academic writing is difficult, specialised work. A nursing care plan requires clinical knowledge. A quantitative finance dissertation requires statistical expertise. A legal analysis requires both subject mastery and methodological precision.
          </p>
          <p>
            Too many platforms treat this as interchangeable content work. Writers Creek was built on a different premise: <strong class="text-slate-900">match the writer to the work by expertise, not just availability.</strong>
          </p>
          <p>
            The result is better outcomes for clients, better assignments for writers, and a platform where the word "academic" actually means something.
          </p>
        </div>
      </div>
    </section>

    <!-- ── QUALITY STANDARDS ──────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">How we maintain standards</h2>
          <p class="mt-4 text-lg text-slate-600">Four checkpoints between application and assignment delivery.</p>
        </div>

        <div class="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="s in qualityStandards"
            :key="s.step"
            class="relative"
          >
            <p class="mb-4 text-5xl font-black text-brand-400/20">{{ s.step }}</p>
            <h3 class="text-base font-bold text-slate-900">{{ s.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ s.desc }}</p>
          </div>
        </div>

        <div class="mt-14 rounded-2xl border border-brand-200 bg-brand-50 p-8 text-center">
          <p class="text-lg font-semibold text-brand-900">This is why our vetting pass rate is selective.</p>
          <p class="mt-2 text-brand-700">Writers who pass this process work alongside peers at the same standard. That bar matters.</p>
        </div>
      </div>
    </section>

    <!-- ── VALUES ─────────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">What we stand for</h2>
          <p class="mt-4 text-lg text-slate-600">The principles behind how the platform is built and how we treat writers.</p>
        </div>
        <div class="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="v in values"
            :key="v.title"
            class="rounded-2xl border border-slate-100 bg-white p-7 shadow-sm"
          >
            <div class="mb-4 text-3xl">{{ v.icon }}</div>
            <h3 class="text-base font-bold text-slate-900">{{ v.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ v.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── DISCIPLINES ────────────────────────────────────────────────────── -->
    <section class="bg-slate-900 py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Disciplines we cover</h2>
          <p class="mt-4 text-lg text-slate-400">If your subject is on this list, there is almost certainly demand for your work.</p>
        </div>
        <div class="mt-10 flex flex-wrap justify-center gap-3">
          <span
            v-for="d in disciplines"
            :key="d"
            class="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 transition-colors hover:border-brand-400/40 hover:bg-brand-400/10 hover:text-brand-300"
          >
            {{ d }}
          </span>
        </div>
        <p class="mt-8 text-center text-sm text-slate-500">Not on this list? Apply anyway — we review all applications individually.</p>
      </div>
    </section>

    <!-- ── DIFFERENCE ─────────────────────────────────────────────────────── -->
    <section class="bg-white py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">
        <div class="grid items-center gap-14 lg:grid-cols-2">

          <div>
            <h2 class="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Why this is different from other platforms</h2>
            <div class="mt-6 space-y-4 text-slate-600">
              <p>Many writing platforms accept any writer who signs up. Their model is volume: a large pool of writers competing on price, with clients choosing the cheapest bid.</p>
              <p>Writers Creek is the opposite. We limit the writer pool to people who can genuinely handle academic-level work in their subject area. Clients pay more because they receive specialist expertise. Writers earn more because the work requires it.</p>
              <p>That selectivity is not cosmetic. It is baked into the application process, the vetting quiz, the editorial review during onboarding, and the tier progression that ties earnings to performance.</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="flex items-start gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-700">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Credential-verified writers only</p>
                <p class="mt-1 text-sm text-slate-600">Postgraduate degrees or active professional credentials, verified before approval.</p>
              </div>
            </div>
            <div class="flex items-start gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-700">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Subject-matched assignments</p>
                <p class="mt-1 text-sm text-slate-600">Nursing assignments go to nurses. Finance assignments go to finance specialists. No mismatched work.</p>
              </div>
            </div>
            <div class="flex items-start gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-700">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Published, transparent rates</p>
                <p class="mt-1 text-sm text-slate-600">No hidden bidding. No race to the bottom. Rates are level-based and public.</p>
              </div>
            </div>
            <div class="flex items-start gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-100 text-green-700">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              </div>
              <div>
                <p class="font-semibold text-slate-900">Bi-weekly payouts without chasing</p>
                <p class="mt-1 text-sm text-slate-600">Earnings are released on a fixed schedule. No invoicing, no payment delays.</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── FINAL CTA ───────────────────────────────────────────────────────── -->
    <section class="bg-slate-900 py-24">
      <div class="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <p class="text-sm font-semibold uppercase tracking-widest text-brand-400">Join the network</p>
        <h2 class="mt-4 text-4xl font-bold text-white sm:text-5xl">
          If this sounds like the right fit, apply.
        </h2>
        <p class="mt-5 text-lg text-slate-400">
          Applications take 10 minutes. Decisions are made within 48 hours. No commitment required until you accept an assignment.
        </p>
        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <NuxtLink
            to="/apply"
            class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-4 text-base font-bold text-white shadow-lg shadow-brand-900/50 transition-all hover:bg-brand-500"
          >
            Start your application →
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
