<template>
  <div class="space-y-6">
    <!-- Earnings Summary Bar - Always Visible -->
    <div class="bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 rounded-2xl shadow-xl p-6 text-white">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <!-- Pending Earnings - Most Important -->
        <div class="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-semibold text-white/90 uppercase tracking-wide">Pending Earnings</p>
            <span class="text-2xl">💰</span>
    </div>
          <p class="text-4xl font-bold mb-1">
            {{ writerEarningsData?.pending_payments ? `$${writerEarningsData.pending_payments.toFixed(2)}` : '$0.00' }}
          </p>
          <p class="text-xs text-white/80">Awaiting payment</p>
          <router-link
        to="/writer/payments"
            class="mt-3 inline-block text-sm font-semibold text-white hover:text-white/80 underline"
          >
            View Payments →
          </router-link>
      </div>

        <!-- Total Earnings -->
        <div class="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-semibold text-white/90 uppercase tracking-wide">Total Earnings</p>
            <span class="text-2xl">💵</span>
          </div>
          <p class="text-4xl font-bold mb-1">
            {{ writerEarningsData?.total_earnings ? `$${writerEarningsData.total_earnings.toFixed(2)}` : '$0.00' }}
          </p>
          <p class="text-xs text-white/80">{{ writerEarningsData?.this_month ? `$${writerEarningsData.this_month.toFixed(2)} this month` : 'No earnings yet' }}</p>
      </div>

        <!-- Active Orders Count -->
        <div class="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-semibold text-white/90 uppercase tracking-wide">Active Orders</p>
            <span class="text-2xl">📝</span>
          </div>
          <p class="text-4xl font-bold mb-1">{{ activeOrdersCount }}</p>
          <p class="text-xs text-white/80">{{ inProgressCount }} in progress</p>
          </div>

        <!-- Completion Rate -->
        <div class="bg-white/20 backdrop-blur-sm rounded-xl p-5 border border-white/30">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-semibold text-white/90 uppercase tracking-wide">Completion Rate</p>
            <span class="text-2xl">✅</span>
        </div>
          <p class="text-4xl font-bold mb-1">
            {{ writerPerformanceData?.completion_rate ? `${writerPerformanceData.completion_rate.toFixed(0)}%` : '0%' }}
        </p>
          <p class="text-xs text-white/80">{{ writerPerformanceData?.completed_orders || 0 }} completed</p>
        </div>
      </div>
    </div>

    <!-- Orders Section - Main Focus -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <!-- Orders Header with Tabs -->
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <svg class="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              My Orders
            </h2>
            <p class="text-sm text-gray-600 mt-1">Manage and track all your assigned orders</p>
          </div>
          <div class="flex items-center gap-3">
              <router-link
              to="/writer/queue" 
              class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-semibold flex items-center gap-2 shadow-sm"
              >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Browse Orders
              </router-link>
        </div>
      </div>

        <!-- Status Tabs -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2 px-1">
          <button
            v-for="tab in orderTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-2.5 rounded-lg text-sm font-semibold transition-all whitespace-nowrap flex items-center gap-2',
              activeTab === tab.id
                ? `${tab.bgColor} ${tab.textColor} shadow-md border-2 ${tab.borderColor}`
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            ]"
          >
            <!-- Colored Number Circle -->
            <span 
              :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white',
                tab.color
              ]"
            >
              {{ tab.count }}
            </span>
            {{ tab.label }}
          </button>
      </div>
    </div>

      <!-- Orders Content -->
      <div class="p-6">
        <!-- Loading State -->
        <div v-if="ordersLoading || (activeTab === 'available' && availableOrdersLoading) || (activeTab === 'order_requests' && orderRequestsLoading)" class="flex items-center justify-center py-16">
          <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading orders...</p>
      </div>
    </div>

        <!-- Empty State -->
        <div v-else-if="filteredOrders.length === 0" class="text-center py-16">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
      </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No {{ getActiveTabLabel() }} orders</h3>
          <p class="text-gray-600 mb-4">{{ getEmptyStateMessage() }}</p>
              <router-link
            v-if="activeTab !== 'completed'"
            to="/writer/queue" 
            class="inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-semibold"
              >
            Browse Available Orders
              </router-link>
      </div>

        <!-- Orders Table -->
        <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">#</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Title</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Date</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Pages</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Earnings</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Deadline</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Client</th>
                  <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="order in filteredOrders"
                  :key="order.id"
                  class="hover:bg-gray-50 transition-colors cursor-pointer"
                  :class="{
                    'bg-orange-50 hover:bg-orange-100': order.status === 'revision_requested',
                    'bg-red-50 hover:bg-red-100 border-l-4 border-red-500': isOverdue(order) && isInProgress(order),
                    'bg-amber-50 hover:bg-amber-100 border-l-4 border-amber-500': !isOverdue(order) && isDueSoon(order) && isInProgress(order)
                  }"
                  @click="$router.push(`/orders/${order.id}`)"
                >
                  <!-- Order ID -->
                  <td class="px-4 py-4 whitespace-nowrap">
        <div class="flex items-center gap-2">
                      <div class="w-10 h-10 bg-gradient-to-br from-emerald-400 to-green-500 rounded-lg flex items-center justify-center text-white font-bold shadow-md">
                        #{{ order.id }}
        </div>
      </div>
                  </td>
                  
                  <!-- Title -->
                  <td class="px-4 py-4 max-w-xs sm:max-w-sm">
                    <div class="flex flex-col">
                      <span class="text-sm font-semibold text-gray-900 truncate">
                        {{ getShortTitle(order) }}
                      </span>
                      <span
                        v-if="order.subject?.name || order.subject"
                        class="text-xs text-gray-500 mt-0.5 truncate"
                      >
                        {{ order.subject?.name || order.subject }}
                      </span>
        </div>
                  </td>
                  
                  <!-- Status -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <OrderStatusTooltip :status="order.status" position="bottom">
                      <span
                        class="px-3 py-1 rounded-full text-xs font-semibold"
                        :class="getOrderStatusClass(order.status)"
                      >
                        {{ formatStatus(order.status) }}
                      </span>
                    </OrderStatusTooltip>
                  </td>
                  
                  <!-- Date -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-600">
                      {{ formatDate(order.created_at) }}
                    </span>
                  </td>
                  
                  <!-- Pages -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm font-medium text-gray-900">
                      {{ order.number_of_pages || order.pages || 0 }}
                    </span>
                  </td>
                  
                  <!-- Earnings -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm font-bold text-emerald-600">
                      ${{ (Number(order.writer_compensation) || 0).toFixed(2) }}
                    </span>
                  </td>
                  
                  <!-- Deadline -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span
                      class="text-sm font-semibold"
                      :class="isOverdue(order) ? 'text-red-600' : isDueSoon(order) ? 'text-orange-600' : 'text-gray-900'"
                    >
                      {{ formatDeadline(order) }}
                    </span>
                  </td>
                  
                  <!-- Client -->
                  <td class="px-4 py-4 whitespace-nowrap">
                    <span class="text-sm text-gray-600">
                      {{ order.client_username || order.client?.username || order.client?.email || 'N/A' }}
                    </span>
                  </td>
                  
                  <!-- Action -->
                  <td class="px-4 py-4 whitespace-nowrap" @click.stop>
                    <button
                      v-if="activeTab !== 'available'"
                      @click="$router.push(`/orders/${order.id}`)"
                      class="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-semibold shadow-sm"
                    >
                      {{ getActionButtonText(order.status) }}
                    </button>
                    <div v-else class="flex gap-2">
                      <button
                        @click="$router.push(`/orders/${order.id}`)"
                        class="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-semibold"
              >
                View
                      </button>
                      <button
                        @click="$router.push(`/writer/queue?order=${order.id}`)"
                        class="px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-xs font-semibold"
                      >
                        Request
                      </button>
            </div>
                  </td>
                </tr>
              </tbody>
            </table>
        </div>
      </div>

        <!-- Load More / Pagination -->
        <div v-if="filteredOrders.length > 0 && (hasMoreOrders || currentPage > 1)" class="mt-6 text-center space-y-2">
          <p v-if="filteredOrders.length > 0" class="text-sm text-gray-600 mb-2">
            Showing {{ filteredOrders.length }} {{ filteredOrders.length === 1 ? 'order' : 'orders' }}
            <span v-if="hasMoreOrders">(more available)</span>
          </p>
          <button
            v-if="hasMoreOrders"
            @click="loadMoreOrders"
            :disabled="ordersLoading"
            class="px-6 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-semibold disabled:opacity-50 flex items-center gap-2 mx-auto"
          >
            <ArrowPathIcon class="w-4 h-4" :class="{ 'animate-spin': ordersLoading }" />
            Load More Orders
          </button>
              </div>
              </div>
            </div>
            
    <!-- Writer Performance Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Late Orders Card -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all">
        <div class="flex items-center justify-between mb-4">
          <div class="flex-1">
            <p class="text-sm font-semibold text-gray-600 mb-1 uppercase tracking-wide">Late Orders</p>
            <div class="flex items-baseline gap-2">
              <p class="text-4xl font-bold text-red-600">{{ lateOrdersCount }}</p>
              <p class="text-xs text-gray-500">orders</p>
          </div>
        </div>
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <span class="text-3xl font-bold text-red-600">{{ lateOrdersCount }}</span>
          </div>
            </div>
        <p class="text-xs text-gray-600 mt-2">Orders past deadline</p>
        <router-link
          v-if="lateOrdersCount > 0"
          to="/writer/orders?status=late"
          class="mt-3 inline-block text-sm font-semibold text-red-600 hover:text-red-700 underline"
        >
          View Late Orders →
        </router-link>
          </div>
          
      <!-- Overall Rating Card -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all">
          <div class="flex items-center justify-between mb-4">
          <div class="flex-1">
            <p class="text-sm font-semibold text-gray-600 mb-1 uppercase tracking-wide">Overall Rating</p>
            <div class="flex items-baseline gap-2">
              <p class="text-4xl font-bold text-yellow-600">
                {{ overallRating || 'N/A' }}
              </p>
              <p v-if="overallRating" class="text-xs text-gray-500">/ 5.0</p>
                </div>
                </div>
          <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center">
            <span v-if="overallRating" class="text-2xl font-bold text-yellow-600">{{ overallRating }}</span>
            <span v-else class="text-2xl">⭐</span>
              </div>
                </div>
        <p class="text-xs text-gray-600 mt-2">
          {{ totalReviews > 0 ? `From ${totalReviews} reviews` : 'No reviews yet' }}
        </p>
              <router-link
          v-if="totalReviews > 0"
          to="/writer/performance"
          class="mt-3 inline-block text-sm font-semibold text-yellow-600 hover:text-yellow-700 underline"
        >
          View Performance →
              </router-link>
          </div>

      <!-- Escalations Card -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all">
          <div class="flex items-center justify-between mb-4">
          <div class="flex-1">
            <p class="text-sm font-semibold text-gray-600 mb-1 uppercase tracking-wide">Escalations</p>
            <div class="flex items-baseline gap-2">
              <p class="text-4xl font-bold text-orange-600">{{ escalationsCount }}</p>
              <p class="text-xs text-gray-500">issues</p>
            </div>
          </div>
          <div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
            <span class="text-3xl font-bold text-orange-600">{{ escalationsCount }}</span>
              </div>
                    </div>
        <p class="text-xs text-gray-600 mt-2">Orders requiring attention</p>
        <router-link
          v-if="escalationsCount > 0"
          to="/writer/orders?status=escalated"
          class="mt-3 inline-block text-sm font-semibold text-orange-600 hover:text-orange-700 underline"
        >
          View Escalations →
        </router-link>
        </div>
      </div>
        
    <!-- Quick Stats Sidebar (Collapsible) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Next Deadline Widget -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Next Deadline</h3>
          <ClockIcon class="w-6 h-6 text-amber-500" />
        </div>
        <div v-if="nextDeadlineInfo">
          <p class="text-2xl font-bold text-gray-900 mb-1">
            {{ formatDate(nextDeadlineInfo.deadline) }}
          </p>
          <p class="text-sm text-gray-600 mb-2">{{ nextDeadlineInfo.topic || 'Assigned order' }}</p>
          <p class="text-xs font-semibold text-amber-600 mb-3">{{ deadlineCountdown }}</p>
          <router-link
            v-if="nextDeadlineOrderLink"
            :to="nextDeadlineOrderLink"
            class="block w-full text-center px-4 py-2 bg-amber-50 text-amber-700 rounded-lg hover:bg-amber-100 transition-colors text-sm font-semibold"
          >
            Open Order →
          </router-link>
        </div>
        <div v-else class="text-center py-4 text-gray-500">
          <p class="text-sm">No upcoming deadlines</p>
      </div>
    </div>

      <!-- Availability Toggle -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">Availability</h3>
          <component 
            :is="isAvailabilityOnline ? CheckCircleIcon : MoonIcon" 
            class="w-6 h-6"
            :class="isAvailabilityOnline ? 'text-green-500' : 'text-gray-400'"
          />
      </div>
        <p class="text-2xl font-bold mb-2" :class="isAvailabilityOnline ? 'text-green-600' : 'text-gray-600'">
          {{ isAvailabilityOnline ? 'Available' : 'On Break' }}
        </p>
        <p class="text-sm text-gray-600 mb-4">
          {{ isAvailabilityOnline ? 'You appear in the pool for instant assignments' : 'You will not auto-receive urgent orders' }}
        </p>
          <button 
          @click="toggleAvailability"
          :disabled="availabilityLoading"
          class="w-full px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          :class="isAvailabilityOnline ? 'bg-red-50 text-red-600 hover:bg-red-100' : 'bg-green-50 text-green-600 hover:bg-green-100'"
        >
          {{ isAvailabilityOnline ? 'Mark as On Break' : 'Mark as Available' }}
          </button>
    </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
        <div class="space-y-2">
          <router-link
            to="/writer/queue"
            class="flex items-center gap-3 p-3 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors group"
          >
            <div class="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-sm">
              <CursorArrowRaysIcon class="w-5 h-5" />
    </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900 group-hover:text-emerald-700">Browse Orders</p>
              <p class="text-xs text-gray-600">Find new assignments</p>
            </div>
            <svg class="w-5 h-5 text-gray-400 group-hover:text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
            <router-link
            to="/writer/payments"
            class="flex items-center gap-3 p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors group"
            >
            <div class="w-10 h-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center shadow-sm">
              <BanknotesIcon class="w-5 h-5" />
          </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900 group-hover:text-purple-700">View Payments</p>
              <p class="text-xs text-gray-600">Payment history</p>
        </div>
            <svg class="w-5 h-5 text-gray-400 group-hover:text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
          <router-link
            to="/writer/performance"
            class="flex items-center gap-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors group"
          >
            <div class="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center shadow-sm">
              <ChartBarSquareIcon class="w-5 h-5" />
        </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900 group-hover:text-blue-700">Performance</p>
              <p class="text-xs text-gray-600">View analytics</p>
      </div>
            <svg class="w-5 h-5 text-gray-400 group-hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        </router-link>
      </div>
                  </div>
                </div>
                </div>

  <!-- Availability Confirmation Dialog -->
  <ConfirmationDialog
    v-if="confirm.show.value"
    v-model:show="confirm.show"
    :title="unref(confirm.title)"
    :message="unref(confirm.message)"
    :details="unref(confirm.details)"
    :variant="unref(confirm.variant)"
    :icon="unref(confirm.icon)"
    :confirm-text="unref(confirm.confirmText)"
    :cancel-text="unref(confirm.cancelText)"
    @confirm="confirm.onConfirm"
    @cancel="confirm.onCancel"
  />
