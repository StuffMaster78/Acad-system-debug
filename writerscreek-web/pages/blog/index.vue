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
  if (!apiBase) return
  loading.value = true
  try {
    const res = await $fetch<{ meta: { total_count: number }; items: CmsPost[] }>(
      `${apiBase}/api/v2/pages/`,
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

function setCategory(cat: string) { activeCategory.value = cat }

async function goPage(p: number) {
  await loadPage(p)
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

const CAT_COLOR: Record<string, string> = {
  'Writing Quality':   'bg-brand-50 text-brand-700',
  'Earnings & Pay':    'bg-emerald-50 text-emerald-700',
  'Platform Updates':  'bg-slate-100 text-slate-700',
  'Academic Writing':  'bg-indigo-50 text-indigo-700',
  'Career & Growth':   'bg-amber-50 text-amber-700',
}
function catColor(cat: string) { return CAT_COLOR[cat] ?? 'bg-slate-100 text-slate-600' }
</script>

<template>
  <div>

    <!-- ── Hero ──────────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden bg-slate-900 py-16 text-center">
      <div class="pointer-events-none absolute inset-0 bg-[radial-gradient(rgba(56,189,248,0.07)_1.5px,transparent_1.5px)] [background-size:28px_28px]" />
      <div class="relative mx-auto max-w-2xl px-4 sm:px-6">
        <p class="mb-3 text-xs font-bold uppercase tracking-widest text-brand-400">Resources</p>
        <h1 class="text-4xl font-bold text-white sm:text-5xl">Writer Blog</h1>
        <p class="mt-4 text-lg text-slate-300">Guides, quality advice, and platform updates — written for Writers Creek writers.</p>
      </div>
    </section>

    <!-- ── Content ───────────────────────────────────────────────────────── -->
    <section class="bg-white py-14">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-screen-xl 2xl:px-12">

        <!-- Loading skeletons -->
        <div v-if="loading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="i in 6" :key="i" class="animate-pulse overflow-hidden rounded-2xl border border-slate-200">
            <div class="h-44 bg-slate-100" />
            <div class="space-y-3 p-5">
              <div class="h-3 w-1/3 rounded bg-slate-100" />
              <div class="h-4 w-3/4 rounded bg-slate-100" />
              <div class="h-3 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <!-- No CMS content yet -->
        <div v-else-if="!hasCms" class="mx-auto max-w-md py-20 text-center">
          <div class="mb-6 flex justify-center">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
              <svg class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
              </svg>
            </div>
          </div>
          <h2 class="text-xl font-bold text-slate-900">Articles coming soon</h2>
          <p class="mt-2 text-slate-600">We are preparing writer guides, quality tips, and payout FAQs. Check back shortly.</p>
          <NuxtLink to="/apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-brand-700">
            Apply to write while you wait
          </NuxtLink>
        </div>

        <template v-else>
          <!-- Category filter -->
          <div v-if="categories.length > 1" class="mb-10 flex flex-wrap gap-2">
            <button
              v-for="cat in categories"
              :key="cat"
              class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
              :class="activeCategory === cat
                ? 'border-brand-600 bg-brand-600 text-white'
                : 'border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
              @click="setCategory(cat)"
            >{{ cat }}</button>
          </div>

          <!-- Featured post -->
          <NuxtLink
            v-if="featured"
            :to="`/blog/${featured.meta.slug}`"
            class="group mb-10 flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md sm:flex-row"
          >
            <div class="h-52 shrink-0 overflow-hidden bg-slate-100 sm:h-auto sm:w-2/5">
              <img
                v-if="featured.thumbnail"
                :src="featured.thumbnail.url"
                :alt="featured.title"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div v-else class="flex h-full items-center justify-center">
                <span class="select-none text-5xl font-extrabold text-slate-200">W</span>
              </div>
            </div>
            <div class="flex flex-1 flex-col justify-center space-y-3 p-6 sm:p-8">
              <div class="flex items-center gap-3 text-xs text-slate-500">
                <span
                  v-if="featured.category_name"
                  class="rounded-full px-2.5 py-0.5 font-semibold"
                  :class="catColor(featured.category_name)"
                >{{ featured.category_name }}</span>
                <span v-if="featured.reading_time_minutes">{{ featured.reading_time_minutes }} min read</span>
              </div>
              <h2 class="text-xl font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ featured.title }}</h2>
              <p v-if="featured.excerpt" class="line-clamp-3 text-sm leading-relaxed text-slate-500">{{ featured.excerpt }}</p>
              <div class="flex items-center gap-4 pt-1">
                <time class="text-xs text-slate-400">{{ fmtDate(featured.meta.first_published_at) }}</time>
                <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read article →</span>
              </div>
            </div>
          </NuxtLink>

          <!-- Post grid -->
          <div v-if="rest.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="post in rest"
              :key="post.meta.slug"
              :to="`/blog/${post.meta.slug}`"
              class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
            >
              <div class="h-44 overflow-hidden bg-slate-100">
                <img
                  v-if="post.thumbnail"
                  :src="post.thumbnail.url"
                  :alt="post.title"
                  class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div v-else class="flex h-full items-center justify-center">
                  <span class="select-none text-2xl font-extrabold text-slate-200">W</span>
                </div>
              </div>
              <div class="flex flex-1 flex-col space-y-2.5 p-5">
                <div class="flex items-center gap-2.5 text-xs text-slate-500">
                  <span
                    v-if="post.category_name"
                    class="rounded-full px-2.5 py-0.5 font-semibold"
                    :class="catColor(post.category_name)"
                  >{{ post.category_name }}</span>
                  <span v-if="post.reading_time_minutes">{{ post.reading_time_minutes }} min</span>
                </div>
                <h2 class="line-clamp-2 flex-1 text-sm font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ post.title }}</h2>
                <p v-if="post.excerpt" class="line-clamp-2 text-xs leading-relaxed text-slate-500">{{ post.excerpt }}</p>
                <div class="flex items-center justify-between border-t border-slate-100 pt-1.5">
                  <time class="text-xs text-slate-400">{{ fmtDate(post.meta.first_published_at) }}</time>
                  <span class="text-xs text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">Read →</span>
                </div>
              </div>
            </NuxtLink>
          </div>

          <!-- Empty filtered state -->
          <div v-else-if="!featured" class="py-16 text-center text-slate-500">
            No articles in this category yet.
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="mt-12 flex items-center justify-center gap-2">
            <button
              :disabled="page === 1"
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-sm text-slate-500 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
              @click="goPage(page - 1)"
            >←</button>
            <button
              v-for="p in totalPages"
              :key="p"
              class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
              :class="p === page
                ? 'border-brand-600 bg-brand-600 text-white'
                : 'border-slate-200 text-slate-500 hover:border-brand-400 hover:text-brand-600'"
              @click="goPage(p)"
            >{{ p }}</button>
            <button
              :disabled="page === totalPages"
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-sm text-slate-500 transition-colors hover:border-brand-400 hover:text-brand-600 disabled:cursor-not-allowed disabled:opacity-40"
              @click="goPage(page + 1)"
            >→</button>
          </div>
        </template>

      </div>
    </section>

    <!-- ── CTA strip ──────────────────────────────────────────────────────── -->
    <section class="bg-slate-50 py-12 text-center">
      <div class="mx-auto max-w-xl space-y-4 px-4">
        <h2 class="text-xl font-bold text-slate-900">Ready to join?</h2>
        <p class="text-sm text-slate-500">Credential-verified writers. Level-based pay from $18 to $45/page. Bi-weekly payouts.</p>
        <NuxtLink to="/apply" class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white transition-colors hover:bg-brand-700">
          Apply to write →
        </NuxtLink>
      </div>
    </section>

  </div>
</template>
