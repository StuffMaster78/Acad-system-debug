<template>
  <div class="space-y-4">
    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="localFilters.status" @change="$emit('load', localFilters)" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="flagged">Flagged</option>
            <option value="shadowed">Shadowed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Rating</label>
          <select v-model="localFilters.rating" @change="$emit('load', localFilters)" class="w-full border rounded px-3 py-2">
            <option value="">All Ratings</option>
            <option value="5">5 Stars</option>
            <option value="4">4 Stars</option>
            <option value="3">3 Stars</option>
            <option value="2">2 Stars</option>
            <option value="1">1 Star</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="localFilters.website" @change="$emit('load', localFilters)" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="localFilters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search reviews..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Reviews Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewer</th>
              <th v-if="reviewType === 'writer' || reviewType === 'order'" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
              <th v-if="reviewType === 'order'" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Comment</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="review in reviews" :key="review.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ review.reviewer_name || review.reviewer?.username || 'N/A' }}
              </td>
              <td v-if="reviewType === 'writer' || reviewType === 'order'" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ review.writer_name || review.writer?.username || 'N/A' }}
              </td>
              <td v-if="reviewType === 'order'" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                #{{ typeof review.order === 'object' ? review.order?.id : review.order || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1">
                  <span v-for="i in 5" :key="i" class="text-lg" :class="i <= review.rating ? 'text-yellow-400' : 'text-gray-300'">★</span>
                  <span class="ml-1 text-sm text-gray-600">({{ review.rating }})</span>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                {{ review.comment || 'No comment' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(review)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ getStatusText(review) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(review.submitted_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="$emit('view', review)" class="text-blue-600 hover:underline mr-2">View</button>
                <button
                  v-if="!review.is_approved"
                  @click="$emit('moderate', review, 'approve', { is_approved: true })"
                  class="text-green-600 hover:underline mr-2"
                >
                  Approve
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!reviews.length" class="text-center py-12 text-gray-500">
          No reviews found.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import apiClient from '@/api/client'

const props = defineProps({
  reviews: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  filters: {
    type: Object,
    default: () => ({})
  },
  reviewType: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['load', 'moderate', 'view'])

const localFilters = ref({ ...props.filters })
const websites = ref([])

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('load', localFilters.value)
  }, 500)
}

const resetFilters = () => {
  localFilters.value = {
    status: '',
    rating: '',
    website: '',
    search: '',
  }
  emit('load', localFilters.value)
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

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

loadWebsites()
</script>

