<template>
  <div class="privacy-settings">
    <div class="max-w-4xl mx-auto p-6">
      <h1 class="text-3xl font-bold mb-6">Privacy & Security Settings</h1>

      <!-- Privacy Score -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-blue-900">Your Privacy Score</h2>
            <p class="text-blue-700 mt-1">Higher score = More privacy</p>
          </div>
          <div class="text-4xl font-bold text-blue-600">{{ privacyScore }}/100</div>
        </div>
        <div class="mt-4">
          <div class="w-full bg-blue-200 rounded-full h-3">
            <div
              class="bg-blue-600 h-3 rounded-full transition-all duration-300"
              :style="{ width: `${privacyScore}%` }"
            ></div>
          </div>
        </div>
      </div>

      <!-- Profile Visibility -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Who Can See Your Profile</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Writers
            </label>
            <p class="text-sm text-gray-500 mb-2">
              Writers assigned to your orders can see your basic profile
            </p>
            <select
              v-model="settings.profile_visibility.to_writers"
              @change="updateVisibility"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="hidden">Hidden</option>
              <option value="private">Private</option>
              <option value="limited">Limited</option>
              <option value="public">Public</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Administrators
            </label>
            <p class="text-sm text-gray-500 mb-2">
              Administrators can see your full profile for support purposes
            </p>
            <select
              v-model="settings.profile_visibility.to_admins"
              @change="updateVisibility"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="hidden">Hidden</option>
              <option value="private">Private</option>
              <option value="limited">Limited</option>
              <option value="public">Public</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Support Staff
            </label>
            <p class="text-sm text-gray-500 mb-2">
              Support staff can see your profile to assist with issues
            </p>
            <select
              v-model="settings.profile_visibility.to_support"
              @change="updateVisibility"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="hidden">Hidden</option>
              <option value="private">Private</option>
              <option value="limited">Limited</option>
              <option value="public">Public</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Data Sharing -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Data Sharing Preferences</h2>
        
        <div class="space-y-4">
          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="settings.data_sharing.analytics"
              @change="updateDataSharing"
              class="mr-3 w-4 h-4 text-blue-600"
            />
            <div>
              <span class="font-medium">Allow Usage Analytics</span>
              <p class="text-sm text-gray-500">Help us improve by sharing anonymous usage data</p>
            </div>
          </label>

          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="settings.data_sharing.marketing"
              @change="updateDataSharing"
              class="mr-3 w-4 h-4 text-blue-600"
            />
            <div>
              <span class="font-medium">Allow Marketing Communications</span>
              <p class="text-sm text-gray-500">Receive promotional emails and offers</p>
            </div>
          </label>

          <label class="flex items-center">
            <input
              type="checkbox"
              v-model="settings.data_sharing.third_party"
              @change="updateDataSharing"
              class="mr-3 w-4 h-4 text-blue-600"
            />
            <div>
              <span class="font-medium">Allow Third-Party Data Sharing</span>
              <p class="text-sm text-gray-500">Share data with trusted partners (anonymized)</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Data Access Log -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Recent Data Access</h2>
        <p class="text-sm text-gray-500 mb-4">See who has accessed your data</p>
        
        <div v-if="loadingAccessLog" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
        
        <div v-else-if="accessLog.length === 0" class="text-center py-8 text-gray-500">
          No recent data access
        </div>
        
        <div v-else class="space-y-2">
          <div
            v-for="log in accessLog"
            :key="log.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <p class="font-medium">{{ log.accessed_by.email }}</p>
              <p class="text-sm text-gray-500">{{ log.access_type }} • {{ formatDate(log.accessed_at) }}</p>
            </div>
            <div class="text-sm text-gray-500">
              {{ log.location || log.ip_address }}
            </div>
          </div>
        </div>
      </div>

      <!-- Data Export -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Export Your Data</h2>
        <p class="text-sm text-gray-500 mb-4">
          Download all your data in JSON format (GDPR compliance)
        </p>
        <button
          @click="exportData"
          :disabled="exporting"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ exporting ? 'Exporting...' : 'Download All My Data' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import privacyAPI from '@/api/privacy'

const privacyScore = ref(0)
const settings = ref({
  profile_visibility: {
    to_writers: 'limited',
    to_admins: 'public',
    to_support: 'public'
  },
  data_sharing: {
    analytics: true,
    marketing: false,
    third_party: false
  }
})
const accessLog = ref([])
const loadingAccessLog = ref(false)
const exporting = ref(false)

onMounted(async () => {
  await loadSettings()
  await loadAccessLog()
})

const loadSettings = async () => {
  try {
    const response = await privacyAPI.getSettings()
    settings.value = {
      profile_visibility: response.data.profile_visibility,
      data_sharing: response.data.data_sharing
    }
    privacyScore.value = response.data.privacy_score
  } catch (error) {
    console.error('Failed to load privacy settings:', error)
  }
}

const loadAccessLog = async () => {
  loadingAccessLog.value = true
  try {
    const response = await privacyAPI.getAccessLog({ limit: 20, days: 30 })
    accessLog.value = response.data.logs
  } catch (error) {
    console.error('Failed to load access log:', error)
  } finally {
    loadingAccessLog.value = false
  }
}

const updateVisibility = async () => {
  try {
    const response = await privacyAPI.updateVisibility(settings.value.profile_visibility)
    privacyScore.value = response.data.privacy_score
  } catch (error) {
    console.error('Failed to update visibility:', error)
  }
}

const updateDataSharing = async () => {
  try {
    const response = await privacyAPI.updateDataSharing(settings.value.data_sharing)
    privacyScore.value = response.data.privacy_score
  } catch (error) {
    console.error('Failed to update data sharing:', error)
  }
}

const exportData = async () => {
  exporting.value = true
  try {
    const response = await privacyAPI.exportData()
    // Download as JSON file
    const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `my-data-export-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export data:', error)
    alert('Failed to export data. Please try again.')
  } finally {
    exporting.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

