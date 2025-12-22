<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
        <p class="mt-1 text-sm text-gray-600">Manage users, accounts, and security settings</p>
      </div>
      <div class="flex items-center gap-3">
        <router-link
          v-if="authStore.isAdmin || authStore.isSuperAdmin"
          to="/admin/users"
          class="px-4 py-2 rounded-lg font-medium transition-colors bg-gray-100 text-gray-700 hover:bg-gray-200"
        >
          Advanced Management
        </router-link>
        <button
          v-if="authStore.isAdmin || authStore.isSuperAdmin"
          @click="showCreateModal = true"
          class="px-4 py-2 rounded-lg font-medium transition-colors bg-primary-600 text-white hover:bg-primary-700"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create User
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <p class="text-xs font-medium text-gray-600 mb-1">Total Users</p>
        <p class="text-2xl font-bold text-gray-900">{{ userStats.total_users || users.length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <p class="text-xs font-medium text-gray-600 mb-1">Active</p>
        <p class="text-2xl font-bold text-green-600">{{ userStats.active_users || users.filter(u => u.is_active).length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <p class="text-xs font-medium text-gray-600 mb-1">Suspended</p>
        <p class="text-2xl font-bold text-red-600">{{ userStats.suspended_users || users.filter(u => u.is_suspended).length }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <p class="text-xs font-medium text-gray-600 mb-1">With 2FA</p>
        <p class="text-2xl font-bold text-blue-600">{{ usersWith2FA }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Name, email..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Role</label>
          <select v-model="filters.role" @change="loadUsers" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
            <option value="">All Roles</option>
            <option value="client">Client</option>
            <option value="writer">Writer</option>
            <option value="editor">Editor</option>
            <option value="support">Support</option>
            <option value="admin">Admin</option>
            <option v-if="authStore.isSuperAdmin" value="superadmin">Superadmin</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" @change="loadUsers" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="blacklisted">Blacklisted</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium">
            Reset Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="ml-3 text-gray-600">Loading users...</p>
      </div>
    </div>

    <!-- Users List -->
    <div v-else class="bg-white rounded-lg shadow-sm p-6 overflow-hidden">
      <div v-if="!users.length" class="text-center py-12 text-gray-500">
        <p>No users found.</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Joined</th>
              <th v-if="authStore.isAdmin || authStore.isSuperAdmin" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="shrink-0 h-10 w-10 rounded-full bg-linear-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-sm mr-3">
                    {{ getUserInitials(user) }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ user.full_name || user.username }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span :class="getRoleBadgeClass(user.role)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ user.role_display || user.role || 'N/A' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span v-if="user.is_blacklisted" class="px-2 py-1 rounded text-xs bg-black text-white font-medium">Blacklisted</span>
                <span v-else-if="user.is_suspended" class="px-2 py-1 rounded text-xs bg-red-100 text-red-800 font-medium">Suspended</span>
                <span v-else-if="user.is_active" class="px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium">Active</span>
                <span v-else class="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800 font-medium">Inactive</span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(user.date_joined) }}
              </td>
              <td v-if="authStore.isAdmin || authStore.isSuperAdmin" class="px-4 py-3 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <button
                    @click="viewUserDetails(user)"
                    class="text-primary-600 hover:text-primary-800 hover:underline font-medium"
                  >
                    View
                  </button>
                  <div class="relative">
                    <button
                      @click="actionsMenuOpen = actionsMenuOpen === user.id ? null : user.id"
                      class="text-gray-600 hover:text-gray-800"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </button>
                    <div
                      v-if="actionsMenuOpen === user.id"
                      class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10"
                      @click.stop
                    >
                      <div class="py-1">
                        <button
                          @click="resetUserPassword(user)"
                          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Reset Password
                        </button>
                        <button
                          @click="viewUserSecurity(user)"
                          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Security Settings
                        </button>
                        <button
                          @click="viewUserProfileRequests(user)"
                          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Update Requests
                        </button>
                        <router-link
                          :to="`/admin/users?user=${user.id}`"
                          class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Full Management
                        </router-link>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- User Details Modal -->
    <div
      v-if="selectedUser"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="selectedUser = null"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">User Details</h2>
            <button
              @click="selectedUser = null"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div v-if="loadingUserDetails" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-2 text-gray-600">Loading user details...</p>
          </div>

          <div v-else-if="userDetails" class="space-y-6">
            <!-- User Info -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-xs font-medium text-gray-600">Name</label>
                <p class="text-sm font-medium text-gray-900">{{ userDetails.full_name || userDetails.username || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-600">Email</label>
                <p class="text-sm text-gray-900">{{ userDetails.email || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-600">Role</label>
                <p class="text-sm text-gray-900">{{ userDetails.role_display || userDetails.role || 'N/A' }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-600">Status</label>
                <span
                  v-if="userDetails.is_blacklisted"
                  class="inline-block px-2 py-1 rounded text-xs bg-black text-white font-medium"
                >
                  Blacklisted
                </span>
                <span
                  v-else-if="userDetails.is_suspended"
                  class="inline-block px-2 py-1 rounded text-xs bg-red-100 text-red-800 font-medium"
                >
                  Suspended
                </span>
                <span
                  v-else-if="userDetails.is_active"
                  class="inline-block px-2 py-1 rounded text-xs bg-green-100 text-green-800 font-medium"
                >
                  Active
                </span>
                <span v-else class="inline-block px-2 py-1 rounded text-xs bg-gray-100 text-gray-800 font-medium">
                  Inactive
                </span>
              </div>
            </div>

            <!-- Security Settings -->
            <div v-if="securitySettings" class="border-t pt-4">
              <h3 class="text-lg font-semibold text-gray-900 mb-3">Security Settings</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="text-xs font-medium text-gray-600">2FA Enabled</label>
                  <p class="text-sm text-gray-900">
                    <span v-if="securitySettings.two_factor_enabled" class="text-green-600 font-medium">✓ Enabled</span>
                    <span v-else class="text-gray-500">Not enabled</span>
                  </p>
                </div>
                <div>
                  <label class="text-xs font-medium text-gray-600">2FA Method</label>
                  <p class="text-sm text-gray-900">{{ securitySettings.two_factor_method || 'N/A' }}</p>
                </div>
                <div>
                  <label class="text-xs font-medium text-gray-600">Email Verified</label>
                  <p class="text-sm text-gray-900">
                    <span v-if="securitySettings.email_verified" class="text-green-600 font-medium">✓ Verified</span>
                    <span v-else class="text-gray-500">Not verified</span>
                  </p>
                </div>
                <div>
                  <label class="text-xs font-medium text-gray-600">Backup Codes</label>
                  <p class="text-sm text-gray-900">{{ securitySettings.backup_codes_remaining || 0 }} remaining</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="border-t pt-4 flex gap-3">
              <button
                @click="resetUserPassword(userDetails)"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium"
              >
                Reset Password
              </button>
              <button
                @click="viewUserSecurity(userDetails)"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                View Security
              </button>
              <router-link
                :to="`/admin/users?user=${userDetails.id}`"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium inline-block"
              >
                Full Management
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeCreateModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-900">Create New User</h2>
            <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="createUser" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Username *</label>
              <input
                v-model="userForm.username"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                v-model="userForm.email"
                type="email"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  v-model="userForm.first_name"
                  type="text"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input
                  v-model="userForm.last_name"
                  type="text"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Role *</label>
              <select
                v-model="userForm.role"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="client">Client</option>
                <option value="writer">Writer</option>
                <option value="editor">Editor</option>
                <option value="support">Support</option>
                <option v-if="authStore.isSuperAdmin" value="admin">Admin</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Password *</label>
              <input
                v-model="userForm.password"
                type="password"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div class="flex items-center">
              <input
                v-model="userForm.is_active"
                type="checkbox"
                class="rounded"
              />
              <label class="ml-2 text-sm text-gray-700">Active</label>
            </div>
            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                :disabled="creatingUser"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm font-medium"
              >
                {{ creatingUser ? 'Creating...' : 'Create User' }}
              </button>
              <button
                type="button"
                @click="closeCreateModal"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Password Reset Modal -->
    <div
      v-if="showPasswordResetModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showPasswordResetModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Reset Password</h3>
        <p class="text-sm text-gray-600 mb-4">
          A temporary password will be generated and sent to {{ passwordResetUser?.email }}
        </p>
        <div v-if="passwordResetResult" class="mb-4 p-3 rounded bg-green-50 border border-green-200">
          <p class="text-sm text-green-800 font-medium">Password reset successful!</p>
          <p class="text-xs text-green-700 mt-1">Temporary password: <code class="bg-green-100 px-2 py-1 rounded">{{ passwordResetResult.temp_password }}</code></p>
        </div>
        <div class="flex gap-3">
          <button
            @click="confirmPasswordReset"
            :disabled="resettingPassword"
            class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm font-medium"
          >
            {{ resettingPassword ? 'Resetting...' : 'Reset Password' }}
          </button>
          <button
            @click="showPasswordResetModal = false; passwordResetUser = null; passwordResetResult = null"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      <div class="flex items-center justify-between">
        <p>{{ message }}</p>
        <button @click="message = ''" class="ml-4 text-white hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import usersAPI from '@/api/users'
import accountAPI from '@/api/account'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref([])
const message = ref('')
const messageSuccess = ref(false)

// Filters
const filters = ref({
  search: '',
  role: '',
  status: ''
})

// User stats
const userStats = ref({
  total_users: 0,
  active_users: 0,
  suspended_users: 0
})

// User details modal
const selectedUser = ref(null)
const userDetails = ref(null)
const loadingUserDetails = ref(false)
const securitySettings = ref(null)
const actionsMenuOpen = ref(null)

// Password reset
const showPasswordResetModal = ref(false)
const passwordResetUser = ref(null)
const resettingPassword = ref(false)
const passwordResetResult = ref(null)

// Create user
const showCreateModal = ref(false)
const creatingUser = ref(false)
const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'client',
  phone_number: '',
  password: '',
  is_active: true
})

// Computed
const usersWith2FA = computed(() => {
  // This would need to be fetched from API or calculated
  return 0 // Placeholder
})

let searchTimeout = null

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.role) params.role = filters.value.role
    if (filters.value.status === 'suspended') params.is_suspended = 'true'
    if (filters.value.status === 'blacklisted') params.is_blacklisted = 'true'
    if (filters.value.status === 'active') {
      params.is_active = 'true'
      params.is_suspended = 'false'
    }
    if (filters.value.status === 'inactive') params.is_active = 'false'

    // For admins/superadmins, use admin management API to get all users
    // For other roles, use regular users API
    if (authStore.isAdmin || authStore.isSuperAdmin) {
      const res = await adminManagementAPI.listUsers(params)
      users.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
      
      // Load stats
      try {
        const statsRes = await adminManagementAPI.getUserStats()
        userStats.value = statsRes.data
      } catch (e) {
        console.error('Failed to load stats:', e)
      }
    } else {
      // For non-admin users, they can only see themselves or limited users
      const res = await usersAPI.list(params)
      users.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    }
  } catch (e) {
    message.value = 'Failed to load users: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadUsers()
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    role: '',
    status: ''
  }
  loadUsers()
}

const viewUserDetails = async (user) => {
  selectedUser.value = user
  loadingUserDetails.value = true
  userDetails.value = null
  securitySettings.value = null
  
  try {
    // Load full user details
    const res = await adminManagementAPI.getUser(user.id)
    userDetails.value = res.data
    
    // Load security settings (if available)
    try {
      // Note: This endpoint might need to be created or use a different approach
      // For now, we'll try to get 2FA status from account API
      // Since this is for another user, we might need an admin endpoint
      // For now, skip this or use a placeholder
    } catch (e) {
      console.error('Failed to load security settings:', e)
    }
  } catch (e) {
    message.value = 'Failed to load user details: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loadingUserDetails.value = false
  }
}

const resetUserPassword = (user) => {
  passwordResetUser.value = user
  passwordResetResult.value = null
  showPasswordResetModal.value = true
}

const confirmPasswordReset = async () => {
  if (!passwordResetUser.value) return
  
  resettingPassword.value = true
  try {
    const res = await adminManagementAPI.resetPassword(passwordResetUser.value.id)
    passwordResetResult.value = res.data
    message.value = 'Password reset successful. Temporary password sent to user.'
    messageSuccess.value = true
    setTimeout(() => {
      showPasswordResetModal.value = false
      passwordResetUser.value = null
      passwordResetResult.value = null
    }, 3000)
  } catch (e) {
    message.value = 'Failed to reset password: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    resettingPassword.value = false
  }
}

const viewUserSecurity = async (user) => {
  // Navigate to user's security settings or show in modal
  // For now, just show a message
  message.value = 'Security settings view - feature coming soon'
  messageSuccess.value = false
  selectedUser.value = null
}

const viewUserProfileRequests = async (user) => {
  // Navigate to profile update requests
  message.value = 'Profile update requests - feature coming soon'
  messageSuccess.value = false
  selectedUser.value = null
}

const createUser = async () => {
  creatingUser.value = true
  try {
    await adminManagementAPI.createUser(userForm.value)
    message.value = 'User created successfully'
    messageSuccess.value = true
    closeCreateModal()
    await loadUsers()
  } catch (e) {
    message.value = 'Failed to create user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    creatingUser.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  userForm.value = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'client',
    phone_number: '',
    password: '',
    is_active: true
  }
}

const getUserInitials = (user) => {
  const name = user.full_name || user.username || user.email || 'U'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getRoleBadgeClass = (role) => {
  const classes = {
    client: 'bg-blue-100 text-blue-800',
    writer: 'bg-green-100 text-green-800',
    editor: 'bg-purple-100 text-purple-800',
    support: 'bg-yellow-100 text-yellow-800',
    admin: 'bg-red-100 text-red-800',
    superadmin: 'bg-indigo-100 text-indigo-800',
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

// Close actions menu when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    actionsMenuOpen.value = null
  }
}

onMounted(() => {
  loadUsers()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  if (searchTimeout) clearTimeout(searchTimeout)
})
</script>


