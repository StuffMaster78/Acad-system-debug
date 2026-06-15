<script setup lang="ts">
import { BookOpen, GraduationCap, Search, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Our Subject Specialists — 500+ Verified Essay Writers | EssayManiacs',
  description: 'Meet EssayManiacs subject-specialist writers. Every writer holds a postgraduate degree in their declared field and passed our 4-stage vetting process.',
  ogTitle: 'EssayManiacs Writers — Subject Specialists in 100+ Fields',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/writers' }] })

const SUBJECTS = ['All', 'Humanities', 'Social Sciences', 'STEM', 'Business', 'Law', 'Health']

const active = ref('All')
const search = ref('')

const writers = [
  { name: 'Dr. Amara L.',   initials: 'AL', degree: "PhD · English Literature",   orders: 2140, rating: 5.0, available: true,  subjects: ['Literature', 'History', 'Philosophy'],     tier: 'Lead',     tags: ['Humanities'] },
  { name: 'Prof. Kwame D.', initials: 'KD', degree: 'PhD · Philosophy',           orders: 1530, rating: 5.0, available: true,  subjects: ['Philosophy', 'Ethics', 'Political Theory'],tier: 'Lead',     tags: ['Humanities'] },
  { name: 'Dr. Sophie R.',  initials: 'SR', degree: "Master's · Media Studies",   orders:  870, rating: 5.0, available: true,  subjects: ['Media Studies', 'Film Theory', 'Cultural Studies'], tier: 'Senior', tags: ['Humanities'] },
  { name: 'Dr. Marcus T.',  initials: 'MT', degree: 'PhD · Sociology',            orders: 1860, rating: 4.9, available: true,  subjects: ['Sociology', 'Anthropology', 'Gender Studies'], tier: 'Lead',   tags: ['Social Sciences'] },
  { name: 'Dr. Nadia F.',   initials: 'NF', degree: 'PhD · Psychology',           orders: 2050, rating: 4.9, available: false, subjects: ['Psychology', 'Cognitive Science', 'Counselling'], tier: 'Lead', tags: ['Social Sciences'] },
  { name: 'Dr. Riya P.',    initials: 'RP', degree: "Master's · Political Science", orders: 990, rating: 5.0, available: true, subjects: ['Political Science', 'IR', 'Sociology'],     tier: 'Senior', tags: ['Social Sciences'] },
  { name: 'Dr. Owen B.',    initials: 'OB', degree: 'PhD · Environmental Science', orders: 730, rating: 5.0, available: true,  subjects: ['Environmental Science', 'Biology', 'Chemistry'], tier: 'Senior', tags: ['STEM'] },
  { name: 'Dr. Priya S.',   initials: 'PS', degree: 'PhD · Statistics',           orders: 1240, rating: 5.0, available: true,  subjects: ['Statistics', 'Data Analysis', 'Mathematics'], tier: 'Lead',   tags: ['STEM'] },
  { name: 'Dr. Lena V.',    initials: 'LV', degree: 'PhD · Chemistry',            orders:  860, rating: 5.0, available: true,  subjects: ['Chemistry', 'Biology', 'Biochemistry'],     tier: 'Senior', tags: ['STEM'] },
  { name: 'Dr. Hassan O.',  initials: 'HO', degree: 'PhD · Economics',            orders: 1680, rating: 4.9, available: true,  subjects: ['Economics', 'Finance', 'Business Strategy'], tier: 'Lead',   tags: ['Business'] },
  { name: 'Prof. Fatima R.',initials: 'FR', degree: 'PhD · Marketing',            orders: 1120, rating: 5.0, available: false, subjects: ['Marketing', 'Business', 'Consumer Behaviour'], tier: 'Lead',  tags: ['Business'] },
  { name: 'Dr. James C.',   initials: 'JC', degree: "Master's · Business Admin",  orders:  640, rating: 5.0, available: true,  subjects: ['MBA', 'Management', 'Entrepreneurship'],   tier: 'Senior', tags: ['Business'] },
  { name: 'Dr. Chloe N.',   initials: 'CN', degree: 'LLM · Law',                  orders:  920, rating: 5.0, available: true,  subjects: ['Law', 'Contract Law', 'Constitutional Law'], tier: 'Senior', tags: ['Law'] },
  { name: 'Dr. Arjun S.',   initials: 'AS', degree: 'PhD · Criminology',          orders:  580, rating: 4.9, available: true,  subjects: ['Criminal Justice', 'Law', 'Criminology'],   tier: 'Senior', tags: ['Law'] },
  { name: 'Dr. Dana H.',    initials: 'DH', degree: "Master's · Public Health",   orders:  480, rating: 5.0, available: true,  subjects: ['Public Health', 'Nursing', 'Healthcare'],   tier: 'Senior', tags: ['Health'] },
  { name: 'Dr. Elin R.',    initials: 'ER', degree: 'PhD · Nursing',              orders:  760, rating: 5.0, available: true,  subjects: ['Nursing', 'Healthcare', 'Pharmacology'],    tier: 'Lead',   tags: ['Health'] },
]

const FILTER_MAP: Record<string, string[]> = {
  'Humanities':      ['Literature', 'History', 'Philosophy', 'Media Studies', 'Film', 'Cultural'],
  'Social Sciences': ['Sociology', 'Anthropology', 'Gender', 'Psychology', 'Cognitive', 'Counselling', 'Political', 'IR'],
  'STEM':            ['Environmental', 'Biology', 'Chemistry', 'Statistics', 'Data', 'Mathematics', 'Biochemistry'],
  'Business':        ['Economics', 'Finance', 'Business', 'Marketing', 'MBA', 'Management', 'Entrepreneurship'],
  'Law':             ['Law', 'Contract', 'Constitutional', 'Criminal', 'Criminology'],
  'Health':          ['Public Health', 'Nursing', 'Healthcare', 'Pharmacology'],
}

const filtered = computed(() => {
  let list = writers
  if (active.value !== 'All') {
    const terms = FILTER_MAP[active.value] ?? []
    list = list.filter(w => w.subjects.some(s => terms.some(t => s.toLowerCase().includes(t.toLowerCase()))))
  }
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(w => w.subjects.some(s => s.toLowerCase().includes(q)) || w.degree.toLowerCase().includes(q))
  }
  return list
})

