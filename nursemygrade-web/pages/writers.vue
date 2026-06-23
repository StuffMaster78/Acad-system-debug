<script setup lang="ts">
import { Search, ShieldCheck, Star } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Our Nurse Writers — BSN, MSN & DNP Specialists | NurseMyGrade',
  description: 'Meet the credentialed nurse writers behind NurseMyGrade. Every writer holds an active nursing licence — BSN minimum, with MSN and DNP specialists for graduate work.',
  ogTitle: 'NurseMyGrade Writers — BSN, MSN & DNP Qualified Nurses',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://nursemygrade.com/writers' }] })

const LEVELS = ['All', 'BSN', 'MSN', 'DNP / PhD']
const SPECIALTIES = ['All', 'Med-Surgical', 'Mental Health', 'Pediatrics', 'Critical Care', 'Family NP', 'DNP / Research']

const activeLevel    = ref('All')
const activeSpec     = ref('All')
const search         = ref('')

const writers = [
  { name: 'Dr. Sarah K.',    initials: 'SK', credential: 'DNP, APRN',        orders: 1840, rating: 5.0, available: true,  specialties: ['DNP / Research', 'Med-Surgical'],            level: 'DNP / PhD' },
  { name: 'Marcus T., MSN',  initials: 'MT', credential: 'MSN, FNP-C',       orders:  960, rating: 5.0, available: true,  specialties: ['Family NP', 'Med-Surgical'],                  level: 'MSN' },
  { name: 'Rosa C., BSN',    initials: 'RC', credential: 'BSN, RN',           orders:  480, rating: 5.0, available: true,  specialties: ['Mental Health', 'Med-Surgical'],               level: 'BSN' },
  { name: 'Dr. Amina O.',    initials: 'AO', credential: 'DNP, FNP',          orders: 1120, rating: 5.0, available: false, specialties: ['DNP / Research', 'Family NP'],               level: 'DNP / PhD' },
  { name: 'Yvette N., MSN',  initials: 'YN', credential: 'MSN, PMHNP-BC',     orders:  740, rating: 5.0, available: true,  specialties: ['Mental Health', 'DNP / Research'],            level: 'MSN' },
  { name: 'David M., ADN',   initials: 'DM', credential: 'ADN, RN',           orders:  320, rating: 4.9, available: true,  specialties: ['Med-Surgical', 'Pediatrics'],                 level: 'BSN' },
  { name: 'Jenna H., BSN',   initials: 'JH', credential: 'BSN, RN',           orders:  410, rating: 5.0, available: true,  specialties: ['Pediatrics', 'Med-Surgical'],                 level: 'BSN' },
  { name: 'Dr. Fatou B.',    initials: 'FB', credential: 'PhD, RN',           orders:  680, rating: 5.0, available: true,  specialties: ['DNP / Research', 'Critical Care'],            level: 'DNP / PhD' },
  { name: 'Kenji B., MSN',   initials: 'KB', credential: 'MSN, RN-BC',        orders:  530, rating: 4.9, available: false, specialties: ['Med-Surgical', 'Critical Care'],              level: 'MSN' },
  { name: 'Carmen D., BSN',  initials: 'CD', credential: 'BSN, RN, CCRN',     orders:  610, rating: 5.0, available: true,  specialties: ['Critical Care', 'Med-Surgical'],              level: 'BSN' },
  { name: 'Tricia L., MSN',  initials: 'TL', credential: 'MSN, NE-BC',        orders:  390, rating: 5.0, available: true,  specialties: ['Family NP', 'DNP / Research'],               level: 'MSN' },
  { name: 'Dr. Luke V.',     initials: 'LV', credential: 'DNP, CRNA',         orders:  490, rating: 5.0, available: true,  specialties: ['DNP / Research', 'Critical Care'],            level: 'DNP / PhD' },
]

const filtered = computed(() => {
  let list = writers
  if (activeLevel.value !== 'All')
    list = list.filter(w => w.level === activeLevel.value || (activeLevel.value === 'BSN' && w.level === 'BSN'))
  if (activeSpec.value !== 'All')
    list = list.filter(w => w.specialties.includes(activeSpec.value))
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    list = list.filter(w => w.specialties.some(s => s.toLowerCase().includes(q)) || w.credential.toLowerCase().includes(q))
  }
  return list
})

