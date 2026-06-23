<script setup lang="ts">
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const route   = useRoute()
const slug    = route.params.slug as string
const config  = useRuntimeConfig()
const apiBase     = config.public.apiBase || ''
const wagtailBase = `${apiBase}/wagtail`

// ── CMS types ─────────────────────────────────────────────────────────────
interface Block { type: string; value: unknown }
interface CmsArticle {
  id: number
  meta: { slug: string; first_published_at: string; seo_title: string; search_description: string }
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
}

// ── Try CMS first ──────────────────────────────────────────────────────────
const { data: cmsArticle } = await useAsyncData<CmsArticle | null>(
  `em-blog-${slug}`,
  async () => {
    if (!wagtailBase) return null
    try {
      const res = await $fetch<{ items: CmsArticle[] }>(
        `${wagtailBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── CMS related posts ──────────────────────────────────────────────────────
const { data: cmsRelated } = await useAsyncData<{ meta: { slug: string }; title: string; excerpt: string; reading_time_minutes: number; category_name: string; thumbnail: { url: string } | null }[]>(
  `em-blog-related-${slug}`,
  async () => {
    if (!wagtailBase || !cmsArticle.value) return []
    try {
      const res = await $fetch<{ items: { meta: { slug: string }; title: string; excerpt: string; reading_time_minutes: number; category_name: string; thumbnail: { url: string } | null }[] }>(
        `${wagtailBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail', order: '-first_published_at', limit: 4 } },
      )
      return (res.items ?? []).filter(p => p.meta?.slug !== slug).slice(0, 3)
    } catch { return [] }
  },
)

// ── Static fallback ────────────────────────────────────────────────────────
const { getBySlug, getAll, getByAuthor } = useBlog()
const staticPost = cmsArticle.value ? null : getBySlug(slug)

if (!cmsArticle.value && !staticPost) {
  throw createError({ statusCode: 404, message: 'Post not found' })
}

// ── Static-only data ───────────────────────────────────────────────────────
const related  = staticPost ? getAll().filter(p => p.slug !== slug && p.category === staticPost.category).slice(0, 3) : []
const byAuthor = staticPost?.author ? getByAuthor(staticPost.author.slug, slug).slice(0, 4) : []
const { toc, processedBody } = staticPost ? useToc(staticPost.body) : { toc: [], processedBody: '' }

// ── CMS TOC ────────────────────────────────────────────────────────────────
const cmsToc = computed(() => extractToc(cmsArticle.value?.body ?? []))

// Reading progress bar
const readingProgress = ref(0)
const tocOpen = ref(false)
const stickyBarDismissed = ref(false)
const activeTocId = ref('')

let tocObserver: IntersectionObserver | null = null

onMounted(() => {
  tocOpen.value = window.innerWidth >= 1024

  function updateProgress() {
    const doc = document.documentElement
    const scrollTop = doc.scrollTop || document.body.scrollTop
    const scrollHeight = doc.scrollHeight - doc.clientHeight
    readingProgress.value = scrollHeight > 0 ? Math.round((scrollTop / scrollHeight) * 100) : 0
  }
  window.addEventListener('scroll', updateProgress, { passive: true })

  // Active TOC section tracking
  tocObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) activeTocId.value = entry.target.id
      }
    },
    { rootMargin: '-20% 0px -70% 0px' },
  )
  nextTick(() => {
    const allToc = [...cmsToc.value.map(t => t.id), ...toc.map(t => t.anchor)]
    allToc.forEach(id => {
      const el = document.getElementById(id)
      if (el) tocObserver?.observe(el)
    })
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', updateProgress)
    tocObserver?.disconnect()
  })
})

// Engagement (works off slug regardless of CMS vs static)
const { pageId, stats, myReact, bookmarked, ready, react, toggleBookmark, reactionCount, fmtCount } =
  useEngagement(slug)

const reactions: { type: 'helpful' | 'love' | 'insightful'; emoji: string; label: string }[] = [
  { type: 'helpful',    emoji: '👍', label: 'Helpful'    },
  { type: 'love',       emoji: '❤️', label: 'Love this'  },
  { type: 'insightful', emoji: '💡', label: 'Insightful' },
]

