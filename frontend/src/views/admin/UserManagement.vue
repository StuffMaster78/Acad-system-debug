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
    <EnhancedDataTable
      :items="users"
      :columns="usersColumns"
      :loading="loading"
      :searchable="true"
      search-placeholder="Search users by name, email, username..."
      :search-fields="['full_name', 'username', 'email', 'phone_number']"
      :sortable="true"
      :striped="true"
      empty-message="No users found"
      empty-description="Try adjusting your filters or create a new user"
      empty-icon="👤"
    >
      <template #headerActions>
        <div class="flex items-center gap-2">
          <input
            type="checkbox"
            @change="toggleSelectAll"
            :checked="selectedUsers.length === users.length && users.length > 0"
            class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            title="Select All"
          />
          <span v-if="selectedUsers.length > 0" class="text-sm text-gray-600 dark:text-gray-400">
            {{ selectedUsers.length }} selected
          </span>
        </div>
      </template>
      
      <template #cell-select="{ item }">
        <input
          type="checkbox"
          :value="item.id"
          v-model="selectedUsers"
          class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
        />
      </template>
      
      <template #cell-user="{ item }">
        <div class="flex items-center gap-2">
          <div class="shrink-0 h-7 w-7 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold text-xs">
            {{ getUserInitials(item) }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-medium text-gray-900 dark:text-gray-100 text-xs">{{ item.full_name || item.username }}</span>
              <span class="text-gray-400 dark:text-gray-500 text-xs">•</span>
              <span class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px]">{{ item.email }}</span>
              <span v-if="item.phone_number" class="text-xs text-gray-400 dark:text-gray-500 truncate max-w-[120px]" :title="item.phone_number">📞</span>
            </div>
          </div>
        </div>
      </template>
      
      <template #cell-role="{ item }">
        <span v-if="item.role || item.role_display" :class="getRoleBadgeClass(item.role)" class="px-2 py-0.5 rounded-full text-xs font-medium inline-block">
          {{ item.role_display || item.role || 'N/A' }}
        </span>
        <span v-else class="text-xs text-gray-400 dark:text-gray-500">—</span>
      </template>
      
      <template #cell-website="{ item }">
        <div v-if="item.website && (item.website.name || item.website.domain)" class="text-xs">
          <span v-if="item.website.name" class="font-medium text-gray-900 dark:text-gray-100 truncate max-w-[150px]">{{ item.website.name }}</span>
          <span v-else-if="item.website.domain" class="text-gray-500 dark:text-gray-400 truncate max-w-[150px]">{{ item.website.domain }}</span>
        </div>
        <span v-else class="text-xs text-gray-400 dark:text-gray-500">—</span>
      </template>
      
      <template #cell-status="{ item }">
        <span v-if="item.is_blacklisted" class="px-2 py-0.5 rounded-full text-xs font-medium bg-black text-white">Blacklisted</span>
        <span v-else-if="item.is_suspended" class="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">Suspended</span>
        <span v-else-if="item.is_on_probation" class="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300">Probation</span>
        <span v-else-if="item.is_active" class="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">Active</span>
        <span v-else class="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300">Inactive</span>
      </template>
      
      <template #cell-last_login="{ item }">
        <div v-if="item.last_login" class="flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
          <span class="text-xs text-gray-600 dark:text-gray-400">{{ formatDate(item.last_login) }}</span>
        </div>
        <span v-else class="text-xs text-gray-400 dark:text-gray-500">Never</span>
      </template>
      
      <template #cell-actions="{ item }">
        <div class="flex items-center gap-1.5">
          <button
            @click="viewUserDetail(item)"
            class="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 dark:bg-blue-900/20 rounded hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            title="View Profile"
          >
            View
          </button>
          <button
            @click="editUser(item)"
            class="px-2 py-1 text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 rounded hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
            title="Edit User"
          >
            Edit
          </button>
          <button
            v-if="canImpersonateUser(item)"
            @click="impersonateUser(item)"
            class="px-2 py-1 text-xs font-medium text-purple-600 bg-purple-50 dark:bg-purple-900/20 rounded hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
            title="Impersonate User"
          >
            🎭
          </button>
          <div class="relative">
            <button
              @click="toggleActionsMenu(item.id)"
              class="px-2 py-1 text-xs font-medium text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              title="More Actions"
            >
              ⋯
            </button>
            <div
              v-if="actionsMenuOpen === item.id"
              class="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-xl z-20 border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div class="py-1 max-h-[500px] overflow-y-auto">
                <!-- Status Actions -->
                <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase bg-gray-50 dark:bg-gray-700/50 sticky top-0">Status</div>
                <button
                  @click="suspendUserAction(item); actionsMenuOpen = null"
                  v-if="!item.is_suspended && item.role !== 'superadmin'"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
                >
                  <span>⛔</span> Suspend
                </button>
                <button
                  @click="unsuspendUserAction(item); actionsMenuOpen = null"
                  v-else-if="item.is_suspended"
                  class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors flex items-center gap-2"
                >
                  <span>✅</span> Unsuspend
                </button>
                <button
                  @click="blacklistUserAction(item); actionsMenuOpen = null"
                  v-if="!item.is_blacklisted && item.role !== 'superadmin' && item.role !== 'admin' && isSuperAdmin"
                  class="block w-full text-left px-4 py-2 text-sm text-black dark:text-red-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                >
                  <span>🚫</span> Blacklist
                </button>
                <button
                  @click="unblacklistUserAction(item); actionsMenuOpen = null"
                  v-else-if="item.is_blacklisted && isSuperAdmin"
                  class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors flex items-center gap-2"
                >
                  <span>✅</span> Unblacklist
                </button>
                <button
                  @click="probationUserAction(item); actionsMenuOpen = null"
                  v-if="!item.is_on_probation && item.role !== 'admin'"
                  class="block w-full text-left px-4 py-2 text-sm text-yellow-600 dark:text-yellow-400 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-colors flex items-center gap-2"
                >
                  <span>⚠️</span> Place on Probation
                </button>
                <button
                  @click="removeProbationAction(item); actionsMenuOpen = null"
                  v-else-if="item.is_on_probation"
                  class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors flex items-center gap-2"
                >
                  <span>✅</span> Remove Probation
                </button>
                <button
                  @click="activateUserAction(item); actionsMenuOpen = null"
                  v-if="!item.is_active"
                  class="block w-full text-left px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors flex items-center gap-2"
                >
                  <span>✅</span> Activate
                </button>
                <button
                  @click="deactivateUserAction(item); actionsMenuOpen = null"
                  v-else-if="item.is_active && item.role !== 'superadmin'"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                >
                  <span>⏸️</span> Deactivate
                </button>
                
                <!-- Account Actions -->
                <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase bg-gray-50 dark:bg-gray-700/50 sticky top-0">Account</div>
                <button
                  @click="resetPasswordAction(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors flex items-center gap-2"
                >
                  <span>🔑</span> Reset Password
                </button>
                <button
                  v-if="canImpersonateUser(item)"
                  @click="impersonateUser(item); actionsMenuOpen = null"
                  class="block w-full text-left px-4 py-2 text-sm text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors flex items-center gap-2"
                >
                  <span>🎭</span> Impersonate
                </button>
                
                <!-- Admin Actions (Superadmin only) -->
                <template v-if="isSuperAdmin">
                  <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  <div class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase bg-gray-50 dark:bg-gray-700/50 sticky top-0">Admin</div>
                  <button
                    @click="changeRoleAction(item); actionsMenuOpen = null"
                    v-if="item.role !== 'superadmin'"
                    class="block w-full text-left px-4 py-2 text-sm text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors flex items-center gap-2"
                  >
                    <span>👤</span> Change Role
                  </button>
                  <button
                    @click="promoteToAdminAction(item); actionsMenuOpen = null"
                    v-if="!['admin', 'superadmin'].includes(item.role)"
                    class="block w-full text-left px-4 py-2 text-sm text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors flex items-center gap-2"
                  >
                    <span>⭐</span> Promote to Admin
                  </button>
                  <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  <button
                    @click="deleteUserAction(item); actionsMenuOpen = null"
                    v-if="item.role !== 'superadmin'"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
                  >
                    <span>🗑️</span> Delete User
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </template>
    </EnhancedDataTable>

    <!-- Create/Edit User Modal -->
    <div v-if="showCreateModal || editingUser" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingUser ? 'Edit User' : 'Create User' }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingUser ? 'Update user information and settings' : 'Create a new user account' }}</p>
            </div>
            <button 
              @click="closeModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="saveUser" class="space-y-6">
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
                <div v-if="!editingUser">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Password <span class="text-red-500">*</span>
                  </label>
                  <input 
                    v-model="userForm.password" 
                    type="password" 
                    required 
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Enter password"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Minimum 8 characters recommended</p>
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
          </form>
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-end gap-3">
          <button 
            type="button" 
            @click="closeModal" 
            class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            @click="saveUser"
            :disabled="saving"
            class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            {{ saving ? 'Saving...' : (editingUser ? 'Update User' : 'Create User') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Action Modals -->
    <div v-if="showActionModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="closeActionModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-lg w-full my-auto overflow-hidden flex flex-col max-h-[90vh]">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-orange-50 to-red-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ actionModalTitle }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Please provide the required information</p>
            </div>
            <button 
              @click="closeActionModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="confirmAction" class="space-y-4">
            <div v-if="currentAction === 'suspend' || currentAction === 'probation' || currentAction === 'blacklist'">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reason <span class="text-red-500">*</span>
              </label>
              <textarea 
                v-model="actionData.reason" 
                rows="4" 
                required 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="Enter reason for this action..."
              ></textarea>
            </div>
            <div v-if="currentAction === 'suspend' || currentAction === 'probation'">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Duration (days)</label>
              <input 
                v-model.number="actionData.duration_days" 
                type="number" 
                min="1" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                placeholder="30"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Leave empty for indefinite duration</p>
            </div>
            <div v-if="currentAction === 'change_role'">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                New Role <span class="text-red-500">*</span>
              </label>
              <select 
                v-model="actionData.role" 
                required 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              >
                <option value="client">Client</option>
                <option value="writer">Writer</option>
                <option value="editor">Editor</option>
                <option value="support">Support</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </form>
        </div>
        
        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-end gap-3">
          <button 
            type="button" 
            @click="closeActionModal" 
            class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            @click="confirmAction"
            :disabled="saving"
            :class="[
              'px-5 py-2.5 text-sm font-medium rounded-lg transition-colors flex items-center gap-2',
              currentAction === 'delete' || currentAction === 'blacklist'
                ? 'bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed'
            ]"
          >
            <span v-if="saving" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
            {{ saving ? 'Processing...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog />
    
    <!-- Input Modal -->
    <InputModal />
    
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
              :disabled="endingImpersonation"
              class="btn btn-secondary inline-flex items-center gap-2"
              :aria-label="endingImpersonation ? 'Ending impersonation...' : 'End impersonation'"
              :aria-busy="endingImpersonation"
            >
              <svg 
                v-if="endingImpersonation"
                class="animate-spin h-4 w-4" 
                fill="none" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ endingImpersonation ? 'Ending...' : 'End Impersonation' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-4 rounded-lg mb-4 shadow-sm border" :class="messageSuccess ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'">
      <div class="flex items-center gap-2">
        <span v-if="messageSuccess" class="text-green-600 text-xl font-bold">✓</span>
        <span v-else class="text-red-600 text-xl font-bold">✗</span>
        <span class="font-medium">{{ message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import apiClient from '@/api/client'
import usersAPI from '@/api/users'
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import InputModal from '@/components/common/InputModal.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { formatWebsiteName } from '@/utils/formatDisplay'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()
const inputModal = useInputModal()

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
    
    // Process the response structure
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
    
    // Process users data
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
      const response = await adminManagementAPI.patchUser(editingUser.value.id, data)
      const successMsg = 'User updated successfully!'
      message.value = successMsg
      messageSuccess.value = true
      showSuccess(successMsg)
      // Keep message visible for a moment before closing modal
      setTimeout(() => {
        closeModal()
      }, 1500)
      await loadUsers()
      await loadStats()
    } else {
      await adminManagementAPI.createUser(userForm.value)
      const successMsg = 'User created successfully!'
      message.value = successMsg
      messageSuccess.value = true
      showSuccess(successMsg)
      // Keep message visible for a moment before closing modal
      setTimeout(() => {
        closeModal()
      }, 1500)
      await loadUsers()
      await loadStats()
    }
  } catch (e) {
    console.error('Error saving user:', e)
    const errorMsg = e.response?.data?.error || 
                     e.response?.data?.detail || 
                     e.response?.data?.message ||
                     (typeof e.response?.data === 'string' ? e.response.data : JSON.stringify(e.response?.data)) ||
                     e.message ||
                     'Failed to save user. Please try again.'
    const fullErrorMsg = 'Failed to save user: ' + errorMsg
    message.value = fullErrorMsg
    messageSuccess.value = false
    showError(fullErrorMsg)
  } finally {
    saving.value = false
  }
}

const viewUser = (user) => {
  editingUser.value = user
  showCreateModal.value = true
}

const viewUserDetail = (user) => {
  router.push(`/admin/users/${user.id}/view`)
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
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to suspend ${selectedUsers.value.length} selected user(s)?`,
    'Suspend Users'
  )
  if (!confirmed) return
  
  const reason = await inputModal.showModal(
    'Enter suspension reason',
    'Suspension Reason',
    {
      label: 'Reason',
      placeholder: 'Enter reason for suspension...',
      multiline: true,
      rows: 3,
      required: true,
      defaultValue: 'Bulk suspension'
    }
  )
  if (reason === null) return
  
  const durationDays = await inputModal.showModal(
    'Enter duration in days',
    'Suspension Duration',
    {
      label: 'Duration (days)',
      placeholder: '30',
      required: true,
      defaultValue: '30'
    }
  )
  if (durationDays === null) return
  
  const duration = durationDays ? parseInt(durationDays) : 30
  
  try {
    const res = await adminManagementAPI.bulkSuspend(selectedUsers.value, reason, duration)
    showSuccess(res.data.message || `Suspended ${res.data.suspended_count} user(s)`)
    selectedUsers.value = []
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to suspend users. Please try again.')
    showError(errorMsg)
  }
}

const bulkActivate = async () => {
  const confirmed = await confirm.showDialog(
    `Activate ${selectedUsers.value.length} selected user(s)?`,
    'Activate Users'
  )
  if (!confirmed) return
  try {
    const res = await adminManagementAPI.bulkActivate(selectedUsers.value)
    showSuccess(res.data.message || `Activated ${res.data.activated_count} user(s)`)
    selectedUsers.value = []
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to activate users. Please try again.')
    showError(errorMsg)
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
  router.push(`/admin/users/${user.id}/edit`)
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
  // Clear message after modal closes (but keep it visible for a few seconds if it's a success)
  if (messageSuccess.value) {
    setTimeout(() => {
      message.value = ''
      messageSuccess.value = false
    }, 5000) // Keep success message visible for 5 seconds
  } else {
    // Clear error messages immediately when modal closes
    message.value = ''
    messageSuccess.value = false
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
  const confirmed = await confirm.showDialog(
    `Unsuspend ${user.username}?`,
    'Unsuspend User'
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.unsuspendUser(user.id)
    showSuccess(`User ${user.username} unsuspended successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to unsuspend user. Please try again.')
    showError(errorMsg)
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
  const confirmed = await confirm.showDialog(
    `Remove ${user.username} from probation?`,
    'Remove Probation'
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.removeFromProbation(user.id)
    showSuccess(`User ${user.username} removed from probation successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to remove probation. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const resetPasswordAction = async (user) => {
  const confirmed = await confirm.showDialog(
    `Reset password for ${user.username}? A new password will be generated and sent to their email.`,
    'Reset Password'
  )
  if (!confirmed) return
  try {
    const res = await adminManagementAPI.resetPassword(user.id)
    showSuccess(res.data.message || 'Password reset successfully. New password sent to user email.')
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to reset password. Please try again.')
    showError(errorMsg)
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
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to promote ${user.username} to admin? This will grant them full administrative access.`,
    'Promote to Admin',
    {
      details: 'This action grants the user full administrative privileges. Make sure this is intended.'
    }
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.promoteToAdmin(user.id)
    showSuccess(`User ${user.username} promoted to admin successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to promote user. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const deleteUserAction = async (user) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete ${user.username}? This action cannot be undone.`,
    'Delete User',
    {
      details: 'This will permanently delete the user account and all associated data. This action cannot be reversed.'
    }
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.deleteUser(user.id)
    showSuccess(`User ${user.username} deleted successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to delete user. Please try again.')
    showError(errorMsg)
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
  const confirmed = await confirm.showDialog(
    `Unblacklist ${user.username}?`,
    'Unblacklist User'
  )
  if (!confirmed) return
  try {
    // Note: Backend might need an unblacklist endpoint, for now we'll use a workaround
    await adminManagementAPI.patchUser(user.id, { is_blacklisted: false })
    showSuccess(`User ${user.username} unblacklisted successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to unblacklist user. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const activateUserAction = async (user) => {
  const confirmed = await confirm.showDialog(
    `Activate ${user.username}?`,
    'Activate User'
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.patchUser(user.id, { is_active: true })
    showSuccess(`User ${user.username} activated successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to activate user. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const deactivateUserAction = async (user) => {
  const confirmed = await confirm.showDialog(
    `Deactivate ${user.username}?`,
    'Deactivate User'
  )
  if (!confirmed) return
  try {
    await adminManagementAPI.patchUser(user.id, { is_active: false })
    showSuccess(`User ${user.username} deactivated successfully`)
    await loadUsers()
    await loadStats()
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to deactivate user. Please try again.')
    showError(errorMsg)
  }
  actionsMenuOpen.value = null
}

const confirmAction = async () => {
  saving.value = true
  message.value = ''
  try {
    let successMsg = ''
    if (currentAction.value === 'suspend') {
      await adminManagementAPI.suspendUser(
        currentUser.value.id,
        actionData.value.reason,
        actionData.value.duration_days
      )
      successMsg = `User ${currentUser.value.username} suspended successfully`
    } else if (currentAction.value === 'probation') {
      await adminManagementAPI.placeOnProbation(
        currentUser.value.id,
        actionData.value.reason,
        actionData.value.duration_days
      )
      successMsg = `User ${currentUser.value.username} placed on probation successfully`
    } else if (currentAction.value === 'blacklist') {
      await adminManagementAPI.blacklistUser(
        currentUser.value.id,
        actionData.value.reason
      )
      successMsg = `User ${currentUser.value.username} blacklisted successfully`
    } else if (currentAction.value === 'change_role') {
      await adminManagementAPI.changeRole(currentUser.value.id, actionData.value.role)
      successMsg = `User ${currentUser.value.username} role changed to ${actionData.value.role} successfully`
    }
    
    if (successMsg) {
      message.value = successMsg
      messageSuccess.value = true
      showSuccess(successMsg)
      // Keep message visible for a moment before closing modal
      setTimeout(() => {
        closeActionModal()
      }, 1500)
      await loadUsers()
      await loadStats()
    }
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to perform action. Please try again.')
    message.value = errorMsg
    messageSuccess.value = false
    showError(errorMsg)
  } finally {
    saving.value = false
  }
}

const closeActionModal = () => {
  showActionModal.value = false
  currentAction.value = ''
  currentUser.value = null
  actionData.value = { reason: '', duration_days: 30, role: '' }
  // Clear message after modal closes (but keep it visible for a few seconds if it's a success)
  if (messageSuccess.value) {
    setTimeout(() => {
      message.value = ''
      messageSuccess.value = false
    }, 5000) // Keep success message visible for 5 seconds
  } else {
    // Clear error messages immediately when modal closes
    message.value = ''
    messageSuccess.value = false
  }
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
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Column definitions for Users table
const usersColumns = computed(() => [
  {
    key: 'select',
    label: '',
    sortable: false,
    class: 'w-12'
  },
  {
    key: 'user',
    label: 'User',
    sortable: true,
    format: (value, item) => item.full_name || item.username || item.email
  },
  {
    key: 'role',
    label: 'Role',
    sortable: true,
    class: 'w-28'
  },
  {
    key: 'website',
    label: 'Website',
    sortable: false
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    class: 'w-32'
  },
  {
    key: 'last_login',
    label: 'Last Login',
    sortable: true,
    format: (value) => formatDate(value),
    class: 'w-40'
  },
  {
    key: 'date_joined',
    label: 'Joined',
    sortable: true,
    format: (value) => formatDate(value),
    class: 'w-40'
  },
  {
    key: 'actions',
    label: 'Actions',
    sortable: false,
    align: 'right',
    class: 'w-48'
  }
])

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
    // Store a flag to indicate this is an impersonation tab (for closing later)
    localStorage.setItem('_is_impersonation_tab', 'true')
    const baseUrl = window.location.origin
    const impersonateUrl = `${baseUrl}/impersonate?token=${encodeURIComponent(token)}`
    // Remove 'noopener' to allow window.opener access for closing the tab
    // This is safe because we control both windows and they're same-origin
    window.open(impersonateUrl, '_blank', 'noreferrer')
    
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

const endingImpersonation = ref(false)

const endImpersonation = async () => {
  endingImpersonation.value = true
  try {
    message.value = ''
    const res = await authStore.endImpersonation()
    if (res?.success === false) {
      message.value = res.error || 'Failed to end impersonation'
      messageSuccess.value = false
    } else {
      // Show success message if not an impersonation tab
      const isImpersonationTab = localStorage.getItem('_is_impersonation_tab') === 'true'
      if (!isImpersonationTab) {
        message.value = res?.message || 'Impersonation ended. Admin session restored.'
        messageSuccess.value = true
      }
      
      // Note: This function is called from the admin tab (parent window)
      // The impersonation tab should handle closing itself when ending impersonation
      // The admin tab remains logged in with its own session - no redirect needed
    }
    
    // If there's an error message from the store, display it
    if (authStore.error) {
      message.value = authStore.error
      messageSuccess.value = false
    }
  } catch (e) {
    const errorMessage = e?.response?.data?.error || 
                        e?.response?.data?.detail || 
                        e?.message || 
                        'Failed to end impersonation. Please try again.'
    message.value = errorMessage
    messageSuccess.value = false
  } finally {
    endingImpersonation.value = false
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

/* Make table rows more compact - everything on one line */
:deep(.enhanced-data-table table tbody tr) {
  height: auto;
}

:deep(.enhanced-data-table table tbody tr td) {
  padding: 0.5rem 1rem !important;
  vertical-align: middle;
  white-space: nowrap;
}

:deep(.enhanced-data-table table thead tr th) {
  padding: 0.5rem 1rem !important;
}

/* Allow text truncation in user cell */
:deep(.enhanced-data-table table tbody tr td .flex) {
  white-space: nowrap;
}

:deep(.enhanced-data-table table tbody tr td .truncate) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

