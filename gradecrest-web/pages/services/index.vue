<script setup lang="ts">
import { ArrowRight } from '@lucide/vue'
import type { CmsServicePageListItem } from '~/types/cms'

useSeoMeta({
  title: 'Academic Writing Services — Essays, Research Papers, Dissertations | GradeCrest',
  description: 'Expert academic writing across 100+ subjects. Essays, research papers, dissertations, nursing, law, business, data analysis and more. Human-written, grade guaranteed.',
  ogTitle: 'GradeCrest Academic Writing Services',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useSeoBase('https://gradecrest.com/services')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Services', url: 'https://gradecrest.com/services' },
])

const app = useAppUrl()

const { data: cmsServices } = await useAsyncData(
  'cms-service-pages',
  () => fetchCmsServicePages(),
  { default: () => [] },
)

type ServiceCard = {
  slug: string
  title: string
  price: number
  desc: string
}

type ServiceCategory = {
  title: string
  services: ServiceCard[]
}

const categories = [
  {
    title: 'Writing & Essays',
    services: [
      { slug: 'essay-writing',        title: 'Essay Writing',           price: 13, desc: 'Argumentative, analytical, descriptive, and reflective essays across every subject and level.' },
      { slug: 'research-papers',       title: 'Research Papers',         price: 15, desc: 'Original, citation-rich research papers with a full methodology and proper academic structure.' },
      { slug: 'term-papers',           title: 'Term Papers',             price: 14, desc: 'Well-argued semester papers delivered on time and formatted to your institution\'s requirements.' },
      { slug: 'case-studies',          title: 'Case Studies',            price: 15, desc: 'In-depth case analysis with structured argumentation and evidence-backed conclusions.' },
      { slug: 'literature-review',     title: 'Literature Reviews',      price: 16, desc: 'Comprehensive reviews synthesising sources into a coherent scholarly narrative.' },
      { slug: 'coursework',            title: 'Coursework Help',         price: 14, desc: 'Ongoing assignment support from a single dedicated writer throughout your module.' },
    ],
  },
  {
    title: 'Advanced Academic Work',
    services: [
      { slug: 'dissertations',         title: 'Dissertations & Theses',  price: 22, desc: 'Full dissertation support: proposal, all chapters, methodology, data analysis, discussion.' },
      { slug: 'thesis-writing',        title: 'Thesis Writing',          price: 22, desc: 'Graduate-level thesis support with a writer matched to your exact field and level.' },
      { slug: 'data-analysis',         title: 'Data Analysis',           price: 20, desc: 'SPSS, R, Python, or Excel analysis with written interpretation and charts.' },
      { slug: 'capstone-projects',     title: 'Capstone Projects',       price: 22, desc: 'End-of-programme projects with research, analysis, and presentation support.' },
    ],
  },
  {
    title: 'Specialist Subjects',
    services: [
      { slug: 'nursing-essays',        title: 'Nursing Essays',          price: 15, desc: 'SOAP notes, care plans, EBP papers, pharmacology, and clinical case studies.' },
      { slug: 'admission-essays',      title: 'Admission Essays',        price: 15, desc: 'Personal statements, college essays, and graduate school applications.' },
      { slug: 'online-class-help',     title: 'Online Class Help',       price: 14, desc: 'Assignment completion for fully online courses — consistent quality throughout.' },
      { slug: 'homework-help',         title: 'Homework Help',           price: 13, desc: 'Day-to-day assignment support across any subject, any level.' },
    ],
  },
  {
    title: 'Editing & Quality',
    services: [
      { slug: 'editing-proofreading',  title: 'Editing & Proofreading',  price: 8,  desc: 'Grammar, clarity, structure, flow, and formatting corrected by professional editors.' },
    ],
  },
] satisfies ServiceCategory[]

const servicePrice = (service: CmsServicePageListItem) => {
  const parsed = Number(service.pricing_from)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 14
}

