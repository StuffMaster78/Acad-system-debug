<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Media Library</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage blog images, videos, and media assets</p>
      </div>
      <div class="flex gap-2">
        <button @click="showUploadModal = true" class="btn btn-primary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload Media
        </button>
        <button @click="loadMedia" :disabled="loading" class="btn btn-secondary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Media</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Images</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.images }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Videos</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.videos }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Dark Mode Images</p>
        <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400">{{ stats.dark_mode }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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

    <!-- Media Grid -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!mediaItems.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No media found</p>
        <button @click="showUploadModal = true" class="mt-4 btn btn-primary">Upload Your First Media</button>
      </div>
      
      <div v-else class="p-6">
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div
            v-for="item in mediaItems"
            :key="item.id"
            class="relative group cursor-pointer border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
            @click="selectMedia(item)"
          >
            <!-- Image Preview -->
            <div v-if="activeTab === 'images' || activeTab === 'dark-mode'" class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
              <img
                v-if="item.file_url || item.image"
                :src="item.file_url || item.image"
                :alt="item.alt_text || item.name"
                class="w-full h-full object-cover"
              />
              <svg v-else class="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            
            <!-- Video Preview -->
            <div v-else-if="activeTab === 'videos'" class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
              <video
                v-if="item.video_url || item.file_url"
                :src="item.video_url || item.file_url"
                class="w-full h-full object-cover"
                muted
              ></video>
              <svg v-else class="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            
            <!-- Overlay on Hover -->
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
              <div class="flex gap-2">
                <button @click.stop="viewMedia(item)" class="px-3 py-1 bg-white text-gray-900 rounded text-sm hover:bg-gray-100">
                  View
                </button>
                <button @click.stop="deleteMedia(item)" class="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">
                  Delete
                </button>
              </div>
            </div>
            
            <!-- Media Info -->
            <div class="p-2 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
              <p class="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">{{ item.name || item.filename || 'Untitled' }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatFileSize(item.file_size) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeUploadModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Upload Media</h3>
        </div>
        <form @submit.prevent="uploadMedia" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Select Files *</label>
            <input
              ref="fileInput"
              type="file"
              multiple
              accept="image/*,video/*"
              @change="handleFileSelect"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">You can select multiple files</p>
          </div>
          <div v-if="selectedFiles.length > 0" class="space-y-2">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Selected Files:</p>
            <div v-for="(file, index) in selectedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <span class="text-sm text-gray-900 dark:text-gray-100">{{ file.name }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatFileSize(file.size) }}</span>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
            <select
              v-model="uploadForm.website"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select Website</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="uploading || selectedFiles.length === 0" class="btn btn-primary flex-1">
              {{ uploading ? 'Uploading...' : `Upload ${selectedFiles.length} File(s)` }}
            </button>
            <button type="button" @click="closeUploadModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Media Modal -->
    <div v-if="viewingMedia" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click.self="viewingMedia = null">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">{{ viewingMedia.name || 'Media Preview' }}</h3>
          <button @click="viewingMedia = null" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <div v-if="viewingMedia.file_url || viewingMedia.image" class="mb-4">
            <img :src="viewingMedia.file_url || viewingMedia.image" :alt="viewingMedia.alt_text" class="max-w-full h-auto rounded-lg" />
          </div>
          <div v-else-if="viewingMedia.video_url" class="mb-4">
            <video :src="viewingMedia.video_url" controls class="max-w-full rounded-lg"></video>
          </div>
          <div class="space-y-2 text-sm">
            <div><span class="font-medium">Name:</span> {{ viewingMedia.name || '—' }}</div>
            <div><span class="font-medium">Size:</span> {{ formatFileSize(viewingMedia.file_size) }}</div>
            <div><span class="font-medium">Type:</span> {{ viewingMedia.file_type || viewingMedia.content_type || '—' }}</div>
            <div><span class="font-medium">Uploaded:</span> {{ formatDate(viewingMedia.created_at) }}</div>
            <div v-if="viewingMedia.alt_text"><span class="font-medium">Alt Text:</span> {{ viewingMedia.alt_text }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const uploading = ref(false)
const mediaItems = ref([])
const websites = ref([])
const stats = ref({ total: 0, images: 0, videos: 0, dark_mode: 0 })
const activeTab = ref('images')
const showUploadModal = ref(false)
const viewingMedia = ref(null)
const selectedFiles = ref([])
const fileInput = ref(null)

const tabs = [
  { id: 'images', label: 'Images' },
  { id: 'videos', label: 'Videos' },
  { id: 'dark-mode', label: 'Dark Mode Images' },
]

const filters = ref({
  search: '',
  website: '',
})

const uploadForm = ref({
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
    if (filters.value.website) params.website = filters.value.website
    
    let res
    if (activeTab.value === 'images') {
      res = await blogPagesAPI.listMedia(params)
    } else if (activeTab.value === 'videos') {
      res = await blogPagesAPI.listBlogVideos(params)
    } else if (activeTab.value === 'dark-mode') {
      res = await blogPagesAPI.listDarkModeImages(params)
    }
    
    mediaItems.value = res?.data?.results || res?.data || []
    
    // Calculate stats (aggregate from all tabs)
    await calculateStats()
  } catch (error) {
    console.error('Failed to load media:', error)
    showError('Failed to load media: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const calculateStats = async () => {
  try {
    const [imagesRes, videosRes, darkModeRes] = await Promise.all([
      blogPagesAPI.listMedia({}),
      blogPagesAPI.listBlogVideos({}),
      blogPagesAPI.listDarkModeImages({}),
    ])
    
    stats.value = {
      total: (imagesRes?.data?.results || imagesRes?.data || []).length +
             (videosRes?.data?.results || videosRes?.data || []).length +
             (darkModeRes?.data?.results || darkModeRes?.data || []).length,
      images: (imagesRes?.data?.results || imagesRes?.data || []).length,
      videos: (videosRes?.data?.results || videosRes?.data || []).length,
      dark_mode: (darkModeRes?.data?.results || darkModeRes?.data || []).length,
    }
  } catch (error) {
    console.error('Failed to calculate stats:', error)
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

const handleFileSelect = (event) => {
  selectedFiles.value = Array.from(event.target.files || [])
}

const uploadMedia = async () => {
  if (selectedFiles.value.length === 0) {
    showError('Please select at least one file')
    return
  }
  
  uploading.value = true
  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      if (uploadForm.value.website) formData.append('website', uploadForm.value.website)
      
      if (activeTab.value === 'images') {
        await blogPagesAPI.uploadMedia(formData)
      } else if (activeTab.value === 'videos') {
        await blogPagesAPI.createBlogVideo(formData)
      } else if (activeTab.value === 'dark-mode') {
        await blogPagesAPI.createDarkModeImage(formData)
      }
    }
    
    showSuccess(`Successfully uploaded ${selectedFiles.value.length} file(s)`)
    closeUploadModal()
    await loadMedia()
    await calculateStats()
  } catch (error) {
    console.error('Failed to upload media:', error)
    showError('Failed to upload media: ' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const selectMedia = (item) => {
  viewingMedia.value = item
}

const viewMedia = (item) => {
  viewingMedia.value = item
}

const deleteMedia = async (item) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${item.name || item.filename}"?`,
    'Delete Media',
    {
      details: 'This action cannot be undone. The media file will be permanently removed from the library.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    if (activeTab.value === 'images') {
      await blogPagesAPI.deleteMedia(item.id)
    } else if (activeTab.value === 'videos') {
      await blogPagesAPI.deleteBlogVideo(item.id)
    } else if (activeTab.value === 'dark-mode') {
      await blogPagesAPI.deleteDarkModeImage(item.id)
    }
    
    showSuccess('Media deleted successfully')
    await loadMedia()
    await calculateStats()
  } catch (error) {
    console.error('Failed to delete media:', error)
    showError('Failed to delete media: ' + (error.response?.data?.detail || error.message))
  }
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  uploadForm.value = { website: '' }
  if (fileInput.value) fileInput.value.value = ''
}

const resetFilters = () => {
  filters.value = { search: '', website: '' }
  loadMedia()
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
  return new Date(dateString).toLocaleString()
}

watch(activeTab, () => {
  loadMedia()
})

onMounted(async () => {
  await Promise.all([loadMedia(), loadWebsites(), calculateStats()])
})
</script>

<style scoped>
@reference "tailwindcss";
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

