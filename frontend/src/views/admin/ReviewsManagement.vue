<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reviews Management</h1>
        <p class="mt-2 text-gray-600">Moderate and manage website, writer, and order reviews</p>
      </div>
      <router-link
        to="/admin/reviews/moderation"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        📋 Moderation Queue
      </router-link>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Pending Approval</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.pending_approval || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Flagged Reviews</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.flagged || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.approved || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Shadowed</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.shadowed || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Reviews Tab Content -->
    <div v-if="activeTab === 'website'" class="space-y-4">
      <ReviewsList
        :reviews="websiteReviews"
        :loading="loading"
        :filters="filters"
        @load="loadWebsiteReviews"
        @moderate="moderateReview"
        @view="viewReview"
        review-type="website"
      />
    </div>

    <div v-if="activeTab === 'writer'" class="space-y-4">
      <ReviewsList
        :reviews="writerReviews"
        :loading="loading"
        :filters="filters"
        @load="loadWriterReviews"
        @moderate="moderateReview"
        @view="viewReview"
        review-type="writer"
      />
    </div>

    <div v-if="activeTab === 'order'" class="space-y-4">
      <ReviewsList
        :reviews="orderReviews"
        :loading="loading"
        :filters="filters"
        @load="loadOrderReviews"
        @moderate="moderateReview"
        @view="viewReview"
        review-type="order"
      />
    </div>

    <!-- Review Detail Modal -->
    <div v-if="viewingReview" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Review Details</h3>
          <button @click="viewingReview = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Reviewer:</span>
              <p class="text-gray-900 font-medium">{{ viewingReview.reviewer_name || viewingReview.reviewer?.username || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Rating:</span>
              <div class="flex items-center gap-1 mt-1">
                <span v-for="i in 5" :key="i" class="text-2xl" :class="i <= viewingReview.rating ? 'text-yellow-400' : 'text-gray-300'">★</span>
                <span class="ml-2 text-gray-700">({{ viewingReview.rating }}/5)</span>
              </div>
            </div>
            <div v-if="viewingReview.writer_name || viewingReview.writer">
              <span class="text-sm font-medium text-gray-600">Writer:</span>
              <p class="text-gray-900">{{ viewingReview.writer_name || viewingReview.writer?.username || 'N/A' }}</p>
            </div>
            <div v-if="viewingReview.order">
              <span class="text-sm font-medium text-gray-600">Order:</span>
              <p class="text-gray-900">#{{ typeof viewingReview.order === 'object' ? viewingReview.order?.id : viewingReview.order }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Website:</span>
              <p class="text-gray-900">{{ typeof viewingReview.website === 'object' ? viewingReview.website?.name : 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Submitted:</span>
              <p class="text-gray-900">{{ formatDateTime(viewingReview.submitted_at) }}</p>
            </div>
          </div>

          <div v-if="viewingReview.comment" class="border-t pt-4">
            <span class="text-sm font-medium text-gray-600">Comment:</span>
            <SafeHtml 
              :content="viewingReview.comment"
              container-class="text-gray-700 mt-2"
            />
          </div>

          <div class="border-t pt-4">
            <div class="flex items-center gap-4 mb-4">
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="getStatusClass(viewingReview)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ getStatusText(viewingReview) }}
              </span>
            </div>
            <div v-if="viewingReview.flag_reason" class="mt-2 p-3 bg-red-50 border border-red-200 rounded">
              <span class="text-sm font-medium text-red-800">Flag Reason:</span>
              <p class="text-red-700 mt-1">{{ viewingReview.flag_reason }}</p>
            </div>
          </div>

          <!-- Moderation Actions -->
          <div class="border-t pt-4 space-y-3">
            <h4 class="font-semibold mb-2">Moderation Actions</h4>
            <div class="flex flex-wrap gap-2">
              <button
                v-if="!viewingReview.is_approved"
                @click="approveReview(viewingReview)"
                class="btn btn-primary bg-green-600 hover:bg-green-700"
              >
                Approve
              </button>
              <button
                v-if="!viewingReview.is_shadowed"
                @click="showShadowModal = true"
                class="btn btn-primary bg-yellow-600 hover:bg-yellow-700"
              >
                Shadow
              </button>
              <button
                v-if="viewingReview.is_shadowed"
                @click="unshadowReview(viewingReview)"
                class="btn btn-primary bg-blue-600 hover:bg-blue-700"
              >
                Unshadow
              </button>
              <button
                v-if="!viewingReview.is_flagged"
                @click="showFlagModal = true"
                class="btn btn-primary bg-red-600 hover:bg-red-700"
              >
                Flag
              </button>
              <button
                @click="deleteReview(viewingReview)"
                class="btn btn-secondary bg-red-500 hover:bg-red-600 text-white"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Shadow Modal -->
    <div v-if="showShadowModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">Shadow Review</h3>
        <form @submit.prevent="shadowReview(viewingReview)">
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Reason (optional)</label>
            <textarea v-model="moderationReason" rows="3" class="w-full border rounded px-3 py-2" placeholder="Reason for shadowing this review"></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button type="button" @click="showShadowModal = false; moderationReason = ''" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary bg-yellow-600 hover:bg-yellow-700">Shadow Review</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Flag Modal -->
    <div v-if="showFlagModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">Flag Review</h3>
        <form @submit.prevent="flagReview(viewingReview)">
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Flag Reason *</label>
            <textarea v-model="moderationReason" rows="3" required class="w-full border rounded px-3 py-2" placeholder="Reason for flagging this review"></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button type="button" @click="showFlagModal = false; moderationReason = ''" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary bg-red-600 hover:bg-red-700">Flag Review</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { reviewsAPI } from '@/api'
import apiClient from '@/api/client'
import ReviewsList from './components/ReviewsList.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'

const activeTab = ref('website')
const tabs = [
  { id: 'website', label: 'Website Reviews' },
  { id: 'writer', label: 'Writer Reviews' },
  { id: 'order', label: 'Order Reviews' },
]

const componentError = ref(null)
const initialLoading = ref(true)
const websiteReviews = ref([])
const writerReviews = ref([])
const orderReviews = ref([])
const websites = ref([])
const loading = ref(false)
const viewingReview = ref(null)
const showShadowModal = ref(false)
const showFlagModal = ref(false)
const moderationReason = ref('')

const stats = ref({
  pending_approval: 0,
  flagged: 0,
  approved: 0,
  shadowed: 0,
})

const filters = ref({
  status: '',
  rating: '',
  website: '',
  search: '',
})

const loadWebsiteReviews = async (params = {}) => {
  loading.value = true
  try {
    const queryParams = { ...filters.value, ...params }
    const res = await reviewsAPI.listWebsiteReviews(queryParams)
    websiteReviews.value = res.data.results || res.data || []
    calculateStats()
  } catch (error) {
    showMessage('Failed to load website reviews: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadWriterReviews = async (params = {}) => {
  loading.value = true
  try {
    const queryParams = { ...filters.value, ...params }
    const res = await reviewsAPI.listWriterReviews(queryParams)
    writerReviews.value = res.data.results || res.data || []
    calculateStats()
  } catch (error) {
    showMessage('Failed to load writer reviews: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const loadOrderReviews = async (params = {}) => {
  loading.value = true
  try {
    const queryParams = { ...filters.value, ...params }
    const res = await reviewsAPI.listOrderReviews(queryParams)
    orderReviews.value = res.data.results || res.data || []
    calculateStats()
  } catch (error) {
    showMessage('Failed to load order reviews: ' + (error.response?.data?.detail || error.message), false)
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
  const allReviews = [...websiteReviews.value, ...writerReviews.value, ...orderReviews.value]
  stats.value = {
    pending_approval: allReviews.filter(r => !r.is_approved && !r.is_flagged).length,
    flagged: allReviews.filter(r => r.is_flagged).length,
    approved: allReviews.filter(r => r.is_approved).length,
    shadowed: allReviews.filter(r => r.is_shadowed).length,
  }
}

const viewReview = (review) => {
  viewingReview.value = review
}

const moderateReview = async (review, action, data) => {
  try {
    let apiCall
    if (activeTab.value === 'website') {
      apiCall = reviewsAPI.moderateWebsiteReview(review.id, data)
    } else if (activeTab.value === 'writer') {
      apiCall = reviewsAPI.moderateWriterReview(review.id, data)
    } else {
      apiCall = reviewsAPI.moderateOrderReview(review.id, data)
    }
    
    await apiCall
    showMessage('Review moderated successfully', true)
    await reloadCurrentTab()
    if (viewingReview.value?.id === review.id) {
      viewingReview.value = null
    }
  } catch (error) {
    showMessage('Failed to moderate review: ' + (error.response?.data?.detail || error.message), false)
  }
}

const approveReview = async (review) => {
  await moderateReview(review, 'approve', { is_approved: true })
}

const shadowReview = async (review) => {
  await moderateReview(review, 'shadow', { is_shadowed: true, flag_reason: moderationReason.value })
  showShadowModal.value = false
  moderationReason.value = ''
}

const unshadowReview = async (review) => {
  await moderateReview(review, 'unshadow', { is_shadowed: false, flag_reason: '' })
}

const flagReview = async (review) => {
  await moderateReview(review, 'flag', { is_flagged: true, flag_reason: moderationReason.value })
  showFlagModal.value = false
  moderationReason.value = ''
}

const deleteReview = async (review) => {
  if (!confirm('Are you sure you want to delete this review? This action cannot be undone.')) return
  
  try {
    let apiCall
    if (activeTab.value === 'website') {
      apiCall = reviewsAPI.deleteWebsiteReview(review.id)
    } else if (activeTab.value === 'writer') {
      apiCall = reviewsAPI.deleteWriterReview(review.id)
    } else {
      apiCall = reviewsAPI.deleteOrderReview(review.id)
    }
    
    await apiCall
    showMessage('Review deleted successfully', true)
    await reloadCurrentTab()
    if (viewingReview.value?.id === review.id) {
      viewingReview.value = null
    }
  } catch (error) {
    showMessage('Failed to delete review: ' + (error.response?.data?.detail || error.message), false)
  }
}

const reloadCurrentTab = async () => {
  if (activeTab.value === 'website') {
    await loadWebsiteReviews()
  } else if (activeTab.value === 'writer') {
    await loadWriterReviews()
  } else {
    await loadOrderReviews()
  }
}

const getStatusClass = (review) => {
  if (review.is_flagged) return 'bg-red-100 text-red-800'
  if (review.is_shadowed) return 'bg-gray-100 text-gray-800'
  if (review.is_approved) return 'bg-green-100 text-green-800'
  return 'bg-yellow-100 text-yellow-800'
}

const getStatusText = (review) => {
  if (review.is_flagged) return 'Flagged'
  if (review.is_shadowed) return 'Shadowed'
  if (review.is_approved) return 'Approved'
  return 'Pending'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
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

watch(activeTab, (newTab) => {
  if (newTab === 'website') {
    loadWebsiteReviews()
  } else if (newTab === 'writer') {
    loadWriterReviews()
  } else if (newTab === 'order') {
    loadOrderReviews()
  }
})

onMounted(async () => {
  try {
    await Promise.all([
      loadWebsites(),
      loadWebsiteReviews()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ReviewsManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

