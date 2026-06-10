<script setup lang="ts">
const portal = usePortalStore()
const { getAll: getAllServices } = useServices()
const serviceStrip = getAllServices()

const pillars = [
  {
    icon: 'file-text',
    title: 'Research & Essays',
    desc: 'Research papers, essays, dissertations, case studies, literature reviews — written from scratch by subject-specialist writers with the right credentials for your level.',
    href: '/services',
  },
  {
    icon: 'bar-chart-3',
    title: 'Data & Analysis',
    desc: 'SPSS, R, Python, or Excel data analysis with full written interpretation, methodology support, and charts — for dissertations, research papers, or standalone assignments.',
    href: '/services/data-analysis',
  },
  {
    icon: 'graduation-cap',
    title: 'Coursework & Support',
    desc: 'Regular assignments, online class help, presentations, and lab reports — handled by the same writer throughout so your work stays consistent and on time.',
    href: '/class-support',
  },
]

const stats = [
  { value: '14,700+', label: 'Papers delivered' },
  { value: '200+',    label: 'Expert writers' },
  { value: '4.8/5',   label: 'Average rating' },
  { value: '98%',     label: 'On-time delivery' },
]

const services = [
  { icon: 'file-text',      title: 'Research Papers', href: '/services/research-papers', desc: 'Original, citation-rich papers across STEM, business, humanities, and social sciences.' },
  { icon: 'pen-line',       title: 'Essays',          href: '/services/essays',          desc: 'Argumentative, analytical, descriptive — any format, any level.' },
  { icon: 'graduation-cap', title: 'Dissertations',   href: '/services/dissertations',   desc: 'Full thesis support: proposal, chapters, methodology, data analysis.' },
  { icon: 'briefcase',      title: 'Case Studies',    href: '/services/case-studies',    desc: 'In-depth analysis with structured arguments and evidence.' },
  { icon: 'bar-chart-3',    title: 'Data Analysis',   href: '/services/data-analysis',   desc: 'SPSS, R, Python — with full write-up and interpretation.' },
  { icon: 'flask-conical',  title: 'Lab Reports',     href: '/services/lab-reports',     desc: 'Clear, structured lab write-ups with correct methodology sections.' },
]

const steps = [
  { title: 'Fill in your brief',           desc: 'Complete the order form with your topic, deadline, level, and any instructions or sample files.' },
  { title: 'Secure checkout',              desc: 'Pay securely. Your payment is held in escrow until you approve the completed work.' },
  { title: 'Communicate with your writer', desc: 'Message your assigned expert directly, share files, and track progress in real time.' },
  { title: 'Download & review',            desc: "Receive your paper and request free revisions until you're fully satisfied." },
]

const guarantees = [
  { icon: 'trophy',       title: 'Grade or money back',       desc: "If the work doesn't meet your stated grade target, we'll refund or rewrite — no questions asked." },
  { icon: 'check-circle', title: '100% original papers',      desc: 'Every paper is written from scratch and verified against plagiarism databases before delivery.' },
  { icon: 'bot',          title: 'Zero AI content',           desc: 'Every paper is written by a human expert. We provide a free AI-detection report on request.' },
  { icon: 'lock',         title: 'Your privacy protected',    desc: 'We never share your identity, order details, or personal data with any third party.' },
  { icon: 'refresh-cw',  title: 'Unlimited free revisions',  desc: 'Within the revision window, request as many changes as you need at zero extra cost.' },
  { icon: 'user-check',  title: 'Dedicated assigned writer', desc: 'The same expert handles your revisions so context and tone stay consistent throughout.' },
]

const subjects = [
  'Biology', 'Chemistry', 'Physics', 'Engineering', 'Statistics', 'Nursing',
  'Business', 'Finance', 'Marketing', 'Law', 'Psychology', 'History',
  'Literature', 'Philosophy', 'Public Health', 'Accounting', 'Sociology', 'Economics',
]

