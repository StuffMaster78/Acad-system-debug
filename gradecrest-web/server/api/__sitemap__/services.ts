// Returns all CMS service page URLs for @nuxtjs/sitemap dynamic source.
// Sitemap module fetches this endpoint at build/generate time.
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const apiBase = (config.apiBaseInternal as string) || config.public.apiBase || ''

  if (!apiBase) return []

  try {
    const resp = await $fetch<{ results: { slug: string; updated_at?: string }[] }>(
      `${apiBase}/cms-api/service-pages/`,
    )
    return (resp.results ?? []).map(s => ({
      loc:        `/services/${s.slug}`,
      changefreq: 'weekly',
      priority:   0.8,
      lastmod:    s.updated_at ?? undefined,
    }))
  } catch {
    return []
  }
})