const levelStyle: Record<string, string> = {
  'BSN':      'border-brand-200 bg-brand-50 text-brand-700',
  'MSN':      'border-teal-200  bg-teal-50  text-teal-700',
  'DNP / PhD':'border-violet-200 bg-violet-50 text-violet-700',
}
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-gradient-to-br from-brand-900 to-brand-700 py-20">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:48px_48px]" />
      <div class="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Meet the nurses</p>
        <h1 class="text-4xl font-extrabold text-white sm:text-5xl">
          Real nurses.<br class="hidden sm:block" /> Real credentials.
        </h1>
        <p class="mx-auto mt-4 max-w-xl text-lg text-brand-200">
          Every writer on NurseMyGrade holds an active nursing licence and passed a clinical knowledge assessment. BSN is the floor — MSN and DNP specialists handle graduate and doctoral work.
        </p>

        <div class="mt-10 flex flex-wrap justify-center gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <p class="text-2xl font-extrabold text-white">500+</p>
            <span class="mt-1 inline-block rounded-full border border-brand-200 bg-brand-100 px-2.5 py-0.5 text-xs font-bold text-brand-700">Total writers</span>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <p class="text-2xl font-extrabold text-white">4,800+</p>
            <span class="mt-1 inline-block rounded-full border border-teal-200 bg-teal-100 px-2.5 py-0.5 text-xs font-bold text-teal-700">BSN</span>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <p class="text-2xl font-extrabold text-white">MSN / NP</p>
            <span class="mt-1 inline-block rounded-full border border-violet-200 bg-violet-100 px-2.5 py-0.5 text-xs font-bold text-violet-700">Graduate level</span>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-center backdrop-blur-sm">
            <p class="text-2xl font-extrabold text-white">DNP / PhD</p>
            <span class="mt-1 inline-block rounded-full border border-amber-200 bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-700">Doctoral</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Filters ────────────────────────────────────────────────────────── -->
    <div class="sticky top-16 z-20 border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto max-w-7xl px-4 py-3 sm:px-6 space-y-2">
        <div class="flex items-center gap-3 overflow-x-auto">
          <span class="shrink-0 text-xs font-bold text-slate-400">LEVEL</span>
          <div class="flex gap-1.5">
            <button
              v-for="l in LEVELS" :key="l"
              class="shrink-0 rounded-full border px-3.5 py-1.5 text-xs font-semibold transition-colors"
              :class="activeLevel === l ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300'"
              @click="activeLevel = l"
            >{{ l }}</button>
          </div>
          <div class="mx-2 h-4 w-px shrink-0 bg-slate-200" />
          <div class="relative shrink-0">
            <Search class="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input v-model="search" type="text" placeholder="Specialty…" class="h-8 rounded-lg border border-slate-200 pl-8 pr-3 text-sm placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-200" />
          </div>
        </div>
        <div class="flex items-center gap-3 overflow-x-auto">
          <span class="shrink-0 text-xs font-bold text-slate-400">AREA</span>
          <div class="flex gap-1.5">
            <button
              v-for="s in SPECIALTIES" :key="s"
              class="shrink-0 rounded-full border px-3.5 py-1 text-xs font-medium transition-colors"
              :class="activeSpec === s ? 'border-teal-600 bg-teal-600 text-white' : 'border-slate-200 bg-white text-slate-600 hover:border-teal-300'"
              @click="activeSpec = s"
            >{{ s }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Writers grid ───────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p class="mb-5 text-sm text-slate-500">Showing <strong class="text-slate-700">{{ filtered.length }}</strong> nurse writers</p>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          <div
            v-for="w in filtered"
            :key="w.name"
            class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-sm font-extrabold text-brand-700">
                {{ w.initials }}
              </div>
              <div class="flex flex-col items-end gap-1.5">
                <span class="rounded-full border px-2.5 py-0.5 text-[10px] font-bold" :class="levelStyle[w.level]">{{ w.level }}</span>
                <span class="flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold" :class="w.available ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-400'">
                  {{ w.available ? '✓' : '·' }}
                </span>
              </div>
            </div>

            <div class="mt-3">
              <p class="font-bold text-slate-900">{{ w.name }}</p>
              <div class="mt-0.5 flex items-center gap-1.5 text-xs text-slate-500">
                <ShieldCheck class="h-3.5 w-3.5 shrink-0 text-brand-500" />
                {{ w.credential }}
              </div>
            </div>

            <div class="mt-3 flex flex-wrap gap-1">
              <span
                v-for="s in w.specialties"
                :key="s"
                class="rounded-full bg-brand-50 border border-brand-100 px-2 py-0.5 text-[11px] text-brand-600"
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
    <section class="bg-brand-700 py-14 text-center">
      <div class="mx-auto max-w-xl px-4">
        <h2 class="text-2xl font-extrabold text-white">Matched automatically. No browsing required.</h2>
        <p class="mt-2 text-brand-200">Tell us your assignment type and we assign the right nurse writer for it.</p>
        <NuxtLink
          to="/order"
          class="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 shadow-lg transition-colors hover:bg-brand-50"
        >
          Place my order — from $24/page
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
