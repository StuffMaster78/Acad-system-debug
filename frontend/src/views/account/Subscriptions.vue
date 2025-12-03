<template>
  <div class="subscriptions-page">
    <div class="max-w-6xl mx-auto p-6">
      <div class="page-header mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Communication Preferences</h1>
        <p class="text-gray-600">Manage how and when you receive updates from us</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">{{ error }}</p>
        <button 
          @click="fetchData" 
          class="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Master Switch -->
        <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6 shadow-sm">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 mb-1">All Subscriptions</h2>
              <p class="text-sm text-gray-600">Master switch to enable/disable all subscriptions</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.all_subscriptions_enabled"
                @change="updateMasterSwitch"
                :disabled="saving"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <!-- Marketing Consent -->
        <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6 shadow-sm">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h2 class="text-xl font-semibold text-gray-900 mb-1">Marketing Consent</h2>
              <p class="text-sm text-gray-600 mb-2">
                Allow us to send you marketing communications, promotional offers, and special deals.
              </p>
              <p v-if="preferences.marketing_consent_date" class="text-xs text-gray-500">
                Consent given on: {{ formatDate(preferences.marketing_consent_date) }}
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                v-model="preferences.marketing_consent"
                @change="updateMarketingConsent"
                :disabled="saving || !preferences.all_subscriptions_enabled"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        <!-- Channel Preferences -->
        <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6 shadow-sm">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Delivery Channels</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.email_enabled"
                @change="updateChannelPreferences"
                :disabled="saving"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-700">Email</span>
            </label>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.sms_enabled"
                @change="updateChannelPreferences"
                :disabled="saving"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-700">SMS</span>
            </label>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.push_enabled"
                @change="updateChannelPreferences"
                :disabled="saving"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-700">Push Notifications</span>
            </label>
            <label class="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.in_app_enabled"
                @change="updateChannelPreferences"
                :disabled="saving"
                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span class="text-gray-700">In-App Notifications</span>
            </label>
          </div>
        </div>

        <!-- Do Not Disturb -->
        <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 mb-1">Quiet Hours</h2>
              <p class="text-sm text-gray-600">Set hours when you don't want to receive non-critical notifications</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="preferences.dnd_enabled"
                @change="updateDNDSettings"
                :disabled="saving"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <div v-if="preferences.dnd_enabled" class="grid grid-cols-2 gap-4 mt-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Start Hour</label>
              <input
                type="number"
                v-model.number="preferences.dnd_start_hour"
                @change="updateDNDSettings"
                :disabled="saving"
                min="0"
                max="23"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">End Hour</label>
              <input
                type="number"
                v-model.number="preferences.dnd_end_hour"
                @change="updateDNDSettings"
                :disabled="saving"
                min="0"
                max="23"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <!-- Subscription Types -->
        <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Subscription Types</h2>
          <div class="space-y-4">
            <div
              v-for="subscription in subscriptions"
              :key="subscription.subscription_type"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h3 class="text-lg font-medium text-gray-900">
                      {{ getSubscriptionLabel(subscription.subscription_type) }}
                    </h3>
                    <span
                      v-if="subscription.is_subscribed"
                      class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
                    >
                      Subscribed
                    </span>
                    <span
                      v-else
                      class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
                    >
                      Not Subscribed
                    </span>
                    <span
                      v-if="subscription.subscription_type === 'transactional_messages'"
                      class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800"
                    >
                      Required
                    </span>
                  </div>
                  <p class="text-sm text-gray-600 mb-3">
                    {{ getSubscriptionDescription(subscription.subscription_type) }}
                  </p>
                  
                  <!-- Frequency Selector -->
                  <div v-if="subscription.is_subscribed" class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                    <select
                      :value="subscription.frequency"
                      @change="updateFrequency(subscription.subscription_type, $event.target.value)"
                      :disabled="saving"
                      class="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="immediate">Immediate</option>
                      <option value="daily">Daily Digest</option>
                      <option value="weekly">Weekly Digest</option>
                      <option value="monthly">Monthly Digest</option>
                    </select>
                  </div>

                  <!-- Channel Selector -->
                  <div v-if="subscription.is_subscribed" class="mb-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">Preferred Channels</label>
                    <div class="flex flex-wrap gap-2">
                      <label
                        v-for="channel in availableChannels"
                        :key="channel.value"
                        class="flex items-center space-x-1 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          :checked="subscription.preferred_channels.includes(channel.value)"
                          @change="toggleChannel(subscription.subscription_type, channel.value, $event.target.checked)"
                          :disabled="saving"
                          class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <span class="text-sm text-gray-700">{{ channel.label }}</span>
                      </label>
                    </div>
                  </div>
                </div>
                
                <!-- Toggle Button -->
                <div class="ml-4">
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="subscription.is_subscribed"
                      @change="toggleSubscription(subscription.subscription_type, $event.target.checked)"
                      :disabled="saving || subscription.subscription_type === 'transactional_messages' || !preferences.all_subscriptions_enabled"
                      class="sr-only peer"
                    />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 peer-disabled:opacity-50 peer-disabled:cursor-not-allowed"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useToast } from '@/composables/useToast'
import subscriptionsAPI from '@/api/subscriptions'

const { success, error: showError } = useToast()

const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const subscriptions = ref([])
const preferences = ref({
  all_subscriptions_enabled: true,
  marketing_consent: false,
  marketing_consent_date: null,
  email_enabled: true,
  sms_enabled: false,
  push_enabled: false,
  in_app_enabled: true,
  dnd_enabled: false,
  dnd_start_hour: 22,
  dnd_end_hour: 6,
  transactional_enabled: true,
})

