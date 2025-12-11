<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Editor Workload Tracker</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Monitor and manage editor workload and capacity</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Editors</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Available</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.available || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">At Capacity</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.at_capacity || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Tasks</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total_tasks || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by editor email or name..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="availabilityFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadWorkloads"
        >
          <option value="">All Availability</option>
          <option value="true">Available</option>
          <option value="false">Unavailable</option>
        </select>
        <select
          v-model="capacityFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadWorkloads"
        >
          <option value="">All Capacity</option>
          <option value="at_capacity">At Capacity</option>
          <option value="available">Has Capacity</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading editor workloads...</p>
    </div>

    <!-- Workloads Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Editor</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Tasks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Capacity</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Utilization</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="workload in workloads"
              :key="workload.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ workload.editor_email || workload.editor || 'Unknown' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    workload.is_available ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                  ]"
                >
                  {{ workload.is_available ? 'Available' : 'Unavailable' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ workload.current_active_tasks || 0 }} / {{ workload.max_active_tasks || 10 }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">
                  {{ workload.max_active_tasks || 10 }} max
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-24 bg-gray-200 rounded-full h-2 dark:bg-gray-700 mr-2">
                    <div
                      class="h-2 rounded-full transition-all"
                      :class="getUtilizationColor(workload)"
                      :style="{ width: `${getUtilizationPercent(workload)}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600 dark:text-gray-400">
                    {{ getUtilizationPercent(workload) }}%
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="editWorkload(workload)"
                  class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                >
                  Edit
                </button>
                <button
                  @click="viewDetails(workload)"
                  class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="workloads.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No editor workloads found
      </div>
    </div>

    <!-- Edit Workload Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      title="Edit Editor Workload"
      size="md"
    >
      <div v-if="editingWorkload" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Max Active Tasks</label>
          <input
            v-model.number="form.max_active_tasks"
            type="number"
            min="1"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_available"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Available</span>
          </label>
        </div>
        <div v-if="formError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ formError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveWorkload"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : 'Update' }}
        </button>
      </template>
    </Modal>

    <!-- View Details Modal -->
    <Modal
      :visible="showDetailsModal"
      @close="closeDetailsModal"
      :title="`Editor Workload Details - ${selectedWorkload?.editor_email || 'Editor'}`"
      size="lg"
    >
      <div v-if="selectedWorkload" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Editor</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedWorkload.editor_email || selectedWorkload.editor }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
            <span
              :class="[
                'px-2 py-1 text-xs font-semibold rounded-full',
                selectedWorkload.is_available ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
              ]"
            >
              {{ selectedWorkload.is_available ? 'Available' : 'Unavailable' }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Current Tasks</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedWorkload.current_active_tasks || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Max Tasks</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedWorkload.max_active_tasks || 10 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Utilization</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ getUtilizationPercent(selectedWorkload) }}%</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Remaining Capacity</p>
            <p class="font-medium text-gray-900 dark:text-white">
              {{ (selectedWorkload.max_active_tasks || 10) - (selectedWorkload.current_active_tasks || 0) }} tasks
            </p>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'
import Modal from '@/components/common/Modal.vue'
import { writerCapacityAPI } from '@/api/writer-capacity'

const { success: showSuccess, error: showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const workloads = ref([])
const stats = ref({})
const searchQuery = ref('')
const availabilityFilter = ref('')
const capacityFilter = ref('')
const showModal = ref(false)
const showDetailsModal = ref(false)
const editingWorkload = ref(null)
const selectedWorkload = ref(null)
const formError = ref('')

const form = ref({
  max_active_tasks: 10,
  is_available: true,
})

const debouncedSearch = debounce(() => {
  loadWorkloads()
}, 300)

const getUtilizationPercent = (workload) => {
  if (!workload.max_active_tasks || workload.max_active_tasks === 0) return 0
  const current = workload.current_active_tasks || 0
  const max = workload.max_active_tasks
  return Math.round((current / max) * 100)
}

const getUtilizationColor = (workload) => {
  const percent = getUtilizationPercent(workload)
  if (percent >= 90) return 'bg-red-500'
  if (percent >= 75) return 'bg-orange-500'
  if (percent >= 50) return 'bg-yellow-500'
  return 'bg-green-500'
}

const loadWorkloads = async () => {
  loading.value = true
  try {
    const params = {}
    if (availabilityFilter.value !== '') params.is_available = availabilityFilter.value === 'true'
    
    const response = await writerCapacityAPI.editor.list(params)
    let allWorkloads = response.data.results || response.data || []
    
    if (capacityFilter.value === 'at_capacity') {
      allWorkloads = allWorkloads.filter(w => {
        const current = w.current_active_tasks || 0
        const max = w.max_active_tasks || 10
        return current >= max
      })
    } else if (capacityFilter.value === 'available') {
      allWorkloads = allWorkloads.filter(w => {
        const current = w.current_active_tasks || 0
        const max = w.max_active_tasks || 10
        return current < max
      })
    }
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allWorkloads = allWorkloads.filter(w => 
        (w.editor_email && w.editor_email.toLowerCase().includes(query)) ||
        (w.editor && String(w.editor).toLowerCase().includes(query))
      )
    }
    
    workloads.value = allWorkloads
    
    stats.value = {
      total: allWorkloads.length,
      available: allWorkloads.filter(w => w.is_available).length,
      at_capacity: allWorkloads.filter(w => {
        const current = w.current_active_tasks || 0
        const max = w.max_active_tasks || 10
        return current >= max
      }).length,
      total_tasks: allWorkloads.reduce((sum, w) => sum + (w.current_active_tasks || 0), 0),
    }
  } catch (error) {
    showError('Failed to load editor workloads')
    console.error('Error loading workloads:', error)
  } finally {
    loading.value = false
  }
}

const editWorkload = (workload) => {
  editingWorkload.value = workload
  form.value = {
    max_active_tasks: workload.max_active_tasks || 10,
    is_available: workload.is_available !== undefined ? workload.is_available : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingWorkload.value = null
  formError.value = ''
}

const saveWorkload = async () => {
  saving.value = true
  formError.value = ''
  try {
    await writerCapacityAPI.editor.update(editingWorkload.value.id, form.value)
    showSuccess('Editor workload updated successfully')
    closeModal()
    loadWorkloads()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to update workload'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const viewDetails = (workload) => {
  selectedWorkload.value = workload
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedWorkload.value = null
}

onMounted(() => {
  loadWorkloads()
})
</script>

