<script setup lang="ts">
import { ArrowRight, Calendar, ChevronLeft, ChevronRight, Clock } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Academic Writing Blog — Tips, Guides & Resources | GradeCrest',
  description: 'Academic writing guides, essay tips, dissertation advice, and study resources from GradeCrest\'s expert team.',
  ogTitle: 'GradeCrest Blog — Academic Writing Resources',
})
useSeoBase('https://gradecrest.com/blog')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Blog', url: 'https://gradecrest.com/blog' },
])

interface BlogPost {
  id: number
  meta: { slug: string; first_published_at: string; html_url: string }
  title: string
  excerpt: string
  reading_time_minutes: number
  category_name: string
  thumbnail: { url: string } | null
  author_name: string
}

const config = useRuntimeConfig()
// All Wagtail calls go through /wagtail/... — a Nitro server route that
// uses Node.js http.request() to inject Host: gradecrest.com (the Fetch
// API treats Host as a forbidden header and silently drops it).
const apiBase = config.public.apiBase || ''
const wagtailBase = `${apiBase}/wagtail`
const PAGE_SIZE = 12

const page     = ref(1)
const total    = ref(0)
const posts    = ref<BlogPost[]>([])
const pending  = ref(false)
const error    = ref(false)
const activeCategory = ref('All')

async function loadPage(p: number, cat?: string) {
  pending.value = true
  error.value   = false
  try {
    const params: Record<string, unknown> = {
      type:   'cms_blog.BlogPostPage',
      fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail,author_name',
      order:  '-first_published_at',
      limit:  PAGE_SIZE,
      offset: (p - 1) * PAGE_SIZE,
    }
    if (cat && cat !== 'All') params.category_name = cat
    const res = await $fetch<{ meta: { total_count: number }; items: BlogPost[] }>(
      `${wagtailBase}/api/v2/pages/`,
      { params },
    )
    total.value = res?.meta?.total_count ?? 0
    posts.value = res.items ?? []
    page.value  = p
  } catch {
    error.value = true
  } finally {
    pending.value = false
  }
}

// Also fetch categories for the filter bar
const { data: allForCats } = await useAsyncData('gc-blog-cats', async () => {
  try {
    const res = await $fetch<{ items: BlogPost[] }>(
      `${wagtailBase}/api/v2/pages/`,
      { params: { type: 'cms_blog.BlogPostPage', fields: 'category_name', limit: 500 } },
    )
    return res.items ?? []
  } catch { return [] }
})

await loadPage(1)

const totalPages = computed(() => Math.ceil(total.value / PAGE_SIZE))

const categories = computed(() => {
  const cats = new Set((allForCats.value ?? []).map((p: BlogPost) => p.category_name).filter(Boolean))
  return ['All', ...cats]
})

async function selectCategory(cat: string) {
  activeCategory.value = cat
  await loadPage(1, cat)
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
}

