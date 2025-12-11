<template>
  <div class="space-y-6 p-6" v-if="!componentError && !initialLoading">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Class Management</h1>
        <p class="mt-2 text-gray-600">Manage class bundles, installments, and configurations</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Create Manual Bundle
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Bundles</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Not Started</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.not_started || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Completed</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.completed || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Exhausted</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.exhausted || 0 }}</p>
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
        </button>
      </nav>
    </div>

    <!-- Bundles Tab -->
    <div v-if="activeTab === 'bundles'" class="space-y-4">
      <!-- Filters -->
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="filters.status" @change="loadBundles" class="w-full border rounded px-3 py-2">
              <option value="">All Statuses</option>
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="exhausted">Exhausted</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Pricing Source</label>
            <select v-model="filters.pricing_source" @change="loadBundles" class="w-full border rounded px-3 py-2">
              <option value="">All Sources</option>
              <option value="config">From Config</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Search</label>
            <input
              v-model="filters.search"
              @input="debouncedSearch"
              type="text"
              placeholder="Bundle ID, client..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website</label>
            <select v-model="filters.website" @change="loadBundles" class="w-full border rounded px-3 py-2">
              <option value="">All Websites</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <!-- Bundles Table -->
      <div class="card overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Writer</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classes</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Price</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deposit</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="bundle in bundles" :key="bundle.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ bundle.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ bundle.client?.username || bundle.client?.email || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span v-if="bundle.assigned_writer">
                    {{ bundle.assigned_writer?.username || 'N/A' }}
                  </span>
                  <button v-else @click="openAssignWriterModal(bundle)" class="text-blue-600 hover:underline text-xs">
                    Assign
                  </button>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(bundle.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(bundle.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ bundle.number_of_classes || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(bundle.total_price || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div class="flex flex-col">
                    <span>${{ parseFloat(bundle.deposit_paid || 0).toFixed(2) }} / ${{ parseFloat(bundle.deposit_required || 0).toFixed(2) }}</span>
                    <span v-if="bundle.deposit_paid < bundle.deposit_required" class="text-xs text-red-600">Unpaid</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(bundle.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center gap-2">
                    <button @click="viewBundle(bundle)" class="text-blue-600 hover:underline">View</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!loading && bundles.length === 0" class="text-center py-12 text-gray-500">
          <p>No bundles found</p>
        </div>
      </div>
    </div>

    <!-- Installments Tab -->
    <div v-if="activeTab === 'installments'" class="space-y-4">
      <div class="card p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Bundle ID</label>
            <input
              v-model.number="installmentFilters.bundle_id"
              @input="debouncedInstallmentSearch"
              type="number"
              placeholder="Filter by bundle ID"
              class="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="installmentFilters.is_paid" @change="loadInstallments" class="w-full border rounded px-3 py-2">
              <option value="">All</option>
              <option value="true">Paid</option>
              <option value="false">Unpaid</option>
            </select>
          </div>
          <div class="flex items-end">
            <button @click="resetInstallmentFilters" class="btn btn-secondary w-full">Reset</button>
          </div>
        </div>
      </div>

      <div class="card overflow-hidden">
        <div v-if="installmentsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bundle ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Paid Date</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="installment in installments" :key="installment.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ installment.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  #{{ installment.class_bundle?.id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(installment.amount || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ formatDate(installment.due_date) }}
                  <span v-if="isOverdue(installment.due_date) && !installment.is_paid" class="ml-2 text-xs text-red-600">⚠️ Overdue</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ installment.paid_at ? formatDateTime(installment.paid_at) : 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="installment.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                        class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ installment.is_paid ? 'Paid' : 'Pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button @click="viewBundleFromInstallment(installment)" class="text-blue-600 hover:underline">View Bundle</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Configs Tab -->
    <div v-if="activeTab === 'configs'" class="space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">Bundle Configurations</h3>
        <button @click="openConfigModal()" class="btn btn-primary">➕ Add Config</button>
      </div>

      <div class="card overflow-hidden">
        <div v-if="configsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Level</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bundle Size</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in configs" :key="config.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ config.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ config.name || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ config.level || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ config.duration || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{{ config.bundle_size || 'N/A' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ parseFloat(config.price || 0).toFixed(2) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ config.website?.name || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex items-center gap-2">
                    <button @click="editConfig(config)" class="text-blue-600 hover:underline">Edit</button>
                    <button @click="deleteConfig(config)" class="text-red-600 hover:underline">Delete</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Bundle Detail Modal -->
    <div v-if="viewingBundle" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-5xl w-full my-auto max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">Class Bundle #{{ viewingBundle.id }}</h2>
            <button @click="viewingBundle = null" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Bundle Information</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Client:</span> {{ viewingBundle.client?.username || 'N/A' }}</div>
                <div><span class="font-medium text-gray-600">Writer:</span> 
                  <span v-if="viewingBundle.assigned_writer">
                    {{ viewingBundle.assigned_writer?.username || 'N/A' }}
                  </span>
                  <button v-else @click="openAssignWriterModal(viewingBundle)" class="text-blue-600 hover:underline text-xs">
                    Assign Writer
                  </button>
                </div>
                <div><span class="font-medium text-gray-600">Status:</span> 
                  <span :class="getStatusClass(viewingBundle.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ getStatusLabel(viewingBundle.status) }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Pricing Source:</span> 
                  <span :class="viewingBundle.pricing_source === 'config' ? 'text-blue-600' : 'text-purple-600'">
                    {{ viewingBundle.pricing_source === 'config' ? 'From Config' : 'Manual' }}
                  </span>
                </div>
                <div><span class="font-medium text-gray-600">Number of Classes:</span> {{ viewingBundle.number_of_classes || 0 }}</div>
                <div><span class="font-medium text-gray-600">Total Price:</span> ${{ parseFloat(viewingBundle.total_price || 0).toFixed(2) }}</div>
                <div><span class="font-medium text-gray-600">Deposit Required:</span> ${{ parseFloat(viewingBundle.deposit_required || 0).toFixed(2) }}</div>
                <div><span class="font-medium text-gray-600">Deposit Paid:</span> ${{ parseFloat(viewingBundle.deposit_paid || 0).toFixed(2) }}</div>
                <div><span class="font-medium text-gray-600">Balance Remaining:</span> ${{ parseFloat(viewingBundle.balance_remaining || 0).toFixed(2) }}</div>
              </div>
            </div>
            <div class="space-y-4">
              <h3 class="text-lg font-semibold border-b pb-2">Timeline</h3>
              <div class="space-y-2 text-sm">
                <div><span class="font-medium text-gray-600">Created:</span> {{ formatDateTime(viewingBundle.created_at) }}</div>
                <div><span class="font-medium text-gray-600">Updated:</span> {{ formatDateTime(viewingBundle.updated_at) }}</div>
                <div v-if="viewingBundle.start_date"><span class="font-medium text-gray-600">Start Date:</span> {{ formatDate(viewingBundle.start_date) }}</div>
                <div v-if="viewingBundle.end_date"><span class="font-medium text-gray-600">End Date:</span> {{ formatDate(viewingBundle.end_date) }}</div>
                <div v-if="viewingBundle.installments_enabled">
                  <span class="font-medium text-gray-600">Installments:</span> 
                  {{ viewingBundle.installment_count || 0 }} installments enabled
                </div>
              </div>
            </div>
          </div>

          <!-- Installments Section -->
          <div v-if="viewingBundle.installments && viewingBundle.installments.length > 0" class="mb-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold border-b pb-2 flex-1">Installments</h3>
              <button v-if="!viewingBundle.installments_enabled" @click="openInstallmentConfigModal(viewingBundle)" class="btn btn-sm btn-primary">
                Configure Installments
              </button>
            </div>
            <div class="space-y-3">
              <div v-for="installment in viewingBundle.installments" :key="installment.id" class="p-3 bg-gray-50 rounded border">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <div class="flex items-center gap-4 text-sm">
                      <span class="font-medium">Installment #{{ installment.installment_number || 'N/A' }}</span>
                      <span class="font-medium">${{ parseFloat(installment.amount || 0).toFixed(2) }}</span>
                      <span class="text-gray-600">Due: {{ formatDate(installment.due_date) }}</span>
                      <span v-if="installment.paid_at" class="text-gray-600">Paid: {{ formatDateTime(installment.paid_at) }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span :class="installment.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" 
                          class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ installment.is_paid ? 'Paid' : 'Pending' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button v-if="viewingBundle.deposit_paid < viewingBundle.deposit_required" @click="openDepositPaymentModal(viewingBundle)" class="btn btn-primary bg-green-600 hover:bg-green-700">
              Process Deposit Payment
            </button>
            <button v-if="!viewingBundle.installments_enabled && viewingBundle.installments?.length === 0" @click="openInstallmentConfigModal(viewingBundle)" class="btn btn-primary bg-purple-600 hover:bg-purple-700">
              Configure Installments
            </button>
            <button @click="showBundleThreadsModal = true" class="btn btn-primary bg-blue-600 hover:bg-blue-700">
              💬 View Messages
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Threads Modal -->
    <ClassMessageThreads
      v-if="viewingBundle"
      :show="showBundleThreadsModal"
      :class-id="viewingBundle.id"
      class-type="bundle"
      @close="showBundleThreadsModal = false"
    />
            <button @click="openEditBundleModal(viewingBundle)" class="btn btn-secondary">Edit</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Manual Bundle Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Create Manual Bundle</h3>
          <button @click="closeCreateModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Client *</label>
            <input v-model="createForm.client_id" type="number" placeholder="Client ID" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website *</label>
            <select v-model="createForm.website_id" class="w-full border rounded px-3 py-2">
              <option value="">Select website...</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Number of Classes *</label>
            <input v-model.number="createForm.number_of_classes" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Total Price *</label>
            <input v-model.number="createForm.total_price" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Deposit Required</label>
            <input v-model.number="createForm.deposit_required" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Level</label>
            <input v-model="createForm.level" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Duration</label>
            <input v-model="createForm.duration" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Start Date</label>
            <input v-model="createForm.start_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">End Date</label>
            <input v-model="createForm.end_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex items-center gap-2">
            <input v-model="createForm.installments_enabled" type="checkbox" id="installments_enabled" />
            <label for="installments_enabled" class="text-sm">Enable Installments</label>
          </div>
          <div v-if="createForm.installments_enabled">
            <label class="block text-sm font-medium mb-1">Installment Count</label>
            <input v-model.number="createForm.installment_count" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveCreateBundle" class="btn btn-primary flex-1">Create Bundle</button>
            <button @click="closeCreateModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Installment Configuration Modal -->
    <div v-if="showInstallmentConfigModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-md w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Configure Installments</h3>
          <button @click="closeInstallmentConfigModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Installment Count *</label>
            <input v-model.number="installmentConfigForm.installment_count" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Interval (weeks)</label>
            <input v-model.number="installmentConfigForm.interval_weeks" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveInstallmentConfig" class="btn btn-primary flex-1">Save</button>
            <button @click="closeInstallmentConfigModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Deposit Payment Modal -->
    <div v-if="showDepositPaymentModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-md w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Process Deposit Payment</h3>
          <button @click="closeDepositPaymentModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Payment Method *</label>
            <select v-model="depositPaymentForm.payment_method" class="w-full border rounded px-3 py-2">
              <option value="wallet">Wallet</option>
              <option value="stripe">Stripe</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Discount Code (optional)</label>
            <input v-model="depositPaymentForm.discount_code" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="processDepositPayment" class="btn btn-primary flex-1">Process Payment</button>
            <button @click="closeDepositPaymentModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign Writer Modal -->
    <div v-if="showAssignWriterModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-3xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Assign Writer to Bundle #{{ currentBundleForAction?.id }}</h3>
          <button @click="closeAssignWriterModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        
        <div v-if="currentBundleForAction" class="mb-4 p-4 bg-gray-50 rounded">
          <p class="text-sm text-gray-600">
            <strong>Client:</strong> {{ currentBundleForAction.client?.username || currentBundleForAction.client?.email || 'N/A' }}<br>
            <strong>Classes:</strong> {{ currentBundleForAction.number_of_classes || 0 }}<br>
            <strong>Status:</strong> {{ getStatusLabel(currentBundleForAction.status) }}
          </p>
        </div>
        
        <div v-if="writersLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading available writers...</span>
        </div>
        
        <div v-else-if="availableWriters.length === 0" class="text-center py-12 text-gray-500">
          <p>No available writers found</p>
        </div>
        
        <div v-else class="space-y-3">
          <div class="mb-4">
            <input
              v-model="writerSearchQuery"
              type="text"
              placeholder="Search writers by name, email, or username..."
              class="w-full border rounded px-3 py-2"
            />
          </div>
          
          <div class="max-h-96 overflow-y-auto space-y-2">
            <div
              v-for="writer in filteredWriters"
              :key="writer.id"
              class="p-4 border rounded hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{ 'bg-blue-50 border-blue-300': selectedWriterId === writer.id }"
              @click="selectedWriterId = writer.id"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <input
                      type="radio"
                      :id="`writer-${writer.id}`"
                      :value="writer.id"
                      v-model="selectedWriterId"
                      class="cursor-pointer"
                    />
                    <label :for="`writer-${writer.id}`" class="cursor-pointer flex-1">
                      <div class="font-medium text-gray-900">
                        {{ writer.username || writer.email || `Writer #${writer.id}` }}
                      </div>
                      <div class="text-sm text-gray-600 mt-1">
                        <span v-if="writer.email">{{ writer.email }}</span>
                        <span v-if="writer.writer_profile">
                          <span v-if="writer.writer_profile.rating">
                            ⭐ {{ parseFloat(writer.writer_profile.rating).toFixed(1) }}
                          </span>
                          <span v-if="writer.active_orders !== undefined" class="ml-2">
                            Active Orders: {{ writer.active_orders }}
                          </span>
                        </span>
                      </div>
                    </label>
                  </div>
                </div>
                <button
                  @click.stop="assignWriter(writer.id)"
                  :disabled="assigningWriter"
                  class="btn btn-primary btn-sm"
                >
                  {{ assigningWriter ? 'Assigning...' : 'Assign' }}
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex gap-2 pt-4 border-t mt-4">
          <button
            @click="selectedWriterId && assignWriter(selectedWriterId)"
            :disabled="!selectedWriterId || assigningWriter"
            class="btn btn-primary flex-1"
          >
            {{ assigningWriter ? 'Assigning...' : 'Assign Selected Writer' }}
          </button>
          <button @click="closeAssignWriterModal" class="btn btn-secondary flex-1">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit Bundle Modal -->
    <div v-if="showEditBundleModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">Edit Bundle #{{ editingBundle?.id }}</h3>
          <button @click="closeEditBundleModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        
        <div v-if="editingBundle" class="mb-4 p-4 bg-gray-50 rounded">
          <p class="text-sm text-gray-600">
            <strong>Client:</strong> {{ editingBundle.client?.username || editingBundle.client?.email || 'N/A' }}<br>
            <strong>Website:</strong> {{ editingBundle.website?.name || 'N/A' }}<br>
            <strong>Pricing Source:</strong> {{ editingBundle.pricing_source === 'config' ? 'From Config' : 'Manual' }}
          </p>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Number of Classes *</label>
            <input v-model.number="editBundleForm.number_of_classes" type="number" min="1" class="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Total Price *</label>
            <input v-model.number="editBundleForm.total_price" type="number" step="0.01" min="0" class="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Deposit Required</label>
            <input v-model.number="editBundleForm.deposit_required" type="number" step="0.01" min="0" :max="editBundleForm.total_price" class="w-full border rounded px-3 py-2" />
            <p class="text-xs text-gray-500 mt-1">Cannot exceed total price</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select v-model="editBundleForm.status" class="w-full border rounded px-3 py-2">
              <option value="not_started">Not Started</option>
              <option value="in_progress">In Progress</option>
              <option value="exhausted">Exhausted</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Level</label>
            <input v-model="editBundleForm.level" type="text" class="w-full border rounded px-3 py-2" placeholder="e.g., Beginner, Intermediate, Advanced" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Duration</label>
            <input v-model="editBundleForm.duration" type="text" class="w-full border rounded px-3 py-2" placeholder="e.g., 3 months, 6 weeks" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Start Date</label>
            <input v-model="editBundleForm.start_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">End Date</label>
            <input v-model="editBundleForm.end_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex items-center gap-2">
            <input v-model="editBundleForm.installments_enabled" type="checkbox" id="edit_installments_enabled" />
            <label for="edit_installments_enabled" class="text-sm">Enable Installments</label>
          </div>
          <div v-if="editBundleForm.installments_enabled">
            <label class="block text-sm font-medium mb-1">Installment Count</label>
            <input v-model.number="editBundleForm.installment_count" type="number" min="1" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-2 pt-4 border-t">
            <button @click="saveEditBundle" class="btn btn-primary flex-1">Save Changes</button>
            <button @click="closeEditBundleModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Config Modal -->
    <div v-if="showConfigModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-2xl w-full my-auto p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">{{ editingConfig ? 'Edit' : 'Create' }} Bundle Config</h3>
          <button @click="closeConfigModal" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Name *</label>
            <input v-model="configForm.name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Website *</label>
            <select v-model="configForm.website_id" class="w-full border rounded px-3 py-2">
              <option value="">Select website...</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Level</label>
            <input v-model="configForm.level" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Duration</label>
            <input v-model="configForm.duration" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Bundle Size</label>
            <input v-model.number="configForm.bundle_size" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Price *</label>
            <input v-model.number="configForm.price" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div class="flex gap-2 pt-4">
            <button @click="saveConfig" class="btn btn-primary flex-1">Save</button>
            <button @click="closeConfigModal" class="btn btn-secondary flex-1">Cancel</button>
          </div>
        </div>
      </div>
    </div>

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
import { ref, computed, onMounted } from 'vue'
import { classManagementAPI, usersAPI, writerAssignmentAPI } from '@/api'
import apiClient from '@/api/client'

const componentError = ref(null)
const initialLoading = ref(true)
const loading = ref(false)
const installmentsLoading = ref(false)
const configsLoading = ref(false)
const bundles = ref([])
const installments = ref([])
const configs = ref([])
const websites = ref([])
const viewingBundle = ref(null)
const showCreateModal = ref(false)
const showInstallmentConfigModal = ref(false)
const showDepositPaymentModal = ref(false)
const showConfigModal = ref(false)
const showAssignWriterModal = ref(false)
const availableWriters = ref([])
const writersLoading = ref(false)
const assigningWriter = ref(false)
const selectedWriterId = ref(null)
const writerSearchQuery = ref('')

const filteredWriters = computed(() => {
  if (!writerSearchQuery.value) return availableWriters.value
  
  const query = writerSearchQuery.value.toLowerCase()
  return availableWriters.value.filter(writer => {
    const username = (writer.username || '').toLowerCase()
    const email = (writer.email || '').toLowerCase()
    const fullName = (writer.full_name || writer.get_full_name || '').toLowerCase()
    return username.includes(query) || email.includes(query) || fullName.includes(query)
  })
})
const showBundleThreadsModal = ref(false)
const showEditBundleModal = ref(false)
const editingBundle = ref(null)
const editingConfig = ref(null)
const currentBundleForAction = ref(null)

const activeTab = ref('bundles')
const tabs = [
  { id: 'bundles', label: 'Bundles' },
  { id: 'installments', label: 'Installments' },
  { id: 'configs', label: 'Configurations' },
]

const filters = ref({
  status: '',
  pricing_source: '',
  search: '',
  website: '',
})

const installmentFilters = ref({
  bundle_id: '',
  is_paid: '',
})

const stats = ref({
  total: 0,
  in_progress: 0,
  not_started: 0,
  completed: 0,
  exhausted: 0,
})

const createForm = ref({
  client_id: '',
  website_id: '',
  number_of_classes: 0,
  total_price: 0,
  deposit_required: 0,
  level: '',
  duration: '',
  start_date: '',
  end_date: '',
  installments_enabled: false,
  installment_count: 0,
})

const editBundleForm = ref({
  number_of_classes: 0,
  total_price: 0,
  deposit_required: 0,
  level: '',
  duration: '',
  start_date: '',
  end_date: '',
  status: 'in_progress',
  installments_enabled: false,
  installment_count: 0,
})

const installmentConfigForm = ref({
  installment_count: 0,
  interval_weeks: 2,
})

const depositPaymentForm = ref({
  payment_method: 'wallet',
  discount_code: '',
})

const editBundleForm = ref({
  number_of_classes: 0,
  total_price: 0,
  deposit_required: 0,
  level: '',
  duration: '',
  start_date: '',
  end_date: '',
  status: 'in_progress',
  installments_enabled: false,
  installment_count: 0,
})

const configForm = ref({
  name: '',
  website_id: '',
  level: '',
  duration: '',
  bundle_size: 0,
  price: 0,
})

const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null
let installmentSearchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadBundles()
  }, 500)
}

const debouncedInstallmentSearch = () => {
  clearTimeout(installmentSearchTimeout)
  installmentSearchTimeout = setTimeout(() => {
    loadInstallments()
  }, 500)
}

const loadBundles = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.pricing_source) params.pricing_source = filters.value.pricing_source
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website

    const res = await classManagementAPI.listBundles(params)
    bundles.value = res.data.results || res.data || []
    
    // Calculate stats
    stats.value.total = bundles.value.length
    stats.value.in_progress = bundles.value.filter(b => b.status === 'in_progress').length
    stats.value.not_started = bundles.value.filter(b => b.status === 'not_started').length
    stats.value.completed = bundles.value.filter(b => b.status === 'completed').length
    stats.value.exhausted = bundles.value.filter(b => b.status === 'exhausted').length
  } catch (error) {
    console.error('Error loading bundles:', error)
    showMessage('Failed to load bundles: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    loading.value = false
  }
}