const tierStyle: Record<string, string> = {
  Lead:   'bg-brand-100 text-brand-700',
  Senior: 'bg-violet-100 text-violet-700',
}

const stats = [
  { value: '500+',  label: 'Active writers'     },
  { value: '100+',  label: 'Subject areas'      },
  { value: '2/100', label: 'Acceptance rate'    },
  { value: '4.8/5', label: 'Average rating'     },
]
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="pointer-events-none absolute -top-32 right-0 h-[500px] w-[500px] rounded-full bg-brand-500 opacity-20 blur-[120px]" />
      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">The writers</p>
        <h1 class="text-4xl font-extrabold text-white sm:text-5xl">
          Subject obsessives.<br class="hidden sm:block" /> Not generalists.
        </h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-brand-200">
          Every writer passed a 4-stage vetting process and holds a postgraduate degree in their declared subject. We turn away 98 out of 100 applicants.
        </p>
        <div class="mt-10 flex flex-wrap justify-center gap-4">
          <div v-for="s in stats" :key="s.label" class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <p class="text-2xl font-extrabold text-white">{{ s.value }}</p>
            <p class="mt-0.5 text-xs text-brand-300">{{ s.label }}</p>
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
            v-for="s in SUBJECTS" :key="s"
            class="shrink-0 rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors"
            :class="active === s ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            @click="active = s"
          >{{ s }}</button>
        </div>
      </div>
    </div>

    <!-- ── Writers grid ───────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p class="mb-5 text-sm text-slate-500">Showing <strong class="text-slate-700">{{ filtered.length }}</strong> writers</p>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="w in filtered"
            :key="w.name"
            class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
          >
            <!-- Avatar row -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-base font-extrabold text-brand-700">
                {{ w.initials }}
              </div>
              <div class="flex flex-col items-end gap-1.5">
                <span class="rounded-full px-2.5 py-0.5 text-[10px] font-bold" :class="tierStyle[w.tier] ?? 'bg-slate-100 text-slate-600'">{{ w.tier }}</span>
                <span class="flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold" :class="w.available ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'">
                  {{ w.available ? '✓' : '·' }}
                </span>
              </div>
            </div>

            <!-- Name + degree -->
            <div class="mt-3">
              <p class="font-bold text-slate-900">{{ w.name }}</p>
              <div class="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
                <GraduationCap class="h-3.5 w-3.5 shrink-0 text-brand-500" />
                {{ w.degree }}
              </div>
            </div>

            <!-- Subjects -->
            <div class="mt-3 flex flex-wrap gap-1">
              <span
                v-for="s in w.subjects.slice(0, 3)"
                :key="s"
                class="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] text-slate-600"
              >{{ s }}</span>
            </div>

            <!-- Stats -->
            <div class="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
              <div class="flex items-center gap-1 text-amber-500">
                <Star class="h-3.5 w-3.5 fill-amber-400" />
                <span class="font-bold text-slate-800">{{ w.rating.toFixed(1) }}</span>
              </div>
              <div class="flex items-center gap-1 text-slate-400">
                <BookOpen class="h-3.5 w-3.5" />
                <span>{{ w.orders.toLocaleString() }} orders</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-14 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-extrabold text-white">Get matched to your subject expert.</h2>
        <p class="mt-2 text-brand-200">We assign the right writer automatically — no browsing required.</p>
        <a
          :href="app.order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Start my essay
        </a>
      </div>
    </section>

  </div>
</template>
