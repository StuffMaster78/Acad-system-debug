<script setup lang="ts">
import { markRaw } from 'vue'
import { BookOpen, FileText, GraduationCap, ClipboardList, Hospital, Stethoscope, PenLine, Microscope, Pill } from '@lucide/vue'

const app = useAppUrl()

useSeoMeta({
  title: 'Nursing Blog — Care Plans, SOAP Notes & Study Guides | NurseMyGrade',
  description: 'Evidence-based guides on care plans, SOAP notes, nursing capstones, and clinical coursework — written by BSN, MSN, and DNP nurses.',
  ogTitle: 'NurseMyGrade Blog — Nursing Study Resources',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://nursemygrade.com/blog' }] })

interface Post {
  slug: string
  title: string
  excerpt: string
  category: string
  readingTime: number
  publishedAt: string
  thumbnail: string | null
  fromCms: boolean
}

interface CmsPost {
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

const cmsPosts   = ref<CmsPost[]>([])
const cmsTotal   = ref(0)
const cmsPage    = ref(1)
const cmsLoading = ref(false)
const cmsError   = ref(false)
const usingCms   = ref(false)

async function loadCmsPage(p: number) {
  if (!apiBase) return
  cmsLoading.value = true; cmsError.value = false
  try {
    const res = await $fetch<{ meta: { total_count: number }; items: CmsPost[] }>(
      `${wagtailBase}/api/v2/pages/`,
      { params: { type: 'cms_blog.BlogPostPage', fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail,author_name', order: '-first_published_at', limit: PAGE_SIZE, offset: (p - 1) * PAGE_SIZE } },
    )
    cmsTotal.value = res?.meta?.total_count ?? 0
    cmsPosts.value = res.items ?? []
    cmsPage.value  = p
    if (res.items?.length) usingCms.value = true
  } catch { cmsError.value = true }
  finally { cmsLoading.value = false }
}

await loadCmsPage(1)

const { getAll } = useBlog()
const staticPosts = usingCms.value ? [] : getAll()

function normCms(p: CmsPost): Post {
  return { slug: p.meta.slug, title: p.title, excerpt: p.excerpt, category: p.category_name || '', readingTime: p.reading_time_minutes || 1, publishedAt: p.meta.first_published_at, thumbnail: p.thumbnail?.url ?? null, fromCms: true }
}
function normStatic(p: ReturnType<typeof getAll>[0]): Post {
  return { slug: p.slug, title: p.title, excerpt: p.excerpt, category: p.category, readingTime: Number.parseInt(p.readTime, 10) || 1, publishedAt: p.date, thumbnail: null, fromCms: false }
}

const allPosts = computed<Post[]>(() =>
  usingCms.value ? cmsPosts.value.map(normCms) : staticPosts.map(normStatic)
)

const cmsTotalPages = computed(() => Math.ceil(cmsTotal.value / PAGE_SIZE))

const categories = computed(() => {
  const cats = new Set(allPosts.value.map(p => p.category).filter(Boolean))
  return ['All', ...cats]
})
const activeCategory = ref('All')
const currentPage    = ref(1)
const STATIC_PER_PAGE = 9

const filtered = computed(() =>
  activeCategory.value === 'All' ? allPosts.value : allPosts.value.filter(p => p.category === activeCategory.value)
)

const featured = computed(() => (currentPage.value === 1 && activeCategory.value === 'All') ? filtered.value[0] ?? null : null)
const rest = computed(() => {
  if (usingCms.value) return featured.value ? filtered.value.slice(1) : filtered.value
  const skip  = featured.value ? 1 : 0
  const start = skip + (currentPage.value - 1) * STATIC_PER_PAGE
  return filtered.value.slice(start, start + STATIC_PER_PAGE)
})
const staticTotalPages = computed(() => 1 + Math.ceil(Math.max(filtered.value.length - 1, 0) / STATIC_PER_PAGE))

function setCategory(cat: string) { activeCategory.value = cat; currentPage.value = 1; cmsPage.value = 1 }
function goPage(p: number) { if (usingCms.value) loadCmsPage(p); else { currentPage.value = p; if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' }) } }

const totalPages = computed(() => usingCms.value ? cmsTotalPages.value : staticTotalPages.value)
const activePage = computed(() => usingCms.value ? cmsPage.value : currentPage.value)
const displayTotal = computed(() =>
  usingCms.value && activeCategory.value === 'All' ? cmsTotal.value : filtered.value.length
)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
}

// Tile appearance per category — fallback covers CMS-generated categories
const CAT_TILE: Record<string, { icon: ReturnType<typeof markRaw>; bg: string; text: string; border: string }> = {
  'All':                  { icon: markRaw(BookOpen),     bg: 'bg-brand-50',   text: 'text-brand-700',  border: 'border-brand-200' },
  'Nursing Papers':       { icon: markRaw(FileText),     bg: 'bg-teal-50',    text: 'text-teal-700',   border: 'border-teal-200'  },
  'Capstone & Research':  { icon: markRaw(GraduationCap),bg: 'bg-indigo-50',  text: 'text-indigo-700', border: 'border-indigo-200'},
  'Citation & Format':    { icon: markRaw(ClipboardList),bg: 'bg-slate-50',   text: 'text-slate-700',  border: 'border-slate-200' },
  'Clinical Simulations': { icon: markRaw(Hospital),     bg: 'bg-emerald-50', text: 'text-emerald-700',border: 'border-emerald-200'},
  'Nursing School':       { icon: markRaw(Stethoscope),  bg: 'bg-rose-50',    text: 'text-rose-700',   border: 'border-rose-200'  },
  'Essays':               { icon: markRaw(PenLine),      bg: 'bg-amber-50',   text: 'text-amber-700',  border: 'border-amber-200' },
  'Research Papers':      { icon: markRaw(Microscope),   bg: 'bg-blue-50',    text: 'text-blue-700',   border: 'border-blue-200'  },
  'SOAP Notes':           { icon: markRaw(ClipboardList),bg: 'bg-cyan-50',    text: 'text-cyan-700',   border: 'border-cyan-200'  },
  'Care Plans':           { icon: markRaw(Pill),         bg: 'bg-violet-50',  text: 'text-violet-700', border: 'border-violet-200'},
}
function tile(cat: string) {
  return CAT_TILE[cat] ?? { icon: markRaw(BookOpen), bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' }
}

const CAT_BADGE: Record<string, string> = {
  'Nursing Papers':       'bg-brand-50  text-brand-700',
  'Capstone & Research':  'bg-slate-100 text-slate-700',
  'Citation & Format':    'bg-indigo-50 text-indigo-700',
  'Clinical Simulations': 'bg-emerald-50 text-emerald-700',
  'Nursing School':       'bg-rose-50   text-rose-700',
  'Essays':               'bg-brand-50  text-brand-700',
  'Research Papers':      'bg-blue-50   text-blue-700',
}
function catBadge(cat: string) { return CAT_BADGE[cat] ?? 'bg-slate-100 text-slate-600' }
</script>

<template>
  <div class="min-h-screen bg-slate-50">

    <!-- ── Header: clean clinical white ─────────────────────────────────────── -->
    <section class="bg-white border-b border-slate-100 pt-10 pb-6">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div class="mb-2 inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-3 py-1">
              <span class="size-2 rounded-full bg-emerald-500 animate-pulse" />
              <span class="text-xs font-semibold text-brand-700 uppercase tracking-wide">Clinical Resource Centre</span>
            </div>
            <h1 class="text-3xl font-bold text-ink sm:text-4xl">Nursing Study Hub</h1>
            <p class="mt-2 text-sm text-graphite max-w-md">
              Evidence-based care plans, SOAP notes, capstone guides and clinical tips — written by BSN, MSN, and DNP nurses.
            </p>
            <div class="mt-4 flex flex-wrap gap-2 text-xs">
              <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-slate-600">✓ NANDA approved</span>
              <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-slate-600">✓ APA 7th format</span>
              <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-slate-600">✓ Evidence-based</span>
            </div>
          </div>
          <div class="shrink-0 text-right hidden sm:block">
            <p class="text-xs text-slate-400 uppercase tracking-wide mb-1">Clinical Guides</p>
            <p class="text-4xl font-bold text-brand-600">{{ displayTotal }}<span class="text-2xl">+</span></p>
            <p class="text-xs text-slate-400 mt-1">Written by real nurses</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Topic tiles ───────────────────────────────────────────────────────── -->
    <section class="bg-white border-b border-slate-100 pb-8 pt-6">
      <div class="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">Browse by topic</p>
        <div class="grid grid-cols-3 gap-3 sm:grid-cols-4 lg:grid-cols-6">
          <button
            v-for="cat in categories" :key="cat"
            class="group flex flex-col items-center gap-2 rounded-2xl border-2 px-2 py-4 text-center transition-all"
            :class="activeCategory === cat
              ? [tile(cat).bg, tile(cat).border, 'shadow-sm scale-[1.02]']
              : 'border-slate-100 bg-white hover:border-slate-200 hover:bg-slate-50'"
            @click="setCategory(cat)"
          >
            <component :is="tile(cat).icon" class="h-5 w-5" />
            <span class="text-[10px] font-bold leading-snug"
              :class="activeCategory === cat ? tile(cat).text : 'text-slate-500'">
              {{ cat }}
            </span>
          </button>
        </div>
      </div>
    </section>

    <!-- ── Article list ──────────────────────────────────────────────────────── -->
    <section class="py-8">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">

        <!-- Active filter label -->
        <div v-if="activeCategory !== 'All'" class="mb-5 flex items-center gap-2">
          <span class="text-sm font-semibold text-ink">{{ activeCategory }}</span>
          <span class="text-xs text-slate-400">· {{ filtered.length }} articles</span>
          <button class="ml-2 text-xs text-brand-600 hover:underline" @click="setCategory('All')">Clear</button>
        </div>

        <!-- Loading skeleton -->
        <div v-if="cmsLoading" class="space-y-4">
          <div v-for="i in 5" :key="i" class="flex gap-5 rounded-2xl bg-white p-5 animate-pulse shadow-sm">
            <div class="h-32 w-44 shrink-0 rounded-xl bg-slate-100" />
            <div class="flex-1 space-y-3 py-2">
              <div class="h-3 w-1/4 rounded bg-slate-100" />
              <div class="h-5 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
              <div class="h-3 w-2/3 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="!filtered.length" class="py-20 text-center space-y-4">
          <p class="text-sm text-slate-500">No articles in this category yet.</p>
          <a :href="app.order"
            class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700">
            Place an order →
          </a>
        </div>

        <div v-else class="space-y-3">

          <!-- Featured: large card -->
          <NuxtLink v-if="featured" :to="`/blog/${featured.slug}`"
            class="group flex flex-col gap-5 rounded-2xl bg-white p-5 shadow-sm transition-all hover:shadow-md sm:flex-row sm:items-stretch">
            <div class="h-52 w-full shrink-0 overflow-hidden rounded-xl bg-slate-100 sm:h-auto sm:w-64">
              <img v-if="featured.thumbnail" :src="featured.thumbnail" :alt="featured.title"
                class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
              <div v-else class="flex h-full min-h-[180px] items-center justify-center bg-brand-50">
                <span class="text-5xl font-extrabold text-brand-200 select-none">N</span>
              </div>
            </div>
            <div class="flex flex-1 flex-col justify-center space-y-3">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full bg-brand-600 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase tracking-wide">Latest</span>
                <span v-if="featured.category"
                  :class="catBadge(featured.category)"
                  class="rounded-full px-2.5 py-0.5 text-[10px] font-bold">
                  {{ featured.category }}
                </span>
                <span class="text-xs text-slate-400">{{ featured.readingTime }} min read</span>
              </div>
              <h2 class="text-xl font-bold leading-snug text-ink transition-colors group-hover:text-brand-700 sm:text-2xl">
                {{ featured.title }}
              </h2>
              <p v-if="featured.excerpt" class="line-clamp-3 text-sm leading-relaxed text-graphite">
                {{ featured.excerpt }}
              </p>
              <div class="flex items-center gap-4 pt-1 text-xs text-slate-400">
                <span>{{ formatDate(featured.publishedAt) }}</span>
                <span class="font-semibold text-brand-600 group-hover:underline ml-auto">Read guide →</span>
              </div>
            </div>
          </NuxtLink>

          <!-- Compact article rows -->
          <NuxtLink
            v-for="post in rest" :key="post.slug"
            :to="`/blog/${post.slug}`"
            class="group flex items-center gap-4 rounded-2xl bg-white p-4 shadow-sm transition-all hover:shadow-md"
          >
            <div class="h-24 w-36 shrink-0 overflow-hidden rounded-xl bg-slate-100">
              <img v-if="post.thumbnail" :src="post.thumbnail" :alt="post.title"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div v-else class="flex h-full items-center justify-center bg-brand-50">
                <span class="text-2xl font-extrabold text-brand-200 select-none">N</span>
              </div>
            </div>
            <div class="min-w-0 flex-1 space-y-1">
              <div class="flex flex-wrap items-center gap-2">
                <span v-if="post.category"
                  :class="catBadge(post.category)"
                  class="rounded-full px-2 py-0.5 text-[10px] font-bold">
                  {{ post.category }}
                </span>
                <span class="text-xs text-slate-400">{{ post.readingTime }} min</span>
              </div>
              <h2 class="text-sm font-bold leading-snug text-ink group-hover:text-brand-700 transition-colors line-clamp-2 sm:text-base">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="hidden line-clamp-1 text-xs leading-relaxed text-graphite sm:block">
                {{ post.excerpt }}
              </p>
              <p class="text-xs text-slate-400">{{ formatDate(post.publishedAt) }}</p>
            </div>
            <div class="shrink-0 text-slate-300 group-hover:text-brand-600 transition-colors">→</div>
          </NuxtLink>

        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
          <button :disabled="activePage === 1"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:opacity-40 transition-colors"
            @click="goPage(activePage - 1)">←</button>
          <button v-for="p in totalPages" :key="p"
            class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
            :class="p === activePage ? 'border-brand-600 bg-brand-600 text-white' : 'bg-white border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
            @click="goPage(p)">{{ p }}</button>
          <button :disabled="activePage === totalPages"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:opacity-40 transition-colors"
            @click="goPage(activePage + 1)">→</button>
        </div>

      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────────────── -->
    <section class="bg-brand-900 py-14 text-center">
      <div class="mx-auto max-w-xl space-y-4 px-4">
        <p class="text-xs font-bold uppercase tracking-widest text-brand-400">Expert Help Available</p>
        <h2 class="text-2xl font-bold text-white">Need a nurse to write it for you?</h2>
        <p class="text-brand-200 text-sm">BSN · MSN · DNP writers. NANDA, SOAP, APA 7th. Grade or money back.</p>
        <a :href="app.order"
          class="inline-flex items-center gap-2 rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors">
          Get my nurse writer →
        </a>
      </div>
    </section>

  </div>
</template>