</template>

<script setup>
import { computed, ref, watch, onMounted, unref } from 'vue'
import {
  ClockIcon,
  CheckCircleIcon,
  MoonIcon,
  ArrowPathIcon,
  CursorArrowRaysIcon,
  BanknotesIcon,
  ChartBarSquareIcon,
} from '@heroicons/vue/24/outline'
import ordersAPI from '@/api/orders'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import onlineStatusAPI from '@/api/online-status'
import { useAuthStore } from '@/stores/auth'
import OrderStatusTooltip from '@/components/common/OrderStatusTooltip.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const props = defineProps({
  writerEarningsData: Object,
  writerPerformanceData: Object,
  writerQueueData: Object,
  writerBadgesData: Object,
  writerLevelData: Object,
  writerSummaryData: Object,
  writerPaymentStatus: Object,
  recentOrders: Array,
  recentOrdersLoading: Boolean,
  loading: Boolean,
  availabilityStatus: Object,
  realtimeWidgetData: Object
})

const emit = defineEmits(['order-requested', 'refresh-requested', 'availability-updated'])

const authStore = useAuthStore()
const confirm = useConfirmDialog()

// Orders state
const activeTab = ref('in_progress') // Default to In Progress tab
const ordersLoading = ref(props.recentOrdersLoading)
const allOrders = ref([...props.recentOrders])
const availableOrders = ref([])
const availableOrdersLoading = ref(false)
const orderRequests = ref([])
const orderRequestsLoading = ref(false)
const currentPage = ref(1)
const hasMoreOrders = ref(false)

