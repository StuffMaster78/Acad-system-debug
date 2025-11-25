<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Users</h1>
      <router-link
        v-if="authStore.isAdmin || authStore.isSuperAdmin"
        to="/admin/users"
        class="px-4 py-2 rounded-lg font-medium transition-colors bg-primary-600 text-white hover:bg-primary-700"
      >
        Full User Management
      </router-link>
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
                  <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-sm mr-3">
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
                <router-link
                  :to="`/admin/users?user=${user.id}`"
                  class="text-primary-600 hover:text-primary-800 hover:underline"
                >
                  Manage
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import usersAPI from '@/api/users'

const authStore = useAuthStore()
const loading = ref(false)
const users = ref([])
const message = ref('')
const messageSuccess = ref(false)

const loadUsers = async () => {
  loading.value = true
  try {
    // For admins/superadmins, use admin management API to get all users
    // For other roles, use regular users API
    if (authStore.isAdmin || authStore.isSuperAdmin) {
      const res = await adminManagementAPI.listUsers({})
      users.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    } else {
      // For non-admin users, they can only see themselves or limited users
      const res = await usersAPI.list({})
      users.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    }
  } catch (e) {
    message.value = 'Failed to load users: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
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

onMounted(() => {
  loadUsers()
})
</script>


