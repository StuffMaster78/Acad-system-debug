<script setup lang="ts">
import { ArrowRight } from '@lucide/vue'
import type { CmsServicePageListItem } from '~/types/cms'

useSeoMeta({
  title: 'Academic Writing Services — Essays, Research Papers, Dissertations | GradeCrest',
  description: 'Expert academic writing across 100+ subjects. Essays, research papers, dissertations, nursing, law, business, data analysis and more. Human-written, grade guaranteed.',
  ogTitle: 'GradeCrest Academic Writing Services',
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

const visibleCategories = computed(() => cmsCategories.value.length ? cmsCategories.value : categories)
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-navy-900 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">What we offer</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Academic Writing Services</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">
          100+ subjects covered. Undergraduate through PhD. Every paper written by a verified human expert.
        </p>
      </div>
    </section>

    <!-- Categories -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-16">
        <div v-for="cat in visibleCategories" :key="cat.title">
          <h2 class="text-xl font-bold text-ink mb-6 pb-3 border-b border-slate-200">{{ cat.title }}</h2>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="svc in cat.services" :key="svc.slug"
              :to="`/services/${svc.slug}`"
              class="group flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-card hover:shadow-lift hover:-translate-y-0.5 transition-all"
            >
              <div>
                <h3 class="text-sm font-semibold text-ink group-hover:text-gc-600 transition-colors">{{ svc.title }}</h3>
                <p class="mt-1.5 text-xs text-graphite leading-relaxed">{{ svc.desc }}</p>
              </div>
              <div class="mt-4 flex items-center justify-between">
                <span class="text-xs font-semibold text-graphite">From <span class="text-ink">${{ svc.price }}/page</span></span>
                <ArrowRight class="size-4 text-gc-600 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Not sure which service you need?</h2>
        <p class="text-sm text-graphite">Place an order and describe your assignment — we'll match you with the right expert.</p>
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
