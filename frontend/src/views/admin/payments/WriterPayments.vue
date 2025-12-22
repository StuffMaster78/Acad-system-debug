<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4">
    <PageHeader
      title="Writer Payments"
      subtitle="Writer payments grouped by bi-weekly and monthly periods"
      @refresh="loadPayments"
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-linear-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-blue-700 truncate">Total Bi-Weekly</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-blue-900 break-all leading-tight">${{ formatCurrency(summary.total_biweekly_amount || 0) }}</p>
        <p class="text-xs text-blue-600">{{ summary.total_biweekly_payments || 0 }} payments</p>
      </div>
      <div class="bg-linear-to-br from-green-50 to-green-100 rounded-lg shadow border border-green-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-green-700 truncate">Total Monthly</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-green-900 break-all leading-tight">${{ formatCurrency(summary.total_monthly_amount || 0) }}</p>
        <p class="text-xs text-green-600">{{ summary.total_monthly_payments || 0 }} payments</p>
      </div>
      <div class="bg-linear-to-br from-purple-50 to-purple-100 rounded-lg shadow border border-purple-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-purple-700 truncate">Total Amount</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-purple-900 break-all leading-tight">${{ formatCurrency((summary.total_biweekly_amount || 0) + (summary.total_monthly_amount || 0)) }}</p>
        <p class="text-xs text-purple-600">{{ (summary.total_biweekly_payments || 0) + (summary.total_monthly_payments || 0) }} total payments</p>
      </div>
      <div class="bg-linear-to-br from-orange-50 to-orange-100 rounded-lg shadow border border-orange-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-orange-700 truncate">Periods</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-orange-900 break-all leading-tight">{{ biweeklyPayments.length + monthlyPayments.length }}</p>
        <p class="text-xs text-orange-600">payment periods</p>
      </div>
    </div>

    <div class="bg-white p-4 rounded-lg shadow border border-gray-200 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Website</label>
          <select
            v-model="filters.website_id"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPayments"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Period Type</label>
          <select
            v-model="filters.period_type"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPayments"
          >
            <option value="both">Both Periods</option>
            <option value="biweekly">Bi-Weekly Only</option>
            <option value="monthly">Monthly Only</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPayments"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Date To</label>
          <input
            v-model="filters.date_to"
            type="date"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPayments"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
          >
            Reset Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Type Tabs -->
    <div v-if="filters.period_type === 'both'" class="bg-white rounded-lg shadow border border-gray-200 mb-6">
      <div class="flex border-b border-gray-200">
        <button
          @click="activePaymentTab = 'biweekly'"
          :class="[
            'flex-1 px-6 py-4 text-sm font-medium transition-colors border-b-2',
            activePaymentTab === 'biweekly'
              ? 'border-blue-500 text-blue-600 bg-blue-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          ]"
        >
          <div class="flex items-center justify-center gap-2">
            <div class="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Bi-Weekly Payments</span>
            <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              {{ biweeklyPayments.length }}
            </span>
          </div>
        </button>
        <button
          @click="activePaymentTab = 'monthly'"
          :class="[
            'flex-1 px-6 py-4 text-sm font-medium transition-colors border-b-2',
            activePaymentTab === 'monthly'
              ? 'border-green-500 text-green-600 bg-green-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          ]"
        >
          <div class="flex items-center justify-center gap-2">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Monthly Payments</span>
            <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              {{ monthlyPayments.length }}
            </span>
          </div>
        </button>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Bi-Weekly Payments -->
      <div v-if="(filters.period_type === 'both' && activePaymentTab === 'biweekly') || filters.period_type === 'biweekly'">
        <div class="flex items-center gap-3 mb-4">
          <div class="h-8 w-1 bg-blue-500 rounded-full"></div>
          <h2 class="text-2xl font-bold text-gray-900">Bi-Weekly Payments</h2>
          <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            {{ biweeklyPayments.length }} periods
          </span>
        </div>
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="mt-2 text-gray-500">Loading payments...</p>
        </div>
        <div v-else-if="biweeklyPayments.length === 0" class="bg-white rounded-lg shadow border border-gray-200 p-12 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-4 text-gray-500 text-lg">No bi-weekly payments found</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="period in biweeklyPayments"
            :key="period.schedule_id"
            class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden transition-all hover:shadow-md"
            :class="expandedPeriods[period.schedule_id] ? 'border-blue-300' : ''"
          >
            <div 
              class="px-6 py-4 bg-linear-to-r from-blue-50 to-blue-100 border-b border-blue-200 cursor-pointer transition-colors hover:from-blue-100 hover:to-blue-150"
              :class="expandedPeriods[period.schedule_id] ? 'from-blue-100 to-blue-150' : ''"
              @click="togglePeriod(period.schedule_id)"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4 flex-1">
                  <div class="flex items-center gap-2">
                    <svg 
                      class="w-5 h-5 text-blue-600 transition-transform"
                      :class="expandedPeriods[period.schedule_id] ? 'rotate-90' : ''"
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-semibold text-lg text-blue-900">
                      {{ formatDate(period.scheduled_date) }}
                  </h3>
                    <div class="flex items-center gap-4 mt-1 text-sm text-blue-700">
                      <span class="font-mono text-xs">{{ period.reference_code }}</span>
                      <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {{ period.writer_count }} writers
                      </span>
                      <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {{ period.total_orders || 0 }} orders
                      </span>
                      <span 
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          period.completed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        ]"
                      >
                        {{ period.completed ? 'Completed' : 'Pending' }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="text-right ml-4 flex items-center gap-4">
                  <div>
                    <div class="text-2xl font-bold text-blue-900">
                      ${{ formatCurrency(period.total_amount || 0) }}
                    </div>
                    <div class="text-xs text-blue-600 font-medium">Total Amount</div>
              </div>
                  <button
                    v-if="!period.completed"
                    @click.stop="markPeriodAsPaid(period.schedule_id)"
                    :disabled="markingAsPaid"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center gap-2"
                    title="Mark all payments in this period as paid"
                  >
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ markingAsPaid ? 'Processing...' : 'Mark All Paid' }}
                  </button>
                </div>
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
                    <template v-for="payment in period.payments" :key="payment.id">
                    <tr 
                        class="hover:bg-blue-50 transition-colors"
                    >
                      <td class="px-4 py-2">
                          <div class="flex items-center gap-2">
                            <button
                              @click.stop="expandedPayments[payment.id] = !expandedPayments[payment.id]"
                              class="p-1 hover:bg-blue-100 rounded transition-colors"
                              v-if="payment.orders && payment.orders.length > 0"
                            >
                              <svg 
                                class="w-4 h-4 text-blue-600 transition-transform"
                                :class="expandedPayments[payment.id] ? 'rotate-90' : ''"
                                fill="none" 
                                viewBox="0 0 24 24" 
                                stroke="currentColor"
                              >
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                              </svg>
                            </button>
                            <div class="flex-1 cursor-pointer" @click="viewPaymentDetails(payment)">
                        <div class="font-medium">{{ payment.writer.full_name || payment.writer.username }}</div>
                        <div class="text-xs text-gray-500">{{ payment.writer.email }}</div>
                        <div class="text-xs text-gray-400">{{ payment.writer.registration_id }}</div>
                            </div>
                            <button
                              @click.stop="viewWriterWallet(payment.writer)"
                              class="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors flex items-center gap-1"
                              title="View Writer's Wallet"
                            >
                              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                              </svg>
                              Wallet
                            </button>
                          </div>
                      </td>
                        <td class="px-4 py-2 text-right font-medium cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.amount) }}
                      </td>
                        <td class="px-4 py-2 text-right text-green-600 cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.tips || 0) }}
                      </td>
                        <td class="px-4 py-2 text-right text-red-600 cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.fines || 0) }}
                      </td>
                        <td class="px-4 py-2 text-right font-bold cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.total_earnings || payment.amount) }}
                      </td>
                        <td class="px-4 py-2 text-center cursor-pointer" @click="viewPaymentDetails(payment)">
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
                        <td class="px-4 py-2 text-xs text-gray-500 font-mono cursor-pointer" @click="viewPaymentDetails(payment)">
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
                      <tr v-if="expandedPayments[payment.id] && payment.orders && payment.orders.length > 0" class="bg-blue-50/50">
                        <td colspan="8" class="px-4 py-2">
                          <div class="ml-8">
                            <div class="text-xs font-semibold text-gray-700 mb-2">Orders ({{ payment.orders.length }})</div>
                            <div class="space-y-1">
                              <div 
                                v-for="order in payment.orders" 
                                :key="order.id"
                                class="flex items-center justify-between text-xs bg-white rounded px-3 py-2 border border-gray-200 hover:bg-blue-50 transition-colors"
                              >
                                <div class="flex items-center gap-3 flex-1">
                                  <router-link
                                    :to="`/orders/${order.id}`"
                                    class="font-mono font-medium text-blue-600 hover:text-blue-800 hover:underline"
                                    @click.stop
                                  >
                                    #{{ order.id }}
                                  </router-link>
                                  <span class="text-gray-600 truncate max-w-md" :title="order.topic">{{ order.topic || 'N/A' }}</span>
                                </div>
                                <span class="font-medium text-gray-900">${{ formatCurrency(order.amount_paid || 0) }}</span>
                              </div>
                            </div>
                            <div class="mt-2 pt-2 border-t border-gray-300 flex items-center justify-between text-xs font-semibold">
                              <span class="text-gray-700">Total from Orders:</span>
                              <span class="text-gray-900">${{ formatCurrency(payment.amount) }}</span>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Payments -->
      <div v-if="(filters.period_type === 'both' && activePaymentTab === 'monthly') || filters.period_type === 'monthly'">
        <div class="flex items-center gap-3 mb-4" :class="filters.period_type === 'both' ? '' : 'mt-8'">
          <div class="h-8 w-1 bg-green-500 rounded-full"></div>
          <h2 class="text-2xl font-bold text-gray-900">Monthly Payments</h2>
          <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            {{ monthlyPayments.length }} periods
          </span>
        </div>
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p class="mt-2 text-gray-500">Loading payments...</p>
        </div>
        <div v-else-if="monthlyPayments.length === 0" class="bg-white rounded-lg shadow border border-gray-200 p-12 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-4 text-gray-500 text-lg">No monthly payments found</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="period in monthlyPayments"
            :key="period.schedule_id"
            class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden transition-all hover:shadow-md"
            :class="expandedPeriods[period.schedule_id] ? 'border-green-300' : ''"
          >
            <div 
              class="px-6 py-4 bg-linear-to-r from-green-50 to-green-100 border-b border-green-200 cursor-pointer transition-colors hover:from-green-100 hover:to-green-150"
              :class="expandedPeriods[period.schedule_id] ? 'from-green-100 to-green-150' : ''"
              @click="togglePeriod(period.schedule_id)"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4 flex-1">
                  <div class="flex items-center gap-2">
                    <svg 
                      class="w-5 h-5 text-green-600 transition-transform"
                      :class="expandedPeriods[period.schedule_id] ? 'rotate-90' : ''"
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="font-semibold text-lg text-green-900">
                      {{ formatDate(period.scheduled_date) }}
                  </h3>
                    <div class="flex items-center gap-4 mt-1 text-sm text-green-700">
                      <span class="font-mono text-xs">{{ period.reference_code }}</span>
                      <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {{ period.writer_count }} writers
                      </span>
                      <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        {{ period.total_orders || 0 }} orders
                      </span>
                      <span 
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          period.completed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                        ]"
                      >
                        {{ period.completed ? 'Completed' : 'Pending' }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="text-right ml-4 flex items-center gap-4">
                  <div>
                    <div class="text-2xl font-bold text-green-900">
                      ${{ formatCurrency(period.total_amount || 0) }}
                    </div>
                    <div class="text-xs text-green-600 font-medium">Total Amount</div>
              </div>
                  <button
                    v-if="!period.completed"
                    @click.stop="markPeriodAsPaid(period.schedule_id)"
                    :disabled="markingAsPaid"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center gap-2"
                    title="Mark all payments in this period as paid"
                  >
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ markingAsPaid ? 'Processing...' : 'Mark All Paid' }}
                  </button>
                </div>
              </div>
            </div>
            <div v-if="expandedPeriods[period.schedule_id] && period.payments.length > 0" class="p-6">
              <div class="mb-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
                  <div class="text-xs text-blue-700 font-medium mb-1">Base Amount</div>
                  <div class="text-lg font-bold text-blue-900">${{ formatCurrency(period.total_amount - (period.total_tips || 0) + (period.total_fines || 0)) }}</div>
                </div>
                <div class="bg-green-50 rounded-lg p-3 border border-green-200">
                  <div class="text-xs text-green-700 font-medium mb-1">Tips</div>
                  <div class="text-lg font-bold text-green-900">${{ formatCurrency(period.total_tips || 0) }}</div>
                </div>
                <div class="bg-red-50 rounded-lg p-3 border border-red-200">
                  <div class="text-xs text-red-700 font-medium mb-1">Fines</div>
                  <div class="text-lg font-bold text-red-900">${{ formatCurrency(period.total_fines || 0) }}</div>
                </div>
                <div class="bg-purple-50 rounded-lg p-3 border border-purple-200">
                  <div class="text-xs text-purple-700 font-medium mb-1">Total Earnings</div>
                  <div class="text-lg font-bold text-purple-900">${{ formatCurrency(period.total_earnings || period.total_amount) }}</div>
                </div>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50 border-b-2 border-gray-200">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Writer</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Orders</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Amount</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Tips</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Fines</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Total</th>
                      <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                      <th class="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <template v-for="payment in period.payments" :key="payment.id">
                      <tr 
                        class="hover:bg-green-50 transition-colors"
                      >
                        <td class="px-4 py-3">
                          <div class="flex items-center gap-2">
                            <button
                              @click.stop="expandedPayments[payment.id] = !expandedPayments[payment.id]"
                              class="p-1 hover:bg-green-100 rounded transition-colors"
                              v-if="payment.orders && payment.orders.length > 0"
                            >
                              <svg 
                                class="w-4 h-4 text-green-600 transition-transform"
                                :class="expandedPayments[payment.id] ? 'rotate-90' : ''"
                                fill="none" 
                                viewBox="0 0 24 24" 
                                stroke="currentColor"
                              >
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                              </svg>
                            </button>
                            <div class="flex-1 cursor-pointer" @click="viewPaymentDetails(payment)">
                              <div class="font-medium text-gray-900">{{ payment.writer.full_name || payment.writer.username }}</div>
                              <div class="text-xs text-gray-500 truncate max-w-xs">{{ payment.writer.email }}</div>
                              <div class="text-xs text-gray-400 font-mono">{{ payment.writer.registration_id }}</div>
                            </div>
                            <button
                              @click.stop="viewWriterWallet(payment.writer)"
                              class="ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors flex items-center gap-1"
                              title="View Writer's Wallet"
                            >
                              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                              </svg>
                              Wallet
                            </button>
                          </div>
                        </td>
                        <td class="px-4 py-3 text-right cursor-pointer" @click="viewPaymentDetails(payment)">
                          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {{ payment.order_count || 0 }}
                          </span>
                      </td>
                        <td class="px-4 py-3 text-right font-medium text-gray-900 break-all cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.amount) }}
                      </td>
                        <td class="px-4 py-3 text-right text-green-600 font-medium break-all cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.tips || 0) }}
                      </td>
                        <td class="px-4 py-3 text-right text-red-600 font-medium break-all cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.fines || 0) }}
                      </td>
                        <td class="px-4 py-3 text-right font-bold text-gray-900 break-all cursor-pointer" @click="viewPaymentDetails(payment)">
                          ${{ formatCurrency(payment.total_earnings || payment.amount) }}
                      </td>
                        <td class="px-4 py-3 text-center cursor-pointer" @click="viewPaymentDetails(payment)">
                        <span
                          :class="[
                              'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            payment.status === 'Paid'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-yellow-100 text-yellow-800',
                          ]"
                        >
                          {{ payment.status }}
                        </span>
                      </td>
                        <td class="px-4 py-3 text-center">
                          <div class="flex items-center justify-center gap-2">
                        <button
                          @click.stop="viewPaymentDetails(payment)"
                              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                              title="View payment details"
                            >
                              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                              View
                            </button>
                            <button
                              v-if="payment.status !== 'Paid'"
                              @click.stop="markPaymentAsPaid(payment.id)"
                              :disabled="markingAsPaid"
                              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              title="Mark as paid"
                            >
                              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {{ markingAsPaid ? 'Processing...' : 'Mark Paid' }}
                        </button>
                          </div>
                      </td>
                    </tr>
                      <tr v-if="expandedPayments[payment.id] && payment.orders && payment.orders.length > 0" class="bg-green-50/50">
                        <td colspan="8" class="px-4 py-3">
                          <div class="ml-8">
                            <div class="text-xs font-semibold text-gray-700 mb-2">Orders ({{ payment.orders.length }})</div>
                            <div class="space-y-1">
                              <div 
                                v-for="order in payment.orders" 
                                :key="order.id"
                                class="flex items-center justify-between text-xs bg-white rounded px-3 py-2 border border-gray-200 hover:bg-green-50 transition-colors"
                              >
                                <div class="flex items-center gap-3 flex-1">
                                  <router-link
                                    :to="`/orders/${order.id}`"
                                    class="font-mono font-medium text-blue-600 hover:text-blue-800 hover:underline"
                                    @click.stop
                                  >
                                    #{{ order.id }}
                                  </router-link>
                                  <span class="text-gray-600 truncate max-w-md" :title="order.topic">{{ order.topic || 'N/A' }}</span>
                  </div>
                                <span class="font-medium text-gray-900">${{ formatCurrency(order.amount_paid || 0) }}</span>
                </div>
              </div>
                            <div class="mt-2 pt-2 border-t border-gray-300 flex items-center justify-between text-xs font-semibold">
                              <span class="text-gray-700">Total from Orders:</span>
                              <span class="text-gray-900">${{ formatCurrency(payment.amount) }}</span>
              </div>
            </div>
                        </td>
                    </tr>
                    </template>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else-if="expandedPeriods[period.schedule_id] && period.payments.length === 0" class="p-6 text-center text-gray-500">
              No payments in this period
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Details Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showPaymentModal = false">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6 border-b pb-4">
            <h3 class="text-2xl font-bold text-gray-900">Payment Details</h3>
            <button @click="showPaymentModal = false" class="text-gray-500 hover:text-gray-700 text-2xl transition-colors">✕</button>
          </div>

          <div v-if="breakdownLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>

          <div v-else-if="selectedPayment" class="space-y-6">
            <!-- Payment Summary -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div class="flex items-start justify-between mb-4">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm flex-1">
                <div>
                    <span class="text-gray-600 font-medium">Payment ID:</span>
                    <div class="font-mono font-medium text-gray-900 mt-1">{{ selectedPayment.reference_code }}</div>
                </div>
                <div>
                    <span class="text-gray-600 font-medium">Writer:</span>
                    <div class="font-medium text-gray-900 mt-1">{{ selectedPayment.writer.full_name || selectedPayment.writer.username }}</div>
                    <div class="text-xs text-gray-500 mt-0.5">{{ selectedPayment.writer.registration_id }}</div>
                    <button
                      @click="viewWriterWallet(selectedPayment.writer)"
                      class="mt-2 px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors flex items-center gap-1"
                      title="View Writer's Wallet"
                    >
                      <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                      View Wallet
                    </button>
                </div>
                  <div>
                    <span class="text-gray-600 font-medium">Status:</span>
                    <div class="mt-1">
                    <span
                      :class="[
                          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
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
                    <span class="text-gray-600 font-medium">Date:</span>
                    <div class="font-medium text-gray-900 mt-1">{{ selectedPayment.payment_date ? formatDate(selectedPayment.payment_date) : 'N/A' }}</div>
                  </div>
                </div>
                <button
                  v-if="selectedPayment.status !== 'Paid'"
                  @click="markPaymentAsPaid(selectedPayment.id)"
                  :disabled="markingAsPaid"
                  class="ml-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium flex items-center gap-2"
                  title="Mark this payment as paid"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ markingAsPaid ? 'Processing...' : 'Mark as Paid' }}
                </button>
              </div>
            </div>

            <!-- Amount Breakdown -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div class="text-sm text-blue-700 mb-1 font-medium">Base Amount</div>
                <div class="text-2xl font-bold text-blue-900">${{ formatCurrency(selectedPayment.amount) }}</div>
              </div>
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <div class="text-sm text-green-700 mb-1 font-medium">Tips</div>
                <div class="text-2xl font-bold text-green-900">${{ formatCurrency(selectedPayment.tips || 0) }}</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 border border-red-200">
                <div class="text-sm text-red-700 mb-1 font-medium">Fines</div>
                <div class="text-2xl font-bold text-red-900">${{ formatCurrency(selectedPayment.fines || 0) }}</div>
              </div>
              <div class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <div class="text-sm text-purple-700 mb-1 font-medium">Total Earnings</div>
                <div class="text-2xl font-bold text-purple-900">${{ formatCurrency(selectedPayment.total_earnings || selectedPayment.amount) }}</div>
              </div>
            </div>

            <!-- Orders -->
            <div v-if="paymentBreakdown && paymentBreakdown.orders && paymentBreakdown.orders.length > 0">
              <h4 class="text-lg font-semibold mb-3 text-gray-900">Orders ({{ paymentBreakdown.orders.length }})</h4>
              <div class="overflow-x-auto border border-gray-200 rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Order ID</th>
                      <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Topic</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Pages</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Slides</th>
                      <th class="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">Amount Paid</th>
                      <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date Submitted</th>
                      <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="order in paymentBreakdown.orders" :key="order.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-4 py-3 text-sm">
                        <router-link
                          :to="`/orders/${order.id}`"
                          class="font-mono text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          #{{ order.id }}
                        </router-link>
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-700 max-w-xs truncate" :title="order.topic || 'N/A'">{{ order.topic || 'N/A' }}</td>
                      <td class="px-4 py-3 text-sm text-right text-gray-700">{{ order.number_of_pages || '-' }}</td>
                      <td class="px-4 py-3 text-sm text-right text-gray-700">{{ order.number_of_slides || '-' }}</td>
                      <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">${{ formatCurrency(order.amount_paid || 0) }}</td>
                      <td class="px-4 py-3 text-sm text-gray-700">
                        {{ order.submitted_at ? formatDate(order.submitted_at) : (order.completed_at ? formatDate(order.completed_at) : '-') }}
                      </td>
                      <td class="px-4 py-3 text-sm">
                        <span
                          :class="[
                            'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                            order.status === 'Completed' || order.status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : order.status === 'In Progress' || order.status === 'in_progress'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                          ]"
                        >
                          {{ order.status || 'N/A' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else-if="selectedPayment.order_ids && selectedPayment.order_ids.length > 0">
              <h4 class="text-lg font-semibold mb-3 text-gray-900">Orders ({{ selectedPayment.order_ids.length }})</h4>
              <div class="text-sm text-gray-600 bg-gray-50 rounded-lg p-4 border border-gray-200">
                Order IDs: <span class="font-mono">{{ selectedPayment.order_ids.join(', ') }}</span>
              </div>
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
      :confirmText="confirmDialog.confirmText"
      :cancelText="confirmDialog.cancelText"
      @confirm="confirmDialog.onConfirm"
      @cancel="confirmDialog.onCancel"
      @update:show="showConfirmDialog = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'

const router = useRouter()

const { success, error, warning, info } = useToast()

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
const expandedPayments = ref({})
const activePaymentTab = ref('biweekly')
const showPaymentModal = ref(false)
const selectedPayment = ref(null)
const paymentBreakdown = ref(null)
const breakdownLoading = ref(false)
const markingAsPaid = ref(false)
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
  activePaymentTab.value = 'biweekly'
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
  } catch (err) {
    console.error('Failed to load payment breakdown:', err)
    error('Failed to load payment breakdown: ' + (err.response?.data?.detail || err.message))
    paymentBreakdown.value = null
  } finally {
    breakdownLoading.value = false
  }
}

