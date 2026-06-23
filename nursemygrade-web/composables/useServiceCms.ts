export interface CmsServicePage {
  id: number
  title: string
  slug: string
  pricing_from: string | null
  pricing_to: string | null
  turnaround_hours_fastest: number | null
  turnaround_hours_standard: number | null
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
  // In SSR, call Django directly with the site hostname so the API filters
  // by site correctly. On the client, route through the /api/v2 proxy.
  const apiBase = import.meta.server
    ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
    : (config.public.apiBase || '')
  const extraHeaders = import.meta.server
    ? { Host: config.siteHostname as string || 'nursemygrade.com' }
    : undefined
  const fields = [
    'title', 'slug', 'pricing_from', 'pricing_to',
    'turnaround_hours_fastest', 'turnaround_hours_standard',
    'primary_cta_text', 'primary_cta_url',
    'reviewer', 'last_substantive_update', 'body',
  ].join(',')

  const { data, status, error } = useFetch<{ items: CmsServicePage[] }>(
    `${apiBase}/api/v2/pages/`,
    {
      query: { type: 'cms_service_pages.ServicePage', slug: serviceSlug, fields },
      headers: extraHeaders,
      onResponseError() {},
    },
  )

  const page = computed<CmsServicePage | null>(() => data.value?.items?.[0] ?? null)
  const hasContent = computed(() => !!page.value?.body?.length)
  const loading = computed(() => status.value === 'pending')

  return { page, hasContent, loading, error }
}
