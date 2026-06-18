export interface CmsBlock<T = unknown> {
  id?: string | null
  type: string
  value: T
}

export interface CmsServicePageListItem {
  id: number
  title: string
  slug: string
  nav_label?: string
  url?: string
  template_key: string
  search_description?: string
  category?: {
    name: string
    slug: string
  } | null
  pricing_from?: string | null
  pricing_to?: string | null
  turnaround_hours_fastest?: number | null
  turnaround_hours_standard?: number | null
  primary_cta_text: string
  primary_cta_url: string
}

export interface CmsServicePage extends CmsServicePageListItem {
  meta: {
    seo_title: string
    search_description?: string
    first_published_at?: string | null
    last_published_at?: string | null
    last_substantive_update?: string | null
  }
  hero: {
    headline: string
    subheadline?: string
  }
  includes_items: string[]
  delivers_items: string[]
  who_for?: string
  body: CmsBlock[]
  faqs: Array<{
    question: string
    answer: string
  }>
  reviewer?: {
    name: string
    slug: string
    credentials?: string
  } | null
  related_services: CmsServicePageListItem[]
  schema?: Record<string, unknown>
}
