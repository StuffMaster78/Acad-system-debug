<template>
  <div class="order-status-metrics space-y-6 p-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Order Status Metrics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track order status distribution and workflow metrics</p>
      </div>
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Date Range Selector -->
        <select
          v-model="selectedDays"
          @change="fetchSummary"
          class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          :disabled="loading"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="180">Last 180 days</option>
          <option :value="365">Last year</option>
          <option :value="0">All time</option>
        </select>
        <button
          @click="exportData"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
          :disabled="loading || !summaryData"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </button>
      <button
        @click="refreshMetrics"
        :disabled="loading"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !summaryData" class="flex items-center justify-center py-20">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading metrics...</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="summaryData" class="space-y-6">
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Orders</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ totalOrders.toLocaleString() }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">📦</span>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
              <p class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{{ completedCount.toLocaleString() }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">✅</span>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">In Progress</p>
              <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{{ inProgressCount.toLocaleString() }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">🔄</span>
            </div>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Completion Rate</p>
              <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ completionRate }}%</p>
            </div>
            <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">📊</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Status Breakdown Cards -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <div
        v-for="status in orderStatusBreakdown"
        :key="status.name"
          class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4 border-l-4 hover:shadow-md transition-all cursor-pointer transform hover:scale-105"
        :class="status.borderColor"
        @click="viewOrdersByStatus(status.status)"
      >
          <div class="flex items-center justify-between mb-2">
            <p class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ status.name }}</p>
            <span class="text-lg">{{ status.icon }}</span>
          </div>
          <p class="text-2xl font-bold" :class="status.textColor">{{ status.value }}</p>
          <p v-if="status.percentage" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ status.percentage }}%</p>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Status Distribution Pie Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Status Distribution</h2>
            <button
              @click="chartType = chartType === 'pie' ? 'donut' : 'pie'"
              class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
            >
              Switch to {{ chartType === 'pie' ? 'Donut' : 'Pie' }}
            </button>
          </div>
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <apexchart
            v-else
            :type="chartType"
            height="350"
            :options="pieChartOptions"
            :series="pieChartSeries"
          ></apexchart>
    </div>

        <!-- Status Distribution Bar Chart -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Status Breakdown</h2>
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <apexchart
            v-else
            type="bar"
            height="350"
            :options="barChartOptions"
            :series="barChartSeries"
          ></apexchart>
        </div>
      </div>

      <!-- Detailed Status Distribution -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Detailed Status Distribution</h2>
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="status in orderStatusBreakdown"
          :key="status.name"
            class="flex items-center gap-4"
        >
            <div class="flex items-center gap-3 min-w-[120px]">
              <span class="text-xl">{{ status.icon }}</span>
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ status.name }}</span>
            </div>
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ status.value }} orders</span>
                <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ status.percentage }}%</span>
            </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                  class="h-3 rounded-full transition-all duration-500"
                :class="status.bgColor"
                :style="{ width: `${status.percentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

      <!-- Quick Actions & Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <router-link
            to="/admin/orders"
              class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
          >
              <div class="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400">View All Orders</div>
              <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Manage and filter all orders</div>
          </router-link>
          <router-link
            to="/admin/orders?status=pending"
              class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
          >
              <div class="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400">Pending Orders</div>
              <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Review and assign pending orders</div>
          </router-link>
          <router-link
            to="/admin/orders?status=in_progress"
              class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
            >
              <div class="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400">Orders in Progress</div>
              <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Monitor active work</div>
            </router-link>
            <router-link
              to="/admin/orders?status=on_revision"
              class="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
            >
              <div class="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400">Revision Requests</div>
              <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Handle revision requests</div>
          </router-link>
        </div>
      </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Status Summary</h2>
        <div class="space-y-4">
            <div class="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Total Orders</span>
              <span class="text-lg font-bold text-blue-700 dark:text-blue-400">{{ totalOrders.toLocaleString() }}</span>
            </div>
            <div class="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Completed</span>
              <span class="text-lg font-bold text-green-700 dark:text-green-400">{{ completedCount.toLocaleString() }}</span>
            </div>
            <div class="flex items-center justify-between p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">In Progress</span>
              <span class="text-lg font-bold text-yellow-700 dark:text-yellow-400">{{ inProgressCount.toLocaleString() }}</span>
            </div>
            <div class="flex items-center justify-between p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">On Revision</span>
              <span class="text-lg font-bold text-orange-700 dark:text-orange-400">{{ revisionCount.toLocaleString() }}</span>
          </div>
            <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Disputed</span>
              <span class="text-lg font-bold text-red-700 dark:text-red-400">{{ disputedCount.toLocaleString() }}</span>
          </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex items-center justify-center py-20">
      <div class="text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">No data available</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Try refreshing or adjusting the date range.</p>
        <div class="mt-6">
          <button
            @click="fetchSummary"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dashboardAPI from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const summaryData = ref(null)