// Availability state
const availabilityLoading = ref(false)
const lastAvailabilityPing = ref(null)

// Fetch all orders by status
const fetchOrdersByStatus = async (statuses = null, page = 1, includeArchived = false) => {
  ordersLoading.value = true
  try {
    const params = {
      assigned_writer: true,
      page_size: 50,
      ordering: '-created_at',
      page
    }
    
    // Include archived orders if requested
    if (includeArchived) {
      params.include_archived = true
    }
    
    if (statuses && statuses.length > 0) {
      // Backend parses status as CSV, so we can pass comma-separated values
      params.status = statuses.join(',')
    }
    
    const response = await ordersAPI.list(params)
    const orders = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
    
    if (page === 1) {
      // For page 1, replace orders for this status
      // But keep orders from other statuses that might be in allOrders
      if (statuses && statuses.length > 0) {
        // Remove orders with these statuses first (but keep archived if we're not fetching archived)
        if (!includeArchived) {
          allOrders.value = allOrders.value.filter(o => !statuses.includes(o.status) || o.is_archived)
        } else {
          allOrders.value = allOrders.value.filter(o => !statuses.includes(o.status))
        }
        // Then add new orders
        allOrders.value = [...allOrders.value, ...orders]
      } else if (includeArchived) {
        // For archived orders, replace all archived orders
        allOrders.value = allOrders.value.filter(o => !o.is_archived)
        allOrders.value = [...allOrders.value, ...orders]
      } else {
        // For "all orders" (non-archived), replace everything
        allOrders.value = orders.filter(o => !o.is_archived)
      }
    } else {
      // For subsequent pages, append new orders (avoiding duplicates)
      const existingIds = new Set(allOrders.value.map(o => o.id))
      const newOrders = orders.filter(o => !existingIds.has(o.id))
      allOrders.value = [...allOrders.value, ...newOrders]
    }
    
    hasMoreOrders.value = response.data?.next ? true : false
  } catch (err) {
    console.error('Failed to fetch orders:', err)
    if (page === 1) {
      // Only clear on first page error
      if (!statuses || statuses.length === 0) {
        allOrders.value = []
      }
    }
  } finally {
    ordersLoading.value = false
  }
}

