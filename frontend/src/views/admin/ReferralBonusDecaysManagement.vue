<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Referral Bonus Decays</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage referral bonus decay rules and configurations</p>
      </div>
    </div>

    <!-- Info Card -->
    <div class="card p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700">
      <h3 class="font-semibold text-blue-900 dark:text-blue-200 mb-2">ℹ️ About Referral Bonus Decays</h3>
      <p class="text-sm text-blue-800 dark:text-blue-300">
        Referral bonus decays allow you to automatically reduce referral bonuses over time. This helps manage long-term referral program costs
        while still rewarding referrers. Decay rules can be configured per website and applied monthly.
      </p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Decay Rules</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ decays.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active Rules</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ decays.filter(d => d.is_active).length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique Websites</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueWebsites.length }}</p>
      </div>
    </div>

    <!-- Decays Table -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Decay Rate</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Frequency</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Last Applied</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="decay in decays"
              :key="decay.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ decay.website_name || decay.website || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ decay.decay_rate || decay.rate || 'N/A' }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ decay.frequency || 'Monthly' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    decay.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                  ]"
                >
                  {{ decay.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatDate(decay.last_applied || decay.updated_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="decays.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="mb-2">No referral bonus decay rules found.</p>
        <p class="text-sm">Decay rules are managed through the backend API. Contact your administrator to configure decay rules.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import referralsAPI from '@/api/referrals'

const { error: showError } = useToast()

const loading = ref(false)
const decays = ref([])

const uniqueWebsites = computed(() => {
  return [...new Set(decays.value.map(d => d.website || d.website_id).filter(Boolean))]
})

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadDecays = async () => {
  loading.value = true
  try {
    const response = await referralsAPI.listBonusDecays()
    // Handle placeholder response
    if (response.data && response.data.status) {
      decays.value = []
    } else {
      decays.value = response.data.results || response.data || []
    }
  } catch (error) {
    // If endpoint returns placeholder, show empty state
    decays.value = []
    console.log('Referral bonus decays endpoint may not be fully implemented yet')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDecays()
})
</script>

