<script setup lang="ts">
import { ArrowRight, BookOpen, Search, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Our Research Specialists — PhD & Master\'s Writers | ResearchPaperMate',
  description: 'Meet ResearchPaperMate\'s verified researchers. Every writer holds a postgraduate degree in their subject area and passed our four-stage vetting process.',
  ogTitle: 'ResearchPaperMate Writers — PhD & Masters Researchers',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/writers' }] })

const FIELDS = ['All', 'Business', 'Sciences', 'Law & Politics', 'Social Sciences', 'Humanities', 'STEM']

const active = ref('All')
const search = ref('')

const writers = [
  { name: 'Dr. Marcus L.',   initials: 'ML', degree: 'PhD · Business Strategy',    field: 'Business',        orders: 1560, rating: 4.9, available: true,  subjects: ['Strategy', 'Finance', 'Economics']         },
  { name: 'Dr. Yuki T.',     initials: 'YT', degree: 'PhD · Economics',            field: 'Business',        orders: 1230, rating: 5.0, available: false, subjects: ['Macroeconomics', 'Policy', 'Econometrics'] },
  { name: 'Dr. Isabelle P.', initials: 'IP', degree: "Master's · EU Policy",       field: 'Business',        orders:  610, rating: 5.0, available: true,  subjects: ['EU Policy', 'International Business', 'Regulation'] },
  { name: 'Dr. Elin R.',     initials: 'ER', degree: 'PhD · Molecular Biology',    field: 'Sciences',        orders:  870, rating: 5.0, available: true,  subjects: ['Molecular Biology', 'Biochemistry', 'CRISPR'] },
  { name: 'Dr. Chioma A.',   initials: 'CA', degree: 'MPH · Public Health',        field: 'Sciences',        orders:  740, rating: 5.0, available: true,  subjects: ['Public Health', 'Epidemiology', 'Health Policy'] },
  { name: 'Dr. Priya T.',    initials: 'PT', degree: "Master's · Nursing",         field: 'Sciences',        orders:  540, rating: 5.0, available: true,  subjects: ['Nursing Research', 'EBP', 'Healthcare']   },
  { name: 'Dr. James C.',    initials: 'JC', degree: 'PhD · International Relations', field: 'Law & Politics', orders: 1120, rating: 5.0, available: true, subjects: ['Security Studies', 'IR Theory', 'Geopolitics'] },
  { name: 'Dr. Arjun S.',    initials: 'AS', degree: "Master's · Environmental Law", field: 'Law & Politics', orders:  680, rating: 5.0, available: true,  subjects: ['International Law', 'Environmental Law', 'Policy'] },
  { name: 'Dr. Kwame A.',    initials: 'KA', degree: 'PhD · Development Economics', field: 'Social Sciences', orders:  590, rating: 5.0, available: false, subjects: ['Development Studies', 'African Studies', 'Policy'] },
  { name: 'Dr. Lena V.',     initials: 'LV', degree: 'PhD · Political Economy',   field: 'Social Sciences', orders:  910, rating: 5.0, available: true,  subjects: ['Political Economy', 'Sociology', 'Inequality'] },
  { name: 'Dr. Daniel O.',   initials: 'DO', degree: "Master's · Sociology",       field: 'Social Sciences', orders:  430, rating: 5.0, available: true,  subjects: ['Quantitative Methods', 'SPSS', 'Social Research'] },
  { name: 'Prof. Emily T.',  initials: 'ET', degree: 'PhD · English Literature',   field: 'Humanities',      orders: 1840, rating: 5.0, available: true,  subjects: ['Literary Theory', 'Cultural Studies', 'Discourse'] },
  { name: 'Dr. Finn L.',     initials: 'FL', degree: "Master's · Philosophy",      field: 'Humanities',      orders:  380, rating: 5.0, available: true,  subjects: ['Ethics', 'Political Philosophy', 'Critical Theory'] },
  { name: 'Dr. Caleb R.',    initials: 'CR', degree: 'PhD · Statistics',           field: 'STEM',            orders: 1380, rating: 5.0, available: false, subjects: ['Statistics', 'Data Analysis', 'R / SPSS']  },
  { name: 'Dr. Nadia F.',    initials: 'NF', degree: 'PhD · Computer Science',     field: 'STEM',            orders:  640, rating: 4.9, available: true,  subjects: ['Machine Learning', 'Algorithms', 'Systems']  },
  { name: 'Dr. Owen B.',     initials: 'OB', degree: 'PhD · Engineering Ethics',   field: 'STEM',            orders:  290, rating: 5.0, available: true,  subjects: ['Engineering Ethics', 'Sustainability', 'Policy'] },
]

const FIELD_MAP: Record<string, string[]> = {
  'Business':        ['Strategy', 'Finance', 'Economics', 'Policy', 'Econometrics', 'Business', 'Regulation'],
  'Sciences':        ['Molecular', 'Biochemistry', 'CRISPR', 'Public Health', 'Epidemiology', 'Health', 'Nursing', 'EBP'],
  'Law & Politics':  ['Security', 'IR', 'Geopolitics', 'Law', 'Environmental', 'International'],
  'Social Sciences': ['Development', 'African', 'Political Economy', 'Sociology', 'Inequality', 'Quantitative', 'SPSS', 'Social Research'],
  'Humanities':      ['Literary', 'Cultural', 'Discourse', 'Ethics', 'Philosophy', 'Critical Theory'],
  'STEM':            ['Statistics', 'Data', 'R /', 'Machine Learning', 'Algorithms', 'Systems', 'Engineering', 'Sustainability'],
}

const filtered = computed(() => {
  let list = writers
  if (active.value !== 'All') {
    const terms = FIELD_MAP[active.value] ?? []
    list = list.filter(w =>
      w.field === active.value ||
      w.subjects.some(s => terms.some(t => s.toLowerCase().includes(t.toLowerCase())))
    )
  }
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(w => w.subjects.some(s => s.toLowerCase().includes(q)) || w.degree.toLowerCase().includes(q))
  }
  return list
})
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute right-0 top-0 h-96 w-96 rounded-full bg-brand-600 opacity-20 blur-[120px]" />

      <div class="relative mx-auto max-w-5xl px-4 sm:px-6">
        <div class="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">The research team</p>
            <h1 class="text-4xl font-extrabold text-white sm:text-5xl leading-tight">
              Verified<br />researchers.<br />Not AI.
            </h1>
            <p class="mt-5 text-lg text-brand-200 leading-relaxed">
              Every writer holds a verified postgraduate degree in their subject and passed our four-stage vetting process. We reject over 95% of applicants.
            </p>
            <a
              :href="app.order"
              class="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
            >
              Get matched to a researcher <ArrowRight class="h-4 w-4" />
            </a>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p class="text-3xl font-extrabold text-white">200+</p>
              <p class="mt-1 text-sm text-brand-300">Active researchers</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p class="text-3xl font-extrabold text-white">95%</p>
              <p class="mt-1 text-sm text-brand-300">Rejection rate</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p class="text-3xl font-extrabold text-white">100+</p>
              <p class="mt-1 text-sm text-brand-300">Subject areas</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
              <p class="text-3xl font-extrabold text-white">4.8/5</p>
              <p class="mt-1 text-sm text-brand-300">Average rating</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Filter bar ─────────────────────────────────────────────────────── -->
    <div class="sticky top-16 z-20 border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto flex max-w-7xl items-center gap-3 overflow-x-auto px-4 py-3 sm:px-6">
        <div class="relative shrink-0">
          <Search class="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Search subject…"
            class="h-8 rounded-lg border border-slate-200 pl-8 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-200"
          />
        </div>
        <div class="flex gap-1.5">
          <button
            v-for="f in FIELDS" :key="f"
            class="shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors"
            :class="active === f ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            @click="active = f"
          >{{ f }}</button>
        </div>
      </div>
    </div>

    <!-- ── Writers grid ───────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p class="mb-5 text-sm text-slate-500">Showing <strong class="text-slate-700">{{ filtered.length }}</strong> researchers</p>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="w in filtered"
            :key="w.name"
            class="group flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-brand-200 hover:shadow-md"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-sm font-extrabold text-white">
                {{ w.initials }}
              </div>
              <span
                class="flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold"
                :class="w.available ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'"
              >{{ w.available ? '✓' : '·' }}</span>
            </div>

            <div class="mt-3">
              <p class="font-bold text-slate-900">{{ w.name }}</p>
              <div class="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
                <BookOpen class="h-3.5 w-3.5 shrink-0 text-brand-500" />
                {{ w.degree }}
              </div>
            </div>

            <div class="mt-3 flex flex-wrap gap-1">
              <span
                v-for="s in w.subjects.slice(0, 3)"
                :key="s"
                class="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600 group-hover:bg-brand-50 group-hover:text-brand-600 transition-colors"
              >{{ s }}</span>
            </div>

            <div class="mt-auto border-t border-slate-100 pt-3 flex items-center justify-between text-xs">
              <div class="flex items-center gap-1">
                <Star class="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                <span class="font-bold text-slate-800">{{ w.rating.toFixed(1) }}</span>
              </div>
              <span class="text-slate-400">{{ w.orders.toLocaleString() }} orders</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-14 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-extrabold text-white">Matched to your subject. Automatically.</h2>
        <p class="mt-2 text-brand-200">No browsing required — we assign the right specialist for your field and level.</p>
        <a
          :href="app.order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Start my research paper <ArrowRight class="h-4 w-4" />
        </a>
      </div>
    </section>

  </div>
</template>
