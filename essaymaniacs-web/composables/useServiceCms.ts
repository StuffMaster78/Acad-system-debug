export interface CmsServicePage {
  id: number
  title: string
  slug: string
  hero_headline: string
  hero_sub: string
  pricing_from: string | null
  pricing_to: string | null
  turnaround_hours_fastest: number | null
  turnaround_hours_standard: number | null
  includes_items: { type: string; id: string; value: string }[]
  delivers_items: { type: string; id: string; value: string }[]
  who_for: string
  primary_cta_text: string
  primary_cta_url: string
  reviewer: { name: string; role: string } | null
  last_substantive_update: string | null
  hero_image?: { url: string } | null
  thumbnail?: { url: string } | null
  body: CmsBlock[]
  schema?: Record<string, unknown>
}

export interface CmsBlock {
  type: string
  id: string
  value: unknown
}

export function useServiceCms(serviceSlug: string) {
  const config = useRuntimeConfig()
  const apiBase = import.meta.server
    ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
    : (config.public.apiBase || '')
  const extraHeaders = import.meta.server
    ? { Host: (config as Record<string, unknown>).siteHostname as string || 'essaymaniacs.com' }
    : undefined

  const { data, status, error } = useFetch<{ items: CmsServicePage[] }>(
    `${apiBase}/api/v2/pages/`,
    {
      key: `svc-cms-em-${serviceSlug}`,
      headers: extraHeaders,
      query: {
        type: 'cms_service_pages.ServicePage',
        slug: serviceSlug,
        fields: [
          'title', 'slug',
          'hero_headline', 'hero_sub',
          'pricing_from', 'pricing_to',
          'turnaround_hours_fastest', 'turnaround_hours_standard',
          'includes_items', 'delivers_items', 'who_for',
          'primary_cta_text', 'primary_cta_url',
          'reviewer', 'last_substantive_update', 'body',
        ].join(','),
      },
      onResponseError() {},
    },
  )

  const page = computed<CmsServicePage | null>(() => data.value?.items?.[0] ?? null)
  const hasContent = computed(() => !!page.value?.body?.length)
  const loading = computed(() => status.value === 'pending')

  return { page, hasContent, loading, error }
}
