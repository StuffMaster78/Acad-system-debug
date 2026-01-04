<template>
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-300 overflow-hidden">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 bg-gradient-to-b from-white to-gray-50 dark:from-[#0f0f0f] dark:to-[#1a1a1a] border-r border-gray-200/50 dark:border-gray-800/50 backdrop-blur-sm transform transition-all duration-300 ease-in-out shadow-xl',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'lg:translate-x-0',
        sidebarCollapsed ? 'w-20' : 'w-72'
      ]"
      :aria-label="sidebarCollapsed ? 'Collapsed navigation sidebar' : 'Navigation sidebar'"
      role="navigation"
    >
      <div class="flex flex-col h-full">
        <!-- Logo & Toggle - Compact -->
        <div class="flex items-center justify-between h-16 px-3 border-b border-gray-200/60 dark:border-gray-800/60 bg-white/80 dark:bg-[#0f0f0f]/80 backdrop-blur-md transition-colors duration-300">
          <Logo 
            :size="'md'"
            :variant="'gradient'"
            :show-text="true"
            :collapsed="sidebarCollapsed"
          />
          <button
            @click="sidebarCollapsed = !sidebarCollapsed"
            class="hidden lg:flex p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 shrink-0 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
            :aria-label="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
            :aria-expanded="!sidebarCollapsed"
          >
            <svg v-if="!sidebarCollapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
          <button
            @click="sidebarOpen = false"
            class="lg:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            aria-label="Close sidebar"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Sidebar Search (All roles) - Compact -->
        <div v-show="!sidebarCollapsed" class="px-3 pt-3 pb-2 border-b border-gray-200/60 dark:border-gray-800/60 transition-all duration-300">
          <div class="relative">
            <input
              ref="sidebarSearchInput"
              v-model="sidebarSearchQuery"
              type="text"
              :placeholder="`Search menu... (${isMac ? '⌘' : 'Ctrl'}+K)`"
              class="w-full px-3 py-2 pl-9 pr-3 text-[13px] font-normal leading-normal bg-white/60 dark:bg-gray-900/60 border border-gray-200/80 dark:border-gray-700/80 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 transition-all duration-200 placeholder-gray-400 dark:placeholder-gray-500 backdrop-blur-sm shadow-sm hover:shadow-md hover:border-gray-300 dark:hover:border-gray-600 search-input"
              aria-label="Search navigation menu"
            />
            <svg class="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button
              v-if="sidebarSearchQuery"
              @click="clearSearch"
              class="absolute right-3 top-3 w-4 h-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-0.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
              title="Clear search"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <!-- Collapsed Search Button -->
        <div v-show="sidebarCollapsed" class="px-3 pt-5 pb-4 border-b border-gray-200/60 dark:border-gray-800/60">
          <button
            @click="sidebarCollapsed = false"
            class="w-full p-2.5 rounded-xl text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            title="Search menu"
            aria-label="Expand sidebar to search"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>

        <!-- Navigation - Compact -->
        <nav class="flex-1 px-3 py-3 space-y-1 overflow-y-auto custom-scrollbar scroll-smooth" aria-label="Main navigation">
          <!-- Dashboard - Always at top -->
          <SidebarTooltip :text="'Dashboard'" :collapsed="sidebarCollapsed">
            <router-link
              to="/dashboard"
              :class="[
                'flex items-center rounded-lg transition-all duration-200 mb-3 group relative overflow-hidden leading-tight focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-1 dark:focus:ring-offset-gray-900',
                $route.name === 'Dashboard' || $route.path === '/dashboard'
                  ? 'bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 text-white shadow-md shadow-primary-500/20'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80 hover:shadow-sm',
                sidebarCollapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
              ]"
              :aria-label="sidebarCollapsed ? 'Dashboard' : undefined"
            >
            <div :class="[
              'flex items-center justify-center transition-all duration-300 shrink-0 rounded-md',
              $route.name === 'Dashboard' || $route.path === '/dashboard' 
                ? 'bg-white/20' 
                : 'bg-gray-100 dark:bg-gray-800 group-hover:bg-primary-50 dark:group-hover:bg-primary-900/20',
              sidebarCollapsed ? 'mr-0 w-8 h-8' : 'mr-2.5 w-8 h-8'
            ]">
              <svg class="w-4 h-4" :class="$route.name === 'Dashboard' || $route.path === '/dashboard' ? 'text-white' : 'text-gray-600 dark:text-gray-400 group-hover:text-primary-600 dark:group-hover:text-primary-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            </div>
              <span v-show="!sidebarCollapsed" :class="[
                'text-[13px] font-medium transition-opacity duration-300',
                $route.name === 'Dashboard' || $route.path === '/dashboard' ? 'font-semibold' : ''
              ]">Dashboard</span>
            </router-link>
          </SidebarTooltip>

          <!-- Place New Order Button - Prominent at top (Client) - Compact -->
          <div v-if="authStore.isClient" class="mb-3">
            <SidebarTooltip :text="'Place New Order'" :collapsed="sidebarCollapsed">
              <router-link
                to="/orders/wizard"
                :class="[
                  'flex items-center justify-center w-full py-2 text-[13px] font-medium rounded-lg transition-all duration-200 bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 hover:shadow-md active:scale-[0.98] shadow-md shadow-primary-500/20 group leading-tight focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-1 dark:focus:ring-offset-gray-900',
                  sidebarCollapsed ? 'px-2' : 'px-3'
                ]"
                :aria-label="sidebarCollapsed ? 'Place New Order' : undefined"
              >
              <svg class="w-4 h-4 transition-transform duration-300 group-hover:scale-110 shrink-0" :class="sidebarCollapsed ? '' : 'mr-2'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
                <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Place New Order</span>
                <span v-show="!sidebarCollapsed" class="ml-1.5 px-1.5 py-0.5 text-[9px] font-semibold bg-yellow-400/90 text-yellow-900 rounded-full shadow-sm tracking-wide">NEW</span>
              </router-link>
            </SidebarTooltip>
          </div>

          <!-- Create Order Button - Prominent at top (Admin/SuperAdmin) -->
          <div v-if="authStore.isAdmin || authStore.isSuperAdmin" class="mb-5">
            <SidebarTooltip :text="'Create Order'" :collapsed="sidebarCollapsed">
              <router-link
                to="/admin/orders/create"
                :class="[
                  'flex items-center justify-center w-full py-3 text-sm font-semibold rounded-xl transition-all duration-300 bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-primary-500/25 group leading-relaxed focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
                  sidebarCollapsed ? 'px-2' : 'px-4'
                ]"
                :aria-label="sidebarCollapsed ? 'Create Order' : undefined"
              >
              <svg class="w-4.5 h-4.5 transition-transform duration-300 group-hover:scale-110 shrink-0" :class="sidebarCollapsed ? '' : 'mr-2.5'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
                <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Create Order</span>
                <span v-show="!sidebarCollapsed" class="ml-2 px-2 py-0.5 text-[10px] font-bold bg-yellow-400/90 text-yellow-900 rounded-full shadow-sm tracking-wide">NEW</span>
              </router-link>
            </SidebarTooltip>
          </div>

          <!-- Orders section - Simplified and at top - Compact -->
          <div v-if="authStore.isClient && shouldShowItem('Orders', 'All Orders Pending In Progress Completed Disputed Templates')" class="space-y-1 mb-3">
            <div v-show="!sidebarCollapsed" class="px-3 py-1.5 mb-1">
              <h3 class="text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider leading-tight">
                Orders
              </h3>
            </div>
            <SidebarTooltip :text="'Orders'" :collapsed="sidebarCollapsed">
              <button 
                @click="ordersOpen = !ordersOpen"
                :aria-expanded="ordersOpen"
                :aria-label="sidebarCollapsed ? 'Orders menu' : undefined"
                :class="[
                  'w-full flex items-center justify-between rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 active:scale-[0.99] group leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-1 dark:focus:ring-offset-gray-900',
                  sidebarCollapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
                ]"
              >
              <span class="flex items-center">
                  <div :class="[
                    'flex items-center justify-center rounded-md bg-blue-100/80 dark:bg-blue-900/30 group-hover:bg-blue-200 dark:group-hover:bg-blue-800/50 transition-colors duration-300 shrink-0',
                    sidebarCollapsed ? 'w-8 h-8' : 'w-8 h-8 mr-2.5'
                  ]">
                    <SidebarIcon icon-name="clipboard-list" size="sm" icon-class="text-blue-600 dark:text-blue-400" />
                  </div>
                  <span v-show="!sidebarCollapsed" class="text-[13px] font-medium transition-opacity duration-300">Orders</span>
              </span>
                <ChevronIcon v-show="!sidebarCollapsed" :is-open="ordersOpen" size="sm" class="text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors shrink-0" />
              </button>
            </SidebarTooltip>
            <div v-if="ordersOpen && !sidebarCollapsed" class="ml-4 space-y-1.5 animate-fade-in mt-3 pl-3 border-l-3 border-blue-300/60 dark:border-blue-700/60">
              <!-- Quick Access -->
              <router-link v-if="shouldShowItem('All Orders', 'View all your orders')" :to="authStore.isClient ? '/client/orders' : '/orders'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:translate-x-1 hover:shadow-sm group leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && !$route.query.status && !$route.query.is_paid ? 'bg-blue-50/90 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-semibold shadow-sm border-l-2 border-blue-500' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && !$route.query.status && !$route.query.is_paid ? 'bg-blue-100 dark:bg-blue-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30'">
                      <SidebarIcon icon-name="clipboard-list" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && !$route.query.status && !$route.query.is_paid ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400'" tooltip="View all your orders" />
                    </div>
                    <span class="truncate">All Orders</span>
                  </div>
                <span v-if="orderStatusCounts.total > 0" class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 shadow-sm shrink-0">
                  {{ orderStatusCounts.total }}
                </span>
              </router-link>
              
              <!-- Payment Status -->
              <div class="pt-3 mt-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <div class="px-3.5 py-1.5 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 leading-tight">Payment</div>
                <router-link v-if="shouldShowItem('Unpaid', 'Orders awaiting payment')" :to="authStore.isClient ? '/client/orders?is_paid=false' : '/orders?is_paid=false'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-orange-50/80 dark:hover:bg-orange-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 leading-relaxed focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'false' ? 'bg-orange-50/90 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 font-semibold border-l-3 border-orange-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'false' ? 'bg-orange-100 dark:bg-orange-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-orange-100 dark:group-hover:bg-orange-900/30'">
                      <SidebarIcon icon-name="credit-card" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'false' ? 'text-orange-600 dark:text-orange-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-orange-600 dark:group-hover:text-orange-400'" tooltip="Orders awaiting payment" />
                    </div>
                    <span class="truncate">Unpaid <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.unpaid }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Paid', 'Paid orders')" :to="authStore.isClient ? '/client/orders?is_paid=true' : '/orders?is_paid=true'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-green-50/80 dark:hover:bg-green-900/20 hover:translate-x-1 hover:shadow-sm group leading-relaxed focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'true' ? 'bg-green-50/90 dark:bg-green-900/40 text-green-700 dark:text-green-300 font-semibold border-l-3 border-green-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'true' ? 'bg-green-100 dark:bg-green-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-green-100 dark:group-hover:bg-green-900/30'">
                      <SidebarIcon icon-name="check-circle" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.is_paid === 'true' ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-green-600 dark:group-hover:text-green-400'" tooltip="Paid orders" />
                    </div>
                    <span class="truncate">Paid <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.paid }})</span></span>
                  </div>
              </router-link>
              </div>
              
              <!-- Active Orders -->
              <div class="pt-3 mt-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <div class="px-3.5 py-1.5 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 leading-tight">Active</div>
                <router-link v-if="shouldShowItem('Pending', 'Pending orders')" :to="authStore.isClient ? '/client/orders?status=pending' : '/orders?status=pending'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-yellow-50/80 dark:hover:bg-yellow-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 leading-relaxed focus:outline-none focus:ring-2 focus:ring-yellow-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'pending' ? 'bg-yellow-50/90 dark:bg-yellow-900/40 text-yellow-700 dark:text-yellow-300 font-semibold border-l-3 border-yellow-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-yellow-100 dark:group-hover:bg-yellow-900/30'">
                      <SidebarIcon icon-name="clock" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-yellow-600 dark:group-hover:text-yellow-400'" tooltip="Pending orders" />
                    </div>
                    <span class="truncate">Pending <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.pending }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('In Progress', 'Orders in progress')" :to="authStore.isClient ? '/client/orders?status=in_progress' : '/orders?status=in_progress'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium rounded-lg transition-all duration-300 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'in_progress' ? 'bg-blue-50/90 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-semibold border-l-3 border-blue-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'in_progress' ? 'bg-blue-100 dark:bg-blue-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30'">
                      <SidebarIcon icon-name="cog" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'in_progress' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400'" class="animate-spin-slow" tooltip="Orders in progress" />
                    </div>
                    <span class="truncate">In Progress <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.in_progress }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Submitted', 'Submitted orders')" :to="authStore.isClient ? '/client/orders?status=submitted' : '/orders?status=submitted'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-indigo-50/80 dark:hover:bg-indigo-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'submitted' ? 'bg-indigo-50/90 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-semibold border-l-3 border-indigo-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'submitted' ? 'bg-indigo-100 dark:bg-indigo-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900/30'">
                      <SidebarIcon icon-name="paper-airplane" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'submitted' ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'" tooltip="Submitted orders" />
                    </div>
                    <span class="truncate">Submitted <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.submitted }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Under Editing', 'Orders under editing')" :to="authStore.isClient ? '/client/orders?status=under_editing' : '/orders?status=under_editing'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-purple-50/80 dark:hover:bg-purple-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'under_editing' ? 'bg-purple-50/90 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 font-semibold border-l-3 border-purple-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'under_editing' ? 'bg-purple-100 dark:bg-purple-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30'">
                      <SidebarIcon icon-name="pencil" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'under_editing' ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400'" tooltip="Orders under editing" />
                    </div>
                    <span class="truncate">Under Editing <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.under_editing }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Available', 'Available orders')" :to="authStore.isClient ? '/client/orders?status=available' : '/orders?status=available'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-emerald-50/80 dark:hover:bg-emerald-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'available' ? 'bg-emerald-50/90 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 font-semibold border-l-3 border-emerald-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'available' ? 'bg-emerald-100 dark:bg-emerald-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-emerald-100 dark:group-hover:bg-emerald-900/30'">
                      <SidebarIcon icon-name="clipboard" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'available' ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-emerald-600 dark:group-hover:text-emerald-400'" tooltip="Available orders" />
                    </div>
                    <span class="truncate">Available <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.available }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('On Hold', 'Orders on hold')" :to="authStore.isClient ? '/client/orders?status=on_hold' : '/orders?status=on_hold'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-orange-50/80 dark:hover:bg-orange-900/20 hover:translate-x-1 hover:shadow-sm group focus:outline-none focus:ring-2 focus:ring-orange-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'on_hold' ? 'bg-orange-50/90 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300 font-semibold border-l-3 border-orange-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'on_hold' ? 'bg-orange-100 dark:bg-orange-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-orange-100 dark:group-hover:bg-orange-900/30'">
                      <SidebarIcon icon-name="clock" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'on_hold' ? 'text-orange-600 dark:text-orange-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-orange-600 dark:group-hover:text-orange-400'" tooltip="Orders on hold" />
                    </div>
                    <span class="truncate">On Hold <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.on_hold }})</span></span>
                  </div>
              </router-link>
              </div>
              
              <!-- Completed -->
              <div class="pt-3 mt-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <div class="px-3.5 py-2 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider leading-tight mb-2">Completed</div>
                <router-link v-if="shouldShowItem('Completed', 'Completed orders')" :to="authStore.isClient ? '/client/orders?status=completed' : '/orders?status=completed'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-green-50/80 dark:hover:bg-green-900/20 hover:translate-x-1 hover:shadow-sm group focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'completed' ? 'bg-green-50/90 dark:bg-green-900/40 text-green-700 dark:text-green-300 font-semibold border-l-3 border-green-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'completed' ? 'bg-green-100 dark:bg-green-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-green-100 dark:group-hover:bg-green-900/30'">
                      <SidebarIcon icon-name="check-circle" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-green-600 dark:group-hover:text-green-400'" tooltip="Completed orders" />
                    </div>
                    <span class="truncate">Completed <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.completed }})</span></span>
                  </div>
              </router-link>
              </div>
              
              <!-- Issues -->
              <div class="pt-3 mt-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <div class="px-3.5 py-2 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider leading-tight mb-2">Issues</div>
                <router-link v-if="shouldShowItem('Revision Requested', 'Orders requiring revision')" :to="authStore.isClient ? '/client/orders?status=revision_requested' : '/orders?status=revision_requested'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-amber-50/80 dark:hover:bg-amber-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'revision_requested' ? 'bg-amber-50/90 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 font-semibold border-l-3 border-amber-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'revision_requested' ? 'bg-amber-100 dark:bg-amber-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-amber-100 dark:group-hover:bg-amber-900/30'">
                      <SidebarIcon icon-name="arrow-left" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'revision_requested' ? 'text-amber-600 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-amber-600 dark:group-hover:text-amber-400'" tooltip="Orders requiring revision" />
                    </div>
                    <span class="truncate">Revision Requested <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.revision_requested }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Disputed', 'Disputed orders')" :to="authStore.isClient ? '/client/orders?status=disputed' : '/orders?status=disputed'" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-red-50/80 dark:hover:bg-red-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'disputed' ? 'bg-red-50/90 dark:bg-red-900/40 text-red-700 dark:text-red-300 font-semibold border-l-3 border-red-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'disputed' ? 'bg-red-100 dark:bg-red-800/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-red-100 dark:group-hover:bg-red-900/30'">
                      <SidebarIcon icon-name="exclamation-triangle" size="sm" :icon-class="(authStore.isClient ? $route.path === '/client/orders' : $route.path === '/orders') && $route.query.status === 'disputed' ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400'" tooltip="Disputed orders" />
                    </div>
                    <span class="truncate">Disputed <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.disputed }})</span></span>
                  </div>
              </router-link>
                <router-link v-if="shouldShowItem('Cancelled', 'Cancelled orders')" to="/orders?status=cancelled" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-gray-100/80 dark:hover:bg-gray-800/80 hover:translate-x-1 hover:shadow-sm group focus:outline-none focus:ring-2 focus:ring-gray-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900" :class="$route.path === '/orders' && $route.query.status === 'cancelled' ? 'bg-gray-100/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 font-semibold border-l-3 border-gray-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300" :class="$route.path === '/orders' && $route.query.status === 'cancelled' ? 'bg-gray-200 dark:bg-gray-700/50' : 'bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-gray-200 dark:group-hover:bg-gray-700/50'">
                      <SidebarIcon icon-name="ban" size="sm" :icon-class="$route.path === '/orders' && $route.query.status === 'cancelled' ? 'text-gray-600 dark:text-gray-400' : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-400'" tooltip="Cancelled orders" />
                    </div>
                    <span class="truncate">Cancelled <span class="text-gray-500 dark:text-gray-400">({{ orderStatusCounts.cancelled }})</span></span>
                  </div>
                </router-link>
              </div>
              
              <!-- Order Transitions (Admin/SuperAdmin only) -->
              <div v-if="(authStore.isAdmin || authStore.isSuperAdmin) && hasTransitionCounts" class="pt-3 mt-2 border-t border-gray-200/50 dark:border-gray-700/50">
                <div class="px-3.5 py-2 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider leading-tight mb-2">Available Transitions</div>
                
                <router-link v-if="orderStatusCounts.can_transition_to_in_progress > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-blue-50/80 dark:hover:bg-blue-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" tooltip="Orders that can transition to In Progress" />
                    </div>
                    <span class="truncate text-xs">→ In Progress</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_in_progress }}
                  </span>
                </router-link>
                
                <router-link v-if="orderStatusCounts.can_transition_to_submitted > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-purple-50/80 dark:hover:bg-purple-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-purple-100 dark:group-hover:bg-purple-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" tooltip="Orders that can transition to Submitted" />
                    </div>
                    <span class="truncate text-xs">→ Submitted</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_submitted }}
                  </span>
                </router-link>
                
                <router-link v-if="orderStatusCounts.can_transition_to_completed > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-green-50/80 dark:hover:bg-green-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-green-100 dark:group-hover:bg-green-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-green-600 dark:group-hover:text-green-400" tooltip="Orders that can transition to Completed" />
                    </div>
                    <span class="truncate text-xs">→ Completed</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-green-100 dark:bg-green-900/60 text-green-800 dark:text-green-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_completed }}
                  </span>
                </router-link>
                
                <router-link v-if="orderStatusCounts.can_transition_to_on_hold > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-orange-50/80 dark:hover:bg-orange-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-orange-100 dark:group-hover:bg-orange-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-orange-600 dark:group-hover:text-orange-400" tooltip="Orders that can transition to On Hold" />
                    </div>
                    <span class="truncate text-xs">→ On Hold</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-orange-100 dark:bg-orange-900/60 text-orange-800 dark:text-orange-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_on_hold }}
                  </span>
                </router-link>
                
                <router-link v-if="orderStatusCounts.can_transition_to_revision_requested > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-yellow-50/80 dark:hover:bg-yellow-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-yellow-100 dark:group-hover:bg-yellow-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-yellow-600 dark:group-hover:text-yellow-400" tooltip="Orders that can transition to Revision Requested" />
                    </div>
                    <span class="truncate text-xs">→ Revision</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-yellow-100 dark:bg-yellow-900/60 text-yellow-800 dark:text-yellow-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_revision_requested }}
                  </span>
                </router-link>
                
                <router-link v-if="orderStatusCounts.can_transition_to_cancelled > 0" to="/admin/orders" class="flex items-center justify-between px-3.5 py-2 text-sm font-medium leading-relaxed rounded-lg transition-all duration-300 hover:bg-red-50/80 dark:hover:bg-red-900/20 hover:translate-x-1 hover:shadow-sm group mb-1.5" :class="'text-gray-700 dark:text-gray-300'">
                  <div class="flex items-center min-w-0 flex-1">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-4 transition-colors duration-300 bg-gray-100/80 dark:bg-gray-800/50 group-hover:bg-red-100 dark:group-hover:bg-red-900/30">
                      <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-gray-500 dark:text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400" tooltip="Orders that can transition to Cancelled" />
                    </div>
                    <span class="truncate text-xs">→ Cancelled</span>
                  </div>
                  <span class="ml-2.5 px-2 py-0.5 text-[11px] font-semibold rounded-full bg-red-100 dark:bg-red-900/60 text-red-800 dark:text-red-200 shadow-sm shrink-0">
                    {{ orderStatusCounts.can_transition_to_cancelled }}
                  </span>
                </router-link>
              </div>
              
              <div class="border-t border-gray-200 dark:border-gray-700 my-2"></div>
              
              <!-- Link to view all statuses on orders page -->
              <router-link v-if="shouldShowItem('View All Statuses', 'View all order statuses')" to="/orders" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-primary-50 hover:translate-x-1 text-primary-600 font-medium group">
                <SidebarIcon icon-name="search" size="sm" icon-class="text-primary-600 mr-3" tooltip="View all order statuses" />
                View All Statuses
                <SidebarIcon icon-name="arrow-right" size="sm" icon-class="text-primary-600 ml-auto" />
              </router-link>
              
              <div class="border-t border-gray-200 dark:border-gray-700 my-2"></div>
              
              <!-- Order Templates -->
              <router-link v-if="shouldShowItem('Order Templates', 'Manage order templates')" to="/orders/templates" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-primary-50 hover:translate-x-1 font-medium text-primary-600 group">
                <SidebarIcon icon-name="template" size="sm" icon-class="text-primary-600" class="mr-4" tooltip="Manage order templates" />
                  Order Templates
              </router-link>
            </div>
          </div>

          <!-- Client Account section (Wallet, Referrals, Loyalty) -->
          <div v-if="authStore.isClient && shouldShowItem('Account', 'Wallet Referrals Loyalty Discounts')" class="space-y-1.5 mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
            <div class="px-4 py-3 mb-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <h3 class="text-xs font-bold text-green-700 dark:text-green-300 uppercase tracking-widest flex items-center gap-2">
                <SidebarIcon icon-name="wallet" size="sm" icon-class="text-green-600 dark:text-green-400" />
                <span>Account</span>
              </h3>
            </div>
            <router-link
              v-if="shouldShowItem('My Wallet', 'Manage your wallet and balance')"
              to="/wallet"
              :class="[
                'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 leading-relaxed group',
                $route.name === 'Wallet'
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
              ]"
            >
              <SidebarIcon icon-name="wallet" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-4" tooltip="Manage your wallet and balance" />
              My Wallet
            </router-link>
            <router-link
              v-if="shouldShowItem('Payment History', 'View all your payments and receipts')"
              to="/payments"
              :class="[
                'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 leading-relaxed group',
                $route.name === 'Payments'
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
              ]"
            >
              <SidebarIcon
                icon-name="credit-card"
                size="md"
                icon-class="text-gray-600 group-hover:text-primary-600 mr-3"
                tooltip="View all your payments and receipts"
              />
              Payment History
            </router-link>
            <router-link
              v-if="shouldShowItem('Referrals', 'Refer friends and earn rewards')"
              to="/referrals"
              :class="[
                'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 leading-relaxed group',
                $route.name === 'Referrals'
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
              ]"
            >
              <SidebarIcon icon-name="gift" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Refer friends and earn rewards" />
              Referrals
            </router-link>
            <router-link
              v-if="shouldShowItem('Loyalty Program', 'View loyalty points and rewards')"
              to="/loyalty"
              :class="[
                'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 leading-relaxed group',
                $route.name === 'Loyalty'
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
              ]"
            >
              <SidebarIcon icon-name="star" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-3" tooltip="View loyalty points and rewards" />
              Loyalty Program
            </router-link>
            <router-link
              v-if="shouldShowItem('Discounts', 'Available discounts and coupons')"
              to="/discounts"
              :class="[
                'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 leading-relaxed group',
                $route.name === 'ClientDiscounts'
                  ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
              ]"
            >
              <SidebarIcon icon-name="discount" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Available discounts and coupons" />
              Discounts
            </router-link>
          </div>

          <!-- Writer Groups - Organized by category -->
          <template v-if="authStore.isWriter">
            <!-- Orders Group -->
            <div v-if="shouldShowItem('Orders & Work', 'My Orders Queue Requests Revision Workload Calendar')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-blue-700 dark:text-blue-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="clipboard-list" size="sm" icon-class="text-blue-600 dark:text-blue-400" />
                  <span>Orders & Work</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Orders & Work'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerOrdersOpen = !writerOrdersOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="clipboard-list" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Orders</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerOrdersOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerOrdersOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link
                  v-if="shouldShowItem('My Orders', 'View all your orders')"
                  to="/writer/orders"
                  class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/orders')}"
                >
                  <SidebarIcon icon-name="clipboard" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View all your orders" />
                  My Orders
                </router-link>
                <router-link
                  v-if="shouldShowItem('Order Queue', 'Available orders in queue')"
                  to="/writer/queue"
                  class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/queue')}"
                >
                  <div class="flex items-center">
                    <SidebarIcon icon-name="clipboard" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Available orders in queue" />
                    Order Queue
                  </div>
                  <span
                    v-if="writerQueueCounts.available + writerQueueCounts.preferred > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 animate-pulse"
                  >
                    {{ writerQueueCounts.available + writerQueueCounts.preferred }}
                  </span>
                </router-link>
                <router-link
                  v-if="shouldShowItem('Order Requests', 'Order requests from clients')"
                  to="/writer/order-requests"
                  class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/order-requests')}"
                >
                  <div class="flex items-center">
                    <SidebarIcon icon-name="clipboard" size="sm" icon-class="text-gray-500 group-hover:text-indigo-600 mr-3" tooltip="Order requests from clients" />
                    Order Requests
                  </div>
                  <span
                    v-if="writerQueueCounts.requests > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-800 animate-pulse"
                  >
                    {{ writerQueueCounts.requests }}
                  </span>
                </router-link>
                <router-link
                  v-if="shouldShowItem('Revision Requests', 'Orders requiring revision')"
                  to="/writer/orders?status=revision_requested"
                  class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                  :class="{'bg-primary-50 text-primary-700 font-medium': $route.query.status === 'revision_requested'}"
                >
                  <div class="flex items-center">
                    <SidebarIcon icon-name="exclamation-triangle" size="sm" icon-class="text-gray-500 group-hover:text-amber-600 mr-3" tooltip="Orders requiring revision" />
                    Revision Requests
                  </div>
                  <span
                    v-if="writerRevisionRequestsCount > 0"
                    class="ml-2 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 animate-pulse"
                  >
                    {{ writerRevisionRequestsCount }}
                  </span>
                </router-link>
                <router-link v-if="shouldShowItem('Workload & Capacity', 'Manage workload and capacity')" to="/writer/workload" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/workload')}">
                  <SidebarIcon icon-name="scale" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage workload and capacity" />
                  Workload & Capacity
                </router-link>
                <router-link v-if="shouldShowItem('Deadline Calendar', 'View deadline calendar')" to="/writer/calendar" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/calendar')}">
                  <SidebarIcon icon-name="calendar" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View deadline calendar" />
                  Deadline Calendar
                </router-link>
                <router-link v-if="shouldShowItem('Deadline Extensions', 'Request deadline extensions')" to="/writer/deadline-extensions" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/deadline-extensions')}">
                  <SidebarIcon icon-name="clock-alarm" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Request deadline extensions" />
                  Deadline Extensions
                </router-link>
                <router-link v-if="shouldShowItem('Hold Requests', 'Request order holds')" to="/writer/order-holds" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/order-holds')}">
                  <SidebarIcon icon-name="stop" size="sm" icon-class="text-gray-500 group-hover:text-red-600 mr-3" tooltip="Request order holds" />
                  Hold Requests
                </router-link>
              </div>
            </div>

            <!-- Finances Group -->
            <div v-if="shouldShowItem('Finances', 'Payments Payment Requests Advance Payments Tips Fines')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-green-700 dark:text-green-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="wallet" size="sm" icon-class="text-green-600 dark:text-green-400" />
                  <span>Finances</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Finances'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerFinancesOpen = !writerFinancesOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="wallet" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Finances</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerFinancesOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerFinancesOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link v-if="shouldShowItem('Payments', 'View payment history')" to="/writer/payments" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/payments')}">
                  <SidebarIcon icon-name="credit-card" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View payment history" />
                  Payments
                </router-link>
                <router-link v-if="shouldShowItem('Payment Requests', 'Request payments')" to="/writer/payment-request" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/payment-request')}">
                  <SidebarIcon icon-name="credit-card" size="sm" icon-class="text-gray-500 group-hover:text-indigo-600 mr-3" tooltip="Request payments" />
                  Payment Requests
                </router-link>
                <router-link v-if="shouldShowItem('Advance Payments', 'Request advance payments')" to="/writer/advance-payments" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/advance-payments')}">
                  <SidebarIcon icon-name="dollar-sign" size="sm" icon-class="text-gray-500 group-hover:text-green-600 mr-3" tooltip="Request advance payments" />
                  Advance Payments
                </router-link>
                <router-link v-if="shouldShowItem('Tips', 'View tips received')" to="/writer/tips" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tips')}">
                  <SidebarIcon icon-name="star" size="sm" icon-class="text-gray-500 group-hover:text-yellow-500 mr-3" tooltip="View tips received" />
                  Tips
                </router-link>
                <router-link v-if="shouldShowItem('Fines & Appeals', 'View fines and submit appeals')" to="/writer/fines" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-red-50 hover:translate-x-1 group" :class="{'bg-red-50 text-red-700 font-medium': $route.path.startsWith('/writer/fines')}">
                  <SidebarIcon icon-name="ban" size="sm" icon-class="text-gray-500 group-hover:text-red-600 mr-3" tooltip="View fines and submit appeals" />
                  Fines & Appeals
                </router-link>
              </div>
            </div>

            <!-- Reviews & Ratings Group -->
            <div v-if="shouldShowItem('Reviews & Performance', 'Reviews Performance Badges Level')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-yellow-700 dark:text-yellow-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="star" size="sm" icon-class="text-yellow-600 dark:text-yellow-400" />
                  <span>Reviews & Performance</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Reviews & Performance'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerReviewsOpen = !writerReviewsOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="star" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Reviews & Ratings</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerReviewsOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerReviewsOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link v-if="shouldShowItem('My Reviews', 'View your reviews')" to="/writer/reviews" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/reviews')}">
                  <SidebarIcon icon-name="star" size="sm" icon-class="text-gray-500 group-hover:text-yellow-500 mr-3" tooltip="View your reviews" />
                  My Reviews
                </router-link>
                <router-link v-if="shouldShowItem('Performance', 'Performance metrics')" to="/writer/performance" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/performance')}">
                  <SidebarIcon icon-name="presentation-chart" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Performance metrics" />
                      Performance
                    </router-link>
                    <router-link v-if="shouldShowItem('Badges', 'View earned badges')" to="/writer/badges" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/badges')}">
                      <SidebarIcon icon-name="badge-check" size="sm" icon-class="text-gray-500 group-hover:text-yellow-600 mr-3" tooltip="View earned badges" />
                      Badges
                    </router-link>
                    <router-link v-if="shouldShowItem('Badge Analytics', 'Badge analytics and insights')" to="/writer/badge-analytics" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/badge-analytics')}">
                      <SidebarIcon icon-name="fire" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Badge analytics and insights" />
                      Badge Analytics
                    </router-link>
                    <router-link v-if="shouldShowItem('Level Details', 'Writer level details')" to="/writer/level-details" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/level-details')}">
                      <SidebarIcon icon-name="academic-cap" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Writer level details" />
                      Level Details
                </router-link>
              </div>
            </div>

            <!-- User Management Group -->
            <div v-if="shouldShowItem('Account Management', 'Profile Settings Pen Name Resources')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-purple-700 dark:text-purple-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="user" size="sm" icon-class="text-purple-600 dark:text-purple-400" />
                  <span>Account Management</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Account Management'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerUserManagementOpen = !writerUserManagementOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="user" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">User Management</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerUserManagementOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerUserManagementOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link v-if="shouldShowItem('Profile Settings', 'Manage profile settings')" to="/writer/profile-settings" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/profile-settings')}">
                  <SidebarIcon icon-name="cog" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage profile settings" />
                  Profile Settings
                </router-link>
                <router-link v-if="shouldShowItem('Pen Name Management', 'Manage pen names')" to="/writer/pen-name" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/pen-name')}">
                  <SidebarIcon icon-name="pencil" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage pen names" />
                  Pen Name Management
                </router-link>
                <router-link v-if="shouldShowItem('Resources & Guides', 'Resources and guides')" to="/writer/resources" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/resources')}">
                  <SidebarIcon icon-name="book" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Resources and guides" />
                  Resources & Guides
                </router-link>
              </div>
            </div>

            <!-- Activity Group -->
            <div v-if="shouldShowItem('Activity & Communication', 'Dashboard Summary Communications Tickets Activity Logs')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800 dark:to-slate-900 rounded-lg border border-gray-200 dark:border-gray-700 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="table" size="sm" icon-class="text-gray-600 dark:text-gray-400" />
                  <span>Activity & Communication</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Activity & Communication'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerActivityOpen = !writerActivityOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="table" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Activity</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerActivityOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerActivityOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link v-if="shouldShowItem('Dashboard Summary', 'Dashboard summary')" to="/writer/dashboard-summary" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/dashboard-summary')}">
                  <SidebarIcon icon-name="view-grid" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Dashboard summary" />
                      Dashboard Summary
                    </router-link>
                    <router-link v-if="shouldShowItem('Communications', 'Communications')" to="/writer/communications" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/communications')}">
                      <SidebarIcon icon-name="inbox" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Communications" />
                      Communications
                    </router-link>
                    <router-link v-if="shouldShowItem('My Tickets', 'Support tickets')" to="/writer/tickets" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tickets')}">
                      <SidebarIcon icon-name="ticket" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Support tickets" />
                      My Tickets
                    </router-link>
                    <router-link v-if="shouldShowItem('Activity Logs', 'Activity logs')" to="/activity" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/activity')}">
                      <SidebarIcon icon-name="table" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Activity logs" />
                      Activity Logs
                </router-link>
              </div>
            </div>

            <!-- Discipline Group -->
            <div v-if="shouldShowItem('Discipline & Appeals', 'Discipline Status History Appeal')" class="space-y-1.5 mb-6">
              <div v-show="!sidebarCollapsed" class="px-4 py-3 mb-3 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-lg border border-red-200 dark:border-red-800 transition-opacity duration-300">
                <h3 class="text-xs font-bold text-red-700 dark:text-red-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="scale" size="sm" icon-class="text-red-600 dark:text-red-400" />
                  <span>Discipline & Appeals</span>
                </h3>
              </div>
              <SidebarTooltip :text="'Discipline & Appeals'" :collapsed="sidebarCollapsed">
                <button 
                  @click="writerDisciplineOpen = !writerDisciplineOpen" 
                  :class="[
                    'w-full flex items-center justify-between py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:shadow-sm active:scale-[0.98]',
                    sidebarCollapsed ? 'px-2 justify-center' : 'px-4'
                  ]"
                >
                  <span class="flex items-center">
                    <SidebarIcon icon-name="scale" size="md" icon-class="text-gray-600" :class="sidebarCollapsed ? '' : 'mr-3.5'" />
                    <span v-show="!sidebarCollapsed" class="transition-opacity duration-300">Discipline</span>
                  </span>
                  <ChevronIcon v-show="!sidebarCollapsed" :is-open="writerDisciplineOpen" size="sm" class="text-gray-400 shrink-0" />
                </button>
              </SidebarTooltip>
              <div v-if="writerDisciplineOpen && !sidebarCollapsed" class="ml-6 space-y-1 animate-fade-in">
                <router-link v-if="shouldShowItem('Status & History', 'Discipline status and history')" to="/writer/discipline-status" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/discipline-status')}">
                  <SidebarIcon icon-name="scroll" size="sm" icon-class="text-gray-500 group-hover:text-primary-600" class="mr-4" tooltip="Discipline status and history" />
                  Status & History
                </router-link>
                <router-link v-if="shouldShowItem('Submit Appeal', 'Submit an appeal')" to="/writer/tickets" class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group" :class="{'bg-primary-50 text-primary-700 font-medium': $route.path.startsWith('/writer/tickets')}">
                  <SidebarIcon icon-name="annotation" size="sm" icon-class="text-gray-500 group-hover:text-primary-600" class="mr-4" tooltip="Submit an appeal" />
                      Submit Appeal
                </router-link>
              </div>
            </div>
          </template>

          <!-- Admin/Superadmin Grouped Navigation -->
          <template v-if="authStore.isAdmin || authStore.isSuperAdmin">
            <!-- Core Operations Group -->
            <div v-if="shouldShowItem('Core Operations', 'Orders Special Orders Users Support Tickets')" class="mb-6">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                <h3 class="text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="cog" size="sm" icon-class="text-primary-600 dark:text-primary-400" />
                  <span>Core Operations</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <!-- Orders Section -->
                <div v-if="shouldShowItem('Orders', 'Order Management Pending In Progress Completed Disputed')" class="space-y-1">
                  <button 
                    @click="adminGroups.orders = !adminGroups.orders" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                <span class="flex items-center">
                  <svg class="w-5 h-5 mr-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Orders
                </span>
                    <ChevronIcon :is-open="adminGroups.orders" size="sm" class="text-gray-400" />
              </button>
                  <div v-if="adminGroups.orders" class="ml-6 space-y-1.5 animate-fade-in mt-3 pl-2 border-l-2 border-gray-200 dark:border-gray-700">
                    <router-link 
                      v-if="shouldShowItem('All Orders', 'View all orders')"
                      to="/admin/orders" 
                      class="flex items-center justify-between px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/orders' }) && !$route.query.status ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-semibold shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                    >
                      <div class="flex items-center">
                        <SidebarIcon icon-name="clipboard-list" size="sm" :icon-class="isRouteActive({ to: '/admin/orders' }) && !$route.query.status ? 'text-primary-600' : 'text-gray-500 group-hover:text-primary-600'" class="mr-4" tooltip="View all orders" />
                        <span>All Orders</span>
                      </div>
                      <span v-if="orderStatusCounts.total > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {{ orderStatusCounts.total }}
                      </span>
                    </router-link>
                    
                    <!-- Active Orders Group -->
                    <div class="pt-2">
                      <div class="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Active</div>
                    <router-link 
                      v-if="shouldShowItem('Pending', 'Pending orders')"
                      to="/admin/orders?status=pending" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'pending' ? 'bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 font-semibold border-l-4 border-yellow-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                      <SidebarIcon icon-name="clock" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'pending' ? 'text-yellow-600' : 'text-gray-500 group-hover:text-yellow-600'" class="mr-4" tooltip="Pending orders" />
                          <span>Pending</span>
                        </div>
                        <span v-if="orderStatusCounts.pending > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200">
                          {{ orderStatusCounts.pending }}
                        </span>
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('In Progress', 'Orders in progress')"
                      to="/admin/orders?status=in_progress" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'in_progress' ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-semibold border-l-4 border-blue-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                      <SidebarIcon icon-name="cog" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'in_progress' ? 'text-blue-600' : 'text-gray-500 group-hover:text-blue-600'" class="mr-4 animate-spin-slow" tooltip="Orders in progress" />
                          <span>In Progress</span>
                        </div>
                        <span v-if="orderStatusCounts.in_progress > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200">
                          {{ orderStatusCounts.in_progress }}
                        </span>
                    </router-link>
                      <router-link 
                        v-if="shouldShowItem('Available', 'Available orders')"
                        to="/admin/orders?status=available" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'available' ? 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 font-semibold border-l-4 border-emerald-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="clipboard" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'available' ? 'text-emerald-600' : 'text-gray-500 group-hover:text-emerald-600'" class="mr-4" tooltip="Available orders" />
                          <span>Available</span>
                        </div>
                        <span v-if="orderStatusCounts.available > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-200">
                          {{ orderStatusCounts.available }}
                        </span>
                      </router-link>
                      <router-link 
                        v-if="shouldShowItem('On Hold', 'Orders on hold')"
                        to="/admin/orders?status=on_hold" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-orange-50 dark:hover:bg-orange-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'on_hold' ? 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-semibold border-l-4 border-orange-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="stop" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'on_hold' ? 'text-orange-600' : 'text-gray-500 group-hover:text-orange-600'" class="mr-4" tooltip="Orders on hold" />
                          <span>On Hold</span>
                        </div>
                        <span v-if="orderStatusCounts.on_hold > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-200">
                          {{ orderStatusCounts.on_hold }}
                        </span>
                      </router-link>
                      <router-link 
                        v-if="shouldShowItem('Under Editing', 'Orders under editing')"
                        to="/admin/orders?status=under_editing" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-purple-50 dark:hover:bg-purple-900/20 hover:translate-x-1 group"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'under_editing' ? 'bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-semibold border-l-4 border-purple-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="pencil" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'under_editing' ? 'text-purple-600' : 'text-gray-500 group-hover:text-purple-600'" class="mr-4" tooltip="Orders under editing" />
                          <span>Under Editing</span>
                        </div>
                        <span v-if="orderStatusCounts.under_editing > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200">
                          {{ orderStatusCounts.under_editing }}
                        </span>
                      </router-link>
                    </div>
                    
                    <!-- Review Group -->
                    <div class="pt-2">
                      <div class="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Review</div>
                      <router-link 
                        v-if="shouldShowItem('Submitted', 'Submitted orders')"
                        to="/admin/orders?status=submitted" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'submitted' ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-semibold border-l-4 border-indigo-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="paper-airplane" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'submitted' ? 'text-indigo-600' : 'text-gray-500 group-hover:text-indigo-600'" class="mr-4" tooltip="Submitted orders" />
                          <span>Submitted</span>
                        </div>
                        <span v-if="orderStatusCounts.submitted > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-800 dark:text-indigo-200">
                          {{ orderStatusCounts.submitted }}
                        </span>
                      </router-link>
                      <router-link 
                        v-if="shouldShowItem('Revision Requested', 'Orders requiring revision')"
                        to="/admin/orders?status=revision_requested" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-amber-50 dark:hover:bg-amber-900/20 hover:translate-x-1 group"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'revision_requested' ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 font-semibold border-l-4 border-amber-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="arrow-left" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'revision_requested' ? 'text-amber-600' : 'text-gray-500 group-hover:text-amber-600'" class="mr-4" tooltip="Orders requiring revision" />
                          <span>Revision Requested</span>
                        </div>
                        <span v-if="orderStatusCounts.revision_requested > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-200">
                          {{ orderStatusCounts.revision_requested }}
                        </span>
                      </router-link>
                    </div>
                    
                    <!-- Completed Group -->
                    <div class="pt-2">
                      <div class="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Completed</div>
                    <router-link 
                      v-if="shouldShowItem('Completed', 'Completed orders')"
                      to="/admin/orders?status=completed" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-green-50 dark:hover:bg-green-900/20 hover:translate-x-1 group"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'completed' ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 font-semibold border-l-4 border-green-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                      <SidebarIcon icon-name="clipboard-check" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'completed' ? 'text-green-600' : 'text-gray-500 group-hover:text-green-600'" class="mr-4" tooltip="Completed orders" />
                          <span>Completed</span>
                        </div>
                        <span v-if="orderStatusCounts.completed > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200">
                          {{ orderStatusCounts.completed }}
                        </span>
                    </router-link>
                    </div>
                    
                    <!-- Issues Group -->
                    <div class="pt-2">
                      <div class="px-3 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Issues</div>
                    <router-link 
                      v-if="shouldShowItem('Disputed', 'Disputed orders')"
                      to="/admin/orders?status=disputed" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-red-50 dark:hover:bg-red-900/20 hover:translate-x-1 group mb-1"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'disputed' ? 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 font-semibold border-l-4 border-red-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                      <SidebarIcon icon-name="exclamation-triangle" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'disputed' ? 'text-red-600' : 'text-gray-500 group-hover:text-red-600'" class="mr-4" tooltip="Disputed orders" />
                          <span>Disputed</span>
                        </div>
                        <span v-if="orderStatusCounts.disputed > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200">
                          {{ orderStatusCounts.disputed }}
                        </span>
                </router-link>
                      <router-link 
                        v-if="shouldShowItem('Cancelled', 'Cancelled orders')"
                        to="/admin/orders?status=cancelled" 
                        class="flex items-center justify-between px-3 py-2 text-sm leading-relaxed font-medium rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 hover:translate-x-1 group"
                        :class="$route.path === '/admin/orders' && $route.query.status === 'cancelled' ? 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-semibold border-l-4 border-gray-500 shadow-sm' : 'text-gray-700 dark:text-gray-300'"
                      >
                        <div class="flex items-center">
                          <SidebarIcon icon-name="ban" size="sm" :icon-class="$route.path === '/admin/orders' && $route.query.status === 'cancelled' ? 'text-gray-600' : 'text-gray-500 group-hover:text-gray-600'" class="mr-3" tooltip="Cancelled orders" />
                          <span>Cancelled</span>
                        </div>
                        <span v-if="orderStatusCounts.cancelled > 0" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                          {{ orderStatusCounts.cancelled }}
                        </span>
                      </router-link>
                    </div>
              </div>
            </div>
            
                <!-- Special Orders -->
                <router-link
                  v-if="shouldShowItem('Special Orders', 'Manage special orders')"
                  to="/admin/special-orders"
                  :class="[
                    'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 group leading-relaxed',
                    isRouteActive({ to: '/admin/special-orders' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="sparkles" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-4" tooltip="Manage special orders" />
                  Special Orders
                </router-link>
                
                <!-- Users Section -->
                <div v-if="shouldShowItem('Users', 'User Management Clients Writers Editors Support Admins')" class="space-y-1">
                  <button 
                    @click="adminGroups.users = !adminGroups.users" 
                    class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm active:scale-[0.98]"
                  >
                <span class="flex items-center">
                  <svg class="w-5 h-5 mr-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  Users
                </span>
                    <ChevronIcon :is-open="adminGroups.users" size="sm" class="text-gray-400" />
              </button>
                  <div v-if="adminGroups.users" class="ml-6 space-y-1 animate-fade-in">
                    <router-link 
                      v-if="shouldShowItem('All Users', 'View all users')"
                      to="/admin/users" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/users' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="users" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View all users" />
                      All Users
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Clients', 'Client users')"
                      to="/admin/users?role=client" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="user" size="sm" icon-class="text-gray-500 group-hover:text-blue-600 mr-3" tooltip="Client users" />
                      Clients
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Writers', 'Writer users')"
                      to="/admin/users?role=writer" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="pencil" size="sm" icon-class="text-gray-500 group-hover:text-green-600 mr-3" tooltip="Writer users" />
                      Writers
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Editors', 'Editor users')"
                      to="/admin/users?role=editor" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="pencil" size="sm" icon-class="text-gray-500 group-hover:text-indigo-600 mr-3" tooltip="Editor users" />
                      Editors
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Support', 'Support users')"
                      to="/admin/users?role=support" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="headphones" size="sm" icon-class="text-gray-500 group-hover:text-yellow-600 mr-3" tooltip="Support users" />
                      Support
                    </router-link>
                    <router-link 
                      v-if="authStore.isSuperAdmin && shouldShowItem('Admins', 'Admin users')"
                      to="/admin/users?role=admin" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="user-circle" size="sm" icon-class="text-gray-500 group-hover:text-purple-600 mr-3" tooltip="Admin users" />
                      Admins
                    </router-link>
              </div>
            </div>
            
                <!-- Support Tickets -->
              <router-link
                  v-if="shouldShowItem('Support Tickets', 'Manage support tickets')"
                  to="/admin/support-tickets"
                :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/support-tickets' })
                    ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                ]"
              >
                  <SidebarIcon icon-name="ticket" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage support tickets" />
                  Support Tickets
              </router-link>
              </div>
            </div>
            
            <!-- Financial Management Group -->
            <div v-if="shouldShowItem('Financial Management', 'Payments Refunds Disputes Tips Fines Wallets Invoices')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <h3 class="text-xs font-bold text-green-700 dark:text-green-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="wallet" size="sm" icon-class="text-green-600 dark:text-green-400" />
                  <span>Financial Management</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <div v-if="shouldShowItem('Payments', 'Client Payments Writer Payments Payment Requests Invoices Wallets')" class="space-y-1">
                  <button 
                    @click="adminGroups.payments = !adminGroups.payments" 
                    class="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 hover:bg-gray-100 hover:shadow-sm active:scale-[0.98]"
                  >
                <span class="flex items-center">
                  <svg class="w-5 h-5 mr-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  Payments
                </span>
                    <ChevronIcon :is-open="adminGroups.payments" size="sm" class="text-gray-400" />
              </button>
                  <div v-if="adminGroups.payments" class="ml-7 space-y-0.5 animate-fade-in mt-2">
                    <router-link
                      v-if="shouldShowItem('Client Payments', 'View all client payments and transactions')"
                      to="/admin/payments/client-payments"
                      class="flex items-center px-4 py-3 text-sm rounded-xl transition-all duration-300 hover:scale-[1.02] group leading-relaxed border-2"
                      :class="isRouteActive({ to: '/admin/payments/client-payments' }) 
                        ? 'bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-600 text-white font-bold shadow-lg border-blue-400' 
                        : 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100 hover:border-blue-300 font-semibold shadow-sm'"
                    >
                      <div class="flex items-center justify-center w-8 h-8 rounded-lg mr-3"
                           :class="isRouteActive({ to: '/admin/payments/client-payments' }) 
                             ? 'bg-white/20' 
                             : 'bg-blue-100 group-hover:bg-blue-200'">
                        <SidebarIcon 
                          icon-name="credit-card" 
                          size="sm" 
                          :icon-class="isRouteActive({ to: '/admin/payments/client-payments' }) 
                            ? 'text-white' 
                            : 'text-blue-600 group-hover:text-blue-700'" 
                          tooltip="View all client payments and transactions" 
                        />
                      </div>
                      <span class="tracking-wide" :class="isRouteActive({ to: '/admin/payments/client-payments' }) ? 'font-bold text-base' : 'font-semibold'">
                        Client Payments
                      </span>
                      <span v-if="!isRouteActive({ to: '/admin/payments/client-payments' })" class="ml-auto text-xs font-medium text-blue-500 opacity-75">
                        💳
                      </span>
                    </router-link>
                    <router-link
                      v-if="shouldShowItem('Payment Requests', 'Manage writer payment requests')"
                      to="/admin/payments/payment-requests"
                      class="flex items-center px-3 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 hover:bg-amber-50 hover:translate-x-1 group leading-relaxed shadow-sm"
                      :class="isRouteActive({ to: '/admin/payments/payment-requests' }) ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold shadow-md' : 'text-amber-700 hover:text-amber-800'"
                    >
                      <div class="w-8 h-8 flex items-center justify-center rounded-lg mr-3 transition-colors"
                           :class="isRouteActive({ to: '/admin/payments/payment-requests' }) 
                             ? 'bg-white/20' 
                             : 'bg-amber-100 group-hover:bg-amber-200'">
                        <SidebarIcon 
                          icon-name="file-text" 
                          size="sm" 
                          :icon-class="isRouteActive({ to: '/admin/payments/payment-requests' }) 
                            ? 'text-white' 
                            : 'text-amber-600 group-hover:text-amber-700'" 
                          tooltip="Manage writer payment requests" 
                        />
                      </div>
                      <span class="tracking-wide" :class="isRouteActive({ to: '/admin/payments/payment-requests' }) ? 'font-bold text-base' : 'font-semibold'">
                        Payment Requests
                      </span>
                      <span v-if="!isRouteActive({ to: '/admin/payments/payment-requests' })" class="ml-auto text-xs font-medium text-amber-500 opacity-75">
                        📋
                      </span>
                    </router-link>
                    <router-link
                      v-if="shouldShowItem('Writer Payments', 'Manage writer payments')"
                      to="/admin/payments/writer-payments"
                      class="flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group leading-relaxed"
                      :class="isRouteActive({ to: '/admin/payments/writer-payments' }) ? 'bg-primary-50 text-primary-700 font-semibold' : ''"
                    >
                      <SidebarIcon icon-name="cash" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage writer payments" />
                      Writer Payments
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Invoices', 'View and manage invoices')"
                      to="/admin/invoices" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/invoices' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="receipt-tax" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View and manage invoices" />
                      Invoices
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Wallets', 'Manage user wallets')"
                      to="/admin/wallets" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/wallets' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="wallet" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage user wallets" />
                      Wallets
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Payment Management', 'Batch payment management')"
                      to="/admin/payments/batched" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/payments/batched' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="view-grid" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Batch payment management" />
                      Payment Management
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('All Payments', 'View all payments')"
                      to="/admin/payments/all" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/payments/all' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="currency-dollar" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="View all payments" />
                      All Payments
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Payment Logs', 'Payment transaction logs')"
                      to="/admin/payments/logs" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/payments/logs' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="archive" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Payment transaction logs" />
                      Payment Logs
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Financial Overview', 'Financial overview and analytics')"
                      to="/admin/financial-overview" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                      :class="isRouteActive({ to: '/admin/financial-overview' }) ? 'bg-primary-50 text-primary-700 font-medium' : ''"
                    >
                      <SidebarIcon icon-name="calculator" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Financial overview and analytics" />
                      Financial Overview
                    </router-link>
                  </div>
                </div>
                
                <router-link
                  v-if="shouldShowItem('Refunds', 'Manage refunds')"
                  to="/admin/refunds"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/refunds' })
                      ? 'bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 shadow-sm border-l-4 border-orange-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-orange-50 dark:hover:bg-orange-900/20 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="arrow-left" size="md" :icon-class="isRouteActive({ to: '/admin/refunds' }) ? 'text-orange-600' : 'text-gray-600 group-hover:text-orange-600'" class="mr-3" tooltip="Manage refunds" />
                  Refunds
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Disputes', 'Manage disputes')"
                  to="/admin/disputes"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/disputes' })
                      ? 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 shadow-sm border-l-4 border-red-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="scale" size="md" :icon-class="isRouteActive({ to: '/admin/disputes' }) ? 'text-red-600' : 'text-gray-600 group-hover:text-red-600'" class="mr-3" tooltip="Manage disputes" />
                  Disputes
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Tips', 'Manage tips')"
                  to="/admin/tips"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/tips' })
                      ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 shadow-sm border-l-4 border-green-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="dollar-sign" size="md" :icon-class="isRouteActive({ to: '/admin/tips' }) ? 'text-green-600' : 'text-gray-600 group-hover:text-green-600'" class="mr-3" tooltip="Manage tips" />
                  Tips
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Fines', 'Manage fines')"
                  to="/admin/fines"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/fines' })
                      ? 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 shadow-sm border-l-4 border-red-500'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="ban" size="md" :icon-class="isRouteActive({ to: '/admin/fines' }) ? 'text-red-600' : 'text-gray-600 group-hover:text-red-600'" class="mr-3" tooltip="Manage fines" />
                  Fines
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Holidays & Campaigns', 'Manage holidays and campaigns')"
                  to="/admin/holidays"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/holidays' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="star" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-3" tooltip="Manage holidays and campaigns" />
                  Holidays & Campaigns
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Advance Payments', 'Manage advance payments')"
                  to="/admin/advance-payments"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/advance-payments' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="dollar-sign" size="md" icon-class="text-gray-600 group-hover:text-green-600" class="mr-3" tooltip="Manage advance payments" />
                  Advance Payments
                </router-link>
              </div>
            </div>
            
            <!-- Content & Services Group -->
            <div v-if="shouldShowItem('Content & Services', 'Reviews Class Management Express Classes Blog SEO Media')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <h3 class="text-xs font-bold text-blue-700 dark:text-blue-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="newspaper" size="sm" icon-class="text-blue-600 dark:text-blue-400" />
                  <span>Content & Services</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <div v-if="shouldShowItem('Reviews', 'All Reviews Moderation Aggregation')" class="space-y-1">
                  <button 
                    @click="adminGroups.reviews = !adminGroups.reviews" 
                    class="w-full flex items-center justify-between px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 text-gray-700 hover:bg-gray-100 hover:shadow-sm active:scale-[0.98]"
                  >
                    <span class="flex items-center">
                      <svg class="w-5 h-5 mr-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      Reviews
                    </span>
                    <ChevronIcon :is-open="adminGroups.reviews" size="sm" class="text-gray-400" />
                  </button>
                  <div v-if="adminGroups.reviews" class="ml-7 space-y-0.5 animate-fade-in mt-2">
                    <router-link 
                      v-if="shouldShowItem('All Reviews', 'View all reviews')"
                      to="/admin/reviews" 
                      class="flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group leading-relaxed"
                    >
                      <SidebarIcon icon-name="star" size="sm" icon-class="text-gray-500 group-hover:text-yellow-500 mr-3" tooltip="View all reviews" />
                      All Reviews
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Moderation', 'Review moderation')"
                      to="/admin/reviews/moderation" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="shield-check" size="sm" icon-class="text-gray-500 group-hover:text-blue-600 mr-3" tooltip="Review moderation" />
                      Moderation
                    </router-link>
                    <router-link 
                      v-if="shouldShowItem('Aggregation', 'Review aggregation')"
                      to="/admin/review-aggregation" 
                      class="flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group"
                    >
                      <SidebarIcon icon-name="collection" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Review aggregation" />
                      Aggregation
                    </router-link>
                  </div>
                </div>
                
                <router-link
                  v-if="shouldShowItem('Class Management', 'Manage classes')"
                  to="/admin/class-management"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/class-management' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="book" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage classes" />
                  Class Management
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Express Classes', 'Manage express classes')"
                  to="/admin/express-classes"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/express-classes' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="lightning" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-3" tooltip="Manage express classes" />
                  Express Classes
                </router-link>
              </div>
            </div>

            <!-- Content Management Group -->
            <div v-if="shouldShowItem('Content Management', 'Blog SEO Media File Management')" class="mb-6">
              <button
                @click="adminGroups.contentManagement = !adminGroups.contentManagement"
                class="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-gray-700 hover:bg-gray-100 hover:shadow-sm active:scale-[0.98]"
              >
                <span class="flex items-center">
                  <svg class="w-5 h-5 mr-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Content Management
                </span>
                <ChevronIcon :is-open="adminGroups.contentManagement" size="sm" class="text-gray-400" />
              </button>
              <div v-if="adminGroups.contentManagement" class="ml-6 space-y-1 animate-fade-in">
                <router-link
                  v-if="shouldShowItem('Blog Pages', 'Manage blog posts')"
                  to="/admin/blog"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/blog' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="newspaper" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage blog posts" />
                  Blog Pages
                </router-link>
                <router-link
                  v-if="shouldShowItem('SEO Pages', 'Manage SEO service pages')"
                  to="/admin/seo-pages"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/seo-pages' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="globe" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage SEO service pages" />
                  SEO Pages (Service)
                </router-link>
                <router-link
                  v-if="shouldShowItem('SEO Landing Pages', 'Manage SEO landing pages')"
                  to="/admin/seo-pages-blocks"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/seo-pages-blocks' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="template" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage SEO landing pages" />
                  SEO Landing Pages
                </router-link>
                <router-link
                  v-if="shouldShowItem('Blog Authors', 'Manage blog authors')"
                  to="/admin/blog-authors"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/blog-authors' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="identification" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage blog authors" />
                  Blog Authors
                </router-link>
                <router-link
                  v-if="shouldShowItem('Media Library', 'Manage media library')"
                  to="/admin/media-library"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/media-library' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="photograph" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="Manage media library" />
                  Media Library
                </router-link>
                <router-link
                  v-if="shouldShowItem('File Management', 'File management')"
                  to="/admin/files"
                  :class="[
                    'flex items-center px-3 py-2 text-sm leading-relaxed rounded-lg transition-all duration-200 hover:bg-gray-100 hover:translate-x-1 group',
                    isRouteActive({ to: '/admin/files' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300'
                  ]"
                >
                  <SidebarIcon icon-name="folder" size="sm" icon-class="text-gray-500 group-hover:text-primary-600 mr-3" tooltip="File management" />
                  File Management
                </router-link>
              </div>
            </div>

            <!-- Analytics & Reporting Group -->
            <div v-if="shouldShowItem('Analytics & Reporting', 'Advanced Enhanced Pricing Discount Writer Performance Referral Loyalty Campaign Refined')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <h3 class="text-xs font-bold text-purple-700 dark:text-purple-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="chart-bar" size="sm" icon-class="text-purple-600 dark:text-purple-400" />
                  <span>Analytics & Reporting</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  v-if="shouldShowItem('Advanced Analytics', 'Advanced analytics dashboard')"
                  to="/admin/advanced-analytics"
                  :class="[
                    'flex items-center px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-200 group leading-relaxed',
                    isRouteActive({ to: '/admin/advanced-analytics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="trending-up" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Advanced analytics dashboard" />
                  Advanced Analytics
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Enhanced Analytics', 'Enhanced analytics dashboard')"
                  to="/admin/enhanced-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/enhanced-analytics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="presentation-chart" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Enhanced analytics dashboard" />
                  Enhanced Analytics
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Analytics & Reports', 'Comprehensive yearly analytics and reports')"
                  to="/admin/analytics-reports"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/analytics-reports' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="chart-bar" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Comprehensive yearly analytics and reports" />
                  Analytics & Reports
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Refined Stats', 'View largest spend and orders by country, state, and subject')"
                  to="/admin/geographic-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ name: 'RefinedStats', to: '/admin/geographic-analytics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="globe-alt" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="View largest spend and orders by country, state, and subject" />
                  Refined Stats
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Pricing Analytics', 'Pricing analytics')"
                  to="/admin/pricing-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/pricing-analytics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="dollar-sign" size="md" icon-class="text-gray-600 group-hover:text-green-600" class="mr-3" tooltip="Pricing analytics" />
                  Pricing Analytics
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Discount Analytics', 'Discount analytics')"
                  to="/admin/discount-analytics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/discount-analytics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="discount" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Discount analytics" />
                  Discount Analytics
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Writer Performance', 'Writer performance metrics')"
                  to="/admin/writer-performance"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/writer-performance' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="user" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Writer performance metrics" />
                  Writer Performance
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Referral Tracking', 'Referral tracking and analytics')"
                  to="/admin/referral-tracking"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/referral-tracking' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="gift" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Referral tracking and analytics" />
                  Referral Tracking
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Loyalty Tracking', 'Loyalty tracking and analytics')"
                  to="/admin/loyalty-tracking"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/loyalty-tracking' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="star" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-3" tooltip="Loyalty tracking and analytics" />
                  Loyalty Tracking
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Loyalty Management', 'Loyalty program management')"
                  to="/admin/loyalty-management"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/loyalty-management' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="trophy" size="md" icon-class="text-gray-600 group-hover:text-yellow-600" class="mr-3" tooltip="Loyalty program management" />
                  Loyalty Management
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Campaign Analytics', 'Campaign analytics')"
                  to="/admin/campaigns"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/campaigns' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="megaphone" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Campaign analytics" />
                  Campaign Analytics
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Content Reporting', 'Content metrics and reporting')"
                  to="/admin/content-metrics-report"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/content-metrics-report' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="document-text" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Content metrics and reporting" />
                  Content Reporting
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Order Status Metrics', 'Order status metrics and analytics')"
                  to="/admin/order-status-metrics"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/order-status-metrics' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="clipboard-list" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Order status metrics and analytics" />
                  Order Status Metrics
                </router-link>
              </div>
            </div>

            <!-- System Management Group -->
            <div v-if="shouldShowItem('System Management', 'Configurations Screened Words Flagged Messages System Health Activity Logs Email Notification Duplicate')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800 dark:to-slate-900 rounded-lg border border-gray-200 dark:border-gray-700">
                <h3 class="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="cog" size="sm" icon-class="text-gray-600 dark:text-gray-400" />
                  <span>System Management</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  v-if="shouldShowItem('Configurations', 'System configurations')"
                  to="/admin/configs"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/configs' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="adjustments" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="System configurations" />
                  Configurations
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Screened Words', 'Manage screened words')"
                  to="/admin/screened-words"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/screened-words' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="ban" size="md" icon-class="text-gray-600 group-hover:text-red-600" class="mr-3" tooltip="Manage screened words" />
                  Screened Words
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Flagged Messages', 'Review flagged messages')"
                  to="/admin/flagged-messages"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/flagged-messages' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="exclamation-triangle" size="md" icon-class="text-gray-600 group-hover:text-yellow-600" class="mr-3" tooltip="Review flagged messages" />
                  Flagged Messages
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('System Health', 'System health monitoring')"
                  to="/admin/system-health"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/system-health' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="shield" size="md" icon-class="text-gray-600 group-hover:text-green-600" class="mr-3" tooltip="System health monitoring" />
                  System Health
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Activity Logs', 'View activity logs')"
                  to="/admin/activity-logs"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/activity-logs' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="table" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="View activity logs" />
                  Activity Logs
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Email Management', 'Email management')"
                  to="/admin/emails"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/emails' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="mail" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Email management" />
                  Email Management
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Notification Profiles', 'Notification profiles')"
                  to="/admin/notification-profiles"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/notification-profiles' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="bell" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Notification profiles" />
                  Notification Profiles
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Notification Groups', 'Notification groups')"
                  to="/admin/notification-groups"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/notification-groups' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="users" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Notification groups" />
                  Notification Groups
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Duplicate Detection', 'Duplicate content detection')"
                  to="/admin/duplicate-detection"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/duplicate-detection' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="search" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Duplicate content detection" />
                  Duplicate Detection
                </router-link>
              </div>
            </div>

            <!-- Discipline & Appeals Group -->
            <div v-if="shouldShowItem('Discipline & Appeals', 'Writer Discipline Appeals Config Blacklist')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <h3 class="text-xs font-bold text-red-700 dark:text-red-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="scale" size="sm" icon-class="text-red-600 dark:text-red-400" />
                  <span>Discipline & Appeals</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  v-if="shouldShowItem('Writer Discipline', 'Writer discipline management')"
                  to="/admin/writer-discipline"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/writer-discipline' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="scroll" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Writer discipline management" />
                  Writer Discipline
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Appeals', 'Manage appeals')"
                  to="/admin/appeals"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/appeals' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="annotation" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage appeals" />
                  Appeals
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Discipline Config', 'Discipline configuration')"
                  to="/admin/discipline-config"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/discipline-config' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="adjustments" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Discipline configuration" />
                  Discipline Config
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Client Email Blacklist', 'Manage blacklisted client emails')"
                  to="/admin/client-email-blacklist"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/client-email-blacklist' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="ban" size="md" icon-class="text-gray-600 group-hover:text-red-600" class="mr-3" tooltip="Manage blacklisted client emails" />
                  Client Email Blacklist
                </router-link>
              </div>
            </div>

            <!-- Writer Management Group -->
            <div v-if="shouldShowItem('Writer Management', 'Writer Management Resources Samples Hierarchy')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                <h3 class="text-xs font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="pencil" size="sm" icon-class="text-indigo-600 dark:text-indigo-400" />
                  <span>Writer Management</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  v-if="shouldShowItem('Writer Management', 'Manage writers')"
                  to="/admin/users?role=writer"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/users', query: { role: 'writer' } })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="users" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage writers" />
                  Writer Management
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Writer Resources & Samples', 'Manage writer resources and samples')"
                  to="/admin/writer-resources"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/writer-resources' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="book" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage writer resources and samples" />
                  Writer Resources & Samples
                </router-link>
                
                <router-link
                  v-if="shouldShowItem('Writer Hierarchy', 'Writer hierarchy management')"
                  to="/admin/writer-hierarchy"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/writer-hierarchy' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="chart-bar" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Writer hierarchy management" />
                  Writer Hierarchy
                </router-link>
              </div>
            </div>

            <!-- Multi-Tenant Group -->
            <div v-if="shouldShowItem('Multi-Tenant', 'Websites')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-cyan-50 to-teal-50 dark:from-cyan-900/20 dark:to-teal-900/20 rounded-lg border border-cyan-200 dark:border-cyan-800">
                <h3 class="text-xs font-bold text-cyan-700 dark:text-cyan-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="home" size="sm" icon-class="text-cyan-600 dark:text-cyan-400" />
                  <span>Multi-Tenant</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  v-if="shouldShowItem('Websites', 'Manage websites')"
                  to="/websites"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/websites' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="home" size="md" icon-class="text-gray-600 group-hover:text-primary-600" class="mr-3" tooltip="Manage websites" />
                  Websites
                </router-link>
              </div>
            </div>

            <!-- Superadmin Only -->
            <div v-if="authStore.isSuperAdmin && shouldShowItem('Superadmin', 'Superadmin dashboard')" class="mb-8">
              <div class="px-4 py-3 mb-3 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <h3 class="text-xs font-bold text-yellow-700 dark:text-yellow-300 uppercase tracking-widest flex items-center gap-2">
                  <SidebarIcon icon-name="star" size="sm" icon-class="text-yellow-600 dark:text-yellow-400" />
                  <span>Superadmin</span>
                </h3>
              </div>
              <div class="space-y-1.5">
                <router-link
                  to="/admin/superadmin"
                  :class="[
                    'flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group',
                    isRouteActive({ to: '/admin/superadmin' })
                      ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm hover:translate-x-1'
                  ]"
                >
                  <SidebarIcon icon-name="star" size="md" icon-class="text-gray-600 group-hover:text-yellow-500" class="mr-3" tooltip="Superadmin dashboard" />
                  Superadmin Dashboard
                </router-link>
              </div>
            </div>
          </template>

          <!-- Other navigation items (profile/settings/privacy/security for all, tickets/etc for non-admin) -->
          <template v-for="item in navigationItems">
            <SidebarTooltip 
              v-if="shouldShowItem(item.label, item.description || '')"
              :key="item.name"
              :text="item.label"
              :collapsed="sidebarCollapsed"
            >
              <router-link
                :to="item.name && !item.to?.includes('?') ? { name: item.name } : item.to"
                :class="[
                  'flex items-center rounded-lg transition-all duration-200 group leading-tight focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-1 dark:focus:ring-offset-gray-900',
                  isRouteActive(item)
                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50',
                  sidebarCollapsed ? 'px-2 py-2 justify-center' : 'px-3 py-2'
                ]"
                :aria-label="sidebarCollapsed ? item.label : undefined"
              >
                <div :class="[
                  'flex items-center justify-center shrink-0 rounded-md transition-colors',
                  'w-8 h-8',
                  isRouteActive(item)
                    ? 'bg-primary-100 dark:bg-primary-900/40'
                    : 'bg-gray-100 dark:bg-gray-800/50 group-hover:bg-gray-200 dark:group-hover:bg-gray-700',
                  sidebarCollapsed ? 'mr-0' : 'mr-2.5'
                ]">
                  <SidebarIcon 
                    :icon-name="getIconNameFromEmoji(item.icon)" 
                    size="sm" 
                    :icon-class="isRouteActive(item) ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-300'" 
                  />
                </div>
                <span v-show="!sidebarCollapsed" class="text-[13px] font-medium transition-opacity duration-300 flex-1">{{ item.label }}</span>
                <!-- Unread count badge for Announcements -->
                <span 
                  v-if="item.name === 'Announcements' && unreadAnnouncementsCount > 0"
                  class="ml-auto flex items-center justify-center min-w-[18px] h-4.5 px-1.5 text-[10px] font-semibold text-white bg-red-600 dark:bg-red-500 rounded-full"
                  :class="sidebarCollapsed ? 'absolute -top-1 -right-1' : ''"
                >
                  {{ unreadAnnouncementsCount > 99 ? '99+' : unreadAnnouncementsCount }}
                </span>
              </router-link>
            </SidebarTooltip>
          </template>
        </nav>

        <!-- User section - Compact -->
        <div :class="[
          'border-t border-gray-200 dark:border-gray-700 transition-all duration-300',
          sidebarCollapsed ? 'p-2' : 'p-3'
        ]">
          <div :class="[
            'flex items-center justify-between mb-2',
            sidebarCollapsed ? 'justify-center' : ''
          ]">
            <div :class="[
              'flex items-center',
              sidebarCollapsed ? 'justify-center' : ''
            ]">
              <SidebarTooltip :text="authStore.user?.email || 'User Profile'" :collapsed="sidebarCollapsed">
                <button
                  @click="toggleProfileDropdown"
                  class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center shrink-0 shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900 cursor-pointer"
                  :aria-label="sidebarCollapsed ? 'User profile menu' : 'User profile menu'"
                  :aria-expanded="showProfileDropdown"
                >
                  <span class="text-primary-600 dark:text-primary-400 text-sm font-semibold">
                    {{ userInitials }}
                  </span>
                </button>
              </SidebarTooltip>
              <div v-show="!sidebarCollapsed" class="ml-3 min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{{ authStore.user?.email }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 capitalize">{{ authStore.userRole }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="authStore.isImpersonating && !sidebarCollapsed" class="mb-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-xs text-yellow-800 dark:text-yellow-200">
            Impersonating as {{ authStore.user?.email }}
          </div>

          <button
            v-show="!sidebarCollapsed"
            @click="handleLogout"
            class="w-full btn btn-secondary text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            aria-label="Sign out"
          >
            Sign Out
          </button>
          <SidebarTooltip :text="'Sign Out'" :collapsed="sidebarCollapsed">
            <button
              v-show="sidebarCollapsed"
              @click="handleLogout"
              class="w-full p-2 rounded-lg text-gray-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
              aria-label="Sign out"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </SidebarTooltip>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div :class="['h-screen overflow-hidden flex flex-col transition-all duration-300', sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-72']">
      <!-- Top bar -->
      <header class="sticky top-0 z-40 bg-white dark:bg-[#111111] border-b border-gray-200 dark:border-gray-800 backdrop-blur-sm bg-opacity-95 dark:bg-opacity-95">
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
            <div class="relative flex items-center gap-3">
              <ThemeToggle />
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
                class="absolute right-0 mt-2 w-80 bg-white dark:bg-[#1a1a1a] rounded-lg shadow-lg border border-gray-200 dark:border-gray-800 z-50 max-h-96 overflow-hidden flex flex-col backdrop-blur-sm"
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
                  <div v-else-if="recentActivities.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
                    No activities
                  </div>
                  <div v-else class="divide-y divide-gray-100 dark:divide-gray-700">
                    <div
                      v-for="activity in recentActivities"
                      :key="activity.id"
                      class="p-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
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
                            <span class="text-xs text-gray-500 dark:text-gray-400 truncate">
                              {{ activity.user_email || 'N/A' }}
                            </span>
                          </div>
                          <p class="text-sm text-gray-900 dark:text-gray-100 line-clamp-2 leading-relaxed">
                            {{ activity.display_description || activity.description || 'No description' }}
                          </p>
                          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 leading-relaxed">
                            {{ formatActivityDate(activity.timestamp || activity.formatted_timestamp) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="p-3 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#1a1a1a]">
                  <router-link
                    to="/activity"
                    @click="closeActivitiesDropdown"
                    class="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium leading-relaxed"
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
                <div class="p-3 border-b border-gray-200">
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="font-semibold text-gray-900 text-sm leading-tight">Notifications</h3>
                    <button
                      @click="closeNotificationsDropdown"
                      class="text-gray-400 hover:text-gray-600"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <div class="flex items-center justify-between">
                    <div class="inline-flex bg-gray-100 rounded-full p-0.5 text-xs">
                      <button
                        class="px-3 py-1 rounded-full transition-colors"
                        :class="notificationsFilter === 'unread' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-800'"
                        @click="() => { notificationsFilter = 'unread'; loadRecentNotifications(); }"
                      >
                        Unread
                      </button>
                      <button
                        class="px-3 py-1 rounded-full transition-colors"
                        :class="notificationsFilter === 'all' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-800'"
                        @click="() => { notificationsFilter = 'all'; loadRecentNotifications(); }"
                      >
                        All
                      </button>
                    </div>
                    <button
                      v-if="unreadCount > 0"
                      @click="markAllNotificationsRead"
                      :disabled="markingAllRead"
                      class="text-[11px] text-primary-600 hover:text-primary-700 disabled:opacity-50"
                    >
                      {{ markingAllRead ? 'Marking...' : 'Mark all read' }}
                    </button>
                  </div>
                </div>

                <div class="overflow-y-auto flex-1">
                  <div v-if="notificationsLoading" class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  </div>
                  <div v-else-if="recentNotifications.length === 0" class="text-center py-8 text-gray-500 text-sm leading-relaxed">
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
                        <div v-if="!notif.is_read" class="shrink-0 w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-1 leading-relaxed">
                            {{ notif.title }}
                          </p>
                          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                            {{ notif.message }}
                          </p>
                          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 leading-relaxed">
                            {{ notif.time_ago || formatNotificationDate(notif.created_at) }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="p-3 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#1a1a1a]">
                  <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-2 leading-relaxed">
                    <span>
                      <span class="font-medium">{{ unreadCount }}</span>
                      <span> unread</span>
                      <span v-if="totalNotificationCount > 0">
                        <span class="mx-1">·</span>
                        <span>{{ totalNotificationCount }} total</span>
                      </span>
                    </span>
                  </div>
                  <router-link
                    to="/notifications"
                    @click="closeNotificationsDropdown"
                    class="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium leading-relaxed"
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
                class="flex items-center text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 focus:outline-none"
              >
                <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center relative">
                  <span class="text-primary-600 dark:text-primary-400 text-sm font-medium">
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
                class="absolute right-0 mt-2 w-56 bg-white dark:bg-[#1a1a1a] rounded-lg shadow-lg border border-gray-200 dark:border-gray-800 z-50 backdrop-blur-sm"
              >
                <div class="p-2">
                  <router-link
                    :to="authStore.isWriter ? '/writer/profile-settings' : '/profile'"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Profile
                  </router-link>
                  <router-link
                    to="/notifications"
                    @click="closeProfileDropdown"
                    class="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex items-center justify-between"
                  >
                    <span>Notifications</span>
                    <span v-if="unreadCount > 0" class="px-2 py-0.5 text-xs font-bold text-white bg-red-600 rounded-full">
                      {{ unreadCount > 99 ? '99+' : unreadCount }}
                    </span>
                  </router-link>
                  <router-link
                    to="/profile/settings"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Settings
                  </router-link>
                  <router-link
                    to="/profile/privacy-security"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Privacy & Security
                  </router-link>
                  <router-link
                    to="/profile/security"
                    @click="closeProfileDropdown"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Security Activity
                  </router-link>
                  <div class="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg"
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
      <main class="flex-1 overflow-y-auto bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
        <div class="p-6 sm:p-8 lg:p-10 xl:p-12 max-w-[1600px] mx-auto min-h-full">
        <router-view />
        </div>
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
import announcementsAPI from '@/api/announcements'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import Logo from '@/components/common/Logo.vue'
import SessionTimeoutWarning from '@/components/common/SessionTimeoutWarning.vue'
import ChevronIcon from '@/components/common/ChevronIcon.vue'
import SidebarIcon from '@/components/common/SidebarIcon.vue'
import SidebarTooltip from '@/components/common/SidebarTooltip.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import sessionManager from '@/services/sessionManager'
import { useTheme } from '@/composables/useTheme'
import writerDashboardAPI from '@/api/writer-dashboard'
import ordersAPI from '@/api/orders'
import adminOrdersAPI from '@/api/admin-orders'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const sidebarOpen = ref(false)
// Load sidebar collapsed state from localStorage with default to false
const getInitialSidebarState = () => {
  try {
    const stored = localStorage.getItem('sidebarCollapsed')
    return stored === 'true'
  } catch {
    return false
  }
}
const sidebarCollapsed = ref(getInitialSidebarState())
const sidebarSearchQuery = ref('')
const ordersOpen = ref(true)
const sidebarSearchInput = ref(null)

// Persist sidebar collapsed state to localStorage
watch(sidebarCollapsed, (newValue) => {
  try {
    localStorage.setItem('sidebarCollapsed', String(newValue))
  } catch (error) {
    console.warn('Failed to save sidebar state to localStorage:', error)
  }
})

// Keyboard shortcuts
const { register, isMac } = useKeyboardShortcuts()

// Register Cmd/Ctrl+K to focus sidebar search
onMounted(() => {
  register(isMac ? 'cmd+k' : 'ctrl+k', () => {
    // Focus the sidebar search input
    if (sidebarSearchInput.value) {
      sidebarSearchInput.value.focus()
      sidebarSearchInput.value.select()
    }
  }, {
    description: 'Focus sidebar search',
    preventDefault: true
  })
})

// Filter sidebar items based on search query
const shouldShowItem = (label, description = '') => {
  if (!sidebarSearchQuery.value) return true
  const query = sidebarSearchQuery.value.toLowerCase()
  const searchText = (label + ' ' + description).toLowerCase()
  return searchText.includes(query)
}

// Clear search function
const clearSearch = () => {
  sidebarSearchQuery.value = ''
}

// Auto-expand groups when searching
watch(sidebarSearchQuery, (newQuery) => {
  if (!newQuery) return
  
  const query = newQuery.toLowerCase()
  
  // Admin/Superadmin groups
  if (authStore.isAdmin || authStore.isSuperAdmin) {
    if (query.includes('order') || query.includes('pending') || query.includes('progress') || query.includes('completed') || query.includes('disputed') || query.includes('submitted') || query.includes('revision') || query.includes('cancelled') || query.includes('special')) {
      adminGroups.value.orders = true
    }
    if (query.includes('user') || query.includes('client') || query.includes('writer') || query.includes('editor') || query.includes('support') || query.includes('admin')) {
      adminGroups.value.users = true
    }
    if (query.includes('payment') || query.includes('refund') || query.includes('dispute') || query.includes('tip') || query.includes('fine') || query.includes('wallet') || query.includes('invoice') || query.includes('financial') || query.includes('advance') || query.includes('transaction')) {
      adminGroups.value.payments = true
    }
    if (query.includes('review') || query.includes('rating') || query.includes('moderation') || query.includes('feedback')) {
      adminGroups.value.reviews = true
    }
    if (query.includes('blog') || query.includes('seo') || query.includes('media') || query.includes('file') || query.includes('content') || query.includes('page') || query.includes('article')) {
      adminGroups.value.contentManagement = true
    }
    // Auto-expand analytics when searching
    if (query.includes('analytics') || query.includes('report') || query.includes('statistic') || query.includes('metric') || query.includes('dashboard') || query.includes('chart') || query.includes('graph') || query.includes('pricing') || query.includes('discount') || query.includes('referral') || query.includes('loyalty') || query.includes('campaign') || query.includes('geographic')) {
      // Analytics section doesn't have a collapsible group, but we can ensure it's visible
    }
    // Auto-expand system management when searching
    if (query.includes('config') || query.includes('setting') || query.includes('system') || query.includes('health') || query.includes('log') || query.includes('notification') || query.includes('email') || query.includes('duplicate') || query.includes('screened') || query.includes('flagged') || query.includes('message')) {
      // System management section visibility
    }
    // Auto-expand discipline when searching
    if (query.includes('discipline') || query.includes('appeal') || query.includes('blacklist') || query.includes('warning')) {
      // Discipline section visibility
    }
    // Auto-expand multi-tenant when searching
    if (query.includes('tenant') || query.includes('website') || query.includes('domain') || query.includes('multi')) {
      // Multi-tenant section visibility
    }
  }
  
  // Writer groups
  if (authStore.isWriter) {
    if (query.includes('order') || query.includes('queue') || query.includes('workload') || query.includes('calendar') || query.includes('available') || query.includes('assigned') || query.includes('my order')) {
      writerOrdersOpen.value = true
    }
    if (query.includes('payment') || query.includes('finance') || query.includes('tip') || query.includes('fine') || query.includes('advance') || query.includes('request') || query.includes('wallet')) {
      writerFinancesOpen.value = true
    }
    if (query.includes('review') || query.includes('performance') || query.includes('badge') || query.includes('rating') || query.includes('analytics')) {
      writerReviewsOpen.value = true
    }
    if (query.includes('profile') || query.includes('account') || query.includes('pen name') || query.includes('resource') || query.includes('setting')) {
      writerUserManagementOpen.value = true
    }
    if (query.includes('activity') || query.includes('communication') || query.includes('ticket') || query.includes('dashboard') || query.includes('message')) {
      writerActivityOpen.value = true
    }
    if (query.includes('discipline') || query.includes('appeal') || query.includes('status') || query.includes('history')) {
      writerDisciplineOpen.value = true
    }
  }
  
  // Client groups
  if (authStore.isClient) {
    if (query.includes('order') || query.includes('pending') || query.includes('progress') || query.includes('completed') || query.includes('unpaid') || query.includes('paid') || query.includes('template')) {
      ordersOpen.value = true
    }
    if (query.includes('wallet') || query.includes('balance') || query.includes('transaction')) {
      // Wallet section
    }
  }
  
  // Editor groups
  if (authStore.isEditor) {
    if (query.includes('task') || query.includes('available') || query.includes('performance')) {
      // Editor sections
    }
  }
  
  // Support groups
  if (authStore.isSupport) {
    if (query.includes('ticket') || query.includes('support') || query.includes('help')) {
      // Support sections
    }
  }
})
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
  contentManagement: false,
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
    if (newPath.startsWith('/admin/blog') || newPath.startsWith('/admin/seo-pages') || 
        newPath.startsWith('/admin/media-library') || newPath.startsWith('/admin/files')) {
      adminGroups.value.contentManagement = true
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

// Order status counts for sidebar
const orderStatusCounts = ref({
  pending: 0,
  in_progress: 0,
  submitted: 0,
  completed: 0,
  revision_requested: 0,
  disputed: 0,
  cancelled: 0,
  available: 0,
  on_hold: 0,
  under_editing: 0,
  unpaid: 0,
  paid: 0,
  total: 0,
  // Transition counts
  can_transition_to_in_progress: 0,
  can_transition_to_submitted: 0,
  can_transition_to_completed: 0,
  can_transition_to_cancelled: 0,
  can_transition_to_on_hold: 0,
  can_transition_to_available: 0,
  can_transition_to_revision_requested: 0,
  can_transition_to_disputed: 0,
  can_transition_to_under_editing: 0,
  can_transition_to_closed: 0,
  can_transition_to_reopened: 0,
})

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

// Load order status counts for sidebar
const loadOrderStatusCounts = async () => {
  if (!authStore.isAuthenticated) return
  
  try {
    // For admins, use admin dashboard API
    if (authStore.isAdmin || authStore.isSuperAdmin) {
      const resp = await adminOrdersAPI.getDashboard().catch(() => null)
      if (resp?.data?.summary) {
        const summary = resp.data.summary
        const transitionCounts = resp.data.transition_counts || {}
    orderStatusCounts.value = {
      pending: summary.pending_orders || 0,
      in_progress: summary.in_progress_orders || 0,
      submitted: summary.submitted_orders || 0,
      completed: summary.completed_orders || 0,
      revision_requested: summary.revision_requested_orders || 0,
      disputed: summary.disputed_orders || 0,
      cancelled: summary.cancelled_orders || 0,
      available: summary.available_orders || 0,
      on_hold: summary.on_hold_orders || 0,
      under_editing: summary.under_editing_orders || 0,
      unpaid: summary.unpaid_orders || 0,
      paid: summary.paid_orders || 0,
      total: summary.total_orders || 0,
      // Add transition counts
      can_transition_to_in_progress: summary.can_transition_to_in_progress || transitionCounts.can_transition_to_in_progress || 0,
      can_transition_to_submitted: summary.can_transition_to_submitted || transitionCounts.can_transition_to_submitted || 0,
      can_transition_to_completed: summary.can_transition_to_completed || transitionCounts.can_transition_to_completed || 0,
      can_transition_to_cancelled: summary.can_transition_to_cancelled || transitionCounts.can_transition_to_cancelled || 0,
      can_transition_to_on_hold: summary.can_transition_to_on_hold || transitionCounts.can_transition_to_on_hold || 0,
      can_transition_to_available: summary.can_transition_to_available || transitionCounts.can_transition_to_available || 0,
      can_transition_to_revision_requested: summary.can_transition_to_revision_requested || transitionCounts.can_transition_to_revision_requested || 0,
      can_transition_to_disputed: summary.can_transition_to_disputed || transitionCounts.can_transition_to_disputed || 0,
      can_transition_to_under_editing: summary.can_transition_to_under_editing || transitionCounts.can_transition_to_under_editing || 0,
      can_transition_to_closed: summary.can_transition_to_closed || transitionCounts.can_transition_to_closed || 0,
      can_transition_to_reopened: summary.can_transition_to_reopened || transitionCounts.can_transition_to_reopened || 0,
    }
        return
      }
    }
    
    // For clients and writers, fetch counts by status
    const statuses = ['pending', 'in_progress', 'submitted', 'completed', 'revision_requested', 'disputed', 'cancelled', 'available', 'on_hold', 'under_editing']
    const counts = {}
    
    // Fetch counts for each status
    await Promise.all(
      statuses.map(async (status) => {
        try {
          const resp = await ordersAPI.list({ status, page_size: 1 })
          counts[status] = resp?.data?.count || 0
        } catch {
          counts[status] = 0
        }
      })
    )
    
    // Also get unpaid/paid counts
    try {
      const unpaidResp = await ordersAPI.list({ is_paid: false, page_size: 1 })
      counts.unpaid = unpaidResp?.data?.count || 0
    } catch {
      counts.unpaid = 0
    }
    
    try {
      const paidResp = await ordersAPI.list({ is_paid: true, page_size: 1 })
      counts.paid = paidResp?.data?.count || 0
    } catch {
      counts.paid = 0
    }
    
    try {
      const totalResp = await ordersAPI.list({ page_size: 1 })
      counts.total = totalResp?.data?.count || 0
    } catch {
      counts.total = 0
    }
    
    orderStatusCounts.value = {
      pending: counts.pending || 0,
      in_progress: counts.in_progress || 0,
      submitted: counts.submitted || 0,
      completed: counts.completed || 0,
      revision_requested: counts.revision_requested || 0,
      disputed: counts.disputed || 0,
      cancelled: counts.cancelled || 0,
      available: counts.available || 0,
      on_hold: counts.on_hold || 0,
      under_editing: counts.under_editing || 0,
      unpaid: counts.unpaid || 0,
      paid: counts.paid || 0,
      total: counts.total || 0,
    }
  } catch (error) {
    // Sidebar should fail silently if metrics can't be loaded
    console.error('Failed to load order status counts:', error)
  }
}

// Notifications state
const showNotificationsDropdown = ref(false)
const showProfileDropdown = ref(false)
const unreadCount = ref(0)
const totalNotificationCount = ref(0)
const notificationsFilter = ref<'unread' | 'all'>('unread')
const recentNotifications = ref([])
const notificationsLoading = ref(false)
const markingAllRead = ref(false)
const notificationsDropdownRef = ref(null)
const profileDropdownRef = ref(null)

// Announcements state
const unreadAnnouncementsCount = ref(0)
let announcementsCountInterval = null

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
let orderCountsInterval = null

const appName = import.meta.env.VITE_APP_NAME || 'WriteFlow'

const hasTransitionCounts = computed(() => {
  if (!authStore.isAdmin && !authStore.isSuperAdmin) return false
  return (
    orderStatusCounts.value.can_transition_to_in_progress > 0 ||
    orderStatusCounts.value.can_transition_to_submitted > 0 ||
    orderStatusCounts.value.can_transition_to_completed > 0 ||
    orderStatusCounts.value.can_transition_to_on_hold > 0 ||
    orderStatusCounts.value.can_transition_to_revision_requested > 0 ||
    orderStatusCounts.value.can_transition_to_cancelled > 0 ||
    orderStatusCounts.value.can_transition_to_available > 0 ||
    orderStatusCounts.value.can_transition_to_disputed > 0 ||
    orderStatusCounts.value.can_transition_to_under_editing > 0 ||
    orderStatusCounts.value.can_transition_to_closed > 0 ||
    orderStatusCounts.value.can_transition_to_reopened > 0
  )
})

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
      name: 'ScreenedWordsManagement',
      to: '/admin/screened-words',
      label: 'Screened Words',
      icon: '🚫',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'FlaggedMessagesManagement',
      to: '/admin/flagged-messages',
      label: 'Flagged Messages',
      icon: '⚠️',
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
      name: 'UserManagement', // Use the actual route name, query params will be handled by the path
      to: '/admin/users?role=writer',
      label: 'Writer Management',
      icon: '✍️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'WriterResourcesManagement',
      to: '/admin/writer-resources',
      label: 'Writer Resources & Samples',
      icon: '📚',
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
      name: 'AnalyticsReports',
      to: '/admin/analytics-reports',
      label: 'Analytics & Reports',
      icon: '📈',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'RefinedStats',
      to: '/admin/geographic-analytics',
      label: 'Refined Stats',
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
      name: 'BlogAuthors',
      to: '/admin/blog-authors',
      label: 'Blog Authors',
      icon: '🖊️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'MediaLibrary',
      to: '/admin/media-library',
      label: 'Media Library',
      icon: '🖼️',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ContentMetricsDashboard',
      to: '/admin/content-metrics',
      label: 'Content Metrics',
      icon: '📈',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'ContentMetricsReport',
      to: '/admin/content-metrics-report',
      label: 'Content Reporting',
      icon: '📊',
      roles: ['admin', 'superadmin'],
    },
    {
      name: 'OrderStatusMetrics',
      to: '/admin/order-status-metrics',
      label: 'Order Status Metrics',
      icon: '📋',
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
      icon: '👤',
    },
    {
      name: 'Settings',
      to: '/profile/settings',
      label: 'Settings',
      icon: '🔧',
      roles: ['client', 'admin', 'superadmin', 'writer', 'editor', 'support'],
    },
    {
      name: 'PrivacySecurity',
      to: '/profile/privacy-security',
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
      name: 'Announcements',
      to: '/announcements',
      label: 'Announcements',
      icon: '📢',
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
  if (path.startsWith('/admin/blog') || path.startsWith('/admin/seo-pages') || 
      path.startsWith('/admin/media-library') || path.startsWith('/admin/files')) {
    adminGroups.value.contentManagement = true
  }
  // Also expand orders section for client orders (both /orders and /client/orders)
  if ((path.startsWith('/orders') || path.startsWith('/client/orders')) && authStore.isClient) {
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

// Load unread announcements count
const loadUnreadAnnouncementsCount = async () => {
  if (!authStore.isAuthenticated) {
    unreadAnnouncementsCount.value = 0
    return
  }
  try {
    const response = await announcementsAPI.getUnreadCount()
    unreadAnnouncementsCount.value = response.data.unread_count || 0
  } catch (error) {
    // Silently handle errors - don't spam console
    if (error.response?.status !== 429 && error.response?.status !== 401) {
      console.error('Failed to load unread announcements count:', error)
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
      limit: 5,
      status: notificationsFilter.value === 'unread' ? 'unread' : 'all',
    })
    
    // Handle both paginated (results) and non-paginated (array) responses
    let feedItems = []
    if (Array.isArray(response.data)) {
      // Non-paginated response
      feedItems = response.data
    } else if (response.data.results && Array.isArray(response.data.results)) {
      // Paginated response
      feedItems = response.data.results
      totalNotificationCount.value = response.data.count || response.data.total || feedItems.length
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

// Map emoji icons to SidebarIcon icon names
const getIconNameFromEmoji = (emoji) => {
  const emojiToIconMap = {
    '📊': 'chart-bar',
    '📝': 'document',
    '📋': 'clipboard',
    '💰': 'wallet',
    '💳': 'credit-card',
    '⭐': 'star',
    '📚': 'book',
    '⚡': 'lightning',
    '⚖️': 'scale',
    '💸': 'dollar-sign',
    '🚫': 'ban',
    '🎉': 'star',
    '💵': 'dollar-sign',
    '💼': 'wallet',
    '📄': 'document',
    '↩️': 'arrow-left',
    '👤': 'user',
    '👥': 'users',
    '✍️': 'pencil',
    '🎧': 'headphones',
    '👔': 'user-circle',
    '🎫': 'ticket',
    '📈': 'trending-up',
    '📉': 'trending-down',
    '🏆': 'trophy',
    '🏅': 'academic-cap',
    '⚙️': 'cog',
    '✏️': 'pencil',
    '🛡️': 'shield',
    '🛑': 'stop',
    '⏰': 'clock-alarm',
    '📅': 'calendar',
    '📜': 'scroll',
    '💬': 'chat',
    '🎁': 'gift',
    '🎟️': 'discount',
    '🔒': 'shield',
    '🔍': 'search',
    '🌐': 'home',
    '👑': 'star',
    '📧': 'mail',
    '🔔': 'bell',
    '📢': 'megaphone',
    '🏥': 'shield',
    '🎛️': 'cog',
  }
  return emojiToIconMap[emoji] || 'document'
}

const handleLogout = async () => {
  try {
    // Close all dropdowns
    closeNotificationsDropdown()
    closeActivitiesDropdown()
    closeProfileDropdown()
    
    // Stop session monitoring
    if (sessionManager) {
      sessionManager.stop()
    }
    
    // Clear intervals
    if (unreadCountInterval) {
      clearTimeout(unreadCountInterval)
      unreadCountInterval = null
    }
    if (orderCountsInterval) {
      clearInterval(orderCountsInterval)
      orderCountsInterval = null
    }
    if (announcementsCountInterval) {
      clearInterval(announcementsCountInterval)
      announcementsCountInterval = null
    }
    
    // Logout (this will handle redirect)
    await authStore.logout()
  } catch (error) {
    console.error('Error during logout:', error)
    // Force redirect even if logout fails
    window.location.href = '/login'
  }
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
  
  // Listen for postMessage redirects from impersonation tabs
  const handlePostMessage = (event) => {
    // Verify origin for security
    if (event.origin !== window.location.origin) {
      return
    }
    
    if (event.data && event.data.type === 'redirect' && event.data.path) {
      router.push(event.data.path)
    }
  }
  window.addEventListener('message', handlePostMessage)
  
  // Store handler for cleanup
  window._impersonationRedirectHandler = handlePostMessage
  
  // Load initial unread count
  loadUnreadCount()
  loadUnreadAnnouncementsCount()
  
  // Load order status counts
  loadOrderStatusCounts()
  loadWriterSidebarMetrics()
  
  // Refresh order counts periodically (every 2 minutes)
  orderCountsInterval = setInterval(() => {
    loadOrderStatusCounts()
    if (authStore.isWriter) {
      loadWriterSidebarMetrics()
    }
  }, 120000) // 2 minutes
  
  // Poll for unread announcements count (every 2 minutes)
  announcementsCountInterval = setInterval(() => {
    loadUnreadAnnouncementsCount()
  }, 120000) // 2 minutes
  
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
  
  // Also reload when route changes (user might have read notifications or announcements)
  router.afterEach(() => {
    loadUnreadCount()
    loadUnreadAnnouncementsCount()
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
  if (orderCountsInterval) {
    clearInterval(orderCountsInterval)
    orderCountsInterval = null
  }
  if (announcementsCountInterval) {
    clearInterval(announcementsCountInterval)
    announcementsCountInterval = null
  }
  document.removeEventListener('click', handleClickOutside)
  
  // Clean up postMessage listener
  if (window._impersonationRedirectHandler) {
    window.removeEventListener('message', window._impersonationRedirectHandler)
    delete window._impersonationRedirectHandler
  }
  
  sessionManager.stop() // Stop session monitoring
})
</script>

<style scoped>
/* Animation for fade-in */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}

/* Slow spin animation for in-progress items */
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}

/* Improved typography and spacing */
.sidebar-section-title {
  letter-spacing: 0.05em;
  font-size: 0.6875rem; /* 11px */
  line-height: 1.5;
}

/* Better line height for navigation items */
nav a,
nav button {
  line-height: 1.6;
}

/* Improved spacing for nested items */
.animate-fade-in {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Better font rendering */
nav {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "kern" 1;
  text-rendering: optimizeLegibility;
}

/* Improved readability for small text */
.text-xs {
  font-size: 0.6875rem; /* 11px */
  line-height: 1.5;
}

/* Better spacing for section dividers */
.border-t {
  border-top-width: 1px;
}

/* Smooth transitions for sidebar items */
.sidebar-item {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-item:hover {
  transform: translateX(2px);
}

/* Improved spacing for nested items */
.sidebar-nested {
  margin-left: 1.5rem;
  padding-left: 0.5rem;
  border-left: 2px solid transparent;
  transition: border-color 0.2s;
}

/* Custom scrollbar for sidebar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
  transition: background 0.2s;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.3);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.5);
}

.sidebar-nested:hover {
  border-left-color: rgb(59 130 246);
}

/* Enhanced visual hierarchy */
.sidebar-section-title {
  letter-spacing: 0.05em;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgb(107 114 128);
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

/* Custom scrollbar for sidebar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 3px;
  transition: background 0.2s;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(75, 85, 99, 0.3);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(75, 85, 99, 0.5);
}
</style>

