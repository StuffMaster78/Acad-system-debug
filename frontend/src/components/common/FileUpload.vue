<template>
  <div class="file-upload">
    <!-- Drag and Drop Zone -->
    <div
      v-if="!files.length || multiple"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @dragenter.prevent
      class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
      :class="[
        isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50',
        error ? 'border-red-300 bg-red-50' : '',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-primary-400'
      ]"
      @click="!disabled && $refs.fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        :multiple="multiple"
        :accept="accept"
        class="hidden"
        @change="handleFileSelect"
        :disabled="disabled"
      />
      
      <div v-if="!uploading" class="space-y-2">
        <div class="text-4xl">📎</div>
        <div class="text-sm font-medium text-gray-700">
          {{ label || (multiple ? 'Drop files here or click to browse' : 'Drop file here or click to browse') }}
        </div>
        <div class="text-xs text-gray-500">
          {{ accept ? `Accepted: ${accept}` : 'All file types' }}
          <span v-if="maxSize"> • Max size: {{ formatFileSize(maxSize) }}</span>
        </div>
      </div>
      
      <div v-else class="space-y-2">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <div class="text-sm text-gray-600">Uploading...</div>
      </div>
    </div>

    <!-- File List -->
    <div v-if="files.length > 0" class="mt-4 space-y-2">
      <div
        v-for="(file, index) in files"
        :key="file.id || index"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
      >
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="text-2xl">📄</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-900 truncate">
              {{ file.name || file.file_name }}
            </div>
            <div class="text-xs text-gray-500">
              <span v-if="file.size || file.file_size">{{ formatFileSize(file.size || file.file_size) }}</span>
              <span v-if="file.uploaded_at" class="ml-2">
                Uploaded {{ formatDate(file.uploaded_at) }}
              </span>
            </div>
            <!-- Upload Progress -->
            <div v-if="file.uploading" class="mt-2">
              <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  class="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                  :style="{ width: `${file.progress || 0}%` }"
                ></div>
              </div>
              <div class="text-xs text-gray-500 mt-1">{{ file.progress || 0 }}%</div>
            </div>
            <!-- Error Message -->
            <div v-if="file.error" class="text-xs text-red-600 mt-1">
              {{ file.error }}
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <!-- Preview/Download Button -->
          <button
            v-if="file.url || file.download_url"
            @click="handleDownload(file)"
            class="p-2 text-gray-600 hover:text-primary-600 hover:bg-gray-100 rounded"
            title="Download"
          >
            ⬇️
          </button>
          <!-- Remove Button -->
          <button
            v-if="!disabled && !file.uploading"
            @click="removeFile(index)"
            class="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded"
            title="Remove"
          >
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error && !files.some(f => f.error)" class="mt-2 text-sm text-red-600">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  multiple: {
    type: Boolean,
    default: false
  },
  accept: {
    type: String,
    default: ''
  },
  maxSize: {
    type: Number,
    default: null // in bytes
  },
  label: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  autoUpload: {
    type: Boolean,
    default: false
  },
  uploadUrl: {
    type: String,
    default: ''
  },
  uploadData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'upload', 'upload-success', 'upload-error', 'remove'])

const files = ref([...props.modelValue])
const isDragging = ref(false)
const uploading = ref(false)
const error = ref('')

watch(() => props.modelValue, (newVal) => {
  files.value = [...newVal]
}, { deep: true })

watch(files, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

const handleDrop = (event) => {
  if (props.disabled) return
  isDragging.value = false
  const droppedFiles = Array.from(event.dataTransfer.files)
  processFiles(droppedFiles)
}

const handleFileSelect = (event) => {
  if (props.disabled) return
  const selectedFiles = Array.from(event.target.files || [])
  processFiles(selectedFiles)
  // Reset input
  if (event.target) {
    event.target.value = ''
  }
}

const processFiles = (fileList) => {
  error.value = ''
  
  const newFiles = fileList.map(file => {
    // Validate file size
    if (props.maxSize && file.size > props.maxSize) {
      error.value = `File "${file.name}" exceeds maximum size of ${formatFileSize(props.maxSize)}`
      return null
    }
    
    // Validate file type
    if (props.accept) {
      const acceptedTypes = props.accept.split(',').map(t => t.trim())
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
      const fileType = file.type
      
      const isAccepted = acceptedTypes.some(acceptType => {
        if (acceptType.startsWith('.')) {
          return fileExtension === acceptType.toLowerCase()
        }
        return fileType.match(acceptType.replace('*', '.*'))
      })
      
      if (!isAccepted) {
        error.value = `File "${file.name}" is not an accepted file type`
        return null
      }
    }
    
    return {
      file: file,
      name: file.name,
      size: file.size,
      type: file.type,
      uploading: props.autoUpload,
      progress: 0
    }
  }).filter(f => f !== null)
  
  if (props.multiple) {
    files.value.push(...newFiles)
  } else {
    files.value = newFiles.length > 0 ? [newFiles[0]] : []
  }
  
  // Auto-upload if enabled
  if (props.autoUpload && props.uploadUrl) {
    newFiles.forEach(fileObj => {
      uploadFile(fileObj)
    })
  }
  
  emit('upload', newFiles.map(f => f.file))
}

const uploadFile = async (fileObj) => {
  if (!props.uploadUrl) {
    console.warn('No upload URL provided')
    return
  }
  
  fileObj.uploading = true
  fileObj.progress = 0
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', fileObj.file)
    
    // Add additional data
    Object.keys(props.uploadData).forEach(key => {
      formData.append(key, props.uploadData[key])
    })
    
    // Use XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest()
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        fileObj.progress = Math.round((e.loaded / e.total) * 100)
      }
    })
    
    const uploadPromise = new Promise((resolve, reject) => {
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            resolve(response)
          } catch (e) {
            resolve(xhr.responseText)
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText}`))
        }
      })
      
      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'))
      })
      
      xhr.open('POST', props.uploadUrl)
      
      // Add auth token
      const token = localStorage.getItem('access_token')
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      }
      
      xhr.send(formData)
    })
    
    const response = await uploadPromise
    
    // Update file object with server response
    Object.assign(fileObj, {
      id: response.id || response.data?.id,
      url: response.url || response.data?.url,
      download_url: response.download_url || response.data?.download_url,
      uploaded_at: response.uploaded_at || response.data?.uploaded_at || new Date().toISOString(),
      uploading: false,
      progress: 100
    })
    
    emit('upload-success', fileObj, response)
  } catch (err) {
    fileObj.error = err.message || 'Upload failed'
    fileObj.uploading = false
    emit('upload-error', fileObj, err)
  } finally {
    uploading.value = files.value.some(f => f.uploading)
  }
}

const removeFile = (index) => {
  const removed = files.value[index]
  files.value.splice(index, 1)
  emit('remove', removed)
}

const handleDownload = (file) => {
  const url = file.download_url || file.url
  if (url) {
    window.open(url, '_blank')
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.file-upload {
  width: 100%;
}
</style>

