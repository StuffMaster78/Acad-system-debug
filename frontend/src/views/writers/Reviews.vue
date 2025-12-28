<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Reviews</h1>
        <p class="mt-2 text-gray-600">View and manage reviews you've received from clients</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Reviews</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_reviews || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Average Rating</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.average_rating ? stats.average_rating.toFixed(1) : 'N/A' }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">5 Star</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.five_star || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Flagged</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.flagged || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">This Month</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.this_month || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Rating</label>
          <select v-model="filters.rating" @change="loadReviews" class="w-full border rounded px-3 py-2">
            <option value="">All Ratings</option>
            <option value="5">5 Stars</option>
            <option value="4">4 Stars</option>
            <option value="3">3 Stars</option>
            <option value="2">2 Stars</option>
            <option value="1">1 Star</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadReviews" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="approved">Approved</option>
            <option value="flagged">Flagged</option>
            <option value="shadowed">Shadowed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Date From</label>
          <input v-model="filters.date_from" type="date" class="w-full border rounded px-3 py-2" @change="loadReviews" />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Reviews Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="reviewsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="reviews.length === 0" class="text-center py-12">
        <div class="text-4xl mb-4">⭐</div>
        <p class="text-gray-600 text-lg">No reviews found</p>
        <p class="text-sm text-gray-400 mt-2">Reviews from clients will appear here</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gradient-to-r from-gray-50 via-gray-50 to-gray-100">
          <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Date
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Client
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Rating
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Comment
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Status
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Actions
              </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(review, index) in reviews"
              :key="review.id"
              :class="[
                'transition-all duration-150 hover:bg-blue-50/50 cursor-pointer',
                index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'
              ]"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ formatDate(review.submitted_at) }}</div>
                <div class="text-xs text-gray-500 mt-0.5">{{ formatTime(review.submitted_at) }}</div>
              </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                  <div class="shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span class="text-primary-600 text-xs font-semibold">
                      {{ (review.reviewer_name || 'A')[0].toUpperCase() }}
                    </span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ review.reviewer_name || 'Anonymous' }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1">
                  <div class="flex">
                    <span
                      v-for="i in 5"
                      :key="i"
                      :class="i <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                      class="text-lg"
                    >
                      ★
                    </span>
                  </div>
                  <span class="ml-2 text-sm font-bold text-gray-900">{{ review.rating }}/5</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-700 max-w-md">
                  <p class="line-clamp-2">{{ review.comment || 'No comment provided' }}</p>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="review.is_approved"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 border border-green-200"
                >
                  <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
                  Approved
                </span>
                <span
                  v-else-if="review.is_flagged"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-200"
                >
                  <span class="w-1.5 h-1.5 bg-orange-500 rounded-full mr-1.5"></span>
                  Flagged
                </span>
                <span
                  v-else-if="review.is_shadowed"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-200"
                >
                  <span class="w-1.5 h-1.5 bg-gray-500 rounded-full mr-1.5"></span>
                  Shadowed
                </span>
                <span
                  v-else
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800 border border-yellow-200"
                >
                  <span class="w-1.5 h-1.5 bg-yellow-500 rounded-full mr-1.5"></span>
                  Pending
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-3">
                  <button
                    @click.stop="viewReview(review)"
                    class="text-primary-600 hover:text-primary-800 font-medium transition-colors"
                  >
                    View
                  </button>
                  <button
                    v-if="!review.is_flagged"
                    @click.stop="openDisputeModal(review)"
                    class="text-orange-600 hover:text-orange-800 font-medium transition-colors"
                  >
                    Dispute
                  </button>
                </div>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Review Detail Modal -->
    <div v-if="selectedReview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Review Details</h2>
            <button @click="selectedReview = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rating</label>
              <div class="flex items-center">
                <span class="text-yellow-400 text-2xl">★</span>
                <span class="ml-2 text-lg font-semibold text-gray-900">{{ selectedReview.rating }}/5</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <span v-if="selectedReview.is_approved" class="px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800">Approved</span>
              <span v-else-if="selectedReview.is_flagged" class="px-3 py-1 text-sm font-semibold rounded-full bg-orange-100 text-orange-800">Flagged</span>
              <span v-else-if="selectedReview.is_shadowed" class="px-3 py-1 text-sm font-semibold rounded-full bg-gray-100 text-gray-800">Shadowed</span>
              <span v-else class="px-3 py-1 text-sm font-semibold rounded-full bg-yellow-100 text-yellow-800">Pending</span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client</label>
              <p class="text-sm text-gray-900">{{ selectedReview.reviewer_name || 'Anonymous' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedReview.submitted_at) }}</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Comment</label>
            <SafeHtml 
              :content="selectedReview.comment || 'No comment provided'"
              container-class="text-sm text-gray-900"
            />
          </div>
          <div v-if="selectedReview.flag_reason">
            <label class="block text-sm font-medium text-gray-700 mb-1">Flag Reason</label>
            <p class="text-sm text-gray-900">{{ selectedReview.flag_reason }}</p>
          </div>
          <div v-if="selectedReview.dispute_reason">
            <label class="block text-sm font-medium text-gray-700 mb-1">Your Dispute Reason</label>
            <p class="text-sm text-gray-900">{{ selectedReview.dispute_reason }}</p>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button v-if="!selectedReview.is_flagged" @click="openDisputeModal(selectedReview)" class="btn btn-warning">Dispute Review</button>
          <button @click="selectedReview = null" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Dispute Modal -->
    <div v-if="showDisputeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
        <div class="p-6 border-b">
          <h2 class="text-2xl font-bold text-gray-900">Dispute Review</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Review</label>
            <div class="p-3 bg-gray-50 rounded">
              <p class="text-sm text-gray-700">{{ disputingReview?.comment || 'No comment' }}</p>
              <p class="text-xs text-gray-500 mt-1">Rating: {{ disputingReview?.rating }}/5</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Dispute Reason *</label>
            <textarea v-model="disputeForm.reason" rows="6" class="w-full border rounded px-3 py-2" placeholder="Explain why you are disputing this review..."></textarea>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="closeDisputeModal" class="btn btn-secondary">Cancel</button>
          <button @click="submitDispute" :disabled="submittingDispute" class="btn btn-warning">
            {{ submittingDispute ? 'Submitting...' : 'Submit Dispute' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import reviewsAPI from '@/api/reviews'
import { useAuthStore } from '@/stores/auth'
import SafeHtml from '@/components/common/SafeHtml.vue'

const authStore = useAuthStore()
const reviews = ref([])
const reviewsLoading = ref(false)
const stats = ref({})
const filters = ref({
  rating: '',
  status: '',
  date_from: '',
})
const selectedReview = ref(null)
const showDisputeModal = ref(false)
const disputingReview = ref(null)
const disputeForm = ref({
  reason: '',
})
const submittingDispute = ref(false)

const loadReviews = async () => {
  reviewsLoading.value = true
  try {
    const params = {}
    if (filters.value.rating) params.rating = filters.value.rating
    if (filters.value.status) {
      if (filters.value.status === 'approved') params.is_approved = true
      if (filters.value.status === 'flagged') params.is_flagged = true
      if (filters.value.status === 'shadowed') params.is_shadowed = true
    }
    if (filters.value.date_from) params.submitted_at__gte = filters.value.date_from
    
    const response = await reviewsAPI.listWriterReviews(params)
    reviews.value = response.data.results || response.data || []
    
    // Calculate stats
    const totalReviews = reviews.value.length
    const ratings = reviews.value.map(r => r.rating).filter(r => r)
    const averageRating = ratings.length > 0 ? ratings.reduce((a, b) => a + b, 0) / ratings.length : 0
    const fiveStar = reviews.value.filter(r => r.rating === 5).length
    const flagged = reviews.value.filter(r => r.is_flagged).length
    const now = new Date()
    const thisMonth = reviews.value.filter(r => {
      const reviewDate = new Date(r.submitted_at)
      return reviewDate.getMonth() === now.getMonth() && reviewDate.getFullYear() === now.getFullYear()
    }).length
    
    stats.value = {
      total_reviews: totalReviews,
      average_rating: averageRating,
      five_star: fiveStar,
      flagged: flagged,
      this_month: thisMonth,
    }
  } catch (error) {
    console.error('Failed to load reviews:', error)
  } finally {
    reviewsLoading.value = false
  }
}

const viewReview = (review) => {
  selectedReview.value = review
}

const openDisputeModal = (review) => {
  disputingReview.value = review
  disputeForm.value.reason = review.dispute_reason || ''
  showDisputeModal.value = true
}

const closeDisputeModal = () => {
  showDisputeModal.value = false
  disputingReview.value = null
  disputeForm.value.reason = ''
}

const submitDispute = async () => {
  if (!disputeForm.value.reason.trim()) {
    alert('Please provide a reason for disputing this review')
    return
  }
  
  submittingDispute.value = true
  try {
    await reviewsAPI.disputeWriterReview(disputingReview.value.id, {
      reason: disputeForm.value.reason,
    })
    await loadReviews()
    closeDisputeModal()
    if (selectedReview.value && selectedReview.value.id === disputingReview.value.id) {
      selectedReview.value = null
      viewReview(disputingReview.value)
    }
    alert('Dispute submitted successfully')
  } catch (error) {
    console.error('Failed to submit dispute:', error)
    alert('Failed to submit dispute. Please try again.')
  } finally {
    submittingDispute.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    rating: '',
    status: '',
    date_from: '',
  }
  loadReviews()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadReviews()
})
</script>

