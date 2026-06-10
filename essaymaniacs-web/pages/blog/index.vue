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

const featured = computed(() => (currentPage.value === 1 ? filtered.value[0] ?? null : null))

const rest = computed(() => {
  const skip = currentPage.value === 1 ? 1 : 0
  const start = skip + (currentPage.value - 1) * POSTS_PER_PAGE
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

// Category → visual cover: gradient + icon
const CAT_COVER: Record<string, { bg: string; icon: string; accent: string }> = {
  'Essays':         { bg: 'from-brand-800 to-brand-600',  icon: 'pen-line',       accent: 'bg-brand-500' },
  'Research Papers':{ bg: 'from-blue-900 to-blue-600',    icon: 'file-text',      accent: 'bg-blue-500' },
  'Dissertations':  { bg: 'from-slate-800 to-slate-600',  icon: 'graduation-cap', accent: 'bg-slate-500' },
  'Academic Tips':  { bg: 'from-emerald-800 to-emerald-600', icon: 'book-open',   accent: 'bg-emerald-500' },
}
const DEFAULT_COVER = { bg: 'from-brand-800 to-brand-600', icon: 'pen-line', accent: 'bg-brand-500' }

function cover(category: string) {
  return CAT_COVER[category] ?? DEFAULT_COVER
}

const fmtDate = (d: string) =>
  new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

useSeoMeta({
  title: 'Academic Writing Blog | EssayManiacs',
  description: 'Practical guides on essays, research papers, dissertations, and every academic writing challenge — by subject specialists.',
})
useHead({ link: [{ rel: 'canonical', href: 'https://essaymaniacs.com/blog' }] })
</script>

<template>
  <div class="bg-white">

    <!-- ── Page header ─────────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 bg-white px-4 pb-0 pt-10 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-600">EssayManiacs Blog</p>
            <h1 class="font-serif text-4xl font-bold text-slate-900 sm:text-5xl">Writing guides<br class="hidden sm:block" /> that actually help</h1>
            <p class="mt-3 max-w-xl text-base text-slate-600">
              Practical, specific advice on essays, dissertations, research papers, and every assignment in between.
            </p>
          </div>
          <NuxtLink to="/order" class="btn-primary shrink-0">Get your essay written →</NuxtLink>
        </div>

        <!-- Category pills -->
        <div class="mt-8 flex gap-1 overflow-x-auto pb-0" style="scrollbar-width: none;">
          <button
            class="shrink-0 border-b-2 px-4 py-3 text-sm font-semibold transition-colors"
            :class="activeCategory === null ? 'border-brand-600 text-brand-700' : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="setCategory(null)"
          >
            All <span class="ml-1 text-xs opacity-60">{{ posts.length }}</span>
          </button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="shrink-0 border-b-2 px-4 py-3 text-sm font-semibold transition-colors"
            :class="activeCategory === cat ? 'border-brand-600 text-brand-700' : 'border-transparent text-slate-500 hover:text-slate-900'"
            @click="setCategory(cat)"
          >
            {{ cat }} <span class="ml-1 text-xs opacity-60">{{ posts.filter(p => p.category === cat).length }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">

      <!-- ── Featured article (image-left hero card) ──────────────────── -->
      <NuxtLink
        v-if="featured"
        :href="`/blog/${featured.slug}`"
        class="group mb-12 grid overflow-hidden rounded-3xl border border-slate-200 shadow-sm transition-all hover:shadow-lg sm:grid-cols-[380px_1fr]"
      >
        <!-- Cover image area -->
        <div
          class="relative flex min-h-[220px] items-center justify-center bg-gradient-to-br sm:min-h-[280px]"
          :class="cover(featured.category).bg"
        >
          <!-- Decorative grid pattern -->
          <div class="absolute inset-0 opacity-10"
            style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 24px 24px;" />
          <!-- Icon -->
          <div class="relative flex h-20 w-20 items-center justify-center rounded-2xl bg-white/20 backdrop-blur-sm ring-1 ring-white/30">
            <Icon :name="cover(featured.category).icon" class="h-10 w-10 text-white" />
          </div>
          <!-- Category chip -->
          <div class="absolute bottom-4 left-4">
            <span class="rounded-full bg-white/20 px-3 py-1 text-xs font-bold text-white backdrop-blur-sm ring-1 ring-white/30">
              {{ featured.category }}
            </span>
          </div>
          <!-- "Featured" label -->
          <div class="absolute right-4 top-4">
            <span class="rounded-full bg-white/20 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white backdrop-blur-sm">
              Featured
            </span>
          </div>
        </div>

        <!-- Content -->
        <div class="flex flex-col justify-between bg-white p-7 sm:p-8">
          <div>
            <p class="mb-3 flex items-center gap-3 text-xs text-slate-400">
              <time>{{ fmtDate(featured.date) }}</time>
              <span>·</span>
              <span>{{ featured.readTime }}</span>
            </p>
            <h2 class="font-serif text-2xl font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 sm:text-3xl">
              {{ featured.title }}
            </h2>
            <p class="mt-3 text-base leading-relaxed text-slate-600 line-clamp-3">{{ featured.excerpt }}</p>
          </div>
          <div class="mt-6 flex items-center justify-between border-t border-slate-100 pt-5">
            <div v-if="featured.author" class="flex items-center gap-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
                {{ featured.author.name[0] }}
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-800">{{ featured.author.name }}</p>
                <p class="text-xs text-slate-400">{{ featured.author.credentials }}</p>
              </div>
            </div>
            <span class="inline-flex items-center gap-2 rounded-lg bg-brand-700 px-5 py-2.5 text-sm font-bold text-white transition-colors group-hover:bg-brand-800">
              Read article
              <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
            </span>
          </div>
        </div>
      </NuxtLink>

      <!-- ── Article grid — image-first cards ─────────────────────────── -->
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="post in rest"
          :key="post.slug"
          :href="`/blog/${post.slug}`"
          class="group flex flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white transition-all hover:shadow-md"
        >
          <!-- Cover image -->
          <div
            class="relative flex h-44 items-center justify-center bg-gradient-to-br"
            :class="cover(post.category).bg"
          >
            <div class="absolute inset-0 opacity-10"
              style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 20px 20px;" />
            <div class="relative flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm ring-1 ring-white/30">
              <Icon :name="cover(post.category).icon" class="h-7 w-7 text-white" />
            </div>
            <div class="absolute bottom-3 left-3">
              <span class="rounded-full bg-white/20 px-2.5 py-0.5 text-[10px] font-bold text-white backdrop-blur-sm ring-1 ring-white/20">
                {{ post.category }}
              </span>
            </div>
          </div>

          <!-- Content -->
          <div class="flex flex-1 flex-col p-5">
            <p class="mb-2 text-xs text-slate-400">{{ fmtDate(post.date) }} · {{ post.readTime }}</p>
            <h2 class="flex-1 font-serif text-base font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">
              {{ post.title }}
            </h2>
            <p class="mt-2 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ post.excerpt }}</p>

            <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
              <div v-if="post.author" class="flex items-center gap-2">
                <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-[10px] font-bold text-brand-700">
                  {{ post.author.name[0] }}
                </div>
                <span class="text-xs font-medium text-slate-600">{{ post.author.name.split(' ')[0] }}</span>
              </div>
              <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
            </div>
          </div>
        </NuxtLink>

        <!-- Inline CTA card — appears as a natural 4th/7th/10th card -->
        <div
          v-if="rest.length >= 5"
          class="flex flex-col items-center justify-center overflow-hidden rounded-3xl bg-brand-700 p-7 text-center"
        >
          <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15">
            <Icon name="pen-line" class="h-7 w-7 text-white" />
          </div>
          <p class="font-serif text-lg font-bold text-white">Need an essay written?</p>
          <p class="mt-2 text-sm text-brand-200">Subject specialists ready now · From $10/page</p>
          <NuxtLink to="/order" class="mt-5 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50">
            Place my order →
          </NuxtLink>
        </div>
      </div>

      <!-- ── Pagination ────────────────────────────────────────────────── -->
      <div v-if="totalPages > 1" class="mt-12 flex items-center justify-center gap-2">
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
            :class="p === currentPage ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-200 text-slate-600 hover:border-brand-300'"
            @click="goToPage(p)"
          >{{ p }}</button>
          <span v-else-if="p === 2 && currentPage > 3 || p === totalPages - 1 && currentPage < totalPages - 2" class="text-slate-400 text-sm">…</span>
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