// Smart pagination: always show first, last, current±2, ellipsis between gaps
const pageNumbers = computed(() => {
  const total = totalPages.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const cur = page.value
  const pages: (number | '…')[] = []
  const add = (n: number | '…') => {
    if (pages[pages.length - 1] !== n) pages.push(n)
  }
  add(1)
  if (cur > 4) add('…')
  for (let p = Math.max(2, cur - 2); p <= Math.min(total - 1, cur + 2); p++) add(p)
  if (cur < total - 3) add('…')
  add(total)
  return pages
})
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-forest-950 py-16 text-center relative overflow-hidden">
      <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
      <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
        <p class="text-xs font-semibold uppercase tracking-widest text-gc-400 mb-3">Resources</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Academic Writing Blog</h1>
        <p class="mt-4 text-lg text-slate-300 max-w-xl mx-auto">
          Essays, dissertations, research papers — tips and guides from our expert team.
        </p>
      </div>
    </section>

    <!-- Content -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

        <!-- Error -->
        <div v-if="error" class="py-20 text-center text-sm text-graphite">
          Could not load articles. Please try again later.
        </div>

        <!-- Loading skeleton -->
        <div v-else-if="pending && !posts.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="i in 12" :key="i" class="rounded-2xl border border-slate-200 overflow-hidden animate-pulse">
            <div class="h-44 bg-slate-100" />
            <div class="p-5 space-y-3">
              <div class="h-3 w-1/3 rounded bg-slate-100" />
              <div class="h-4 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
              <div class="h-3 w-2/3 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <template v-else>
          <!-- Category filter + result count -->
          <div class="mb-8 flex flex-wrap items-center justify-between gap-4">
            <div class="flex flex-wrap gap-2">
              <button
                v-for="cat in categories" :key="cat"
                class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
                :class="activeCategory === cat
                  ? 'bg-gc-600 border-gc-600 text-white'
                  : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
                @click="selectCategory(cat)"
              >{{ cat }}</button>
            </div>
            <p class="shrink-0 text-sm text-slate-400">
              <span class="font-semibold text-ink">{{ total }}</span> article{{ total !== 1 ? 's' : '' }}
            </p>
          </div>

          <!-- Empty state -->
          <div v-if="!posts.length && !pending" class="py-20 text-center space-y-4">
            <p class="text-sm text-graphite">No articles published yet — check back soon.</p>
            <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-6 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
              Place an order <ArrowRight class="size-4" />
            </a>
          </div>

          <template v-else>
            <!-- Featured post (page 1, All category, not loading) -->
            <NuxtLink
              v-if="activeCategory === 'All' && page === 1 && posts.length && !pending"
              :to="`/blog/${posts[0]?.meta?.slug}`"
              class="group mb-10 flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card transition-all hover:-translate-y-0.5 hover:shadow-lift sm:flex-row"
            >
              <div class="h-52 shrink-0 overflow-hidden bg-slate-100 sm:h-auto sm:w-2/5">
                <img v-if="posts[0].thumbnail?.url" :src="posts[0].thumbnail.url" :alt="posts[0].title"
                  class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <div v-else class="flex h-full items-center justify-center">
                  <span class="select-none text-5xl font-extrabold text-slate-200">G</span>
                </div>
              </div>
              <div class="flex flex-1 flex-col justify-center space-y-3 p-6 sm:p-8">
                <div class="flex items-center gap-3 text-xs text-graphite">
                  <span v-if="posts[0].category_name" class="rounded-full bg-gc-50 px-2.5 py-0.5 font-semibold text-gc-700">{{ posts[0].category_name }}</span>
                  <span class="flex items-center gap-1"><Clock class="size-3" />{{ posts[0].reading_time_minutes || 1 }} min read</span>
                </div>
                <h2 class="text-xl font-bold leading-snug text-ink transition-colors group-hover:text-gc-600">{{ posts[0].title }}</h2>
                <p v-if="posts[0].excerpt" class="line-clamp-3 text-sm leading-relaxed text-graphite">{{ posts[0].excerpt }}</p>
                <div class="flex items-center gap-4 pt-1">
                  <div class="flex items-center gap-1.5 text-xs text-graphite">
                    <Calendar class="size-3" /> {{ formatDate(posts[0].meta?.first_published_at) }}
                  </div>
                  <span class="flex items-center gap-1 text-xs font-semibold text-gc-600 group-hover:underline">
                    Read article <ArrowRight class="size-3" />
                  </span>
                </div>
              </div>
            </NuxtLink>

            <!-- Post grid -->
            <div
              class="grid gap-6 transition-opacity duration-200 sm:grid-cols-2 lg:grid-cols-3"
              :class="pending ? 'opacity-50 pointer-events-none' : ''"
            >
              <NuxtLink
                v-for="post in (activeCategory === 'All' && page === 1 ? posts.slice(1) : posts)"
                :key="post.id"
                :to="`/blog/${post.meta?.slug}`"
                class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card transition-all hover:-translate-y-0.5 hover:shadow-lift"
              >
                <div class="h-44 overflow-hidden bg-slate-100">
                  <img v-if="post.thumbnail?.url" :src="post.thumbnail.url" :alt="post.title"
                    class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                  <div v-else class="flex h-full items-center justify-center">
                    <span class="select-none text-2xl font-extrabold text-slate-200">G</span>
                  </div>
                </div>
                <div class="flex flex-1 flex-col space-y-2.5 p-5">
                  <div class="flex items-center gap-2.5 text-xs text-graphite">
                    <span v-if="post.category_name" class="rounded-full bg-gc-50 px-2.5 py-0.5 font-semibold text-gc-700">{{ post.category_name }}</span>
                    <span v-if="post.reading_time_minutes" class="flex items-center gap-1"><Clock class="size-3" />{{ post.reading_time_minutes }} min</span>
                  </div>
                  <h2 class="line-clamp-2 flex-1 text-sm font-bold leading-snug text-ink transition-colors group-hover:text-gc-600">{{ post.title }}</h2>
                  <p v-if="post.excerpt" class="line-clamp-2 text-xs leading-relaxed text-graphite">{{ post.excerpt }}</p>
                  <div class="flex items-center justify-between border-t border-slate-100 pt-1.5">
                    <div class="flex items-center gap-1 text-xs text-graphite">
                      <Calendar class="size-3" />{{ formatDate(post.meta?.first_published_at) }}
                    </div>
                    <ArrowRight class="size-3.5 text-gc-600 opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </div>
              </NuxtLink>
            </div>

            <!-- Pagination -->
            <nav
              v-if="totalPages > 1"
              class="mt-12 flex items-center justify-center gap-1.5"
              aria-label="Blog pagination"
            >
              <!-- Prev -->
              <button
                :disabled="page === 1"
                class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:border-gc-400 hover:text-gc-600 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Previous page"
                @click="loadPage(page - 1, activeCategory !== 'All' ? activeCategory : undefined)"
              >
                <ChevronLeft class="size-4" />
              </button>

              <!-- Page numbers with smart ellipsis -->
              <template v-for="(p, i) in pageNumbers" :key="i">
                <span v-if="p === '…'" class="flex h-9 w-9 items-center justify-center text-sm text-slate-400" aria-hidden="true">…</span>
                <button
                  v-else
                  class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
                  :class="p === page
                    ? 'bg-gc-600 border-gc-600 text-white'
                    : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
                  :aria-label="`Page ${p}`"
                  :aria-current="p === page ? 'page' : undefined"
                  @click="loadPage(Number(p), activeCategory !== 'All' ? activeCategory : undefined)"
                >{{ p }}</button>
              </template>

              <!-- Next -->
              <button
                :disabled="page === totalPages"
                class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:border-gc-400 hover:text-gc-600 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Next page"
                @click="loadPage(page + 1, activeCategory !== 'All' ? activeCategory : undefined)"
              >
                <ChevronRight class="size-4" />
              </button>
            </nav>

            <!-- Page indicator -->
            <p v-if="totalPages > 1" class="mt-3 text-center text-xs text-slate-400">
              Page {{ page }} of {{ totalPages }} · {{ total }} articles
            </p>
          </template>
        </template>

      </div>
    </section>

    <!-- CTA -->
    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Ready to get expert help?</h2>
        <p class="text-sm text-graphite">Human-written papers, grade guaranteed, from $13/page.</p>
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
