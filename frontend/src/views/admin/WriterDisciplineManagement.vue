<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Discipline Management</h1>
        <p class="mt-2 text-gray-600">Manage strikes, warnings, and view discipline history for writers</p>
      </div>
      <button
        @click="showIssueStrikeModal = true"
        class="btn btn-primary"
      >
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Issue Strike
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Total Active Strikes</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.totalStrikes || 0 }}</p>
      </div>
      <div class="card p-4 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Active Warnings</p>
        <p class="text-2xl font-bold text-yellow-900">{{ stats.totalWarnings || 0 }}</p>
      </div>
      <div class="card p-4 bg-orange-50 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Suspended Writers</p>
        <p class="text-2xl font-bold text-orange-900">{{ stats.suspendedWriters || 0 }}</p>
      </div>
      <div class="card p-4 bg-gray-50 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Blacklisted Writers</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.blacklistedWriters || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search Writer</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Username, email..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadStrikes" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">View</label>
          <select v-model="activeTab" @change="loadData" class="w-full border rounded px-3 py-2">
            <option value="strikes">Strikes</option>
            <option value="warnings">Warnings</option>
            <option value="status">Writer Status</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Strikes Tab -->
    <div v-if="activeTab === 'strikes'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Issued By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="strike in strikes" :key="strike.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div>
                    <div class="font-medium text-gray-900">{{ strike.writer_username }}</div>
                    <div class="text-sm text-gray-500">{{ strike.writer_email }}</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ strike.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ strike.issued_by_username || 'System' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(strike.issued_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    @click="revokeStrike(strike)"
                    class="text-red-600 hover:text-red-800 text-sm"
                    title="Revoke this strike"
                  >
                    Revoke
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!strikes.length" class="text-center py-12 text-gray-500">
          No strikes found.
        </div>
      </div>
    </div>

    <!-- Warnings Tab -->
    <div v-if="activeTab === 'warnings'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Issued By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="warning in warnings" :key="warning.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ warning.writer?.user?.username || 'N/A' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getWarningTypeClass(warning.warning_type)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ warning.warning_type }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ warning.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ warning.issued_by?.username || 'System' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(warning.issued_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="warning.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs font-medium">
                    {{ warning.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    v-if="warning.is_active"
                    @click="deactivateWarning(warning)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    Deactivate
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!warnings.length" class="text-center py-12 text-gray-500">
          No warnings found.
        </div>
      </div>
    </div>

    <!-- Writer Status Tab -->
    <div v-if="activeTab === 'status'" class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active Strikes</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Strike</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="status in writerStatuses" :key="status.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ status.writer?.user?.username || 'N/A' }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getStatusBadgeClass(status)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ getStatusText(status) }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                  {{ status.active_strikes || 0 }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ status.last_strike_at ? formatDate(status.last_strike_at) : 'Never' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <button
                    @click="viewWriterDetails(status.writer)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!writerStatuses.length" class="text-center py-12 text-gray-500">
          No writer statuses found.
        </div>
      </div>
    </div>

    <!-- Issue Strike Modal -->
    <div v-if="showIssueStrikeModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Issue Strike to Writer</h2>
          <button @click="closeStrikeModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-blue-900 mb-2">What is a Strike?</h3>
          <p class="text-sm text-blue-800">
            A strike is a formal disciplinary action recorded against a writer for policy violations. 
            Strikes accumulate and can trigger automatic suspensions or blacklisting based on your 
            discipline configuration. Each strike should have a clear reason documented.
          </p>
        </div>

        <form @submit.prevent="issueStrike" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer *</label>
            <select v-model="strikeForm.writer" required class="w-full border rounded px-3 py-2">
              <option value="">Choose a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason for Strike *</label>
            <textarea
              v-model="strikeForm.reason"
              rows="4"
              required
              placeholder="Describe the policy violation or issue that warrants this strike..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              Be specific and clear. This reason will be visible to the writer and used for records.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeStrikeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Issuing...' : 'Issue Strike' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Issue Warning Modal -->
    <div v-if="showIssueWarningModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Issue Warning to Writer</h2>
          <button @click="closeWarningModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-yellow-900 mb-2">What is a Warning?</h3>
          <p class="text-sm text-yellow-800">
            A warning is a less severe disciplinary action than a strike. Warnings can accumulate 
            and may trigger automatic probation or suspension based on your escalation configuration. 
            Use warnings for minor infractions before issuing strikes.
          </p>
        </div>

        <form @submit.prevent="issueWarning" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer *</label>
            <select v-model="warningForm.writer" required class="w-full border rounded px-3 py-2">
              <option value="">Choose a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Warning Type *</label>
            <select v-model="warningForm.warning_type" required class="w-full border rounded px-3 py-2">
              <option value="minor">Minor</option>
              <option value="major">Major</option>
              <option value="critical">Critical</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">
              Critical warnings are more serious and may trigger immediate action.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason *</label>
            <textarea
              v-model="warningForm.reason"
              rows="4"
              required
              placeholder="Describe the issue..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Expires At (Optional)</label>
            <input
              v-model="warningForm.expires_at"
              type="datetime-local"
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              Leave empty for warnings that don't expire automatically.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeWarningModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Issuing...' : 'Issue Warning' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { writerManagementAPI, appealsAPI } from '@/api'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'
import { formatWriterName } from '@/utils/formatDisplay'

const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('strikes')
const strikes = ref([])
const warnings = ref([])
const writerStatuses = ref([])
const availableWriters = ref([])
const websites = ref([])
const message = ref('')
const messageSuccess = ref(false)

const showIssueStrikeModal = ref(false)
const showIssueWarningModal = ref(false)

const stats = ref({
  totalStrikes: 0,
  totalWarnings: 0,
  suspendedWriters: 0,
  blacklistedWriters: 0,
})

const filters = ref({
  search: '',
  website: '',
})

const strikeForm = ref({
  writer: '',
  reason: '',
})

const warningForm = ref({
  writer: '',
  warning_type: 'minor',
  reason: '',
  expires_at: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadData()
  }, 500)
}

const loadData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'strikes') {
      await loadStrikes()
    } else if (activeTab.value === 'warnings') {
      await loadWarnings()
    } else if (activeTab.value === 'status') {
      await loadWriterStatuses()
    }
  } catch (e) {
    message.value = 'Failed to load data: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const loadStrikes = async () => {
  try {
    const params = {}
    if (filters.value.website) params.website = filters.value.website
    if (filters.value.search) params.search = filters.value.search
    
    const res = await writerManagementAPI.listStrikes(params)
    strikes.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.totalStrikes = strikes.value.length
  } catch (e) {
    console.error('Failed to load strikes:', e)
  }
}

