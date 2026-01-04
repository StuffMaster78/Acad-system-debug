<template>
      <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
  <div class="space-y-5 sm:space-y-6 md:space-y-8 p-4 sm:p-5 md:p-6 lg:p-8" v-if="!componentError && !initialLoading">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Regular Orders Management</h1>
        <p class="mt-1 sm:mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-400">Manage regular writing orders, assignments, and status transitions</p>
      </div>
      <div class="flex gap-3">
        <router-link
          to="/admin/orders/create"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Order
        </router-link>
      </div>
    </div>

    <!-- Stats Cards - 2 Columns, 3 Rows Layout -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <!-- Row 1 -->
      <StatusCard
        label="Total Orders"
        :value="dashboardData?.summary?.total_orders || stats.total || 0"
        icon-svg="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        variant="primary"
        @click="filterByStatus('')"
      />
      <StatusCard
        label="In Progress"
        :value="dashboardData?.summary?.in_progress_orders || stats.in_progress || 0"
        icon-svg="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        variant="warning"
        @click="filterByStatus('in_progress')"
      />
      
      <!-- Row 2 -->
      <StatusCard
        label="Completed"
        :value="dashboardData?.summary?.completed_orders || stats.completed || 0"
        icon-svg="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        variant="success"
        @click="filterByStatus('completed')"
      />
      <StatusCard
        label="Total Revenue"
        :value="dashboardData?.summary?.total_revenue || 0"
        icon-svg="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        variant="info"
        unit="$"
        :format-value="(v) => formatCurrency(v)"
        @click="filterByStatus('')"
      />
      
      <!-- Row 3 -->
      <StatusCard
        label="Needs Assignment"
        :value="dashboardData?.summary?.needs_assignment || 0"
        icon-svg="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        variant="warning"
        :badge="dashboardData?.summary?.needs_assignment > 0 ? 'Action Required' : null"
        @click="filterByNeedsAssignment"
      />
      <StatusCard
        label="Overdue"
        :value="dashboardData?.summary?.overdue_orders || 0"
        icon-svg="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        variant="danger"
        :badge="dashboardData?.summary?.overdue_orders > 0 ? 'Urgent' : null"
        @click="filterByOverdue"
      />
    </div>
    
    <!-- Additional Stats Row - 2 Columns -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <StatusCard
        label="Avg Order Value"
        :value="dashboardData?.summary?.avg_order_value || 0"
        icon-svg="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        variant="info"
        unit="$"
        :format-value="(v) => formatCurrency(v)"
        @click="filterByStatus('')"
      />
      <StatusCard
        label="Pending Orders"
        :value="dashboardData?.summary?.pending_orders || 0"
        icon-svg="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        variant="info"
        @click="filterByStatus('pending')"
      />
    </div>
    
    <!-- Quick Action Tabs -->
    <div class="border-b border-gray-200 mb-3 sm:mb-4">
      <nav class="-mb-px flex space-x-3 sm:space-x-4 md:space-x-6 lg:space-x-8 overflow-x-auto scrollbar-hide">
        <button
          @click="activeQuickTab = 'all'"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm shrink-0',
            activeQuickTab === 'all'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          All Orders
        </button>
        <button
          @click="activeQuickTab = 'assignment'"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm shrink-0',
            activeQuickTab === 'assignment'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Assignment Queue
          <span v-if="dashboardData?.summary?.needs_assignment" class="ml-1 sm:ml-2 bg-orange-500 text-white text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 rounded-full">
            {{ dashboardData.summary.needs_assignment }}
          </span>
        </button>
        <button
          @click="activeQuickTab = 'overdue'"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm shrink-0',
            activeQuickTab === 'overdue'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Overdue
          <span v-if="dashboardData?.summary?.overdue_orders" class="ml-1 sm:ml-2 bg-red-500 text-white text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 rounded-full">
            {{ dashboardData.summary.overdue_orders }}
          </span>
        </button>
        <button
          @click="activeQuickTab = 'stuck'"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm shrink-0',
            activeQuickTab === 'stuck'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Stuck Orders
        </button>
        <button
          @click="activeQuickTab = 'writer-requests'"
          :class="[
            'whitespace-nowrap py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm shrink-0',
            activeQuickTab === 'writer-requests'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Writer Requests
          <span
            v-if="writerRequests.length"
            class="ml-1 sm:ml-2 bg-indigo-500 text-white text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5 rounded-full"
          >
            {{ writerRequests.length }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Assignment Queue -->
    <div v-if="activeQuickTab === 'assignment'" class="card p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold">Orders Needing Assignment</h2>
        <div class="flex items-center gap-2 text-sm text-gray-600">
          <span>Sorted by priority</span>
          <button
            @click="loadAssignmentQueue"
            :disabled="loadingAssignment"
            class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm transition-colors"
          >
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
      
      <div v-if="loadingAssignment" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-2 text-gray-500">Loading assignment queue...</p>
      </div>
      <div v-else-if="assignmentQueue.length === 0" class="text-center py-8 text-gray-500">
        <p class="text-sm font-medium">No orders need assignment</p>
        <p class="text-xs mt-1">All orders have been assigned or are in progress</p>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="order in assignmentQueue"
          :key="order.id"
          class="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="flex justify-between items-start gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-gray-900 dark:text-gray-100">Order #{{ order.id }}</span>
                  <span
                    v-if="order.priority_score"
                    class="px-2 py-0.5 text-xs font-bold rounded"
                    :class="getPriorityBadgeClass(order.priority_score)"
                  >
                    Priority: {{ order.priority_score.toFixed(1) }}
                  </span>
                </div>
              </div>
              
              <p class="font-medium text-gray-900 dark:text-gray-100 mb-1">
                {{ order.topic || 'Untitled Order' }}
              </p>
              
              <div class="flex flex-wrap items-center gap-3 text-sm text-gray-600 dark:text-gray-400 mb-2">
                <span class="inline-flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(order.website || order.website_name)"></span>
                  {{ getWebsiteName(order) }}
                </span>
                <span>·</span>
                <span>Client: {{ order.client_username || 'N/A' }}</span>
                <span>·</span>
                <span>Status: <span class="font-medium">{{ order.status }}</span></span>
                <span v-if="order.urgency" class="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs font-medium">
                  {{ order.urgency === 'high' ? '🔴 High Urgency' : order.urgency === 'medium' ? '🟡 Medium' : '🟢 Normal' }}
                </span>
              </div>
              
              <!-- Writer Requests (if any) -->
              <div v-if="order.writer_requests && order.writer_requests.length > 0" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Writer Requests ({{ order.writer_requests.length }})
                </p>
                <div class="space-y-2">
                  <div
                    v-for="request in order.writer_requests.slice(0, 3)"
                    :key="request.id"
                    class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs"
                  >
                    <div class="flex items-center gap-2">
                      <span class="font-medium">{{ request.writer_username || request.writer_name || 'Writer' }}</span>
                      <span
                        v-if="request.priority_score"
                        class="px-1.5 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded"
                      >
                        Score: {{ request.priority_score.toFixed(1) }}
                      </span>
                      <span v-if="request.rating" class="text-gray-500">
                        ⭐ {{ request.rating.toFixed(1) }}
                      </span>
                    </div>
                    <button
                      @click.stop="openAssignModalFromRequest(request)"
                      class="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-xs transition-colors"
                    >
                      Assign
                    </button>
                  </div>
                  <p v-if="order.writer_requests.length > 3" class="text-xs text-gray-500 text-center">
                    +{{ order.writer_requests.length - 3 }} more request(s)
                  </p>
                </div>
              </div>
            </div>
            
            <div class="flex flex-col gap-2">
              <button
                v-if="!order.assigned_writer && !order.writer_username && order.is_paid"
                @click.stop="openAssignModal(order)"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium whitespace-nowrap"
              >
                Assign Writer
              </button>
              <button
                v-else-if="!order.assigned_writer && !order.writer_username && !order.is_paid"
                @click.stop="showUnpaidWarningModal = true; currentOrderForAction = order"
                class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm font-medium whitespace-nowrap"
                title="Order must be paid before assigning writer"
              >
                ⚠️ Assign Writer
              </button>
              <button
                @click.stop="viewOrder(order)"
                class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm whitespace-nowrap"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Overdue Orders -->
    <div v-if="activeQuickTab === 'overdue'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 sm:p-6">
      <h2 class="text-xl font-bold mb-4">Overdue Orders</h2>
      <div v-if="loadingOverdue" class="text-center py-8">Loading...</div>
      <div v-else-if="overdueOrders.length === 0" class="text-center py-8 text-gray-500">
        No overdue orders
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in overdueOrders"
          :key="order.id"
          class="border border-red-200 rounded p-4 hover:bg-red-50 cursor-pointer"
          @click="viewOrder(order)"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold text-red-900">Order #{{ order.id }} - {{ order.topic }}</p>
              <p class="text-sm text-gray-600">
                <span class="inline-flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(order.website || order.website_name)"></span>
                  {{ getWebsiteName(order) }}
                </span>
                · Client: {{ order.client_username || 'N/A' }}
              </p>
              <p class="text-sm text-red-600">Deadline: {{ formatDate(order.client_deadline) }}</p>
            </div>
            <span class="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">Overdue</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Stuck Orders -->
    <div v-if="activeQuickTab === 'stuck'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 sm:p-6">
      <h2 class="text-xl font-bold mb-4">Stuck Orders (No Progress)</h2>
      <div v-if="loadingStuck" class="text-center py-8">Loading...</div>
      <div v-else-if="stuckOrders.length === 0" class="text-center py-8 text-gray-500">
        No stuck orders
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in stuckOrders"
          :key="order.id"
          class="border border-yellow-200 rounded p-4 hover:bg-yellow-50 cursor-pointer"
          @click="viewOrder(order)"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold text-yellow-900">Order #{{ order.id }} - {{ order.topic }}</p>
              <p class="text-sm text-gray-600">
                <span class="inline-flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(order.website || order.website_name)"></span>
                  {{ getWebsiteName(order) }}
                </span>
                · Client: {{ order.client_username || 'N/A' }}
              </p>
              <p class="text-sm text-yellow-600">Last Updated: {{ formatDate(order.updated_at) }}</p>
            </div>
            <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">Stuck</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Writer Order Requests -->
    <div v-if="activeQuickTab === 'writer-requests'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 sm:p-6">
      <h2 class="text-xl font-bold mb-4">Writer Order Requests</h2>
      <p class="text-sm text-gray-600 mb-4">
        Review and manage orders that writers have requested to work on.
      </p>

      <div v-if="loadingWriterRequests" class="text-center py-8">
        Loading writer requests...
      </div>
      <div v-else-if="writerRequests.length === 0" class="text-center py-8 text-gray-500">
        <p>No writer requests found.</p>
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="req in writerRequests"
          :key="req.id"
          class="border rounded p-4 hover:bg-gray-50 cursor-pointer"
          @click="viewOrder({ id: req.order_id || req.order?.id })"
        >
          <div class="flex justify-between items-start">
            <div class="space-y-1">
              <p class="font-semibold">
                Order #{{ req.order_id || req.order?.id }} -
                {{ req.order_topic || req.order?.topic || 'No topic' }}
              </p>
              <p class="text-sm text-gray-600">
                <span class="inline-flex items-center gap-1">
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="getWebsiteColorClass(req.website || req.website_name || (req.order && req.order.website))"
                  ></span>
                  {{ req.website_name || getWebsiteName(req.order || {}) }}
                </span>
                · Writer:
                {{ req.writer_name || req.writer_username || req.writer?.user?.username || req.writer_id || 'N/A' }}
              </p>
              <p class="text-xs text-gray-500">
                Requested: {{ formatDateTime(req.requested_at || req.created_at) }}
              </p>
            </div>
            <div class="flex flex-col gap-2 items-end">
              <span
                class="px-2 py-1 rounded-full text-xs font-semibold"
                :class="req.approved ? 'bg-green-100 text-green-800' : (req.rejected ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800')"
              >
                {{ req.approved ? 'Approved' : (req.rejected ? 'Rejected' : 'Pending') }}
              </span>
              <button
                v-if="!req.approved && !req.rejected"
                @click.stop="openAssignModalFromRequest(req)"
                class="btn btn-primary btn-sm"
              >
                Assign from Request
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-5 sm:p-6 mb-6">
      <div class="space-y-4">
        <!-- First Row: Main Filters -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Order ID"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Website</label>
            <select 
              v-model="filters.website" 
              @change="loadOrders" 
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Websites</option>
              <option v-for="website in uniqueWebsites" :key="website.id || website" :value="website.id || website">
                {{ typeof website === 'string' ? website : (website.name || website.domain || website.id || 'N/A') }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Status</label>
            <select 
              v-model="filters.status" 
              @change="loadOrders" 
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Statuses</option>
              <option value="created">Created</option>
              <option value="pending">Pending</option>
              <option value="unpaid">Unpaid</option>
              <option value="available">Available</option>
              <option value="in_progress">In Progress</option>
              <option value="on_hold">On Hold</option>
              <option value="submitted">Submitted</option>
              <option value="under_editing">Under Editing</option>
              <option value="completed">Completed</option>
              <option value="disputed">Disputed</option>
              <option value="cancelled">Cancelled</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Payment</label>
            <select 
              v-model="filters.is_paid" 
              @change="loadOrders" 
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">All</option>
              <option value="true">Paid</option>
              <option value="false">Unpaid</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Include Archived</label>
            <select 
              v-model="filters.include_archived" 
              @change="loadOrders" 
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option :value="true">Yes (All Orders)</option>
              <option :value="false">No (Exclude Archived)</option>
            </select>
          </div>
        </div>

        <!-- Second Row: Additional Filters and Actions -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Client</label>
            <input
              v-model="filters.client"
              @input="debouncedSearch"
              type="text"
              placeholder="Client username"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Writer</label>
            <input
              v-model="filters.writer"
              @input="debouncedSearch"
              type="text"
              placeholder="Writer username"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-2 cursor-pointer h-10 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <input
                type="checkbox"
                v-model="filters.include_deleted"
                @change="loadOrders"
                class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Include Deleted</span>
            </label>
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-2 cursor-pointer h-10 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <input
                type="checkbox"
                v-model="filters.only_deleted"
                @change="loadOrders"
                class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Only Deleted</span>
            </label>
          </div>
          <div class="flex items-end sm:col-span-2 lg:col-span-1">
            <button 
              @click="resetFilters" 
              class="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedOrders.length > 0" class="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl border-2 border-yellow-300 dark:border-yellow-700 shadow-sm p-5 sm:p-6 mb-6">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-yellow-800">
          {{ selectedOrders.length }} order(s) selected
        </span>
        <div class="flex gap-2">
          <button @click="openBulkAssignModal" class="btn btn-sm btn-primary">Bulk Assign</button>
          <button @click="bulkAutoAssign" class="btn btn-sm btn-indigo">Auto-Assign Selected</button>
          <button @click="bulkStatusChange" class="btn btn-sm btn-primary">Change Status</button>
          <button @click="selectedOrders = []" class="btn btn-sm btn-secondary">Clear Selection</button>
        </div>
      </div>
    </div>

    <!-- All Orders Table -->
    <div id="orders-list-section" v-if="activeQuickTab === 'all'" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                <input type="checkbox" @change="toggleSelectAll" :checked="allSelected" />
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payment</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deadline</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in orders" :key="order.id" :class="['hover:bg-gray-50', order.is_deleted ? 'bg-red-50 opacity-75' : '']">
              <td class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="order.id" 
                  v-model="selectedOrders"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <div class="flex items-center gap-2">
                  #{{ order.id }}
                  <span v-if="order.is_deleted" class="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-semibold" title="Soft Deleted">🗑️ Deleted</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div v-if="order.website || order.website_name" class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(order.website || order.website_name)"></div>
                  <span class="text-gray-700 font-medium">{{ getWebsiteName(order) }}</span>
                </div>
                <span v-else class="text-gray-400 italic">N/A</span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">{{ order.topic || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ order.client_username || order.client?.username || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                <span v-if="order.writer_username || order.assigned_writer">
                  {{ order.writer_username || order.assigned_writer?.username || 'N/A' }}
                </span>
                <button 
                  v-else-if="order.is_paid" 
                  @click="openAssignModal(order)" 
                  class="text-blue-600 hover:underline text-xs"
                >
                  Assign
                </button>
                <button 
                  v-else 
                  @click="showUnpaidWarningModal = true; currentOrderForAction = order" 
                  class="text-yellow-600 hover:underline text-xs font-semibold"
                  title="Order must be paid before assigning writer"
                >
                  ⚠️ Assign
                </button>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(order.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ getStatusLabel(order.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="order.is_paid ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ order.is_paid ? 'Paid' : 'Unpaid' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${{ parseFloat(order.total_price || 0).toFixed(2) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatDate(order.client_deadline || order.deadline) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatDate(order.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex gap-2">
                  <button @click="viewOrder(order)" class="text-blue-600 hover:underline">View</button>
                  <button @click="openActionMenu(order)" class="text-gray-600 hover:underline">Actions</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && orders.length === 0" class="text-center py-12 text-gray-500">
        <p>No orders found</p>
      </div>
    </div>

    <!-- Order Detail Modal - Removed: Now using page-based navigation -->
    <!-- Modal removed - order details now open in a dedicated page at /admin/orders/:id -->
    <div v-if="false" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-6xl w-full my-auto max-h-[95vh] overflow-y-auto shadow-2xl">
        <div class="p-6">
          <!-- Header -->
          <div class="flex items-center justify-between mb-6 pb-4 border-b">
            <div>
              <h2 class="text-3xl font-bold text-gray-900">Order #{{ viewingOrder.id }}</h2>
              <p class="text-sm text-gray-600 mt-1 flex items-center gap-2">
                <span>{{ viewingOrder.topic || 'Untitled Order' }}</span>
                <EnhancedStatusBadge
                  v-if="viewingOrder.status"
                  :status="viewingOrder.status"
                  :show-tooltip="true"
                  :show-priority="true"
                />
                <span
                  v-if="viewingOrder.is_paid !== undefined"
                  :class="[
                    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                    viewingOrder.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  ]"
                >
                  {{ viewingOrder.is_paid ? 'Paid' : 'Unpaid' }}
                </span>
              </p>
            </div>
            <button @click="closeOrderModal" class="text-gray-500 hover:text-gray-700 text-2xl p-2 hover:bg-gray-100 rounded-lg transition-colors">✕</button>
          </div>

          <!-- Tabs Navigation -->
          <div class="border-b border-gray-200 mb-6">
            <nav class="flex space-x-1 overflow-x-auto" aria-label="Tabs">
              <button
                v-for="tab in orderTabs"
                :key="tab.id"
                @click="handleTabChange(tab.id)"
                :class="[
                  'py-3 px-4 border-b-2 font-medium text-sm transition-all relative whitespace-nowrap',
                  activeOrderTab === tab.id
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                <span class="flex items-center gap-2">
                  <span>{{ tab.icon }}</span>
                  <span>{{ tab.label }}</span>
                  </span>
              </button>
            </nav>
                </div>

          <!-- Overview Tab -->
          <div v-if="activeOrderTab === 'overview'" class="space-y-6">
            <!-- Order Details Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Left Column: Basic Information -->
              <div class="space-y-6">
                <!-- Order Identification -->
                <div class="bg-gray-50 rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Order Identification</h3>
                  <div class="space-y-3 text-sm">
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Order ID:</span>
                      <span class="font-mono text-gray-900">#{{ viewingOrder.id }}</span>
                </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Status:</span>
                      <EnhancedStatusBadge
                        v-if="viewingOrder.status"
                        :status="viewingOrder.status"
                        :show-tooltip="true"
                      />
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Date Posted:</span>
                      <span class="text-gray-900">{{ formatDateTime(viewingOrder.created_at) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Client Information -->
                <div class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Client Information</h3>
                  <div class="space-y-3 text-sm">
                    <div v-if="viewingOrder.is_unattributed" class="bg-orange-50 border border-orange-200 rounded-lg p-3 space-y-2">
                      <div class="flex justify-between items-center">
                        <span class="font-medium text-orange-700">Order Type:</span>
                        <span class="text-orange-600 font-semibold">Unattributed</span>
                      </div>
                      <div v-if="viewingOrder.fake_client_id" class="flex justify-between items-center">
                        <span class="font-medium text-gray-700">Client ID (shown to writer):</span>
                        <span class="font-mono text-gray-600">{{ viewingOrder.fake_client_id }}</span>
                      </div>
                      <div v-if="viewingOrder.external_contact_name" class="flex justify-between items-center">
                        <span class="font-medium text-gray-700">Contact Name:</span>
                        <span class="text-gray-900">{{ viewingOrder.external_contact_name }}</span>
                      </div>
                      <div v-if="viewingOrder.external_contact_email" class="flex justify-between items-center">
                        <span class="font-medium text-gray-700">Contact Email:</span>
                        <span class="text-gray-900">{{ viewingOrder.external_contact_email }}</span>
                      </div>
                    </div>
                    <div v-else class="space-y-3">
                      <div class="flex items-center justify-between">
                        <span class="font-medium text-gray-600">Client:</span>
                        <div class="flex items-center gap-2">
                          <UserDisplayName :user="(typeof viewingOrder.client === 'object' && viewingOrder.client !== null) ? viewingOrder.client : { id: viewingOrder.client_id || viewingOrder.client, role: 'client', registration_id: viewingOrder.client_registration_id }" />
                          <OnlineStatusIndicator
                            v-if="viewingOrder.client_id"
                            :user-id="viewingOrder.client_id"
                            :show-time-indicator="true"
                          />
                        </div>
                      </div>
                      <div v-if="viewingOrder.client" class="flex items-center justify-between">
                        <span class="font-medium text-gray-600">Client Email:</span>
                        <span class="text-gray-900">{{ viewingOrder.client.email || viewingOrder.client_email || 'N/A' }}</span>
                      </div>
                      <div v-if="viewingOrder.client" class="flex items-center justify-between">
                        <span class="font-medium text-gray-600">Registration ID:</span>
                        <span class="font-mono text-gray-900">{{ viewingOrder.client.registration_id || viewingOrder.client_registration_id || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Writer Information -->
                <div v-if="viewingOrder.writer_username || viewingOrder.writer || viewingOrder.assigned_writer" class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Writer Information</h3>
                  <div class="space-y-3 text-sm">
                    <div class="flex items-center justify-between">
                      <span class="font-medium text-gray-600">Writer:</span>
                      <div class="flex items-center gap-2">
                        <UserDisplayName :user="(typeof (viewingOrder.writer || viewingOrder.assigned_writer) === 'object' && (viewingOrder.writer || viewingOrder.assigned_writer) !== null) ? (viewingOrder.writer || viewingOrder.assigned_writer) : { id: viewingOrder.writer_id || viewingOrder.writer || viewingOrder.assigned_writer, role: 'writer', pen_name: viewingOrder.writer_pen_name, registration_id: viewingOrder.writer_registration_id }" />
                        <OnlineStatusIndicator
                          v-if="viewingOrder.writer_id"
                          :user-id="viewingOrder.writer_id"
                          :show-time-indicator="true"
                        />
                      </div>
                    </div>
                    <div v-if="viewingOrder.writer" class="flex items-center justify-between">
                      <span class="font-medium text-gray-600">Writer Email:</span>
                      <span class="text-gray-900">{{ viewingOrder.writer.email || viewingOrder.writer_email || 'N/A' }}</span>
                    </div>
                    <div v-if="viewingOrder.writer" class="flex items-center justify-between">
                      <span class="font-medium text-gray-600">Registration ID:</span>
                      <span class="font-mono text-gray-900">{{ viewingOrder.writer.registration_id || viewingOrder.writer_registration_id || 'N/A' }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Writer Information</h3>
                  <div class="text-sm">
                  <button 
                      v-if="viewingOrder.is_paid" 
                    @click="openAssignModal(viewingOrder)" 
                      class="text-blue-600 hover:underline font-medium"
                  >
                    Assign Writer
                  </button>
                  <button 
                    v-else 
                      @click="showUnpaidWarningModal = true; currentOrderForAction = viewingOrder" 
                      class="text-yellow-600 hover:underline font-semibold"
                    title="Order must be paid before assigning writer"
                  >
                      ⚠️ Assign Writer (Unpaid)
                  </button>
                </div>
                </div>

                <!-- Order Specifications -->
                <div class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Order Specifications</h3>
                  <div class="space-y-3 text-sm">
                    <div v-if="viewingOrder.website || viewingOrder.website_name" class="flex items-center justify-between">
                      <span class="font-medium text-gray-600">Website:</span>
                      <div class="flex items-center gap-2">
                        <div class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(viewingOrder.website || viewingOrder.website_name)"></div>
                        <span class="text-gray-900">{{ getWebsiteName(viewingOrder) }}</span>
                      </div>
                    </div>
                    <div v-if="viewingOrder.type_of_work" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Type of Work:</span>
                      <span class="text-gray-900">{{ viewingOrder.type_of_work?.name || viewingOrder.type_of_work_name || 'N/A' }}</span>
                    </div>
                    <div v-if="viewingOrder.academic_level" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Academic Level:</span>
                      <span class="text-gray-900">{{ viewingOrder.academic_level?.name || viewingOrder.academic_level_name || 'N/A' }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Number of Pages:</span>
                      <span class="text-gray-900">{{ viewingOrder.number_of_pages || 0 }}</span>
                    </div>
                    <div v-if="viewingOrder.number_of_slides" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Number of Slides:</span>
                      <span class="text-gray-900">{{ viewingOrder.number_of_slides || 0 }}</span>
                    </div>
                    <div v-if="viewingOrder.number_of_refereces || viewingOrder.number_of_sources" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Number of Sources:</span>
                      <span class="text-gray-900">{{ viewingOrder.number_of_refereces || viewingOrder.number_of_sources || 0 }}</span>
                    </div>
                    <div v-if="viewingOrder.formatting_style" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Formatting Style:</span>
                      <span class="text-gray-900">{{ viewingOrder.formatting_style?.name || viewingOrder.formatting_style_name || 'N/A' }}</span>
                    </div>
                    <div v-if="viewingOrder.english_type" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">English Type:</span>
                      <span class="text-gray-900">{{ viewingOrder.english_type?.name || viewingOrder.english_type_name || 'N/A' }}</span>
                    </div>
                  </div>
                </div>

                <!-- Additional Services -->
                <div v-if="viewingOrder.extra_services && viewingOrder.extra_services.length > 0" class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Additional Services</h3>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="service in viewingOrder.extra_services"
                      :key="service.id || service"
                      class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium"
                    >
                      {{ service.name || service }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Right Column: Timeline, Financial, Deadlines -->
              <div class="space-y-6">
                <!-- Status Timeline -->
                <div class="bg-white rounded-lg border border-gray-200 p-4">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">Status Timeline</h3>
                    <span class="text-xs font-medium text-gray-600 bg-gray-100 px-3 py-1.5 rounded-full">
                      {{ statusTimeline.length }} {{ statusTimeline.length === 1 ? 'event' : 'events' }}
                    </span>
                  </div>
                  <div v-if="statusTimeline.length === 0" class="text-sm text-gray-500 py-8 text-center">
                    <p>No status updates recorded yet.</p>
                  </div>
                  <ol v-else class="relative border-l-2 border-gray-300 pl-8 space-y-6">
                    <li
                      v-for="(entry, index) in statusTimeline"
                      :key="entry.key"
                      class="relative group pb-2"
                    >
                      <span 
                        class="absolute -left-[34px] top-0.5 w-8 h-8 rounded-full bg-blue-50 border-2 border-white shadow-md flex items-center justify-center text-lg transition-all duration-200 group-hover:scale-110 z-10"
                        :class="{
                          'ring-2 ring-blue-200': index === statusTimeline.length - 1
                        }"
                      >
                        {{ entry.icon }}
                      </span>
                      <div class="w-full min-w-0 pr-4">
                        <div class="text-sm font-semibold text-gray-900 mb-1">
                          {{ entry.label }}
                        </div>
                        <div v-if="entry.description" class="text-xs text-gray-600 mb-1">
                          {{ entry.description }}
                        </div>
                        <div class="text-xs text-gray-500">
                          {{ entry.relativeTime }}
                        </div>
                      </div>
                    </li>
                  </ol>
                </div>

                <!-- Financial Information -->
                <div class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Financial Information</h3>
                  <div class="space-y-3 text-sm">
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Total Price:</span>
                      <span class="text-gray-900 font-semibold">${{ parseFloat(viewingOrder.total_price || 0).toFixed(2) }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Writer Compensation:</span>
                      <span class="text-gray-900">${{ parseFloat(viewingOrder.writer_compensation || 0).toFixed(2) }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Paid:</span>
                      <span :class="viewingOrder.is_paid ? 'text-green-600 font-semibold' : 'text-yellow-600 font-semibold'">
                    {{ viewingOrder.is_paid ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
            </div>

                <!-- Deadlines -->
                <div class="bg-white rounded-lg border border-gray-200 p-4">
                  <h3 class="text-lg font-semibold mb-4 text-gray-900">Deadlines</h3>
                  <div class="space-y-3 text-sm">
                    <div v-if="viewingOrder.client_deadline" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Client Deadline:</span>
                      <span class="text-gray-900">{{ formatDateTime(viewingOrder.client_deadline) }}</span>
              </div>
                    <div v-if="viewingOrder.writer_deadline" class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Writer Deadline:</span>
                      <span class="text-gray-900">{{ formatDateTime(viewingOrder.writer_deadline) }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Created:</span>
                      <span class="text-gray-900">{{ formatDateTime(viewingOrder.created_at) }}</span>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="font-medium text-gray-600">Last Updated:</span>
                      <span class="text-gray-900">{{ formatDateTime(viewingOrder.updated_at) }}</span>
                    </div>
                  </div>
                </div>
            </div>
          </div>

            <!-- Progress Bar -->
            <div
              v-if="viewingOrder.assigned_writer && (displayProgressPercentage > 0 || viewingOrder.status === 'in_progress' || viewingOrder.status === 'submitted')"
              class="bg-white rounded-lg border border-gray-200 p-6"
            >
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Order Progress</h3>
                <button
                  @click="loadLatestProgress"
                  class="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-1.5"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
              </div>
              <ProgressBar
                :progress-percentage="displayProgressPercentage"
                :last-update="latestProgressUpdate"
              />
            </div>

            <!-- Instructions -->
            <div
              v-if="viewingOrder.instructions || viewingOrder.order_instructions"
              class="bg-white rounded-lg border border-gray-200 p-6"
            >
              <h3 class="text-lg font-semibold mb-4 text-gray-900">Instructions</h3>
              <div class="prose prose-sm max-w-none">
                <SafeHtml 
                  :content="viewingOrder.instructions || viewingOrder.order_instructions"
                  container-class="text-gray-700 text-sm leading-relaxed"
                />
              </div>
            </div>

            <!-- Notes -->
            <div
              v-if="viewingOrder.completion_notes"
              class="bg-white rounded-lg border border-gray-200 p-4"
            >
              <h3 class="text-lg font-semibold mb-3 text-gray-900">Notes</h3>
              <div class="text-gray-700 text-sm whitespace-pre-wrap">{{ viewingOrder.completion_notes }}</div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t flex-wrap">
            <button @click="showOrderThreadsModal = true" class="btn btn-primary bg-blue-600 hover:bg-blue-700">
              💬 View Messages
            </button>
            <button 
              v-if="!viewingOrder.assigned_writer && viewingOrder.is_paid" 
              @click="openActionModal(viewingOrder, 'assign_order')" 
              class="btn btn-primary"
            >
              Assign Writer
            </button>
            <button 
              v-else-if="!viewingOrder.assigned_writer && !viewingOrder.is_paid"
                @click="showUnpaidWarningModal = true; currentOrderForAction = viewingOrder"
              class="btn btn-secondary bg-yellow-600 hover:bg-yellow-700"
              title="Order must be paid before assigning writer"
            >
              ⚠️ Assign Writer
            </button>
            <button 
              v-else-if="viewingOrder.assigned_writer && viewingOrder.is_paid"
              @click="openActionModal(viewingOrder, 'reassign_order')" 
                class="btn btn-primary bg-orange-600 hover:bg-orange-700"
            >
              Reassign Writer
            </button>
            <button 
              v-else-if="viewingOrder.assigned_writer && !viewingOrder.is_paid"
                @click="showUnpaidWarningModal = true; currentOrderForAction = viewingOrder"
              class="btn btn-secondary bg-yellow-600 hover:bg-yellow-700"
              title="Order must be paid before reassigning writer"
            >
              ⚠️ Reassign Writer
            </button>
            <button 
              @click="openActionModal(viewingOrder)" 
              class="btn btn-primary bg-purple-600 hover:bg-purple-700"
            >
              More Actions
            </button>
            <button @click="openEditModal(viewingOrder)" class="btn btn-secondary">Edit</button>
          </div>
        </div>

          <!-- Files Tab -->
          <div v-if="activeOrderTab === 'files'" class="space-y-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  Files
                </h3>
                <p class="text-sm text-gray-600">View and manage order files</p>
              </div>
              <button
                @click="loadOrderFiles"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium flex items-center gap-2"
                :disabled="loadingOrderFiles"
              >
                <svg v-if="loadingOrderFiles" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {{ loadingOrderFiles ? 'Loading...' : 'Refresh' }}
              </button>
            </div>

            <div v-if="loadingOrderFiles" class="text-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p class="mt-4 text-gray-600">Loading files...</p>
            </div>

            <div v-else-if="orderFiles.length === 0" class="text-center py-12 text-gray-500">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p>No files found for this order</p>
            </div>

            <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded By</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="file in orderFiles" :key="file.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ file.file_name || (file.file ? file.file.split('/').pop() : 'N/A') }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ file.category?.name || 'Uncategorized' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ file.uploaded_by_username || file.uploaded_by_email || 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ file.is_downloadable ? '✓ Downloadable' : '🔒 Locked' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDateTime(file.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center gap-2">
                        <button
                          @click="downloadOrderFile(file)"
                          class="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs flex items-center gap-1"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                          Download
                        </button>
                        <button
                          @click="toggleOrderFileDownload(file)"
                          class="px-2 py-1.5 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors text-xs"
                          :title="file.is_downloadable ? 'Lock file' : 'Unlock file'"
                        >
                          {{ file.is_downloadable ? '🔒' : '🔓' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Enhanced Status Tab -->
          <div v-if="activeOrderTab === 'enhanced-status'" class="space-y-6">
            <EnhancedOrderStatus :order-id="viewingOrder.id" />
          </div>

          <!-- Progress Tab -->
          <div v-if="activeOrderTab === 'progress'" class="space-y-6">
            <div class="bg-white rounded-lg border border-gray-200 p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Order Progress
              </h3>
              <ProgressBar
                v-if="viewingOrder.assigned_writer"
                :progress-percentage="displayProgressPercentage"
                :last-update="latestProgressUpdate"
              />
              <div v-else class="text-center py-8 text-gray-500">
                <p>No writer assigned yet. Progress will be available once a writer is assigned.</p>
              </div>
              <div v-if="viewingOrder.assigned_writer" class="mt-6">
                <ProgressHistory :order-id="viewingOrder.id" />
              </div>
            </div>
          </div>

          <!-- Messages Tab -->
          <div v-if="activeOrderTab === 'messages'" class="space-y-6">
            <OrderMessagesTabbed 
              :order-id="viewingOrder.id" 
              :order-topic="viewingOrder.topic || 'Untitled Order'"
            />
          </div>

          <!-- Draft Requests Tab -->
          <div v-if="activeOrderTab === 'draft-requests'" class="space-y-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Draft Requests
                </h3>
                <p class="text-sm text-gray-600">View and manage draft requests for this order</p>
              </div>
              <button
                @click="loadDraftRequests"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium flex items-center gap-2"
                :disabled="loadingDraftRequests"
              >
                <svg v-if="loadingDraftRequests" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {{ loadingDraftRequests ? 'Loading...' : 'Refresh' }}
              </button>
            </div>

            <div v-if="loadingDraftRequests" class="text-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>

            <div v-else-if="draftRequests.length === 0" class="text-center py-12 text-gray-500">
              <p>No draft requests found for this order</p>
            </div>

            <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested By</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requested At</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fulfilled At</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="request in draftRequests" :key="request.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{{ request.id }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {{ request.requested_by_username || request.requested_by_email || 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="{
                          'bg-yellow-100 text-yellow-800': request.status === 'pending',
                          'bg-blue-100 text-blue-800': request.status === 'in_progress',
                          'bg-green-100 text-green-800': request.status === 'fulfilled',
                          'bg-red-100 text-red-800': request.status === 'cancelled'
                        }"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ request.status }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                      {{ request.message || 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDateTime(request.requested_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ request.fulfilled_at ? formatDateTime(request.fulfilled_at) : 'N/A' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- External Links Tab -->
          <div v-if="activeOrderTab === 'links'" class="space-y-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  External Links
                </h3>
                <p class="text-sm text-gray-600">View and manage external file links for this order</p>
              </div>
              <button
                @click="loadExternalLinks"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium flex items-center gap-2"
                :disabled="loadingExternalLinks"
              >
                <svg v-if="loadingExternalLinks" class="animate-spin w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {{ loadingExternalLinks ? 'Loading...' : 'Refresh' }}
              </button>
            </div>

            <div v-if="loadingExternalLinks" class="text-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>

            <div v-else-if="externalLinks.length === 0" class="text-center py-12 text-gray-500">
              <p>No external links found for this order</p>
            </div>

            <div v-else class="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">URL</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created At</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="link in externalLinks" :key="link.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 text-sm">
                      <a :href="link.url" target="_blank" class="text-blue-600 hover:underline truncate block max-w-xs">
                        {{ link.url }}
                      </a>
                    </td>
                    <td class="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                      {{ link.description || 'N/A' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="{
                          'bg-yellow-100 text-yellow-800': link.status === 'pending',
                          'bg-green-100 text-green-800': link.status === 'approved',
                          'bg-red-100 text-red-800': link.status === 'rejected'
                        }"
                        class="px-2 py-1 rounded-full text-xs font-medium"
                      >
                        {{ link.status || 'pending' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDateTime(link.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex items-center gap-2">
                        <button
                          v-if="link.status === 'pending'"
                          @click="approveExternalLink(link)"
                          class="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-xs"
                        >
                          Approve
                        </button>
                        <button
                          v-if="link.status === 'pending'"
                          @click="rejectExternalLink(link)"
                          class="px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-xs"
                        >
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Actions Tab -->
          <div v-if="activeOrderTab === 'actions'" class="space-y-6">
            <div class="bg-white rounded-lg border border-gray-200 p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Order Actions
              </h3>
              <div class="flex gap-2 flex-wrap">
                <button @click="showOrderThreadsModal = true" class="btn btn-primary bg-blue-600 hover:bg-blue-700">
                  💬 View Messages
                </button>
                <button 
                  v-if="!viewingOrder.assigned_writer && viewingOrder.is_paid" 
                  @click="openActionModal(viewingOrder, 'assign_order')" 
                  class="btn btn-primary"
                >
                  Assign Writer
                </button>
                <button 
                  v-else-if="!viewingOrder.assigned_writer && !viewingOrder.is_paid"
                  @click="showUnpaidWarningModal = true; currentOrderForAction = viewingOrder"
                  class="btn btn-secondary bg-yellow-600 hover:bg-yellow-700"
                  title="Order must be paid before assigning writer"
                >
                  ⚠️ Assign Writer
                </button>
                <button 
                  v-else-if="viewingOrder.assigned_writer && viewingOrder.is_paid"
                  @click="openActionModal(viewingOrder, 'reassign_order')" 
                  class="btn btn-primary bg-orange-600 hover:bg-orange-700"
                >
                  Reassign Writer
                </button>
                <button 
                  v-else-if="viewingOrder.assigned_writer && !viewingOrder.is_paid"
                  @click="showUnpaidWarningModal = true; currentOrderForAction = viewingOrder"
                  class="btn btn-secondary bg-yellow-600 hover:bg-yellow-700"
                  title="Order must be paid before reassigning writer"
                >
                  ⚠️ Reassign Writer
                </button>
                <button 
                  @click="openActionModal(viewingOrder)" 
                  class="btn btn-primary bg-purple-600 hover:bg-purple-700"
                >
                  More Actions
                </button>
                <button @click="openEditModal(viewingOrder)" class="btn btn-secondary">Edit</button>
              </div>
            </div>
          </div>

          <!-- History Tab -->
          <div v-if="activeOrderTab === 'history'" class="space-y-6">
            <div class="bg-white rounded-lg border border-gray-200 p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Order History
              </h3>
              <div class="space-y-4">
                <div v-if="statusTimeline.length === 0" class="text-center py-8 text-gray-500">
                  <p>No history available</p>
                </div>
                <div v-else class="space-y-4">
                  <div
                    v-for="entry in statusTimeline"
                    :key="entry.key"
                    class="flex items-start gap-4 p-4 bg-gray-50 rounded-lg"
                  >
                    <div class="text-2xl">{{ entry.icon }}</div>
                    <div class="flex-1">
                      <div class="font-semibold text-gray-900">{{ entry.label }}</div>
                      <div v-if="entry.description" class="text-sm text-gray-600 mt-1">{{ entry.description }}</div>
                      <div class="text-xs text-gray-500 mt-2">{{ entry.relativeTime }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Assign Writer Modal -->
    <Transition name="modal">
      <div v-if="showAssignModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="closeAssignModal">
        <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full my-auto max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-xl font-bold text-white">Assign Writer</h3>
                <p v-if="currentOrderForAction" class="text-sm text-blue-100 mt-1">
                  Order #{{ currentOrderForAction.id }} · {{ currentOrderForAction.topic || 'Untitled Order' }}
                </p>
              </div>
              <button 
                @click="closeAssignModal" 
                class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors"
                :disabled="assigning"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Order Summary -->
          <div v-if="currentOrderForAction" class="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500 dark:text-gray-400">Pages:</span>
                <span class="ml-2 font-medium">{{ currentOrderForAction.number_of_pages || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Deadline:</span>
                <span class="ml-2 font-medium">{{ formatDate(currentOrderForAction.client_deadline) }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Type:</span>
                <span class="ml-2 font-medium">{{ currentOrderForAction.type_of_work?.name || 'N/A' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Level:</span>
                <span class="ml-2 font-medium">{{ currentOrderForAction.academic_level?.name || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto p-6">
            <!-- Search/Filter -->
            <div class="mb-4">
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  v-model="writerSearch"
                  type="text"
                  placeholder="Search writers by name, email, or level..."
                  class="w-full pl-10 pr-4 py-2.5 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <!-- Writers List -->
            <div v-if="loadingWriters" class="text-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p class="mt-4 text-gray-600 dark:text-gray-400">Loading writers...</p>
            </div>

            <div v-else-if="filteredWriters.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
              <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <p>No writers found</p>
            </div>

            <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              <div
                v-for="writer in filteredWriters"
                :key="writer.id"
                @click="selectWriter(writer.id)"
                :class="[
                  'p-4 border-2 rounded-xl cursor-pointer transition-all',
                  assignForm.writerId === writer.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md'
                ]"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold">
                        {{ (writer.username || writer.email || 'W')[0].toUpperCase() }}
                      </div>
                      <div>
                        <h4 class="font-semibold text-gray-900 dark:text-white">{{ formatWriterName(writer) }}</h4>
                        <p class="text-xs text-gray-500 dark:text-gray-400">{{ writer.email }}</p>
                      </div>
                    </div>
                    <div class="flex flex-wrap gap-2 mt-2">
                      <span v-if="writer.profile?.writer_level" class="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full font-medium">
                        {{ writer.profile.writer_level.name || writer.profile.writer_level.level || 'Level ' + (writer.profile.writer_level.level || 'N/A') }}
                      </span>
                      <span v-if="writer.workload" class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium">
                        {{ writer.workload.active_orders_count || 0 }}/{{ writer.workload.max_orders || 5 }} orders
                      </span>
                      <span v-if="writer.workload?.capacity !== undefined && writer.workload.capacity > 0" class="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                        {{ writer.workload.capacity }} slot{{ writer.workload.capacity !== 1 ? 's' : '' }} available
                      </span>
                      <span v-else-if="writer.workload?.capacity === 0" class="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 text-xs rounded-full">
                        Full
                      </span>
                      <span v-if="writer.profile?.rating" class="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded-full">
                        ⭐ {{ writer.profile.rating.toFixed(1) }}
                      </span>
                    </div>
                    <div v-if="writer.workload" class="mt-2 text-xs text-gray-600 dark:text-gray-400">
                      <p>Active: {{ writer.workload.active_orders_count || 0 }} | Max: {{ writer.workload.max_orders || 5 }} | Capacity: {{ writer.workload.capacity || 0 }}</p>
                    </div>
                  </div>
                  <div v-if="assignForm.writerId === writer.id" class="shrink-0">
                    <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Reason Input -->
            <div v-if="assignForm.writerId" class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Assignment Reason (Optional)
              </label>
              <textarea
                v-model="assignForm.reason"
                placeholder="Add any notes or instructions for this assignment..."
                rows="3"
                class="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-none"
              ></textarea>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex gap-3">
            <button
              @click="closeAssignModal"
              :disabled="assigning"
              class="flex-1 px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              @click="confirmAssign"
              :disabled="!assignForm.writerId || assigning"
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
            >
              <svg v-if="assigning" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ assigning ? 'Assigning...' : (currentOrderForAction?.assigned_writer ? 'Reassign Writer' : 'Assign Writer') }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Edit Order Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between z-10">
          <h3 class="text-xl font-bold">Edit Order</h3>
          <button @click="closeEditModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Topic</label>
            <input v-model="editForm.topic" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Total Price</label>
            <input v-model.number="editForm.total_price" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Writer Compensation</label>
            <input v-model.number="editForm.writer_compensation" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="editForm.status" class="w-full border rounded px-3 py-2">
              <option v-for="status in orderStatuses" :key="status.value" :value="status.value">
                {{ status.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Client Deadline</label>
            <input v-model="editForm.client_deadline" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Writer Deadline</label>
            <input v-model="editForm.writer_deadline" type="datetime-local" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Instructions</label>
            <textarea v-model="editForm.order_instructions" class="w-full border rounded px-3 py-2" rows="5"></textarea>
          </div>
          <div class="flex gap-2 pt-4 border-t sticky bottom-0 bg-white -mx-6 px-6 py-4">
            <button @click="saveEdit" class="btn btn-primary flex-1">Save</button>
            <button @click="closeEditModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Threads Modal -->
    
    <!-- Unpaid Order Warning Modal -->
    <Transition name="modal">
      <div v-if="showUnpaidWarningModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="showUnpaidWarningModal = false">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/50 flex items-center justify-center">
              <span class="text-2xl">⚠️</span>
            </div>
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Order Not Paid</h3>
          </div>
          
          <div class="space-y-4">
            <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <p class="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                Cannot Assign Writer
              </p>
              <p class="text-sm text-yellow-700 dark:text-yellow-300">
                Only paid orders can be assigned to writers. Order #{{ currentOrderForAction?.id || 'N/A' }} has not been marked as paid yet.
              </p>
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
              <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">
                <strong>To assign a writer:</strong>
              </p>
              <ol class="list-decimal list-inside text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>Mark this order as paid first</li>
                <li>Then proceed with writer assignment</li>
              </ol>
            </div>
            
            <div class="flex gap-2 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                @click="showUnpaidWarningModal = false"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Close
              </button>
              <button
                @click="openActionModal(currentOrderForAction, 'mark_paid'); showUnpaidWarningModal = false"
                class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                Mark as Paid
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <OrderThreadsModal
      v-if="showOrderThreadsModal && viewingOrder"
      :order-id="viewingOrder.id"
      @close="showOrderThreadsModal = false"
    />

    <!-- Order Action Modal -->
    <OrderActionModal
      :visible="showActionModal"
      @update:visible="showActionModal = $event"
      :order="currentOrderForAction"
      :selected-action="selectedAction"
      :available-actions="availableActions"
      :available-writers="availableWriters"
      @success="handleActionSuccess"
      @error="handleActionError"
    />

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Loading State -->
  <div v-else-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>

  <!-- Confirmation Dialog - Only render when needed -->
    <ConfirmationDialog
      v-if="confirmShow"
      :show="confirmShow"
      @update:show="confirmShow = $event"
      :title="unref(confirm.title)"
      :message="unref(confirm.message)"
      :details="unref(confirm.details)"
      :variant="unref(confirm.variant)"
      :icon="unref(confirm.icon)"
      :confirm-text="unref(confirm.confirmText)"
      :cancel-text="unref(confirm.cancelText)"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, unref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ordersAPI, usersAPI, adminOrdersAPI, writerOrderRequestsAPI, writerAssignmentAPI } from '@/api'
import { formatWriterName } from '@/utils/formatDisplay'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'
import OrderActionModal from '@/components/order/OrderActionModal.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'
import UserDisplayName from '@/components/common/UserDisplayName.vue'
import OnlineStatusIndicator from '@/components/common/OnlineStatusIndicator.vue'
import ProgressBar from '@/components/orders/ProgressBar.vue'
import EnhancedStatusBadge from '@/components/common/EnhancedStatusBadge.vue'
import SafeHtml from '@/components/common/SafeHtml.vue'
import progressAPI from '@/api/progress'
import orderFilesAPI from '@/api/order-files'
import EnhancedOrderStatus from '@/components/client/EnhancedOrderStatus.vue'
import OrderMessagesTabbed from '@/components/order/OrderMessagesTabbed.vue'
import ProgressHistory from '@/components/orders/ProgressHistory.vue'
import draftRequestsAPI from '@/api/draft-requests'
import { getStatusLabel, getStatusIcon, canAssignOrder, canReassignOrder } from '@/utils/orderStatus'
import StatusCard from '@/components/common/StatusCard.vue'

const route = useRoute()
const router = useRouter()

const confirm = useConfirmDialog()
const confirmShow = ref(false)
const { success: showSuccessToast, error: showErrorToast } = useToast()

// Keep local v-model ref in sync with composable state
watch(
  () => confirm.show.value,
  (val) => {
    confirmShow.value = val
  },
  { immediate: true }
)

watch(confirmShow, (val) => {
  if (confirm.show.value !== val) {
    confirm.show.value = val
  }
})

const loading = ref(false)
const orders = ref([])
const selectedOrders = ref([])
const viewingOrder = ref(null)
const activeOrderTab = ref('overview')
const orderFiles = ref([])
const loadingOrderFiles = ref(false)
const draftRequests = ref([])
const loadingDraftRequests = ref(false)
const externalLinks = ref([])
const loadingExternalLinks = ref(false)
const showAssignModal = ref(false)
const showUnpaidWarningModal = ref(false)
const showEditModal = ref(false)
const showOrderThreadsModal = ref(false)
const showActionModal = ref(false)
const availableWriters = ref([])
const availableActions = ref([])
const selectedAction = ref(null)
const currentOrderForAction = ref(null)
const initialLoading = ref(true)
const componentError = ref(null)
const writerSearch = ref('')
const loadingWriters = ref(false)
const assigning = ref(false)
const savingEdit = ref(false)

// Initialize filters from route query params
const initializeFiltersFromRoute = () => {
  const query = route.query
  return {
    search: query.search || '',
    status: query.status || '',
    is_paid: query.is_paid || '',
    client: query.client || '',
    writer: query.writer || '',
    website: query.website || '',
    include_archived: query.include_archived !== 'false', // Default to true for admin
    include_deleted: query.include_deleted === 'true',
    only_deleted: query.only_deleted === 'true',
  }
}

const filters = ref(initializeFiltersFromRoute())

const stats = ref({
  total: 0,
  in_progress: 0,
  completed: 0,
  unpaid: 0,
  disputed: 0,
  needs_assignment: 0,
  overdue: 0,
  total_revenue: 0,
  avg_order_value: 0,
})
const dashboardData = ref(null)
const assignmentQueue = ref([])
const overdueOrders = ref([])
const stuckOrders = ref([])
const loadingDashboard = ref(false)
const loadingAssignment = ref(false)
const loadingOverdue = ref(false)
const loadingStuck = ref(false)
const writerRequests = ref([])
const loadingWriterRequests = ref(false)

const assignForm = ref({
  writerId: '',
  reason: '',
})

const showBulkAssignModal = ref(false)
const bulkAssigning = ref(false)
const bulkAssignForm = ref({
  strategy: 'balanced',
  writer_ids: [],
  reason: 'Bulk assignment',
})

const canBulkAssign = computed(() => {
  if (bulkAssignForm.value.strategy === 'best_match') {
    return true // No writer selection needed
  }
  return bulkAssignForm.value.writer_ids.length > 0
})

const editForm = ref({
  topic: '',
  total_price: 0,
  writer_compensation: 0,
  status: '',
  client_deadline: '',
  writer_deadline: '',
  order_instructions: '',
})

const message = ref('')
const messageSuccess = ref(false)
const activeQuickTab = ref('all')

const orderStatuses = [
  { value: 'created', label: 'Created' },
  { value: 'pending', label: 'Pending' },
  { value: 'unpaid', label: 'Unpaid' },
  { value: 'available', label: 'Available' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'on_hold', label: 'On Hold' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'under_editing', label: 'Under Editing' },
  { value: 'completed', label: 'Completed' },
  { value: 'disputed', label: 'Disputed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'archived', label: 'Archived' },
]

let searchTimeout = null

const allSelected = computed(() => {
  return orders.value.length > 0 && selectedOrders.value.length === orders.value.length
})

// Extract unique websites from orders for filter dropdown
const uniqueWebsites = computed(() => {
  const websitesMap = new Map()
  orders.value.forEach(order => {
    const website = order.website || order.website_name
    if (website) {
      const key = typeof website === 'object' ? (website.id || website.name || website.domain) : website
      if (!websitesMap.has(key)) {
        websitesMap.set(key, website)
      }
    }
  })
  return Array.from(websitesMap.values())
})

const orderTransitions = computed(() => {
  const summary = dashboardData.value?.summary || {}
  const transitionCounts = dashboardData.value?.transition_counts || {}
  
  // Map transition keys to readable labels and colors
  const transitionMap = {
    'can_transition_to_in_progress': { label: '→ In Progress', colorClass: 'text-blue-600' },
    'can_transition_to_submitted': { label: '→ Submitted', colorClass: 'text-purple-600' },
    'can_transition_to_completed': { label: '→ Completed', colorClass: 'text-green-600' },
    'can_transition_to_cancelled': { label: '→ Cancelled', colorClass: 'text-red-600' },
    'can_transition_to_on_hold': { label: '→ On Hold', colorClass: 'text-orange-600' },
    'can_transition_to_available': { label: '→ Available', colorClass: 'text-indigo-600' },
    'can_transition_to_revision_requested': { label: '→ Revision', colorClass: 'text-yellow-600' },
    'can_transition_to_disputed': { label: '→ Disputed', colorClass: 'text-red-600' },
    'can_transition_to_under_editing': { label: '→ Under Editing', colorClass: 'text-pink-600' },
    'can_transition_to_closed': { label: '→ Closed', colorClass: 'text-gray-600' },
    'can_transition_to_reopened': { label: '→ Reopened', colorClass: 'text-teal-600' },
  }
  
  // Get counts from either summary or transition_counts
  const allCounts = { ...summary, ...transitionCounts }
  
  return Object.entries(transitionMap)
    .map(([key, config]) => ({
      key,
      label: config.label,
      colorClass: config.colorClass,
      count: allCounts[key] || 0
    }))
    .filter(item => item.count > 0) // Only show transitions with orders
    .sort((a, b) => b.count - a.count) // Sort by count descending
})

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadOrders()
  }, 500)
}

const loadWriterRequests = async () => {
  loadingWriterRequests.value = true
  try {
    const res = await writerOrderRequestsAPI.list({ page_size: 100 })
    // Support both paginated and non-paginated responses
    const data = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    writerRequests.value = data
  } catch (error) {
    console.error('Error loading writer order requests:', error)
    showMessage('Failed to load writer requests: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingWriterRequests.value = false
  }
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const res = await adminOrdersAPI.getDashboard()
    dashboardData.value = res.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadAssignmentQueue = async () => {
  loadingAssignment.value = true
  try {
    const res = await adminOrdersAPI.getAssignmentQueue({ limit: 50 })
    assignmentQueue.value = res.data.orders || []
  } catch (error) {
    console.error('Error loading assignment queue:', error)
    showMessage('Failed to load assignment queue: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingAssignment.value = false
  }
}

const loadOverdueOrders = async () => {
  loadingOverdue.value = true
  try {
    const res = await adminOrdersAPI.getOverdueOrders({ limit: 50 })
    overdueOrders.value = res.data.orders || []
  } catch (error) {
    console.error('Error loading overdue orders:', error)
    showMessage('Failed to load overdue orders: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingOverdue.value = false
  }
}

const loadStuckOrders = async () => {
  loadingStuck.value = true
  try {
    const res = await adminOrdersAPI.getStuckOrders({ limit: 50 })
    stuckOrders.value = res.data.orders || []
  } catch (error) {
    console.error('Error loading stuck orders:', error)
    showMessage('Failed to load stuck orders: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingStuck.value = false
  }
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      // Admin/superadmin should see all orders including archived by default
      include_archived: filters.value.include_archived !== false,
      // Request more orders per page for admin views
      page_size: 500,
      // Exclude special orders - they have their own page
      is_special_order: false,
    }
    // Apply status filter - pass it even if empty string to clear previous filter
    if (filters.value.status !== undefined && filters.value.status !== null) {
      params.status = filters.value.status
    }
    // Apply payment status filter
    if (filters.value.is_paid !== undefined && filters.value.is_paid !== null && filters.value.is_paid !== '') {
      params.is_paid = filters.value.is_paid === 'true' || filters.value.is_paid === true
    }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.writer) params.writer = filters.value.writer
    if (filters.value.website) params.website = filters.value.website
    // Note: Backend needs to support include_deleted and only_deleted params
    // For now, filtering is done on frontend
    if (filters.value.include_deleted) params.include_deleted = true
    if (filters.value.only_deleted) params.only_deleted = true

    const res = await ordersAPI.list(params)
    let allOrders = res.data.results || res.data || []
    
    // Frontend filtering for soft-deleted orders (until backend supports it)
    if (filters.value.only_deleted) {
      allOrders = allOrders.filter(o => o.is_deleted === true)
    } else if (!filters.value.include_deleted) {
      // Exclude soft-deleted orders if not including them
      allOrders = allOrders.filter(o => !o.is_deleted)
    }
    
    // Apply overdue filter if requested
    if (route.query.overdue === 'true') {
      const now = new Date()
      allOrders = allOrders.filter(order => {
        const deadline = order.client_deadline || order.deadline
        if (!deadline) return false
        return new Date(deadline) < now && 
               !['completed', 'cancelled', 'archived'].includes(order.status?.toLowerCase())
      })
    }
    
    orders.value = allOrders
    
    // Calculate stats (fallback if dashboard not loaded)
    stats.value.total = orders.value.length
    stats.value.in_progress = orders.value.filter(o => o.status === 'in_progress').length
    stats.value.completed = orders.value.filter(o => o.status === 'completed').length
    stats.value.unpaid = orders.value.filter(o => !o.is_paid).length
    stats.value.disputed = orders.value.filter(o => o.status === 'disputed').length
  } catch (error) {
    console.error('Error loading orders:', error)
    showMessage('Failed to load orders: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const getWebsiteName = (order) => {
  if (order.website_name) return order.website_name
  if (order.website?.name) return order.website.name
  if (order.website?.domain) return order.website.domain
  if (typeof order.website === 'string') return order.website
  return 'N/A'
}

const getWebsiteColorClass = (website) => {
  if (!website) return 'bg-gray-300'
  
  // Generate a consistent color based on website name/domain
  const name = typeof website === 'string' ? website : (website?.name || website?.domain || '')
  const colors = [
    'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500', 
    'bg-indigo-500', 'bg-yellow-500', 'bg-red-500', 'bg-teal-500'
  ]
  
  // Simple hash function to get consistent color
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const loadWriters = async (orderId = null) => {
  loadingWriters.value = true
  try {
    // Use writer assignment API to get writers with workload, level, and limit info
    const res = await writerAssignmentAPI.getAvailableWriters(orderId)
    availableWriters.value = res.data.writers || res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading writers:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to load writers'
    showMessage('Failed to load writers: ' + errorMsg, false)
    availableWriters.value = []
  } finally {
    loadingWriters.value = false
  }
}

const filteredWriters = computed(() => {
  if (!writerSearch.value) return availableWriters.value
  
  const search = writerSearch.value.toLowerCase()
  return availableWriters.value.filter(writer => {
    const name = formatWriterName(writer).toLowerCase()
    const email = (writer.email || '').toLowerCase()
    const level = (writer.writer_level?.name || writer.writer_level || '').toLowerCase()
    return name.includes(search) || email.includes(search) || level.includes(search)
  })
})

const selectWriter = (writerId) => {
  assignForm.value.writerId = writerId
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    is_paid: '',
    client: '',
    writer: '',
    website: '',
    include_archived: true, // Admin/superadmin should see all orders by default
    include_deleted: false,
    only_deleted: false,
  }
  loadOrders()
}

// Filter functions for status cards
const filterByStatus = (status) => {
  try {
    filters.value.status = status || ''
    filters.value.search = '' // Clear search when filtering by status
    // Update URL query params
    const newQuery = { ...route.query }
    if (status) {
      newQuery.status = status
    } else {
      delete newQuery.status
    }
    delete newQuery.overdue // Clear overdue filter when filtering by status
    router.push({ query: newQuery })
    loadOrders()
    // Scroll to orders list
    setTimeout(() => {
      const ordersSection = document.getElementById('orders-list-section')
      if (ordersSection) {
        ordersSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)
  } catch (error) {
    console.error('Error in filterByStatus:', error)
    showErrorToast('Failed to apply filter')
  }
}

const filterByNeedsAssignment = () => {
  try {
    // Filter for orders that need assignment (available status)
    filters.value.status = 'available'
    filters.value.search = '' // Clear search
    // Update URL query params
    const newQuery = { ...route.query }
    newQuery.status = 'available'
    delete newQuery.overdue // Clear overdue filter
    router.push({ query: newQuery })
    loadOrders()
    // Scroll to orders list
    setTimeout(() => {
      const ordersSection = document.getElementById('orders-list-section')
      if (ordersSection) {
        ordersSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)
  } catch (error) {
    console.error('Error in filterByNeedsAssignment:', error)
    showErrorToast('Failed to apply filter')
  }
}

const filterByOverdue = () => {
  try {
    // Filter for overdue orders - clear status and let frontend filter by deadline
    filters.value.status = ''
    filters.value.search = '' // Clear search
    // Update URL query params
    const newQuery = { ...route.query }
    delete newQuery.status // Clear status filter
    newQuery.overdue = 'true'
    router.push({ query: newQuery })
    loadOrders()
    // Scroll to orders list
    setTimeout(() => {
      const ordersSection = document.getElementById('orders-list-section')
      if (ordersSection) {
        ordersSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 100)
  } catch (error) {
    console.error('Error in filterByOverdue:', error)
    showErrorToast('Failed to apply filter')
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedOrders.value = []
  } else {
    selectedOrders.value = orders.value.map(o => o.id)
  }
}

const latestProgressPercentage = ref(0)
const latestProgressUpdate = ref(null)

const viewOrder = async (order) => {
  // Navigate to the order detail page instead of opening a modal
  router.push({ name: 'AdminOrderDetail', params: { id: order.id } })
}

const closeOrderModal = () => {
  viewingOrder.value = null
  activeOrderTab.value = 'overview'
  latestProgressPercentage.value = 0
  latestProgressUpdate.value = null
  orderFiles.value = []
  draftRequests.value = []
  externalLinks.value = []
}

const handleTabChange = (tabId) => {
  activeOrderTab.value = tabId
  if (tabId === 'files') {
    loadOrderFiles()
  } else if (tabId === 'draft-requests') {
    loadDraftRequests()
  } else if (tabId === 'links') {
    loadExternalLinks()
  }
}

const orderTabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'enhanced-status', label: 'Enhanced Status', icon: '📈' },
    { id: 'progress', label: 'Progress', icon: '📊' },
    { id: 'messages', label: 'Messages', icon: '💬' },
    { id: 'files', label: 'Files', icon: '📁' },
    { id: 'draft-requests', label: 'Draft Requests', icon: '📝' },
    { id: 'links', label: 'External Links', icon: '🔗' },
    { id: 'actions', label: 'Actions', icon: '⚡' },
  ]
  // Add History tab for admin/superadmin/support
  baseTabs.push({ id: 'history', label: 'History', icon: '🕒' })
  return baseTabs
})

const loadOrderFiles = async () => {
  if (!viewingOrder.value) return
  loadingOrderFiles.value = true
  try {
    const res = await orderFilesAPI.list({ order: viewingOrder.value.id })
    orderFiles.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load order files:', error)
    showMessage('Failed to load files: ' + (error.response?.data?.detail || error.message), false)
    orderFiles.value = []
  } finally {
    loadingOrderFiles.value = false
  }
}

const downloadOrderFile = async (file) => {
  try {
    const response = await orderFilesAPI.getSignedUrl(file.id)
    if (response.data.signed_url) {
      window.open(response.data.signed_url, '_blank')
    } else {
      showMessage('Failed to get download URL', false)
    }
  } catch (error) {
    console.error('Failed to download file:', error)
    showMessage('Failed to download file: ' + (error.response?.data?.detail || error.message), false)
  }
}

const toggleOrderFileDownload = async (file) => {
  try {
    await orderFilesAPI.toggleDownload(file.id)
    await loadOrderFiles()
    showMessage('File download status updated', true)
  } catch (error) {
    console.error('Failed to toggle file download:', error)
    showMessage('Failed to update file download status: ' + (error.response?.data?.detail || error.message), false)
  }
}

const loadDraftRequests = async () => {
  if (!viewingOrder.value) return
  loadingDraftRequests.value = true
  try {
    const res = await draftRequestsAPI.listDraftRequests({ order: viewingOrder.value.id })
    draftRequests.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load draft requests:', error)
    showMessage('Failed to load draft requests: ' + (error.response?.data?.detail || error.message), false)
    draftRequests.value = []
  } finally {
    loadingDraftRequests.value = false
  }
}

const loadExternalLinks = async () => {
  if (!viewingOrder.value) return
  loadingExternalLinks.value = true
  try {
    const res = await orderFilesAPI.listExternalLinks({ order: viewingOrder.value.id })
    externalLinks.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (error) {
    console.error('Failed to load external links:', error)
    showMessage('Failed to load external links: ' + (error.response?.data?.detail || error.message), false)
    externalLinks.value = []
  } finally {
    loadingExternalLinks.value = false
  }
}

const approveExternalLink = async (link) => {
  try {
    await orderFilesAPI.approveExternalLink(link.id)
    await loadExternalLinks()
    showMessage('External link approved', true)
  } catch (error) {
    console.error('Failed to approve external link:', error)
    showMessage('Failed to approve link: ' + (error.response?.data?.detail || error.message), false)
  }
}

const rejectExternalLink = async (link) => {
  try {
    await orderFilesAPI.rejectExternalLink(link.id)
    await loadExternalLinks()
    showMessage('External link rejected', true)
  } catch (error) {
    console.error('Failed to reject external link:', error)
    showMessage('Failed to reject link: ' + (error.response?.data?.detail || error.message), false)
  }
}

const loadLatestProgress = async () => {
  if (!viewingOrder.value) return
  
  try {
    const response = await progressAPI.getLatestProgress(viewingOrder.value.id)
    if (response.data.latest_report) {
      latestProgressPercentage.value = response.data.progress_percentage || 0
      latestProgressUpdate.value = response.data.latest_report.timestamp
    } else {
      latestProgressPercentage.value = 0
      latestProgressUpdate.value = null
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load latest progress:', error)
    }
    latestProgressPercentage.value = 0
    latestProgressUpdate.value = null
  }
}

const displayProgressPercentage = computed(() => {
  if (!viewingOrder.value) return 0
  
  const status = viewingOrder.value.status?.toLowerCase()
  
  // Completed/approved/closed orders show 100%
  if (['completed', 'approved', 'closed'].includes(status)) {
    return 100
  }
  
  // If order is in revision or returned to progress, show actual progress
  if (['revision_requested', 'revision_in_progress', 'in_progress', 'assigned', 'draft', 'submitted', 'under_editing'].includes(status)) {
    return latestProgressPercentage.value
  }
  
  return latestProgressPercentage.value
})

const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`
  return formatDateTime(dateString)
}

const formatStatusLabel = (status) => {
  if (!status) return ''
  return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const statusTimeline = computed(() => {
  if (!viewingOrder.value) return []

  const entries = []
  const seenEntries = new Set()

  const pushEntry = (key, status, timestamp, extra = {}) => {
    if (!timestamp) return

    const timestampDate = new Date(timestamp)
    if (isNaN(timestampDate.getTime())) return

    const normalizedStatus = status?.toLowerCase()?.trim()
    if (!normalizedStatus) return

    const timestampKey = Math.floor(timestampDate.getTime() / 1000)
    const dedupeKey = `${normalizedStatus}|${timestampKey}`

    if (seenEntries.has(dedupeKey)) return
    seenEntries.add(dedupeKey)

    entries.push({
      key,
      status: normalizedStatus,
      label: extra.label || getStatusLabel(normalizedStatus) || formatStatusLabel(status),
      timestamp: timestampDate.toISOString(),
      relativeTime: formatRelativeTime(timestamp),
      description: extra.description || null,
      icon: extra.icon || getStatusIcon(normalizedStatus) || '•',
    })
  }

  // Always include creation timestamp
  if (viewingOrder.value.created_at) {
    pushEntry('created', 'created', viewingOrder.value.created_at, {
      description: 'Order placed',
    })
  }

  // Process transition logs
  const transitionLogs = Array.isArray(viewingOrder.value.transitions)
    ? viewingOrder.value.transitions
    : []
  transitionLogs.forEach((log) => {
    if (!log || !log.timestamp) return

    const newStatus = (log.new_status || log.action || '').toLowerCase().trim()
    if (!newStatus) return

    const descriptionParts = []
    if (log.action && log.action !== newStatus) {
      descriptionParts.push(formatStatusLabel(log.action))
    }
    if (log.is_automatic) {
      descriptionParts.push('Automatic transition')
    }
    if (log.user) {
      const userName = log.user?.username || log.user?.full_name || log.user?.email || 'System'
      descriptionParts.push(`by ${userName}`)
    }
    if (log.old_status && log.old_status.toLowerCase() !== newStatus) {
      descriptionParts.push(`from ${formatStatusLabel(log.old_status)}`)
    }

    pushEntry(`transition-${log.id || Date.now()}`, newStatus, log.timestamp, {
      description: descriptionParts.length > 0 ? descriptionParts.join(' • ') : null,
    })
  })

  // Fallback to milestone timestamps
  const milestoneTimestamps = [
    { key: 'submitted_at', status: 'submitted', timestamp: viewingOrder.value.submitted_at, description: 'Writer submitted deliverables' },
    { key: 'completed_at', status: 'completed', timestamp: viewingOrder.value.completed_at, description: 'Order marked as completed' },
    { key: 'approved_at', status: 'approved', timestamp: viewingOrder.value.approved_at, description: 'Order approved' },
    { key: 'closed_at', status: 'closed', timestamp: viewingOrder.value.closed_at, description: 'Order closed' },
    { key: 'cancelled_at', status: 'cancelled', timestamp: viewingOrder.value.cancelled_at, description: 'Order cancelled' }
  ]
  
  milestoneTimestamps.forEach(entry => {
    if (entry.timestamp) {
      pushEntry(entry.key, entry.status, entry.timestamp, { 
        description: entry.description,
      })
    }
  })

  // Include current status if not already in timeline
  const currentStatus = viewingOrder.value.status?.toLowerCase()?.trim()
  if (currentStatus && currentStatus !== 'created') {
    const hasCurrentStatus = entries.some(e => e.status === currentStatus)
    if (!hasCurrentStatus && viewingOrder.value.updated_at) {
      pushEntry('current_status', currentStatus, viewingOrder.value.updated_at, {
        description: 'Current status',
      })
    }
  }

  // Sort by timestamp
  return entries.sort((a, b) => {
    const dateA = new Date(a.timestamp)
    const dateB = new Date(b.timestamp)
    return dateA.getTime() - dateB.getTime()
  })
})

const openAssignModal = async (order) => {
  // Check if order is paid and available
  if (!order.is_paid) {
    currentOrderForAction.value = order
    showUnpaidWarningModal.value = true
    return
  }
  
  if (order.status !== 'available') {
    showMessage(`Order must be in 'available' status to be assigned. Current status: ${order.status}`, false)
    return
  }
  
  currentOrderForAction.value = order
  assignForm.value = {
    writerId: null,
    reason: ''
  }
  
  // Load writers with workload info for this specific order
  await loadWriters(order.id)
  
  showAssignModal.value = true
}

const closeAssignModal = () => {
  if (assigning.value) return // Prevent closing while assigning
  showAssignModal.value = false
  assignForm.value = { writerId: '', reason: '' }
  writerSearch.value = ''
  currentOrderForAction.value = null
}

const confirmAssign = async () => {
  if (!assignForm.value.writerId || !currentOrderForAction.value) return
  
  const selectedWriter = availableWriters.value.find(w => w.id === assignForm.value.writerId)
  const writerName = selectedWriter ? (selectedWriter.username || selectedWriter.email || `Writer #${selectedWriter.id}`) : 'selected writer'
  const isReassign = currentOrderForAction.value.assigned_writer || currentOrderForAction.value.writer_username
  const currentWriter = currentOrderForAction.value.assigned_writer?.username || currentOrderForAction.value.writer_username || 'current writer'
  
  // Show confirmation with details
  const confirmed = await confirm.showDialog(
    isReassign 
      ? `Reassign Order #${currentOrderForAction.value.id}?`
      : `Assign Order #${currentOrderForAction.value.id}?`,
    isReassign ? 'Reassign Writer' : 'Assign Writer',
    {
      details: isReassign
        ? `You are about to reassign "${currentOrderForAction.value.topic || 'Untitled'}" from ${currentWriter} to ${writerName}. The current writer will be notified, and the new writer will receive the assignment.`
        : `You are about to assign "${currentOrderForAction.value.topic || 'Untitled'}" to ${writerName}. The writer will be notified and can start working on the order.`,
      variant: isReassign ? 'warning' : 'default',
      icon: isReassign ? '🔄' : '👤',
      confirmText: isReassign ? 'Reassign Writer' : 'Assign Writer',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  assigning.value = true
  try {
    if (isReassign) {
      await ordersAPI.reassignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
      const successMsg = `Order #${currentOrderForAction.value.id} has been reassigned to ${writerName} successfully!`
      showMessage(successMsg, true)
      showSuccessToast(successMsg)
    } else {
      await ordersAPI.assignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
      const successMsg = `Order #${currentOrderForAction.value.id} has been assigned to ${writerName} successfully! The writer has been notified.`
      showMessage(successMsg, true)
      showSuccessToast(successMsg)
    }
    closeAssignModal()
    await loadOrders()
    await loadAssignmentQueue() // Refresh assignment queue
    if (viewingOrder.value && viewingOrder.value.id === currentOrderForAction.value.id) {
      await viewOrder(currentOrderForAction.value)
    }
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to assign writer', `Unable to ${isReassign ? 'reassign' : 'assign'} writer for Order #${currentOrderForAction.value.id}. Please try again or contact support if the issue persists.`)
    showMessage(errorMsg, false)
    showErrorToast(errorMsg)
  } finally {
    assigning.value = false
  }
}

const openReassignModal = (order) => {
  openAssignModal(order)
}

const openEditModal = (order) => {
  editForm.value = {
    topic: order.topic || '',
    total_price: order.total_price || 0,
    writer_compensation: order.writer_compensation || 0,
    status: order.status || '',
    client_deadline: order.client_deadline ? new Date(order.client_deadline).toISOString().slice(0, 16) : '',
    writer_deadline: order.writer_deadline ? new Date(order.writer_deadline).toISOString().slice(0, 16) : '',
    order_instructions: order.order_instructions || order.instructions || '',
  }
  currentOrderForAction.value = order
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editForm.value = {
    topic: '',
    total_price: 0,
    writer_compensation: 0,
    status: '',
    client_deadline: '',
    writer_deadline: '',
    order_instructions: '',
  }
  currentOrderForAction.value = null
}

const saveEdit = async () => {
  if (!currentOrderForAction.value) return
  
  try {
    const updateData = { ...editForm.value }
    if (updateData.client_deadline) {
      updateData.client_deadline = new Date(updateData.client_deadline).toISOString()
    }
    if (updateData.writer_deadline) {
      updateData.writer_deadline = new Date(updateData.writer_deadline).toISOString()
    }
    
    await ordersAPI.patch(currentOrderForAction.value.id, updateData)
    showMessage('Order updated successfully', true)
    closeEditModal()
    loadOrders()
    if (viewingOrder.value && viewingOrder.value.id === currentOrderForAction.value.id) {
      await viewOrder(currentOrderForAction.value)
    }
  } catch (error) {
    showMessage('Failed to update order: ' + (error.response?.data?.detail || error.message), false)
  }
}

// Open action modal with optional pre-selected action
const openActionModal = async (order, action = null) => {
  // Check payment status for assign/reassign actions
  if ((action === 'assign_order' || action === 'reassign_order') && !order.is_paid) {
    currentOrderForAction.value = order
    showUnpaidWarningModal.value = true
    return
  }
  
  currentOrderForAction.value = order
  selectedAction.value = action
  
  // Load available actions for this order
  try {
    const response = await ordersAPI.getAvailableActions(order.id)
    if (response.data && response.data.available_actions) {
      availableActions.value = response.data.available_actions
    }
  } catch (error) {
    console.error('Failed to load available actions:', error)
    // Fallback: try to get actions from order status
    availableActions.value = []
  }
  
  // Load writers if needed for assign/reassign
  if ((action === 'assign_order' || action === 'reassign_order')) {
    // Check if order is paid and available
    if (action === 'assign_order' && (!order.is_paid || order.status !== 'available')) {
      if (!order.is_paid) {
        showUnpaidWarningModal.value = true
        return
      }
      if (order.status !== 'available') {
        showMessage(`Order must be in 'available' status to be assigned. Current status: ${order.status}`, false)
        return
      }
    }
    await loadWriters(order.id)
  }
  
  showActionModal.value = true
}

// Handle successful action
const handleActionSuccess = async (data) => {
  showMessage(data.message || 'Action completed successfully', true)
  await loadOrders()
  
  // Refresh viewing order if it's the same
  if (viewingOrder.value && currentOrderForAction.value && viewingOrder.value.id === currentOrderForAction.value.id) {
    await viewOrder(currentOrderForAction.value)
  }
  
  // Update current order if provided
  if (data.order) {
    currentOrderForAction.value = data.order
    if (viewingOrder.value && viewingOrder.value.id === data.order.id) {
      viewingOrder.value = data.order
    }
  }
}

// Handle action error
const handleActionError = (error) => {
  const errorMessage = error.detail || error.message || 'Failed to execute action'
  showMessage(errorMessage, false)
}

// Legacy methods kept for backward compatibility but now use modal
const approveOrder = async (order) => {
  await openActionModal(order, 'approve_order')
}

const completeOrder = async (order) => {
  await openActionModal(order, 'complete_order')
}

const holdOrder = async (order) => {
  await openActionModal(order, 'hold_order')
}

const resumeOrder = async (order) => {
  await openActionModal(order, 'resume_order')
}

const cancelOrder = async (order) => {
  await openActionModal(order, 'cancel_order')
}

const openActionMenu = (order) => {
  // For now, just open the detail modal
  viewOrder(order)
}

const openBulkAssignModal = async () => {
  if (selectedOrders.value.length === 0) {
    showMessage('Please select at least one order', false)
    return
  }
  
  // Load writers if not already loaded
  if (availableWriters.value.length === 0) {
    await loadWriters()
  }
  
  // Reset form
  bulkAssignForm.value = {
    strategy: 'balanced',
    writer_ids: [],
    reason: 'Bulk assignment',
  }
  
  showBulkAssignModal.value = true
}

const closeBulkAssignModal = () => {
  showBulkAssignModal.value = false
  bulkAssignForm.value = {
    strategy: 'balanced',
    writer_ids: [],
    reason: 'Bulk assignment',
  }
}

const confirmBulkAssign = async () => {
  if (!canBulkAssign.value) return
  
  bulkAssigning.value = true
  try {
    const assignments = selectedOrders.value.map(orderId => ({
      order_id: orderId,
    }))
    
    const response = await ordersAPI.bulkAssign({
      assignments,
      strategy: bulkAssignForm.value.strategy,
      writer_ids: bulkAssignForm.value.writer_ids.length > 0 ? bulkAssignForm.value.writer_ids : undefined,
      reason: bulkAssignForm.value.reason,
    })
    
    showMessage(
      response.data?.message || `Successfully assigned ${selectedOrders.value.length} order(s)`,
      true
    )
    
    closeBulkAssignModal()
    selectedOrders.value = []
    await loadOrders()
    await loadAssignmentQueue()
  } catch (error) {
    const errorMsg = getErrorMessage(
      error,
      'Failed to bulk assign',
      `Unable to assign ${selectedOrders.value.length} order(s). Please try again.`
    )
    showMessage(errorMsg, false)
  } finally {
    bulkAssigning.value = false
  }
}

const bulkAutoAssign = async () => {
  if (selectedOrders.value.length === 0) {
    showMessage('Please select at least one order', false)
    return
  }
  
  const confirmed = await confirm.showDialog(
    `Auto-assign ${selectedOrders.value.length} selected order(s)?`,
    'Auto-Assign Orders',
    {
      details: 'The system will automatically assign the best matching writers based on expertise, rating, and availability.',
      variant: 'default',
      icon: '🤖',
      confirmText: 'Auto-Assign',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  bulkAssigning.value = true
  try {
    const response = await ordersAPI.bulkAutoAssign({
      order_ids: selectedOrders.value,
    })
    
    showMessage(
      response.data?.message || `Successfully auto-assigned ${selectedOrders.value.length} order(s)`,
      true
    )
    
    selectedOrders.value = []
    await loadOrders()
    await loadAssignmentQueue()
  } catch (error) {
    const errorMsg = getErrorMessage(
      error,
      'Failed to auto-assign',
      `Unable to auto-assign ${selectedOrders.value.length} order(s). Please try again.`
    )
    showMessage(errorMsg, false)
  } finally {
    bulkAssigning.value = false
  }
}

const bulkStatusChange = async () => {
  if (selectedOrders.value.length === 0) {
    showMessage('Please select at least one order', false)
    return
  }

  const newStatus = prompt(
    'Enter new status (e.g. in_progress, submitted, completed, cancelled, on_hold):'
  )
  if (!newStatus) return

  const confirmed = await confirm.showDialog(
    `Change status of ${selectedOrders.value.length} order(s) to "${newStatus}"?`,
    'Bulk Status Change',
    {
      details:
        'The system will attempt to transition each selected order using the unified transition endpoint. ' +
        'Invalid transitions will be skipped and reported.',
      variant: 'warning',
      icon: '⚠️',
      confirmText: 'Change Status',
      cancelText: 'Cancel',
    }
  )

  if (!confirmed) return

  bulkAssigning.value = true

  let successCount = 0
  const failed = []

  try {
    for (const orderId of selectedOrders.value) {
      try {
        await ordersAPI.transition(
          orderId,
          newStatus,
          'Bulk status change from Order Management',
          { bulk: true }
        )
        successCount += 1
      } catch (error) {
        const errorMsg = getErrorMessage(
          error,
          `Failed to change status for order #${orderId}`,
          `Unable to change status for order #${orderId}.`
        )
        failed.push({ orderId, error: errorMsg })
      }
    }

    if (failed.length === 0) {
      showMessage(
        `Successfully changed status for ${successCount} order(s) to "${newStatus}".`,
        true
      )
    } else {
      const summary =
        `Changed status for ${successCount} order(s) to "${newStatus}". ` +
        `${failed.length} order(s) failed.\n` +
        failed
          .slice(0, 3)
          .map((f) => `#${f.orderId}: ${f.error}`)
          .join('\n')

      showMessage(summary, false)
    }

    await loadOrders()
    await loadAssignmentQueue()
  } finally {
    bulkAssigning.value = false
  }
}

const openAssignModalFromRequest = async (req) => {
  // Check payment status before opening assign modal
  const order = req.order || req
  if (order && !order.is_paid) {
    currentOrderForAction.value = order
    showUnpaidWarningModal.value = true
    return
  }
  
  // Check if order is in available status
  if (order && order.status !== 'available') {
    showMessage(`Order must be in 'available' status to be assigned. Current status: ${order.status}`, false)
    return
  }
  // Confirm with the admin before assigning
  const writerLabel =
    req.writer_name ||
    req.writer_username ||
    (req.writer && req.writer.user && req.writer.user.username) ||
    'this writer'

  const confirmed = await confirm.showDialog(
    `Assign order #${req.order_id || req.order?.id} to ${writerLabel}?`,
    'Assign Order',
    {
      details: 'This will approve the writer request and assign the order to them.',
      variant: 'default',
      icon: '📋',
      confirmText: 'Assign',
      cancelText: 'Cancel'
    }
  )

  if (!confirmed) {
    return
  }

  try {
    // Let the backend both approve the request and assign the order
    await writerOrderRequestsAPI.assignFromRequest(req.id, {
      reason: `Approved from writer request: ${req.reason || ''}`.trim(),
    })

    showMessage('Writer assigned successfully from request.', true)

    // Refresh relevant data
    await Promise.all([
      loadWriterRequests(),
      loadOrders(),
      loadAssignmentQueue(),
    ])
  } catch (error) {
    console.error('Failed to assign from writer request:', error)
    showMessage(
      'Failed to assign from writer request: ' + (error.response?.data?.error || error.message),
      false
    )
  }
}

const getStatusClass = (status) => {
  const classes = {
    'created': 'bg-gray-100 text-gray-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'unpaid': 'bg-red-100 text-red-800',
    'available': 'bg-blue-100 text-blue-800',
    'in_progress': 'bg-green-100 text-green-800',
    'on_hold': 'bg-orange-100 text-orange-800',
    'submitted': 'bg-purple-100 text-purple-800',
    'under_editing': 'bg-indigo-100 text-indigo-800',
    'completed': 'bg-green-100 text-green-800',
    'disputed': 'bg-red-100 text-red-800',
    'cancelled': 'bg-gray-100 text-gray-800',
    'archived': 'bg-gray-100 text-gray-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPriorityBadgeClass = (score) => {
  if (!score) return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  if (score >= 80) return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  if (score >= 60) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
  if (score >= 40) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

watch(activeQuickTab, (newTab) => {
  if (newTab === 'assignment') {
    loadAssignmentQueue()
  } else if (newTab === 'overdue') {
    loadOverdueOrders()
  } else if (newTab === 'stuck') {
    loadStuckOrders()
  } else if (newTab === 'writer-requests') {
    loadWriterRequests()
  } else if (newTab === 'all') {
    loadOrders()
  }
})

// Track if we're already loading to prevent duplicate calls
let isRouteWatchLoading = false

// Watch route query params and sync filters
watch(
  () => route.query,
  (query, oldQuery) => {
    // Skip if already loading or if query hasn't actually changed
    if (isRouteWatchLoading) return
    
    // Update filters from route query
    const newStatus = query.status || ''
    const newIsPaid = query.is_paid || ''
    const newSearch = query.search || ''
    const newClient = query.client || ''
    const newWriter = query.writer || ''
    const newWebsite = query.website || ''
    
    // Only reload if filters actually changed
    const filtersChanged = 
      filters.value.status !== newStatus ||
      filters.value.is_paid !== newIsPaid ||
      filters.value.search !== newSearch ||
      filters.value.client !== newClient ||
      filters.value.writer !== newWriter ||
      filters.value.website !== newWebsite
    
    if (!filtersChanged && oldQuery) return
    
    filters.value.status = newStatus
    filters.value.is_paid = newIsPaid
    filters.value.search = newSearch
    filters.value.client = newClient
    filters.value.writer = newWriter
    filters.value.website = newWebsite
    filters.value.include_archived = query.include_archived !== 'false'
    filters.value.include_deleted = query.include_deleted === 'true'
    filters.value.only_deleted = query.only_deleted === 'true'
    
    // Reload orders with new filters
    isRouteWatchLoading = true
    loadOrders().finally(() => {
      isRouteWatchLoading = false
    })
  },
  { immediate: true, deep: true }
)

onMounted(async () => {
  try {
    initialLoading.value = true
    componentError.value = null
    
    // Initialize filters from route query on mount (watch will handle the loadOrders call)
    filters.value = initializeFiltersFromRoute()
    
    // Load dashboard and writers (loadOrders will be called by the route watch)
    await Promise.all([
      loadDashboard(),
      loadWriters()
    ])
    
    // If route watch didn't trigger (no query params), load orders now
    if (!route.query.status && !route.query.is_paid && !route.query.search) {
      await loadOrders()
    }
    
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing OrderManagement:', error)
    componentError.value = error?.message || error?.toString() || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

<style scoped>
/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}

/* Hide scrollbar for tabs on mobile/tablet */
.scrollbar-hide {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;  /* Chrome, Safari and Opera */
}

/* Prevent overlapping and ensure proper spacing */
.status-card {
  position: relative;
  isolation: isolate;
}

/* Optimize for 13" laptops (1024px - 1440px) */
@media (min-width: 1024px) and (max-width: 1440px) {
  .status-card {
    min-height: 180px;
  }
}

/* Ensure cards don't overlap in grid */
.grid > * {
  position: relative;
  z-index: 1;
}

.grid > *:hover {
  z-index: 10;
}

/* Prevent text overflow in cards */
.status-card h3 {
  word-break: break-word;
  hyphens: auto;
}
</style>

