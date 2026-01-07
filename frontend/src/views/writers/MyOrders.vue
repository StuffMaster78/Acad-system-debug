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
          
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-blue-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">
                In Progress
              </p>
              <p class="text-4xl font-extrabold text-blue-900">
                {{ stats.in_progress || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <PencilIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-amber-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-amber-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-amber-600 uppercase tracking-wider mb-2">
                Due Soon
              </p>
              <p class="text-4xl font-extrabold text-amber-900">
                {{ stats.due_soon || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <ClockIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-emerald-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2">
                Submitted
              </p>
              <p class="text-4xl font-extrabold text-emerald-900">
                {{ stats.submitted || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <PaperAirplaneIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-indigo-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-indigo-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-2">
                Total Active
              </p>
              <p class="text-4xl font-extrabold text-indigo-900">
                {{ stats.total_active || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <ChartBarIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-100">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h3 class="text-xl font-extrabold text-gray-900 flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-md">
              <FunnelIcon class="w-5 h-5 text-white" />
            </div>
            <span>Filters & Search</span>
          </h3>
          <div class="flex items-center gap-3">
            <button
              @click="showAdvancedFilters = !showAdvancedFilters"
              class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition-all border-2 border-transparent hover:border-primary-200"
            >
              <ChevronDownIcon :class="['w-4 h-4 transition-transform', showAdvancedFilters && 'rotate-180']" />
              <span>{{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced</span>
            </button>
            <button
              @click="resetFilters"
              class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-xl transition-all border-2 border-transparent hover:border-gray-200"
            >
              <ArrowPathIcon class="w-4 h-4" />
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
          <label class="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
            <MagnifyingGlassIcon class="w-4 h-4 text-gray-500" />
            <span>Search</span>
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon class="w-5 h-5 text-gray-400" />
            </div>
            <input
              v-model="searchQuery"
              @input="debouncedSearch"
              type="text"
              placeholder="Search by topic or order ID..."
              class="w-full border-2 border-gray-200 rounded-xl pl-10 pr-4 py-2.5 text-sm font-medium focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
            />
          </div>
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

      <!-- Orders Table -->
      <div v-else class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <!-- Table Controls -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-gray-50 border-b border-gray-200">
          <div class="flex items-center gap-2">
            <label class="text-sm text-gray-700">Show</label>
            <select
              v-model="pagination.itemsPerPage"
              @change="loadOrders(1)"
              class="border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <label class="text-sm text-gray-700">entries</label>
          </div>
          <div class="flex items-center gap-2">
            <label class="text-sm text-gray-700">Search:</label>
            <input
              v-model="searchQuery"
              @input="debouncedSearch"
              type="text"
              placeholder="Search orders..."
              class="border border-gray-300 rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-48"
            />
          </div>
                </div>
                
        <div class="overflow-x-auto max-h-96 sm:max-h-[420px] border border-gray-200 rounded-lg shadow-inner">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr class="bg-teal-50">
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">#</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Status
                    </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Writer
                        </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Paper Topic
                        </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Writer Deadline
                        </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Editor Deadline
                        </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Client Deadline
                        </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Paper Subject
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Pages / Cost
                  </div>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="order in orders"
                :key="order.id"
                class="hover:bg-gray-50 transition-colors cursor-pointer bg-gray-50"
                            :class="{
                  'bg-orange-50 hover:bg-orange-100': order.status === 'revision_requested',
                  'bg-red-50 hover:bg-red-100 border-l-4 border-red-500': isOverdue(order.writer_deadline || order.client_deadline || order.deadline) && isInProgress(order),
                  'bg-amber-50 hover:bg-amber-100 border-l-4 border-amber-500': isDueSoon(order) && isInProgress(order) && !isOverdue(order.writer_deadline || order.client_deadline || order.deadline)
                }"
                @click="$router.push(`/orders/${order.id}`)"
              >
                <!-- Order ID with green circle icon -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span class="text-white text-xs font-bold">+</span>
                        </div>
                    <span class="text-sm font-medium text-gray-900">{{ order.id }}</span>
                        </div>
                </td>
                
                <!-- Status -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <OrderStatusTooltip :status="order.status" position="bottom">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold text-white bg-green-700">
                      {{ formatStatus(order.status) }}
                    </span>
                  </OrderStatusTooltip>
                </td>
                
                <!-- Writer -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900">
                    {{ order.assigned_writer?.username || order.assigned_writer?.email || order.writer_username || 'Unassigned' }}
                  </span>
                </td>
                
                <!-- Paper Topic -->
                <td class="px-4 py-3 max-w-xs sm:max-w-sm">
                  <span class="text-sm text-gray-900 truncate">
                    {{ getShortTitle(order.topic) }}
                  </span>
                </td>
                
                <!-- Writer Deadline -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900">
                    {{ formatTableDeadline(order.writer_deadline) }}
                  </span>
                </td>
                
                <!-- Editor Deadline -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900">
                    {{ formatTableDeadline(order.editor_deadline) }}
                  </span>
                </td>
                
                <!-- Client Deadline -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900">
                    {{ formatTableDeadline(order.client_deadline || order.deadline) }}
                  </span>
                </td>
                
                <!-- Paper Subject -->
                <td class="px-4 py-3">
                  <span class="text-sm text-gray-900">
                    {{ order.subject?.name || order.subject || 'N/A' }}
                  </span>
                </td>
                
                <!-- Pages / Cost -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900">
                    {{ order.pages || order.number_of_pages || 0 }}/ $ {{ formatCurrency(order.writer_compensation || order.total_price || 0) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
      </div>

      <!-- Pagination -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-gray-50 border-t border-gray-200">
          <div class="text-sm text-gray-700">
          Showing
            <span class="font-semibold text-gray-900">
              {{ pagination?.start_index || 1 }}
          </span>
          to
            <span class="font-semibold text-gray-900">
              {{ pagination?.end_index || orders.length }}
          </span>
          of
            <span class="font-semibold text-gray-900">
              {{ pagination?.total_count || orders.length }}
          </span>
            entries
        </div>
          <div class="flex items-center gap-2">
          <button
              @click="loadOrders(pagination?.current_page - 1 || 1)"
              :disabled="!pagination?.has_previous || loading"
              class="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>
          <button
              v-for="page in getPaginationPages()"
              :key="page"
              @click="loadOrders(page)"
              :class="[
                'px-3 py-1.5 text-sm font-medium rounded transition-colors',
                page === (pagination?.current_page || 1)
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button
              @click="loadOrders(pagination?.current_page + 1 || 1)"
              :disabled="!pagination?.has_next || loading"
              class="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
          </div>
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
import { ref, onMounted, computed, unref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowPathIcon,
  PencilIcon,
  ClockIcon,
  PaperAirplaneIcon,
  ChartBarIcon,
  FunnelIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'
import ordersAPI from '@/api/orders'
import writerDashboardAPI from '@/api/writer-dashboard'
import { debounce } from '@/utils/debounce'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import OrderStatusTooltip from '@/components/common/OrderStatusTooltip.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import EnhancedStatusBadge from '@/components/common/EnhancedStatusBadge.vue'

const router = useRouter()
const route = useRoute()
const { error: showError, success: showSuccess } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const orders = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  has_next: false,
  has_previous: false,
  start_index: 0,
  end_index: 0,
  itemsPerPage: 10
})
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
    console.log('Loading orders, page:', page) // Debug log
    
    const itemsPerPage = pagination.value?.itemsPerPage || 50
    const params = {
      page,
      page_size: itemsPerPage,
      // Note: Backend automatically filters by assigned_writer for writers
      // We'll filter to only assigned orders on the frontend if needed
    }
    
    console.log('API params:', params) // Debug log

    // Handle archived query parameter
    if (route.query.archived === 'true') {
      params.include_archived = true
      params.only_archived = true
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
    
    console.log('Orders API Response:', response) // Debug log
    
    // Load priorities in background (don't block order loading)
    loadPriorities().catch(err => {
      console.warn('Failed to load priorities:', err)
    })
    
    // Handle different response structures
    let ordersList = []
    if (response.data) {
      if (Array.isArray(response.data.results)) {
        ordersList = response.data.results
      } else if (Array.isArray(response.data)) {
        ordersList = response.data
      }
    }
    
    // Extract service types from orders for filter dropdown
    if (ordersList.length > 0) {
      const types = new Set()
      ordersList.forEach(order => {
        if (order.service_type?.name) {
          types.add(order.service_type.name)
        } else if (order.service_type) {
          types.add(order.service_type)
        }
      })
      serviceTypes.value = Array.from(types).sort()
    }
    
    // Filter to only show assigned orders (not available or requested orders)
    // Backend returns assigned + available + requested, but "My Orders" should only show assigned
    // Check both assigned_writer (object) and assigned_writer_id (ID field)
    const assignedOrders = ordersList.filter(order => {
      // Order is assigned if either assigned_writer object exists or assigned_writer_id is set
      const hasAssignedWriter = (order.assigned_writer !== null && order.assigned_writer !== undefined) ||
                                (order.assigned_writer_id !== null && order.assigned_writer_id !== undefined)
      return hasAssignedWriter
    })
    
    console.log(`Total orders: ${ordersList.length}, Assigned orders: ${assignedOrders.length}`) // Debug log
    
    orders.value = assignedOrders.map(order => ({
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
      
    // Set pagination (itemsPerPage already declared above)
    if (response.data && response.data.results) {
      pagination.value = {
        current_page: response.data.current_page || page,
        total_pages: response.data.total_pages || 1,
        total_count: response.data.count || assignedOrders.length,
        has_next: response.data.next !== null,
        has_previous: response.data.previous !== null,
        start_index: ((response.data.current_page || page) - 1) * itemsPerPage + 1,
        end_index: Math.min((response.data.current_page || page) * itemsPerPage, response.data.count || assignedOrders.length),
        itemsPerPage: itemsPerPage
      }
    } else {
      pagination.value = {
        current_page: page,
        total_pages: 1,
        total_count: assignedOrders.length,
        has_next: false,
        has_previous: false,
        start_index: 1,
        end_index: assignedOrders.length,
        itemsPerPage: itemsPerPage
      }
    }
  } catch (error) {
    console.error('Failed to load orders:', error)
    console.error('Error details:', error.response || error.message)
    console.error('Error stack:', error.stack)
    
    // Always clear loading state
    loading.value = false
    
    const errorMsg = getErrorMessage(error, 'Failed to load orders. Please try again.')
    showError(errorMsg)
    orders.value = []
    pagination.value = {
      current_page: page,
      total_pages: 1,
      total_count: 0,
      has_next: false,
      has_previous: false,
      start_index: 0,
      end_index: 0,
    }
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

const isOverdue = (deadline) => {
  if (!deadline) return false
  const date = new Date(deadline)
  const now = new Date()
  return date < now
}

const isDueSoon = (order) => {
  const deadline = order.writer_deadline || order.client_deadline || order.deadline
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const now = new Date()
  const hours = (deadlineDate - now) / 3600000
  // Consider "due soon" if deadline is within 48 hours (2 days) and not yet overdue
  return hours > 0 && hours <= 48
}

const isInProgress = (order) => {
  // Treat only truly active states as “in progress” for overdue highlighting.
  // Submitted / approved / closed should NOT be marked as overdue.
  const inProgressStatuses = ['in_progress', 'under_editing', 'on_revision', 'revision_requested', 'assigned']
  return inProgressStatuses.includes(order.status)
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

const formatTableDeadline = (deadline) => {
  if (!deadline) return 'N/A'
  const date = new Date(deadline)
  const day = String(date.getDate()).padStart(2, '0')
  const month = date.toLocaleDateString('en-US', { month: 'short' })
  const year = date.getFullYear()
  const hours = date.getHours()
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const ampm = hours >= 12 ? 'PM' : 'AM'
  const displayHours = hours % 12 || 12
  return `${day}/${month}/${year} ${displayHours}:${minutes} ${ampm}`
}

const getShortTitle = (topic) => {
  const base = topic || 'No topic'
  const maxLength = 50
  if (base.length <= maxLength) return base
  return base.slice(0, maxLength) + '…'
}

const getPaginationPages = () => {
  if (!pagination.value || pagination.value.total_pages <= 1) {
    return [1]
  }
  const current = pagination.value.current_page || 1
  const total = pagination.value.total_pages || 1
  
  // Show max 5 page numbers
  const pages = []
  if (total <= 5) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
    } else if (current >= total - 2) {
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      for (let i = current - 2; i <= current + 2; i++) {
        pages.push(i)
      }
    }
  }
  return pages
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

// Watch for route query changes (especially archived parameter)
watch(
  () => route.query.archived,
  (newArchived) => {
    // Reload orders when archived parameter changes
    loadOrders(1)
  }
)

onMounted(() => {
  loadPriorities()
  // Check if archived parameter is in route
  if (route.query.archived === 'true') {
    loadOrders(1)
  } else {
  loadOrders()
  }
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

