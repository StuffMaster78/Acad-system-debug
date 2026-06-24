<script setup lang="ts">
const route   = useRoute()
const slug    = route.params.slug as string
const config  = useRuntimeConfig()
const apiBase    = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''
// Rewrite relative /media/ URLs to absolute so the browser can load images.
// On the server apiBase is the internal Django URL; in prod media is on CDN.
function absMedia(url: string | null | undefined): string | null {
  if (!url || !url.startsWith('/media/') || !apiBase.includes('localhost')) return url ?? null
  return `${apiBase}${url}`
}

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
      const item = res.items?.[0] ?? null
      if (item?.thumbnail?.url) item.thumbnail.url = absMedia(item.thumbnail.url) ?? item.thumbnail.url
      return item
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


function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

function authorInitials(name: string | undefined) {
  if (!name) return 'W'
  const parts = name.trim().split(/\s+/)
  return parts.length >= 2 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : name[0].toUpperCase()
}

// ── Link rewriting ────────────────────────────────────────────────────────────
const { getAll: getAllServices } = useServices()
const _wcServiceSlugs = new Set(getAllServices().map(s => s.slug))
const _wcFixedRoutes  = new Set([
  'order', 'pricing', 'contact', 'about', 'faq', 'blog', 'services',
  'authors', 'privacy', 'terms', 'refunds', 'resources', 'login', 'register',
])

function slugifyHeading(text: string): string {
  return text.toLowerCase().replace(/[^\w\s-]/g, '').trim().replace(/[\s_]+/g, '-').replace(/-+/g, '-')
}

function injectHeadingIds(html: string): string {
  return html.replace(
    /<(h[23])([^>]*)>([\s\S]*?)<\/h[23]>/gi,
    (orig, tag, attrs, inner) => {
      if (/\bid\s*=/.test(attrs)) return orig
      const id = slugifyHeading(inner.replace(/<[^>]+>/g, '').trim())
      return id ? `<${tag}${attrs} id="${id}" class="scroll-mt-24">${inner}</${tag}>` : orig
    },
  )
}

function rewriteLinks(html: string): string {
  if (!html) return html
  html = injectHeadingIds(html)
  // Strip legacy .php extension from internal relative links before slug routing.
  html = html.replace(/href="(\/[^"#?]*)\.php([?#][^"]*)?"(?=[^>]*>)/gi,
    (_, path, qs) => `href="${path}${qs ?? ''}"`)
  let out = html.replace(/href="\/([a-z][a-z0-9-]*)"/g, (_match, slug) => {
    if (_wcServiceSlugs.has(slug)) return `href="/services/${slug}"`
    if (_wcFixedRoutes.has(slug))  return _match
    return `href="/blog/${slug}"`
  })
  out = out.replace(/(<a\s[^>]*href="https?:\/\/[^"]*"[^>]*)>/gi, (m, attrs) =>
    /target=/i.test(attrs) ? m : `${attrs} target="_blank" rel="noopener noreferrer">`
  )
  return out
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
    return typeof value === 'string' ? rewriteLinks(value) : ''
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
    return `<div class="callout callout-${v.style ?? 'note'}">${rewriteLinks(v.body)}</div>`
  }

  if (type === 'code') {
    const v = value as { code: string; language?: string }
    return `<pre><code class="language-${v.language ?? 'text'}">${v.code}</code></pre>`
  }

  if (type === 'table') {
    const v = value as { style?: string; caption?: string; table?: { data?: string[][]; first_row_is_table_header?: boolean; first_col_is_header?: boolean } }
    const rows = v.table?.data ?? []
    if (!rows.length) return ''
    const hasHead = v.table?.first_row_is_table_header
    const hasCol  = v.table?.first_col_is_header
    const cap     = v.caption ? `<p class="mb-2 text-[11px] font-bold uppercase tracking-widest text-slate-400">${v.caption}</p>` : ''
    const thead   = hasHead && rows[0]
      ? `<thead><tr>${rows[0].map(c => `<th class="bg-slate-900 px-5 py-3 text-left text-[11px] font-bold uppercase tracking-wider text-slate-300 whitespace-nowrap">${c}</th>`).join('')}</tr></thead>`
      : ''
    const body = rows.slice(hasHead ? 1 : 0).map(row =>
      `<tr class="border-t border-slate-100 transition-colors hover:bg-slate-50/60">${row.map((c, ci) =>
        ci === 0 && hasCol
          ? `<th class="border-r border-slate-100 bg-slate-50 px-5 py-3.5 text-left text-[13px] font-semibold whitespace-nowrap">${c}</th>`
          : `<td class="px-5 py-3.5 text-[13px] leading-relaxed text-slate-600">${c}</td>`,
      ).join('')}</tr>`,
    ).join('')
    return `${cap}<div class="overflow-hidden rounded-2xl border border-slate-200 shadow-sm"><div class="overflow-x-auto"><table class="w-full border-collapse text-sm">${thead}<tbody>${body}</tbody></table></div></div>`
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
      // Use slugifyHeading — matches what injectHeadingIds injects into the rendered HTML
      for (const m of block.value.matchAll(/<h([23])[^>]*>([\s\S]*?)<\/h[23]>/gi)) {
        const text = m[2].replace(/<[^>]+>/g, '').trim()
        if (text) items.push({ id: slugifyHeading(text), text, level: `h${m[1]}` })
      }
    }
  }
  return items
})

// ── Engagement ───────────────────────────────────────────────────────────────
const { stats, myReact, ready: engReady, react, reactionCount, fmtCount } = useEngagement(slug)

const reactions = [
  { type: 'helpful'    as const, emoji: '👍', label: 'Helpful'    },
  { type: 'love'       as const, emoji: '❤️', label: 'Love this'  },
  { type: 'insightful' as const, emoji: '💡', label: 'Insightful' },
]

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
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
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

        <!-- Article TOC -->
        <ArticleToc
          v-if="toc.length >= 3"
          :items="toc"
          variant="cards"
        />

        <!-- Article body -->
        <div
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-bold prose-headings:tracking-tight
                 prose-a:text-brand-600 prose-a:underline prose-a:decoration-brand-300 hover:prose-a:decoration-brand-600
                 prose-strong:text-slate-900
                 prose-blockquote:border-brand-400 prose-blockquote:text-slate-700
                 prose-pre:bg-slate-900 prose-code:text-brand-600"
          v-html="bodyHtml"
        />

        <!-- Reaction bar -->
        <div v-if="engReady && stats" class="mt-10 rounded-2xl border border-slate-100 bg-white p-6 shadow-sm text-center">
          <p class="mb-4 text-sm font-semibold text-slate-700">Was this article helpful?</p>
          <div class="flex justify-center gap-3">
            <button
              v-for="r in reactions"
              :key="r.type"
              class="flex items-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold transition-all"
              :class="myReact === r.type
                ? 'border-brand-400 bg-brand-50 text-brand-700 shadow-sm'
                : 'border-slate-200 bg-white text-slate-600 hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700'"
              @click="react(r.type)"
            >
              <span>{{ r.emoji }}</span>
              <span>{{ r.label }}</span>
              <span
                v-if="reactionCount(r.type) > 0"
                class="rounded-full px-1.5 py-0.5 text-[11px] font-bold"
                :class="myReact === r.type ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-500'"
              >{{ fmtCount(reactionCount(r.type)) }}</span>
            </button>
          </div>
        </div>

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

<style scoped>
:deep(a[target="_blank"][href^="http"])::after {
  content: '\2197';
  display: inline-block;
  font-size: 0.65em;
  vertical-align: super;
  margin-left: 0.15em;
  opacity: 0.7;
}
</style>
