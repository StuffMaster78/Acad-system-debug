<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Payment Management</h1>
        <p class="mt-2 text-gray-600">Manage writer payments, requests, and reconciliation</p>
      </div>
      <div class="flex gap-2">
        <router-link
          to="/admin/payments/all"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
        >
          All Payments
        </router-link>
        <router-link
          to="/admin/financial-overview"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Financial Overview
        </router-link>
        <button
          v-if="(authStore.isAdmin || authStore.isSuperAdmin) && activeTab === 'payments'"
          @click="showClearModal = true"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Mark All as Paid
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'payments'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'payments'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Payments
        </button>
        <button
          @click="activeTab = 'requests'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'requests'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Payment Requests
        </button>
        <button
          @click="activeTab = 'reconciliation'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'reconciliation'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Reconciliation
        </button>
      </nav>
    </div>

    <!-- Payments Tab -->
    <div v-if="activeTab === 'payments'">

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Period Type</label>
          <select v-model="filters.period_type" @change="loadPayments" class="w-full border rounded px-3 py-2">
            <option value="both">All Periods</option>
            <option value="biweekly">Bi-Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadPayments"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            @change="loadPayments"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div v-if="summary" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Bi-Weekly</p>
        <p class="text-3xl font-bold text-blue-900">${{ formatCurrency(summary.total_biweekly_amount || 0) }}</p>
        <p class="text-xs text-blue-600 mt-1">{{ summary.total_biweekly_payments || 0 }} payments</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Total Monthly</p>
        <p class="text-3xl font-bold text-green-900">${{ formatCurrency(summary.total_monthly_amount || 0) }}</p>
        <p class="text-xs text-green-600 mt-1">{{ summary.total_monthly_payments || 0 }} payments</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Amount</p>
        <p class="text-3xl font-bold text-purple-900">${{ formatCurrency((summary.total_biweekly_amount || 0) + (summary.total_monthly_amount || 0)) }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Total Payments</p>
        <p class="text-3xl font-bold text-orange-900">{{ (summary.total_biweekly_payments || 0) + (summary.total_monthly_payments || 0) }}</p>
      </div>
    </div>

    <!-- Bi-Weekly Payments -->
    <div v-if="biweeklyPayments.length > 0" class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold">Bi-Weekly Payments</h2>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="period in biweeklyPayments"
          :key="period.schedule_id"
          class="transition-colors"
        >
          <!-- Period Header (Clickable) -->
          <div
            @click="togglePeriod(period.schedule_id)"
            class="px-6 py-4 cursor-pointer hover:bg-gray-50 flex items-center justify-between"
          >
            <div class="flex-1 grid grid-cols-6 gap-4 items-center">
              <div>
                <div class="font-medium text-gray-900">{{ period.reference_code }}</div>
                <div class="text-xs text-gray-500">{{ formatDate(period.scheduled_date) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Writers</div>
                <div class="font-medium">{{ period.writer_count }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Orders</div>
                <div class="font-medium">{{ period.total_orders }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Amount</div>
                <div class="font-medium">${{ formatCurrency(period.total_amount) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Status</div>
                <div>
                  <span :class="period.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ period.completed ? 'Completed' : 'Pending' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  v-if="!period.completed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                  @click.stop="markPeriodAsPaid(period.schedule_id)"
                  :disabled="markingAsPaid"
                  class="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {{ markingAsPaid ? 'Processing...' : 'Mark All as Paid' }}
                </button>
                <span class="text-lg">{{ expandedPeriods[period.schedule_id] ? '▼' : '▶' }}</span>
              </div>
            </div>
          </div>

          <!-- Expanded Payment Details -->
          <div v-if="expandedPeriods[period.schedule_id]" class="bg-gray-50 px-6 py-4">
            <div class="mb-4 grid grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Total Tips:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_tips || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Total Fines:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_fines || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Total Earnings:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_earnings || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Processed By:</span>
                <span class="font-medium ml-2">{{ period.processed_by?.username || 'System' }}</span>
              </div>
            </div>

            <!-- Payments Table -->
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tips</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fines</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="payment in period.payments" :key="payment.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-mono">{{ payment.reference_code }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div>{{ payment.writer.full_name }}</div>
                    <div class="text-xs text-gray-500">{{ payment.writer.registration_id }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ payment.writer.email }}</td>
                  <td class="px-4 py-3 text-sm text-center">{{ payment.order_count }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm text-green-600">${{ formatCurrency(payment.tips || 0) }}</td>
                  <td class="px-4 py-3 text-sm text-red-600">${{ formatCurrency(payment.fines || 0) }}</td>
                  <td class="px-4 py-3 text-sm font-bold">${{ formatCurrency(payment.total_earnings || payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusClass(payment.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center gap-2 flex-wrap">
                      <button
                        @click="viewPaymentBreakdown(payment.id)"
                        class="text-blue-600 hover:underline text-xs"
                      >
                        View Details
                      </button>
                      <button
                        v-if="payment.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="markPaymentAsPaid(payment.id)"
                        :disabled="markingAsPaid"
                        class="text-green-600 hover:underline text-xs"
                      >
                        {{ markingAsPaid ? 'Processing...' : 'Mark as Paid' }}
                      </button>
                      <button
                        v-if="(authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="showMoveToNextPeriodModal(payment)"
                        class="text-purple-600 hover:underline text-xs"
                        :title="getAdjustmentReason(payment.id)"
                      >
                        Move to Next Period
                      </button>
                      <button
                        v-if="(authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="showAdjustOrderStatusModal(payment)"
                        class="text-orange-600 hover:underline text-xs"
                      >
                        Adjust for Order
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Payments -->
    <div v-if="monthlyPayments.length > 0" class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-xl font-semibold">Monthly Payments</h2>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="period in monthlyPayments"
          :key="period.schedule_id"
          class="transition-colors"
        >
          <!-- Period Header (Clickable) -->
          <div
            @click="togglePeriod(period.schedule_id)"
            class="px-6 py-4 cursor-pointer hover:bg-gray-50 flex items-center justify-between"
          >
            <div class="flex-1 grid grid-cols-6 gap-4 items-center">
              <div>
                <div class="font-medium text-gray-900">{{ period.reference_code }}</div>
                <div class="text-xs text-gray-500">{{ formatDate(period.scheduled_date) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Writers</div>
                <div class="font-medium">{{ period.writer_count }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Orders</div>
                <div class="font-medium">{{ period.total_orders }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Amount</div>
                <div class="font-medium">${{ formatCurrency(period.total_amount) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Status</div>
                <div>
                  <span :class="period.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ period.completed ? 'Completed' : 'Pending' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  v-if="!period.completed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                  @click.stop="markPeriodAsPaid(period.schedule_id)"
                  :disabled="markingAsPaid"
                  class="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {{ markingAsPaid ? 'Processing...' : 'Mark All as Paid' }}
                </button>
                <span class="text-lg">{{ expandedPeriods[period.schedule_id] ? '▼' : '▶' }}</span>
              </div>
            </div>
          </div>

          <!-- Expanded Payment Details -->
          <div v-if="expandedPeriods[period.schedule_id]" class="bg-gray-50 px-6 py-4">
            <div class="mb-4 grid grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Total Tips:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_tips || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Total Fines:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_fines || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Total Earnings:</span>
                <span class="font-medium ml-2">${{ formatCurrency(period.total_earnings || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-600">Processed By:</span>
                <span class="font-medium ml-2">{{ period.processed_by?.username || 'System' }}</span>
              </div>
            </div>

            <!-- Payments Table -->
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tips</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fines</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="payment in period.payments" :key="payment.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-mono">{{ payment.reference_code }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div>{{ payment.writer.full_name }}</div>
                    <div class="text-xs text-gray-500">{{ payment.writer.registration_id }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ payment.writer.email }}</td>
                  <td class="px-4 py-3 text-sm text-center">{{ payment.order_count }}</td>
                  <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm text-green-600">${{ formatCurrency(payment.tips || 0) }}</td>
                  <td class="px-4 py-3 text-sm text-red-600">${{ formatCurrency(payment.fines || 0) }}</td>
                  <td class="px-4 py-3 text-sm font-bold">${{ formatCurrency(payment.total_earnings || payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusClass(payment.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center gap-2">
                      <button
                        @click="viewPaymentBreakdown(payment.id)"
                        class="text-blue-600 hover:underline"
                      >
                        View Details
                      </button>
                      <button
                        v-if="payment.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                        @click="markPaymentAsPaid(payment.id)"
                        :disabled="markingAsPaid"
                        class="text-green-600 hover:underline text-xs"
                      >
                        {{ markingAsPaid ? 'Processing...' : 'Mark as Paid' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-if="!loading && biweeklyPayments.length === 0 && monthlyPayments.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <p class="text-gray-500 text-lg">No payment periods found</p>
      </div>
    </div>

    <!-- Payment Breakdown Modal -->
    <div v-if="showBreakdownModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold">Payment Breakdown</h3>
            <button @click="showBreakdownModal = false" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div v-if="breakdownLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="paymentBreakdown" class="space-y-6">
            <!-- Batch Summary (for batch breakdown) -->
            <div v-if="paymentBreakdown.writers" class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Batch Reference:</span>
                  <div class="font-mono font-medium">{{ paymentBreakdown.reference_code }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Schedule Type:</span>
                  <div class="font-medium">{{ paymentBreakdown.schedule_type }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Scheduled Date:</span>
                  <div class="font-medium">{{ formatDate(paymentBreakdown.scheduled_date) }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <div>
                    <span :class="paymentBreakdown.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ paymentBreakdown.completed ? 'Completed' : 'Pending' }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Total Writers:</span>
                  <div class="font-medium text-lg">{{ paymentBreakdown.total_writers }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Total Amount:</span>
                  <div class="font-medium text-lg text-green-600">${{ formatCurrency(paymentBreakdown.total_amount) }}</div>
                </div>
              </div>
            </div>
            
            <!-- Payment Summary (for individual payment breakdown) -->
            <div v-else class="bg-gray-50 rounded-lg p-4">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Payment ID:</span>
                  <div class="font-mono font-medium">{{ paymentBreakdown.reference_code }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Writer:</span>
                  <div class="font-medium">{{ paymentBreakdown.writer?.full_name || 'N/A' }}</div>
                  <div class="text-xs text-gray-500">{{ paymentBreakdown.writer?.registration_id || '' }}</div>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <div>
                    <span :class="getStatusClass(paymentBreakdown.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ paymentBreakdown.status }}
                    </span>
                  </div>
                </div>
                <div>
                  <span class="text-gray-600">Date:</span>
                  <div class="font-medium">{{ formatDateTime(paymentBreakdown.payment_date) }}</div>
                </div>
              </div>
            </div>

            <!-- Summary Stats -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm text-blue-700 mb-1">Total Orders</div>
                <div class="text-2xl font-bold text-blue-900">{{ paymentBreakdown.summary.total_orders }}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm text-green-700 mb-1">Total Tips</div>
                <div class="text-2xl font-bold text-green-900">${{ formatCurrency(paymentBreakdown.summary.total_tips) }}</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="text-sm text-red-700 mb-1">Total Fines</div>
                <div class="text-2xl font-bold text-red-900">${{ formatCurrency(paymentBreakdown.summary.total_fines) }}</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div class="text-sm text-purple-700 mb-1">Net Earnings</div>
                <div class="text-2xl font-bold text-purple-900">${{ formatCurrency(paymentBreakdown.summary.net_earnings) }}</div>
              </div>
            </div>

            <!-- Writers (for batch breakdown) -->
            <div v-if="paymentBreakdown.writers">
              <h4 class="text-lg font-semibold mb-3">Writers ({{ paymentBreakdown.writers.length }})</h4>
              <div class="space-y-4">
                <div v-for="writer in paymentBreakdown.writers" :key="writer.writer_id" class="bg-white border rounded-lg p-4">
                  <div class="flex items-center justify-between mb-3">
                    <div>
                      <div class="font-medium text-lg">{{ writer.writer_name }}</div>
                      <div class="text-sm text-gray-500">{{ writer.writer_email }}</div>
                      <div class="text-xs text-gray-400">{{ writer.registration_id }}</div>
                    </div>
                    <div class="text-right">
                      <div class="text-sm text-gray-600">Total Amount</div>
                      <div class="text-xl font-bold text-green-600">${{ formatCurrency(writer.total_amount) }}</div>
                      <div>
                        <span :class="getStatusClass(writer.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                          {{ writer.status }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-3 gap-4 mb-3 text-sm">
                    <div>
                      <span class="text-gray-600">Orders:</span>
                      <span class="font-medium ml-2">{{ writer.orders_count }}</span>
                    </div>
                    <div>
                      <span class="text-gray-600">Tips:</span>
                      <span class="font-medium text-green-600 ml-2">${{ formatCurrency(writer.tips) }}</span>
                    </div>
                    <div>
                      <span class="text-gray-600">Fines:</span>
                      <span class="font-medium text-red-600 ml-2">${{ formatCurrency(writer.fines) }}</span>
                    </div>
                  </div>
                  
                  <div v-if="writer.orders && writer.orders.length > 0" class="mt-3">
                    <div class="text-xs font-medium text-gray-600 mb-2">Order Breakdown:</div>
                    <div class="space-y-1">
                      <div v-for="order in writer.orders" :key="order.order_id" class="flex items-center justify-between text-xs bg-gray-50 px-2 py-1 rounded">
                        <div>
                          <span class="font-medium">Order #{{ order.order_id }}</span>
                          <span class="text-gray-500 ml-2">{{ order.order_topic }}</span>
                        </div>
                        <div class="font-medium">${{ formatCurrency(order.amount) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Orders (for individual payment breakdown) -->
            <div v-else>
              <h4 class="text-lg font-semibold mb-3">Orders ({{ paymentBreakdown.orders?.length || 0 }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completed</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="order in paymentBreakdown.orders" :key="order.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-mono">#{{ order.id }}</td>
                      <td class="px-4 py-3 text-sm">{{ order.topic || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm">
                        <span :class="getStatusClass(order.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                          {{ order.status }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(order.amount_paid) }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(order.completed_at) }}</td>
                      <td class="px-4 py-3 text-sm">
                        <router-link
                          :to="`/orders/${order.id}`"
                          class="text-blue-600 hover:underline"
                        >
                          View
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Tips -->
            <div v-if="paymentBreakdown.tips && paymentBreakdown.tips.length > 0">
              <h4 class="text-lg font-semibold mb-3">Tips ({{ paymentBreakdown.tips.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="tip in paymentBreakdown.tips" :key="tip.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-medium text-green-600">${{ formatCurrency(tip.amount) }}</td>
                      <td class="px-4 py-3 text-sm">
                        <router-link
                          v-if="tip.order_id"
                          :to="`/orders/${tip.order_id}`"
                          class="text-blue-600 hover:underline"
                        >
                          #{{ tip.order_id }}
                        </router-link>
                        <span v-else class="text-gray-400">Direct Tip</span>
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ tip.reason || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(tip.sent_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Fines -->
            <div v-if="paymentBreakdown.fines && paymentBreakdown.fines.length > 0">
              <h4 class="text-lg font-semibold mb-3">Fines ({{ paymentBreakdown.fines.length }})</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="fine in paymentBreakdown.fines" :key="fine.id" class="hover:bg-gray-50">
                      <td class="px-4 py-3 text-sm font-medium text-red-600">${{ formatCurrency(fine.amount) }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ fine.fine_type || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ fine.reason || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(fine.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Requests Tab -->
    <div v-if="activeTab === 'requests'" class="space-y-4">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-semibold">Payout Requests</h2>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="request in payoutRequests" :key="request.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm">
                  <div>{{ request.writer.name }}</div>
                  <div class="text-xs text-gray-500">{{ request.writer.email }}</div>
                </td>
                <td class="px-4 py-3 text-sm font-medium">${{ formatCurrency(request.amount_requested) }}</td>
                <td class="px-4 py-3 text-sm">
                  <span :class="getStatusClass(request.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ request.status }}
                  </span>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(request.requested_at) }}</td>
                <td class="px-4 py-3 text-sm">
                  <button
                    v-if="request.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin)"
                    @click="approvePayoutRequest(request.id)"
                    class="text-green-600 hover:underline text-xs"
                  >
                    Approve
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Reconciliation Tab -->
    <div v-if="activeTab === 'reconciliation'" class="space-y-4">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold mb-4">Payment Adjustments</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment ID</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Adjustment</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Admin</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="adj in adjustments" :key="adj.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-sm font-mono">#{{ adj.payment_id }}</td>
                <td class="px-4 py-3 text-sm">{{ adj.writer.name }}</td>
                <td class="px-4 py-3 text-sm" :class="parseFloat(adj.adjustment_amount) < 0 ? 'text-red-600' : 'text-green-600'">
                  ${{ formatCurrency(adj.adjustment_amount) }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ adj.reason }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ adj.admin }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(adj.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Move to Next Period Modal -->
    <div v-if="showMoveModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Move Payment to Next Period</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Reason (required)</label>
            <textarea
              v-model="moveReason"
              class="w-full border rounded px-3 py-2"
              rows="3"
              placeholder="Enter reason for moving this payment..."
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Target Period Type</label>
            <select v-model="targetPeriodType" class="w-full border rounded px-3 py-2">
              <option value="">Same as current</option>
              <option value="biweekly">Bi-Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="showMoveModal = false" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
              Cancel
            </button>
            <button @click="moveToNextPeriod" class="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
              Move Payment
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Adjust for Order Status Modal -->
    <div v-if="showAdjustModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Adjust Payment for Order Status</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Order Status</label>
            <select v-model="orderStatus" class="w-full border rounded px-3 py-2">
              <option value="">Select status...</option>
              <option value="disputed">Disputed</option>
              <option value="cancelled">Cancelled</option>
              <option value="revision_requested">Revision Requested</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Additional Reason (optional)</label>
            <textarea
              v-model="adjustReason"
              class="w-full border rounded px-3 py-2"
              rows="3"
              placeholder="Enter additional reason..."
            ></textarea>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="showAdjustModal = false" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
              Cancel
            </button>
            <button @click="adjustForOrderStatus" class="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
              Adjust Payment
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mark All as Paid Modal (Clear Payments) -->
    <div v-if="showClearModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Mark Payments as Paid</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Clear Options</label>
            <select v-model="clearOption" class="w-full border rounded px-3 py-2">
              <option value="all">All Writers</option>
              <option value="writer">Specific Writer</option>
              <option value="selected">Selected Payments</option>
            </select>
          </div>
          <div v-if="clearOption === 'writer'">
            <label class="block text-sm font-medium mb-1">Writer ID</label>
            <input v-model="clearWriterId" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="bg-blue-50 border border-blue-200 rounded p-3">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> "Clear Payments" will mark all selected payments as paid. This action cannot be undone.
            </p>
          </div>
          <div class="flex gap-2 justify-end">
            <button @click="showClearModal = false" class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">
              Cancel
            </button>
            <button @click="clearPayments" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              Mark as Paid
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import apiClient from '@/api/client'
import writerPaymentsAPI from '@/api/writer-payments'
import paymentsAPI from '@/api/payments'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const activeTab = ref('payments')
const loading = ref(false)
const biweeklyPayments = ref([])
const monthlyPayments = ref([])
const summary = ref(null)
const expandedPeriods = ref({})
const showBreakdownModal = ref(false)
const paymentBreakdown = ref(null)
const breakdownLoading = ref(false)
const markingAsPaid = ref(false)
const payoutRequests = ref([])
const adjustments = ref([])
const showMoveModal = ref(false)
const showAdjustModal = ref(false)
const showClearModal = ref(false)
const selectedPayment = ref(null)
const moveReason = ref('')
const targetPeriodType = ref('')
const orderStatus = ref('')
const adjustReason = ref('')
const clearOption = ref('all')
const clearWriterId = ref('')
const markAsPaid = ref(true)

const filters = ref({
  period_type: 'both',
  date_from: '',
  date_to: '',
})

const loadPayments = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.period_type !== 'both') {
      params.period_type = filters.value.period_type
    }
    if (filters.value.date_from) {
      params.date_from = filters.value.date_from
    }
    if (filters.value.date_to) {
      params.date_to = filters.value.date_to
    }

    const response = await apiClient.get('/writer-wallet/writer-payments/grouped/', { params })
    biweeklyPayments.value = response.data.biweekly || []
    monthlyPayments.value = response.data.monthly || []
    summary.value = response.data.summary || {}
  } catch (error) {
    console.error('Failed to load payments:', error)
  } finally {
    loading.value = false
  }
}

const togglePeriod = (scheduleId) => {
  expandedPeriods.value[scheduleId] = !expandedPeriods.value[scheduleId]
}

const viewBatchBreakdown = async (scheduleId) => {
  breakdownLoading.value = true
  showBreakdownModal.value = true
  try {
    const response = await paymentsAPI.getBatchBreakdown(scheduleId)
    paymentBreakdown.value = response.data
  } catch (error) {
    console.error('Failed to load batch breakdown:', error)
    alert('Failed to load batch breakdown: ' + (error.response?.data?.detail || error.message))
  } finally {
    breakdownLoading.value = false
  }
}

const viewPaymentBreakdown = async (paymentId) => {
  breakdownLoading.value = true
  showBreakdownModal.value = true
  try {
    const response = await apiClient.get(`/writer-wallet/scheduled-payments/${paymentId}/breakdown/`)
    paymentBreakdown.value = response.data
  } catch (error) {
    console.error('Failed to load payment breakdown:', error)
    alert('Failed to load payment breakdown: ' + (error.response?.data?.detail || error.message))
  } finally {
    breakdownLoading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    period_type: 'both',
    date_from: '',
    date_to: '',
  }
  loadPayments()
}

const markPaymentAsPaid = async (paymentId) => {
  if (!confirm('Are you sure you want to mark this payment as paid?')) {
    return
  }
  
  markingAsPaid.value = true
  try {
    await apiClient.post(`/writer-wallet/scheduled-payments/${paymentId}/mark-as-paid/`)
    alert('Payment marked as paid successfully!')
    await loadPayments()
  } catch (error) {
    console.error('Failed to mark payment as paid:', error)
    alert('Failed to mark payment as paid: ' + (error.response?.data?.error || error.message))
  } finally {
    markingAsPaid.value = false
  }
}

const markPeriodAsPaid = async (scheduleId) => {
  if (!confirm('Are you sure you want to mark all payments in this period as paid?')) {
    return
  }
  
  markingAsPaid.value = true
  try {
    await apiClient.post('/writer-wallet/scheduled-payments/bulk-mark-as-paid/', {
      schedule_id: scheduleId
    })
    alert('All payments in this period have been marked as paid!')
    await loadPayments()
  } catch (error) {
    console.error('Failed to mark payments as paid:', error)
    alert('Failed to mark payments as paid: ' + (error.response?.data?.error || error.message))
  } finally {
    markingAsPaid.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const getStatusClass = (status) => {
  const statusMap = {
    'Paid': 'bg-green-100 text-green-800',
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Blocked': 'bg-red-100 text-red-800',
    'Delayed': 'bg-orange-100 text-orange-800',
    'Voided': 'bg-gray-100 text-gray-800',
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

const showMoveToNextPeriodModal = (payment) => {
  selectedPayment.value = payment
  moveReason.value = ''
  targetPeriodType.value = ''
  showMoveModal.value = true
}

const moveToNextPeriod = async () => {
  if (!moveReason.value.trim()) {
    alert('Please enter a reason')
    return
  }

  try {
    const response = await writerPaymentsAPI.moveToNextPeriod(selectedPayment.value.id, {
      reason: moveReason.value,
      target_period_type: targetPeriodType.value || null
    })
    alert(response.data.message)
    showMoveModal.value = false
    await loadPayments()
    await loadAdjustments()
  } catch (error) {
    console.error('Failed to move payment:', error)
    alert('Failed to move payment: ' + (error.response?.data?.error || error.message))
  }
}

const showAdjustOrderStatusModal = (payment) => {
  selectedPayment.value = payment
  orderStatus.value = ''
  adjustReason.value = ''
  showAdjustModal.value = true
}

const adjustForOrderStatus = async () => {
  if (!orderStatus.value) {
    alert('Please select an order status')
    return
  }

  try {
    const response = await writerPaymentsAPI.adjustForOrderStatus(selectedPayment.value.id, {
      order_status: orderStatus.value,
      reason: adjustReason.value
    })
    alert(response.data.message)
    showAdjustModal.value = false
    await loadPayments()
    await loadAdjustments()
  } catch (error) {
    console.error('Failed to adjust payment:', error)
    alert('Failed to adjust payment: ' + (error.response?.data?.error || error.message))
  }
}

const clearPayments = async () => {
  if (!confirm('Are you sure you want to mark these payments as paid? This action cannot be undone.')) {
    return
  }

  try {
    // Clear payments = Mark as paid (always)
    const data = { mark_as_paid: true }
    if (clearOption.value === 'writer' && clearWriterId.value) {
      data.writer_id = parseInt(clearWriterId.value)
    } else if (clearOption.value === 'selected') {
      // You can add selected payment IDs here
      data.payment_ids = []
    }

    const response = await writerPaymentsAPI.clearPayments(data)
    alert(response.data.message)
    showClearModal.value = false
    await loadPayments()
  } catch (error) {
    console.error('Failed to clear payments:', error)
    alert('Failed to clear payments: ' + (error.response?.data?.error || error.message))
  }
}

const loadPayoutRequests = async () => {
  try {
    const response = await writerPaymentsAPI.getPayoutRequests({})
    payoutRequests.value = response.data.results || []
  } catch (error) {
    console.error('Failed to load payout requests:', error)
  }
}

const approvePayoutRequest = async (payoutId) => {
  if (!confirm('Are you sure you want to approve this payout request?')) {
    return
  }

  try {
    await writerPaymentsAPI.approvePayout(payoutId)
    alert('Payout approved successfully!')
    await loadPayoutRequests()
  } catch (error) {
    console.error('Failed to approve payout:', error)
    alert('Failed to approve payout: ' + (error.response?.data?.error || error.message))
  }
}

const loadAdjustments = async () => {
  try {
    const response = await writerPaymentsAPI.getAdjustments({})
    adjustments.value = response.data.results || []
  } catch (error) {
    console.error('Failed to load adjustments:', error)
  }
}

const getAdjustmentReason = (paymentId) => {
  const adj = adjustments.value.find(a => a.payment_id === paymentId)
  return adj ? adj.reason : ''
}

onMounted(() => {
  loadPayments()
  loadPayoutRequests()
  loadAdjustments()
})
</script>

