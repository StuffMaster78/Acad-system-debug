<script setup lang="ts">
// CMS-driven list merged with local enrichment (icon, hero copy, includes)
const services = useCmsServiceList()
const { getBySlug } = useServices()

const popularSlugs = new Set(['research-papers', 'essays', 'dissertations', 'literature-reviews'])
const popularLabel: Record<string, string> = {
  'research-papers':   'Most popular',
  'dissertations':     'Full support',
  'essays':            'Popular',
  'literature-reviews':'Popular',
}

// ── Category tabs ─────────────────────────────────────────────────────────────
const serviceCategories = [
  { key: 'all',        label: 'All' },
  { key: 'papers',     label: 'Papers & Essays' },
  { key: 'research',   label: 'Research' },
  { key: 'analysis',   label: 'Data & Analysis' },
  { key: 'specialist', label: 'Specialist' },
] as const

type TabKey = typeof serviceCategories[number]['key']
const activeTab = ref<TabKey>('all')

const slugsByTab: Record<TabKey, string[]> = {
  all:        [],
  papers:     ['essays', 'coursework', 'presentations', 'case-studies'],
  research:   ['research-papers', 'literature-reviews', 'dissertations'],
  analysis:   ['data-analysis', 'lab-reports'],
  specialist: ['research-papers', 'dissertations', 'literature-reviews', 'data-analysis'],
}

const visibleServices = computed(() => {
  if (activeTab.value === 'all') return services.value
  const slugs = slugsByTab[activeTab.value]
  const bySlug = services.value.filter(s => slugs.includes(s.slug))
  return bySlug.length ? bySlug : services.value
})

const subjectAreas = [
  {
    area: 'STEM',
    subjects: ['Biology', 'Chemistry', 'Physics', 'Mathematics', 'Statistics', 'Engineering', 'Computer Science', 'Environmental Science'],
  },
  {
    area: 'Business & Finance',
    subjects: ['Accounting', 'Finance', 'Marketing', 'HR Management', 'Supply Chain', 'Economics', 'Entrepreneurship', 'Business Law'],
  },
  {
    area: 'Healthcare & Social Sciences',
    subjects: ['Nursing', 'Public Health', 'Psychology', 'Sociology', 'Social Work', 'Counseling', 'Pharmacology'],
  },
  {
    area: 'Humanities & Law',
    subjects: ['History', 'Literature', 'Philosophy', 'Law', 'Political Science', 'Cultural Studies', 'Media Studies', 'Education'],
  },
]

const usps = [
  { icon: 'message-square', title: 'Direct writer communication', desc: 'Message your writer throughout the order — share files, ask questions, give feedback in real time.' },
  { icon: 'bot',            title: 'Zero AI content guarantee',   desc: 'Every paper is 100% human-written. We provide a free AI-detection report on request.' },
  { icon: 'zap',            title: '2-hour minimum turnaround',   desc: 'Need it urgently? We can deliver in as little as 2 hours for shorter assignments.' },
  { icon: 'shield-check',   title: 'Anti-plagiarism guarantee',   desc: 'Every paper is checked against major databases. Free Turnitin-style report included.' },
  { icon: 'trophy',         title: 'Grade or money back',         desc: "We stand behind our work. If the stated grade target isn't met, we refund or rewrite." },
  { icon: 'lock',           title: 'Complete privacy',            desc: 'Your identity and order details are never shared with any third party.' },
]

