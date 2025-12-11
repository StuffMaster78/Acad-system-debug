<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Newsletter Analytics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track newsletter performance and engagement metrics</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Newsletters</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || analytics.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Avg Open Rate</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ formatPercent(stats.avg_open_rate) }}%</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Avg Click Rate</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ formatPercent(stats.avg_click_rate) }}%</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Total Recipients</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.total_recipients || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by newsletter title..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <input
          v-model="dateFrom"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadAnalytics"
        />
        <input
          v-model="dateTo"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadAnalytics"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading newsletter analytics...</p>
    </div>

    <!-- Analytics Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Newsletter</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Sent Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Recipients</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Opens</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Open Rate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Clicks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Click Rate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="item in analytics"
              :key="item.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ item.newsletter_title || item.newsletter || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatDate(item.sent_date || item.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ item.recipients_count || item.total_recipients || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ item.opens_count || item.total_opens || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="text-sm font-semibold text-gray-900 dark:text-white mr-2">
                    {{ formatPercent(item.open_rate) }}%
                  </span>
                  <div class="w-16 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div
                      class="h-2 rounded-full bg-green-500"
                      :style="{ width: `${Math.min(item.open_rate || 0, 100)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ item.clicks_count || item.total_clicks || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="text-sm font-semibold text-gray-900 dark:text-white mr-2">
                    {{ formatPercent(item.click_rate) }}%
                  </span>
                  <div class="w-16 bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div
                      class="h-2 rounded-full bg-blue-500"
                      :style="{ width: `${Math.min(item.click_rate || 0, 100)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="viewDetails(item)"
                  class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="analytics.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No newsletter analytics found
      </div>
    </div>

    <!-- View Details Modal -->
    <Modal
      :visible="showDetailsModal"
      @close="closeDetailsModal"
      :title="`Newsletter Analytics - ${selectedAnalytics?.newsletter_title || 'Details'}`"
      size="lg"
    >
      <div v-if="selectedAnalytics" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Newsletter</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedAnalytics.newsletter_title || selectedAnalytics.newsletter }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Sent Date</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatDate(selectedAnalytics.sent_date || selectedAnalytics.created_at) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Recipients</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedAnalytics.recipients_count || selectedAnalytics.total_recipients || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Opens</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedAnalytics.opens_count || selectedAnalytics.total_opens || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Open Rate</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatPercent(selectedAnalytics.open_rate) }}%</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Clicks</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedAnalytics.clicks_count || selectedAnalytics.total_clicks || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Click Rate</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ formatPercent(selectedAnalytics.click_rate) }}%</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Unsubscribes</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedAnalytics.unsubscribes_count || selectedAnalytics.total_unsubscribes || 0 }}</p>
          </div>
        </div>
        <div v-if="selectedAnalytics.notes" class="mt-4">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedAnalytics.notes }}</p>
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
import blogPagesAPI from '@/api/blog-pages'

const { error: showError } = useToast()

const loading = ref(false)
const analytics = ref([])
const stats = ref({})
const searchQuery = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const showDetailsModal = ref(false)
const selectedAnalytics = ref(null)

const debouncedSearch = debounce(() => {
  loadAnalytics()
}, 300)

const formatPercent = (value) => {
  if (!value && value !== 0) return '0.00'
  return Number(value).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    const params = {}
    if (dateFrom.value) params.sent_date__gte = dateFrom.value
    if (dateTo.value) params.sent_date__lte = dateTo.value
    
    const response = await blogPagesAPI.listNewsletterAnalytics(params)
    let allAnalytics = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allAnalytics = allAnalytics.filter(a => 
        (a.newsletter_title && a.newsletter_title.toLowerCase().includes(query)) ||
        (a.newsletter && String(a.newsletter).toLowerCase().includes(query))
      )
    }
    
    analytics.value = allAnalytics
    
    // Calculate stats
    const total = allAnalytics.length
    const totalRecipients = allAnalytics.reduce((sum, a) => sum + (a.recipients_count || a.total_recipients || 0), 0)
    const totalOpens = allAnalytics.reduce((sum, a) => sum + (a.opens_count || a.total_opens || 0), 0)
    const totalClicks = allAnalytics.reduce((sum, a) => sum + (a.clicks_count || a.total_clicks || 0), 0)
    
    stats.value = {
      total,
      total_recipients: totalRecipients,
      avg_open_rate: total > 0 && totalRecipients > 0 ? (totalOpens / totalRecipients) * 100 : 0,
      avg_click_rate: total > 0 && totalRecipients > 0 ? (totalClicks / totalRecipients) * 100 : 0,
    }
  } catch (error) {
    showError('Failed to load newsletter analytics')
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const viewDetails = (item) => {
  selectedAnalytics.value = item
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedAnalytics.value = null
}

onMounted(() => {
  loadAnalytics()
})
</script>

