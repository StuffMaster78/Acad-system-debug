<template>
  <div class="min-h-screen bg-gray-50 py-10 px-4">
    <div class="max-w-3xl mx-auto bg-white shadow-sm rounded-xl p-6 md:p-8">
      <header class="mb-6 border-b border-gray-200 pb-4">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900">
          {{ page?.title || 'Terms & Conditions' }}
        </h1>
        <p v-if="metaInfo" class="mt-2 text-sm text-gray-500">
          {{ metaInfo }}
        </p>
      </header>

      <section v-if="loading" class="py-10 text-center text-gray-500">
        <div class="inline-flex items-center justify-center mb-3">
          <span class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></span>
        </div>
        <p>Loading terms &amp; conditions…</p>
      </section>

      <section v-else-if="error" class="py-6">
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>
      </section>

      <section v-else-if="page" class="prose max-w-none">
        <!-- Render HTML content if it looks like HTML, otherwise plain text -->
        <div v-if="isHtml" v-html="page.content"></div>
        <pre v-else class="whitespace-pre-wrap text-gray-800 text-sm leading-relaxed">
{{ page.content }}
        </pre>
      </section>

      <section v-else class="py-6 text-gray-500">
        Terms &amp; conditions have not been configured for this website yet.
        Please contact support if you believe this is an error.
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import websitesAPI from '@/api/websites'

const loading = ref(false)
const error = ref('')
const page = ref(null)

const TERMS_SLUG = 'terms' // convention: each tenant creates a static page with slug 'terms'

const metaInfo = computed(() => {
  if (!page.value) return ''
  const parts = []
  if (page.value.last_updated) {
    parts.push(`Last updated: ${new Date(page.value.last_updated).toLocaleDateString()}`)
  }
  if (page.value.language) {
    parts.push(page.value.language.toUpperCase())
  }
  return parts.join(' • ')
})

const isHtml = computed(() => {
  if (!page.value?.content) return false
  // Simple heuristic: if content contains HTML tags, treat as HTML
  return /<\/?[a-z][\s\S]*>/i.test(page.value.content)
})

const getWebsiteDomain = () => {
  // Prefer explicit environment variable if provided
  const envDomain = import.meta.env.VITE_WEBSITE_DOMAIN
  if (envDomain) return envDomain

  // Fallback: use current host (no scheme)
  if (typeof window !== 'undefined') {
    return window.location.host.replace(/^www\./, '')
  }

  return null
}

const loadTerms = async () => {
  loading.value = true
  error.value = ''

  try {
    const website = getWebsiteDomain()
    const params = {}
    if (website) {
      params.website = website
    }

    const res = await websitesAPI.getStaticPage(TERMS_SLUG, params)
    page.value = res.data
  } catch (e) {
    console.error('Failed to load terms page:', e)
    error.value =
      e?.response?.data?.error ||
      e?.response?.data?.detail ||
      'Failed to load terms & conditions. Please try again later.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTerms()
})
</script>

<style scoped>
.prose :deep(h2) {
  @apply text-xl font-semibold mt-6 mb-2;
}

.prose :deep(h3) {
  @apply text-lg font-semibold mt-4 mb-1;
}

.prose :deep(p) {
  @apply mb-3 leading-relaxed;
}

.prose :deep(ul),
.prose :deep(ol) {
  @apply mb-3 ml-6 list-disc;
}
</style>


