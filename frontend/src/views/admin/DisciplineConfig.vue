<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Discipline Configuration
            </h1>
            <p class="text-gray-600 dark:text-gray-400">
              Configure automatic discipline rules and thresholds for writers
            </p>
          </div>
          <button
            v-if="selectedWebsite && currentConfig"
            @click="loadConfig"
            :disabled="loading"
            class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>

        <!-- Info Banner -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
          <h3 class="font-semibold text-blue-900 dark:text-blue-300 mb-2 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            How Discipline Configuration Works
          </h3>
          <p class="text-sm text-blue-800 dark:text-blue-300 mb-2">
            Configure automatic disciplinary actions that trigger when writers accumulate strikes or warnings. 
            These rules help maintain quality standards by automatically escalating discipline based on violations.
          </p>
          <ul class="text-sm text-blue-800 dark:text-blue-300 list-disc list-inside space-y-1">
            <li><strong>Max Strikes:</strong> Number of strikes before a warning is escalated to suspension</li>
            <li><strong>Auto Suspend Days:</strong> Duration (in days) for automatic suspensions</li>
            <li><strong>Auto Blacklist Strikes:</strong> Number of strikes that trigger automatic blacklisting</li>
          </ul>
        </div>

        <!-- Website Selector -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Website <span class="text-red-500">*</span>
          </label>
          <select
            v-model="selectedWebsite"
            @change="loadConfig"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :disabled="loading"
          >
            <option value="">Choose a website...</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">
              {{ formatWebsiteName(site) }}
            </option>
          </select>
          <p v-if="!selectedWebsite" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Select a website to configure discipline rules for that website's writers
          </p>
        </div>
      </div>

      <!-- Configuration Form -->
      <div v-if="selectedWebsite" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p class="ml-3 text-gray-600 dark:text-gray-400">Loading configuration...</p>
        </div>
        
        <div v-else class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">Discipline Rules</h2>
            <span
              v-if="currentConfig"
              class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Configuration Exists
            </span>
            <span
              v-else
              class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              No Configuration
            </span>
          </div>
          
          <form @submit.prevent="saveConfig" class="space-y-6">
            <!-- Max Strikes -->
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max Strikes Before Suspension <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="configForm.max_strikes"
                type="number"
                min="1"
                max="10"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.max_strikes }"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                When a writer reaches this number of strikes, they will be automatically suspended.
                Recommended: 3-5 strikes
              </p>
              <div v-if="errors.max_strikes" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ errors.max_strikes }}
              </div>
              <div class="mt-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded p-3">
                <p class="text-sm text-yellow-800 dark:text-yellow-300">
                  <strong>Example:</strong> If set to 3, a writer with 3 strikes will be automatically suspended.
                </p>
              </div>
            </div>

            <!-- Auto Suspend Days -->
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Automatic Suspension Duration (Days) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="configForm.auto_suspend_days"
                type="number"
                min="1"
                max="365"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.auto_suspend_days }"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                How many days a writer will be suspended when they reach the max strikes threshold.
                Recommended: 7-30 days
              </p>
              <div v-if="errors.auto_suspend_days" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ errors.auto_suspend_days }}
              </div>
              <div class="mt-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded p-3">
                <p class="text-sm text-yellow-800 dark:text-yellow-300">
                  <strong>Example:</strong> If set to 7, a writer will be suspended for 7 days when they reach max strikes.
                </p>
              </div>
            </div>

            <!-- Auto Blacklist Strikes -->
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Strikes Before Automatic Blacklisting <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="configForm.auto_blacklist_strikes"
                type="number"
                min="1"
                max="20"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :class="{ 'border-red-500': errors.auto_blacklist_strikes }"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                When a writer accumulates this many strikes, they will be automatically blacklisted.
                This should be higher than max_strikes. Recommended: 5-10 strikes
              </p>
              <div v-if="errors.auto_blacklist_strikes" class="mt-1 text-sm text-red-600 dark:text-red-400">
                {{ errors.auto_blacklist_strikes }}
              </div>
              <div class="mt-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3">
                <p class="text-sm text-red-800 dark:text-red-300">
                  <strong>Warning:</strong> Blacklisting is permanent and prevents the writer from accessing the platform.
                  Use this threshold carefully.
                </p>
              </div>
            </div>

            <!-- Validation Summary -->
            <div v-if="hasValidationErrors" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h4 class="font-semibold text-red-900 dark:text-red-300 mb-2 flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Validation Errors
              </h4>
              <ul class="text-sm text-red-800 dark:text-red-300 list-disc list-inside space-y-1">
                <li v-if="errors.max_strikes">{{ errors.max_strikes }}</li>
                <li v-if="errors.auto_suspend_days">{{ errors.auto_suspend_days }}</li>
                <li v-if="errors.auto_blacklist_strikes">{{ errors.auto_blacklist_strikes }}</li>
                <li v-if="errors.general">{{ errors.general }}</li>
              </ul>
            </div>

            <!-- Current Status Display -->
            <div v-if="currentConfig" class="bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h3 class="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Current Configuration
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Max Strikes</p>
                  <p class="text-lg font-bold text-gray-900 dark:text-white">{{ currentConfig.max_strikes }}</p>
                </div>
                <div class="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Suspend Days</p>
                  <p class="text-lg font-bold text-gray-900 dark:text-white">{{ currentConfig.auto_suspend_days }}</p>
                </div>
                <div class="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
                  <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Blacklist At</p>
                  <p class="text-lg font-bold text-gray-900 dark:text-white">{{ currentConfig.auto_blacklist_strikes }}</p>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                @click="resetForm"
                class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Reset
              </button>
              <button
                type="submit"
                :disabled="saving || hasValidationErrors"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg v-if="saving" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ saving ? 'Saving...' : (currentConfig ? 'Update Configuration' : 'Create Configuration') }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- No Website Selected -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">No Website Selected</h3>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Please select a website to configure discipline rules.</p>
      </div>

      <!-- Success/Error Messages -->
      <div
        v-if="message"
        class="mt-6 p-4 rounded-lg flex items-start gap-3"
        :class="messageSuccess ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'"
      >
        <svg
          v-if="messageSuccess"
          class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg
          v-else
          class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p :class="messageSuccess ? 'text-green-800 dark:text-green-300' : 'text-red-800 dark:text-red-300'">
          {{ message }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const errors = ref({
  max_strikes: '',
  auto_suspend_days: '',
  auto_blacklist_strikes: '',
  general: ''
})

const configForm = ref({
  max_strikes: 3,
  auto_suspend_days: 7,
  auto_blacklist_strikes: 5,
})

const hasValidationErrors = computed(() => {
  return !!(
    errors.value.max_strikes ||
    errors.value.auto_suspend_days ||
    errors.value.auto_blacklist_strikes ||
    errors.value.general
  )
})

const validateForm = () => {
  // Reset errors
  errors.value = {
    max_strikes: '',
    auto_suspend_days: '',
    auto_blacklist_strikes: '',
    general: ''
  }

  // Validate max_strikes
  if (!configForm.value.max_strikes || configForm.value.max_strikes < 1 || configForm.value.max_strikes > 10) {
    errors.value.max_strikes = 'Max strikes must be between 1 and 10'
  }

  // Validate auto_suspend_days
  if (!configForm.value.auto_suspend_days || configForm.value.auto_suspend_days < 1 || configForm.value.auto_suspend_days > 365) {
    errors.value.auto_suspend_days = 'Suspension days must be between 1 and 365'
  }

  // Validate auto_blacklist_strikes
  if (!configForm.value.auto_blacklist_strikes || configForm.value.auto_blacklist_strikes < 1 || configForm.value.auto_blacklist_strikes > 20) {
    errors.value.auto_blacklist_strikes = 'Blacklist strikes must be between 1 and 20'
  }

  // Validate logical consistency
  if (configForm.value.auto_blacklist_strikes <= configForm.value.max_strikes) {
    errors.value.auto_blacklist_strikes = 'Blacklist strikes must be greater than max strikes'
  }

  return !hasValidationErrors.value
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
    showToast('Failed to load websites', 'error')
  }
}

