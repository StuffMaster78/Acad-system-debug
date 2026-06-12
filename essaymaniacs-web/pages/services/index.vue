<script setup lang="ts">
const services = useCmsServiceList()
const { getAll, getBySlug } = useServices()

// Category tabs — group services by type
const tabs = [
  { id: 'all',       label: 'All services' },
  { id: 'essays',    label: 'Essays' },
  { id: 'research',  label: 'Research & Theses' },
  { id: 'admission', label: 'Admission' },
  { id: 'editing',   label: 'Editing & Other' },
]

const slugsByTab: Record<string, string[]> = {
  essays:    ['essays', 'argumentative-essays', 'reflective-essays', 'term-papers', 'coursework', 'book-reports', 'creative-writing'],
  research:  ['research-papers', 'dissertations', 'literature-reviews', 'annotated-bibliographies', 'lab-reports', 'data-analysis'],
  admission: ['admission-essays', 'scholarship-essays', 'personal-statements'],
  editing:   ['proofreading', 'presentations', 'business-reports', 'case-studies'],
}

const activeTab = ref('all')

const displayed = computed(() => {
  const all = services.value.length ? services.value : getAll().map(s => ({
    slug: s.slug, title: s.title, navLabel: s.navLabel, icon: s.icon,
    heroSub: s.hero.sub, priceFrom: s.priceFrom, category: null,
  }))
  if (activeTab.value === 'all') return all
  const slugs = slugsByTab[activeTab.value] ?? []
  return all.filter(s => slugs.includes(s.slug))
})

const trustItems = [
  { icon: 'bot',          text: 'Zero AI content — every essay is human-written' },
  { icon: 'shield-check', text: 'Free plagiarism report with every order' },
  { icon: 'refresh-cw',  text: 'Unlimited free revisions within your window' },
  { icon: 'trophy',       text: 'Grade or money back — no questions asked' },
  { icon: 'zap',          text: 'As fast as 2 hours for urgent orders' },
  { icon: 'lock',         text: 'Complete confidentiality, always' },
]

useSeoMeta({
  title: 'Essay & Academic Writing Services — 20 Types | EssayManiacs',
  description: 'Expert essays, research papers, dissertations, admission essays, and more — written by subject-obsessed specialists. From $10/page.',
})

useHead({
  link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/services' }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Essay Writing Services',
      itemListElement: (services.value.length ? services.value : getAll()).map((s, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        name: s.title ?? s.navLabel,
        url: `https://essaymaniacs.com/services/${s.slug}`,
      })),
    }),
  }],
})
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-64 w-64 rounded-full bg-brand-500 opacity-20 blur-[80px]" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">20 essay types · 100+ subjects</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Find your essay type.<br class="hidden sm:block" /> Find your subject specialist.</h1>
        <p class="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-brand-200">From a 500-word argumentative essay to a PhD dissertation — matched to a writer who has a degree in your exact subject and has written dozens of them.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">Place an order — from $10/page</NuxtLink>
          <NuxtLink to="/pricing" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10">See pricing</NuxtLink>
        </div>
        <div class="mt-6 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-brand-300">
          <span>✓ Grade or money back</span><span>✓ Zero AI</span><span>✓ Subject-matched writer</span>
        </div>
      </div>
    </section>

    <!-- ── Category tabs ─────────────────────────────────────────────── -->
    <section class="sticky top-16 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex overflow-x-auto" style="scrollbar-width: none;">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="shrink-0 border-b-2 px-5 py-4 text-sm font-semibold transition-colors"
            :class="activeTab === tab.id
              ? 'border-brand-600 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
            <span
              v-if="tab.id !== 'all'"
              class="ml-1.5 rounded-full px-1.5 py-0.5 text-[10px]"
              :class="activeTab === tab.id ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-500'"
            >{{ slugsByTab[tab.id]?.length }}</span>
          </button>
        </div>
      </div>
    </section>

    <!-- ── Service cards ─────────────────────────────────────────────── -->
    <section class="bg-white py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

        <Transition name="fade" mode="out-in">
          <div :key="activeTab" class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            <NuxtLink
              v-for="s in displayed"
              :key="s.slug"
              :href="`/services/${s.slug}`"
              class="group relative flex flex-col overflow-hidden rounded-3xl border border-slate-100 bg-white p-7 transition-all hover:border-brand-200 hover:shadow-md"
            >
              <!-- Accent corner -->
              <div class="absolute right-0 top-0 h-16 w-16 overflow-hidden rounded-bl-none rounded-br-none rounded-tl-none rounded-tr-3xl">
                <div class="absolute right-0 top-0 h-10 w-10 translate-x-4 -translate-y-4 rotate-45 bg-brand-50 transition-colors group-hover:bg-brand-100" />
              </div>

              <div class="mb-5 flex items-center gap-4">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-100 transition-colors group-hover:bg-brand-700">
                  <Icon :name="s.icon" class="h-6 w-6 text-brand-700 transition-colors group-hover:text-white" />
                </div>
                <div>
                  <h2 class="font-bold text-slate-900 transition-colors group-hover:text-brand-700 leading-tight">{{ s.navLabel }}</h2>
                  <p class="text-sm font-semibold text-brand-600">From ${{ s.priceFrom }}/page</p>
                </div>
              </div>

              <p v-if="s.heroSub" class="flex-1 text-sm leading-relaxed text-slate-600">{{ s.heroSub }}</p>

              <!-- Includes preview -->
              <ul v-if="getBySlug(s.slug)?.includes?.length" class="mt-4 space-y-1.5 border-t border-slate-100 pt-4">
                <li
                  v-for="b in getBySlug(s.slug)!.includes.slice(0, 2)"
                  :key="b"
                  class="flex items-start gap-2 text-xs text-slate-500"
                >
                  <svg class="mt-0.5 h-3 w-3 shrink-0 text-brand-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                  {{ b }}
                </li>
              </ul>

              <div class="mt-5 flex items-center justify-between">
                <span class="text-xs font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">
                  View details →
                </span>
              </div>
            </NuxtLink>
          </div>
        </Transition>

      </div>
    </section>

    <!-- ── Subjects band ─────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-16">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-10 text-center">
          <h2 class="font-serif text-3xl font-bold text-white">100+ subjects covered</h2>
          <p class="mt-3 text-brand-300">Writers hired for subject-matter expertise, not just writing ability.</p>
        </div>
        <div class="flex flex-wrap justify-center gap-2">
          <span
            v-for="sub in ['History', 'Psychology', 'Sociology', 'Business', 'Law', 'Economics', 'Literature', 'Philosophy', 'Biology', 'Chemistry', 'Engineering', 'Nursing', 'Marketing', 'Finance', 'Political Science', 'Education', 'Statistics', 'Media Studies', 'Accounting', 'Environmental Science']"
            :key="sub"
            class="rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-brand-200"
          >{{ sub }}</span>
          <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-brand-400">+80 more</span>
        </div>
      </div>
    </section>

    <!-- ── Order form ────────────────────────────────────────────────── -->
    <section class="bg-brand-50 py-16">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-6 text-center text-xs font-bold uppercase tracking-widest text-brand-600">Get your instant quote</p>
        <MultiStepOrderForm />
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-16 text-center">
      <div class="mx-auto max-w-2xl px-4">
        <h2 class="text-3xl font-bold text-white">Not sure which type fits your assignment?</h2>
        <p class="mt-4 text-lg text-brand-200">Describe it and we'll match you with the right specialist in minutes.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">Start my order — from $10/page</NuxtLink>
          <NuxtLink to="/contact" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-white/10">Ask us first</NuxtLink>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
