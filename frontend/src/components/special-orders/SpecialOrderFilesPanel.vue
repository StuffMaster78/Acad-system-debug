<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Order Files</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">Upload and manage files for this special order</p>
      </div>
      <button
        v-if="allowUpload"
        @click="showUpload = !showUpload"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
      >
        {{ showUpload ? 'Hide Upload' : 'Upload Files' }}
      </button>
    </div>

    <div v-if="allowUpload && showUpload" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Description <span class="text-gray-400">(Optional)</span>
        </label>
        <textarea
          v-model="uploadForm.description"
          rows="3"
          class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
          placeholder="Add a brief description for these files..."
        ></textarea>
      </div>
      <FileUpload
        v-model="uploadedFiles"
        :multiple="true"
        :auto-upload="false"
        :max-size="100 * 1024 * 1024"
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.zip,.rar,.xls,.xlsx,.ppt,.pptx"
        label="Drop files here or click to browse"
      />
      <div class="flex items-center gap-3">
        <button
          @click="uploadSelectedFiles"
          :disabled="uploadedFiles.length === 0 || uploadingFiles"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm"
        >
          {{ uploadingFiles ? 'Uploading...' : `Upload ${uploadedFiles.length} File(s)` }}
        </button>
        <span v-if="uploadSuccess" class="text-sm text-green-600">{{ uploadSuccess }}</span>
        <span v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</span>
      </div>
    </div>

    <div v-if="loadingFiles" class="text-center py-10 text-gray-500 dark:text-gray-400">
      Loading files...
    </div>

    <div v-else-if="files.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <p>No files uploaded yet</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="file in files"
        :key="file.id"
        class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
      >
        <div class="flex items-center gap-3">
          <span class="text-2xl">📄</span>
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ file.file_name || 'Unnamed' }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(file.uploaded_at) }}</p>
            <p v-if="file.description" class="text-xs text-gray-500 dark:text-gray-400">{{ file.description }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <a
            v-if="file.file_url || file.url"
            :href="file.file_url || file.url"
            target="_blank"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
          >
            Download
          </a>
          <button
            v-if="canDelete(file)"
            @click="deleteFile(file.id)"
            class="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import FileUpload from '@/components/common/FileUpload.vue'
import specialOrdersAPI from '@/api/special-orders'

const props = defineProps({
  specialOrderId: {
    type: [Number, String],
    required: true
  },
  allowUpload: {
    type: Boolean,
    default: true
  },
  canDeleteAll: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['count-change'])

const authStore = useAuthStore()
const currentUserId = authStore.user?.id

const files = ref([])
const loadingFiles = ref(false)
const showUpload = ref(false)
const uploadedFiles = ref([])
const uploadingFiles = ref(false)
const uploadSuccess = ref('')
const uploadError = ref('')
const uploadForm = ref({ description: '' })

const loadFiles = async () => {
  if (!props.specialOrderId) return
  loadingFiles.value = true
  try {
    const response = await specialOrdersAPI.listInquiryFiles(props.specialOrderId)
    files.value = response.data.results || response.data || []
    emit('count-change', files.value.length)
  } catch (err) {
    console.error('Error loading files:', err)
    files.value = []
    emit('count-change', 0)
  } finally {
    loadingFiles.value = false
  }
}

const uploadSelectedFiles = async () => {
  if (!uploadedFiles.value.length || !props.specialOrderId) return
  uploadingFiles.value = true
  uploadError.value = ''
  uploadSuccess.value = ''
  try {
    const uploadPromises = uploadedFiles.value.map(fileObj => {
      return specialOrdersAPI.uploadInquiryFile({
        file: fileObj.file || fileObj,
        special_order: props.specialOrderId,
        description: uploadForm.value.description || ''
      })
    })
    await Promise.all(uploadPromises)
    uploadSuccess.value = `Uploaded ${uploadedFiles.value.length} file(s)`
    uploadedFiles.value = []
    uploadForm.value.description = ''
    await loadFiles()
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Failed to upload files'
  } finally {
    uploadingFiles.value = false
  }
}

const deleteFile = async (fileId) => {
  if (!confirm('Are you sure you want to delete this file?')) return
  try {
    await specialOrdersAPI.deleteInquiryFile(fileId)
    await loadFiles()
  } catch (err) {
    console.error('Error deleting file:', err)
  }
}

const canDelete = (file) => {
  if (props.canDeleteAll) return true
  return file.uploaded_by === currentUserId
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

watch(() => props.specialOrderId, loadFiles)
onMounted(loadFiles)
</script>
