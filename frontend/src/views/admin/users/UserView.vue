<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Breadcrumbs -->
      <nav class="mb-6" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-2 text-sm">
          <li>
            <router-link to="/admin" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Admin
            </router-link>
          </li>
          <li class="text-gray-400 dark:text-gray-500">/</li>
          <li>
            <router-link to="/admin/users" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Users
            </router-link>
          </li>
          <li class="text-gray-400 dark:text-gray-500">/</li>
          <li class="text-gray-900 dark:text-white font-medium" aria-current="page">
            {{ user?.full_name || user?.username || 'User' }}
          </li>
        </ol>
      </nav>

      <!-- Header Section -->
      <div v-if="user" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div class="px-6 py-6">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-5">
              <div class="h-20 w-20 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-bold text-3xl shadow-lg">
                {{ getUserInitials(user) }}
              </div>
              <div>
                <div class="flex items-center gap-3 mb-2">
                  <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
                    {{ user.full_name || user.username }}
                  </h1>
                  <span
                    :class="getRoleBadgeClass(user.role)"
                    class="px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide"
                  >
                    {{ user.role_display || user.role }}
                  </span>
                  <span
                    v-if="user.is_active"
                    class="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300"
                  >
                    Active
                  </span>
                  <span
                    v-else
                    class="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300"
                  >
                    Inactive
                  </span>
                </div>
                <p class="text-gray-600 dark:text-gray-400 mb-1">{{ user.email }}</p>
                <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mt-2">
                  <span v-if="user.phone_number">
                    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    {{ user.phone_number }}
                  </span>
                  <span v-if="user.website?.name">
                    <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    {{ user.website.name }}
                  </span>
                  <span v-if="user.date_joined">
                    Joined {{ formatDate(user.date_joined) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <button
                v-if="canImpersonateUser(user)"
                @click="impersonateUser"
                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Impersonate
              </button>
              <router-link
                :to="`/admin/users/${userId}/edit`"
                class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 shadow-sm"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit User
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading user details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
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

      <!-- Stats Cards (for clients/writers) -->
      <div v-if="user && !loading && !error" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- Client Stats -->
        <div v-if="user.role === 'client'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Wallet Balance</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ (walletBalance || 0).toFixed(2) }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div v-if="user.role === 'client'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Orders</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ orders.length }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>
        
        <!-- Writer Stats -->
        <div v-if="user.role === 'writer'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Completed Orders</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ writerStats.completedOrders || 0 }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div v-if="user.role === 'writer'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Earned</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ (writerStats.totalEarned || 0).toFixed(2) }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div v-if="user.role === 'writer'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Pending Earnings</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ (writerStats.pendingEarnings || 0).toFixed(2) }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div v-if="user.role === 'writer'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">In Progress</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ writerStats.inProgressOrders || 0 }}</p>
            </div>
            <div class="h-12 w-12 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div v-if="user && !loading && !error" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="flex space-x-8 px-6" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              ]"
            >
              {{ tab.label }}
              <span v-if="tab.count !== undefined" class="ml-2 py-0.5 px-2 rounded-full text-xs" :class="activeTab === tab.id ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'">
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>
      </div>

      <!-- Tab Content: Overview -->
      <div v-if="user && !loading && !error && activeTab === 'overview'" class="space-y-6">
        <!-- Basic Information Card -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Basic Information</h3>
          </div>
          <div class="p-6">
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Username</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.username }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Email</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.email }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Phone Number</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.phone_number || 'Not provided' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Website</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.website?.name || 'Not assigned' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Member Since</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ formatDateTime(user.date_joined) }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Last Login</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.last_login ? formatDateTime(user.last_login) : 'Never' }}</dd>
              </div>
            </dl>
          </div>
        </div>

        <!-- Status Information Card -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Account Status</h3>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Account Status</span>
                <span
                  :class="user.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'"
                  class="px-3 py-1 rounded-full text-xs font-semibold"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div v-if="user.is_suspended" class="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div>
                  <span class="text-sm font-medium text-red-800 dark:text-red-300">Suspended</span>
                  <p class="text-xs text-red-600 dark:text-red-400 mt-1">{{ user.suspension_reason || 'No reason provided' }}</p>
                  <p v-if="user.suspension_end_date" class="text-xs text-red-500 dark:text-red-400 mt-1">
                    Until: {{ formatDateTime(user.suspension_end_date) }}
                  </p>
                </div>
              </div>
              <div v-if="user.is_on_probation" class="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <div>
                  <span class="text-sm font-medium text-yellow-800 dark:text-yellow-300">On Probation</span>
                  <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">{{ user.probation_reason || 'No reason provided' }}</p>
                </div>
              </div>
              <div v-if="user.is_blacklisted" class="flex items-center justify-between p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <span class="text-sm font-medium text-red-800 dark:text-red-300">Blacklisted - Permanently banned</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Information Card (for clients) -->
        <div v-if="user.client_profile" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Client Profile</h3>
          </div>
          <div class="p-6">
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Registration ID</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.client_profile.registration_id || 'N/A' }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <!-- Tab Content: Orders -->
      <div v-if="user && !loading && !error && activeTab === 'orders'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Orders
                <span v-if="orders.length > 0" class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
                  ({{ orders.length }})
                </span>
              </h3>
              <button
                @click="viewUserOrders"
                class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                View All Orders
              </button>
            </div>
          </div>
          <div class="p-6">
          
          <div v-if="ordersLoading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading orders...</p>
          </div>
          
          <div v-else-if="ordersError" class="text-center py-8 text-red-600 dark:text-red-400">
            {{ ordersError }}
          </div>
          
          <div v-else-if="orders.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">📦</div>
            <p>No orders found</p>
          </div>
          
          <!-- Orders grouped by status (for writers) -->
          <div v-else-if="user.role === 'writer'" class="space-y-6">
            <!-- In Progress Orders -->
            <div v-if="ordersByStatus.inProgress.length > 0">
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">
                In Progress ({{ ordersByStatus.inProgress.length }})
              </h4>
              <div class="space-y-3">
                <div
                  v-for="order in ordersByStatus.inProgress"
                  :key="order.id"
                  @click="viewOrder(order.id)"
                  class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                >
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <span class="font-semibold text-gray-900 dark:text-white">#{{ order.id }}</span>
                      <span
                        class="px-2 py-1 text-xs font-semibold rounded-full"
                        :class="getStatusClass(order.status)"
                      >
                        {{ formatStatus(order.status) }}
                      </span>
                    </div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                      {{ order.topic || 'Untitled Order' }}
                    </h4>
                    <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span v-if="order.created_at">
                        Created: {{ formatDate(order.created_at) }}
                      </span>
                      <span v-if="order.writer_deadline || order.client_deadline">
                        Deadline: {{ formatDate(order.writer_deadline || order.client_deadline) }}
                      </span>
                      <span v-if="order.number_of_pages">
                        {{ order.number_of_pages }} pages
                      </span>
                    </div>
                  </div>
                  <div class="text-right ml-4">
                    <p v-if="order.writer_compensation || order.total_price" class="font-semibold text-gray-900 dark:text-white">
                      ${{ ((order.writer_compensation || order.total_price) || 0).toFixed(2) }}
                    </p>
                    <button
                      @click.stop="viewOrder(order.id)"
                      class="mt-2 px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-medium"
                    >
                      View →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Completed Orders -->
            <div v-if="ordersByStatus.completed.length > 0">
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">
                Completed ({{ ordersByStatus.completed.length }})
              </h4>
              <div class="space-y-3">
                <div
                  v-for="order in ordersByStatus.completed"
                  :key="order.id"
                  @click="viewOrder(order.id)"
                  class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                >
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <span class="font-semibold text-gray-900 dark:text-white">#{{ order.id }}</span>
                      <span
                        class="px-2 py-1 text-xs font-semibold rounded-full"
                        :class="getStatusClass(order.status)"
                      >
                        {{ formatStatus(order.status) }}
                      </span>
                    </div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                      {{ order.topic || 'Untitled Order' }}
                    </h4>
                    <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span v-if="order.completed_at || order.submitted_at">
                        Completed: {{ formatDate(order.completed_at || order.submitted_at) }}
                      </span>
                      <span v-if="order.number_of_pages">
                        {{ order.number_of_pages }} pages
                      </span>
                    </div>
                  </div>
                  <div class="text-right ml-4">
                    <p v-if="order.writer_compensation || order.total_price" class="font-semibold text-gray-900 dark:text-white">
                      ${{ ((order.writer_compensation || order.total_price) || 0).toFixed(2) }}
                    </p>
                    <button
                      @click.stop="viewOrder(order.id)"
                      class="mt-2 px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-medium"
                    >
                      View →
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Other Status Orders -->
            <div v-if="ordersByStatus.other.length > 0">
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">
                Other ({{ ordersByStatus.other.length }})
              </h4>
              <div class="space-y-3">
                <div
                  v-for="order in ordersByStatus.other"
                  :key="order.id"
                  @click="viewOrder(order.id)"
                  class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                >
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <span class="font-semibold text-gray-900 dark:text-white">#{{ order.id }}</span>
                      <span
                        class="px-2 py-1 text-xs font-semibold rounded-full"
                        :class="getStatusClass(order.status)"
                      >
                        {{ formatStatus(order.status) }}
                      </span>
                    </div>
                    <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                      {{ order.topic || 'Untitled Order' }}
                    </h4>
                    <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span v-if="order.created_at">
                        Created: {{ formatDate(order.created_at) }}
                      </span>
                      <span v-if="order.number_of_pages">
                        {{ order.number_of_pages }} pages
                      </span>
                    </div>
                  </div>
                  <div class="text-right ml-4">
                    <p v-if="order.writer_compensation || order.total_price" class="font-semibold text-gray-900 dark:text-white">
                      ${{ ((order.writer_compensation || order.total_price) || 0).toFixed(2) }}
                    </p>
                    <button
                      @click.stop="viewOrder(order.id)"
                      class="mt-2 px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-medium"
                    >
                      View →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Regular orders list (for clients and others) -->
          <div v-else class="space-y-3">
            <div
              v-for="order in orders"
              :key="order.id"
              @click="viewOrder(order.id)"
              class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
            >
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <span class="font-semibold text-gray-900 dark:text-white">#{{ order.id }}</span>
                  <span
                    class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="getStatusClass(order.status)"
                  >
                    {{ formatStatus(order.status) }}
                  </span>
                </div>
                <h4 class="font-medium text-gray-900 dark:text-white mb-1">
                  {{ order.topic || 'Untitled Order' }}
                </h4>
                <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <span v-if="order.created_at">
                    Created: {{ formatDate(order.created_at) }}
                  </span>
                  <span v-if="order.client_deadline">
                    Deadline: {{ formatDate(order.client_deadline) }}
                  </span>
                  <span v-if="order.number_of_pages">
                    {{ order.number_of_pages }} pages
                  </span>
                </div>
              </div>
              <div class="text-right ml-4">
                <p v-if="order.total_price" class="font-semibold text-gray-900 dark:text-white">
                  ${{ (order.total_price || 0).toFixed(2) }}
                </p>
                <button
                  @click.stop="viewOrder(order.id)"
                  class="mt-2 px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-medium"
                >
                  View →
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>

      <!-- Tab Content: Activity -->
      <div v-if="user && !loading && !error && activeTab === 'activity'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Activity Logs</h3>
              <button
                @click="viewUserActivity"
                class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                View All Activity
              </button>
            </div>
          </div>
          <div class="p-6">
          
          <div v-if="activityLogsLoading" class="text-center py-4">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
          </div>
          
          <div v-else-if="activityLogs.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">📋</div>
            <p>No recent activity</p>
          </div>
          
          <div v-else class="space-y-3">
            <div
              v-for="log in activityLogs"
              :key="log.id"
              class="flex items-start gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                <span class="text-xs font-semibold text-primary-600 dark:text-primary-400">
                  {{ log.action_type?.charAt(0) || 'A' }}
                </span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-gray-900 dark:text-white">
                  {{ log.description || 'Activity logged' }}
                </p>
                <div class="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
                  <span>{{ formatDateTime(log.timestamp) }}</span>
                  <span v-if="log.action_type">•</span>
                  <span v-if="log.action_type">{{ log.action_type }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Wallet (for clients) -->
      <div v-if="user && !loading && !error && activeTab === 'wallet' && user.role === 'client'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Wallet</h3>
              <button
                @click="viewUserWallet"
                class="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                View Details
              </button>
            </div>
          </div>
          <div class="p-6">
            <div v-if="walletLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading wallet information...</p>
            </div>
            <div v-else-if="walletError" class="text-center py-8 text-red-600 dark:text-red-400">
              {{ walletError }}
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-6 rounded-xl border border-blue-200 dark:border-blue-700">
                <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-2">Balance</p>
                <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">${{ (walletBalance || 0).toFixed(2) }}</p>
              </div>
              <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-6 rounded-xl border border-green-200 dark:border-green-700">
                <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-2">Total Deposited</p>
                <p class="text-3xl font-bold text-green-900 dark:text-green-100">${{ (walletTotalDeposited || 0).toFixed(2) }}</p>
              </div>
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-6 rounded-xl border border-purple-200 dark:border-purple-700">
                <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-2">Total Spent</p>
                <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">${{ (walletTotalSpent || 0).toFixed(2) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Referrals (for clients) -->
      <div v-if="user && !loading && !error && activeTab === 'referrals' && user.role === 'client'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Referral Program</h3>
          </div>
          <div class="p-6">
            <div v-if="referralLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading referral information...</p>
            </div>
            
            <div v-else-if="referralInfo" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Referrals</p>
                <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ referralInfo.totalReferrals || 0 }}</p>
              </div>
              <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Successful</p>
                <p class="text-2xl font-bold text-green-900 dark:text-green-100">{{ referralInfo.successfulReferrals || 0 }}</p>
              </div>
              <div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Earned</p>
                <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">${{ (referralInfo.totalEarned || 0).toFixed(2) }}</p>
              </div>
            </div>
            
            <div v-if="referralInfo.referrals && referralInfo.referrals.length > 0" class="mt-4">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Recent Referrals</h4>
              <div class="space-y-2">
                <div
                  v-for="referral in referralInfo.referrals"
                  :key="referral.id"
                  class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                      Referred: {{ referral.referred_user?.username || referral.referred_email || 'N/A' }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {{ formatDate(referral.created_at || referral.referral_date) }}
                    </p>
                  </div>
                  <div class="text-right">
                    <span
                      class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="referral.status === 'successful' || referral.is_successful ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'"
                    >
                      {{ referral.status || 'Pending' }}
                    </span>
                    <p v-if="referral.referral_bonus || referral.amount" class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                      ${{ ((referral.referral_bonus || referral.amount) || 0).toFixed(2) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>No referral information available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Loyalty (for clients) -->
      <div v-if="user && !loading && !error && activeTab === 'loyalty' && user.role === 'client'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Loyalty Program</h3>
          </div>
          <div class="p-6">
            <div v-if="loyaltyLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading loyalty information...</p>
            </div>
            
            <div v-else-if="loyaltyInfo" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Loyalty Points</p>
                <p class="text-2xl font-bold text-yellow-900 dark:text-yellow-100">
                  {{ loyaltyInfo.points || loyaltyInfo.current_points || 0 }}
                </p>
              </div>
              <div class="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Tier</p>
                <p class="text-2xl font-bold text-indigo-900 dark:text-indigo-100">
                  {{ loyaltyInfo.tier || loyaltyInfo.current_tier || 'N/A' }}
                </p>
              </div>
              <div class="bg-pink-50 dark:bg-pink-900/20 p-4 rounded-lg">
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Points Value</p>
                <p class="text-2xl font-bold text-pink-900 dark:text-pink-100">
                  ${{ ((loyaltyInfo.points_value || loyaltyInfo.points || 0) * 0.01 || 0).toFixed(2) }}
                </p>
              </div>
            </div>
            
            <div v-if="loyaltyInfo.next_tier" class="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p class="text-sm text-gray-600 dark:text-gray-400">
                <span class="font-medium text-gray-900 dark:text-white">Next Tier:</span>
                {{ loyaltyInfo.next_tier.name || loyaltyInfo.next_tier }}
                <span v-if="loyaltyInfo.points_to_next_tier">
                  ({{ loyaltyInfo.points_to_next_tier }} points needed)
                </span>
              </p>
            </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
              <p>No loyalty information available</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Profile (for writers) -->
      <div v-if="user && !loading && !error && activeTab === 'profile' && user.role === 'writer'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Writer Profile</h3>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Level</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.writer_profile?.writer_level?.name || user.writer_profile?.level || 'Not Set' }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Registration ID</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ user.writer_profile?.registration_id || 'N/A' }}</dd>
              </div>
              <div v-if="user.writer_profile?.writer_level">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Earning Mode</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">{{ formatEarningMode(user.writer_profile.writer_level.earning_mode) }}</dd>
              </div>
              <div v-if="user.writer_profile?.writer_level">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Base Pay</dt>
                <dd class="text-sm text-gray-900 dark:text-white font-medium">${{ (user.writer_profile.writer_level.base_pay_per_page || 0).toFixed(2) }}/page</dd>
              </div>
            </div>
            
            <!-- Level Selector (Admin Only) -->
            <div v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'superadmin'" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <label class="block text-sm font-medium text-gray-900 dark:text-white mb-3">
                Set Writer Level
              </label>
              <div class="flex items-center gap-3">
                <select
                  v-model="selectedLevelId"
                  :disabled="writerLevelsLoading || updatingLevel"
                  class="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                >
                  <option :value="null">-- Select Level --</option>
                  <option
                    v-for="level in writerLevels"
                    :key="level.id"
                    :value="level.id"
                  >
                    {{ level.name }}
                    <span v-if="level.earning_mode === 'fixed_per_page'">
                      - ${{ (level.base_pay_per_page || 0).toFixed(2) }}/page
                    </span>
                    <span v-else-if="level.earning_mode === 'percentage_of_order_cost'">
                      - {{ level.earnings_percentage_of_cost || 0 }}% of cost
                    </span>
                    <span v-else-if="level.earning_mode === 'percentage_of_order_total'">
                      - {{ level.earnings_percentage_of_total || 0 }}% of total
                    </span>
                  </option>
                </select>
                <button
                  @click="updateWriterLevel"
                  :disabled="!selectedLevelId || updatingLevel || selectedLevelId === user.writer_profile?.writer_level?.id"
                  class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
                >
                  <span v-if="updatingLevel" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                  <span>{{ updatingLevel ? 'Updating...' : 'Update Level' }}</span>
                </button>
              </div>
              <p v-if="user.writer_profile?.writer_level" class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Current: {{ user.writer_profile.writer_level.name }}
                <span v-if="user.writer_profile.writer_level.max_orders" class="ml-2">
                  (Max Orders: {{ user.writer_profile.writer_level.max_orders }})
                </span>
              </p>
            </div>

            <!-- Takes Restrictions (Admin Only) -->
            <div v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'superadmin'" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 mb-4">
                <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">Order Takes Restrictions</h4>
                <p class="text-xs text-blue-700 dark:text-blue-300 mb-3">
                  Control whether this writer can take orders directly from their profile. This restriction only applies to writers taking orders themselves; admins can still assign orders manually.
                </p>
                <div class="space-y-2 text-xs text-blue-600 dark:text-blue-400">
                  <p><strong>Level-Based Restriction:</strong> Writer's level allows up to {{ user.writer_profile?.writer_level?.max_orders || 0 }} simultaneous orders.</p>
                  <p><strong>Profile Override:</strong> You can disable takes entirely for this writer regardless of their level.</p>
                </div>
              </div>
              
              <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div class="flex-1">
                  <label class="block text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Allow Order Takes
                  </label>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    When disabled, writer cannot take orders from their profile (admins can still assign manually)
                  </p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="canTakeOrders"
                    @change="updateTakesRestriction"
                    :disabled="updatingTakesRestriction"
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div v-if="user.writer_profile?.writer_level" class="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                <p class="text-xs text-yellow-800 dark:text-yellow-200">
                  <strong>Current Status:</strong> 
                  <span v-if="canTakeOrders">
                    Writer can take up to {{ user.writer_profile.writer_level.max_orders }} orders (level limit).
                  </span>
                  <span v-else>
                    Writer cannot take orders (restricted by admin override).
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content: Security -->
      <div v-if="user && !loading && !error && activeTab === 'security'" class="space-y-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Account Security</h3>
          </div>
          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">2FA Status</p>
                </div>
                <span
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="user.is_2fa_enabled ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
                >
                  {{ user.is_2fa_enabled ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Account Status</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">Active Status</p>
                </div>
                <span
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="user.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'"
                >
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              
              <div v-if="user.is_staff" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Staff Access</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">Admin Panel Access</p>
                </div>
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                  Enabled
                </span>
              </div>
              </div>
            
              <div class="space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Email Verified</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">Email Confirmation</p>
                </div>
                <span
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="user.is_email_verified ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'"
                >
                  {{ user.is_email_verified ? 'Verified' : 'Unverified' }}
                </span>
              </div>
              
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Account Locked</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">Login Security</p>
                </div>
                <span
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="user.is_locked ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'"
                >
                  {{ user.is_locked ? 'Locked' : 'Unlocked' }}
                </span>
              </div>
              
              <div v-if="user.date_joined" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">Member Since</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(user.date_joined) }}</p>
                </div>
              </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import ordersAPI from '@/api/orders'
import walletAPI from '@/api/wallet'
import activityLogsAPI from '@/api/activity-logs'
import clientDashboardAPI from '@/api/client-dashboard'
import writerManagementAPI from '@/api/writer-management'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()

const userId = computed(() => parseInt(route.params.id))
const user = ref(null)
const loading = ref(true)
const error = ref(null)
const activeTab = ref('overview')

// Orders state
const orders = ref([])
const ordersLoading = ref(false)
const ordersError = ref(null)

// Wallet state (for clients)
const walletBalance = ref(0)
const walletTotalDeposited = ref(0)
const walletTotalSpent = ref(0)
const walletLoading = ref(false)
const walletError = ref(null)

// Writer statistics state
const writerStats = ref({
  completedOrders: 0,
  totalEarned: 0,
  pendingEarnings: 0,
  inProgressOrders: 0,
})
const writerStatsLoading = ref(false)

// Activity logs state
const activityLogs = ref([])
const activityLogsLoading = ref(false)
const activityLogsError = ref(null)

// Referral information (for clients)
const referralInfo = ref(null)
const referralLoading = ref(false)

// Loyalty information (for clients)
const loyaltyInfo = ref(null)
const loyaltyLoading = ref(false)

// Writer level management
const writerLevels = ref([])
const writerLevelsLoading = ref(false)
const updatingLevel = ref(false)
const selectedLevelId = ref(null)

// Takes restrictions management
const canTakeOrders = ref(true)
const updatingTakesRestriction = ref(false)

// Computed: Orders grouped by status (for writers)
const ordersByStatus = computed(() => {
  if (!user.value || user.value.role !== 'writer') {
    return { inProgress: [], completed: [], other: [] }
  }
  
  const inProgress = orders.value.filter(o => 
    ['in_progress', 'under_editing', 'revision_in_progress', 'on_hold'].includes(o.status)
  )
  const completed = orders.value.filter(o => 
    ['completed', 'submitted', 'approved', 'closed', 'rated', 'reviewed'].includes(o.status)
  )
  const other = orders.value.filter(o => 
    !['in_progress', 'under_editing', 'revision_in_progress', 'on_hold', 
      'completed', 'submitted', 'approved', 'closed', 'rated', 'reviewed'].includes(o.status)
  )
  
  return { inProgress, completed, other }
})

// Computed: Tabs with counts
const tabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'orders', label: 'Orders', count: orders.value.length },
    { id: 'activity', label: 'Activity', count: activityLogs.value.length },
  ]
  
  if (user.value?.role === 'client') {
    baseTabs.push({ id: 'wallet', label: 'Wallet' })
    if (referralInfo.value) {
      baseTabs.push({ id: 'referrals', label: 'Referrals', count: referralInfo.value.totalReferrals })
    }
    if (loyaltyInfo.value) {
      baseTabs.push({ id: 'loyalty', label: 'Loyalty' })
    }
  }
  
  if (user.value?.role === 'writer') {
    baseTabs.push({ id: 'profile', label: 'Profile' })
  }
  
  baseTabs.push({ id: 'security', label: 'Security' })
  
  return baseTabs
})

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

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getRoleBadgeClass = (role) => {
  const classes = {
    client: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
    writer: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
    editor: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
    support: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
    admin: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
    superadmin: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300',
  }
  return classes[role] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
}

const canImpersonateUser = (user) => {
  if (!user || !authStore.user) return false
  const userRole = user.role || null
  if (!userRole) return false
  const currentUser = authStore.user
  if (!currentUser || !currentUser.role) return false
  const isAdmin = ['admin', 'superadmin'].includes(currentUser.role)
  if (!isAdmin) return false
  return ['client', 'writer'].includes(userRole)
}

const loadUser = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await adminManagementAPI.getUser(userId.value)
    user.value = res.data
  } catch (e) {
    const errorMsg = getErrorMessage(e, 'Failed to load user details', `Unable to load user #${userId.value}. Please try again.`)
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const viewUserWallet = () => {
  if (user.value?.role === 'client') {
    router.push(`/admin/wallets?user=${user.value.id}`)
  }
}

const viewUserOrders = () => {
  router.push(`/orders?user=${user.value.id}`)
}

const viewOrder = (orderId) => {
  router.push(`/orders/${orderId}`)
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'on_hold': 'On Hold',
    'revision': 'Revision',
    'disputed': 'Disputed',
    'submitted': 'Submitted',
    'under_editing': 'Under Editing',
    'revision_requested': 'Revision Requested',
    'approved': 'Approved',
    'closed': 'Closed',
    'rated': 'Rated',
    'reviewed': 'Reviewed',
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'pending': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
    'in_progress': 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
    'completed': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
    'cancelled': 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
    'on_hold': 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300',
    'revision': 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
    'disputed': 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
    'submitted': 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300',
    'under_editing': 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
    'revision_requested': 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
    'approved': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
    'closed': 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300',
    'rated': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
    'reviewed': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
  }
  return classMap[status] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
}

