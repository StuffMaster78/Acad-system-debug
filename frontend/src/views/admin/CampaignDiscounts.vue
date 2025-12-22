<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <div class="flex items-center gap-3 mb-2">
          <router-link
            to="/admin/campaigns"
            class="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </router-link>
          <h1 class="text-3xl font-bold text-gray-900">Campaign Discounts</h1>
        </div>
        <p v-if="campaign" class="text-gray-600">
          Discounts for: <span class="font-semibold">{{ campaign.campaign_name || campaign.name }}</span>
        </p>
        <p v-else class="text-gray-600">Loading campaign details...</p>
      </div>
      <div class="flex items-center gap-3">
        <router-link
          :to="`/admin/campaigns/${campaignId}/analytics`"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          View Analytics
        </router-link>
        <div class="flex items-center gap-3">
          <button
            @click="openBulkGenerateModal"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Generate Discounts
          </button>
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Discount
          </button>
        </div>
      </div>
    </div>

    <!-- Campaign Info Card -->
    <div v-if="campaign" class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <span class="text-sm font-medium text-gray-600">Campaign Name</span>
          <p class="text-gray-900 font-semibold">{{ campaign.campaign_name || campaign.name }}</p>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600">Status</span>
          <span :class="getStatusClass(campaign)" class="px-3 py-1 rounded-full text-xs font-medium inline-block mt-1">
            {{ getStatusText(campaign) }}
          </span>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600">Period</span>
          <p class="text-gray-900 text-sm">{{ formatDate(campaign.start_date) }} - {{ formatDate(campaign.end_date) }}</p>
        </div>
        <div>
          <span class="text-sm font-medium text-gray-600">Total Discounts</span>
          <p class="text-gray-900 font-semibold text-xl">{{ discounts.length }}</p>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Discounts</p>
        <p class="text-3xl font-bold text-blue-900">{{ discounts.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900">{{ activeCount }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Total Uses</p>
        <p class="text-3xl font-bold text-yellow-900">{{ totalUses }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Savings</p>
        <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(totalSavings) }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
      
      <div v-else-if="error" class="p-6 text-center">
        <p class="text-red-600">{{ error }}</p>
        <button @click="loadDiscounts" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          Retry
        </button>
      </div>
      
      <div v-else-if="discounts.length === 0" class="p-12 text-center text-gray-500">
        <p class="text-lg mb-2">No discounts found for this campaign</p>
        <button
          @click="openCreateModal"
          class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Create First Discount
        </button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
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
                  <span class="font-mono font-medium text-gray-900">{{ discount.code || discount.discount_code }}</span>
                  <button
                    @click="copyCode(discount.code || discount.discount_code)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                    title="Copy code"
                  >
                    📋
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                {{ discount.discount_type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <span v-if="discount.discount_type === 'percent'">
                  {{ discount.value || discount.discount_value }}%
                </span>
                <span v-else>
                  ${{ formatCurrency(discount.value || discount.discount_value) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ discount.used_count || 0 }}
                <span v-if="discount.max_uses || discount.usage_limit">
                  / {{ discount.max_uses || discount.usage_limit }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ discount.end_date ? formatDate(discount.end_date) : 'No expiry' }}
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
                    v-if="discount.is_active"
                    @click="deactivateDiscount(discount)"
                    class="text-yellow-600 hover:underline"
                  >
                    Deactivate
                  </button>
                  <button
                    v-else
                    @click="activateDiscount(discount)"
                    class="text-green-600 hover:underline"
                  >
                    Activate
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Discount Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">{{ editingDiscount ? 'Edit Discount' : 'Create Discount' }}</h3>
          <button @click="closeModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <form @submit.prevent="saveDiscount" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Discount Code *</label>
            <input
              v-model="form.discount_code"
              type="text"
              required
              class="w-full border rounded px-3 py-2"
              placeholder="e.g., SUMMER2024"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Type *</label>
              <select v-model="form.discount_type" required class="w-full border rounded px-3 py-2">
                <option value="percent">Percentage</option>
                <option value="fixed">Fixed Amount</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Value *</label>
              <input
                v-model.number="form.discount_value"
                type="number"
                step="0.01"
                required
                class="w-full border rounded px-3 py-2"
                placeholder="10 or 5.00"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Start Date</label>
              <input
                v-model="form.start_date"
                type="datetime-local"
                class="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">End Date</label>
              <input
                v-model="form.end_date"
                type="datetime-local"
                class="w-full border rounded px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Usage Limit</label>
            <input
              v-model.number="form.usage_limit"
              type="number"
              class="w-full border rounded px-3 py-2"
              placeholder="Leave empty for unlimited"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full border rounded px-3 py-2"
              placeholder="Optional description"
            ></textarea>
          </div>

          <div class="flex gap-2 pt-4">
            <button type="submit" class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
              {{ editingDiscount ? 'Update' : 'Create' }} Discount
            </button>
            <button type="button" @click="closeModal" class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Discount Modal -->
    <div v-if="viewingDiscount" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
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
              <span class="text-sm font-medium text-gray-600">Valid Until:</span>
              <p class="text-gray-900">{{ viewingDiscount.end_date ? formatDate(viewingDiscount.end_date) : 'No expiry' }}</p>
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

    <!-- Bulk Discount Generation Modal -->
    <div v-if="showBulkGenerateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Generate Discounts for Campaign</h3>
          <button @click="closeBulkGenerateModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <form @submit.prevent="generateDiscounts" class="space-y-6">
          <div>
            <label class="block text-sm font-medium mb-1">Campaign</label>
            <input
              :value="campaign?.campaign_name || campaign?.name || 'Loading...'"
              disabled
              class="w-full border rounded px-3 py-2 bg-gray-100"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Number of Discounts *</label>
              <input
                v-model.number="bulkGenerateForm.total"
                type="number"
                required
                min="1"
                max="1000"
                class="w-full border rounded px-3 py-2"
                placeholder="e.g., 100"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Code Prefix</label>
              <input
                v-model="bulkGenerateForm.prefix"
                type="text"
                maxlength="10"
                class="w-full border rounded px-3 py-2"
                placeholder="e.g., BF2024"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Code Length</label>
              <input
                v-model.number="bulkGenerateForm.code_length"
                type="number"
                min="4"
                max="12"
                class="w-full border rounded px-3 py-2"
                placeholder="6"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Discount Type *</label>
              <select v-model="bulkGenerateForm.discount_type" required class="w-full border rounded px-3 py-2">
                <option value="percent">Percentage</option>
                <option value="fixed">Fixed Amount</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Discount Value *</label>
              <input
                v-model.number="bulkGenerateForm.discount_value"
                type="number"
                required
                step="0.01"
                min="0"
                :max="bulkGenerateForm.discount_type === 'percent' ? 100 : undefined"
                class="w-full border rounded px-3 py-2"
                :placeholder="bulkGenerateForm.discount_type === 'percent' ? 'e.g., 20' : 'e.g., 10.00'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Usage Limit (per code)</label>
              <input
                v-model.number="bulkGenerateForm.usage_limit"
                type="number"
                min="1"
                class="w-full border rounded px-3 py-2"
                placeholder="Leave empty for unlimited"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Start Date</label>
              <input
                v-model="bulkGenerateForm.start_date"
                type="datetime-local"
                class="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">End Date</label>
              <input
                v-model="bulkGenerateForm.end_date"
                type="datetime-local"
                class="w-full border rounded px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="bulkGenerateForm.is_active"
                type="checkbox"
                class="rounded"
              />
              <span class="text-sm">Activate discounts immediately</span>
            </label>
          </div>

          <div class="flex justify-end gap-2 pt-4 border-t">
            <button type="button" @click="closeBulkGenerateModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">Cancel</button>
            <button type="submit" :disabled="generating" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {{ generating ? 'Generating...' : `Generate ${bulkGenerateForm.total || 0} Discounts` }}
            </button>
          </div>
        </form>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { discountsAPI } from '@/api'

const route = useRoute()
const campaignId = route.params.id

const loading = ref(false)
const error = ref(null)
const campaign = ref(null)
const discounts = ref([])
const viewingDiscount = ref(null)
const showModal = ref(false)
const editingDiscount = ref(null)
const showBulkGenerateModal = ref(false)
const generating = ref(false)
const message = ref('')
const messageSuccess = ref(false)

const filters = ref({
  is_active: null,
  discount_type: '',
  search: '',
})

const form = ref({
  discount_code: '',
  discount_type: 'percent',
  discount_value: 0,
  start_date: '',
  end_date: '',
  usage_limit: null,
  description: '',
  promotional_campaign: campaignId,
})

const bulkGenerateForm = ref({
  total: 10,
  prefix: '',
  code_length: 6,
  discount_type: 'percent',
  discount_value: 0,
  usage_limit: null,
  start_date: '',
  end_date: '',
  is_active: true,
})

let searchTimeout = null

const activeCount = computed(() => {
  return discounts.value.filter(d => d.is_active).length
})

const totalUses = computed(() => {
  return discounts.value.reduce((sum, d) => sum + (d.used_count || 0), 0)
})

const totalSavings = computed(() => {
  // This would need to come from backend analytics
  // For now, return 0 or calculate from usage if available
  return 0
})

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDiscounts()
  }, 500)
}

