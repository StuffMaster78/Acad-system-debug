<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Manage your account information and preferences</p>
    </div>

    <!-- Profile Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-6">
      <form @submit.prevent="saveProfile">
        <!-- Personal Information -->
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Personal Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Full Name
              </label>
              <input
                v-model="profile.full_name"
                type="text"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email
              </label>
              <input
                v-model="profile.email"
                type="email"
                disabled
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
              />
              <p class="mt-1 text-xs text-gray-500">Email cannot be changed</p>
            </div>
          </div>
        </div>

        <!-- Contact Information -->
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Contact Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phone Number
              </label>
              <input
                v-model="profile.phone"
                type="tel"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Timezone
              </label>
              <select
                v-model="profile.timezone"
                class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option v-for="tz in timezones" :key="tz" :value="tz">{{ tz }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            type="submit"
            :disabled="saving"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Account Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Orders</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_orders || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Spent</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ (stats.total_spent || 0).toFixed(2) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Member Since</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ formatDate(authStore.user?.date_joined) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import clientDashboardAPI from '@/api/client-dashboard'

const authStore = useAuthStore()

const saving = ref(false)
const profile = ref({
  full_name: '',
  email: '',
  phone: '',
  timezone: 'UTC'
})
const stats = ref({})
const timezones = ref([
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Asia/Tokyo',
  'Australia/Sydney'
])

const fetchProfile = async () => {
  try {
    const response = await usersAPI.getProfile()
    const user = response.data
    profile.value = {
      full_name: user.full_name || '',
      email: user.email || '',
      phone: user.phone || '',
      timezone: user.timezone || 'UTC'
    }
  } catch (err) {
    console.error('Failed to fetch profile:', err)
  }
}

const fetchStats = async () => {
  try {
    const response = await clientDashboardAPI.getStats(365)
    stats.value = response.data || {}
  } catch (err) {
    console.error('Failed to fetch stats:', err)
  }
}

const saveProfile = async () => {
  saving.value = true
  try {
    await usersAPI.updateProfile(profile.value)
    await authStore.getProfile() // Refresh auth store
    alert('Profile updated successfully!')
  } catch (err) {
    console.error('Failed to update profile:', err)
    alert(err.response?.data?.detail || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

onMounted(async () => {
  await Promise.all([fetchProfile(), fetchStats()])
})
</script>