const loadOrders = async () => {
  if (!user.value) return
  
  ordersLoading.value = true
  ordersError.value = null
  
  try {
    // Fetch orders for this user
    // For clients, filter by client ID; for writers, filter by assigned_writer
    const params = {
      page_size: 50, // Get more orders for writers to calculate stats
      ordering: '-created_at'
    }
    
    if (user.value.role === 'client') {
      params.client = user.value.id
    } else if (user.value.role === 'writer') {
      params.assigned_writer = user.value.id
    }
    
    const response = await ordersAPI.list(params)
    const data = response.data
    orders.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
    
    // Calculate writer statistics if this is a writer
    if (user.value.role === 'writer') {
      calculateWriterStats()
    }
  } catch (e) {
    ordersError.value = getErrorMessage(e, 'Failed to load orders', 'Unable to load orders for this user.')
  } finally {
    ordersLoading.value = false
  }
}

const calculateWriterStats = () => {
  if (!user.value || user.value.role !== 'writer') return
  
  writerStatsLoading.value = true
  
  try {
    // Calculate completed orders
    const completedOrders = orders.value.filter(o => 
      ['completed', 'submitted', 'approved', 'closed', 'rated', 'reviewed'].includes(o.status)
    )
    
    // Calculate in progress orders
    const inProgressOrders = orders.value.filter(o => 
      ['in_progress', 'under_editing', 'revision_in_progress', 'on_hold'].includes(o.status)
    )
    
    // Calculate total earned (from completed orders)
    // Use writer_compensation if available, otherwise estimate from total_price
    const totalEarned = completedOrders.reduce((sum, order) => {
      const earnings = order.writer_compensation || 
                      (order.total_price ? order.total_price * 0.5 : 0) // Fallback estimate
      return sum + (parseFloat(earnings) || 0)
    }, 0)
    
    // Calculate pending earnings (completed but not yet paid)
    // This is a simplified calculation - in reality, you'd check payment status
    // For now, we'll consider all completed orders as potentially pending until paid
    const pendingEarnings = completedOrders.reduce((sum, order) => {
      const earnings = order.writer_compensation || 
                      (order.total_price ? order.total_price * 0.5 : 0)
      // If order has payment_status, check it; otherwise assume pending
      const isPaid = order.payment_status === 'paid' || order.writer_paid === true
      return sum + (isPaid ? 0 : (parseFloat(earnings) || 0))
    }, 0)
    
    writerStats.value = {
      completedOrders: completedOrders.length,
      totalEarned,
      pendingEarnings,
      inProgressOrders: inProgressOrders.length,
    }
  } catch (e) {
    console.error('Error calculating writer stats:', e)
  } finally {
    writerStatsLoading.value = false
  }
}

