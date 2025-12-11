<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Duplicate Account Detection</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Detect and manage suspected duplicate accounts</p>
      </div>
      <button
        @click="loadDuplicates"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Scanning...' : 'Scan for Duplicates' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Groups</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total?.suspected_groups || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Clients</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.clients?.suspected_groups || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Writers</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.writers?.suspected_groups || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Users Involved</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total?.users_involved || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <select
          v-model="roleFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadDuplicates"
        >
          <option value="">All Roles</option>
          <option value="client">Clients</option>
          <option value="writer">Writers</option>
        </select>
        <select
          v-model="confidenceFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadDuplicates"
        >
          <option value="low">Low Confidence</option>
          <option value="medium">Medium Confidence</option>
          <option value="high">High Confidence</option>
        </select>
        <input
          v-model.number="limitFilter"
          type="number"
          min="10"
          max="500"
          placeholder="Limit"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="loadDuplicates"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Scanning for duplicate accounts...</p>
    </div>

    <!-- Duplicates List -->
    <div v-else class="space-y-4">
      <div
        v-for="(duplicate, index) in duplicates"
        :key="index"
        class="card p-6"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <span
              :class="[
                'px-3 py-1 text-sm font-semibold rounded-full',
                duplicate.confidence === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                duplicate.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
              ]"
            >
              {{ duplicate.confidence?.toUpperCase() || 'LOW' }} Confidence
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ duplicate.match_count || 0 }} matches
            </span>
          </div>
        </div>
        
        <div class="space-y-3">
          <div
            v-for="user in duplicate.users"
            :key="user.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <p class="font-semibold text-gray-900 dark:text-white">{{ user.username || user.email }}</p>
                  <span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                    {{ user.role }}
                  </span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ user.email }}</p>
                <div class="flex gap-4 text-xs text-gray-500 dark:text-gray-400 mt-2">
                  <span>ID: {{ user.id }}</span>
                  <span v-if="user.website">Website: {{ user.website.name || user.website.id }}</span>
                  <span v-if="user.date_joined">Joined: {{ formatDate(user.date_joined) }}</span>
                </div>
              </div>
              <button
                @click="viewUser(user.id)"
                class="ml-4 px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                View
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="duplicate.signals && duplicate.signals.length > 0" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Detection Signals:</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(signal, sigIndex) in duplicate.signals"
              :key="sigIndex"
              class="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded"
            >
              {{ signal }}
            </span>
          </div>
        </div>
        
        <div v-if="duplicate.detection_types && duplicate.detection_types.length > 0" class="mt-2">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Detection Types:</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(type, typeIndex) in duplicate.detection_types"
              :key="typeIndex"
              class="px-2 py-1 text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 rounded"
            >
              {{ type }}
            </span>
          </div>
        </div>
      </div>
      
      <div v-if="duplicates.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No duplicate accounts detected
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import adminManagementAPI from '@/api/admin-management'

const router = useRouter()
const { error: showError } = useToast()

const loading = ref(false)
const duplicates = ref([])
const stats = ref({})
const roleFilter = ref('')
const confidenceFilter = ref('low')
const limitFilter = ref(100)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadDuplicates = async () => {
  loading.value = true
  try {
    const params = {
      min_confidence: confidenceFilter.value,
      limit: limitFilter.value,
    }
    if (roleFilter.value) params.role = roleFilter.value
    
    const [duplicatesResponse, statsResponse] = await Promise.all([
      adminManagementAPI.detectDuplicates(params),
      adminManagementAPI.getDuplicateStats(),
    ])
    
    duplicates.value = duplicatesResponse.data?.results || []
    stats.value = statsResponse.data || {}
  } catch (error) {
    showError('Failed to load duplicate accounts')
    console.error('Error loading duplicates:', error)
  } finally {
    loading.value = false
  }
}

const viewUser = (userId) => {
  router.push(`/admin/users/${userId}`)
}

onMounted(() => {
  loadDuplicates()
})
</script>

