<template>
  <div class="tenant-management space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Tenant Management</h1>
        <p class="mt-2 text-gray-600">Manage all tenants (websites) across the platform</p>
      </div>
      <div class="flex items-center gap-4">
        <button
          @click="showComparison = !showComparison"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {{ showComparison ? 'Hide' : 'Show' }} Comparison
        </button>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Create Tenant
        </button>
        <button
          @click="refreshData"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="handleFilter"
            type="text"
            placeholder="Search tenants..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" @change="handleFilter" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deleted">Deleted</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select v-model="filters.sortBy" @change="handleFilter" class="w-full border rounded px-3 py-2">
            <option value="name">Name</option>
            <option value="created_at">Created Date</option>
            <option value="order_count">Order Count</option>
            <option value="revenue">Revenue</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="resetFilters"
            class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Tenants"
        :value="summary.total_tenants || 0"
        icon="🏢"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Active Tenants"
        :value="summary.active_tenants || 0"
        icon="✅"
        bgColor="bg-green-100"
      />
      <StatsCard
        name="Inactive Tenants"
        :value="summary.inactive_tenants || 0"
        icon="⏸️"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="Deleted Tenants"
        :value="summary.deleted_tenants || 0"
        icon="🗑️"
        bgColor="bg-red-100"
      />
    </div>

    <!-- Tenant Comparison View -->
    <div v-if="showComparison" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Cross-Tenant Comparison</h2>
      <div v-if="loadingComparison" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="comparisonData" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tenant</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orders</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completion Rate</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Disputes</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tickets</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="tenant in comparisonData.tenants" :key="tenant.tenant_id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">{{ tenant.tenant_name }}</div>
                <div class="text-sm text-gray-500">{{ tenant.domain }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ tenant.metrics?.users?.total || 0 }}
                <span class="text-gray-500">(+{{ tenant.metrics?.users?.new_this_period || 0 }})</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ tenant.metrics?.orders?.total || 0 }}
                <span class="text-gray-500">({{ tenant.metrics?.orders?.completed || 0 }} completed)</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                ${{ formatCurrency(tenant.metrics?.revenue?.total || 0) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ tenant.metrics?.orders?.completion_rate || 0 }}%
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ tenant.metrics?.disputes?.total || 0 }}
                <span class="text-gray-500">({{ tenant.metrics?.disputes?.resolution_rate || 0 }}% resolved)</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ tenant.metrics?.support?.total_tickets || 0 }}
                <span class="text-gray-500">({{ tenant.metrics?.support?.resolution_rate || 0 }}% resolved)</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tenant List -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">All Tenants</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="tenants.length === 0" class="text-center py-8 text-gray-500">
        No tenants found
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="tenant in tenants"
          :key="tenant.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900">{{ tenant.name }}</h3>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    tenant.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
                    tenant.is_deleted ? 'bg-red-100 text-red-800' : ''
                  ]"
                >
                  {{ tenant.is_deleted ? 'Deleted' : tenant.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="text-sm text-gray-600 mb-2">
                <span class="font-medium">Domain:</span> {{ tenant.domain || 'N/A' }}
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div>
                  <div class="text-xs text-gray-500">Users</div>
                  <div class="text-sm font-medium">{{ tenant.user_count || 0 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">Orders</div>
                  <div class="text-sm font-medium">{{ tenant.order_count || 0 }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">Revenue</div>
                  <div class="text-sm font-medium">${{ formatCurrency(tenant.total_revenue || 0) }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">Avg Order Value</div>
                  <div class="text-sm font-medium">${{ formatCurrency(tenant.avg_order_value || 0) }}</div>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                @click="viewTenantDetails(tenant.id)"
                class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
              >
                View Details
              </button>
              <button
                @click="viewTenantAnalytics(tenant.id)"
                class="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
              >
                Analytics
              </button>
              <button
                @click="editTenant(tenant)"
                class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                :disabled="tenant.is_deleted"
              >
                Edit
              </button>
              <button
                v-if="!tenant.is_deleted"
                @click="deleteTenant(tenant.id)"
                class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
              >
                Delete
              </button>
              <button
                v-else
                @click="restoreTenant(tenant.id)"
                class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
              >
                Restore
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Tenant Modal -->
    <Modal v-if="showCreateModal" @close="showCreateModal = false">
      <template #header>
        <h3 class="text-xl font-semibold">Create New Tenant</h3>
      </template>
      <template #body>
        <form @submit.prevent="handleCreateTenant" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              v-model="tenantForm.name"
              type="text"
              required
              class="w-full border rounded px-3 py-2"
              placeholder="Tenant name"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Domain *</label>
            <input
              v-model="tenantForm.domain"
              type="text"
              required
              class="w-full border rounded px-3 py-2"
              placeholder="example.com"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="tenantForm.description"
              rows="3"
              class="w-full border rounded px-3 py-2"
              placeholder="Tenant description"
            />
          </div>
          <div>
            <label class="flex items-center gap-2">
              <input
                v-model="tenantForm.is_active"
                type="checkbox"
                class="rounded"
              />
              <span class="text-sm text-gray-700">Active</span>
            </label>
          </div>
          <div class="flex gap-3 pt-4">
            <button
              type="submit"
              :disabled="creating"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {{ creating ? 'Creating...' : 'Create Tenant' }}
            </button>
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </template>
    </Modal>

    <!-- Tenant Details Modal -->
    <Modal v-if="selectedTenant" @close="selectedTenant = null">
      <template #header>
        <h3 class="text-xl font-semibold">Tenant Details</h3>
      </template>
      <template #body>
        <div v-if="loadingDetails" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else-if="tenantDetails" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm text-gray-500">Name</div>
              <div class="font-medium">{{ tenantDetails.name }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Domain</div>
              <div class="font-medium">{{ tenantDetails.domain }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Status</div>
              <div class="font-medium">
                <span :class="tenantDetails.is_active ? 'text-green-600' : 'text-gray-600'">
                  {{ tenantDetails.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Created</div>
              <div class="font-medium">{{ formatDate(tenantDetails.created_at) }}</div>
            </div>
          </div>
          <div v-if="tenantDetails.statistics" class="mt-6 pt-6 border-t">
            <h4 class="font-semibold mb-4">Statistics</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-sm text-gray-500">Total Users</div>
                <div class="text-lg font-bold">{{ tenantDetails.statistics.total_users || 0 }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">Total Orders</div>
                <div class="text-lg font-bold">{{ tenantDetails.statistics.total_orders || 0 }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">Total Revenue</div>
                <div class="text-lg font-bold">${{ formatCurrency(tenantDetails.statistics.total_revenue || 0) }}</div>
              </div>
              <div>
                <div class="text-sm text-gray-500">Active Orders</div>
                <div class="text-lg font-bold">{{ tenantDetails.statistics.active_orders || 0 }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Modal>

    <!-- Tenant Analytics Modal -->
    <Modal v-if="analyticsTenantId" @close="analyticsTenantId = null" size="large">
      <template #header>
        <h3 class="text-xl font-semibold">Tenant Analytics</h3>
      </template>
      <template #body>
        <div v-if="loadingAnalytics" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else-if="tenantAnalytics" class="space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-blue-50 rounded-lg">
              <div class="text-sm text-gray-600">Total Revenue</div>
              <div class="text-2xl font-bold">${{ formatCurrency(tenantAnalytics.total_revenue || 0) }}</div>
            </div>
            <div class="p-4 bg-green-50 rounded-lg">
              <div class="text-sm text-gray-600">Total Orders</div>
              <div class="text-2xl font-bold">{{ tenantAnalytics.total_orders || 0 }}</div>
            </div>
          </div>
          <div v-if="tenantAnalytics.revenue_trends" class="mt-6">
            <h4 class="font-semibold mb-4">Revenue Trends</h4>
            <ChartWidget
              title="Revenue Over Time"
              type="line"
              :series="revenueTrendsSeries"
              :options="revenueTrendsOptions"
            />
          </div>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import superadminAPI from '@/api/superadmin'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import ChartWidget from '@/components/dashboard/ChartWidget.vue'
import Modal from '@/components/common/Modal.vue'

const { showToast } = useToast()

// State
const loading = ref(false)
const loadingComparison = ref(false)
const loadingDetails = ref(false)
const loadingAnalytics = ref(false)
const creating = ref(false)
const tenants = ref([])
const summary = ref({})
const comparisonData = ref(null)
const selectedTenant = ref(null)
const tenantDetails = ref(null)
const analyticsTenantId = ref(null)
const tenantAnalytics = ref(null)
const showCreateModal = ref(false)
const showComparison = ref(false)

// Filters
const filters = ref({
  search: '',
  status: '',
  sortBy: 'name'
})

// Form
const tenantForm = ref({
  name: '',
  domain: '',
  description: '',
  is_active: true
})

// Methods
const fetchTenants = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.sortBy) params.ordering = filters.value.sortBy
    
    const response = await superadminAPI.listTenants(params)
    tenants.value = response?.data?.tenants || []
    summary.value = response?.data?.summary || {}
  } catch (err) {
    console.error('Failed to fetch tenants:', err)
    showToast('Failed to load tenants', 'error')
    tenants.value = []
  } finally {
    loading.value = false
  }
}

const fetchComparison = async () => {
  if (!showComparison.value) return
  
  loadingComparison.value = true
  try {
    const response = await superadminAPI.getTenantComparison({ days: 30 })
    comparisonData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch comparison:', err)
    showToast('Failed to load comparison data', 'error')
  } finally {
    loadingComparison.value = false
  }
}

const viewTenantDetails = async (id) => {
  selectedTenant.value = { id }
  loadingDetails.value = true
  try {
    const response = await superadminAPI.getTenantDetails(id)
    tenantDetails.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch tenant details:', err)
    showToast('Failed to load tenant details', 'error')
  } finally {
    loadingDetails.value = false
  }
}

const viewTenantAnalytics = async (id) => {
  analyticsTenantId.value = id
  loadingAnalytics.value = true
  try {
    const response = await superadminAPI.getTenantAnalytics(id, { days: 30 })
    tenantAnalytics.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch tenant analytics:', err)
    showToast('Failed to load tenant analytics', 'error')
  } finally {
    loadingAnalytics.value = false
  }
}

const handleCreateTenant = async () => {
  creating.value = true
  try {
    await superadminAPI.createTenant(tenantForm.value)
    showToast('Tenant created successfully', 'success')
    showCreateModal.value = false
    tenantForm.value = { name: '', domain: '', description: '', is_active: true }
    await fetchTenants()
  } catch (err) {
    console.error('Failed to create tenant:', err)
    showToast(err.response?.data?.detail || 'Failed to create tenant', 'error')
  } finally {
    creating.value = false
  }
}

const editTenant = (tenant) => {
  // TODO: Implement edit functionality
  showToast('Edit functionality coming soon', 'info')
}

const deleteTenant = async (id) => {
  if (!confirm('Are you sure you want to delete this tenant?')) return
  
  try {
    await superadminAPI.deleteTenant(id)
    showToast('Tenant deleted successfully', 'success')
    await fetchTenants()
  } catch (err) {
    console.error('Failed to delete tenant:', err)
    showToast(err.response?.data?.detail || 'Failed to delete tenant', 'error')
  }
}

const restoreTenant = async (id) => {
  try {
    await superadminAPI.restoreTenant(id)
    showToast('Tenant restored successfully', 'success')
    await fetchTenants()
  } catch (err) {
    console.error('Failed to restore tenant:', err)
    showToast(err.response?.data?.detail || 'Failed to restore tenant', 'error')
  }
}

const handleFilter = () => {
  fetchTenants()
}

const resetFilters = () => {
  filters.value = { search: '', status: '', sortBy: 'name' }
  fetchTenants()
}

const refreshData = () => {
  fetchTenants()
  if (showComparison.value) {
    fetchComparison()
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Computed
const revenueTrendsSeries = computed(() => {
  if (!tenantAnalytics.value?.revenue_trends?.length) return []
  return [{
    name: 'Revenue',
    data: tenantAnalytics.value.revenue_trends.map(t => parseFloat(t.revenue || 0))
  }]
})

const revenueTrendsOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: {
    categories: tenantAnalytics.value?.revenue_trends?.map(t => {
      if (t.date) {
        return new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || []
  },
  yaxis: { title: { text: 'Revenue ($)' } },
  stroke: { curve: 'smooth' },
  colors: ['#3B82F6']
}))

// Watch
watch(showComparison, (newVal) => {
  if (newVal) {
    fetchComparison()
  }
})

// Lifecycle
onMounted(() => {
  fetchTenants()
})
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

