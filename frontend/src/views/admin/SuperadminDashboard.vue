<template>
  <div class="superadmin-dashboard space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Superadmin Dashboard</h1>
        <p class="mt-2 text-gray-600">System-wide management and multi-tenant operations</p>
      </div>
      <button @click="refreshDashboard" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- System Stats -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <p class="text-sm text-blue-700 mb-1">Total Users</p>
              <p class="text-3xl font-bold text-blue-900">{{ dashboardStats.total_users || 0 }}</p>
            </div>
            <div class="bg-green-50 rounded-lg p-6 border border-green-200">
              <p class="text-sm text-green-700 mb-1">Total Orders</p>
              <p class="text-3xl font-bold text-green-900">{{ dashboardStats.total_orders || 0 }}</p>
            </div>
            <div class="bg-purple-50 rounded-lg p-6 border border-purple-200">
              <p class="text-sm text-purple-700 mb-1">Total Revenue</p>
              <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(dashboardStats.total_revenue || 0) }}</p>
            </div>
            <div class="bg-orange-50 rounded-lg p-6 border border-orange-200">
              <p class="text-sm text-orange-700 mb-1">Active Tenants</p>
              <p class="text-3xl font-bold text-orange-900">{{ websites.length }}</p>
            </div>
          </div>

          <!-- Additional Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-red-50 rounded-lg p-4 border border-red-200">
              <p class="text-sm text-red-700 mb-1">Suspended Users</p>
              <p class="text-2xl font-bold text-red-900">{{ dashboardStats.suspended_users || 0 }}</p>
            </div>
            <div class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <p class="text-sm text-yellow-700 mb-1">Pending Payouts</p>
              <p class="text-2xl font-bold text-yellow-900">${{ formatCurrency(dashboardStats.pending_payouts || 0) }}</p>
            </div>
            <div class="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
              <p class="text-sm text-indigo-700 mb-1">Total Disputes</p>
              <p class="text-2xl font-bold text-indigo-900">{{ dashboardStats.total_disputes || 0 }}</p>
            </div>
          </div>

          <!-- User Breakdown by Role -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">User Breakdown by Role</h3>
            <div class="grid grid-cols-2 md:grid-cols-6 gap-4">
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Clients</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.total_clients || 0 }}</p>
              </div>
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Writers</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.total_writers || 0 }}</p>
              </div>
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Editors</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.total_editors || 0 }}</p>
              </div>
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Support</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.total_support || 0 }}</p>
              </div>
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Admins</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.total_admins || 0 }}</p>
              </div>
              <div class="text-center p-4 bg-gray-50 rounded">
                <p class="text-sm text-gray-600">Suspended</p>
                <p class="text-2xl font-bold text-gray-900">{{ dashboardStats.suspended_users || 0 }}</p>
              </div>
            </div>
          </div>

          <!-- Recent Activity Logs -->
          <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold mb-4">Recent Superadmin Activity</h3>
            <div v-if="recentLogsLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
            <div v-else-if="recentLogs.length === 0" class="text-center py-8 text-gray-500">
              No recent activity
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="log in recentLogs"
                :key="log.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded"
              >
                <div>
                  <p class="text-sm font-medium">{{ log.action_type }}</p>
                  <p class="text-xs text-gray-600">{{ log.details || '-' }}</p>
                </div>
                <div class="text-right">
                  <p class="text-xs text-gray-600">{{ formatDate(log.timestamp) }}</p>
                  <p class="text-xs text-gray-500">{{ log.superadmin?.username || 'System' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- User Management Tab -->
        <div v-if="activeTab === 'users'" class="space-y-6">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Cross-Tenant User Management</h2>
            <button
              @click="showCreateUserModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Create User
            </button>
          </div>

          <!-- Filters -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              v-model="userFilters.search"
              @input="debouncedLoadUsers"
              type="text"
              placeholder="Search users..."
              class="border rounded px-3 py-2"
            />
            <select
              v-model="userFilters.role"
              @change="loadUsers"
              class="border rounded px-3 py-2"
            >
              <option value="">All Roles</option>
              <option value="client">Client</option>
              <option value="writer">Writer</option>
              <option value="editor">Editor</option>
              <option value="support">Support</option>
              <option value="admin">Admin</option>
              <option value="superadmin">Superadmin</option>
            </select>
            <select
              v-model="userFilters.is_suspended"
              @change="loadUsers"
              class="border rounded px-3 py-2"
            >
              <option value="">All Status</option>
              <option value="false">Active</option>
              <option value="true">Suspended</option>
            </select>
          </div>

          <!-- Users Table -->
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="user in users" :key="user.id">
                  <td class="px-4 py-3 text-sm">{{ user.username }}</td>
                  <td class="px-4 py-3 text-sm">{{ user.email }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 capitalize">{{ user.role }}</span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span
                      class="px-2 py-1 text-xs rounded"
                      :class="user.is_suspended ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
                    >
                      {{ user.is_suspended ? 'Suspended' : 'Active' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">{{ user.website?.name || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex gap-2">
                      <button
                        v-if="user.is_suspended"
                        @click="reactivateUser(user.id)"
                        class="text-green-600 hover:text-green-800 text-xs"
                      >
                        Reactivate
                      </button>
                      <button
                        v-else
                        @click="suspendUser(user.id)"
                        class="text-red-600 hover:text-red-800 text-xs"
                      >
                        Suspend
                      </button>
                      <button
                        @click="openChangeRoleModal(user)"
                        class="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        Change Role
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tenant Management Tab -->
        <div v-if="activeTab === 'tenants'" class="space-y-6">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Tenant/Website Management</h2>
            <button
              @click="showCreateWebsiteModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Create Website
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Domain</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="website in websites" :key="website.id">
                  <td class="px-4 py-3 text-sm font-medium">{{ website.name }}</td>
                  <td class="px-4 py-3 text-sm">{{ website.domain }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span
                      class="px-2 py-1 text-xs rounded"
                      :class="website.is_deleted ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
                    >
                      {{ website.is_deleted ? 'Deleted' : 'Active' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span
                      class="px-2 py-1 text-xs rounded"
                      :class="website.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                    >
                      {{ website.is_active ? 'Yes' : 'No' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex gap-2">
                      <button
                        @click="editWebsite(website)"
                        class="text-blue-600 hover:text-blue-800 text-xs"
                      >
                        Edit
                      </button>
                      <button
                        v-if="!website.is_deleted"
                        @click="softDeleteWebsite(website.id)"
                        class="text-red-600 hover:text-red-800 text-xs"
                      >
                        Delete
                      </button>
                      <button
                        v-else
                        @click="restoreWebsite(website.id)"
                        class="text-green-600 hover:text-green-800 text-xs"
                      >
                        Restore
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Superadmin Profiles Tab -->
        <div v-if="activeTab === 'profiles'" class="space-y-6">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-semibold">Superadmin Profiles</h2>
            <button
              @click="showCreateProfileModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Create Profile
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permissions</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="profile in profiles" :key="profile.id">
                  <td class="px-4 py-3 text-sm">{{ profile.user?.username || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div class="flex flex-wrap gap-1">
                      <span
                        v-for="(value, key) in profile"
                        :key="key"
                        v-if="key.startsWith('can_') && value"
                        class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800"
                      >
                        {{ key.replace('can_', '').replace('_', ' ') }}
                      </span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm">{{ formatDate(profile.created_at) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <button
                      @click="editProfile(profile)"
                      class="text-blue-600 hover:text-blue-800 text-xs mr-2"
                    >
                      Edit
                    </button>
                    <button
                      @click="deleteProfile(profile.id)"
                      class="text-red-600 hover:text-red-800 text-xs"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Activity Logs Tab -->
        <div v-if="activeTab === 'logs'" class="space-y-6">
          <h2 class="text-xl font-semibold">Superadmin Activity Logs</h2>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Superadmin</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="log in logs" :key="log.id">
                  <td class="px-4 py-3 text-sm font-medium">{{ log.action_type }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ log.details || '-' }}</td>
                  <td class="px-4 py-3 text-sm">{{ log.superadmin?.username || 'System' }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(log.timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">Create User</h3>
        <form @submit.prevent="handleCreateUser" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input v-model="userForm.username" type="text" class="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input v-model="userForm.email" type="email" class="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <select v-model="userForm.role" class="w-full border rounded px-3 py-2" required>
              <option value="client">Client</option>
              <option value="writer">Writer</option>
              <option value="editor">Editor</option>
              <option value="support">Support</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
            <input v-model="userForm.phone_number" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-3">
            <button type="submit" :disabled="processing" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {{ processing ? 'Creating...' : 'Create User' }}
            </button>
            <button type="button" @click="showCreateUserModal = false" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Role Modal -->
    <div v-if="showChangeRoleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">Change User Role</h3>
        <form @submit.prevent="handleChangeRole" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">New Role</label>
            <select v-model="roleForm.new_role" class="w-full border rounded px-3 py-2" required>
              <option value="client">Client</option>
              <option value="writer">Writer</option>
              <option value="editor">Editor</option>
              <option value="support">Support</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="flex gap-3">
            <button type="submit" :disabled="processing" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {{ processing ? 'Changing...' : 'Change Role' }}
            </button>
            <button type="button" @click="showChangeRoleModal = null" class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { superadminAPI, websitesAPI } from '@/api'
import { debounce } from '@/utils/debounce'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const activeTab = ref('overview')
const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'users', label: 'User Management' },
  { id: 'tenants', label: 'Tenant Management' },
  { id: 'profiles', label: 'Superadmin Profiles' },
  { id: 'logs', label: 'Activity Logs' },
]

const loading = ref(false)
const dashboardStats = ref({})
const users = ref([])
const websites = ref([])
const profiles = ref([])
const logs = ref([])
const recentLogs = ref([])
const recentLogsLoading = ref(false)

const userFilters = ref({
  search: '',
  role: '',
  is_suspended: '',
})

const showCreateUserModal = ref(false)
const showCreateWebsiteModal = ref(false)
const showCreateProfileModal = ref(false)
const showChangeRoleModal = ref(null)
const processing = ref(false)

const userForm = ref({
  username: '',
  email: '',
  role: 'client',
  phone_number: '',
})

const roleForm = ref({
  user_id: null,
  new_role: '',
})

const loadDashboard = async () => {
  loading.value = true
  try {
    const response = await superadminAPI.getDashboard()
    dashboardStats.value = response.data || {}
  } catch (error) {
    console.error('Error loading dashboard:', error)
    dashboardStats.value = {}
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const params = {}
    if (userFilters.value.search) params.search = userFilters.value.search
    if (userFilters.value.role) params.role = userFilters.value.role
    if (userFilters.value.is_suspended !== '') params.is_suspended = userFilters.value.is_suspended
    
    const response = await superadminAPI.listUsers(params)
    users.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading users:', error)
    users.value = []
  }
}

const debouncedLoadUsers = debounce(loadUsers, 500)

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading websites:', error)
    websites.value = []
  }
}

const loadProfiles = async () => {
  try {
    const response = await superadminAPI.listProfiles()
    profiles.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading profiles:', error)
    profiles.value = []
  }
}

const loadLogs = async () => {
  try {
    const response = await superadminAPI.listLogs({ page_size: 50 })
    logs.value = response.data?.results || response.data || []
    recentLogs.value = logs.value.slice(0, 10)
  } catch (error) {
    console.error('Error loading logs:', error)
    logs.value = []
    recentLogs.value = []
  }
}

const handleCreateUser = async () => {
  processing.value = true
  try {
    await superadminAPI.createUser(userForm.value)
    showSuccess('User created successfully!')
    showCreateUserModal.value = false
    userForm.value = { username: '', email: '', role: 'client', phone_number: '' }
    loadUsers()
    loadDashboard()
  } catch (error) {
    console.error('Error creating user:', error)
    showError('Error creating user: ' + (error.response?.data?.detail || error.message))
  } finally {
    processing.value = false
  }
}

const suspendUser = async (userId) => {
  const user = users.value.find(u => u.id === userId)
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to suspend ${user?.username || user?.email || 'this user'}?`,
    'Suspend User',
    {
      details: 'This action will suspend the user account, preventing them from accessing the system. They will not be able to log in until reactivated.',
      confirmText: 'Suspend User',
      cancelText: 'Cancel',
      icon: '⚠️'
    }
  )
  
  if (!confirmed) return
  
  try {
    await superadminAPI.suspendUser({ user_id: userId, reason: 'Suspended by superadmin' })
    showSuccess('User suspended successfully!')
    loadUsers()
  } catch (error) {
    showError('Error suspending user: ' + (error.response?.data?.detail || error.message))
  }
}

const reactivateUser = async (userId) => {
  try {
    await superadminAPI.reactivateUser({ user_id: userId })
    showSuccess('User reactivated successfully!')
    loadUsers()
  } catch (error) {
    console.error('Error reactivating user:', error)
    showError('Error reactivating user: ' + (error.response?.data?.detail || error.message))
  }
}

const openChangeRoleModal = (user) => {
  showChangeRoleModal.value = user
  roleForm.value = {
    user_id: user.id,
    new_role: user.role,
  }
}

const handleChangeRole = async () => {
  processing.value = true
  try {
    await superadminAPI.changeUserRole(roleForm.value)
    showSuccess('User role changed successfully!')
    showChangeRoleModal.value = null
    roleForm.value = { user_id: null, new_role: '' }
    loadUsers()
  } catch (error) {
    console.error('Error changing role:', error)
    showError('Error changing role: ' + (error.response?.data?.detail || error.message))
  } finally {
    processing.value = false
  }
}

const editWebsite = (website) => {
  // Navigate to website management or open edit modal
  window.location.href = `/websites?edit=${website.id}`
}

const softDeleteWebsite = async (id) => {
  const website = websites.value.find(w => w.id === id)
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to soft delete "${website?.name || website?.domain || 'this website'}"?`,
    'Soft Delete Website',
    {
      details: 'This action will mark the website as deleted (soft delete). The website data will be preserved but hidden from normal operations. It can be restored later if needed.',
      confirmText: 'Delete Website',
      cancelText: 'Cancel',
      icon: '🗑️'
    }
  )
  
  if (!confirmed) return
  
  try {
    await websitesAPI.softDeleteWebsite(id)
    showSuccess('Website deleted successfully!')
    loadWebsites()
  } catch (error) {
    showError('Error deleting website: ' + (error.response?.data?.detail || error.message))
  }
}

const restoreWebsite = async (id) => {
  try {
    await websitesAPI.restoreWebsite(id)
    showSuccess('Website restored successfully!')
    loadWebsites()
  } catch (error) {
    console.error('Error restoring website:', error)
    showError('Error restoring website: ' + (error.response?.data?.detail || error.message))
  }
}

const editProfile = (profile) => {
  // Navigate to profile edit or open modal
  // TODO: Implement profile editing functionality
  showMessage('Profile editing feature coming soon', false)
}

const deleteProfile = async (id) => {
  const profile = superadminProfiles.value.find(p => p.id === id)
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete ${profile?.user?.username || profile?.user?.email || 'this superadmin profile'}?`,
    'Delete Superadmin Profile',
    {
      details: 'This action cannot be undone. The superadmin profile and all associated permissions will be permanently removed.',
      confirmText: 'Delete Profile',
      cancelText: 'Cancel',
      icon: '🗑️'
    }
  )
  
  if (!confirmed) return
  
  try {
    await superadminAPI.deleteProfile(id)
    showSuccess('Profile deleted successfully!')
    loadProfiles()
  } catch (error) {
    console.error('Error deleting profile:', error)
    showError('Error deleting profile: ' + (error.response?.data?.detail || error.message))
  }
}

const refreshDashboard = () => {
  loadDashboard()
  if (activeTab.value === 'users') loadUsers()
  if (activeTab.value === 'tenants') loadWebsites()
  if (activeTab.value === 'profiles') loadProfiles()
  if (activeTab.value === 'logs') loadLogs()
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

import { watch } from 'vue'
watch(activeTab, (newTab) => {
  if (newTab === 'users') {
    loadUsers()
  } else if (newTab === 'tenants') {
    loadWebsites()
  } else if (newTab === 'profiles') {
    loadProfiles()
  } else if (newTab === 'logs') {
    loadLogs()
  }
})

onMounted(() => {
  loadDashboard()
  loadUsers()
  loadWebsites()
  loadProfiles()
  loadLogs()
})
</script>

<style scoped>
.superadmin-dashboard {
  min-height: 100vh;
  background-color: #f9fafb;
}
</style>

