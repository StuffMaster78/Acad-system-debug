<template>
  <div class="media-picker">
    <!-- Trigger Button -->
    <button
      v-if="!hideTrigger"
      @click="showModal = true"
      :class="[
        'inline-flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors',
        triggerClass || 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
      ]"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <span>{{ triggerLabel || 'Select Media' }}</span>
    </button>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="handleClose"
    >
      <div class="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ modalTitle || 'Select Media' }}
          </h2>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Filters -->
        <div class="p-4 border-b bg-gray-50">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <input
                v-model="filters.search"
                @input="debouncedSearch"
                type="text"
                placeholder="Search..."
                class="w-full border rounded px-3 py-2 text-sm"
              />
            </div>
            <div>
              <select
                v-model="filters.type"
                @change="loadMedia"
                class="w-full border rounded px-3 py-2 text-sm"
              >
                <option value="">All Types</option>
                <option v-for="type in mediaTypes" :key="type.value" :value="type.value">
                  {{ type.label }}
                </option>
              </select>
            </div>
            <div class="flex gap-2">
              <button
                @click="showUploadForm = true"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700"
              >
                Upload New
              </button>
              <button
                @click="resetFilters"
                class="px-4 py-2 border rounded text-sm hover:bg-gray-100"
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        <!-- Media Grid -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="loading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="mediaAssets.length === 0" class="text-center py-12 text-gray-500">
            No media found. Upload your first asset to get started.
          </div>

          <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <div
              v-for="asset in mediaAssets"
              :key="asset.id"
              @click="handleSelect(asset)"
              :class="[
                'relative aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer border-2 transition-all',
                selectedAsset?.id === asset.id
                  ? 'border-blue-600 ring-2 ring-blue-200'
                  : 'border-transparent hover:border-gray-300'
              ]"
            >
              <!-- Thumbnail -->
              <img
                v-if="asset.type === 'image' && asset.url"
                :src="asset.url"
                :alt="asset.alt_text || asset.title"
                class="w-full h-full object-cover"
              />
              <div v-else-if="asset.type === 'video'" class="w-full h-full flex items-center justify-center">
                <svg class="w-12 h-12 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>

              <!-- Selection Indicator -->
              <div
                v-if="selectedAsset?.id === asset.id"
                class="absolute top-2 right-2 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center"
              >
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>

              <!-- Title Overlay -->
              <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs p-2 truncate">
                {{ asset.title || 'Untitled' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between p-4 border-t bg-gray-50">
          <div class="text-sm text-gray-600">
            {{ mediaAssets.length }} {{ mediaAssets.length === 1 ? 'item' : 'items' }}
          </div>
          <div class="flex gap-2">
            <button
              @click="handleClose"
              class="px-4 py-2 border rounded text-sm hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              v-if="allowMultiple"
              @click="handleConfirmMultiple"
              :disabled="selectedAssets.length === 0"
              class="px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Select {{ selectedAssets.length > 0 ? `(${selectedAssets.length})` : '' }}
            </button>
            <button
              v-else
              @click="handleConfirm"
              :disabled="!selectedAsset"
              class="px-4 py-2 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Select
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Form Modal -->
    <div
      v-if="showUploadForm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4"
      @click.self="showUploadForm = false"
    >
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-xl font-bold mb-4">Upload Media</h3>
          <form @submit.prevent="handleUpload" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">File</label>
              <input
                ref="fileInput"
                type="file"
                @change="handleFileSelect"
                :accept="acceptTypes"
                class="w-full border rounded px-3 py-2"
                required
              />
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
                @click="showUploadForm = false"
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
import { ref, onMounted, computed, watch } from 'vue'
import mediaAPI from '@/api/media'
import websitesAPI from '@/api/websites'

const props = defineProps({
  modelValue: {
    type: [Object, Array],
    default: null
  },
  websiteId: {
    type: Number,
    default: null
  },
  allowMultiple: {
    type: Boolean,
    default: false
  },
  acceptTypes: {
    type: String,
    default: 'image/*,video/*,.pdf,.doc,.docx'
  },
  hideTrigger: {
    type: Boolean,
    default: false
  },
  triggerLabel: {
    type: String,
    default: null
  },
  triggerClass: {
    type: String,
    default: null
  },
  modalTitle: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'selected'])

const showModal = ref(false)
const showUploadForm = ref(false)
const mediaAssets = ref([])
const mediaTypes = ref([])
const websites = ref([])
const loading = ref(false)
const uploading = ref(false)
const selectedAsset = ref(null)
const selectedAssets = ref([])
const fileInput = ref(null)

const filters = ref({
  search: '',
  type: '',
  website_id: props.websiteId || ''
})

const uploadForm = ref({
  title: '',
  alt_text: '',
  website: props.websiteId || ''
})

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
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.website_id) params.website_id = filters.value.website_id

    const response = await mediaAPI.list(params)
    mediaAssets.value = response.data?.results || response.data || []
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
    if (props.websiteId && !uploadForm.value.website) {
      uploadForm.value.website = props.websiteId
    }
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadMediaTypes = async () => {
  try {
    const response = await mediaAPI.getAllTypes()
    mediaTypes.value = response.data || []
  } catch (e) {
    console.error('Failed to load media types:', e)
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

    const response = await mediaAPI.create(formData)
    showUploadForm.value = false
    uploadForm.value = {
      title: '',
      alt_text: '',
      website: props.websiteId || ''
    }
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    // Reload media and select the new asset
    await loadMedia()
    if (response.data) {
      handleSelect(response.data)
    }
  } catch (e) {
    console.error('Failed to upload media:', e)
    alert('Failed to upload media: ' + (e.response?.data?.detail || e.message))
  } finally {
    uploading.value = false
  }
}

const handleSelect = (asset) => {
  if (props.allowMultiple) {
    const index = selectedAssets.value.findIndex(a => a.id === asset.id)
    if (index >= 0) {
      selectedAssets.value.splice(index, 1)
    } else {
      selectedAssets.value.push(asset)
    }
  } else {
    selectedAsset.value = asset
  }
}

const handleConfirm = () => {
  if (selectedAsset.value) {
    emit('update:modelValue', selectedAsset.value)
    emit('selected', selectedAsset.value)
    handleClose()
  }
}

const handleConfirmMultiple = () => {
  if (selectedAssets.value.length > 0) {
    emit('update:modelValue', selectedAssets.value)
    emit('selected', selectedAssets.value)
    handleClose()
  }
}

const handleClose = () => {
  showModal.value = false
  selectedAsset.value = null
  selectedAssets.value = []
}

const resetFilters = () => {
  filters.value = {
    search: '',
    type: '',
    website_id: props.websiteId || ''
  }
  loadMedia()
}

// Watch for modelValue changes to sync selection
watch(() => props.modelValue, (newValue) => {
  if (props.allowMultiple) {
    if (Array.isArray(newValue)) {
      selectedAssets.value = newValue
    }
  } else {
    selectedAsset.value = newValue
  }
}, { immediate: true })

// Watch for modal open to load media
watch(() => showModal.value, (isOpen) => {
  if (isOpen) {
    loadMedia()
    loadWebsites()
    loadMediaTypes()
  }
})

onMounted(() => {
  if (props.modelValue) {
    if (props.allowMultiple && Array.isArray(props.modelValue)) {
      selectedAssets.value = props.modelValue
    } else {
      selectedAsset.value = props.modelValue
    }
  }
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>