const loadWallet = async () => {
  if (!user.value || user.value.role !== 'client') return
  
  walletLoading.value = true
  walletError.value = null
  
  try {
    // Fetch wallet information for this client using admin API
    // First, try to get wallet by user ID from admin wallets endpoint
    const walletsResponse = await walletAPI.admin.listWallets({ user: user.value.id })
    const wallets = walletsResponse.data?.results || walletsResponse.data || []
    
    if (wallets.length > 0) {
      const wallet = wallets[0]
      walletBalance.value = wallet.balance || 0
      walletTotalDeposited.value = wallet.total_deposited || 0
      walletTotalSpent.value = wallet.total_spent || 0
    } else {
      // No wallet found, set defaults
      walletBalance.value = 0
      walletTotalDeposited.value = 0
      walletTotalSpent.value = 0
    }
  } catch (e) {
    // Wallet might not be accessible, that's okay - don't show error
    walletError.value = null
    walletBalance.value = 0
    walletTotalDeposited.value = 0
    walletTotalSpent.value = 0
    console.warn('Could not load wallet information:', e)
  } finally {
    walletLoading.value = false
  }
}

const viewUserActivity = () => {
  router.push(`/activity?user=${user.value.id}`)
}

const impersonateUser = async () => {
  if (!user.value) return
  try {
    const usersAPI = (await import('@/api/users')).default
    const tokenResponse = await usersAPI.generateImpersonationToken(user.value.id)
    
    if (tokenResponse.data?.error) {
      showError(tokenResponse.data.error || 'Failed to generate impersonation token')
      return
    }
    
    const token = tokenResponse.data?.token
    
    if (!token) {
      showError('Failed to generate impersonation token')
      return
    }
    
    // Store admin token temporarily in localStorage for the new tab to use
    const adminToken = authStore.accessToken
    if (adminToken) {
      const tokenData = {
        token: adminToken,
        expiresAt: Date.now() + (5 * 60 * 1000) // 5 minutes
      }
      localStorage.setItem('_impersonation_admin_token', JSON.stringify(tokenData))
    }
    
    localStorage.setItem('_is_impersonation_tab', 'true')
    const baseUrl = window.location.origin
    const impersonateUrl = `${baseUrl}/impersonate?token=${encodeURIComponent(token)}`
    window.open(impersonateUrl, '_blank', 'noreferrer')
    
    showSuccess(`Opening impersonation session for ${user.value.username || user.value.email} in a new tab...`)
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to impersonate user'))
  }
}

