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
      <div class="relative">
        <button
          @click="showExportMenu = !showExportMenu"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Export Report
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <!-- Export Menu Dropdown -->
        <div
          v-if="showExportMenu"
          @click.stop
          class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
          style="position: absolute;"
        >
          <button
            @click="exportToCSV"
            class="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export as CSV
          </button>
          <button
            @click="exportToPDF"
            class="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Export as PDF
          </button>
        </div>
      </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import analyticsAPI from '@/api/advanced-analytics'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { success: showSuccess, error: showError } = useToast()

// State
const loading = ref(false)
const websites = ref([])
const yearlyData = ref([])
const showExportMenu = ref(false)
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

// Export Functions
const exportToCSV = () => {
  try {
    if (!yearlyData.value || yearlyData.value.length === 0) {
      showError('No data available to export')
      return
    }

    // Prepare CSV headers
    const headers = ['Year', 'Orders', 'Classes', 'Revenue ($)', 'Writers', 'Clients', 'Growth Rate (%)']
    
    // Prepare CSV rows
    const rows = yearlyData.value.map(year => {
      const growthRate = year.growth_rate ? parseFloat(year.growth_rate).toFixed(2) : '0.00'
      return [
        year.year || '',
        year.orders || 0,
        year.classes || 0,
        parseFloat(year.revenue || 0).toFixed(2),
        year.writers || 0,
        year.clients || 0,
        growthRate
      ]
    })

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')

    // Add BOM for Excel compatibility
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    
    // Create download link
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    
    // Generate filename
    const startYear = filters.value.startYear || 'all'
    const endYear = filters.value.endYear || 'all'
    const websiteName = websites.value.find(w => w.id === filters.value.websiteId)?.name || 'all'
    const filename = `analytics-report_${websiteName}_${startYear}-${endYear}_${new Date().toISOString().split('T')[0]}.csv`
    
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    showExportMenu.value = false
    showSuccess('Report exported as CSV successfully')
  } catch (error) {
    console.error('Export error:', error)
    showError('Failed to export CSV: ' + (error.message || 'Unknown error'))
  }
}

const exportToPDF = async () => {
  try {
    if (!yearlyData.value || yearlyData.value.length === 0) {
      showError('No data available to export')
      return
    }

    // Try to use backend PDF export if available
    try {
      const params = {
        start_year: filters.value.startYear,
        end_year: filters.value.endYear,
        metrics: filters.value.metrics.join(','),
        website_id: filters.value.websiteId || undefined,
        format: 'pdf'
      }
      
      // Check if backend has export endpoint
      const response = await analyticsAPI.exportReport?.(params)
      
      if (response && response.data) {
        // Backend returned PDF
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        const startYear = filters.value.startYear || 'all'
        const endYear = filters.value.endYear || 'all'
        const websiteName = websites.value.find(w => w.id === filters.value.websiteId)?.name || 'all'
        const filename = `analytics-report_${websiteName}_${startYear}-${endYear}_${new Date().toISOString().split('T')[0]}.pdf`
        
        link.download = filename
        link.click()
        URL.revokeObjectURL(url)
        
        showExportMenu.value = false
        showSuccess('Report exported as PDF successfully')
        return
      }
    } catch (backendError) {
      // Backend export not available, use client-side generation
      // Backend PDF export not available, using client-side generation
    }

    // Client-side PDF generation using window.print() or html2pdf library
    // For now, we'll create a printable HTML version
    const printWindow = window.open('', '_blank')
    
    if (!printWindow) {
      showError('Please allow popups to export PDF')
      return
    }

    // Generate HTML content
    const htmlContent = generatePDFHTML()
    
    printWindow.document.write(htmlContent)
    printWindow.document.close()
    
    // Wait for content to load, then print
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print()
        showExportMenu.value = false
        showSuccess('PDF export opened in print dialog')
      }, 250)
    }
  } catch (error) {
    console.error('PDF export error:', error)
    showError('Failed to export PDF: ' + (error.message || 'Unknown error'))
  }
}

const generatePDFHTML = () => {
  const startYear = filters.value.startYear || 'All'
  const endYear = filters.value.endYear || 'All'
  const websiteName = websites.value.find(w => w.id === filters.value.websiteId)?.name || 'All Websites'
  const generatedDate = new Date().toLocaleString()
  
  let tableRows = ''
  yearlyData.value.forEach(year => {
    const growthRate = year.growth_rate ? parseFloat(year.growth_rate).toFixed(2) : '0.00'
    tableRows += `
      <tr>
        <td style="border: 1px solid #ddd; padding: 8px;">${year.year || ''}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${formatNumber(year.orders || 0)}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${formatNumber(year.classes || 0)}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">$${formatNumber(year.revenue || 0)}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${formatNumber(year.writers || 0)}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${formatNumber(year.clients || 0)}</td>
        <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${growthRate}%</td>
      </tr>
    `
  })

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Analytics Report</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          padding: 20px;
          color: #333;
        }
        h1 {
          color: #1f2937;
          border-bottom: 2px solid #3b82f6;
          padding-bottom: 10px;
        }
        .info {
          margin: 20px 0;
          padding: 15px;
          background: #f3f4f6;
          border-radius: 5px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
        }
        th {
          background: #3b82f6;
          color: white;
          padding: 12px;
          text-align: left;
          border: 1px solid #2563eb;
        }
        td {
          border: 1px solid #ddd;
          padding: 8px;
        }
        tr:nth-child(even) {
          background: #f9fafb;
        }
        .footer {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #ddd;
          font-size: 12px;
          color: #6b7280;
        }
        @media print {
          body { margin: 0; padding: 15px; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <h1>Analytics & Reports</h1>
      <div class="info">
        <p><strong>Website:</strong> ${websiteName}</p>
        <p><strong>Period:</strong> ${startYear} - ${endYear}</p>
        <p><strong>Generated:</strong> ${generatedDate}</p>
        ${bestYearData.value ? `<p><strong>Best Year:</strong> ${bestYearData.value.year} (${bestYearData.value.growthRate}% growth)</p>` : ''}
      </div>
      <table>
        <thead>
          <tr>
            <th>Year</th>
            <th style="text-align: right;">Orders</th>
            <th style="text-align: right;">Classes</th>
            <th style="text-align: right;">Revenue</th>
            <th style="text-align: right;">Writers</th>
            <th style="text-align: right;">Clients</th>
            <th style="text-align: right;">Growth Rate</th>
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
      <div class="footer">
        <p>This report was generated on ${generatedDate}</p>
        <p>Data period: ${startYear} - ${endYear}</p>
      </div>
    </body>
    </html>
  `
}

// Close export menu when clicking outside
const handleClickOutside = (event) => {
  if (showExportMenu.value && !event.target.closest('.relative')) {
    showExportMenu.value = false
  }
}

onMounted(() => {
  loadWebsites()
  loadData()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

