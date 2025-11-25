<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Review Moderation</h1>
        <p class="mt-2 text-gray-600">Approve, reject, or flag reviews pending moderation</p>
      </div>
      <button
        @click="loadModerationQueue"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Reviews</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Website Reviews</p>
        <p class="text-3xl font-bold text-blue-900">{{ countsByType.website || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Writer Reviews</p>
        <p class="text-3xl font-bold text-green-900">{{ countsByType.writer || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Order Reviews</p>
        <p class="text-3xl font-bold text-purple-900">{{ countsByType.order || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Review Type</label>
          <select v-model="filters.type" @change="loadModerationQueue" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="website">Website Reviews</option>
            <option value="writer">Writer Reviews</option>
            <option value="order">Order Reviews</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadModerationQueue" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="flagged">Flagged</option>
            <option value="shadowed">Shadowed</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by reviewer name or content..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && reviews.length === 0" class="card p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="ml-3 text-gray-600">Loading reviews...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="reviews.length === 0" class="card p-12 text-center">
      <p class="text-gray-500 text-lg">No reviews pending moderation</p>
      <p class="text-gray-400 text-sm mt-2">All reviews have been moderated</p>
    </div>

    <!-- Reviews List -->
    <div v-else class="space-y-4">
      <div
        v-for="review in filteredReviews"
        :key="`${review.type}-${review.id}`"
        class="card p-6 hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <span
                class="px-3 py-1 rounded-full text-xs font-medium"
                :class="getTypeClass(review.type)"
              >
                {{ getTypeLabel(review.type) }}
              </span>
              <span
                v-if="review.data.is_flagged"
                class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
              >
                ⚠️ Flagged
              </span>
              <span
                v-if="review.data.is_shadowed"
                class="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
              >
                👁️ Shadowed
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <span class="text-sm font-medium text-gray-600">Reviewer:</span>
                <p class="text-gray-900">{{ review.data.reviewer_name || review.data.reviewer?.username || 'N/A' }}</p>
              </div>
              <div>
                <span class="text-sm font-medium text-gray-600">Submitted:</span>
                <p class="text-gray-900">{{ formatDate(review.data.submitted_at) }}</p>
              </div>
              <div v-if="review.type === 'order' && review.data.order">
                <span class="text-sm font-medium text-gray-600">Order:</span>
                <p class="text-gray-900">#{{ review.data.order }}</p>
              </div>
              <div v-if="review.type === 'writer' && review.data.writer">
                <span class="text-sm font-medium text-gray-600">Writer:</span>
                <p class="text-gray-900">{{ review.data.writer_name || review.data.writer?.username || 'N/A' }}</p>
              </div>
            </div>

            <div v-if="review.data.rating" class="mb-3">
              <span class="text-sm font-medium text-gray-600">Rating:</span>
              <div class="flex items-center gap-1 mt-1">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="text-xl"
                  :class="i <= review.data.rating ? 'text-yellow-400' : 'text-gray-300'"
                >
                  ★
                </span>
                <span class="ml-2 text-gray-600">({{ review.data.rating }}/5)</span>
              </div>
            </div>

            <div v-if="review.data.comment" class="mb-4">
              <span class="text-sm font-medium text-gray-600">Comment:</span>
              <div class="mt-1 p-3 bg-gray-50 rounded border border-gray-200">
                <SafeHtml :content="review.data.comment" container-class="text-gray-700" />
              </div>
            </div>

            <div v-if="review.data.flag_reason" class="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <span class="text-sm font-medium text-red-700">Flag Reason:</span>
              <p class="text-red-800 mt-1">{{ review.data.flag_reason }}</p>
            </div>

            <div v-if="review.data.moderation_notes" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
              <span class="text-sm font-medium text-blue-700">Moderation Notes:</span>
              <p class="text-blue-800 mt-1">{{ review.data.moderation_notes }}</p>
            </div>
          </div>

          <div class="ml-4 flex flex-col gap-2">
            <button
              @click="openModerateModal(review, 'approve')"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              ✓ Approve
            </button>
            <button
              @click="openModerateModal(review, 'reject')"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
            >
              ✗ Reject
            </button>
            <button
              @click="openModerateModal(review, 'flag')"
              class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
            >
              ⚠️ Flag
            </button>
            <button
              @click="openModerateModal(review, 'shadow')"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
            >
              👁️ Shadow
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Moderation Modal -->
    <Modal
      :visible="showModerateModal"
      :title="moderationAction ? `${moderationAction.charAt(0).toUpperCase() + moderationAction.slice(1)} Review` : 'Moderate Review'"
      size="md"
      @update:visible="showModerateModal = $event"
    >
      <div class="space-y-4">
        <div v-if="selectedReview">
          <p class="text-sm text-gray-600 mb-2">
            Review Type: <span class="font-medium">{{ getTypeLabel(selectedReview.type) }}</span>
          </p>
          <p class="text-sm text-gray-600 mb-4">
            Reviewer: <span class="font-medium">{{ selectedReview.data.reviewer_name || selectedReview.data.reviewer?.username || 'N/A' }}</span>
          </p>
        </div>

        <div v-if="moderationAction === 'reject' || moderationAction === 'flag'">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Reason <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="moderationForm.reason"
            rows="3"
            placeholder="Enter reason for rejection or flagging..."
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Moderation Notes (Optional)
          </label>
          <textarea
            v-model="moderationForm.moderation_notes"
            rows="3"
            placeholder="Add internal notes about this moderation decision..."
            class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          ></textarea>
        </div>
      </div>

      <template #footer>
        <button
          @click="showModerateModal = false"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="submitModeration"
          :disabled="saving || (moderationAction === 'reject' || moderationAction === 'flag') && !moderationForm.reason"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Processing...' : 'Confirm' }}
        </button>
      </template>
    </Modal>

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
import adminReviewsAPI from '@/api/admin-reviews'
import Modal from '@/components/common/Modal.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'

const loading = ref(false)
const saving = ref(false)
const reviews = ref([])
const countsByType = ref({ website: 0, writer: 0, order: 0 })
const stats = ref({ pending: 0 })
const message = ref('')
const messageSuccess = ref(false)

const filters = ref({
  type: '',
  status: '',
  search: ''
})

const showModerateModal = ref(false)
const selectedReview = ref(null)
const moderationAction = ref('')
const moderationForm = ref({
  reason: '',
  moderation_notes: ''
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadModerationQueue()
  }, 500)
}

const filteredReviews = computed(() => {
  let filtered = reviews.value

  if (filters.value.status) {
    if (filters.value.status === 'pending') {
      filtered = filtered.filter(r => !r.data.is_approved && !r.data.is_shadowed && !r.data.is_flagged)
    } else if (filters.value.status === 'flagged') {
      filtered = filtered.filter(r => r.data.is_flagged)
    } else if (filters.value.status === 'shadowed') {
      filtered = filtered.filter(r => r.data.is_shadowed)
    }
  }

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(r => {
      const reviewer = (r.data.reviewer_name || r.data.reviewer?.username || '').toLowerCase()
      const comment = (r.data.comment || '').toLowerCase()
      return reviewer.includes(search) || comment.includes(search)
    })
  }

  return filtered
})

const loadModerationQueue = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.type) {
      params.type = filters.value.type
    }
    if (filters.value.status) {
      params.status = filters.value.status
    }

    const res = await adminReviewsAPI.getModerationQueue(params)
    reviews.value = res.data.reviews || []
    countsByType.value = res.data.counts_by_type || { website: 0, writer: 0, order: 0 }
    stats.value = {
      pending: res.data.count || 0
    }
  } catch (error) {
    showMessage('Failed to load moderation queue: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const openModerateModal = (review, action) => {
  selectedReview.value = review
  moderationAction.value = action
  moderationForm.value = {
    reason: review.data.flag_reason || '',
    moderation_notes: review.data.moderation_notes || ''
  }
  showModerateModal.value = true
}

const submitModeration = async () => {
  if (!selectedReview.value) return

  if ((moderationAction.value === 'reject' || moderationAction.value === 'flag') && !moderationForm.value.reason) {
    showMessage('Reason is required for rejection or flagging', false)
    return
  }

  saving.value = true
  try {
    const reviewType = selectedReview.value.type
    const reviewId = selectedReview.value.id

    let result
    if (moderationAction.value === 'approve') {
      result = await adminReviewsAPI.approveReview(reviewType, reviewId, moderationForm.value.moderation_notes)
    } else if (moderationAction.value === 'reject') {
      result = await adminReviewsAPI.rejectReview(reviewType, reviewId, moderationForm.value.reason, moderationForm.value.moderation_notes)
    } else if (moderationAction.value === 'flag') {
      result = await adminReviewsAPI.flagReview(reviewType, reviewId, moderationForm.value.reason, moderationForm.value.moderation_notes)
    } else if (moderationAction.value === 'shadow') {
      result = await adminReviewsAPI.shadowReview(reviewType, reviewId, moderationForm.value.reason || 'Review shadowed by admin', moderationForm.value.moderation_notes)
    }

    showMessage(result?.data?.detail || 'Review moderated successfully', true)
    showModerateModal.value = false
    selectedReview.value = null
    moderationAction.value = ''
    moderationForm.value = { reason: '', moderation_notes: '' }
    await loadModerationQueue()
  } catch (error) {
    showMessage('Failed to moderate review: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const getTypeLabel = (type) => {
  const labels = {
    website: 'Website Review',
    writer: 'Writer Review',
    order: 'Order Review'
  }
  return labels[type] || type
}

const getTypeClass = (type) => {
  const classes = {
    website: 'bg-blue-100 text-blue-800',
    writer: 'bg-green-100 text-green-800',
    order: 'bg-purple-100 text-purple-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(() => {
  loadModerationQueue()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1rem;
}
</style>