const loadInstallments = async () => {
  installmentsLoading.value = true
  try {
    const params = {}
    if (installmentFilters.value.bundle_id) params.bundle = installmentFilters.value.bundle_id
    if (installmentFilters.value.is_paid) params.is_paid = installmentFilters.value.is_paid === 'true'

    const res = await classManagementAPI.listInstallments(params)
    installments.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading installments:', error)
    showMessage('Failed to load installments: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    installmentsLoading.value = false
  }
}

const loadConfigs = async () => {
  configsLoading.value = true
  try {
    const res = await classManagementAPI.listConfigs()
    configs.value = res.data.results || res.data || []
  } catch (error) {
    // Only log and show message if it's not a 404 (endpoint doesn't exist)
    if (error?.response?.status !== 404) {
      console.error('Error loading configs:', error)
      showMessage('Failed to load configs: ' + (error.response?.data?.detail || error.message), false)
    }
    configs.value = []
  } finally {
    configsLoading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    websites.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading websites:', error)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    pricing_source: '',
    search: '',
    website: '',
  }
  loadBundles()
}

const resetInstallmentFilters = () => {
  installmentFilters.value = {
    bundle_id: '',
    is_paid: '',
  }
  loadInstallments()
}

const viewBundle = async (bundle) => {
  try {
    const res = await classManagementAPI.getBundle(bundle.id)
    viewingBundle.value = res.data
  } catch (error) {
    console.error('Error loading bundle:', error)
    showMessage('Failed to load bundle details: ' + (error.response?.data?.detail || error.message), false)
  }
}

const viewBundleFromInstallment = async (installment) => {
  try {
    const res = await classManagementAPI.getBundle(installment.class_bundle)
    viewingBundle.value = res.data
  } catch (error) {
    console.error('Error loading bundle:', error)
    showMessage('Failed to load bundle: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  createForm.value = {
    client_id: '',
    website_id: '',
    number_of_classes: 0,
    total_price: 0,
    deposit_required: 0,
    level: '',
    duration: '',
    start_date: '',
    end_date: '',
    installments_enabled: false,
    installment_count: 0,
  }
}

const saveCreateBundle = async () => {
  try {
    const data = { ...createForm.value }
    if (data.start_date) data.start_date = new Date(data.start_date).toISOString().split('T')[0]
    if (data.end_date) data.end_date = new Date(data.end_date).toISOString().split('T')[0]
    
    await classManagementAPI.createManualBundle(data)
    showMessage('Bundle created successfully', true)
    closeCreateModal()
    loadBundles()
  } catch (error) {
    showMessage('Failed to create bundle: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openInstallmentConfigModal = (bundle) => {
  currentBundleForAction.value = bundle
  installmentConfigForm.value = {
    installment_count: bundle.installment_count || 0,
    interval_weeks: 2,
  }
  showInstallmentConfigModal.value = true
}

const closeInstallmentConfigModal = () => {
  showInstallmentConfigModal.value = false
  currentBundleForAction.value = null
  installmentConfigForm.value = {
    installment_count: 0,
    interval_weeks: 2,
  }
}

const saveInstallmentConfig = async () => {
  if (!currentBundleForAction.value) return
  
  try {
    await classManagementAPI.configureInstallments(currentBundleForAction.value.id, installmentConfigForm.value)
    showMessage('Installments configured successfully', true)
    closeInstallmentConfigModal()
    if (viewingBundle.value && viewingBundle.value.id === currentBundleForAction.value.id) {
      await viewBundle(currentBundleForAction.value)
    }
    loadBundles()
  } catch (error) {
    showMessage('Failed to configure installments: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openDepositPaymentModal = (bundle) => {
  currentBundleForAction.value = bundle
  depositPaymentForm.value = {
    payment_method: 'wallet',
    discount_code: '',
  }
  showDepositPaymentModal.value = true
}

const closeDepositPaymentModal = () => {
  showDepositPaymentModal.value = false
  currentBundleForAction.value = null
  depositPaymentForm.value = {
    payment_method: 'wallet',
    discount_code: '',
  }
}

const processDepositPayment = async () => {
  if (!currentBundleForAction.value) return
  
  try {
    await classManagementAPI.payDeposit(currentBundleForAction.value.id, depositPaymentForm.value)
    showMessage('Deposit payment processed successfully', true)
    closeDepositPaymentModal()
    if (viewingBundle.value && viewingBundle.value.id === currentBundleForAction.value.id) {
      await viewBundle(currentBundleForAction.value)
    }
    loadBundles()
  } catch (error) {
    showMessage('Failed to process deposit payment: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openConfigModal = (config = null) => {
  editingConfig.value = config
  if (config) {
    configForm.value = {
      name: config.name || '',
      website_id: config.website?.id || '',
      level: config.level || '',
      duration: config.duration || '',
      bundle_size: config.bundle_size || 0,
      price: config.price || 0,
    }
  } else {
    configForm.value = {
      name: '',
      website_id: '',
      level: '',
      duration: '',
      bundle_size: 0,
      price: 0,
    }
  }
  showConfigModal.value = true
}

const closeConfigModal = () => {
  showConfigModal.value = false
  editingConfig.value = null
  configForm.value = {
    name: '',
    website_id: '',
    level: '',
    duration: '',
    bundle_size: 0,
    price: 0,
  }
}

const saveConfig = async () => {
  try {
    if (editingConfig.value) {
      await classManagementAPI.updateConfig(editingConfig.value.id, configForm.value)
      showMessage('Config updated successfully', true)
    } else {
      await classManagementAPI.createConfig(configForm.value)
      showMessage('Config created successfully', true)
    }
    closeConfigModal()
    loadConfigs()
  } catch (error) {
    showMessage('Failed to save config: ' + (error.response?.data?.detail || error.message), false)
  }
}

const editConfig = (config) => {
  openConfigModal(config)
}

const deleteConfig = async (config) => {
  if (!confirm('Are you sure you want to delete this config?')) return
  
  try {
    await classManagementAPI.deleteConfig(config.id)
    showMessage('Config deleted successfully', true)
    loadConfigs()
  } catch (error) {
    showMessage('Failed to delete config: ' + (error.response?.data?.detail || error.message), false)
  }
}

const openAssignWriterModal = async (bundle) => {
  currentBundleForAction.value = bundle
  showAssignWriterModal.value = true
  await loadAvailableWriters()
}

const closeAssignWriterModal = () => {
  showAssignWriterModal.value = false
  currentBundleForAction.value = null
  availableWriters.value = []
  selectedWriterId.value = null
  writerSearchQuery.value = ''
}

const loadAvailableWriters = async () => {
  writersLoading.value = true
  try {
    const response = await writerAssignmentAPI.getAvailableWriters()
    availableWriters.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load available writers:', error)
    showMessage('Failed to load available writers: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    writersLoading.value = false
  }
}

const assignWriter = async (writerId) => {
  if (!currentBundleForAction.value) return
  
  assigningWriter.value = true
  try {
    await classManagementAPI.updateBundle(currentBundleForAction.value.id, {
      assigned_writer: writerId
    })
    showMessage('Writer assigned successfully', true)
    closeAssignWriterModal()
    // Refresh bundles and viewing bundle if open
    await loadBundles()
    if (viewingBundle.value && viewingBundle.value.id === currentBundleForAction.value.id) {
      const updated = await classManagementAPI.getBundle(currentBundleForAction.value.id)
      viewingBundle.value = updated.data
    }
  } catch (error) {
    showMessage('Failed to assign writer: ' + (error.response?.data?.detail || error.message), false)
  } finally {
    assigningWriter.value = false
  }
}

const openEditBundleModal = (bundle) => {
  editingBundle.value = bundle
  editBundleForm.value = {
    number_of_classes: bundle.number_of_classes || 0,
    total_price: parseFloat(bundle.total_price || 0),
    deposit_required: parseFloat(bundle.deposit_required || 0),
    level: bundle.level || '',
    duration: bundle.duration || '',
    start_date: bundle.start_date ? new Date(bundle.start_date).toISOString().split('T')[0] : '',
    end_date: bundle.end_date ? new Date(bundle.end_date).toISOString().split('T')[0] : '',
    status: bundle.status || 'in_progress',
    installments_enabled: bundle.installments_enabled || false,
    installment_count: bundle.installment_count || 0,
  }
  showEditBundleModal.value = true
}

const closeEditBundleModal = () => {
  showEditBundleModal.value = false
  editingBundle.value = null
  editBundleForm.value = {
    number_of_classes: 0,
    total_price: 0,
    deposit_required: 0,
    level: '',
    duration: '',
    start_date: '',
    end_date: '',
    status: 'in_progress',
    installments_enabled: false,
    installment_count: 0,
  }
}

const saveEditBundle = async () => {
  if (!editingBundle.value) return
  
  try {
    const data = { ...editBundleForm.value }
    if (data.start_date) data.start_date = new Date(data.start_date).toISOString().split('T')[0]
    if (data.end_date) data.end_date = new Date(data.end_date).toISOString().split('T')[0]
    
    await classManagementAPI.updateBundle(editingBundle.value.id, data)
    showMessage('Bundle updated successfully', true)
    closeEditBundleModal()
    // Refresh bundles and viewing bundle if open
    await loadBundles()
    if (viewingBundle.value && viewingBundle.value.id === editingBundle.value.id) {
      const updated = await classManagementAPI.getBundle(editingBundle.value.id)
      viewingBundle.value = updated.data
    }
  } catch (error) {
    showMessage('Failed to update bundle: ' + (error.response?.data?.detail || error.message), false)
  }
}

const getStatusClass = (status) => {
  const classes = {
    'not_started': 'bg-gray-100 text-gray-800',
    'in_progress': 'bg-green-100 text-green-800',
    'exhausted': 'bg-red-100 text-red-800',
    'completed': 'bg-purple-100 text-purple-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status) => {
  return status ? status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown'
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const isOverdue = (dueDate) => {
  if (!dueDate) return false
  return new Date(dueDate) < new Date() && !dueDate.includes('T')
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

onMounted(async () => {
  try {
    await Promise.all([
      loadBundles(),
      loadInstallments(),
      loadConfigs(),
      loadWebsites()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing ClassManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

