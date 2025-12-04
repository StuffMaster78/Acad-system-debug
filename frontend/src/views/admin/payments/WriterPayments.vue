<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4">
    <PageHeader
      title="Writer Payments"
      subtitle="Writer payments grouped by bi-weekly and monthly periods"
      @refresh="loadPayments"
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card">
        <div class="text-sm text-gray-500">Total Bi-Weekly</div>
        <div class="text-2xl font-bold text-primary-600">
          ${{ summary.total_biweekly_amount.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ summary.total_biweekly_payments }} payments</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Total Monthly</div>
        <div class="text-2xl font-bold text-primary-600">
          ${{ summary.total_monthly_amount.toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">{{ summary.total_monthly_payments }} payments</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Total Amount</div>
        <div class="text-2xl font-bold text-green-600">
          ${{ (summary.total_biweekly_amount + summary.total_monthly_amount).toFixed(2) }}
        </div>
        <div class="text-xs text-gray-400">
          {{ summary.total_biweekly_payments + summary.total_monthly_payments }} total payments
        </div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-500">Periods</div>
        <div class="text-2xl font-bold text-blue-600">
          {{ biweeklyPayments.length + monthlyPayments.length }}
        </div>
        <div class="text-xs text-gray-400">payment periods</div>
      </div>
    </div>

    <div class="bg-white p-4 rounded-lg shadow border border-gray-200 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select
            v-model="filters.website_id"
            class="w-full border rounded px-3 py-2 text-sm"
            @change="loadPayments"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Period Type</label>
          <select
            v-model="filters.period_type"
            class="w-full border rounded px-3 py-2 text-sm"
            @change="loadPayments"
          >
            <option value="both">Both Periods</option>
            <option value="biweekly">Bi-Weekly Only</option>
            <option value="monthly">Monthly Only</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            class="w-full border rounded px-3 py-2 text-sm"
            @change="loadPayments"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            class="w-full border rounded px-3 py-2 text-sm"
            @change="loadPayments"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Bi-Weekly Payments -->
      <div v-if="filters.period_type === 'both' || filters.period_type === 'biweekly'">
        <h2 class="text-xl font-bold mb-4">Bi-Weekly Payments</h2>
        <div v-if="loading" class="text-center py-8 text-gray-500">Loading...</div>
        <div v-else-if="biweeklyPayments.length === 0" class="text-center py-8 text-gray-500">
          No bi-weekly payments found
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="period in biweeklyPayments"
            :key="period.schedule_id"
            class="card border border-gray-200 hover:border-primary-300 transition-colors"
          >
            <div 
              class="flex items-center justify-between mb-4 cursor-pointer"
              @click="togglePeriod(period.schedule_id)"
            >
              <div class="flex items-center gap-3">
                <span class="text-xl">{{ expandedPeriods[period.schedule_id] ? '▼' : '▶' }}</span>
                <div>
                  <h3 class="font-semibold text-lg">
                    {{ new Date(period.scheduled_date).toLocaleDateString() }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    Reference: {{ period.reference_code }} | 
                    {{ period.writer_count }} writers | 
                    Status: {{ period.completed ? 'Completed' : 'Pending' }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-primary-600">
                  ${{ period.total_amount.toFixed(2) }}
                </div>
                <div class="text-xs text-gray-400">Total Amount</div>
              </div>
            </div>
            <div v-if="expandedPeriods[period.schedule_id] && period.payments.length > 0" class="mt-4 border-t pt-4">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-2 text-left">Writer</th>
                      <th class="px-4 py-2 text-right">Amount</th>
                      <th class="px-4 py-2 text-right">Tips</th>
                      <th class="px-4 py-2 text-right">Fines</th>
                      <th class="px-4 py-2 text-right">Total</th>
                      <th class="px-4 py-2 text-center">Status</th>
                      <th class="px-4 py-2 text-left">Reference</th>
                      <th class="px-4 py-2 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y">
                    <tr 
                      v-for="payment in period.payments" 
                      :key="payment.id"
                      class="hover:bg-gray-50 cursor-pointer"
                      @click="viewPaymentDetails(payment)"
                    >
                      <td class="px-4 py-2">
                        <div class="font-medium">{{ payment.writer.full_name || payment.writer.username }}</div>
                        <div class="text-xs text-gray-500">{{ payment.writer.email }}</div>
                        <div class="text-xs text-gray-400">{{ payment.writer.registration_id }}</div>
                      </td>
                      <td class="px-4 py-2 text-right font-medium">
                        ${{ payment.amount.toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right text-green-600">
                        ${{ (payment.tips || 0).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right text-red-600">
                        ${{ (payment.fines || 0).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right font-bold">
                        ${{ (payment.total_earnings || payment.amount).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-center">
                        <span
                          :class="[
                            'px-2 py-1 rounded text-xs',
                            payment.status === 'Paid'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-yellow-100 text-yellow-700',
                          ]"
                        >
                          {{ payment.status }}
                        </span>
                      </td>
                      <td class="px-4 py-2 text-xs text-gray-500 font-mono">
                        {{ payment.reference_code }}
                      </td>
                      <td class="px-4 py-2 text-center">
                        <button
                          @click.stop="viewPaymentDetails(payment)"
                          class="text-blue-600 hover:text-blue-800 text-xs font-medium"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Payments -->
      <div v-if="filters.period_type === 'both' || filters.period_type === 'monthly'">
        <h2 class="text-xl font-bold mb-4">Monthly Payments</h2>
        <div v-if="loading" class="text-center py-8 text-gray-500">Loading...</div>
        <div v-else-if="monthlyPayments.length === 0" class="text-center py-8 text-gray-500">
          No monthly payments found
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="period in monthlyPayments"
            :key="period.schedule_id"
            class="card border border-gray-200 hover:border-primary-300 transition-colors"
          >
            <div 
              class="flex items-center justify-between mb-4 cursor-pointer"
              @click="togglePeriod(period.schedule_id)"
            >
              <div class="flex items-center gap-3">
                <span class="text-xl">{{ expandedPeriods[period.schedule_id] ? '▼' : '▶' }}</span>
                <div>
                  <h3 class="font-semibold text-lg">
                    {{ new Date(period.scheduled_date).toLocaleDateString() }}
                  </h3>
                  <p class="text-sm text-gray-500">
                    Reference: {{ period.reference_code }} | 
                    {{ period.writer_count }} writers | 
                    Status: {{ period.completed ? 'Completed' : 'Pending' }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <div class="text-2xl font-bold text-primary-600">
                  ${{ period.total_amount.toFixed(2) }}
                </div>
                <div class="text-xs text-gray-400">Total Amount</div>
              </div>
            </div>
            <div v-if="expandedPeriods[period.schedule_id] && period.payments.length > 0" class="mt-4 border-t pt-4">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-2 text-left">Writer</th>
                      <th class="px-4 py-2 text-right">Amount</th>
                      <th class="px-4 py-2 text-right">Tips</th>
                      <th class="px-4 py-2 text-right">Fines</th>
                      <th class="px-4 py-2 text-right">Total</th>
                      <th class="px-4 py-2 text-center">Status</th>
                      <th class="px-4 py-2 text-left">Reference</th>
                      <th class="px-4 py-2 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y">
                    <tr 
                      v-for="payment in period.payments" 
                      :key="payment.id"
                      class="hover:bg-gray-50 cursor-pointer"
                      @click="viewPaymentDetails(payment)"
                    >
                      <td class="px-4 py-2">
                        <div class="font-medium">{{ payment.writer.full_name || payment.writer.username }}</div>
                        <div class="text-xs text-gray-500">{{ payment.writer.email }}</div>
                        <div class="text-xs text-gray-400">{{ payment.writer.registration_id }}</div>
                      </td>
                      <td class="px-4 py-2 text-right font-medium">
                        ${{ payment.amount.toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right text-green-600">
                        ${{ (payment.tips || 0).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right text-red-600">
                        ${{ (payment.fines || 0).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-right font-bold">
                        ${{ (payment.total_earnings || payment.amount).toFixed(2) }}
                      </td>
                      <td class="px-4 py-2 text-center">
                        <span
                          :class="[
                            'px-2 py-1 rounded text-xs',
                            payment.status === 'Paid'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-yellow-100 text-yellow-700',
                          ]"
                        >
                          {{ payment.status }}
                        </span>
                      </td>
                      <td class="px-4 py-2 text-xs text-gray-500 font-mono">
                        {{ payment.reference_code }}
                      </td>
                      <td class="px-4 py-2 text-center">
                        <button
                          @click.stop="viewPaymentDetails(payment)"
                          class="text-blue-600 hover:text-blue-800 text-xs font-medium"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Details Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showPaymentModal = false">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold">Payment Details</h3>
            <button @click="showPaymentModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div v-if="breakdownLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="selectedPayment" class="space-y-6">
            <!-- Payment Summary -->
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Payment ID:</span>
                  <div class="font-mono font-medium">{{ selectedPayment.reference_code }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Writer:</span>
                  <div class="font-medium">{{ selectedPayment.writer.full_name || selectedPayment.writer.username }}</div>
                  <div class="text-xs text-gray-500">{{ selectedPayment.writer.registration_id }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <div>
                    <span
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-medium',
                        selectedPayment.status === 'Paid'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800',
                      ]"
                    >
                      {{ selectedPayment.status }}
                    </span>
                  </div>
                </div>
                <div>
                  <span class="text-gray-600">Date:</span>
                  <div class="font-medium">{{ selectedPayment.payment_date ? new Date(selectedPayment.payment_date).toLocaleDateString() : 'N/A' }}</div>
                </div>
              </div>
            </div>

            <!-- Amount Breakdown -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm text-blue-700 mb-1">Base Amount</div>
                <div class="text-2xl font-bold text-blue-900">${{ selectedPayment.amount.toFixed(2) }}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm text-green-700 mb-1">Tips</div>
                <div class="text-2xl font-bold text-green-900">${{ (selectedPayment.tips || 0).toFixed(2) }}</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="text-sm text-red-700 mb-1">Fines</div>
                <div class="text-2xl font-bold text-red-900">${{ (selectedPayment.fines || 0).toFixed(2) }}</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div class="text-sm text-purple-700 mb-1">Total Earnings</div>
                <div class="text-2xl font-bold text-purple-900">${{ (selectedPayment.total_earnings || selectedPayment.amount).toFixed(2) }}</div>
              </div>
            </div>

            <!-- Orders -->
            <div v-if="paymentBreakdown && paymentBreakdown.orders && paymentBreakdown.orders.length > 0">
              <h4 class="text-lg font-semibold mb-3">Orders ({{ paymentBreakdown.orders.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="order in paymentBreakdown.orders" :key="order.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-mono">#{{ order.id }}</td>
                      <td class="px-4 py-3 text-sm">{{ order.topic || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm font-medium">${{ (order.amount_paid || 0).toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else-if="selectedPayment.order_ids && selectedPayment.order_ids.length > 0">
              <h4 class="text-lg font-semibold mb-3">Orders ({{ selectedPayment.order_ids.length }})</h4>
              <div class="text-sm text-gray-600">
                Order IDs: {{ selectedPayment.order_ids.join(', ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Details Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showPaymentModal = false">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold">Payment Details</h3>
            <button @click="showPaymentModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div v-if="breakdownLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="selectedPayment" class="space-y-6">
            <!-- Payment Summary -->
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Payment ID:</span>
                  <div class="font-mono font-medium">{{ selectedPayment.reference_code }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Writer:</span>
                  <div class="font-medium">{{ selectedPayment.writer.full_name || selectedPayment.writer.username }}</div>
                  <div class="text-xs text-gray-500">{{ selectedPayment.writer.registration_id }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <div>
                    <span
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-medium',
                        selectedPayment.status === 'Paid'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800',
                      ]"
                    >
                      {{ selectedPayment.status }}
                    </span>
                  </div>
                </div>
                <div>
                  <span class="text-gray-600">Date:</span>
                  <div class="font-medium">{{ selectedPayment.payment_date ? new Date(selectedPayment.payment_date).toLocaleDateString() : 'N/A' }}</div>
                </div>
              </div>
            </div>

            <!-- Amount Breakdown -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm text-blue-700 mb-1">Base Amount</div>
                <div class="text-2xl font-bold text-blue-900">${{ selectedPayment.amount.toFixed(2) }}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm text-green-700 mb-1">Tips</div>
                <div class="text-2xl font-bold text-green-900">${{ (selectedPayment.tips || 0).toFixed(2) }}</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="text-sm text-red-700 mb-1">Fines</div>
                <div class="text-2xl font-bold text-red-900">${{ (selectedPayment.fines || 0).toFixed(2) }}</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div class="text-sm text-purple-700 mb-1">Total Earnings</div>
                <div class="text-2xl font-bold text-purple-900">${{ (selectedPayment.total_earnings || selectedPayment.amount).toFixed(2) }}</div>
              </div>
            </div>

            <!-- Orders -->
            <div v-if="paymentBreakdown && paymentBreakdown.orders && paymentBreakdown.orders.length > 0">
              <h4 class="text-lg font-semibold mb-3">Orders ({{ paymentBreakdown.orders.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="order in paymentBreakdown.orders" :key="order.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-mono">#{{ order.id }}</td>
                      <td class="px-4 py-3 text-sm">{{ order.topic || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm font-medium">${{ (order.amount_paid || 0).toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else-if="selectedPayment.order_ids && selectedPayment.order_ids.length > 0">
              <h4 class="text-lg font-semibold mb-3">Orders ({{ selectedPayment.order_ids.length }})</h4>
              <div class="text-sm text-gray-600">
                Order IDs: {{ selectedPayment.order_ids.join(', ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'

const loading = ref(false)
const biweeklyPayments = ref([])
const monthlyPayments = ref([])
const summary = ref({
  total_biweekly_amount: 0,
  total_monthly_amount: 0,
  total_biweekly_payments: 0,
  total_monthly_payments: 0,
})
const websites = ref([])
const expandedPeriods = ref({})
const showPaymentModal = ref(false)
const selectedPayment = ref(null)
const paymentBreakdown = ref(null)
const breakdownLoading = ref(false)
const filters = ref({
  website_id: '',
  period_type: 'both',
  date_from: '',
  date_to: '',
})

const loadPayments = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.website_id) params.website_id = filters.value.website_id
    if (filters.value.period_type) params.period_type = filters.value.period_type
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to

    const res = await paymentsAPI.getWriterPaymentsGrouped(params)
    biweeklyPayments.value = res.data.biweekly || []
    monthlyPayments.value = res.data.monthly || []
    summary.value = res.data.summary || {
      total_biweekly_amount: 0,
      total_monthly_amount: 0,
      total_biweekly_payments: 0,
      total_monthly_payments: 0,
    }
  } catch (e) {
    console.error('Failed to load payments:', e)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const updateFilter = (key, value) => {
  filters.value[key] = value
  loadPayments()
}

const clearFilters = () => {
  filters.value = {
    website_id: '',
    period_type: 'both',
    date_from: '',
    date_to: '',
  }
  loadPayments()
}

const togglePeriod = (scheduleId) => {
  expandedPeriods.value[scheduleId] = !expandedPeriods.value[scheduleId]
}

const viewPaymentDetails = async (payment) => {
  selectedPayment.value = payment
  showPaymentModal.value = true
  breakdownLoading.value = true
  
  try {
    const response = await paymentsAPI.getPaymentBreakdown(payment.id)
    paymentBreakdown.value = response.data
  } catch (error) {
    console.error('Failed to load payment breakdown:', error)
    paymentBreakdown.value = null
  } finally {
    breakdownLoading.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadPayments(), loadWebsites()])
})
</script>

<style scoped>
@reference "tailwindcss";
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

