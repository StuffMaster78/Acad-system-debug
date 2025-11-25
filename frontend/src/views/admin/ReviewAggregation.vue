<template>
  <!-- Loading State -->
  <div v-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="window.location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Main Content -->
  <div v-else class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Review Aggregation & Display</h1>
        <p class="mt-2 text-gray-600">Manage review display rules, moderation queue, and aggregation</p>
      </div>
      <button @click="refreshData" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Aggregated Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-for="(stats, type) in aggregatedStats" :key="type" class="bg-white rounded-lg shadow p-6 border">
              <h3 class="text-lg font-semibold mb-4 capitalize">{{ type }} Reviews</h3>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-gray-600">Total:</span>
                  <span class="font-bold">{{ stats.total || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Approved:</span>
                  <span class="font-bold text-green-600">{{ stats.approved || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Pending:</span>
                  <span class="font-bold text-yellow-600">{{ stats.pending || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Flagged:</span>
                  <span class="font-bold text-red-600">{{ stats.flagged || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Shadowed:</span>
                  <span class="font-bold text-gray-600">{{ stats.shadowed || 0 }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Avg Rating:</span>
                  <span class="font-bold">{{ stats.avg_rating ? stats.avg_rating.toFixed(1) : 'N/A' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Moderation Queue Tab -->
        <div v-if="activeTab === 'queue'" class="space-y-6">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Review Moderation Queue</h2>
            <div class="flex gap-4">
              <select v-model="queueFilters.status" @change="loadQueue" class="border rounded px-3 py-2">
                <option value="pending">Pending</option>
                <option value="flagged">Flagged</option>
                <option value="shadowed">Shadowed</option>
                <option value="approved">Approved</option>
              </select>
              <select v-model="queueFilters.type" @change="loadQueue" class="border rounded px-3 py-2">
                <option value="all">All Types</option>
                <option value="website">Website</option>
                <option value="writer">Writer</option>
                <option value="order">Order</option>
              </select>
            </div>
          </div>

          <div v-if="queueLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
          <div v-else-if="reviewQueue.length === 0" class="text-center py-8 text-gray-500">
            No reviews in queue
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewer</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Comment</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="review in reviewQueue" :key="`${review.type}-${review.id}`">
                  <td class="px-4 py-3 text-sm capitalize">{{ review.type }}</td>
                  <td class="px-4 py-3 text-sm">{{ review.reviewer }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex items-center">
                      <span class="font-bold">{{ review.rating }}</span>
                      <span class="text-yellow-500 ml-1">★</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ review.comment || '-' }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span
                      class="px-2 py-1 text-xs rounded"
                      :class="{
                        'bg-green-100 text-green-800': review.status === 'approved',
                        'bg-yellow-100 text-yellow-800': review.status === 'pending',
                        'bg-red-100 text-red-800': review.status === 'flagged',
                        'bg-gray-100 text-gray-800': review.status === 'shadowed',
                      }"
                    >
                      {{ review.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(review.submitted_at) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <button
                      @click="viewReview(review)"
                      class="text-blue-600 hover:text-blue-800 text-xs mr-2"
                    >
                      View
                    </button>
                    <button
                      v-if="review.status === 'pending'"
                      @click="moderateReview(review, 'approve')"
                      class="text-green-600 hover:text-green-800 text-xs mr-2"
                    >
                      Approve
                    </button>
                    <button
                      v-if="review.status !== 'shadowed'"
                      @click="moderateReview(review, 'shadow')"
                      class="text-gray-600 hover:text-gray-800 text-xs mr-2"
                    >
                      Shadow
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Display Rules Tab -->
        <div v-if="activeTab === 'rules'" class="space-y-6">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Review Display Rules</h2>
            <button
              @click="showRuleModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Add Rule
            </button>
          </div>

          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p class="text-sm text-yellow-800">
              <strong>Note:</strong> Display rules configuration will be implemented in a future update.
              This will allow you to configure how reviews are displayed on the frontend, including
              sorting, filtering, and visibility rules.
            </p>
          </div>
        </div>
      </div>
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
              <span class="text-sm font-medium text-gray-600">Type:</span>
              <p class="text-gray-900 font-medium capitalize">{{ viewingReview.type }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Reviewer:</span>
              <p class="text-gray-900 font-medium">{{ viewingReview.reviewer }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Rating:</span>
              <p class="text-gray-900 font-medium">{{ viewingReview.rating }} / 5</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <p class="text-gray-900 font-medium capitalize">{{ viewingReview.status }}</p>
            </div>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Comment:</span>
            <p class="text-gray-900 mt-1">{{ viewingReview.comment || 'No comment' }}</p>
          </div>
          <div>
            <span class="text-sm font-medium text-gray-600">Submitted:</span>
            <p class="text-gray-900">{{ formatDate(viewingReview.submitted_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { reviewAggregationAPI, reviewsAPI } from '@/api'

const componentError = ref(null)
const initialLoading = ref(true)
const activeTab = ref('overview')
const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'queue', label: 'Moderation Queue' },
  { id: 'rules', label: 'Display Rules' },
]

const loading = ref(false)
const queueLoading = ref(false)
const aggregatedStats = ref({})
const reviewQueue = ref([])
const viewingReview = ref(null)
const showRuleModal = ref(false)

const queueFilters = ref({
  status: 'pending',
  type: 'all',
})

const loadStats = async () => {
  loading.value = true
  try {
    const response = await reviewAggregationAPI.getAggregatedStats('all')
    aggregatedStats.value = response.data || {}
  } catch (error) {
    console.error('Error loading stats:', error)
    aggregatedStats.value = {}
  } finally {
    loading.value = false
  }
}

const loadQueue = async () => {
  queueLoading.value = true
  try {
    const response = await reviewAggregationAPI.getReviewQueue(
      queueFilters.value.status,
      queueFilters.value.type
    )
    reviewQueue.value = response.data || []
  } catch (error) {
    console.error('Error loading queue:', error)
    reviewQueue.value = []
  } finally {
    queueLoading.value = false
  }
}

const viewReview = async (review) => {
  try {
    let response
    if (review.type === 'website') {
      response = await reviewAggregationAPI.getWebsiteReview(review.id)
    } else if (review.type === 'writer') {
      response = await reviewAggregationAPI.getWriterReview(review.id)
    } else if (review.type === 'order') {
      response = await reviewAggregationAPI.getOrderReview(review.id)
    }
    
    if (response) {
      viewingReview.value = {
        ...review,
        ...response.data,
      }
    } else {
      viewingReview.value = review
    }
  } catch (error) {
    console.error('Error loading review:', error)
    viewingReview.value = review
  }
}

const moderateReview = async (review, action) => {
  if (!confirm(`Are you sure you want to ${action} this review?`)) return
  
  try {
    const data = {}
    if (action === 'approve') {
      data.is_approved = true
      data.is_shadowed = false
    } else if (action === 'shadow') {
      data.is_shadowed = true
      data.is_approved = false
    }
    
    let response
    if (review.type === 'website') {
      response = await reviewAggregationAPI.moderateWebsiteReview(review.id, data)
    } else if (review.type === 'writer') {
      response = await reviewAggregationAPI.moderateWriterReview(review.id, data)
    } else if (review.type === 'order') {
      response = await reviewAggregationAPI.moderateOrderReview(review.id, data)
    }
    
    if (response) {
      alert('Review moderated successfully!')
      loadQueue()
      loadStats()
    }
  } catch (error) {
    console.error('Error moderating review:', error)
    alert('Error moderating review: ' + (error.response?.data?.detail || error.message))
  }
}

const refreshData = () => {
  loadStats()
  if (activeTab.value === 'queue') {
    loadQueue()
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

watch(activeTab, (newTab) => {
  if (newTab === 'queue') {
    loadQueue()
  }
})

onMounted(async () => {
  try {
    await loadStats()
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ReviewAggregation:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

<style scoped>
/* Add any custom styles here */
</style>