// Fetch available orders (orders writer can request/take)
// Only shows unassigned, paid orders that haven't been assigned to any writer
const fetchAvailableOrders = async () => {
  availableOrdersLoading.value = true
  try {
    // Get available orders from queue data (these are already filtered to be unassigned and paid)
    if (props.writerQueueData?.available_orders) {
      // Filter to ensure only unassigned orders
      availableOrders.value = props.writerQueueData.available_orders.filter(
        order => !order.assigned_writer && order.is_paid && order.status === 'available'
      )
    } else {
      // Fallback: fetch orders with status 'available', unassigned, and paid
      const params = {
        status: 'available',
        assigned_writer: false, // Explicitly unassigned
        is_paid: true,
        page_size: 100,
        ordering: '-created_at'
      }
      const response = await ordersAPI.list(params)
      const orders = Array.isArray(response.data?.results) 
        ? response.data.results 
        : (Array.isArray(response.data) ? response.data : [])
      // Double-check they're unassigned
      availableOrders.value = orders.filter(
        order => !order.assigned_writer && order.is_paid
      )
    }
  } catch (err) {
    console.error('Failed to fetch available orders:', err)
    availableOrders.value = []
  } finally {
    availableOrdersLoading.value = false
  }
}

// Fetch order requests (orders the writer has requested)
const fetchOrderRequests = async () => {
  orderRequestsLoading.value = true
  try {
    const response = await writerDashboardAPI.getOrderRequests()
    if (response?.data) {
      // Get orders from requests, filter out those assigned to other writers
      const requests = response.data.requests || response.data.order_requests || []
      const requestOrders = requests
        .map(req => {
          // Handle both direct order objects and request objects with order property
          const order = req.order || req
          return {
            ...order,
            request_status: req.approved ? 'approved' : (req.status || 'pending'),
            request_id: req.id,
            requested_at: req.requested_at || req.created_at
          }
        })
        .filter(order => {
          // Remove requests where order is assigned to another writer
          if (order.assigned_writer) {
            const assignedWriterId = typeof order.assigned_writer === 'object' 
              ? order.assigned_writer.id 
              : order.assigned_writer
            const currentUserId = authStore.user?.id
            
            // If assigned to another writer, remove from requests
            if (assignedWriterId !== currentUserId) {
              return false
            }
            // If assigned to current writer and approved, it should move to In Progress
            // Keep it here if request is still pending
            if (order.request_status === 'approved' && assignedWriterId === currentUserId) {
              // This will be handled in In Progress tab
              return false
            }
          }
          return true
        })
      orderRequests.value = requestOrders
    } else {
      orderRequests.value = []
    }
  } catch (err) {
    console.error('Failed to fetch order requests:', err)
    orderRequests.value = []
  } finally {
    orderRequestsLoading.value = false
  }
}

