<script setup lang="ts">
const { getAll } = useBlog()
const posts = getAll()

const POSTS_PER_PAGE = 6

const categories = [...new Set(posts.map(p => p.category))]
const activeCategory = ref<string | null>(null)
const currentPage = ref(1)

const filtered = computed(() =>
  activeCategory.value ? posts.filter(p => p.category === activeCategory.value) : posts
)

const totalPages = computed(() => Math.ceil(filtered.value.length / POSTS_PER_PAGE))

const paginated = computed(() => {
  const start = (currentPage.value - 1) * POSTS_PER_PAGE
  return filtered.value.slice(start, start + POSTS_PER_PAGE)
})

function setCategory(cat: string | null) {
  activeCategory.value = cat
  currentPage.value = 1
}

function goToPage(p: number) {
  currentPage.value = p
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

useSeoMeta({
  title: 'Nursing Writing Blog — Care Plans, SOAP Notes, Essays & Guides | NurseMyGrade',
  description: 'Practical guides for nursing students — how to write care plans, SOAP notes, capstone projects, nursing essays, and more from qualified nursing writers.',
})
</script>

<template>
  <div>
    <!-- Hero -->
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-16 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Nursing Writing Blog</h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-brand-100">
          Practical guides for nursing students — written by qualified nurses. Care plans, SOAP notes, APA 7th, capstone strategies, and more.
        </p>
      </div>
    </section>

    <!-- Content + Sidebar -->
    <div class="section">
      <div class="grid gap-10 lg:grid-cols-[1fr_300px]">

        <!-- Left: posts -->
        <div>
          <!-- Category filter -->
          <div class="mb-8 flex flex-wrap gap-2">
            <button
              class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
              :class="activeCategory === null ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-brand-50 hover:text-brand-700'"
              @click="setCategory(null)"
            >
              All <span class="ml-1 text-xs opacity-60">{{ posts.length }}</span>
            </button>
            <button
              v-for="cat in categories"
              :key="cat"
              class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
              :class="activeCategory === cat ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-brand-50 hover:text-brand-700'"
              @click="setCategory(cat)"
            >
              {{ cat }}
              <span class="ml-1 text-xs opacity-60">{{ posts.filter(p => p.category === cat).length }}</span>
            </button>
          </div>

          <!-- Post grid -->
          <div class="grid gap-8 sm:grid-cols-2">
            <NuxtLink
              v-for="post in paginated"
              :key="post.slug"
              :href="`/blog/${post.slug}`"
              class="card group flex flex-col transition-shadow hover:shadow-md"
            >
              <div class="mb-3 flex items-center gap-2">
                <span class="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                  {{ post.category }}
                </span>
                <span class="text-xs text-slate-400">{{ post.readTime }}</span>
              </div>

              <h2 class="flex-1 font-serif text-lg font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">
                {{ post.title }}
              </h2>
              <p class="mt-3 line-clamp-3 text-sm text-slate-500 leading-relaxed">{{ post.excerpt }}</p>

              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
                <div class="flex items-center gap-2">
                  <!-- Author avatar initial -->
                  <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 text-[10px] font-bold text-brand-700">
                    {{ post.author?.name?.[0] ?? '?' }}
                  </div>
                  <span class="text-xs text-slate-500">{{ post.author?.name?.split(' ').slice(0, 2).join(' ') }}</span>
                </div>
                <span class="text-xs font-medium text-brand-600 group-hover:underline">Read →</span>
              </div>
            </NuxtLink>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="mt-10 flex items-center justify-center gap-2">
            <button
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:border-brand-300 hover:text-brand-600 disabled:opacity-30"
              :disabled="currentPage === 1"
              aria-label="Previous page"
              @click="goToPage(currentPage - 1)"
            >
              <Icon name="chevron-right" class="h-4 w-4 rotate-180" />
            </button>

            <template v-for="p in totalPages" :key="p">
              <!-- Show first, last, current ±1, and ellipsis -->
              <template v-if="p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1">
                <button
                  class="flex h-9 w-9 items-center justify-center rounded-lg border text-sm font-medium transition-colors"
                  :class="p === currentPage
                    ? 'border-brand-600 bg-brand-600 text-white'
                    : 'border-slate-200 text-slate-600 hover:border-brand-300 hover:text-brand-600'"
                  @click="goToPage(p)"
                >
                  {{ p }}
                </button>
              </template>
              <span
                v-else-if="p === 2 && currentPage > 3 || p === totalPages - 1 && currentPage < totalPages - 2"
                class="flex h-9 w-9 items-center justify-center text-slate-400 text-sm"
              >…</span>
            </template>

            <button
              class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition-colors hover:border-brand-300 hover:text-brand-600 disabled:opacity-30"
              :disabled="currentPage === totalPages"
              aria-label="Next page"
              @click="goToPage(currentPage + 1)"
            >
              <Icon name="chevron-right" class="h-4 w-4" />
            </button>
          </div>

          <!-- Post count -->
          <p class="mt-4 text-center text-xs text-slate-400">
            Showing {{ (currentPage - 1) * POSTS_PER_PAGE + 1 }}–{{ Math.min(currentPage * POSTS_PER_PAGE, filtered.length) }} of {{ filtered.length }} articles
          </p>
        </div>

        <!-- Right: sticky sidebar -->
        <div class="lg:sticky lg:top-24 lg:self-start">
          <BlogSidebar />
        </div>

      </div>
    </div>
  </div>
</template>
