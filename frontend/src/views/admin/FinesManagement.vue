<template>
  <!-- Loading State -->
  <div v-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="window.location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Main Content -->
  <div v-else class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Fines Management</h1>
        <p class="mt-2 text-gray-600">Manage fines, appeals, fine types, and lateness rules</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Total Fines</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.total_fines || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Appeals</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.pending_appeals || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Waived</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.waived_fines || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Amount</p>
        <p class="text-3xl font-bold text-blue-900">${{ stats.total_amount || '0.00' }}</p>
        <p class="text-xs text-blue-600 mt-1" v-if="stats.recent_count">
          {{ stats.recent_count }} recent (30d)
        </p>
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

    <!-- Fines Tab -->
    <div v-if="activeTab === 'fines'" class="space-y-4">
      <!-- Filters and Actions -->
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 flex-1 mr-4">
            <div>
              <label class="block text-sm font-medium mb-1">Order ID</label>
              <input
                v-model.number="filters.order_id"
                @input="debouncedSearch"
                type="number"
                placeholder="Filter by order ID"
                class="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Status</label>
              <select v-model="filters.status" @change="loadFines" class="w-full border rounded px-3 py-2">
                <option value="">All Statuses</option>
                <option value="issued">Issued</option>
                <option value="appealed">Appealed</option>
                <option value="waived">Waived</option>
                <option value="voided">Voided</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Fine Type</label>
              <select v-model="filters.fine_type" @change="loadFines" class="w-full border rounded px-3 py-2">
                <option value="">All Types</option>
                <option v-for="type in fineTypes" :key="type.id" :value="type.code">{{ type.name }}</option>
              </select>
            </div>
            <div class="flex items-end">
              <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
            </div>
          </div>
          <button @click="showIssueFineModal = true" class="btn btn-primary">Issue Fine</button>
        </div>
      </div>

      <!-- Fines Table -->
      <div class="card overflow-hidden">
        <div v-if="finesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issued</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="fine in fines" :key="fine.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ fine.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <router-link :to="`/orders/${fine.order}`" class="text-blue-600 hover:underline">
                  Order #{{ fine.order }}
                </router-link>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ fine.order?.assigned_writer?.username || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ fine.fine_type_config?.name || fine.fine_type || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">${{ fine.amount || '0.00' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(fine.status)">
                  {{ fine.status || 'issued' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(fine.issued_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="viewFine(fine)" class="text-blue-600 hover:text-blue-900">View</button>
                <button v-if="fine.status === 'issued'" @click="waiveFine(fine.id)" class="text-green-600 hover:text-green-900">Waive</button>
                <button v-if="fine.status === 'issued'" @click="voidFine(fine.id)" class="text-red-600 hover:text-red-900">Void</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!finesLoading && fines.length === 0" class="text-center py-12 text-gray-500">
          No fines found
        </div>
      </div>
    </div>

    <!-- Appeals Tab -->
    <div v-if="activeTab === 'appeals'" class="space-y-4">
      <div class="card overflow-hidden">
        <div v-if="appealsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fine</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Appealed By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="appeal in appeals" :key="appeal.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ appeal.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Fine #{{ appeal.fine }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ appeal.appealed_by?.username || 'N/A' }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ appeal.reason || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getAppealStatusBadgeClass(appeal.status)">
                  {{ appeal.status || 'pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(appeal.created_at) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="viewAppeal(appeal)" class="text-blue-600 hover:text-blue-900">View</button>
                <button v-if="appeal.status === 'pending'" @click="reviewAppeal(appeal.id)" class="text-green-600 hover:text-green-900">Review</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!appealsLoading && appeals.length === 0" class="text-center py-12 text-gray-500">
          No appeals found
        </div>
      </div>
    </div>

    <!-- Fine Types Tab -->
    <div v-if="activeTab === 'fine-types'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Fine Type Configurations</h3>
          <button @click="showFineTypeModal = true" class="btn btn-primary">Add Fine Type</button>
        </div>
        <div v-if="fineTypesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="type in fineTypes" :key="type.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ type.code }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ type.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span v-if="type.calculation_type === 'fixed'">${{ type.fixed_amount || '0.00' }}</span>
                <span v-else-if="type.calculation_type === 'percentage'">{{ type.percentage || '0' }}% of {{ type.base_amount === 'writer_compensation' ? 'Writer Comp' : 'Order Total' }}</span>
                <span v-else-if="type.calculation_type === 'progressive_hourly'">Progressive Hourly</span>
                <span v-else>N/A</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="type.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ type.active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="editFineType(type)" class="text-blue-600 hover:text-blue-900">Edit</button>
                <button @click="deleteFineType(type.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Lateness Rules Tab -->
    <div v-if="activeTab === 'lateness-rules'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Lateness Fine Rules</h3>
          <button @click="showLatenessRuleModal = true" class="btn btn-primary">Add Rule</button>
        </div>
        <div v-if="latenessRulesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Calculation Mode</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hourly Rates</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="rule in latenessRules" :key="rule.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ rule.website_domain || rule.website || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ rule.calculation_mode || 'cumulative' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ rule.first_hour_percentage || 0 }}% / {{ rule.second_hour_percentage || 0 }}% / {{ rule.third_hour_percentage || 0 }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="rule.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ rule.active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                <button @click="editLatenessRule(rule)" class="text-blue-600 hover:text-blue-900">Edit</button>
                <button @click="deleteLatenessRule(rule.id)" class="text-red-600 hover:text-red-900">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Issue Fine Modal -->
    <div v-if="showIssueFineModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">Issue Fine</h3>
            <button @click="closeIssueFineModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="submitIssueFine" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Order ID *</label>
              <input v-model.number="issueFineForm.order_id" type="number" required class="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Fine Type *</label>
              <select v-model="issueFineForm.fine_type_code" required class="w-full border rounded px-3 py-2">
                <option value="">Select Fine Type</option>
                <option v-for="type in fineTypes" :key="type.id" :value="type.code">{{ type.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Reason *</label>
              <textarea v-model="issueFineForm.reason" required class="w-full border rounded px-3 py-2" rows="3"></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Custom Amount (Optional)</label>
              <input v-model.number="issueFineForm.custom_amount" type="number" step="0.01" class="w-full border rounded px-3 py-2" placeholder="Override default amount" />
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeIssueFineModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="issuingFine">
                {{ issuingFine ? 'Issuing...' : 'Issue Fine' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Fine Type Modal -->
    <div v-if="showFineTypeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">{{ editingFineType ? 'Edit Fine Type' : 'Add Fine Type' }}</h3>
            <button @click="closeFineTypeModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="saveFineType" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Code *</label>
                <input
                  v-model="fineTypeForm.code"
                  type="text"
                  required
                  :disabled="editingFineType"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., quality_issue"
                />
                <p class="text-xs text-gray-500 mt-1">Unique identifier (cannot be changed after creation)</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  v-model="fineTypeForm.name"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., Quality Issue"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="fineTypeForm.description"
                class="w-full border rounded px-3 py-2"
                rows="2"
                placeholder="Description of when this fine applies"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Calculation Type *</label>
              <select v-model="fineTypeForm.calculation_type" required class="w-full border rounded px-3 py-2">
                <option value="fixed">Fixed Amount</option>
                <option value="percentage">Percentage of Base Amount</option>
                <option value="progressive_hourly">Progressive Hourly (Late Submission Only)</option>
              </select>
            </div>
            <div v-if="fineTypeForm.calculation_type === 'fixed'" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fixed Amount *</label>
                <input
                  v-model.number="fineTypeForm.fixed_amount"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div v-if="fineTypeForm.calculation_type === 'percentage'" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Percentage *</label>
                <input
                  v-model.number="fineTypeForm.percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Base Amount</label>
                <select v-model="fineTypeForm.base_amount" class="w-full border rounded px-3 py-2">
                  <option value="writer_compensation">Writer Compensation</option>
                  <option value="total_price">Order Total Price</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Min Amount</label>
                <input
                  v-model.number="fineTypeForm.min_amount"
                  type="number"
                  step="0.01"
                  class="w-full border rounded px-3 py-2"
                  placeholder="Optional"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Max Amount</label>
                <input
                  v-model.number="fineTypeForm.max_amount"
                  type="number"
                  step="0.01"
                  class="w-full border rounded px-3 py-2"
                  placeholder="Optional"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
              <select v-model="fineTypeForm.website" class="w-full border rounded px-3 py-2">
                <option value="">All Websites (Global)</option>
                <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
            </div>
            <div class="flex items-center">
              <input
                v-model="fineTypeForm.active"
                type="checkbox"
                id="fine_type_active"
                class="mr-2"
              />
              <label for="fine_type_active" class="text-sm font-medium text-gray-700">Active</label>
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeFineTypeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingFineType">
                {{ savingFineType ? 'Saving...' : (editingFineType ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Lateness Rule Modal -->
    <div v-if="showLatenessRuleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">{{ editingLatenessRule ? 'Edit Lateness Rule' : 'Add Lateness Rule' }}</h3>
            <button @click="closeLatenessRuleModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="saveLatenessRule" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website *</label>
              <select v-model="latenessRuleForm.website" required class="w-full border rounded px-3 py-2">
                <option value="">Select Website</option>
                <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Calculation Mode *</label>
              <select v-model="latenessRuleForm.calculation_mode" required class="w-full border rounded px-3 py-2">
                <option value="cumulative">Cumulative (5% + 10% + 15% = 30% after 3 hours)</option>
                <option value="progressive">Progressive (5% for hour 1, 10% for hour 2, etc.)</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Base Amount *</label>
              <select v-model="latenessRuleForm.base_amount" required class="w-full border rounded px-3 py-2">
                <option value="writer_compensation">Writer Compensation</option>
                <option value="total_price">Order Total Price</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">First Hour % *</label>
                <input
                  v-model.number="latenessRuleForm.first_hour_percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="5.00"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Second Hour % *</label>
                <input
                  v-model.number="latenessRuleForm.second_hour_percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="10.00"
                />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Third Hour % *</label>
                <input
                  v-model.number="latenessRuleForm.third_hour_percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="15.00"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Subsequent Hours % *</label>
                <input
                  v-model.number="latenessRuleForm.subsequent_hours_percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="5.00"
                />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Daily Rate % *</label>
                <input
                  v-model.number="latenessRuleForm.daily_rate_percentage"
                  type="number"
                  step="0.01"
                  required
                  class="w-full border rounded px-3 py-2"
                  placeholder="20.00"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Max Fine %</label>
                <input
                  v-model.number="latenessRuleForm.max_fine_percentage"
                  type="number"
                  step="0.01"
                  class="w-full border rounded px-3 py-2"
                  placeholder="Optional cap"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="latenessRuleForm.description"
                class="w-full border rounded px-3 py-2"
                rows="2"
                placeholder="Admin notes about this rule"
              ></textarea>
            </div>
            <div class="flex items-center">
              <input
                v-model="latenessRuleForm.active"
                type="checkbox"
                id="lateness_rule_active"
                class="mr-2"
              />
              <label for="lateness_rule_active" class="text-sm font-medium text-gray-700">Active</label>
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeLatenessRuleModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingLatenessRule">
                {{ savingLatenessRule ? 'Saving...' : (editingLatenessRule ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { finesAPI, websitesAPI } from '@/api'
import adminManagementAPI from '@/api/admin-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError, success: showSuccess } = useToast()

const tabs = [
  { id: 'fines', label: 'Fines' },
  { id: 'appeals', label: 'Appeals' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'dispute-queue', label: 'Dispute Queue' },
  { id: 'active-fines', label: 'Active Fines' },
  { id: 'fine-types', label: 'Fine Types' },
  { id: 'lateness-rules', label: 'Lateness Rules' },
]

const componentError = ref(null)
const initialLoading = ref(true)
const activeTab = ref('fines')
const stats = ref({})
const fines = ref([])
const appeals = ref([])
const fineTypes = ref([])
const latenessRules = ref([])

const finesLoading = ref(false)
const appealsLoading = ref(false)
const fineTypesLoading = ref(false)
const latenessRulesLoading = ref(false)
const analyticsLoading = ref(false)
const disputeQueueLoading = ref(false)
const activeFinesLoading = ref(false)

const analyticsDays = ref(30)
const analyticsData = ref(null)
const disputeQueue = ref([])
const activeFines = ref([])

const filters = ref({
  order_id: null,
  status: '',
  fine_type: '',
})

const showIssueFineModal = ref(false)
const showFineTypeModal = ref(false)
const showLatenessRuleModal = ref(false)
const issuingFine = ref(false)
const savingFineType = ref(false)
const savingLatenessRule = ref(false)

const websites = ref([])
const editingFineType = ref(null)
const editingLatenessRule = ref(null)

const issueFineForm = ref({
  order_id: null,
  fine_type_code: '',
  reason: '',
  custom_amount: null,
})

const fineTypeForm = ref({
  code: '',
  name: '',
  description: '',
  calculation_type: 'fixed',
  fixed_amount: null,
  percentage: null,
  base_amount: 'writer_compensation',
  min_amount: null,
  max_amount: null,
  website: '',
  active: true,
})

const latenessRuleForm = ref({
  website: '',
  calculation_mode: 'cumulative',
  base_amount: 'writer_compensation',
  first_hour_percentage: 5.00,
  second_hour_percentage: 10.00,
  third_hour_percentage: 15.00,
  subsequent_hours_percentage: 5.00,
  daily_rate_percentage: 20.00,
  max_fine_percentage: null,
  description: '',
  active: true,
})

let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadFines()
  }, 500)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const getStatusBadgeClass = (status) => {
  const classes = {
    issued: 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800',
    appealed: 'px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800',
    waived: 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800',
    voided: 'px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800',
    resolved: 'px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800',
  }
  return classes[status] || classes.issued
}

const getAppealStatusBadgeClass = (status) => {
  const classes = {
    pending: 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800',
    accepted: 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800',
    rejected: 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800',
    escalated: 'px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800',
  }
  return classes[status] || classes.pending
}

const loadStats = async () => {
  try {
    // Use the new dashboard endpoint for comprehensive stats
    const dashboardResponse = await adminManagementAPI.getFinesDashboard()
    const dashboard = dashboardResponse.data
    
    stats.value = {
      total_fines: dashboard.summary?.total_fines || 0,
      pending_appeals: dashboard.summary?.pending_appeals || 0,
      waived_fines: dashboard.summary?.waived_fines || 0,
      voided_fines: dashboard.summary?.voided_fines || 0,
      resolved_fines: dashboard.summary?.resolved_fines || 0,
      total_amount: dashboard.summary?.total_amount || '0.00',
      fines_with_appeals: dashboard.summary?.fines_with_appeals || 0,
      recent_count: dashboard.recent?.count || 0,
      recent_amount: dashboard.recent?.amount || '0.00',
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
    // Fallback to manual calculation if dashboard endpoint fails
    try {
      const [finesRes, appealsRes] = await Promise.all([
        finesAPI.list({ page_size: 1 }),
        finesAPI.listAppeals({ status: 'pending', page_size: 1 }),
      ])
      
      const allFines = finesRes.data.results || finesRes.data || []
      const totalAmount = allFines.reduce((sum, fine) => sum + (parseFloat(fine.amount) || 0), 0)
      const waivedCount = allFines.filter(f => f.status === 'waived').length
      
      stats.value = {
        total_fines: finesRes.data.count || allFines.length,
        pending_appeals: appealsRes.data.count || appealsRes.data.results?.length || 0,
        waived_fines: waivedCount,
        total_amount: totalAmount.toFixed(2),
      }
    } catch (fallbackError) {
      console.error('Failed to load stats (fallback):', fallbackError)
    }
  }
}

const loadFines = async () => {
  finesLoading.value = true
  try {
    const params = {}
    if (filters.value.order_id) params.order = filters.value.order_id
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.fine_type) params.fine_type = filters.value.fine_type
    
    const response = await finesAPI.listFines(params)
    fines.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load fines:', error)
  } finally {
    finesLoading.value = false
  }
}

const loadAppeals = async () => {
  appealsLoading.value = true
  try {
    // Use the new appeals queue endpoint
    const response = await adminManagementAPI.getAppealsQueue()
    appeals.value = response.data || []
  } catch (error) {
    console.error('Failed to load appeals:', error)
    // Fallback to regular API
    try {
      const fallbackResponse = await finesAPI.listAppeals()
      appeals.value = fallbackResponse.data.results || fallbackResponse.data || []
    } catch (fallbackError) {
      console.error('Failed to load appeals (fallback):', fallbackError)
    }
  } finally {
    appealsLoading.value = false
  }
}

const loadFineTypes = async () => {
  fineTypesLoading.value = true
  try {
    const response = await finesAPI.listFineTypes()
    fineTypes.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load fine types:', error)
  } finally {
    fineTypesLoading.value = false
  }
}

const loadLatenessRules = async () => {
  latenessRulesLoading.value = true
  try {
    const response = await finesAPI.listLatenessRules()
    latenessRules.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load lateness rules:', error)
  } finally {
    latenessRulesLoading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    order_id: null,
    status: '',
    fine_type: '',
  }
  loadFines()
}

const viewFine = (fine) => {
  // TODO: Implement fine detail modal
  alert(`Fine #${fine.id} details coming soon`)
}

const waiveFine = async (id) => {
  const reason = prompt('Enter reason for waiving this fine:')
  if (!reason) return
  
  try {
    await adminManagementAPI.waiveFine(id, { reason })
    await loadFines()
    await loadStats()
    showSuccess('Fine waived successfully')
  } catch (error) {
    console.error('Failed to waive fine:', error)
    const errorMsg = getErrorMessage(error, 'Failed to waive fine. Please try again.')
    showError(errorMsg)
  }
}

const voidFine = async (id) => {
  const reason = prompt('Enter reason for voiding this fine:') || 'Fine voided by admin'
  
  try {
    await adminManagementAPI.voidFine(id, { reason })
    await loadFines()
    await loadStats()
    showSuccess('Fine voided successfully')
  } catch (error) {
    console.error('Failed to void fine:', error)
    const errorMsg = getErrorMessage(error, 'Failed to void fine. Please try again.')
    showError(errorMsg)
  }
}

const viewAppeal = (appeal) => {
  // TODO: Implement appeal detail modal
  alert(`Appeal #${appeal.id} details coming soon`)
}

const reviewAppeal = async (id) => {
  const accept = confirm('Do you want to approve this appeal?')
  const reviewNotes = prompt('Enter review notes:') || ''
  
  try {
    if (accept) {
      await adminManagementAPI.approveAppeal(id, { notes: reviewNotes })
      showSuccess('Appeal approved successfully')
    } else {
      await adminManagementAPI.rejectAppeal(id, { notes: reviewNotes })
      showSuccess('Appeal rejected')
    }
    await loadAppeals()
    await loadStats()
  } catch (error) {
    console.error('Failed to review appeal:', error)
    const errorMsg = getErrorMessage(error, 'Failed to review appeal. Please try again.')
    showError(errorMsg)
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const editFineType = (type) => {
  editingFineType.value = type
  fineTypeForm.value = {
    code: type.code || '',
    name: type.name || '',
    description: type.description || '',
    calculation_type: type.calculation_type || 'fixed',
    fixed_amount: type.fixed_amount || null,
    percentage: type.percentage || null,
    base_amount: type.base_amount || 'writer_compensation',
    min_amount: type.min_amount || null,
    max_amount: type.max_amount || null,
    website: type.website || '',
    active: type.active !== false,
  }
  showFineTypeModal.value = true
}

const closeFineTypeModal = () => {
  showFineTypeModal.value = false
  editingFineType.value = null
  fineTypeForm.value = {
    code: '',
    name: '',
    description: '',
    calculation_type: 'fixed',
    fixed_amount: null,
    percentage: null,
    base_amount: 'writer_compensation',
    min_amount: null,
    max_amount: null,
    website: '',
    active: true,
  }
}

const saveFineType = async () => {
  savingFineType.value = true
  try {
    const data = {
      code: fineTypeForm.value.code,
      name: fineTypeForm.value.name,
      description: fineTypeForm.value.description || '',
      calculation_type: fineTypeForm.value.calculation_type,
      base_amount: fineTypeForm.value.base_amount,
      min_amount: fineTypeForm.value.min_amount || null,
      max_amount: fineTypeForm.value.max_amount || null,
      website: fineTypeForm.value.website || null,
      active: fineTypeForm.value.active,
    }
    
    if (fineTypeForm.value.calculation_type === 'fixed') {
      data.fixed_amount = fineTypeForm.value.fixed_amount
    } else if (fineTypeForm.value.calculation_type === 'percentage') {
      data.percentage = fineTypeForm.value.percentage
    }
    
    if (editingFineType.value) {
      await finesAPI.updateFineType(editingFineType.value.id, data)
    } else {
      await finesAPI.createFineType(data)
    }
    
    await loadFineTypes()
    closeFineTypeModal()
  } catch (error) {
    console.error('Failed to save fine type:', error)
    alert(error.response?.data?.detail || error.response?.data?.message || 'Failed to save fine type')
  } finally {
    savingFineType.value = false
  }
}

const deleteFineType = async (id) => {
  if (!confirm('Are you sure you want to delete this fine type?')) return
  try {
    await finesAPI.deleteFineType(id)
    await loadFineTypes()
  } catch (error) {
    console.error('Failed to delete fine type:', error)
    alert('Failed to delete fine type')
  }
}

const editLatenessRule = (rule) => {
  editingLatenessRule.value = rule
  latenessRuleForm.value = {
    website: rule.website || '',
    calculation_mode: rule.calculation_mode || 'cumulative',
    base_amount: rule.base_amount || 'writer_compensation',
    first_hour_percentage: rule.first_hour_percentage || 5.00,
    second_hour_percentage: rule.second_hour_percentage || 10.00,
    third_hour_percentage: rule.third_hour_percentage || 15.00,
    subsequent_hours_percentage: rule.subsequent_hours_percentage || 5.00,
    daily_rate_percentage: rule.daily_rate_percentage || 20.00,
    max_fine_percentage: rule.max_fine_percentage || null,
    description: rule.description || '',
    active: rule.active !== false,
  }
  showLatenessRuleModal.value = true
}

const closeLatenessRuleModal = () => {
  showLatenessRuleModal.value = false
  editingLatenessRule.value = null
  latenessRuleForm.value = {
    website: '',
    calculation_mode: 'cumulative',
    base_amount: 'writer_compensation',
    first_hour_percentage: 5.00,
    second_hour_percentage: 10.00,
    third_hour_percentage: 15.00,
    subsequent_hours_percentage: 5.00,
    daily_rate_percentage: 20.00,
    max_fine_percentage: null,
    description: '',
    active: true,
  }
}

const saveLatenessRule = async () => {
  savingLatenessRule.value = true
  try {
    const data = {
      website: latenessRuleForm.value.website,
      calculation_mode: latenessRuleForm.value.calculation_mode,
      base_amount: latenessRuleForm.value.base_amount,
      first_hour_percentage: latenessRuleForm.value.first_hour_percentage,
      second_hour_percentage: latenessRuleForm.value.second_hour_percentage,
      third_hour_percentage: latenessRuleForm.value.third_hour_percentage,
      subsequent_hours_percentage: latenessRuleForm.value.subsequent_hours_percentage,
      daily_rate_percentage: latenessRuleForm.value.daily_rate_percentage,
      max_fine_percentage: latenessRuleForm.value.max_fine_percentage || null,
      description: latenessRuleForm.value.description || '',
      active: latenessRuleForm.value.active,
    }
    
    if (editingLatenessRule.value) {
      await finesAPI.updateLatenessRule(editingLatenessRule.value.id, data)
    } else {
      await finesAPI.createLatenessRule(data)
    }
    
    await loadLatenessRules()
    closeLatenessRuleModal()
  } catch (error) {
    console.error('Failed to save lateness rule:', error)
    alert(error.response?.data?.detail || error.response?.data?.message || 'Failed to save lateness rule')
  } finally {
    savingLatenessRule.value = false
  }
}

const deleteLatenessRule = async (id) => {
  if (!confirm('Are you sure you want to delete this lateness rule?')) return
  try {
    await finesAPI.deleteLatenessRule(id)
    await loadLatenessRules()
  } catch (error) {
    console.error('Failed to delete lateness rule:', error)
    alert('Failed to delete lateness rule')
  }
}

const closeIssueFineModal = () => {
  showIssueFineModal.value = false
  issueFineForm.value = {
    order_id: null,
    fine_type_code: '',
    reason: '',
    custom_amount: null,
  }
}

const submitIssueFine = async () => {
  issuingFine.value = true
  try {
    const data = {
      order_id: issueFineForm.value.order_id,
      fine_type_code: issueFineForm.value.fine_type_code,
      reason: issueFineForm.value.reason,
    }
    if (issueFineForm.value.custom_amount) {
      data.custom_amount = issueFineForm.value.custom_amount
    }
    
    await finesAPI.issue(data)
    await loadFines()
    await loadStats()
    closeIssueFineModal()
  } catch (error) {
    console.error('Failed to issue fine:', error)
    alert(error.response?.data?.detail || 'Failed to issue fine')
  } finally {
    issuingFine.value = false
  }
}

const loadAnalytics = async () => {
  analyticsLoading.value = true
  try {
    const response = await adminManagementAPI.getFinesDashboardAnalytics({ days: analyticsDays.value })
    analyticsData.value = response?.data || null
  } catch (err) {
    console.error('Failed to load analytics:', err)
    showError('Failed to load analytics')
  } finally {
    analyticsLoading.value = false
  }
}

const loadDisputeQueue = async () => {
  disputeQueueLoading.value = true
  try {
    const response = await adminManagementAPI.getFinesDisputeQueue({})
    disputeQueue.value = response?.data?.disputes || []
  } catch (err) {
    console.error('Failed to load dispute queue:', err)
    showError('Failed to load dispute queue')
  } finally {
    disputeQueueLoading.value = false
  }
}

const loadActiveFines = async () => {
  activeFinesLoading.value = true
  try {
    const response = await adminManagementAPI.getFinesActiveFines({})
    activeFines.value = response?.data?.fines || []
  } catch (err) {
    console.error('Failed to load active fines:', err)
    showError('Failed to load active fines')
  } finally {
    activeFinesLoading.value = false
  }
}

const approveDispute = async (id) => {
  // TODO: Implement approve dispute
  showSuccess('Approve functionality coming soon')
}

const rejectDispute = async (id) => {
  // TODO: Implement reject dispute
  showSuccess('Reject functionality coming soon')
}

const viewFineDetails = (id) => {
  // TODO: Implement view fine details
  showSuccess('View details functionality coming soon')
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const finesTrendsSeries = computed(() => {
  if (!analyticsData.value?.trends?.length) return []
  return [{
    name: 'Fines',
    data: analyticsData.value.trends.map(t => t.count || 0)
  }]
})

const finesTrendsOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: {
    categories: analyticsData.value?.trends?.map(t => {
      if (t.date) {
        return new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return ''
    }).filter(Boolean) || []
  },
  yaxis: { title: { text: 'Count' } },
  stroke: { curve: 'smooth' },
  colors: ['#EF4444']
}))

watch(activeTab, (newTab) => {
  if (newTab === 'fines') {
    loadFines()
    loadFineTypes() // Need fine types for filter dropdown
  } else if (newTab === 'appeals') {
    loadAppeals()
  } else if (newTab === 'analytics') {
    loadAnalytics()
  } else if (newTab === 'dispute-queue') {
    loadDisputeQueue()
  } else if (newTab === 'active-fines') {
    loadActiveFines()
  } else if (newTab === 'fine-types') {
    loadFineTypes()
  } else if (newTab === 'lateness-rules') {
    loadLatenessRules()
  }
})

onMounted(async () => {
  // Set a timeout to ensure page doesn't stay blank forever
  const timeout = setTimeout(() => {
    if (initialLoading.value) {
      console.warn('FinesManagement initialization timeout')
      initialLoading.value = false
      if (!componentError.value) {
        componentError.value = 'Page took too long to load. Please refresh.'
      }
    }
  }, 10000) // 10 second timeout

  try {
    await Promise.all([
      loadWebsites(),
      loadStats(),
      loadFines(),
      loadFineTypes()
    ])
    clearTimeout(timeout)
    initialLoading.value = false
  } catch (error) {
    clearTimeout(timeout)
    console.error('Error initializing FinesManagement:', error)
    componentError.value = error.response?.data?.detail || error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

<style scoped>
/* Component styles */
</style>

