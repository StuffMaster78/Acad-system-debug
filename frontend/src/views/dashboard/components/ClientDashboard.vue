<template>
  <div class="space-y-6">
    <!-- Quick Actions -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <QuickActionCard
        to="/orders/wizard"
        icon="🧭"
        title="Start Order Wizard"
        description="Guided steps to place an order"
      />
      <QuickActionCard
        to="/orders"
        icon="📝"
        title="My Orders"
        description="View and track your orders"
      />
      <QuickActionCard
        to="/wallet"
        icon="💼"
        title="Wallet"
        description="Top up and manage payments"
      />
      <QuickActionCard
        to="/payments"
        icon="💳"
        title="Payment History"
        description="Invoices & receipts"
      />
    </div>

    <!-- Create Order Button - Prominent -->
    <div class="card bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-6 text-white">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold mb-2">Ready to Place an Order?</h2>
          <p class="text-primary-100">Get started with our guided order wizard</p>
        </div>
        <router-link
          to="/orders/wizard"
          class="flex items-center gap-2 px-6 py-3 bg-white text-primary-600 rounded-lg hover:bg-primary-50 transition-colors shadow-md hover:shadow-lg font-semibold"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Order
        </router-link>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Wallet Balance"
        :value="`$${(clientWalletAnalytics?.balance ?? walletBalance).toFixed(2)}`"
        icon="💼"
        subtitle="Current balance"
      />
      <StatsCard
        name="Total Spend"
        :value="`$${(clientDashboardData?.total_spend ?? clientDashboardData?.all_time_spend ?? 0).toFixed(2)}`"
        icon="💰"
        :subtitle="clientDashboardData?.this_month?.spend ? `$${clientDashboardData.this_month.spend.toFixed(2)} this month` : (clientDashboardData?.month_spend ? `$${clientDashboardData.month_spend.toFixed(2)} this month` : 'All time')"
      />
      <StatsCard
        name="Total Orders"
        :value="clientDashboardData?.total_orders ?? 0"
        icon="📝"
        :subtitle="`${clientDashboardData?.this_month?.orders ?? clientDashboardData?.month_orders ?? 0} this month`"
      />
      <StatsCard
        name="Loyalty Points"
        :value="clientLoyaltyData?.loyalty_points ?? 0"
        icon="⭐"
        :subtitle="clientLoyaltyData?.current_tier?.name ?? 'No tier'"
      />
    </div>

    <!-- Additional Summary Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="card p-4 border border-primary-100 bg-primary-50">
        <div class="text-sm font-medium text-gray-600">Pending Payments</div>
        <div class="text-3xl font-bold text-primary-600 mt-2">
          ${{ formatCurrency(clientDashboardData?.pending_payments?.total ?? clientDashboardData?.pending_payments_total ?? 0) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">
          {{ clientDashboardData?.pending_payments?.count ?? 0 }} invoice(s)
        </div>
      </div>
      <div class="card p-4 border border-emerald-100 bg-emerald-50">
        <div class="text-sm font-medium text-gray-600">Active Orders</div>
        <div class="text-3xl font-bold text-emerald-600 mt-2">
          {{ formatNumber(clientDashboardData?.status_breakdown?.in_progress ?? clientDashboardData?.active_orders ?? 0) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Currently in progress</div>
      </div>
      <div class="card p-4 border border-yellow-100 bg-yellow-50">
        <div class="text-sm font-medium text-gray-600">Revision Requests</div>
        <div class="text-3xl font-bold text-yellow-600 mt-2">
          {{ formatNumber(clientDashboardData?.status_breakdown?.on_revision ?? clientDashboardData?.revision_requests ?? 0) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Awaiting action</div>
      </div>
      <div class="card p-4 border border-blue-100 bg-blue-50">
        <div class="text-sm font-medium text-gray-600">Unread Messages</div>
        <div class="text-3xl font-bold text-blue-600 mt-2">
          {{ formatNumber(recentCommunicationsUnread) }}
        </div>
        <div class="text-xs text-gray-500 mt-1">Across communications</div>
      </div>
    </div>

    <!-- Order Status Breakdown -->
    <div v-if="clientDashboardData?.status_breakdown" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Order Status Breakdown</h2>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ formatNumber(clientDashboardData.status_breakdown.pending || 0) }}</div>
          <div class="text-sm text-gray-600 mt-1">⏳ Pending</div>
        </div>
        <div class="text-center p-4 bg-purple-50 rounded-lg">
          <div class="text-2xl font-bold text-purple-600">{{ formatNumber(clientDashboardData.status_breakdown.in_progress || 0) }}</div>
          <div class="text-sm text-gray-600 mt-1">🔄 In Progress</div>
        </div>
        <div class="text-center p-4 bg-orange-50 rounded-lg">
          <div class="text-2xl font-bold text-orange-600">{{ formatNumber(clientDashboardData.status_breakdown.on_revision || 0) }}</div>
          <div class="text-sm text-gray-600 mt-1">✏️ On Revision</div>
        </div>
        <div class="text-center p-4 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ formatNumber(clientDashboardData.status_breakdown.completed || 0) }}</div>
          <div class="text-sm text-gray-600 mt-1">✅ Completed</div>
        </div>
      </div>
    </div>

    <!-- Loyalty Status -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow-sm p-6 border border-yellow-200">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Loyalty Status</h2>
          <span class="text-3xl">⭐</span>
        </div>
        <div v-if="hasLoyaltyData" class="space-y-3">
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">Current Tier</span>
              <span class="text-lg font-bold text-yellow-700">{{ clientLoyaltyData.current_tier?.name || 'None' }}</span>
            </div>
            <div v-if="clientLoyaltyData.next_tier?.name" class="flex items-center justify-between mb-1">
              <span class="text-sm text-gray-600">Next Tier</span>
              <span class="text-sm font-medium text-gray-700">{{ clientLoyaltyData.next_tier.name }}</span>
            </div>
            <div v-if="clientLoyaltyData.points_to_next_tier > 0" class="mt-2">
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs text-gray-600">Points to next tier</span>
                <span class="text-xs font-medium text-gray-700">{{ clientLoyaltyData.points_to_next_tier }} points</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-yellow-500 h-2 rounded-full transition-all"
                  :style="{ width: `${Math.min(100, (clientLoyaltyData.loyalty_points / (clientLoyaltyData.next_tier?.points_required || 1)) * 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
          <div class="pt-3 border-t border-yellow-200">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Points earned this month</span>
              <span class="text-sm font-bold text-yellow-700">+{{ clientLoyaltyData.points_earned_this_month || 0 }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-6 text-sm text-gray-500">
          Loyalty data not available yet.
        </div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Recent Badges</h2>
          <router-link to="/loyalty" class="text-primary-600 text-sm">View all</router-link>
        </div>
        <div v-if="clientLoyaltyData.badges && clientLoyaltyData.badges.length" class="space-y-2">
          <div 
            v-for="badge in clientLoyaltyData.badges.slice(0, 5)" 
            :key="badge.id"
            class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg"
          >
            <div class="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <span class="text-xl">🏆</span>
            </div>
            <div class="flex-1">
              <div class="font-medium text-sm">{{ badge.badge_name }}</div>
              <div class="text-xs text-gray-500">{{ badge.awarded_at ? new Date(badge.awarded_at).toLocaleDateString() : '' }}</div>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">No badges earned yet</div>
      </div>
    </div>

    <!-- Analytics Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartWidget
        title="Order Trends (Last 30 Days)"
        type="area"
        :series="orderTrendsSeries"
        :options="orderTrendsOptions"
        :loading="loading"
      />
      <ChartWidget
        title="Spending Trends (Last 30 Days)"
        type="bar"
        :series="spendingTrendsSeries"
        :options="spendingTrendsOptions"
        :loading="loading"
      />
    </div>

    <!-- Service Breakdown & Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Service Type Breakdown</h2>
        <div v-if="hasServiceBreakdown" class="space-y-3">
          <div 
            v-for="service in clientAnalyticsData.service_breakdown" 
            :key="service.service_type"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <div class="font-medium">{{ service.service_type || 'Unknown' }}</div>
              <div class="text-sm text-gray-500">{{ service.count }} orders</div>
            </div>
            <div class="text-lg font-bold text-green-600">${{ service.total_spend.toFixed(2) }}</div>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">No service data available</div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Order Performance</h2>
        <div v-if="hasPerformanceStats" class="space-y-4">
          <div class="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Average Completion Time</div>
              <div class="text-2xl font-bold text-blue-600">
                {{ clientAnalyticsData.avg_completion_days ? `${Math.round(clientAnalyticsData.avg_completion_days)} days` : 'N/A' }}
              </div>
            </div>
            <span class="text-3xl">⏱️</span>
          </div>
          <div class="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
            <div>
              <div class="text-sm font-medium text-gray-600">Revision Rate</div>
              <div class="text-2xl font-bold text-orange-600">
                {{ clientAnalyticsData.revision_rate ? `${clientAnalyticsData.revision_rate.toFixed(1)}%` : '0%' }}
              </div>
            </div>
            <span class="text-3xl">📝</span>
          </div>
        </div>
        <div v-else class="text-center py-10 text-sm text-gray-500">
          Performance stats not available.
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Recent Orders</h2>
        <router-link to="/orders" class="text-primary-600 text-sm">View all</router-link>
      </div>
      <div v-if="recentOrdersLoading" class="text-sm text-gray-500">Loading...</div>
      <div v-else class="divide-y divide-gray-200">
        <div v-for="o in recentOrders" :key="o.id" class="py-3 flex items-center justify-between">
          <div>
            <div class="font-medium">#{{ o.id }} · {{ o.topic }}</div>
            <div class="text-xs text-gray-500">Status: {{ o.status }} · Created: {{ new Date(o.created_at).toLocaleString() }}</div>
          </div>
          <div class="flex items-center gap-2">
            <router-link
              :to="`/orders/${o.id}/messages`"
              class="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-xs flex items-center gap-1"
              title="Messages"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </router-link>
            <router-link :to="`/orders/${o.id}`" class="text-primary-600 text-sm hover:underline">Open</router-link>
          </div>
        </div>
        <div v-if="!recentOrders.length" class="text-sm text-gray-500">No recent orders.</div>
      </div>
    </div>

    <!-- Communications & Tickets -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Recent Messages</h2>
          <router-link to="/orders" class="text-primary-600 text-sm">View all</router-link>
        </div>
        <div v-if="recentCommunicationsLoading" class="text-sm text-gray-500">Loading...</div>
        <div v-else-if="recentCommunications.length" class="space-y-3">
          <div
            v-for="thread in recentCommunications"
            :key="thread.id"
            class="p-3 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-sm">{{ thread.subject || thread.order_topic || 'Conversation' }}</div>
                <div class="text-xs text-gray-500">
                  Updated: {{ formatDate(thread.updated_at || thread.created_at) }}
                </div>
              </div>
              <span v-if="thread.unread_count" class="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">
                {{ thread.unread_count }} new
              </span>
            </div>
            <div class="text-xs text-gray-500 mt-2 flex items-center gap-2">
              <span>Participants:</span>
              <span class="font-medium text-gray-700">{{ formatParticipants(thread.participants) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">No recent communications</div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Support Tickets</h2>
          <router-link to="/tickets" class="text-primary-600 text-sm">View all</router-link>
        </div>
        <div v-if="recentTicketsLoading" class="text-sm text-gray-500">Loading...</div>
        <div v-else-if="recentTickets.length" class="space-y-3">
          <div
            v-for="ticket in recentTickets"
            :key="ticket.id"
            class="p-3 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-sm">#{{ ticket.id }} · {{ ticket.subject || 'Support Ticket' }}</div>
                <div class="text-xs text-gray-500">
                  Updated: {{ formatDate(ticket.updated_at || ticket.created_at) }}
                </div>
              </div>
              <span class="px-2 py-0.5 text-xs rounded-full"
                :class="getTicketStatusBadge(ticket.status)"
              >
                {{ (ticket.status || 'pending').replace('_', ' ') }}
              </span>
            </div>
            <p class="text-xs text-gray-600 mt-2 line-clamp-2">{{ ticket.preview || ticket.last_message || 'No messages yet' }}</p>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">No recent tickets</div>
      </div>
    </div>

    <!-- Notifications -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Notifications</h2>
          <router-link to="/notifications" class="text-primary-600 text-sm">View all</router-link>
        </div>
        <div v-if="recentNotificationsLoading" class="text-sm text-gray-500">Loading...</div>
        <div v-else-if="recentNotifications.length" class="space-y-2">
          <div v-for="n in recentNotifications.slice(0, 3)" :key="n.id" class="p-2 border rounded hover:bg-gray-50">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="text-sm font-medium">{{ n.title || n.rendered_title }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ formatDate(n.created_at || n.sent_at) }}</div>
              </div>
              <span v-if="!n.is_read" class="w-2 h-2 bg-blue-600 rounded-full ml-2"></span>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">No notifications</div>
      </div>
      <div class="card p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Messages</h2>
        <p class="text-sm text-gray-500 mb-3">Chat with writers and support through your orders.</p>
        <router-link to="/orders" class="inline-block mt-3 text-primary-600 text-sm">View orders with messages</router-link>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Quick Links</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <router-link to="/wallet" class="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">💼</span>
          </div>
          <div>
            <div class="font-medium text-sm">Wallet</div>
            <div class="text-xs text-gray-500">Manage balance</div>
          </div>
        </router-link>
        <router-link to="/discounts" class="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">🎟️</span>
          </div>
          <div>
            <div class="font-medium text-sm">Discounts</div>
            <div class="text-xs text-gray-500">Browse offers</div>
          </div>
        </router-link>
        <router-link to="/loyalty" class="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">⭐</span>
          </div>
          <div>
            <div class="font-medium text-sm">Loyalty</div>
            <div class="text-xs text-gray-500">Points & rewards</div>
          </div>
        </router-link>
        <router-link to="/referrals" class="flex items-center gap-3 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
            <span class="text-2xl">👥</span>
          </div>
          <div>
            <div class="font-medium text-sm">Referrals</div>
            <div class="text-xs text-gray-500">Share & earn</div>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'

const props = defineProps({
  clientDashboardData: {
    type: Object,
    default: () => ({}),
  },
  clientLoyaltyData: {
    type: Object,
    default: () => ({}),
  },
  clientAnalyticsData: {
    type: Object,
    default: () => ({}),
  },
  clientWalletAnalytics: {
    type: Object,
    default: () => ({}),
  },
  walletBalance: {
    type: Number,
    default: 0,
  },
  recentOrders: {
    type: Array,
    default: () => [],
  },
  recentOrdersLoading: Boolean,
  recentNotifications: {
    type: Array,
    default: () => [],
  },
  recentNotificationsLoading: Boolean,
  recentCommunications: {
    type: Array,
    default: () => [],
  },
  recentCommunicationsLoading: Boolean,
  recentTickets: {
    type: Array,
    default: () => [],
  },
  recentTicketsLoading: Boolean,
  loading: Boolean
})

const hasLoyaltyData = computed(() => {
  return !!props.clientLoyaltyData && Object.keys(props.clientLoyaltyData).length > 0
})

const hasServiceBreakdown = computed(() => {
  return (props.clientAnalyticsData?.service_breakdown?.length || 0) > 0
})

const hasPerformanceStats = computed(() => {
  return props.clientAnalyticsData && (
    props.clientAnalyticsData.avg_completion_days ||
    props.clientAnalyticsData.revision_rate
  )
})

const recentCommunicationsUnread = computed(() => {
  return props.recentCommunications?.reduce((sum, thread) => sum + (thread.unread_count || 0), 0) || 0
})

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const orderTrendsSeries = computed(() => {
  if (!props.clientAnalyticsData?.order_trends?.length) return []
  return [{
    name: 'Orders',
    data: props.clientAnalyticsData.order_trends.map(t => t.count)
  }]
})

const orderTrendsOptions = computed(() => ({
  chart: { type: 'area', toolbar: { show: false } },
  xaxis: { 
    categories: props.clientAnalyticsData?.order_trends?.map(t => new Date(t.date).toLocaleDateString()) || [],
    labels: { rotate: -45 }
  },
  yaxis: { title: { text: 'Orders' } },
  stroke: { curve: 'smooth' },
  colors: ['#3B82F6'],
}))

const spendingTrendsSeries = computed(() => {
  if (!props.clientAnalyticsData?.spending_trends?.length) return []
  return [{
    name: 'Spending',
    data: props.clientAnalyticsData.spending_trends.map(t => t.total)
  }]
})

const spendingTrendsOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false } },
  xaxis: { 
    categories: props.clientAnalyticsData?.spending_trends?.map(t => new Date(t.date).toLocaleDateString()) || [],
    labels: { rotate: -45 }
  },
  yaxis: { title: { text: 'Amount ($)' } },
  colors: ['#10B981'],
}))

const formatParticipants = (participants = []) => {
  if (!participants.length) return 'N/A'
  return participants
    .map(participant => participant?.name || participant?.email || participant?.username)
    .filter(Boolean)
    .slice(0, 3)
    .join(', ')
}

const getTicketStatusBadge = (status = 'pending') => {
  const map = {
    pending: 'bg-yellow-100 text-yellow-700',
    open: 'bg-blue-100 text-blue-700',
    closed: 'bg-green-100 text-green-700',
    resolved: 'bg-green-100 text-green-700',
    escalated: 'bg-red-100 text-red-700',
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
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

