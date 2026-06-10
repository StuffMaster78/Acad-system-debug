<script setup lang="ts">
import { ArrowRight, Search, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Our Expert Writers — 600+ Verified Academic Specialists | GradeCrest',
  description: 'Meet GradeCrest\'s 600+ verified expert writers. All hold postgraduate degrees, verified credentials, and subject-specific expertise. Browse by subject.',
  ogTitle: 'GradeCrest Writers — 600+ Verified Experts',
})

useSeoBase('https://gradecrest.com/writers')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Writers', url: 'https://gradecrest.com/writers' },
])

const subjects = ['All', 'STEM', 'Health & Nursing', 'Business', 'Humanities', 'Law', 'Social Sciences']
const activeSubject = ref('All')

const writers = [
  { name: 'Dr. Sarah K.',    degree: 'PhD · Nursing',           orders: 1840, rating: 5.0, subjects: ['Nursing', 'Healthcare'],        tier: 'Expert',   initials: 'SK', available: true  },
  { name: 'Prof. James W.',  degree: 'PhD · English Literature', orders: 2310, rating: 5.0, subjects: ['Literature', 'History'],        tier: 'Expert',   initials: 'JW', available: true  },
  { name: 'Dr. Priya M.',    degree: 'PhD · Business Admin',    orders: 1560, rating: 4.9, subjects: ['MBA', 'Finance', 'Marketing'],   tier: 'Expert',   initials: 'PM', available: true  },
  { name: 'Dr. Emily C.',    degree: "Master's · Law",          orders:  920, rating: 5.0, subjects: ['Law', 'Criminology'],            tier: 'Advanced', initials: 'EC', available: true  },
  { name: 'Dr. Caleb R.',    degree: 'PhD · Statistics',        orders: 1280, rating: 5.0, subjects: ['Statistics', 'Data Analysis'],   tier: 'Expert',   initials: 'CR', available: false },
  { name: 'Prof. Nadia F.',  degree: 'PhD · Psychology',        orders: 1730, rating: 4.9, subjects: ['Psychology', 'Sociology'],       tier: 'Expert',   initials: 'NF', available: true  },
  { name: 'Dr. Marcus T.',   degree: 'PhD · Computer Science',  orders:  680, rating: 5.0, subjects: ['CS', 'Engineering', 'STEM'],    tier: 'Advanced', initials: 'MT', available: true  },
  { name: 'Dr. Amara D.',    degree: "Master's · Education",    orders:  450, rating: 4.9, subjects: ['Education', 'Sociology'],        tier: 'Standard', initials: 'AD', available: true  },
  { name: 'Prof. Lena V.',   degree: 'PhD · Chemistry',         orders:  860, rating: 5.0, subjects: ['Chemistry', 'Biology', 'STEM'], tier: 'Expert',   initials: 'LV', available: true  },
  { name: 'Dr. Hassan O.',   degree: 'PhD · Economics',         orders: 1100, rating: 4.9, subjects: ['Economics', 'Business', 'Finance'], tier: 'Expert', initials: 'HO', available: false},
  { name: 'Dr. Sophie R.',   degree: "Master's · Philosophy",   orders:  390, rating: 5.0, subjects: ['Philosophy', 'Ethics'],          tier: 'Standard', initials: 'SR', available: true  },
  { name: 'Prof. Kezia M.',  degree: 'PhD · Public Health',     orders:  740, rating: 5.0, subjects: ['Public Health', 'Nursing'],      tier: 'Advanced', initials: 'KM', available: true  },
]

const SUBJECT_FILTER: Record<string, string[]> = {
  'STEM':              ['Statistics', 'Data Analysis', 'CS', 'Engineering', 'Chemistry', 'Biology'],
  'Health & Nursing':  ['Nursing', 'Healthcare', 'Public Health'],
  'Business':          ['MBA', 'Finance', 'Marketing', 'Economics', 'Business'],
  'Humanities':        ['Literature', 'History', 'Philosophy', 'Ethics'],
  'Law':               ['Law', 'Criminology'],
  'Social Sciences':   ['Psychology', 'Sociology', 'Education'],
}

const filtered = computed(() => {
  if (activeSubject.value === 'All') return writers
  const terms = SUBJECT_FILTER[activeSubject.value] ?? []
  return writers.filter(w => w.subjects.some(s => terms.some(t => s.includes(t))))
})

