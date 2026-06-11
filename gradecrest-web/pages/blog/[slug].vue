<script setup lang="ts">
import { ArrowRight, Calendar, Clock, Copy, Check, Share2 } from '@lucide/vue'
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const app    = useAppUrl()
const route  = useRoute()
const slug   = route.params.slug as string
const config = useRuntimeConfig()

interface Block { type: string; value: unknown }

interface ArticleDetail {
  id: number
  meta: { slug: string; first_published_at: string; seo_title: string; search_description: string }
  title: string
  excerpt: string
  body: Block[]
  reading_time_minutes: number
  category_name: string
  thumbnail: { url: string } | null
  author_name: string
  author_bio: string
  primary_author?: { name: string; credentials?: string; bio?: string } | null
}

const { data: article, error } = await useAsyncData<ArticleDetail | null>(
  `blog-${slug}`,
  async () => {
    try {
      const res = await $fetch<{ items: ArticleDetail[] }>(
        `${config.public.apiBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// Connected articles — same category, exclude current
const { data: connectedPosts } = await useAsyncData<ArticleDetail[]>(
  `connected-${slug}`,
  async () => {
    try {
      const res = await $fetch<{ items: ArticleDetail[] }>(
        `${config.public.apiBase}/api/v2/pages/`,
        { params: {
          type: 'cms_blog.BlogPostPage',
          fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail,author_name',
          order: '-first_published_at',
          limit: 4,
        }},
      )
      return (res.items ?? []).filter(p => p.meta?.slug !== slug).slice(0, 3)
    } catch { return [] }
  },
)

// SEO — meta description stays in <head> only, never displayed
if (article.value) {
  useSeoMeta({
    title:          article.value.meta.seo_title || `${article.value.title} | GradeCrest Blog`,
    description:    article.value.meta.search_description || article.value.excerpt,
    ogTitle:        article.value.title,
    ogDescription:  article.value.excerpt,
    ogImage:        article.value.thumbnail?.url,
  })
  useSeoBase(`https://gradecrest.com/blog/${slug}`)
  useBreadcrumbs([
    { name: 'Home', url: 'https://gradecrest.com/' },
    { name: 'Blog', url: 'https://gradecrest.com/blog' },
    { name: article.value.title, url: `https://gradecrest.com/blog/${slug}` },
  ])
  useHead({
    script: [{
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline:      article.value.title,
        description:   article.value.excerpt,
        datePublished: article.value.meta.first_published_at,
        author: { '@type': 'Person', name: article.value.author_name || 'GradeCrest Editorial Team' },
        publisher: { '@type': 'Organization', name: 'GradeCrest', url: 'https://gradecrest.com' },
        image: article.value.thumbnail?.url,
      }),
    }],
  })
}

// Table of contents
const toc = computed(() => extractToc(article.value?.body ?? []))
const tocOpen = ref(true)

// Active TOC item via IntersectionObserver
const activeTocId = ref('')
onMounted(() => {
  if (!toc.value.length) return
  const observer = new IntersectionObserver(
    entries => {
      for (const e of entries) {
        if (e.isIntersecting) { activeTocId.value = e.target.id; break }
      }
    },
    { rootMargin: '-80px 0px -60% 0px' },
  )
  toc.value.forEach(item => {
    const el = document.getElementById(item.id)
    if (el) observer.observe(el)
  })
  onUnmounted(() => observer.disconnect())
})

// Reading progress
const readProgress = ref(0)
onMounted(() => {
  const update = () => {
    const el = document.getElementById('article-body')
    if (!el) return
    const { top, height } = el.getBoundingClientRect()
    const scrolled = Math.max(0, -top)
    readProgress.value = Math.min(100, Math.round((scrolled / (height - window.innerHeight)) * 100))
  }
  window.addEventListener('scroll', update, { passive: true })
  onUnmounted(() => window.removeEventListener('scroll', update))
})

// Sharing
const pageUrl = computed(() => `https://gradecrest.com/blog/${slug}`)
const copied = ref(false)
async function copyLink() {
  await navigator.clipboard.writeText(pageUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

// Utils
function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}

const authorInitial = computed(() =>
  (article.value?.author_name || article.value?.primary_author?.name || 'G').charAt(0).toUpperCase()
)
const authorName = computed(() =>
  article.value?.author_name || article.value?.primary_author?.name || 'GradeCrest Editorial Team'
)
const authorCredentials = computed(() =>
  article.value?.primary_author?.credentials || ''
)
const authorBio = computed(() =>
  article.value?.author_bio || article.value?.primary_author?.bio || ''
)
</script>

<template>
  <div class="pt-16">

    <!-- Reading progress bar -->
    <div
      class="fixed top-16 left-0 z-50 h-0.5 bg-gc-500 transition-all duration-100"
      :style="{ width: `${readProgress}%` }"
    />

    <!-- 404 -->
    <div v-if="error || !article" class="min-h-[60vh] flex items-center justify-center">
      <div class="text-center space-y-4 px-4">
        <h1 class="text-2xl font-bold text-ink">Article not found</h1>
        <p class="text-sm text-graphite">This article may have been moved or removed.</p>
        <NuxtLink to="/blog" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700">
          ← Back to blog
        </NuxtLink>
      </div>
    </div>

    <template v-else>

      <!-- Hero -->
      <section class="bg-navy-900 pb-10 pt-10 relative overflow-hidden">
        <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
        <div class="relative mx-auto max-w-4xl px-4 sm:px-6">

          <!-- Breadcrumbs with / separator -->
          <nav class="mb-5 flex items-center gap-1.5 text-xs text-slate-500 flex-wrap">
            <NuxtLink to="/" class="hover:text-slate-300 transition-colors">Home</NuxtLink>
            <span class="text-slate-600">/</span>
            <NuxtLink to="/blog" class="hover:text-slate-300 transition-colors">Blog</NuxtLink>
            <span class="text-slate-600">/</span>
            <span class="text-slate-400 line-clamp-1">{{ article.title }}</span>
          </nav>

          <!-- Category + meta -->
          <div class="flex flex-wrap items-center gap-3 mb-4 text-xs text-slate-400">
            <span
              v-if="article.category_name"
              class="rounded-full bg-gc-500/20 px-3 py-1 font-semibold text-gc-300 text-xs"
            >{{ article.category_name }}</span>
            <span class="flex items-center gap-1"><Clock class="size-3" /> {{ article.reading_time_minutes || 1 }} min read</span>
            <span class="flex items-center gap-1"><Calendar class="size-3" /> {{ formatDate(article.meta.first_published_at) }}</span>
          </div>

          <!-- Title -->
          <h1 class="text-3xl font-bold text-white sm:text-4xl leading-snug max-w-3xl">{{ article.title }}</h1>

          <!-- Author row -->
          <div class="mt-5 flex items-center gap-3">
            <div class="flex size-9 shrink-0 items-center justify-center rounded-full bg-gc-600 text-sm font-bold text-white">
              {{ authorInitial }}
            </div>
            <div>
              <p class="text-sm font-semibold text-white leading-none">{{ authorName }}</p>
              <p v-if="authorCredentials" class="text-xs text-slate-400 mt-0.5">{{ authorCredentials }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Featured image -->
      <div v-if="article.thumbnail?.url" class="bg-navy-900">
        <div class="mx-auto max-w-4xl px-4 sm:px-6 pb-0">
          <img
            :src="article.thumbnail.url"
            :alt="article.title"
            class="w-full rounded-t-2xl object-cover max-h-96"
          />
        </div>
      </div>

      <!-- Body -->
      <section class="bg-white py-10" id="article-body">
        <div class="mx-auto max-w-4xl px-4 sm:px-6">
          <div class="lg:grid lg:grid-cols-[1fr_260px] lg:gap-12 lg:items-start">

            <!-- Main content -->
            <div class="min-w-0">

              <!-- TOC -->
              <div v-if="toc.length >= 3" class="mb-8 rounded-2xl border border-slate-200 bg-slate-50 overflow-hidden">
                <button
                  class="w-full flex items-center justify-between px-5 py-3.5 text-sm font-semibold text-ink hover:bg-slate-100 transition-colors"
                  @click="tocOpen = !tocOpen"
                >
                  <span>Table of Contents</span>
                  <span class="text-graphite text-xs transition-transform duration-200" :class="tocOpen ? 'rotate-180' : ''">▾</span>
                </button>
                <nav v-show="tocOpen" class="px-5 pb-4">
                  <ol class="space-y-1.5 text-sm list-none">
                    <li
                      v-for="(item, i) in toc" :key="item.id"
                      :class="item.level === 'h3' ? 'pl-4' : item.level === 'h4' ? 'pl-8' : ''"
                    >
                      <a
                        :href="`#${item.id}`"
                        class="flex items-baseline gap-2 group transition-colors"
                        :class="activeTocId === item.id ? 'text-gc-600 font-semibold' : 'text-graphite hover:text-gc-600'"
                      >
                        <span class="shrink-0 text-xs text-slate-400 group-hover:text-gc-400 tabular-nums w-4">{{ i + 1 }}.</span>
                        <span class="leading-snug">{{ item.text }}</span>
                      </a>
                    </li>
                  </ol>
                </nav>
              </div>

              <!-- Article body blocks -->
              <div class="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-ink prose-headings:scroll-mt-24 prose-a:text-gc-600 prose-a:no-underline hover:prose-a:underline prose-p:text-graphite prose-p:leading-relaxed prose-li:text-graphite prose-strong:text-ink">
                <BlockRenderer :blocks="article.body" />
              </div>

              <!-- Social sharing -->
              <div class="mt-10 pt-8 border-t border-slate-100 flex flex-wrap items-center gap-3">
                <span class="text-xs font-semibold text-graphite uppercase tracking-widest mr-1">Share</span>
                <a
                  :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(article.title)}&url=${encodeURIComponent(pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-2 rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-medium text-graphite hover:border-slate-300 hover:text-ink transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                  X / Twitter
                </a>
                <a
                  :href="`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-2 rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-medium text-graphite hover:border-blue-300 hover:text-blue-700 transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                  LinkedIn
                </a>
                <a
                  :href="`https://wa.me/?text=${encodeURIComponent(article.title + ' ' + pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-2 rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-medium text-graphite hover:border-green-300 hover:text-green-700 transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                  WhatsApp
                </a>
                <button
                  class="flex items-center gap-2 rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-medium text-graphite hover:border-slate-300 hover:text-ink transition-colors"
                  @click="copyLink"
                >
                  <Check v-if="copied" class="size-3.5 text-green-600" />
                  <Copy v-else class="size-3.5" />
                  {{ copied ? 'Copied!' : 'Copy link' }}
                </button>
              </div>

              <!-- Author card -->
              <div v-if="authorName" class="mt-8 rounded-2xl border border-slate-200 bg-mist p-5 flex items-start gap-4">
                <div class="flex size-12 shrink-0 items-center justify-center rounded-full bg-gc-600 text-base font-bold text-white">
                  {{ authorInitial }}
                </div>
                <div>
                  <p class="text-sm font-semibold text-ink">{{ authorName }}</p>
                  <p v-if="authorCredentials" class="text-xs text-gc-600 font-medium mt-0.5">{{ authorCredentials }}</p>
                  <p v-if="authorBio" class="mt-2 text-xs text-graphite leading-relaxed">{{ authorBio }}</p>
                </div>
              </div>

              <!-- End-of-article CTA -->
              <div class="mt-8 rounded-2xl bg-navy-900 p-7 text-center relative overflow-hidden">
                <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none opacity-50" />
                <div class="relative space-y-3">
                  <p class="text-white font-bold text-lg">Need expert academic writing help?</p>
                  <p class="text-slate-300 text-sm">Human-written, grade guaranteed, from $13/page.</p>
                  <a :href="app.order" class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-7 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
                    Place your order <ArrowRight class="size-4" />
                  </a>
                </div>
              </div>

            </div>

            <!-- Sticky sidebar -->
            <aside class="hidden lg:block">
              <div class="sticky top-24 space-y-5">

                <!-- Sidebar TOC -->
                <div v-if="toc.length >= 2" class="rounded-2xl border border-slate-200 bg-white p-5">
                  <p class="text-xs font-bold uppercase tracking-widest text-graphite mb-3">In this article</p>
                  <nav>
                    <ol class="space-y-2 text-sm list-none">
                      <li
                        v-for="item in toc" :key="item.id"
                        :class="item.level === 'h3' ? 'pl-3' : item.level === 'h4' ? 'pl-6' : ''"
                      >
                        <a
                          :href="`#${item.id}`"
                          class="block leading-snug transition-colors py-0.5"
                          :class="activeTocId === item.id
                            ? 'text-gc-600 font-semibold'
                            : 'text-graphite hover:text-gc-600'"
                        >{{ item.text }}</a>
                      </li>
                    </ol>
                  </nav>
                </div>

                <!-- Sidebar Order CTA -->
                <div class="rounded-2xl bg-gc-600 p-5 text-white text-center space-y-3">
                  <p class="font-bold text-sm leading-snug">Get your paper written by an expert</p>
                  <p class="text-gc-100 text-xs">From $13/page · Grade or money back</p>
                  <a
                    :href="app.order"
                    class="block rounded-xl bg-white text-gc-600 font-bold text-sm py-2.5 hover:bg-gc-50 transition-colors"
                  >
                    Order now
                  </a>
                </div>

              </div>
            </aside>

          </div>
        </div>
      </section>

      <!-- Connected articles -->
      <section v-if="connectedPosts?.length" class="bg-slate-50 border-t border-slate-100 py-12">
        <div class="mx-auto max-w-4xl px-4 sm:px-6">
          <h2 class="text-lg font-bold text-ink mb-6">You might also like</h2>
          <div class="grid gap-5 sm:grid-cols-3">
            <NuxtLink
              v-for="post in connectedPosts" :key="post.meta?.slug"
              :to="`/blog/${post.meta?.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-200 bg-white shadow-card hover:shadow-lift hover:-translate-y-0.5 transition-all overflow-hidden"
            >
              <div class="h-36 bg-slate-100 overflow-hidden">
                <img
                  v-if="post.thumbnail?.url"
                  :src="post.thumbnail.url"
                  :alt="post.title"
                  class="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div v-else class="h-full flex items-center justify-center">
                  <span class="text-xl font-extrabold text-slate-200 select-none">G</span>
                </div>
              </div>
              <div class="p-4 flex-1 flex flex-col gap-2">
                <span v-if="post.category_name" class="text-xs font-semibold text-gc-600">{{ post.category_name }}</span>
                <h3 class="text-sm font-semibold text-ink group-hover:text-gc-600 transition-colors line-clamp-2 flex-1 leading-snug">{{ post.title }}</h3>
                <div class="flex items-center gap-2 text-xs text-graphite pt-1">
                  <span v-if="post.reading_time_minutes">{{ post.reading_time_minutes }} min</span>
                  <span class="text-gc-600 font-medium group-hover:underline">Read →</span>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>

    </template>
  </div>
</template>
