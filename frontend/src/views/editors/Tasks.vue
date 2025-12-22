<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Tasks</h1>
        <p class="mt-2 text-gray-600">Manage your assigned editing tasks</p>
      </div>
      <button @click="loadTasks" :disabled="tasksLoading" class="btn btn-secondary">
        {{ tasksLoading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Active Tasks</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.active_tasks || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending_tasks || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">In Review</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.in_review_tasks || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.completed_tasks || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadTasks" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_review">In Review</option>
            <option value="completed">Completed</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Priority</label>
          <select v-model="filters.priority" @change="loadTasks" class="w-full border rounded px-3 py-2">
            <option value="">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
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

    <!-- Tasks Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="tasksLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Deadline</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pages</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="task in tasks" :key="task.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ task.order?.id || task.order_id || 'N/A' }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ task.order?.title || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusBadgeClass(task.review_status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ task.review_status_display || task.review_status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ task.order?.deadline ? formatDate(task.order.deadline) : 'N/A' }}
              <span v-if="isUrgent(task.order?.deadline)" class="ml-2 text-xs text-red-600">⚠️ Urgent</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ task.order?.number_of_pages || 0 }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(task.assigned_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button v-if="task.review_status === 'pending'" @click="startReview(task)" class="text-blue-600 hover:text-blue-900 mr-3">Start</button>
              <button v-if="task.review_status === 'in_review'" @click="viewTask(task)" class="text-green-600 hover:text-green-900 mr-3">Continue</button>
              <button @click="viewTask(task)" class="text-gray-600 hover:text-gray-900">View</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!tasksLoading && tasks.length === 0" class="text-center py-12 text-gray-500">
        <p>No tasks found</p>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <div v-if="selectedTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Task Details - Order #{{ selectedTask.order?.id || selectedTask.order_id }}</h2>
            <button @click="selectedTask = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-6">
          <!-- Task Info -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <span :class="getStatusBadgeClass(selectedTask.review_status)" class="px-3 py-1 text-sm font-semibold rounded-full">
                {{ selectedTask.review_status_display || selectedTask.review_status }}
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned At</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedTask.assigned_at) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
              <p class="text-sm text-gray-900">{{ selectedTask.order?.deadline ? formatDate(selectedTask.order.deadline) : 'N/A' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pages</label>
              <p class="text-sm text-gray-900">{{ selectedTask.order?.number_of_pages || 0 }}</p>
            </div>
          </div>

          <!-- Order Details -->
          <div v-if="selectedTask.order">
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Order Information</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <p class="text-sm text-gray-900">{{ selectedTask.order.title || 'N/A' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
                <p class="text-sm text-gray-900">{{ selectedTask.order.service_type || 'N/A' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Academic Level</label>
                <p class="text-sm text-gray-900">{{ selectedTask.order.academic_level || 'N/A' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <p class="text-sm text-gray-900">{{ selectedTask.order.subject || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="border-t pt-4">
            <div class="flex justify-end space-x-3">
              <button v-if="selectedTask.review_status === 'pending'" @click="startReview(selectedTask)" class="btn btn-primary">Start Review</button>
              <button v-if="selectedTask.review_status === 'in_review'" @click="showSubmitReviewModal = true" class="btn btn-primary">Submit Review</button>
              <button @click="selectedTask = null" class="btn btn-secondary">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Review Modal -->
    <div v-if="showSubmitReviewModal && selectedTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <h2 class="text-2xl font-bold text-gray-900">Submit Review</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Quality Score (0-10) *</label>
            <input v-model.number="reviewForm.quality_score" type="number" min="0" max="10" step="0.1" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Issues Found</label>
            <textarea v-model="reviewForm.issues_found" rows="3" class="w-full border rounded px-3 py-2" placeholder="Describe any issues found..."></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Corrections Made</label>
            <textarea v-model="reviewForm.corrections_made" rows="3" class="w-full border rounded px-3 py-2" placeholder="Describe corrections made..."></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Recommendations</label>
            <textarea v-model="reviewForm.recommendations" rows="3" class="w-full border rounded px-3 py-2" placeholder="Any recommendations..."></textarea>
          </div>
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input v-model="reviewForm.is_approved" type="checkbox" class="mr-2" />
              <span class="text-sm">Approve for delivery</span>
            </label>
            <label class="flex items-center">
              <input v-model="reviewForm.requires_revision" type="checkbox" class="mr-2" />
              <span class="text-sm">Requires revision</span>
            </label>
          </div>
          <div v-if="reviewForm.requires_revision">
            <label class="block text-sm font-medium mb-1">Revision Notes *</label>
            <textarea v-model="reviewForm.revision_notes" rows="4" class="w-full border rounded px-3 py-2" placeholder="Provide revision notes for the writer..."></textarea>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="closeSubmitReviewModal" class="btn btn-secondary">Cancel</button>
          <button @click="submitReview" :disabled="submittingReview" class="btn btn-primary">
            {{ submittingReview ? 'Submitting...' : 'Submit Review' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { debounce } from '@/utils/debounce'
import editorTasksAPI from '@/api/editor-tasks'

const tasks = ref([])
const tasksLoading = ref(false)
const stats = ref({})
const filters = ref({
  status: '',
  priority: '',
  search: '',
})
const selectedTask = ref(null)
const showSubmitReviewModal = ref(false)
const reviewForm = ref({
  quality_score: null,
  issues_found: '',
  corrections_made: '',
  recommendations: '',
  is_approved: false,
  requires_revision: false,
  revision_notes: '',
})
const submittingReview = ref(false)

const loadTasks = async () => {
  tasksLoading.value = true
  try {
    const params = {}
    if (filters.value.status) params.review_status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    
    const response = await editorTasksAPI.list(params)
    tasks.value = response.data.results || response.data || []
    
    // Calculate stats
    stats.value = {
      active_tasks: tasks.value.filter(t => ['pending', 'in_review'].includes(t.review_status)).length,
      pending_tasks: tasks.value.filter(t => t.review_status === 'pending').length,
      in_review_tasks: tasks.value.filter(t => t.review_status === 'in_review').length,
      completed_tasks: tasks.value.filter(t => t.review_status === 'completed').length,
    }
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    tasksLoading.value = false
  }
}

const loadDashboardStats = async () => {
  try {
    const response = await editorTasksAPI.getDashboardStats()
    if (response.data) {
      stats.value = {
        ...stats.value,
        ...response.data,
      }
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
  }
}

const startReview = async (task) => {
  try {
    await editorTasksAPI.startReview(task.id, {})
    await loadTasks()
    if (selectedTask.value && selectedTask.value.id === task.id) {
      selectedTask.value = task
      await loadTasks()
    }
    alert('Review started successfully')
  } catch (error) {
    console.error('Failed to start review:', error)
    alert('Failed to start review. Please try again.')
  }
}

const viewTask = (task) => {
  selectedTask.value = task
}

const submitReview = async () => {
  if (!reviewForm.value.quality_score && reviewForm.value.quality_score !== 0) {
    alert('Please provide a quality score')
    return
  }
  
  if (reviewForm.value.requires_revision && !reviewForm.value.revision_notes.trim()) {
    alert('Please provide revision notes')
    return
  }
  
  submittingReview.value = true
  try {
    await editorTasksAPI.submitReview({
      task_id: selectedTask.value.id,
      ...reviewForm.value,
    })
    await loadTasks()
    closeSubmitReviewModal()
    selectedTask.value = null
    alert('Review submitted successfully')
  } catch (error) {
    console.error('Failed to submit review:', error)
    alert('Failed to submit review. Please try again.')
  } finally {
    submittingReview.value = false
  }
}

const closeSubmitReviewModal = () => {
  showSubmitReviewModal.value = false
  reviewForm.value = {
    quality_score: null,
    issues_found: '',
    corrections_made: '',
    recommendations: '',
    is_approved: false,
    requires_revision: false,
    revision_notes: '',
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    priority: '',
    search: '',
  }
  loadTasks()
}

const debouncedSearch = debounce(() => {
  loadTasks()
}, 500)

const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_review: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
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
  loadTasks()
  loadDashboardStats()
})
</script>

