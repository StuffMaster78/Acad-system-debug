<template>
  <div class="space-y-6">
    <!-- Breadcrumbs -->
    <nav class="flex items-center gap-2 text-xs sm:text-sm overflow-x-auto whitespace-nowrap" aria-label="Breadcrumb">
      <router-link to="/dashboard" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Dashboard
      </router-link>
      <span class="text-gray-400 dark:text-gray-600">/</span>
      <router-link to="/client/special-orders" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Special Orders
      </router-link>
      <span class="text-gray-400 dark:text-gray-600">/</span>
      <span class="text-gray-900 dark:text-gray-100 font-medium truncate max-w-[60vw] sm:max-w-none">Order #{{ order?.id }}</span>
    </nav>

    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading order details...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <div v-else-if="order" class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Special Order #{{ order.id }}</h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ order.order_type === 'predefined' ? 'Predefined pricing structure' : 'Custom estimated pricing' }}
          </p>
        </div>
        <span
          class="px-3 py-1.5 text-xs font-semibold rounded-full"
          :class="getStatusClass(order.status)"
        >
          {{ getStatusLabel(order.status) }}
        </span>
      </div>

      <!-- Tabs -->
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
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Left Column -->
          <div class="space-y-6">
            <!-- Order Information -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Order Information</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Order ID:</span>
                  <span class="font-mono text-gray-900 dark:text-white">#{{ order.id }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Status:</span>
                  <span :class="getStatusClass(order.status)" class="px-2 py-1 text-xs rounded-full">
                    {{ getStatusLabel(order.status) }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Type:</span>
                  <span :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'" class="px-2 py-1 text-xs rounded-full">
                    {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Duration:</span>
                  <span class="text-gray-900 dark:text-white">{{ order.duration_days || 0 }} days</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Created:</span>
                  <span class="text-gray-900 dark:text-white">{{ formatDate(order.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Inquiry Details -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Inquiry Details</h3>
              <p v-if="order.inquiry_details" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {{ order.inquiry_details }}
              </p>
              <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No details provided</p>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-6">
            <!-- Financial Information -->
            <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Financial Information</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Total Cost:</span>
                  <span class="text-xl font-bold text-gray-900 dark:text-white">
                    <span v-if="order.total_cost">${{ formatCurrency(order.total_cost) }}</span>
                    <span v-else class="text-gray-400 italic">Not set yet</span>
                  </span>
                </div>
                <div v-if="order.budget" class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Your Budget:</span>
                  <span class="text-gray-900 dark:text-white font-semibold">${{ formatCurrency(order.budget) }}</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Deposit Required:</span>
                  <span class="text-gray-900 dark:text-white font-semibold">
                    <span v-if="order.deposit_required">${{ formatCurrency(order.deposit_required) }}</span>
                    <span v-else class="text-gray-400 italic">Not set yet</span>
                  </span>
                </div>
                <div v-if="order.is_approved" class="flex justify-between items-center">
                  <span class="font-medium text-gray-600 dark:text-gray-400">Approved:</span>
                  <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Yes</span>
                </div>
              </div>
            </div>

            <!-- Writer Information -->
            <div v-if="order.writer" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
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
      </div>

      <!-- Messages Tab -->
      <div v-if="activeTab === 'messages'" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 min-h-[500px]">
        <OrderMessagesTabbed :special-order-id="order.id" />
      </div>

      <!-- Files Tab -->
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

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  loadOrder()
})
</script>
