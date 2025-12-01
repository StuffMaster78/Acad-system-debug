<template>
  <div class="advanced-analytics space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
        <p class="mt-2 text-gray-600">Comprehensive analytics and insights across all operations</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedDays"
          @change="fetchDashboard"
          class="px-4 py-2 border rounded-lg"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="180">Last 180 days</option>
          <option :value="365">Last year</option>
        </select>
        <button
          @click="showComparison = !showComparison"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {{ showComparison ? 'Hide' : 'Show' }} Comparison
        </button>
        <button
          @click="fetchDashboard"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="dashboardData?.summary" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Revenue"
        :value="`$${formatCurrency(dashboardData.summary.total_revenue)}`"
        icon="💰"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Total Orders"
        :value="dashboardData.summary.total_orders || 0"
        icon="📦"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Completed Orders"
        :value="dashboardData.summary.completed_orders || 0"
        icon="✅"
        bgColor="bg-purple-100"
        :subtitle="`${dashboardData.summary.completion_rate || 0}% completion rate`"
      />
      <StatsCard
        name="Avg Order Value"
        :value="`$${formatCurrency(dashboardData.summary.avg_order_value)}`"
        icon="📊"
        bgColor="bg-orange-100"
      />
    </div>

    <!-- Additional Summary -->
    <div v-if="dashboardData?.summary" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Tickets"
        :value="dashboardData.summary.total_tickets || 0"
        icon="🎫"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="Total Disputes"
        :value="dashboardData.summary.total_disputes || 0"
        icon="⚖️"
        bgColor="bg-red-100"
      />
      <StatsCard
        name="Total Refunds"
        :value="dashboardData.summary.total_refunds || 0"
        icon="💸"
        bgColor="bg-pink-100"
      />
      <StatsCard
        name="Completion Rate"
        :value="`${dashboardData.summary.completion_rate || 0}%`"
        icon="📈"
        bgColor="bg-indigo-100"
      />
    </div>

    <!-- Revenue Analytics -->
    <div v-if="dashboardData?.revenue_analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartWidget
        title="Daily Revenue Breakdown"
        type="area"
        :series="dailyRevenueSeries"
        :options="dailyRevenueOptions"
        :loading="loading"
      />
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Revenue by Service Type</h2>
        <div v-if="loading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="service in dashboardData.revenue_analytics.by_service_type"
            :key="service.service_type"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <div class="font-medium text-gray-900">{{ service.service_type || 'Unknown' }}</div>
              <div class="text-sm text-gray-500">{{ service.count }} orders</div>
              </div>
            <div class="text-lg font-bold text-primary-600">
              ${{ formatCurrency(service.revenue) }}
            </div>
          </div>
        </div>
      </div>
        </div>

    <!-- Order Analytics -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Order Conversion Funnel</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      <div v-else-if="dashboardData?.order_analytics?.conversion_funnel" class="space-y-4">
        <div
          v-for="(count, stage) in dashboardData.order_analytics.conversion_funnel"
          :key="stage"
          class="flex items-center gap-4"
        >
          <div class="w-32 text-sm font-medium text-gray-700 capitalize">
            {{ stage.replace(/_/g, ' ') }}
          </div>
          <div class="flex-1">
            <div class="h-8 bg-gray-200 rounded-full overflow-hidden">
              <div
                :class="getFunnelColor(stage)"
                class="h-full flex items-center justify-end pr-4 text-white text-sm font-medium transition-all"
                :style="{ width: `${(count / dashboardData.order_analytics.conversion_funnel.created) * 100}%` }"
              >
                <span v-if="count > 0">{{ count }}</span>
              </div>
            </div>
          </div>
          <div class="w-20 text-right text-sm font-medium text-gray-900">
            {{ count }}
          </div>
        </div>
      </div>
    </div>

    <!-- Writer Performance -->
    <div v-if="dashboardData?.writer_performance?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Top Writers by Performance</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completed Orders</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Earnings</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Rating</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="writer in dashboardData.writer_performance" :key="writer.writer_id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">{{ writer.username || 'N/A' }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ writer.completed_orders || 0 }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                ${{ formatCurrency(writer.total_earnings) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ writer.avg_rating ? writer.avg_rating.toFixed(1) : 'N/A' }} ⭐
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Client Analytics -->
    <div v-if="dashboardData?.client_analytics?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Top Clients by Spending</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order Count</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Spent</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="client in dashboardData.client_analytics" :key="client.client_id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">{{ client.username || 'N/A' }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ client.email || 'N/A' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ client.order_count || 0 }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                ${{ formatCurrency(client.total_spent) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      </div>

    <!-- Weekly Trends -->
    <ChartWidget
      v-if="dashboardData?.weekly_trends?.length > 0"
      title="Weekly Trends"
      type="line"
      :series="weeklyTrendsSeries"
      :options="weeklyTrendsOptions"
      :loading="loading"
    />

    <!-- Support & Dispute Metrics -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-if="dashboardData?.support_metrics" class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Support Metrics</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Total Tickets</span>
            <span class="font-bold text-gray-900">{{ dashboardData.support_metrics.total_tickets || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Resolved Tickets</span>
            <span class="font-bold text-green-600">{{ dashboardData.support_metrics.resolved_tickets || 0 }}</span>
          </div>
        </div>
      </div>
      <div v-if="dashboardData?.dispute_metrics" class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Dispute Metrics</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Total Disputes</span>
            <span class="font-bold text-gray-900">{{ dashboardData.dispute_metrics.total_disputes || 0 }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Resolved</span>
            <span class="font-bold text-green-600">{{ dashboardData.dispute_metrics.resolved || 0 }}</span>
              </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Pending</span>
            <span class="font-bold text-yellow-600">{{ dashboardData.dispute_metrics.pending || 0 }}</span>
            </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-gray-700">Resolution Rate</span>
            <span class="font-bold text-blue-600">{{ dashboardData.dispute_metrics.resolution_rate || 0 }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Refund Metrics -->
    <div v-if="dashboardData?.refund_metrics" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Refund Metrics</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Total Refunds</div>
          <div class="text-2xl font-bold text-gray-900">{{ dashboardData.refund_metrics.total_refunds || 0 }}</div>
      </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Total Amount</div>
          <div class="text-2xl font-bold text-red-600">${{ formatCurrency(dashboardData.refund_metrics.total_amount) }}</div>
      </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Approved</div>
          <div class="text-2xl font-bold text-green-600">{{ dashboardData.refund_metrics.approved || 0 }}</div>
        </div>
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-600">Pending</div>
          <div class="text-2xl font-bold text-yellow-600">{{ dashboardData.refund_metrics.pending || 0 }}</div>
        </div>
      </div>
    </div>

    <!-- Period Comparison -->
    <div v-if="showComparison" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Period Comparison</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Period 1 (Days)</label>
          <input
            v-model.number="comparisonForm.period1_days"
            type="number"
            min="1"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Period 2 (Days)</label>
          <input
            v-model.number="comparisonForm.period2_days"
            type="number"
            min="1"
            class="w-full border rounded px-3 py-2"
          />
        </div>
      </div>
      <button
        @click="fetchComparison"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        :disabled="loadingComparison"
      >
        {{ loadingComparison ? 'Loading...' : 'Compare Periods' }}
      </button>
      
      <div v-if="comparisonData" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="font-semibold mb-2">Period 1</h3>
          <div class="space-y-2 text-sm">
            <div>Revenue: ${{ formatCurrency(comparisonData.period1.revenue) }}</div>
            <div>Orders: {{ comparisonData.period1.total_orders }}</div>
            <div>Completed: {{ comparisonData.period1.completed_orders }}</div>
          </div>
        </div>
        <div>
          <h3 class="font-semibold mb-2">Period 2</h3>
          <div class="space-y-2 text-sm">
            <div>Revenue: ${{ formatCurrency(comparisonData.period2.revenue) }}</div>
            <div>Orders: {{ comparisonData.period2.total_orders }}</div>
            <div>Completed: {{ comparisonData.period2.completed_orders }}</div>
          </div>
        </div>
        <div class="md:col-span-2 p-4 bg-blue-50 rounded-lg">
          <h3 class="font-semibold mb-2">Changes</h3>
          <div class="space-y-2 text-sm">
            <div>
              Revenue Change: 
              <span :class="comparisonData.changes.revenue_change_percent >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ comparisonData.changes.revenue_change_percent >= 0 ? '+' : '' }}{{ comparisonData.changes.revenue_change_percent }}%
              </span>
            </div>
            <div>
              Completed Orders Change: 
              <span :class="comparisonData.changes.completed_change_percent >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ comparisonData.changes.completed_change_percent >= 0 ? '+' : '' }}{{ comparisonData.changes.completed_change_percent }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import adminManagementAPI from '@/api/admin-management'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'

const { showToast } = useToast()

// State
const loading = ref(false)
const loadingComparison = ref(false)
const selectedDays = ref(30)
const showComparison = ref(false)
const dashboardData = ref(null)
const comparisonData = ref(null)

const comparisonForm = ref({
  period1_days: 30,
  period2_days: 30
})

// Methods
const fetchDashboard = async () => {
  loading.value = true
  try {
    const response = await adminManagementAPI.getAdvancedAnalytics({ days: selectedDays.value })
    dashboardData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch advanced analytics:', err)
    showToast('Failed to load analytics', 'error')
    dashboardData.value = null
  } finally {
    loading.value = false
  }
}

const fetchComparison = async () => {
  loadingComparison.value = true
  try {
    const response = await adminManagementAPI.getAdvancedAnalyticsComparison({
      period1_days: comparisonForm.value.period1_days,
      period2_days: comparisonForm.value.period2_days
    })
    comparisonData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch comparison:', err)
    showToast('Failed to load comparison', 'error')
  } finally {
    loadingComparison.value = false
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const getFunnelColor = (stage) => {
  const colors = {
    'created': 'bg-blue-500',
    'paid': 'bg-green-500',
    'assigned': 'bg-purple-500',
    'in_progress': 'bg-yellow-500',
    'submitted': 'bg-orange-500',
    'completed': 'bg-green-600',
  }
  return colors[stage] || 'bg-gray-500'
}

// Computed
const dailyRevenueSeries = computed(() => {
  if (!dashboardData.value?.revenue_analytics?.daily_breakdown?.length) return []
  return [{
    name: 'Revenue',
    data: dashboardData.value.revenue_analytics.daily_breakdown.map(d => parseFloat(d.revenue || 0))
  }]
})

const dailyRevenueOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  xaxis: {
    categories: dashboardData.value?.revenue_analytics?.daily_breakdown?.map(d => {
      if (d.date) {
        return new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || []
  },
  yaxis: { title: { text: 'Revenue ($)' } },
  stroke: { curve: 'smooth' },
  colors: ['#10B981'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3,
      stops: [0, 90, 100]
    }
  }
}))

const weeklyTrendsSeries = computed(() => {
  if (!dashboardData.value?.weekly_trends?.length) return []
  return [
    {
      name: 'Orders Created',
      data: dashboardData.value.weekly_trends.map(t => t.orders_created || 0)
    },
    {
      name: 'Orders Completed',
      data: dashboardData.value.weekly_trends.map(t => t.orders_completed || 0)
    },
    {
      name: 'Revenue',
      data: dashboardData.value.weekly_trends.map(t => parseFloat(t.revenue || 0))
    }
  ]
})

const weeklyTrendsOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: {
    categories: dashboardData.value?.weekly_trends?.map(t => {
      if (t.week) {
        return new Date(t.week).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || []
  },
  yaxis: { title: { text: 'Count / Revenue' } },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#3B82F6', '#10B981', '#F59E0B'],
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  }
}))

// Lifecycle
onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>
