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
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-blue-900">{{ dashboardData?.summary?.total_orders || stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-yellow-900">{{ dashboardData?.summary?.in_progress_orders || stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-green-900">{{ dashboardData?.summary?.completed_orders || stats.completed || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Needs Assignment</p>
        <p class="text-3xl font-bold text-orange-900">{{ dashboardData?.summary?.needs_assignment || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Overdue</p>
        <p class="text-3xl font-bold text-red-900">{{ dashboardData?.summary?.overdue_orders || 0 }}</p>
      </div>
    </div>
    
    <!-- Additional Stats Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-purple-900">${{ formatCurrency(dashboardData?.summary?.total_revenue || 0) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Avg Order Value</p>
        <p class="text-3xl font-bold text-indigo-900">${{ formatCurrency(dashboardData?.summary?.avg_order_value || 0) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200">
        <p class="text-sm font-medium text-pink-700 mb-1">Pending Orders</p>
        <p class="text-3xl font-bold text-pink-900">{{ dashboardData?.summary?.pending_orders || 0 }}</p>
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
      <h2 class="text-xl font-bold mb-4">Orders Needing Assignment</h2>
      <div v-if="loadingAssignment" class="text-center py-8">Loading...</div>
      <div v-else-if="assignmentQueue.length === 0" class="text-center py-8 text-gray-500">
        No orders need assignment
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in assignmentQueue"
          :key="order.id"
          class="border rounded p-4 hover:bg-gray-50 cursor-pointer"
          @click="viewOrder(order)"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">Order #{{ order.id }} - {{ order.topic }}</p>
              <p class="text-sm text-gray-600">
                <span class="inline-flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full" :class="getWebsiteColorClass(order.website || order.website_name)"></span>
                  {{ getWebsiteName(order) }}
                </span>
                · Client: {{ order.client_username || 'N/A' }}
              </p>
              <p class="text-sm text-gray-600">Status: {{ order.status }}</p>
            </div>
            <button
              @click.stop="openAssignModal(order)"
              class="btn btn-primary text-sm"
            >
              Assign Writer
            </button>
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
                {{ req.writer_name || req.writer_username || req.writer?.user?.username || 'Unknown' }}
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
      <div class="grid grid-cols-1 md:grid-cols-8 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Order ID, topic, client..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Website</label>
          <select v-model="filters.website" @change="loadOrders" class="w-full border rounded px-3 py-2">
            <option value="">All Websites</option>
            <option v-for="website in uniqueWebsites" :key="website.id || website" :value="website.id || website">
              {{ typeof website === 'string' ? website : (website.name || website.domain || 'Unknown') }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadOrders" class="w-full border rounded px-3 py-2">
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
          <label class="block text-sm font-medium mb-1">Payment</label>
          <select v-model="filters.is_paid" @change="loadOrders" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="true">Paid</option>
            <option value="false">Unpaid</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Include Archived</label>
          <select v-model="filters.include_archived" @change="loadOrders" class="w-full border rounded px-3 py-2">
            <option :value="true">Yes (All Orders)</option>
            <option :value="false">No (Exclude Archived)</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Client</label>
          <input
            v-model="filters.client"
            @input="debouncedSearch"
            type="text"
            placeholder="Client username..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Writer</label>
          <input
            v-model="filters.writer"
            @input="debouncedSearch"
            type="text"
            placeholder="Writer username..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
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
          <button @click="bulkAssign" class="btn btn-sm btn-primary">Bulk Assign</button>
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
            <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="order.id" 
                  v-model="selectedOrders"
                />
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ order.id }}</td>
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
                <button v-else @click="openAssignModal(order)" class="text-blue-600 hover:underline text-xs">
                  Assign
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
                  <button v-else @click="openAssignModal(viewingOrder)" class="text-blue-600 hover:underline text-xs">
                    Assign Writer
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
              v-if="!viewingOrder.assigned_writer" 
              @click="openActionModal(viewingOrder, 'assign_order')" 
              class="btn btn-primary"
            >
              Assign Writer
            </button>
            <button 
              v-else 
              @click="openActionModal(viewingOrder, 'reassign_order')" 
              class="btn btn-primary bg-yellow-600 hover:bg-yellow-700"
            >
              Reassign Writer
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
                      <span v-if="writer.writer_level" class="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full font-medium">
                        {{ writer.writer_level.name || writer.writer_level }}
                      </span>
                      <span v-if="writer.is_available !== false" class="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                        Available
                      </span>
                      <span v-else class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full">
                        Unavailable
                      </span>
                    </div>
                  </div>
                  <div v-if="assignForm.writerId === writer.id" class="flex-shrink-0">
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
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ordersAPI, usersAPI, adminOrdersAPI, writerOrderRequestsAPI } from '@/api'
import { formatWriterName } from '@/utils/formatDisplay'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'
import OrderActionModal from '@/components/order/OrderActionModal.vue'

const loading = ref(false)
const orders = ref([])
const selectedOrders = ref([])
const viewingOrder = ref(null)
const showAssignModal = ref(false)
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

const filters = ref({
  search: '',
  status: '',
  is_paid: '',
  client: '',
  writer: '',
  website: '', // Add website filter
  include_archived: true, // Admin/superadmin should see all orders by default
})

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
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.is_paid) params.is_paid = filters.value.is_paid === 'true'
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.writer) params.writer = filters.value.writer
    if (filters.value.website) params.website = filters.value.website

    const res = await ordersAPI.list(params)
    orders.value = res.data.results || res.data || []
    
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
  return 'Unknown'
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

const loadWriters = async () => {
  loadingWriters.value = true
  try {
    const res = await usersAPI.list({ role: 'writer', is_active: true })
    availableWriters.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading writers:', error)
    showMessage('Failed to load writers: ' + (error.response?.data?.detail || error.message), false)
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
  currentOrderForAction.value = order
  if (availableWriters.value.length === 0) {
    await loadWriters()
  }
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
  
  assigning.value = true
  try {
    const isReassign = currentOrderForAction.value.assigned_writer || currentOrderForAction.value.writer_username
    if (isReassign) {
      await ordersAPI.reassignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
    } else {
      await ordersAPI.assignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
    }
    showMessage('Writer assigned successfully', true)
    closeAssignModal()
    await loadOrders()
    await loadAssignmentQueue() // Refresh assignment queue
    if (viewingOrder.value && viewingOrder.value.id === currentOrderForAction.value.id) {
      await viewOrder(currentOrderForAction.value)
    }
  } catch (error) {
    showMessage('Failed to assign writer: ' + (error.response?.data?.detail || error.message), false)
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
  if ((action === 'assign_order' || action === 'reassign_order') && availableWriters.value.length === 0) {
    await loadWriters()
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

const bulkAssign = () => {
  if (selectedOrders.value.length === 0) return
  // Open assign modal with first selected order
  const firstOrder = orders.value.find(o => o.id === selectedOrders.value[0])
  if (firstOrder) {
    openAssignModal(firstOrder)
  }
}

const bulkStatusChange = () => {
  const newStatus = prompt('Enter new status:')
  if (!newStatus) return
  
  // This would need backend support for bulk updates
  showMessage('Bulk status change not yet implemented', false)
}

const openAssignModalFromRequest = async (req) => {
  // Confirm with the admin before assigning
  const writerLabel =
    req.writer_name ||
    req.writer_username ||
    (req.writer && req.writer.user && req.writer.user.username) ||
    'this writer'

  if (!window.confirm(`Assign order #${req.order_id || req.order?.id} to ${writerLabel}?`)) {
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
  return status ? status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown'
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

onMounted(async () => {
  try {
    initialLoading.value = true
    componentError.value = null
    await Promise.all([
      loadDashboard(),
      loadOrders(),
      loadWriters()
    ])
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