// Order tabs configuration with colors
const orderTabs = computed(() => {
  // Define status groups
  const assignedStatuses = ['assigned', 'pending_writer_assignment'] // Can still reject/accept
  const inProgressStatuses = ['in_progress', 'under_editing', 'submitted'] // Actively working
  const revisionStatuses = ['revision_requested', 'on_revision']
  const completedStatuses = ['completed']
  const cancelledStatuses = ['cancelled']
  const closedStatuses = ['closed'] // Deadline passed, not rated
  
  const tabs = [
    {
      id: 'available',
      label: 'Available',
      statuses: null, // Special case - uses availableOrders (unassigned, paid)
      count: availableOrders.value.length,
      color: 'bg-blue-500',
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      description: 'Paid orders you can request or take'
    },
    {
      id: 'assigned',
      label: 'Assigned',
      statuses: assignedStatuses,
      count: allOrders.value.filter(o => 
        assignedStatuses.includes(o.status) && 
        o.assigned_writer && 
        !inProgressStatuses.includes(o.status)
      ).length,
      color: 'bg-indigo-500',
      textColor: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
      description: 'Orders assigned to you (can accept/reject)'
    },
    {
      id: 'order_requests',
      label: 'Order Requests',
      statuses: null, // Special case - uses orderRequests
      count: orderRequests.value.length,
      color: 'bg-cyan-500',
      textColor: 'text-cyan-600',
      bgColor: 'bg-cyan-50',
      borderColor: 'border-cyan-200',
      description: 'Orders you have requested'
    },
    {
      id: 'in_progress',
      label: 'In Progress',
      statuses: inProgressStatuses,
      count: allOrders.value.filter(o => 
        inProgressStatuses.includes(o.status) && 
        o.assigned_writer
      ).length,
      color: 'bg-emerald-500',
      textColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
      borderColor: 'border-emerald-200',
      description: 'Orders you are actively working on'
    },
    {
      id: 'revision_requests',
      label: 'Revision Requests',
      statuses: revisionStatuses,
      count: allOrders.value.filter(o => revisionStatuses.includes(o.status)).length,
      color: 'bg-orange-500',
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      description: 'Orders requiring revision'
    },
    {
      id: 'completed',
      label: 'Completed',
      statuses: completedStatuses,
      count: allOrders.value.filter(o => completedStatuses.includes(o.status)).length,
      color: 'bg-green-500',
      textColor: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      description: 'Orders you have submitted'
    },
    {
      id: 'disputed',
      label: 'Disputed',
      statuses: ['disputed'],
      count: allOrders.value.filter(o => o.status === 'disputed').length,
      color: 'bg-red-500',
      textColor: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      description: 'Orders under dispute'
    },
    {
      id: 'on_hold',
      label: 'On Hold',
      statuses: ['on_hold'],
      count: allOrders.value.filter(o => o.status === 'on_hold').length,
      color: 'bg-amber-500',
      textColor: 'text-amber-600',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      description: 'Orders on hold'
    },
    {
      id: 'cancelled',
      label: 'Cancelled',
      statuses: cancelledStatuses,
      count: allOrders.value.filter(o => cancelledStatuses.includes(o.status)).length,
      color: 'bg-gray-500',
      textColor: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      description: 'Cancelled orders'
    },
    {
      id: 'closed',
      label: 'Closed',
      statuses: closedStatuses,
      count: allOrders.value.filter(o => closedStatuses.includes(o.status)).length,
      color: 'bg-slate-500',
      textColor: 'text-slate-600',
      bgColor: 'bg-slate-50',
      borderColor: 'border-slate-200',
      description: 'Deadline passed, not rated (candidates for archiving)'
    },
    {
      id: 'archived',
      label: 'Archived',
      statuses: null, // Special case - uses is_archived flag
      count: allOrders.value.filter(o => o.is_archived === true).length,
      color: 'bg-slate-600',
      textColor: 'text-slate-700',
      bgColor: 'bg-slate-100',
      borderColor: 'border-slate-300',
      description: 'Archived orders (view only, locked)'
    },
    {
      id: 'all',
      label: 'All Orders',
      statuses: null,
      count: allOrders.value.length,
      color: 'bg-gray-600',
      textColor: 'text-gray-700',
      bgColor: 'bg-gray-100',
      borderColor: 'border-gray-300'
    }
  ]
  
  return tabs
})

