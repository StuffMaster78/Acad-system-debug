<script setup lang="ts">
const route   = useRoute()
const slug    = route.params.slug as string
const config  = useRuntimeConfig()
const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

interface Block { type: string; value: unknown }

interface CmsPost {
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

const { data: post } = await useAsyncData<CmsPost | null>(
  `wc-blog-${slug}`,
  async () => {
    if (!apiBase) return null
    try {
      const res = await $fetch<{ items: CmsPost[] }>(
        `${apiBase}/api/v2/pages/`,
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

if (!post.value) {
  throw createError({ statusCode: 404, message: 'Post not found' })
}

const { data: relatedPosts } = await useAsyncData<CmsPost[]>(
  `wc-blog-related-${slug}`,
  async () => {
    if (!apiBase || !post.value) return []
    try {
      const res = await $fetch<{ items: CmsPost[] }>(
        `${apiBase}/api/v2/pages/`,
        {
          params: {
            type: 'cms_blog.BlogPostPage',
            fields: 'title,excerpt,reading_time_minutes,category_name,thumbnail',
            order: '-first_published_at',
            limit: 4,
          },
        },
      )
      return (res.items ?? []).filter(p => p.meta?.slug !== slug).slice(0, 3)
    } catch { return [] }
  },
)

const postTitle    = computed(() => post.value?.meta?.seo_title || post.value?.title || '')
const postExcerpt  = computed(() => post.value?.meta?.search_description || post.value?.excerpt || '')
const postDate     = computed(() => post.value?.canonical_published_at || post.value?.meta?.first_published_at || '')
const postImage    = computed(() => post.value?.thumbnail?.url || null)
const postCategory = computed(() => post.value?.category_name || '')

const tocOpen = ref(false)
onMounted(() => { tocOpen.value = window.innerWidth >= 1024 })

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

function authorInitials(name: string | undefined) {
  if (!name) return 'W'
  const parts = name.trim().split(/\s+/)
  return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name[0].toUpperCase()
}

// ── Render body blocks ────────────────────────────────────────────────────────
function renderBlocks(blocks: Block[]): string {
  return blocks.map(b => renderBlock(b)).join('')
}

function slugify(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function renderBlock(b: Block): string {
  const { type, value } = b

  if (type === 'rich_text') {
    return typeof value === 'string' ? value : ''
  }

  if (type === 'heading') {
    const v = value as { text: string; level?: string }
    const level = v.level || 'h2'
    const id = slugify(v.text)
    return `<${level} id="${id}">${v.text}</${level}>`
  }

  if (type === 'image') {
    const v = value as { image?: { url: string; alt?: string }; caption?: string }
    if (!v.image?.url) return ''
    const caption = v.caption ? `<figcaption>${v.caption}</figcaption>` : ''
    return `<figure><img src="${v.image.url}" alt="${v.image.alt ?? ''}" />${caption}</figure>`
  }

  if (type === 'blockquote') {
    const v = value as { quote: string; attribution?: string }
    const attr = v.attribution ? `<cite>${v.attribution}</cite>` : ''
    return `<blockquote><p>${v.quote}</p>${attr}</blockquote>`
  }

  if (type === 'callout') {
    const v = value as { body: string; style?: string }
    return `<div class="callout callout-${v.style ?? 'note'}">${v.body}</div>`
  }

  if (type === 'code') {
    const v = value as { code: string; language?: string }
    return `<pre><code class="language-${v.language ?? 'text'}">${v.code}</code></pre>`
  }

  // Unsupported block types are silently skipped
  return ''
}

const bodyHtml = computed(() => post.value?.body ? renderBlocks(post.value.body) : '')

// ── TOC from body ─────────────────────────────────────────────────────────────
interface TocItem { id: string; text: string; level: string }

const toc = computed<TocItem[]>(() => {
  const items: TocItem[] = []
  for (const block of post.value?.body ?? []) {
    if (block.type === 'heading') {
      const v = block.value as { text: string; level?: string }
      items.push({ id: slugify(v.text), text: v.text, level: v.level || 'h2' })
    }
    if (block.type === 'rich_text' && typeof block.value === 'string') {
      const re = /<h([23])[^>]*id="([^"]*)"[^>]*>(.*?)<\/h\1>/gi
      let m: RegExpExecArray | null
      while ((m = re.exec(block.value)) !== null) {
        items.push({ id: m[2], text: m[3].replace(/<[^>]+>/g, ''), level: `h${m[1]}` })
      }
    }
  }
  return items
})

const siteUrl     = config.public.siteUrl || 'https://writerscreek.com'
const canonicalUrl = `${siteUrl}/blog/${slug}`

useSeoMeta({
  title:                postTitle,
  description:          postExcerpt,
  ogTitle:              postTitle,
  ogDescription:        postExcerpt,
  ogImage:              postImage,
  ogType:               'article',
  articlePublishedTime: postDate,
})

useHead({
  link: [{ rel: 'canonical', href: canonicalUrl }],
  script: computed(() => [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline:      postTitle.value,
      description:   postExcerpt.value,
      datePublished: postDate.value,
      ...(postImage.value ? { image: postImage.value } : {}),
      url: canonicalUrl,
      author: post.value?.author_name
        ? { '@type': 'Person', name: post.value.author_name }
        : { '@type': 'Organization', name: 'Writers Creek' },
      publisher: {
        '@type': 'Organization', name: 'Writers Creek',
        url: 'https://writerscreek.com',
        logo: { '@type': 'ImageObject', url: 'https://writerscreek.com/favicon.svg' },
      },
    }),
  }, {
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://writerscreek.com/' },
        { '@type': 'ListItem', position: 2, name: 'Blog', item: 'https://writerscreek.com/blog' },
        { '@type': 'ListItem', position: 3, name: postTitle.value, item: canonicalUrl },
      ],
    }),
  }]),
})
</script>

