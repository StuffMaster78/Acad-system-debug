<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-6">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <router-link
              :to="`/admin/users/${userId}/view`"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Edit User</h1>
              <p class="text-gray-600 dark:text-gray-400 mt-1">Update user information and settings</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading user details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-12">
        <div class="text-center">
          <div class="flex justify-center mb-4">
            <svg class="w-12 h-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Error Loading User</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-4">{{ error }}</p>
          <button
            @click="loadUser"
            class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Retry</span>
          </button>
        </div>
      </div>

      <!-- Edit Form -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <form @submit.prevent="saveUser" class="p-6 space-y-6">
          <!-- Basic Information -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Basic Information</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Username <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="userForm.username" 
                  type="text" 
                  required 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="Enter username"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email <span class="text-red-500">*</span>
                </label>
                <input 
                  v-model="userForm.email" 
                  type="email" 
                  required 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="user@example.com"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">First Name</label>
                <input 
                  v-model="userForm.first_name" 
                  type="text" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="First name"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Last Name</label>
                <input 
                  v-model="userForm.last_name" 
                  type="text" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="Last name"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Role <span class="text-red-500">*</span>
                </label>
                <select 
                  v-model="userForm.role" 
                  required 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                >
                  <option value="client">Client</option>
                  <option value="writer">Writer</option>
                  <option value="editor">Editor</option>
                  <option value="support">Support</option>
                  <option v-if="authStore.isSuperAdmin" value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Phone</label>
                <input 
                  v-model="userForm.phone_number" 
                  type="tel" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Website</label>
                <select 
                  v-model="userForm.website" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                >
                  <option :value="null">No Website</option>
                  <option v-for="site in websites" :key="site.id" :value="site.id">
                    {{ formatWebsiteName(site) }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Settings -->
          <div class="space-y-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2">Settings</h3>
            <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <input
                v-model="userForm.is_active"
                type="checkbox"
                id="user_active"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label for="user_active" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                Active
              </label>
              <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">User account is active and can log in</p>
            </div>
          </div>

          <!-- Messages -->
          <div v-if="message" class="p-4 rounded-lg shadow-sm border" :class="messageSuccess ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300' : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300'">
            <div class="flex items-center gap-2">
              <span v-if="messageSuccess" class="text-green-600 dark:text-green-400 text-xl font-bold">✓</span>
              <span v-else class="text-red-600 dark:text-red-400 text-xl font-bold">✗</span>
              <span class="font-medium">{{ message }}</span>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <router-link
              :to="`/admin/users/${userId}/view`"
              class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </router-link>
            <button 
              type="submit" 
              :disabled="saving"
              class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
              {{ saving ? 'Saving...' : 'Update User' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import { formatWebsiteName } from '@/utils/formatDisplay'
import apiClient from '@/api/client'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()

const userId = computed(() => parseInt(route.params.id))
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const message = ref('')
const messageSuccess = ref(false)
const websites = ref([])

const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'client',
  phone_number: '',
  website: null,
  is_active: true,
})

const loadUser = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await adminManagementAPI.getUser(userId.value)
    const user = res.data
    userForm.value = {
      username: user.username,
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      phone_number: user.phone_number || '',
      website: user.website?.id || null,
      is_active: user.is_active,
    }
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to load user details', `Unable to load user #${userId.value}. Please try again.`)
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const saveUser = async () => {
  saving.value = true
  message.value = ''
  try {
    const data = { ...userForm.value }
    delete data.password
    const response = await adminManagementAPI.patchUser(userId.value, data)
    const successMsg = 'User updated successfully!'
    message.value = successMsg
    messageSuccess.value = true
    showSuccess(successMsg)
    // Redirect to view page after a short delay
    setTimeout(() => {
      router.push(`/admin/users/${userId.value}/view`)
    }, 1500)
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to save user', 'Unable to update user. Please try again.')
    message.value = errorMsg
    messageSuccess.value = false
    showError(errorMsg)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([loadUser(), loadWebsites()])
})
</script>

