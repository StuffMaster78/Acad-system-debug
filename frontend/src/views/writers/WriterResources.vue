<template>
  <div class="space-y-6">
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Writer Resources</h1>
      <p class="text-gray-600">
        Access guides, tools, and resources to help you improve your writing and grow professionally.
      </p>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            v-model="filters.category"
            @change="loadResources"
            class="w-full border border-gray-300 rounded-lg px-4 py-2"
          >
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            v-model="filters.type"
            @change="loadResources"
            class="w-full border border-gray-300 rounded-lg px-4 py-2"
          >
            <option value="">All Types</option>
            <option value="document">Documents</option>
            <option value="link">Links</option>
            <option value="video">Videos</option>
            <option value="article">Articles</option>
            <option value="tool">Tools</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search resources..."
            class="w-full border border-gray-300 rounded-lg px-4 py-2"
          />
        </div>
      </div>
    </div>

    <!-- Featured Resources -->
    <div v-if="featuredResources.length > 0" class="bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
        Featured Resources
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ResourceCard
          v-for="resource in featuredResources"
          :key="resource.id"
          :resource="resource"
          @view="handleView"
          @download="handleDownload"
        />
      </div>
    </div>

    <!-- All Resources -->
    <div class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">All Resources</h2>
        <span class="text-sm text-gray-600">{{ resources.length }} resources</span>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="resources.length === 0" class="text-center py-12 text-gray-500">
        <p>No resources found</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ResourceCard
          v-for="resource in resources"
          :key="resource.id"
          :resource="resource"
          @view="handleView"
          @download="handleDownload"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { debounce } from 'lodash-es'
import writerAPI from '@/api/writers'
import ResourceCard from '@/components/writers/ResourceCard.vue'

const resources = ref([])
const categories = ref([])
const loading = ref(false)
const filters = ref({
  category: '',
  type: '',
  search: ''
})

const featuredResources = computed(() => {
  return resources.value.filter(r => r.is_featured)
})

const loadCategories = async () => {
  try {
    const response = await writerAPI.getResourceCategories()
    categories.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  }
}

const loadResources = async () => {
  loading.value = true
  try {
    const params = {
      is_active: true
    }
    if (filters.value.category) {
      params.category = filters.value.category
    }
    if (filters.value.type) {
      params.resource_type = filters.value.type
    }
    if (filters.value.search) {
      params.search = filters.value.search
    }
    
    const response = await writerAPI.getResources(params)
    resources.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load resources:', error)
    resources.value = []
  } finally {
    loading.value = false
  }
}

const handleView = async (resource) => {
  try {
    await writerAPI.trackResourceView(resource.id)
    if (resource.resource_type === 'link' && resource.external_url) {
      window.open(resource.external_url, '_blank')
    } else if (resource.resource_type === 'video' && resource.video_url) {
      window.open(resource.video_url, '_blank')
    } else if (resource.resource_type === 'article' && resource.content) {
      // Show article in modal or navigate to detail page
      // For now, just open URL if available
      if (resource.url) {
        window.open(resource.url, '_blank')
      }
    }
  } catch (error) {
    console.error('Failed to track view:', error)
  }
}

const handleDownload = async (resource) => {
  try {
    const response = await writerAPI.downloadResource(resource.id)
    if (response.data.file_url) {
      window.open(response.data.file_url, '_blank')
    }
  } catch (error) {
    console.error('Failed to download resource:', error)
    alert('Failed to download resource. Please try again.')
  }
}

const debouncedSearch = debounce(() => {
  loadResources()
}, 500)

onMounted(async () => {
  await Promise.all([loadCategories(), loadResources()])
})
</script>

