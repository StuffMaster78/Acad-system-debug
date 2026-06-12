<script setup lang="ts">
// CMS-driven list merged with local enrichment (icon, hero copy, includes)
const services = useCmsServiceList()
const { getBySlug } = useServices()

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
        url: `https://researchpapermate.com/services/${s.slug}`,
      })),
    }),
  }],
})
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="relative overflow-hidden bg-brand-900 py-20 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-80 w-80 rounded-full bg-brand-600 opacity-20 blur-[100px]" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="mb-4 text-xs font-bold uppercase tracking-widest text-brand-300">9 service types · 100+ subjects</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">
          Every paper type.<br class="hidden sm:block" /> Every subject. Real experts.
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-brand-200">
          From first-year essays to PhD dissertations — written by verified Master's and PhD specialists who understand your subject and your marker's expectations.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
            Place an order — from $15/page
          </NuxtLink>
          <NuxtLink to="/pricing" class="inline-flex items-center rounded-xl border border-white/20 bg-white/5 px-8 py-3.5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10">
            See pricing
          </NuxtLink>
        </div>
        <div class="mt-6 flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm text-brand-300">
          <span>✓ Grade or money back</span>
          <span>✓ Free Turnitin report</span>
          <span>✓ Zero AI content</span>
        </div>
      </div>
    </section>

    <!-- Paper types grid -->
    <section class="bg-white py-16" id="paper-types">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mb-8 flex items-end justify-between gap-4">
          <div>
            <h2 class="section-heading">Paper types we handle</h2>
            <p class="mt-2 text-slate-500">Each service type has a dedicated team of specialists.</p>
          </div>
          <NuxtLink href="/order" class="hidden shrink-0 text-sm font-semibold text-brand-600 hover:underline sm:block">
            Place order →
          </NuxtLink>
        </div>

        <!-- Mobile + tablet: horizontal scroll with snap -->
        <div class="-mx-4 sm:-mx-6 lg:mx-0">
          <div
            class="flex gap-5 overflow-x-auto scroll-smooth snap-x snap-mandatory px-4 pb-4 sm:px-6 lg:hidden"
            style="scrollbar-width: none;"
          >
            <NuxtLink
              v-for="s in services"
              :key="s.slug"
              :href="`/services/${s.slug}`"
              class="group flex w-72 shrink-0 snap-start flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition-shadow hover:border-brand-200 hover:shadow-md"
            >
              <div class="mb-4 flex items-center gap-3">
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
                  <Icon :name="s.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
                </div>
                <h3 class="font-semibold leading-tight text-slate-900 transition-colors group-hover:text-brand-700">
                  {{ s.navLabel }}
                </h3>
              </div>
              <p v-if="s.heroSub" class="flex-1 text-sm leading-relaxed text-slate-500 line-clamp-3">{{ s.heroSub }}</p>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <span class="text-sm font-bold text-brand-700">From ${{ s.priceFrom }}/page</span>
                <span class="text-xs font-medium text-brand-600 group-hover:underline">Details →</span>
              </div>
            </NuxtLink>
          </div>

          <!-- Desktop: 3-col grid -->
          <div class="hidden lg:grid grid-cols-3 gap-6">
            <NuxtLink
              v-for="s in services"
              :key="s.slug"
              :href="`/services/${s.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-100 bg-white p-6 shadow-sm transition-shadow hover:border-brand-200 hover:shadow-md"
            >
              <div class="mb-4 flex items-center gap-3">
                <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
                  <Icon :name="s.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
                </div>
                <h3 class="text-lg font-semibold text-slate-900 transition-colors group-hover:text-brand-700">
                  {{ s.navLabel }}
                </h3>
              </div>
              <p v-if="s.heroSub" class="flex-1 text-sm leading-relaxed text-slate-600">{{ s.heroSub }}</p>
              <ul v-if="getBySlug(s.slug)?.includes?.length" class="mt-4 space-y-1.5">
                <li v-for="b in getBySlug(s.slug)!.includes.slice(0, 3)" :key="b"
                    class="flex items-start gap-2 text-sm text-slate-500">
                  <Icon name="check" class="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-500" />
                  {{ b }}
                </li>
              </ul>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
                <span class="text-sm font-bold text-brand-700">From ${{ s.priceFrom }}/page</span>
                <span class="text-xs font-medium text-brand-600 group-hover:underline">Learn more →</span>
              </div>
            </NuxtLink>
          </div>
        </div>

        <p class="mt-4 text-center text-xs text-slate-400 lg:hidden">← Scroll to see all paper types →</p>
      </div>
    </section>

    <!-- Subjects -->
    <section class="bg-slate-50" id="subjects">
      <div class="section">
        <h2 class="section-heading text-center">100+ subjects covered</h2>
        <p class="section-sub text-center">Writers hired for subject-matter expertise, not just writing ability.</p>
        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="group in subjectAreas" :key="group.area">
            <h3 class="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ group.area }}</h3>
            <ul class="space-y-2">
              <li v-for="sub in group.subjects" :key="sub"
                class="flex cursor-default items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700 transition-colors hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700">
                <Icon name="check" class="h-3 w-3 shrink-0 text-brand-500" />
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
            <div class="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100">
              <Icon :name="usp.icon" class="h-5 w-5 text-brand-600" />
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
    <section class="bg-brand-50 py-16">
      <div class="mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-6 text-center text-xs font-bold uppercase tracking-widest text-brand-600">Get your instant quote</p>
        <MultiStepOrderForm />
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-900 py-16 text-center">
      <div class="mx-auto max-w-2xl px-4">
        <h2 class="text-3xl font-bold text-white">Not sure what you need?</h2>
        <p class="mt-4 text-brand-200">Describe your assignment and we'll match you with the right subject expert in minutes.</p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50">
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
