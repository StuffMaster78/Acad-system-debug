<template>
  <div class="notification-settings">
    <div class="card p-6">
      <h2 class="text-2xl font-bold mb-6">Notification Preferences</h2>
      <p class="text-gray-600 mb-6">
        Choose how you want to be notified about different events and activities.
      </p>

      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <form v-else @submit.prevent="saveSettings" class="space-y-6">
        <!-- Email Notifications -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-semibold mb-4">Email Notifications</h3>
          <div class="space-y-4">
            <div
              v-for="pref in emailPreferences"
              :key="pref.key"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-1">
                <label class="font-medium text-gray-900">{{ pref.label }}</label>
                <p class="text-sm text-gray-600">{{ pref.description }}</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="preferences[pref.key]"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- Push Notifications -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-semibold mb-4">Push Notifications</h3>
          <div class="space-y-4">
            <div
              v-for="pref in pushPreferences"
              :key="pref.key"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-1">
                <label class="font-medium text-gray-900">{{ pref.label }}</label>
                <p class="text-sm text-gray-600">{{ pref.description }}</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="preferences[pref.key]"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- In-App Notifications -->
        <div class="pb-6">
          <h3 class="text-lg font-semibold mb-4">In-App Notifications</h3>
          <div class="space-y-4">
            <div
              v-for="pref in inAppPreferences"
              :key="pref.key"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex-1">
                <label class="font-medium text-gray-900">{{ pref.label }}</label>
                <p class="text-sm text-gray-600">{{ pref.description }}</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="preferences[pref.key]"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>

        <!-- Error/Success Messages -->
        <div v-if="error" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {{ error }}
        </div>
        <div v-if="success" class="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {{ success }}
        </div>

        <!-- Save Button -->
        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="saving"
            class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Saving...' : 'Save Preferences' }}
          </button>
          <button
            type="button"
            @click="resetToDefaults"
            class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Reset to Defaults
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import notificationsAPI from '@/api/notifications'

const preferences = ref({})
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

const emailPreferences = [
  {
    key: 'email_order_updates',
    label: 'Order Updates',
    description: 'Receive emails when your orders are updated, completed, or have new messages'
  },
  {
    key: 'email_payment_receipts',
    label: 'Payment Receipts',
    description: 'Receive email receipts for payments and transactions'
  },
  {
    key: 'email_ticket_updates',
    label: 'Ticket Updates',
    description: 'Receive emails when support tickets are updated or resolved'
  },
  {
    key: 'email_promotions',
    label: 'Promotions & Offers',
    description: 'Receive emails about special promotions, discounts, and offers'
  },
  {
    key: 'email_account_updates',
    label: 'Account Updates',
    description: 'Receive emails about important account changes and security updates'
  }
]

const pushPreferences = [
  {
    key: 'push_order_updates',
    label: 'Order Updates',
    description: 'Get push notifications for order status changes'
  },
  {
    key: 'push_messages',
    label: 'New Messages',
    description: 'Get push notifications when you receive new messages'
  },
  {
    key: 'push_ticket_updates',
    label: 'Ticket Updates',
    description: 'Get push notifications for ticket updates'
  }
]

const inAppPreferences = [
  {
    key: 'inapp_order_updates',
    label: 'Order Updates',
    description: 'Show in-app notifications for order updates'
  },
  {
    key: 'inapp_messages',
    label: 'New Messages',
    description: 'Show in-app notifications for new messages'
  },
  {
    key: 'inapp_ticket_updates',
    label: 'Ticket Updates',
    description: 'Show in-app notifications for ticket updates'
  },
  {
    key: 'inapp_reviews',
    label: 'New Reviews',
    description: 'Show in-app notifications when you receive new reviews'
  }
]

const loadPreferences = async () => {
  loading.value = true
  error.value = ''
  try {
    // Assuming there's an endpoint for notification preferences
    // This would need to be implemented in the backend
    const response = await notificationsAPI.getPreferences()
    preferences.value = response.data || getDefaultPreferences()
  } catch (err) {
    console.error('Failed to load notification preferences:', err)
    // Use defaults if API fails
    preferences.value = getDefaultPreferences()
  } finally {
    loading.value = false
  }
}

const getDefaultPreferences = () => {
  const defaults = {}
  ;[...emailPreferences, ...pushPreferences, ...inAppPreferences].forEach(pref => {
    defaults[pref.key] = true // Default to enabled
  })
  return defaults
}

const saveSettings = async () => {
  saving.value = true
  error.value = ''
  success.value = ''
  
  try {
    await notificationsAPI.updatePreferences(preferences.value)
    success.value = 'Notification preferences saved successfully!'
    setTimeout(() => {
      success.value = ''
    }, 3000)
  } catch (err) {
    console.error('Failed to save notification preferences:', err)
    error.value = err?.response?.data?.error || err?.response?.data?.message || 'Failed to save preferences. Please try again.'
  } finally {
    saving.value = false
  }
}

const resetToDefaults = () => {
  if (confirm('Are you sure you want to reset all notification preferences to defaults?')) {
    preferences.value = getDefaultPreferences()
    saveSettings()
  }
}

onMounted(() => {
  loadPreferences()
})
</script>

<style scoped>
.notification-settings {
  width: 100%;
}
</style>