const selectedDays = ref(30)
const chartType = ref('pie')

const orderStatusBreakdown = computed(() => {
  if (!summaryData.value || !summaryData.value.orders_by_status) {
    return []
  }
  
  const statusMap = {
    // Initial states
    'draft': { 
      name: 'Draft', 
      icon: '📄', 
      borderColor: 'border-gray-300', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-400'
    },
    'created': { 
      name: 'Created', 
      icon: '🆕', 
      borderColor: 'border-blue-300', 
      textColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-400'
    },
    'pending': { 
      name: 'Pending', 
      icon: '⏳', 
      borderColor: 'border-yellow-400', 
      textColor: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-500'
    },
    'unpaid': { 
      name: 'Unpaid', 
      icon: '💳', 
      borderColor: 'border-orange-300', 
      textColor: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-400'
    },
    // Assignment states
    'available': { 
      name: 'Available', 
      icon: '📋', 
      borderColor: 'border-cyan-400', 
      textColor: 'text-cyan-600 dark:text-cyan-400',
      bgColor: 'bg-cyan-500'
    },
    'pending_writer_assignment': { 
      name: 'Pending Assignment', 
      icon: '👤', 
      borderColor: 'border-indigo-400', 
      textColor: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-500'
    },
    'pending_preferred': { 
      name: 'Pending Preferred', 
      icon: '⭐', 
      borderColor: 'border-amber-400', 
      textColor: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-500'
    },
    'assigned': { 
      name: 'Assigned', 
      icon: '✅', 
      borderColor: 'border-green-300', 
      textColor: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-400'
    },
    // Active work states
    'in_progress': { 
      name: 'In Progress', 
      icon: '🔄', 
      borderColor: 'border-blue-400', 
      textColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-500'
    },
    'under_editing': { 
      name: 'Under Editing', 
      icon: '✏️', 
      borderColor: 'border-purple-400', 
      textColor: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-500'
    },
    'submitted': { 
      name: 'Submitted', 
      icon: '📤', 
      borderColor: 'border-teal-400', 
      textColor: 'text-teal-600 dark:text-teal-400',
      bgColor: 'bg-teal-500'
    },
    'in_review': { 
      name: 'In Review', 
      icon: '🔍', 
      borderColor: 'border-indigo-400', 
      textColor: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-500'
    },
    'under_review': { 
      name: 'Under Review', 
      icon: '🔍', 
      borderColor: 'border-indigo-400', 
      textColor: 'text-indigo-600 dark:text-indigo-400',
      bgColor: 'bg-indigo-500'
    },
    'approved': { 
      name: 'Approved', 
      icon: '✓', 
      borderColor: 'border-green-400', 
      textColor: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-500'
    },
    'rejected': { 
      name: 'Rejected', 
      icon: '✗', 
      borderColor: 'border-red-400', 
      textColor: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-500'
    },
    // Revision states
    'revision_requested': { 
      name: 'Revision Requested', 
      icon: '📝', 
      borderColor: 'border-orange-400', 
      textColor: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-500'
    },
    'on_revision': { 
      name: 'On Revision', 
      icon: '📝', 
      borderColor: 'border-orange-400', 
      textColor: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-500'
    },
    'revised': { 
      name: 'Revised', 
      icon: '📄', 
      borderColor: 'border-amber-400', 
      textColor: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-500'
    },
    // Completion states
    'completed': { 
      name: 'Completed', 
      icon: '✅', 
      borderColor: 'border-green-400', 
      textColor: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-500'
    },
    'rated': { 
      name: 'Rated', 
      icon: '⭐', 
      borderColor: 'border-yellow-400', 
      textColor: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-500'
    },
    'reviewed': { 
      name: 'Reviewed', 
      icon: '📖', 
      borderColor: 'border-green-500', 
      textColor: 'text-green-700 dark:text-green-300',
      bgColor: 'bg-green-600'
    },
    'closed': { 
      name: 'Closed', 
      icon: '🔒', 
      borderColor: 'border-gray-500', 
      textColor: 'text-gray-700 dark:text-gray-300',
      bgColor: 'bg-gray-600'
    },
    // Problem states
    'disputed': { 
      name: 'Disputed', 
      icon: '⚠️', 
      borderColor: 'border-red-400', 
      textColor: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-500'
    },
    'cancelled': { 
      name: 'Cancelled', 
      icon: '❌', 
      borderColor: 'border-gray-400', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-500'
    },
    'canceled': { 
      name: 'Canceled', 
      icon: '❌', 
      borderColor: 'border-gray-400', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-500'
    },
    'refunded': { 
      name: 'Refunded', 
      icon: '💰', 
      borderColor: 'border-gray-400', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-500'
    },
    // System states
    'on_hold': { 
      name: 'On Hold', 
      icon: '⏸️', 
      borderColor: 'border-yellow-300', 
      textColor: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-400'
    },
    'reassigned': { 
      name: 'Reassigned', 
      icon: '🔄', 
      borderColor: 'border-blue-300', 
      textColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-400'
    },
    'critical': { 
      name: 'Critical', 
      icon: '🚨', 
      borderColor: 'border-red-500', 
      textColor: 'text-red-700 dark:text-red-300',
      bgColor: 'bg-red-600'
    },
    'late': { 
      name: 'Late', 
      icon: '⏰', 
      borderColor: 'border-red-400', 
      textColor: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-500'
    },
    'archived': { 
      name: 'Archived', 
      icon: '📦', 
      borderColor: 'border-gray-500', 
      textColor: 'text-gray-700 dark:text-gray-300',
      bgColor: 'bg-gray-600'
    },
    'expired': { 
      name: 'Expired', 
      icon: '⏱️', 
      borderColor: 'border-gray-400', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-500'
    },
    're_opened': { 
      name: 'Reopened', 
      icon: '🔓', 
      borderColor: 'border-blue-400', 
      textColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-500'
    },
  }
  
  const ordersByStatus = summaryData.value.orders_by_status || {}
  const totalOrders = summaryData.value.total_orders || 0
  
  return Object.entries(ordersByStatus).map(([status, count]) => {
    const statusInfo = statusMap[status] || { 
      name: status, 
      icon: '📋', 
      borderColor: 'border-gray-300', 
      textColor: 'text-gray-600 dark:text-gray-400',
      bgColor: 'bg-gray-400'
    }
    return {
      status,
      name: statusInfo.name,
      value: count,
      valueFormatted: count.toLocaleString(),
      icon: statusInfo.icon,
      borderColor: statusInfo.borderColor,
      textColor: statusInfo.textColor,
      bgColor: statusInfo.bgColor,
      percentage: totalOrders > 0 ? parseFloat(((count / totalOrders) * 100).toFixed(1)) : 0,
    }
  }).sort((a, b) => b.value - a.value)
})

