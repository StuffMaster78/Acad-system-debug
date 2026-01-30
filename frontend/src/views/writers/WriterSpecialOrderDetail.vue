<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Special Order #{{ order?.id }}</h1>
        <p class="text-sm text-gray-600 dark:text-gray-400">Manage your assigned special order</p>
      </div>
      <router-link to="/writer/special-orders" class="text-sm text-primary-600 hover:text-primary-700">
        Back to Special Orders
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading special order...</p>
    </div>

    <div v-else-if="error" class="text-center py-12 text-red-600">
      {{ error }}
    </div>

    <div v-else-if="order" class="space-y-6">
      <div class="flex flex-wrap items-center gap-3">
        <span class="px-3 py-1 text-xs font-semibold rounded-full" :class="getStatusClass(order.status)">
          {{ getStatusLabel(order.status) }}
        </span>
        <span
          class="px-2 py-1 text-xs rounded-full"
          :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'"
        >
          {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
        </span>
      </div>

      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div v-if="activeTab === 'overview'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-white">Order Details</h3>
            <div class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <div class="flex justify-between">
                <span class="font-medium text-gray-600 dark:text-gray-400">Duration:</span>
                <span>{{ order.duration_days || 0 }} days</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium text-gray-600 dark:text-gray-400">Total Cost:</span>
                <span>${{ formatCurrency(order.total_cost || 0) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium text-gray-600 dark:text-gray-400">Deposit Required:</span>
                <span>${{ formatCurrency(order.deposit_required || 0) }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-3 text-gray-900 dark:text-white">Inquiry Details</h3>
            <p v-if="order.inquiry_details" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {{ order.inquiry_details }}
            </p>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400">No inquiry details provided.</p>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Client Information</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Client:</span>
                <span class="text-gray-900 dark:text-white">{{ order.client_username || order.client?.username || 'Client' }}</span>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Assigned Writer</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between items-center">
                <span class="font-medium text-gray-600 dark:text-gray-400">Writer:</span>
                <span class="text-gray-900 dark:text-white">{{ order.writer_username || order.writer?.username || 'Assigned' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'messages'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[500px]">
        <OrderMessagesTabbed :special-order-id="order.id" />
      </div>

      <div v-if="activeTab === 'files'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <SpecialOrderFilesPanel :special-order-id="order.id" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import specialOrdersAPI from '@/api/special-orders'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'
import SpecialOrderFilesPanel from '@/components/special-orders/SpecialOrderFilesPanel.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const order = ref(null)
const activeTab = ref('overview')

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'messages', label: 'Messages' },
  { id: 'files', label: 'Files' }
]

const loadOrder = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await specialOrdersAPI.get(route.params.id)
    order.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load order details'
    console.error('Error loading order:', err)
  } finally {
    loading.value = false
  }
}


const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'awaiting_approval': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'inquiry': 'Inquiry',
    'awaiting_approval': 'Awaiting Approval',
    'in_progress': 'In Progress',
    'completed': 'Completed'
  }
  return labels[status] || status
}

const formatCurrency = (amount) => {
  return parseFloat(amount || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

onMounted(loadOrder)
</script>