useSeoMeta({
  title: 'Research Paper Writing Service from $15/Page',
  description: 'Get research papers, essays, and assignments written by human experts. From $15/page. Grade or money back guarantee. 14,700+ papers delivered. 4.8/5 rated.',
  ogTitle: 'ResearchPaperMate — Research Paper Writing Service from $15/Page',
  ogDescription: 'Human-written research papers, essays, and assignments across 100+ subjects. Grade or money back. Zero AI content.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://researchpapermate.com/' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ProfessionalService',
      name: 'ResearchPaperMate',
      description: 'Academic writing service providing research papers, essays, and assignments.',
      url: 'https://researchpapermate.com',
      priceRange: '$15–$50 per page',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '14700' },
    }),
  }],
})
</script>

<template>
  <!-- ─── Hero ─────────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-gradient-to-br from-brand-900 via-brand-700 to-brand-600 py-20 sm:py-28">
    <div class="section relative z-10">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: copy -->
        <div>
          <!-- Urgency pill -->
          <div class="mb-4 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm text-white ring-1 ring-white/20">
            <span class="inline-block h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
            <span><strong>52 writers</strong> online right now · From <strong>$15/page</strong></span>
          </div>

          <h1 class="font-serif text-4xl font-bold leading-tight text-white sm:text-5xl">
            {{ portal.heroHeadline }}
          </h1>
          <p class="mt-5 text-lg text-brand-100 leading-relaxed">
            {{ portal.heroSub }}
          </p>

          <div class="mt-8 flex flex-wrap gap-4">
            <NuxtLink
              to="/order"
              class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base shadow-lg"
            >
              Place your order
            </NuxtLink>
            <NuxtLink
              href="/pricing"
              class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-3.5 text-base"
            >
              See pricing
            </NuxtLink>
          </div>

          <!-- Trust badge row -->
          <div class="mt-8">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: calculator -->
        <div class="lg:pl-8">
          <ClientOnly>
            <OrderCalculator />
            <template #fallback>
              <div class="h-72 animate-pulse rounded-2xl bg-white/10" />
            </template>
          </ClientOnly>
        </div>

      </div>
    </div>
    <div class="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-brand-500 opacity-20 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-blue-400 opacity-20 blur-3xl pointer-events-none" />
  </section>

  <!-- ─── Stats ─────────────────────────────────────────────────────────── -->
  <section class="border-b border-slate-100 bg-white py-10">
    <div class="section py-0">
      <div class="grid grid-cols-2 gap-6 text-center md:grid-cols-4">
        <div v-for="stat in stats" :key="stat.label">
          <div class="text-3xl font-bold text-brand-700">{{ stat.value }}</div>
          <div class="mt-1 text-sm text-slate-500">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Scrollable service strip ───────────────────────────────────── -->
  <section class="border-b border-slate-100 bg-white py-8">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-5 flex items-center justify-between">
        <p class="text-sm font-semibold text-slate-600">All paper types — tap to explore</p>
        <NuxtLink href="/services" class="text-xs font-semibold text-brand-600 hover:underline">View all →</NuxtLink>
      </div>
      <div class="flex gap-3 overflow-x-auto scroll-smooth snap-x snap-mandatory pb-2" style="scrollbar-width: none;">
        <NuxtLink
          v-for="s in serviceStrip"
          :key="s.slug"
          :href="`/services/${s.slug}`"
          class="group snap-start shrink-0 flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 transition-colors hover:border-brand-200 hover:bg-brand-50 w-52"
        >
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-100 transition-colors group-hover:bg-brand-600">
            <Icon name="file-text" class="h-4 w-4 text-brand-600 transition-colors group-hover:text-white" />
          </div>
          <div class="min-w-0">
            <p class="truncate text-xs font-semibold text-slate-800 group-hover:text-brand-700">{{ s.navLabel }}</p>
            <p class="text-xs text-brand-600">from ${{ s.priceFrom }}/page</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Three Pillars ────────────────────────────────────────────────── -->
  <section class="bg-brand-50 py-20">
    <div class="section py-0">
      <div class="text-center">
        <h2 class="section-heading">Research. Analysis. Support.</h2>
        <p class="section-sub">Three ways we help students succeed — pick what fits your situation.</p>
      </div>
      <div class="mt-12 grid gap-8 md:grid-cols-3">
        <NuxtLink
          v-for="p in pillars"
          :key="p.title"
          :href="p.href"
          class="card group flex flex-col transition-shadow hover:shadow-lg hover:border-brand-300"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-100 transition-colors group-hover:bg-brand-600">
            <Icon :name="p.icon" class="h-6 w-6 text-brand-600 transition-colors group-hover:text-white" />
          </div>
          <h3 class="mt-4 text-xl font-bold text-brand-700 transition-colors group-hover:text-brand-900">{{ p.title }}</h3>
          <p class="mt-3 flex-1 text-sm leading-relaxed text-slate-600">{{ p.desc }}</p>
          <span class="mt-4 text-xs font-semibold text-brand-600 group-hover:underline">Learn more →</span>
        </NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Writer Showcase ───────────────────────────────────────────────── -->
  <WriterShowcase />

  <!-- ─── Services ─────────────────────────────────────────────────────── -->
  <section class="bg-slate-50">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">100+ Subjects, Every Paper Type</h2>
        <p class="section-sub">STEM, business, humanities, law, nursing — if you need it written, we cover it.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink v-for="service in services" :key="service.title" :href="service.href"
          class="card group flex flex-col transition-shadow hover:shadow-md hover:border-brand-200">
          <div class="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
            <Icon :name="service.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
          </div>
          <h3 class="font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">{{ service.title }}</h3>
          <p class="mt-2 flex-1 text-sm text-slate-500 leading-relaxed">{{ service.desc }}</p>
          <span class="mt-3 text-xs font-medium text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Learn more →</span>
        </NuxtLink>
      </div>
      <div class="mt-10 flex flex-wrap justify-center gap-2">
        <span
          v-for="sub in subjects"
          :key="sub"
          class="rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
        >
          {{ sub }}
        </span>
        <span class="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-500">
          +80 more
        </span>
      </div>
      <div class="mt-10 text-center">
        <NuxtLink href="/services" class="btn-outline">View all paper types</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── How it works ──────────────────────────────────────────────────── -->
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">How it works</h2>
        <p class="section-sub">Four simple steps from brief to finished paper.</p>
      </div>
      <ol class="mt-12 grid gap-8 md:grid-cols-4">
        <li v-for="(step, i) in steps" :key="step.title" class="flex flex-col items-center text-center">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-700 text-lg font-bold text-white shadow-md">
            {{ i + 1 }}
          </div>
          <h3 class="font-semibold text-slate-900">{{ step.title }}</h3>
          <p class="mt-2 text-sm text-slate-500 leading-relaxed">{{ step.desc }}</p>
        </li>
      </ol>
      <div class="mt-12 text-center">
        <NuxtLink to="/order" class="btn-primary">Start your order now</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Guarantees ────────────────────────────────────────────────────── -->
  <section class="bg-brand-900">
    <div class="section">
      <div class="text-center">
        <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">Our guarantees</h2>
        <p class="mt-4 text-brand-200">We put our reputation behind every single order.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="g in guarantees" :key="g.title" class="rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 transition-colors hover:bg-white/10">
          <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
            <Icon :name="g.icon" class="h-5 w-5 text-white" />
          </div>
          <h3 class="font-semibold text-white">{{ g.title }}</h3>
          <p class="mt-2 text-sm text-brand-200 leading-relaxed">{{ g.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Writing Services We Offer ──────────────────────────────────── -->
  <WritingServicesGrid />

  <!-- ─── Deep content tabs ───────────────────────────────────────────── -->
  <AcademicContentTabs />

  <!-- ─── Testimonials ──────────────────────────────────────────────────── -->
  <TestimonialsSection />

  <!-- ─── FAQ ───────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── Final CTA ─────────────────────────────────────────────────────── -->
  <section class="bg-brand-600 py-20">
    <div class="section py-0 text-center">
      <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">
        Ready? Your deadline is waiting.
      </h2>
      <p class="mt-4 text-brand-100 text-lg">
        Tell us your requirements. We'll match you with the right expert in minutes.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <NuxtLink
          to="/order"
          class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base shadow-lg"
        >
          Place your order — from $15/page
        </NuxtLink>
        <NuxtLink
          href="/contact"
          class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-4 text-base"
        >
          Talk to us first
        </NuxtLink>
      </div>
      <p class="mt-6 text-sm text-brand-200">
        24/7 support · 2-hour minimum turnaround · Free revisions · Grade or money back
      </p>
    </div>
  </section>
</template>
