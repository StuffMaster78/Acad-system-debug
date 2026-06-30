<script setup lang="ts">
useSeoMeta({
  title: 'Writer Resources & Blog | Writers Creek',
  description: 'Guides, tips, and resources for Writers Creek writers — writing quality advice, payout information, platform updates, and academic writing best practice.',
  ogImage:       'https://writerscreek.com/og-default.png',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

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

const config  = useRuntimeConfig()
const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

const PAGE_SIZE = 12
const posts      = ref<CmsPost[]>([])
const totalCount = ref(0)
const page       = ref(1)
const loading    = ref(false)
const hasCms     = ref(false)

async function loadPage(p: number) {
  loading.value = true
  try {
    const res = await $fetch<{ meta: { total_count: number }; items: CmsPost[] }>(
      '/wagtail/api/v2/pages/',
      {
        params: {
          type: 'cms_blog.BlogPostPage',
          fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail,author_name',
          order: '-first_published_at',
          limit: PAGE_SIZE,
          offset: (p - 1) * PAGE_SIZE,
        },
      },
    )
    posts.value      = res.items ?? []
    totalCount.value = res.meta?.total_count ?? 0
    page.value       = p
    if (res.items?.length) hasCms.value = true
  } catch {
    /* leave hasCms false — show placeholder */
  } finally {
    loading.value = false
  }
}

await loadPage(1)

const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE))

const categories = computed(() => {
  const cats = new Set(posts.value.map(p => p.category_name).filter(Boolean))
  return ['All', ...cats]
})
const activeCategory = ref('All')

const filtered = computed(() =>
  activeCategory.value === 'All'
    ? posts.value
    : posts.value.filter(p => p.category_name === activeCategory.value)
)

const featured = computed(() => (page.value === 1 && activeCategory.value === 'All') ? filtered.value[0] ?? null : null)
const rest     = computed(() => featured.value ? filtered.value.slice(1) : filtered.value)

function catCount(cat: string) {
  return posts.value.filter(p => p.category_name === cat).length
}

function setCategory(cat: string) { activeCategory.value = cat }

async function goPage(p: number) {
  await loadPage(p)
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

const CAT_COLOR: Record<string, string> = {
  'Writing Quality':  'bg-brand-50 text-brand-700 ring-brand-200',
  'Earnings & Pay':   'bg-emerald-50 text-emerald-700 ring-emerald-200',
  'Platform Updates': 'bg-slate-100 text-slate-600 ring-slate-200',
  'Academic Writing': 'bg-indigo-50 text-indigo-700 ring-indigo-200',
  'Career & Growth':  'bg-amber-50 text-amber-700 ring-amber-200',
}
function catColor(cat: string) { return CAT_COLOR[cat] ?? 'bg-slate-100 text-slate-600 ring-slate-200' }

const CAT_DOT: Record<string, string> = {
  'Writing Quality':  'bg-brand-500',
  'Earnings & Pay':   'bg-emerald-500',
  'Platform Updates': 'bg-slate-400',
  'Academic Writing': 'bg-indigo-500',
  'Career & Growth':  'bg-amber-500',
}
function catDot(cat: string) { return CAT_DOT[cat] ?? 'bg-slate-400' }

const currentMonth = new Date().toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })
</script>

