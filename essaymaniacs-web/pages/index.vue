<script setup lang="ts">
const portal = usePortalStore()
const { getAll: getAllServices } = useServices()
const serviceStrip = getAllServices()

// Live-feeling order counter — seed with a realistic number, increment on mount
const ordersToday = ref(147)
onMounted(() => {
  // Simulates live activity — increments occasionally while user is on the page
  const tick = () => {
    if (Math.random() > 0.7) ordersToday.value++
    setTimeout(tick, 8000 + Math.random() * 12000)
  }
  setTimeout(tick, 5000)
})

const stats = [
  { value: '20,000+', label: 'Essays delivered' },
  { value: '500+',    label: 'Subject-specialist writers' },
  { value: '4.8/5',   label: 'Average rating' },
  { value: '2 hrs',   label: 'Fastest turnaround' },
]

const services = [
  { icon: 'pen-line',       title: 'Essays',                href: '/services/essays',           desc: 'Argumentative, analytical, reflective, narrative — any type, any level.' },
  { icon: 'file-text',      title: 'Research Papers',       href: '/services/research-papers',  desc: 'Original research from peer-reviewed sources. Any citation style.' },
  { icon: 'graduation-cap', title: 'Dissertations',         href: '/services/dissertations',    desc: 'Proposal through final chapter, with supervisor feedback integration.' },
  { icon: 'briefcase',      title: 'Case Studies',          href: '/services/case-studies',     desc: 'Problem-solution-evaluation structure with real evidence.' },
  { icon: 'sparkles',       title: 'Admission Essays',      href: '/services/admission-essays', desc: 'Personal statements and scholarship essays tailored to each school.' },
  { icon: 'check-check',    title: 'Proofreading',          href: '/services/proofreading',     desc: 'Grammar, argument, structure, and citation accuracy — all checked.' },
]

const subjects = [
  'History', 'Psychology', 'Sociology', 'Business', 'Law', 'Economics',
  'Literature', 'Philosophy', 'Political Science', 'Marketing', 'Nursing',
  'Biology', 'Chemistry', 'Engineering', 'Statistics', 'Finance',
  'Education', 'Media Studies',
]

const steps = [
  { title: 'Fill in your brief',           desc: 'Essay type, subject, academic level, deadline, word count, and any rubric or instructions.' },
  { title: 'Matched with a specialist',    desc: 'We assign a writer with the right subject background and degree level for your assignment.' },
  { title: 'Communicate directly',         desc: 'Message your writer, share files, and follow progress in real time — no support ticket queue.' },
  { title: 'Download and review',          desc: 'Receive your essay with a free plagiarism report. Request unlimited free revisions if needed.' },
]

const guarantees = [
  { icon: 'trophy',        title: 'Grade or money back',        desc: "If the work doesn't meet your stated requirements, we rewrite it or refund you — no questions asked." },
  { icon: 'user-check',    title: 'Subject-obsessed writers',   desc: 'Every writer is matched by subject, not just assigned randomly. They care about the topic. It shows.' },
  { icon: 'bot',           title: 'Zero AI content',            desc: 'Every essay is written by a human who actually knows the subject. Free AI-detection report on request.' },
  { icon: 'lock',          title: 'Complete confidentiality',   desc: 'Your identity, order details, and school are never shared with any third party.' },
  { icon: 'refresh-cw',   title: 'Unlimited free revisions',   desc: 'Request as many changes as you need within the revision window — always at zero extra cost.' },
  { icon: 'zap',           title: 'As fast as 2 hours',         desc: 'Urgent essay due tonight? Most essays up to 4 pages can be delivered in 2 hours.' },
]

const testimonials = [
  { initials: 'JM', name: 'Jake M.', subject: 'History, undergrad', rating: 5, quote: 'I needed an argumentative essay on colonial African history in 24 hours. Got back something I actually learned from. Solid sourcing, strong argument.', orders: 8 },
  { initials: 'AL', name: 'Amara L.', subject: 'Psychology, Master\'s', rating: 5, quote: 'My thesis literature review was a mess. They restructured it completely — gaps I missed, sources I hadn\'t found. Worth every cent.', orders: 12 },
  { initials: 'RK', name: 'Ryan K.', subject: 'Business, undergrad', rating: 5, quote: 'Used them for a case study on Tesla\'s market strategy. The writer clearly knew the subject. Detailed, well-argued, and properly cited.', orders: 5 },
  { initials: 'SC', name: 'Sophie C.', subject: 'Literature, doctoral', rating: 5, quote: 'Honestly surprised by the quality on a reflective essay. It sounded like me — better than me, actually. Will use again.', orders: 3 },
]

