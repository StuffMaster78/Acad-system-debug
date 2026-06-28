// Returns all CMS service and blog page URLs for @nuxtjs/sitemap dynamic source.
// Sitemap module fetches this endpoint at build/generate time.
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const apiBase = (config.apiBaseInternal as string) || config.public.apiBase || ''

  if (!apiBase) return []

  const urls: { loc: string; changefreq: string; priority: number; lastmod?: string }[] = []

  try {
    const resp = await $fetch<{ results: { slug: string; updated_at?: string }[] }>(
      `${apiBase}/cms-api/service-pages/`,
    )
    for (const s of resp.results ?? []) {
      urls.push({ loc: `/services/${s.slug}`, changefreq: 'weekly', priority: 0.8, lastmod: s.updated_at })
    }
  } catch { /* service pages unavailable during build — skip */ }

  try {
    const resp = await $fetch<{ items: { meta: { slug: string; first_published_at?: string } }[] }>(
      `${apiBase}/wagtail/api/v2/pages/`,
      { query: { type: 'cms_blog.BlogPostPage', live: true, fields: 'slug', limit: 500 } },
    )
    for (const p of resp.items ?? []) {
      if (p.meta?.slug) {
        urls.push({ loc: `/blog/${p.meta.slug}`, changefreq: 'monthly', priority: 0.6, lastmod: p.meta.first_published_at })
      }
    }
  } catch { /* blog posts unavailable during build — skip */ }

  return urls
})