const availableChannels = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
  { value: 'push', label: 'Push' },
  { value: 'in_app', label: 'In-App' },
]

const subscriptionLabels = {
  newsletter: 'Newsletter',
  blog_posts: 'Blog Post Updates',
  coupon_updates: 'Coupon Updates',
  marketing_messages: 'Marketing Messages',
  unread_messages: 'Unread Messages',
  transactional_messages: 'Transactional Messages',
  notifications: 'Notifications',
  order_updates: 'Order Updates',
  promotional_offers: 'Promotional Offers',
  product_updates: 'Product Updates',
  security_alerts: 'Security Alerts',
  account_updates: 'Account Updates',
}

const subscriptionDescriptions = {
  newsletter: 'Receive our regular newsletter with updates and insights',
  blog_posts: 'Get notified when we publish new blog posts',
  coupon_updates: 'Receive exclusive coupons and discount codes',
  marketing_messages: 'Promotional offers and marketing communications',
  unread_messages: 'Notifications about unread messages in your account',
  transactional_messages: 'Important account and order-related messages (cannot be disabled)',
  notifications: 'General notifications about your account activity',
  order_updates: 'Updates about your order status and progress',
  promotional_offers: 'Special promotional offers and deals',
  product_updates: 'Updates about new features and product improvements',
  security_alerts: 'Important security alerts and account activity notifications',
  account_updates: 'Updates about your account settings and changes',
}

const getSubscriptionLabel = (type) => subscriptionLabels[type] || type
const getSubscriptionDescription = (type) => subscriptionDescriptions[type] || ''

const fetchData = async () => {
  loading.value = true
  error.value = null
  try {
    const [subscriptionsRes, preferencesRes] = await Promise.all([
      subscriptionsAPI.listAll(),
      subscriptionsAPI.getPreferences(),
    ])
    
    subscriptions.value = subscriptionsRes.data
    preferences.value = { ...preferences.value, ...preferencesRes.data }
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to load subscriptions'
    showError(error.value)
  } finally {
    loading.value = false
  }
}

const updateMasterSwitch = async () => {
  saving.value = true
  try {
    await subscriptionsAPI.updatePreferences({
      all_subscriptions_enabled: preferences.value.all_subscriptions_enabled,
    })
    success('Subscriptions updated successfully')
    await fetchData()
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update subscriptions')
    await fetchData() // Revert on error
  } finally {
    saving.value = false
  }
}

const updateMarketingConsent = async () => {
  saving.value = true
  try {
    await subscriptionsAPI.updatePreferences({
      marketing_consent: preferences.value.marketing_consent,
    })
    success('Marketing consent updated successfully')
    await fetchData()
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update marketing consent')
    await fetchData()
  } finally {
    saving.value = false
  }
}

const updateChannelPreferences = async () => {
  saving.value = true
  try {
    await subscriptionsAPI.updatePreferences({
      email_enabled: preferences.value.email_enabled,
      sms_enabled: preferences.value.sms_enabled,
      push_enabled: preferences.value.push_enabled,
      in_app_enabled: preferences.value.in_app_enabled,
    })
    success('Channel preferences updated')
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update channel preferences')
    await fetchData()
  } finally {
    saving.value = false
  }
}

const updateDNDSettings = async () => {
  saving.value = true
  try {
    await subscriptionsAPI.updatePreferences({
      dnd_enabled: preferences.value.dnd_enabled,
      dnd_start_hour: preferences.value.dnd_start_hour,
      dnd_end_hour: preferences.value.dnd_end_hour,
    })
    success('Quiet hours updated')
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update quiet hours')
    await fetchData()
  } finally {
    saving.value = false
  }
}

const toggleSubscription = async (subscriptionType, isSubscribed) => {
  if (subscriptionType === 'transactional_messages') {
    showError('Transactional messages cannot be unsubscribed')
    return
  }
  
  saving.value = true
  try {
    if (isSubscribed) {
      await subscriptionsAPI.subscribe(subscriptionType)
      success(`Subscribed to ${getSubscriptionLabel(subscriptionType)}`)
    } else {
      await subscriptionsAPI.unsubscribe(subscriptionType)
      success(`Unsubscribed from ${getSubscriptionLabel(subscriptionType)}`)
    }
    await fetchData()
  } catch (err) {
    showError(err.response?.data?.detail || `Failed to ${isSubscribed ? 'subscribe' : 'unsubscribe'}`)
    await fetchData()
  } finally {
    saving.value = false
  }
}

const updateFrequency = async (subscriptionType, frequency) => {
  saving.value = true
  try {
    await subscriptionsAPI.updateFrequency(subscriptionType, frequency)
    success('Frequency updated')
    await fetchData()
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update frequency')
    await fetchData()
  } finally {
    saving.value = false
  }
}

const toggleChannel = async (subscriptionType, channel, enabled) => {
  saving.value = true
  try {
    const subscription = subscriptions.value.find(s => s.subscription_type === subscriptionType)
    const currentChannels = subscription?.preferred_channels || []
    const newChannels = enabled
      ? [...currentChannels, channel]
      : currentChannels.filter(c => c !== channel)
    
    await subscriptionsAPI.updateChannels(subscriptionType, newChannels)
    success('Channels updated')
    await fetchData()
  } catch (err) {
    showError(err.response?.data?.detail || 'Failed to update channels')
    await fetchData()
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.subscriptions-page {
  min-height: calc(100vh - 4rem);
}
</style>

