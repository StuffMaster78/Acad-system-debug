<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('update:show', false)"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
      <!-- Header -->
      <div class="bg-linear-to-r from-blue-600 to-blue-700 p-6 rounded-t-lg">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold text-white">Upload Media</h2>
            <p class="text-blue-100 mt-1">Add new images, videos, or documents to your library</p>
          </div>
          <button
            @click="$emit('update:show', false)"
            class="text-white hover:text-blue-200 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Drop Zone -->
      <div class="p-6">
        <div
          :class="[
            'border-2 border-dashed rounded-lg p-12 text-center transition-all',
            isDragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
          ]"
          @drop="handleDrop"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @dragenter.prevent
        >
          <input
            ref="fileInput"
            type="file"
            @change="handleFileSelect"
            :accept="acceptTypes"
            multiple
            class="hidden"
          />
          
          <div v-if="!selectedFiles.length">
            <div class="w-20 h-20 bg-blue-100 dark:bg-blue-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Drag and drop files here</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">or</p>
            <button
              @click="fileInput?.click()"
              class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Browse Files
            </button>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-4">Supports: Images, Videos, PDFs, Documents</p>
          </div>

          <!-- Selected Files Preview -->
          <div v-else class="space-y-4">
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div
                v-for="(file, index) in selectedFiles"
                :key="index"
                class="relative group"
              >
                <div class="aspect-square bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
                  <img
                    v-if="file.preview"
                    :src="file.preview"
                    :alt="file.name"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <button
                    @click="removeFile(index)"
                    class="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">{{ file.name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-500">{{ formatFileSize(file.size) }}</p>
              </div>
            </div>
            <button
              @click="fileInput?.click()"
              class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              + Add more files
            </button>
          </div>
        </div>

        <!-- Form Fields -->
        <div v-if="selectedFiles.length > 0" class="mt-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="uploadForm.website"
              required
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
            >
              <option value="">Select website...</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Title</label>
              <input
                v-model="uploadForm.title"
                type="text"
                placeholder="Media title (optional)"
                class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Alt Text</label>
              <input
                v-model="uploadForm.alt_text"
                type="text"
                placeholder="For accessibility"
                class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Caption</label>
            <textarea
              v-model="uploadForm.caption"
              rows="3"
              placeholder="Optional caption or description"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Tags (comma-separated)</label>
            <input
              v-model="uploadForm.tags"
              type="text"
              placeholder="tag1, tag2, tag3"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Separate tags with commas</p>
          </div>
        </div>

        <!-- Actions -->
        <div v-if="selectedFiles.length > 0" class="flex gap-4 pt-6 mt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            @click="handleUpload"
            :disabled="uploading || !uploadForm.website"
            class="flex-1 px-6 py-3 bg-linear-to-r from-blue-600 to-blue-700 text-white rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2"
          >
            <span v-if="uploading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
            <span v-else>Upload {{ selectedFiles.length }} {{ selectedFiles.length === 1 ? 'File' : 'Files' }}</span>
          </button>
          <button
            @click="handleCancel"
            class="px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import mediaAPI from '@/api/media'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  websites: {
    type: Array,
    default: () => []
  },
  acceptTypes: {
    type: String,
    default: 'image/*,video/*,.pdf,.doc,.docx'
  }
})

const emit = defineEmits(['update:show', 'uploaded'])

const { success: showSuccess, error: showError } = useToast()

const fileInput = ref(null)
const selectedFiles = ref([])
const isDragging = ref(false)
const uploading = ref(false)

const uploadForm = ref({
  website: '',
  title: '',
  alt_text: '',
  caption: '',
  tags: ''
})

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addFiles(files)
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  addFiles(files)
}

const addFiles = (files) => {
  files.forEach(file => {
    const fileObj = {
      file,
      name: file.name,
      size: file.size,
      preview: null
    }
    
    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        fileObj.preview = e.target.result
      }
      reader.readAsDataURL(file)
    }
    
    selectedFiles.value.push(fileObj)
  })
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const handleUpload = async () => {
  if (!uploadForm.value.website || selectedFiles.value.length === 0) return

  uploading.value = true
  try {
    const uploadPromises = selectedFiles.value.map(async (fileObj) => {
      const formData = new FormData()
      formData.append('file', fileObj.file)
      formData.append('website', uploadForm.value.website)
      if (uploadForm.value.title) formData.append('title', uploadForm.value.title)
      if (uploadForm.value.alt_text) formData.append('alt_text', uploadForm.value.alt_text)
      if (uploadForm.value.caption) formData.append('caption', uploadForm.value.caption)
      if (uploadForm.value.tags) {
        const tags = uploadForm.value.tags.split(',').map(t => t.trim()).filter(t => t)
        formData.append('tags', JSON.stringify(tags))
      }
      return mediaAPI.create(formData)
    })

    await Promise.all(uploadPromises)
    showSuccess(`Successfully uploaded ${selectedFiles.value.length} file(s)`)
    handleCancel()
    emit('uploaded')
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to upload media'))
  } finally {
    uploading.value = false
  }
}

const handleCancel = () => {
  selectedFiles.value = []
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
  emit('update:show', false)
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

watch(() => props.show, (newVal) => {
  if (!newVal) {
    handleCancel()
  }
})
</script>

<style scoped>
.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>

