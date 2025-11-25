<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Tips</h1>
        <p class="mt-2 text-gray-600">View tips received from clients</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Total Tips</p>
        <p class="text-3xl font-bold text-green-900">${{ stats.total_tips || '0.00' }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Received</p>
        <p class="text-3xl font-bold text-blue-900">${{ stats.total_received || '0.00' }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Count</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_count || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">This Month</p>
        <p class="text-3xl font-bold text-yellow-900">${{ stats.this_month || '0.00' }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input v-model="filters.date_from" type="date" class="w-full border rounded px-3 py-2" @change="loadTips" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input v-model="filters.date_to" type="date" class="w-full border rounded px-3 py-2" @change="loadTips" />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Tips Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="tipsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="tips.length === 0" class="text-center py-12">
        <div class="text-4xl mb-4">🎁</div>
        <p class="text-gray-600 text-lg">No tips received yet</p>
        <p class="text-sm text-gray-400 mt-2">Tips from satisfied clients will appear here</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gradient-to-r from-gray-50 via-gray-50 to-gray-100">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Date
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Client
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Order
              </th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Tip Amount
              </th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Your Earning
              </th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Platform Share
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Reason
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(tip, index) in tips"
              :key="tip.id"
              :class="[
                'transition-all duration-150 hover:bg-green-50/50',
                index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'
              ]"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ formatDate(tip.sent_at) }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ formatTime(tip.sent_at) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-green-600 text-xs font-semibold">
                      {{ (tip.client_name || 'C')[0].toUpperCase() }}
                    </span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ tip.client_name || 'N/A' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">
                  <router-link
                    v-if="tip.order"
                    :to="`/orders/${tip.order}`"
                    class="text-primary-600 hover:text-primary-800 font-medium"
                  >
                    {{ tip.order_title || `Order #${tip.order}` }}
                  </router-link>
                  <span v-else>{{ tip.order_title || 'N/A' }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="text-sm font-bold text-green-600">${{ parseFloat(tip.tip_amount).toFixed(2) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="text-sm font-bold text-blue-600">${{ parseFloat(tip.writer_earning || 0).toFixed(2) }}</div>
                <div class="text-xs text-gray-500 mt-0.5">Your share</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="text-sm text-gray-500">${{ parseFloat(tip.platform_profit || 0).toFixed(2) }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-700 max-w-xs">
                  <p class="line-clamp-2">{{ tip.tip_reason || 'No reason provided' }}</p>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="viewTip(tip)"
                  class="text-primary-600 hover:text-primary-800 font-medium transition-colors"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tip Detail Modal -->
    <div v-if="selectedTip" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Tip Details</h2>
            <button @click="selectedTip = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Tip Amount</label>
              <p class="text-lg font-semibold text-green-600">${{ parseFloat(selectedTip.tip_amount).toFixed(2) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Your Earning</label>
              <p class="text-lg font-semibold text-blue-600">${{ parseFloat(selectedTip.writer_earning || 0).toFixed(2) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Platform Share</label>
              <p class="text-sm text-gray-900">${{ parseFloat(selectedTip.platform_profit || 0).toFixed(2) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date Received</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedTip.sent_at) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client</label>
              <p class="text-sm text-gray-900">{{ selectedTip.client_name || 'N/A' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order</label>
              <p class="text-sm text-gray-900">{{ selectedTip.order_title || `Order #${selectedTip.order}` }}</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Reason</label>
            <p class="text-sm text-gray-900 whitespace-pre-wrap">{{ selectedTip.tip_reason || 'No reason provided' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import writerTipsAPI from '@/api/writer-tips'

const tips = ref([])
const tipsLoading = ref(false)
const stats = ref({})
const filters = ref({
  date_from: '',
  date_to: '',
})
const selectedTip = ref(null)

const loadTips = async () => {
  tipsLoading.value = true
  try {
    const params = {}
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    
    const response = await writerTipsAPI.list(params)
    tips.value = response.data.results || response.data || []
    
    // Calculate stats
    const totalTips = tips.value.reduce((sum, tip) => sum + parseFloat(tip.tip_amount || 0), 0)
    const totalReceived = tips.value.reduce((sum, tip) => sum + parseFloat(tip.writer_earning || 0), 0)
    const now = new Date()
    const thisMonth = tips.value
      .filter(tip => {
        const tipDate = new Date(tip.sent_at)
        return tipDate.getMonth() === now.getMonth() && tipDate.getFullYear() === now.getFullYear()
      })
      .reduce((sum, tip) => sum + parseFloat(tip.tip_amount || 0), 0)
    
    stats.value = {
      total_tips: totalTips.toFixed(2),
      total_received: totalReceived.toFixed(2),
      total_count: tips.value.length,
      this_month: thisMonth.toFixed(2),
    }
  } catch (error) {
    console.error('Failed to load tips:', error)
  } finally {
    tipsLoading.value = false
  }
}

const viewTip = (tip) => {
  selectedTip.value = tip
}

const resetFilters = () => {
  filters.value = {
    date_from: '',
    date_to: '',
  }
  loadTips()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadTips()
})
</script>

