<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Management</h1>
        <p class="mt-2 text-gray-600">Manage orders, assignments, and status transitions</p>
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

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-blue-900">{{ dashboardData?.summary?.total_orders || stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-yellow-900">{{ dashboardData?.summary?.in_progress_orders || stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-green-900">{{ dashboardData?.summary?.completed_orders || stats.completed || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Needs Assignment</p>
        <p class="text-3xl font-bold text-orange-900">{{ dashboardData?.summary?.needs_assignment || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Overdue</p>
        <p class="text-3xl font-bold text-red-900">{{ dashboardData?.summary?.overdue_orders || 0 }}</p>
      </div>
    </div>
    
    <!-- Additional Stats Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(dashboardData?.summary?.total_revenue || 0) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Avg Order Value</p>
        <p class="text-3xl font-bold text-indigo-900">${{ formatCurrency(dashboardData?.summary?.avg_order_value || 0) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-pink-50 to-pink-100 border border-pink-200">
        <p class="text-sm font-medium text-pink-700 mb-1">Pending Orders</p>
        <p class="text-3xl font-bold text-pink-900">{{ dashboardData?.summary?.pending_orders || 0 }}</p>
      </div>
    </div>
    
    <!-- Order Transition Counts -->
    <div v-if="dashboardData?.summary || dashboardData?.transition_counts" class="card p-6 bg-white rounded-lg shadow-sm">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Orders by Available Transitions</h2>
      <p class="text-sm text-gray-600 mb-4">Count of orders that can transition to each status</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="transition in orderTransitions"
          :key="transition.key"
          class="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
        >
          <div class="text-xs font-medium text-gray-600 mb-1">{{ transition.label }}</div>
          <div class="text-2xl font-bold" :class="transition.colorClass">
            {{ transition.count }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Action Tabs -->
    <div class="border-b border-gray-200 mb-4">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeQuickTab = 'all'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
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
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeQuickTab === 'assignment'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Assignment Queue
          <span v-if="dashboardData?.summary?.needs_assignment" class="ml-2 bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">
            {{ dashboardData.summary.needs_assignment }}
          </span>
        </button>
        <button
          @click="activeQuickTab = 'overdue'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeQuickTab === 'overdue'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Overdue
          <span v-if="dashboardData?.summary?.overdue_orders" class="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
            {{ dashboardData.summary.overdue_orders }}
          </span>
        </button>
        <button
          @click="activeQuickTab = 'stuck'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
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
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeQuickTab === 'writer-requests'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Writer Requests
          <span
            v-if="writerRequests.length"
            class="ml-2 bg-indigo-500 text-white text-xs px-2 py-0.5 rounded-full"
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
    <div v-if="activeQuickTab === 'overdue'" class="card p-4">
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
    <div v-if="activeQuickTab === 'stuck'" class="card p-4">
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
    <div v-if="activeQuickTab === 'writer-requests'" class="card p-4">
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
    <div class="card p-4">
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
    <div v-if="selectedOrders.length > 0" class="card p-4 bg-yellow-50 border border-yellow-200">
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
    <div v-if="activeQuickTab === 'all'" class="card overflow-hidden">
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

    <!-- Order Detail Modal -->
    <div v-if="viewingOrder" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-5xl w-full my-auto max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">Order #{{ viewingOrder.id }}</h2>
            <button @click="viewingOrder = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Order Information</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Topic:</span> {{ viewingOrder.topic || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Status:</span> 
                  <span :class="getStatusClass(viewingOrder.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(viewingOrder.status) }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Client:</span> {{ viewingOrder.client_username || viewingOrder.client?.username || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Writer:</span> 
                  <span v-if="viewingOrder.writer_username || viewingOrder.assigned_writer">
                    {{ viewingOrder.writer_username || viewingOrder.assigned_writer?.username || 'N/A' }}
                  </span>
                  <button 
                    v-else-if="viewingOrder.is_paid" 
                    @click="openAssignModal(viewingOrder)" 
                    class="text-blue-600 hover:underline text-xs"
                  >
                    Assign Writer
                  </button>
                  <button 
                    v-else 
                    @click="showUnpaidWarningModal = true" 
                    class="text-yellow-600 hover:underline text-xs font-semibold"
                    title="Order must be paid before assigning writer"
                  >
                    ⚠️ Assign Writer
                  </button>
                </div>
                <div><span class="font-medium text-gray-600">Total Price:</span> ${{ parseFloat(viewingOrder.total_price || 0).toFixed(2) }}</div>
                <div><span class="font-medium text-gray-600">Writer Compensation:</span> ${{ parseFloat(viewingOrder.writer_compensation || 0).toFixed(2) }}</div>
                <div><span class="font-medium text-gray-600">Paid:</span> 
                  <span :class="viewingOrder.is_paid ? 'text-green-600' : 'text-red-600'">
                    {{ viewingOrder.is_paid ? 'Yes' : 'No' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Timeline</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Created:</span> {{ formatDateTime(viewingOrder.created_at) }}</div>
                <div><span class="font-medium text-gray-600">Updated:</span> {{ formatDateTime(viewingOrder.updated_at) }}</div>
                <div v-if="viewingOrder.client_deadline"><span class="font-medium text-gray-600">Client Deadline:</span> {{ formatDateTime(viewingOrder.client_deadline) }}</div>
                <div v-if="viewingOrder.writer_deadline"><span class="font-medium text-gray-600">Writer Deadline:</span> {{ formatDateTime(viewingOrder.writer_deadline) }}</div>
              </div>
            </div>
          </div>

          <div v-if="viewingOrder.order_instructions || viewingOrder.instructions" class="mb-6">
            <h3 class="text-lg font-semibold border-b pb-2 mb-2">Instructions</h3>
            <p class="text-gray-700 whitespace-pre-wrap">{{ viewingOrder.order_instructions || viewingOrder.instructions }}</p>
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
              @click="showUnpaidWarningModal = true"
              class="btn btn-secondary bg-yellow-600 hover:bg-yellow-700"
              title="Order must be paid before assigning writer"
            >
              ⚠️ Assign Writer
            </button>
            <button 
              v-else-if="viewingOrder.assigned_writer && viewingOrder.is_paid"
              @click="openActionModal(viewingOrder, 'reassign_order')" 
              class="btn btn-primary bg-yellow-600 hover:bg-yellow-700"
            >
              Reassign Writer
            </button>
            <button 
              v-else-if="viewingOrder.assigned_writer && !viewingOrder.is_paid"
              @click="showUnpaidWarningModal = true"
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
    </div>

    <!-- Enhanced Assign Writer Modal -->
    <Transition name="modal">
      <div v-if="showAssignModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto" @click.self="closeAssignModal">
        <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full my-auto max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
          <!-- Header -->
          <div class="bg-linear-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
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
                      <div class="w-10 h-10 rounded-full bg-linear-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold">
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
              class="flex-1 px-4 py-2.5 bg-linear-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
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
      v-model:visible="showActionModal"
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
      v-model:show="confirmShow"
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
</template>

<script setup>
import { ref, computed, onMounted, watch, unref } from 'vue'
import { useRoute } from 'vue-router'
import { ordersAPI, usersAPI, adminOrdersAPI, writerOrderRequestsAPI, writerAssignmentAPI } from '@/api'
import { formatWriterName } from '@/utils/formatDisplay'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'
import OrderActionModal from '@/components/order/OrderActionModal.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { getErrorMessage } from '@/utils/errorHandler'
import { useToast } from '@/composables/useToast'

const route = useRoute()

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
  }
  loadOrders()
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedOrders.value = []
  } else {
    selectedOrders.value = orders.value.map(o => o.id)
  }
}

const viewOrder = async (order) => {
  try {
    const res = await ordersAPI.get(order.id)
    viewingOrder.value = res.data
  } catch (error) {
    console.error('Error loading order:', error)
    showMessage('Failed to load order details: ' + (error.response?.data?.detail || error.message), false)
  }
}

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

const getStatusLabel = (status) => {
  return status ? status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'
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
</style>

