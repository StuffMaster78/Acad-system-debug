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
  body: CmsBlock[]
}

export interface CmsBlock {
  type: string
  id: string
  value: unknown
}

export function useServiceCms(serviceSlug: string) {
  const config = useRuntimeConfig()
  // /wagtail/[...path] is a Nitro server route that proxies to Django with the
  // correct Host header. Pass the full path so useFetch doesn't strip the
  // /wagtail prefix (ofetch drops the baseURL path when the path starts with /).
  const wagtailBase = `${config.public.apiBase || ''}/wagtail`

  const { data, status, error } = useFetch<{ items: CmsServicePage[] }>(
    `${wagtailBase}/api/v2/pages/`,
    {
      query: {
        type: 'cms_service_pages.ServicePage',
        slug: serviceSlug,
        fields: [
          'title', 'slug', 'pricing_from', 'pricing_to',
          'turnaround_hours_fastest', 'turnaround_hours_standard',
          'primary_cta_text', 'primary_cta_url',
          'reviewer', 'last_substantive_update', 'body', 'schema',
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
