<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Special Orders Management</h1>
        <p class="mt-2 text-gray-600">Manage special orders, approvals, installments, and configurations</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-blue-900">{{ dashboardData?.summary?.total_orders || stats.total_orders || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Awaiting Approval</p>
        <p class="text-3xl font-bold text-yellow-900">{{ dashboardData?.summary?.awaiting_approval || stats.awaiting_approval || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-green-900">{{ dashboardData?.summary?.in_progress || stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-purple-900">{{ dashboardData?.summary?.completed || stats.completed || 0 }}</p>
      </div>
    </div>
    
    <!-- Additional Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Needs Approval</p>
        <p class="text-3xl font-bold text-orange-900">{{ dashboardData?.summary?.needs_approval || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Needs Estimation</p>
        <p class="text-3xl font-bold text-red-900">{{ dashboardData?.summary?.needs_estimation || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200">
        <p class="text-sm font-medium text-indigo-700 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-indigo-900">${{ formatCurrency(dashboardData?.summary?.total_revenue || 0) }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-pink-50 to-pink-100 border border-pink-200">
        <p class="text-sm font-medium text-pink-700 mb-1">Pending Installments</p>
        <p class="text-3xl font-bold text-pink-900">{{ dashboardData?.summary?.pending_installments || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
          <span v-if="tab.badge && tab.badge.value > 0" class="ml-2 bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">
            {{ tab.badge.value }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Approval Queue Tab -->
    <div v-if="activeTab === 'approval-queue'" class="space-y-4">
      <h2 class="text-xl font-bold">Orders Awaiting Approval</h2>
      <div v-if="loadingApproval" class="text-center py-8">Loading...</div>
      <div v-else-if="approvalQueue.length === 0" class="text-center py-8 text-gray-500">
        No orders awaiting approval
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in approvalQueue"
          :key="order.id"
          class="border rounded p-4 hover:bg-gray-50 cursor-pointer"
          @click="viewOrder(order)"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">Order #{{ order.id }}</p>
              <p class="text-sm text-gray-600">Client: {{ order.client_username || 'N/A' }}</p>
              <p class="text-sm text-gray-600">Type: {{ order.order_type }}</p>
              <p class="text-sm text-gray-600">Status: {{ order.status }}</p>
            </div>
            <button
              @click.stop="approveOrder(order)"
              class="btn btn-primary text-sm"
            >
              Approve
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Estimated Queue Tab -->
    <div v-if="activeTab === 'estimated-queue'" class="space-y-4">
      <h2 class="text-xl font-bold">Orders Needing Cost Estimation</h2>
      <div v-if="loadingEstimation" class="text-center py-8">Loading...</div>
      <div v-else-if="estimatedQueue.length === 0" class="text-center py-8 text-gray-500">
        No orders need cost estimation
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="order in estimatedQueue"
          :key="order.id"
          class="border rounded p-4 hover:bg-gray-50 cursor-pointer"
          @click="viewOrder(order)"
        >
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">Order #{{ order.id }}</p>
              <p class="text-sm text-gray-600">Client: {{ order.client_username || 'N/A' }}</p>
              <p class="text-sm text-gray-600">Duration: {{ order.duration_days }} days</p>
            </div>
            <button
              @click.stop="viewOrder(order)"
              class="btn btn-primary text-sm"
            >
              View & Estimate
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Orders Tab -->
    <div v-if="activeTab === 'orders'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="filters.status" @change="loadOrders" class="w-full border rounded px-3 py-2">
              <option value="">All Statuses</option>
              <option value="inquiry">Inquiry</option>
              <option value="awaiting_approval">Awaiting Approval</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Order Type</label>
            <select v-model="filters.order_type" @change="loadOrders" class="w-full border rounded px-3 py-2">
              <option value="">All Types</option>
              <option value="predefined">Predefined</option>
              <option value="estimated">Estimated</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Order ID, client..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website</label>
            <select v-model="filters.website" @change="loadOrders" class="w-full border rounded px-3 py-2">
              <option value="">All Websites</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Orders Table -->
      <div class="card overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Cost</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deposit</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ order.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ order.client?.username || order.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'" 
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(order.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(order.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(order.total_cost || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(order.deposit_required || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(order.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center gap-2">
                    <button @click="viewOrder(order)" class="text-blue-600 hover:underline">View</button>
                    <button v-if="order.status === 'awaiting_approval'" @click="approveOrder(order)" class="text-green-600 hover:underline">Approve</button>
                    <button v-if="order.status === 'estimated' && !order.total_cost" @click="setCost(order)" class="text-purple-600 hover:underline">Set Cost</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!orders.length" class="text-center py-12 text-gray-500">
            No special orders found.
          </div>
        </div>
      </div>
    </div>

    <!-- Installments Tab -->
    <div v-if="activeTab === 'installments'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="installmentFilters.status" @change="loadInstallments" class="w-full border rounded px-3 py-2">
              <option value="">All Statuses</option>
              <option value="paid">Paid</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Order ID</label>
            <input
              v-model="installmentFilters.order_id"
              @input="debouncedInstallmentSearch"
              type="number"
              placeholder="Filter by order ID"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Due Date From</label>
            <input
              v-model="installmentFilters.due_date_from"
              @change="loadInstallments"
              type="date"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div class="flex items-end">
            <button @click="resetInstallmentFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Installments Table -->
      <div class="card overflow-hidden">
        <div v-if="installmentsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paid Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="installment in installments" :key="installment.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  <button @click="viewOrderFromInstallment(installment)" class="text-blue-600 hover:underline">
                    #{{ installment.special_order?.id || 'N/A' }}
                  </button>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ installment.special_order?.client?.username || installment.special_order?.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(installment.amount_due || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(installment.due_date) }}
                  <span v-if="isOverdue(installment.due_date) && !installment.is_paid" class="ml-2 text-xs text-red-600">(Overdue)</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ installment.paid_at ? formatDateTime(installment.paid_at) : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="installment.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ installment.is_paid ? 'Paid' : 'Pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="viewInstallment(installment)" class="text-blue-600 hover:underline mr-2">View</button>
                  <button v-if="!installment.is_paid" @click="markInstallmentPaid(installment)" class="text-green-600 hover:underline">Mark Paid</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!installments.length" class="text-center py-12 text-gray-500">
            No installments found.
          </div>
        </div>
      </div>
    </div>

    <!-- Installment Settings Tab -->
    <div v-if="activeTab === 'installment-settings'" class="space-y-4">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-xl font-semibold">Estimated Order Deposit Settings</h2>
          <p class="text-sm text-gray-600">Configure default deposit percentages for estimated special orders by website</p>
        </div>
        <button @click="createNewEstimatedSetting" class="btn btn-primary">+ Add Setting</button>
      </div>

      <div class="card overflow-hidden">
        <div v-if="estimatedSettingsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Default Deposit %</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="setting in estimatedSettings" :key="setting.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ setting.website?.name || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ parseFloat(setting.default_deposit_percentage || 50).toFixed(2) }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button v-if="setting.id" @click="editEstimatedSetting(setting)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button v-else @click="editEstimatedSetting(setting)" class="text-green-600 hover:underline font-medium">Create Setting</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!estimatedSettings.length" class="text-center py-12 text-gray-500">
            <p class="mb-4">No estimated order settings found.</p>
            <p class="text-sm text-gray-400">Settings will be created automatically when needed, or you can create them manually.</p>
          </div>
        </div>
      </div>

      <!-- Info Card -->
      <div class="card p-4 bg-blue-50 border border-blue-200">
        <h3 class="font-semibold text-blue-900 mb-2">About Installment Settings</h3>
        <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Deposit percentage determines how much clients pay upfront for estimated orders</li>
          <li>Remaining balance is split into installments (typically due 7 days after order creation)</li>
          <li>Predefined orders require full payment upfront (no installments)</li>
          <li>Each website can have its own deposit percentage setting</li>
        </ul>
      </div>
    </div>

    <!-- Configurations Tab -->
    <div v-if="activeTab === 'configs'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Predefined Order Configurations</h2>
        <button @click="createNewConfig" class="btn btn-primary">+ Add Configuration</button>
      </div>

      <div class="card overflow-hidden">
        <div v-if="configsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else>
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Durations</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in predefinedConfigs" :key="config.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ config.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ typeof config.website === 'object' ? config.website?.name : (config.website || 'N/A') }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="config.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" 
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ config.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div v-if="config.durations && config.durations.length > 0">
                    <div v-for="(duration, idx) in config.durations.slice(0, 2)" :key="duration.id || idx" class="text-xs">
                      {{ duration.duration_days }}d: ${{ parseFloat(duration.price || 0).toFixed(2) }}
                    </div>
                    <div v-if="config.durations.length > 2" class="text-xs text-gray-400">
                      +{{ config.durations.length - 2 }} more
                    </div>
                  </div>
                  <span v-else class="text-gray-400">No durations</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button @click="editConfig(config)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button @click="deleteConfig(config.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="!predefinedConfigs.length" class="text-center py-12 text-gray-500">
            No predefined configurations found.
          </div>
        </div>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="viewingOrder" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">Special Order #{{ viewingOrder.id }}</h2>
            <button @click="viewingOrder = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Order Information</h3>
              <div class="space-y-2">
                <div><span class="text-sm font-medium text-gray-600">Client:</span> {{ viewingOrder.client?.username || 'N/A' }}</div>
                <div><span class="text-sm font-medium text-gray-600">Type:</span> 
                  <span :class="viewingOrder.order_type === 'predefined' ? 'text-blue-600' : 'text-purple-600'">
                    {{ viewingOrder.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
                  </span>
                </div>
                <div><span class="text-sm font-medium text-gray-600">Status:</span> 
                  <span :class="getStatusClass(viewingOrder.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(viewingOrder.status) }}
                  </span>
                </div>
                <div><span class="text-sm font-medium text-gray-600">Total Cost:</span> ${{ parseFloat(viewingOrder.total_cost || 0).toFixed(2) }}</div>
                <div><span class="text-sm font-medium text-gray-600">Deposit Required:</span> ${{ parseFloat(viewingOrder.deposit_required || 0).toFixed(2) }}</div>
                <div><span class="text-sm font-medium text-gray-600">Duration:</span> {{ viewingOrder.duration_days }} days</div>
              </div>
            </div>
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Details</h3>
              <div class="space-y-2">
                <div><span class="text-sm font-medium text-gray-600">Created:</span> {{ formatDateTime(viewingOrder.created_at) }}</div>
                <div><span class="text-sm font-medium text-gray-600">Updated:</span> {{ formatDateTime(viewingOrder.updated_at) }}</div>
                <div v-if="viewingOrder.writer"><span class="text-sm font-medium text-gray-600">Writer:</span> {{ viewingOrder.writer?.username || 'N/A' }}</div>
                <div><span class="text-sm font-medium text-gray-600">Approved:</span> {{ viewingOrder.is_approved ? 'Yes' : 'No' }}</div>
                <div v-if="viewingOrder.admin_marked_paid" class="flex items-center gap-2">
                  <span class="text-sm font-medium text-yellow-600">Payment Overridden</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-600">Files Unlocked:</span>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      :checked="viewingOrder.admin_unlocked_files" 
                      @change="toggleFileUnlock(viewingOrder)"
                      class="sr-only peer"
                    />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    <span class="ml-2 text-sm text-gray-700">{{ viewingOrder.admin_unlocked_files ? 'Unlocked' : 'Locked' }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div v-if="viewingOrder.inquiry_details" class="mb-6">
            <h3 class="text-lg font-semibold border-b pb-2 mb-2">Inquiry Details</h3>
            <p class="text-gray-700 whitespace-pre-wrap">{{ viewingOrder.inquiry_details }}</p>
          </div>

          <div v-if="viewingOrder.admin_notes" class="mb-6">
            <h3 class="text-lg font-semibold border-b pb-2 mb-2">Admin Notes</h3>
            <p class="text-gray-700 whitespace-pre-wrap">{{ viewingOrder.admin_notes }}</p>
          </div>

          <!-- Files Section -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold border-b pb-2 flex-1">Files</h3>
              <button v-if="orderFiles.length > 0" @click="refreshFiles" class="text-sm text-blue-600 hover:underline">Refresh</button>
            </div>
            <div v-if="filesLoading" class="flex items-center justify-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
            <div v-else-if="orderFiles.length > 0" class="space-y-3">
              <div v-for="file in orderFiles" :key="file.id" class="p-3 bg-gray-50 rounded border flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <span class="text-sm font-medium text-gray-900">{{ file.category?.name || 'Uncategorized' }}</span>
                    <span class="text-xs text-gray-500">{{ formatDateTime(file.created_at) }}</span>
                    <span v-if="file.uploaded_by" class="text-xs text-gray-500">by {{ file.uploaded_by?.username || 'Unknown' }}</span>
                  </div>
                  <div class="text-xs text-gray-600 mt-1">
                    <span v-if="file.file">File: {{ file.file.split('/').pop() }}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span :class="file.is_downloadable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" 
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ file.is_downloadable ? 'Downloadable' : 'Locked' }}
                  </span>
                  <button @click="toggleFileDownload(file)" class="text-xs text-blue-600 hover:underline">
                    {{ file.is_downloadable ? 'Lock' : 'Unlock' }}
                  </button>
                  <button @click="downloadFile(file)" class="text-xs text-green-600 hover:underline">Download</button>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500 text-sm">
              <p>No files uploaded yet</p>
              <p class="text-xs text-gray-400 mt-1">Files will appear here when uploaded by writers</p>
            </div>
          </div>

          <!-- Installments Section -->
          <div v-if="viewingOrder.installments && viewingOrder.installments.length > 0" class="mb-6">
            <h3 class="text-lg font-semibold border-b pb-2 mb-4">Installments</h3>
            <div class="space-y-3">
              <div v-for="installment in viewingOrder.installments" :key="installment.id" class="p-3 bg-gray-50 rounded border">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-4 text-sm">
                      <span class="font-medium">${{ parseFloat(installment.amount_due || 0).toFixed(2) }}</span>
                      <span class="text-gray-600">Due: {{ formatDate(installment.due_date) }}</span>
                      <span v-if="installment.paid_at" class="text-gray-600">Paid: {{ formatDateTime(installment.paid_at) }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span :class="installment.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                          class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ installment.is_paid ? 'Paid' : 'Pending' }}
                    </span>
                    <button v-if="!installment.is_paid" @click="markInstallmentPaid(installment)" class="text-xs text-green-600 hover:underline">Mark Paid</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button @click="showOrderThreadsModal = true" class="btn btn-primary bg-blue-600 hover:bg-blue-700">
              💬 View Messages
            </button>
            <button v-if="viewingOrder.status === 'awaiting_approval'" @click="approveOrder(viewingOrder)" class="btn btn-primary">Approve Order</button>
            <button v-if="viewingOrder.order_type === 'estimated' && !viewingOrder.total_cost" @click="setCost(viewingOrder)" class="btn btn-primary bg-purple-600 hover:bg-purple-700">Set Cost</button>
            <button v-if="!viewingOrder.admin_marked_paid" @click="overridePayment(viewingOrder)" class="btn btn-primary bg-yellow-600 hover:bg-yellow-700">Override Payment</button>
            <button v-if="viewingOrder.status === 'in_progress'" @click="completeOrder(viewingOrder)" class="btn btn-primary bg-green-600 hover:bg-green-700">Mark Complete</button>
            <button @click="toggleFileUnlock(viewingOrder)" class="btn btn-primary bg-indigo-600 hover:bg-indigo-700">
              {{ viewingOrder.admin_unlocked_files ? 'Lock Files' : 'Unlock Files' }}
            </button>
            <button @click="viewInstallmentsForOrder(viewingOrder)" class="btn btn-secondary">View All Installments</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Set Cost Modal -->
    <div v-if="showCostModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">Set Order Cost</h3>
        <form @submit.prevent="saveCost" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Total Cost *</label>
            <input v-model.number="costForm.total_cost" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Deposit Required *</label>
            <input v-model.number="costForm.deposit_required" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Price Per Day</label>
            <input v-model.number="costForm.price_per_day" type="number" step="0.01" min="0" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="showCostModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">{{ saving ? 'Saving...' : 'Save' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Config Modal (Create/Edit) -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">{{ editingConfig ? 'Edit Configuration' : 'Create Configuration' }}</h3>
          <button @click="closeConfigModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        
        <form @submit.prevent="saveConfig" class="space-y-6">
          <!-- Basic Config Fields -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Name *</label>
              <input v-model="configForm.name" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., Shadow Health" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea v-model="configForm.description" rows="3" class="w-full border rounded px-3 py-2" placeholder="Description of this order type"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <select v-model.number="configForm.website" required class="w-full border rounded px-3 py-2">
                  <option :value="null">Select Website</option>
                  <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
                </select>
              </div>
              <div class="flex items-end">
                <label class="flex items-center">
                  <input v-model="configForm.is_active" type="checkbox" class="mr-2" />
                  <span class="text-sm font-medium">Active</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Durations Section -->
          <div class="border-t pt-4">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-semibold">Duration Pricing</h4>
              <button type="button" @click="addDuration" class="btn btn-primary text-sm">+ Add Duration</button>
            </div>
            
            <div v-if="configForm.durations.length === 0" class="text-center py-4 text-gray-500 text-sm">
              No durations added. Click "Add Duration" to add pricing options.
            </div>
            
            <div v-else class="space-y-3">
              <div v-for="(duration, index) in configForm.durations" :key="index" class="flex items-center gap-3 p-3 bg-gray-50 rounded">
                <div class="flex-1">
                  <label class="block text-xs font-medium mb-1 text-gray-600">Duration (days)</label>
                  <input v-model.number="duration.duration_days" type="number" min="1" required class="w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div class="flex-1">
                  <label class="block text-xs font-medium mb-1 text-gray-600">Price ($)</label>
                  <input v-model.number="duration.price" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2 text-sm" />
                </div>
                <div class="flex items-end">
                  <button type="button" @click="removeDuration(index)" class="text-red-600 hover:text-red-800 px-2 py-1">Remove</button>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-2 pt-4 border-t">
            <button type="button" @click="closeConfigModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingConfig ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Estimated Setting Modal -->
    <div v-if="showEstimatedSettingModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">{{ editingEstimatedSetting?.id ? 'Edit Deposit Setting' : 'Create Deposit Setting' }}</h3>
          <button @click="closeEstimatedSettingModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <form @submit.prevent="saveEstimatedSetting" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Website *</label>
            <select v-model.number="estimatedSettingForm.website" required class="w-full border rounded px-3 py-2" :disabled="!!editingEstimatedSetting?.id">
              <option :value="null">Select Website</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
            <p class="text-xs text-gray-500 mt-1" v-if="editingEstimatedSetting?.id">Website cannot be changed after creation</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Default Deposit Percentage *</label>
            <input v-model.number="estimatedSettingForm.default_deposit_percentage" type="number" step="0.01" min="0" max="100" required class="w-full border rounded px-3 py-2" />
            <p class="text-xs text-gray-500 mt-1">Percentage of total cost required as deposit (0-100)</p>
          </div>
          <div class="bg-blue-50 p-3 rounded text-sm text-blue-800">
            <p><strong>Example:</strong> If deposit is 50% and order total is $100:</p>
            <ul class="list-disc list-inside mt-1">
              <li>Deposit: $50 (due immediately)</li>
              <li>Balance: $50 (due in 7 days)</li>
            </ul>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeEstimatedSettingModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingEstimatedSetting?.id ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Installment Detail Modal -->
    <div v-if="showInstallmentModal && viewingInstallment" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-2xl font-bold">Installment Details</h3>
          <button @click="showInstallmentModal = false; viewingInstallment = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="text-sm font-medium text-gray-600">Order ID:</span>
              <p class="text-gray-900 font-medium">#{{ viewingInstallment.special_order?.id || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Client:</span>
              <p class="text-gray-900">{{ viewingInstallment.special_order?.client?.username || viewingInstallment.special_order?.client?.email || 'N/A' }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Amount Due:</span>
              <p class="text-gray-900 font-semibold text-lg">${{ parseFloat(viewingInstallment.amount_due || 0).toFixed(2) }}</p>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Status:</span>
              <span :class="viewingInstallment.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                    class="px-2 py-1 rounded-full text-xs font-medium">
                {{ viewingInstallment.is_paid ? 'Paid' : 'Pending' }}
              </span>
            </div>
            <div>
              <span class="text-sm font-medium text-gray-600">Due Date:</span>
              <p class="text-gray-900">{{ formatDate(viewingInstallment.due_date) }}</p>
              <span v-if="isOverdue(viewingInstallment.due_date) && !viewingInstallment.is_paid" class="text-xs text-red-600">(Overdue)</span>
            </div>
            <div v-if="viewingInstallment.is_paid">
              <span class="text-sm font-medium text-gray-600">Paid Date:</span>
              <p class="text-gray-900">{{ viewingInstallment.paid_at ? formatDateTime(viewingInstallment.paid_at) : 'N/A' }}</p>
            </div>
          </div>

          <div v-if="viewingInstallment.payment_record" class="border-t pt-4">
            <h4 class="font-semibold mb-2">Payment Record</h4>
            <div class="text-sm text-gray-600">
              <p>Payment ID: {{ viewingInstallment.payment_record?.id || 'N/A' }}</p>
              <p>Status: {{ viewingInstallment.payment_record?.status || 'N/A' }}</p>
            </div>
          </div>

          <div class="flex gap-2 pt-4 border-t">
            <button @click="viewOrderFromInstallment(viewingInstallment)" class="btn btn-secondary">View Order</button>
            <button v-if="!viewingInstallment.is_paid" @click="markInstallmentPaid(viewingInstallment)" class="btn btn-primary">Mark as Paid</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>

    <!-- Order Threads Modal -->
    <OrderThreadsModal
      v-if="showOrderThreadsModal && viewingOrder"
      :order-id="viewingOrder.id"
      @close="showOrderThreadsModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { specialOrdersAPI, orderFilesAPI, adminSpecialOrdersAPI } from '@/api'
import apiClient from '@/api/client'
import OrderThreadsModal from '@/components/order/OrderThreadsModal.vue'

const authStore = useAuthStore()

// Debug: Log to ensure component is loading
console.log('SpecialOrderManagement component loaded')

const activeTab = ref('orders')
const tabs = [
  { id: 'orders', label: 'Orders' },
  { id: 'approval-queue', label: 'Approval Queue', badge: computed(() => dashboardData.value?.summary?.needs_approval || 0) },
  { id: 'estimated-queue', label: 'Estimation Queue', badge: computed(() => dashboardData.value?.summary?.needs_estimation || 0) },
  { id: 'installments', label: 'Installments' },
  { id: 'configs', label: 'Configurations' },
  { id: 'installment-settings', label: 'Installment Settings' },
]

const componentError = ref(null)
const initialLoading = ref(true)
const orders = ref([])
const installments = ref([])
const predefinedConfigs = ref([])
const estimatedSettings = ref([])
const websites = ref([])
const loading = ref(false)
const installmentsLoading = ref(false)
const configsLoading = ref(false)
const estimatedSettingsLoading = ref(false)
const saving = ref(false)
const viewingOrder = ref(null)
const viewingInstallment = ref(null)
const showOrderThreadsModal = ref(false)
const showCostModal = ref(false)
const showConfigModal = ref(false)
const showEstimatedSettingModal = ref(false)
const showInstallmentModal = ref(false)
const currentOrder = ref(null)
const editingConfig = ref(null)
const editingEstimatedSetting = ref(null)
const orderFiles = ref([])
const filesLoading = ref(false)

const configForm = ref({
  name: '',
  description: '',
  website: null,
  is_active: true,
  durations: [], // Array of { duration_days, price }
})

const stats = ref({
  total_orders: 0,
  awaiting_approval: 0,
  in_progress: 0,
  completed: 0,
})
const dashboardData = ref(null)
const approvalQueue = ref([])
const estimatedQueue = ref([])
const loadingDashboard = ref(false)
const loadingApproval = ref(false)
const loadingEstimation = ref(false)

const filters = ref({
  status: '',
  order_type: '',
  search: '',
  website: '',
})

const installmentFilters = ref({
  status: '',
  order_id: '',
  due_date_from: '',
})

const estimatedSettingForm = ref({
  website: null,
  default_deposit_percentage: 50.0,
})

const costForm = ref({
  total_cost: 0,
  deposit_required: 0,
  price_per_day: 0,
})

const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null
let installmentSearchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadOrders()
  }, 500)
}

const debouncedInstallmentSearch = () => {
  clearTimeout(installmentSearchTimeout)
  installmentSearchTimeout = setTimeout(() => {
    loadInstallments()
  }, 500)
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const res = await adminSpecialOrdersAPI.getDashboard()
    dashboardData.value = res.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadApprovalQueue = async () => {
  loadingApproval.value = true
  try {
    const res = await adminSpecialOrdersAPI.getApprovalQueue({ limit: 50 })
    approvalQueue.value = res.data.orders || []
  } catch (error) {
    console.error('Error loading approval queue:', error)
    showMessage('Failed to load approval queue: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingApproval.value = false
  }
}

const loadEstimatedQueue = async () => {
  loadingEstimation.value = true
  try {
    const res = await adminSpecialOrdersAPI.getEstimatedQueue({ limit: 50 })
    estimatedQueue.value = res.data.orders || []
  } catch (error) {
    console.error('Error loading estimated queue:', error)
    showMessage('Failed to load estimated queue: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loadingEstimation.value = false
  }
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.order_type) params.order_type = filters.value.order_type
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website

    console.log('Loading special orders with params:', params)
    const res = await specialOrdersAPI.list(params)
    console.log('Special orders response:', res)
    orders.value = res.data.results || res.data || []
    
    // Calculate stats (fallback if dashboard not loaded)
    stats.value.total_orders = orders.value.length
    stats.value.awaiting_approval = orders.value.filter(o => o.status === 'awaiting_approval').length
    stats.value.in_progress = orders.value.filter(o => o.status === 'in_progress').length
    stats.value.completed = orders.value.filter(o => o.status === 'completed').length
  } catch (error) {
    console.error('Error loading special orders:', error)
    showMessage('Failed to load orders: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (value) => {
  if (!value) return '0.00'
  return parseFloat(value).toFixed(2)
}

const loadInstallments = async () => {
  installmentsLoading.value = true
  try {
    const params = {}
    if (installmentFilters.value.status) {
      params.is_paid = installmentFilters.value.status === 'paid'
    }
    if (installmentFilters.value.order_id) {
      params.special_order = installmentFilters.value.order_id
    }
    if (installmentFilters.value.due_date_from) {
      params.due_date__gte = installmentFilters.value.due_date_from
    }

    const res = await specialOrdersAPI.listInstallments(params)
    installments.value = res.data.results || res.data || []
  } catch (error) {
    showMessage('Failed to load installments: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    installmentsLoading.value = false
  }
}

const loadEstimatedSettings = async () => {
  estimatedSettingsLoading.value = true
  try {
    // Load all settings
    const res = await specialOrdersAPI.listEstimatedSettings()
    const existingSettings = res.data.results || res.data || []
    
    // Load all websites
    const websitesRes = await apiClient.get('/websites/websites/')
    const allWebsites = websitesRes.data.results || websitesRes.data || []
    
    // Create a map of website IDs to settings
    const settingsMap = new Map()
    existingSettings.forEach(setting => {
      const websiteId = typeof setting.website === 'object' ? setting.website?.id : setting.website
      if (websiteId) {
        settingsMap.set(websiteId, setting)
      }
    })
    
    // Combine: existing settings + websites without settings
    const settings = []
    for (const website of allWebsites) {
      if (settingsMap.has(website.id)) {
        settings.push(settingsMap.get(website.id))
      } else {
        // Website doesn't have a setting yet
        settings.push({
          id: null,
          website: website,
          website_id: website.id,
          default_deposit_percentage: 50.0,
          is_new: true,
        })
      }
    }
    
    estimatedSettings.value = settings
  } catch (error) {
    console.error('Error loading estimated settings:', error)
    showMessage('Failed to load estimated settings: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    estimatedSettingsLoading.value = false
  }
}

const resetInstallmentFilters = () => {
  installmentFilters.value = {
    status: '',
    order_id: '',
    due_date_from: '',
  }
  loadInstallments()
}

const loadConfigs = async () => {
  configsLoading.value = true
  try {
    const res = await specialOrdersAPI.listPredefinedConfigs()
    const configs = res.data.results || res.data || []
    
    // Load durations for each config
    for (const config of configs) {
      try {
        const durationsRes = await specialOrdersAPI.listDurations({ predefined_order: config.id })
        config.durations = durationsRes.data.results || durationsRes.data || []
      } catch (err) {
        console.warn(`Failed to load durations for config ${config.id}:`, err)
        config.durations = []
      }
    }
    
    predefinedConfigs.value = configs
  } catch (error) {
    showMessage('Failed to load configurations: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    configsLoading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
    // Don't show error message for websites, it's not critical
  }
}

const viewOrder = async (order) => {
  // Load full order details including installments and files
  try {
    const res = await specialOrdersAPI.get(order.id)
    viewingOrder.value = res.data
    
    // Load installments for this order if not already loaded
    if (!viewingOrder.value.installments || viewingOrder.value.installments.length === 0) {
      try {
        const installmentsRes = await specialOrdersAPI.listInstallments({ special_order: order.id })
        viewingOrder.value.installments = installmentsRes.data.results || installmentsRes.data || []
      } catch (err) {
        console.warn('Failed to load installments:', err)
        viewingOrder.value.installments = []
      }
    }
    
    // Load files for this order
    await loadOrderFiles(order.id)
  } catch (error) {
    // Fallback to using the order object directly
    viewingOrder.value = order
    showMessage('Failed to load full order details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const loadOrderFiles = async (orderId) => {
  filesLoading.value = true
  try {
    // Note: Special orders might not have direct file links in OrderFile model
    // This attempts to load files, but may return empty if special orders use a different system
    // You may need to adjust the filter based on your backend implementation
    const res = await orderFilesAPI.list({ order: orderId })
    orderFiles.value = res.data.results || res.data || []
  } catch (error) {
    console.warn('Failed to load files (may not exist for special orders):', error)
    orderFiles.value = []
  } finally {
    filesLoading.value = false
  }
}

const refreshFiles = async () => {
  if (viewingOrder.value) {
    await loadOrderFiles(viewingOrder.value.id)
  }
}

const toggleFileUnlock = async (order) => {
  if (!confirm(`Are you sure you want to ${order.admin_unlocked_files ? 'lock' : 'unlock'} files for this order?`)) return
  
  saving.value = true
  try {
    const res = await specialOrdersAPI.update(order.id, {
      admin_unlocked_files: !order.admin_unlocked_files
    })
    viewingOrder.value = res.data
    showMessage(`Files ${order.admin_unlocked_files ? 'locked' : 'unlocked'} successfully`, true)
  } catch (error) {
    showMessage('Failed to toggle file unlock: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const toggleFileDownload = async (file) => {
  saving.value = true
  try {
    await orderFilesAPI.toggleDownload(file.id)
    // Refresh file list
    await refreshFiles()
    showMessage('File download status updated', true)
  } catch (error) {
    showMessage('Failed to toggle file download: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const downloadFile = async (file) => {
  try {
    const res = await orderFilesAPI.getSignedUrl(file.id)
    if (res.data.url) {
      window.open(res.data.url, '_blank')
    } else {
      // Fallback to direct download endpoint
      const downloadUrl = `/api/v1/order-files/order-files/${file.id}/download/`
      window.open(downloadUrl, '_blank')
    }
  } catch (error) {
    showMessage('Failed to get download URL: ' + (error.response?.data?.detail || error.message), false)
  }
}

const approveOrder = async (order) => {
  if (!confirm('Are you sure you want to approve this order?')) return
  
  saving.value = true
  try {
    await specialOrdersAPI.approve(order.id)
    showMessage('Order approved successfully', true)
    await loadOrders()
    if (viewingOrder.value?.id === order.id) {
      viewingOrder.value = null
    }
  } catch (error) {
    showMessage('Failed to approve order: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const setCost = (order) => {
  currentOrder.value = order
  costForm.value = {
    total_cost: parseFloat(order.total_cost || 0),
    deposit_required: parseFloat(order.deposit_required || 0),
    price_per_day: parseFloat(order.price_per_day || 0),
  }
  showCostModal.value = true
}

const saveCost = async () => {
  saving.value = true
  try {
    await specialOrdersAPI.update(currentOrder.value.id, costForm.value)
    showMessage('Cost updated successfully', true)
    showCostModal.value = false
    await loadOrders()
    if (viewingOrder.value?.id === currentOrder.value.id) {
      await loadOrders()
      viewingOrder.value = orders.value.find(o => o.id === currentOrder.value.id)
    }
  } catch (error) {
    showMessage('Failed to update cost: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const overridePayment = async (order) => {
  if (!confirm('Override payment status for this order?')) return
  
  saving.value = true
  try {
    await specialOrdersAPI.overridePayment(order.id)
    showMessage('Payment overridden successfully', true)
    await loadOrders()
    if (viewingOrder.value?.id === order.id) {
      viewingOrder.value = orders.value.find(o => o.id === order.id)
    }
  } catch (error) {
    showMessage('Failed to override payment: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const completeOrder = async (order) => {
  if (!confirm('Mark this order as completed?')) return
  
  saving.value = true
  try {
    await specialOrdersAPI.completeOrder(order.id)
    showMessage('Order marked as completed', true)
    await loadOrders()
    if (viewingOrder.value?.id === order.id) {
      viewingOrder.value = null
    }
  } catch (error) {
    showMessage('Failed to complete order: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const viewInstallment = (installment) => {
  viewingInstallment.value = installment
  showInstallmentModal.value = true
}

const viewOrderFromInstallment = async (installment) => {
  if (!installment.special_order?.id) return
  
  try {
    const res = await specialOrdersAPI.get(installment.special_order.id)
    viewingOrder.value = res.data
    // Switch to orders tab to show the order
    activeTab.value = 'orders'
  } catch (error) {
    showMessage('Failed to load order: ' + (error.response?.data?.detail || error.message), false)
  }
}

const markInstallmentPaid = async (installment) => {
  if (!confirm('Mark this installment as paid?')) return
  
  saving.value = true
  try {
    // Update installment to mark as paid
    await specialOrdersAPI.updateInstallment(installment.id, {
      is_paid: true,
    })
    showMessage('Installment marked as paid', true)
    await loadInstallments()
    if (viewingInstallment.value?.id === installment.id) {
      viewingInstallment.value = null
      showInstallmentModal.value = false
    }
  } catch (error) {
    showMessage('Failed to mark installment as paid: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    saving.value = false
  }
}

const editEstimatedSetting = (setting) => {
  editingEstimatedSetting.value = setting
  estimatedSettingForm.value = {
    website: typeof setting.website === 'object' ? setting.website?.id : setting.website_id || setting.website,
    default_deposit_percentage: parseFloat(setting.default_deposit_percentage || 50.0),
  }
  showEstimatedSettingModal.value = true
}

const saveEstimatedSetting = async () => {
  saving.value = true
  try {
    const data = {
      website: estimatedSettingForm.value.website,
      default_deposit_percentage: estimatedSettingForm.value.default_deposit_percentage,
    }
    
    if (editingEstimatedSetting.value && editingEstimatedSetting.value.id) {
      // Update existing
      await specialOrdersAPI.updateEstimatedSettings(editingEstimatedSetting.value.id, data)
      showMessage('Estimated setting updated successfully', true)
    } else {
      // Create new
      await specialOrdersAPI.createEstimatedSettings(data)
      showMessage('Estimated setting created successfully', true)
    }
    
    showEstimatedSettingModal.value = false
    editingEstimatedSetting.value = null
    await loadEstimatedSettings()
  } catch (error) {
    console.error('Error saving estimated setting:', error)
    showMessage('Failed to save setting: ' + (error.response?.data?.detail || error.message || 'Unknown error'), false)
  } finally {
    saving.value = false
  }
}

const createNewEstimatedSetting = () => {
  editingEstimatedSetting.value = null
  estimatedSettingForm.value = {
    website: null,
    default_deposit_percentage: 50.0,
  }
  showEstimatedSettingModal.value = true
}

const closeEstimatedSettingModal = () => {
  showEstimatedSettingModal.value = false
  editingEstimatedSetting.value = null
  estimatedSettingForm.value = {
    website: null,
    default_deposit_percentage: 50.0,
  }
}

const isOverdue = (dueDate) => {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return due < today
}

const viewInstallmentsForOrder = async (order) => {
  try {
    const res = await specialOrdersAPI.listInstallments({ special_order: order.id })
    installments.value = res.data.results || res.data || []
    activeTab.value = 'installments'
    // Update filters to show this order's installments
    installmentFilters.value.order_id = order.id.toString()
  } catch (error) {
    showMessage('Failed to load installments: ' + (error.response?.data?.detail || error.message), false)
  }
}

const editConfig = async (config) => {
  editingConfig.value = config
  
  // Load full config details including durations
  try {
    const res = await specialOrdersAPI.getPredefinedConfig(config.id)
    const fullConfig = res.data
    
    // Load durations
    const durationsRes = await specialOrdersAPI.listDurations({ predefined_order: config.id })
    const durations = durationsRes.data.results || durationsRes.data || []
    
    configForm.value = {
      name: fullConfig.name || '',
      description: fullConfig.description || '',
      website: typeof fullConfig.website === 'object' ? fullConfig.website?.id : fullConfig.website || null,
      is_active: fullConfig.is_active !== false,
      durations: durations.map(d => ({
        id: d.id,
        duration_days: d.duration_days,
        price: parseFloat(d.price || 0),
      })),
    }
    
    showConfigModal.value = true
  } catch (error) {
    showMessage('Failed to load config details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const addDuration = () => {
  configForm.value.durations.push({
    duration_days: 1,
    price: 0,
  })
}

const removeDuration = (index) => {
  configForm.value.durations.splice(index, 1)
}

const createNewConfig = () => {
  editingConfig.value = null
  configForm.value = {
    name: '',
    description: '',
    website: null,
    is_active: true,
    durations: [],
  }
  showConfigModal.value = true
}

const closeConfigModal = () => {
  showConfigModal.value = false
  editingConfig.value = null
  configForm.value = {
    name: '',
    description: '',
    website: null,
    is_active: true,
    durations: [],
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    // Prepare config data (without durations)
    const configData = {
      name: configForm.value.name,
      description: configForm.value.description,
      website: configForm.value.website,
      is_active: configForm.value.is_active,
    }
    
    let configId
    
    if (editingConfig.value) {
      // Update existing config
      const res = await specialOrdersAPI.updatePredefinedConfig(editingConfig.value.id, configData)
      configId = res.data.id
    } else {
      // Create new config
      const res = await specialOrdersAPI.createPredefinedConfig(configData)
      configId = res.data.id
    }
    
    // Handle durations
    // First, get existing durations to know which to delete
    const existingDurationsRes = await specialOrdersAPI.listDurations({ predefined_order: configId })
    const existingDurations = existingDurationsRes.data.results || existingDurationsRes.data || []
    const existingDurationIds = new Set(existingDurations.map(d => d.id))
    const newDurationIds = new Set(configForm.value.durations.filter(d => d.id).map(d => d.id))
    
    // Delete durations that were removed
    for (const existing of existingDurations) {
      if (!newDurationIds.has(existing.id)) {
        try {
          await specialOrdersAPI.deleteDuration(existing.id)
        } catch (err) {
          console.warn(`Failed to delete duration ${existing.id}:`, err)
        }
      }
    }
    
    // Create or update durations
    for (const duration of configForm.value.durations) {
      const durationData = {
        predefined_order: configId,
        website: configForm.value.website,
        duration_days: duration.duration_days,
        price: duration.price,
      }
      
      if (duration.id) {
        // Update existing duration
        await specialOrdersAPI.updateDuration(duration.id, durationData)
      } else {
        // Create new duration
        await specialOrdersAPI.createDuration(durationData)
      }
    }
    
    showMessage(editingConfig.value ? 'Configuration updated successfully' : 'Configuration created successfully', true)
    closeConfigModal()
    await loadConfigs()
  } catch (error) {
    console.error('Error saving config:', error)
    showMessage('Failed to save configuration: ' + (error.response?.data?.detail || error.message || 'Unknown error'), false)
  } finally {
    saving.value = false
  }
}

const deleteConfig = async (id) => {
  if (!confirm('Delete this configuration?')) return
  
  try {
    await specialOrdersAPI.deletePredefinedConfig(id)
    showMessage('Configuration deleted', true)
    await loadConfigs()
  } catch (error) {
    showMessage('Failed to delete configuration: ' + (error.response?.data?.detail || error.message), false)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    order_type: '',
    search: '',
    website: '',
  }
  loadOrders()
}

const getStatusClass = (status) => {
  const classes = {
    inquiry: 'bg-gray-100 text-gray-800',
    awaiting_approval: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status) => {
  const labels = {
    inquiry: 'Inquiry',
    awaiting_approval: 'Awaiting Approval',
    in_progress: 'In Progress',
    completed: 'Completed',
  }
  return labels[status] || status
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
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

watch(activeTab, (newTab) => {
  if (newTab === 'orders') {
    loadOrders()
  } else if (newTab === 'installments') {
    loadInstallments()
  } else if (newTab === 'configs') {
    loadConfigs()
  } else if (newTab === 'installment-settings') {
    loadEstimatedSettings()
  }
})

onMounted(async () => {
  console.log('SpecialOrderManagement mounted, loading data...')
  try {
    await Promise.all([
      loadDashboard(),
      loadWebsites().catch(err => console.warn('Failed to load websites:', err)),
      loadOrders()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error in onMounted:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

