<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Writer Feedback Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage structured feedback for writers</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Feedback</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Avg Rating</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ formatNumber(stats.avg_rating) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Editor Feedback</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.editor_feedback || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Client Feedback</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.client_feedback || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by writer, order ID, or feedback content..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="feedbackTypeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadFeedback"
        >
          <option value="">All Types</option>
          <option value="editor_to_writer">Editor to Writer</option>
          <option value="client_to_writer">Client to Writer</option>
          <option value="client_to_editor">Client to Editor</option>
          <option value="writer_to_client">Writer to Client</option>
        </select>
        <select
          v-model="ratingFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadFeedback"
        >
          <option value="">All Ratings</option>
          <option value="5">5 Stars</option>
          <option value="4">4 Stars</option>
          <option value="3">3 Stars</option>
          <option value="2">2 Stars</option>
          <option value="1">1 Star</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading feedback...</p>
    </div>

    <!-- Feedback List -->
    <div v-else class="space-y-4">
      <div
        v-for="feedback in feedbackList"
        :key="feedback.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Order #{{ feedback.order || feedback.order_id || 'N/A' }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  feedback.feedback_type === 'editor_to_writer' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                  feedback.feedback_type === 'client_to_writer' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                ]"
              >
                {{ formatFeedbackType(feedback.feedback_type) }}
              </span>
              <div class="flex items-center gap-1">
                <span v-for="i in 5" :key="i" class="text-lg"
                  :class="i <= (feedback.overall_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                >
                  ★
                </span>
              </div>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-2">
              <div>
                <span class="text-gray-500 dark:text-gray-400">From:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ feedback.from_user_name || feedback.from_user || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">To:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ feedback.to_user_name || feedback.to_user || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Quality:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ feedback.quality_rating ? '★'.repeat(feedback.quality_rating) : 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Timeliness:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ feedback.timeliness_rating ? '★'.repeat(feedback.timeliness_rating) : 'N/A' }}</span>
              </div>
            </div>
            <div v-if="feedback.strengths" class="mb-2">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Strengths:</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ feedback.strengths }}</p>
            </div>
            <div v-if="feedback.areas_for_improvement" class="mb-2">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Areas for Improvement:</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ feedback.areas_for_improvement }}</p>
            </div>
            <div v-if="feedback.specific_feedback" class="mb-2">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Specific Feedback:</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ feedback.specific_feedback }}</p>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              <span>{{ formatDate(feedback.created_at) }}</span>
              <span v-if="feedback.is_public" class="ml-2 px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded">
                Public
              </span>
              <span v-if="feedback.is_anonymous" class="ml-2 px-2 py-1 bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300 rounded">
                Anonymous
              </span>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="viewFeedback(feedback)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              View
            </button>
            <button
              @click="deleteFeedback(feedback)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div v-if="feedbackList.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No feedback found
      </div>
    </div>

    <!-- View Feedback Modal -->
    <Modal
      :visible="showViewModal"
      @close="closeViewModal"
      title="Feedback Details"
      size="lg"
    >
      <div v-if="selectedFeedback" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">From</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedFeedback.from_user_name || selectedFeedback.from_user }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">To</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedFeedback.to_user_name || selectedFeedback.to_user }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Order</p>
            <p class="font-medium text-gray-900 dark:text-white">#{{ selectedFeedback.order || selectedFeedback.order_id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Type</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatFeedbackType(selectedFeedback.feedback_type) }}</p>
          </div>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Overall Rating</p>
          <div class="flex items-center gap-2">
            <div class="flex">
              <span v-for="i in 5" :key="i" class="text-2xl"
                :class="i <= (selectedFeedback.overall_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
              >
                ★
              </span>
            </div>
            <span class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedFeedback.overall_rating }}/5</span>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Quality</p>
            <div class="flex">
              <span v-for="i in 5" :key="i" class="text-lg"
                :class="i <= (selectedFeedback.quality_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
              >
                ★
              </span>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Communication</p>
            <div class="flex">
              <span v-for="i in 5" :key="i" class="text-lg"
                :class="i <= (selectedFeedback.communication_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
              >
                ★
              </span>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Timeliness</p>
            <div class="flex">
              <span v-for="i in 5" :key="i" class="text-lg"
                :class="i <= (selectedFeedback.timeliness_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
              >
                ★
              </span>
            </div>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Professionalism</p>
            <div class="flex">
              <span v-for="i in 5" :key="i" class="text-lg"
                :class="i <= (selectedFeedback.professionalism_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
              >
                ★
              </span>
            </div>
          </div>
        </div>
        <div v-if="selectedFeedback.strengths">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Strengths</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedFeedback.strengths }}</p>
        </div>
        <div v-if="selectedFeedback.areas_for_improvement">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Areas for Improvement</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedFeedback.areas_for_improvement }}</p>
        </div>
        <div v-if="selectedFeedback.specific_feedback">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Specific Feedback</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedFeedback.specific_feedback }}</p>
        </div>
      </div>
    </Modal>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import writerManagementAPI from '@/api/writer-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const feedbackList = ref([])
