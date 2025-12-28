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
      <EnhancedDataTable
        :items="fines"
        :columns="finesColumns"
        :loading="finesLoading"
        :searchable="true"
        search-placeholder="Search fines by order ID, writer, type..."
        :search-fields="['order', 'fine_type_config.name', 'fine_type']"
        :sortable="true"
        :striped="true"
        empty-message="No fines found"
        empty-description="Try adjusting your filters or issue a new fine"
        empty-icon="💰"
      >
        <template #cell-status="{ value }">
          <span :class="getStatusBadgeClass(value || 'issued')" class="px-2 py-1 text-xs font-semibold rounded-full">
            {{ (value || 'issued').charAt(0).toUpperCase() + (value || 'issued').slice(1) }}
          </span>
        </template>
        <template #cell-order="{ value, item }">
          <router-link :to="`/orders/${item.order || value}`" class="text-blue-600 hover:text-blue-800 font-medium hover:underline">
            Order #{{ item.order || value }}
          </router-link>
        </template>
        <template #cell-amount="{ value }">
          <span class="font-semibold text-gray-900">${{ formatCurrency(value) }}</span>
        </template>
        <template #cell-actions="{ item }">
          <div class="flex items-center gap-2">
            <button
              @click="viewFine(item)"
              class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
              title="View Details"
            >
              View
            </button>
            <button
              v-if="item.status === 'issued'"
              @click="waiveFine(item.id)"
              class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
              title="Waive Fine"
            >
              Waive
            </button>
            <button
              v-if="item.status === 'issued'"
              @click="voidFine(item.id)"
              class="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
              title="Void Fine"
            >
              Void
            </button>
          </div>
        </template>
      </EnhancedDataTable>
    </div>

      <!-- Appeals Tab -->
    <div v-if="activeTab === 'appeals'" class="space-y-4">
      <EnhancedDataTable
        :items="appeals"
        :columns="appealsColumns"
        :loading="appealsLoading"
        :searchable="true"
        search-placeholder="Search appeals by fine ID, reason..."
        :search-fields="['fine', 'reason', 'appealed_by.username']"
        :sortable="true"
        :striped="true"
        empty-message="No appeals found"
        empty-description="All appeals have been reviewed or no appeals have been submitted yet"
        empty-icon="📝"
      >
        <template #cell-status="{ value }">
          <span :class="getAppealStatusBadgeClass(value || 'pending')" class="px-2 py-1 text-xs font-semibold rounded-full">
            {{ (value || 'pending').charAt(0).toUpperCase() + (value || 'pending').slice(1) }}
          </span>
        </template>
        <template #cell-fine="{ value }">
          <span class="font-medium text-gray-900">Fine #{{ value }}</span>
        </template>
        <template #cell-reason="{ value }">
          <div class="max-w-md truncate" :title="value || 'N/A'">
            {{ value || 'N/A' }}
          </div>
        </template>
        <template #cell-actions="{ item }">
          <div class="flex items-center gap-2">
            <button
              @click="viewAppeal(item)"
              class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
              title="View Details"
            >
              View
            </button>
            <button
              v-if="item.status === 'pending'"
              @click="reviewAppeal(item.id)"
              class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
              title="Review Appeal"
            >
              Review
            </button>
          </div>
        </template>
      </EnhancedDataTable>
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

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Fines Analytics</h3>
          <div class="flex items-center gap-4">
            <select v-model="analyticsDays" @change="loadAnalytics" class="border rounded px-3 py-2">
              <option :value="7">Last 7 days</option>
              <option :value="30">Last 30 days</option>
              <option :value="90">Last 90 days</option>
              <option :value="365">Last year</option>
            </select>
            <button @click="loadAnalytics" :disabled="analyticsLoading" class="btn btn-secondary">
              {{ analyticsLoading ? 'Loading...' : 'Refresh' }}
            </button>
          </div>
        </div>
        <div v-if="analyticsLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="analyticsData" class="space-y-6">
          <!-- Analytics Charts/Stats -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div class="text-sm text-gray-600 mb-1">Total Fines Issued</div>
              <div class="text-2xl font-bold text-blue-600">{{ analyticsData.total_fines || 0 }}</div>
            </div>
            <div class="p-4 bg-green-50 rounded-lg border border-green-200">
              <div class="text-sm text-gray-600 mb-1">Total Amount</div>
              <div class="text-2xl font-bold text-green-600">${{ formatCurrency(analyticsData.total_amount || 0) }}</div>
            </div>
            <div class="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <div class="text-sm text-gray-600 mb-1">Average Fine</div>
              <div class="text-2xl font-bold text-orange-600">${{ formatCurrency(analyticsData.average_fine || 0) }}</div>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 bg-white rounded-lg border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-3">Fines by Type</h4>
              <div v-if="analyticsData.fines_by_type?.length" class="space-y-2">
                <div v-for="item in analyticsData.fines_by_type" :key="item.type" class="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span class="text-sm text-gray-700">{{ item.type || item.fine_type || 'N/A' }}</span>
                  <span class="text-sm font-semibold text-gray-900">{{ item.count }} (${{ formatCurrency(item.amount) }})</span>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">No data available</div>
            </div>
            <div class="p-4 bg-white rounded-lg border border-gray-200">
              <h4 class="font-semibold text-gray-900 mb-3">Fines by Status</h4>
              <div v-if="analyticsData.fines_by_status?.length" class="space-y-2">
                <div v-for="item in analyticsData.fines_by_status" :key="item.status" class="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span class="text-sm text-gray-700">{{ formatStatus(item.status) }}</span>
                  <span class="text-sm font-semibold text-gray-900">{{ item.count }} (${{ formatCurrency(item.amount) }})</span>
                </div>
              </div>
              <div v-else class="text-sm text-gray-500">No data available</div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-12 text-gray-500">
          No analytics data available
        </div>
      </div>
    </div>

    <!-- Dispute Queue Tab -->
    <div v-if="activeTab === 'dispute-queue'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Dispute Queue</h3>
          <button @click="loadDisputeQueue" :disabled="disputeQueueLoading" class="btn btn-secondary">
            {{ disputeQueueLoading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
        <div v-if="disputeQueueLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <EnhancedDataTable
          v-else
          :items="disputeQueue"
          :columns="disputeQueueColumns"
          :loading="disputeQueueLoading"
          :searchable="true"
          search-placeholder="Search disputes..."
          :sortable="true"
          :striped="true"
          empty-message="No disputes in queue"
          empty-description="All disputes have been resolved"
          empty-icon="✅"
        >
          <template #cell-status="{ value }">
            <span :class="getStatusBadgeClass(value || 'pending')" class="px-2 py-1 text-xs font-semibold rounded-full">
              {{ (value || 'pending').charAt(0).toUpperCase() + (value || 'pending').slice(1) }}
            </span>
          </template>
          <template #cell-order="{ value, item }">
            <router-link :to="`/orders/${item.order || value}`" class="text-blue-600 hover:text-blue-800 font-medium hover:underline">
              Order #{{ item.order || value }}
            </router-link>
          </template>
          <template #cell-amount="{ value }">
            <span class="font-semibold text-gray-900">${{ formatCurrency(value) }}</span>
          </template>
          <template #cell-actions="{ item }">
            <div class="flex items-center gap-2">
              <button
                @click="viewFine(item)"
                class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                title="View Details"
              >
                View
              </button>
              <button
                v-if="item.appeal && item.appeal.status === 'pending'"
                @click="approveDispute(item.appeal.id)"
                class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
                title="Approve Appeal"
              >
                Approve
              </button>
              <button
                v-if="item.appeal && item.appeal.status === 'pending'"
                @click="rejectDispute(item.appeal.id)"
                class="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
                title="Reject Appeal"
              >
                Reject
              </button>
              <button
                v-if="item.status === 'disputed' && !item.appeal"
                @click="resolveDispute(item.id)"
                class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
                title="Resolve Dispute"
              >
                Resolve
              </button>
            </div>
          </template>
        </EnhancedDataTable>
      </div>
    </div>

    <!-- Active Fines Tab -->
    <div v-if="activeTab === 'active-fines'" class="space-y-4">
      <div class="card p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">Active Fines</h3>
          <button @click="loadActiveFines" :disabled="activeFinesLoading" class="btn btn-secondary">
            {{ activeFinesLoading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
        <div v-if="activeFinesLoading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <EnhancedDataTable
          v-else
          :items="activeFines"
          :columns="finesColumns"
          :loading="activeFinesLoading"
          :searchable="true"
          search-placeholder="Search active fines..."
          :sortable="true"
          :striped="true"
          empty-message="No active fines"
          empty-description="All fines have been resolved or waived"
          empty-icon="✅"
        >
          <template #cell-status="{ value }">
            <span :class="getStatusBadgeClass(value || 'issued')" class="px-2 py-1 text-xs font-semibold rounded-full">
              {{ (value || 'issued').charAt(0).toUpperCase() + (value || 'issued').slice(1) }}
            </span>
          </template>
          <template #cell-order="{ value, item }">
            <router-link :to="`/orders/${item.order || value}`" class="text-blue-600 hover:text-blue-800 font-medium hover:underline">
              Order #{{ item.order || value }}
            </router-link>
          </template>
          <template #cell-amount="{ value }">
            <span class="font-semibold text-gray-900">${{ formatCurrency(value) }}</span>
          </template>
          <template #cell-actions="{ item }">
            <div class="flex items-center gap-2">
              <button
                @click="viewFine(item)"
                class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                title="View Details"
              >
                View
              </button>
              <button
                v-if="item.status === 'issued'"
                @click="waiveFine(item.id)"
                class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-md hover:bg-green-100 transition-colors"
                title="Waive Fine"
              >
                Waive
              </button>
            </div>
          </template>
        </EnhancedDataTable>
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
    <div v-if="showFineTypeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="closeFineTypeModal">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white">{{ editingFineType ? 'Edit Fine Type' : 'Create Fine Type' }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ editingFineType ? 'Update fine type configuration' : 'Configure a new fine type' }}</p>
            </div>
            <button 
              @click="closeFineTypeModal" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <form @submit.prevent="saveFineType" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Code <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="fineTypeForm.code"
                  type="text"
                  required
                  :disabled="editingFineType"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="e.g., quality_issue"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Unique identifier (cannot be changed after creation)</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="fineTypeForm.name"
                  type="text"
                  required
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  placeholder="e.g., Quality Issue"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
              <textarea
                v-model="fineTypeForm.description"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                rows="3"
                placeholder="Description of when this fine applies"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Calculation Type <span class="text-red-500">*</span>
              </label>
              <select 
                v-model="fineTypeForm.calculation_type" 
                required 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              >
                <option value="fixed">Fixed Amount</option>
                <option value="percentage">Percentage of Base Amount</option>
                <option value="progressive_hourly">Progressive Hourly (Late Submission Only)</option>
              </select>
            </div>
            <div v-if="fineTypeForm.calculation_type === 'fixed'" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fixed Amount <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400">$</span>
                  <input
                    v-model.number="fineTypeForm.fixed_amount"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-8 pr-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>
            <div v-if="fineTypeForm.calculation_type === 'percentage'" class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Percentage <span class="text-red-500">*</span>
                </label>
                <div class="relative">
                  <input
                    v-model.number="fineTypeForm.percentage"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    required
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="0.00"
                  />
                  <span class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400">%</span>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Base Amount</label>
                <select 
                  v-model="fineTypeForm.base_amount" 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                >
                  <option value="writer_compensation">Writer Compensation</option>
                  <option value="total_price">Order Total Price</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Min Amount</label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400">$</span>
                  <input
                    v-model.number="fineTypeForm.min_amount"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-8 pr-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Optional"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Max Amount</label>
                <div class="relative">
                  <span class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400">$</span>
                  <input
                    v-model.number="fineTypeForm.max_amount"
                    type="number"
                    step="0.01"
                    min="0"
                    class="w-full border border-gray-300 dark:border-gray-600 rounded-lg pl-8 pr-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Optional"
                  />
                </div>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Website</label>
              <select 
                v-model="fineTypeForm.website" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              >
                <option value="">All Websites (Global)</option>
                <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Leave empty to apply to all websites</p>
            </div>
            <div class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <input
                v-model="fineTypeForm.active"
                type="checkbox"
                id="fine_type_active"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label for="fine_type_active" class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                Active
              </label>
              <p class="ml-auto text-xs text-gray-500 dark:text-gray-400">Only active fine types can be used</p>
            </div>
            
            <!-- Form Footer -->
            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button 
                type="button" 
                @click="closeFineTypeModal" 
                class="px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit"
                :disabled="savingFineType"
                class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                <span v-if="savingFineType" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                {{ savingFineType ? 'Saving...' : (editingFineType ? 'Update Fine Type' : 'Create Fine Type') }}
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

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      :show="confirmProps.show"
      :title="confirmProps.title"
      :message="confirmProps.message"
      :details="confirmProps.details"
      :variant="confirmProps.variant"
      :confirm-text="confirmProps.confirmText"
      :cancel-text="confirmProps.cancelText"
      :icon="confirmProps.icon"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
      @update:show="(val) => confirm.show.value = val"
    />

    <!-- Input Modal - Only render when explicitly shown -->
    <InputModal
      v-if="inputModalProps.show"
      :show="inputModalProps.show"
      :title="inputModalProps.title || 'Input Required'"
      :message="inputModalProps.message"
      :label="inputModalProps.label"
      :placeholder="inputModalProps.placeholder"
      :hint="inputModalProps.hint"
      :multiline="inputModalProps.multiline"
      :rows="inputModalProps.rows"
      :required="inputModalProps.required"
      :default-value="typeof inputModalProps.defaultValue === 'string' ? inputModalProps.defaultValue : ''"
      :confirm-text="inputModalProps.confirmText"
      :cancel-text="inputModalProps.cancelText"
      @submit="inputModal.onSubmit"
      @cancel="inputModal.onCancel"
      @update:show="(val) => inputModal.show.value = val"
    />

    <!-- Fine Detail Modal -->
    <div v-if="showFineDetailModal && selectedFine" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="showFineDetailModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Fine Details</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Fine ID: #{{ selectedFine.id }}</p>
            </div>
            <button 
              @click="showFineDetailModal = false" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Left Column -->
            <div class="space-y-4">
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Order ID</label>
                <router-link 
                  :to="`/orders/${selectedFine.order || selectedFine.order_id}`" 
                  class="text-lg font-semibold text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Order #{{ selectedFine.order || selectedFine.order_id }}
                </router-link>
              </div>
              
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Amount</label>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">${{ formatCurrency(selectedFine.amount) }}</p>
              </div>
              
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Status</label>
                <span :class="getStatusBadgeClass(selectedFine.status)" class="inline-block px-3 py-1.5 text-sm font-semibold rounded-full">
                  {{ (selectedFine.status || 'issued').charAt(0).toUpperCase() + (selectedFine.status || 'issued').slice(1) }}
                </span>
              </div>
            </div>
            
            <!-- Right Column -->
            <div class="space-y-4">
              <div v-if="selectedFine.fine_type || selectedFine.fine_type_config" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Fine Type</label>
                <p class="text-lg font-medium text-gray-900 dark:text-white">
                  {{ selectedFine.fine_type_config?.name || selectedFine.fine_type?.name || selectedFine.fine_type?.code || 'N/A' }}
                </p>
              </div>
              
              <div v-if="selectedFine.reason" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Reason</label>
                <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">{{ selectedFine.reason }}</p>
              </div>
              
              <div v-if="selectedFine.issued_at || selectedFine.created_at" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Issued Date</label>
                <p class="text-sm text-gray-900 dark:text-white">{{ formatDate(selectedFine.issued_at || selectedFine.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer Actions -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-end gap-3">
          <button 
            @click="showFineDetailModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
          <button
            v-if="selectedFine.status === 'issued'"
            @click="waiveFine(selectedFine.id); showFineDetailModal = false"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
          >
            Waive Fine
          </button>
          <button
            v-if="selectedFine.status === 'issued'"
            @click="voidFine(selectedFine.id); showFineDetailModal = false"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
          >
            Void Fine
          </button>
        </div>
      </div>
    </div>

    <!-- Appeal Detail Modal -->
    <div v-if="showAppealDetailModal && selectedAppeal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click.self="showAppealDetailModal = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-orange-50 to-orange-100 dark:from-gray-700 dark:to-gray-800">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Appeal Details</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Appeal ID: #{{ selectedAppeal.id }}</p>
            </div>
            <button 
              @click="showAppealDetailModal = false" 
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Left Column -->
            <div class="space-y-4">
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Fine ID</label>
                <p class="text-lg font-semibold text-gray-900 dark:text-white">Fine #{{ selectedAppeal.fine || selectedAppeal.fine_id }}</p>
              </div>
              
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Status</label>
                <span :class="getAppealStatusBadgeClass(selectedAppeal.status)" class="inline-block px-3 py-1.5 text-sm font-semibold rounded-full">
                  {{ (selectedAppeal.status || 'pending').charAt(0).toUpperCase() + (selectedAppeal.status || 'pending').slice(1) }}
                </span>
              </div>
              
              <div v-if="selectedAppeal.appealed_by" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Appealed By</label>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedAppeal.appealed_by.username || selectedAppeal.appealed_by }}</p>
              </div>
            </div>
            
            <!-- Right Column -->
            <div class="space-y-4">
              <div v-if="selectedAppeal.reason" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Reason</label>
                <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">{{ selectedAppeal.reason }}</p>
              </div>
              
              <div v-if="selectedAppeal.notes" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Review Notes</label>
                <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">{{ selectedAppeal.notes }}</p>
              </div>
              
              <div v-if="selectedAppeal.created_at" class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1 block">Created Date</label>
                <p class="text-sm text-gray-900 dark:text-white">{{ formatDate(selectedAppeal.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer Actions -->
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-end gap-3">
          <button 
            @click="showAppealDetailModal = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
          <button
            v-if="selectedAppeal.status === 'pending'"
            @click="reviewAppeal(selectedAppeal.id); showAppealDetailModal = false"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
          >
            Review Appeal
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { finesAPI, websitesAPI } from '@/api'
import adminManagementAPI from '@/api/admin-management'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import { getErrorMessage } from '@/utils/errorHandler'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import InputModal from '@/components/common/InputModal.vue'
import ErrorDisplay from '@/components/common/ErrorDisplay.vue'
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'

const { error: showError, success: showSuccess } = useToast()
const confirm = useConfirmDialog()
const inputModal = useInputModal()

// Create computed properties to unwrap refs for template usage
const confirmProps = computed(() => ({
  show: confirm.show.value,
  title: confirm.title.value,
  message: confirm.message.value,
  details: confirm.details.value,
  variant: confirm.variant.value,
  confirmText: confirm.confirmText.value,
  cancelText: confirm.cancelText.value,
  icon: confirm.icon.value
}))

const inputModalProps = computed(() => ({
  show: inputModal.show.value,
  title: inputModal.title.value,
  message: inputModal.message.value,
  label: inputModal.label.value,
  placeholder: inputModal.placeholder.value,
  hint: inputModal.hint.value,
  multiline: inputModal.multiline.value,
  rows: inputModal.rows.value,
  required: inputModal.required.value,
  defaultValue: inputModal.defaultValue.value,
  confirmText: inputModal.confirmText.value,
  cancelText: inputModal.cancelText.value
}))

// Ensure modal is hidden on initialization and reset all values
// Use nextTick to ensure this happens after component setup
nextTick(() => {
  inputModal.show.value = false
  inputModal.message.value = null
  inputModal.title.value = 'Input Required'
  inputModal.defaultValue.value = ''
})

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
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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

// Column definitions for EnhancedDataTable
const finesColumns = computed(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    class: 'w-20'
  },
  {
    key: 'order',
    label: 'Order',
    sortable: true
  },
  {
    key: 'order.assigned_writer.username',
    label: 'Writer',
    sortable: false,
    format: (value, item) => item.order?.assigned_writer?.username || 'N/A'
  },
  {
    key: 'fine_type_config.name',
    label: 'Type',
    sortable: true,
    format: (value, item) => item.fine_type_config?.name || item.fine_type || 'N/A'
  },
  {
    key: 'amount',
    label: 'Amount',
    sortable: true,
    align: 'right',
    class: 'w-32'
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    class: 'w-28'
  },
  {
    key: 'issued_at',
    label: 'Issued',
    sortable: true,
    format: (value) => formatDate(value),
    class: 'w-40'
  },
  {
    key: 'actions',
    label: 'Actions',
    sortable: false,
    align: 'right',
    class: 'w-40'
  }
])

const getAppealStatusBadgeClass = (status) => {
  const classes = {
    pending: 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800',
    accepted: 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800',
    rejected: 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800',
    escalated: 'px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800',
  }
  return classes[status] || classes.pending
}

// Column definitions for Appeals table
const disputeQueueColumns = computed(() => [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'order', label: 'Order', sortable: true },
  { key: 'fine_type', label: 'Fine Type', sortable: true },
  { key: 'amount', label: 'Amount', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'created_at', label: 'Created', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false },
])

const appealsColumns = computed(() => [
  {
    key: 'id',
    label: 'ID',
    sortable: true,
    class: 'w-20'
  },
  {
    key: 'fine',
    label: 'Fine ID',
    sortable: true
  },
  {
    key: 'appealed_by.username',
    label: 'Appealed By',
    sortable: false,
    format: (value, item) => item.appealed_by?.username || 'N/A'
  },
  {
    key: 'reason',
    label: 'Reason',
    sortable: false,
    format: (value) => value || 'N/A'
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    class: 'w-28'
  },
  {
    key: 'created_at',
    label: 'Created',
    sortable: true,
    format: (value) => formatDate(value),
    class: 'w-40'
  },
  {
    key: 'actions',
    label: 'Actions',
    sortable: false,
    align: 'right',
    class: 'w-32'
  }
])

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
      const errorMsg = getErrorMessage(fallbackError, 'Failed to load statistics.')
      showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to load fines. Please try again.')
    showError(errorMsg)
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
    // Fallback to regular API
    try {
      const fallbackResponse = await finesAPI.listAppeals()
      appeals.value = fallbackResponse.data.results || fallbackResponse.data || []
    } catch (fallbackError) {
      const errorMsg = getErrorMessage(fallbackError, 'Failed to load appeals. Please try again.')
      showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to load fine types. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to load lateness rules. Please try again.')
    showError(errorMsg)
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

const selectedFine = ref(null)
const showFineDetailModal = ref(false)

const viewFine = async (fine) => {
  // If fine is just an ID, fetch full details; otherwise use the object
  if (typeof fine === 'number' || (typeof fine === 'object' && !fine.amount && !fine.status)) {
    await viewFineDetails(typeof fine === 'number' ? fine : fine.id)
  } else {
    selectedFine.value = fine
    showFineDetailModal.value = true
  }
}

const waiveFine = async (id) => {
  const reason = await inputModal.showModal(
    'Enter reason for waiving this fine',
    'Waive Fine',
    { 
      label: 'Reason',
      placeholder: 'Enter reason for waiving...',
      multiline: true,
      rows: 4,
      required: true
    }
  )
  
  if (!reason) return
  
  try {
    await adminManagementAPI.waiveFine(id, { reason })
    await loadFines()
    await loadStats()
    showSuccess('Fine waived successfully')
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to waive fine. Please try again.')
    showError(errorMsg)
  }
}

const voidFine = async (id) => {
  const reason = await inputModal.showModal(
    'Enter reason for voiding this fine',
    'Void Fine',
    { 
      label: 'Reason',
      placeholder: 'Enter reason for voiding...',
      multiline: true,
      rows: 4,
      defaultValue: 'Fine voided by admin',
      required: false
    }
  )
  
  if (reason === null) return // User cancelled
  
  const finalReason = reason || 'Fine voided by admin'
  
  try {
    await adminManagementAPI.voidFine(id, { reason: finalReason })
    await loadFines()
    await loadStats()
    showSuccess('Fine voided successfully')
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to void fine. Please try again.')
    showError(errorMsg)
  }
}

const selectedAppeal = ref(null)
const showAppealDetailModal = ref(false)

const viewAppeal = (appeal) => {
  selectedAppeal.value = appeal
  showAppealDetailModal.value = true
}

const reviewAppeal = async (id) => {
  const accept = await confirm.showDialog(
    'Do you want to approve this appeal?',
    'Review Appeal',
    {
      variant: 'default',
      confirmText: 'Approve',
      cancelText: 'Reject'
    }
  )
  
  if (accept === null) return // User cancelled
  
  const reviewNotes = await inputModal.showModal(
    accept ? 'Enter review notes for approval (optional)' : 'Enter review notes for rejection (required)',
    accept ? 'Approve Appeal' : 'Reject Appeal',
    { 
      label: 'Notes',
      placeholder: accept ? 'Enter review notes...' : 'Explain why this appeal is being rejected...',
      multiline: true,
      rows: 4,
      required: !accept
    }
  )
  
  if (reviewNotes === null) return // User cancelled
  
  if (!accept && !reviewNotes.trim()) {
    showError('Review notes are required when rejecting an appeal')
    return
  }
  
  try {
    if (accept) {
      await adminManagementAPI.approveAppeal(id, { notes: reviewNotes || '' })
      showSuccess('Appeal approved successfully')
    } else {
      await adminManagementAPI.rejectAppeal(id, { notes: reviewNotes })
      showSuccess('Appeal rejected')
    }
    await Promise.all([loadAppeals(), loadDisputeQueue(), loadFines(), loadStats()])
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to review appeal. Please try again.')
    showError(errorMsg)
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data.results || response.data || []
  } catch (error) {
    // Silently fail - websites are not critical for page functionality
    const errorMsg = getErrorMessage(error, 'Failed to load websites.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to save fine type. Please try again.')
    showError(errorMsg)
  } finally {
    savingFineType.value = false
  }
}

const deleteFineType = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this fine type? This action cannot be undone.',
    'Delete Fine Type'
  )
  
  if (!confirmed) return
  
  try {
    await finesAPI.deleteFineType(id)
    await loadFineTypes()
    showSuccess('Fine type deleted successfully')
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to delete fine type. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to save lateness rule. Please try again.')
    showError(errorMsg)
  } finally {
    savingLatenessRule.value = false
  }
}

const deleteLatenessRule = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this lateness rule? This action cannot be undone.',
    'Delete Lateness Rule'
  )
  
  if (!confirmed) return
  
  try {
    await finesAPI.deleteLatenessRule(id)
    await loadLatenessRules()
    showSuccess('Lateness rule deleted successfully')
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to delete lateness rule. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(error, 'Failed to issue fine. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(err, 'Failed to load analytics. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(err, 'Failed to load dispute queue. Please try again.')
    showError(errorMsg)
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
    const errorMsg = getErrorMessage(err, 'Failed to load active fines. Please try again.')
    showError(errorMsg)
  } finally {
    activeFinesLoading.value = false
  }
}

// Approve dispute/appeal - works with appeal ID
const approveDispute = async (appealId) => {
  try {
    const notes = await inputModal.showModal(
      'Enter review notes for approving this appeal (optional):',
      'Approve Appeal',
      {
        label: 'Review Notes',
        placeholder: 'Add notes about why this appeal is being approved...',
        multiline: true,
        rows: 4,
        required: false
      }
    )
    
    if (notes === null) return // User cancelled
    
    await adminManagementAPI.approveAppeal(appealId, { notes: notes || '' })
    showSuccess('Appeal approved successfully')
    await Promise.all([loadAppeals(), loadDisputeQueue(), loadFines(), loadStats()])
  } catch (err) {
    if (err !== 'cancelled' && err !== null) {
      const errorMsg = getErrorMessage(err, 'Failed to approve appeal')
      showError(errorMsg)
    }
  }
}

// Reject dispute/appeal - works with appeal ID
const rejectDispute = async (appealId) => {
  try {
    const notes = await inputModal.showModal(
      'Enter review notes for rejecting this appeal (required):',
      'Reject Appeal',
      {
        label: 'Review Notes',
        placeholder: 'Explain why this appeal is being rejected...',
        multiline: true,
        rows: 4,
        required: true
      }
    )
    
    if (!notes) {
      showError('Review notes are required to reject an appeal')
      return
    }
    
    await adminManagementAPI.rejectAppeal(appealId, { notes })
    showSuccess('Appeal rejected')
    await Promise.all([loadAppeals(), loadDisputeQueue(), loadFines(), loadStats()])
  } catch (err) {
    if (err !== 'cancelled' && err !== null) {
      const errorMsg = getErrorMessage(err, 'Failed to reject appeal')
      showError(errorMsg)
    }
  }
}

// View fine details - loads fine from API and shows modal
const viewFineDetails = async (fineId) => {
  try {
    const fine = await finesAPI.getFine(fineId)
    selectedFine.value = fine.data
    showFineDetailModal.value = true
  } catch (err) {
    const errorMsg = getErrorMessage(err, 'Failed to load fine details')
    showError(errorMsg)
  }
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
  if (newTab === 'analytics') {
    loadAnalytics()
  } else if (newTab === 'dispute-queue') {
    loadDisputeQueue()
  } else if (newTab === 'active-fines') {
    loadActiveFines()
  } else if (newTab === 'fines') {
    loadFines()
  } else if (newTab === 'appeals') {
    loadAppeals()
  } else if (newTab === 'fine-types') {
    loadFineTypes()
  } else if (newTab === 'lateness-rules') {
    loadLatenessRules()
  }
})

const resolveDispute = async (fineId) => {
  try {
    const result = await inputModal.showModal(
      'Enter resolution notes:',
      'Resolve Dispute',
      {
        label: 'Resolution Notes',
        placeholder: 'Resolution details...',
        multiline: true,
        rows: 4
      }
    )
    if (result) {
      // Call API to resolve dispute
      await adminManagementAPI.waiveFine(fineId, { reason: result, resolve_dispute: true })
      showSuccess('Dispute resolved successfully')
      loadDisputeQueue()
      loadFines()
    }
  } catch (err) {
    if (err !== 'cancelled' && err !== null) {
      const errorMsg = getErrorMessage(err, 'Failed to resolve dispute')
      showError(errorMsg)
    }
  }
}

const formatStatus = (status) => {
  if (!status) return 'N/A'
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(async () => {
  // Ensure InputModal is hidden on mount
  inputModal.show.value = false
  
  // Set a timeout to ensure page doesn't stay blank forever
  const timeout = setTimeout(() => {
    if (initialLoading.value) {
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
    const errorMsg = getErrorMessage(error, 'Failed to initialize page. Please refresh and try again.')
    componentError.value = errorMsg
    initialLoading.value = false
  }
  
  // Final check to ensure modal is hidden
  if (inputModal.show.value) {
    console.warn('InputModal was showing after mount, hiding it now')
    inputModal.show.value = false
  }
})
</script>

<style scoped>
/* Component styles */
</style>

