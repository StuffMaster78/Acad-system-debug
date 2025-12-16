<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white">
          Geographic & Subject Analytics
        </h1>
        <p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
          View largest spend and number of orders by country, state, and subject
        </p>
      </div>
      <div class="flex gap-3">
        <button
          @click="refreshData"
          :disabled="loading"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        <button
          @click="exportData"
          class="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Filters</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Time Range (Days)
          </label>
          <input
            v-model.number="filters.days"
            type="number"
            min="0"
            placeholder="0 = All time"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
            @change="loadData"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Leave 0 or empty for all time
          </p>
        </div>
        <div class="flex items-end">
          <button
            @click="loadData"
            :disabled="loading"
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            Apply Filters
          </button>
        </div>
        <div class="flex items-end">
          <button
            @click="resetFilters"
            class="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="summary" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">Countries</h3>
          <svg class="w-8 h-8 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-3xl font-bold">{{ summary.total_countries }}</p>
        <p class="text-sm opacity-90 mt-1">Unique countries</p>
      </div>

      <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">States/Provinces</h3>
          <svg class="w-8 h-8 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <p class="text-3xl font-bold">{{ summary.total_states }}</p>
        <p class="text-sm opacity-90 mt-1">Unique states/provinces</p>
      </div>

      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">Subjects</h3>
          <svg class="w-8 h-8 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <p class="text-3xl font-bold">{{ summary.total_subjects }}</p>
        <p class="text-sm opacity-90 mt-1">Unique subjects</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Data Tables -->
    <div v-else class="space-y-6">
      <!-- By Country -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Spending & Orders by Country
          </h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Rank</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Country</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total Spend</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Order Count</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Avg. Order Value</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(item, index) in byCountry" :key="item.country" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  #{{ index + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-semibold">
                  {{ item.country || 'Unknown' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right font-semibold">
                  ${{ formatCurrency(item.total_spend) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  {{ item.order_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  ${{ formatCurrency(item.total_spend / item.order_count) }}
                </td>
              </tr>
              <tr v-if="byCountry.length === 0">
                <td colspan="5" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  No data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- By State -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Spending & Orders by State/Province
          </h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Rank</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">State/Province</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total Spend</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Order Count</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Avg. Order Value</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(item, index) in byState" :key="item.state" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  #{{ index + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-semibold">
                  {{ item.state || 'Unknown' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right font-semibold">
                  ${{ formatCurrency(item.total_spend) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  {{ item.order_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  ${{ formatCurrency(item.total_spend / item.order_count) }}
                </td>
              </tr>
              <tr v-if="byState.length === 0">
                <td colspan="5" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  No data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- By Subject -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Spending & Orders by Subject
          </h2>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Rank</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Subject</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total Spend</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Order Count</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Avg. Order Value</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(item, index) in bySubject" :key="item.subject" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  #{{ index + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white font-semibold">
                  {{ item.subject || 'Unknown' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right font-semibold">
                  ${{ formatCurrency(item.total_spend) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  {{ item.order_count }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300 text-right">
                  ${{ formatCurrency(item.total_spend / item.order_count) }}
                </td>
              </tr>
              <tr v-if="bySubject.length === 0">
                <td colspan="5" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  No data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminManagementAPI from '@/api/admin-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const byCountry = ref([])
const byState = ref([])
const bySubject = ref([])
const summary = ref(null)

const filters = ref({
  days: 0,
})

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.days > 0) {
      params.days = filters.value.days
    }

    const response = await adminManagementAPI.getGeographicAnalytics(params)
    byCountry.value = response.data.by_country || []
    byState.value = response.data.by_state || []
    bySubject.value = response.data.by_subject || []
    summary.value = response.data.summary || null
  } catch (error) {
    console.error('Failed to load geographic analytics:', error)
    showError(getErrorMessage(error, 'Failed to load geographic analytics'))
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const resetFilters = () => {
  filters.value = { days: 0 }
  loadData()
}

const formatCurrency = (value) => {
  if (!value || isNaN(value)) return '0.00'
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

const exportData = () => {
  // Create CSV content
  let csvContent = 'Geographic & Subject Analytics\n\n'
  
  // Country data
  csvContent += 'By Country\n'
  csvContent += 'Rank,Country,Total Spend,Order Count,Avg Order Value\n'
  byCountry.value.forEach((item, index) => {
    const avg = item.total_spend / item.order_count
    csvContent += `${index + 1},"${item.country || 'Unknown'}",${item.total_spend},${item.order_count},${avg.toFixed(2)}\n`
  })
  
  // State data
  csvContent += '\nBy State/Province\n'
  csvContent += 'Rank,State/Province,Total Spend,Order Count,Avg Order Value\n'
  byState.value.forEach((item, index) => {
    const avg = item.total_spend / item.order_count
    csvContent += `${index + 1},"${item.state || 'Unknown'}",${item.total_spend},${item.order_count},${avg.toFixed(2)}\n`
  })
  
  // Subject data
  csvContent += '\nBy Subject\n'
  csvContent += 'Rank,Subject,Total Spend,Order Count,Avg Order Value\n'
  bySubject.value.forEach((item, index) => {
    const avg = item.total_spend / item.order_count
    csvContent += `${index + 1},"${item.subject || 'Unknown'}",${item.total_spend},${item.order_count},${avg.toFixed(2)}\n`
  })
  
  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `geographic-analytics-${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  showSuccess('Data exported successfully')
}

onMounted(() => {
  loadData()
})
</script>