const endingImpersonation = ref(false)

const endImpersonation = async () => {
  endingImpersonation.value = true
  try {
    const result = await authStore.endImpersonation()
    // If not an impersonation tab, redirect to users list
    // (If it is an impersonation tab, the store will handle closing it)
    const isImpersonationTab = localStorage.getItem('_is_impersonation_tab') === 'true'
    if (!isImpersonationTab) {
      router.push('/admin/users')
    }
    
    // Show success message if available
    if (result?.message) {
      showSuccess(result.message)
    }
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to end impersonation'))
  } finally {
    endingImpersonation.value = false
  }
}

const loadActivityLogs = async () => {
  if (!user.value) return
  
  activityLogsLoading.value = true
  activityLogsError.value = null
  
  try {
    // Try to get activity logs for this user
    // The API might filter by user ID in the query params
    const response = await activityLogsAPI.list({ user_id: user.value.id, limit: 10 })
    const data = response.data
    activityLogs.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
  } catch (e) {
    // If that fails, try without user filter (admin can see all)
    try {
      const response = await activityLogsAPI.list({ limit: 10 })
      const data = response.data
      // Filter client-side if needed
      const allLogs = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
      activityLogs.value = allLogs.filter(log => 
        log.user === user.value.id || 
        log.user_id === user.value.id ||
        (log.user && typeof log.user === 'object' && log.user.id === user.value.id)
      ).slice(0, 10)
    } catch (e2) {
      activityLogsError.value = null // Don't show error, just don't display logs
      console.warn('Could not load activity logs:', e2)
    }
  } finally {
    activityLogsLoading.value = false
  }
}