const cmsCategories = computed<ServiceCategory[]>(() => {
  const grouped = new Map<string, ServiceCard[]>()

  for (const service of cmsServices.value) {
    const category = service.category?.name || 'Services'
    const current = grouped.get(category) ?? []
    current.push({
      slug: service.slug,
      title: service.title,
      price: servicePrice(service),
      desc: service.search_description || 'Custom academic support from verified GradeCrest experts.',
    })
    grouped.set(category, current)
  }

  return Array.from(grouped.entries()).map(([title, services]) => ({
    title,
    services,
  }))
})

// ── Active tab ────────────────────────────────────────────────────────────────
const activeTab = ref('all')
const tabs = computed(() => [
  { key: 'all', label: 'All services' },
  ...categories.map(c => ({ key: c.title, label: c.title })),
])

// ── Search + pagination (for "All services" tab / CMS pages) ─────────────────
const PER_PAGE = 12
const query    = ref('')
const page     = ref(1)

// All CMS services flattened (with static enrichment where available)
const allCmsServices = computed<ServiceCard[]>(() => {
  const raw = cmsServices.value
  if (!raw?.length) {
    // Fallback: flatten static categories
    return categories.flatMap(c => c.services)
  }
  return raw.map(s => ({
    slug:  s.slug,
    title: s.title,
    price: servicePrice(s),
    desc:  s.search_description || 'Custom academic writing by a verified GradeCrest expert.',
  }))
})

const filteredServices = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return allCmsServices.value
  return allCmsServices.value.filter(
    s => s.title.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q),
  )
})

const totalPages = computed(() => Math.ceil(filteredServices.value.length / PER_PAGE))

const pagedServices = computed(() =>
  filteredServices.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE),
)

watch([query, activeTab], () => { page.value = 1 })

