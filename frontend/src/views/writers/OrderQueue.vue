<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Queue</h1>
        <p class="mt-2 text-gray-600">Browse and request available orders</p>
      </div>
      <button @click="loadQueue" :disabled="loading" class="btn btn-secondary">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Available Orders</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.available_count || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Preferred Orders</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.preferred_count || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">My Requests</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.requests_count || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.approved_count || 0 }}</p>
      </div>
    </div>

    <!-- Take Capacity -->
    <div class="bg-white rounded-lg shadow-sm border border-primary-100 p-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="text-sm font-medium text-primary-600 uppercase tracking-wide">Level Capacity</p>
        <p class="text-xl font-semibold text-gray-900 mt-1">
          {{ levelDetails?.name || 'Unranked' }}
        </p>
        <p class="text-sm text-gray-600">
          Active orders: <span class="font-semibold text-gray-900">{{ takeCapacity.active }}</span> / {{ takeCapacity.maxOrders }}
          ({{ takeCapacity.remaining }} slots remaining)
        </p>
      </div>
      <div class="text-sm text-gray-600">
        <p v-if="!takesEnabled" class="text-red-600 font-medium">
          Taking orders directly is currently disabled by admins. Please request orders instead.
        </p>
        <p v-else-if="takeCapacity.remaining <= 0" class="text-yellow-700 font-medium">
          You’ve reached your current limit. Submit work or request a hold before taking another order.
        </p>
        <p v-else class="text-green-700 font-medium">
          You can take up to {{ takeCapacity.remaining }} more order{{ takeCapacity.remaining === 1 ? '' : 's' }} right now.
        </p>
        <p class="text-xs text-gray-500 mt-2">
          Order holds temporarily freeze deadlines while you wait for client input.
        </p>
      </div>
    </div>

    <!-- Recommended Orders -->
    <div
      v-if="recommendedOrders.length"
      class="bg-white rounded-lg shadow-sm border border-blue-100 p-6"
    >
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p class="text-xs font-semibold text-blue-600 uppercase tracking-wide">Smart Picks</p>
          <h2 class="text-2xl font-bold text-gray-900">Recommended For You</h2>
          <p class="text-sm text-gray-500">Based on your skills, subject preferences, and earning potential.</p>
        </div>
        <button
          class="text-sm font-semibold text-primary-600 hover:text-primary-800"
          @click="activeTab = 'available'"
        >
          View full queue →
        </button>
      </div>
      <div class="mt-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="order in recommendedOrders.slice(0, 6)"
          :key="`recommended-${order.id}`"
          class="border rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow bg-gradient-to-br from-blue-50 to-white"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs text-gray-500">Order #{{ order.id }}</p>
              <p class="text-base font-semibold text-gray-900">{{ order.topic || 'Untitled order' }}</p>
            </div>
            <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full font-semibold">
              Match {{ Math.round(order.match_score || 0) }}%
            </span>
          </div>
          <p class="text-sm text-gray-600 mt-1">{{ order.subject || order.service_type || 'General' }}</p>

          <div class="grid grid-cols-2 gap-3 text-sm text-gray-600 mt-4">
            <div>
              <p class="text-xs uppercase text-gray-400">Potential payout</p>
              <p class="text-green-700 font-semibold">${{ formatCurrency(order.potential_payout) }}</p>
            </div>
            <div>
              <p class="text-xs uppercase text-gray-400">Deadline</p>
              <p class="font-semibold text-gray-900">{{ formatDate(order.deadline) }}</p>
            </div>
          </div>

          <div v-if="order.match_tags?.length" class="flex flex-wrap gap-2 mt-4">
            <span
              v-for="tag in order.match_tags.slice(0, 3)"
              :key="`${order.id}-${tag}`"
              class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium"
            >
              {{ tag }}
            </span>
          </div>

          <div class="flex gap-2 mt-5">
            <button @click="viewOrder(order)" class="flex-1 btn btn-secondary text-sm">
              View
            </button>
            <button
              @click="takeOrder(order)"
              :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders || isOrderRequested(order)"
              class="flex-1 btn btn-primary text-sm"
              :title="!canTakeOrders ? 'You have reached your order limit' : (isOrderRequested(order) ? 'You have already requested this order' : 'Take this order immediately')"
            >
              {{ takingOrder === order.id ? 'Taking...' : 'Take' }}
            </button>
            <button
              @click="openRequestModal(order)"
              :disabled="isOrderRequested(order) || requestingOrder === order.id || takingOrder === order.id"
              class="flex-1 btn btn-primary text-sm"
              :title="isOrderRequested(order) ? 'You have already requested this order' : 'Request this order (requires admin approval)'"
            >
              {{ isOrderRequested(order) ? 'Requested' : (requestingOrder === order.id ? 'Requesting...' : 'Request') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow-sm">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'available'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'available'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Available Orders ({{ availableOrders.length }})
          </button>
          <button
            @click="activeTab = 'preferred'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'preferred'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Preferred Orders ({{ preferredOrders.length }})
          </button>
          <button
            @click="activeTab = 'requests'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'requests'
                ? 'border-yellow-500 text-yellow-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            My Requests ({{ allRequests.length }})
          </button>
        </nav>
      </div>

      <!-- Filters -->
      <div class="p-4 border-b border-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Service Type</label>
            <select v-model="filters.service_type" @change="filterOrders" class="w-full border rounded px-3 py-2">
              <option value="">All Types</option>
              <option v-for="type in serviceTypes" :key="type" :value="type">{{ type }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Min Price</label>
            <input v-model.number="filters.min_price" type="number" @input="filterOrders" class="w-full border rounded px-3 py-2" placeholder="0" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Max Pages</label>
            <input v-model.number="filters.max_pages" type="number" @input="filterOrders" class="w-full border rounded px-3 py-2" placeholder="Any" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Sort By</label>
            <select v-model="sortOption" class="w-full border rounded px-3 py-2">
              <option value="default">Newest first</option>
              <option value="payout_desc">Potential payout (high → low)</option>
              <option value="deadline_asc">Deadline (soonest)</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Available Orders Tab -->
      <div v-if="activeTab === 'available'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="filteredAvailableOrders.length === 0" class="text-center py-12 text-gray-500">
          <p>No available orders found</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="order in filteredAvailableOrders"
            :key="order.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between mb-2">
              <h3 class="font-semibold text-gray-900">Order #{{ order.id }}</h3>
              <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">{{ order.service_type }}</span>
            </div>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ order.topic || 'No topic' }}</p>
            <div class="space-y-1 text-sm text-gray-500 mb-4">
              <div class="flex justify-between">
                <span>Pages:</span>
                <span class="font-medium">{{ order.pages }}</span>
              </div>
              <div class="flex justify-between">
                <span>Price:</span>
                <span class="font-medium text-green-600">${{ order.price?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="flex justify-between">
                <span>Potential payout:</span>
                <span class="font-medium text-green-700">${{ formatCurrency(order.potential_payout) }}</span>
              </div>
              <div class="flex justify-between">
                <span>Deadline:</span>
                <span class="font-medium">{{ formatDate(order.deadline) }}</span>
              </div>
            </div>
            <div v-if="order.match_tags?.length" class="flex flex-wrap gap-2 mt-3">
              <span
                v-for="tag in order.match_tags.slice(0, 3)"
                :key="`${order.id}-tag-${tag}`"
                class="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
              >
                {{ tag }}
              </span>
            </div>
            <div class="flex space-x-2">
              <button @click="viewOrder(order)" class="flex-1 btn btn-secondary text-sm">View</button>
              <button 
                @click="takeOrder(order)" 
                :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders" 
                class="flex-1 btn btn-primary text-sm"
              >
                {{ takingOrder === order.id ? 'Taking...' : 'Take Order' }}
              </button>
              <button 
                @click="requestOrder(order)" 
                :disabled="requestingOrder === order.id || takingOrder === order.id" 
                class="flex-1 btn btn-primary text-sm"
              >
                {{ requestingOrder === order.id ? 'Requesting...' : 'Request' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Preferred Orders Tab -->
      <div v-if="activeTab === 'preferred'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="filteredPreferredOrders.length === 0" class="text-center py-12 text-gray-500">
          <p>No preferred orders found</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="order in filteredPreferredOrders"
            :key="order.id"
            class="border rounded-lg p-4 hover:shadow-md transition-shadow border-purple-200 bg-purple-50"
          >
            <div class="flex items-start justify-between mb-2">
              <h3 class="font-semibold text-gray-900">Order #{{ order.id }}</h3>
              <span class="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">⭐ Preferred</span>
            </div>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ order.topic || 'No topic' }}</p>
            <div class="space-y-1 text-sm text-gray-500 mb-4">
              <div class="flex justify-between">
                <span>Pages:</span>
                <span class="font-medium">{{ order.pages }}</span>
              </div>
              <div class="flex justify-between">
                <span>Price:</span>
                <span class="font-medium text-green-600">${{ order.price?.toFixed(2) || '0.00' }}</span>
              </div>
              <div class="flex justify-between">
                <span>Potential payout:</span>
                <span class="font-medium text-green-700">${{ formatCurrency(order.potential_payout) }}</span>
              </div>
              <div class="flex justify-between">
                <span>Deadline:</span>
                <span class="font-medium">{{ formatDate(order.deadline) }}</span>
              </div>
            </div>
            <div v-if="order.match_tags?.length" class="flex flex-wrap gap-2 mt-3">
              <span
                v-for="tag in order.match_tags.slice(0, 3)"
                :key="`${order.id}-pref-tag-${tag}`"
                class="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
              >
                {{ tag }}
              </span>
            </div>
            <div class="flex space-x-2">
              <button @click="viewOrder(order)" class="flex-1 btn btn-secondary text-sm">View</button>
              <button 
                @click="takeOrder(order)" 
                :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders" 
                class="flex-1 btn btn-primary text-sm"
              >
                {{ takingOrder === order.id ? 'Taking...' : 'Take Order' }}
              </button>
              <button 
                @click="requestOrder(order)" 
                :disabled="requestingOrder === order.id || takingOrder === order.id" 
                class="flex-1 btn btn-primary text-sm"
              >
                {{ requestingOrder === order.id ? 'Requesting...' : 'Request' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- My Requests Tab -->
      <div v-if="activeTab === 'requests'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="allRequests.length === 0" class="text-center py-12 text-gray-500">
          <p>No requests found</p>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topic</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requested</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in allRequests" :key="request.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ request.order_id }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ request.order_topic || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getRequestStatusBadgeClass(request)" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ getRequestStatus(request) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(request.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewOrder({ id: request.order_id })" class="text-blue-600 hover:text-blue-900">View Order</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="selectedOrder" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Order #{{ selectedOrder.id }}</h2>
            <button @click="selectedOrder = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <p class="text-sm text-gray-900">{{ selectedOrder.service_type }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pages</label>
              <p class="text-sm text-gray-900">{{ selectedOrder.pages }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Price</label>
              <p class="text-sm text-gray-900 font-semibold text-green-600">${{ selectedOrder.price?.toFixed(2) || '0.00' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedOrder.deadline) }}</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Topic</label>
            <p class="text-sm text-gray-900">{{ selectedOrder.topic || 'No topic provided' }}</p>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="selectedOrder = null" class="btn btn-secondary">Close</button>
          <button 
            v-if="takesEnabled && !isOrderRequested(selectedOrder)" 
            @click="takeOrder(selectedOrder)" 
            :disabled="takingOrder === selectedOrder.id || requestingOrder === selectedOrder.id || !canTakeOrders" 
            class="btn btn-primary"
            :title="!canTakeOrders ? 'You have reached your order limit' : 'Take this order immediately'"
          >
            {{ takingOrder === selectedOrder.id ? 'Taking...' : 'Take Order' }}
          </button>
          <button 
            v-if="!isOrderRequested(selectedOrder)"
            @click="openRequestModal(selectedOrder)" 
            :disabled="requestingOrder === selectedOrder.id || takingOrder === selectedOrder.id" 
            class="btn btn-primary"
            title="Request this order (requires admin approval)"
          >
            {{ requestingOrder === selectedOrder.id ? 'Requesting...' : 'Request Order' }}
          </button>
          <button 
            v-else
            disabled
            class="btn btn-secondary cursor-not-allowed flex items-center gap-2"
            title="You have already requested this order. Waiting for admin review."
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Already Requested
          </button>
        </div>
      </div>
    </div>

    <!-- Order Request Modal -->
    <Modal
      v-model:visible="showRequestModal"
      title="Request Order"
      size="md"
      @update:visible="closeRequestModal"
    >
      <div v-if="selectedOrderForRequest" class="space-y-4">
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h3 class="font-semibold text-gray-900 mb-2">Order #{{ selectedOrderForRequest.id }}</h3>
          <p class="text-sm text-gray-600">{{ selectedOrderForRequest.topic }}</p>
          <div class="mt-2 text-sm text-gray-500">
            <span>{{ selectedOrderForRequest.service_type }}</span>
            <span class="mx-2">•</span>
            <span>{{ (selectedOrderForRequest.pages || selectedOrderForRequest.number_of_pages || 0) }} pages</span>
            <span class="mx-2">•</span>
            <span class="font-semibold text-green-600">${{ (selectedOrderForRequest.price || 0).toFixed(2) }}</span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason for Request <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="requestReason"
            rows="4"
            placeholder="Please explain why you're interested in this order (e.g., your expertise in this topic, availability, previous experience with similar orders, etc.)"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            required
          ></textarea>
          <p class="mt-1 text-xs text-gray-500">
            This helps admins make informed assignment decisions.
          </p>
        </div>
      </div>

      <template #footer>
        <button
          @click="closeRequestModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="requestOrder"
          :disabled="!requestReason || !requestReason.trim() || requestingOrder === selectedOrderForRequest?.id"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ requestingOrder === selectedOrderForRequest?.id ? 'Submitting...' : 'Submit Request' }}
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import writerDashboardAPI from '@/api/writer-dashboard'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import writerManagementAPI from '@/api/writer-management'
import ordersAPI from '@/api/orders'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess, warning: showWarning } = useToast()

const loading = ref(false)
const activeTab = ref('available')
const availableOrders = ref([])
const preferredOrders = ref([])
const orderRequests = ref([])
const writerRequests = ref([])
const stats = ref({})
const takesEnabled = ref(false)
const filters = ref({
  service_type: '',
  min_price: null,
  max_pages: null,
})
const selectedOrder = ref(null)
const requestingOrder = ref(null)
const takingOrder = ref(null)
const showRequestModal = ref(false)
const selectedOrderForRequest = ref(null)
const requestReason = ref('')
const requestedOrderIds = ref([])  // Track which orders have been requested
const writerProfile = ref(null)
const activeAssignmentCount = ref(0)
const recommendedOrders = ref([])
const sortOption = ref('default')

const serviceTypes = computed(() => {
  const types = new Set()
  availableOrders.value.forEach(o => {
    if (o.service_type) types.add(o.service_type)
  })
  preferredOrders.value.forEach(o => {
    if (o.service_type) types.add(o.service_type)
  })
  return Array.from(types).sort()
})

const allRequests = computed(() => {
  return [...orderRequests.value, ...writerRequests.value].sort((a, b) => {
    const dateA = new Date(a.created_at || 0)
    const dateB = new Date(b.created_at || 0)
    return dateB - dateA
  })
})

const applyFilters = (orders) => {
  let filtered = [...orders]
  if (filters.value.service_type) {
    filtered = filtered.filter(o => o.service_type === filters.value.service_type)
  }
  if (filters.value.min_price !== null && filters.value.min_price !== undefined) {
    filtered = filtered.filter(o => (o.price || 0) >= filters.value.min_price)
  }
  if (filters.value.max_pages !== null && filters.value.max_pages !== undefined) {
    filtered = filtered.filter(o => (o.pages || 0) <= filters.value.max_pages)
  }
  return filtered
}

const getDeadlineTimestamp = (order) => {
  const raw = order?.deadline || order?.created_at
  if (!raw) return Number.MAX_SAFE_INTEGER
  const date = new Date(raw)
  return Number.isNaN(date.getTime()) ? Number.MAX_SAFE_INTEGER : date.getTime()
}

const applySort = (orders) => {
  if (sortOption.value === 'default') {
    return orders
  }
  const sorted = [...orders]
  if (sortOption.value === 'payout_desc') {
    return sorted.sort((a, b) => (b.potential_payout || 0) - (a.potential_payout || 0))
  }
  if (sortOption.value === 'deadline_asc') {
    return sorted.sort((a, b) => getDeadlineTimestamp(a) - getDeadlineTimestamp(b))
  }
  return sorted
}

const filteredAvailableOrders = computed(() => {
  const filtered = applyFilters(availableOrders.value)
  return applySort(filtered)
})

const filteredPreferredOrders = computed(() => {
  const filtered = applyFilters(preferredOrders.value)
  return applySort(filtered)
})

const levelDetails = computed(() => writerProfile.value?.writer_level_details || null)

const takeCapacity = computed(() => {
  const maxOrders = levelDetails.value?.max_orders || 0
  const active = activeAssignmentCount.value
  const remaining = Math.max(0, maxOrders - active)
  return { maxOrders, active, remaining }
})

const canTakeOrders = computed(() => takesEnabled.value && takeCapacity.value.remaining > 0)

const loadQueue = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getOrderQueue()
    const data = response.data
    
    if (typeof data.takes_enabled === 'boolean') {
      takesEnabled.value = data.takes_enabled
    }
    availableOrders.value = data.available_orders || []
    preferredOrders.value = data.preferred_orders || []
    recommendedOrders.value = data.recommended_orders || []
    orderRequests.value = data.order_requests || []
    writerRequests.value = data.writer_requests || []
    
    // Track requested order IDs
    requestedOrderIds.value = data.requested_order_ids || []
    
    // Also mark orders as requested if they're in the requests list
    const allRequestedIds = new Set(requestedOrderIds.value)
    orderRequests.value.forEach(r => {
      if (r.order_id) allRequestedIds.add(r.order_id)
    })
    writerRequests.value.forEach(r => {
      if (r.order_id) allRequestedIds.add(r.order_id)
    })
    requestedOrderIds.value = Array.from(allRequestedIds)
    
    stats.value = {
      available_count: availableOrders.value.length,
      preferred_count: preferredOrders.value.length,
      requests_count: allRequests.value.length,
      approved_count: allRequests.value.filter(r => r.approved || r.status === 'accepted').length,
    }
  } catch (error) {
    console.error('Failed to load order queue:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load order queue. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const loadWriterContext = async () => {
  try {
    const profileResponse = await writerManagementAPI.getMyProfile()
    writerProfile.value = profileResponse.data
  } catch (error) {
    console.error('Failed to load writer profile:', error)
  }
  await loadActiveAssignments()
}

const loadActiveAssignments = async () => {
  try {
    const response = await ordersAPI.list({
      assigned_writer: true,
      status__in: 'in_progress,under_editing,revision_requested,on_hold',
      page_size: 1,
    })
    if (typeof response.data?.count === 'number') {
      activeAssignmentCount.value = response.data.count
    } else {
      const results = response.data?.results || response.data || []
      activeAssignmentCount.value = results.length
    }
  } catch (error) {
    console.error('Failed to load active assignments:', error)
  }
}

const isOrderRequested = (order) => {
  if (!order || !order.id) return false
  const orderId = order.id
  return (
    requestedOrderIds.value.includes(orderId) ||
    order.is_requested ||
    orderRequests.value.some(r => r.order_id === orderId) ||
    writerRequests.value.some(r => r.order_id === orderId)
  )
}

const openRequestModal = (order) => {
  if (!order || !order.id) return
  selectedOrderForRequest.value = order
  requestReason.value = ''
  showRequestModal.value = true
}

const closeRequestModal = () => {
  showRequestModal.value = false
  selectedOrderForRequest.value = null
  requestReason.value = ''
}

const requestOrder = async () => {
  const order = selectedOrderForRequest.value
  if (!order || !order.id) return
  
  // Prevent duplicate requests
  if (requestingOrder.value === order.id) {
    return
  }
  
  // Validate reason
  const reason = requestReason.value?.trim() || ''
  if (!reason) {
    showError('Please provide a reason for requesting this order.')
    return
  }
  
  if (reason.length < 10) {
    showError('Please provide a more detailed reason (at least 10 characters).')
    return
  }
  
  if (reason.length > 2000) {
    showError('Reason is too long (maximum 2000 characters).')
    return
  }
  
  // Check if already requested
  if (isOrderRequested(order)) {
    showWarning('You have already requested this order. Please wait for admin review.')
    closeRequestModal()
    return
  }
  
  requestingOrder.value = order.id
  
  // Optimistic update: mark order as requested immediately
  const orderId = order.id
  if (!requestedOrderIds.value.includes(orderId)) {
    requestedOrderIds.value.push(orderId)
  }
  
  try {
    await writerOrderRequestsAPI.create({
      order_id: order.id,
      reason: reason,
    })
    
    // Refresh queue to get latest state
    await loadQueue()
    
    showSuccess('Order request submitted successfully! Your request is pending admin review.')
    closeRequestModal()
    
    if (selectedOrder.value && selectedOrder.value.id === order.id) {
      selectedOrder.value = null
    }
  } catch (error) {
    console.error('Failed to request order:', error)
    
    // Revert optimistic update on error
    requestedOrderIds.value = requestedOrderIds.value.filter(id => id !== orderId)
    
    const errorMsg = getErrorMessage(error, 'Failed to request order. Please try again.')
    
    // Provide more specific error messages
    if (errorMsg.includes('already requested') || errorMsg.includes('already')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('limit reached') || errorMsg.includes('maximum')) {
      showWarning(errorMsg)
    } else {
      showError(errorMsg)
    }
  } finally {
    requestingOrder.value = null
  }
}

const takeOrder = async (order) => {
  if (!order || !order.id) return
  
  // Prevent duplicate takes
  if (takingOrder.value === order.id) {
    return
  }
  
  // Check if already requested or taken
  if (isOrderRequested(order)) {
    showWarning('You have already requested this order. Please wait for admin review.')
    return
  }
  
  // Validate capacity
  if (!canTakeOrders.value) {
    if (!takesEnabled.value) {
      showWarning('Taking orders directly is currently disabled. Please submit a request instead.')
    } else {
      showWarning(
        `You have reached your current take limit (${takeCapacity.value.maxOrders} orders). ` +
        'Submit existing work or request a hold before taking another order.'
      )
    }
    return
  }
  
  // Confirm action
  if (!confirm(
    `Are you sure you want to take Order #${order.id}?\n\n` +
    `This will assign it to you immediately and you'll be responsible for completing it by the deadline.\n\n` +
    `Current capacity: ${takeCapacity.value.active}/${takeCapacity.value.maxOrders} orders`
  )) {
    return
  }
  
  takingOrder.value = order.id
  
  // Optimistic update: remove from available orders immediately
  const orderId = order.id
  const wasInAvailable = availableOrders.value.some(o => o.id === orderId)
  const wasInPreferred = preferredOrders.value.some(o => o.id === orderId)
  const wasInRecommended = recommendedOrders.value.some(o => o.id === orderId)
  
  if (wasInAvailable) {
    availableOrders.value = availableOrders.value.filter(o => o.id !== orderId)
  }
  if (wasInPreferred) {
    preferredOrders.value = preferredOrders.value.filter(o => o.id !== orderId)
  }
  if (wasInRecommended) {
    recommendedOrders.value = recommendedOrders.value.filter(o => o.id !== orderId)
  }
  
  // Optimistically update capacity
  const previousActiveCount = activeAssignmentCount.value
  activeAssignmentCount.value = Math.min(activeAssignmentCount.value + 1, takeCapacity.value.maxOrders)
  
  try {
    await writerOrderRequestsAPI.createTake({
      order: order.id,
    })
    
    // Refresh queue and assignments to get latest state
    await Promise.all([
      loadQueue(),
      loadActiveAssignments()
    ])
    
    showSuccess(`Order #${order.id} taken successfully! It has been assigned to you.`)
    
    // Close modal if open
    if (selectedOrder.value && selectedOrder.value.id === order.id) {
      selectedOrder.value = null
    }
  } catch (error) {
    console.error('Failed to take order:', error)
    
    // Revert optimistic updates on error
    if (wasInAvailable || wasInPreferred || wasInRecommended) {
      await loadQueue()
    }
    activeAssignmentCount.value = previousActiveCount
    
    const errorMsg = getErrorMessage(error, 'Failed to take order. Please try again.')
    
    // Provide more specific error messages
    if (errorMsg.includes('already assigned') || errorMsg.includes('already taken')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('not available') || errorMsg.includes('status')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('limit') || errorMsg.includes('maximum')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('disabled')) {
      showWarning(errorMsg)
    } else {
      showError(errorMsg)
    }
  } finally {
    takingOrder.value = null
  }
}

const viewOrder = (order) => {
  selectedOrder.value = order
}

const resetFilters = () => {
  filters.value = {
    service_type: '',
    min_price: null,
    max_pages: null,
  }
  sortOption.value = 'default'
}

const filterOrders = () => {
  // Filters are reactive, no action needed
}

const getRequestStatus = (request) => {
  if (request.approved) return 'Approved'
  if (request.status === 'accepted') return 'Accepted'
  if (request.status === 'pending') return 'Pending'
  if (request.status === 'rejected' || request.status === 'declined') return 'Rejected'
  if (request.status === 'expired') return 'Expired'
  return 'Pending'
}

const getRequestStatusBadgeClass = (request) => {
  if (request.approved || request.status === 'accepted') return 'bg-green-100 text-green-800'
  if (request.status === 'pending') return 'bg-yellow-100 text-yellow-800'
  if (request.status === 'rejected' || request.status === 'declined' || request.status === 'expired') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const formatCurrency = (value) => Number(value || 0).toFixed(2)

// Removed requestOrderFromCard - now using openRequestModal directly

onMounted(() => {
  loadQueue()
  loadWriterContext()
})
</script>