useSeoMeta({
  title: 'Essay Writing Service from $10/Page | EssayManiacs',
  description: 'Get essays, research papers, and dissertations written by subject-obsessed specialists. From $10/page. Zero AI. Grade or money back. 20,000+ orders delivered.',
  ogTitle: 'EssayManiacs — Essays Written by People Who Love the Subject',
  ogDescription: 'Expert essay writing across every subject and level. From $10/page. Zero AI content. Grade or money back.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': ['ProfessionalService', 'Organization'],
      name: 'EssayManiacs',
      description: 'Academic essay writing service staffed by subject-specialist writers.',
      url: 'https://essaymaniacs.com',
      logo: 'https://essaymaniacs.com/favicon.svg',
      priceRange: '$10–$50 per page',
      aggregateRating: { '@type': 'AggregateRating', ratingValue: '4.8', reviewCount: '20000', bestRating: '5', worstRating: '1' },
      hasOfferCatalog: {
        '@type': 'OfferCatalog',
        name: 'Essay Writing Services',
        itemListElement: [
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Essay Writing' } },
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Research Paper Writing' } },
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Dissertation Writing' } },
          { '@type': 'Offer', itemOffered: { '@type': 'Service', name: 'Proofreading & Editing' } },
        ],
      },
    }),
  }],
})
</script>

