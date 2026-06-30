<script setup lang="ts">
import type { CmsServicePage } from '~/composables/useServiceCms'

const route = useRoute()
const slug  = route.params.slug as string

const { getBySlug } = useServices()

// ── Step 1: check static service registry ─────────────────────────────────
const staticService = getBySlug(slug)

// ── Step 2: check CMS for a ServicePage ───────────────────────────────────
const config  = useRuntimeConfig()
const apiBase = config.public.apiBase || ''

const { data: svcCheck } = await useAsyncData<boolean>(
  `slug-svc-check-${slug}`,
  async () => {
    if (staticService) return true
    try {
      const res = await $fetch<{ meta: { total_count: number } }>(
        `${apiBase}/api/v2/pages/`,
        { params: { type: 'cms_service_pages.ServicePage', slug, fields: 'title' } },
      )
      return (res?.meta?.total_count ?? 0) > 0
    } catch { return false }
  },
)

const isServicePage = svcCheck.value === true

// ── Step 3a: fetch CMS service page at page level (when it's a service) ───
// Same /wagtail proxy pattern — sets Host: researchpapermate.com internally.
const svcFields = [
  'title', 'slug', 'pricing_from', 'pricing_to',
  'turnaround_hours_fastest', 'turnaround_hours_standard',
  'primary_cta_text', 'primary_cta_url',
  'reviewer', 'last_substantive_update', 'hero_image', 'thumbnail', 'body',
].join(',')

const { data: cmsServicePage } = await useAsyncData<CmsServicePage | null>(
  `svc-rpm-${slug}`,
  async () => {
    if (!isServicePage) return null
    try {
      const res = await $fetch<{ items: CmsServicePage[] }>(
        '/wagtail/api/v2/pages/',
        { params: { type: 'cms_service_pages.ServicePage', slug, fields: svcFields } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── Step 3b: fetch blog post at page level (when it's a blog post) ────────
interface CmsArticle {
  id: number
  meta: { slug: string; first_published_at: string; seo_title: string; search_description: string }
  title: string; excerpt: string; body: { type: string; value: unknown }[]
  reading_time_minutes: number; word_count: number; category_name: string
  tag_names: string[]; thumbnail: { url: string } | null
  author_name: string; author_credentials: string; author_bio: string
  canonical_published_at: string | null; last_substantive_update: string | null
  lead_magnet: { slug: string; title: string; description: string } | null
}

const { data: blogArticle } = await useAsyncData<CmsArticle | null>(
  `rpm-blog-${slug}`,
  async () => {
    if (isServicePage) return null
    try {
      const res = await $fetch<{ items: CmsArticle[] }>(
        '/wagtail/api/v2/pages/',
        { params: { type: 'cms_blog.BlogPostPage', slug, fields: '*' } },
      )
      return res.items?.[0] ?? null
    } catch { return null }
  },
)

// ── 404 guard ─────────────────────────────────────────────────────────────
const { getBySlug: getBlogBySlug } = useBlog()
const staticPost = isServicePage ? null : (blogArticle.value ? null : getBlogBySlug(slug))
if (!isServicePage && !blogArticle.value && !staticPost) {
  throw createError({ statusCode: 404, fatal: true, message: 'Page not found' })
}
</script>

<template>
  <div>
    <!-- Service page: CMS data fetched at page level, passed as prop -->
    <ServiceSlugPage v-if="isServicePage" :slug="slug" :cms-page="cmsServicePage ?? null" />
    <!-- Blog post: article fetched at page level, passed as prop -->
    <BlogPostPage v-else :slug="slug" :article="blogArticle ?? null" />
  </div>
</template>
