<template>
  <div class="space-y-6">
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <QuickActionCard
        to="/support/tickets"
        icon="🎫"
        title="Tickets"
        description="Manage support tickets"
      />
      <QuickActionCard
        to="/support/queue"
        icon="📋"
        title="Ticket Queue"
        description="View ticket queue"
      />
      <QuickActionCard
        to="/orders"
        icon="📝"
        title="Order Management"
        description="Handle order issues"
      />
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Open Tickets"
        :value="supportDashboardData?.open_tickets_count || 0"
        icon="🎫"
      />
      <StatsCard
        name="Resolved Today"
        :value="supportDashboardData?.resolved_today_count || 0"
        icon="✅"
      />
      <StatsCard
        name="Pending Orders"
        :value="supportDashboardData?.pending_orders_count || 0"
        icon="⏳"
      />
      <StatsCard
        name="Escalations"
        :value="supportDashboardData?.escalations_count || 0"
        icon="🚨"
      />
    </div>

    <!-- Ticket Analytics Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Ticket Status Distribution -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Ticket Status Distribution</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <apexchart
          v-else-if="ticketStatusSeries.length > 0"
          type="donut"
          height="300"
          :options="ticketStatusOptions"
          :series="ticketStatusSeries"
        ></apexchart>
        <div v-else class="h-64 flex items-center justify-center text-gray-500">
          No ticket data available
        </div>
      </div>

      <!-- Ticket Trends -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Ticket Trends (Last 7 Days)</h2>
        <div v-if="loading" class="flex items-center justify-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <apexchart
          v-else-if="ticketTrendsSeries.length > 0"
          type="area"
          height="300"
          :options="ticketTrendsOptions"
          :series="ticketTrendsSeries"
        ></apexchart>
        <div v-else class="h-64 flex items-center justify-center text-gray-500">
          No trend data available
        </div>
      </div>
    </div>

    <!-- Performance Metrics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm p-6 border border-blue-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold text-gray-900">Response Time</h3>
          <span class="text-3xl">⚡</span>
        </div>
        <div class="text-3xl font-bold text-blue-600">
          {{ supportDashboardData?.avg_response_time ? `${supportDashboardData.avg_response_time}h` : 'N/A' }}
        </div>
        <p class="text-sm text-gray-600 mt-2">Average response time</p>
      </div>
      <div class="card bg-linear-to-br from-green-50 to-green-100 rounded-lg shadow-sm p-6 border border-green-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold text-gray-900">Resolution Rate</h3>
          <span class="text-3xl">✅</span>
        </div>
        <div class="text-3xl font-bold text-green-600">
          {{ supportDashboardData?.resolution_rate ? `${supportDashboardData.resolution_rate}%` : 'N/A' }}
        </div>
        <p class="text-sm text-gray-600 mt-2">Tickets resolved</p>
      </div>
      <div class="card bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow-sm p-6 border border-purple-200">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-lg font-semibold text-gray-900">Satisfaction</h3>
          <span class="text-3xl">⭐</span>
        </div>
        <div class="text-3xl font-bold text-purple-600">
          {{ supportDashboardData?.avg_satisfaction ? `${supportDashboardData.avg_satisfaction}/5` : 'N/A' }}
        </div>
        <p class="text-sm text-gray-600 mt-2">Average rating</p>
      </div>
    </div>

    <!-- Recent Tickets -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Recent Tickets</h2>
        <router-link to="/support/tickets" class="text-primary-600 text-sm">View all</router-link>
      </div>
      <div v-if="supportRecentTicketsLoading" class="text-center py-8 text-gray-500">
        <div class="text-sm">Loading tickets...</div>
      </div>
      <div v-else-if="supportRecentTickets && supportRecentTickets.length" class="divide-y divide-gray-200">
        <div v-for="ticket in supportRecentTickets.slice(0, 5)" :key="ticket.id" class="py-3 flex items-center justify-between hover:bg-gray-50 rounded-lg px-2">
          <div class="flex-1">
            <div class="font-medium">#{{ ticket.id }} · {{ ticket.title }}</div>
            <div class="text-xs text-gray-500 mt-1">
              <span :class="getTicketStatusClass(ticket.status)" class="px-2 py-0.5 rounded-full text-xs font-medium mr-2">
                {{ ticket.status_display || ticket.status }}
              </span>
              <span :class="getTicketPriorityClass(ticket.priority)" class="px-2 py-0.5 rounded-full text-xs font-medium mr-2">
                {{ ticket.priority_display || ticket.priority }}
              </span>
              <span v-if="ticket.created_at" class="text-gray-400">
                {{ new Date(ticket.created_at).toLocaleDateString() }}
              </span>
            </div>
          </div>
          <router-link :to="`/tickets/${ticket.id}`" class="text-primary-600 text-sm hover:underline">View</router-link>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-sm">No recent tickets</div>
        <router-link to="/support/queue" class="text-primary-600 text-sm mt-2 inline-block">View ticket queue →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'

const props = defineProps({
  supportDashboardData: Object,
  supportRecentTickets: Array,
  supportRecentTicketsLoading: Boolean,
  loading: Boolean
})

// Chart Series
const ticketStatusSeries = computed(() => {
  if (!props.supportDashboardData) return []
  
  return [
    props.supportDashboardData.open_tickets_count || 0,
    props.supportDashboardData.resolved_today_count || 0,
    props.supportDashboardData.escalations_count || 0,
    props.supportDashboardData.pending_orders_count || 0
  ]
})

const ticketTrendsSeries = computed(() => {
  // Mock trend data - adjust based on actual API response
  if (!props.supportDashboardData) return []
  
  // If API provides trend data, use it; otherwise create from available data
  const data = props.supportDashboardData
  return [
    {
      name: 'Tickets',
      data: [
        data.open_tickets_count || 0,
        data.resolved_today_count || 0,
        data.escalations_count || 0
      ]
    }
  ]
})

// Chart Options
const ticketStatusOptions = computed(() => ({
  chart: {
    type: 'donut',
    toolbar: { show: false }
  },
  labels: ['Open', 'Resolved Today', 'Escalations', 'Pending Orders'],
  colors: ['#f59e0b', '#10b981', '#ef4444', '#3b82f6'],
  legend: {
    position: 'bottom'
  },
  dataLabels: {
    enabled: true,
    formatter: (val) => `${Math.round(val)}%`
  }
}))

const ticketTrendsOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false }
  },
  xaxis: {
    categories: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
  },
  yaxis: {
    title: { text: 'Number of Tickets' }
  },
  stroke: {
    curve: 'smooth',
    width: 2
  },
  colors: ['#3b82f6'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.3
    }
  }
}))

const getTicketStatusClass = (status) => {
  const classes = {
    open: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    closed: 'bg-green-100 text-green-800',
    awaiting_response: 'bg-orange-100 text-orange-800',
    escalated: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getTicketPriorityClass = (priority) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}
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