function goPage(n: number) {
  page.value = Math.max(1, Math.min(n, totalPages.value))
  // Scroll to top of service grid smoothly
  if (import.meta.client) {
    document.getElementById('svc-grid')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// ── Category tab view (curated, non-paginated) ────────────────────────────────
const tabServices = computed(() => {
  if (activeTab.value === 'all') return []
  return categories.find(c => c.title === activeTab.value)?.services ?? []
})
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="relative overflow-hidden bg-forest-950 py-16 text-center">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="mb-3 text-xs font-semibold uppercase tracking-widest text-gold-400">What we offer</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Academic Writing Services</h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-slate-300">
          174 services across 100+ subjects. Undergraduate through PhD. Every paper by a verified expert.
        </p>
        <!-- Search bar -->
        <div class="mx-auto mt-8 max-w-md">
          <div class="relative">
            <svg class="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-slate-400 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
            </svg>
            <input
              v-model="query"
              type="search"
              placeholder="Search services…"
              class="w-full rounded-xl border border-white/20 bg-white/10 py-3 pl-10 pr-4 text-sm text-white placeholder:text-slate-400 backdrop-blur-sm focus:border-gc-400 focus:outline-none focus:ring-1 focus:ring-gc-400"
              @input="activeTab = 'all'"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Tab bar -->
    <div class="sticky top-16 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex gap-0 overflow-x-auto scrollbar-none">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="shrink-0 border-b-2 px-4 py-3.5 text-sm font-medium whitespace-nowrap transition-colors"
            :class="activeTab === tab.key
              ? 'border-gc-600 text-gc-700'
              : 'border-transparent text-graphite hover:text-ink'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>
      </div>
    </div>

    <!-- ── ALL SERVICES tab (paginated + searchable) ──────────────────────── -->
    <section v-if="activeTab === 'all'" id="svc-grid" class="bg-white py-12 scroll-mt-32">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

        <!-- Result count -->
        <div class="mb-6 flex items-center justify-between gap-4">
          <p class="text-sm text-graphite">
            <template v-if="query">
              <span class="font-semibold text-ink">{{ filteredServices.length }}</span> results for "<span class="font-medium">{{ query }}</span>"
            </template>
            <template v-else>
              Showing <span class="font-semibold text-ink">{{ (page - 1) * 12 + 1 }}–{{ Math.min(page * 12, filteredServices.length) }}</span>
              of <span class="font-semibold text-ink">{{ filteredServices.length }}</span> services
            </template>
          </p>
          <button
            v-if="query"
            class="text-xs font-semibold text-gc-600 hover:underline"
            @click="query = ''"
          >Clear search</button>
        </div>

        <!-- Grid -->
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="svc in pagedServices"
            :key="svc.slug"
            :to="`/${svc.slug}`"
            class="group flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition-all hover:-translate-y-0.5 hover:border-gc-300 hover:shadow-lift"
          >
            <div>
              <h3 class="text-sm font-semibold text-ink transition-colors group-hover:text-gc-600">{{ svc.title }}</h3>
              <p class="mt-1.5 text-xs leading-relaxed text-graphite line-clamp-2">{{ svc.desc }}</p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <span class="text-xs font-semibold text-graphite">From <span class="text-ink">${{ svc.price }}/page</span></span>
              <ArrowRight class="size-4 text-gc-600 opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          </NuxtLink>
        </div>

        <!-- Empty state -->
        <div v-if="!pagedServices.length" class="py-20 text-center">
          <p class="text-graphite">No services match "<span class="font-medium text-ink">{{ query }}</span>".</p>
          <button class="mt-3 text-sm font-semibold text-gc-600 hover:underline" @click="query = ''">Clear search</button>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
          <button
            :disabled="page === 1"
            class="flex size-9 items-center justify-center rounded-lg border border-slate-200 text-sm font-semibold text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            @click="goPage(page - 1)"
          >←</button>

          <template v-for="p in totalPages" :key="p">
            <!-- Show first, last, current ±1, and ellipsis -->
            <template v-if="p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1)">
              <button
                class="flex size-9 items-center justify-center rounded-lg border text-sm font-semibold transition-colors"
                :class="p === page
                  ? 'border-gc-600 bg-gc-600 text-white'
                  : 'border-slate-200 text-graphite hover:bg-slate-50'"
                @click="goPage(p)"
              >{{ p }}</button>
            </template>
            <span
              v-else-if="p === page - 2 || p === page + 2"
              class="flex size-9 items-center justify-center text-sm text-slate-400"
            >…</span>
          </template>

          <button
            :disabled="page === totalPages"
            class="flex size-9 items-center justify-center rounded-lg border border-slate-200 text-sm font-semibold text-graphite transition-colors hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
            @click="goPage(page + 1)"
          >→</button>
        </div>
      </div>
    </section>

    <!-- ── CATEGORY tabs (curated, no pagination) ─────────────────────────── -->
    <section v-else id="svc-grid" class="bg-white py-12 scroll-mt-32">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="svc in tabServices"
            :key="svc.slug"
            :to="`/${svc.slug}`"
            class="group flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-card transition-all hover:-translate-y-0.5 hover:border-gc-300 hover:shadow-lift"
          >
            <div>
              <h3 class="text-sm font-semibold text-ink transition-colors group-hover:text-gc-600">{{ svc.title }}</h3>
              <p class="mt-1.5 text-xs leading-relaxed text-graphite">{{ svc.desc }}</p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <span class="text-xs font-semibold text-graphite">From <span class="text-ink">${{ svc.price }}/page</span></span>
              <ArrowRight class="size-4 text-gc-600 opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          </NuxtLink>
        </div>
        <p class="mt-8 text-center text-sm text-graphite">
          Looking for something else?
          <button class="font-semibold text-gc-600 hover:underline" @click="activeTab = 'all'">Browse all 174 services →</button>
        </p>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Not sure which service you need?</h2>
        <p class="text-sm text-graphite">Place an order and describe your assignment — we'll match you with the right expert.</p>
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white transition-colors hover:bg-gc-700">
          Order now — from $13/page <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
