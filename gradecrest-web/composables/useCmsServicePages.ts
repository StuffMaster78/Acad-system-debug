import type { CmsServicePage, CmsServicePageListItem } from '~/types/cms'

export async function fetchCmsServicePage(slug: string) {
  const config = useRuntimeConfig()
  const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

  if (import.meta.server && !apiBase) {
    return null
  }

  try {
    return await $fetch<CmsServicePage>(
      `${apiBase}/cms-api/service-pages/by-slug/${encodeURIComponent(slug)}/`,
    )
  } catch {
    return null
  }
}

export async function fetchCmsServicePages() {
  const config = useRuntimeConfig()
  const apiBase = (import.meta.server && (config.apiBaseInternal as string)) || config.public.apiBase || ''

  if (import.meta.server && !apiBase) {
    return []
  }

  try {
    const response = await $fetch<{ results: CmsServicePageListItem[] }>(
      `${apiBase}/cms-api/service-pages/`,
    )
    return response.results ?? []
  } catch {
    return []
  }
}