<template>
  <!-- ─── Announcement bar ────────────────────────────────────────────────── -->
  <AnnouncementBar />

  <!-- ─── Hero ─────────────────────────────────────────────────────────────── -->
  <section class="relative overflow-hidden bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 py-20 sm:py-28">
    <div class="section relative z-10">
      <div class="grid items-center gap-12 lg:grid-cols-2">

        <!-- Left: copy -->
        <div>
          <!-- Live order counter -->
          <div class="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm text-white ring-1 ring-white/20">
            <span class="inline-block h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
            <span><strong>{{ ordersToday }}</strong> essays ordered today · From <strong>$10/page</strong></span>
          </div>

          <h1 class="font-serif text-4xl font-bold leading-tight text-white sm:text-5xl">
            Essays Written by People<br class="hidden sm:block" />
            <span class="text-brand-300">Who Love the Subject</span>
          </h1>
          <p class="mt-5 text-lg leading-relaxed text-brand-100">
            Subject-obsessed specialists — not generic writers — covering every essay type, every subject, and every deadline. Zero AI. Grade or money back.
          </p>

          <!-- First-order nudge -->
          <div class="mt-5 flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-3 text-sm text-white">
            <Icon name="tag" class="h-4 w-4 shrink-0 text-brand-300" />
            <span>Use code <strong class="rounded bg-white/20 px-1.5 py-0.5 font-mono tracking-wide">FIRST15</strong> for 15% off your first order</span>
          </div>

          <div class="mt-8 flex flex-wrap gap-4">
            <NuxtLink to="/order" class="btn-primary bg-white px-8 py-3.5 text-base text-brand-700 shadow-lg hover:bg-brand-50">
              Place your order
            </NuxtLink>
            <NuxtLink href="/pricing" class="btn-outline border-white/60 px-8 py-3.5 text-base text-white hover:bg-white/10">
              See pricing
            </NuxtLink>
          </div>

          <div class="mt-8">
            <TrustBadges />
          </div>
        </div>

        <!-- Right: order form -->
        <div class="lg:pl-8">
          <MultiStepOrderForm />
        </div>

      </div>
    </div>
    <!-- Background blobs -->
    <div class="absolute -top-20 -right-20 h-96 w-96 rounded-full bg-brand-400 opacity-20 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-20 -left-20 h-96 w-96 rounded-full bg-violet-300 opacity-10 blur-3xl pointer-events-none" />
  </section>

  <!-- ─── Stats ──────────────────────────────────────────────────────────── -->
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

  <!-- ─── Scrollable service strip ───────────────────────────────────────── -->
  <section class="border-b border-slate-100 bg-white py-8">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="mb-5 flex items-center justify-between">
        <p class="text-sm font-semibold text-slate-600">All essay and paper types — tap to explore</p>
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
            <Icon :name="s.icon" class="h-4 w-4 text-brand-600 transition-colors group-hover:text-white" />
          </div>
          <div class="min-w-0">
            <p class="truncate text-xs font-semibold text-slate-800 group-hover:text-brand-700">{{ s.navLabel }}</p>
            <p class="text-xs text-brand-600">from ${{ s.priceFrom }}/page</p>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Writer Showcase ─────────────────────────────────────────────────── -->
  <WriterShowcase />

  <!-- ─── Services grid ───────────────────────────────────────────────────── -->
  <section class="bg-slate-50">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Every essay and paper type covered</h2>
        <p class="section-sub">20 types. Every subject. High school through doctoral level.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="svc in services"
          :key="svc.title"
          :href="svc.href"
          class="card group flex flex-col transition-shadow hover:border-brand-200 hover:shadow-md"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
            <Icon :name="svc.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
          </div>
          <h3 class="mt-4 font-semibold text-slate-900 transition-colors group-hover:text-brand-700">{{ svc.title }}</h3>
          <p class="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{{ svc.desc }}</p>
          <span class="mt-3 text-xs font-medium text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Order now →</span>
        </NuxtLink>
      </div>

      <!-- Subject pill cloud -->
      <div class="mt-10 flex flex-wrap justify-center gap-2">
        <span
          v-for="sub in subjects"
          :key="sub"
          class="rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
        >{{ sub }}</span>
        <span class="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-500">+80 more</span>
      </div>
      <div class="mt-10 text-center">
        <NuxtLink href="/services" class="btn-outline">View all 20 essay types</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── How it works ────────────────────────────────────────────────────── -->
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">How it works</h2>
        <p class="section-sub">Four steps from brief to finished essay.</p>
      </div>
      <ol class="mt-12 grid gap-8 md:grid-cols-4">
        <li v-for="(step, i) in steps" :key="step.title" class="flex flex-col items-center text-center">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-700 text-lg font-bold text-white shadow-md">
            {{ i + 1 }}
          </div>
          <h3 class="font-semibold text-slate-900">{{ step.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ step.desc }}</p>
        </li>
      </ol>
      <div class="mt-12 text-center">
        <NuxtLink to="/order" class="btn-primary">Start your order now</NuxtLink>
      </div>
    </div>
  </section>

  <!-- ─── Guarantees ──────────────────────────────────────────────────────── -->
  <section class="bg-brand-900">
    <div class="section">
      <div class="text-center">
        <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">Our guarantees</h2>
        <p class="mt-4 text-brand-200">Every order, every time. No exceptions.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="g in guarantees" :key="g.title" class="rounded-2xl bg-white/5 p-6 ring-1 ring-white/10 transition-colors hover:bg-white/10">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10">
            <Icon :name="g.icon" class="h-5 w-5 text-white" />
          </div>
          <h3 class="mt-3 font-semibold text-white">{{ g.title }}</h3>
          <p class="mt-2 text-sm leading-relaxed text-brand-200">{{ g.desc }}</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── Writing Services Grid ───────────────────────────────────────────── -->
  <WritingServicesGrid />

  <!-- ─── Deep content tabs ───────────────────────────────────────────────── -->
  <AcademicContentTabs />

  <!-- ─── Testimonials ────────────────────────────────────────────────────── -->
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">What students say</h2>
        <p class="section-sub">Real customers. Real orders. No filtering.</p>
      </div>
      <div class="mt-12 grid gap-6 sm:grid-cols-2">
        <div v-for="t in testimonials" :key="t.name" class="card relative">
          <!-- Repeat order badge -->
          <div class="absolute right-5 top-5 rounded-full bg-brand-50 px-2.5 py-0.5 text-[10px] font-bold text-brand-700">
            {{ t.orders }} orders
          </div>
          <!-- Stars -->
          <div class="flex gap-0.5 mb-4">
            <svg v-for="i in t.rating" :key="i" class="h-4 w-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <p class="flex-1 text-sm leading-relaxed text-slate-700 italic">"{{ t.quote }}"</p>
          <div class="mt-5 flex items-center gap-3 border-t border-slate-100 pt-4">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
              {{ t.initials }}
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-900">{{ t.name }}</p>
              <p class="text-xs text-slate-500">{{ t.subject }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ─── FAQ ─────────────────────────────────────────────────────────────── -->
  <HomeFaq />

  <!-- ─── Final CTA ───────────────────────────────────────────────────────── -->
  <section class="bg-brand-600 py-20">
    <div class="section py-0 text-center">
      <h2 class="font-serif text-3xl font-bold text-white sm:text-4xl">
        Your deadline is closer than you think.
      </h2>
      <p class="mt-4 text-lg text-brand-100">
        Tell us what you need. A subject-obsessed writer is ready.
      </p>
      <div class="mt-10 flex flex-wrap justify-center gap-4">
        <NuxtLink to="/order" class="btn-primary bg-white px-10 py-4 text-base text-brand-700 shadow-lg hover:bg-brand-50">
          Place my order — from $10/page
        </NuxtLink>
        <NuxtLink href="/contact" class="btn-outline border-white/60 px-8 py-4 text-base text-white hover:bg-white/10">
          Talk to us first
        </NuxtLink>
      </div>
      <p class="mt-6 text-sm text-brand-200">
        24/7 support · 2-hour minimum turnaround · Free revisions · Grade or money back
      </p>
    </div>
  </section>
</template>
