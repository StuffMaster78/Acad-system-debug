<template>
  <div
    v-if="asset"
    class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-white dark:bg-gray-800 rounded-lg max-w-6xl w-full max-h-[95vh] overflow-hidden shadow-2xl flex flex-col">
      <!-- Header -->
      <div class="bg-linear-to-r from-gray-800 to-gray-900 dark:from-gray-700 dark:to-gray-800 p-4 flex items-center justify-between">
        <div class="flex-1 min-w-0">
          <h2 class="text-xl font-bold text-white truncate">{{ asset.title || 'Untitled Asset' }}</h2>
          <p class="text-gray-300 text-sm mt-1">{{ formatFileSize(asset.size_bytes) }} • {{ asset.type || 'Unknown' }}</p>
        </div>
        <div class="flex items-center gap-2 ml-4">
          <button
            @click="$emit('edit', asset)"
            class="p-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            title="Edit"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click="$emit('delete', asset)"
            class="p-2 text-gray-300 hover:text-red-400 hover:bg-gray-700 rounded-lg transition-colors"
            title="Delete"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button
            @click="$emit('close')"
            class="p-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            title="Close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Preview Content -->
      <div class="flex-1 overflow-auto bg-gray-900 p-8 flex items-center justify-center">
        <img
          v-if="asset.type === 'image' && asset.url"
          :src="asset.url"
          :alt="asset.alt_text || asset.title"
          class="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
        />
        <div v-else-if="asset.type === 'video'" class="text-center">
          <div class="w-32 h-32 bg-purple-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-16 h-16 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
          <p class="text-gray-300 text-lg">Video Preview</p>
          <p class="text-gray-500 text-sm mt-2">{{ asset.title || 'Untitled Video' }}</p>
          <a
            v-if="asset.url"
            :href="asset.url"
            target="_blank"
            class="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Open Video
          </a>
        </div>
        <div v-else class="text-center">
          <div class="w-32 h-32 bg-orange-900/40 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-16 h-16 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p class="text-gray-300 text-lg">Document Preview</p>
          <p class="text-gray-500 text-sm mt-2">{{ asset.title || 'Untitled Document' }}</p>
          <a
            v-if="asset.url"
            :href="asset.url"
            target="_blank"
            class="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Open Document
          </a>
        </div>
      </div>

      <!-- Details Footer -->
      <div class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Details</h3>
            <dl class="space-y-2 text-sm">
              <div class="flex justify-between">
                <dt class="text-gray-500 dark:text-gray-400">Alt Text</dt>
                <dd class="text-gray-900 dark:text-white font-medium">{{ asset.alt_text || 'Not set' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500 dark:text-gray-400">MIME Type</dt>
                <dd class="text-gray-900 dark:text-white font-medium">{{ asset.mime_type || 'Unknown' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500 dark:text-gray-400">Dimensions</dt>
                <dd class="text-gray-900 dark:text-white font-medium">
                  <span v-if="asset.width && asset.height">{{ asset.width }} × {{ asset.height }}px</span>
                  <span v-else>N/A</span>
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500 dark:text-gray-400">Uploaded</dt>
                <dd class="text-gray-900 dark:text-white font-medium">{{ formatDate(asset.created_at) }}</dd>
              </div>
            </dl>
          </div>
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Metadata</h3>
            <div v-if="asset.caption" class="mb-3">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Caption</p>
              <p class="text-sm text-gray-900 dark:text-white">{{ asset.caption }}</p>
            </div>
            <div v-if="asset.tags && asset.tags.length > 0">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Tags</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in asset.tags"
                  :key="tag"
                  class="px-2 py-1 bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300 text-xs rounded-full"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500 dark:text-gray-400">No tags</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  asset: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'delete'])

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
</script>

