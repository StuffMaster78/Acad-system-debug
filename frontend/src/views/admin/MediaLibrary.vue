<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Media Library</h1>
        <p class="mt-2 text-gray-600">Manage images, videos, documents, and other media assets</p>
      </div>
      <button @click="showUploadModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Upload Media
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by title, tags..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Type</label>
          <select v-model="filters.type" @change="loadMedia" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option v-for="type in mediaTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website_id" @change="loadMedia" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Media Grid -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="mediaAssets.length === 0" class="text-center py-12">
      <p class="text-gray-500">No media assets found. Upload your first asset to get started.</p>
    </div>

    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <div
        v-for="asset in mediaAssets"
        :key="asset.id"
        class="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
        @click="selectAsset(asset)"
      >
        <!-- Thumbnail/Preview -->
        <div class="aspect-square bg-gray-100 flex items-center justify-center relative group">
          <img
            v-if="asset.type === 'image' && asset.url"
            :src="asset.url"
            :alt="asset.alt_text || asset.title"
            class="w-full h-full object-cover"
          />
          <div v-else-if="asset.type === 'video'" class="text-center p-4">
            <svg class="w-12 h-12 text-gray-400 mx-auto" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <div v-else class="text-center p-4">
            <svg class="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <!-- Overlay Actions -->
          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
            <button
              @click.stop="editAsset(asset)"
              class="p-2 bg-white rounded text-gray-700 hover:bg-gray-100"
              title="Edit"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click.stop="deleteAsset(asset)"
              class="p-2 bg-red-500 rounded text-white hover:bg-red-600"
              title="Delete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Asset Info -->
        <div class="p-3">
          <p class="text-sm font-medium text-gray-900 truncate" :title="asset.title">
            {{ asset.title || 'Untitled' }}
          </p>
          <p class="text-xs text-gray-500 mt-1">
            {{ formatFileSize(asset.size_bytes) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="px-4 py-2 border rounded disabled:opacity-50"
      >
        Previous
      </button>
      <span class="px-4 py-2 text-sm text-gray-600">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="px-4 py-2 border rounded disabled:opacity-50"
      >
        Next
      </button>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showUploadModal = false">
      <div class="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h2 class="text-2xl font-bold mb-4">Upload Media</h2>
          
          <form @submit.prevent="handleUpload" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">File</label>
              <input
                ref="fileInput"
                type="file"
                @change="handleFileSelect"
                accept="image/*,video/*,.pdf,.doc,.docx"
                class="w-full border rounded px-3 py-2"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Website</label>
              <select v-model="uploadForm.website" required class="w-full border rounded px-3 py-2">
                <option value="">Select website...</option>
                <option v-for="website in websites" :key="website.id" :value="website.id">
                  {{ website.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Title</label>
              <input
                v-model="uploadForm.title"
                type="text"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Alt Text</label>
              <input
                v-model="uploadForm.alt_text"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="For accessibility"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Caption</label>
              <textarea
                v-model="uploadForm.caption"
                rows="3"
                class="w-full border rounded px-3 py-2"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Tags (comma-separated)</label>
              <input
                v-model="uploadForm.tags"
                type="text"
                class="w-full border rounded px-3 py-2"
                placeholder="tag1, tag2, tag3"
              />
            </div>

            <div class="flex gap-4 pt-4">
              <button
                type="submit"
                :disabled="uploading"
                class="flex-1 bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                <span v-if="uploading">Uploading...</span>
                <span v-else>Upload</span>
              </button>
              <button
                type="button"
                @click="showUploadModal = false"
                class="px-6 py-2 border rounded"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingAsset" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="editingAsset = null">
      <div class="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h2 class="text-2xl font-bold mb-4">Edit Media</h2>
          
          <form @submit.prevent="handleUpdate" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Title</label>
              <input
                v-model="editForm.title"
                type="text"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Alt Text</label>
              <input
                v-model="editForm.alt_text"
                type="text"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Caption</label>
              <textarea
                v-model="editForm.caption"
                rows="3"
                class="w-full border rounded px-3 py-2"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-2">Tags (comma-separated)</label>
              <input
                v-model="editForm.tags"
                type="text"
                class="w-full border rounded px-3 py-2"
              />
            </div>

            <div class="flex gap-4 pt-4">
              <button
                type="submit"
                :disabled="saving"
                class="flex-1 bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                <span v-if="saving">Saving...</span>
                <span v-else>Save</span>
              </button>
              <button
                type="button"
                @click="editingAsset = null"
                class="px-6 py-2 border rounded"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import mediaAPI from '@/api/media'
import websitesAPI from '@/api/websites'

const mediaAssets = ref([])
const websites = ref([])
const mediaTypes = ref([])
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const showUploadModal = ref(false)
const editingAsset = ref(null)
const fileInput = ref(null)

const filters = ref({
  search: '',
  type: '',
  website_id: ''
})

const uploadForm = ref({
  website: '',
  title: '',
  alt_text: '',
  caption: '',
  tags: ''
})

const editForm = ref({
  title: '',
  alt_text: '',
  caption: '',
  tags: ''
})

const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 20

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadMedia()
  }, 500)
}

const loadMedia = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.website_id) params.website_id = filters.value.website_id

    const response = await mediaAPI.list(params)
    mediaAssets.value = response.data?.results || response.data || []
    totalPages.value = Math.ceil((response.data?.count || mediaAssets.value.length) / pageSize)
  } catch (e) {
    console.error('Failed to load media:', e)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites({ is_active: true })
    websites.value = response.data?.results || response.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadMediaTypes = async () => {
  try {
    const response = await mediaAPI.getAllTypes()
    mediaTypes.value = Array.isArray(response.data) ? response.data : []
  } catch (e) {
    console.error('Failed to load media types:', e)
    mediaTypes.value = [] // Set empty array on error
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    uploadForm.value.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleUpload = async () => {
  if (!fileInput.value?.files[0]) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', fileInput.value.files[0])
    formData.append('website', uploadForm.value.website)
    if (uploadForm.value.title) formData.append('title', uploadForm.value.title)
    if (uploadForm.value.alt_text) formData.append('alt_text', uploadForm.value.alt_text)
    if (uploadForm.value.caption) formData.append('caption', uploadForm.value.caption)
    if (uploadForm.value.tags) {
      const tags = uploadForm.value.tags.split(',').map(t => t.trim()).filter(t => t)
      formData.append('tags', JSON.stringify(tags))
    }

    await mediaAPI.create(formData)
    showUploadModal.value = false
    resetUploadForm()
    loadMedia()
  } catch (e) {
    console.error('Failed to upload media:', e)
    alert('Failed to upload media: ' + (e.response?.data?.detail || e.message))
  } finally {
    uploading.value = false
  }
}

const editAsset = (asset) => {
  editingAsset.value = asset
  editForm.value = {
    title: asset.title || '',
    alt_text: asset.alt_text || '',
    caption: asset.caption || '',
    tags: (asset.tags || []).join(', ')
  }
}

const handleUpdate = async () => {
  saving.value = true
  try {
    const data = {
      title: editForm.value.title,
      alt_text: editForm.value.alt_text,
      caption: editForm.value.caption
    }
    if (editForm.value.tags) {
      data.tags = editForm.value.tags.split(',').map(t => t.trim()).filter(t => t)
    }

    await mediaAPI.patch(editingAsset.value.id, data)
    editingAsset.value = null
    loadMedia()
  } catch (e) {
    console.error('Failed to update media:', e)
    alert('Failed to update media: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

const deleteAsset = async (asset) => {
  if (!confirm(`Are you sure you want to delete "${asset.title || 'this asset'}"?`)) return

  try {
    await mediaAPI.delete(asset.id)
    loadMedia()
  } catch (e) {
    console.error('Failed to delete media:', e)
    alert('Failed to delete media: ' + (e.response?.data?.detail || e.message))
  }
}

const selectAsset = (asset) => {
  // Emit event or handle selection
  console.log('Selected asset:', asset)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    type: '',
    website_id: ''
  }
  currentPage.value = 1
  loadMedia()
}

const resetUploadForm = () => {
  uploadForm.value = {
    website: '',
    title: '',
    alt_text: '',
    caption: '',
    tags: ''
  }
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadMedia()
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  loadMedia()
  loadWebsites()
  loadMediaTypes()
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>

