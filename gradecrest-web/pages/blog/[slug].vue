<script setup lang="ts">
import { ArrowLeft, ArrowRight, Calendar, Clock } from '@lucide/vue'
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const app   = useAppUrl()
const route = useRoute()
const slug  = route.params.slug as string
const config = useRuntimeConfig()

interface Block {
  type: string
  value: unknown
}

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
  related_posts: { slug: string; title: string; excerpt: string; thumbnail: { url: string } | null }[]
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
    } catch {
      return null
    }
  },
)

if (article.value) {
  useSeoMeta({
    title:       article.value.meta.seo_title || `${article.value.title} | GradeCrest Blog`,
    description: article.value.meta.search_description || article.value.excerpt,
    ogTitle:     article.value.title,
    ogDescription: article.value.excerpt,
    ogImage:     article.value.thumbnail?.url,
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
        headline: article.value.title,
        description: article.value.excerpt,
        datePublished: article.value.meta.first_published_at,
        author: { '@type': 'Person', name: article.value.author_name || 'GradeCrest Editorial Team' },
        publisher: { '@type': 'Organization', name: 'GradeCrest', url: 'https://gradecrest.com' },
        image: article.value.thumbnail?.url,
      }),
    }],
  })
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <div class="pt-16">

    <!-- 404 state -->
    <div v-if="error || !article" class="min-h-[60vh] flex items-center justify-center">
      <div class="text-center space-y-4 px-4">
        <h1 class="text-2xl font-bold text-ink">Article not found</h1>
        <p class="text-graphite text-sm">This article may have been moved or removed.</p>
        <NuxtLink to="/blog" class="inline-flex items-center gap-2 text-sm font-semibold text-gc-600 hover:text-gc-700 transition-colors">
          <ArrowLeft class="size-4" /> Back to blog
        </NuxtLink>
      </div>
    </div>

    <template v-else>
      <!-- Hero -->
      <section class="bg-navy-900 py-14 relative overflow-hidden">
        <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none" />
        <div class="relative mx-auto max-w-3xl px-4 sm:px-6">
          <NuxtLink to="/blog" class="mb-5 inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors">
            <ArrowLeft class="size-3.5" /> All articles
          </NuxtLink>
          <div class="flex items-center gap-3 mb-4 text-xs text-slate-400">
            <span v-if="article.category_name" class="rounded-full bg-gc-500/20 px-2.5 py-0.5 font-semibold text-gc-300">{{ article.category_name }}</span>
            <span class="flex items-center gap-1"><Clock class="size-3" /> {{ article.reading_time_minutes }} min read</span>
            <span class="flex items-center gap-1"><Calendar class="size-3" /> {{ formatDate(article.meta.first_published_at) }}</span>
          </div>
          <h1 class="text-3xl font-bold text-white sm:text-4xl leading-snug">{{ article.title }}</h1>
          <p v-if="article.excerpt" class="mt-4 text-slate-300 leading-relaxed max-w-2xl">{{ article.excerpt }}</p>
          <p v-if="article.author_name" class="mt-4 text-xs text-slate-400">By {{ article.author_name }}</p>
        </div>
      </section>

      <!-- Thumbnail -->
      <div v-if="article.thumbnail?.url" class="mx-auto max-w-3xl px-4 sm:px-6 -mb-4 mt-8">
        <img :src="article.thumbnail.url" :alt="article.title" class="w-full rounded-2xl object-cover max-h-80" />
      </div>

      <!-- Article body -->
      <section class="bg-white py-12">
        <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <!-- StreamField body rendered via shared BlockRenderer -->
          <div class="prose prose-sm prose-slate max-w-none prose-headings:font-bold prose-headings:text-ink prose-a:text-gc-600 prose-a:no-underline hover:prose-a:underline [&_.prose-content]:mb-4 [&_.prose-content_p]:mb-4 [&_.not-prose]:not-prose">
            <BlockRenderer :blocks="article.body" />
          </div>

          <!-- Author bio -->
          <div v-if="article.author_name" class="mt-12 rounded-2xl border border-slate-200 bg-mist p-5 flex items-start gap-4">
            <div class="flex size-11 shrink-0 items-center justify-center rounded-xl bg-gc-50 text-sm font-bold text-gc-700">
              {{ article.author_name.charAt(0) }}
            </div>
            <div>
              <p class="text-sm font-semibold text-ink">{{ article.author_name }}</p>
              <p v-if="article.author_bio" class="mt-1 text-xs text-graphite leading-relaxed">{{ article.author_bio }}</p>
            </div>
          </div>

          <!-- End-of-article CTA -->
          <div class="mt-10 rounded-2xl bg-navy-900 p-7 text-center space-y-4 relative overflow-hidden">
            <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none opacity-50" />
            <div class="relative">
              <p class="text-white font-bold text-lg">Need expert academic writing help?</p>
              <p class="text-slate-300 text-sm mt-1">Human-written, grade guaranteed, from $13/page.</p>
              <a :href="app.order" class="mt-4 inline-flex items-center gap-2 rounded-xl bg-gc-600 px-7 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
                Place your order <ArrowRight class="size-4" />
              </a>
            </div>
          </div>

        </div>
      </section>

      <!-- Related posts -->
      <section v-if="article.related_posts?.length" class="bg-mist py-12">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 class="text-lg font-bold text-ink mb-6">Related articles</h2>
          <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="rel in article.related_posts" :key="rel.slug"
              :to="`/blog/${rel.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-200 bg-white shadow-card hover:shadow-lift transition-all overflow-hidden"
            >
              <div class="h-36 bg-slate-100 overflow-hidden">
                <img v-if="rel.thumbnail?.url" :src="rel.thumbnail.url" :alt="rel.title" class="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                <div v-else class="h-full flex items-center justify-center">
                  <span class="text-xl font-extrabold text-slate-200 select-none">G</span>
                </div>
              </div>
              <div class="p-4 flex-1 flex flex-col">
                <h3 class="text-sm font-semibold text-ink group-hover:text-gc-600 transition-colors line-clamp-2 flex-1">{{ rel.title }}</h3>
                <div class="mt-3 flex items-center justify-between">
                  <span class="text-xs text-graphite line-clamp-1 flex-1 pr-2">{{ rel.excerpt }}</span>
                  <ArrowRight class="size-3.5 text-gc-600 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>

    </template>
  </div>
</template>