// Filtered orders based on active tab
const filteredOrders = computed(() => {
  const tab = orderTabs.value.find(t => t.id === activeTab.value)
  if (!tab) return []
  
  const currentUserId = authStore.user?.id
  
  // Special case for available orders (unassigned, paid orders)
  if (tab.id === 'available') {
    return availableOrders.value.filter(o => 
      !o.assigned_writer && 
      o.is_paid && 
      o.status === 'available' &&
      !o.is_archived
    )
  }
  
  // Special case for assigned orders (can still reject/accept)
  if (tab.id === 'assigned') {
    const assignedStatuses = ['assigned', 'pending_writer_assignment']
    return allOrders.value.filter(o => {
      if (o.is_archived) return false
      if (!assignedStatuses.includes(o.status)) return false
      // Must be assigned to current writer
      const assignedWriterId = typeof o.assigned_writer === 'object' ? o.assigned_writer.id : o.assigned_writer
      if (assignedWriterId !== currentUserId) return false
      // Exclude if already in progress
      if (['in_progress', 'under_editing', 'submitted'].includes(o.status)) return false
      return true
    })
  }
  
  // Special case for order requests
  if (tab.id === 'order_requests') {
    return orderRequests.value.filter(o => !o.is_archived)
  }
  
  // Special case for in progress (actively working)
  if (tab.id === 'in_progress') {
    const inProgressStatuses = ['in_progress', 'under_editing', 'submitted']
    return allOrders.value.filter(o => {
      if (o.is_archived) return false
      if (!inProgressStatuses.includes(o.status)) return false
      // Must be assigned to current writer
      const assignedWriterId = typeof o.assigned_writer === 'object' ? o.assigned_writer.id : o.assigned_writer
      return assignedWriterId === currentUserId
    })
  }
  
  // Special case for revision requests
  if (tab.id === 'revision_requests') {
    const revisionStatuses = ['revision_requested', 'on_revision']
    return allOrders.value.filter(o => {
      if (o.is_archived) return false
      if (!revisionStatuses.includes(o.status)) return false
      // Must be assigned to current writer
      const assignedWriterId = typeof o.assigned_writer === 'object' ? o.assigned_writer.id : o.assigned_writer
      return assignedWriterId === currentUserId
    })
  }
  
  // Special case for archived orders
  if (tab.id === 'archived') {
    return allOrders.value.filter(o => o.is_archived === true)
  }
  
  // Filter by status for other tabs
  if (tab.statuses) {
    return allOrders.value.filter(o => {
      if (o.is_archived && tab.id !== 'archived') return false
      if (!tab.statuses.includes(o.status)) return false
      // For assigned orders, ensure they belong to current writer
      if (tab.id === 'completed' || tab.id === 'disputed' || tab.id === 'on_hold' || tab.id === 'cancelled' || tab.id === 'closed') {
        const assignedWriterId = typeof o.assigned_writer === 'object' ? o.assigned_writer.id : o.assigned_writer
        return assignedWriterId === currentUserId
      }
      return true
    })
  }
  
  // All orders (excluding archived unless it's the all tab)
  if (tab.id === 'all') {
    return allOrders.value
  }
  
  return []
})

// Order counts
const activeOrdersCount = computed(() => {
  return allOrders.value.filter(o => 
    ['in_progress', 'under_editing', 'on_hold', 'submitted', 'revision_requested', 'on_revision'].includes(o.status)
  ).length
})

const inProgressCount = computed(() => {
  return allOrders.value.filter(o => o.status === 'in_progress').length
})

// Late Orders Count (orders past deadline)
const lateOrdersCount = computed(() => {
  const now = new Date()
  return allOrders.value.filter(order => {
    const deadline = order.writer_deadline || order.client_deadline || order.deadline
    if (!deadline) return false
    const deadlineDate = new Date(deadline)
    // Only count active orders that are past deadline
    const isActive = ['in_progress', 'under_editing', 'on_revision', 'revision_requested', 'submitted'].includes(order.status)
    return isActive && deadlineDate < now
  }).length
})

// Overall Rating
const overallRating = computed(() => {
  const rating = props.writerPerformanceData?.avg_rating
  if (!rating || rating === 0) return null
  return rating.toFixed(1)
})

// Total Reviews
const totalReviews = computed(() => {
  return props.writerPerformanceData?.total_reviews || 0
})

// Escalations Count (disputed orders + orders with escalation flags)
const escalationsCount = computed(() => {
  // Count disputed orders
  const disputed = allOrders.value.filter(o => o.status === 'disputed').length
  // Could also check for escalation flags if they exist in the order data
  // For now, we'll use disputed orders as escalations
  return disputed
})

// Watch active tab and fetch orders
watch(activeTab, async (newTab) => {
  const tab = orderTabs.value.find(t => t.id === newTab)
  if (tab) {
    currentPage.value = 1
    if (tab.id === 'available') {
      await fetchAvailableOrders()
    } else if (tab.id === 'order_requests') {
      await fetchOrderRequests()
    } else if (tab.id === 'archived') {
      // For archived orders, fetch with include_archived flag
      await fetchOrdersByStatus(null, 1, true)
    } else if (tab.id === 'all') {
      // For "all orders", fetch without status filter (excluding archived by default)
      await fetchOrdersByStatus(null, 1, false)
    } else if (tab.statuses) {
      // Fetch orders for specific statuses (excluding archived)
      await fetchOrdersByStatus(tab.statuses, 1, false)
    }
  }
}, { immediate: false })

// Watch for changes in recentOrders prop
watch(() => props.recentOrders, (newOrders) => {
  if (newOrders && newOrders.length > 0) {
    // Merge with existing orders, avoiding duplicates
    const existingIds = new Set(allOrders.value.map(o => o.id))
    const newUniqueOrders = newOrders.filter(o => !existingIds.has(o.id))
    allOrders.value = [...allOrders.value, ...newUniqueOrders]
  }
}, { deep: true })

watch(() => props.recentOrdersLoading, (loading) => {
  ordersLoading.value = loading
})

