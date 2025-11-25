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
              <p class="text-sm text-gray-600">Client: {{ order.client_username || 'N/A' }}</p>
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
              <p class="text-sm text-gray-600">Client: {{ order.client_username || 'N/A' }}</p>
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
              <p class="text-sm text-gray-600">Client: {{ order.client_username || 'N/A' }}</p>
              <p class="text-sm text-yellow-600">Last Updated: {{ formatDate(order.updated_at) }}</p>
            </div>
            <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">Stuck</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-6 gap-4">
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

    <!-- Orders Table -->
    <div class="card overflow-hidden">
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
    <div v-if="viewingOrder" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-y-auto">
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

    <!-- Assign Writer Modal -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Assign Writer</h3>
          <button @click="closeAssignModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select Writer</label>
            <select v-model="assignForm.writerId" class="w-full border rounded px-3 py-2">
              <option value="">Select a writer...</option>
              <option v-for="writer in availableWriters" :key="writer.id" :value="writer.id">
                {{ formatWriterName(writer) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Reason (optional)</label>
            <textarea v-model="assignForm.reason" class="w-full border rounded px-3 py-2" rows="3"></textarea>
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="confirmAssign" class="btn btn-primary flex-1">Assign</button>
            <button @click="closeAssignModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Order Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Edit Order</h3>
          <button @click="closeEditModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
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
          <div class="flex gap-2 pt-4">
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
import { ordersAPI, usersAPI, adminOrdersAPI } from '@/api'
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

const filters = ref({
  search: '',
  status: '',
  is_paid: '',
  client: '',
  writer: '',
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

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadOrders()
  }, 500)
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
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.is_paid) params.is_paid = filters.value.is_paid === 'true'
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.client) params.client = filters.value.client
    if (filters.value.writer) params.writer = filters.value.writer

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

const loadWriters = async () => {
  try {
    const res = await usersAPI.list({ role: 'writer', is_active: true })
    availableWriters.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading writers:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    is_paid: '',
    client: '',
    writer: '',
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
  showAssignModal.value = false
  assignForm.value = { writerId: '', reason: '' }
  currentOrderForAction.value = null
}

const confirmAssign = async () => {
  if (!assignForm.value.writerId || !currentOrderForAction.value) return
  
  try {
    const isReassign = currentOrderForAction.value.assigned_writer || currentOrderForAction.value.writer_username
    if (isReassign) {
      await ordersAPI.reassignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
    } else {
      await ordersAPI.assignWriter(currentOrderForAction.value.id, assignForm.value.writerId, assignForm.value.reason)
    }
    showMessage('Writer assigned successfully', true)
    closeAssignModal()
    loadOrders()
    if (viewingOrder.value && viewingOrder.value.id === currentOrderForAction.value.id) {
      await viewOrder(currentOrderForAction.value)
    }
  } catch (error) {
    showMessage('Failed to assign writer: ' + (error.response?.data?.detail || error.message), false)
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
  } else if (newTab === 'all') {
    loadOrders()
  }
})

onMounted(async () => {
  try {
    await Promise.all([
      loadDashboard(),
      loadOrders(),
      loadWriters()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing OrderManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

