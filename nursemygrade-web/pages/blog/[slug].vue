<script setup lang="ts">
import BlockRenderer from '~/components/cms/BlockRenderer.vue'

const route   = useRoute()
const slug    = route.params.slug as string
const config  = useRuntimeConfig()
const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

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
  `nmg-blog-${slug}`,
  async () => {
    if (!apiBase) return null
    try {
      const res = await $fetch<{ items: CmsArticle[] }>(
        `${apiBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── CMS related posts ──────────────────────────────────────────────────────
const { data: cmsRelated } = await useAsyncData<{ meta: { slug: string }; title: string; reading_time_minutes: number; category_name: string; thumbnail: { url: string } | null }[]>(
  `nmg-blog-related-${slug}`,
  async () => {
    if (!apiBase || !cmsArticle.value) return []
    try {
      const res = await $fetch<{ items: { meta: { slug: string }; title: string; reading_time_minutes: number; category_name: string; thumbnail: { url: string } | null }[] }>(
        `${apiBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', fields: 'title,reading_time_minutes,category_name,thumbnail', order: '-first_published_at', limit: 4 } },
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

const tocOpen = ref(false)
onMounted(() => { tocOpen.value = window.innerWidth >= 1024 })

const { stats, myReact, bookmarked, ready, react, toggleBookmark, reactionCount, fmtCount } =
  useEngagement(slug)

const reactions: { type: 'helpful' | 'love' | 'insightful'; emoji: string; label: string }[] = [
  { type: 'helpful',   emoji: '👍', label: 'Helpful'   },
  { type: 'love',      emoji: '❤️', label: 'Love this' },
  { type: 'insightful',emoji: '💡', label: 'Insightful' },
]

// Mid-article inline CTA (static posts only)
const inlineCta = `
<div class="not-prose my-10 border-y border-slate-200 py-8">
  <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <p class="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">NurseMyGrade</p>
      <p class="text-[1.05rem] font-bold leading-snug text-slate-900">Clinical rotations, coursework, and a deadline — all at once. A BSN or MSN nurse can take this off your plate.</p>
      <div class="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-500">
        <span>✓ NANDA · SOAP · APA 7th — clinically accurate</span>
        <span>✓ From $24/page · As fast as 3 hours</span>
        <span>✓ Grade or money back</span>
      </div>
    </div>
    <a href="/order" class="mt-1 shrink-0 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-slate-700 whitespace-nowrap">
      Get my nurse writer
      <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
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
  d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : ''

const authorInitials = computed(() => {
  if (cmsArticle.value) return (cmsArticle.value.author_name || 'N').charAt(0).toUpperCase()
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
  'Nursing Papers':       { bg: 'from-brand-800 to-brand-600',      icon: 'stethoscope' },
  'Capstone & Research':  { bg: 'from-slate-800 to-slate-600',       icon: 'graduation-cap' },
  'Citation & Format':    { bg: 'from-indigo-800 to-indigo-600',     icon: 'book-open' },
  'Clinical Simulations': { bg: 'from-emerald-800 to-emerald-600',   icon: 'monitor' },
  'Dissertations':        { bg: 'from-slate-800 to-slate-600',       icon: 'file-text' },
  'Essays':               { bg: 'from-brand-800 to-brand-600',       icon: 'pen-line' },
  'Nursing School':       { bg: 'from-rose-800 to-rose-600',         icon: 'book-open' },
  'Research Papers':      { bg: 'from-blue-900 to-blue-700',         icon: 'search' },
}

const postCategory = computed(() => cmsArticle.value?.category_name || staticPost?.category || '')
const postCover    = computed(() => CAT_COVER[postCategory.value] ?? { bg: 'from-brand-800 to-brand-600', icon: 'pen-line' })
const postTitle    = computed(() => cmsArticle.value?.title   || staticPost?.title   || '')
const postExcerpt  = computed(() => cmsArticle.value?.excerpt || staticPost?.excerpt || '')
const postDate     = computed(() => cmsArticle.value?.canonical_published_at || cmsArticle.value?.meta?.first_published_at || staticPost?.date || '')

const config2 = useRuntimeConfig()
const siteUrl = config2.public.siteUrl || 'https://nursemygrade.com'
const canonicalUrl = `${siteUrl}/blog/${slug}`

useSeoMeta({
  title:         computed(() => cmsArticle.value?.meta?.seo_title || postTitle.value),
  description:   computed(() => cmsArticle.value?.meta?.search_description || postExcerpt.value),
  ogTitle:       postTitle,
  ogDescription: postExcerpt,
  articlePublishedTime: postDate,
  articleAuthor: computed(() => cmsArticle.value?.author_name || staticPost?.author?.name),
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline:    postTitle.value,
      description: postExcerpt.value,
      datePublished: postDate.value,
      url: canonicalUrl,
      author: cmsArticle.value
        ? { '@type': 'Person', name: cmsArticle.value.author_name || 'NurseMyGrade', description: cmsArticle.value.author_bio }
        : staticPost?.author
          ? { '@type': 'Person', name: staticPost.author.name, description: staticPost.author.bio, honorificSuffix: staticPost.author.credentials,
              ...(staticPost.author.orcid ? { sameAs: [`https://orcid.org/${staticPost.author.orcid}`] } : {}) }
          : { '@type': 'Organization', name: 'NurseMyGrade' },
      publisher: {
        '@type': 'Organization',
        name: 'NurseMyGrade',
        url: 'https://nursemygrade.com',
        logo: { '@type': 'ImageObject', url: 'https://nursemygrade.com/favicon.svg' },
      },
    }),
  }],
})
</script>