const loadReferralInfo = async () => {
  if (!user.value || user.value.role !== 'client') return
  
  referralLoading.value = true
  try {
    // Try to get referral info from admin API
    const response = await adminManagementAPI.listReferrals({ client: user.value.id })
    const data = response.data
    const referrals = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
    
    if (referrals.length > 0) {
      referralInfo.value = {
        totalReferrals: referrals.length,
        successfulReferrals: referrals.filter(r => r.status === 'successful' || r.is_successful).length,
        totalEarned: referrals.reduce((sum, r) => sum + (parseFloat(r.referral_bonus || r.amount || 0) || 0), 0),
        referrals: referrals.slice(0, 5) // Show recent 5
      }
    }
  } catch (e) {
    console.warn('Could not load referral info:', e)
  } finally {
    referralLoading.value = false
  }
}

const loadLoyaltyInfo = async () => {
  if (!user.value || user.value.role !== 'client') return
  
  loyaltyLoading.value = true
  try {
    // Note: This might need to be called as the user themselves, or via admin API
    // For now, we'll try to get it from client dashboard API
    // This might fail if not accessible, which is okay
    const response = await clientDashboardAPI.getLoyalty()
    loyaltyInfo.value = response.data
  } catch (e) {
    console.warn('Could not load loyalty info:', e)
  } finally {
    loyaltyLoading.value = false
  }
}

