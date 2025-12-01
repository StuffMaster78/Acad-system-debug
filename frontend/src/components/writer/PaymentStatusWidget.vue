<template>
  <div class="space-y-6">
    <!-- Payment Status Summary Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Earnings"
        :value="`$${formatCurrency(paymentStatus?.summary?.total_earnings || 0)}`"
        icon="💰"
        subtitle="All time"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Pending Payments"
        :value="`$${formatCurrency(paymentStatus?.summary?.pending_amount || 0)}`"
        icon="⏳"
        :subtitle="`${paymentStatus?.summary?.pending_payments || 0} payments`"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="Delayed Payments"
        :value="`$${formatCurrency(paymentStatus?.summary?.delayed_amount || 0)}`"
        icon="⚠️"
        :subtitle="`${paymentStatus?.summary?.delayed_payments?.length || 0} payments`"
        bgColor="bg-orange-100"
      />
      <StatsCard
        name="Recent (30d)"
        :value="`$${formatCurrency(paymentStatus?.summary?.recent_paid_30d || 0)}`"
        icon="📈"
        subtitle="Paid this month"
        bgColor="bg-blue-100"
      />
    </div>

    <!-- Additional Summary Cards -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="card bg-white rounded-lg shadow-sm p-4 border border-purple-100">
        <div class="text-sm font-medium text-gray-600 mb-1">Total Bonuses</div>
        <div class="text-2xl font-bold text-purple-900">
          ${{ formatCurrency(paymentStatus?.summary?.total_bonuses || 0) }}
        </div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-4 border border-pink-100">
        <div class="text-sm font-medium text-gray-600 mb-1">Total Tips</div>
        <div class="text-2xl font-bold text-pink-900">
          ${{ formatCurrency(paymentStatus?.summary?.total_tips || 0) }}
        </div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-4 border border-red-100">
        <div class="text-sm font-medium text-gray-600 mb-1">Total Fines</div>
        <div class="text-2xl font-bold text-red-900">
          ${{ formatCurrency(paymentStatus?.summary?.total_fines || 0) }}
        </div>
      </div>
      <div class="card bg-white rounded-lg shadow-sm p-4 border border-indigo-100">
        <div class="text-sm font-medium text-gray-600 mb-1">Payout Requests</div>
        <div class="text-2xl font-bold text-indigo-900">
          {{ paymentStatus?.summary?.pending_payout_requests || 0 }}
        </div>
        <div class="text-xs text-gray-500 mt-1">
          ${{ formatCurrency(paymentStatus?.summary?.pending_payout_amount || 0) }} pending
        </div>
      </div>
    </div>

    <!-- Payment Status Breakdown -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Payment Status Breakdown</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="paymentStatus?.status_breakdown" class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div
          v-for="(data, status) in paymentStatus.status_breakdown"
          :key="status"
          class="text-center p-4 rounded-lg border"
          :class="getStatusColorClass(status)"
        >
          <div class="text-sm font-medium text-gray-600 mb-1">{{ status }}</div>
          <div class="text-2xl font-bold mb-1">{{ data.count || 0 }}</div>
          <div class="text-xs text-gray-500">${{ formatCurrency(data.total_amount || 0) }}</div>
        </div>
      </div>
    </div>

    <!-- Payment Trends Chart -->
    <ChartWidget
      v-if="paymentTrendsSeries.length > 0"
      title="Payment Trends (Last 12 Weeks)"
      type="line"
      :series="paymentTrendsSeries"
      :options="paymentTrendsOptions"
      :loading="loading"
    />

    <!-- Pending Payments List -->
    <div v-if="paymentStatus?.pending_payments?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Pending Payments</h2>
        <router-link to="/writer/payments" class="text-primary-600 text-sm hover:underline">
          View all →
        </router-link>
      </div>
      <div class="space-y-2">
        <div
          v-for="payment in paymentStatus.pending_payments.slice(0, 5)"
          :key="payment.id"
          class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200"
        >
          <div class="flex-1">
            <div class="font-medium text-gray-900">
              Order #{{ payment.order_id || 'N/A' }}
              <span v-if="payment.special_order_id">(Special Order #{{ payment.special_order_id }})</span>
            </div>
            <div class="text-sm text-gray-600 mt-1">
              Amount: ${{ formatCurrency(payment.amount) }}
              <span v-if="payment.bonuses > 0"> + ${{ formatCurrency(payment.bonuses) }} bonus</span>
              <span v-if="payment.tips > 0"> + ${{ formatCurrency(payment.tips) }} tip</span>
              <span v-if="payment.fines > 0"> - ${{ formatCurrency(payment.fines) }} fine</span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              Status: {{ payment.status }}
              <span v-if="payment.processed_at">
                · Processed: {{ formatDate(payment.processed_at) }}
              </span>
            </div>
          </div>
          <router-link
            v-if="payment.order_id"
            :to="`/orders/${payment.order_id}`"
            class="text-primary-600 text-sm hover:underline ml-4"
          >
            View Order
          </router-link>
        </div>
      </div>
    </div>

    <!-- Delayed Payments List -->
    <div v-if="paymentStatus?.delayed_payments?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900">Delayed Payments</h2>
        <span class="text-sm text-orange-600 font-medium">
          {{ paymentStatus.delayed_payments.length }} delayed
        </span>
      </div>
      <div class="space-y-2">
        <div
          v-for="payment in paymentStatus.delayed_payments.slice(0, 5)"
          :key="payment.id"
          class="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200"
        >
          <div class="flex-1">
            <div class="font-medium text-gray-900">Order #{{ payment.order_id || 'N/A' }}</div>
            <div class="text-sm text-gray-600 mt-1">
              Amount: ${{ formatCurrency(payment.amount) }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              Status: {{ payment.status }}
              <span v-if="payment.updated_at">
                · Last updated: {{ formatDate(payment.updated_at) }}
              </span>
            </div>
          </div>
          <router-link
            v-if="payment.order_id"
            :to="`/orders/${payment.order_id}`"
            class="text-primary-600 text-sm hover:underline ml-4"
          >
            View Order
          </router-link>
        </div>
      </div>
    </div>

    <!-- Payout Requests -->
    <div v-if="paymentStatus?.payout_requests?.length > 0" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Payout Requests</h2>
      <div class="space-y-2">
        <div
          v-for="request in paymentStatus.payout_requests"
          :key="request.id"
          class="flex items-center justify-between p-3 bg-indigo-50 rounded-lg border border-indigo-200"
        >
          <div>
            <div class="font-medium text-gray-900">
              ${{ formatCurrency(request.amount_requested) }}
            </div>
            <div class="text-sm text-gray-600 mt-1">
              Status: <span :class="getRequestStatusClass(request.status)">{{ request.status }}</span>
            </div>
            <div class="text-xs text-gray-500 mt-1">
              Requested: {{ formatDate(request.requested_at) }}
              <span v-if="request.processed_at">
                · Processed: {{ formatDate(request.processed_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payout Method Status -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Payout Method</h2>
      <div class="flex items-center justify-between">
        <div>
          <div class="text-sm text-gray-600">
            Verification Status:
            <span :class="paymentStatus?.summary?.has_verified_payout_method ? 'text-green-600 font-medium' : 'text-yellow-600 font-medium'">
              {{ paymentStatus?.summary?.has_verified_payout_method ? 'Verified ✓' : 'Not Verified' }}
            </span>
          </div>
          <div class="text-xs text-gray-500 mt-1">
            Payment Schedule: {{ paymentStatus?.summary?.payment_schedule || 'N/A' }}
          </div>
        </div>
        <router-link
          to="/writer/payout-preferences"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
        >
          Manage Payout Method
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'

const props = defineProps({
  paymentStatus: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusColorClass = (status) => {
  const colors = {
    'Paid': 'bg-green-50 border-green-200',
    'Pending': 'bg-yellow-50 border-yellow-200',
    'Delayed': 'bg-orange-50 border-orange-200',
    'Blocked': 'bg-red-50 border-red-200',
    'Voided': 'bg-gray-50 border-gray-200',
  }
  return colors[status] || 'bg-gray-50 border-gray-200'
}

const getRequestStatusClass = (status) => {
  const classes = {
    'Pending': 'text-yellow-600 font-medium',
    'Approved': 'text-green-600 font-medium',
    'Rejected': 'text-red-600 font-medium',
  }
  return classes[status] || 'text-gray-600'
}

const paymentTrendsSeries = computed(() => {
  if (!props.paymentStatus?.payment_trends?.length) return []
  
  // Group by status
  const statuses = ['Paid', 'Pending', 'Delayed']
  return statuses.map(status => ({
    name: status,
    data: props.paymentStatus.payment_trends
      .filter(t => t.status === status)
      .map(t => parseFloat(t.total_amount || 0))
  })).filter(series => series.data.length > 0)
})

const paymentTrendsOptions = computed(() => ({
  chart: {
    type: 'line',
    toolbar: { show: false },
    zoom: { enabled: false }
  },
  xaxis: {
    categories: props.paymentStatus?.payment_trends
      ?.map(t => {
        if (t.week) {
          const date = new Date(t.week)
          return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }
        return ''
      })
      .filter(Boolean) || [],
    labels: { rotate: -45 }
  },
  yaxis: {
    title: { text: 'Amount ($)' }
  },
  stroke: { curve: 'smooth', width: 2 },
  colors: ['#10B981', '#F59E0B', '#EF4444'],
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  }
}))
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

