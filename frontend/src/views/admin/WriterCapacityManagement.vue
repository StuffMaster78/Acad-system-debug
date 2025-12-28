<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Writer Capacity Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage writer capacity, availability, and blackout periods</p>
      </div>
      <button @click="loadCapacities" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Writers</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">At Capacity</p>
        <p class="text-3xl font-bold text-red-600 dark:text-red-400">{{ stats.at_capacity }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Available</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.available }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">With Blackouts</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.with_blackouts }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by writer name..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.status"
            @change="loadCapacities"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="available">Available</option>
            <option value="at_capacity">At Capacity</option>
            <option value="blackout">Has Blackouts</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Capacities List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!capacities.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No writer capacities found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Max Orders</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Active Orders</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Available</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blackout Periods</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="capacity in capacities" :key="capacity.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ capacity.writer?.username || capacity.writer?.email || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ capacity.writer?.role || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ capacity.max_active_orders || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ capacity.current_active_orders || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ (capacity.max_active_orders || 0) - (capacity.current_active_orders || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ capacity.blackout_periods?.length || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(capacity)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusText(capacity) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewCapacity(capacity)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editCapacity(capacity)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal && editingCapacity" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Edit Writer Capacity</h3>
        </div>
        <form @submit.prevent="saveCapacity" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Max Active Orders *</label>
            <input
              v-model.number="capacityForm.max_active_orders"
              type="number"
              min="1"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Current Active Orders</label>
            <input
              v-model.number="capacityForm.current_active_orders"
              type="number"
              min="0"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Manually update if needed</p>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : 'Update' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { writerCapacityAPI } from '@/api/writer-capacity'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'

const { showSuccess, showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const capacities = ref([])
const stats = ref({ total: 0, at_capacity: 0, available: 0, with_blackouts: 0 })
const showEditModal = ref(false)
const editingCapacity = ref(null)

const filters = ref({
  search: '',
  status: '',
})

const capacityForm = ref({
  max_active_orders: 5,
  current_active_orders: 0,
})

const debouncedSearch = debounce(() => {
  loadCapacities()
}, 300)

const loadCapacities = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    
    const res = await writerCapacityAPI.list(params)
    capacities.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: capacities.value.length,
      at_capacity: capacities.value.filter(c => {
        const max = c.max_active_orders || 0
        const current = c.current_active_orders || 0
        return current >= max
      }).length,
      available: capacities.value.filter(c => {
        const max = c.max_active_orders || 0
        const current = c.current_active_orders || 0
        return current < max
      }).length,
      with_blackouts: capacities.value.filter(c => c.blackout_periods && c.blackout_periods.length > 0).length,
    }
  } catch (error) {
    console.error('Failed to load capacities:', error)
    showError('Failed to load capacities: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewCapacity = (capacity) => {
  // Show capacity details
  alert(`Writer: ${capacity.writer?.username || 'N/A'}\nMax Orders: ${capacity.max_active_orders || 'N/A'}\nActive: ${capacity.current_active_orders || 0}\nBlackouts: ${capacity.blackout_periods?.length || 0}`)
}

const editCapacity = (capacity) => {
  editingCapacity.value = capacity
  capacityForm.value = {
    max_active_orders: capacity.max_active_orders || 5,
    current_active_orders: capacity.current_active_orders || 0,
  }
  showEditModal.value = true
}

const saveCapacity = async () => {
  saving.value = true
  try {
    if (editingCapacity.value.id) {
      await writerCapacityAPI.update(editingCapacity.value.id, capacityForm.value)
      showSuccess('Capacity updated successfully')
    } else {
      await writerCapacityAPI.create({
        ...capacityForm.value,
        writer: editingCapacity.value.writer?.id || editingCapacity.value.writer,
      })
      showSuccess('Capacity created successfully')
    }
    
    closeModal()
    await loadCapacities()
  } catch (error) {
    console.error('Failed to save capacity:', error)
    showError('Failed to save capacity: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showEditModal.value = false
  editingCapacity.value = null
  capacityForm.value = {
    max_active_orders: 5,
    current_active_orders: 0,
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  loadCapacities()
}

const getStatusBadgeClass = (capacity) => {
  const max = capacity.max_active_orders || 0
  const current = capacity.current_active_orders || 0
  
  if (current >= max) {
    return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  } else if (capacity.blackout_periods && capacity.blackout_periods.length > 0) {
    return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
  } else {
    return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
  }
}

const getStatusText = (capacity) => {
  const max = capacity.max_active_orders || 0
  const current = capacity.current_active_orders || 0
  
  if (current >= max) {
    return 'At Capacity'
  } else if (capacity.blackout_periods && capacity.blackout_periods.length > 0) {
    return 'Blackout'
  } else {
    return 'Available'
  }
}

onMounted(() => {
  loadCapacities()
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
</style>

