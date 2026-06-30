<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Research Paper Blog — APA, MLA & Writing Guides | ResearchPaperMate',
  description: 'Practical guides on research papers, citations, literature reviews, and academic writing — from Master\'s and PhD writers across 100+ fields.',
  ogTitle: 'ResearchPaperMate Blog — Research & Writing Resources',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})
useHead({ link: [{ rel: 'canonical', href: 'https://researchpapermate.com/blog' }] })

// ── Shared shape used for both CMS and static posts ──────────────────────
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

// ── CMS types ─────────────────────────────────────────────────────────────
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

const config    = useRuntimeConfig()
const PAGE_SIZE = 12

const cmsPosts   = ref<CmsPost[]>([])
const cmsTotal   = ref(0)
const cmsPage    = ref(1)
const cmsLoading = ref(false)
const cmsError   = ref(false)
const usingCms   = ref(false)

async function loadCmsPage(p: number) {
  cmsLoading.value = true; cmsError.value = false
  try {
    // /wagtail proxy (server/routes/wagtail/[...path].ts) sets Host: researchpapermate.com
    // internally, so both SSR and client-side pagination hit the correct site.
    const res = await $fetch<{ meta: { total_count: number }; items: CmsPost[] }>(
      '/wagtail/api/v2/pages/',
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

// ── Static fallback ────────────────────────────────────────────────────────
const { getAll } = useBlog()
const staticPosts = usingCms.value ? [] : getAll()

// ── Normalise ──────────────────────────────────────────────────────────────
function normCms(p: CmsPost): Post {
  const thumbUrl = p.thumbnail?.url ?? null
  // Make relative /media/... URLs absolute so NuxtImg can serve them
  const siteUrl = config.public.siteUrl || 'https://researchpapermate.com'
  const thumbnail = thumbUrl ? (thumbUrl.startsWith('http') ? thumbUrl : `${siteUrl}${thumbUrl}`) : null
  return { slug: p.meta.slug, title: p.title, excerpt: p.excerpt, category: p.category_name || '', readingTime: p.reading_time_minutes || 1, publishedAt: p.meta.first_published_at, thumbnail, fromCms: true }
}
function normStatic(p: ReturnType<typeof getAll>[0]): Post {
  return {
    slug: p.slug,
    title: p.title,
    excerpt: p.excerpt,
    category: p.category,
    readingTime: Number.parseInt(p.readTime, 10) || 1,
    publishedAt: p.date,
    thumbnail: null,
    fromCms: false,
  }
}

const allPosts = computed<Post[]>(() =>
  usingCms.value ? cmsPosts.value.map(normCms) : staticPosts.map(normStatic)
)

const cmsTotalPages = computed(() => Math.ceil(cmsTotal.value / PAGE_SIZE))

// ── Category filter (works for both sources) ──────────────────────────────
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

const CAT_COLOR: Record<string, string> = {
  'Research Papers':    'bg-brand-50  text-claret-700',
  'Citations & Style':  'bg-blue-50   text-blue-700',
  'Literature Reviews': 'bg-indigo-50 text-indigo-700',
  'Dissertations':      'bg-slate-100 text-slate-700',
  'Study Tips':         'bg-amber-50  text-amber-700',
  'Essays':             'bg-violet-50 text-violet-700',
}
function catColor(cat: string) { return CAT_COLOR[cat] ?? 'bg-slate-100 text-slate-600' }
</script>

<template>
  <div class="bg-parchment-50 min-h-screen" style="--parchment-50: #fdf8f0">

    <!-- ── Header: academic journal cover ───────────────────────────────────── -->
    <!-- amber rule = journal cover spine -->
    <div class="h-1.5 bg-gradient-to-r from-amber-500 via-amber-400 to-amber-600" />
    <section class="bg-claret-950 border-b border-claret-800">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">

        <!-- Journal masthead -->
        <div class="border-b border-claret-800 pb-5 mb-5 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-[0.25em] text-amber-500">ResearchPaperMate</p>
            <h1 class="text-3xl font-bold text-white sm:text-4xl tracking-tight">Research Writing Library</h1>
          </div>
          <!-- Journal volume block -->
          <div class="shrink-0 border border-claret-700 rounded px-4 py-2 text-right">
            <p class="text-[9px] font-bold uppercase tracking-[0.2em] text-claret-400">Academic Reference Series</p>
            <p class="text-xs text-amber-400 font-semibold mt-0.5">
              Vol. {{ new Date().getFullYear() }} · Issue {{ new Date().getMonth() + 1 }} · {{ displayTotal }} Guides
            </p>
          </div>
        </div>

        <!-- Description + discipline tags -->
        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <p class="text-claret-300 text-sm max-w-lg leading-relaxed">
            APA · MLA · Chicago · Harvard style guides, literature review frameworks, and research methodology primers —
            written by Master's and PhD researchers across 100+ disciplines.
          </p>
          <div class="flex flex-wrap gap-1.5 sm:justify-end shrink-0">
            <span v-for="d in ['APA 7th', 'MLA 9th', 'Chicago', 'Harvard', 'IEEE']" :key="d"
              class="rounded border border-claret-700 px-2 py-0.5 text-[10px] font-semibold text-claret-300">
              {{ d }}
            </span>
          </div>
        </div>

        <!-- Category filter as academic subject tabs -->
        <div v-if="categories.length > 1" class="mt-6 flex flex-wrap gap-2 border-t border-claret-800 pt-5">
          <button
            v-for="cat in categories" :key="cat"
            class="rounded border px-3 py-1 text-xs font-semibold transition-colors"
            :class="activeCategory === cat
              ? 'border-amber-500 bg-amber-500 text-claret-950'
              : 'border-claret-700 text-claret-300 hover:border-amber-400 hover:text-amber-300'"
            @click="setCategory(cat)"
          >{{ cat }}</button>
        </div>
      </div>
    </section>

    <!-- ── Content: numbered journal index layout ─────────────────────────── -->
    <section class="py-10">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">

        <!-- Loading -->
        <div v-if="cmsLoading" class="space-y-5">
          <div v-for="i in 5" :key="i" class="flex gap-6 animate-pulse bg-white rounded-xl p-5">
            <div class="h-32 w-44 shrink-0 rounded-lg bg-slate-100" />
            <div class="flex-1 space-y-3 py-2">
              <div class="h-3 w-1/4 rounded bg-slate-100" />
              <div class="h-5 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="!filtered.length" class="py-20 text-center space-y-4">
          <p class="text-sm text-slate-500">No articles yet.</p>
          <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-6 py-3 text-sm font-bold text-white hover:bg-amber-700">
            Place an order →
          </a>
        </div>

        <div v-else class="space-y-4">

          <!-- Featured: large card with image on right (reversed from NMG) -->
          <NuxtLink v-if="featured" :to="`/${featured.slug}`"
            class="group flex flex-col-reverse gap-5 rounded-2xl border border-claret-100 bg-white p-6 shadow-sm hover:shadow-md transition-all sm:flex-row">
            <!-- Content (left) -->
            <div class="flex flex-1 flex-col justify-center space-y-3">
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold uppercase tracking-widest text-amber-600">Featured</span>
                <span v-if="featured.category" class="rounded px-2 py-0.5 text-[10px] font-bold" :class="catColor(featured.category)">
                  {{ featured.category }}
                </span>
              </div>
              <h2 class="text-xl font-bold leading-snug text-ink group-hover:text-claret-700 transition-colors sm:text-2xl">
                {{ featured.title }}
              </h2>
              <p v-if="featured.excerpt" class="line-clamp-3 text-sm leading-relaxed text-graphite">{{ featured.excerpt }}</p>
              <div class="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-1">
                <span>{{ featured.readingTime }} min read</span>
                <span>{{ formatDate(featured.publishedAt) }}</span>
                <span class="text-claret-700 font-semibold group-hover:underline ml-auto">Read full article →</span>
              </div>
            </div>
            <!-- Image (right, taller) -->
            <div class="h-48 w-full shrink-0 overflow-hidden rounded-xl bg-slate-100 sm:h-auto sm:w-64">
              <NuxtImg v-if="featured.thumbnail" :src="featured.thumbnail" :alt="featured.title"
                width="512" height="288" fetchpriority="high" loading="eager"
                class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
              <div v-else class="flex h-full items-center justify-center bg-parchment-100">
                <span class="text-5xl font-extrabold text-parchment-300 select-none">R</span>
              </div>
            </div>
          </NuxtLink>

          <!-- Numbered article entries -->
          <NuxtLink
            v-for="(post, idx) in rest" :key="post.slug"
            :to="`/${post.slug}`"
            class="group flex items-stretch gap-5 rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition-all hover:shadow-md hover:border-claret-100"
          >
            <!-- Entry number -->
            <div class="flex w-10 shrink-0 flex-col items-center justify-center">
              <span class="text-xl font-extrabold text-slate-200 tabular-nums">
                {{ String((featured ? idx + 2 : idx + 1)).padStart(2, '0') }}
              </span>
            </div>
            <!-- Thumbnail -->
            <div class="h-24 w-36 shrink-0 overflow-hidden rounded-lg bg-slate-100">
              <NuxtImg v-if="post.thumbnail" :src="post.thumbnail" :alt="post.title"
                width="144" height="96" loading="lazy"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
              <div v-else class="flex h-full items-center justify-center bg-parchment-100">
                <span class="text-2xl font-extrabold text-parchment-300 select-none">R</span>
              </div>
            </div>
            <!-- Content -->
            <div class="min-w-0 flex-1 py-1 space-y-1.5">
              <div class="flex items-center gap-2">
                <span v-if="post.category" class="rounded px-2 py-0.5 text-[10px] font-bold" :class="catColor(post.category)">
                  {{ post.category }}
                </span>
                <span class="text-xs text-slate-400">{{ post.readingTime }} min read</span>
              </div>
              <h2 class="font-bold leading-snug text-ink group-hover:text-claret-700 transition-colors line-clamp-2">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="line-clamp-2 text-xs leading-relaxed text-graphite hidden sm:block">
                <span class="font-semibold text-slate-500 uppercase tracking-wide text-[9px]">Abstract — </span>{{ post.excerpt }}
              </p>
              <p class="text-xs text-slate-400">{{ formatDate(post.publishedAt) }}</p>
            </div>
            <!-- Arrow -->
            <div class="flex shrink-0 items-center pl-2">
              <span class="text-slate-200 group-hover:text-claret-700 transition-colors text-lg">→</span>
            </div>
          </NuxtLink>

        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
          <button :disabled="activePage === 1"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-amber-400 hover:text-amber-600 disabled:opacity-40 transition-colors"
            @click="goPage(activePage - 1)">←</button>
          <button v-for="p in totalPages" :key="p"
            class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
            :class="p === activePage ? 'border-amber-500 bg-amber-500 text-white' : 'bg-white border-slate-200 text-slate-500 hover:border-amber-400 hover:text-amber-600'"
            @click="goPage(p)">{{ p }}</button>
          <button :disabled="activePage === totalPages"
            class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-amber-400 hover:text-amber-600 disabled:opacity-40 transition-colors"
            @click="goPage(activePage + 1)">→</button>
        </div>

      </div>
    </section>

    <!-- CTA: academic/dark -->
    <section class="bg-claret-950 py-14 text-center border-t border-claret-800">
      <div class="mx-auto max-w-xl space-y-4 px-4">
        <p class="text-xs font-bold uppercase tracking-widest text-amber-400">Expert Research Writers</p>
        <h2 class="text-2xl font-bold text-white">Need your research paper written?</h2>
        <p class="text-claret-300 text-sm">Master's and PhD writers across 100+ subjects. Properly cited, from $15/page.</p>
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-3.5 text-sm font-bold text-claret-950 hover:bg-amber-400 transition-colors">
          Place my order →
        </a>
      </div>
    </section>

  </div>
</template>