<template>
  <div class="section">

    <!-- Cover band -->
    <div
      class="relative -mx-4 mb-10 flex h-56 items-center justify-center overflow-hidden bg-gradient-to-br sm:-mx-6 sm:h-72 lg:-mx-8"
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

    <div class="grid gap-10 lg:grid-cols-[1fr_300px]">

      <!-- ── Left: article content ──────────────────────────────────── -->
      <article class="min-w-0">

        <!-- Meta bar -->
        <div class="mb-4 flex flex-wrap items-center gap-3">
          <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700">{{ postCategory }}</span>
          <span class="text-xs text-slate-400">{{ cmsArticle ? `${cmsArticle.reading_time_minutes || 1} min read` : staticPost?.readTime }}</span>
          <time class="text-xs text-slate-400">{{ fmtDate(postDate) }}</time>
          <ClientOnly>
            <template v-if="stats">
              <span class="flex items-center gap-1 text-xs text-slate-400">
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                {{ fmtCount(stats.views) }} views
              </span>
            </template>
          </ClientOnly>
        </div>

        <!-- Title + excerpt -->
        <h1 class="font-serif text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">{{ postTitle }}</h1>
        <p class="mt-4 text-lg leading-relaxed text-slate-600">{{ postExcerpt }}</p>

        <!-- Author byline + bookmark -->
        <div v-if="cmsArticle?.author_name || staticPost?.author" class="mt-6 flex items-center gap-3 border-t border-slate-100 pt-5">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
            {{ authorInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-slate-900">{{ cmsArticle?.author_name || staticPost?.author?.name }}</p>
            <p class="text-xs text-slate-500">{{ cmsArticle?.author_credentials || staticPost?.author?.credentials }}</p>
          </div>
          <ClientOnly>
            <button
              v-if="ready && pageId"
              class="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
              :class="bookmarked ? 'border-brand-200 bg-brand-50 text-brand-700' : 'border-slate-200 bg-white text-slate-500 hover:border-brand-200 hover:text-brand-700'"
              @click="toggleBookmark"
            >
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" :d="'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'" :fill="bookmarked ? 'currentColor' : 'none'" />
              </svg>
              {{ bookmarked ? 'Saved' : 'Save' }}
            </button>
          </ClientOnly>
        </div>

        <!-- TOC: CMS -->
        <nav v-if="cmsArticle && cmsToc.length >= 3" class="mt-8 rounded-xl border border-slate-200 bg-slate-50" aria-label="Table of contents">
          <button class="flex w-full items-center justify-between px-5 py-4 text-left" :aria-expanded="tocOpen" @click="tocOpen = !tocOpen">
            <span class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/></svg>
              In this article
              <span class="rounded-full bg-slate-200 px-1.5 py-0.5 text-[10px] font-bold text-slate-600">{{ cmsToc.length }}</span>
            </span>
            <svg class="h-4 w-4 text-slate-400 transition-transform duration-200" :class="tocOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <Transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 max-h-0" enter-to-class="opacity-100 max-h-[600px]" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 max-h-[600px]" leave-to-class="opacity-0 max-h-0">
            <div v-if="tocOpen" class="overflow-hidden border-t border-slate-200 px-5 pb-5 pt-4">
              <ol class="space-y-1.5">
                <li v-for="item in cmsToc" :key="item.id" :class="item.level === 'h3' ? 'ml-4' : ''">
                  <a :href="`#${item.id}`" class="text-sm text-brand-600 hover:underline" @click="tocOpen = false">{{ item.text }}</a>
                </li>
              </ol>
            </div>
          </Transition>
        </nav>

        <!-- TOC: static -->
        <nav v-else-if="staticPost && toc.length >= 3" class="mt-8 rounded-xl border border-slate-200 bg-slate-50" aria-label="Table of contents">
          <button class="flex w-full items-center justify-between px-5 py-4 text-left" :aria-expanded="tocOpen" @click="tocOpen = !tocOpen">
            <span class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/></svg>
              In this article
              <span class="rounded-full bg-slate-200 px-1.5 py-0.5 text-[10px] font-bold text-slate-600">{{ toc.length }}</span>
            </span>
            <svg class="h-4 w-4 text-slate-400 transition-transform duration-200" :class="tocOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
          </button>
          <Transition enter-active-class="transition-all duration-200 ease-out" enter-from-class="opacity-0 max-h-0" enter-to-class="opacity-100 max-h-[600px]" leave-active-class="transition-all duration-150 ease-in" leave-from-class="opacity-100 max-h-[600px]" leave-to-class="opacity-0 max-h-0">
            <div v-if="tocOpen" class="overflow-hidden border-t border-slate-200 px-5 pb-5 pt-4">
              <ol class="space-y-1.5">
                <li v-for="item in toc" :key="item.anchor" :class="item.level === 'h3' ? 'ml-4' : ''">
                  <a :href="`#${item.anchor}`" class="text-sm text-brand-600 hover:underline" @click="tocOpen = false">{{ item.text }}</a>
                </li>
              </ol>
            </div>
          </Transition>
        </nav>

        <!-- CMS body -->
        <div
          v-if="cmsArticle"
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-serif prose-headings:font-bold
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-900"
        >
          <BlockRenderer :blocks="cmsArticle.body" />
        </div>

        <!-- Static body -->
        <div
          v-else
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-serif prose-headings:font-bold
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-900"
          v-html="bodyWithInlineCta"
        />

        <!-- Reactions -->
        <ClientOnly>
          <div v-if="ready && pageId" class="mt-10 rounded-2xl border border-slate-100 bg-slate-50 px-6 py-5">
            <p class="mb-4 text-center text-sm font-semibold text-slate-700">Was this article helpful?</p>
            <div class="flex justify-center gap-3">
              <button
                v-for="r in reactions" :key="r.type"
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
            <p class="mt-3 text-center text-xs text-slate-400">{{ stats ? fmtCount(stats.views) + ' nursing students have read this article' : '' }}</p>
          </div>
        </ClientOnly>

        <!-- Share -->
        <div class="mt-6">
          <ClientOnly><ShareButtons :title="postTitle" /></ClientOnly>
        </div>

        <!-- End-of-article CTA -->
        <div class="mt-10 rounded-2xl bg-brand-900 p-8">
          <div class="sm:flex sm:items-center sm:justify-between sm:gap-8">
            <div>
              <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-400">500+ BSN · MSN · DNP nurses available now</p>
              <h2 class="font-serif text-2xl font-bold text-white">Still staring at a blank page?</h2>
              <p class="mt-2 leading-relaxed text-brand-200">
                A real nurse who knows your subject can write your care plan, SOAP note, capstone,
                or essay — from scratch, clinically accurate, from $24/page.
              </p>
              <ul class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm text-brand-300">
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Grade or money back</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Zero AI — nurse-written</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> As fast as 3 hours</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Free Turnitin report</li>
              </ul>
            </div>
            <NuxtLink to="/order" class="mt-6 block shrink-0 rounded-xl bg-white px-8 py-3 text-center text-sm font-bold text-brand-700 transition-colors hover:bg-brand-50 sm:mt-0">
              Order my nursing paper →
            </NuxtLink>
          </div>
        </div>

        <!-- Author card -->
        <div v-if="cmsArticle?.author_name || staticPost?.author" class="mt-10 overflow-hidden rounded-2xl border border-slate-200 bg-white">
          <div class="flex items-start gap-5 border-b border-slate-100 bg-slate-50 px-6 py-6">
            <div class="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-2xl font-bold text-brand-700 ring-2 ring-white shadow-sm">
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
                  <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-300 group-hover:bg-brand-600 transition-colors" />
                  <div class="min-w-0">
                    <p class="text-sm font-medium leading-snug text-slate-800 group-hover:text-brand-700 transition-colors line-clamp-2">{{ p.title }}</p>
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

        <div class="mt-6">
          <EditorialProcess :published-at="postDate" />
        </div>

        <!-- Related posts -->
        <div v-if="(cmsArticle && cmsRelated?.length) || (!cmsArticle && related.length)" class="mt-16">
          <h2 class="mb-6 font-serif text-xl font-bold text-slate-900">More on {{ postCategory }}</h2>
          <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <template v-if="cmsArticle">
              <NuxtLink
                v-for="r in cmsRelated" :key="r.meta?.slug"
                :href="`/blog/${r.meta?.slug}`"
                class="card group flex flex-col transition-shadow hover:border-brand-200 hover:shadow-md"
              >
                <div class="mb-2 flex items-center gap-2">
                  <span class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">{{ r.category_name }}</span>
                  <span class="text-xs text-slate-400">{{ r.reading_time_minutes }} min</span>
                </div>
                <h3 class="flex-1 font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 line-clamp-2">{{ r.title }}</h3>
                <span class="mt-4 text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
              </NuxtLink>
            </template>
            <template v-else>
              <NuxtLink
                v-for="r in related" :key="r.slug"
                :href="`/blog/${r.slug}`"
                class="card group flex flex-col transition-shadow hover:border-brand-200 hover:shadow-md"
              >
                <div class="mb-2 flex items-center gap-2">
                  <span class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">{{ r.category }}</span>
                  <span class="text-xs text-slate-400">{{ r.readTime }}</span>
                </div>
                <h3 class="flex-1 font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">{{ r.title }}</h3>
                <p class="mt-2 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ r.excerpt }}</p>
                <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                  <time class="text-xs text-slate-400">{{ new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</time>
                  <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
                </div>
              </NuxtLink>
            </template>
          </div>
        </div>

      </article>

      <!-- ── Right: sticky sidebar ──────────────────────────────────── -->
      <div class="lg:sticky lg:top-24 lg:self-start">
        <BlogSidebar />
      </div>

    </div>
  </div>
</template>