<template>
  <div class="section">

    <!-- Breadcrumb + meta -->
    <nav class="mb-8 flex items-center gap-2 text-xs text-slate-400" aria-label="Breadcrumb">
      <NuxtLink href="/blog" class="font-medium text-brand-600 hover:underline">Blog</NuxtLink>
      <span>›</span>
      <span v-if="postCategory" class="rounded-full bg-brand-50 px-2 py-0.5 font-semibold text-brand-700">{{ postCategory }}</span>
    </nav>

    <div class="grid gap-12 lg:grid-cols-[1fr_280px]">

      <!-- ── Article ─────────────────────────────────────────────────────── -->
      <article class="min-w-0">

        <!-- Cover image -->
        <div v-if="postImage" class="mb-10 overflow-hidden rounded-2xl">
          <img :src="postImage" :alt="postTitle" class="h-64 w-full object-cover sm:h-80" />
        </div>

        <!-- Category + meta -->
        <div class="mb-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
          <span v-if="postCategory" class="rounded-full bg-brand-50 px-3 py-1 font-semibold text-brand-700">{{ postCategory }}</span>
          <span v-if="post?.reading_time_minutes">{{ post.reading_time_minutes }} min read</span>
          <time v-if="postDate">{{ fmtDate(postDate) }}</time>
        </div>

        <!-- Title + excerpt -->
        <h1 class="text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">{{ postTitle }}</h1>
        <p v-if="postExcerpt" class="mt-4 text-lg leading-relaxed text-slate-600">{{ postExcerpt }}</p>

        <!-- Author byline -->
        <div v-if="post?.author_name" class="mt-6 flex items-center gap-3 border-t border-slate-100 pt-5">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
            {{ authorInitials(post.author_name) }}
          </div>
          <div>
            <p class="text-sm font-semibold text-slate-900">{{ post.author_name }}</p>
            <p v-if="post.author_credentials" class="text-xs text-slate-500">{{ post.author_credentials }}</p>
          </div>
        </div>

        <!-- TOC -->
        <nav
          v-if="toc.length >= 3"
          class="mt-8 rounded-xl border border-slate-200 bg-slate-50"
          aria-label="Table of contents"
        >
          <button
            class="flex w-full items-center justify-between px-5 py-4 text-left"
            :aria-expanded="tocOpen"
            @click="tocOpen = !tocOpen"
          >
            <span class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h10"/></svg>
              In this article
              <span class="rounded-full bg-slate-200 px-1.5 py-0.5 text-[10px] font-bold text-slate-600">{{ toc.length }}</span>
            </span>
            <svg
              class="h-4 w-4 text-slate-400 transition-transform duration-200"
              :class="tocOpen ? 'rotate-180' : ''"
              fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 max-h-0"
            enter-to-class="opacity-100 max-h-[600px]"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 max-h-[600px]"
            leave-to-class="opacity-0 max-h-0"
          >
            <div v-if="tocOpen" class="overflow-hidden border-t border-slate-200 px-5 pb-5 pt-4">
              <ol class="space-y-1.5">
                <li v-for="item in toc" :key="item.id" :class="item.level === 'h3' ? 'ml-4' : ''">
                  <a
                    :href="`#${item.id}`"
                    class="text-sm text-brand-600 hover:underline"
                    @click="tocOpen = false"
                  >{{ item.text }}</a>
                </li>
              </ol>
            </div>
          </Transition>
        </nav>

        <!-- Article body -->
        <div
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-bold prose-headings:tracking-tight
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-900
                 prose-blockquote:border-brand-400 prose-blockquote:text-slate-700
                 prose-pre:bg-slate-900 prose-code:text-brand-600"
          v-html="bodyHtml"
        />

        <!-- End-of-article CTA -->
        <div class="mt-12 rounded-2xl bg-slate-900 p-8">
          <div class="sm:flex sm:items-center sm:justify-between sm:gap-8">
            <div>
              <p class="mb-1 text-xs font-bold uppercase tracking-widest text-brand-400">Writers Creek</p>
              <h2 class="text-2xl font-bold text-white">Write at your level. Get paid fairly.</h2>
              <p class="mt-2 leading-relaxed text-slate-300">
                Credential-verified writers. Level-based rates from $18–$45/page. Bi-weekly payouts without chasing.
              </p>
              <ul class="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-400">
                <li class="flex items-center gap-1"><span class="text-brand-400">✓</span> Postgrad credentials required</li>
                <li class="flex items-center gap-1"><span class="text-brand-400">✓</span> Subject-matched assignments only</li>
                <li class="flex items-center gap-1"><span class="text-brand-400">✓</span> Apply in 10 minutes</li>
              </ul>
            </div>
            <NuxtLink
              to="/apply"
              class="mt-6 block shrink-0 rounded-xl bg-brand-600 px-8 py-3 text-center text-sm font-bold text-white transition-colors hover:bg-brand-500 sm:mt-0"
            >
              Apply to write →
            </NuxtLink>
          </div>
        </div>

        <!-- Author bio -->
        <div v-if="post?.author_name" class="mt-10 overflow-hidden rounded-2xl border border-slate-200">
          <div class="flex items-start gap-5 border-b border-slate-100 bg-slate-50 px-6 py-6">
            <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-xl font-bold text-brand-700 shadow-sm ring-2 ring-white">
              {{ authorInitials(post.author_name) }}
            </div>
            <div class="min-w-0">
              <p class="text-lg font-bold text-slate-900">{{ post.author_name }}</p>
              <p v-if="post.author_credentials" class="mt-0.5 text-sm font-medium text-slate-500">{{ post.author_credentials }}</p>
            </div>
          </div>
          <div v-if="post.author_bio" class="px-6 py-5">
            <p class="text-sm leading-7 text-slate-600">{{ post.author_bio }}</p>
          </div>
        </div>

        <!-- Related posts -->
        <div v-if="relatedPosts?.length" class="mt-16">
          <h2 class="mb-6 text-xl font-bold text-slate-900">More from the blog</h2>
          <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="r in relatedPosts"
              :key="r.meta?.slug"
              :to="`/blog/${r.meta?.slug}`"
              class="group flex flex-col rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md"
            >
              <div class="mb-2 flex items-center gap-2 text-xs text-slate-500">
                <span
                  v-if="r.category_name"
                  class="rounded-full bg-brand-50 px-2 py-0.5 font-semibold text-brand-700"
                >{{ r.category_name }}</span>
                <span v-if="r.reading_time_minutes">{{ r.reading_time_minutes }} min</span>
              </div>
              <h3 class="flex-1 text-sm font-bold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 line-clamp-3">{{ r.title }}</h3>
              <span class="mt-4 text-xs font-semibold text-brand-600 group-hover:underline">Read →</span>
            </NuxtLink>
          </div>
        </div>

      </article>

      <!-- ── Sticky sidebar ─────────────────────────────────────────────── -->
      <aside class="hidden lg:block">
        <div class="sticky top-28 space-y-6">

          <!-- Quick apply card -->
          <div class="rounded-2xl border border-brand-200 bg-brand-50 p-6">
            <p class="text-xs font-bold uppercase tracking-widest text-brand-600">Join Writers Creek</p>
            <p class="mt-3 text-base font-bold leading-snug text-slate-900">Earn $18–$45/page writing in your subject area.</p>
            <ul class="mt-4 space-y-2 text-sm text-slate-600">
              <li class="flex items-center gap-2"><span class="text-brand-600">✓</span> Postgrad credentials required</li>
              <li class="flex items-center gap-2"><span class="text-brand-600">✓</span> Bi-weekly payouts</li>
              <li class="flex items-center gap-2"><span class="text-brand-600">✓</span> Application takes 10 min</li>
            </ul>
            <NuxtLink
              to="/apply"
              class="mt-5 block w-full rounded-xl bg-brand-600 py-3 text-center text-sm font-bold text-white transition-colors hover:bg-brand-700"
            >
              Apply now →
            </NuxtLink>
          </div>

          <!-- Earnings card -->
          <div class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">Writer levels</p>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between">
                <span class="text-slate-600">Entry</span>
                <span class="font-semibold text-slate-900">$18–$22/page</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-600">Standard</span>
                <span class="font-semibold text-slate-900">$24–$28/page</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-600">Senior</span>
                <span class="font-semibold text-slate-900">$30–$36/page</span>
              </div>
              <div class="flex justify-between border-t border-slate-100 pt-3">
                <span class="font-bold text-slate-900">Expert</span>
                <span class="font-bold text-brand-600">$38–$45/page</span>
              </div>
            </div>
            <NuxtLink to="/earnings" class="mt-4 block text-xs font-semibold text-brand-600 hover:underline">
              Full earnings breakdown →
            </NuxtLink>
          </div>

          <!-- Recent posts -->
          <div v-if="relatedPosts?.length" class="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <p class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">More articles</p>
            <div class="space-y-4">
              <NuxtLink
                v-for="r in relatedPosts"
                :key="r.meta?.slug"
                :to="`/blog/${r.meta?.slug}`"
                class="group flex gap-3 text-sm"
              >
                <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-300 transition-colors group-hover:bg-brand-600" />
                <span class="leading-snug text-slate-700 line-clamp-2 group-hover:text-brand-700 transition-colors">{{ r.title }}</span>
              </NuxtLink>
            </div>
          </div>

        </div>
      </aside>

    </div>

  </div>
</template>
