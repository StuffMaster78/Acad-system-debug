<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Discipline Configuration</h1>
        <p class="mt-2 text-gray-600">Configure automatic discipline rules and thresholds for writers</p>
      </div>
    </div>

    <!-- Info Banner -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 class="font-semibold text-blue-900 mb-2">How Discipline Configuration Works</h3>
      <p class="text-sm text-blue-800 mb-2">
        Configure automatic disciplinary actions that trigger when writers accumulate strikes or warnings. 
        These rules help maintain quality standards by automatically escalating discipline based on violations.
      </p>
      <ul class="text-sm text-blue-800 list-disc list-inside space-y-1">
        <li><strong>Max Strikes:</strong> Number of strikes before a warning is escalated to suspension</li>
        <li><strong>Auto Suspend Days:</strong> Duration (in days) for automatic suspensions</li>
        <li><strong>Auto Blacklist Strikes:</strong> Number of strikes that trigger automatic blacklisting</li>
      </ul>
    </div>

    <!-- Website Selector -->
    <div class="card p-4">
      <label class="block text-sm font-medium mb-2">Select Website</label>
      <select v-model="selectedWebsite" @change="loadConfig" class="w-full border rounded px-3 py-2">
        <option value="">Choose a website...</option>
        <option v-for="site in websites" :key="site.id" :value="site.id">
          {{ formatWebsiteName(site) }}
        </option>
      </select>
    </div>

    <!-- Configuration Form -->
    <div v-if="selectedWebsite" class="card p-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <h2 class="text-xl font-bold mb-4">Discipline Rules</h2>
        
        <form @submit.prevent="saveConfig" class="space-y-6">
          <!-- Max Strikes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Max Strikes Before Suspension
            </label>
            <input
              v-model.number="configForm.max_strikes"
              type="number"
              min="1"
              max="10"
              required
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              When a writer reaches this number of strikes, they will be automatically suspended.
              Recommended: 3-5 strikes
            </p>
            <div class="mt-2 bg-yellow-50 border border-yellow-200 rounded p-3">
              <p class="text-sm text-yellow-800">
                <strong>Example:</strong> If set to 3, a writer with 3 strikes will be automatically suspended.
              </p>
            </div>
          </div>

          <!-- Auto Suspend Days -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Automatic Suspension Duration (Days)
            </label>
            <input
              v-model.number="configForm.auto_suspend_days"
              type="number"
              min="1"
              max="365"
              required
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              How many days a writer will be suspended when they reach the max strikes threshold.
              Recommended: 7-30 days
            </p>
            <div class="mt-2 bg-yellow-50 border border-yellow-200 rounded p-3">
              <p class="text-sm text-yellow-800">
                <strong>Example:</strong> If set to 7, a writer will be suspended for 7 days when they reach max strikes.
              </p>
            </div>
          </div>

          <!-- Auto Blacklist Strikes -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Strikes Before Automatic Blacklisting
            </label>
            <input
              v-model.number="configForm.auto_blacklist_strikes"
              type="number"
              min="1"
              max="20"
              required
              class="w-full border rounded px-3 py-2"
            />
            <p class="text-xs text-gray-500 mt-1">
              When a writer accumulates this many strikes, they will be automatically blacklisted.
              This should be higher than max_strikes. Recommended: 5-10 strikes
            </p>
            <div class="mt-2 bg-red-50 border border-red-200 rounded p-3">
              <p class="text-sm text-red-800">
                <strong>Warning:</strong> Blacklisting is permanent and prevents the writer from accessing the platform.
                Use this threshold carefully.
              </p>
            </div>
          </div>

          <!-- Current Status Display -->
          <div v-if="currentConfig" class="bg-gray-50 border rounded p-4">
            <h3 class="font-semibold text-gray-900 mb-2">Current Configuration</h3>
            <div class="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Max Strikes:</span>
                <span class="ml-2 font-medium">{{ currentConfig.max_strikes }}</span>
              </div>
              <div>
                <span class="text-gray-600">Suspend Days:</span>
                <span class="ml-2 font-medium">{{ currentConfig.auto_suspend_days }}</span>
              </div>
              <div>
                <span class="text-gray-600">Blacklist At:</span>
                <span class="ml-2 font-medium">{{ currentConfig.auto_blacklist_strikes }}</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button
              type="button"
              @click="resetForm"
              class="btn btn-secondary"
            >
              Reset
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="btn btn-primary"
            >
              {{ saving ? 'Saving...' : (currentConfig ? 'Update Configuration' : 'Create Configuration') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- No Website Selected -->
    <div v-else class="card p-12 text-center">
      <p class="text-gray-500">Please select a website to configure discipline rules.</p>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { writerManagementAPI } from '@/api'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'
import { formatWebsiteName } from '@/utils/formatDisplay'

const { showToast } = useToast()

const loading = ref(false)
const saving = ref(false)
const websites = ref([])
const selectedWebsite = ref('')
const currentConfig = ref(null)
const message = ref('')
const messageSuccess = ref(false)

const configForm = ref({
  max_strikes: 3,
  auto_suspend_days: 7,
  auto_blacklist_strikes: 5,
})

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadConfig = async () => {
  if (!selectedWebsite.value) {
    currentConfig.value = null
    return
  }

  loading.value = true
  try {
    const res = await writerManagementAPI.getDisciplineConfigByWebsite(selectedWebsite.value)
    if (res.data && res.data.website) {
      currentConfig.value = res.data
      configForm.value = {
        max_strikes: res.data.max_strikes || 3,
        auto_suspend_days: res.data.auto_suspend_days || 7,
        auto_blacklist_strikes: res.data.auto_blacklist_strikes || 5,
      }
    } else {
      // No config exists, use defaults
      currentConfig.value = null
      configForm.value = {
        max_strikes: 3,
        auto_suspend_days: 7,
        auto_blacklist_strikes: 5,
      }
    }
  } catch (e) {
    console.error('Failed to load config:', e)
    // Use defaults if config doesn't exist
    currentConfig.value = null
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  if (!selectedWebsite.value) {
    message.value = 'Please select a website first'
    messageSuccess.value = false
    return
  }

  saving.value = true
  message.value = ''
  
  try {
    const data = {
      website: selectedWebsite.value,
      ...configForm.value,
    }

    if (currentConfig.value) {
      // Update existing config
      await writerManagementAPI.updateDisciplineConfig(selectedWebsite.value, data)
      message.value = 'Configuration updated successfully'
    } else {
      // Create new config
      await writerManagementAPI.createDisciplineConfig(data)
      message.value = 'Configuration created successfully'
    }
    
    messageSuccess.value = true
    await loadConfig()
    showToast(message.value, 'success')
  } catch (e) {
    message.value = 'Failed to save configuration: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  if (currentConfig.value) {
    configForm.value = {
      max_strikes: currentConfig.value.max_strikes || 3,
      auto_suspend_days: currentConfig.value.auto_suspend_days || 7,
      auto_blacklist_strikes: currentConfig.value.auto_blacklist_strikes || 5,
    }
  } else {
    configForm.value = {
      max_strikes: 3,
      auto_suspend_days: 7,
      auto_blacklist_strikes: 5,
    }
  }
}

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.btn-primary {
  background-color: #2563eb;
  color: white;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  padding: 1.5rem;
}
</style>

