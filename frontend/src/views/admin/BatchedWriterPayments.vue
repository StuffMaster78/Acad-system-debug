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
      <!-- Payment Type Sub-Tabs -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex space-x-6">
          <button
            @click="paymentTypeTab = 'all'"
            :class="[
              'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
              paymentTypeTab === 'all'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            All Payments
          </button>
          <button
            @click="paymentTypeTab = 'biweekly'"
            :class="[
              'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
              paymentTypeTab === 'biweekly'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Bi-Weekly Payments
          </button>
          <button
            @click="paymentTypeTab = 'monthly'"
            :class="[
              'py-3 px-1 border-b-2 font-medium text-sm transition-colors',
              paymentTypeTab === 'monthly'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Monthly Payments
          </button>
        </nav>
      </div>

    <!-- Filters -->
      <div class="bg-white rounded-lg shadow border border-gray-200 p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">Period Type</label>
          <select v-model="filters.period_type" @change="loadPayments" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            <option value="both">All Periods</option>
            <option value="biweekly">Bi-Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadPayments"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            @change="loadPayments"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full font-medium">Reset</button>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
      <div v-if="summary" :class="[
        'grid gap-4',
        paymentTypeTab === 'all' ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4' : 'grid-cols-1 sm:grid-cols-2'
      ]">
        <div v-if="paymentTypeTab === 'all' || paymentTypeTab === 'biweekly'" class="bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-blue-700 truncate">Total Bi-Weekly</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-blue-900 break-all leading-tight">${{ formatCurrency(summary.total_biweekly_amount || 0) }}</p>
          <p class="text-xs text-blue-600">{{ summary.total_biweekly_payments || 0 }} payments</p>
      </div>
        <div v-if="paymentTypeTab === 'all' || paymentTypeTab === 'monthly'" class="bg-linear-to-br from-green-50 to-green-100 rounded-lg shadow border border-green-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-green-700 truncate">Total Monthly</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-green-900 break-all leading-tight">${{ formatCurrency(summary.total_monthly_amount || 0) }}</p>
          <p class="text-xs text-green-600">{{ summary.total_monthly_payments || 0 }} payments</p>
      </div>
        <div v-if="paymentTypeTab === 'all'" class="bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow border border-purple-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-purple-700 truncate">Total Amount</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-purple-900 break-all leading-tight">${{ formatCurrency((summary.total_biweekly_amount || 0) + (summary.total_monthly_amount || 0)) }}</p>
      </div>
        <div v-if="paymentTypeTab === 'all'" class="bg-linear-to-br from-orange-50 to-orange-100 rounded-lg shadow border border-orange-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-orange-700 truncate">Total Payments</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-orange-900 break-all leading-tight">{{ (summary.total_biweekly_payments || 0) + (summary.total_monthly_payments || 0) }}</p>
        </div>
        <div v-if="paymentTypeTab === 'biweekly'" class="bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow border border-purple-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-purple-700 truncate">Total Amount</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-purple-900 break-all leading-tight">${{ formatCurrency(summary.total_biweekly_amount || 0) }}</p>
        </div>
        <div v-if="paymentTypeTab === 'monthly'" class="bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow border border-purple-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-purple-700 truncate">Total Amount</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-purple-900 break-all leading-tight">${{ formatCurrency(summary.total_monthly_amount || 0) }}</p>
      </div>
    </div>

    <!-- Bi-Weekly Payments -->
      <div v-if="(paymentTypeTab === 'all' || paymentTypeTab === 'biweekly') && biweeklyPayments.length > 0" class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 bg-linear-to-r from-blue-50 to-blue-100">
          <h2 class="text-xl font-semibold text-blue-900">Bi-Weekly Payments</h2>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="period in biweeklyPayments"
          :key="period.schedule_id"
          class="transition-colors"
          :class="expandedPeriods[period.schedule_id] ? 'bg-blue-50/30' : ''"
        >
          <!-- Period Header (Clickable) -->
          <div
            @click="togglePeriod(period.schedule_id)"
            :class="[
              'px-6 py-4 cursor-pointer flex items-center justify-between transition-all duration-200',
              expandedPeriods[period.schedule_id] 
                ? 'bg-blue-50 border-l-4 border-blue-500 shadow-sm' 
                : 'hover:bg-blue-50/30 hover:border-l-4 hover:border-blue-300 border-l-4 border-transparent'
            ]"
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
                <div class="font-medium text-gray-900 break-all">${{ formatCurrency(period.total_amount) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Status</div>
                <div>
                  <span :class="period.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ period.completed ? 'Completed' : 'Pending' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2 justify-end">
                <button
                  v-if="!period.completed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                  @click.stop="markPeriodAsPaid(period.schedule_id)"
                  :disabled="markingAsPaid"
                  class="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {{ markingAsPaid ? 'Processing...' : 'Mark All as Paid' }}
                </button>
                <span v-if="expandedPeriods[period.schedule_id]" class="text-xs text-blue-600 font-medium">
                  Click to collapse
                </span>
                <span v-else class="text-xs text-gray-400 font-medium">
                  Click to expand
                </span>
              </div>
            </div>
          </div>

          <!-- Expanded Payment Details -->
          <div v-if="expandedPeriods[period.schedule_id]" class="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <div class="mb-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Tips</span>
                <span class="font-bold text-green-700 text-lg">${{ formatCurrency(period.total_tips || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Fines</span>
                <span class="font-bold text-red-700 text-lg">${{ formatCurrency(period.total_fines || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Earnings</span>
                <span class="font-bold text-blue-700 text-lg">${{ formatCurrency(period.total_earnings || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Processed By</span>
                <span class="font-medium text-gray-900">{{ period.processed_by?.username || 'System' }}</span>
              </div>
            </div>

            <!-- Payments Table -->
            <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200" style="min-width: 1200px;">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Payment ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Writer</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Orders</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Amount</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Tips</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Fines</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Total</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="payment in period.payments" :key="payment.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-mono">{{ payment.reference_code }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div>{{ payment.writer.full_name }}</div>
                    <div class="text-xs text-gray-500">{{ payment.writer.registration_id }}</div>
                  </td>
                    <td class="px-4 py-3 text-sm text-gray-600 truncate max-w-xs">{{ payment.writer.email }}</td>
                  <td class="px-4 py-3 text-sm text-center">{{ payment.order_count }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-gray-900 break-all">${{ formatCurrency(payment.amount) }}</td>
                    <td class="px-4 py-3 text-sm text-green-600 font-medium break-all">${{ formatCurrency(payment.tips || 0) }}</td>
                    <td class="px-4 py-3 text-sm text-red-600 font-medium break-all">${{ formatCurrency(payment.fines || 0) }}</td>
                    <td class="px-4 py-3 text-sm font-bold text-gray-900 break-all">${{ formatCurrency(payment.total_earnings || payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusClass(payment.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center gap-2 flex-wrap">
                      <button
                        @click="viewPaymentBreakdown(payment.id)"
                        class="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-xs font-medium transition-colors"
                        title="View Details"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        View
                      </button>
                      <button
                        v-if="payment.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="markPaymentAsPaid(payment.id)"
                        :disabled="markingAsPaid"
                        class="inline-flex items-center gap-1 px-2 py-1 text-green-600 hover:bg-green-50 rounded text-xs font-medium transition-colors disabled:opacity-50"
                        title="Mark as Paid"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {{ markingAsPaid ? 'Processing...' : 'Mark Paid' }}
                      </button>
                      <button
                        v-if="(authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="showMoveToNextPeriodModal(payment)"
                        class="inline-flex items-center gap-1 px-2 py-1 text-purple-600 hover:bg-purple-50 rounded text-xs font-medium transition-colors"
                        :title="getAdjustmentReason(payment.id)"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                        Move
                      </button>
                      <button
                        v-if="(authStore.isAdmin || authStore.isSuperAdmin)"
                        @click="showAdjustOrderStatusModal(payment)"
                        class="inline-flex items-center gap-1 px-2 py-1 text-orange-600 hover:bg-orange-50 rounded text-xs font-medium transition-colors"
                        title="Adjust for Order"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Adjust
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
    </div>

    <!-- Monthly Payments -->
      <div v-if="(paymentTypeTab === 'all' || paymentTypeTab === 'monthly') && monthlyPayments.length > 0" class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 bg-linear-to-r from-green-50 to-green-100">
        <h2 class="text-xl font-semibold text-green-900">Monthly Payments</h2>
      </div>
      <div class="divide-y divide-gray-200">
        <div
          v-for="period in monthlyPayments"
          :key="period.schedule_id"
          class="transition-colors"
          :class="expandedPeriods[period.schedule_id] ? 'bg-green-50/30' : ''"
        >
          <!-- Period Header (Clickable) -->
          <div
            @click="togglePeriod(period.schedule_id)"
            :class="[
              'px-6 py-4 cursor-pointer flex items-center justify-between transition-all duration-200',
              expandedPeriods[period.schedule_id] 
                ? 'bg-green-50 border-l-4 border-green-500 shadow-sm' 
                : 'hover:bg-green-50/30 hover:border-l-4 hover:border-green-300 border-l-4 border-transparent'
            ]"
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
                <div class="font-medium text-gray-900 break-all">${{ formatCurrency(period.total_amount) }}</div>
              </div>
              <div class="text-sm">
                <div class="text-gray-500">Status</div>
                <div>
                  <span :class="period.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ period.completed ? 'Completed' : 'Pending' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2 justify-end">
                <button
                  v-if="!period.completed && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                  @click.stop="markPeriodAsPaid(period.schedule_id)"
                  :disabled="markingAsPaid"
                  class="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
                >
                  {{ markingAsPaid ? 'Processing...' : 'Mark All as Paid' }}
                </button>
                <span v-if="expandedPeriods[period.schedule_id]" class="text-xs text-green-600 font-medium">
                  Click to collapse
                </span>
                <span v-else class="text-xs text-gray-400 font-medium">
                  Click to expand
                </span>
              </div>
            </div>
          </div>

          <!-- Expanded Payment Details -->
          <div v-if="expandedPeriods[period.schedule_id]" class="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <div class="mb-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Tips</span>
                <span class="font-bold text-green-700 text-lg">${{ formatCurrency(period.total_tips || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Fines</span>
                <span class="font-bold text-red-700 text-lg">${{ formatCurrency(period.total_fines || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Total Earnings</span>
                <span class="font-bold text-blue-700 text-lg">${{ formatCurrency(period.total_earnings || 0) }}</span>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-200">
                <span class="text-gray-600 block mb-1">Processed By</span>
                <span class="font-medium text-gray-900">{{ period.processed_by?.username || 'System' }}</span>
              </div>
            </div>

            <!-- Payments Table -->
            <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200" style="min-width: 1200px;">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Payment ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Writer</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Orders</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Amount</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Tips</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Fines</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Total</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="payment in period.payments" :key="payment.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-mono">{{ payment.reference_code }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div>{{ payment.writer.full_name }}</div>
                    <div class="text-xs text-gray-500">{{ payment.writer.registration_id }}</div>
                  </td>
                    <td class="px-4 py-3 text-sm text-gray-600 truncate max-w-xs">{{ payment.writer.email }}</td>
                  <td class="px-4 py-3 text-sm text-center">{{ payment.order_count }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-gray-900 break-all">${{ formatCurrency(payment.amount) }}</td>
                    <td class="px-4 py-3 text-sm text-green-600 font-medium break-all">${{ formatCurrency(payment.tips || 0) }}</td>
                    <td class="px-4 py-3 text-sm text-red-600 font-medium break-all">${{ formatCurrency(payment.fines || 0) }}</td>
                    <td class="px-4 py-3 text-sm font-bold text-gray-900 break-all">${{ formatCurrency(payment.total_earnings || payment.amount) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getStatusClass(payment.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ payment.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center gap-2">
                      <button
                        @click="viewPaymentBreakdown(payment.id)"
                          class="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-xs font-medium transition-colors"
                          title="View Details"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          View
                      </button>
                      <button
                        v-if="payment.status === 'Pending' && (authStore.isAdmin || authStore.isSuperAdmin || authStore.isSupport)"
                        @click="markPaymentAsPaid(payment.id)"
                        :disabled="markingAsPaid"
                          class="inline-flex items-center gap-1 px-2 py-1 text-green-600 hover:bg-green-50 rounded text-xs font-medium transition-colors disabled:opacity-50"
                          title="Mark as Paid"
                      >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {{ markingAsPaid ? 'Processing...' : 'Mark Paid' }}
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
    </div>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-if="!loading && (
        (paymentTypeTab === 'all' && biweeklyPayments.length === 0 && monthlyPayments.length === 0) ||
        (paymentTypeTab === 'biweekly' && biweeklyPayments.length === 0) ||
        (paymentTypeTab === 'monthly' && monthlyPayments.length === 0)
      )" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <p class="text-gray-500 text-lg">
          <span v-if="paymentTypeTab === 'biweekly'">No bi-weekly payment periods found</span>
          <span v-else-if="paymentTypeTab === 'monthly'">No monthly payment periods found</span>
          <span v-else>No payment periods found</span>
        </p>
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
                          class="inline-flex items-center gap-1 px-2 py-1 text-blue-600 hover:bg-blue-50 rounded text-xs font-medium transition-colors"
                          title="View Order"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
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
    <div v-if="activeTab === 'requests'" class="space-y-6">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-linear-to-br from-yellow-50 to-yellow-100 rounded-lg shadow border border-yellow-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-yellow-700 truncate">Pending Requests</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-yellow-900 break-all leading-tight">{{ paymentRequestsSummary.pending || 0 }}</p>
          <p class="text-xs text-yellow-600">awaiting review</p>
        </div>
        <div class="bg-linear-to-br from-green-50 to-green-100 rounded-lg shadow border border-green-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-green-700 truncate">Approved</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-green-900 break-all leading-tight">{{ paymentRequestsSummary.approved || 0 }}</p>
          <p class="text-xs text-green-600">approved requests</p>
        </div>
        <div class="bg-linear-to-br from-red-50 to-red-100 rounded-lg shadow border border-red-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-red-700 truncate">Rejected</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-red-900 break-all leading-tight">{{ paymentRequestsSummary.rejected || 0 }}</p>
          <p class="text-xs text-red-600">rejected requests</p>
        </div>
        <div class="bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
          <p class="text-xs font-medium text-blue-700 truncate">Total Amount</p>
          <p class="text-base sm:text-lg lg:text-xl font-bold text-blue-900 break-all leading-tight">${{ formatCurrency(paymentRequestsSummary.total_amount || 0) }}</p>
          <p class="text-xs text-blue-600">all requests</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Website</label>
            <select
              v-model="paymentRequestFilters.website_id"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              @change="loadPaymentRequests"
            >
              <option value="">All Websites</option>
              <option v-for="website in websites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
            <select
              v-model="paymentRequestFilters.status"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              @change="loadPaymentRequests"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="processed">Processed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Search</label>
            <input
              v-model="paymentRequestFilters.search"
              type="text"
              placeholder="Writer email or name..."
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              @input="debouncedPaymentRequestSearch"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Date From</label>
            <input
              v-model="paymentRequestFilters.date_from"
              type="date"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              @change="loadPaymentRequests"
            />
          </div>
          <div class="flex items-end">
            <button
              @click="clearPaymentRequestFilters"
              class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Payment Requests Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div v-if="paymentRequestsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="paymentRequests.length === 0" class="text-center py-12 text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2 text-sm font-medium">No payment requests found</p>
          <p class="mt-1 text-xs text-gray-400">Try adjusting your filters</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 text-xs">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Date</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Writer</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Requested</th>
                <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Available</th>
                <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Status</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Reason</th>
                <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Reviewed By</th>
                <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="request in paymentRequests" :key="request.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-3 py-2 text-xs text-gray-900 font-normal whitespace-nowrap">
                  {{ formatDate(request.created_at) }}
                </td>
                <td class="px-3 py-2 text-xs whitespace-nowrap">
                  <div class="font-medium text-gray-900">{{ request.writer_wallet_data?.writer?.username || 'N/A' }}</div>
                  <div class="text-gray-500 text-xs">{{ request.writer_wallet_data?.writer?.email || '' }}</div>
                </td>
                <td class="px-3 py-2 text-xs text-right font-semibold text-gray-900 whitespace-nowrap">
                  ${{ formatCurrency(request.requested_amount) }}
                </td>
                <td class="px-3 py-2 text-xs text-right font-normal text-gray-600 whitespace-nowrap">
                  ${{ formatCurrency(request.available_balance) }}
                </td>
                <td class="px-3 py-2 text-xs text-center whitespace-nowrap">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                        :class="getPaymentRequestStatusClass(request.status)">
                    {{ request.status }}
                  </span>
                </td>
                <td class="px-3 py-2 text-xs text-gray-600 font-normal max-w-xs truncate whitespace-nowrap" :title="request.reason">
                  {{ request.reason || '—' }}
                </td>
                <td class="px-3 py-2 text-xs text-gray-600 font-normal whitespace-nowrap">
                  <div v-if="request.reviewed_by_username">
                    <div class="font-medium">{{ request.reviewed_by_username }}</div>
                    <div class="text-gray-500 text-xs">{{ formatDate(request.reviewed_at) }}</div>
                  </div>
                  <span v-else class="text-gray-400">—</span>
                </td>
                <td class="px-3 py-2 text-xs text-center whitespace-nowrap">
                  <div class="flex items-center justify-center gap-1">
                  <button
                      v-if="request.status === 'pending'"
                      @click="approvePaymentRequest(request)"
                      class="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs font-medium"
                      title="Approve Request"
                  >
                    Approve
                  </button>
                    <button
                      v-if="request.status === 'pending'"
                      @click="rejectPaymentRequest(request)"
                      class="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-xs font-medium"
                      title="Reject Request"
                    >
                      Reject
                    </button>
                    <button
                      @click="viewPaymentRequestDetails(request)"
                      class="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-xs font-medium"
                      title="View Details"
                    >
                      View
                    </button>
                  </div>
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
          <table class="min-w-full divide-y divide-gray-200" style="min-width: 800px;">
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

  <!-- Confirmation Dialog -->
  <ConfirmationDialog
    :show="showConfirmDialog"
    :title="confirmDialog.title"
    :message="confirmDialog.message"
    :details="confirmDialog.details"
    :icon="confirmDialog.icon"
    :variant="confirmDialog.variant"
    :confirm-text="confirmDialog.confirmText"
    :cancel-text="confirmDialog.cancelText"
    @confirm="confirmDialog.onConfirm"
    @cancel="showConfirmDialog = false"
    @update:show="showConfirmDialog = $event"
  />

  <!-- Toast Container -->
  <ToastContainer />
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { debounce } from '@/utils/debounce'
import apiClient from '@/api/client'
import writerPaymentsAPI from '@/api/writer-payments'
import paymentsAPI from '@/api/payments'
import { useAuthStore } from '@/stores/auth'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import { useToast } from '@/composables/useToast'

const authStore = useAuthStore()
const { success, error, warning, info } = useToast()

const activeTab = ref('payments')
const paymentTypeTab = ref('all') // 'all', 'biweekly', 'monthly'
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
const paymentRequests = ref([])
const paymentRequestsLoading = ref(false)
const websites = ref([])
const paymentRequestFilters = ref({
  website_id: '',
  status: '',
  search: '',
  date_from: '',
  date_to: '',
})
const paymentRequestPagination = ref({
  page: 1,
  page_size: 50,
  count: 0,
  next: null,
  previous: null,
})
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

// Confirmation dialog state
const showConfirmDialog = ref(false)
const confirmDialog = ref({
  title: '',
  message: '',
  details: '',
  icon: null,
  variant: 'default',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  onConfirm: () => {},
  onCancel: () => {},
})

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
  } catch (err) {
    console.error('Failed to load payments:', err)
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
  } catch (err) {
    console.error('Failed to load batch breakdown:', err)
    error('Failed to load batch breakdown: ' + (err.response?.data?.detail || err.message))
    showBreakdownModal.value = false
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
  } catch (err) {
    console.error('Failed to load payment breakdown:', err)
    error('Failed to load payment breakdown: ' + (err.response?.data?.detail || err.message))
    showBreakdownModal.value = false
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
  confirmDialog.value = {
    title: 'Mark Payment as Paid',
    message: 'Are you sure you want to mark this payment as paid?',
    icon: '💰',
    variant: 'default',
    confirmText: 'Mark as Paid',
    cancelText: 'Cancel',
    onConfirm: async () => {
  markingAsPaid.value = true
  try {
    await apiClient.post(`/writer-wallet/scheduled-payments/${paymentId}/mark-as-paid/`)
        success('Payment marked as paid successfully!')
    await loadPayments()
      } catch (err) {
        console.error('Failed to mark payment as paid:', err)
        error('Failed to mark payment as paid: ' + (err.response?.data?.error || err.message))
  } finally {
    markingAsPaid.value = false
  }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const markPeriodAsPaid = async (scheduleId) => {
  confirmDialog.value = {
    title: 'Mark All Payments as Paid',
    message: 'Are you sure you want to mark all payments in this period as paid?',
    icon: '💰',
    variant: 'default',
    confirmText: 'Mark All as Paid',
    cancelText: 'Cancel',
    onConfirm: async () => {
  markingAsPaid.value = true
  try {
    await apiClient.post('/writer-wallet/scheduled-payments/bulk-mark-as-paid/', {
      schedule_id: scheduleId
    })
        success('All payments in this period have been marked as paid!')
    await loadPayments()
      } catch (err) {
        console.error('Failed to mark payments as paid:', err)
        error('Failed to mark payments as paid: ' + (err.response?.data?.error || err.message))
  } finally {
    markingAsPaid.value = false
  }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  const num = parseFloat(value)
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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
    warning('Please enter a reason for moving this payment')
    return
  }

  try {
    const response = await writerPaymentsAPI.moveToNextPeriod(selectedPayment.value.id, {
      reason: moveReason.value,
      target_period_type: targetPeriodType.value || null
    })
    success(response.data.message || 'Payment moved to next period successfully')
    showMoveModal.value = false
    await loadPayments()
    await loadAdjustments()
  } catch (err) {
    console.error('Failed to move payment:', err)
    error('Failed to move payment: ' + (err.response?.data?.error || err.message))
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
    warning('Please select an order status')
    return
  }

  try {
    const response = await writerPaymentsAPI.adjustForOrderStatus(selectedPayment.value.id, {
      order_status: orderStatus.value,
      reason: adjustReason.value
    })
    success(response.data.message || 'Payment adjusted successfully')
    showAdjustModal.value = false
    await loadPayments()
    await loadAdjustments()
  } catch (err) {
    console.error('Failed to adjust payment:', err)
    error('Failed to adjust payment: ' + (err.response?.data?.error || err.message))
  }
}

const clearPayments = async () => {
  confirmDialog.value = {
    title: 'Mark Payments as Paid',
    message: 'Are you sure you want to mark these payments as paid?',
    details: 'This action cannot be undone.',
    icon: '⚠️',
    variant: 'warning',
    confirmText: 'Mark as Paid',
    cancelText: 'Cancel',
    onConfirm: async () => {
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
        success(response.data.message || 'Payments marked as paid successfully')
    showClearModal.value = false
    await loadPayments()
      } catch (err) {
        console.error('Failed to clear payments:', err)
        error('Failed to clear payments: ' + (err.response?.data?.error || err.message))
      }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const loadPayoutRequests = async () => {
  try {
    const response = await writerPaymentsAPI.getPayoutRequests({})
    payoutRequests.value = response.data.results || []
  } catch (err) {
    console.error('Failed to load payout requests:', err)
  }
}

const approvePayoutRequest = async (payoutId) => {
  confirmDialog.value = {
    title: 'Approve Payout Request',
    message: 'Are you sure you want to approve this payout request?',
    icon: '✓',
    variant: 'default',
    confirmText: 'Approve',
    cancelText: 'Cancel',
    onConfirm: async () => {
  try {
    await writerPaymentsAPI.approvePayout(payoutId)
        success('Payout approved successfully!')
    await loadPayoutRequests()
      } catch (err) {
        console.error('Failed to approve payout:', err)
        error('Failed to approve payout: ' + (err.response?.data?.error || err.message))
      }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const loadAdjustments = async () => {
  try {
    const response = await writerPaymentsAPI.getAdjustments({})
    adjustments.value = response.data.results || []
  } catch (err) {
    console.error('Failed to load adjustments:', err)
  }
}

const getAdjustmentReason = (paymentId) => {
  const adj = adjustments.value.find(a => a.payment_id === paymentId)
  return adj ? adj.reason : ''
}

const paymentRequestsSummary = computed(() => {
  const pending = paymentRequests.value.filter(r => r.status === 'pending').length
  const approved = paymentRequests.value.filter(r => r.status === 'approved').length
  const rejected = paymentRequests.value.filter(r => r.status === 'rejected').length
  const total_amount = paymentRequests.value.reduce((sum, r) => sum + parseFloat(r.requested_amount || 0), 0)
  
  return {
    pending,
    approved,
    rejected,
    total_amount,
  }
})

const loadWebsites = async () => {
  try {
    const response = await apiClient.get('/websites/websites/')
    websites.value = response.data.results || response.data || []
  } catch (err) {
    console.error('Failed to load websites:', err)
  }
}

const loadPaymentRequests = async () => {
  paymentRequestsLoading.value = true
  try {
    const params = {
      page: paymentRequestPagination.value.page,
      page_size: paymentRequestPagination.value.page_size,
    }
    
    if (paymentRequestFilters.value.website_id) params.website_id = paymentRequestFilters.value.website_id
    if (paymentRequestFilters.value.status) params.status = paymentRequestFilters.value.status
    if (paymentRequestFilters.value.search) params.search = paymentRequestFilters.value.search
    if (paymentRequestFilters.value.date_from) params.date_from = paymentRequestFilters.value.date_from
    if (paymentRequestFilters.value.date_to) params.date_to = paymentRequestFilters.value.date_to
    
    const response = await paymentsAPI.listPaymentRequests(params)
    paymentRequests.value = response.data.results || response.data || []
    
    paymentRequestPagination.value = {
      page: paymentRequestPagination.value.page,
      page_size: paymentRequestPagination.value.page_size,
      count: response.data.count || paymentRequests.value.length,
      next: response.data.next,
      previous: response.data.previous,
    }
  } catch (err) {
    console.error('Failed to load payment requests:', err)
    error('Failed to load payment requests')
    paymentRequests.value = []
  } finally {
    paymentRequestsLoading.value = false
  }
}

const clearPaymentRequestFilters = () => {
  paymentRequestFilters.value = {
    website_id: '',
    status: '',
    search: '',
    date_from: '',
    date_to: '',
  }
  paymentRequestPagination.value.page = 1
  loadPaymentRequests()
}

const debouncedPaymentRequestSearch = debounce(() => {
  paymentRequestPagination.value.page = 1
  loadPaymentRequests()
}, 500)

const getPaymentRequestStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    processed: 'bg-blue-100 text-blue-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const approvePaymentRequest = (request) => {
  confirmDialog.value = {
    title: 'Approve Payment Request',
    message: `Are you sure you want to approve this payment request of $${formatCurrency(request.requested_amount)}?`,
    icon: '✅',
    variant: 'default',
    confirmText: 'Approve',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        await paymentsAPI.approvePaymentRequest(request.id)
        success('Payment request approved successfully')
        await loadPaymentRequests()
      } catch (err) {
        console.error('Failed to approve payment request:', err)
        error('Failed to approve payment request: ' + (err.response?.data?.error || err.message))
      }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const rejectPaymentRequest = (request) => {
  confirmDialog.value = {
    title: 'Reject Payment Request',
    message: `Are you sure you want to reject this payment request of $${formatCurrency(request.requested_amount)}?`,
    icon: '❌',
    variant: 'default',
    confirmText: 'Reject',
    cancelText: 'Cancel',
    onConfirm: async () => {
      try {
        await paymentsAPI.rejectPaymentRequest(request.id, {
          review_notes: 'Rejected by admin',
        })
        success('Payment request rejected')
        await loadPaymentRequests()
      } catch (err) {
        console.error('Failed to reject payment request:', err)
        error('Failed to reject payment request: ' + (err.response?.data?.error || err.message))
      }
    },
    onCancel: () => {},
  }
  showConfirmDialog.value = true
}

const viewPaymentRequestDetails = (request) => {
  info(`Payment Request Details:\nWriter: ${request.writer_wallet_data?.writer?.username || 'N/A'}\nAmount: $${formatCurrency(request.requested_amount)}\nStatus: ${request.status}\nReason: ${request.reason || 'N/A'}`)
}

// Watch for tab changes to load payment requests
watch(activeTab, (newTab) => {
  if (newTab === 'requests' && paymentRequests.value.length === 0) {
    loadPaymentRequests()
  }
})

onMounted(() => {
  loadPayments()
  loadPayoutRequests()
  loadAdjustments()
  loadWebsites()
  // Load payment requests when tab is active
  if (activeTab.value === 'requests') {
    loadPaymentRequests()
  }
})
</script>