// Mid-article CTA injected after the 4th paragraph (static posts only)
const inlineCta = `
<div class="not-prose my-12" style="border-radius:1rem;overflow:hidden;background:linear-gradient(135deg,#3b0764 0%,#5b21b6 52%,#7c3aed 100%);position:relative;">
  <div style="position:absolute;inset:0;background-image:radial-gradient(circle,rgba(255,255,255,0.07) 1px,transparent 1px);background-size:26px 26px;pointer-events:none;"></div>
  <div style="position:absolute;top:-56px;right:-56px;width:208px;height:208px;border-radius:9999px;background:radial-gradient(circle,rgba(255,255,255,0.13),transparent 65%);pointer-events:none;"></div>
  <div style="position:relative;padding:2rem 1.75rem;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1.5rem;">
    <div style="flex:1;min-width:0;">
      <p style="margin:0 0 0.5rem;font-size:0.625rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.5);">EssayManiacs &mdash; 500+ subject specialists</p>
      <p style="margin:0 0 0.75rem;font-size:1.125rem;font-weight:800;line-height:1.35;color:#ffffff;">Deadline looming? Get a specialist writer on it &mdash; properly cited, original, from $10/page.</p>
      <div style="display:flex;flex-wrap:wrap;gap:0.25rem 1.25rem;">
        <span style="font-size:0.6875rem;color:rgba(255,255,255,0.85);display:flex;align-items:center;gap:0.375rem;"><span style="color:#4ade80;">&#10003;</span> Grade or money back</span>
        <span style="font-size:0.6875rem;color:rgba(255,255,255,0.85);display:flex;align-items:center;gap:0.375rem;"><span style="color:#4ade80;">&#10003;</span> Zero AI content</span>
        <span style="font-size:0.6875rem;color:rgba(255,255,255,0.85);display:flex;align-items:center;gap:0.375rem;"><span style="color:#4ade80;">&#10003;</span> As fast as 2 hours</span>
        <span style="font-size:0.6875rem;color:rgba(255,255,255,0.85);display:flex;align-items:center;gap:0.375rem;"><span style="color:#4ade80;">&#10003;</span> Free plagiarism report</span>
      </div>
    </div>
    <a href="/order" style="flex-shrink:0;display:inline-flex;align-items:center;gap:0.5rem;background:#ffffff;color:#4c1d95;font-weight:700;font-size:0.875rem;padding:0.75rem 1.75rem;border-radius:0.75rem;text-decoration:none;white-space:nowrap;box-shadow:0 0 28px rgba(167,139,250,0.5);">
      Place my order
      <svg style="width:1rem;height:1rem;" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
    </a>
  </div>
</div>`

const bodyWithInlineCta = computed(() => {
  let count = 0
  let insertAt = -1
  const re = /<\/p>/gi
  let m: RegExpExecArray | null
  while ((m = re.exec(processedBody)) !== null) {
    count++
    if (count === 4) { insertAt = m.index + m[0].length; break }
  }
  if (insertAt === -1) return processedBody
  return processedBody.slice(0, insertAt) + inlineCta + processedBody.slice(insertAt)
})

const fmtDate = (d: string | null | undefined) =>
  d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }) : ''

const authorInitials = computed(() => {
  if (cmsArticle.value) return (cmsArticle.value.author_name || 'E').charAt(0).toUpperCase()
  if (!staticPost?.author) return '?'
  const w = staticPost.author.name.trim().split(/\s+/)
  return w.length >= 2 ? (w[0][0] + w[w.length - 1][0]).toUpperCase() : staticPost.author.name[0].toUpperCase()
})

const ROLE_BADGE: Record<string, string> = {
  'Senior Writer':         'bg-brand-100 text-brand-700',
  'Subject Matter Expert': 'bg-amber-100 text-amber-700',
  'Writer':                'bg-slate-100 text-slate-600',
  'Editor':                'bg-violet-100 text-violet-700',
}

const CAT_COVER: Record<string, { bg: string; icon: string }> = {
  'Essays':          { bg: 'from-brand-800 to-brand-600',     icon: 'pen-line' },
  'Research Papers': { bg: 'from-blue-900 to-blue-600',       icon: 'file-text' },
  'Dissertations':   { bg: 'from-slate-800 to-slate-600',     icon: 'graduation-cap' },
  'Academic Tips':   { bg: 'from-emerald-800 to-emerald-600', icon: 'book-open' },
}