// Load more orders
const loadMoreOrders = async () => {
  const tab = orderTabs.value.find(t => t.id === activeTab.value)
  if (tab && hasMoreOrders.value) {
    currentPage.value++
    if (tab.id === 'available' || tab.id === 'order_requests') {
      // For available orders and requests, we might need to fetch more from queue
      // For now, these are usually limited, so we'll skip pagination
      hasMoreOrders.value = false
    } else if (tab.id === 'archived') {
      await fetchOrdersByStatus(null, currentPage.value, true)
    } else if (tab.id === 'all') {
      await fetchOrdersByStatus(null, currentPage.value, false)
    } else if (tab.statuses) {
      await fetchOrdersByStatus(tab.statuses, currentPage.value, false)
    }
  }
}

// Refresh orders
const refreshOrders = async () => {
  const tab = orderTabs.value.find(t => t.id === activeTab.value)
  if (tab) {
    currentPage.value = 1
    if (tab.id === 'available') {
      await fetchAvailableOrders()
    } else if (tab.id === 'order_requests') {
      await fetchOrderRequests()
    } else if (tab.id === 'archived') {
      await fetchOrdersByStatus(null, 1, true)
    } else if (tab.id === 'all') {
      await fetchOrdersByStatus(null, 1, false)
    } else if (tab.statuses) {
      await fetchOrdersByStatus(tab.statuses, 1, false)
    }
  }
  // Also emit to parent to refresh
  emit('refresh-requested', { scope: 'orders' })
}

// Format functions
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  })
}

const formatDeadline = (order) => {
  const deadline = order.writer_deadline || order.client_deadline || order.deadline
  if (!deadline) return 'No deadline'
  
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const diffMs = deadlineDate - now
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffHours < 0) return 'Overdue'
  if (diffHours < 24) return `${diffHours}h remaining`
  if (diffDays < 7) return `${diffDays}d remaining`
  
  return deadlineDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

const isOverdue = (order) => {
  const deadline = order.writer_deadline || order.client_deadline || order.deadline
  if (!deadline) return false
  return new Date(deadline) < new Date()
}

const isDueSoon = (order) => {
  const deadline = order.writer_deadline || order.client_deadline || order.deadline
  if (!deadline) return false
  const hours = (new Date(deadline) - new Date()) / 3600000
  // Consider "due soon" if deadline is within 48 hours (2 days)
  return hours > 0 && hours <= 48
}

const isInProgress = (order) => {
  // Treat only truly active states as “in progress” for overdue highlighting.
  // Submitted / approved / closed should NOT be marked as overdue.
  const inProgressStatuses = ['in_progress', 'under_editing', 'on_revision', 'revision_requested', 'assigned']
  return inProgressStatuses.includes(order.status)
}

