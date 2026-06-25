// Server route called by @nuxtjs/sitemap at build time.
// Fetches live blog post slugs from Wagtail and returns [{loc}].
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const base = config.public.apiBase || ''

  const urls: { loc: string }[] = []

  try {
    const res = await $fetch<{ items: { meta: { slug: string } }[] }>(
      `${base}/api/v2/pages/`,
      {
        query: {
          type: 'cms_blog.BlogPostPage',
          live: true,
          fields: 'slug',
          limit: 500,
        },
      },
    )
    for (const item of res.items ?? []) {
      if (item.meta?.slug) urls.push({ loc: `/${item.meta.slug}` })
    }
  } catch { /* Wagtail unavailable during build — skip */ }

  return urls
})