const loadWarnings = async () => {
  try {
    const params = {}
    if (filters.value.website) params.website = filters.value.website
    
    const res = await writerManagementAPI.listWarnings(params)
    warnings.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.totalWarnings = warnings.value.filter(w => w.is_active).length
  } catch (e) {
    console.error('Failed to load warnings:', e)
  }
}

const loadWriterStatuses = async () => {
  try {
    const res = await writerManagementAPI.listWriterStatuses()
    writerStatuses.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    stats.value.suspendedWriters = writerStatuses.value.filter(s => s.is_suspended).length
    stats.value.blacklistedWriters = writerStatuses.value.filter(s => s.is_blacklisted).length
  } catch (e) {
    console.error('Failed to load writer statuses:', e)
  }
}

const loadWriters = async () => {
  try {
    const res = await writerManagementAPI.listWriters()
    availableWriters.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (e) {
    console.error('Failed to load writers:', e)
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const issueStrike = async () => {
  saving.value = true
  message.value = ''
  try {
    await writerManagementAPI.createStrike({
      writer: strikeForm.value.writer,
      reason: strikeForm.value.reason,
    })
    message.value = 'Strike issued successfully'
    messageSuccess.value = true
    closeStrikeModal()
    await loadStrikes()
    showToast('Strike issued successfully', 'success')
  } catch (e) {
    message.value = 'Failed to issue strike: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const issueWarning = async () => {
  saving.value = true
  message.value = ''
  try {
    await writerManagementAPI.createWarning({
      writer: warningForm.value.writer,
      warning_type: warningForm.value.warning_type,
      reason: warningForm.value.reason,
      expires_at: warningForm.value.expires_at || null,
    })
    message.value = 'Warning issued successfully'
    messageSuccess.value = true
    closeWarningModal()
    await loadWarnings()
    showToast('Warning issued successfully', 'success')
  } catch (e) {
    message.value = 'Failed to issue warning: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const revokeStrike = async (strike) => {
  if (!confirm(`Are you sure you want to revoke this strike?\n\nReason: ${strike.reason}\n\nThis action cannot be undone.`)) return
  
  try {
    await writerManagementAPI.revokeStrike(strike.id)
    message.value = 'Strike revoked successfully'
    messageSuccess.value = true
    await loadStrikes()
    showToast('Strike revoked successfully', 'success')
  } catch (e) {
    message.value = 'Failed to revoke strike: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const deactivateWarning = async (warning) => {
  if (!confirm('Are you sure you want to deactivate this warning?')) return
  
  try {
    await writerManagementAPI.deactivateWarning(warning.id)
    message.value = 'Warning deactivated successfully'
    messageSuccess.value = true
    await loadWarnings()
    showToast('Warning deactivated successfully', 'success')
  } catch (e) {
    message.value = 'Failed to deactivate warning: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const viewWriterDetails = (writer) => {
  // Navigate to writer detail page or show modal
  window.location.href = `/admin/user-management?role=writer&search=${writer?.user?.username || ''}`
}

const closeStrikeModal = () => {
  showIssueStrikeModal.value = false
  strikeForm.value = { writer: '', reason: '' }
}

const closeWarningModal = () => {
  showIssueWarningModal.value = false
  warningForm.value = { writer: '', warning_type: 'minor', reason: '', expires_at: '' }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// formatWriterName is now imported from utils

const getWarningTypeClass = (type) => {
  const classes = {
    minor: 'bg-yellow-100 text-yellow-800',
    major: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusBadgeClass = (status) => {
  if (status.is_blacklisted) return 'bg-black text-white'
  if (status.is_suspended) return 'bg-red-100 text-red-800'
  if (status.is_on_probation) return 'bg-yellow-100 text-yellow-800'
  if (status.is_active) return 'bg-green-100 text-green-800'
  return 'bg-gray-100 text-gray-800'
}

const getStatusText = (status) => {
  if (status.is_blacklisted) return 'Blacklisted'
  if (status.is_suspended) return 'Suspended'
  if (status.is_on_probation) return 'On Probation'
  if (status.is_active) return 'Active'
  return 'Inactive'
}

onMounted(async () => {
  await Promise.all([loadData(), loadWriters(), loadWebsites()])
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

