<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-extrabold text-gray-900 dark:text-white">Analytics & Reports</h1>
        <p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
          Comprehensive analytics comparing orders, classes, income, and more across years
        </p>
      </div>
      <button
        @click="exportReport"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Export Report
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Filters</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Year</label>
          <select
            v-model="filters.startYear"
            @change="loadData"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
          >
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Year</label>
          <select
            v-model="filters.endYear"
            @change="loadData"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
          >
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <!-- Metrics Selection -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Metrics</label>
          <select
            v-model="filters.metrics"
            @change="loadData"
            multiple
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
            size="4"
          >
            <option value="orders">Orders</option>
            <option value="classes">Classes</option>
            <option value="income">Income</option>
            <option value="writers">Writers</option>
            <option value="clients">Clients</option>
            <option value="revenue">Revenue</option>
          </select>
        </div>
        <!-- Website Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Website</label>
          <select
            v-model="filters.websiteId"
            @change="loadData"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <button
          @click="loadData"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Apply Filters
        </button>
        <button
          @click="resetFilters"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Best Year Highlights -->
    <div v-if="bestYearData" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">Best Year: {{ bestYearData.year }}</h3>
          <div class="text-3xl">🏆</div>
        </div>
        <p class="text-blue-100 text-sm mb-4">Highest performance across all metrics</p>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-blue-100">Total Revenue:</span>
            <span class="font-bold">${{ formatNumber(bestYearData.totalRevenue) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-blue-100">Total Orders:</span>
            <span class="font-bold">{{ formatNumber(bestYearData.totalOrders) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-blue-100">Growth Rate:</span>
            <span class="font-bold">{{ bestYearData.growthRate }}%</span>
          </div>
        </div>
      </div>
      <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">Peak Orders</h3>
          <div class="text-3xl">📈</div>
        </div>
        <p class="text-green-100 text-sm mb-4">{{ peakOrdersYear.year }}</p>
        <div class="text-4xl font-bold">{{ formatNumber(peakOrdersYear.count) }}</div>
        <p class="text-green-100 text-sm mt-2">orders</p>
      </div>
      <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold">Peak Revenue</h3>
          <div class="text-3xl">💰</div>
        </div>
        <p class="text-purple-100 text-sm mb-4">{{ peakRevenueYear.year }}</p>
        <div class="text-4xl font-bold">${{ formatNumber(peakRevenueYear.revenue) }}</div>
        <p class="text-purple-100 text-sm mt-2">total revenue</p>
      </div>
    </div>

    <!-- Year-over-Year Comparison Chart -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Year-over-Year Comparison</h2>
      <div v-if="loading" class="flex items-center justify-center h-96">
        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600"></div>
      </div>
      <div v-else-if="yearlyComparisonSeries.length > 0">
        <apexchart
          type="line"
          height="400"
          :options="yearlyComparisonOptions"
          :series="yearlyComparisonSeries"
        ></apexchart>
      </div>
      <div v-else class="text-center py-16 text-gray-500">
        <p>No data available for the selected period</p>
      </div>
    </div>

    <!-- Metrics Comparison Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Orders vs Classes -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Orders vs Classes</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <apexchart
          v-else
          type="bar"
          height="300"
          :options="ordersVsClassesOptions"
          :series="ordersVsClassesSeries"
        ></apexchart>
      </div>

      <!-- Income Trend -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Income Trend</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <apexchart
          v-else
          type="area"
          height="300"
          :options="incomeTrendOptions"
          :series="incomeTrendSeries"
        ></apexchart>
      </div>
    </div>

    <!-- Revenue Breakdown -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Revenue Breakdown by Year</h2>
      <div v-if="loading" class="flex items-center justify-center h-96">
        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600"></div>
      </div>
      <apexchart
        v-else
        type="bar"
        height="400"
        :options="revenueBreakdownOptions"
        :series="revenueBreakdownSeries"
      ></apexchart>
    </div>

    <!-- Detailed Metrics Table -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="p-6">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4">Detailed Metrics by Year</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Year</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Orders</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Classes</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Revenue</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Writers</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Clients</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Growth</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="year in yearlyMetrics"
                :key="year.year"
                :class="year.year === bestYearData?.year ? 'bg-yellow-50 dark:bg-yellow-900/20' : ''"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {{ year.year }}
                  <span v-if="year.year === bestYearData?.year" class="ml-2 text-yellow-600">🏆</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatNumber(year.orders) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatNumber(year.classes) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  ${{ formatNumber(year.revenue) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatNumber(year.writers) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatNumber(year.clients) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span
                    :class="year.growth >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'"
                  >
                    {{ year.growth >= 0 ? '+' : '' }}{{ year.growth.toFixed(1) }}%
                  </span>
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
import { ref, computed, onMounted } from 'vue'
import analyticsAPI from '@/api/advanced-analytics'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { success: showSuccess, error: showError } = useToast()

// State
const loading = ref(false)
const websites = ref([])
const yearlyData = ref([])
const bestYearData = computed(() => {
  if (!yearlyMetrics.value || yearlyMetrics.value.length === 0) return null
  
  // Calculate composite score: revenue (50%) + orders (30%) + growth (20%)
  const scored = yearlyMetrics.value.map(year => ({
    ...year,
    score: (year.revenue * 0.5) + (year.orders * 0.3) + (Math.max(year.growth, 0) * 100 * 0.2)
  }))
  
  const best = scored.reduce((max, year) => year.score > max.score ? year : max, scored[0])
  
  return {
    year: best.year,
    totalRevenue: best.revenue,
    totalOrders: best.orders,
    growthRate: best.growth
  }
})

// Filters
const filters = ref({
  startYear: new Date().getFullYear() - 5,
  endYear: new Date().getFullYear(),
  metrics: ['orders', 'classes', 'income'],
  websiteId: ''
})

// Available years (last 10 years)
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear - i)
})

// Yearly metrics for table
const yearlyMetrics = computed(() => {
  if (!yearlyData.value || yearlyData.value.length === 0) return []
  
  return yearlyData.value.map((year, index) => {
    const prevYear = yearlyData.value[index + 1]
    const growth = prevYear
      ? ((year.revenue - prevYear.revenue) / prevYear.revenue) * 100
      : 0
    
    return {
      year: year.year,
      orders: year.orders || 0,
      classes: year.classes || 0,
      revenue: year.revenue || 0,
      writers: year.writers || 0,
      clients: year.clients || 0,
      growth
    }
  }).reverse()
})

// Peak years
const peakOrdersYear = computed(() => {
  if (!yearlyMetrics.value || yearlyMetrics.value.length === 0) return { year: 'N/A', count: 0 }
  const peak = yearlyMetrics.value.reduce((max, year) => 
    year.orders > max.orders ? year : max, yearlyMetrics.value[0]
  )
  return { year: peak.year, count: peak.orders }
})

const peakRevenueYear = computed(() => {
  if (!yearlyMetrics.value || yearlyMetrics.value.length === 0) return { year: 'N/A', revenue: 0 }
  const peak = yearlyMetrics.value.reduce((max, year) => 
    year.revenue > max.revenue ? year : max, yearlyMetrics.value[0]
  )
  return { year: peak.year, revenue: peak.revenue }
})

// Chart Series
const yearlyComparisonSeries = computed(() => {
  if (!yearlyData.value || yearlyData.value.length === 0) return []
  
  const series = []
  const years = yearlyData.value.map(d => d.year).reverse()
  
  if (filters.value.metrics.includes('orders')) {
    series.push({
      name: 'Orders',
      data: yearlyData.value.map(d => d.orders || 0).reverse()
    })
  }
  
  if (filters.value.metrics.includes('classes')) {
    series.push({
      name: 'Classes',
      data: yearlyData.value.map(d => d.classes || 0).reverse()
    })
  }
  
  if (filters.value.metrics.includes('income') || filters.value.metrics.includes('revenue')) {
    series.push({
      name: 'Revenue',
      data: yearlyData.value.map(d => d.revenue || 0).reverse()
    })
  }
  
  if (filters.value.metrics.includes('writers')) {
    series.push({
      name: 'Writers',
      data: yearlyData.value.map(d => d.writers || 0).reverse()
    })
  }
  
  if (filters.value.metrics.includes('clients')) {
    series.push({
      name: 'Clients',
      data: yearlyData.value.map(d => d.clients || 0).reverse()
    })
  }
  
  return series
})

const ordersVsClassesSeries = computed(() => {
  if (!yearlyData.value || yearlyData.value.length === 0) return []
  
  return [
    {
      name: 'Orders',
      data: yearlyData.value.map(d => d.orders || 0).reverse()
    },
    {
      name: 'Classes',
      data: yearlyData.value.map(d => d.classes || 0).reverse()
    }
  ]
})

const incomeTrendSeries = computed(() => {
  if (!yearlyData.value || yearlyData.value.length === 0) return []
  
  return [
    {
      name: 'Revenue',
      data: yearlyData.value.map(d => d.revenue || 0).reverse()
    }
  ]
})

const revenueBreakdownSeries = computed(() => {
  if (!yearlyData.value || yearlyData.value.length === 0) return []
  
  return [
    {
      name: 'Revenue',
      data: yearlyData.value.map(d => d.revenue || 0).reverse()
    }
  ]
})

// Chart Options
const yearlyComparisonOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: true },
    zoom: { enabled: true }
  },
  xaxis: {
    categories: yearlyData.value.map(d => d.year).reverse(),
    title: { text: 'Year' }
  },
  yaxis: {
    title: { text: 'Count/Amount' }
  },
  stroke: {
    curve: 'smooth',
    width: 3
  },
  markers: {
    size: 5
  },
  legend: {
    position: 'top'
  },
  tooltip: {
    shared: true,
    intersect: false
  },
  colors: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4']
}))

const ordersVsClassesOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  xaxis: {
    categories: yearlyData.value.map(d => d.year).reverse(),
    title: { text: 'Year' }
  },
  yaxis: {
    title: { text: 'Count' }
  },
  colors: ['#3b82f6', '#10b981'],
  legend: {
    position: 'top'
  }
}))

const incomeTrendOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false }
  },
  xaxis: {
    categories: yearlyData.value.map(d => d.year).reverse(),
    title: { text: 'Year' }
  },
  yaxis: {
    title: { text: 'Revenue ($)' },
    labels: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  },
  colors: ['#10b981'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3
    }
  },
  tooltip: {
    y: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  }
}))

const revenueBreakdownOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: true }
  },
  xaxis: {
    categories: yearlyData.value.map(d => d.year).reverse(),
    title: { text: 'Year' }
  },
  yaxis: {
    title: { text: 'Revenue ($)' },
    labels: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  },
  colors: ['#3b82f6'],
  dataLabels: {
    enabled: true,
    formatter: (value) => `$${formatNumber(value)}`
  },
  tooltip: {
    y: {
      formatter: (value) => `$${formatNumber(value)}`
    }
  }
}))

// Methods
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      start_year: filters.value.startYear,
      end_year: filters.value.endYear,
      metrics: filters.value.metrics.join(','),
      website_id: filters.value.websiteId || undefined
    }
    
    const response = await analyticsAPI.getYearlyComparison(params)
    yearlyData.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Failed to load analytics data:', error)
    showError(getErrorMessage(error, 'Failed to load analytics data'))
    yearlyData.value = []
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites({ is_active: true })
    websites.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    startYear: new Date().getFullYear() - 5,
    endYear: new Date().getFullYear(),
    metrics: ['orders', 'classes', 'income'],
    websiteId: ''
  }
  loadData()
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return new Intl.NumberFormat('en-US').format(Math.round(num))
}

const exportReport = () => {
  showSuccess('Export feature coming soon!')
  // TODO: Implement CSV/PDF export
}

onMounted(() => {
  loadWebsites()
  loadData()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