const totalOrders = computed(() => {
  return summaryData.value?.total_orders || 0
})

const completedCount = computed(() => {
  const completed = orderStatusBreakdown.value.find(s => s.status === 'completed')?.value || 0
  const reviewed = orderStatusBreakdown.value.find(s => s.status === 'reviewed')?.value || 0
  const rated = orderStatusBreakdown.value.find(s => s.status === 'rated')?.value || 0
  const closed = orderStatusBreakdown.value.find(s => s.status === 'closed')?.value || 0
  return completed + reviewed + rated + closed
})

const inProgressCount = computed(() => {
  const inProgress = orderStatusBreakdown.value.find(s => s.status === 'in_progress')?.value || 0
  const underEditing = orderStatusBreakdown.value.find(s => s.status === 'under_editing')?.value || 0
  const assigned = orderStatusBreakdown.value.find(s => s.status === 'assigned')?.value || 0
  const submitted = orderStatusBreakdown.value.find(s => s.status === 'submitted')?.value || 0
  const inReview = orderStatusBreakdown.value.find(s => s.status === 'in_review' || s.status === 'under_review')?.value || 0
  return inProgress + underEditing + assigned + submitted + inReview
})

const revisionCount = computed(() => {
  const onRevision = orderStatusBreakdown.value.find(s => s.status === 'on_revision')?.value || 0
  const revisionRequested = orderStatusBreakdown.value.find(s => s.status === 'revision_requested')?.value || 0
  const revised = orderStatusBreakdown.value.find(s => s.status === 'revised')?.value || 0
  return onRevision + revisionRequested + revised
})

