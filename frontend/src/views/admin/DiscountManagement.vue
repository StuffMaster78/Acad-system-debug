<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Discount Management</h1>
        <p class="mt-2 text-gray-600">Create and manage discount codes for all users or specific users</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        + Create Discount
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Discounts</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.active || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Expired</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.expired || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Uses</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_uses || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.is_active" @change="loadDiscounts" class="w-full border rounded px-3 py-2">
            <option :value="null">All Statuses</option>
            <option :value="true">Active</option>
            <option :value="false">Inactive</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Type</label>
          <select v-model="filters.discount_type" @change="loadDiscounts" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="fixed">Fixed Amount</option>
            <option value="percent">Percentage</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Audience</label>
          <select v-model="filters.audience" @change="loadDiscounts" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="general">General (All Users)</option>
            <option value="specific">Specific Users</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Code, description..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Discounts Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Audience</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valid Until</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="discount in discounts" :key="discount.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900 font-mono">{{ discount.code || discount.discount_code }}</span>
                  <button
                    @click="copyCode(discount.code || discount.discount_code)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                    title="Copy code"
                  >
                    📋
                  </button>
                </div>
                <div v-if="discount.description" class="text-xs text-gray-500 mt-1 truncate max-w-xs" :title="discount.description">
                  {{ discount.description }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span :class="discount.discount_type === 'percent' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ discount.discount_type === 'percent' ? 'Percentage' : 'Fixed' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <span v-if="discount.discount_type === 'percent'">
                  {{ discount.value || discount.discount_value }}%
                </span>
                <span v-else>
                  ${{ discount.value || discount.discount_value }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="discount.is_general" class="text-blue-600 font-medium">All Users</span>
                <span v-else-if="discount.assigned_to_client_email || discount.assigned_to_client_username" class="text-purple-600">
                  {{ discount.assigned_to_client_username || discount.assigned_to_client_email }}
                </span>
                <span v-else-if="discount.assigned_to_users && discount.assigned_to_users.length > 0" class="text-orange-600">
                  {{ discount.assigned_to_users.length }} user(s)
                </span>
                <span v-else class="text-gray-400">N/A</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>
                  <span class="font-medium">{{ discount.used_count || 0 }}</span>
                  <span v-if="discount.max_uses || discount.usage_limit" class="text-gray-400">
                    / {{ discount.max_uses || discount.usage_limit }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="discount.end_date || discount.expiry_date">
                  {{ formatDate(discount.end_date || discount.expiry_date) }}
                </span>
                <span v-else class="text-gray-400">No expiry</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(discount)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ getStatusText(discount) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button @click="viewDiscount(discount)" class="text-blue-600 hover:underline">View</button>
                  <button @click="editDiscount(discount)" class="text-green-600 hover:underline">Edit</button>
                  <button
                    @click="toggleActive(discount)"
                    class="text-yellow-600 hover:underline"
                  >
                    {{ discount.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!discounts.length" class="text-center py-12 text-gray-500">
          No discounts found.
        </div>
      </div>
    </div>

    <!-- Create/Edit Discount Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">{{ editingDiscount ? 'Edit Discount' : 'Create Discount' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>
          
          <form @submit.prevent="saveDiscount" class="space-y-6">
            <!-- Basic Information -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Discount Code *</label>
                <input
                  v-model="discountForm.code"
                  type="text"
                  required
                  maxlength="32"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., SAVE20"
                />
                <p class="text-xs text-gray-500 mt-1">Unique code (max 32 characters)</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Discount Type *</label>
                <select v-model="discountForm.discount_type" required class="w-full border rounded px-3 py-2">
                  <option value="percent">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Discount Value *</label>
                <input
                  v-model.number="discountForm.value"
                  type="number"
                  required
                  step="0.01"
                  min="0"
                  :max="discountForm.discount_type === 'percent' ? 100 : undefined"
                  class="w-full border rounded px-3 py-2"
                  :placeholder="discountForm.discount_type === 'percent' ? 'e.g., 20' : 'e.g., 10.00'"
                />
                <p class="text-xs text-gray-500 mt-1">
                  {{ discountForm.discount_type === 'percent' ? 'Percentage (1-100)' : 'Fixed amount in dollars' }}
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Origin Type</label>
                <select v-model="discountForm.origin_type" class="w-full border rounded px-3 py-2">
                  <option value="manual">Manual</option>
                  <option value="automatic">Automatic</option>
                  <option value="system">System Generated</option>
                  <option value="client">Client Specific</option>
                  <option value="promo">Promotional Campaign</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea
                v-model="discountForm.description"
                rows="2"
                class="w-full border rounded px-3 py-2"
                placeholder="Description of the discount..."
              ></textarea>
            </div>

            <!-- Target Audience -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-4">Target Audience</h3>
              <div class="space-y-4">
                <div>
                  <label class="flex items-center gap-2">
                    <input
                      type="radio"
                      v-model="discountForm.is_general"
                      :value="true"
                      @change="handleAudienceChange(true)"
                      class="rounded"
                    />
                    <span class="font-medium">All Users (General)</span>
                  </label>
                </div>
                <div>
                  <label class="flex items-center gap-2">
                    <input
                      type="radio"
                      v-model="discountForm.is_general"
                      :value="false"
                      @change="handleAudienceChange(false)"
                      class="rounded"
                    />
                    <span class="font-medium">Specific Users</span>
                  </label>
                </div>

                <!-- Specific User Assignment -->
                <div v-if="!discountForm.is_general" class="ml-6 space-y-4 border-l-2 border-gray-200 pl-4">
                  <div>
                    <label class="block text-sm font-medium mb-2">Assign to Users by Email</label>
                    <div class="space-y-2">
                      <div class="flex gap-2">
                        <input
                          v-model="newUserEmail"
                          type="email"
                          placeholder="Enter email address"
                          class="flex-1 border rounded px-3 py-2"
                          @keyup.enter="addUserByEmail"
                        />
                        <button
                          type="button"
                          @click="addUserByEmail"
                          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Add
                        </button>
                      </div>
                      <div v-if="assignedUserEmails.length > 0" class="flex flex-wrap gap-2 mt-2">
                        <span
                          v-for="(email, idx) in assignedUserEmails"
                          :key="idx"
                          class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center gap-2"
                        >
                          {{ email }}
                          <button
                            type="button"
                            @click="removeUserEmail(idx)"
                            class="text-blue-600 hover:text-blue-800"
                          >
                            ✕
                          </button>
                        </span>
                      </div>
                      <p class="text-xs text-gray-500 mt-1">
                        Users will be looked up by email and assigned to this discount
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium mb-2">Or Assign to Single Client</label>
                    <input
                      v-model="clientSearch"
                      type="text"
                      placeholder="Search by email or username..."
                      class="w-full border rounded px-3 py-2"
                      @input="searchClients"
                    />
                    <div v-if="clientSearchResults.length > 0" class="mt-2 border rounded max-h-40 overflow-y-auto">
                      <button
                        v-for="client in clientSearchResults"
                        :key="client.id"
                        type="button"
                        @click="selectClient(client)"
                        class="w-full text-left px-3 py-2 hover:bg-gray-50 border-b last:border-b-0"
                      >
                        <div class="font-medium">{{ client.username }}</div>
                        <div class="text-xs text-gray-500">{{ client.email }}</div>
                      </button>
                    </div>
                    <div v-if="selectedClient" class="mt-2 px-3 py-2 bg-blue-50 rounded">
                      <div class="flex items-center justify-between">
                        <span class="text-sm font-medium">{{ selectedClient.username }} ({{ selectedClient.email }})</span>
                        <button type="button" @click="selectedClient = null" class="text-blue-600 hover:text-blue-800">Remove</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Time Constraints -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-4">Time Constraints</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Start Date</label>
                  <input
                    v-model="discountForm.start_date"
                    type="datetime-local"
                    class="w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">End Date (Optional)</label>
                  <input
                    v-model="discountForm.end_date"
                    type="datetime-local"
                    class="w-full border rounded px-3 py-2"
                  />
                </div>
              </div>
            </div>

            <!-- Usage Constraints -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-4">Usage Constraints</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Total Usage Limit</label>
                  <input
                    v-model.number="discountForm.max_uses"
                    type="number"
                    min="0"
                    class="w-full border rounded px-3 py-2"
                    placeholder="Leave empty for unlimited"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">Per User Usage Limit</label>
                  <input
                    v-model.number="discountForm.per_user_usage_limit"
                    type="number"
                    min="0"
                    class="w-full border rounded px-3 py-2"
                    placeholder="Leave empty for unlimited"
                  />
                </div>
                <div>
                  <label class="flex items-center gap-2 mt-4">
                    <input
                      v-model="discountForm.applies_to_first_order_only"
                      type="checkbox"
                      class="rounded"
                    />
                    <span class="text-sm">Applies to first order only</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Order Constraints -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-4">Order Constraints</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Minimum Order Value</label>
                  <input
                    v-model.number="discountForm.min_order_value"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full border rounded px-3 py-2"
                    placeholder="Leave empty for no minimum"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">Maximum Discount Value</label>
                  <input
                    v-model.number="discountForm.max_discount_value"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full border rounded px-3 py-2"
                    placeholder="Leave empty for no maximum"
                  />
                </div>
              </div>
            </div>

            <!-- Stacking -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-4">Stacking Options</h3>
              <div>
                <label class="flex items-center gap-2">
                  <input
                    v-model="discountForm.stackable"
                    type="checkbox"
                    class="rounded"
                  />
                  <span class="text-sm">Allow stacking with other discounts</span>
                </label>
              </div>
            </div>

            <div class="flex justify-end gap-2 pt-4 border-t">
              <button type="button" @click="closeModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">Cancel</button>
              <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                {{ saving ? 'Saving...' : (editingDiscount ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Discount Detail Modal -->
    <div v-if="viewingDiscount" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Discount Details</h3>
          <button @click="viewingDiscount = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Code:</span>
              <div class="flex items-center gap-2 mt-1">
                <p class="text-gray-900 font-mono font-medium">{{ viewingDiscount.code || viewingDiscount.discount_code }}</p>
                <button
                  @click="copyCode(viewingDiscount.code || viewingDiscount.discount_code)"
                  class="text-blue-600 hover:text-blue-800 text-sm"
                  title="Copy code"
                >
                  📋 Copy
                </button>
              </div>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Type:</span>
              <p class="text-gray-900 capitalize">{{ viewingDiscount.discount_type }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Value:</span>
              <p class="text-gray-900 font-medium">
                <span v-if="viewingDiscount.discount_type === 'percent'">
                  {{ viewingDiscount.value || viewingDiscount.discount_value }}%
                </span>
                <span v-else>
                  ${{ viewingDiscount.value || viewingDiscount.discount_value }}
                </span>
              </p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="getStatusClass(viewingDiscount)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ getStatusText(viewingDiscount) }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Usage:</span>
              <p class="text-gray-900">
                {{ viewingDiscount.used_count || 0 }}
                <span v-if="viewingDiscount.max_uses || viewingDiscount.usage_limit">
                  / {{ viewingDiscount.max_uses || viewingDiscount.usage_limit }}
                </span>
              </p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Audience:</span>
              <p class="text-gray-900">
                <span v-if="viewingDiscount.is_general">All Users</span>
                <span v-else-if="viewingDiscount.assigned_to_client_email">
                  {{ viewingDiscount.assigned_to_client_username || viewingDiscount.assigned_to_client_email }}
                </span>
                <span v-else>Specific Users</span>
              </p>
            </div>
          </div>

          <div v-if="viewingDiscount.description" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Description:</span>
            <p class="text-gray-700 mt-2">{{ viewingDiscount.description }}</p>
          </div>

          <div class="border-t pt-4 flex gap-2">
            <button
              @click="editDiscount(viewingDiscount); viewingDiscount = null"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Edit Discount
            </button>
            <button
              @click="copyCode(viewingDiscount.code || viewingDiscount.discount_code)"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              📋 Copy Code
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import discountsAPI from '@/api/discounts'
import usersAPI from '@/api/users'
import apiClient from '@/api/client'

const authStore = useAuthStore()

const discounts = ref([])
const websites = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingDiscount = ref(null)
const viewingDiscount = ref(null)

const stats = ref({
  total: 0,
  active: 0,
  expired: 0,
  total_uses: 0,
})

const filters = ref({
  is_active: null,
  discount_type: '',
  audience: '',
  search: '',
})

const discountForm = ref({
  code: '',
  description: '',
  discount_type: 'percent',
  origin_type: 'manual',
  value: 0,
  is_general: true,
  start_date: '',
  end_date: '',
  max_uses: null,
  per_user_usage_limit: null,
  applies_to_first_order_only: false,
  min_order_value: null,
  max_discount_value: null,
  stackable: false,
  assigned_to_users: [],
  assigned_to_client: null,
})

const newUserEmail = ref('')
const assignedUserEmails = ref([])
const assignedUserIds = ref([])
const clientSearch = ref('')
const clientSearchResults = ref([])
const selectedClient = ref(null)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDiscounts()
  }, 500)
}

const loadDiscounts = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.is_active !== null) {
      params.is_active = filters.value.is_active
    }
    if (filters.value.discount_type) {
      params.discount_type = filters.value.discount_type
    }
    if (filters.value.search) {
      params.search = filters.value.search
    }

    const res = await discountsAPI.list(params)
    let allDiscounts = res.data.results || res.data || []
    
    // Filter by audience if specified
    if (filters.value.audience === 'general') {
      allDiscounts = allDiscounts.filter(d => d.is_general)
    } else if (filters.value.audience === 'specific') {
      allDiscounts = allDiscounts.filter(d => !d.is_general)
    }
    
    discounts.value = allDiscounts
    calculateStats()
  } catch (error) {
    showMessage('Failed to load discounts: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const calculateStats = () => {
  stats.value = {
    total: discounts.value.length,
    active: discounts.value.filter(d => d.is_active && !isExpired(d)).length,
    expired: discounts.value.filter(d => isExpired(d)).length,
    total_uses: discounts.value.reduce((sum, d) => sum + (d.used_count || 0), 0),
  }
}

const isExpired = (discount) => {
  if (!discount.end_date && !discount.expiry_date) return false
  const expiry = discount.end_date || discount.expiry_date
  return new Date(expiry) < new Date()
}

const resetFilters = () => {
  filters.value = {
    is_active: null,
    discount_type: '',
    audience: '',
    search: '',
  }
  loadDiscounts()
}

const openCreateModal = () => {
  editingDiscount.value = null
  discountForm.value = {
    code: '',
    description: '',
    discount_type: 'percent',
    origin_type: 'manual',
    value: 0,
    is_general: true,
    start_date: new Date().toISOString().slice(0, 16),
    end_date: '',
    max_uses: null,
    per_user_usage_limit: null,
    applies_to_first_order_only: false,
    min_order_value: null,
    max_discount_value: null,
    stackable: false,
    assigned_to_users: [],
    assigned_to_client: null,
  }
  assignedUserEmails.value = []
  assignedUserIds.value = []
  selectedClient.value = null
  clientSearch.value = ''
  clientSearchResults.value = []
  showModal.value = true
}

const editDiscount = async (discount) => {
  try {
    const res = await discountsAPI.get(discount.id)
    const data = res.data
    
    editingDiscount.value = discount
    discountForm.value = {
      code: data.code || data.discount_code || '',
      description: data.description || '',
      discount_type: data.discount_type || 'percent',
      origin_type: data.origin_type || 'manual',
      value: data.value || data.discount_value || 0,
      is_general: data.is_general !== undefined ? data.is_general : true,
      start_date: data.start_date ? new Date(data.start_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
      end_date: data.end_date ? new Date(data.end_date).toISOString().slice(0, 16) : '',
      max_uses: data.max_uses || data.usage_limit || null,
      per_user_usage_limit: data.per_user_usage_limit || null,
      applies_to_first_order_only: data.applies_to_first_order_only || false,
      min_order_value: data.min_order_value || null,
      max_discount_value: data.max_discount_value || null,
      stackable: data.stackable || false,
      assigned_to_users: data.assigned_to_users || [],
      assigned_to_client: data.assigned_to_client || null,
    }
    
    // Load assigned users if any
    if (data.assigned_to_users && data.assigned_to_users.length > 0) {
      assignedUserIds.value = data.assigned_to_users.map(u => typeof u === 'object' ? u.id : u)
      // Try to get emails - might need to fetch user details
      assignedUserEmails.value = data.assigned_to_users.map(u => typeof u === 'object' ? (u.email || '') : '')
    } else {
      assignedUserEmails.value = []
      assignedUserIds.value = []
    }
    
    selectedClient.value = data.assigned_to_client ? {
      id: typeof data.assigned_to_client === 'object' ? data.assigned_to_client.id : data.assigned_to_client,
      username: data.assigned_to_client_username || '',
      email: data.assigned_to_client_email || '',
    } : null
    
    showModal.value = true
  } catch (error) {
    showMessage('Failed to load discount details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const viewDiscount = async (discount) => {
  try {
    const res = await discountsAPI.get(discount.id)
    viewingDiscount.value = res.data
  } catch (error) {
    viewingDiscount.value = discount
    showMessage('Failed to load discount details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const handleAudienceChange = (isGeneral) => {
  if (isGeneral) {
    assignedUserEmails.value = []
    assignedUserIds.value = []
    selectedClient.value = null
    discountForm.value.assigned_to_client = null
  }
}

const addUserByEmail = async () => {
  if (!newUserEmail.value.trim()) return
  
  const email = newUserEmail.value.trim().toLowerCase()
  
  // Check if already added
  if (assignedUserEmails.value.includes(email)) {
    showMessage('User already added', false)
    return
  }
  
  try {
    // Search for user by email
    const res = await usersAPI.list({ search: email, role: 'client' })
    const users = res.data.results || res.data || []
    const user = users.find(u => u.email.toLowerCase() === email)
    
    if (user) {
      assignedUserEmails.value.push(email)
      assignedUserIds.value.push(user.id)
      newUserEmail.value = ''
    } else {
      showMessage(`User with email ${email} not found. Please ensure the user exists.`, false)
    }
  } catch (error) {
    showMessage('Failed to find user: ' + (error.response?.data?.detail || error.message), false)
  }
}

const removeUserEmail = (index) => {
  assignedUserEmails.value.splice(index, 1)
  assignedUserIds.value.splice(index, 1)
}

const searchClients = async () => {
  if (!clientSearch.value.trim()) {
    clientSearchResults.value = []
    return
  }
  
  try {
    const res = await usersAPI.list({ search: clientSearch.value, role: 'client' })
    clientSearchResults.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to search clients:', error)
    clientSearchResults.value = []
  }
}

const selectClient = (client) => {
  selectedClient.value = client
  discountForm.value.assigned_to_client = client.id
  clientSearch.value = ''
  clientSearchResults.value = []
}

const saveDiscount = async () => {
  saving.value = true
  try {
    const data = {
      code: discountForm.value.code,
      description: discountForm.value.description,
      discount_type: discountForm.value.discount_type,
      origin_type: discountForm.value.origin_type,
      value: discountForm.value.value,
      is_general: discountForm.value.is_general,
      start_date: discountForm.value.start_date || null,
      end_date: discountForm.value.end_date || null,
      max_uses: discountForm.value.max_uses || null,
      per_user_usage_limit: discountForm.value.per_user_usage_limit || null,
      applies_to_first_order_only: discountForm.value.applies_to_first_order_only,
      min_order_value: discountForm.value.min_order_value || null,
      max_discount_value: discountForm.value.max_discount_value || null,
      stackable: discountForm.value.stackable,
    }
    
    // Handle user assignment
    if (!discountForm.value.is_general) {
      if (selectedClient.value) {
        data.assigned_to_client = selectedClient.value.id
      } else if (assignedUserIds.value.length > 0) {
        data.assigned_to_users = assignedUserIds.value
      }
    }
    
    if (editingDiscount.value) {
      await discountsAPI.update(editingDiscount.value.id, data)
      showMessage('Discount updated successfully', true)
    } else {
      await discountsAPI.create(data)
      showMessage('Discount created successfully', true)
    }
    
    closeModal()
    await loadDiscounts()
  } catch (error) {
    showMessage('Failed to save discount: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message), false)
  } finally {
    saving.value = false
  }
}

const toggleActive = async (discount) => {
  try {
    await discountsAPI.update(discount.id, { is_active: !discount.is_active })
    showMessage(`Discount ${discount.is_active ? 'deactivated' : 'activated'} successfully`, true)
    await loadDiscounts()
  } catch (error) {
    showMessage('Failed to update discount: ' + (error.response?.data?.detail || error.message), false)
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    showMessage('Discount code copied to clipboard!', true)
  }).catch(() => {
    showMessage('Failed to copy code', false)
  })
}

const closeModal = () => {
  showModal.value = false
  editingDiscount.value = null
  newUserEmail.value = ''
  assignedUserEmails.value = []
  assignedUserIds.value = []
  selectedClient.value = null
  clientSearch.value = ''
  clientSearchResults.value = []
}

const getStatusClass = (discount) => {
  if (isExpired(discount)) return 'bg-gray-100 text-gray-800'
  if (!discount.is_active) return 'bg-red-100 text-red-800'
  return 'bg-green-100 text-green-800'
}

const getStatusText = (discount) => {
  if (isExpired(discount)) return 'Expired'
  if (!discount.is_active) return 'Inactive'
  return 'Active'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const message = ref('')
const messageSuccess = ref(false)

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(async () => {
  await Promise.all([
    loadWebsites(),
    loadDiscounts()
  ])
})
</script>

