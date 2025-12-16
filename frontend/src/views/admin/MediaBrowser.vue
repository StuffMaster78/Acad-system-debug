<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Media Browser</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Browse and select media files for blog posts</p>
      </div>
      <div class="flex gap-2">
        <button @click="viewMode = 'grid'" :class="['btn', viewMode === 'grid' ? 'btn-primary' : 'btn-secondary']">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          Grid
        </button>
        <button @click="viewMode = 'list'" :class="['btn', viewMode === 'list' ? 'btn-primary' : 'btn-secondary']">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          List
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Media</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Images</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.images) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Videos</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatNumber(stats.videos) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Size</p>
        <p class="text-sm font-bold text-purple-600 dark:text-purple-400">{{ formatFileSize(stats.total_size) }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search media..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Type</label>
          <select
            v-model="filters.media_type"
            @change="loadMedia"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Types</option>
            <option value="image">Images</option>
            <option value="video">Videos</option>
            <option value="document">Documents</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
          <select
            v-model="filters.website"
            @change="loadMedia"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Media Grid View -->
    <div v-if="viewMode === 'grid'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!media.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No media found</p>
      </div>
      <div v-else class="p-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="item in media"
          :key="item.id"
          @click="selectMedia(item)"
          class="relative cursor-pointer group border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
        >
          <div v-if="item.file_type === 'image'" class="aspect-square bg-gray-100 dark:bg-gray-700">
            <img :src="item.file_url || item.url" :alt="item.file_name || item.name" class="w-full h-full object-cover" />
          </div>
          <div v-else class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
            <svg class="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center">
            <div class="opacity-0 group-hover:opacity-100 text-white text-sm font-medium text-center px-2">
              {{ item.file_name || item.name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Media List View -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!media.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No media found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Preview</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Size</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Uploaded</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="item in media" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="item.file_type === 'image'" class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded overflow-hidden">
                  <img :src="item.file_url || item.url" :alt="item.file_name || item.name" class="w-full h-full object-cover" />
                </div>
                <div v-else class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded flex items-center justify-center">
                  <svg class="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.file_name || item.name || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ item.file_type || 'unknown' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatFileSize(item.file_size || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(item.uploaded_at || item.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="selectMedia(item)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">Select</button>
                  <button @click="viewMedia(item)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">View</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'

const { showSuccess, showError } = useToast()

const loading = ref(false)
const media = ref([])
const websites = ref([])
const viewMode = ref('grid')
const stats = ref({ total: 0, images: 0, videos: 0, total_size: 0 })

const filters = ref({
  search: '',
  media_type: '',
  website: '',
})

const debouncedSearch = debounce(() => {
  loadMedia()
}, 300)

const loadMedia = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.media_type) params.media_type = filters.value.media_type
    if (filters.value.website) params.website = filters.value.website
    
    const res = await blogPagesAPI.browseMedia(params)
    media.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: media.value.length,
      images: media.value.filter(m => m.file_type === 'image' || m.type === 'image').length,
      videos: media.value.filter(m => m.file_type === 'video' || m.type === 'video').length,
      total_size: media.value.reduce((sum, m) => sum + (m.file_size || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load media:', error)
    showError('Failed to load media: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    websites.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const selectMedia = (item) => {
  // Emit event or copy URL to clipboard
  const url = item.file_url || item.url
  if (url) {
    navigator.clipboard.writeText(url).then(() => {
      showSuccess('Media URL copied to clipboard')
    }).catch(() => {
      showError('Failed to copy URL')
    })
  }
}

const viewMedia = (item) => {
  const url = item.file_url || item.url
  if (url) {
    window.open(url, '_blank')
  }
}

const resetFilters = () => {
  filters.value = { search: '', media_type: '', website: '' }
  loadMedia()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

onMounted(async () => {
  await Promise.all([loadMedia(), loadWebsites()])
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
</style>

