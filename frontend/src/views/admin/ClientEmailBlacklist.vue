<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Client Email Blacklist</h1>
        <p class="mt-2 text-gray-600">Manage blacklisted client email addresses to prevent registration and access</p>
      </div>
      <button
        @click="showAddModal = true"
        class="btn btn-primary"
      >
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Email to Blacklist
      </button>
    </div>

    <!-- Stats Card -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Total Blacklisted Emails</p>
        <p class="text-2xl font-bold text-red-900">{{ blacklistedEmails.length }}</p>
      </div>
      <div class="card p-4 bg-gray-50 border border-gray-200">
        <p class="text-sm font-medium text-gray-700 mb-1">Active Blacklist Entries</p>
        <p class="text-2xl font-bold text-gray-900">{{ blacklistedEmails.length }}</p>
      </div>
      <div class="card p-4 bg-blue-50 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Recently Added</p>
        <p class="text-2xl font-bold text-blue-900">{{ recentCount }}</p>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search Email</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by email address..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset Filters</button>
        </div>
      </div>
    </div>

    <!-- Blacklisted Emails Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date Added</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="entry in filteredEmails" :key="entry.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ entry.email }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900 max-w-md">{{ entry.reason || 'No reason provided' }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(entry.date_added) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <button
                    @click="removeEmail(entry)"
                    class="text-red-600 hover:text-red-800 text-sm font-medium"
                    title="Remove from blacklist"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!filteredEmails.length && !loading" class="text-center py-12 text-gray-500">
          <p class="text-lg mb-2">No blacklisted emails found</p>
          <p class="text-sm">Click "Add Email to Blacklist" to add an email address</p>
        </div>
      </div>
    </div>

    <!-- Add Email Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">Add Email to Blacklist</h2>
          <button @click="closeAddModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <h3 class="font-semibold text-red-900 mb-2">⚠️ Important</h3>
          <p class="text-sm text-red-800">
            Blacklisted email addresses will be prevented from:
            <ul class="list-disc list-inside mt-2 space-y-1">
              <li>Registering new accounts</li>
              <li>Logging into existing accounts</li>
              <li>Accessing any system features</li>
            </ul>
            This action should be used for spam, fraud, or policy violations.
          </p>
        </div>

        <form @submit.prevent="addEmail" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Email Address *</label>
            <input
              v-model="emailForm.email"
              type="email"
              required
              placeholder="example@domain.com"
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              Enter the email address to blacklist. This will prevent all access for this email.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason for Blacklisting *</label>
            <textarea
              v-model="emailForm.reason"
              rows="4"
              required
              placeholder="Describe why this email is being blacklisted (e.g., spam, fraud, policy violation)..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">
              Be specific and clear. This reason will be used for records and auditing.
            </p>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeAddModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Adding...' : 'Add to Blacklist' }}
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
import { clientManagementAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const blacklistedEmails = ref([])
const message = ref('')
const messageSuccess = ref(false)
const showAddModal = ref(false)

const filters = ref({
  search: '',
})

const emailForm = ref({
  email: '',
  reason: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Filtering is done client-side via computed property
  }, 300)
}

const filteredEmails = computed(() => {
  if (!filters.value.search) return blacklistedEmails.value
  
  const search = filters.value.search.toLowerCase()
  return blacklistedEmails.value.filter(entry => 
    entry.email.toLowerCase().includes(search) ||
    (entry.reason && entry.reason.toLowerCase().includes(search))
  )
})

const recentCount = computed(() => {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  return blacklistedEmails.value.filter(entry => {
    const dateAdded = new Date(entry.date_added)
    return dateAdded >= thirtyDaysAgo
  }).length
})

const loadBlacklistedEmails = async () => {
  loading.value = true
  try {
    const response = await clientManagementAPI.listBlacklistedEmails()
    blacklistedEmails.value = Array.isArray(response.data) ? response.data : []
  } catch (e) {
    message.value = 'Failed to load blacklisted emails: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    loading.value = false
  }
}

const addEmail = async () => {
  saving.value = true
  message.value = ''
  try {
    await clientManagementAPI.addBlacklistedEmail(
      emailForm.value.email.trim(),
      emailForm.value.reason.trim()
    )
    message.value = `Email ${emailForm.value.email} has been added to the blacklist`
    messageSuccess.value = true
    closeAddModal()
    await loadBlacklistedEmails()
    showToast(message.value, 'success')
  } catch (e) {
    message.value = 'Failed to add email to blacklist: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const removeEmail = async (entry) => {
  if (!confirm(`Are you sure you want to remove ${entry.email} from the blacklist?\n\nThis will allow this email to register and access the system again.`)) return
  
  try {
    await clientManagementAPI.removeBlacklistedEmail(entry.email)
    message.value = `Email ${entry.email} has been removed from the blacklist`
    messageSuccess.value = true
    await loadBlacklistedEmails()
    showToast(message.value, 'success')
  } catch (e) {
    message.value = 'Failed to remove email from blacklist: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const closeAddModal = () => {
  showAddModal.value = false
  emailForm.value = { email: '', reason: '' }
}

const resetFilters = () => {
  filters.value = { search: '' }
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

onMounted(() => {
  loadBlacklistedEmails()
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
.btn-primary:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
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

