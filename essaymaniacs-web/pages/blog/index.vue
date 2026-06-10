<script setup lang="ts">
const { getAll } = useBlog()
const posts = getAll()

const categories = [...new Set(posts.map(p => p.category))]
const activeCategory = ref<string | null>(null)
const currentPage = ref(1)
const POSTS_PER_PAGE = 9

const filtered = computed(() =>
  activeCategory.value ? posts.filter(p => p.category === activeCategory.value) : posts
)

const featured = computed(() => filtered.value[0] ?? null)
const rest = computed(() => {
  const start = currentPage.value === 1
    ? 1 + (currentPage.value - 1) * POSTS_PER_PAGE
    : (currentPage.value - 1) * POSTS_PER_PAGE
  return filtered.value.slice(start, start + POSTS_PER_PAGE)
})

const totalPages = computed(() => {
  const remaining = filtered.value.length - 1
  return 1 + Math.ceil(Math.max(remaining, 0) / POSTS_PER_PAGE)
})

function setCategory(cat: string | null) {
  activeCategory.value = cat
  currentPage.value = 1
}

function goToPage(p: number) {
  currentPage.value = p
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

const fmtDate = (d: string) =>
  new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

useSeoMeta({
  title: 'Academic Writing Blog | EssayManiacs',
  description: 'Practical guides on essays, research papers, dissertations, and every academic writing challenge. Written by subject specialists.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/blog' }] })
</script>

<template>
  <div class="bg-white">

    <!-- ── Page header ─────────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 px-4 py-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-600">EssayManiacs</p>
            <h1 class="font-serif text-4xl font-bold text-slate-900 sm:text-5xl">Writing guides<br class="hidden sm:block" /> that actually help</h1>
            <p class="mt-3 max-w-xl text-lg text-slate-600">
              Practical, specific advice on essays, dissertations, research papers, and every assignment in between — by writers who do this every day.
            </p>
          </div>
          <div class="shrink-0">
            <NuxtLink to="/order" class="btn-primary">
              Get your essay written →
            </NuxtLink>
          </div>
        </div>

        <!-- Category pills -->
        <div class="mt-8 flex flex-wrap gap-2">
          <button
            class="rounded-full border px-4 py-1.5 text-sm font-medium transition-all"
            :class="activeCategory === null
              ? 'border-brand-600 bg-brand-600 text-white'
              : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'"
            @click="setCategory(null)"
          >
            All articles <span class="ml-1 text-xs opacity-70">{{ posts.length }}</span>
          </button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="rounded-full border px-4 py-1.5 text-sm font-medium transition-all"
            :class="activeCategory === cat
              ? 'border-brand-600 bg-brand-600 text-white'
              : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-700'"
            @click="setCategory(cat)"
          >
            {{ cat }} <span class="ml-1 text-xs opacity-70">{{ posts.filter(p => p.category === cat).length }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">

      <!-- ── Featured article ─────────────────────────────────────────── -->
      <NuxtLink
        v-if="featured && currentPage === 1"
        :href="`/blog/${featured.slug}`"
        class="group mb-14 flex flex-col gap-6 overflow-hidden rounded-3xl border-l-4 border-brand-600 bg-slate-50 p-8 transition-all hover:bg-brand-50 sm:flex-row sm:items-center lg:gap-12"
      >
        <!-- Left: content -->
        <div class="flex-1">
          <div class="mb-3 flex flex-wrap items-center gap-3">
            <span class="rounded-full bg-brand-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-brand-700">
              {{ featured.category }}
            </span>
            <span class="text-xs text-slate-400">{{ featured.readTime }}</span>
            <time class="text-xs text-slate-400">{{ fmtDate(featured.date) }}</time>
          </div>
          <h2 class="font-serif text-2xl font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 sm:text-3xl">
            {{ featured.title }}
          </h2>
          <p class="mt-3 text-base leading-relaxed text-slate-600 line-clamp-3">{{ featured.excerpt }}</p>
          <div class="mt-5 flex items-center gap-3">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white">
              {{ featured.author?.name?.[0] ?? '?' }}
            </div>
            <span class="text-sm font-medium text-slate-700">{{ featured.author?.name }}</span>
            <span class="ml-auto text-sm font-semibold text-brand-600 group-hover:underline">Read article →</span>
          </div>
        </div>

        <!-- Right: visual accent -->
        <div class="hidden shrink-0 items-center justify-center sm:flex">
          <div class="flex h-36 w-36 items-center justify-center rounded-2xl bg-brand-100">
            <Icon name="book-open" class="h-16 w-16 text-brand-400" />
          </div>
        </div>
      </NuxtLink>

      <!-- ── Article grid ─────────────────────────────────────────────── -->
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="post in rest"
          :key="post.slug"
          :href="`/blog/${post.slug}`"
          class="group flex flex-col overflow-hidden rounded-2xl border border-slate-100 bg-white transition-all hover:border-brand-200 hover:shadow-sm"
        >
          <!-- Category accent bar -->
          <div class="h-1 w-full bg-brand-200 transition-colors group-hover:bg-brand-600" />

          <div class="flex flex-1 flex-col p-6">
            <div class="mb-3 flex items-center gap-2">
              <span class="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                {{ post.category }}
              </span>
              <span class="text-xs text-slate-400">{{ post.readTime }}</span>
            </div>

            <h2 class="flex-1 font-serif text-lg font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">
              {{ post.title }}
            </h2>
            <p class="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-500">{{ post.excerpt }}</p>

            <div class="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
              <div class="flex items-center gap-2">
                <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-[10px] font-bold text-brand-700">
                  {{ post.author?.name?.[0] ?? '?' }}
                </div>
                <span class="text-xs text-slate-500">{{ post.author?.name?.split(' ')[0] }}</span>
              </div>
              <time class="text-xs text-slate-400">{{ fmtDate(post.date) }}</time>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- ── Inline CTA after 2nd row ─────────────────────────────────── -->
      <div v-if="rest.length >= 6" class="my-10 border-y border-slate-200 py-8">
        <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="mb-1 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">EssayManiacs</p>
            <p class="text-base font-bold leading-snug text-slate-900">Reading about essays instead of getting yours written?</p>
            <p class="mt-1 text-sm text-slate-500">Subject specialists available now · From $10/page · Grade or money back</p>
          </div>
          <NuxtLink to="/order" class="shrink-0 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-slate-700 whitespace-nowrap">
            Place my order
            <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
          </NuxtLink>
        </div>
      </div>

      <!-- ── Pagination ────────────────────────────────────────────────── -->
      <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
        <button
          class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:border-brand-300 hover:text-brand-600 disabled:opacity-30"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <Icon name="chevron-right" class="h-4 w-4 rotate-180" />
        </button>
        <template v-for="p in totalPages" :key="p">
          <button
            v-if="p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1"
            class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
            :class="p === currentPage ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-600'"
            @click="goToPage(p)"
          >{{ p }}</button>
          <span v-else-if="p === 2 && currentPage > 3 || p === totalPages - 1 && currentPage < totalPages - 2"
            class="text-slate-400 text-sm">…</span>
        </template>
        <button
          class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:border-brand-300 hover:text-brand-600 disabled:opacity-30"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <Icon name="chevron-right" class="h-4 w-4" />
        </button>
      </div>
    </div>

  </div>
</template>