const markPaymentAsPaid = async (paymentId) => {
  confirmDialog.value = {
    title: 'Mark Payment as Paid',
    message: 'Are you sure you want to mark this payment as paid?',
    details: 'This action will update the payment status and cannot be undone.',
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
        // Refresh modal if open
        if (selectedPayment.value && selectedPayment.value.id === paymentId) {
          selectedPayment.value.status = 'Paid'
          selectedPayment.value.payment_date = new Date().toISOString()
        }
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
  const period = [...biweeklyPayments.value, ...monthlyPayments.value].find(p => p.schedule_id === scheduleId)
  const paymentCount = period?.payments?.length || 0
  const totalAmount = period?.total_amount || 0
  
  confirmDialog.value = {
    title: 'Mark All Payments as Paid',
    message: `Are you sure you want to mark all ${paymentCount} payments in this period as paid?`,
    details: `This will mark ${paymentCount} payment(s) totaling $${formatCurrency(totalAmount)} as paid. This action cannot be undone.`,
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
        success(`All ${paymentCount} payments in this period have been marked as paid!`)
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
  if (!value && value !== 0) return '0.00'
  return parseFloat(value).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const viewWriterWallet = (writer) => {
  // Navigate to wallet management page with writer filter
  if (writer && writer.email) {
    router.push({
      path: '/admin/wallets',
      query: { 
        tab: 'writers',
        search: writer.email 
      }
    })
  } else {
    router.push({
      path: '/admin/wallets',
      query: { tab: 'writers' }
    })
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
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

