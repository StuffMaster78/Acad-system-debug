<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Duplicate Account Detection</h1>
        <p class="mt-2 text-gray-600">Identify suspected clients and writers with multiple accounts across websites</p>
      </div>
      <button
        @click="runDetection"
        :disabled="detecting"
        class="btn btn-primary"
      >
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        {{ detecting ? 'Detecting...' : 'Run Detection' }}
      </button>
    </div>

    <!-- Info Banner -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 class="font-semibold text-blue-900 mb-2">How Duplicate Detection Works</h3>
      <p class="text-sm text-blue-800 mb-2">
        This system analyzes multiple signals to identify suspected duplicate accounts:
      </p>
      <ul class="text-sm text-blue-800 list-disc list-inside space-y-1">
        <li><strong>Email Similarity:</strong> Detects accounts with similar/normalized emails (e.g., user@gmail.com vs user+1@gmail.com)</li>
        <li><strong>IP Address Overlap:</strong> Identifies accounts that have logged in from the same IP addresses</li>
        <li><strong>Name Similarity:</strong> Finds accounts with similar first and last names</li>
        <li><strong>Cross-Website Activity:</strong> Detects users active across multiple websites with matching patterns</li>
      </ul>
      <p class="text-sm text-blue-800 mt-2">
        <strong>Note:</strong> These are suspected duplicates. Review each case carefully before taking action, 
        as legitimate users may share IPs (e.g., family members, office networks) or have similar names.
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Suspected Client Groups</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.clients?.suspected_groups || 0 }}</p>
        <p class="text-xs text-red-600 mt-1">{{ stats.clients?.users_involved || 0 }} users involved</p>
      </div>
      <div class="card p-4 bg-orange-50 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Suspected Writer Groups</p>
        <p class="text-2xl font-bold text-orange-900">{{ stats.writers?.suspected_groups || 0 }}</p>
        <p class="text-xs text-orange-600 mt-1">{{ stats.writers?.users_involved || 0 }} users involved</p>
      </div>
      <div class="card p-4 bg-purple-50 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Suspected</p>
        <p class="text-2xl font-bold text-purple-900">{{ stats.total?.suspected_groups || 0 }}</p>
        <p class="text-xs text-purple-600 mt-1">{{ stats.total?.users_involved || 0 }} total users</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Role</label>
          <select v-model="filters.role" @change="loadDuplicates" class="w-full border rounded px-3 py-2">
            <option value="">All Roles</option>
            <option value="client">Clients Only</option>
            <option value="writer">Writers Only</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Confidence Level</label>
          <select v-model="filters.min_confidence" @change="loadDuplicates" class="w-full border rounded px-3 py-2">
            <option value="low">Low & Above</option>
            <option value="medium">Medium & Above</option>
            <option value="high">High Only</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Detection Type</label>
          <select v-model="filters.detection_type" @change="loadDuplicates" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="email">Email Similarity</option>
            <option value="ip_address">IP Address</option>
            <option value="name_similarity">Name Similarity</option>
            <option value="cross_website">Cross-Website</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Duplicates Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Websites</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Detection Signals</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="(dup, index) in duplicates" :key="index" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="space-y-2">
                    <div v-for="user in dup.users" :key="user.id" class="flex items-center gap-2">
                      <div class="flex-1">
                        <div class="font-medium text-gray-900">{{ user.username }}</div>
                        <div class="text-sm text-gray-500">{{ user.email }}</div>
                        <div class="text-xs text-gray-400">
                          {{ user.role }} • Joined: {{ formatDate(user.date_joined) }}
                        </div>
                        <div class="flex items-center gap-2 mt-1">
                          <span v-if="user.is_suspended" class="px-1.5 py-0.5 rounded text-xs bg-red-100 text-red-800">Suspended</span>
                          <span v-if="user.is_blacklisted" class="px-1.5 py-0.5 rounded text-xs bg-black text-white">Blacklisted</span>
                          <span v-if="!user.is_active" class="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-800">Inactive</span>
                        </div>
                      </div>
                      <button
                        @click="viewUserDetails(user.id)"
                        class="text-blue-600 hover:text-blue-800 text-sm"
                        title="View User Details"
                      >
                        👁️
                      </button>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="space-y-1">
                    <span
                      v-for="website in dup.websites"
                      :key="website.id"
                      class="inline-block px-2 py-1 rounded text-xs bg-blue-100 text-blue-800 mr-1 mb-1"
                    >
                      {{ website.name }}
                    </span>
                    <span v-if="!dup.websites.length" class="text-xs text-gray-400">—</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="space-y-1">
                    <div
                      v-for="(signal, idx) in dup.signals"
                      :key="idx"
                      class="text-xs text-gray-700"
                    >
                      • {{ signal }}
                    </div>
                    <div class="text-xs text-gray-500 mt-1">
                      Types: {{ dup.detection_types.join(', ') }}
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getConfidenceClass(dup.confidence)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ dup.confidence }}
                  </span>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ dup.match_count }} match{{ dup.match_count !== 1 ? 'es' : '' }}
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <button
                      @click="viewDuplicateDetails(dup)"
                      class="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Details
                    </button>
                    <button
                      @click="markAsReviewed(dup)"
                      class="text-green-600 hover:text-green-800 text-sm"
                      title="Mark as Reviewed"
                    >
                      ✓
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!duplicates.length" class="text-center py-12 text-gray-500">
          <p class="mb-2">No suspected duplicates found.</p>
          <p class="text-sm text-gray-400">Click "Run Detection" to scan for duplicate accounts.</p>
        </div>
      </div>
    </div>

    <!-- Duplicate Detail Modal -->
    <div v-if="viewingDuplicate" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold">Duplicate Account Details</h2>
          <button @click="viewingDuplicate = null" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div class="space-y-6">
          <!-- Users Section -->
          <div>
            <h3 class="text-lg font-semibold mb-3">Suspected Duplicate Users</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="user in viewingDuplicate.users"
                :key="user.id"
                class="border rounded-lg p-4"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-semibold">{{ user.username }}</h4>
                  <span :class="getRoleBadgeClass(user.role)" class="px-2 py-1 rounded text-xs">
                    {{ user.role }}
                  </span>
                </div>
                <div class="space-y-1 text-sm">
                  <div><span class="text-gray-600">Email:</span> {{ user.email }}</div>
                  <div><span class="text-gray-600">Name:</span> {{ user.first_name }} {{ user.last_name }}</div>
                  <div><span class="text-gray-600">Website:</span> {{ user.website?.name || 'N/A' }}</div>
                  <div><span class="text-gray-600">Joined:</span> {{ formatDateTime(user.date_joined) }}</div>
                  <div><span class="text-gray-600">Last Login:</span> {{ user.last_login ? formatDateTime(user.last_login) : 'Never' }}</div>
                  <div class="flex items-center gap-2 mt-2">
                    <button
                      @click="viewUserDetails(user.id)"
                      class="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View Full Profile →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Detection Signals -->
          <div>
            <h3 class="text-lg font-semibold mb-3">Detection Signals</h3>
            <div class="bg-gray-50 border rounded-lg p-4">
              <ul class="space-y-2">
                <li v-for="(signal, idx) in viewingDuplicate.signals" :key="idx" class="flex items-start">
                  <span class="text-green-600 mr-2">•</span>
                  <span class="text-sm text-gray-700">{{ signal }}</span>
                </li>
              </ul>
              <div class="mt-3 pt-3 border-t">
                <span class="text-xs font-medium text-gray-600">Detection Types:</span>
                <span class="ml-2 text-xs text-gray-700">{{ viewingDuplicate.detection_types.join(', ') }}</span>
              </div>
            </div>
          </div>

          <!-- Confidence & Recommendations -->
          <div>
            <h3 class="text-lg font-semibold mb-3">Confidence & Recommendations</h3>
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div class="flex items-center gap-2 mb-2">
                <span :class="getConfidenceClass(viewingDuplicate.confidence)" class="px-2 py-1 rounded text-xs font-medium">
                  {{ viewingDuplicate.confidence.toUpperCase() }} Confidence
                </span>
                <span class="text-xs text-gray-600">{{ viewingDuplicate.match_count }} matching signal(s)</span>
              </div>
              <p class="text-sm text-yellow-800 mt-2">
                <strong>Recommendation:</strong>
                <span v-if="viewingDuplicate.confidence === 'high'">
                  High confidence suggests these are likely duplicate accounts. Review user activity and consider merging or suspending duplicates.
                </span>
                <span v-else-if="viewingDuplicate.confidence === 'medium'">
                  Medium confidence - these accounts share some characteristics but may be legitimate. Investigate further before taking action.
                </span>
                <span v-else>
                  Low confidence - these accounts have minor similarities. May be false positives (e.g., family members, shared networks).
                </span>
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-2 pt-4 border-t">
            <button
              @click="viewUserDetails(viewingDuplicate.users[0].id)"
              class="btn btn-primary flex-1"
            >
              View First User
            </button>
            <button
              v-if="viewingDuplicate.users.length > 1"
              @click="viewUserDetails(viewingDuplicate.users[1].id)"
              class="btn btn-secondary flex-1"
            >
              View Second User
            </button>
            <button
              @click="markAsReviewed(viewingDuplicate)"
              class="btn bg-green-600 text-white hover:bg-green-700"
            >
              Mark as Reviewed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { duplicateDetectionAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'

const { showToast } = useToast()
const router = useRouter()

const loading = ref(false)
const detecting = ref(false)
const duplicates = ref([])
const stats = ref({
  clients: { suspected_groups: 0, users_involved: 0 },
  writers: { suspected_groups: 0, users_involved: 0 },
  total: { suspected_groups: 0, users_involved: 0 },
})
const viewingDuplicate = ref(null)
const message = ref('')
const messageSuccess = ref(false)

const filters = ref({
  role: '',
  min_confidence: 'low',
  detection_type: '',
})

const runDetection = async () => {
  detecting.value = true
  message.value = ''
  try {
    await loadDuplicates()
    await loadStats()
    showToast('Duplicate detection completed', 'success')
  } catch (e) {
    message.value = 'Failed to run detection: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    detecting.value = false
  }
}

const loadDuplicates = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.role) params.role = filters.value.role
    if (filters.value.min_confidence) params.min_confidence = filters.value.min_confidence
    if (filters.value.detection_type) {
      // Filter client-side by detection type
    }
    
    const res = await duplicateDetectionAPI.detectDuplicates(params)
    let results = res.data?.results || []
    
    // Filter by detection type if specified
    if (filters.value.detection_type) {
      results = results.filter(dup => 
        dup.detection_types.includes(filters.value.detection_type)
      )
    }
    
    duplicates.value = results
  } catch (e) {
    message.value = 'Failed to load duplicates: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await duplicateDetectionAPI.getStats()
    stats.value = res.data || stats.value
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const viewDuplicateDetails = (dup) => {
  viewingDuplicate.value = dup
}

const viewUserDetails = (userId) => {
  router.push(`/admin/users?user=${userId}`)
}

const markAsReviewed = (dup) => {
  // In a full implementation, this would mark the duplicate as reviewed in the backend
  // For now, just remove from the list
  const index = duplicates.value.findIndex(d => 
    JSON.stringify(d.user_ids) === JSON.stringify(dup.user_ids)
  )
  if (index > -1) {
    duplicates.value.splice(index, 1)
    showToast('Marked as reviewed', 'success')
  }
}

const resetFilters = () => {
  filters.value = {
    role: '',
    min_confidence: 'low',
    detection_type: '',
  }
  loadDuplicates()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getConfidenceClass = (confidence) => {
  const classes = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-gray-100 text-gray-800',
  }
  return classes[confidence] || 'bg-gray-100 text-gray-800'
}

const getRoleBadgeClass = (role) => {
  const classes = {
    client: 'bg-blue-100 text-blue-800',
    writer: 'bg-green-100 text-green-800',
    editor: 'bg-purple-100 text-purple-800',
    admin: 'bg-red-100 text-red-800',
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await loadStats()
})
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.btn-primary {
  background-color: #2563eb;
  color: white;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  padding: 1.5rem;
}
</style>