const loadConfig = async () => {
  if (!selectedWebsite.value) {
    currentConfig.value = null
    return
  }

  loading.value = true
  message.value = ''
  errors.value = { max_strikes: '', auto_suspend_days: '', auto_blacklist_strikes: '', general: '' }
  
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
    if (e.response?.status !== 404) {
      message.value = 'Failed to load configuration: ' + (e.response?.data?.detail || e.message)
      messageSuccess.value = false
    }
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  if (!selectedWebsite.value) {
    message.value = 'Please select a website first'
    messageSuccess.value = false
    showToast(message.value, 'error')
    return
  }

  // Validate form
  if (!validateForm()) {
    message.value = 'Please fix validation errors before saving'
    messageSuccess.value = false
    showToast(message.value, 'error')
    return
  }

  saving.value = true
  message.value = ''
  errors.value = { max_strikes: '', auto_suspend_days: '', auto_blacklist_strikes: '', general: '' }
  
  try {
    const data = {
      website: selectedWebsite.value,
      max_strikes: configForm.value.max_strikes,
      auto_suspend_days: configForm.value.auto_suspend_days,
      auto_blacklist_strikes: configForm.value.auto_blacklist_strikes,
    }

    if (currentConfig.value && currentConfig.value.id) {
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
    
    // Clear message after 5 seconds
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    const errorMsg = e.response?.data?.detail || e.response?.data?.error || e.message || 'Failed to save configuration'
    message.value = 'Failed to save configuration: ' + errorMsg
    messageSuccess.value = false
    errors.value.general = errorMsg
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
  errors.value = { max_strikes: '', auto_suspend_days: '', auto_blacklist_strikes: '', general: '' }
  message.value = ''
}

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
/* Additional custom styles if needed */
</style>
