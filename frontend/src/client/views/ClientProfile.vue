<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Manage your account information and preferences</p>
    </div>

    <!-- Profile Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700 space-y-6">
      <div>
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

        <!-- Contact Information (Read-only) -->
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Contact Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phone Number
              </label>
              <p class="text-gray-900 dark:text-white">{{ profile.phone || '—' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Timezone
              </label>
              <p class="text-gray-900 dark:text-white">{{ profile.timezone || '—' }}</p>
            </div>
          </div>
        </div>

        <!-- Edit Link -->
        <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
          <router-link
            to="/account/settings"
            class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Edit Profile in Settings
          </router-link>
        </div>
      </div>
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

const profile = ref({
  full_name: '',
  email: '',
  phone: '',
  timezone: 'UTC'
})
const stats = ref({})

const fetchProfile = async () => {
  try {
    const response = await usersAPI.getProfile()
    const user = response.data
    profile.value = {
      full_name: user.full_name || '',
      email: user.email || '',
      phone: user.phone || user.phone_number || '',
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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
}

onMounted(async () => {
  await Promise.all([fetchProfile(), fetchStats()])
})
</script>

