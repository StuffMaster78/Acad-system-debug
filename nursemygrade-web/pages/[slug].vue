<script setup lang="ts">
// Root-level catch-all: redirects old SEO URLs like /reliable-and-cheap-bsn-writing-service
// to their canonical /services/[slug] or /blog/[slug] path.
const route = useRoute()
const slug = route.params.slug as string
const config = useRuntimeConfig()
const base = String(config.public.apiBase || '')

const { data: redirect } = await useAsyncData<string | null>(`root-redirect-${slug}`, async () => {
  try {
    // Try ServicePage first
    const svc = await $fetch<{ meta: { total_count: number } }>(`${base}/api/v2/pages/`, {
      params: { type: 'cms_service_pages.ServicePage', slug, fields: 'title' },
    })
    if ((svc as any).meta?.total_count > 0) return `/services/${slug}`

    // Try BlogPostPage
    const blog = await $fetch<{ meta: { total_count: number } }>(`${base}/api/v2/pages/`, {
      params: { type: 'cms_blog.BlogPostPage', slug, fields: 'title' },
    })
    if ((blog as any).meta?.total_count > 0) return `/blog/${slug}`
  } catch { /* fall through to 404 */ }
  return null
})

if (redirect.value) {
  await navigateTo(redirect.value, { redirectCode: 301 })
} else {
  throw createError({ statusCode: 404, statusMessage: 'Page not found' })
}
</script>

<template><div /></template>
