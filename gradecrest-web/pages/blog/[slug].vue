<script setup lang="ts">
import { ArrowRight, Calendar, Clock, Check, Printer, Tag } from '@lucide/vue'
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const app    = useAppUrl()
const route  = useRoute()

const gcInlineCta = `
<div class="not-prose my-10 border-y border-slate-200 py-8">
  <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">GradeCrest</p>
      <p class="text-[1.05rem] font-bold leading-snug text-slate-900">Deadline coming up? Get a subject-specialist writer on it — properly cited, from scratch, from $13/page.</p>
      <div class="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-500">
        <span>✓ Grade or money back</span>
        <span>✓ Zero AI — human-written</span>
        <span>✓ From $13/page · Unlimited revisions</span>
      </div>
    </div>
    <a href="/order" class="mt-1 shrink-0 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-slate-700 whitespace-nowrap">
      Place my order
      <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
    </a>
  </div>
</div>`
const slug   = route.params.slug as string
const config = useRuntimeConfig()
const apiBase     = config.public.apiBase || ''
const wagtailBase = `${apiBase}/wagtail`
const ssrHeaders  = import.meta.server ? { Host: config.siteHostname as string || 'gradecrest.com' } : undefined

interface Block { type: string; value: unknown }

interface ArticleDetail {
  id: number
  page_content_type_id: number
  meta: {
    slug: string
    first_published_at: string
    seo_title: string
    search_description: string
  }
  title: string
  excerpt: string
  body: Block[]
  reading_time_minutes: number
  word_count: number
  category_name: string
  tag_names: string[]
  thumbnail: { url: string } | null
  author_name: string
  author_credentials: string
  author_bio: string
  canonical_published_at: string | null
  last_substantive_update: string | null
  reviewer?: { name: string; credentials?: string } | null
  views_count?: number
  likes_count?: number
}

const { data: article, error } = await useAsyncData<ArticleDetail | null>(
  `blog-${slug}`,
  async () => {
    try {
      const res = await $fetch<{ items: ArticleDetail[] }>(
        `${wagtailBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// Static fallback — shown when CMS is unreachable in dev
const { getBySlug } = useBlog()
const staticPost = article.value ? null : getBySlug(slug)

// Connected articles
const { data: connectedPosts } = await useAsyncData<ArticleDetail[]>(
  `connected-${slug}`,
  async () => {
    try {
      const res = await $fetch<{ items: ArticleDetail[] }>(
        `${wagtailBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail,author_name', order: '-first_published_at', limit: 4 }, headers: ssrHeaders },
      )
      return (res.items ?? []).filter(p => p.meta?.slug !== slug).slice(0, 3)
    } catch { return [] }
  },
)

// SEO — search_description goes to <head> only, never displayed
if (article.value) {
  useSeoMeta({
    title:         article.value.meta.seo_title || `${article.value.title} | GradeCrest Blog`,
    description:   article.value.meta.search_description || article.value.excerpt,
    ogTitle:       article.value.title,
    ogDescription: article.value.excerpt,
    ogImage:       article.value.thumbnail?.url,
    ogType:        'article',
    ogImageWidth:  1200,
    ogImageHeight: 630,
    twitterCard:   'summary_large_image',
  })
  useSeoBase(`https://gradecrest.com/blog/${slug}`)
  useBreadcrumbs([
    { name: 'Home', url: 'https://gradecrest.com/' },
    { name: 'Blog', url: 'https://gradecrest.com/blog' },
    { name: article.value.title, url: `https://gradecrest.com/blog/${slug}` },
  ])

  const gcFaqBlocks = (article.value.body ?? []).filter(b => b.type === 'faq') as Array<{ type: string; value: { question: string; answer: string } }>

  const gcLdScripts: { type: string; innerHTML: string }[] = [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline:      article.value.title,
      description:   article.value.excerpt,
      datePublished: article.value.canonical_published_at || article.value.meta.first_published_at,
      ...(article.value.last_substantive_update ? { dateModified: article.value.last_substantive_update } : {}),
      author: { '@type': 'Person', name: article.value.author_name || 'GradeCrest Editorial Team' },
      publisher: { '@type': 'Organization', name: 'GradeCrest', url: 'https://gradecrest.com' },
      image: article.value.thumbnail?.url,
      wordCount: article.value.word_count,
      speakable: {
        '@type': 'SpeakableSpecification',
        cssSelector: ['.post-excerpt', '.key-takeaways', 'h1'],
      },
    }),
  }]

  if (gcFaqBlocks.length >= 2) {
    gcLdScripts.push({
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: gcFaqBlocks.map(b => ({
          '@type': 'Question',
          name: b.value.question,
          acceptedAnswer: { '@type': 'Answer', text: b.value.answer },
        })),
      }),
    })
  }

  useHead({ script: gcLdScripts })
}