const postCategory = computed(() => cmsArticle.value?.category_name || staticPost?.category || '')
const postCover    = computed(() => CAT_COVER[postCategory.value] ?? { bg: 'from-brand-800 to-brand-600', icon: 'pen-line' })

const config2 = useRuntimeConfig()
const siteUrl = config2.public.siteUrl || 'https://essaymaniacs.com'
const canonicalUrl = `${siteUrl}/blog/${slug}`

const postTitle     = computed(() => cmsArticle.value?.title   || staticPost?.title   || '')
const postExcerpt   = computed(() => cmsArticle.value?.excerpt || staticPost?.excerpt || '')
const postDate      = computed(() => cmsArticle.value?.canonical_published_at || cmsArticle.value?.meta?.first_published_at || staticPost?.date || '')
const postModified  = computed(() => cmsArticle.value?.last_substantive_update || null)
const postImage     = computed(() => cmsArticle.value?.thumbnail?.url || null)

// FAQ blocks → FAQPage schema (when 2+ FAQ items present in CMS article)
const faqBlocks = computed(() =>
  (cmsArticle.value?.body ?? []).filter(b => b.type === 'faq') as Array<{ type: string; value: { question: string; answer: string } }>
)

useSeoMeta({
  title:                computed(() => cmsArticle.value?.meta?.seo_title || postTitle.value),
  description:          computed(() => cmsArticle.value?.meta?.search_description || postExcerpt.value),
  ogTitle:              postTitle,
  ogDescription:        postExcerpt,
  ogImage:              postImage,
  ogType:               'article',
  articlePublishedTime: postDate,
  articleModifiedTime:  postModified,
  articleAuthor:        computed(() => {
    const author = cmsArticle.value?.author_name || staticPost?.author?.name
    return author ? [author] : null
  }),
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

const ldScripts = computed(() => {
  const scripts: { type: string; innerHTML: string }[] = []

  // Article schema
  scripts.push({
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline:      postTitle.value,
      description:   postExcerpt.value,
      datePublished: postDate.value,
      ...(postModified.value ? { dateModified: postModified.value } : {}),
      ...(postImage.value ? { image: postImage.value } : {}),
      url: canonicalUrl,
      author: cmsArticle.value
        ? { '@type': 'Person', name: cmsArticle.value.author_name || 'EssayManiacs', description: cmsArticle.value.author_bio }
        : staticPost?.author
          ? { '@type': 'Person', name: staticPost.author.name, description: staticPost.author.bio, honorificSuffix: staticPost.author.credentials,
              ...(staticPost.author.orcid ? { sameAs: [`https://orcid.org/${staticPost.author.orcid}`] } : {}) }
          : { '@type': 'Organization', name: 'EssayManiacs' },
      publisher: {
        '@type': 'Organization',
        name: 'EssayManiacs',
        url: 'https://essaymaniacs.com',
        logo: { '@type': 'ImageObject', url: 'https://essaymaniacs.com/favicon.svg' },
      },
      speakable: {
        '@type': 'SpeakableSpecification',
        cssSelector: ['.post-excerpt', '.key-takeaways', 'h1'],
      },
    }),
  })

  // BreadcrumbList schema
  scripts.push({
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home',    item: 'https://essaymaniacs.com/' },
        { '@type': 'ListItem', position: 2, name: 'Blog',    item: 'https://essaymaniacs.com/blog' },
        { '@type': 'ListItem', position: 3, name: postTitle.value, item: canonicalUrl },
      ],
    }),
  })

  // FAQPage schema (when 2+ FAQ blocks are in the article)
  if (faqBlocks.value.length >= 2) {
    scripts.push({
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: faqBlocks.value.map(b => ({
          '@type': 'Question',
          name: b.value.question,
          acceptedAnswer: { '@type': 'Answer', text: b.value.answer },
        })),
      }),
    })
  }

  return scripts
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: ldScripts,
})
</script>

