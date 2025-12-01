<template>
  <div class="escalations space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Escalation Management</h1>
        <p class="mt-2 text-gray-600">Manage escalated tickets and issues</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="statusFilter"
          @change="fetchEscalations"
          class="px-4 py-2 border rounded-lg"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
          <option value="in_progress">In Progress</option>
        </select>
        <button
          @click="fetchEscalations"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="escalationsData" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Escalations"
        :value="escalationsData.total_escalations || 0"
        icon="📢"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Pending"
        :value="escalationsData.unresolved_count || 0"
        icon="⏳"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="Resolved"
        :value="escalationsData.resolved_count || 0"
        icon="✅"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Resolution Rate"
        :value="`${formatNumber(escalationsData.resolution_rate || 0)}%`"
        icon="📊"
        bgColor="bg-purple-100"
      />
    </div>

    <!-- Escalations List -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Escalations</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="escalationsData?.escalations?.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticket ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Escalated By</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Escalated To</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Escalated At</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="escalation in escalationsData.escalations" :key="escalation.id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">#{{ escalation.ticket_id || 'N/A' }}</div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ escalation.escalation_reason || 'N/A' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ escalation.escalated_by_username || 'N/A' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ escalation.escalated_to_username || 'N/A' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span
                  :class="getStatusColor(escalation.status)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ escalation.status || 'N/A' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(escalation.escalated_at) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">
                <button
                  @click="viewTicket(escalation.ticket_id)"
                  class="text-primary-600 hover:text-primary-800 font-medium mr-2"
                >
                  View
                </button>
                <button
                  v-if="escalation.status === 'pending'"
                  @click="resolveEscalation(escalation.id)"
                  class="text-green-600 hover:text-green-800 font-medium"
                >
                  Resolve
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-2">📢</div>
        <p>No escalations found</p>
      </div>
    </div>

    <!-- Escalation Reasons Breakdown -->
    <div v-if="escalationsData?.reasons_breakdown?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Escalation Reasons Breakdown</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="reason in escalationsData.reasons_breakdown"
          :key="reason.escalation_reason"
          class="p-4 bg-gray-50 rounded-lg"
        >
          <div class="text-sm text-gray-600">{{ reason.escalation_reason || 'Unknown' }}</div>
          <div class="text-2xl font-bold text-gray-900">{{ reason.count }}</div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="card bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <span class="text-red-600 text-xl mr-2">⚠️</span>
        <p class="text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import supportDashboardAPI from '@/api/support-dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'

const loading = ref(false)
const error = ref(null)
const statusFilter = ref('')
const escalationsData = ref(null)

const fetchEscalations = async () => {
  loading.value = true
  error.value = null
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const response = await supportDashboardAPI.getDashboardEscalations(params)
    escalationsData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load escalations'
    console.error('Error fetching escalations:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toFixed(1)
}

const getStatusColor = (status) => {
  const colors = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'resolved': 'bg-green-100 text-green-800',
    'in_progress': 'bg-blue-100 text-blue-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const viewTicket = (ticketId) => {
  // Navigate to ticket detail page
  window.location.href = `/tickets/${ticketId}`
}

const resolveEscalation = async (escalationId) => {
  // TODO: Implement escalation resolution
  alert(`Resolve escalation ${escalationId}`)
}

onMounted(() => {
  fetchEscalations()
})
</script>

<style scoped>
.escalations {
  max-width: 1400px;
  margin: 0 auto;
}
</style>

