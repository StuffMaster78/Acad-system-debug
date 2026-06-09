<script setup lang="ts">
const writers = [
  {
    initials: 'AM',
    name: 'Angela M.',
    credential: 'DNP, FNP-BC',
    specialty: 'Advanced Practice Nursing',
    tags: ['SOAP Notes', 'Capstone Projects', 'NP Coursework'],
    rating: 4.98,
    orders: 312,
    onTime: 100,
  },
  {
    initials: 'RO',
    name: 'Rachel O.',
    credential: 'MSN, RN-BC',
    specialty: 'Medical-Surgical Nursing',
    tags: ['Care Plans', 'Case Studies', 'Nursing Essays'],
    rating: 4.97,
    orders: 279,
    onTime: 99,
  },
  {
    initials: 'JN',
    name: 'James N.',
    credential: 'DNP, CRNA',
    specialty: 'Perioperative & Critical Care',
    tags: ['Research Papers', 'Dissertations', 'Pharmacology'],
    rating: 4.99,
    orders: 198,
    onTime: 100,
  },
  {
    initials: 'SW',
    name: 'Sophia W.',
    credential: 'MSN, CNM',
    specialty: 'Maternal & Child Health',
    tags: ['Concept Maps', 'OB Nursing', 'Care Plans'],
    rating: 4.97,
    orders: 241,
    onTime: 99,
  },
  {
    initials: 'DK',
    name: 'David K.',
    credential: 'BSN, RN',
    specialty: 'Psychiatric & Mental Health Nursing',
    tags: ['Mental Health Essays', 'Reflective Journals', 'Coursework'],
    rating: 4.96,
    orders: 187,
    onTime: 98,
  },
  {
    initials: 'TL',
    name: 'Tina L.',
    credential: 'PhD, MSN',
    specialty: 'Nursing Education & Research',
    tags: ['Dissertations', 'Literature Reviews', 'Capstone Projects'],
    rating: 5.0,
    orders: 156,
    onTime: 100,
  },
]
</script>

<template>
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Written by real nurses</h2>
        <p class="section-sub">
          Every writer is a credentialed nursing professional — BSN, MSN, or DNP — with hands-on clinical experience.
          No generic academic writers. Only nurses who've been there.
        </p>
      </div>

      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="w in writers"
          :key="w.name"
          class="card group flex flex-col transition-shadow hover:shadow-md hover:border-brand-200"
        >
          <div class="flex items-start gap-4">
            <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-lg font-bold text-brand-700 ring-2 ring-brand-50">
              {{ w.initials }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-slate-900">{{ w.name }}</p>
              <p class="text-xs font-bold text-brand-600">{{ w.credential }}</p>
              <p class="text-xs text-slate-500">{{ w.specialty }}</p>
            </div>
          </div>

          <div class="mt-3 flex items-center gap-4 text-xs text-slate-500">
            <div class="flex items-center gap-1">
              <svg class="h-3.5 w-3.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
              <span class="font-bold text-slate-800">{{ w.rating }}</span>
            </div>
            <span><strong class="text-slate-700">{{ w.orders }}</strong> orders</span>
            <span><strong class="text-slate-700">{{ w.onTime }}%</strong> on-time</span>
          </div>

          <div class="mt-3 flex flex-wrap gap-1.5">
            <span
              v-for="tag in w.tags"
              :key="tag"
              class="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700"
            >{{ tag }}</span>
          </div>

          <div class="mt-4 border-t border-slate-100 pt-4">
            <NuxtLink
              to="/order"
              class="block w-full rounded-lg border border-brand-200 py-2 text-center text-sm font-medium text-brand-700 transition-colors hover:border-brand-600 hover:bg-brand-600 hover:text-white"
            >
              Order with this expert
            </NuxtLink>
          </div>
        </div>
      </div>

      <div class="mt-10 text-center">
        <p class="text-sm text-slate-500">Showing 6 of 500+ verified nursing writers</p>
        <NuxtLink to="/order" class="btn-primary mt-4 inline-flex">
          Browse all writers &amp; place order
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
