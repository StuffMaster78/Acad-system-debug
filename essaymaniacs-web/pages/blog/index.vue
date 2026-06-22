<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Academic Writing Blog — Essay Guides & Tips | EssayManiacs',
  description: 'Expert guides on essays, dissertations, research papers, and academic writing. Tips from subject-specialist writers at EssayManiacs.',
  ogTitle: 'EssayManiacs Blog — Academic Writing Resources',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/blog' }] })

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
const STATIC_PER_PAGE = 12

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

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
}

const CAT_COLOR: Record<string, string> = {
  'Essays':         'bg-brand-50 text-brand-700',
  'Research Papers':'bg-blue-50   text-blue-700',
  'Dissertations':  'bg-slate-100 text-slate-700',
  'Study Tips':     'bg-amber-50  text-amber-700',
}
function catColor(cat: string) { return CAT_COLOR[cat] ?? 'bg-slate-100 text-slate-600' }
</script>

<template>
  <div class="min-h-screen bg-white">

    <!-- ── Header: editorial reading hub (no dark background) ───────────────── -->
    <section class="border-b border-slate-100 bg-white pt-10">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">

        <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between pb-6">
          <div>
            <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-brand-500 mb-1">EssayManiacs · Writing Hub</p>
            <h1 class="text-3xl font-extrabold text-ink sm:text-4xl leading-tight">
              Write Better.<span class="text-brand-600"> Grade Higher.</span>
            </h1>
            <p class="mt-2 text-sm text-graphite max-w-md">
              Expert guides on essays, research papers, dissertations and more — from specialist writers across 100+ subjects.
            </p>
          </div>
          <a :href="app.order"
            class="shrink-0 self-start sm:self-end inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
            Get expert help →
          </a>
        </div>

        <!-- Category tab bar -->
        <div class="flex overflow-x-auto scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0">
          <button
            v-for="cat in categories" :key="cat"
            class="shrink-0 border-b-2 px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap"
            :class="activeCategory === cat
              ? 'border-brand-600 text-brand-700 font-semibold'
              : 'border-transparent text-slate-500 hover:text-ink hover:border-slate-200'"
            @click="setCategory(cat)"
          >{{ cat }}</button>
          <span class="ml-auto shrink-0 flex items-center pl-6 pb-3 text-xs text-slate-400 whitespace-nowrap">
            {{ filtered.length }} articles
          </span>
        </div>

      </div>
    </section>

    <!-- ── Reading list ──────────────────────────────────────────────────────── -->
    <section class="bg-white py-8">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">

        <!-- Loading skeleton -->
        <div v-if="cmsLoading" class="divide-y divide-slate-100">
          <div v-for="i in 5" :key="i" class="flex gap-5 py-7 animate-pulse">
            <div class="flex-1 space-y-3">
              <div class="h-3 w-24 rounded bg-slate-100" />
              <div class="h-5 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
              <div class="h-3 w-1/2 rounded bg-slate-100" />
            </div>
            <div class="h-24 w-36 shrink-0 rounded-xl bg-slate-100" />
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="!filtered.length" class="py-20 text-center space-y-4">
          <p class="text-sm text-slate-500">No articles yet. Check back soon.</p>
          <a :href="app.order"
            class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700">
            Place an order →
          </a>
        </div>

        <template v-else>
          <div class="divide-y divide-slate-100">

            <!-- Featured: Editor's Pick, larger treatment -->
            <NuxtLink v-if="featured" :to="`/blog/${featured.slug}`"
              class="group flex flex-col gap-5 py-8 sm:flex-row sm:items-start sm:gap-8">
              <div class="flex-1 min-w-0 space-y-3">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full bg-brand-600 px-2.5 py-0.5 text-[10px] font-bold text-white uppercase tracking-wide">
                    Editor's Pick
                  </span>
                  <span v-if="featured.category"
                    :class="catColor(featured.category)"
                    class="rounded-full px-2.5 py-0.5 text-[10px] font-bold">
                    {{ featured.category }}
                  </span>
                </div>
                <h2 class="text-2xl font-extrabold leading-snug text-ink group-hover:text-brand-700 transition-colors sm:text-3xl">
                  {{ featured.title }}
                </h2>
                <p v-if="featured.excerpt" class="text-sm leading-relaxed text-graphite line-clamp-3">
                  {{ featured.excerpt }}
                </p>
                <div class="flex items-center gap-3 pt-1 text-xs text-slate-400">
                  <span>{{ featured.readingTime }} min read</span>
                  <span>·</span>
                  <span>{{ formatDate(featured.publishedAt) }}</span>
                  <span class="ml-auto font-semibold text-brand-600 group-hover:underline">Read article →</span>
                </div>
              </div>
              <div class="h-48 w-full shrink-0 overflow-hidden rounded-2xl bg-slate-100 sm:h-40 sm:w-60">
                <img v-if="featured.thumbnail" :src="featured.thumbnail" :alt="featured.title"
                  class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
                <div v-else class="flex h-full items-center justify-center bg-brand-50">
                  <span class="text-5xl font-extrabold text-brand-200 select-none">E</span>
                </div>
              </div>
            </NuxtLink>

            <!-- Compact reading list rows -->
            <NuxtLink
              v-for="post in rest" :key="post.slug"
              :to="`/blog/${post.slug}`"
              class="group flex items-start gap-4 py-6 transition-colors hover:bg-slate-50/70 -mx-4 px-4 sm:mx-0 sm:px-0"
            >
              <div class="flex-1 min-w-0 space-y-1.5">
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="post.category"
                    :class="catColor(post.category)"
                    class="rounded-full px-2 py-0.5 text-[10px] font-bold">
                    {{ post.category }}
                  </span>
                  <span class="text-xs text-slate-400">{{ post.readingTime }} min read</span>
                </div>
                <h2 class="text-[1rem] font-bold leading-snug text-ink group-hover:text-brand-700 transition-colors line-clamp-2">
                  {{ post.title }}
                </h2>
                <p v-if="post.excerpt"
                  class="hidden text-xs leading-relaxed text-graphite line-clamp-2 sm:block">
                  {{ post.excerpt }}
                </p>
                <p class="text-xs text-slate-400">{{ formatDate(post.publishedAt) }}</p>
              </div>
              <div class="h-20 w-28 shrink-0 overflow-hidden rounded-xl bg-slate-100 sm:h-24 sm:w-36">
                <img v-if="post.thumbnail" :src="post.thumbnail" :alt="post.title"
                  class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <div v-else class="flex h-full items-center justify-center">
                  <span class="text-2xl font-extrabold text-slate-200 select-none">E</span>
                </div>
              </div>
            </NuxtLink>

          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
            <button :disabled="activePage === 1"
              class="flex h-9 w-9 items-center justify-center rounded-lg bg-white border border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:opacity-40 transition-colors"
              @click="goPage(activePage - 1)">←</button>
            <button v-for="p in totalPages" :key="p"
              class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
              :class="p === activePage ? 'border-brand-600 bg-brand-600 text-white' : 'bg-white border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
              @click="goPage(p)">{{ p }}</button>
            <button :disabled="activePage === totalPages"
              class="flex h-9 w-9 items-center justify-center rounded-lg bg-white border border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:opacity-40 transition-colors"
              @click="goPage(activePage + 1)">→</button>
          </div>
        </template>

      </div>
    </section>

    <!-- ── CTA ────────────────────────────────────────────────────────────────── -->
    <section class="border-t border-slate-100 bg-brand-50 py-14 text-center">
      <div class="mx-auto max-w-xl space-y-4 px-4">
        <p class="text-xs font-bold uppercase tracking-widest text-brand-400">Deadline coming up?</p>
        <h2 class="text-2xl font-extrabold text-ink">Your paper, handled.</h2>
        <p class="text-sm text-graphite">Subject specialists across 100+ fields. Grade or money back. From $10/page.</p>
        <a :href="app.order"
          class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors shadow-md">
          Start my order →
        </a>
      </div>
    </section>

  </div>
</template>
