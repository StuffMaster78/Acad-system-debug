<script setup lang="ts">
const route = useRoute()
const slug = route.params.slug as string
const config = useRuntimeConfig()

const { getBySlug } = useServices()

// ── Step 1: check static service registry ─────────────────────────────────
const staticService = getBySlug(slug)

// ── Step 2: check CMS for a ServicePage with this slug ───────────────────
const apiBase = import.meta.server
  ? ((config as Record<string, unknown>).apiBaseInternal as string || 'http://localhost:8000')
  : (config.public.apiBase || '')

const { data: svcCheck } = await useAsyncData<boolean>(
  `slug-svc-check-${slug}`,
  async () => {
    if (staticService) return true
    try {
      const res = await $fetch<{ meta: { total_count: number } }>(
        `${apiBase}/api/v2/pages/`,
        {
          params: { type: 'cms_service_pages.ServicePage', slug, fields: 'title' },
          headers: import.meta.server
            ? { Host: (config as Record<string, unknown>).siteHostname as string || 'essaymaniacs.com' }
            : undefined,
        },
      )
      return (res?.meta?.total_count ?? 0) > 0
    } catch { return false }
  },
)

const isServicePage = svcCheck.value === true
</script>

<template>
  <div>
    <!-- Service page content -->
    <CmsServiceSlugPage v-if="isServicePage" :slug="slug" />
    <!-- Blog post content -->
    <CmsBlogPostPage v-else :slug="slug" />
  </div>
</template>
