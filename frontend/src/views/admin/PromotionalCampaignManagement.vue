<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Promotional Campaign Management</h1>
        <p class="mt-2 text-gray-600">Create and manage promotional campaigns and their associated discounts</p>
      </div>
      <button
        @click="openCreateModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        + Create Campaign
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Campaigns</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.active || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Upcoming</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.upcoming || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Discounts</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.total_discounts || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadCampaigns" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Campaign Type</label>
          <input
            v-model="filters.campaign_type"
            @input="debouncedSearch"
            type="text"
            placeholder="e.g., flash-sale, email-blast"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Campaign name..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Campaigns Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Campaign Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discounts</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="campaign in campaigns" :key="campaign.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="font-medium text-gray-900">{{ campaign.campaign_name || campaign.name }}</div>
                  <div v-if="campaign.description" class="text-xs text-gray-500 truncate max-w-xs mt-1" :title="campaign.description">
                    {{ campaign.description }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span v-if="campaign.campaign_type" class="px-2 py-1 bg-gray-100 rounded text-xs">
                  {{ campaign.campaign_type }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div>{{ formatDate(campaign.start_date) }}</div>
                <div class="text-xs text-gray-400">to {{ formatDate(campaign.end_date) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <router-link
                  :to="`/admin/campaigns/${campaign.id}/discounts`"
                  class="text-blue-600 hover:underline font-medium"
                >
                  {{ campaign.discount_count || campaign.discounts?.length || 0 }} discount(s)
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(campaign)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ getStatusText(campaign) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button @click="viewCampaign(campaign)" class="text-blue-600 hover:underline">View</button>
                  <button @click="editCampaign(campaign)" class="text-green-600 hover:underline">Edit</button>
                  <button
                    v-if="campaign.status === 'active'"
                    @click="pauseCampaign(campaign)"
                    class="text-yellow-600 hover:underline"
                  >
                    Pause
                  </button>
                  <button
                    v-else-if="campaign.status === 'paused' || campaign.status === 'draft'"
                    @click="activateCampaign(campaign)"
                    class="text-green-600 hover:underline"
                  >
                    Activate
                  </button>
                  <button
                    @click="openBulkGenerateModal(campaign)"
                    class="text-purple-600 hover:underline"
                  >
                    Generate Discounts
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!campaigns.length" class="text-center py-12 text-gray-500">
          No campaigns found.
        </div>
      </div>
    </div>

    <!-- Create/Edit Campaign Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">{{ editingCampaign ? 'Edit Campaign' : 'Create Campaign' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>
          
          <form @submit.prevent="saveCampaign" class="space-y-6">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Campaign Name *</label>
                <input
                  v-model="campaignForm.campaign_name"
                  type="text"
                  required
                  maxlength="100"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., Black Friday Sale"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Campaign Type</label>
                <input
                  v-model="campaignForm.campaign_type"
                  type="text"
                  maxlength="50"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., flash-sale, email-blast"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea
                v-model="campaignForm.description"
                rows="3"
                class="w-full border rounded px-3 py-2"
                placeholder="Campaign description..."
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Start Date *</label>
                <input
                  v-model="campaignForm.start_date"
                  type="datetime-local"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">End Date *</label>
                <input
                  v-model="campaignForm.end_date"
                  type="datetime-local"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Status</label>
              <select v-model="campaignForm.status" class="w-full border rounded px-3 py-2">
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="pending">Pending</option>
              </select>
            </div>

            <div class="flex justify-end gap-2 pt-4 border-t">
              <button type="button" @click="closeModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors">Cancel</button>
              <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                {{ saving ? 'Saving...' : (editingCampaign ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Campaign Detail Modal -->
    <div v-if="viewingCampaign" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Campaign Details</h3>
          <button @click="viewingCampaign = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Campaign Name:</span>
              <p class="text-gray-900 font-medium">{{ viewingCampaign.campaign_name || viewingCampaign.name }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="getStatusClass(viewingCampaign)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ getStatusText(viewingCampaign) }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Start Date:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingCampaign.start_date) }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">End Date:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingCampaign.end_date) }}</p>
            </div>
            <div v-if="viewingCampaign.campaign_type">
              <span class="text-sm font-medium text-gray-600">Type:</span>
              <p class="text-gray-900">{{ viewingCampaign.campaign_type }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Discounts:</span>
              <p class="text-gray-900">{{ viewingCampaign.discount_count || viewingCampaign.discounts?.length || 0 }}</p>
            </div>
          </div>

          <div v-if="viewingCampaign.description" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Description:</span>
            <p class="text-gray-700 mt-2">{{ viewingCampaign.description }}</p>
          </div>

          <div class="border-t pt-4 flex gap-2">
            <button
              @click="editCampaign(viewingCampaign); viewingCampaign = null"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Edit Campaign
            </button>
            <button
              @click="openBulkGenerateModal(viewingCampaign); viewingCampaign = null"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Generate Discounts
            </button>
            <router-link
              :to="`/admin/campaigns/${viewingCampaign.id}/analytics`"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Analytics
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Discount Generation Modal -->
    <div v-if="showBulkGenerateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Generate Discounts for Campaign</h3>
          <button @click="closeBulkGenerateModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <form @submit.prevent="generateDiscounts" class="space-y-6">
          <div>
            <label class="block text-sm font-medium mb-1">Campaign</label>
            <input
              :value="selectedCampaignForGeneration?.campaign_name || selectedCampaignForGeneration?.name"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import discountsAPI from '@/api/discounts'
import apiClient from '@/api/client'

const router = useRouter()

const campaigns = ref([])
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)
const showModal = ref(false)
const showBulkGenerateModal = ref(false)
const editingCampaign = ref(null)
const viewingCampaign = ref(null)
const selectedCampaignForGeneration = ref(null)

const stats = ref({
  total: 0,
  active: 0,
  upcoming: 0,
  total_discounts: 0,
})

const filters = ref({
  status: '',
  campaign_type: '',
  search: '',
})

const campaignForm = ref({
  campaign_name: '',
  description: '',
  campaign_type: '',
  start_date: '',
  end_date: '',
  status: 'draft',
  is_active: true,
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

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadCampaigns()
  }, 500)
}

const loadCampaigns = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) {
      params.status = filters.value.status
    }
    if (filters.value.campaign_type) {
      params.campaign_type = filters.value.campaign_type
    }
    if (filters.value.search) {
      params.search = filters.value.search
    }

    const res = await discountsAPI.listCampaigns(params)
    let allCampaigns = res.data.results || res.data || []
    
    // Load discount counts for each campaign
    for (const campaign of allCampaigns) {
      try {
        const discountRes = await discountsAPI.list({ promotional_campaign: campaign.id })
        campaign.discount_count = (discountRes.data.results || discountRes.data || []).length
      } catch (error) {
        campaign.discount_count = 0
      }
    }
    
    campaigns.value = allCampaigns
    calculateStats()
  } catch (error) {
    showMessage('Failed to load campaigns: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const now = new Date()
  stats.value = {
    total: campaigns.value.length,
    active: campaigns.value.filter(c => {
      const start = new Date(c.start_date)
      const end = new Date(c.end_date)
      return c.is_active && start <= now && now <= end
    }).length,
    upcoming: campaigns.value.filter(c => {
      const start = new Date(c.start_date)
      return c.is_active && start > now
    }).length,
    total_discounts: campaigns.value.reduce((sum, c) => sum + (c.discount_count || 0), 0),
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    campaign_type: '',
    search: '',
  }
  loadCampaigns()
}

const openCreateModal = () => {
  editingCampaign.value = null
  campaignForm.value = {
    campaign_name: '',
    description: '',
    campaign_type: '',
    start_date: new Date().toISOString().slice(0, 16),
    end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    status: 'draft',
    is_active: true,
  }
  showModal.value = true
}

const editCampaign = async (campaign) => {
  try {
    const res = await discountsAPI.getCampaign(campaign.id)
    const data = res.data
    
    editingCampaign.value = campaign
    campaignForm.value = {
      campaign_name: data.campaign_name || data.name || '',
      description: data.description || '',
      campaign_type: data.campaign_type || '',
      start_date: data.start_date ? new Date(data.start_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
      end_date: data.end_date ? new Date(data.end_date).toISOString().slice(0, 16) : '',
      status: data.status || 'draft',
      is_active: data.is_active !== undefined ? data.is_active : true,
    }
    showModal.value = true
  } catch (error) {
    showMessage('Failed to load campaign details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const viewCampaign = async (campaign) => {
  try {
    const res = await discountsAPI.getCampaign(campaign.id)
    viewingCampaign.value = res.data
  } catch (error) {
    viewingCampaign.value = campaign
    showMessage('Failed to load campaign details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const saveCampaign = async () => {
  saving.value = true
  try {
    const data = {
      campaign_name: campaignForm.value.campaign_name,
      description: campaignForm.value.description,
      campaign_type: campaignForm.value.campaign_type || null,
      start_date: campaignForm.value.start_date || null,
      end_date: campaignForm.value.end_date || null,
      status: campaignForm.value.status,
      is_active: campaignForm.value.is_active,
    }
    
    if (editingCampaign.value) {
      await discountsAPI.updateCampaign(editingCampaign.value.id, data)
      showMessage('Campaign updated successfully', true)
    } else {
      await discountsAPI.createCampaign(data)
      showMessage('Campaign created successfully', true)
    }
    
    closeModal()
    await loadCampaigns()
  } catch (error) {
    showMessage('Failed to save campaign: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message), false)
  } finally {
    saving.value = false
  }
}

const activateCampaign = async (campaign) => {
  try {
    await discountsAPI.updateCampaign(campaign.id, { status: 'active', is_active: true })
    showMessage('Campaign activated successfully', true)
    await loadCampaigns()
  } catch (error) {
    showMessage('Failed to activate campaign: ' + (error.response?.data?.detail || error.message), false)
  }
}

const pauseCampaign = async (campaign) => {
  try {
    await discountsAPI.updateCampaign(campaign.id, { status: 'paused', is_active: false })
    showMessage('Campaign paused successfully', true)
    await loadCampaigns()
  } catch (error) {
    showMessage('Failed to pause campaign: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openBulkGenerateModal = (campaign) => {
  selectedCampaignForGeneration.value = campaign
  bulkGenerateForm.value = {
    total: 10,
    prefix: (campaign.campaign_name || campaign.name || '').substring(0, 10).toUpperCase().replace(/\s/g, ''),
    code_length: 6,
    discount_type: 'percent',
    discount_value: 0,
    usage_limit: null,
    start_date: campaign.start_date ? new Date(campaign.start_date).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
    end_date: campaign.end_date ? new Date(campaign.end_date).toISOString().slice(0, 16) : '',
    is_active: true,
  }
  showBulkGenerateModal.value = true
}

const generateDiscounts = async () => {
  if (!selectedCampaignForGeneration.value) return
  
  generating.value = true
  try {
    // Use the bulk create endpoint if available, or create individually
    const campaign = selectedCampaignForGeneration.value
    
    // For now, we'll need to create a backend endpoint for bulk generation
    // Or we can call the discount generator service
    const response = await apiClient.post('/discounts/discounts/bulk-generate/', {
      campaign_id: campaign.id,
      campaign_slug: campaign.slug,
      total: bulkGenerateForm.value.total,
      prefix: bulkGenerateForm.value.prefix,
      code_length: bulkGenerateForm.value.code_length,
      discount_type: bulkGenerateForm.value.discount_type,
      discount_value: bulkGenerateForm.value.discount_value,
      usage_limit: bulkGenerateForm.value.usage_limit,
      start_date: bulkGenerateForm.value.start_date,
      end_date: bulkGenerateForm.value.end_date,
      is_active: bulkGenerateForm.value.is_active,
    })
    
    showMessage(`Successfully generated ${bulkGenerateForm.value.total} discount codes`, true)
    closeBulkGenerateModal()
    await loadCampaigns()
  } catch (error) {
    showMessage('Failed to generate discounts: ' + (error.response?.data?.detail || JSON.stringify(error.response?.data) || error.message), false)
  } finally {
    generating.value = false
  }
}

const closeBulkGenerateModal = () => {
  showBulkGenerateModal.value = false
  selectedCampaignForGeneration.value = null
}

const closeModal = () => {
  showModal.value = false
  editingCampaign.value = null
}

const getStatusClass = (campaign) => {
  const status = campaign.status || (campaign.is_active ? 'active' : 'inactive')
  const statusMap = {
    draft: 'bg-gray-100 text-gray-800',
    active: 'bg-green-100 text-green-800',
    paused: 'bg-yellow-100 text-yellow-800',
    pending: 'bg-blue-100 text-blue-800',
    completed: 'bg-purple-100 text-purple-800',
    archived: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

const getStatusText = (campaign) => {
  return campaign.status ? campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1) : (campaign.is_active ? 'Active' : 'Inactive')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
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

onMounted(() => {
  loadCampaigns()
})
</script>

