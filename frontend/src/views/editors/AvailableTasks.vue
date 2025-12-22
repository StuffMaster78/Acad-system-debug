<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Available Tasks</h1>
        <p class="mt-2 text-gray-600">Claim unassigned editing tasks</p>
      </div>
      <button @click="loadAvailableTasks" :disabled="loading" class="btn btn-secondary">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Available Tasks</p>
        <p class="text-3xl font-bold text-blue-900">{{ availableTasks.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Urgent</p>
        <p class="text-3xl font-bold text-yellow-900">{{ urgentTasks.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">High Priority</p>
        <p class="text-3xl font-bold text-orange-900">{{ highPriorityTasks.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Can Claim</p>
        <p class="text-3xl font-bold text-green-900">{{ canClaimCount }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Service Type</label>
          <select v-model="filters.service_type" @change="filterTasks" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option v-for="type in serviceTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Max Pages</label>
          <input v-model.number="filters.max_pages" type="number" @input="filterTasks" class="w-full border rounded px-3 py-2" placeholder="Any" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by order ID..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Available Tasks Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service Type</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pages</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deadline</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="task in filteredTasks" :key="task.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ task.order?.id || task.order_id || 'N/A' }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ task.order?.title || task.order_topic || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ task.order?.service_type || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ task.order?.number_of_pages || task.order?.pages || 0 }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ task.order?.deadline ? formatDate(task.order.deadline) : (task.order_deadline ? formatDate(task.order_deadline) : 'N/A') }}
              <span v-if="isUrgent(task.order?.deadline || task.order_deadline)" class="ml-2 text-xs text-red-600">⚠️ Urgent</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusBadgeClass(task.review_status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ task.review_status_display || task.review_status || 'Unclaimed' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button @click="viewTask(task)" class="text-blue-600 hover:text-blue-900 mr-3">View</button>
              <button @click="claimTask(task)" :disabled="claimingTask === task.id" class="text-green-600 hover:text-green-900">
                {{ claimingTask === task.id ? 'Claiming...' : 'Claim' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && filteredTasks.length === 0" class="text-center py-12 text-gray-500">
        <p>No available tasks found</p>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <div v-if="selectedTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Task Details - Order #{{ selectedTask.order?.id || selectedTask.order_id }}</h2>
            <button @click="selectedTask = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <p class="text-sm text-gray-900">{{ selectedTask.order?.service_type || 'N/A' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pages</label>
              <p class="text-sm text-gray-900">{{ selectedTask.order?.number_of_pages || selectedTask.order?.pages || 0 }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
              <p class="text-sm text-gray-900">{{ selectedTask.order?.deadline ? formatDate(selectedTask.order.deadline) : (selectedTask.order_deadline ? formatDate(selectedTask.order_deadline) : 'N/A') }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <span :class="getStatusBadgeClass(selectedTask.review_status)" class="px-3 py-1 text-sm font-semibold rounded-full">
                {{ selectedTask.review_status_display || selectedTask.review_status || 'Unclaimed' }}
              </span>
            </div>
          </div>
          <div v-if="selectedTask.order">
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <p class="text-sm text-gray-900">{{ selectedTask.order.title || selectedTask.order_topic || 'N/A' }}</p>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="selectedTask = null" class="btn btn-secondary">Close</button>
          <button @click="claimTask(selectedTask)" :disabled="claimingTask === selectedTask.id" class="btn btn-primary">
            {{ claimingTask === selectedTask.id ? 'Claiming...' : 'Claim Task' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { debounce } from '@/utils/debounce'
import editorTasksAPI from '@/api/editor-tasks'

const loading = ref(false)
const availableTasks = ref([])
const filters = ref({
  service_type: '',
  max_pages: null,
  search: '',
})
const selectedTask = ref(null)
const claimingTask = ref(null)

const serviceTypes = computed(() => {
  const types = new Set()
  availableTasks.value.forEach(t => {
    if (t.order?.service_type) types.add(t.order.service_type)
  })
  return Array.from(types).sort()
})

const urgentTasks = computed(() => {
  return availableTasks.value.filter(t => {
    const deadline = t.order?.deadline || t.order_deadline
    return isUrgent(deadline)
  })
})

const highPriorityTasks = computed(() => {
  // Tasks with deadlines within 3 days
  const now = new Date()
  return availableTasks.value.filter(t => {
    const deadline = t.order?.deadline || t.order_deadline
    if (!deadline) return false
    const deadlineDate = new Date(deadline)
    const daysUntilDeadline = (deadlineDate - now) / (1000 * 60 * 60 * 24)
    return daysUntilDeadline <= 3 && daysUntilDeadline >= 0
  })
})

const canClaimCount = computed(() => {
  return availableTasks.value.length
})

const filteredTasks = computed(() => {
  let filtered = [...availableTasks.value]
  
  if (filters.value.service_type) {
    filtered = filtered.filter(t => t.order?.service_type === filters.value.service_type)
  }
  if (filters.value.max_pages !== null) {
    filtered = filtered.filter(t => (t.order?.number_of_pages || t.order?.pages || 0) <= filters.value.max_pages)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(t => {
      const orderId = String(t.order?.id || t.order_id || '')
      return orderId.includes(search)
    })
  }
  
  return filtered
})

const loadAvailableTasks = async () => {
  loading.value = true
  try {
    const response = await editorTasksAPI.getAvailableTasks({})
    availableTasks.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load available tasks:', error)
    alert('Failed to load available tasks. Please try again.')
  } finally {
    loading.value = false
  }
}

const claimTask = async (task) => {
  if (!task || (!task.order?.id && !task.order_id)) return
  
  claimingTask.value = task.id
  try {
    await editorTasksAPI.claim({
      order_id: task.order?.id || task.order_id,
    })
    await loadAvailableTasks()
    alert('Task claimed successfully')
    if (selectedTask.value && selectedTask.value.id === task.id) {
      selectedTask.value = null
    }
  } catch (error) {
    console.error('Failed to claim task:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Failed to claim task. Please try again.'
    alert(errorMsg)
  } finally {
    claimingTask.value = null
  }
}

const viewTask = (task) => {
  selectedTask.value = task
}

const resetFilters = () => {
  filters.value = {
    service_type: '',
    max_pages: null,
    search: '',
  }
}

const filterTasks = () => {
  // Filters are reactive, no action needed
}

const debouncedSearch = debounce(() => {
  // Search is handled by computed property
}, 500)

const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_review: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    unclaimed: 'bg-gray-100 text-gray-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const isUrgent = (deadline) => {
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const daysUntilDeadline = (deadlineDate - now) / (1000 * 60 * 60 * 24)
  return daysUntilDeadline <= 2 && daysUntilDeadline >= 0
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadAvailableTasks()
})
</script>

