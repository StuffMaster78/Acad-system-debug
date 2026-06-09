<script setup lang="ts">
const { getAll } = useServices()
const services = getAll()

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
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Academic Writing Services',
      itemListElement: services.map((s, i) => ({
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
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-20 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Academic Writing Services</h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-brand-100">
          Expert writers across every discipline — STEM, business, law, healthcare, humanities.
          If it needs to be written, we cover it.
        </p>
        <div class="mt-8 flex flex-wrap justify-center gap-4">
          <NuxtLink to="/order" class="btn-primary bg-white text-brand-700 hover:bg-brand-50 px-8 py-3.5 text-base">
            Get started from $15/page
          </NuxtLink>
          <NuxtLink to="/pricing" class="btn-outline border-white/60 text-white hover:bg-white/10 px-8 py-3.5 text-base">
            See pricing
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Paper types grid -->
    <section class="section" id="paper-types">
      <h2 class="section-heading text-center">Paper types we handle</h2>
      <p class="section-sub text-center">Each service type has a dedicated team of specialists.</p>
      <div class="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="s in services"
          :key="s.slug"
          :href="`/services/${s.slug}`"
          class="card group flex flex-col transition-shadow hover:shadow-md"
        >
          <div class="mb-4 flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100 transition-colors group-hover:bg-brand-600">
              <Icon :name="s.icon" class="h-5 w-5 text-brand-600 transition-colors group-hover:text-white" />
            </div>
            <h2 class="text-lg font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">
              {{ s.navLabel }}
            </h2>
          </div>
          <p class="flex-1 text-sm text-slate-600 leading-relaxed">{{ s.hero.sub }}</p>
          <ul class="mt-4 space-y-1.5">
            <li v-for="b in s.includes.slice(0, 3)" :key="b" class="flex items-start gap-2 text-sm text-slate-500">
              <span class="mt-0.5 font-bold text-brand-500">✓</span>{{ b }}
            </li>
          </ul>
          <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
            <span class="text-sm font-semibold text-brand-700">From ${{ s.priceFrom }}/page</span>
            <span class="text-xs font-medium text-brand-600 group-hover:underline">Learn more →</span>
          </div>
        </NuxtLink>
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
                class="rounded-lg border border-brand-100 bg-white px-3 py-2 text-sm text-slate-700">
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

    <!-- Calculator -->
    <section class="bg-slate-50">
      <div class="section max-w-2xl">
        <h2 class="section-heading text-center">Get your instant quote</h2>
        <p class="section-sub text-center">Pick your level and deadline — see your price in seconds.</p>
        <div class="mt-10">
          <ClientOnly>
            <OrderCalculator />
            <template #fallback><div class="h-72 animate-pulse rounded-2xl bg-slate-200" /></template>
          </ClientOnly>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="bg-brand-700 py-16 text-center">
      <h2 class="font-serif text-3xl font-bold text-white">Not sure what you need?</h2>
      <p class="mt-4 text-brand-200">Place an order, describe your task, and we'll match you with the right expert.</p>
      <NuxtLink to="/order" class="btn-primary mt-8 bg-white text-brand-700 hover:bg-brand-50 px-10 py-4 text-base">
        Start your order — from $15/page
      </NuxtLink>
    </section>
  </div>
</template>
