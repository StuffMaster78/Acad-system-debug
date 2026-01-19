<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Fines Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track and manage writer fines and revenue</p>
      </div>
      <button
        @click="showIssueModal = true"
        class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Issue Fine
      </button>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Fines</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ statistics.total_fines || 0 }}</p>
        <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">${{ formatCurrency(statistics.total_amount || 0) }}</p>
      </div>
      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-700 rounded-lg p-6">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Revenue</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">${{ formatCurrency(statistics.total_revenue || 0) }}</p>
        <p class="text-xs text-green-600 dark:text-green-400 mt-1">From paid fines</p>
      </div>
      <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-6">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Recent (30d)</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ statistics.recent_fines_count || 0 }}</p>
        <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">${{ formatCurrency(statistics.recent_revenue || 0) }}</p>
      </div>
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Pending</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">
          {{ (statistics.status_breakdown?.issued?.count || 0) + (statistics.status_breakdown?.disputed?.count || 0) }}
        </p>
        <p class="text-xs text-purple-600 dark:text-purple-400 mt-1">Awaiting resolution</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadData" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="issued">Issued</option>
            <option value="paid">Paid</option>
            <option value="disputed">Disputed</option>
            <option value="waived">Waived</option>
            <option value="voided">Voided</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Start Date</label>
          <input v-model="filters.start_date" type="date" @change="loadData" class="w-full border rounded px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">End Date</label>
          <input v-model="filters.end_date" type="date" @change="loadData" class="w-full border rounded px-3 py-2" />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Fines Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Issued</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="fines.length === 0">
              <td colspan="7" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                No fines found
              </td>
            </tr>
            <tr
              v-for="fine in fines"
              :key="fine.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">#{{ fine.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                <a :href="`/orders/${fine.order?.id}`" class="text-blue-600 hover:underline">Order #{{ fine.order?.id }}</a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ fine.fine_type_config?.name || fine.fine_type || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">
                ${{ formatCurrency(fine.amount) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(fine.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusLabel(fine.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(fine.imposed_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    @click="viewFine(fine)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    title="View Details"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    v-if="fine.status === 'issued' || fine.status === 'disputed'"
                    @click="waiveFine(fine)"
                    class="text-green-600 hover:text-green-900 dark:text-green-400"
                    title="Waive Fine"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <button
                    v-if="fine.status === 'issued' || fine.status === 'disputed'"
                    @click="voidFine(fine)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400"
                    title="Void Fine"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="!loading && fines.length > 0" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Showing {{ fines.length }} fine(s)
        </div>
      </div>
    </div>

    <!-- Issue Fine Modal -->
    <div
      v-if="showIssueModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="showIssueModal = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Issue Fine</h3>
            <button @click="showIssueModal = false" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="issueFine" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Order ID *</label>
              <input
                v-model.number="fineForm.order_id"
                type="number"
                required
                placeholder="Order ID"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fine Type *</label>
              <input
                v-model="fineForm.fine_type_code"
                type="text"
                required
                placeholder="e.g., quality_issue, late_submission"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Reason *</label>
              <textarea
                v-model="fineForm.reason"
                required
                rows="3"
                placeholder="Detailed reason for the fine"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Custom Amount (Optional)</label>
              <input
                v-model.number="fineForm.custom_amount"
                type="number"
                step="0.01"
                placeholder="Override default amount"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div class="flex gap-3 pt-4">
              <button
                type="button"
                @click="showIssueModal = false"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="issuing"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ issuing ? 'Issuing...' : 'Issue Fine' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import finesAPI from '@/api/fines'

const { showToast } = useToast()

const loading = ref(true)
const fines = ref([])
const statistics = ref(null)
const showIssueModal = ref(false)
const issuing = ref(false)

const filters = ref({
  status: '',
  start_date: '',
  end_date: '',
})

const fineForm = ref({
  order_id: '',
  fine_type_code: '',
  reason: '',
  custom_amount: null,
})

const loadData = async () => {
  loading.value = true
  try {
    const [finesResponse, statsResponse] = await Promise.all([
      finesAPI.listFines(filters.value),
      finesAPI.getStatistics(filters.value)
    ])
    fines.value = Array.isArray(finesResponse.data) ? finesResponse.data : finesResponse.data.results || []
    statistics.value = statsResponse.data
  } catch (error) {
    showToast('Failed to load fines: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error loading fines:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    start_date: '',
    end_date: '',
  }
  loadData()
}

const issueFine = async () => {
  issuing.value = true
  try {
    await finesAPI.issue(fineForm.value)
    showToast('Fine issued successfully', 'success')
    showIssueModal.value = false
    fineForm.value = {
      order_id: '',
      fine_type_code: '',
      reason: '',
      custom_amount: null,
    }
    await loadData()
  } catch (error) {
    showToast('Failed to issue fine: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error issuing fine:', error)
  } finally {
    issuing.value = false
  }
}

const viewFine = (fine) => {
  // Navigate to fine detail or show modal
  console.log('View fine:', fine)
}

const waiveFine = async (fine) => {
  if (!confirm(`Are you sure you want to waive fine #${fine.id}?`)) return
  
  try {
    await finesAPI.waiveFine(fine.id, { reason: 'Waived by admin' })
    showToast('Fine waived successfully', 'success')
    await loadData()
  } catch (error) {
    showToast('Failed to waive fine: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error waiving fine:', error)
  }
}

const voidFine = async (fine) => {
  if (!confirm(`Are you sure you want to void fine #${fine.id}?`)) return
  
  try {
    await finesAPI.voidFine(fine.id, { reason: 'Voided by admin' })
    showToast('Fine voided successfully', 'success')
    await loadData()
  } catch (error) {
    showToast('Failed to void fine: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error voiding fine:', error)
  }
}

const getStatusClass = (status) => {
  const classes = {
    'issued': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'paid': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'disputed': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'waived': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'voided': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'resolved': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'issued': 'Issued',
    'paid': 'Paid',
    'disputed': 'Disputed',
    'waived': 'Waived',
    'voided': 'Voided',
    'resolved': 'Resolved',
  }
  return labels[status] || status
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  loadData()
})
</script>