const loadCampaign = async () => {
  try {
    const res = await discountsAPI.getCampaign(campaignId)
    campaign.value = res.data
  } catch (error) {
    console.error('Failed to load campaign:', error)
    // Don't set error state, just log it
  }
}

const loadDiscounts = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {
      promotional_campaign: campaignId, // Filter by campaign ID
    }
    
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
    discounts.value = res.data.results || res.data || []
  } catch (err) {
    // Only set error if it's not a 404
    if (err?.response?.status !== 404) {
      error.value = err?.response?.data?.detail || err.message || 'Failed to load discounts'
      console.error('Failed to load discounts:', err)
    } else {
      discounts.value = []
    }
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingDiscount.value = null
  form.value = {
    discount_code: '',
    discount_type: 'percent',
    discount_value: 0,
    start_date: '',
    end_date: '',
    usage_limit: null,
    description: '',
    promotional_campaign: campaignId,
  }
  showModal.value = true
}

const editDiscount = (discount) => {
  editingDiscount.value = discount
  form.value = {
    discount_code: discount.code || discount.discount_code,
    discount_type: discount.discount_type,
    discount_value: discount.value || discount.discount_value,
    start_date: discount.start_date ? new Date(discount.start_date).toISOString().slice(0, 16) : '',
    end_date: discount.end_date ? new Date(discount.end_date).toISOString().slice(0, 16) : '',
    usage_limit: discount.max_uses || discount.usage_limit || null,
    description: discount.description || '',
    promotional_campaign: campaignId,
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingDiscount.value = null
}

const saveDiscount = async () => {
  try {
    const data = {
      ...form.value,
    }
    
    // Use campaign slug for create/update (serializer expects slug, not ID)
    if (campaign.value?.slug) {
      data.promotional_campaign = campaign.value.slug
    } else {
      // If campaign not loaded yet, load it first
      if (!campaign.value) {
        await loadCampaign()
      }
      if (campaign.value?.slug) {
        data.promotional_campaign = campaign.value.slug
      } else {
        showMessage('Campaign slug not available. Please refresh the page.', false)
        return
      }
    }
    
    // Convert datetime-local to ISO string
    if (data.start_date) {
      data.start_date = new Date(data.start_date).toISOString()
    }
    if (data.end_date) {
      data.end_date = new Date(data.end_date).toISOString()
    }

    if (editingDiscount.value) {
      await discountsAPI.update(editingDiscount.value.id, data)
      showMessage('Discount updated successfully', true)
    } else {
      await discountsAPI.create(data)
      showMessage('Discount created successfully', true)
    }
    
    closeModal()
    loadDiscounts()
  } catch (error) {
    showMessage('Failed to save discount: ' + (error.response?.data?.detail || error.message), false)
  }
}

const viewDiscount = (discount) => {
  viewingDiscount.value = discount
}

const activateDiscount = async (discount) => {
  try {
    await discountsAPI.update(discount.id, { is_active: true })
    showMessage('Discount activated successfully', true)
    loadDiscounts()
  } catch (error) {
    showMessage('Failed to activate discount: ' + (error.response?.data?.detail || error.message), false)
  }
}

const deactivateDiscount = async (discount) => {
  try {
    await discountsAPI.update(discount.id, { is_active: false })
    showMessage('Discount deactivated successfully', true)
    loadDiscounts()
  } catch (error) {
    showMessage('Failed to deactivate discount: ' + (error.response?.data?.detail || error.message), false)
  }
}

const resetFilters = () => {
  filters.value = {
    is_active: null,
    discount_type: '',
    search: '',
  }
  loadDiscounts()
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code)
  showMessage('Code copied to clipboard', true)
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getStatusClass = (item) => {
  const isActive = item.is_active
  const now = new Date()
  const endDate = item.end_date ? new Date(item.end_date) : null
  
  if (!isActive) {
    return 'bg-gray-100 text-gray-800'
  }
  if (endDate && endDate < now) {
    return 'bg-red-100 text-red-800'
  }
  return 'bg-green-100 text-green-800'
}

const getStatusText = (item) => {
  const isActive = item.is_active
  const now = new Date()
  const endDate = item.end_date ? new Date(item.end_date) : null
  
  if (!isActive) {
    return 'Inactive'
  }
  if (endDate && endDate < now) {
    return 'Expired'
  }
  return 'Active'
}

const openBulkGenerateModal = () => {
  if (!campaign.value) {
    showMessage('Please wait for campaign to load', false)
    return
  }
  
  // Pre-fill form with campaign defaults
  bulkGenerateForm.value = {
    total: 10,
    prefix: (campaign.value.campaign_name || campaign.value.name || '').substring(0, 10).toUpperCase().replace(/\s/g, ''),
    code_length: 6,
    discount_type: 'percent',
    discount_value: 0,
    usage_limit: null,
    start_date: campaign.value.start_date ? new Date(campaign.value.start_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
    end_date: campaign.value.end_date ? new Date(campaign.value.end_date).toISOString().slice(0, 16) : '',
    is_active: true,
  }
  showBulkGenerateModal.value = true
}

const closeBulkGenerateModal = () => {
  showBulkGenerateModal.value = false
  generating.value = false
}

const generateDiscounts = async () => {
  if (!campaign.value) return
  
  generating.value = true
  try {
    const data = {
      campaign_id: campaign.value.id,
      campaign_slug: campaign.value.slug,
      total: bulkGenerateForm.value.total,
      prefix: bulkGenerateForm.value.prefix,
      code_length: bulkGenerateForm.value.code_length,
      discount_type: bulkGenerateForm.value.discount_type,
      discount_value: bulkGenerateForm.value.discount_value,
      usage_limit: bulkGenerateForm.value.usage_limit,
      start_date: bulkGenerateForm.value.start_date ? new Date(bulkGenerateForm.value.start_date).toISOString() : null,
      end_date: bulkGenerateForm.value.end_date ? new Date(bulkGenerateForm.value.end_date).toISOString() : null,
      is_active: bulkGenerateForm.value.is_active,
    }
    
    await discountsAPI.bulkGenerate(data)
    showMessage(`Successfully generated ${bulkGenerateForm.value.total} discount codes`, true)
    closeBulkGenerateModal()
    loadDiscounts()
  } catch (error) {
    showMessage('Failed to generate discounts: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message), false)
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  // Load campaign first, then discounts (so we can use slug if available)
  await loadCampaign()
  loadDiscounts()
})
</script>

