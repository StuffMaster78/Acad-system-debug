<script setup lang="ts">
import { ArrowRight, Calendar, Clock } from '@lucide/vue'

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
  category: string
  thumbnail: { url: string } | null
  author_name: string
}

const config = useRuntimeConfig()

const { data: posts, pending, error } = await useAsyncData<BlogPost[]>(
  'blog-posts',
  async () => {
    try {
      const res = await $fetch<{ items: BlogPost[] }>(
        `${config.public.apiBase}/api/v1/cms/pages/`,
        { params: { type: 'blog.ArticlePage', fields: 'title,excerpt,reading_time_minutes,category,thumbnail,author_name', order: '-first_published_at', limit: 24 } },
      )
      return res.items ?? []
    } catch {
      return []
    }
  },
)

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

const categories = computed(() => {
  const cats = new Set((posts.value ?? []).map(p => p.category).filter(Boolean))
  return ['All', ...cats]
})
const activeCategory = ref('All')
const filtered = computed(() =>
  activeCategory.value === 'All'
    ? (posts.value ?? [])
    : (posts.value ?? []).filter(p => p.category === activeCategory.value),
)
</script>

<template>
  <div class="pt-16">

    <!-- Hero -->
    <section class="bg-navy-900 py-16 text-center relative overflow-hidden">
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

        <!-- Error state -->
        <div v-if="error" class="text-center py-20 text-graphite text-sm">
          Could not load articles. Please try again later.
        </div>

        <!-- Loading skeleton -->
        <div v-else-if="pending" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="i in 6" :key="i" class="rounded-2xl border border-slate-200 overflow-hidden animate-pulse">
            <div class="h-44 bg-slate-100" />
            <div class="p-5 space-y-3">
              <div class="h-3 bg-slate-100 rounded w-1/3" />
              <div class="h-4 bg-slate-100 rounded w-3/4" />
              <div class="h-3 bg-slate-100 rounded" />
              <div class="h-3 bg-slate-100 rounded w-2/3" />
            </div>
          </div>
        </div>

        <template v-else>
          <!-- Category filter -->
          <div v-if="categories.length > 1" class="flex flex-wrap gap-2 mb-8">
            <button
              v-for="cat in categories" :key="cat"
              class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
              :class="activeCategory === cat ? 'bg-gc-600 border-gc-600 text-white' : 'border-slate-200 text-graphite hover:border-gc-400 hover:text-gc-600'"
              @click="activeCategory = cat"
            >{{ cat }}</button>
          </div>

          <!-- Empty state -->
          <div v-if="!filtered.length" class="text-center py-20 space-y-4">
            <p class="text-graphite text-sm">No articles published yet — check back soon.</p>
            <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-6 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
              Place an order <ArrowRight class="size-4" />
            </a>
          </div>

          <!-- Post grid -->
          <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="post in filtered" :key="post.id"
              :to="`/blog/${post.meta.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-200 bg-white shadow-card hover:shadow-lift hover:-translate-y-0.5 transition-all overflow-hidden"
            >
              <!-- Thumbnail -->
              <div class="h-44 bg-slate-100 overflow-hidden">
                <img
                  v-if="post.thumbnail?.url"
                  :src="post.thumbnail.url"
                  :alt="post.title"
                  class="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div v-else class="h-full flex items-center justify-center">
                  <span class="text-2xl font-extrabold text-slate-200 select-none">G</span>
                </div>
              </div>

              <!-- Meta -->
              <div class="flex flex-col flex-1 p-5 space-y-3">
                <div class="flex items-center gap-3 text-xs text-graphite">
                  <span v-if="post.category" class="rounded-full bg-gc-50 px-2.5 py-0.5 font-semibold text-gc-700">{{ post.category }}</span>
                  <span v-if="post.reading_time_minutes" class="flex items-center gap-1">
                    <Clock class="size-3" /> {{ post.reading_time_minutes }} min read
                  </span>
                </div>
                <h2 class="text-sm font-bold text-ink leading-snug group-hover:text-gc-600 transition-colors line-clamp-2">{{ post.title }}</h2>
                <p v-if="post.excerpt" class="text-xs text-graphite leading-relaxed line-clamp-3 flex-1">{{ post.excerpt }}</p>
                <div class="flex items-center justify-between pt-1 border-t border-slate-100">
                  <div class="flex items-center gap-1.5 text-xs text-graphite">
                    <Calendar class="size-3" />
                    {{ formatDate(post.meta.first_published_at) }}
                  </div>
                  <ArrowRight class="size-3.5 text-gc-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            </NuxtLink>
          </div>
        </template>

      </div>
    </section>

    <!-- CTA -->
    <section class="bg-mist py-12 text-center">
      <div class="mx-auto max-w-xl px-4 space-y-4">
        <h2 class="text-xl font-bold text-ink">Ready to get expert help?</h2>
        <p class="text-sm text-graphite">Human-written papers, grade guaranteed, from $13/page.</p>
        <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
          Place your order <ArrowRight class="size-4" />
        </a>
      </div>
    </section>

  </div>
</template>
