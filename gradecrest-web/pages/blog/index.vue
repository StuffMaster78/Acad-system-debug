<script setup lang="ts">
import { ArrowRight, Calendar, Clock, Search, ChevronLeft, ChevronRight } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Academic Writing Blog — Tips, Guides & Resources | GradeCrest',
  description: 'Academic writing guides, essay tips, dissertation advice, and study resources from GradeCrest\'s expert team.',
  ogTitle: 'GradeCrest Blog — Academic Writing Resources',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useSeoBase('https://gradecrest.com/blog')
useBreadcrumbs([
  { name: 'Home', url: 'https://gradecrest.com/' },
  { name: 'Blog', url: 'https://gradecrest.com/blog' },
])

interface BlogPost {
  id: number
  meta: { slug: string; first_published_at: string }
  title: string
  excerpt: string
  reading_time_minutes: number
  category_name: string
  thumbnail: { url: string } | null
  author_name: string
}

const config      = useRuntimeConfig()
const apiBase     = config.public.apiBase || ''
const wagtailBase = `${apiBase}/wagtail`
const PAGE_SIZE   = 12

const page    = ref(1)
const total   = ref(0)
const posts   = ref<BlogPost[]>([])
const pending = ref(false)
const error   = ref(false)
const activeCategory = ref('All')
const searchQuery    = ref('')

async function loadPage(p: number, cat?: string) {
  pending.value = true; error.value = false
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
      `${wagtailBase}/api/v2/pages/`, { params },
    )
    total.value = res?.meta?.total_count ?? 0
    posts.value = res.items ?? []
    page.value  = p
  } catch { error.value = true }
  finally { pending.value = false }
}

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

const pageNumbers = computed(() => {
  const t = totalPages.value
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1)
  const cur = page.value
  const pages: (number | '…')[] = []
  const add = (n: number | '…') => { if (pages[pages.length - 1] !== n) pages.push(n) }
  add(1)
  if (cur > 4) add('…')
  for (let p = Math.max(2, cur - 2); p <= Math.min(t - 1, cur + 2); p++) add(p)
  if (cur < t - 3) add('…')
  add(t)
  return pages
})

// Show hero card + two large + rest in grid
const heroPost    = computed(() => (activeCategory.value === 'All' && page.value === 1) ? posts.value[0] ?? null : null)
const largeCards  = computed(() => (activeCategory.value === 'All' && page.value === 1) ? posts.value.slice(1, 3) : [])
const gridPosts   = computed(() => {
  const skip = heroPost.value ? (largeCards.value.length > 0 ? 3 : 1) : 0
  return posts.value.slice(skip)
})
</script>

