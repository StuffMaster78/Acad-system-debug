<script setup lang="ts">
const writers = [
  {
    initials: 'GO',
    color: 'bg-purple-600',
    name: 'Grace O.',
    degree: 'PhD Psychology',
    tags: ['Psychology', 'Social Work', 'Education'],
    rating: 4.9,
    orders: 892,
    onTime: 99,
  },
  {
    initials: 'DK',
    color: 'bg-blue-600',
    name: 'Daniel K.',
    degree: 'MSc Statistics',
    tags: ['Statistics', 'Data Analysis', 'R / SPSS'],
    rating: 5.0,
    orders: 1204,
    onTime: 100,
  },
  {
    initials: 'AN',
    color: 'bg-rose-600',
    name: 'Amara N.',
    degree: 'MA English Literature',
    tags: ['Literature', 'Essays', 'Creative Writing'],
    rating: 4.9,
    orders: 673,
    onTime: 98,
  },
  {
    initials: 'VA',
    color: 'bg-teal-600',
    name: 'Victor A.',
    degree: 'PhD Chemistry',
    tags: ['Chemistry', 'Biology', 'Lab Reports'],
    rating: 5.0,
    orders: 445,
    onTime: 100,
  },
  {
    initials: 'SM',
    color: 'bg-amber-600',
    name: 'Sarah M.',
    degree: 'MBA, Finance',
    tags: ['Business', 'Finance', 'Marketing'],
    rating: 4.9,
    orders: 1567,
    onTime: 99,
  },
  {
    initials: 'JT',
    color: 'bg-slate-600',
    name: 'James T.',
    degree: 'LLM (Law)',
    tags: ['Law', 'Political Science', 'Policy'],
    rating: 4.8,
    orders: 789,
    onTime: 97,
  },
]

function stars(rating: number) {
  return Math.round(rating)
}
</script>

<template>
  <section class="bg-white">
    <div class="section">
      <div class="text-center">
        <h2 class="section-heading">Meet your expert writers</h2>
        <p class="section-sub">
          200+ verified writers — hired for subject-matter expertise, not just writing ability.
          Every writer holds a Master's or PhD degree in their field.
        </p>
      </div>

      <div class="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="w in writers"
          :key="w.name"
          class="card group flex flex-col transition-shadow hover:shadow-md"
        >
          <div class="flex items-start gap-4">
            <div
              :class="[w.color, 'flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-lg font-bold text-white shadow-sm']"
            >
              {{ w.initials }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-slate-900">{{ w.name }}</p>
              <p class="text-sm text-slate-500">{{ w.degree }}</p>
              <div class="mt-1 flex items-center gap-1.5">
                <div class="flex gap-0.5">
                  <svg
                    v-for="i in stars(w.rating)"
                    :key="i"
                    class="h-3 w-3 text-amber-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                  </svg>
                </div>
                <span class="text-sm font-semibold text-slate-800">{{ w.rating }}</span>
              </div>
            </div>
          </div>

          <div class="mt-3 flex items-center gap-4 text-xs text-slate-500">
            <span><strong class="text-slate-700">{{ w.orders.toLocaleString() }}</strong> orders</span>
            <span><strong class="text-slate-700">{{ w.onTime }}%</strong> on-time</span>
          </div>

          <div class="mt-3 flex flex-wrap gap-1.5">
            <span
              v-for="tag in w.tags"
              :key="tag"
              class="rounded-full bg-parchment-100 px-2.5 py-1 text-xs font-medium text-claret-700"
            >
              {{ tag }}
            </span>
          </div>

          <div class="mt-4 border-t border-slate-100 pt-4">
            <NuxtLink
              to="/order"
              class="block w-full rounded-lg border border-parchment-300 py-2 text-center text-sm font-medium text-claret-700 transition-colors hover:border-amber-600 hover:bg-amber-600 hover:text-white"
            >
              Order with this expert
            </NuxtLink>
          </div>
        </div>
      </div>

      <div class="mt-10 text-center">
        <p class="text-sm text-slate-500">Showing 6 of 200+ writers · All verified with degree credentials</p>
        <NuxtLink to="/order" class="btn-primary mt-4 inline-flex">
          Browse all writers &amp; place order
        </NuxtLink>
      </div>
    </div>
  </section>
</template>
