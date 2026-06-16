interface SiteSettings {
  site_name: string
  favicon_url: string | null
  og_image_url: string | null
  schema_org_logo_url: string | null
  google_analytics_id: string
  schema_org_name: string
  promo_bar_enabled: boolean
  promo_code: string
  promo_message: string
  promo_suffix: string
}

const _cache = ref<SiteSettings | null>(null)

export async function fetchSiteSettings(): Promise<SiteSettings | null> {
  if (_cache.value) return _cache.value
  const config = useRuntimeConfig()
  try {
    const effectiveBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase
    const data = await $fetch<SiteSettings>(`${effectiveBase}/cms-api/site-settings/`)
    _cache.value = data
    return data
  } catch {
    return null
  }
}