<template>
  <div class="pt-16 bg-white">

    <!-- Magazine header bar -->
    <div class="border-b border-slate-200 bg-white sticky top-16 z-30">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex items-center gap-0 overflow-x-auto scrollbar-hide py-0">
          <!-- Category tabs -->
          <button
            v-for="cat in categories" :key="cat"
            class="shrink-0 border-b-2 px-4 py-3.5 text-sm font-semibold transition-colors whitespace-nowrap"
            :class="activeCategory === cat
              ? 'border-gc-600 text-gc-700'
              : 'border-transparent text-graphite hover:text-ink hover:border-slate-300'"
            @click="selectCategory(cat)"
          >{{ cat }}</button>

          <!-- Article count -->
          <span class="ml-auto shrink-0 pl-6 text-xs text-slate-400 py-3.5 whitespace-nowrap">
            {{ total }} articles
          </span>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error" class="py-20 text-center text-sm text-graphite mx-auto max-w-7xl px-4">
      Could not load articles. Please try again.
    </div>

    <!-- Loading skeleton -->
    <div v-else-if="pending && !posts.length" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div class="h-[420px] animate-pulse rounded-2xl bg-slate-100" />
      <div class="grid grid-cols-2 gap-6">
        <div class="h-72 animate-pulse rounded-2xl bg-slate-100" />
        <div class="h-72 animate-pulse rounded-2xl bg-slate-100" />
      </div>
    </div>

    <template v-else>

      <!-- Empty state -->
      <div v-if="!posts.length && !pending" class="py-20 text-center space-y-4 mx-auto max-w-xl px-4">
        <p class="text-sm text-graphite">No articles published yet — check back soon.</p>
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-6 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place an order <ArrowRight class="size-4" />
        </a>
      </div>

      <div v-else class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 space-y-6" :class="pending ? 'opacity-60 pointer-events-none' : ''">

        <!-- ── Hero card: full-width image with title overlay ── -->
        <NuxtLink
          v-if="heroPost"
          :to="`/${heroPost.meta?.slug}`"
          class="group relative block overflow-hidden rounded-2xl"
          style="min-height:420px"
        >
          <!-- Background image -->
          <div class="absolute inset-0">
            <img
              v-if="heroPost.thumbnail?.url"
              :src="heroPost.thumbnail.url"
              :alt="heroPost.title"
              class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
            />
            <div v-else class="h-full w-full bg-forest-900 flex items-center justify-center">
              <span class="text-9xl font-extrabold text-forest-700 select-none">G</span>
            </div>
          </div>
          <!-- Dark gradient overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-black/10" />
          <!-- Content -->
          <div class="relative flex h-full flex-col justify-end p-8 sm:p-10" style="min-height:420px">
            <div class="flex items-center gap-3 mb-4">
              <span v-if="heroPost.category_name"
                class="rounded-full bg-gc-600 px-3 py-1 text-xs font-bold text-white uppercase tracking-wide">
                {{ heroPost.category_name }}
              </span>
              <span class="flex items-center gap-1 text-xs text-white/70">
                <Clock class="size-3" />{{ heroPost.reading_time_minutes || 1 }} min read
              </span>
            </div>
            <h2 class="text-3xl font-bold leading-tight text-white sm:text-4xl max-w-3xl group-hover:text-gc-200 transition-colors">
              {{ heroPost.title }}
            </h2>
            <p v-if="heroPost.excerpt" class="mt-3 line-clamp-2 text-base text-white/80 max-w-2xl">{{ heroPost.excerpt }}</p>
            <div class="mt-5 flex items-center gap-4">
              <div class="flex items-center gap-2">
                <div class="size-7 rounded-full bg-gc-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
                  {{ (heroPost.author_name || 'G').charAt(0) }}
                </div>
                <span class="text-sm text-white/80">{{ heroPost.author_name }}</span>
              </div>
              <span class="flex items-center gap-1 text-xs text-white/60">
                <Calendar class="size-3" />{{ formatDate(heroPost.meta?.first_published_at) }}
              </span>
              <span class="ml-auto flex items-center gap-1.5 rounded-full bg-white/20 px-4 py-1.5 text-sm font-semibold text-white backdrop-blur-sm group-hover:bg-gc-600 transition-colors">
                Read article <ArrowRight class="size-3.5" />
              </span>
            </div>
          </div>
        </NuxtLink>

        <!-- ── Two large cards side by side ── -->
        <div v-if="largeCards.length" class="grid gap-6 sm:grid-cols-2">
          <NuxtLink
            v-for="post in largeCards" :key="post.id"
            :to="`/${post.meta?.slug}`"
            class="group relative overflow-hidden rounded-2xl"
            style="min-height:280px"
          >
            <div class="absolute inset-0">
              <NuxtImg v-if="post.thumbnail?.url" :src="post.thumbnail.url" :alt="post.title"
                width="800" height="450" fetchpriority="high" loading="eager"
                class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
              <div v-else class="h-full w-full bg-forest-900 flex items-center justify-center">
                <span class="text-6xl font-extrabold text-forest-700 select-none">G</span>
              </div>
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent" />
            <div class="relative flex h-full flex-col justify-end p-6" style="min-height:280px">
              <span v-if="post.category_name"
                class="mb-2 inline-block self-start rounded-full bg-white/20 px-2.5 py-0.5 text-[10px] font-bold text-white/90 uppercase tracking-wide backdrop-blur-sm">
                {{ post.category_name }}
              </span>
              <h2 class="text-lg font-bold leading-snug text-white group-hover:text-gc-200 transition-colors line-clamp-3">
                {{ post.title }}
              </h2>
              <div class="mt-3 flex items-center gap-3 text-xs text-white/60">
                <span class="flex items-center gap-1"><Clock class="size-3" />{{ post.reading_time_minutes || 1 }} min</span>
                <span class="flex items-center gap-1"><Calendar class="size-3" />{{ formatDate(post.meta?.first_published_at) }}</span>
              </div>
            </div>
          </NuxtLink>
        </div>

        <!-- ── Standard grid for remaining posts ── -->
        <div v-if="gridPosts.length" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="post in gridPosts" :key="post.id"
            :to="`/${post.meta?.slug}`"
            class="group flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <!-- Image with fixed height -->
            <div class="relative h-48 overflow-hidden bg-slate-100 shrink-0">
              <NuxtImg v-if="post.thumbnail?.url" :src="post.thumbnail.url" :alt="post.title"
                width="400" height="192" loading="lazy"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div v-else class="flex h-full items-center justify-center">
                <span class="select-none text-4xl font-extrabold text-slate-200">G</span>
              </div>
              <!-- Category on image -->
              <span v-if="post.category_name"
                class="absolute left-3 top-3 rounded-full bg-gc-600 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase tracking-wide">
                {{ post.category_name }}
              </span>
            </div>
            <!-- Content -->
            <div class="flex flex-1 flex-col p-4 space-y-2">
              <h2 class="line-clamp-2 font-bold leading-snug text-ink transition-colors group-hover:text-gc-600 text-sm">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="line-clamp-2 text-xs leading-relaxed text-graphite flex-1">{{ post.excerpt }}</p>
              <div class="flex items-center justify-between border-t border-slate-100 pt-2 text-xs text-graphite">
                <div class="flex items-center gap-2">
                  <div class="size-5 rounded-full bg-gc-100 flex items-center justify-center text-[9px] font-bold text-gc-700 shrink-0">
                    {{ (post.author_name || 'G').charAt(0) }}
                  </div>
                  <span>{{ post.author_name || 'GradeCrest' }}</span>
                </div>
                <div class="flex items-center gap-1 text-slate-400">
                  <Clock class="size-3" />{{ post.reading_time_minutes || 1 }} min
                </div>
              </div>
            </div>
          </NuxtLink>
        </div>

        <!-- Pagination -->
        <nav v-if="totalPages > 1" class="flex items-center justify-center gap-1.5 pt-4">
          <button :disabled="page === 1"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:border-gc-400 hover:text-gc-600 disabled:cursor-not-allowed disabled:opacity-40"
            @click="loadPage(page - 1, activeCategory !== 'All' ? activeCategory : undefined)">
            <ChevronLeft class="size-4" />
          </button>
          <template v-for="(p, i) in pageNumbers" :key="i">
            <span v-if="p === '…'" class="flex h-9 w-9 items-center justify-center text-sm text-slate-400">…</span>
            <button v-else
              class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
              :class="p === page ? 'bg-gc-600 border-gc-600 text-white' : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
              @click="loadPage(Number(p), activeCategory !== 'All' ? activeCategory : undefined)">
              {{ p }}
            </button>
          </template>
          <button :disabled="page === totalPages"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-graphite transition-colors hover:border-gc-400 hover:text-gc-600 disabled:cursor-not-allowed disabled:opacity-40"
            @click="loadPage(page + 1, activeCategory !== 'All' ? activeCategory : undefined)">
            <ChevronRight class="size-4" />
          </button>
        </nav>
        <p v-if="totalPages > 1" class="text-center text-xs text-slate-400">Page {{ page }} of {{ totalPages }}</p>

      </div>
    </template>

    <!-- Bottom CTA -->
    <div class="border-t border-slate-100 bg-forest-950 py-14 text-center mt-8">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <p class="text-xs font-bold uppercase tracking-widest text-gc-400">Ready to get started?</p>
        <h2 class="text-2xl font-bold text-white">Get expert academic help today</h2>
        <p class="text-sm text-slate-300">Human-written papers — grade guaranteed, from $13/page.</p>
        <a href="/order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </div>

  </div>
</template>