const loadWriterLevels = async () => {
  if (!user.value || user.value.role !== 'writer') return
  
  writerLevelsLoading.value = true
  try {
    // Get available writer levels
    const response = await apiClient.get('/writer-management/writer-levels/', {
      params: { is_active: true }
    })
    const data = response.data
    writerLevels.value = Array.isArray(data?.results) ? data.results : (Array.isArray(data) ? data : [])
    
    // Set current level as selected
    if (user.value.writer_profile?.writer_level?.id) {
      selectedLevelId.value = user.value.writer_profile.writer_level.id
    }
  } catch (e) {
    console.warn('Could not load writer levels:', e)
  } finally {
    writerLevelsLoading.value = false
  }
}

const updateWriterLevel = async () => {
  if (!user.value || !user.value.writer_profile || !selectedLevelId.value) return
  
  updatingLevel.value = true
  try {
    // Get writer profile - the user object should have writer_profile with an id
    let writerProfileId = user.value.writer_profile.id
    
    // If we don't have the profile ID directly, try to get it from the writer endpoint
    if (!writerProfileId) {
      try {
        const profileResponse = await writerManagementAPI.getWriter(user.value.id)
        writerProfileId = profileResponse.data?.id || profileResponse.data?.writer_profile?.id
      } catch (e) {
        console.warn('Could not get writer profile ID:', e)
      }
    }
    
    if (!writerProfileId) {
      throw new Error('Writer profile ID not found. Please ensure the user has a writer profile.')
    }
    
    // Update writer profile via writers endpoint (this is the correct endpoint based on URLs)
    const response = await apiClient.patch(
      `/writer-management/writers/${writerProfileId}/`,
      { writer_level: selectedLevelId.value }
    )
    
    // Reload user data to get updated profile
    await loadUser()
    
    // Update selected level to match new level
    if (user.value.writer_profile?.writer_level?.id) {
      selectedLevelId.value = user.value.writer_profile.writer_level.id
    }
    
    showSuccess('Writer level updated successfully!')
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to update writer level', 'Unable to update writer level. Please try again.'))
  } finally {
    updatingLevel.value = false
  }
}