const disputedCount = computed(() => {
  const disputed = orderStatusBreakdown.value.find(s => s.status === 'disputed')
  return disputed ? disputed.value : 0
})

const completionRate = computed(() => {
  if (totalOrders.value === 0) return 0
  return ((completedCount.value / totalOrders.value) * 100).toFixed(1)
})

// Chart Series
const pieChartSeries = computed(() => {
  return orderStatusBreakdown.value.map(s => s.value)
})

const barChartSeries = computed(() => {
  return [{
    name: 'Orders',
    data: orderStatusBreakdown.value.map(s => s.value)
  }]
})

// Chart Options
const pieChartOptions = computed(() => {
  const isDark = document.documentElement.classList.contains('dark')
  const colors = orderStatusBreakdown.value.map(s => {
    const colorMap = {
      'bg-yellow-500': '#eab308',
      'bg-yellow-400': '#facc15',
      'bg-yellow-300': '#fde047',
      'bg-blue-500': '#3b82f6',
      'bg-blue-400': '#60a5fa',
      'bg-blue-300': '#93c5fd',
      'bg-purple-500': '#a855f7',
      'bg-purple-400': '#c084fc',
      'bg-green-500': '#10b981',
      'bg-green-400': '#34d399',
      'bg-green-300': '#6ee7b7',
      'bg-green-600': '#059669',
      'bg-orange-500': '#f97316',
      'bg-orange-400': '#fb923c',
      'bg-orange-300': '#fdba74',
      'bg-red-500': '#ef4444',
      'bg-red-400': '#f87171',
      'bg-red-600': '#dc2626',
      'bg-gray-500': '#6b7280',
      'bg-gray-400': '#9ca3af',
      'bg-gray-300': '#d1d5db',
      'bg-gray-600': '#4b5563',
      'bg-cyan-500': '#06b6d4',
      'bg-cyan-400': '#22d3ee',
      'bg-indigo-500': '#6366f1',
      'bg-indigo-400': '#818cf8',
      'bg-amber-500': '#f59e0b',
      'bg-amber-400': '#fbbf24',
      'bg-teal-500': '#14b8a6',
      'bg-teal-400': '#2dd4bf',
    }
    return colorMap[s.bgColor] || '#6b7280'
  })

  return {
    chart: {
      type: chartType.value,
      toolbar: { show: true },
      fontFamily: 'Inter, sans-serif',
    },
    labels: orderStatusBreakdown.value.map(s => s.name),
    colors: colors,
    legend: {
      position: 'bottom',
      labels: {
        colors: isDark ? '#e5e7eb' : '#374151',
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val) => `${val.toFixed(1)}%`,
      style: {
        colors: isDark ? ['#ffffff'] : ['#000000'],
      },
    },
    tooltip: {
      y: {
        formatter: (val) => `${val.toLocaleString()} orders`,
      },
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: true,
            total: {
              show: true,
              label: 'Total Orders',
              formatter: () => totalOrders.value.toLocaleString(),
              color: isDark ? '#e5e7eb' : '#374151',
            },
          },
        },
      },
    },
  }
})

