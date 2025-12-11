<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Compression Monitoring</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor response compression statistics and performance</p>
      </div>
      <button
        @click="clearStats"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        Clear Stats
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Compressions</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_compressions || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Avg Compression</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ formatNumber(stats.avg_compression_ratio) }}%</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Bytes Saved</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ formatBytes(stats.total_bytes_saved) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">MB Saved</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ formatNumber(stats.total_saved_mb) }} MB</p>
      </div>
    </div>

    <!-- Settings -->
    <div class="card p-4">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Compression Settings</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Min Length</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ compressionSettings.compress_min_length || 200 }} bytes</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Compression Level</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ compressionSettings.compress_level || 6 }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">MIME Types</p>
          <p class="text-sm text-gray-900 dark:text-white">{{ compressionSettings.compress_mimetypes?.join(', ') || 'All' }}</p>
        </div>
      </div>
    </div>

    <!-- Size Breakdown -->
    <div class="card p-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Size Breakdown</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Original Size</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatBytes(stats.total_original_size) }}</p>
        </div>
        <div class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Compressed Size</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatBytes(stats.total_compressed_size) }}</p>
        </div>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-700">
        <div
          class="bg-green-500 h-4 rounded-full transition-all"
          :style="{ width: `${getCompressionPercent()}%` }"
        ></div>
      </div>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
        {{ getCompressionPercent() }}% compression achieved
      </p>
    </div>

    <!-- Endpoint Statistics -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Endpoint Statistics</h2>
        <input
          v-model.number="limitFilter"
          type="number"
          min="100"
          max="10000"
          placeholder="Limit"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedLoadStats"
        />
      </div>
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(endpoint, index) in endpointStats"
          :key="index"
          class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-medium text-gray-900 dark:text-white">{{ endpoint.endpoint || 'Unknown' }}</h3>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ endpoint.count }} compressions</span>
          </div>
          <div class="grid grid-cols-3 gap-4 text-sm mb-2">
            <div>
              <p class="text-gray-500 dark:text-gray-400">Original</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ formatBytes(endpoint.total_original) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Compressed</p>
              <p class="font-semibold text-gray-900 dark:text-white">{{ formatBytes(endpoint.total_compressed) }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Saved</p>
              <p class="font-semibold text-green-600 dark:text-green-400">{{ formatBytes(endpoint.total_saved) }}</p>
            </div>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
            <div
              class="bg-green-500 h-2 rounded-full"
              :style="{ width: `${endpoint.compression_ratio || 0}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ formatNumber(endpoint.compression_ratio) }}% compression
          </p>
        </div>
        <div v-if="endpointStats.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No endpoint statistics available
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
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const stats = ref({})
const endpointStats = ref([])
const compressionSettings = ref({})
const limitFilter = ref(1000)

const debouncedLoadStats = debounce(() => {
  loadStats()
}, 300)

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(2)
}

const formatBytes = (bytes) => {
  if (!bytes && bytes !== 0) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

const getCompressionPercent = () => {
  if (!stats.value.total_original_size || stats.value.total_original_size === 0) return 0
  const saved = stats.value.total_bytes_saved || 0
  return Math.round((saved / stats.value.total_original_size) * 100)
}

const loadStats = async () => {
  loading.value = true
  try {
    const response = await adminManagementAPI.getCompressionStats(limitFilter.value || 1000)
    const data = response.data || {}
    
    stats.value = {
      total_compressions: data.total_compressions || 0,
      avg_compression_ratio: data.avg_compression_ratio || 0,
      total_bytes_saved: data.total_bytes_saved || 0,
      total_original_size: data.total_original_size || 0,
      total_compressed_size: data.total_compressed_size || 0,
      total_saved_mb: data.total_saved_mb || 0,
    }
    
    compressionSettings.value = data.settings || {}
    
    // Convert endpoint_stats object to array
    endpointStats.value = Object.entries(data.endpoint_stats || {}).map(([endpoint, stats]) => ({
      endpoint,
      ...stats,
    })).sort((a, b) => b.total_saved - a.total_saved)
  } catch (error) {
    showError('Failed to load compression statistics')
    console.error('Error loading stats:', error)
  } finally {
    loading.value = false
  }
}

const clearStats = () => {
  confirm.showDestructive(
    'Clear Compression Statistics',
    'Are you sure you want to clear all compression monitoring data?',
    'This action cannot be undone. All compression history will be permanently deleted.',
    async () => {
      try {
        await adminManagementAPI.clearCompressionStats()
        showSuccess('Compression statistics cleared successfully')
        loadStats()
      } catch (error) {
        showError('Failed to clear statistics')
      }
    }
  )
}

onMounted(() => {
  loadStats()
})
</script>

