<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Content Metrics & SEO Health</h1>
        <p class="mt-2 text-gray-600">
          Website-level performance across blogs and service pages, with SEO health flags.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <select
          v-model="selectedWebsiteId"
          @change="loadAll"
          class="border rounded px-3 py-2 text-sm"
        >
          <option disabled value="">Select website</option>
          <option
            v-for="site in websites"
            :key="site.id"
            :value="site.id"
          >
            {{ site.name || site.domain || ('Website #' + site.id) }}
          </option>
        </select>
        <button
          @click="refreshMetrics"
          :disabled="loading.metrics || !selectedWebsiteId"
          class="btn btn-secondary flex items-center gap-2"
        >
          <svg
            class="w-4 h-4"
            :class="{ 'animate-spin': loading.metrics }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="bg-red-50 border-l-4 border-red-400 p-4 rounded"
    >
      <p class="text-sm text-red-800">
        {{ error }}
      </p>
    </div>

    <!-- Top-level metrics -->
    <div v-if="metrics" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <p class="text-xs uppercase text-gray-500 font-semibold">Total Posts</p>
        <p class="mt-2 text-2xl font-bold text-gray-900">{{ metrics.total_posts }}</p>
        <p class="mt-1 text-xs text-gray-500">
          {{ metrics.published_posts }} published &middot; {{ metrics.draft_posts }} drafts
        </p>
      </div>
      <div class="card p-4">
        <p class="text-xs uppercase text-gray-500 font-semibold">Clicks</p>
        <p class="mt-2 text-2xl font-bold text-gray-900">{{ metrics.total_clicks }}</p>
        <p class="mt-1 text-xs text-gray-500">
          {{ metrics.total_conversions }} conversions
        </p>
      </div>
      <div class="card p-4">
        <p class="text-xs uppercase text-gray-500 font-semibold">Top Category</p>
        <p class="mt-2 text-sm font-semibold text-gray-900">
          {{ topCategory?.name || '—' }}
        </p>
        <p class="mt-1 text-xs text-gray-500">
          {{ topCategory ? (topCategory.post_count + ' posts, ' + topCategory.clicks + ' clicks') : 'No data yet' }}
        </p>
      </div>
      <div class="card p-4">
        <p class="text-xs uppercase text-gray-500 font-semibold">Top Tag</p>
        <p class="mt-2 text-sm font-semibold text-gray-900">
          {{ topTag?.name || '—' }}
        </p>
        <p class="mt-1 text-xs text-gray-500">
          {{ topTag ? (topTag.post_count + ' posts, ' + topTag.clicks + ' clicks') : 'No data yet' }}
        </p>
      </div>
    </div>

    <!-- Category & Tag breakdowns -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-gray-900">By Category</h2>
        </div>
        <div v-if="!categoryRows.length" class="text-sm text-gray-500 py-4">No category metrics yet.</div>
        <div v-else class="space-y-2 max-h-80 overflow-auto">
          <div
            v-for="row in categoryRows"
            :key="row.name"
            class="flex items-center justify-between text-sm"
          >
            <div>
              <p class="font-medium text-gray-900">{{ row.name }}</p>
              <p class="text-xs text-gray-500">
                {{ row.post_count }} posts &middot; {{ row.clicks }} clicks &middot;
                {{ row.conversions }} conversions
              </p>
            </div>
            <button
              class="text-xs text-primary-600 hover:text-primary-800"
              @click="loadCategory(row.name)"
            >
              View
            </button>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-gray-900">By Tag</h2>
        </div>
        <div v-if="!tagRows.length" class="text-sm text-gray-500 py-4">No tag metrics yet.</div>
        <div v-else class="space-y-2 max-h-80 overflow-auto">
          <div
            v-for="row in tagRows"
            :key="row.name"
            class="flex items-center justify-between text-sm"
          >
            <div>
              <p class="font-medium text-gray-900">{{ row.name }}</p>
              <p class="text-xs text-gray-500">
                {{ row.post_count }} posts &middot; {{ row.clicks }} clicks &middot;
                {{ row.conversions }} conversions
              </p>
            </div>
            <button
              class="text-xs text-primary-600 hover:text-primary-800"
              @click="loadTag(row.name)"
            >
              View
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- SEO health & audit -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-gray-900">SEO Health (Blogs)</h2>
        </div>
        <div v-if="!seoHealth.blog_audit.length" class="text-sm text-gray-500 py-4">
          No SEO issues detected for blogs.
        </div>
        <div v-else class="space-y-2 max-h-80 overflow-auto text-sm">
          <div
            v-for="item in seoHealth.blog_audit"
            :key="item.id"
            class="border-b last:border-0 pb-2"
          >
            <div class="flex justify-between">
              <div>
                <p class="font-medium text-gray-900">
                  {{ item.title }}
                </p>
                <p class="text-xs text-gray-500">
                  /blogs/{{ item.slug }}
                </p>
              </div>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs"
                    :class="item.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'">
                {{ item.status }}
              </span>
            </div>
            <p class="mt-1 text-xs text-red-600">
              Issues: {{ item.issues.join(', ') }}
            </p>
          </div>
        </div>
      </div>

      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-semibold text-gray-900">SEO Health (Service Pages)</h2>
        </div>
        <div v-if="!seoHealth.service_page_audit.length" class="text-sm text-gray-500 py-4">
          No SEO issues detected for service pages.
        </div>
        <div v-else class="space-y-2 max-h-80 overflow-auto text-sm">
          <div
            v-for="item in seoHealth.service_page_audit"
            :key="item.id"
            class="border-b last:border-0 pb-2"
          >
            <div class="flex justify-between">
              <div>
                <p class="font-medium text-gray-900">
                  {{ item.title }}
                </p>
                <p class="text-xs text-gray-500">
                  /service-pages/{{ item.slug }}
                </p>
              </div>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800">
                {{ item.status }}
              </span>
            </div>
            <p class="mt-1 text-xs text-red-600">
              Issues: {{ item.issues.join(', ') }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import blogApi from '@/api/blog-pages'
import apiClient from '@/api/client'

const websites = ref([])
const selectedWebsiteId = ref('')

const metrics = ref(null)
const seoHealth = reactive({
  blog_audit: [],
  service_page_audit: [],
})

const loading = reactive({
  websites: false,
  metrics: false,
  audit: false,
})

const error = ref('')

const categoryRows = computed(() => {
  if (!metrics.value || !metrics.value.category_metrics) return []
  return Object.entries(metrics.value.category_metrics).map(([name, data]) => ({
    name,
    post_count: data.post_count || 0,
    clicks: data.view_count || data.clicks || 0,
    conversions: data.conversion_count || data.conversions || 0,
  }))
})

const tagRows = computed(() => {
  if (!metrics.value || !metrics.value.tag_metrics) return []
  return Object.entries(metrics.value.tag_metrics).map(([name, data]) => ({
    name,
    post_count: data.post_count || 0,
    clicks: data.view_count || data.clicks || 0,
    conversions: data.conversion_count || data.conversions || 0,
  }))
})

const topCategory = computed(() => {
  if (!categoryRows.value.length) return null
  return [...categoryRows.value].sort((a, b) => (b.clicks || 0) - (a.clicks || 0))[0]
})

const topTag = computed(() => {
  if (!tagRows.value.length) return null
  return [...tagRows.value].sort((a, b) => (b.clicks || 0) - (a.clicks || 0))[0]
})

async function loadWebsites() {
  try {
    loading.websites = true
    const { data } = await apiClient.get('/websites/websites/')
    websites.value = data.results || data
    if (!selectedWebsiteId.value && websites.value.length) {
      selectedWebsiteId.value = websites.value[0].id
    }
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load websites.'
  } finally {
    loading.websites = false
  }
}

async function loadMetrics() {
  if (!selectedWebsiteId.value) return
  try {
    loading.metrics = true
    error.value = ''
    const { data } = await blogApi.getWebsiteMetricsLatest({
      website_id: selectedWebsiteId.value,
      seo_health_limit: 50,
    })
    metrics.value = data
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load website metrics.'
  } finally {
    loading.metrics = false
  }
}

async function loadAudit() {
  if (!selectedWebsiteId.value) return
  try {
    loading.audit = true
    const { data } = await blogApi.getContentAuditOverview({
      website_id: selectedWebsiteId.value,
    })
    seoHealth.blog_audit = data.blog_audit || []
    seoHealth.service_page_audit = data.service_page_audit || []
  } catch (e) {
    console.error(e)
    error.value = error.value || 'Failed to load content audit.'
  } finally {
    loading.audit = false
  }
}

async function loadCategory(categoryName) {
  if (!selectedWebsiteId.value || !categoryName) return
  try {
    const { data } = await blogApi.getWebsiteMetricsByCategory({
      website_id: selectedWebsiteId.value,
      category: categoryName,
    })
    // For now we just log; you could extend this to show a modal/detail view
    console.info('Category metrics', data)
  } catch (e) {
    console.error(e)
  }
}

async function loadTag(tagName) {
  if (!selectedWebsiteId.value || !tagName) return
  try {
    const { data } = await blogApi.getWebsiteMetricsByTag({
      website_id: selectedWebsiteId.value,
      tag: tagName,
    })
    console.info('Tag metrics', data)
  } catch (e) {
    console.error(e)
  }
}

async function refreshMetrics() {
  await Promise.all([loadMetrics(), loadAudit()])
}

async function loadAll() {
  await Promise.all([loadMetrics(), loadAudit()])
}

onMounted(async () => {
  await loadWebsites()
  await loadAll()
})
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}
</style>


