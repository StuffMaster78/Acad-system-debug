<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ease-in-out',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'lg:translate-x-0'
      ]"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <h1 class="text-xl font-bold text-primary-600">{{ appName }}</h1>
          <button
            @click="sidebarOpen = false"
            class="lg:hidden text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <!-- Dashboard - Always at top -->
          <router-link
            to="/dashboard"
            :class="[
              'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors mb-4',
              $route.name === 'Dashboard' || $route.path === '/dashboard'
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-700 hover:bg-gray-100'
            ]"
          >
            <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">📊</span>
            Dashboard
          </router-link>

          <!-- Place New Order Button - Prominent at top (Client) -->
          <div v-if="authStore.isClient" class="mb-4">
            <router-link
              to="/orders/wizard"
              class="flex items-center justify-center w-full px-4 py-3 text-sm font-semibold rounded-lg transition-colors bg-primary-600 text-white hover:bg-primary-700 shadow-sm"
            >
              <span class="mr-2">🛒</span>
              Place New Order
              <span class="ml-2 px-2 py-0.5 text-xs bg-yellow-400 text-yellow-900 rounded-full font-bold">NEW</span>
            </router-link>
          </div>

          <!-- Create Order Button - Prominent at top (Admin/SuperAdmin) -->
          <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="mb-4">
            <router-link
              to="/admin/orders/create"
              class="flex items-center justify-center w-full px-4 py-3 text-sm font-semibold rounded-lg transition-colors bg-primary-600 text-white hover:bg-primary-700 shadow-sm"
            >
              <span class="mr-2">➕</span>
              Create Order
              <span class="ml-2 px-2 py-0.5 text-xs bg-yellow-400 text-yellow-900 rounded-full font-bold">NEW</span>
            </router-link>
          </div>

          <!-- Orders section - Simplified and at top -->
          <div v-if="authStore.isClient" class="space-y-1 mb-4">
            <button @click="ordersOpen = !ordersOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
              <span class="flex items-center">
                <span class="w-5 h-5 mr-3">📝</span>
                Orders
              </span>
              <span>{{ ordersOpen ? '▾' : '▸' }}</span>
            </button>
            <div v-if="ordersOpen" class="ml-6 space-y-1">
              <!-- Quick Access -->
              <router-link to="/orders" class="block px-3 py-2 text-sm rounded hover:bg-gray-100 font-medium">📋 All Orders</router-link>
              <router-link to="/orders?is_paid=false" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">💳 Unpaid</router-link>
              <router-link to="/orders?is_paid=true" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">✅ Paid</router-link>
              
              <div class="border-t my-2"></div>
              
              <!-- Most Common Statuses Only -->
              <div class="px-3 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wider">Quick Filters</div>
              <router-link to="/orders?status=pending" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">⏳ Pending</router-link>
              <router-link to="/orders?status=in_progress" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">⚙️ In Progress</router-link>
              <router-link to="/orders?status=submitted" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">📤 Submitted</router-link>
              <router-link to="/orders?status=completed" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">🎉 Completed</router-link>
              <router-link to="/orders?status=revision_requested" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">🔁 Revision Requested</router-link>
              <router-link to="/orders?status=disputed" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">⚠️ Disputed</router-link>
              <router-link to="/orders?status=cancelled" class="block px-3 py-2 text-sm rounded hover:bg-gray-100">❌ Cancelled</router-link>
              
              <div class="border-t my-2"></div>
              
              <!-- Link to view all statuses on orders page -->
              <router-link to="/orders" class="block px-3 py-2 text-sm rounded hover:bg-gray-100 text-primary-600 font-medium">
                🔍 View All Statuses →
              </router-link>
              
              <div class="border-t my-2"></div>
              
              <!-- Order Templates -->
              <router-link to="/orders/templates" class="block px-3 py-2 text-sm rounded hover:bg-gray-100 font-medium text-primary-600">
                📋 Order Templates
              </router-link>
            </div>
          </div>

          <!-- Client Account section (Wallet, Referrals, Loyalty) -->
          <div v-if="authStore.isClient" class="space-y-1 mb-4 pb-4 border-b border-gray-200">
            <div class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Account</div>
            <router-link
              to="/wallet"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'Wallet'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">💼</span>
              My Wallet
            </router-link>
            <router-link
              to="/referrals"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'Referrals'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">🎁</span>
              Referrals
            </router-link>
            <router-link
              to="/loyalty"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'Loyalty'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">⭐</span>
              Loyalty Program
            </router-link>
            <router-link
              to="/discounts"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'ClientDiscounts'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">🎟️</span>
              Discounts
            </router-link>
            <router-link
              to="/account/privacy"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'PrivacySettings'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">🔒</span>
              Privacy & Security
            </router-link>
            <router-link
              to="/account/security"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                $route.name === 'SecurityActivity'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span class="w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none">🛡️</span>
              Security Activity
            </router-link>
          </div>

          <!-- Writer Groups - Organized by category -->
          <template v-if="authStore.isWriter">
            <!-- Orders Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerOrdersOpen = !writerOrdersOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">📝</span>
                  Orders
                </span>
                <span>{{ writerOrdersOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerOrdersOpen" class="ml-6 space-y-1">
                <router-link
                  to="/writer/orders"
                  class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/orders')}"
                >
                  📋 My Orders
                </router-link>
                <router-link
                  to="/writer/queue"
                  class="flex items-center justify-between px-3 py-2 text-sm rounded hover:bg-gray-100"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/queue')}"
                >
                  <span>📋 Order Queue</span>
                  <span
                    v-if="writerQueueCounts.available + writerQueueCounts.preferred > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800"
                  >
                    {{ writerQueueCounts.available + writerQueueCounts.preferred }}
                  </span>
                </router-link>
                <router-link
                  to="/writer/order-requests"
                  class="flex items-center justify-between px-3 py-2 text-sm rounded hover:bg-gray-100"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/order-requests')}"
                >
                  <span>📋 Order Requests</span>
                  <span
                    v-if="writerQueueCounts.requests > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-800"
                  >
                    {{ writerQueueCounts.requests }}
                  </span>
                </router-link>
                <router-link
                  to="/writer/orders?status=revision_requested"
                  class="flex items-center justify-between px-3 py-2 text-sm rounded hover:bg-gray-100"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.query.status === 'revision_requested'}"
                >
                  <span>⚠️ Revision Requests</span>
                  <span
                    v-if="writerRevisionRequestsCount > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800"
                  >
                    {{ writerRevisionRequestsCount }}
                  </span>
                </router-link>
                <router-link to="/writer/workload" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/workload')}">⚖️ Workload & Capacity</router-link>
                <router-link to="/writer/calendar" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/calendar')}">📅 Deadline Calendar</router-link>
                <router-link to="/writer/deadline-extensions" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/deadline-extensions')}">⏰ Deadline Extensions</router-link>
                <router-link to="/writer/order-holds" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/order-holds')}">🛑 Hold Requests</router-link>
              </div>
            </div>

            <!-- Finances Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerFinancesOpen = !writerFinancesOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">💰</span>
                  Finances
                </span>
                <span>{{ writerFinancesOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerFinancesOpen" class="ml-6 space-y-1">
                <router-link to="/writer/payments" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/payments')}">💳 Payments</router-link>
                <router-link to="/writer/payment-request" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/payment-request')}">💳 Payment Requests</router-link>
                <router-link to="/writer/advance-payments" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/advance-payments')}">💸 Advance Payments</router-link>
                <router-link to="/writer/tips" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tips')}">💰 Tips</router-link>
                <router-link to="/writer/fines" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-red-50 text-red-700 font-medium': $route.path.startsWith('/writer/fines')}">🚫 Fines & Appeals</router-link>
              </div>
            </div>

            <!-- Reviews & Ratings Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerReviewsOpen = !writerReviewsOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">⭐</span>
                  Reviews & Ratings
                </span>
                <span>{{ writerReviewsOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerReviewsOpen" class="ml-6 space-y-1">
                <router-link to="/writer/reviews" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/reviews')}">⭐ My Reviews</router-link>
                <router-link to="/writer/performance" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/performance')}">📊 Performance</router-link>
                <router-link to="/writer/badges" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/badges')}">🏆 Badges</router-link>
                <router-link to="/writer/badge-analytics" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/badge-analytics')}">📈 Badge Analytics</router-link>
                <router-link to="/writer/level-details" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/level-details')}">🏅 Level Details</router-link>
              </div>
            </div>

            <!-- User Management Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerUserManagementOpen = !writerUserManagementOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">👤</span>
                  User Management
                </span>
                <span>{{ writerUserManagementOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerUserManagementOpen" class="ml-6 space-y-1">
                <router-link to="/writer/profile-settings" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/profile-settings')}">⚙️ Profile Settings</router-link>
                <router-link to="/writer/pen-name" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/pen-name')}">✏️ Pen Name Management</router-link>
                <router-link to="/writer/resources" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/resources')}">📚 Resources & Guides</router-link>
              </div>
            </div>

            <!-- Activity Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerActivityOpen = !writerActivityOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">📊</span>
                  Activity
                </span>
                <span>{{ writerActivityOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerActivityOpen" class="ml-6 space-y-1">
                <router-link to="/writer/dashboard-summary" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/dashboard-summary')}">📊 Dashboard Summary</router-link>
                <router-link to="/writer/communications" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/communications')}">💬 Communications</router-link>
                <router-link to="/writer/tickets" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tickets')}">🎫 My Tickets</router-link>
                <router-link to="/activity" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/activity')}">📊 Activity Logs</router-link>
              </div>
            </div>

            <!-- Discipline Group -->
            <div class="space-y-1 mb-4">
              <button @click="writerDisciplineOpen = !writerDisciplineOpen" class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100">
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">⚖️</span>
                  Discipline
                </span>
                <span>{{ writerDisciplineOpen ? '▾' : '▸' }}</span>
              </button>
              <div v-if="writerDisciplineOpen" class="ml-6 space-y-1">
                <router-link to="/writer/discipline-status" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/discipline-status')}">📜 Status & History</router-link>
                <router-link to="/writer/tickets" class="block px-3 py-2 text-sm rounded hover:bg-gray-100" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tickets')}">📝 Submit Appeal</router-link>
              </div>
            </div>
          </template>

          <!-- Admin/Superadmin Grouped Navigation -->
          <template v-if="authStore.isAdmin || authStore.isSuperAdmin">
            <!-- Core Operations Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>⚙️</span>
                  Core Operations
                </h3>
              </div>
              <div class="space-y-1">
                <!-- Orders Section -->
                <div class="space-y-1">
                  <button 
                    @click="adminGroups.orders = !adminGroups.orders" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                  >
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">📝</span>
                  Orders
                </span>
                    <span class="text-xs">{{ adminGroups.orders ? '▾' : '▸' }}</span>
              </button>
                  <div v-if="adminGroups.orders" class="ml-6 space-y-1">
                    <router-link 
                      to="/admin/orders" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                      :class="isRouteActive({ to: '/admin/orders' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      📋 All Orders
                    </router-link>
                    <router-link 
                      to="/admin/orders?status=pending" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      ⏳ Pending
                    </router-link>
                    <router-link 
                      to="/admin/orders?status=in_progress" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      ⚙️ In Progress
                    </router-link>
                    <router-link 
                      to="/admin/orders?status=completed" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      ✅ Completed
                    </router-link>
                    <router-link 
                      to="/admin/orders?status=disputed" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      ⚠️ Disputed
                </router-link>
              </div>
            </div>
            
                <!-- Special Orders -->
                <router-link
                  to="/admin/special-orders"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/special-orders' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">⭐</span>
                  Special Orders
                </router-link>
                
                <!-- Users Section -->
                <div class="space-y-1">
                  <button 
                    @click="adminGroups.users = !adminGroups.users" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                  >
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">👥</span>
                  Users
                </span>
                    <span class="text-xs">{{ adminGroups.users ? '▾' : '▸' }}</span>
              </button>
                  <div v-if="adminGroups.users" class="ml-6 space-y-1">
                    <router-link 
                      to="/admin/users" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                      :class="isRouteActive({ to: '/admin/users' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      All Users
                    </router-link>
                    <router-link 
                      to="/admin/users?role=client" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      👤 Clients
                    </router-link>
                    <router-link 
                      to="/admin/users?role=writer" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      ✍️ Writers
                    </router-link>
                    <router-link 
                      to="/admin/users?role=editor" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      📝 Editors
                    </router-link>
                    <router-link 
                      to="/admin/users?role=support" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      🎧 Support
                    </router-link>
                    <router-link 
                      v-if="authStore.isSuperAdmin"
                      to="/admin/users?role=admin" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      👔 Admins
                    </router-link>
              </div>
            </div>
            
                <!-- Support Tickets -->
              <router-link
                  to="/admin/support-tickets"
                :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/support-tickets' })
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                  <span class="w-5 h-5 mr-3">🎫</span>
                  Support Tickets
              </router-link>
              </div>
            </div>
            
            <!-- Financial Management Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>💰</span>
                  Financial
                </h3>
              </div>
              <div class="space-y-1">
                <div class="space-y-1">
                  <button 
                    @click="adminGroups.payments = !adminGroups.payments" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                  >
                <span class="flex items-center">
                  <span class="w-5 h-5 mr-3">💳</span>
                  Payments
                </span>
                    <span class="text-xs">{{ adminGroups.payments ? '▾' : '▸' }}</span>
              </button>
                  <div v-if="adminGroups.payments" class="ml-6 space-y-1">
                <router-link
                  to="/admin/payments/writer-payments"
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                      :class="isRouteActive({ to: '/admin/payments/writer-payments' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      Writer Payments
                    </router-link>
                    <router-link 
                      to="/admin/payments/batched" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      Payment Management
                    </router-link>
                    <router-link 
                      to="/admin/payments/all" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      All Payments
                    </router-link>
                    <router-link 
                      to="/admin/payments/logs" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      Payment Logs
                    </router-link>
                    <router-link 
                      to="/admin/financial-overview" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      Financial Overview
                    </router-link>
                  </div>
                </div>
                
                <router-link
                  to="/admin/refunds"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/refunds' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">↩️</span>
                  Refunds
                </router-link>
                
                <router-link
                  to="/admin/disputes"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/disputes' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">⚖️</span>
                  Disputes
                </router-link>
                
                <router-link
                  to="/admin/tips"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/tips' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">💸</span>
                  Tips
                </router-link>
                
                <router-link
                  to="/admin/fines"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/fines' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🚫</span>
                  Fines
                </router-link>
                
                <router-link
                  to="/admin/holidays"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/holidays' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🎉</span>
                  Holidays & Campaigns
                </router-link>
                
                <router-link
                  to="/admin/advance-payments"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/advance-payments' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">💵</span>
                  Advance Payments
                </router-link>
                
                <router-link
                  to="/admin/wallets"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/wallets' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">💼</span>
                  Wallets
                </router-link>
                
                <router-link
                  to="/admin/invoices"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/invoices' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📄</span>
                  Invoices
                </router-link>
              </div>
            </div>
            
            <!-- Content & Services Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>📝</span>
                  Content & Services
                </h3>
              </div>
              <div class="space-y-1">
                <div class="space-y-1">
                  <button 
                    @click="adminGroups.reviews = !adminGroups.reviews" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors text-gray-700 hover:bg-gray-100"
                  >
                <span class="flex items-center">
                      <span class="w-5 h-5 mr-3">💬</span>
                      Reviews
                </span>
                    <span class="text-xs">{{ adminGroups.reviews ? '▾' : '▸' }}</span>
              </button>
                  <div v-if="adminGroups.reviews" class="ml-6 space-y-1">
                    <router-link 
                      to="/admin/reviews" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      All Reviews
                    </router-link>
                    <router-link 
                      to="/admin/reviews/moderation" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      Moderation
                    </router-link>
                    <router-link 
                      to="/admin/review-aggregation" 
                      class="block px-3 py-2 text-sm rounded hover:bg-gray-100"
                    >
                      Aggregation
                    </router-link>
                  </div>
                </div>
                
                <router-link
                  to="/admin/class-management"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/class-management' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📚</span>
                  Class Management
                </router-link>
                
                <router-link
                  to="/admin/express-classes"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/express-classes' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">⚡</span>
                  Express Classes
                </router-link>
                
                <router-link
                  to="/admin/blog"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/blog' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📝</span>
                  Blog Pages
                </router-link>
                
                <router-link
                  to="/admin/seo-pages"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/seo-pages' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🔍</span>
                  SEO Pages
                </router-link>
                
                <router-link
                  to="/admin/files"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/files' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📁</span>
                  File Management
                </router-link>
              </div>
            </div>

            <!-- Analytics & Reporting Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>📊</span>
                  Analytics
                </h3>
              </div>
              <div class="space-y-1">
                <router-link
                  to="/admin/advanced-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/advanced-analytics' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📈</span>
                  Advanced Analytics
                </router-link>
                
                <router-link
                  to="/admin/enhanced-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/enhanced-analytics' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📉</span>
                  Enhanced Analytics
                </router-link>
                
                <router-link
                  to="/admin/pricing-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/pricing-analytics' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">💰</span>
                  Pricing Analytics
                </router-link>
                
                <router-link
                  to="/admin/discount-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/discount-analytics' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🎟️</span>
                  Discount Analytics
                </router-link>
                
                <router-link
                  to="/admin/writer-performance"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/writer-performance' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">👤</span>
                  Writer Performance
                </router-link>
                
                <router-link
                  to="/admin/referral-tracking"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/referral-tracking' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🎁</span>
                  Referral Tracking
                </router-link>
                
                <router-link
                  to="/admin/loyalty-tracking"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/loyalty-tracking' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">⭐</span>
                  Loyalty Tracking
                </router-link>
                
                <router-link
                  to="/admin/loyalty-management"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/loyalty-management' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🏆</span>
                  Loyalty Management
                </router-link>
                
                <router-link
                  to="/admin/campaigns"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/campaigns' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📢</span>
                  Campaign Analytics
                </router-link>
              </div>
            </div>

            <!-- System Management Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>⚙️</span>
                  System
                </h3>
              </div>
              <div class="space-y-1">
                <router-link
                  to="/admin/configs"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/configs' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🎛️</span>
                  Configurations
                </router-link>
                
                <router-link
                  to="/admin/system-health"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/system-health' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🏥</span>
                  System Health
                </router-link>
                
                <router-link
                  to="/admin/activity-logs"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/activity-logs' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📋</span>
                  Activity Logs
                </router-link>
                
                <router-link
                  to="/admin/emails"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/emails' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📧</span>
                  Email Management
                </router-link>
                
                <router-link
                  to="/admin/notification-profiles"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/notification-profiles' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🔔</span>
                  Notification Profiles
                </router-link>
                
                <router-link
                  to="/admin/notification-groups"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/notification-groups' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">👥</span>
                  Notification Groups
                </router-link>
                
                <router-link
                  to="/admin/duplicate-detection"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/duplicate-detection' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🔍</span>
                  Duplicate Detection
                </router-link>
              </div>
            </div>

            <!-- Discipline & Appeals Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>⚖️</span>
                  Discipline
                </h3>
              </div>
              <div class="space-y-1">
                <router-link
                  to="/admin/writer-discipline"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/writer-discipline' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📜</span>
                  Writer Discipline
                </router-link>
                
                <router-link
                  to="/admin/appeals"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/appeals' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">📝</span>
                  Appeals
                </router-link>
                
                <router-link
                  to="/admin/discipline-config"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/discipline-config' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">⚙️</span>
                  Discipline Config
                </router-link>
              </div>
            </div>

            <!-- Multi-Tenant Group -->
            <div class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>🌐</span>
                  Multi-Tenant
                </h3>
              </div>
              <div class="space-y-1">
                <router-link
                  to="/websites"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/websites' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">🌐</span>
                  Websites
                </router-link>
              </div>
            </div>

            <!-- Superadmin Only -->
            <div v-if="authStore.isSuperAdmin" class="mb-6">
              <div class="px-4 py-2 mb-2">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <span>👑</span>
                  Superadmin
                </h3>
              </div>
              <div class="space-y-1">
                <router-link
                  to="/admin/superadmin"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
                    isRouteActive({ to: '/admin/superadmin' })
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  ]"
                >
                  <span class="w-5 h-5 mr-3">👑</span>
                  Superadmin Dashboard
                </router-link>
              </div>
            </div>
          </template>

          <!-- Other navigation items (profile/settings/privacy/security for all, tickets/etc for non-admin) -->
          <template v-for="item in navigationItems">
            <router-link
              v-if="
                (
                  // Tickets / notifications / general activity only for non-admin users
                  !authStore.isAdmin &&
                  !authStore.isSuperAdmin &&
                  (item.name === 'Tickets' || item.name === 'Notifications' || item.name === 'ActivityLogsGeneral')
                )
                ||
                (
                  // Profile & account links for all roles (including admin/superadmin)
                  item.name === 'Profile' ||
                  item.name === 'Settings' ||
                  item.name === 'PrivacySettings' ||
                  item.name === 'SecurityActivity'
                )
              "
              :key="item.name"
              :to="item.to"
              :class="[
                'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                isRouteActive(item)
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              ]"
            >
              <span 
                :class="[
                  'w-5 h-5 mr-3 flex items-center justify-center text-base leading-none select-none',
                  isRouteActive(item)
                    ? 'opacity-100'
                    : 'opacity-75 hover:opacity-100'
                ]"
              >{{ item.icon || '📋' }}</span>
              {{ item.label }}
            </router-link>
          </template>
        </nav>

        <!-- User section -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                <span class="text-primary-600 text-sm font-medium">
                  {{ userInitials }}
                </span>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ authStore.user?.email }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ authStore.userRole }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="authStore.isImpersonating" class="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
            Impersonating as {{ authStore.user?.email }}
          </div>

          <button
            @click="handleLogout"
            class="w-full btn btn-secondary text-sm"
          >
            Sign Out
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="lg:pl-64 h-screen overflow-hidden flex flex-col">
      <!-- Top bar -->
      <header class="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="lg:hidden text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div class="flex-1 flex items-center justify-between">
            <div class="hidden sm:block text-sm text-gray-500 dark:text-gray-400">
              <span class="font-medium text-gray-700 dark:text-gray-100">{{ $route.meta.title || 'Dashboard' }}</span>
            </div>
            <div class="flex items-center space-x-4 flex-1 max-w-2xl mx-4">
              <!-- Global Search -->
              <div class="flex-1 max-w-xl">
                <GlobalSearch />
              </div>
            <!-- Activity & Theme -->
            <div class="relative">
              <button
                @click="toggleTheme"
                class="mr-3 text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100"
                :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
              >
                <span v-if="isDark">🌙</span>
                <span v-else>☀️</span>
              </button>
              <button 
                @click="toggleActivitiesDropdown"
                class="relative text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100 focus:outline-none"
                title="User Activity"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-label="Activity">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </button>
              
              <!-- Activities Dropdown -->
              <div
                v-if="showActivitiesDropdown"
                ref="activitiesDropdownRef"
                class="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-hidden flex flex-col"
              >
                <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <h3 class="font-semibold text-gray-900 dark:text-gray-100">Activities</h3>
                  <button
                    @click="closeActivitiesDropdown"
                    class="text-gray-400 hover:text-gray-600"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div class="overflow-y-auto flex-1">
                  <div v-if="activitiesLoading" class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  </div>
                  <div v-else-if="recentActivities.length === 0" class="text-center py-8 text-gray-500 text-sm">
                    No activities
                  </div>
                  <div v-else class="divide-y divide-gray-100">
                    <div
                      v-for="activity in recentActivities"
                      :key="activity.id"
                      class="p-3 hover:bg-gray-50 transition-colors"
                    >
                      <div class="flex items-start gap-2">
                        <div class="flex-1 min-w-0">
                          <div class="flex items-center gap-2 mb-1">
                            <span 
                              :class="getRoleBadgeClass(activity.user_role)"
                              class="px-1.5 py-0.5 rounded text-xs font-medium"
                            >
                              {{ activity.user_role || 'user' }}
                            </span>
                            <span class="text-xs text-gray-500 truncate">
                              {{ activity.user_email || 'N/A' }}
                            </span>
                          </div>
                          <p class="text-sm text-gray-900 line-clamp-2">
                            {{ activity.display_description || activity.description || 'No description' }}
                          </p>
                          <p class="text-xs text-gray-400 mt-1">
                            {{ formatActivityDate(activity.timestamp || activity.formatted_timestamp) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="p-3 border-t border-gray-200 bg-gray-50">
                  <router-link
                    to="/activity"
                    @click="closeActivitiesDropdown"
                    class="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    All activities →
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Notifications -->
            <div class="relative">
              <button 
                @click="toggleNotificationsDropdown"
                class="relative text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span 
                  v-if="unreadCount > 0"
                  class="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-5 px-1.5 text-xs font-bold text-white bg-red-600 rounded-full ring-2 ring-white"
                >
                  {{ unreadCount > 99 ? '99+' : unreadCount }}
                </span>
              </button>
              
              <!-- Notifications Dropdown -->
              <div
                v-if="showNotificationsDropdown"
                ref="notificationsDropdownRef"
                class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-hidden flex flex-col"
              >
                <div class="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 class="font-semibold text-gray-900">Notifications</h3>
                  <div class="flex items-center gap-2">
                    <button
                      v-if="unreadCount > 0"
                      @click="markAllNotificationsRead"
                      :disabled="markingAllRead"
                      class="text-xs text-primary-600 hover:text-primary-700 disabled:opacity-50"
                    >
                      {{ markingAllRead ? 'Marking...' : 'Mark all read' }}
                    </button>
                    <button
                      @click="closeNotificationsDropdown"
                      class="text-gray-400 hover:text-gray-600"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                <div class="overflow-y-auto flex-1">
                  <div v-if="notificationsLoading" class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  </div>
                  <div v-else-if="recentNotifications.length === 0" class="text-center py-8 text-gray-500 text-sm">
                    No notifications
                  </div>
                  <div v-else class="divide-y divide-gray-100">
                    <div
                      v-for="notif in recentNotifications"
                      :key="notif.id"
                      :class="[
                        'p-3 hover:bg-gray-50 cursor-pointer transition-colors',
                        !notif.is_read ? 'bg-blue-50' : ''
                      ]"
                      @click="handleNotificationClick(notif)"
                    >
                      <div class="flex items-start gap-2">
                        <div v-if="!notif.is_read" class="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 line-clamp-1">
                            {{ notif.title }}
                          </p>
                          <p class="text-xs text-gray-600 mt-1 line-clamp-2">
                            {{ notif.message }}
                          </p>
                          <p class="text-xs text-gray-400 mt-1">
                            {{ notif.time_ago || formatNotificationDate(notif.created_at) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="p-3 border-t border-gray-200 bg-gray-50">
                  <router-link
                    to="/notifications"
                    @click="closeNotificationsDropdown"
                    class="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    View all notifications
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Profile menu -->
            <div class="relative">
              <button
                @click="toggleProfileDropdown"
                class="flex items-center text-sm text-gray-700 hover:text-gray-900 focus:outline-none"
              >
                <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center relative">
                  <span class="text-primary-600 text-sm font-medium">
                    {{ userInitials }}
                  </span>
                  <span 
                    v-if="unreadCount > 0"
                    class="absolute -top-1 -right-1 w-3 h-3 bg-red-600 rounded-full ring-2 ring-white"
                  ></span>
                </div>
              </button>
              
              <!-- Profile Dropdown -->
              <div
                v-if="showProfileDropdown"
                ref="profileDropdownRef"
                class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
              >
                <div class="p-2">
                  <router-link
                    :to="authStore.isWriter ? '/writer/profile-settings' : '/profile'"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Profile Settings
                  </router-link>
                  <router-link
                    to="/notifications"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg flex items-center justify-between"
                  >
                    <span>Notifications</span>
                    <span v-if="unreadCount > 0" class="px-2 py-0.5 text-xs font-bold text-white bg-red-600 rounded-full">
                      {{ unreadCount > 99 ? '99+' : unreadCount }}
                    </span>
                  </router-link>
                  <router-link
                    to="/account/settings"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Settings
                  </router-link>
                  <router-link
                    to="/account/privacy"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Privacy & Security
                  </router-link>
                  <router-link
                    to="/account/security"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg"
                  >
                    Security Activity
                  </router-link>
                  <div class="border-t border-gray-200 my-1"></div>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <router-view />
      </main>
    </div>
    
    <!-- Session Timeout Warning -->
    <SessionTimeoutWarning
      :show="showSessionWarning"
      :remaining-seconds="sessionRemainingSeconds"
      @stay-logged-in="handleStayLoggedIn"
      @logout-now="handleSessionLogout"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getAccessibleRoutes } from '@/utils/permissions'
import notificationsAPI from '@/api/notifications'
import activityAPI from '@/api/activity-logs'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import SessionTimeoutWarning from '@/components/common/SessionTimeoutWarning.vue'
import sessionManager from '@/services/sessionManager'
import { useTheme } from '@/composables/useTheme'
import writerDashboardAPI from '@/api/writer-dashboard'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { isDark, toggleTheme } = useTheme()
const sidebarOpen = ref(false)
const ordersOpen = ref(true)
const orderManagementOpen = ref(false)
const usersOpen = ref(false)
const paymentsOpen = ref(false)
const configsOpen = ref(false)

// Admin navigation groups state
const adminGroups = ref({
  orders: false,
  users: false,
  payments: false,
  reviews: false,
})

// Auto-expand admin groups based on current route
watch(() => route.path, (newPath) => {
  if (authStore.isAdmin || authStore.isSuperAdmin) {
    // Auto-expand relevant groups based on current route
    if (newPath.startsWith('/admin/orders')) {
      adminGroups.value.orders = true
    }
    if (newPath.startsWith('/admin/users')) {
      adminGroups.value.users = true
    }
    if (newPath.startsWith('/admin/payments') || newPath.startsWith('/admin/refunds') || newPath.startsWith('/admin/disputes') || newPath.startsWith('/admin/tips') || newPath.startsWith('/admin/fines') || newPath.startsWith('/admin/advance-payments') || newPath.startsWith('/admin/wallets') || newPath.startsWith('/admin/invoices') || newPath.startsWith('/admin/financial-overview')) {
      adminGroups.value.payments = true
    }
    if (newPath.startsWith('/admin/reviews')) {
      adminGroups.value.reviews = true
    }
  }
}, { immediate: true })

// Writer sidebar groups - open Orders by default for better UX
const writerOrdersOpen = ref(true)
const writerFinancesOpen = ref(false)
const writerReviewsOpen = ref(false)
const writerUserManagementOpen = ref(false)
const writerActivityOpen = ref(false)
const writerDisciplineOpen = ref(false)

// Writer sidebar smart counts
const writerQueueCounts = ref({
  available: 0,
  preferred: 0,
  requests: 0,
})
const writerRevisionRequestsCount = ref(0)

const loadWriterSidebarMetrics = async () => {
  if (!authStore.isWriter) return
  try {
    const [queueResp, summaryResp] = await Promise.all([
      writerDashboardAPI.getOrderQueue().catch(() => null),
      writerDashboardAPI.getDashboardSummary().catch(() => null),
    ])

    if (queueResp && queueResp.data) {
      const data = queueResp.data
      const available = Array.isArray(data.available_orders) ? data.available_orders.length : 0
      const preferred = Array.isArray(data.preferred_orders) ? data.preferred_orders.length : 0
      const orderRequests = Array.isArray(data.order_requests) ? data.order_requests : []
      const writerRequests = Array.isArray(data.writer_requests) ? data.writer_requests : []
      const allRequests = [...orderRequests, ...writerRequests]

      writerQueueCounts.value = {
        available,
        preferred,
        requests: allRequests.length,
      }
    }

    if (summaryResp && summaryResp.data) {
      const summary = summaryResp.data
      if (Array.isArray(summary.revision_requests)) {
        writerRevisionRequestsCount.value = summary.revision_requests.length
      } else if (typeof summary.revision_requests_count === 'number') {
        writerRevisionRequestsCount.value = summary.revision_requests_count
      } else {
        writerRevisionRequestsCount.value = 0
      }
    }
  } catch (error) {
    // Sidebar should fail silently if metrics can't be loaded
    console.error('Failed to load writer sidebar metrics:', error)
  }
}

// Notifications state
const showNotificationsDropdown = ref(false)
const showProfileDropdown = ref(false)
const unreadCount = ref(0)
const recentNotifications = ref([])
const notificationsLoading = ref(false)
const markingAllRead = ref(false)
const notificationsDropdownRef = ref(null)
const profileDropdownRef = ref(null)

// Activities state
const showActivitiesDropdown = ref(false)
const recentActivities = ref([])
const activitiesLoading = ref(false)
const activitiesDropdownRef = ref(null)

// Session timeout state
const showSessionWarning = ref(false)
const sessionRemainingSeconds = ref(0)
let unreadCountInterval = null
let unreadCountBackoffDelay = 60000 // Start with 60 seconds (1 minute)
const MAX_BACKOFF_DELAY = 300000 // Max 5 minutes
const BACKOFF_MULTIPLIER = 2

const appName = import.meta.env.VITE_APP_NAME || 'Writing System'

const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return 'U'
  const name = user.full_name || user.email || 'User'
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const navigationItems = computed(() => {
  const role = authStore.userRole
  const accessibleRoutes = getAccessibleRoutes(role) || []
  
  const allItems = [
    {
      name: 'Dashboard',
      to: '/dashboard',
      label: 'Dashboard',
      icon: '📊',
    },
    // Orders - only show for non-clients (clients have collapsible section)
    {
      name: 'Orders',
      to: '/orders',
      label: 'Orders',
      icon: '📝',
      roles: ['admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'Tickets',
      to: '/tickets',
      label: 'Tickets',
      icon: '🎫',
      roles: ['client', 'admin', 'support'],
    },
    {
      name: 'ConfigManagement',
      to: '/admin/configs',
      label: 'Configurations',
      icon: '🎛️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'OrderManagement',
      to: '/admin/orders',
      label: 'Order Management',
      icon: '📋',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'SpecialOrderManagement',
      to: '/admin/special-orders',
      label: 'Special Orders',
      icon: '⭐',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ClassManagement',
      to: '/admin/class-management',
      label: 'Class Management',
      icon: '📚',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ExpressClassesManagement',
      to: '/admin/express-classes',
      label: 'Express Classes',
      icon: '⚡',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ReviewsManagement',
      to: '/admin/reviews',
      label: 'Reviews Management',
      icon: '💬',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'RefundManagement',
      to: '/admin/refunds',
      label: 'Refund Management',
      icon: '💰',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'DisputeManagement',
      to: '/admin/disputes',
      label: 'Dispute Management',
      icon: '⚖️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'TipManagement',
      to: '/admin/tips',
      label: 'Tip Management',
      icon: '💸',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'FileManagement',
      to: '/admin/files',
      label: 'File Management',
      icon: '📁',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'FinesManagement',
      to: '/admin/fines',
      label: 'Fines Management',
      icon: '⚖️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'SystemHealth',
      to: '/admin/system-health',
      label: 'System Health',
      icon: '🏥',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'AdvancePaymentsManagement',
      to: '/admin/advance-payments',
      label: 'Advance Payments',
      icon: '💵',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ActivityLogs',
      to: '/admin/activity-logs',
      label: 'Activity Logs',
      icon: '📋',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'SupportTicketsManagement',
      to: '/admin/support-tickets',
      label: 'Support Tickets',
      icon: '🎫',
      roles: ['admin', 'superadmin', 'support'],
    },
    {
      name: 'DiscountAnalytics',
      to: '/admin/discount-analytics',
      label: 'Discount Analytics',
      icon: '📊',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'DiscountManagement',
      to: '/admin/discounts',
      label: 'Discount Management',
      icon: '🎟️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'PromotionalCampaignManagement',
      to: '/admin/campaigns',
      label: 'Promotional Campaigns',
      icon: '📢',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WriterPerformanceAnalytics',
      to: '/admin/writer-performance',
      label: 'Writer Performance',
      icon: '👥',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WriterManagement',
      to: '/admin/users?role=writer',
      label: 'Writer Management',
      icon: '✍️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WriterHierarchy',
      to: '/admin/writer-hierarchy',
      label: 'Writer Hierarchy',
      icon: '📊',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WriterDisciplineManagement',
      to: '/admin/writer-discipline',
      label: 'Writer Discipline',
      icon: '⚠️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'DisciplineConfig',
      to: '/admin/discipline-config',
      label: 'Discipline Config',
      icon: '⚙️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'AppealsManagement',
      to: '/admin/appeals',
      label: 'Appeals',
      icon: '📋',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'DuplicateAccountDetection',
      to: '/admin/duplicate-detection',
      label: 'Duplicate Detection',
      icon: '🔍',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ReferralTracking',
      to: '/admin/referral-tracking',
      label: 'Referral Tracking',
      icon: '🔗',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'LoyaltyTracking',
      to: '/admin/loyalty-tracking',
      label: 'Loyalty Tracking',
      icon: '⭐',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'LoyaltyManagement',
      to: '/admin/loyalty-management',
      label: 'Loyalty Management',
      icon: '⭐',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'AdvancedAnalytics',
      to: '/admin/advanced-analytics',
      label: 'Advanced Analytics',
      icon: '📊',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'SuperadminDashboard',
      to: '/admin/superadmin',
      label: 'Superadmin Dashboard',
      icon: '👑',
      roles: ['superadmin'],
    },
    {
      name: 'ReviewAggregation',
      to: '/admin/review-aggregation',
      label: 'Review Aggregation',
      icon: '⭐',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'PricingAnalytics',
      to: '/admin/pricing-analytics',
      label: 'Pricing Analytics',
      icon: '💰',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'EnhancedAnalytics',
      to: '/admin/enhanced-analytics',
      label: 'Enhanced Analytics',
      icon: '📊',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'EmailManagement',
      to: '/admin/emails',
      label: 'Email Management',
      icon: '📧',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'BlogManagement',
      to: '/admin/blog',
      label: 'Blog Pages',
      icon: '📝',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'SEOPagesManagement',
      to: '/admin/seo-pages',
      label: 'SEO Pages',
      icon: '🔍',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WalletManagement',
      to: '/admin/wallets',
      label: 'Wallet Management',
      icon: '💰',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WebsiteManagement',
      to: '/websites',
      label: 'Websites',
      icon: '🌐',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'Profile',
      to: '/profile',
      label: 'Profile',
      icon: '⚙️',
    },
    {
      name: 'Settings',
      to: '/account/settings',
      label: 'Settings',
      icon: '🔧',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'PrivacySettings',
      to: '/account/privacy',
      label: 'Privacy & Security',
      icon: '🔒',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'SecurityActivity',
      to: '/account/security',
      label: 'Security Activity',
      icon: '🛡️',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    // Payments - handled as collapsible section for admin/superadmin, regular link for clients
    {
      name: 'Payments',
      to: '/payments',
      label: 'Payments',
      icon: '💳',
      roles: ['client'],
    },
    // Referrals and Loyalty are client-only features
    // They are accessed via direct links in the client account section (lines 102-125)
    // Admins/Superadmins have access to tracking dashboards only (ReferralTracking, LoyaltyTracking)
    {
      name: 'Messages',
      to: '/messages',
      label: 'Messages',
      icon: '💬',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'Notifications',
      to: '/notifications',
      label: 'Notifications',
      icon: '🔔',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'ActivityLogsGeneral',
      to: '/activity',
      label: 'User Activity',
      icon: '📊',
      roles: ['admin', 'superadmin', 'support', 'writer', 'client', 'editor'],
    },
    // Writer items are now grouped in the sidebar template, but keep them here for filtering
    // They won't be rendered as individual items since they're in collapsible groups
    {
      name: 'EditorTasks',
      to: '/editor/tasks',
      label: 'My Tasks',
      icon: '📝',
      roles: ['editor'],
    },
    {
      name: 'SupportTicketQueue',
      to: '/support/queue',
      label: 'Ticket Queue',
      icon: '🎫',
      roles: ['support', 'admin', 'superadmin'],
    },
    {
      name: 'SupportTickets',
      to: '/support/tickets',
      label: 'Recent Tickets',
      icon: '📋',
      roles: ['support', 'admin', 'superadmin'],
    },
    {
      name: 'EditorAvailableTasks',
      to: '/editor/available-tasks',
      label: 'Available Tasks',
      icon: '🔍',
      roles: ['editor'],
    },
    {
      name: 'EditorPerformance',
      to: '/editor/performance',
      label: 'Performance',
      icon: '📊',
      roles: ['editor'],
    },
    {
      name: 'Wallet',
      to: '/wallet',
      label: 'My Wallet',
      icon: '💼',
      roles: ['client'],
    },
  ]
  
  return allItems.filter(item => {
    if (!item.roles) return true
    return item.roles.includes(role)
  })
})

onMounted(() => {
  // Existing mounted logic (session, notifications, etc.) is above;
  // here we only trigger writer-specific sidebar metrics.
  loadWriterSidebarMetrics()
})

// Helper function to check if a route is active
const isRouteActive = (item) => {
  if (!item || !item.to) return false
  // Check by route name first (most reliable)
  if (item.name && route.name === item.name) {
    return true
  }
  // Fallback: check by path (handles cases where route name might not match exactly)
  const currentPath = route.path
  const itemPath = item.to.split('?')[0] // Remove query params
  if (currentPath === itemPath || currentPath.startsWith(itemPath + '/')) {
    return true
  }
  // Also check if current path matches with query params
  if (item.to.includes('?') && currentPath === itemPath) {
    const itemParams = new URLSearchParams(item.to.split('?')[1])
    const currentParams = new URLSearchParams(route.query)
    // Check if all item params are present in current params
    let allMatch = true
    for (const [key, value] of itemParams.entries()) {
      if (currentParams.get(key) !== value) {
        allMatch = false
        break
      }
    }
    if (allMatch) return true
  }
  return false
}

const updateExpandedSections = (path) => {
  if (!path) return
  if (path.startsWith('/admin/orders') || path.startsWith('/admin/special-orders')) {
    orderManagementOpen.value = true
  }
  if (path.startsWith('/admin/users')) {
    usersOpen.value = true
  }
  if (path.startsWith('/admin/payments') || path.startsWith('/admin/financial-overview')) {
    paymentsOpen.value = true
  }
  if (path.startsWith('/admin/configs')) {
    configsOpen.value = true
  }
  // Also expand orders section for client orders
  if (path.startsWith('/orders') && authStore.isClient) {
    ordersOpen.value = true
  }
  
  // Writer groups
  if (authStore.isWriter) {
    // Orders group - expand for writer orders pages AND general order detail pages
    if (path.startsWith('/writer/orders') || path.startsWith('/writer/queue') || 
        path.startsWith('/writer/order-requests') || path.startsWith('/writer/workload') || 
        path.startsWith('/writer/calendar') || path.includes('revision_requested') ||
        (path.startsWith('/orders') && /^\/orders\/\d+/.test(path))) {
      writerOrdersOpen.value = true
    }
    // Finances group
    if (path.startsWith('/writer/payments') || path.startsWith('/writer/payment-request') || 
        path.startsWith('/writer/advance-payments') || path.startsWith('/writer/tips') || path.startsWith('/writer/fines')) {
      writerFinancesOpen.value = true
    }
    // Reviews group
    if (path.startsWith('/writer/reviews') || path.startsWith('/writer/performance') || 
        path.startsWith('/writer/badges')) {
      writerReviewsOpen.value = true
    }
    // User Management group
    if (path.startsWith('/writer/profile-settings') || path.startsWith('/writer/pen-name') || 
        path.startsWith('/writer/resources')) {
      writerUserManagementOpen.value = true
    }
    // Activity group
    if (path.startsWith('/writer/communications') || path.startsWith('/writer/tickets') || 
        path.startsWith('/activity')) {
      writerActivityOpen.value = true
    }
  }
}

watch(
  () => route.path,
  (path) => {
    updateExpandedSections(path)
  },
  { immediate: true }
)

// Handle click outside for dropdowns
const handleClickOutside = (event) => {
  if (showNotificationsDropdown.value && notificationsDropdownRef.value) {
    if (!notificationsDropdownRef.value.contains(event.target) && 
        !event.target.closest('button[class*="relative"]')) {
      closeNotificationsDropdown()
    }
  }
  if (showActivitiesDropdown.value && activitiesDropdownRef.value) {
    if (!activitiesDropdownRef.value.contains(event.target) && 
        !event.target.closest('button[class*="relative"]')) {
      closeActivitiesDropdown()
    }
  }
  if (showProfileDropdown.value && profileDropdownRef.value) {
    if (!profileDropdownRef.value.contains(event.target) && 
        !event.target.closest('button[class*="flex items-center"]')) {
      closeProfileDropdown()
    }
  }
}

// Notifications functions with exponential backoff for rate limiting
const loadUnreadCount = async () => {
  if (!authStore.isAuthenticated) {
    unreadCount.value = 0
    return
  }
  try {
    const response = await notificationsAPI.getUnreadCount()
    unreadCount.value = response.data.unread_count || response.data.count || 0
    // Reset backoff on successful request
    unreadCountBackoffDelay = 60000
  } catch (error) {
    // Handle 429 (Too Many Requests) gracefully with exponential backoff
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      if (retryAfter) {
        // Use server-suggested retry delay
        unreadCountBackoffDelay = parseInt(retryAfter) * 1000
      } else {
        // Apply exponential backoff
        unreadCountBackoffDelay = Math.min(
          unreadCountBackoffDelay * BACKOFF_MULTIPLIER,
          MAX_BACKOFF_DELAY
        )
      }
      // Silently handle rate limiting - don't log as error
      // The polling will automatically use the increased delay
      return
    }
    // Only log non-rate-limit errors
    if (error.response?.status !== 429) {
      console.error('Failed to load unread count:', error)
    }
  }
}

const loadRecentNotifications = async () => {
  if (!authStore.isAuthenticated) {
    recentNotifications.value = []
    return
  }
  if (notificationsLoading.value) return
  notificationsLoading.value = true
  try {
    const response = await notificationsAPI.getNotifications({
      limit: 5
    })
    
    // Handle both paginated (results) and non-paginated (array) responses
    let feedItems = []
    if (Array.isArray(response.data)) {
      // Non-paginated response
      feedItems = response.data
    } else if (response.data.results && Array.isArray(response.data.results)) {
      // Paginated response
      feedItems = response.data.results
    } else if (response.data && typeof response.data === 'object') {
      // Single item or unexpected structure, try to extract
      feedItems = [response.data]
    }
    
    // Transform to flat structure for easier display
    // Feed endpoint returns NotificationFeedItemSerializer
    // Structure: { id (status id), notification: {...}, is_read, pinned, ... }
    recentNotifications.value = feedItems.slice(0, 5).map(item => {
      // Handle both feed item format (with nested notification) and direct notification format
      const notification = item.notification || item
      return {
        id: notification.id || item.id,
        statusId: item.id, // Keep status ID for marking as read (from NotificationFeedItemSerializer)
        title: notification.title || notification.rendered_title || 'Notification',
        message: notification.message || notification.rendered_message || notification.description || '',
        link: notification.link || notification.rendered_link || null,
        created_at: notification.created_at || notification.sent_at || item.created_at,
        is_read: item.is_read !== undefined ? item.is_read : (notification.is_read || false),
        pinned: item.pinned || false,
        category: notification.category || 'general',
        priority: notification.priority || item.priority || 'normal',
        priority_label: notification.priority_label || null,
        event: notification.event || null,
        time_ago: notification.time_ago || null
      }
    })
  } catch (error) {
    console.error('Failed to load notifications:', error)
    recentNotifications.value = []
  } finally {
    notificationsLoading.value = false
  }
}

const toggleNotificationsDropdown = async () => {
  showNotificationsDropdown.value = !showNotificationsDropdown.value
  if (showNotificationsDropdown.value) {
    await loadRecentNotifications()
  }
  // Close profile dropdown if open
  if (showProfileDropdown.value) {
    showProfileDropdown.value = false
  }
  // Close activities dropdown if open
  if (showActivitiesDropdown.value) {
    showActivitiesDropdown.value = false
  }
}

const closeNotificationsDropdown = () => {
  showNotificationsDropdown.value = false
}

const toggleProfileDropdown = () => {
  showProfileDropdown.value = !showProfileDropdown.value
  // Close notifications dropdown if open
  if (showNotificationsDropdown.value) {
    showNotificationsDropdown.value = false
  }
  // Close activities dropdown if open
  if (showActivitiesDropdown.value) {
    showActivitiesDropdown.value = false
  }
}

const closeProfileDropdown = () => {
  showProfileDropdown.value = false
}

const handleNotificationClick = async (notification) => {
  // Mark as read if unread (use statusId if available, otherwise notification ID)
  if (!notification.is_read) {
    try {
      if (notification.statusId) {
        // Use status-based endpoint
        await notificationsAPI.markAsRead(notification.statusId)
      } else {
        // Fallback to notification ID endpoint
        await notificationsAPI.markNotificationAsRead(notification.id)
      }
      notification.is_read = true
      await loadUnreadCount()
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }
  
  // Navigate to notification link if available
  if (notification.link) {
    const link = notification.link
    if (link.startsWith('http')) {
      window.open(link, '_blank')
    } else {
      router.push(link)
    }
  } else {
    // Navigate to notifications page
    router.push('/notifications')
  }
  
  closeNotificationsDropdown()
}

const markAllNotificationsRead = async () => {
  if (markingAllRead.value) return
  markingAllRead.value = true
  try {
    await notificationsAPI.markAllAsRead()
    // Update local state
    recentNotifications.value.forEach(notif => {
      notif.is_read = true
    })
    unreadCount.value = 0
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  } finally {
    markingAllRead.value = false
  }
}

const formatNotificationDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

// Activities functions
const loadRecentActivities = async () => {
  if (activitiesLoading.value) return
  activitiesLoading.value = true
  try {
    const response = await activityAPI.list({ limit: 5 })
    
    // Handle both paginated (results) and non-paginated (array) responses
    let activities = []
    if (Array.isArray(response.data)) {
      activities = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      activities = response.data.results
    } else {
      activities = []
    }
    
    recentActivities.value = activities.slice(0, 5)
  } catch (error) {
    console.error('Failed to load activities:', error)
    recentActivities.value = []
  } finally {
    activitiesLoading.value = false
  }
}

const toggleActivitiesDropdown = async () => {
  showActivitiesDropdown.value = !showActivitiesDropdown.value
  if (showActivitiesDropdown.value) {
    await loadRecentActivities()
  }
  // Close notifications dropdown if open
  if (showNotificationsDropdown.value) {
    showNotificationsDropdown.value = false
  }
  // Close profile dropdown if open
  if (showProfileDropdown.value) {
    showProfileDropdown.value = false
  }
}

const closeActivitiesDropdown = () => {
  showActivitiesDropdown.value = false
}

const formatActivityDate = (dateString) => {
  if (!dateString) return ''
  
  let date
  
  // If it's already formatted (from backend), try to parse it
  // Format: "05:55 16, Nov 2025"
  if (typeof dateString === 'string' && dateString.includes(',') && dateString.includes(':')) {
    try {
      // Parse format like "05:55 16, Nov 2025"
      const match = dateString.match(/(\d{2}):(\d{2}) (\d+), (\w+) (\d+)/)
      if (match) {
        const [, hour, minute, day, month, year] = match
        const monthMap = {
          'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
          'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
          'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        const monthNum = monthMap[month] || '01'
        // Create ISO string: YYYY-MM-DDTHH:mm:ss
        const isoString = `${year}-${monthNum}-${day.padStart(2, '0')}T${hour}:${minute}:00`
        date = new Date(isoString)
      } else {
        date = new Date(dateString)
      }
    } catch (e) {
      date = new Date(dateString)
    }
  } else {
    // For ISO date strings
    date = new Date(dateString)
  }
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    return dateString
  }
  
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} minutes ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  
  return date.toLocaleDateString()
}

const getRoleBadgeClass = (role) => {
  const classes = {
    admin: 'bg-red-100 text-red-700',
    superadmin: 'bg-purple-100 text-purple-700',
    client: 'bg-blue-100 text-blue-700',
    writer: 'bg-green-100 text-green-700',
    editor: 'bg-indigo-100 text-indigo-700',
    support: 'bg-yellow-100 text-yellow-700',
    user: 'bg-gray-100 text-gray-700',
  }
  return classes[role?.toLowerCase()] || 'bg-gray-100 text-gray-700'
}

const handleLogout = async () => {
  closeNotificationsDropdown()
  closeActivitiesDropdown()
  closeProfileDropdown()
  sessionManager.stop() // Stop session monitoring
  await authStore.logout()
  router.push('/login')
}

// Session timeout handlers
const handleSessionWarning = (remainingSeconds) => {
  sessionRemainingSeconds.value = remainingSeconds
  showSessionWarning.value = true
}

const handleSessionLogout = () => {
  showSessionWarning.value = false
  handleLogout()
}

const handleStayLoggedIn = () => {
  showSessionWarning.value = false
}

// Close sidebar on route change (mobile)
router.afterEach(() => {
  if (window.innerWidth < 1024) {
    sidebarOpen.value = false
  }
})

// Close sidebar on outside click (mobile)
onMounted(() => {
  const handleSidebarClickOutside = (e) => {
    if (window.innerWidth < 1024 && sidebarOpen.value) {
      const sidebar = document.querySelector('aside')
      if (sidebar && !sidebar.contains(e.target) && !e.target.closest('button')) {
        sidebarOpen.value = false
      }
    }
  }
  document.addEventListener('click', handleSidebarClickOutside)
  document.addEventListener('click', handleClickOutside)
  
  // Load initial unread count
  loadUnreadCount()
  
  // Poll for unread count with adaptive interval (starts at 60 seconds)
  // Interval adjusts based on rate limiting (exponential backoff)
  const scheduleNextPoll = () => {
    if (unreadCountInterval) {
      clearTimeout(unreadCountInterval)
    }
    unreadCountInterval = setTimeout(() => {
      loadUnreadCount().finally(() => {
        scheduleNextPoll()
      })
    }, unreadCountBackoffDelay)
  }
  
  // Start adaptive polling
  scheduleNextPoll()
  
  // Also reload when route changes (user might have read notifications)
  router.afterEach(() => {
    loadUnreadCount()
  })
  
  // Start session timeout monitoring
  if (authStore.isAuthenticated) {
    sessionManager.start(handleSessionWarning, handleSessionLogout)
  }
})

onUnmounted(() => {
  if (unreadCountInterval) {
    clearTimeout(unreadCountInterval)
    unreadCountInterval = null
  }
  document.removeEventListener('click', handleClickOutside)
  sessionManager.stop() // Stop session monitoring
})
</script>

