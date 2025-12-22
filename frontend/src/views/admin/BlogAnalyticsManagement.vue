<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Blog Analytics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track clicks, conversions, and shares for blog posts</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="activeTab = 'clicks'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'clicks' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Clicks
        </button>
        <button
          @click="activeTab = 'conversions'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'conversions' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Conversions
        </button>
        <button
          @click="activeTab = 'shares'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'shares' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Shares
        </button>
      </div>
    </div>

    <!-- Clicks Tab -->
    <div v-if="activeTab === 'clicks'">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Clicks</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ clicks.length }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Unique IPs</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ uniqueIPs }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Today</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ todayClicks }}</p>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">IP Address</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="click in clicks"
                :key="click.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  Blog #{{ click.blog || click.blog_id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ click.ip_address || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ click.user || click.user_id || 'Anonymous' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatDate(click.timestamp || click.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="clicks.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          No clicks found
        </div>
      </div>
    </div>

    <!-- Conversions Tab -->
    <div v-if="activeTab === 'conversions'">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Conversions</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ conversions.length }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Order Page Clicks</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ orderPageClicks }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Orders Placed</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ ordersPlaced }}</p>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Order Page Clicked</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Order Placed</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="conversion in conversions"
                :key="conversion.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  Blog #{{ conversion.blog || conversion.blog_id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ conversion.user || conversion.user_id || 'Anonymous' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      conversion.clicked_order_page ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ conversion.clicked_order_page ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      conversion.order_placed ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ conversion.order_placed ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatDate(conversion.timestamp || conversion.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="conversions.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          No conversions found
        </div>
      </div>
    </div>

    <!-- Shares Tab -->
    <div v-if="activeTab === 'shares'">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Shares</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ shares.length }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Unique Platforms</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ uniquePlatforms }}</p>
        </div>
        <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">This Week</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ thisWeekShares }}</p>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Platform</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Timestamp</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="share in shares"
                :key="share.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  Blog #{{ share.blog || share.blog_id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ share.platform || share.social_platform || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ share.user || share.user_id || 'Anonymous' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatDate(share.timestamp || share.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="shares.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          No shares found
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import blogPagesAPI from '@/api/blog-pages'

const { error: showError } = useToast()

const activeTab = ref('clicks')
const loading = ref(false)
const clicks = ref([])
const conversions = ref([])
const shares = ref([])

const uniqueIPs = computed(() => {
  return new Set(clicks.value.map(c => c.ip_address).filter(Boolean)).size
})

const todayClicks = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return clicks.value.filter(c => {
    const date = c.timestamp || c.created_at
    return date && date.startsWith(today)
  }).length
})

const orderPageClicks = computed(() => {
  return conversions.value.filter(c => c.clicked_order_page).length
})

const ordersPlaced = computed(() => {
  return conversions.value.filter(c => c.order_placed).length
})

const uniquePlatforms = computed(() => {
  return new Set(shares.value.map(s => s.platform || s.social_platform).filter(Boolean)).size
})

const thisWeekShares = computed(() => {
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  return shares.value.filter(s => {
    const date = s.timestamp || s.created_at
    return date && date >= weekAgo
  }).length
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadClicks = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listBlogClicks()
    clicks.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load blog clicks')
    console.error('Error loading clicks:', error)
  } finally {
    loading.value = false
  }
}

const loadConversions = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listBlogConversions()
    conversions.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load blog conversions')
    console.error('Error loading conversions:', error)
  } finally {
    loading.value = false
  }
}

const loadShares = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listBlogShares()
    shares.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load blog shares')
    console.error('Error loading shares:', error)
  } finally {
    loading.value = false
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'clicks' && clicks.value.length === 0) {
    loadClicks()
  } else if (newTab === 'conversions' && conversions.value.length === 0) {
    loadConversions()
  } else if (newTab === 'shares' && shares.value.length === 0) {
    loadShares()
  }
})

onMounted(() => {
  loadClicks()
})
</script>