// TOC — prefer structured heading blocks; fall back to h2/h3 in paragraph HTML
const toc = computed(() => {
  const fromBlocks = extractToc(article.value?.body ?? [])
  if (fromBlocks.length >= 3) return fromBlocks
  const items: { id: string; text: string; level: string }[] = []
  for (const block of (article.value?.body ?? [])) {
    if (block.type !== 'paragraph' || typeof block.value !== 'string') continue
    for (const m of block.value.matchAll(/<h([23])[^>]*>([\s\S]*?)<\/h[23]>/gi)) {
      const text = m[2].replace(/<[^>]+>/g, '').trim()
      if (text) items.push({ id: slugifyHeading(text), text, level: `h${m[1]}` })
    }
  }
  return items
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

// Back-to-top
const showBackToTop = ref(false)
onMounted(() => {
  const check = () => { showBackToTop.value = window.scrollY > 600 }
  window.addEventListener('scroll', check, { passive: true })
  onUnmounted(() => window.removeEventListener('scroll', check))
})
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

// ── Engagement: view tracking + star rating feedback ─────────────────────
const viewsDisplay = ref(article.value?.views_count ?? 0)

onMounted(async () => {
  const a = article.value
  if (!a?.id || !a.page_content_type_id) return
  const base = config.public.apiBase || ''
  if (!base) return
  try {
    await $fetch(`${base}/cms-api/engagement/track-view/`, {
      method: 'POST',
      body: { content_type_id: a.page_content_type_id, object_id: a.id },
    })
    viewsDisplay.value = (a.views_count ?? 0) + 1
  } catch { /* non-critical */ }
})

// Star rating feedback
const hoverRating    = ref(0)
const selectedRating = ref(0)
const feedbackState  = ref<'idle' | 'rating' | 'done'>('idle')
const selectedTags   = ref<Set<string>>(new Set())
const feedbackComment = ref('')
const feedbackTags   = ['Very helpful', 'Easy to understand', 'Well-structured', 'Needs examples', 'Missing info', 'Too long']

function selectRating(star: number) {
  selectedRating.value = star
  feedbackState.value  = 'rating'
}
function toggleTag(tag: string) {
  const s = new Set(selectedTags.value)
  s.has(tag) ? s.delete(tag) : s.add(tag)
  selectedTags.value = s
}
async function submitFeedback() {
  feedbackState.value = 'done'
  const a = article.value
  if (!a?.id || !a.page_content_type_id) return
  const base = config.public.apiBase || ''
  if (!base) return
  try {
    await $fetch(`${base}/cms-api/engagement/react/`, {
      method: 'POST',
      body: {
        content_type_id: a.page_content_type_id,
        object_id: a.id,
        reaction_type: selectedRating.value >= 3 ? 'thumbs_up' : 'thumbs_down',
      },
    })
  } catch { /* non-critical */ }
}

// Sharing
const pageUrl = computed(() => `https://gradecrest.com/blog/${slug}`)
const copied = ref(false)
async function copyLink() {
  await navigator.clipboard.writeText(pageUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
function printPage() { window.print() }

// Utils
function formatDate(iso: string | null | undefined) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })
}
function formatDateShort(iso: string | null | undefined) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })
}