const getShortTitle = (order) => {
  const base = order.topic || 'Untitled Order'
  const maxLength = 50
  if (base.length <= maxLength) return base
  return base.slice(0, maxLength) + '…'
}

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getOrderStatusClass = (status) => {
  const statusMap = {
    'in_progress': 'bg-blue-100 text-blue-800',
    'under_editing': 'bg-indigo-100 text-indigo-800',
    'submitted': 'bg-purple-100 text-purple-800',
    'revision_requested': 'bg-orange-100 text-orange-800',
    'on_revision': 'bg-orange-100 text-orange-800',
    'completed': 'bg-green-100 text-green-800',
    'approved': 'bg-green-100 text-green-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'on_hold': 'bg-gray-100 text-gray-800',
    'disputed': 'bg-red-100 text-red-800',
    'cancelled': 'bg-red-100 text-red-800',
  }
  return statusMap[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const getActionButtonText = (status) => {
  const statusMap = {
    'in_progress': 'Continue Working',
    'under_editing': 'View Order',
    'submitted': 'View Order',
    'revision_requested': 'Start Revision',
    'on_revision': 'Continue Revision',
    'completed': 'View Order',
    'pending': 'Start Working',
  }
  return statusMap[status?.toLowerCase()] || 'View Order'
}

const getActiveTabLabel = () => {
  const tab = orderTabs.value.find(t => t.id === activeTab.value)
  return tab?.label.toLowerCase() || 'orders'
}

const getEmptyStateMessage = () => {
  const messages = {
    'available': 'No available orders at the moment. Check back soon!',
    'assigned': 'No orders assigned to you at the moment.',
    'order_requests': 'You haven\'t requested any orders yet. Browse available orders to get started!',
    'in_progress': 'You have no orders in progress. Browse available orders to get started!',
    'revision_requests': 'Great! No revision requests at the moment.',
    'completed': 'You haven\'t completed any orders yet.',
    'disputed': 'Great! No disputed orders.',
    'on_hold': 'No orders on hold.',
    'cancelled': 'No cancelled orders.',
    'closed': 'No closed orders.',
    'archived': 'No archived orders.',
    'all': 'You don\'t have any orders yet. Browse available orders to get started!'
  }
  return messages[activeTab.value] || 'No orders found.'
}

// Next deadline info
const nextDeadlineInfo = computed(() => {
  const deadlines = []
  allOrders.value.forEach(order => {
    const deadline = order.writer_deadline || order.deadline || order.client_deadline
    if (deadline && !['completed', 'approved', 'closed', 'cancelled'].includes(order.status)) {
      deadlines.push({
        deadline,
        orderId: order.id,
        topic: order.topic,
      })
    }
  })
  if (!deadlines.length) return null
  return deadlines.sort((a, b) => new Date(a.deadline) - new Date(b.deadline))[0]
})

const nextDeadlineOrderLink = computed(() => {
  return nextDeadlineInfo.value ? `/orders/${nextDeadlineInfo.value.orderId}` : null
})

const deadlineCountdown = computed(() => {
  if (!nextDeadlineInfo.value) return 'No deadlines'
  const deadline = new Date(nextDeadlineInfo.value.deadline)
  const now = new Date()
  const diffMs = deadline - now
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMs < 0) return 'Overdue!'
  if (diffHours < 24) return `${diffHours}h remaining`
  if (diffDays < 7) return `${diffDays}d remaining`
  return deadline.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
})

// Availability
const isAvailabilityOnline = computed(() => {
  return props.availabilityStatus?.is_online ?? false
})

const availabilityMessage = computed(() => {
  return props.availabilityStatus?.message || null
})

const toggleAvailability = async () => {
  const newStatus = !isAvailabilityOnline.value

  // When going online, require an explicit confirmation so writers
  // understand the consequences of being marked as available.
  if (newStatus) {
    const confirmed = await confirm.showWarning(
      'When you mark yourself as available, you may start receiving urgent or instant assignments. Make sure you are ready to accept and complete new orders on time.',
      'Mark yourself as available?',
      {
        details:
          '• You will appear in the pool for instant assignments.\n' +
          '• New orders can be routed to you automatically while you are online.\n' +
          '• Only stay available when you actively intend to take and complete orders.\n' +
          '• Switch back to “On Break” to stop automatic assignments.',
        confirmText: "Yes, I'm available",
        cancelText: 'Cancel',
        icon: '⚡',
      }
    )

    if (!confirmed) {
      return
    }
  }

    availabilityLoading.value = true
  try {
    await onlineStatusAPI.updateAvailability({
      is_online: newStatus,
    })
    emit('availability-updated', { is_online: newStatus })
    lastAvailabilityPing.value = new Date()
  } catch (err) {
    console.error('Failed to toggle availability:', err)
  } finally {
      availabilityLoading.value = false
  }
}

// Fetch all orders for the writer (for counting and filtering)
const fetchAllWriterOrders = async () => {
  try {
    // Fetch non-archived orders
    const params = {
      assigned_writer: true,
      page_size: 100, // Get more orders for accurate counts
      ordering: '-created_at',
      include_archived: false
    }
    
    const response = await ordersAPI.list(params)
    const orders = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
    
    // Merge with existing orders, avoiding duplicates
    const existingIds = new Set(allOrders.value.map(o => o.id))
    const newOrders = orders.filter(o => !existingIds.has(o.id))
    allOrders.value = [...allOrders.value, ...newOrders]
    
    // If there are more pages, fetch them too (for accurate counts)
    if (response.data?.next) {
      let nextPage = 2
      while (nextPage <= 5) { // Limit to 5 pages to avoid too many requests
        try {
          const nextResponse = await ordersAPI.list({ ...params, page: nextPage })
          const nextOrders = Array.isArray(nextResponse.data?.results) 
            ? nextResponse.data.results 
            : (Array.isArray(nextResponse.data) ? nextResponse.data : [])
          
          if (nextOrders.length === 0) break
          
          const newNextOrders = nextOrders.filter(o => !existingIds.has(o.id))
          allOrders.value = [...allOrders.value, ...newNextOrders]
          nextOrders.forEach(o => existingIds.add(o.id))
          
          if (!nextResponse.data?.next) break
          nextPage++
        } catch (err) {
          console.error(`Failed to fetch page ${nextPage}:`, err)
          break
        }
      }
    }
    
    // Also fetch archived orders separately for the archived tab count
    try {
      const archivedParams = {
        assigned_writer: true,
        page_size: 100,
        ordering: '-created_at',
        include_archived: true
      }
      const archivedResponse = await ordersAPI.list(archivedParams)
      const archivedOrders = Array.isArray(archivedResponse.data?.results) 
        ? archivedResponse.data.results.filter(o => o.is_archived === true)
        : (Array.isArray(archivedResponse.data) ? archivedResponse.data.filter(o => o.is_archived === true) : [])
      
      // Merge archived orders
      const newArchivedOrders = archivedOrders.filter(o => !existingIds.has(o.id))
      allOrders.value = [...allOrders.value, ...newArchivedOrders]
    } catch (err) {
      console.error('Failed to fetch archived orders:', err)
    }
  } catch (err) {
    console.error('Failed to fetch all writer orders:', err)
  }
}

// Initialize
onMounted(async () => {
  // Fetch all orders first for accurate counts
  await fetchAllWriterOrders()
  
  // If we already have orders from props, merge them
  if (props.recentOrders && props.recentOrders.length > 0) {
    const existingIds = new Set(allOrders.value.map(o => o.id))
    const newOrders = props.recentOrders.filter(o => !existingIds.has(o.id))
    allOrders.value = [...allOrders.value, ...newOrders]
  }
  
  // Load in progress orders by default
  const inProgressStatuses = ['in_progress', 'under_editing', 'submitted']
  await fetchOrdersByStatus(inProgressStatuses, 1)
  
  // Fetch available orders
  await fetchAvailableOrders()
  
  // Fetch order requests
  await fetchOrderRequests()
})

// Watch for queue data changes to update available orders
watch(() => props.writerQueueData, (newQueueData) => {
  if (newQueueData?.available_orders) {
    availableOrders.value = newQueueData.available_orders
  }
}, { deep: true, immediate: true })
</script>
