<template>
  <div class="space-y-6">
    <PageHeader
      title="Client Payments"
      subtitle="All payments and transactions made by clients"
      @refresh="loadPayments"
    />

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'daily'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'daily'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Daily (Today)
        </button>
        <button
          @click="activeTab = 'weekly'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'weekly'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          This Week
        </button>
        <button
          @click="activeTab = 'monthly'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'monthly'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          This Month
        </button>
        <button
          @click="activeTab = 'all'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'all'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          All Payments
        </button>
      </nav>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <div class="bg-linear-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div class="text-sm font-medium opacity-90">Total Payments</div>
        <div class="text-3xl font-bold mt-2">${{ formatCurrency(summary.totalAmount) }}</div>
        <div class="text-xs opacity-75 mt-1">{{ summary.totalTransactions }} transactions</div>
      </div>
      <div class="bg-linear-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
        <div class="text-sm font-medium opacity-90">Order Payments</div>
        <div class="text-3xl font-bold mt-2">${{ formatCurrency(summary.orderPayments) }}</div>
        <div class="text-xs opacity-75 mt-1">{{ summary.orderPaymentCount }} payments</div>
      </div>
      <div class="bg-linear-to-br from-indigo-500 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div class="text-sm font-medium opacity-90">Class Payments</div>
        <div class="text-3xl font-bold mt-2">${{ formatCurrency(summary.classPayments) }}</div>
        <div class="text-xs opacity-75 mt-1">{{ summary.classPaymentCount }} payments</div>
      </div>
      <div class="bg-linear-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
        <div class="text-sm font-medium opacity-90">Wallet Top-ups</div>
        <div class="text-3xl font-bold mt-2">${{ formatCurrency(summary.walletTopups) }}</div>
        <div class="text-xs opacity-75 mt-1">{{ summary.walletTopupCount }} top-ups</div>
      </div>
      <div class="bg-linear-to-br from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
        <div class="text-sm font-medium opacity-90">Tips Given</div>
        <div class="text-3xl font-bold mt-2">${{ formatCurrency(summary.tips) }}</div>
        <div class="text-xs opacity-75 mt-1">{{ summary.tipCount }} tips</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Client email, name, or reference..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
          <select
            v-model="filters.website_id"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @change="loadPayments"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Payment Type</label>
          <select
            v-model="filters.payment_type"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @change="loadPayments"
          >
            <option value="">All Types</option>
            <option value="standard">Standard Orders</option>
            <option value="predefined_special">Special Orders</option>
            <option value="estimated_special">Estimated Special Orders</option>
            <option value="class_payment">Class Payments (All)</option>
            <option value="wallet_loading">Wallet Top-ups</option>
            <option value="tip">Tips</option>
            <option value="wallet_transaction">Wallet Transactions</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @change="loadPayments"
          >
            <option value="">All Statuses</option>
            <option value="succeeded">Succeeded</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @change="loadPayments"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            @change="loadPayments"
          />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button
          @click="clearFilters"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Clear Filters
        </button>
        <button
          @click="exportToCSV"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
        >
          📥 Export CSV
        </button>
      </div>
    </div>

    <!-- Payments Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="payments.length === 0" class="text-center py-12 text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No client payments found</p>
        <p v-if="error" class="mt-1 text-xs text-red-500">Error: {{ error }}</p>
        <p v-else class="mt-1 text-xs text-gray-400">Try adjusting your filters or check back later</p>
      </div>
      
      <div v-else class="overflow-x-auto shadow-sm rounded-lg border border-gray-200">
        <table class="min-w-full divide-y divide-gray-200" style="min-width: 1200px;">
          <thead class="bg-linear-to-r from-blue-50 to-indigo-50 border-b-2 border-blue-200">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Date
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Client
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  Payment Type
                </div>
              </th>
              <th class="px-6 py-4 text-right text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center justify-end gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Amount
                </div>
              </th>
              <th class="px-6 py-4 text-center text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center justify-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Status
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  Payment Method
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
                  </svg>
                  Reference ID
                </div>
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  Related Item
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="payment in payments" :key="payment.id" class="hover:bg-blue-50/50 transition-all duration-150 border-b border-gray-100">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ formatDate(payment.created_at) }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ formatTime(payment.created_at) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-linear-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-xs font-bold">
                    {{ (payment.client?.username || 'N/A').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-gray-900">{{ payment.client?.username || 'N/A' }}</div>
                    <div class="text-xs text-gray-500 truncate max-w-[200px]" :title="payment.client?.email || ''">
                      {{ payment.client?.email || '' }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm"
                      :class="getTypeClass(payment.payment_type)">
                  {{ payment.payment_type_label || payment.payment_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <div class="text-base font-bold text-gray-900">
                  ${{ formatCurrency(payment.amount) }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold shadow-sm"
                      :class="getStatusClass(payment.status)">
                  <span class="w-2 h-2 rounded-full mr-2" :class="getStatusDotClass(payment.status)"></span>
                  {{ payment.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-700">{{ payment.payment_method || 'N/A' }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="font-mono text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded border border-gray-200 inline-block">
                  {{ payment.reference_id || payment.transaction_id || '—' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="payment.order_id" class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Order
                  </span>
                  <router-link :to="`/orders/${payment.order_id}`" class="text-blue-600 hover:text-blue-800 font-semibold text-sm hover:underline">
                    #{{ payment.order_id }}
                  </router-link>
                </div>
                <div v-else-if="payment.special_order_id" class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800 border border-purple-200">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    Special
                  </span>
                  <span class="text-purple-600 font-semibold text-sm">#{{ payment.special_order_id }}</span>
                </div>
                <div v-else-if="payment.class_purchase_id" class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    Class
                  </span>
                  <span class="text-green-600 font-semibold text-sm">#{{ payment.class_purchase_id }}</span>
                </div>
                <div v-else-if="payment.writer" class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-orange-100 text-orange-800 border border-orange-200">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Writer
                  </span>
                  <span class="text-orange-600 font-semibold text-sm">{{ payment.writer.username }}</span>
                </div>
                <span v-else class="text-gray-400 text-sm">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="!loading && payments.length > 0" class="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-700">
          Showing {{ ((pagination.page - 1) * pagination.page_size) + 1 }} to 
          {{ Math.min(pagination.page * pagination.page_size, pagination.count) }} of 
          {{ pagination.count }} payments
        </div>
        <div class="flex gap-2">
          <button
            @click="previousPage"
            :disabled="!pagination.previous"
            class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="!pagination.next"
            class="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { debounce } from '@/utils/debounce'
import PageHeader from '@/components/common/PageHeader.vue'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'

const loading = ref(false)
const payments = ref([])
const allPayments = ref([]) // Store all payments for filtering
const websites = ref([])
const activeTab = ref('all') // Start with 'all' to show all payments initially
const error = ref(null)
const filters = ref({
  search: '',
  website_id: '',
  payment_type: '',
  status: '',
  date_from: '',
  date_to: '',
})
const pagination = ref({
  page: 1,
  page_size: 50,
  count: 0,
  next: null,
  previous: null,
})

// Calculate date ranges
const getDateRange = (tab) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  switch (tab) {
    case 'daily':
      const todayStr = today.toISOString().split('T')[0]
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      const tomorrowStr = tomorrow.toISOString().split('T')[0]
      return {
        date_from: todayStr,
        date_to: tomorrowStr,
      }
    case 'weekly':
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - today.getDay()) // Start of week (Sunday)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6) // End of week (Saturday)
      return {
        date_from: weekStart.toISOString().split('T')[0],
        date_to: weekEnd.toISOString().split('T')[0],
      }
    case 'monthly':
      const monthStart = new Date(today.getFullYear(), today.getMonth(), 1)
      const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      return {
        date_from: monthStart.toISOString().split('T')[0],
        date_to: monthEnd.toISOString().split('T')[0],
      }
    default:
      return { date_from: '', date_to: '' }
  }
}

const filteredPayments = computed(() => {
  let filtered = [...allPayments.value]
  
  // Apply date range based on active tab
  if (activeTab.value !== 'all') {
    const dateRange = getDateRange(activeTab.value)
    filtered = filtered.filter(p => {
      const paymentDate = new Date(p.created_at).toISOString().split('T')[0]
      return (!dateRange.date_from || paymentDate >= dateRange.date_from) &&
             (!dateRange.date_to || paymentDate <= dateRange.date_to)
    })
  }
  
  return filtered
})

const summary = computed(() => {
  const filtered = filteredPayments.value
  const totalAmount = filtered.reduce((sum, p) => sum + (p.amount || 0), 0)
  const orderPayments = filtered
    .filter(p => p.type === 'order_payment' && p.payment_type === 'standard')
    .reduce((sum, p) => sum + (p.amount || 0), 0)
  const orderPaymentCount = filtered.filter(p => p.type === 'order_payment' && p.payment_type === 'standard').length
  const classPayments = filtered
    .filter(p => p.type === 'order_payment' && p.payment_type === 'class_payment')
    .reduce((sum, p) => sum + (p.amount || 0), 0)
  const classPaymentCount = filtered.filter(p => p.type === 'order_payment' && p.payment_type === 'class_payment').length
  const walletTopups = filtered
    .filter(p => p.payment_type === 'wallet_loading' || (p.type === 'client_wallet' && p.payment_type_label?.includes('Top')))
    .reduce((sum, p) => sum + (p.amount || 0), 0)
  const walletTopupCount = filtered.filter(p => p.payment_type === 'wallet_loading' || (p.type === 'client_wallet' && p.payment_type_label?.includes('Top'))).length
  const tips = filtered
    .filter(p => p.type === 'tip')
    .reduce((sum, p) => sum + (p.amount || 0), 0)
  const tipCount = filtered.filter(p => p.type === 'tip').length
  
  return {
    totalAmount,
    totalTransactions: filtered.length,
    orderPayments,
    orderPaymentCount,
    classPayments,
    classPaymentCount,
    walletTopups,
    walletTopupCount,
    tips,
    tipCount,
  }
})

const loadPayments = async (loadAll = false) => {
  loading.value = true
  try {
    const params = {}
    
    // For daily/weekly/monthly, load all data for calculations
    if (loadAll || activeTab.value !== 'all') {
      params.page_size = 1000
    } else {
      params.page = pagination.value.page
      params.page_size = pagination.value.page_size
    }
    
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website_id) params.website_id = filters.value.website_id
    if (filters.value.payment_type) params.payment_type = filters.value.payment_type
    if (filters.value.status) params.status = filters.value.status
    
    // Only apply date filters if not using tabs
    if (activeTab.value === 'all') {
      if (filters.value.date_from) params.date_from = filters.value.date_from
      if (filters.value.date_to) params.date_to = filters.value.date_to
    }

    let response
    try {
      response = await paymentsAPI.getClientPayments(params)
      console.log('Client payments response:', response.data)
      allPayments.value = response.data.results || []
      console.log('Loaded payments:', allPayments.value.length)
    } catch (err) {
      console.error('Client payments endpoint failed, trying all-transactions fallback:', err)
      error.value = err.message
      // Fallback to all-transactions and filter client-side
      try {
        const fallbackResponse = await paymentsAPI.getAllTransactions({ page_size: 1000, ...params })
        console.log('Fallback response:', fallbackResponse.data)
        // Filter to only client-related transactions (exclude writer transactions)
        const clientOnly = (fallbackResponse.data.results || []).filter(t => 
          (t.type === 'order_payment' && t.client && !t.writer) || 
          (t.type === 'client_wallet') || 
          (t.type === 'tip' && t.client && !t.writer)
        )
        console.log('Filtered client payments:', clientOnly.length)
        allPayments.value = clientOnly
        response = { data: { results: clientOnly, count: clientOnly.length, next: null, previous: null } }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
        error.value = fallbackError.message
        allPayments.value = []
        response = { data: { results: [], count: 0, next: null, previous: null } }
      }
    }
    
    // Apply client-side filtering for tabs
    let filtered = [...allPayments.value]
    console.log('All payments before filtering:', allPayments.value.length)
    
    if (activeTab.value !== 'all') {
      const dateRange = getDateRange(activeTab.value)
      console.log('Date range for tab:', activeTab.value, dateRange)
      filtered = filtered.filter(p => {
        if (!p.created_at) return false
        const paymentDate = new Date(p.created_at).toISOString().split('T')[0]
        return (!dateRange.date_from || paymentDate >= dateRange.date_from) &&
               (!dateRange.date_to || paymentDate <= dateRange.date_to)
      })
      console.log('Filtered payments after date filter:', filtered.length)
    }
    
    // Apply pagination for display
    if (activeTab.value === 'all' && !loadAll) {
      const start = (pagination.value.page - 1) * pagination.value.page_size
      const end = start + pagination.value.page_size
      payments.value = filtered.slice(start, end)
      console.log('Pagination applied. Showing:', payments.value.length, 'of', filtered.length)
      
      pagination.value = {
        page: pagination.value.page,
        page_size: pagination.value.page_size,
        count: response?.data?.count || filtered.length,
        next: response?.data?.next || null,
        previous: response?.data?.previous || null,
      }
    } else {
      // For tabs, show all filtered results
      payments.value = filtered
      console.log('Tab view. Showing all filtered:', payments.value.length)
      pagination.value = {
        page: 1,
        page_size: filtered.length,
        count: filtered.length,
        next: null,
        previous: null,
      }
    }
  } catch (error) {
    console.error('Failed to load client payments:', error)
    // Ensure we have empty arrays if everything fails
    if (!allPayments.value || allPayments.value.length === 0) {
      allPayments.value = []
      payments.value = []
    }
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const response = await apiClient.get('/websites/websites/')
    websites.value = response.data.results || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const clearFilters = () => {
  filters.value = {
    search: '',
    website_id: '',
    payment_type: '',
    status: '',
    date_from: '',
    date_to: '',
  }
  pagination.value.page = 1
  loadPayments()
}

const debouncedSearch = debounce(() => {
  pagination.value.page = 1
  loadPayments()
}, 500)

const nextPage = () => {
  if (pagination.value.next) {
    pagination.value.page += 1
    loadPayments()
  }
}

const previousPage = () => {
  if (pagination.value.previous) {
    pagination.value.page -= 1
    loadPayments()
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
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

const getStatusClass = (status) => {
  const classes = {
    'succeeded': 'bg-green-100 text-green-800',
    'completed': 'bg-blue-100 text-blue-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'failed': 'bg-red-100 text-red-800',
  }
  return classes[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const getStatusDotClass = (status) => {
  const classes = {
    'succeeded': 'bg-green-500',
    'completed': 'bg-blue-500',
    'pending': 'bg-yellow-500',
    'failed': 'bg-red-500',
  }
  return classes[status?.toLowerCase()] || 'bg-gray-500'
}

const getTypeClass = (type) => {
  const classes = {
    'standard': 'bg-blue-100 text-blue-800',
    'predefined_special': 'bg-purple-100 text-purple-800',
    'estimated_special': 'bg-purple-100 text-purple-800',
    'class_payment': 'bg-indigo-100 text-indigo-800',
    'wallet_loading': 'bg-orange-100 text-orange-800',
    'tip': 'bg-pink-100 text-pink-800',
    'wallet_transaction': 'bg-gray-100 text-gray-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const exportToCSV = () => {
  const headers = ['Date', 'Client', 'Email', 'Type', 'Amount', 'Status', 'Payment Method', 'Reference', 'Related']
  const rows = payments.value.map(p => [
    formatDate(p.created_at),
    p.client?.username || '',
    p.client?.email || '',
    p.payment_type_label || p.payment_type,
    `$${formatCurrency(p.amount)}`,
    p.status,
    p.payment_method,
    p.reference_id || p.transaction_id,
    p.order_id ? `Order #${p.order_id}` : p.special_order_id ? `Special #${p.special_order_id}` : p.class_purchase_id ? `Class #${p.class_purchase_id}` : p.writer ? `Writer: ${p.writer.username}` : '—'
  ])
  
  const csv = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `client-payments-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

// Watch for tab changes
watch(activeTab, () => {
  pagination.value.page = 1
  loadPayments(true)
})

onMounted(async () => {
  try {
    console.log('Client Payments page mounted. Loading data...')
    await Promise.all([loadPayments(true), loadWebsites()])
    console.log('Initial load complete. Payments:', payments.value.length, 'All payments:', allPayments.value.length)
  } catch (error) {
    console.error('Error loading initial data:', error)
    error.value = error.message || 'Failed to load payments'
  }
})
</script>

<style scoped>
@reference "tailwindcss";
</style>

