/**
 * Server route called by @nuxtjs/sitemap at build time.
 * Fetches live service and blog slugs from the Wagtail API and returns
 * them as [{loc}] — the format the sitemap module expects.
 *
 * The sitemap module auto-discovers all pre-rendered static pages via
 * crawlLinks; this route adds dynamic slugs that might not be linked
 * from any pre-rendered page yet.
 */
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const base = config.public.apiBase || ''

  const urls: { loc: string }[] = []

  try {
    // Blog posts
    const blogRes = await $fetch<{ items: { meta: { slug: string } }[] }>(
      `${base}/api/v2/pages/`,
      {
        query: {
          type: 'cms_blog.BlogPostPage',
          live: true,
          fields: 'slug',
          limit: 500,
        },
      }
    )
    for (const item of blogRes.items ?? []) {
      if (item.meta?.slug) urls.push({ loc: `/blog/${item.meta.slug}` })
    }
  } catch { /* Wagtail unavailable during build — skip */ }

  try {
    // Service pages
    const svcRes = await $fetch<{ items: { meta: { slug: string } }[] }>(
      `${base}/api/v2/pages/`,
      {
        query: {
          type: 'cms_service_pages.ServicePage',
          live: true,
          fields: 'slug',
          limit: 100,
        },
      }
    )
    for (const item of svcRes.items ?? []) {
      if (item.meta?.slug) urls.push({ loc: `/services/${item.meta.slug}` })
    }
  } catch { /* Wagtail unavailable during build — skip */ }

  return urls
})