<template>
  <div class="min-h-screen bg-[#F8F9FA]">

    <!-- ── Masthead ───────────────────────────────────────────────────────── -->
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-5">
          <div class="flex items-center gap-4">
            <div class="h-9 w-9 rounded-xl bg-brand-600 flex items-center justify-center">
              <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </div>
            <div>
              <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-brand-600">Writers Creek</p>
              <h1 class="text-lg font-bold leading-tight text-slate-900">Writer Resource Hub</h1>
            </div>
          </div>
          <div class="hidden items-center gap-6 sm:flex">
            <p class="text-xs text-slate-400">{{ currentMonth }}</p>
            <span v-if="totalCount" class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              {{ totalCount }} articles
            </span>
            <NuxtLink to="/apply"
              class="rounded-lg bg-brand-600 px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-brand-700">
              Apply to write →
            </NuxtLink>
          </div>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div class="lg:flex lg:gap-10 xl:gap-14">

        <!-- ── Sidebar ─────────────────────────────────────────────────────── -->
        <aside class="hidden lg:block lg:w-56 xl:w-60 shrink-0">
          <div class="sticky top-8 space-y-6">

            <!-- Category nav -->
            <div>
              <p class="mb-3 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">Topics</p>
              <nav class="space-y-0.5">
                <button
                  v-for="cat in categories"
                  :key="cat"
                  class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm transition-all text-left"
                  :class="activeCategory === cat
                    ? 'bg-brand-600 font-semibold text-white shadow-sm'
                    : 'text-slate-600 hover:bg-white hover:text-slate-900 hover:shadow-sm'"
                  @click="setCategory(cat)"
                >
                  <span class="flex items-center gap-2.5">
                    <span
                      v-if="cat !== 'All'"
                      class="h-1.5 w-1.5 rounded-full shrink-0"
                      :class="activeCategory === cat ? 'bg-white' : catDot(cat)"
                    />
                    <span v-else class="h-1.5 w-1.5 rounded-full shrink-0"
                      :class="activeCategory === cat ? 'bg-white' : 'bg-slate-300'" />
                    {{ cat }}
                  </span>
                  <span
                    class="tabular-nums text-xs"
                    :class="activeCategory === cat ? 'text-white/70' : 'text-slate-400'"
                  >
                    {{ cat === 'All' ? posts.length : catCount(cat) }}
                  </span>
                </button>
              </nav>
            </div>

            <!-- Divider -->
            <div class="border-t border-slate-200" />

            <!-- Sidebar CTA -->
            <div class="rounded-2xl bg-slate-900 p-5 text-white">
              <p class="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400 mb-2">Join the team</p>
              <p class="text-sm leading-relaxed text-slate-200">
                Write for us. Earn from <span class="font-bold text-white">$18–$45</span> per page with bi-weekly payouts.
              </p>
              <ul class="mt-3 space-y-1.5">
                <li v-for="point in ['Credential-verified writers', 'Level-based pay', 'Flexible deadlines']" :key="point"
                  class="flex items-center gap-2 text-xs text-slate-300">
                  <svg class="h-3.5 w-3.5 shrink-0 text-brand-400" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  {{ point }}
                </li>
              </ul>
              <NuxtLink to="/apply"
                class="mt-4 block rounded-xl bg-brand-500 px-4 py-2.5 text-center text-xs font-bold text-white transition-colors hover:bg-brand-400">
                Apply now →
              </NuxtLink>
            </div>
          </div>
        </aside>

        <!-- ── Main content ────────────────────────────────────────────────── -->
        <main class="flex-1 min-w-0">

          <!-- Loading skeletons -->
          <div v-if="loading" class="space-y-6">
            <div class="animate-pulse h-64 rounded-2xl bg-slate-200" />
            <div class="grid gap-px bg-slate-200 rounded-2xl overflow-hidden sm:grid-cols-2 lg:grid-cols-3">
              <div v-for="i in 6" :key="i" class="animate-pulse bg-white p-6 h-44" />
            </div>
          </div>

          <!-- No CMS content -->
          <div v-else-if="!hasCms" class="py-24 text-center">
            <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm">
              <svg class="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
              </svg>
            </div>
            <h2 class="text-lg font-bold text-slate-900">Articles coming soon</h2>
            <p class="mt-2 text-sm text-slate-500">We're preparing writer guides, quality tips, and payout FAQs.</p>
            <NuxtLink to="/apply"
              class="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-brand-700">
              Apply to write while you wait
            </NuxtLink>
          </div>

          <template v-else>

            <!-- Mobile category scroll -->
            <div class="lg:hidden -mx-4 mb-8 overflow-x-auto px-4">
              <div class="flex gap-2 pb-1 w-max">
                <button
                  v-for="cat in categories"
                  :key="cat"
                  class="flex items-center gap-1.5 rounded-full border px-4 py-1.5 text-sm font-medium whitespace-nowrap transition-colors"
                  :class="activeCategory === cat
                    ? 'border-brand-600 bg-brand-600 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:border-brand-400 hover:text-brand-700'"
                  @click="setCategory(cat)"
                >
                  <span
                    v-if="cat !== 'All'"
                    class="h-1.5 w-1.5 rounded-full"
                    :class="activeCategory === cat ? 'bg-white' : catDot(cat)"
                  />
                  {{ cat }}
                </button>
              </div>
            </div>

            <!-- ── Featured article ──────────────────────────────────────── -->
            <NuxtLink
              v-if="featured"
              :to="`/${featured.meta.slug}`"
              class="group mb-8 block overflow-hidden rounded-2xl bg-slate-900 shadow-lg"
            >
              <div class="relative">
                <!-- Background image -->
                <img
                  v-if="featured.thumbnail"
                  :src="featured.thumbnail.url"
                  :alt="featured.title"
                  class="absolute inset-0 h-full w-full object-cover opacity-20 transition-opacity duration-500 group-hover:opacity-25"
                />
                <!-- Decorative number -->
                <div
                  aria-hidden="true"
                  class="pointer-events-none absolute right-8 top-4 select-none font-black text-[9rem] leading-none text-white/[0.04] sm:text-[12rem]"
                >01</div>
                <!-- Content -->
                <div class="relative px-7 py-9 sm:px-10 sm:py-12">
                  <div class="flex flex-wrap items-center gap-2.5 mb-5">
                    <span class="inline-flex items-center gap-1.5 rounded-full bg-brand-500/20 px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-brand-300 ring-1 ring-brand-500/30">
                      <span class="h-1.5 w-1.5 rounded-full bg-brand-400" />
                      Featured
                    </span>
                    <span v-if="featured.category_name" class="text-xs text-slate-400">
                      {{ featured.category_name }}
                    </span>
                  </div>
                  <h2 class="max-w-2xl text-2xl font-bold leading-snug text-white transition-colors group-hover:text-brand-300 sm:text-3xl lg:text-[2rem]">
                    {{ featured.title }}
                  </h2>
                  <p v-if="featured.excerpt" class="mt-3 max-w-xl text-sm leading-relaxed text-slate-400 line-clamp-2">
                    {{ featured.excerpt }}
                  </p>
                  <div class="mt-7 flex items-center gap-1">
                    <div class="flex items-center gap-3 text-xs text-slate-500">
                      <span v-if="featured.author_name" class="font-medium text-slate-300">{{ featured.author_name }}</span>
                      <span v-if="featured.author_name">·</span>
                      <time>{{ fmtDate(featured.meta.first_published_at) }}</time>
                      <span>·</span>
                      <span>{{ featured.reading_time_minutes }} min read</span>
                    </div>
                    <span class="ml-auto text-xs font-semibold text-brand-400 transition-all group-hover:text-brand-300 group-hover:translate-x-0.5">
                      Read article →
                    </span>
                  </div>
                </div>
              </div>
            </NuxtLink>

            <!-- ── Section header ────────────────────────────────────────── -->
            <div class="mb-5 flex items-center gap-4">
              <h2 class="shrink-0 text-[11px] font-bold uppercase tracking-[0.15em] text-slate-400">
                {{ activeCategory === 'All' ? 'Latest articles' : activeCategory }}
              </h2>
              <div class="h-px flex-1 bg-slate-200" />
              <span class="shrink-0 text-[11px] text-slate-400">{{ rest.length }} article{{ rest.length !== 1 ? 's' : '' }}</span>
            </div>

            <!-- ── Article mosaic ────────────────────────────────────────── -->
            <div
              v-if="rest.length"
              class="grid grid-cols-1 gap-px overflow-hidden rounded-2xl bg-slate-200 shadow-sm sm:grid-cols-2 lg:grid-cols-3"
            >
              <NuxtLink
                v-for="(post, idx) in rest"
                :key="post.meta.slug"
                :to="`/${post.meta.slug}`"
                class="group flex flex-col bg-white p-6 transition-colors duration-150 hover:bg-[#F8F9FA]"
              >
                <!-- Top row: number + category -->
                <div class="mb-4 flex items-start justify-between">
                  <span class="font-black text-2xl leading-none text-slate-100 select-none tabular-nums">
                    {{ String(idx + 2).padStart(2, '0') }}
                  </span>
                  <span
                    v-if="post.category_name"
                    class="rounded-full px-2.5 py-0.5 text-[10px] font-semibold ring-1"
                    :class="catColor(post.category_name)"
                  >{{ post.category_name }}</span>
                </div>

                <!-- Thumbnail (optional) -->
                <div
                  v-if="post.thumbnail"
                  class="mb-4 overflow-hidden rounded-xl bg-slate-100"
                  style="aspect-ratio: 16/7;"
                >
                  <img
                    :src="post.thumbnail.url"
                    :alt="post.title"
                    class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
                    loading="lazy"
                  />
                </div>

                <!-- Title -->
                <h3 class="flex-1 text-sm font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 line-clamp-2">
                  {{ post.title }}
                </h3>

                <!-- Excerpt -->
                <p v-if="post.excerpt" class="mt-2 text-xs leading-relaxed text-slate-400 line-clamp-2">
                  {{ post.excerpt }}
                </p>

                <!-- Footer meta -->
                <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3.5">
                  <div class="flex items-center gap-2 text-[11px] text-slate-400">
                    <time>{{ fmtDate(post.meta.first_published_at) }}</time>
                    <span>·</span>
                    <span>{{ post.reading_time_minutes }} min</span>
                  </div>
                  <span class="text-[11px] font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">
                    Read →
                  </span>
                </div>
              </NuxtLink>
            </div>

            <!-- Empty filtered state -->
            <div v-else-if="!featured" class="rounded-2xl bg-white py-20 text-center shadow-sm">
              <p class="text-sm text-slate-400">No articles in this category yet.</p>
            </div>

            <!-- ── Pagination ─────────────────────────────────────────────── -->
            <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-1.5">
              <button
                :disabled="page === 1"
                class="h-9 rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-500 shadow-sm transition-colors hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
                @click="goPage(page - 1)"
              >← Prev</button>

              <div class="flex gap-1">
                <button
                  v-for="p in totalPages"
                  :key="p"
                  class="h-9 w-9 rounded-lg border text-sm font-medium shadow-sm transition-colors"
                  :class="p === page
                    ? 'border-brand-600 bg-brand-600 text-white'
                    : 'border-slate-200 bg-white text-slate-500 hover:border-brand-400 hover:text-brand-600'"
                  @click="goPage(p)"
                >{{ p }}</button>
              </div>

              <button
                :disabled="page === totalPages"
                class="h-9 rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-500 shadow-sm transition-colors hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
                @click="goPage(page + 1)"
              >Next →</button>
            </div>

          </template>
        </main>
      </div>
    </div>

  </div>
</template>
