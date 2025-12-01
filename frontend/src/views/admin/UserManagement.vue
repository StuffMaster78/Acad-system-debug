<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
        <p class="mt-2 text-gray-600">Manage all users (writers, editors, support, clients)</p>
      </div>
      <div class="flex items-center gap-3">
        <router-link
          to="/admin/deletion-requests"
          class="btn btn-secondary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Deletion Requests
        </router-link>
        <button
          @click="showCreateModal = true"
          class="btn btn-primary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create User
        </button>
      </div>
    </div>

    <!-- Enhanced Stats Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-8 gap-2 sm:gap-3">
      <router-link
        to="/admin/deletion-requests"
        class="card p-3 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 hover:shadow-md transition-shadow cursor-pointer"
      >
        <p class="text-xs font-medium text-orange-700 mb-0.5">Deletion Requests</p>
        <p class="text-xl sm:text-2xl font-bold text-orange-900">{{ pendingDeletionCount || 0 }}</p>
        <p class="text-xs text-orange-600 mt-0.5">Click to review</p>
      </router-link>
      <div class="card p-3 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-xs font-medium text-blue-700 mb-0.5">Total Users</p>
        <p class="text-xl sm:text-2xl font-bold text-blue-900">{{ userStats.total_users || 0 }}</p>
        <p class="text-xs text-blue-600 mt-0.5">All roles</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-xs font-medium text-green-700 mb-0.5">Active</p>
        <p class="text-xl sm:text-2xl font-bold text-green-900">{{ userStats.active_users || 0 }}</p>
        <p class="text-xs text-green-600 mt-0.5">{{ userStats.total_users ? ((userStats.active_users / userStats.total_users) * 100).toFixed(1) : 0 }}%</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-xs font-medium text-red-700 mb-0.5">Suspended</p>
        <p class="text-xl sm:text-2xl font-bold text-red-900">{{ userStats.suspended_users || 0 }}</p>
        <p class="text-xs text-red-600 mt-0.5">Attention</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-xs font-medium text-purple-700 mb-0.5">Clients</p>
        <p class="text-xl sm:text-2xl font-bold text-purple-900">{{ userStats.by_role?.client || 0 }}</p>
        <p class="text-xs text-purple-600 mt-0.5">Registered</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-xs font-medium text-indigo-700 mb-0.5">Writers</p>
        <p class="text-xl sm:text-2xl font-bold text-indigo-900">{{ userStats.by_role?.writer || 0 }}</p>
        <p class="text-xs text-indigo-600 mt-0.5">Active</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-xs font-medium text-yellow-700 mb-0.5">Probation</p>
        <p class="text-xl sm:text-2xl font-bold text-yellow-900">{{ userStats.on_probation || 0 }}</p>
        <p class="text-xs text-yellow-600 mt-0.5">Review</p>
      </div>
      <div class="card p-3 bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200">
        <p class="text-xs font-medium text-gray-700 mb-0.5">Blacklisted</p>
        <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ userStats.blacklisted_users || 0 }}</p>
        <p class="text-xs text-gray-600 mt-0.5">Banned</p>
      </div>
    </div>

    <!-- Bulk Actions Bar -->
    <div v-if="selectedUsers.length > 0" class="card p-2 sm:p-3 bg-blue-50 border border-blue-200">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <div class="flex flex-wrap items-center gap-2">
          <span class="font-medium text-blue-900 text-xs sm:text-sm">{{ selectedUsers.length }} selected</span>
          <button @click="bulkSuspend" class="px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700 whitespace-nowrap">Suspend</button>
          <button @click="bulkActivate" class="px-2 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 whitespace-nowrap">Activate</button>
          <button @click="bulkExport" class="px-2 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700 whitespace-nowrap">Export</button>
        </div>
        <button @click="selectedUsers = []" class="text-blue-600 hover:text-blue-800 text-xs sm:text-sm whitespace-nowrap">Clear</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-3">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-3">
        <div>
          <label class="block text-xs font-medium mb-0.5">Role</label>
          <select v-model="filters.role" @change="loadUsers" class="w-full border rounded px-2 py-1.5 text-xs">
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
          <label class="block text-xs font-medium mb-0.5">Status</label>
          <select v-model="filters.status" @change="loadUsers" class="w-full border rounded px-2 py-1.5 text-xs">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="blacklisted">Blacklisted</option>
            <option value="probation">On Probation</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium mb-0.5">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Name, email..."
            class="w-full border rounded px-2 py-1.5 text-xs"
          />
        </div>
        <div>
          <label class="block text-xs font-medium mb-0.5">Website</label>
          <select v-model="filters.website" @change="loadUsers" class="w-full border rounded px-2 py-1.5 text-xs">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full text-xs py-1.5">Reset</button>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                  <input type="checkbox" @change="toggleSelectAll" :checked="selectedUsers.length === users.length && users.length > 0" class="rounded" />
                </th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">User</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Role</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Website</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Status</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Last Login</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Joined</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase whitespace-nowrap">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" :class="['hover:bg-gray-50', selectedUsers.includes(user.id) ? 'bg-blue-50' : '']">
              <td class="px-3 py-2 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="user.id" 
                  v-model="selectedUsers"
                  class="rounded"
                />
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-xs mr-2">
                    {{ getUserInitials(user) }}
                  </div>
                  <div class="min-w-0">
                    <div class="font-medium text-gray-900 text-xs truncate">{{ user.full_name || user.username }}</div>
                    <div class="text-xs text-gray-500 truncate">{{ user.email }}</div>
                    <div v-if="user.phone_number" class="text-xs text-gray-400 truncate">{{ user.phone_number }}</div>
                  </div>
                </div>
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span v-if="user.role || user.role_display" :class="getRoleBadgeClass(user.role)" class="px-2 py-0.5 rounded-full text-xs font-medium inline-block">
                  {{ user.role_display || user.role || 'N/A' }}
                </span>
                <span v-else class="text-xs text-gray-400">—</span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <div v-if="user.website && (user.website.name || user.website.domain)" class="text-xs">
                  <div v-if="user.website.name" class="font-medium text-gray-900 truncate max-w-[120px]">{{ user.website.name }}</div>
                  <div v-if="user.website.domain" class="text-xs text-gray-500 truncate max-w-[120px]">{{ user.website.domain }}</div>
                </div>
                <span v-else class="text-xs text-gray-400">—</span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <span v-if="user.is_blacklisted" class="px-1.5 py-0.5 rounded text-xs bg-black text-white font-medium">Blacklisted</span>
                <span v-else-if="user.is_suspended" class="px-1.5 py-0.5 rounded text-xs bg-red-100 text-red-800 font-medium">Suspended</span>
                <span v-else-if="user.is_on_probation" class="px-1.5 py-0.5 rounded text-xs bg-yellow-100 text-yellow-800 font-medium">Probation</span>
                <span v-else-if="user.is_active" class="px-1.5 py-0.5 rounded text-xs bg-green-100 text-green-800 font-medium">Active</span>
                <span v-else class="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-800 font-medium">Inactive</span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                <div v-if="user.last_login" class="flex items-center">
                  <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></span>
                  <span class="truncate max-w-[100px]">{{ formatDate(user.last_login) }}</span>
                </div>
                <span v-else class="text-gray-400">Never</span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-500">
                <span v-if="user.date_joined" class="truncate max-w-[100px] inline-block">{{ formatDate(user.date_joined) }}</span>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-3 py-2 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <button @click="viewUserDetail(user)" class="text-blue-600 hover:text-blue-800 hover:underline text-sm" title="View Profile">👁️</button>
                  <button @click="editUser(user)" class="text-green-600 hover:text-green-800 hover:underline text-sm" title="Edit">✏️</button>
                  <button
                    v-if="canImpersonateUser(user)"
                    @click="impersonateUser(user)"
                    class="text-purple-600 hover:text-purple-800 hover:underline font-bold"
                    title="Impersonate User"
                    style="font-size: 1.1em; min-width: 24px; display: inline-block;"
                  >
                    🎭
                  </button>
                  <div class="relative">
                    <button @click="toggleActionsMenu(user.id)" class="text-gray-600 hover:text-gray-900 text-sm font-bold" title="More Actions">⋯</button>
                    <div v-if="actionsMenuOpen === user.id" class="absolute right-0 mt-1 w-56 bg-white rounded-md shadow-lg z-50 border max-h-[400px] overflow-y-auto">
                      <div class="py-1">
                        <!-- Status Actions -->
                        <div class="px-2 py-1 text-xs font-semibold text-gray-500 uppercase border-b bg-gray-50 sticky top-0">Status</div>
                        <button @click="suspendUserAction(user)" v-if="!user.is_suspended && user.role !== 'superadmin'" class="block w-full text-left px-3 py-1.5 text-xs text-red-600 hover:bg-gray-100">Suspend</button>
                        <button @click="unsuspendUserAction(user)" v-else-if="user.is_suspended" class="block w-full text-left px-3 py-1.5 text-xs text-green-600 hover:bg-gray-100">Unsuspend</button>
                        <button @click="blacklistUserAction(user)" v-if="!user.is_blacklisted && user.role !== 'superadmin' && user.role !== 'admin' && isSuperAdmin" class="block w-full text-left px-3 py-1.5 text-xs text-black hover:bg-gray-100">Blacklist</button>
                        <button @click="unblacklistUserAction(user)" v-else-if="user.is_blacklisted && isSuperAdmin" class="block w-full text-left px-3 py-1.5 text-xs text-green-600 hover:bg-gray-100">Unblacklist</button>
                        <button @click="probationUserAction(user)" v-if="!user.is_on_probation && user.role !== 'admin'" class="block w-full text-left px-3 py-1.5 text-xs text-yellow-600 hover:bg-gray-100">Place on Probation</button>
                        <button @click="removeProbationAction(user)" v-else-if="user.is_on_probation" class="block w-full text-left px-3 py-1.5 text-xs text-green-600 hover:bg-gray-100">Remove Probation</button>
                        <button @click="activateUserAction(user)" v-if="!user.is_active" class="block w-full text-left px-3 py-1.5 text-xs text-green-600 hover:bg-gray-100">Activate</button>
                        <button @click="deactivateUserAction(user)" v-else-if="user.is_active && user.role !== 'superadmin'" class="block w-full text-left px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100">Deactivate</button>
                        
                        <!-- Account Actions -->
                        <div class="px-2 py-1 text-xs font-semibold text-gray-500 uppercase border-b mt-1 bg-gray-50 sticky top-0">Account</div>
                        <button @click="resetPasswordAction(user)" class="block w-full text-left px-3 py-1.5 text-xs text-blue-600 hover:bg-gray-100">Reset Password</button>
                        <button
                          v-if="canImpersonateUser(user)"
                          @click="impersonateUser(user)"
                          class="block w-full text-left px-3 py-1.5 text-xs text-purple-600 hover:bg-gray-100"
                        >
                          Impersonate
                        </button>
                        
                        <!-- Admin Actions (Superadmin only) -->
                        <template v-if="isSuperAdmin">
                          <div class="px-2 py-1 text-xs font-semibold text-gray-500 uppercase border-b mt-1 bg-gray-50 sticky top-0">Admin</div>
                          <button @click="changeRoleAction(user)" v-if="user.role !== 'superadmin'" class="block w-full text-left px-3 py-1.5 text-xs text-purple-600 hover:bg-gray-100">Change Role</button>
                          <button @click="promoteToAdminAction(user)" v-if="!['admin', 'superadmin'].includes(user.role)" class="block w-full text-left px-3 py-1.5 text-xs text-indigo-600 hover:bg-gray-100">Promote to Admin</button>
                          <button @click="deleteUserAction(user)" v-if="user.role !== 'superadmin'" class="block w-full text-left px-3 py-1.5 text-xs text-red-600 hover:bg-gray-100">Delete User</button>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
        
        <div v-if="!users.length" class="text-center py-12 text-gray-500 text-sm">
          No users found.
        </div>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div v-if="showCreateModal || editingUser" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingUser ? 'Edit User' : 'Create User' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveUser" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Username *</label>
                <input v-model="userForm.username" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Email *</label>
                <input v-model="userForm.email" type="email" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">First Name</label>
                <input v-model="userForm.first_name" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Last Name</label>
                <input v-model="userForm.last_name" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Role *</label>
                <select v-model="userForm.role" required class="w-full border rounded px-3 py-2">
                  <option value="client">Client</option>
                  <option value="writer">Writer</option>
                  <option value="editor">Editor</option>
                  <option value="support">Support</option>
                  <option v-if="authStore.isSuperAdmin" value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Phone</label>
                <input v-model="userForm.phone_number" type="tel" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Website</label>
                <select v-model="userForm.website" class="w-full border rounded px-3 py-2">
                  <option :value="null">No Website</option>
                  <option v-for="site in websites" :key="site.id" :value="site.id">
                    {{ formatWebsiteName(site) }}
                  </option>
                </select>
              </div>
              <div v-if="!editingUser">
                <label class="block text-sm font-medium mb-1">Password *</label>
                <input v-model="userForm.password" type="password" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Active</label>
                <input v-model="userForm.is_active" type="checkbox" class="mt-2" />
              </div>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingUser ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Action Modals -->
    <div v-if="showActionModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-md w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">{{ actionModalTitle }}</h3>
        <form @submit.prevent="confirmAction" class="space-y-4">
          <div v-if="currentAction === 'suspend' || currentAction === 'probation' || currentAction === 'blacklist'">
            <label class="block text-sm font-medium mb-1">Reason</label>
            <textarea v-model="actionData.reason" rows="3" class="w-full border rounded px-3 py-2" required></textarea>
          </div>
          <div v-if="currentAction === 'suspend' || currentAction === 'probation'">
            <label class="block text-sm font-medium mb-1">Duration (days)</label>
            <input v-model.number="actionData.duration_days" type="number" min="1" class="w-full border rounded px-3 py-2" />
          </div>
          <div v-if="currentAction === 'change_role'">
            <label class="block text-sm font-medium mb-1">New Role</label>
            <select v-model="actionData.role" class="w-full border rounded px-3 py-2" required>
              <option value="client">Client</option>
              <option value="writer">Writer</option>
              <option value="editor">Editor</option>
              <option value="support">Support</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeActionModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Processing...' : 'Confirm' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Detail Modal -->
    <div v-if="viewingUser" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-4">
              <div class="h-16 w-16 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-bold text-2xl">
                {{ getUserInitials(viewingUser) }}
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">{{ viewingUser.full_name || viewingUser.username }}</h2>
                <p class="text-gray-500">{{ viewingUser.email }}</p>
              </div>
            </div>
            <button @click="closeUserDetail" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <!-- Basic Info -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">Basic Information</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Username:</span>
                  <span class="ml-2 text-gray-900">{{ viewingUser.username }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Email:</span>
                  <span class="ml-2 text-gray-900">{{ viewingUser.email }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Phone:</span>
                  <span class="ml-2 text-gray-900">{{ viewingUser.phone_number || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Role:</span>
                  <span :class="getRoleBadgeClass(viewingUser.role)" class="ml-2 px-2 py-1 rounded-full text-xs font-medium">
                    {{ viewingUser.role_display || viewingUser.role }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Website:</span>
                  <span class="ml-2 text-gray-900">{{ viewingUser.website?.name || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Status & Dates -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">Status & Activity</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Active:</span>
                  <span :class="viewingUser.is_active ? 'text-green-600' : 'text-red-600'" class="ml-2 font-medium">
                    {{ viewingUser.is_active ? 'Yes' : 'No' }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Last Login:</span>
                  <span class="ml-2 text-gray-900">{{ viewingUser.last_login ? formatDateTime(viewingUser.last_login) : 'Never' }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Joined:</span>
                  <span class="ml-2 text-gray-900">{{ formatDateTime(viewingUser.date_joined) }}</span>
                </div>
                <div v-if="viewingUser.is_suspended">
                  <span class="text-sm font-medium text-red-600">Suspended:</span>
                  <span class="ml-2 text-red-600">{{ viewingUser.suspension_reason || 'No reason provided' }}</span>
                  <div v-if="viewingUser.suspension_end_date" class="text-xs text-gray-500 mt-1">
                    Until: {{ formatDateTime(viewingUser.suspension_end_date) }}
                  </div>
                </div>
                <div v-if="viewingUser.is_on_probation">
                  <span class="text-sm font-medium text-yellow-600">On Probation:</span>
                  <span class="ml-2 text-yellow-600">{{ viewingUser.probation_reason || 'No reason provided' }}</span>
                </div>
                <div v-if="viewingUser.is_blacklisted">
                  <span class="text-sm font-medium text-red-800">Blacklisted:</span>
                  <span class="ml-2 text-red-800">Permanently banned</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Profile Information -->
          <div v-if="viewingUser.writer_profile || viewingUser.client_profile" class="mb-6">
            <h3 class="text-lg font-semibold text-gray-900 border-b pb-2 mb-4">Profile Information</h3>
            <div v-if="viewingUser.writer_profile" class="bg-indigo-50 p-4 rounded-lg">
              <h4 class="font-medium text-indigo-900 mb-2">Writer Profile</h4>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div><span class="text-gray-600">Level:</span> <span class="font-medium">{{ viewingUser.writer_profile.level || 'N/A' }}</span></div>
                <div><span class="text-gray-600">Specialization:</span> <span class="font-medium">{{ viewingUser.writer_profile.specialization || 'N/A' }}</span></div>
              </div>
            </div>
            <div v-if="viewingUser.client_profile" class="bg-purple-50 p-4 rounded-lg mt-2">
              <h4 class="font-medium text-purple-900 mb-2">Client Profile</h4>
              <div class="text-sm">
                <div><span class="text-gray-600">Registration ID:</span> <span class="font-medium">{{ viewingUser.client_profile.registration_id || 'N/A' }}</span></div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button @click="editUser(viewingUser); closeUserDetail()" class="btn btn-primary">Edit User</button>
            <button @click="viewUserWallet(viewingUser)" v-if="viewingUser.role === 'client'" class="btn btn-secondary">View Wallet</button>
            <button @click="viewUserOrders(viewingUser)" class="btn btn-secondary">View Orders</button>
            <button @click="viewUserActivity(viewingUser)" class="btn btn-secondary">Activity Log</button>
            <button
              v-if="canImpersonateUser(viewingUser)"
              @click="impersonateUser(viewingUser)"
              class="btn btn-secondary"
            >
              Impersonate
            </button>
            <button
              v-if="authStore.isImpersonating"
              @click="endImpersonation"
              class="btn btn-secondary"
            >
              End Impersonation
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import apiClient from '@/api/client'
import usersAPI from '@/api/users'
import { formatWebsiteName } from '@/utils/formatDisplay'

const route = useRoute()
const authStore = useAuthStore()

// Computed properties for role checks
const isSuperAdmin = computed(() => {
  const user = authStore.user
  return user && user.role === 'superadmin'
})

const isAdmin = computed(() => {
  const user = authStore.user
  return user && ['admin', 'superadmin'].includes(user.role)
})

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingUser = ref(null)
const viewingUser = ref(null)
const actionsMenuOpen = ref(null)
const selectedUsers = ref([])

const filters = ref({
  role: '',
  status: '',
  search: '',
  website: '',
})

const userStats = ref({
  total_users: 0,
  by_role: {},
  active_users: 0,
  suspended_users: 0,
  blacklisted_users: 0,
  on_probation: 0,
})

const pendingDeletionCount = ref(0)

const showActionModal = ref(false)
const currentAction = ref('')
const currentUser = ref(null)
const actionModalTitle = ref('')
const actionData = ref({ reason: '', duration_days: 30, role: '' })
const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadUsers()
  }, 500)
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.role) params.role = filters.value.role
    if (filters.value.status === 'suspended') params.is_suspended = 'true'
    if (filters.value.status === 'blacklisted') params.is_blacklisted = 'true'
    if (filters.value.status === 'probation') params.is_on_probation = 'true'
    if (filters.value.status === 'active') {
      params.is_active = 'true'
      params.is_suspended = 'false'
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    
    const res = await adminManagementAPI.listUsers(params)
    
    // Debug: Log the raw response structure
    console.log('Raw API Response:', {
      hasData: !!res.data,
      dataType: typeof res.data,
      isArray: Array.isArray(res.data),
      hasResults: !!res.data?.results,
      resultsType: typeof res.data?.results,
      resultsIsArray: Array.isArray(res.data?.results),
      firstItem: res.data?.results?.[0] || res.data?.[0] || null
    })
    
    const userList = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    
    // Debug: Log first user to see what we're getting
    if (userList.length > 0) {
      console.log('Sample user from API (raw):', JSON.stringify(userList[0], null, 2))
      console.log('Sample user role:', userList[0].role)
      console.log('Sample user website:', userList[0].website)
    }
    
    // Ensure all fields are properly mapped from backend
    users.value = userList.map(user => {
      // Check what fields are actually present
      const hasRole = 'role' in user && user.role !== null && user.role !== undefined
      const hasWebsite = 'website' in user && user.website !== null && user.website !== undefined
      
      if (!hasRole) {
        console.warn('User missing role field in raw data:', user.id, user.username, Object.keys(user))
      }
      if (!hasWebsite) {
        console.warn('User missing website field in raw data:', user.id, user.username)
      }
      
      // Preserve all original data, explicitly set fields
      const mappedUser = {
        ...user,
        // Ensure role is present - use actual value from user object
        role: hasRole ? user.role : (user.role || null),
        role_display: user.role_display || (user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : null),
        // Ensure website is properly formatted (preserve object structure)
        website: hasWebsite ? (typeof user.website === 'object' ? user.website : null) : (user.website || null),
        // Ensure phone_number is present
        phone_number: user.phone_number || null,
        // Ensure status fields are booleans
        is_active: user.is_active !== undefined ? Boolean(user.is_active) : true,
        is_suspended: user.is_suspended !== undefined ? Boolean(user.is_suspended) : false,
        is_blacklisted: user.is_blacklisted !== undefined ? Boolean(user.is_blacklisted) : false,
        is_on_probation: user.is_on_probation !== undefined ? Boolean(user.is_on_probation) : false,
        // Ensure dates are present (preserve as strings from backend)
        date_joined: user.date_joined || null,
        last_login: user.last_login || null,
      }
      
      // Final check after mapping
      if (!mappedUser.role && !mappedUser.role_display) {
        console.error('User STILL missing role after mapping:', mappedUser.id, mappedUser.username, 'Available keys:', Object.keys(mappedUser))
      }
      if (!mappedUser.website) {
        console.error('User STILL missing website after mapping:', mappedUser.id, mappedUser.username)
      }
      
      return mappedUser
    })
  } catch (e) {
    message.value = 'Failed to load users: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await adminManagementAPI.getUserStats()
    userStats.value = res.data
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const loadPendingDeletionCount = async () => {
  try {
    const res = await usersAPI.getDeletionRequests('pending')
    pendingDeletionCount.value = res.data?.count || 0
  } catch (e) {
    console.error('Failed to load pending deletion count:', e)
    // Don't show error to user, just set to 0
    pendingDeletionCount.value = 0
  }
}

const websites = ref([])
const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  role: 'client',
  phone_number: '',
  website: null,
  password: '',
  is_active: true,
})

const saveUser = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingUser.value) {
      const data = { ...userForm.value }
      delete data.password
      await adminManagementAPI.patchUser(editingUser.value.id, data)
      message.value = 'User updated successfully'
    } else {
      await adminManagementAPI.createUser(userForm.value)
      message.value = 'User created successfully'
    }
    messageSuccess.value = true
    closeModal()
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to save user: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const viewUser = (user) => {
  editingUser.value = user
  showCreateModal.value = true
}

const viewUserDetail = async (user) => {
  try {
    const res = await adminManagementAPI.getUser(user.id)
    viewingUser.value = res.data
  } catch (e) {
    message.value = 'Failed to load user details: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeUserDetail = () => {
  viewingUser.value = null
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

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const toggleSelectAll = (event) => {
  if (event.target.checked) {
    selectedUsers.value = users.value.map(u => u.id)
  } else {
    selectedUsers.value = []
  }
}

const bulkSuspend = async () => {
  if (!confirm(`Suspend ${selectedUsers.value.length} selected user(s)?`)) return
  try {
    const reason = prompt('Enter suspension reason:', 'Bulk suspension')
    if (!reason) return
    
    const durationDays = prompt('Enter duration in days (default: 30):', '30')
    const duration = durationDays ? parseInt(durationDays) : 30
    
    const res = await adminManagementAPI.bulkSuspend(selectedUsers.value, reason, duration)
    message.value = res.data.message || `Suspended ${res.data.suspended_count} user(s)`
    messageSuccess.value = true
    selectedUsers.value = []
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to suspend users: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const bulkActivate = async () => {
  if (!confirm(`Activate ${selectedUsers.value.length} selected user(s)?`)) return
  try {
    const res = await adminManagementAPI.bulkActivate(selectedUsers.value)
    message.value = res.data.message || `Activated ${res.data.activated_count} user(s)`
    messageSuccess.value = true
    selectedUsers.value = []
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to activate users: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const bulkExport = () => {
  const selected = users.value.filter(u => selectedUsers.value.includes(u.id))
  const csv = [
    ['Name', 'Email', 'Role', 'Website', 'Status', 'Joined', 'Last Login'].join(','),
    ...selected.map(u => [
      u.full_name || u.username,
      u.email,
      u.role,
      u.website?.name || 'N/A',
      u.is_active ? 'Active' : 'Inactive',
      u.date_joined,
      u.last_login || 'Never'
    ].join(','))
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
  
  message.value = `Exported ${selectedUsers.value.length} users`
  messageSuccess.value = true
}

const viewUserWallet = (user) => {
  if (user.role === 'client') {
    window.location.href = `/admin/wallets?user=${user.id}`
  }
}

const viewUserOrders = (user) => {
  window.location.href = `/orders?user=${user.id}`
}

const viewUserActivity = (user) => {
  window.location.href = `/activity?user=${user.id}`
}

const editUser = (user) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    email: user.email,
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    role: user.role,
    phone_number: user.phone_number || '',
    website: user.website?.id || null,
    password: '',
    is_active: user.is_active,
  }
  showCreateModal.value = true
}

const closeModal = () => {
  showCreateModal.value = false
  editingUser.value = null
  userForm.value = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'client',
    phone_number: '',
    website: null,
    password: '',
    is_active: true,
  }
}

const toggleActionsMenu = (userId) => {
  actionsMenuOpen.value = actionsMenuOpen.value === userId ? null : userId
}

const suspendUserAction = (user) => {
  currentAction.value = 'suspend'
  currentUser.value = user
  actionModalTitle.value = `Suspend ${user.username}`
  actionData.value = { reason: '', duration_days: 30 }
  showActionModal.value = true
  actionsMenuOpen.value = null
}

const unsuspendUserAction = async (user) => {
  if (!confirm(`Unsuspend ${user.username}?`)) return
  try {
    await adminManagementAPI.unsuspendUser(user.id)
    message.value = `User ${user.username} unsuspended`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to unsuspend user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const probationUserAction = (user) => {
  currentAction.value = 'probation'
  currentUser.value = user
  actionModalTitle.value = `Place ${user.username} on Probation`
  actionData.value = { reason: '', duration_days: 30 }
  showActionModal.value = true
  actionsMenuOpen.value = null
}

const removeProbationAction = async (user) => {
  if (!confirm(`Remove ${user.username} from probation?`)) return
  try {
    await adminManagementAPI.removeFromProbation(user.id)
    message.value = `User ${user.username} removed from probation`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to remove probation: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const resetPasswordAction = async (user) => {
  if (!confirm(`Reset password for ${user.username}?`)) return
  try {
    const res = await adminManagementAPI.resetPassword(user.id)
    message.value = res.data.message || 'Password reset successfully'
    messageSuccess.value = true
  } catch (e) {
    message.value = 'Failed to reset password: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const changeRoleAction = (user) => {
  currentAction.value = 'change_role'
  currentUser.value = user
  actionModalTitle.value = `Change Role for ${user.username}`
  actionData.value = { role: user.role }
  showActionModal.value = true
  actionsMenuOpen.value = null
}

const promoteToAdminAction = async (user) => {
  if (!confirm(`Promote ${user.username} to admin?`)) return
  try {
    await adminManagementAPI.promoteToAdmin(user.id)
    message.value = `User ${user.username} promoted to admin`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to promote user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const deleteUserAction = async (user) => {
  if (!confirm(`Delete ${user.username}? This action cannot be undone.`)) return
  try {
    await adminManagementAPI.deleteUser(user.id)
    message.value = `User ${user.username} deleted`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to delete user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const blacklistUserAction = (user) => {
  currentAction.value = 'blacklist'
  currentUser.value = user
  actionModalTitle.value = `Blacklist ${user.username}`
  actionData.value = { reason: '' }
  showActionModal.value = true
  actionsMenuOpen.value = null
}

const unblacklistUserAction = async (user) => {
  if (!confirm(`Unblacklist ${user.username}?`)) return
  try {
    // Note: Backend might need an unblacklist endpoint, for now we'll use a workaround
    await adminManagementAPI.patchUser(user.id, { is_blacklisted: false })
    message.value = `User ${user.username} unblacklisted`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to unblacklist user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const activateUserAction = async (user) => {
  if (!confirm(`Activate ${user.username}?`)) return
  try {
    await adminManagementAPI.patchUser(user.id, { is_active: true })
    message.value = `User ${user.username} activated`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to activate user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const deactivateUserAction = async (user) => {
  if (!confirm(`Deactivate ${user.username}?`)) return
  try {
    await adminManagementAPI.patchUser(user.id, { is_active: false })
    message.value = `User ${user.username} deactivated`
    messageSuccess.value = true
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to deactivate user: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const confirmAction = async () => {
  saving.value = true
  message.value = ''
  try {
    if (currentAction.value === 'suspend') {
      await adminManagementAPI.suspendUser(
        currentUser.value.id,
        actionData.value.reason,
        actionData.value.duration_days
      )
      message.value = `User ${currentUser.value.username} suspended`
    } else if (currentAction.value === 'probation') {
      await adminManagementAPI.placeOnProbation(
        currentUser.value.id,
        actionData.value.reason,
        actionData.value.duration_days
      )
      message.value = `User ${currentUser.value.username} placed on probation`
    } else if (currentAction.value === 'blacklist') {
      await adminManagementAPI.blacklistUser(
        currentUser.value.id,
        actionData.value.reason
      )
      message.value = `User ${currentUser.value.username} blacklisted`
    } else if (currentAction.value === 'change_role') {
      await adminManagementAPI.changeRole(currentUser.value.id, actionData.value.role)
      message.value = `User ${currentUser.value.username} role changed to ${actionData.value.role}`
    }
    messageSuccess.value = true
    closeActionModal()
    await loadUsers()
    await loadStats()
  } catch (e) {
    message.value = 'Failed to perform action: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeActionModal = () => {
  showActionModal.value = false
  currentAction.value = ''
  currentUser.value = null
  actionData.value = { reason: '', duration_days: 30, role: '' }
}

const resetFilters = () => {
  filters.value = { role: '', status: '', search: '', website: '' }
  selectedUsers.value = []
  loadUsers()
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

const canImpersonateUser = (user) => {
  // Early return if user is missing
  if (!user) {
    console.debug('canImpersonateUser: No user provided')
    return false
  }
  
  // Get role - check both role and role_display fields
  const userRole = user.role || null
  if (!userRole) {
    console.debug('canImpersonateUser: User has no role', { userId: user.id, username: user.username })
    return false
  }
  
  // Check if current user is admin or superadmin
  const currentUser = authStore.user
  if (!currentUser) {
    console.debug('canImpersonateUser: No current user in authStore')
    return false
  }
  
  if (!currentUser.role) {
    console.debug('canImpersonateUser: Current user has no role', { currentUser })
    return false
  }
  
  const isAdmin = ['admin', 'superadmin'].includes(currentUser.role)
  if (!isAdmin) {
    console.debug('canImpersonateUser: Current user is not admin/superadmin', { currentUserRole: currentUser.role })
    return false
  }
  
  // Check if target user is client or writer (can impersonate these roles)
  const canImpersonate = ['client', 'writer'].includes(userRole)
  
  if (!canImpersonate) {
    console.debug('canImpersonateUser: Target user role cannot be impersonated', { userRole })
  }
  
  return canImpersonate
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/')
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const impersonateUser = async (user) => {
  try {
    message.value = ''
    
    // Import usersAPI to generate token
    const usersAPI = (await import('@/api/users')).default
    
    // Generate impersonation token
    const tokenResponse = await usersAPI.generateImpersonationToken(user.id)
    
    if (tokenResponse.data?.error) {
      message.value = tokenResponse.data.error || 'Failed to generate impersonation token'
      messageSuccess.value = false
      return
    }
    
    const token = tokenResponse.data?.token
    
    if (!token) {
      message.value = 'Failed to generate impersonation token'
      messageSuccess.value = false
      return
    }
    
    // Store admin token temporarily in localStorage for the new tab to use
    // This will be cleared after impersonation starts
    // Using localStorage instead of sessionStorage so it's accessible across tabs
    const adminToken = authStore.accessToken
    if (adminToken) {
      // Store with a timestamp to auto-expire after 5 minutes
      const tokenData = {
        token: adminToken,
        expiresAt: Date.now() + (5 * 60 * 1000) // 5 minutes
      }
      localStorage.setItem('_impersonation_admin_token', JSON.stringify(tokenData))
    }
    
    // Open new tab with impersonation token
    const baseUrl = window.location.origin
    const impersonateUrl = `${baseUrl}/impersonate?token=${encodeURIComponent(token)}`
    window.open(impersonateUrl, '_blank', 'noopener,noreferrer')
    
    message.value = `Opening impersonation session for ${user.username || user.email} in a new tab...`
    messageSuccess.value = true
    actionsMenuOpen.value = null
    viewingUser.value = null
  } catch (e) {
    console.error('Impersonation error:', e)
    message.value = e?.response?.data?.error || 
                    e?.response?.data?.detail || 
                    e?.message || 
                    'Failed to impersonate user'
    messageSuccess.value = false
  }
}

const endImpersonation = async () => {
  try {
    message.value = ''
    const res = await authStore.endImpersonation()
    if (res?.success === false) {
      message.value = res.error || 'Failed to end impersonation'
      messageSuccess.value = false
    } else {
      message.value = 'Impersonation ended. Admin session restored.'
      messageSuccess.value = true
    }
  } catch (e) {
    message.value = e?.message || 'Failed to end impersonation'
    messageSuccess.value = false
  }
}

// Watch for route query changes (role filter from navigation)
watch(() => route.query.role, (newRole) => {
  if (newRole && newRole !== filters.value.role) {
    filters.value.role = newRole
    loadUsers()
  }
}, { immediate: true })

// Close actions menu on outside click
onMounted(async () => {
  // Set role filter from URL query parameter if present
  if (route.query.role) {
    filters.value.role = route.query.role
  }
  await Promise.all([loadUsers(), loadStats(), loadWebsites(), loadPendingDeletionCount()])
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      actionsMenuOpen.value = null
    }
  })
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