const barChartOptions = computed(() => {
  const isDark = document.documentElement.classList.contains('dark')
  const colors = orderStatusBreakdown.value.map(s => {
    const colorMap = {
      'bg-yellow-500': '#eab308',
      'bg-yellow-400': '#facc15',
      'bg-yellow-300': '#fde047',
      'bg-blue-500': '#3b82f6',
      'bg-blue-400': '#60a5fa',
      'bg-blue-300': '#93c5fd',
      'bg-purple-500': '#a855f7',
      'bg-purple-400': '#c084fc',
      'bg-green-500': '#10b981',
      'bg-green-400': '#34d399',
      'bg-green-300': '#6ee7b7',
      'bg-green-600': '#059669',
      'bg-orange-500': '#f97316',
      'bg-orange-400': '#fb923c',
      'bg-orange-300': '#fdba74',
      'bg-red-500': '#ef4444',
      'bg-red-400': '#f87171',
      'bg-red-600': '#dc2626',
      'bg-gray-500': '#6b7280',
      'bg-gray-400': '#9ca3af',
      'bg-gray-300': '#d1d5db',
      'bg-gray-600': '#4b5563',
      'bg-cyan-500': '#06b6d4',
      'bg-cyan-400': '#22d3ee',
      'bg-indigo-500': '#6366f1',
      'bg-indigo-400': '#818cf8',
      'bg-amber-500': '#f59e0b',
      'bg-amber-400': '#fbbf24',
      'bg-teal-500': '#14b8a6',
      'bg-teal-400': '#2dd4bf',
    }
    return colorMap[s.bgColor] || '#6b7280'
  })

  return {
    chart: {
      type: 'bar',
      toolbar: { show: true },
      fontFamily: 'Inter, sans-serif',
    },
    xaxis: {
      categories: orderStatusBreakdown.value.map(s => s.name),
      labels: {
        style: {
          colors: isDark ? '#9ca3af' : '#6b7280',
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: isDark ? '#9ca3af' : '#6b7280',
        },
        formatter: (val) => val.toLocaleString(),
      },
    },
    colors: colors,
    dataLabels: {
      enabled: true,
      formatter: (val) => val.toLocaleString(),
      style: {
        colors: isDark ? ['#ffffff'] : ['#000000'],
      },
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        columnWidth: '60%',
        distributed: true,
      },
    },
    tooltip: {
      y: {
        formatter: (val) => `${val.toLocaleString()} orders`,
      },
    },
    grid: {
      borderColor: isDark ? '#374151' : '#e5e7eb',
    },
  }
})

const fetchSummary = async () => {
  loading.value = true
  try {
    const params = selectedDays.value > 0 ? { days: selectedDays.value } : {}
    const response = await dashboardAPI.getDashboard(params)
    // Extract order status data from dashboard response
    summaryData.value = {
      total_orders: response.data?.total_orders || 0,
      orders_by_status: response.data?.orders_by_status || {}
    }
  } catch (error) {
    console.error('Failed to fetch order status metrics:', error)
    // Show error notification if you have a notification system
  } finally {
    loading.value = false
  }
}

const refreshMetrics = () => {
  fetchSummary()
}

const viewOrdersByStatus = (status) => {
  router.push(`/admin/orders?status=${status}`)
}

const exportData = () => {
  if (!summaryData.value) return
  
  const data = {
    period: selectedDays.value === 0 ? 'All time' : `Last ${selectedDays.value} days`,
    total_orders: totalOrders.value,
    completion_rate: `${completionRate.value}%`,
    breakdown: orderStatusBreakdown.value.map(s => ({
      status: s.name,
      count: s.value,
      percentage: `${s.percentage}%`
    }))
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `order-status-metrics-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.order-status-metrics {
  min-height: calc(100vh - 4rem);
}
</style>