const displayTitle     = computed(() => article.value?.title || staticPost?.title || '')
const authorInitial    = computed(() => (article.value?.author_name || staticPost?.author || 'G').charAt(0).toUpperCase())
const authorName       = computed(() => article.value?.author_name || staticPost?.author || 'GradeCrest Editorial Team')
const authorCredentials = computed(() => article.value?.author_credentials || staticPost?.authorCredentials || '')
const authorBio        = computed(() => article.value?.author_bio || '')
const publishedDate    = computed(() => article.value?.canonical_published_at || article.value?.meta?.first_published_at || staticPost?.date)
const updatedDate      = computed(() => article.value?.last_substantive_update)
const wordCount        = computed(() => article.value?.word_count || 0)
const tags             = computed(() => article.value?.tag_names ?? [])
</script>

<template>
  <div class="pt-16">

    <!-- Reading progress bar -->
    <div
      class="fixed top-16 left-0 z-50 h-0.5 bg-gc-500 transition-all duration-100 print:hidden"
      :style="{ width: `${readProgress}%` }"
    />

    <!-- 404 -->
    <div v-if="(error || !article) && !staticPost" class="min-h-[60vh] flex items-center justify-center">
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
      <section class="bg-forest-950 pb-10 pt-10 relative overflow-hidden print:bg-white print:pb-4">
        <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none print:hidden" />
        <div class="relative mx-auto max-w-5xl px-4 sm:px-6">

          <!-- Breadcrumbs / separator -->
          <nav class="mb-5 flex items-center gap-1.5 text-xs text-slate-500 flex-wrap print:text-slate-400">
            <NuxtLink to="/" class="hover:text-slate-300 transition-colors">Home</NuxtLink>
            <span class="text-slate-600">/</span>
            <NuxtLink to="/blog" class="hover:text-slate-300 transition-colors">Blog</NuxtLink>
            <span class="text-slate-600">/</span>
            <span class="text-slate-400 line-clamp-1">{{ article?.title ?? staticPost?.title }}</span>
          </nav>

          <!-- Category + meta row -->
          <div class="flex flex-wrap items-center gap-3 mb-4 text-xs text-slate-400">
            <span
              v-if="article?.category_name || staticPost?.category"
              class="rounded-full bg-gc-500/20 px-3 py-1 font-semibold text-gc-300 text-xs"
            >{{ article?.category_name ?? staticPost?.category }}</span>
            <span class="flex items-center gap-1">
              <Clock class="size-3" />
              {{ article?.reading_time_minutes || staticPost?.readTime || '1 min read' }}
            </span>
            <span v-if="wordCount" class="flex items-center gap-1">
              {{ wordCount.toLocaleString() }} words
            </span>
            <span class="flex items-center gap-1">
              <Calendar class="size-3" />
              {{ formatDate(publishedDate ?? staticPost?.date ?? '') }}
            </span>
            <span v-if="updatedDate" class="text-gc-400 font-medium">
              · Updated {{ formatDateShort(updatedDate) }}
            </span>
          </div>

          <!-- Title -->
          <h1 class="text-3xl font-bold text-white sm:text-4xl leading-snug max-w-3xl print:text-ink">
            {{ article?.title ?? staticPost?.title }}
          </h1>

          <!-- Author + reviewer row -->
          <div class="mt-5 flex flex-wrap items-center gap-4">
            <!-- Author -->
            <div class="flex items-center gap-2.5">
              <div class="flex size-9 shrink-0 items-center justify-center rounded-full bg-gc-600 text-sm font-bold text-white">
                {{ authorInitial || (staticPost?.author ?? 'G').charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-semibold text-white leading-none">{{ authorName || staticPost?.author }}</p>
                <p v-if="authorCredentials || staticPost?.authorCredentials" class="text-xs text-slate-400 mt-0.5">{{ authorCredentials || staticPost?.authorCredentials }}</p>
              </div>
            </div>
            <!-- Reviewer badge -->
            <div
              v-if="article?.reviewer"
              class="flex items-center gap-1.5 rounded-full border border-gc-500/30 bg-gc-500/10 px-3 py-1 text-xs text-gc-300"
            >
              <svg class="size-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/></svg>
              Expert reviewed
            </div>
          </div>
        </div>
      </section>

      <!-- Featured image -->
      <div v-if="article?.thumbnail?.url" class="bg-forest-950 print:hidden">
        <div class="mx-auto max-w-5xl px-4 sm:px-6">
          <img :src="article.thumbnail.url" :alt="article?.title ?? ''" class="w-full rounded-t-2xl object-cover max-h-96" />
        </div>
      </div>

      <!-- Body -->
      <section class="bg-white py-10" id="article-body">
        <div class="mx-auto max-w-5xl px-4 sm:px-6">
          <div class="lg:grid lg:grid-cols-[1fr_260px] lg:gap-12">

            <!-- Main content -->
            <div class="min-w-0">

              <!-- Article TOC -->
              <ArticleToc
                v-if="toc.length >= 3"
                :items="toc"
                variant="cards"
                class="mb-8 print:hidden"
              />

              <!-- Article body: CMS (StreamField blocks) or static (HTML) -->
              <div class="prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-ink prose-headings:scroll-mt-24 prose-a:text-gc-600 prose-a:underline prose-a:decoration-gc-300 hover:prose-a:decoration-gc-600 prose-p:text-graphite prose-p:leading-relaxed prose-li:text-graphite prose-strong:text-ink">
                <BlockRenderer v-if="article?.body?.length" :blocks="article.body" :inline-cta="gcInlineCta" link-context="blog" />
                <div v-else-if="staticPost">
                  <p class="lead">{{ staticPost.excerpt }}</p>
                  <div class="not-prose my-8 rounded-xl border border-gc-100 bg-gc-50 px-5 py-4 text-sm text-gc-800">
                    📖 This is a preview of a full article. The complete guide is available once our CMS is connected.
                  </div>
                </div>

                <!-- Lead magnet — shown only when staff attaches a resource in Wagtail -->
                <div v-if="article?.lead_magnet" class="mt-10 not-prose">
                  <LeadMagnet
                    :attachment-slug="article.lead_magnet.slug"
                    :title="article.lead_magnet.title"
                    :description="article.lead_magnet.description"
                  />
                </div>
              </div>

              <!-- Tags -->
              <div v-if="tags.length" class="mt-8 pt-6 border-t border-slate-100 print:hidden">
                <div class="flex flex-wrap items-center gap-2">
                  <Tag class="size-3.5 text-graphite shrink-0" />
                  <NuxtLink
                    v-for="tag in tags" :key="tag"
                    :to="`/blog?tag=${encodeURIComponent(tag)}`"
                    class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-graphite hover:border-gc-300 hover:bg-gc-50 hover:text-gc-700 transition-colors"
                  >{{ tag }}</NuxtLink>
                </div>
              </div>

              <!-- Social sharing + print -->
              <div class="mt-8 pt-6 border-t border-slate-100 flex flex-wrap items-center gap-2 print:hidden">
                <span class="text-xs font-semibold text-graphite uppercase tracking-widest mr-1">Share</span>
                <a
                  :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(displayTitle)}&url=${encodeURIComponent(pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-graphite hover:border-slate-300 hover:text-ink transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                  X
                </a>
                <a
                  :href="`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-graphite hover:border-blue-300 hover:text-blue-700 transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                  LinkedIn
                </a>
                <a
                  :href="`https://wa.me/?text=${encodeURIComponent(displayTitle + ' ' + pageUrl)}`"
                  target="_blank" rel="noopener"
                  class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-graphite hover:border-green-300 hover:text-green-700 transition-colors"
                >
                  <svg class="size-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                  WhatsApp
                </a>
                <button
                  class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-graphite hover:border-slate-300 hover:text-ink transition-colors"
                  @click="copyLink"
                >
                  <Check v-if="copied" class="size-3.5 text-green-600" />
                  <svg v-else class="size-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                  {{ copied ? 'Copied!' : 'Copy link' }}
                </button>
                <button
                  class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-graphite hover:border-slate-300 hover:text-ink transition-colors ml-auto"
                  @click="printPage"
                >
                  <Printer class="size-3.5" />
                  Print
                </button>
              </div>

              <!-- Star rating feedback -->
              <div class="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white print:hidden">
                <div class="border-b border-slate-100 px-5 py-4">
                  <p class="text-sm font-semibold text-ink">Rate this article</p>
                  <p class="mt-0.5 text-xs text-graphite">
                    <template v-if="viewsDisplay">
                      <span class="font-semibold text-slate-600">{{ viewsDisplay.toLocaleString() }}</span> students read this ·
                    </template>
                    Your feedback helps us improve
                  </p>
                </div>
                <div class="p-5 space-y-4">
                  <!-- Idle / rating state -->
                  <template v-if="feedbackState !== 'done'">
                    <!-- Stars -->
                    <div class="flex items-center gap-1">
                      <button
                        v-for="star in 5" :key="star"
                        class="text-3xl leading-none transition-all hover:scale-110 focus:outline-none"
                        :class="(hoverRating || selectedRating) >= star ? 'text-amber-400' : 'text-slate-200'"
                        @mouseenter="hoverRating = star"
                        @mouseleave="hoverRating = 0"
                        @click="selectRating(star)"
                        :aria-label="`Rate ${star} out of 5`"
                      >★</button>
                      <span v-if="selectedRating" class="ml-2 text-xs text-slate-500">
                        {{ ['', 'Poor', 'Fair', 'Good', 'Great', 'Excellent!'][selectedRating] }}
                      </span>
                    </div>
                    <!-- Quick tags + comment after rating is selected -->
                    <template v-if="feedbackState === 'rating'">
                      <p class="text-xs font-medium text-graphite">What did you think? <span class="text-slate-400 font-normal">(optional)</span></p>
                      <div class="flex flex-wrap gap-2">
                        <button
                          v-for="tag in feedbackTags" :key="tag"
                          class="rounded-full border px-3 py-1 text-xs transition-colors"
                          :class="selectedTags.has(tag)
                            ? 'border-gc-400 bg-gc-50 text-gc-700 font-semibold'
                            : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700'"
                          @click="toggleTag(tag)"
                        >{{ tag }}</button>
                      </div>
                      <textarea
                        v-model="feedbackComment"
                        placeholder="Any other thoughts? (optional)"
                        rows="2"
                        class="w-full resize-none rounded-xl border border-slate-200 px-3 py-2 text-xs text-ink placeholder:text-slate-400 focus:border-gc-300 focus:outline-none focus:ring-2 focus:ring-gc-100"
                      />
                      <button
                        class="rounded-xl bg-gc-600 px-5 py-2 text-xs font-bold text-white hover:bg-gc-700 transition-colors"
                        @click="submitFeedback"
                      >Submit feedback</button>
                    </template>
                  </template>
                  <!-- Done state -->
                  <div v-else class="flex items-center gap-3 py-1">
                    <div class="flex size-9 shrink-0 items-center justify-center rounded-full bg-gc-100">
                      <svg class="size-4 text-gc-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/>
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-ink">Thanks for your feedback!</p>
                      <p class="text-xs text-graphite">It helps us write better guides for students like you.</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Author card -->
              <div v-if="authorName" class="mt-8 rounded-2xl border border-slate-200 bg-mist p-5 flex items-start gap-4">
                <div class="flex size-12 shrink-0 items-center justify-center rounded-full bg-gc-600 text-base font-bold text-white">
                  {{ authorInitial }}
                </div>
                <div class="flex-1">
                  <div class="flex flex-wrap items-baseline gap-2">
                    <p class="text-sm font-semibold text-ink">{{ authorName }}</p>
                    <span v-if="authorCredentials" class="text-xs font-medium text-gc-600 bg-gc-50 rounded-full px-2 py-0.5">
                      {{ authorCredentials }}
                    </span>
                  </div>
                  <p v-if="authorBio" class="mt-2 text-xs text-graphite leading-relaxed">{{ authorBio }}</p>
                  <p v-if="publishedDate" class="mt-2 text-xs text-slate-400">
                    Published {{ formatDate(publishedDate) }}
                    <span v-if="updatedDate"> · Last updated {{ formatDate(updatedDate) }}</span>
                  </p>
                </div>
              </div>

              <!-- "What are you waiting for?" end conversion section -->
              <div class="mt-10 rounded-2xl overflow-hidden border border-slate-200 print:hidden">
                <div class="bg-forest-950 p-7 text-center relative overflow-hidden">
                  <div class="absolute inset-0 bg-hero-grid bg-grid-40 pointer-events-none opacity-50" />
                  <div class="relative">
                    <p class="text-xl font-bold text-white mb-1">What are you waiting for?</p>
                    <p class="text-slate-300 text-sm mb-5">
                      Get your paper written by a human expert — grade guaranteed, zero AI content.
                    </p>
                    <a
                      href="/order"
                      class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors"
                    >
                      Place your order <ArrowRight class="size-4" />
                    </a>
                  </div>
                </div>
                <div class="bg-mist px-6 py-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center border-t border-slate-100">
                  <div v-for="trust in [
                    { label: 'Plagiarism-free', icon: '✓' },
                    { label: 'Grade guaranteed', icon: '✓' },
                    { label: 'Unlimited revisions', icon: '✓' },
                    { label: 'From $13/page', icon: '✓' },
                  ]" :key="trust.label">
                    <p class="text-xs font-semibold text-ink">{{ trust.icon }} {{ trust.label }}</p>
                  </div>
                </div>
              </div>

            </div>

            <!-- Sticky sidebar (desktop) -->
            <aside class="hidden lg:block lg:self-start lg:sticky lg:top-24 print:hidden">
              <div class="max-h-[calc(100vh-6rem)] overflow-y-auto space-y-5 pb-4">

                <!-- Sidebar TOC: chapter progress -->
                <div v-if="toc.length >= 2" class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
                  <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
                    <p class="text-xs font-bold uppercase tracking-widest text-graphite">In this article</p>
                    <span v-if="activeTocIndex >= 0" class="text-xs tabular-nums text-slate-400">
                      {{ activeTocIndex + 1 }}/{{ toc.length }}
                    </span>
                  </div>
                  <nav class="p-4">
                    <ol class="relative list-none space-y-0">
                      <!-- Track line -->
                      <div class="absolute left-[9px] top-2.5 bottom-2.5 w-px bg-slate-200" />
                      <!-- Progress fill -->
                      <div
                        class="absolute left-[9px] top-2.5 w-px bg-gc-500 transition-all duration-500 ease-out"
                        :style="{ height: `calc(${tocProgress}% * (100% - 20px) / 100 + 2px)` }"
                      />
                      <li
                        v-for="(item, i) in toc" :key="item.id"
                        class="relative flex gap-3 pb-4 last:pb-0"
                        :class="item.level === 'h3' ? 'pl-3' : item.level === 'h4' ? 'pl-5' : ''"
                      >
                        <!-- Chapter dot -->
                        <div
                          class="relative z-10 mt-0.5 flex size-[18px] shrink-0 items-center justify-center rounded-full border-2 transition-all duration-300"
                          :class="i < activeTocIndex
                            ? 'border-gc-500 bg-gc-500'
                            : activeTocId === item.id
                              ? 'border-gc-600 bg-gc-600 scale-110 shadow-sm'
                              : 'border-slate-300 bg-white'"
                        >
                          <svg v-if="i < activeTocIndex" class="size-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                          </svg>
                          <span v-else class="text-[7px] font-bold tabular-nums"
                            :class="activeTocId === item.id ? 'text-white' : 'text-slate-400'">
                            {{ i + 1 }}
                          </span>
                        </div>
                        <!-- Chapter link -->
                        <a
                          :href="`#${item.id}`"
                          class="flex-1 pt-0.5 text-sm leading-snug transition-colors"
                          :class="activeTocId === item.id
                            ? 'font-semibold text-gc-700'
                            : i < activeTocIndex
                              ? 'text-slate-400 hover:text-gc-600'
                              : 'text-graphite hover:text-gc-600'"
                        >{{ item.text }}</a>
                      </li>
                    </ol>
                  </nav>
                </div>

                <!-- Compact price calculator -->
                <ClientOnly>
                  <PricingCalculator />
                  <template #fallback><div class="h-96 animate-pulse rounded-2xl bg-forest-900/40" /></template>
                </ClientOnly>

                <!-- Sidebar Order CTA -->
                <div class="rounded-2xl bg-gc-600 p-5 text-white space-y-3">
                  <p class="font-bold text-sm leading-snug">Get your paper written by an expert</p>
                  <ul class="text-xs text-gc-100 space-y-1">
                    <li>✓ Human-written, zero AI</li>
                    <li>✓ Grade or money back</li>
                    <li>✓ From $13/page</li>
                  </ul>
                  <a href="/order" class="block rounded-xl bg-white text-gc-700 font-bold text-sm py-2.5 text-center hover:bg-gc-50 transition-colors">
                    Order now →
                  </a>
                </div>

                <!-- Social proof nudge -->
                <div v-if="article?.category_name || staticPost?.category" class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-center">
                  <p class="text-xs font-semibold text-emerald-700">🎓 Popular this week</p>
                  <p class="text-xs text-emerald-600 mt-0.5">Students are ordering expert help with <span class="font-semibold">{{ article?.category_name ?? staticPost?.category }}</span></p>
                </div>

                <!-- Last updated -->
                <div v-if="updatedDate || publishedDate || staticPost?.date" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-xs text-graphite space-y-1">
                  <p v-if="publishedDate || staticPost?.date"><span class="font-medium text-ink">Published:</span> {{ formatDate(publishedDate ?? staticPost?.date ?? '') }}</p>
                  <p v-if="updatedDate"><span class="font-medium text-ink">Last updated:</span> {{ formatDate(updatedDate) }}</p>
                  <p v-if="article?.reviewer"><span class="font-medium text-ink">Reviewed by:</span> {{ article?.reviewer?.name }}</p>
                </div>

              </div>
            </aside>

          </div>
        </div>
      </section>

      <!-- Connected articles -->
      <section v-if="connectedPosts?.length" class="bg-slate-50 border-t border-slate-100 py-12 print:hidden">
        <div class="mx-auto max-w-5xl px-4 sm:px-6">
          <h2 class="text-lg font-bold text-ink mb-6">You might also like</h2>
          <div class="grid gap-5 sm:grid-cols-3">
            <NuxtLink
              v-for="post in connectedPosts" :key="post.meta?.slug"
              :to="`/blog/${post.meta?.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-200 bg-white shadow-card hover:shadow-lift hover:-translate-y-0.5 transition-all overflow-hidden"
            >
              <div class="h-36 bg-slate-100 overflow-hidden">
                <img v-if="post.thumbnail?.url" :src="post.thumbnail.url" :alt="post.title" class="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300" />
                <div v-else class="h-full flex items-center justify-center"><span class="text-xl font-extrabold text-slate-200 select-none">G</span></div>
              </div>
              <div class="p-4 flex-1 flex flex-col gap-2">
                <span v-if="post.category_name" class="text-xs font-semibold text-gc-600">{{ post.category_name }}</span>
                <h3 class="text-sm font-semibold text-ink group-hover:text-gc-600 transition-colors line-clamp-2 flex-1 leading-snug">{{ post.title }}</h3>
                <div class="flex items-center gap-2 text-xs text-graphite pt-1">
                  <span v-if="post.reading_time_minutes">{{ post.reading_time_minutes }} min</span>
                  <span class="text-gc-600 font-medium group-hover:underline ml-auto">Read →</span>
                </div>
              </div>
            </NuxtLink>
          </div>
        </div>
      </section>

    </template>

    <!-- Mobile floating CTA -->
    <div class="fixed bottom-0 inset-x-0 z-40 lg:hidden bg-white border-t border-slate-200 px-4 py-3 flex items-center gap-3 shadow-xl print:hidden">
      <div class="flex-1 min-w-0">
        <p class="text-xs font-bold text-ink leading-none">Need help with your paper?</p>
        <p class="text-xs text-graphite mt-0.5 truncate">Human-written · Grade guaranteed</p>
      </div>
      <a href="/order" class="shrink-0 rounded-xl bg-gc-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-gc-700 transition-colors">
        Order now
      </a>
    </div>

    <!-- Back to top -->
    <Transition
      enter-active-class="transition duration-200"
      enter-from-class="opacity-0 translate-y-2"
      leave-active-class="transition duration-150"
      leave-to-class="opacity-0 translate-y-2"
    >
      <button
        v-if="showBackToTop"
        class="fixed bottom-20 right-5 z-40 flex size-10 items-center justify-center rounded-full bg-forest-950 text-white shadow-lg hover:bg-forest-800 transition-colors lg:bottom-6 print:hidden"
        @click="scrollToTop"
        aria-label="Back to top"
      >↑</button>
    </Transition>

  </div>
</template>