const formatEarningMode = (mode) => {
  const modeMap = {
    'fixed_per_page': 'Fixed Per Page',
    'percentage_of_order_cost': 'Percentage of Cost',
    'percentage_of_order_total': 'Percentage of Total',
  }
  return modeMap[mode] || mode
}

const updateTakesRestriction = async () => {
  if (!user.value || !user.value.writer_profile) return
  
  updatingTakesRestriction.value = true
  try {
    let writerProfileId = user.value.writer_profile.id
    
    if (!writerProfileId) {
      try {
        const profileResponse = await writerManagementAPI.getWriter(user.value.id)
        writerProfileId = profileResponse.data?.id || profileResponse.data?.writer_profile?.id
      } catch (e) {
        console.warn('Could not get writer profile ID:', e)
      }
    }
    
    if (!writerProfileId) {
      throw new Error('Writer profile ID not found.')
    }
    
    await apiClient.patch(
      `/writer-management/writers/${writerProfileId}/`,
      { can_take_orders: canTakeOrders.value }
    )
    
    await loadUser()
    showSuccess('Takes restriction updated successfully!')
  } catch (e) {
    showError(getErrorMessage(e, 'Failed to update takes restriction', 'Unable to update restriction. Please try again.'))
    // Revert the toggle on error
    canTakeOrders.value = user.value.writer_profile?.can_take_orders ?? true
  } finally {
    updatingTakesRestriction.value = false
  }
}

onMounted(async () => {
  await loadUser()
  if (user.value) {
    await Promise.all([
      loadOrders(),
      loadWallet(),
      loadActivityLogs(),
      loadReferralInfo(),
      loadLoyaltyInfo(),
      loadWriterLevels()
    ])
    
    // Initialize takes restriction toggle
    if (user.value.writer_profile) {
      canTakeOrders.value = user.value.writer_profile.can_take_orders !== false
    }
  }
})
</script>