const stats = ref({})
const searchQuery = ref('')
const feedbackTypeFilter = ref('')
const ratingFilter = ref('')
const showViewModal = ref(false)
const selectedFeedback = ref(null)

const debouncedSearch = debounce(() => {
  loadFeedback()
}, 300)

const formatNumber = (num) => {
  if (!num && num !== 0) return '0.0'
  return Number(num).toFixed(1)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const formatFeedbackType = (type) => {
  if (!type) return 'N/A'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const loadFeedback = async () => {
  loading.value = true
  try {
    const params = {}
    if (feedbackTypeFilter.value) params.feedback_type = feedbackTypeFilter.value
    if (ratingFilter.value) params.overall_rating = ratingFilter.value
    
    const response = await writerManagementAPI.listFeedback(params)
    let allFeedback = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allFeedback = allFeedback.filter(f => 
        (f.from_user_name && f.from_user_name.toLowerCase().includes(query)) ||
        (f.to_user_name && f.to_user_name.toLowerCase().includes(query)) ||
        (f.order && String(f.order).includes(query)) ||
        (f.strengths && f.strengths.toLowerCase().includes(query)) ||
        (f.areas_for_improvement && f.areas_for_improvement.toLowerCase().includes(query))
      )
    }
    
    feedbackList.value = allFeedback
    
    // Calculate stats
    const ratings = allFeedback.filter(f => f.overall_rating).map(f => f.overall_rating)
    stats.value = {
      total: allFeedback.length,
      avg_rating: ratings.length > 0 ? ratings.reduce((sum, r) => sum + r, 0) / ratings.length : 0,
      editor_feedback: allFeedback.filter(f => f.feedback_type === 'editor_to_writer').length,
      client_feedback: allFeedback.filter(f => f.feedback_type === 'client_to_writer').length,
    }
  } catch (error) {
    showError('Failed to load feedback')
    console.error('Error loading feedback:', error)
  } finally {
    loading.value = false
  }
}

const viewFeedback = (feedback) => {
  selectedFeedback.value = feedback
  showViewModal.value = true
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedFeedback.value = null
}

const deleteFeedback = (feedback) => {
  confirm.showDestructive(
    'Delete Feedback',
    `Are you sure you want to delete this feedback?`,
    `Order #${feedback.order || feedback.order_id}\nType: ${formatFeedbackType(feedback.feedback_type)}`,
    async () => {
      try {
        await writerManagementAPI.deleteFeedback(feedback.id)
        showSuccess('Feedback deleted successfully')
        loadFeedback()
      } catch (error) {
        showError('Failed to delete feedback')
      }
    }
  )
}

onMounted(() => {
  loadFeedback()
})
</script>