useSeoMeta({
  title: 'Academic Writing Services — 100+ Subjects | ResearchPaperMate',
  description: 'Expert help with research papers, essays, dissertations, case studies, lab reports, data analysis, and more — across 100+ academic subjects. From $15/page.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://researchpapermate.com/services' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Academic Writing Services',
      itemListElement: services.value.map((s, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        name: s.title,
        url: `https://researchpapermate.com/${s.slug}`,
      })),
    }),
  }],
})
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="relative overflow-hidden bg-claret-950 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-80 w-80 rounded-full bg-brand-600 opacity-20 blur-[100px]" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-amber-400">9 service types · 100+ subjects</p>
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">
          Every paper type.<br class="hidden sm:block" /> Every subject. Real experts.
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-claret-200">
          From first-year essays to PhD dissertations — written by verified Master's and PhD specialists who understand your subject and your marker's expectations.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-900 shadow-lg transition-colors hover:bg-parchment-100">
            Place an order — from $15/page
          </NuxtLink>
          <NuxtLink to="/pricing" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
            See pricing
          </NuxtLink>
        </div>
        <div class="mt-6 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-amber-400">
          <span>✓ Grade or money back</span>
          <span>✓ Free Turnitin report</span>
          <span>✓ Zero AI content</span>
        </div>
      </div>
    </section>

    <!-- Paper types grid -->
    <section class="bg-white py-16" id="paper-types">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="mb-8 text-center">
          <h2 class="font-serif text-3xl font-bold text-ink-DEFAULT sm:text-4xl">Paper types we handle</h2>
          <p class="mt-3 text-ink-secondary">Every service has a dedicated team of subject specialists.</p>
        </div>

        <!-- Tab bar -->
        <div class="mb-8 flex flex-wrap justify-center gap-2">
          <button
            v-for="tab in serviceCategories"
            :key="tab.key"
            class="rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors"
            :class="activeTab === tab.key
              ? 'border-claret-700 bg-claret-900 text-white'
              : 'border-parchment-300 bg-white text-ink-secondary hover:border-claret-400 hover:text-ink-DEFAULT'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <div class="grid gap-5 sm:grid-cols-2">
          <NuxtLink
            v-for="s in visibleServices"
            :key="s.slug"
            :href="`/${s.slug}`"
            class="group relative flex flex-col rounded-2xl border bg-white p-6 shadow-sm transition-all hover:shadow-md"
            :class="popularSlugs.has(s.slug)
              ? 'border-amber-300 ring-1 ring-amber-200'
              : 'border-parchment-300 hover:border-amber-200'"
          >
            <!-- Popular badge -->
            <div
              v-if="popularSlugs.has(s.slug)"
              class="absolute -top-3 left-5 rounded-full bg-amber-500 px-3 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white shadow"
            >
              {{ popularLabel[s.slug] ?? 'Popular' }}
            </div>

            <!-- Header row: icon + title + price -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3">
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-parchment-200 transition-colors group-hover:bg-claret-900">
                  <Icon :name="s.icon" class="h-5 w-5 text-claret-800 transition-colors group-hover:text-amber-400" />
                </div>
                <h3 class="font-bold leading-tight text-ink-DEFAULT transition-colors group-hover:text-claret-800">
                  {{ s.navLabel }}
                </h3>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-lg font-bold text-claret-800">${{ s.priceFrom }}</p>
                <p class="text-[10px] text-ink-muted">/page</p>
              </div>
            </div>

            <!-- Description -->
            <p v-if="s.heroSub" class="mt-3 text-sm leading-relaxed text-ink-secondary line-clamp-2">{{ s.heroSub }}</p>

            <!-- Includes bullets -->
            <ul v-if="getBySlug(s.slug)?.includes?.length" class="mt-4 space-y-1.5">
              <li
                v-for="b in getBySlug(s.slug)!.includes.slice(0, 3)"
                :key="b"
                class="flex items-start gap-2 text-xs text-ink-secondary"
              >
                <svg class="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
                </svg>
                {{ b }}
              </li>
            </ul>

            <!-- CTA -->
            <div class="mt-5 pt-4 border-t border-parchment-200">
              <span class="inline-flex items-center gap-1.5 rounded-lg bg-claret-900 px-4 py-2 text-xs font-bold text-white transition-colors group-hover:bg-claret-800">
                Order {{ s.navLabel.toLowerCase() }}
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
              </span>
            </div>
          </NuxtLink>
        </div>

        <p class="mt-10 text-center text-sm text-ink-muted">
          Don't see your paper type?
          <NuxtLink href="/contact" class="font-semibold text-amber-700 hover:underline">Tell us what you need →</NuxtLink>
        </p>
      </div>
    </section>

    <!-- Subjects -->
    <section class="bg-parchment-100" id="subjects">
      <div class="section">
        <h2 class="section-heading text-center">100+ subjects covered</h2>
        <p class="section-sub text-center">Writers hired for subject-matter expertise, not just writing ability.</p>
        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="group in subjectAreas" :key="group.area">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ group.area }}</h3>
            <ul class="space-y-2">
              <li v-for="sub in group.subjects" :key="sub"
                class="flex cursor-default items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition-colors hover:border-amber-200 hover:bg-parchment-100 hover:text-claret-700">
                <Icon name="check" class="h-3 w-3 shrink-0 text-amber-600" />
                {{ sub }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Why us -->
    <section class="bg-white">
      <div class="section">
        <h2 class="section-heading text-center">Why ResearchPaperMate?</h2>
        <p class="section-sub text-center">Built for students who need reliable, grade-backed academic help.</p>
        <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="usp in usps" :key="usp.title" class="flex gap-4">
            <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100">
              <Icon :name="usp.icon" class="h-5 w-5 text-amber-700" />
            </div>
            <div>
              <h3 class="font-semibold text-slate-900">{{ usp.title }}</h3>
              <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ usp.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Order form -->
    <section class="bg-parchment-100 py-16">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-6 text-center text-xs font-bold uppercase tracking-widest text-amber-700">Get your instant quote</p>
        <MultiStepOrderForm />
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-claret-950 py-16 text-center">
      <div class="mx-auto max-w-2xl px-4">
        <h2 class="font-serif text-3xl font-bold text-white">Not sure what you need?</h2>
        <p class="mt-4 text-claret-200">Describe your assignment and we'll match you with the right subject expert in minutes.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-claret-700 shadow-lg transition-colors hover:bg-parchment-100">
            Start your order — from $15/page
          </NuxtLink>
          <NuxtLink to="/contact" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10">
            Ask us first
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
