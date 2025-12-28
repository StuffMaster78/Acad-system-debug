<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              My Orders
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Manage your assigned orders and track deadlines
            </p>
          </div>
          <button
            @click="loadOrders"
            :disabled="loading"
            class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md p-6 border-l-4 border-blue-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
                In Progress
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-blue-900">
                {{ stats.in_progress || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">📝</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-md p-6 border-l-4 border-yellow-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide mb-2">
                Due Soon
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-yellow-900">
                {{ stats.due_soon || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-yellow-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">⏰</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-md p-6 border-l-4 border-green-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
                Submitted
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-green-900">
                {{ stats.submitted || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">✅</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-md p-6 border-l-4 border-purple-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-purple-700 uppercase tracking-wide mb-2">
                Total Active
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-purple-900">
                {{ stats.total_active || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-xl shadow-md p-6 mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h3 class="text-xl font-bold text-gray-900 flex items-center gap-2">
            <span class="text-2xl">🔍</span>
            <span>Filters</span>
          </h3>
          <div class="flex items-center gap-3">
            <button
              @click="showAdvancedFilters = !showAdvancedFilters"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
            >
              <span>{{ showAdvancedFilters ? '▼' : '▶' }}</span>
              <span>{{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced</span>
            </button>
            <button
              @click="resetFilters"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <span>↻</span>
              <span>Reset All</span>
            </button>
          </div>
        </div>
      
      <!-- Basic Filters -->
      <div class="flex flex-wrap items-center gap-4 mb-4">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            v-model="filters.status"
            @change="loadOrders"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="in_progress">In Progress</option>
            <option value="submitted">Submitted</option>
            <option value="under_editing">Under Editing</option>
            <option value="revision_requested">
              Revision Requested
            </option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
            <option value="approved">Approved</option>
          </select>
        </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
              Priority
            </label>
            <select
              v-model="filters.priority"
              @change="loadOrders"
              class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
            >
            <option value="">All Priorities</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>
        </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
              Sort By
            </label>
            <select
              v-model="sortBy"
              @change="loadOrders"
              class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
            >
            <option value="deadline_asc">
              Deadline (Earliest First)
            </option>
            <option value="deadline_desc">
              Deadline (Latest First)
            </option>
            <option value="priority_desc">
              Priority (High to Low)
            </option>
            <option value="priority_asc">
              Priority (Low to High)
            </option>
            <option value="created_desc">Newest First</option>
            <option value="created_asc">Oldest First</option>
          </select>
        </div>
        <div class="flex-1 min-w-[200px]">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            v-model="searchQuery"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by topic or order ID..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
      
      <!-- Advanced Filters -->
      <div
        v-if="showAdvancedFilters"
        class="border-t pt-4 mt-4 space-y-4"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Deadline Range -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Deadline From
              </label>
              <input
                v-model="filters.deadline_from"
                @change="loadOrders"
                type="date"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Deadline To
              </label>
              <input
                v-model="filters.deadline_to"
                @change="loadOrders"
                type="date"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
              />
            </div>
            
            <!-- Payment Amount Range -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Min Payment ($)
              </label>
              <input
                v-model.number="filters.min_payment"
                @input="debouncedFilter"
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Max Payment ($)
              </label>
              <input
                v-model.number="filters.max_payment"
                @input="debouncedFilter"
                type="number"
                min="0"
                step="0.01"
                placeholder="No limit"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
            
            <!-- Client Name -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Client Name
              </label>
              <input
                v-model="filters.client_name"
                @input="debouncedFilter"
                type="text"
                placeholder="Filter by client..."
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
            
            <!-- Service Type -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Service Type
              </label>
              <select
                v-model="filters.service_type"
                @change="loadOrders"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
              >
                <option value="">All Services</option>
                <option
                  v-for="service in serviceTypes"
                  :key="service"
                  :value="service"
                >
                  {{ service }}
                </option>
              </select>
            </div>
            
            <!-- Subject -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Subject
              </label>
              <input
                v-model="filters.subject"
                @input="debouncedFilter"
                type="text"
                placeholder="Filter by subject..."
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
            
            <!-- Pages Range -->
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Min Pages
              </label>
              <input
                v-model.number="filters.min_pages"
                @input="debouncedFilter"
                type="number"
                min="0"
                placeholder="0"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Max Pages
              </label>
              <input
                v-model.number="filters.max_pages"
                @input="debouncedFilter"
                type="number"
                min="0"
                placeholder="No limit"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
              />
            </div>
        </div>
      </div>
    </div>

      <!-- Orders List -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading orders...</p>
        </div>
      </div>

      <div v-else-if="orders.length === 0" class="bg-white rounded-xl shadow-sm p-16 text-center">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-6">
          <span class="text-4xl">📭</span>
        </div>
        <p class="text-lg font-semibold text-gray-900 mb-2">No orders found</p>
        <p class="text-sm text-gray-500 mb-6 max-w-md mx-auto">
          Check the order queue to find available orders.
        </p>
        <router-link
          to="/writer/queue"
          class="inline-flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-all shadow-md hover:shadow-lg"
        >
          View Order Queue
        </router-link>
      </div>

      <div v-else class="space-y-5">
        <div
          v-for="order in orders"
          :key="order.id"
          class="bg-white rounded-xl shadow-md border border-gray-200 hover:shadow-lg transition-all"
        >
          <div class="p-6 sm:p-8">
            <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-3 mb-4">
                  <h3 class="text-xl font-bold text-gray-900">
                    Order #{{ order.id }}
                  </h3>
                  <span
                    :class="getPriorityBadgeClass(order.priority || 'medium')"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide cursor-pointer hover:opacity-80 transition-opacity"
                    @click="showPriorityModal(order)"
                    :title="`Priority: ${(order.priority || 'medium').toUpperCase()}. Click to change.`"
                  >
                    <span>{{ getPriorityIcon(order.priority || 'medium') }}</span>
                    <span>{{ formatPriority(order.priority || 'medium') }}</span>
                  </span>
                  <EnhancedStatusBadge
                    :status="order.status"
                    :show-tooltip="true"
                    :show-priority="true"
                  />
                  <span
                    v-if="isDueSoon(order.writer_deadline || order.client_deadline || order.deadline)"
                    class="px-3 py-1.5 rounded-full text-xs font-bold bg-red-100 text-red-700 uppercase tracking-wide"
                  >
                    ⚠️ Due Soon
                  </span>
                </div>
                
                <p class="text-base font-semibold text-gray-900 mb-4 line-clamp-2">
                  {{ order.topic || 'No topic' }}
                </p>
                
                <!-- Revision Notes Section -->
                <div v-if="order.status === 'revision_requested'" class="mb-4 p-4 bg-orange-50 border-l-4 border-orange-500 rounded-lg">
                  <div class="flex items-start gap-3">
                    <div class="shrink-0 mt-0.5">
                      <span class="text-2xl">⚠️</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <h4 class="text-sm font-bold text-orange-900 uppercase tracking-wide mb-2">
                        Revision Required
                      </h4>
                      <div v-if="order.revision_request || order.revision_notes || order.revision_instructions" class="space-y-2">
                        <div v-if="order.revision_request?.title || order.revision_request?.description" class="text-sm text-gray-800">
                          <p v-if="order.revision_request?.title" class="font-semibold text-gray-900 mb-1">
                            {{ order.revision_request.title }}
                          </p>
                          <p v-if="order.revision_request?.description" class="text-gray-700 whitespace-pre-wrap">
                            {{ order.revision_request.description }}
                          </p>
                        </div>
                        <div v-if="order.revision_request?.client_notes" class="text-sm text-gray-700 bg-white p-3 rounded border border-orange-200">
                          <p class="font-semibold text-gray-900 mb-1">Client Notes:</p>
                          <p class="whitespace-pre-wrap">{{ order.revision_request.client_notes }}</p>
                        </div>
                        <div v-if="order.revision_request?.changes_required && order.revision_request.changes_required.length > 0" class="text-sm">
                          <p class="font-semibold text-gray-900 mb-2">Specific Changes Required:</p>
                          <ul class="list-disc list-inside space-y-1 text-gray-700 ml-2">
                            <li v-for="(change, idx) in order.revision_request.changes_required" :key="idx">
                              <span v-if="change.section" class="font-medium">{{ change.section }}:</span>
                              <span v-if="change.issue">{{ change.issue }}</span>
                              <span v-if="change.request" class="text-gray-600"> - {{ change.request }}</span>
                            </li>
                          </ul>
                        </div>
                        <div v-if="order.revision_notes" class="text-sm text-gray-700 bg-white p-3 rounded border border-orange-200">
                          <p class="font-semibold text-gray-900 mb-1">Revision Notes:</p>
                          <p class="whitespace-pre-wrap">{{ order.revision_notes }}</p>
                        </div>
                        <div v-if="order.revision_instructions" class="text-sm text-gray-700 bg-white p-3 rounded border border-orange-200">
                          <p class="font-semibold text-gray-900 mb-1">Revision Instructions:</p>
                          <p class="whitespace-pre-wrap">{{ order.revision_instructions }}</p>
                        </div>
                        <div v-if="order.revision_request?.severity" class="flex items-center gap-2 text-xs">
                          <span class="font-semibold text-gray-700">Severity:</span>
                          <span 
                            class="px-2 py-1 rounded-full font-medium"
                            :class="{
                              'bg-red-100 text-red-700': order.revision_request.severity === 'critical',
                              'bg-orange-100 text-orange-700': order.revision_request.severity === 'major',
                              'bg-yellow-100 text-yellow-700': order.revision_request.severity === 'moderate',
                              'bg-blue-100 text-blue-700': order.revision_request.severity === 'minor'
                            }"
                          >
                            {{ order.revision_request.severity?.charAt(0).toUpperCase() + order.revision_request.severity?.slice(1) }}
                          </span>
                        </div>
                        <div v-if="order.revision_request?.agreed_deadline || order.revision_request?.requested_deadline" class="text-xs text-gray-600">
                          <span class="font-semibold">Deadline:</span>
                          {{ formatDateTime(order.revision_request.agreed_deadline || order.revision_request.requested_deadline) }}
                        </div>
                      </div>
                      <div v-else class="text-sm text-gray-700">
                        <p>Please review the order details for revision requirements.</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                      Pages
                    </p>
                    <p class="text-base font-bold text-gray-900">
                      {{ order.pages || order.number_of_pages || 'N/A' }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                      Service
                    </p>
                    <p class="text-base font-semibold text-gray-900 truncate" :title="order.service_type?.name || order.service_type || 'N/A'">
                      {{ order.service_type?.name || order.service_type || 'N/A' }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                      Deadline
                    </p>
                    <p
                      class="text-base font-semibold"
                      :class="getDeadlineClass(order.writer_deadline || order.client_deadline || order.deadline)"
                    >
                      {{ formatDeadline(order.writer_deadline || order.client_deadline || order.deadline) }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                      Price
                    </p>
                    <p class="text-base font-bold text-green-600 truncate">
                      ${{ formatCurrency(order.total_price) }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="flex flex-col gap-3 lg:ml-6 lg:shrink-0">
                <router-link
                  :to="`/orders/${order.id}`"
                  class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all shadow-sm text-sm whitespace-nowrap"
                >
                  View Details
                </router-link>
                <button
                  v-if="canSubmit(order)"
                  @click="submitOrder(order)"
                  :disabled="submittingOrder === order.id"
                  class="inline-flex items-center justify-center px-5 py-2.5 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm whitespace-nowrap"
                >
                  {{ submittingOrder === order.id ? 'Submitting...' : 'Submit Order' }}
                </button>
                <button
                  v-if="order.status === 'revision_requested'"
                  @click="viewRevision(order)"
                  class="inline-flex items-center justify-center px-5 py-2.5 bg-yellow-600 text-white font-semibold rounded-lg hover:bg-yellow-700 transition-all shadow-sm hover:shadow-md text-sm whitespace-nowrap"
                >
                  View Revision
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div
        v-if="pagination && pagination.total_pages > 1"
        class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white rounded-xl shadow-md p-6 mt-8"
      >
        <div class="text-sm font-medium text-gray-700">
          Showing
          <span class="font-bold text-gray-900">
            {{ pagination.start_index || 1 }}
          </span>
          to
          <span class="font-bold text-gray-900">
            {{ pagination.end_index || orders.length }}
          </span>
          of
          <span class="font-bold text-gray-900">
            {{ pagination.total_count || orders.length }}
          </span>
          orders
        </div>
        <div class="flex gap-3">
          <button
            @click="loadOrders(pagination.current_page - 1)"
            :disabled="!pagination.has_previous || loading"
            class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm text-sm"
          >
            Previous
          </button>
          <button
            @click="loadOrders(pagination.current_page + 1)"
            :disabled="!pagination.has_next || loading"
            class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm text-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>

  <!-- Priority Modal -->
  <Modal
    v-model:visible="showPriorityModalFlag"
    title="Set Order Priority"
    size="md"
  >
    <div v-if="selectedOrderForPriority" class="space-y-4">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm font-medium text-blue-900 mb-1">
          Order #{{ selectedOrderForPriority.id }}
        </p>
        <p class="text-sm text-blue-700">
          {{ selectedOrderForPriority.topic || 'No topic' }}
        </p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Priority Level
        </label>
        <select
          v-model="priorityForm.priority"
          class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
        >
          <option value="high">🔴 High Priority</option>
          <option value="medium">🟡 Medium Priority</option>
          <option value="low">🟢 Low Priority</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Notes (Optional)
        </label>
        <textarea
          v-model="priorityForm.notes"
          rows="3"
          placeholder="Add notes about why you set this priority..."
          class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 resize-none"
          maxlength="500"
        ></textarea>
        <p class="text-xs text-gray-500 mt-1">
          {{ (priorityForm.notes || '').length }}/500 characters
        </p>
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-end gap-3">
        <button
          @click="closePriorityModal"
          class="btn btn-secondary"
        >
          Cancel
        </button>
        <button
          @click="savePriority"
          :disabled="savingPriority"
          class="btn btn-primary"
        >
          {{ savingPriority ? 'Saving...' : 'Save Priority' }}
        </button>
      </div>
    </template>
  </Modal>

  <!-- Confirmation Dialog -->
  <ConfirmationDialog
    v-if="confirm.show.value"
    v-model:show="confirm.show"
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
import { ref, onMounted, computed, unref } from 'vue'
import { useRouter } from 'vue-router'
import ordersAPI from '@/api/orders'
import writerDashboardAPI from '@/api/writer-dashboard'
import { debounce } from '@/utils/debounce'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import EnhancedStatusBadge from '@/components/common/EnhancedStatusBadge.vue'

const router = useRouter()
const { error: showError, success: showSuccess } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const orders = ref([])
const pagination = ref(null)
const submittingOrder = ref(null)

const filters = ref({
  status: '',
  priority: '',
  deadline_from: '',
  deadline_to: '',
  min_payment: null,
  max_payment: null,
  client_name: '',
  service_type: '',
  subject: '',
  min_pages: null,
  max_pages: null,
})

const sortBy = ref('deadline_asc')
const searchQuery = ref('')
const showAdvancedFilters = ref(false)
const priorities = ref({})
const serviceTypes = ref([])
const showPriorityModalFlag = ref(false)
const selectedOrderForPriority = ref(null)
const priorityForm = ref({
  priority: 'medium',
  notes: '',
})
const savingPriority = ref(false)

const stats = computed(() => {
  const inProgress = orders.value.filter(o => o.status === 'in_progress').length
  const submitted = orders.value.filter(o => o.status === 'submitted' || o.status === 'under_editing').length
  const dueSoon = orders.value.filter(o => {
    const deadline = o.writer_deadline || o.client_deadline || o.deadline
    return deadline && isDueSoon(deadline)
  }).length
  
  return {
    in_progress: inProgress,
    submitted: submitted,
    due_soon: dueSoon,
    total_active: orders.value.filter(o => 
      ['in_progress', 'submitted', 'under_editing', 'revision_requested', 'on_hold'].includes(o.status)
    ).length,
  }
})

const loadOrders = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      assigned_writer: true, // Only get orders assigned to current writer
    }

    if (filters.value.status) {
      params.status = filters.value.status
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // Advanced filters
    if (filters.value.deadline_from) {
      params.writer_deadline__gte = filters.value.deadline_from
    }
    if (filters.value.deadline_to) {
      params.writer_deadline__lte = filters.value.deadline_to
    }
    if (filters.value.min_payment !== null && filters.value.min_payment !== '') {
      params.total_price__gte = filters.value.min_payment
    }
    if (filters.value.max_payment !== null && filters.value.max_payment !== '') {
      params.total_price__lte = filters.value.max_payment
    }
    if (filters.value.client_name) {
      params.client__username__icontains = filters.value.client_name
    }
    if (filters.value.service_type) {
      params.service_type__name = filters.value.service_type
    }
    if (filters.value.subject) {
      params.subject__name__icontains = filters.value.subject
    }
    if (filters.value.min_pages !== null && filters.value.min_pages !== '') {
      params.pages__gte = filters.value.min_pages
    }
    if (filters.value.max_pages !== null && filters.value.max_pages !== '') {
      params.pages__lte = filters.value.max_pages
    }

    // Handle sorting
    if (sortBy.value === 'deadline_asc') {
      params.ordering = 'writer_deadline,client_deadline,deadline'
    } else if (sortBy.value === 'deadline_desc') {
      params.ordering = '-writer_deadline,-client_deadline,-deadline'
    } else if (sortBy.value === 'created_desc') {
      params.ordering = '-created_at'
    } else if (sortBy.value === 'created_asc') {
      params.ordering = 'created_at'
    }

    const response = await ordersAPI.list(params)
    
    // Load priorities
    await loadPriorities()
    
    // Extract service types from orders for filter dropdown
    if (response.data.results) {
      const types = new Set()
      response.data.results.forEach(order => {
        if (order.service_type?.name) {
          types.add(order.service_type.name)
        } else if (order.service_type) {
          types.add(order.service_type)
        }
      })
      serviceTypes.value = Array.from(types).sort()
    }
    
    if (response.data.results) {
      orders.value = response.data.results.map(order => ({
        ...order,
        priority: priorities.value[order.id]?.priority || 'medium',
      }))
      
      // Apply priority filter
      if (filters.value.priority) {
        orders.value = orders.value.filter(
          o => o.priority === filters.value.priority
        )
      }
      
      // Apply priority sorting
      if (sortBy.value === 'priority_desc' || sortBy.value === 'priority_asc') {
        const priorityValues = { high: 3, medium: 2, low: 1 }
        orders.value.sort((a, b) => {
          const aVal = priorityValues[a.priority] || 2
          const bVal = priorityValues[b.priority] || 2
          return sortBy.value === 'priority_desc' 
            ? bVal - aVal 
            : aVal - bVal
        })
      }
      
      pagination.value = {
        current_page: response.data.current_page || page,
        total_pages: response.data.total_pages || 1,
        total_count: response.data.count || response.data.results.length,
        has_next: response.data.next !== null,
        has_previous: response.data.previous !== null,
        start_index: ((response.data.current_page || page) - 1) * (response.data.page_size || 20) + 1,
        end_index: Math.min((response.data.current_page || page) * (response.data.page_size || 20), response.data.count || response.data.results.length),
      }
    } else {
      orders.value = Array.isArray(response.data) ? response.data : []
      pagination.value = null
    }
  } catch (error) {
    console.error('Failed to load orders:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load orders. Please try again.')
    showError(errorMsg)
    orders.value = []
  } finally {
    loading.value = false
  }
}

const submitOrder = async (order) => {
  const confirmed = await confirm.showDialog(
    `Are you sure you want to submit Order #${order.id}? This will mark it as completed and send it for editing.`,
    'Submit Order',
    {
      variant: 'default',
      icon: '📤',
      confirmText: 'Submit',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return

  submittingOrder.value = order.id
  try {
    await ordersAPI.executeAction(order.id, 'submit_order')
    showSuccess('Order submitted successfully!')
    await loadOrders(pagination.value?.current_page || 1)
  } catch (error) {
    console.error('Failed to submit order:', error)
    const errorMsg = getErrorMessage(error, 'Failed to submit order. Please try again.')
    showError(errorMsg)
  } finally {
    submittingOrder.value = null
  }
}

const loadPriorities = async () => {
  try {
    const response = await writerDashboardAPI.getOrderPriorities()
    priorities.value = response.data.priorities || {}
  } catch (error) {
    console.error('Failed to load priorities:', error)
    priorities.value = {}
  }
}

const showPriorityModal = (order) => {
  selectedOrderForPriority.value = order
  priorityForm.value = {
    priority: order.priority || 'medium',
    notes: priorities.value[order.id]?.notes || '',
  }
  showPriorityModalFlag.value = true
}

const closePriorityModal = () => {
  showPriorityModalFlag.value = false
  selectedOrderForPriority.value = null
  priorityForm.value = {
    priority: 'medium',
    notes: '',
  }
}

const savePriority = async () => {
  if (!selectedOrderForPriority.value) return
  
  savingPriority.value = true
  try {
    await writerDashboardAPI.setOrderPriority(
      selectedOrderForPriority.value.id,
      {
        priority: priorityForm.value.priority,
        notes: priorityForm.value.notes,
      }
    )
    
    // Update local state
    priorities.value[selectedOrderForPriority.value.id] = {
      priority: priorityForm.value.priority,
      notes: priorityForm.value.notes,
    }
    
    // Update order in list
    const orderIndex = orders.value.findIndex(
      o => o.id === selectedOrderForPriority.value.id
    )
    if (orderIndex !== -1) {
      orders.value[orderIndex].priority = priorityForm.value.priority
    }
    
    showSuccess('Priority updated successfully!')
    closePriorityModal()
  } catch (error) {
    console.error('Failed to save priority:', error)
    const errorMsg = getErrorMessage(
      error,
      'Failed to save priority. Please try again.'
    )
    showError(errorMsg)
  } finally {
    savingPriority.value = false
  }
}

const getPriorityIcon = (priority) => {
  const icons = {
    high: '🔴',
    medium: '🟡',
    low: '🟢',
  }
  return icons[priority] || '🟡'
}

const formatPriority = (priority) => {
  return priority.charAt(0).toUpperCase() + priority.slice(1)
}

const getPriorityBadgeClass = (priority) => {
  const classes = {
    high: 'bg-red-100 text-red-700 hover:bg-red-200',
    medium: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200',
    low: 'bg-green-100 text-green-700 hover:bg-green-200',
  }
  return classes[priority] || classes.medium
}

const viewRevision = (order) => {
  router.push(`/orders/${order.id}`)
}

const canSubmit = (order) => {
  return order.status === 'in_progress' || order.status === 'on_hold'
}

const formatStatus = (status) => {
  const statusMap = {
    'in_progress': 'In Progress',
    'submitted': 'Submitted',
    'under_editing': 'Under Editing',
    'revision_requested': 'Revision Requested',
    'on_hold': 'On Hold',
    'completed': 'Completed',
    'approved': 'Approved',
  }
  return statusMap[status] || status
}

const getStatusBadgeClass = (status) => {
  const classes = {
    'in_progress': 'bg-blue-100 text-blue-700',
    'submitted': 'bg-yellow-100 text-yellow-700',
    'under_editing': 'bg-purple-100 text-purple-700',
    'revision_requested': 'bg-orange-100 text-orange-700',
    'on_hold': 'bg-gray-100 text-gray-700',
    'completed': 'bg-green-100 text-green-700',
    'approved': 'bg-green-100 text-green-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const formatDeadline = (deadline) => {
  if (!deadline) return 'No deadline'
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))

  if (diffMs < 0) {
    return `Overdue (${date.toLocaleDateString()})`
  } else if (diffDays === 0) {
    return `Today (${diffHours}h remaining)`
  } else if (diffDays === 1) {
    return `Tomorrow (${diffHours}h remaining)`
  } else if (diffDays < 7) {
    return `${diffDays} days (${date.toLocaleDateString()})`
  } else {
    return date.toLocaleDateString()
  }
}

const getDeadlineClass = (deadline) => {
  if (!deadline) return 'text-gray-500'
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMs < 0) {
    return 'text-red-600 font-bold'
  } else if (diffDays <= 1) {
    return 'text-red-600'
  } else if (diffDays <= 3) {
    return 'text-orange-600'
  } else {
    return 'text-gray-900'
  }
}

const isDueSoon = (deadline) => {
  if (!deadline) return false
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date - now
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  return diffDays <= 2 && diffMs > 0
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

const debouncedSearch = debounce(() => {
  loadOrders(1)
}, 500)

const debouncedFilter = debounce(() => {
  loadOrders(1)
}, 500)

const resetFilters = () => {
  filters.value = {
    status: '',
    priority: '',
    deadline_from: '',
    deadline_to: '',
    min_payment: null,
    max_payment: null,
    client_name: '',
    service_type: '',
    subject: '',
    min_pages: null,
    max_pages: null,
  }
  searchQuery.value = ''
  sortBy.value = 'deadline_asc'
  loadOrders(1)
}

onMounted(() => {
  loadPriorities()
  loadOrders()
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

