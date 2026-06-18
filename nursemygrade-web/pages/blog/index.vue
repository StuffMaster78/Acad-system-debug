<script setup lang="ts">
const app = useAppUrl()

useSeoMeta({
  title: 'Nursing Blog — Care Plans, SOAP Notes & Study Guides | NurseMyGrade',
  description: 'Evidence-based guides on care plans, SOAP notes, nursing capstones, and clinical coursework — written by BSN, MSN, and DNP nurses.',
  ogTitle: 'NurseMyGrade Blog — Nursing Study Resources',
})
useHead({ link: [{ rel: 'canonical', href: 'https://nursemygrade.com/blog' }] })

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

const config   = useRuntimeConfig()
const apiBase  = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''
const PAGE_SIZE = 12

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
      `${apiBase}/api/v2/pages/`,
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
  return { slug: p.meta.slug, title: p.title, excerpt: p.excerpt, category: p.category_name || '', readingTime: p.reading_time_minutes || 1, publishedAt: p.meta.first_published_at, thumbnail: p.thumbnail?.url ?? null, fromCms: true }
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

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

const CAT_COLOR: Record<string, string> = {
  'Nursing Papers':       'bg-brand-50  text-brand-700',
  'Capstone & Research':  'bg-slate-100 text-slate-700',
  'Citation & Format':    'bg-indigo-50 text-indigo-700',
  'Clinical Simulations': 'bg-emerald-50 text-emerald-700',
  'Nursing School':       'bg-rose-50   text-rose-700',
  'Essays':               'bg-brand-50  text-brand-700',
  'Research Papers':      'bg-blue-50   text-blue-700',
}
function catColor(cat: string) { return CAT_COLOR[cat] ?? 'bg-slate-100 text-slate-600' }
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-brand-900 py-16 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]" />
      <div class="relative mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-300">Resources</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Nursing Blog</h1>
        <p class="mt-4 text-lg text-brand-200">Care plans, SOAP notes, capstones, and clinical guides — written by real nurses.</p>
      </div>
    </section>

    <!-- ── Content ────────────────────────────────────────────────────────── -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

        <div v-if="cmsLoading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="i in 6" :key="i" class="animate-pulse overflow-hidden rounded-2xl border border-slate-200">
            <div class="h-44 bg-slate-100" />
            <div class="space-y-3 p-5">
              <div class="h-3 w-1/3 rounded bg-slate-100" />
              <div class="h-4 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <template v-else>
          <!-- Category filter -->
          <div v-if="categories.length > 1" class="mb-8 flex flex-wrap gap-2">
            <button
              v-for="cat in categories" :key="cat"
              class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
              :class="activeCategory === cat ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
              @click="setCategory(cat)"
            >{{ cat }}</button>
          </div>

          <!-- Empty -->
          <div v-if="!filtered.length" class="space-y-4 py-20 text-center">
            <p class="text-sm text-slate-500">No articles yet — check back soon.</p>
            <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
              Place an order <Icon name="arrow-right" class="h-4 w-4" />
            </a>
          </div>

          <template v-else>
            <!-- Featured post -->
            <NuxtLink
              v-if="featured"
              :to="`/blog/${featured.slug}`"
              class="group mb-10 flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md sm:flex-row"
            >
              <div class="h-52 shrink-0 overflow-hidden bg-slate-100 sm:h-auto sm:w-2/5">
                <img v-if="featured.thumbnail" :src="featured.thumbnail" :alt="featured.title" class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <div v-else class="flex h-full items-center justify-center">
                  <span class="select-none text-5xl font-extrabold text-slate-200">N</span>
                </div>
              </div>
              <div class="flex flex-1 flex-col justify-center space-y-3 p-6 sm:p-8">
                <div class="flex items-center gap-3 text-xs text-slate-500">
                  <span v-if="featured.category" class="rounded-full px-2.5 py-0.5 font-semibold" :class="catColor(featured.category)">{{ featured.category }}</span>
                  <span class="flex items-center gap-1"><Icon name="clock" class="h-3 w-3" />{{ featured.readingTime }} min read</span>
                </div>
                <h2 class="text-xl font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ featured.title }}</h2>
                <p v-if="featured.excerpt" class="line-clamp-3 text-sm leading-relaxed text-slate-500">{{ featured.excerpt }}</p>
                <div class="flex items-center gap-4 pt-1">
                  <span class="flex items-center gap-1 text-xs text-slate-400"><Icon name="calendar" class="h-3 w-3" />{{ formatDate(featured.publishedAt) }}</span>
                  <span class="flex items-center gap-1 text-xs font-semibold text-brand-600 group-hover:underline">Read article <Icon name="arrow-right" class="h-3 w-3" /></span>
                </div>
              </div>
            </NuxtLink>

            <!-- Post grid -->
            <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <NuxtLink
                v-for="post in rest"
                :key="post.slug"
                :to="`/blog/${post.slug}`"
                class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
              >
                <div class="h-44 overflow-hidden bg-slate-100">
                  <img v-if="post.thumbnail" :src="post.thumbnail" :alt="post.title" class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                  <div v-else class="flex h-full items-center justify-center">
                    <span class="select-none text-2xl font-extrabold text-slate-200">N</span>
                  </div>
                </div>
                <div class="flex flex-1 flex-col space-y-2.5 p-5">
                  <div class="flex items-center gap-2.5 text-xs text-slate-500">
                    <span v-if="post.category" class="rounded-full px-2.5 py-0.5 font-semibold" :class="catColor(post.category)">{{ post.category }}</span>
                    <span v-if="post.readingTime" class="flex items-center gap-1"><Icon name="clock" class="h-3 w-3" />{{ post.readingTime }} min</span>
                  </div>
                  <h2 class="line-clamp-2 flex-1 text-sm font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ post.title }}</h2>
                  <p v-if="post.excerpt" class="line-clamp-2 text-xs leading-relaxed text-slate-500">{{ post.excerpt }}</p>
                  <div class="flex items-center justify-between border-t border-slate-100 pt-1.5">
                    <span class="flex items-center gap-1 text-xs text-slate-400"><Icon name="calendar" class="h-3 w-3" />{{ formatDate(post.publishedAt) }}</span>
                    <Icon name="arrow-right" class="h-3.5 w-3.5 text-brand-600 opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </div>
              </NuxtLink>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="mt-12 flex items-center justify-center gap-2">
              <button :disabled="activePage === 1" class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-sm text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40 transition-colors" @click="goPage(activePage - 1)">←</button>
              <button
                v-for="p in totalPages" :key="p"
                class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
                :class="p === activePage ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
                @click="goPage(p)"
              >{{ p }}</button>
              <button :disabled="activePage === totalPages" class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-sm text-slate-500 hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40 transition-colors" @click="goPage(activePage + 1)">→</button>
            </div>
          </template>
        </template>

      </div>
    </section>

    <!-- ── CTA ───────────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-12 text-center">
      <div class="mx-auto max-w-xl space-y-4 px-4">
        <h2 class="text-xl font-bold text-slate-900">Need a nurse to write it for you?</h2>
        <p class="text-sm text-slate-500">BSN · MSN · DNP writers. NANDA, SOAP, APA 7th. Grade or money back.</p>
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white transition-colors hover:bg-brand-700">
          Get my nurse writer <Icon name="arrow-right" class="h-4 w-4" />
        </a>
      </div>
    </section>

  </div>
</template>
