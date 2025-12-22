<template>
  <div
    v-if="asset"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
      <!-- Header -->
      <div class="bg-linear-to-r from-indigo-600 to-indigo-700 p-6 rounded-t-lg">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold text-white">Edit Media</h2>
            <p class="text-indigo-100 mt-1">{{ asset.title || 'Untitled Asset' }}</p>
          </div>
          <button
            @click="$emit('close')"
            class="text-white hover:text-indigo-200 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="p-6">
        <!-- Preview -->
        <div class="mb-6">
          <div class="aspect-video bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
            <img
              v-if="asset.type === 'image' && asset.url"
              :src="asset.url"
              :alt="asset.alt_text || asset.title"
              class="w-full h-full object-contain"
            />
            <div v-else-if="asset.type === 'video'" class="w-full h-full flex items-center justify-center">
              <div class="text-center">
                <svg class="w-16 h-16 text-purple-400 mx-auto mb-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <p class="text-gray-600 dark:text-gray-400">Video File</p>
              </div>
            </div>
            <div v-else class="w-full h-full flex items-center justify-center">
              <div class="text-center">
                <svg class="w-16 h-16 text-orange-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-600 dark:text-gray-400">Document File</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleUpdate" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Title
            </label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Alt Text
            </label>
            <input
              v-model="editForm.alt_text"
              type="text"
              placeholder="For accessibility"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white transition-all"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Describe the image for screen readers</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Caption
            </label>
            <textarea
              v-model="editForm.caption"
              rows="4"
              placeholder="Optional caption or description"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white transition-all"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tags (comma-separated)
            </label>
            <input
              v-model="editForm.tags"
              type="text"
              placeholder="tag1, tag2, tag3"
              class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white transition-all"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Separate tags with commas</p>
          </div>

          <!-- Asset Info -->
          <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Asset Information</h3>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-gray-500 dark:text-gray-400">Type</p>
                <p class="font-medium text-gray-900 dark:text-white mt-1">{{ asset.type || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-gray-500 dark:text-gray-400">Size</p>
                <p class="font-medium text-gray-900 dark:text-white mt-1">{{ formatFileSize(asset.size_bytes) }}</p>
              </div>
              <div>
                <p class="text-gray-500 dark:text-gray-400">Uploaded</p>
                <p class="font-medium text-gray-900 dark:text-white mt-1">{{ formatDate(asset.created_at) }}</p>
              </div>
              <div>
                <p class="text-gray-500 dark:text-gray-400">MIME Type</p>
                <p class="font-medium text-gray-900 dark:text-white mt-1">{{ asset.mime_type || 'Unknown' }}</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-6 py-3 bg-linear-to-r from-indigo-600 to-indigo-700 text-white rounded-lg font-medium hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md flex items-center justify-center gap-2"
            >
              <span v-if="saving" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></span>
              <span v-else>Save Changes</span>
            </button>
            <button
              type="button"
              @click="$emit('close')"
              class="px-6 py-3 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
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
  asset: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'updated'])

const { success: showSuccess, error: showError } = useToast()

const saving = ref(false)
const editForm = ref({
  title: '',
  alt_text: '',
  caption: '',
  tags: ''
})

const initializeForm = () => {
  if (props.asset) {
    editForm.value = {
      title: props.asset.title || '',
      alt_text: props.asset.alt_text || '',
      caption: props.asset.caption || '',
      tags: (props.asset.tags || []).join(', ')
    }
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

    await mediaAPI.patch(props.asset.id, data)
    showSuccess('Media updated successfully')
    emit('updated')
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to update media'))
  } finally {
    saving.value = false
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

watch(() => props.asset, () => {
  initializeForm()
}, { immediate: true })
</script>

<style scoped>
.aspect-video {
  aspect-ratio: 16 / 9;
}
</style>