const tierColor = { Expert: 'text-gc-700 bg-gc-50', Advanced: 'text-amber-700 bg-amber-50', Standard: 'text-slate-600 bg-slate-100' }
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-navy-900 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">The team</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">600+ Expert Writers</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">
          Every writer holds a postgraduate degree. Credentials are verified before a writer handles their first order.
        </p>
        <div class="mt-6 flex flex-wrap justify-center gap-6 text-sm text-slate-400">
          <span>✓ Verified degree credentials</span>
          <span>✓ Subject-specific expertise</span>
          <span>✓ Direct messaging included</span>
        </div>
      </div>
    </section>

    <!-- Filter + grid -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <!-- Subject filter tabs -->
        <div class="flex flex-wrap gap-2 mb-8">
          <button
            v-for="sub in subjects" :key="sub"
            class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
            :class="activeSubject === sub ? 'bg-gc-600 border-gc-600 text-white' : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
            @click="activeSubject = sub"
          >{{ sub }}</button>
        </div>

        <!-- Writer cards -->
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="w in filtered" :key="w.name"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card hover:shadow-lift transition-shadow"
          >
            <div class="flex items-start gap-3">
              <div class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-gc-50 text-sm font-bold text-gc-700">
                {{ w.initials }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center justify-between gap-1">
                  <p class="text-sm font-semibold text-ink truncate">{{ w.name }}</p>
                  <span class="flex size-2 shrink-0 rounded-full" :class="w.available ? 'bg-emerald-500' : 'bg-slate-300'" :title="w.available ? 'Available' : 'Busy'" />
                </div>
                <p class="text-xs text-graphite">{{ w.degree }}</p>
                <div class="mt-1 flex items-center gap-1">
                  <Star class="size-3 fill-amber-400 text-amber-400" />
                  <span class="text-xs font-semibold text-ink">{{ w.rating.toFixed(1) }}</span>
                  <span class="text-xs text-graphite">· {{ w.orders.toLocaleString() }} orders</span>
                </div>
              </div>
            </div>
            <div class="mt-3 flex flex-wrap gap-1.5">
              <span v-for="sub in w.subjects" :key="sub" class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-graphite">{{ sub }}</span>
            </div>
            <div class="mt-3 flex items-center justify-between">
              <span class="rounded-full px-2.5 py-0.5 text-[11px] font-semibold" :class="tierColor[w.tier as keyof typeof tierColor]">{{ w.tier }}</span>
              <a :href="app.order" class="text-xs font-semibold text-gc-600 hover:text-gc-700 transition-colors flex items-center gap-1">
                Hire <ArrowRight class="size-3" />
              </a>
            </div>
          </div>
        </div>

        <p class="mt-8 text-center text-sm text-graphite">
          Showing {{ filtered.length }} of 600+ writers. Your writer is matched to your subject automatically.
        </p>
      </div>
    </section>

    <!-- Verification section -->
    <section class="bg-mist py-14">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center space-y-8">
        <div>
          <h2 class="text-2xl font-bold text-ink mb-3">How we verify our writers</h2>
          <p class="text-graphite max-w-xl mx-auto">Every writer goes through a multi-stage process before handling their first order.</p>
        </div>
        <div class="grid gap-5 sm:grid-cols-3">
          <div v-for="step in [
            { n: '01', title: 'Application review',  desc: 'CV, degree certificates, and writing samples reviewed by our editorial team.' },
            { n: '02', title: 'Skills assessment',   desc: 'Grammar test, subject knowledge test, and a graded writing sample.' },
            { n: '03', title: 'Trial orders',        desc: 'New writers complete supervised trial orders before joining the full platform.' },
          ]" :key="step.n" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card text-left">
            <span class="text-3xl font-extrabold text-slate-100 select-none">{{ step.n }}</span>
            <h3 class="mt-1 text-sm font-semibold text-ink">{{ step.title }}</h3>
            <p class="mt-1 text-sm text-graphite leading-relaxed">{{ step.desc }}</p>
          </div>
        </div>
        <NuxtLink to="/apply" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
          Want to join our team? Apply here <ArrowRight class="size-4" />
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