<template>
  <div>

    <!-- ── Reading progress bar ──────────────────────────────────────── -->
    <ClientOnly>
      <div
        class="fixed left-0 top-0 z-50 h-1 bg-brand-600 transition-all duration-75"
        :style="{ width: `${readingProgress}%` }"
      />
    </ClientOnly>

    <!-- ── Mobile sticky quote bar ───────────────────────────────────── -->
    <ClientOnly>
      <Transition
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="translate-y-full"
        enter-to-class="translate-y-0"
        leave-active-class="transition-transform duration-200 ease-in"
        leave-from-class="translate-y-0"
        leave-to-class="translate-y-full"
      >
        <div
          v-if="readingProgress > 15 && !stickyBarDismissed"
          class="fixed bottom-0 left-0 right-0 z-40 lg:hidden"
        >
          <div class="border-t border-slate-200 bg-white px-4 py-3 shadow-[0_-4px_20px_rgba(0,0,0,0.08)]">
            <div class="flex items-center gap-3">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-slate-900 leading-tight">Need this written for you?</p>
                <p class="text-xs text-slate-500 truncate">From $10/page · Grade guaranteed · As fast as 2 hrs</p>
              </div>
              <NuxtLink to="/order" class="shrink-0 rounded-lg bg-brand-700 px-4 py-2 text-xs font-bold text-white transition-colors hover:bg-brand-800">Get a quote</NuxtLink>
              <button class="shrink-0 flex h-7 w-7 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors" aria-label="Dismiss" @click="stickyBarDismissed = true">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </ClientOnly>

    <!-- ── Cover band ─────────────────────────────────────────────────── -->
    <div
      class="relative flex h-56 items-center justify-center overflow-hidden bg-gradient-to-br sm:h-72"
      :class="postCover.bg"
    >
      <div class="absolute inset-0 opacity-10"
        style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 28px 28px;" />
      <div v-if="cmsArticle?.thumbnail?.url" class="absolute inset-0">
        <img :src="cmsArticle.thumbnail.url" :alt="postTitle" class="h-full w-full object-cover opacity-30" />
      </div>
      <div class="relative flex h-24 w-24 items-center justify-center rounded-3xl bg-white/20 backdrop-blur-sm ring-1 ring-white/30">
        <Icon :name="postCover.icon" class="h-12 w-12 text-white" />
      </div>
      <nav class="absolute bottom-4 left-4 flex items-center gap-2 text-xs" aria-label="Breadcrumb">
        <NuxtLink href="/blog" class="font-semibold text-white/70 hover:text-white transition-colors">Blog</NuxtLink>
        <svg class="h-3 w-3 text-white/40" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
        <span class="rounded-full bg-white/20 px-2.5 py-0.5 font-semibold text-white backdrop-blur-sm">{{ postCategory }}</span>
      </nav>
    </div>

    <!-- ── Article header ────────────────────────────────────────────── -->
    <div class="border-b border-slate-100 bg-white">
      <div class="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <div class="mb-4 flex flex-wrap items-center gap-3">
          <span class="text-xs text-slate-400">
            {{ cmsArticle ? `${cmsArticle.reading_time_minutes || 1} min read` : staticPost?.readTime }}
          </span>
          <time class="text-xs text-slate-400">{{ fmtDate(postDate) }}</time>
          <ClientOnly>
            <span v-if="stats" class="flex items-center gap-1 text-xs text-slate-400">
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
              {{ fmtCount(stats.views) }} views
            </span>
          </ClientOnly>
        </div>

        <h1 class="font-serif text-3xl font-bold leading-tight text-slate-900 sm:text-4xl lg:text-5xl">
          {{ postTitle }}
        </h1>
        <p class="mt-5 text-lg leading-relaxed text-slate-600">{{ postExcerpt }}</p>

        <div class="mt-8 flex items-center gap-4 border-t border-slate-100 pt-6">
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-700 text-sm font-bold text-white">
            {{ authorInitials }}
          </div>
          <div class="flex-1">
            <p class="font-semibold text-slate-900">{{ cmsArticle?.author_name || staticPost?.author?.name || 'EssayManiacs' }}</p>
            <p class="text-xs text-slate-500">{{ cmsArticle?.author_credentials || staticPost?.author?.credentials }}</p>
          </div>
          <ClientOnly>
            <button
              v-if="ready && pageId"
              class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
              :class="bookmarked ? 'border-brand-200 bg-brand-50 text-brand-700' : 'border-slate-200 bg-white text-slate-500 hover:border-brand-200 hover:text-brand-700'"
              @click="toggleBookmark"
            >
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" :d="'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'" :fill="bookmarked ? 'currentColor' : 'none'"/></svg>
              {{ bookmarked ? 'Saved' : 'Save' }}
            </button>
          </ClientOnly>
        </div>
      </div>
    </div>

    <!-- ── Article body ───────────────────────────────────────────────── -->
    <div class="bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-10 py-12 lg:grid-cols-[1fr_260px] lg:items-start">

          <!-- Left: reading column -->
          <div class="min-w-0">

            <!-- TOC: CMS (block-based) — numbered magazine style with active tracking -->
            <nav
              v-if="cmsArticle && cmsToc.length >= 3"
              class="mb-10 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
              aria-label="Table of contents"
            >
              <button
                class="flex w-full items-center justify-between bg-gradient-to-r from-brand-950 to-brand-800 px-5 py-3.5"
                :aria-expanded="tocOpen"
                @click="tocOpen = !tocOpen"
              >
                <span class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-white/80">
                  <svg class="h-3.5 w-3.5 text-brand-300" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/></svg>
                  In This Article
                  <span class="rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-bold text-white">{{ cmsToc.length }}</span>
                </span>
                <svg class="h-4 w-4 text-white/50 transition-transform" :class="tocOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <Transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 max-h-0" enter-to-class="opacity-100 max-h-[700px]" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 max-h-[700px]" leave-to-class="opacity-0 max-h-0">
                <ol v-if="tocOpen" class="divide-y divide-slate-100">
                  <li v-for="(item, idx) in cmsToc" :key="item.id"
                    :class="[item.level === 'h3' ? 'pl-10' : '', activeTocId === item.id ? 'bg-brand-50' : 'bg-white hover:bg-slate-50']"
                    class="transition-colors">
                    <a :href="`#${item.id}`"
                      class="flex items-center gap-3 px-5 py-3 text-sm"
                      :class="activeTocId === item.id ? 'text-brand-700 font-semibold' : 'text-slate-600 hover:text-brand-600'"
                      @click="tocOpen = false">
                      <span class="flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold transition-colors"
                        :class="activeTocId === item.id ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-400'">
                        {{ idx + 1 }}
                      </span>
                      <span class="leading-snug">{{ item.text }}</span>
                      <svg v-if="activeTocId === item.id" class="ml-auto size-3 shrink-0 text-brand-500" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                    </a>
                  </li>
                </ol>
              </Transition>
            </nav>

            <!-- TOC: static (HTML-based) -->
            <nav
              v-else-if="staticPost && toc.length >= 3"
              class="mb-10 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
              aria-label="Table of contents"
            >
              <button
                class="flex w-full items-center justify-between bg-gradient-to-r from-brand-950 to-brand-800 px-5 py-3.5"
                :aria-expanded="tocOpen"
                @click="tocOpen = !tocOpen"
              >
                <span class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-white/80">
                  <svg class="h-3.5 w-3.5 text-brand-300" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/></svg>
                  In This Article
                  <span class="rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-bold text-white">{{ toc.length }}</span>
                </span>
                <svg class="h-4 w-4 text-white/50 transition-transform" :class="tocOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <Transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 max-h-0" enter-to-class="opacity-100 max-h-[700px]" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 max-h-[700px]" leave-to-class="opacity-0 max-h-0">
                <ol v-if="tocOpen" class="divide-y divide-slate-100">
                  <li v-for="(item, idx) in toc" :key="item.anchor"
                    :class="[item.level === 'h3' ? 'pl-10' : '', activeTocId === item.anchor ? 'bg-brand-50' : 'bg-white hover:bg-slate-50']"
                    class="transition-colors">
                    <a :href="`#${item.anchor}`"
                      class="flex items-center gap-3 px-5 py-3 text-sm"
                      :class="activeTocId === item.anchor ? 'text-brand-700 font-semibold' : 'text-slate-600 hover:text-brand-600'"
                      @click="tocOpen = false">
                      <span class="flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold transition-colors"
                        :class="activeTocId === item.anchor ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-400'">
                        {{ idx + 1 }}
                      </span>
                      <span class="leading-snug">{{ item.text }}</span>
                    </a>
                  </li>
                </ol>
              </Transition>
            </nav>

            <!-- CMS body: BlockRenderer -->
            <div
              v-if="cmsArticle"
              class="prose prose-slate prose-lg max-w-none
                     prose-headings:font-serif prose-headings:font-bold
                     prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                     prose-strong:text-slate-900"
            >
              <BlockRenderer :blocks="cmsArticle.body" :inline-cta="inlineCta" />
            </div>

            <!-- Static body: v-html -->
            <div
              v-else
              class="prose prose-slate prose-lg max-w-none
                     prose-headings:font-serif prose-headings:font-bold
                     prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                     prose-strong:text-slate-900
                     first-letter:float-left first-letter:mr-3 first-letter:font-serif first-letter:text-5xl first-letter:font-bold first-letter:leading-none first-letter:text-brand-700"
              v-html="bodyWithInlineCta"
            />

            <!-- Reactions -->
            <ClientOnly>
              <div v-if="ready && pageId" class="mt-12 rounded-2xl border border-slate-100 bg-slate-50 px-6 py-6">
                <p class="mb-4 text-center text-sm font-semibold text-slate-700">Was this guide helpful?</p>
                <div class="flex justify-center gap-3">
                  <button
                    v-for="r in reactions"
                    :key="r.type"
                    class="flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-medium transition-all"
                    :class="myReact === r.type ? 'border-brand-300 bg-brand-50 text-brand-700 shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700'"
                    @click="react(r.type)"
                  >
                    <span class="text-base leading-none">{{ r.emoji }}</span>
                    <span>{{ r.label }}</span>
                    <span v-if="reactionCount(r.type) > 0" class="rounded-full px-1.5 py-0.5 text-[11px] font-bold" :class="myReact === r.type ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-500'">
                      {{ fmtCount(reactionCount(r.type)) }}
                    </span>
                  </button>
                </div>
              </div>
            </ClientOnly>

            <!-- Share -->
            <div class="mt-8 lg:hidden">
              <ClientOnly><ShareButtons :title="postTitle" :url="canonicalUrl" /></ClientOnly>
            </div>

            <!-- Author card -->
            <div v-if="cmsArticle?.author_name || staticPost?.author" class="mt-10 overflow-hidden rounded-3xl border border-slate-200 bg-white">
              <div class="flex items-start gap-5 border-b border-slate-100 bg-slate-50 px-6 py-6">
                <div class="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-brand-700 text-2xl font-bold text-white ring-2 ring-white shadow-sm">
                  {{ authorInitials }}
                </div>
                <div class="min-w-0">
                  <p class="text-lg font-bold text-slate-900">{{ cmsArticle?.author_name || staticPost?.author?.name }}</p>
                  <p class="mt-0.5 text-sm font-medium text-slate-500">{{ cmsArticle?.author_credentials || staticPost?.author?.credentials }}</p>
                </div>
              </div>
              <div class="px-6 py-5">
                <p class="text-sm leading-7 text-slate-600">{{ cmsArticle?.author_bio || staticPost?.author?.bio }}</p>
                <template v-if="staticPost?.author">
                  <div class="mt-4 flex flex-wrap gap-2">
                    <a v-if="staticPost.author.linkedin" :href="staticPost.author.linkedin" target="_blank" rel="noreferrer" class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700">LinkedIn</a>
                    <a v-if="staticPost.author.twitter" :href="`https://twitter.com/${staticPost.author.twitter}`" target="_blank" rel="noreferrer" class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-300 hover:text-brand-700">@{{ staticPost.author.twitter }}</a>
                  </div>
                </template>
              </div>
              <div v-if="byAuthor.length" class="border-t border-slate-100 px-6 py-5">
                <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">More by {{ staticPost?.author?.name.split(' ')[0] }}</p>
                <ul class="space-y-3">
                  <li v-for="p in byAuthor" :key="p.slug">
                    <NuxtLink :href="`/blog/${p.slug}`" class="group flex items-start gap-3">
                      <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-300 transition-colors group-hover:bg-brand-600" />
                      <div class="min-w-0">
                        <p class="text-sm font-medium leading-snug text-slate-800 transition-colors group-hover:text-brand-700 line-clamp-2">{{ p.title }}</p>
                        <p class="mt-0.5 text-xs text-slate-400">{{ p.category }} · {{ p.readTime }}</p>
                      </div>
                    </NuxtLink>
                  </li>
                </ul>
                <NuxtLink :href="`/authors/${staticPost?.author?.slug}`" class="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-brand-700 hover:underline">
                  All articles by {{ staticPost?.author?.name.split(' ').slice(0, 2).join(' ') }} →
                </NuxtLink>
              </div>
            </div>

            <!-- End-of-article CTA -->
            <div class="mt-10 overflow-hidden rounded-3xl bg-brand-900 p-8">
              <div class="sm:flex sm:items-center sm:justify-between sm:gap-8">
                <div>
                  <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-400">500+ subject specialists available</p>
                  <h2 class="font-serif text-2xl font-bold text-white">Still staring at a blank page?</h2>
                  <p class="mt-2 leading-relaxed text-brand-200">A writer who loves your subject can handle this essay from scratch — properly cited, from $10/page.</p>
                  <ul class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm text-brand-300">
                    <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Grade or money back</li>
                    <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Zero AI content</li>
                    <li class="flex items-center gap-1"><span class="text-green-400">✓</span> As fast as 2 hours</li>
                    <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Free plagiarism report</li>
                  </ul>
                </div>
                <NuxtLink to="/order" class="mt-6 block shrink-0 rounded-xl bg-white px-8 py-3 text-center text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50 sm:mt-0">
                  Place my order →
                </NuxtLink>
              </div>
            </div>

            <div class="mt-6">
              <EditorialProcess :published-at="postDate" />
            </div>

          </div><!-- end left column -->

          <!-- Right: sticky sidebar -->
          <aside class="hidden lg:block">
            <div class="sticky top-24 space-y-6">
              <ClientOnly>
                <MultiStepOrderForm />
                <template #fallback><div class="h-96 animate-pulse rounded-2xl bg-slate-100" /></template>
              </ClientOnly>
              <div class="flex flex-col items-center">
                <ClientOnly>
                  <ShareButtons :title="postTitle" :url="canonicalUrl" :vertical="true" />
                </ClientOnly>
              </div>
            </div>
          </aside>

        </div>
      </div>
    </div>

    <!-- ── Related articles ───────────────────────────────────────────── -->
    <div
      v-if="(cmsArticle && cmsRelated?.length) || (!cmsArticle && related.length)"
      class="border-t border-slate-100 bg-slate-50 py-16"
    >
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 class="mb-8 font-serif text-2xl font-bold text-slate-900">
          More on {{ postCategory }}
        </h2>
        <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <!-- CMS related -->
          <template v-if="cmsArticle">
            <NuxtLink
              v-for="r in cmsRelated" :key="r.meta?.slug"
              :href="`/blog/${r.meta?.slug}`"
              class="group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
            >
              <div class="h-36 overflow-hidden bg-slate-100">
                <img v-if="r.thumbnail?.url" :src="r.thumbnail.url" :alt="r.title" class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <div v-else class="flex h-full items-center justify-center"><span class="select-none text-xl font-extrabold text-slate-200">E</span></div>
              </div>
              <div class="flex flex-1 flex-col p-4">
                <span class="mb-1 text-xs font-semibold text-brand-600">{{ r.category_name }}</span>
                <h3 class="flex-1 text-sm font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 line-clamp-2">{{ r.title }}</h3>
                <span class="mt-3 text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
              </div>
            </NuxtLink>
          </template>
          <!-- Static related -->
          <template v-else>
            <NuxtLink
              v-for="r in related" :key="r.slug"
              :href="`/blog/${r.slug}`"
              class="group flex flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white transition-all hover:border-brand-200 hover:shadow-md"
            >
              <div class="flex flex-1 flex-col p-6">
                <div class="mb-3 flex items-center gap-2">
                  <span class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">{{ r.category }}</span>
                  <span class="text-xs text-slate-400">{{ r.readTime }}</span>
                </div>
                <h3 class="flex-1 font-serif font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ r.title }}</h3>
                <p class="mt-2 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ r.excerpt }}</p>
                <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                  <time class="text-xs text-slate-400">{{ new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }) }}</time>
                  <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
                </div>
              </div>
            </NuxtLink>
          </template>
        </div>
      </div>
    </div>

  </div>
</template>
