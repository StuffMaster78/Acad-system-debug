<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Order Queue
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Browse and request available orders
            </p>
          </div>
          <button
            @click="loadQueue"
            :disabled="loading"
            class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-50 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md transform hover:-translate-y-0.5"
          >
            <ArrowPathIcon :class="['w-5 h-5', loading && 'animate-spin']" />
            <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-blue-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">
                Available Orders
              </p>
              <p class="text-4xl font-extrabold text-blue-900">
                {{ stats.available_count || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <ClipboardDocumentListIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-purple-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-purple-600 uppercase tracking-wider mb-2">
                Preferred Orders
              </p>
              <p class="text-4xl font-extrabold text-purple-900">
                {{ stats.preferred_count || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <StarIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-amber-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-amber-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-amber-600 uppercase tracking-wider mb-2">
                My Requests
              </p>
              <p class="text-4xl font-extrabold text-amber-900">
                {{ stats.requests_count || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <DocumentTextIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
        <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-emerald-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-emerald-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <div class="relative flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2">
                Approved
              </p>
              <p class="text-4xl font-extrabold text-emerald-900">
                {{ stats.approved_count || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                <CheckCircleIcon class="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- Take Capacity -->
    <div class="bg-white rounded-lg shadow-sm border border-primary-100 p-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="text-sm font-medium text-primary-600 uppercase tracking-wide">Level Capacity</p>
        <p class="text-xl font-semibold text-gray-900 mt-1">
          {{ levelDetails?.name || 'Unranked' }}
        </p>
        <div class="space-y-2">
          <div class="flex items-center gap-4 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-gray-600">Active:</span>
              <span class="font-semibold text-gray-900">{{ takeCapacity.active }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-600">Max:</span>
              <span class="font-semibold text-gray-900">{{ takeCapacity.maxOrders }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-600">Remaining:</span>
              <span class="font-bold" :class="takeCapacity.remaining > 0 ? 'text-green-600' : 'text-red-600'">
                {{ takeCapacity.remaining }}
              </span>
            </div>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              class="h-2.5 rounded-full transition-all duration-300"
              :class="capacityBarColorClass"
              :style="{ width: `${capacityPercentage}%` }"
            ></div>
          </div>
        </div>
      </div>
      <div class="text-sm text-gray-600">
        <p v-if="!takesEnabled" class="text-red-600 font-medium">
          Taking orders directly is currently disabled by admins. Please request orders instead.
        </p>
        <p v-else-if="takeCapacity.remaining <= 0" class="text-yellow-700 font-medium">
          You’ve reached your current limit. Submit work or request a hold before taking another order.
        </p>
        <p v-else class="text-green-700 font-medium">
          You can take up to {{ takeCapacity.remaining }} more order{{ takeCapacity.remaining === 1 ? '' : 's' }} right now.
        </p>
        <p class="text-xs text-gray-500 mt-2">
          Order holds temporarily freeze deadlines while you wait for client input.
        </p>
      </div>
    </div>

      <!-- Recommended Orders -->
      <div
        v-if="recommendedOrders.length"
        class="bg-white rounded-xl shadow-md border-l-4 border-blue-600 p-6 sm:p-8 mb-8"
      >
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="space-y-2">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <SparklesIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">
                  Smart Picks
                </p>
                <h2 class="text-2xl font-extrabold text-gray-900">
                  Recommended For You
                </h2>
              </div>
            </div>
            <p class="text-sm text-gray-600 leading-relaxed max-w-2xl">
              Based on your skills, subject preferences, and earning potential.
            </p>
          </div>
          <button
            type="button"
            class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-bold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-xl transition-all border-2 border-transparent hover:border-primary-200 whitespace-nowrap"
            @click="scrollToTabs"
          >
            <span>View full queue</span>
            <ArrowRightIcon class="w-4 h-4" />
          </button>
        </div>
      <div class="mt-4 space-y-4">
        <div
          v-for="order in recommendedOrders.slice(0, 6)"
          :key="`recommended-${order.id}`"
          class="bg-gradient-to-r from-blue-50 to-white border-2 border-blue-200 rounded-xl p-5 sm:p-6 hover:shadow-lg transition-all"
        >
          <div class="flex flex-col lg:flex-row lg:items-start gap-4">
            <!-- Left Section: Order Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4 mb-3">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-xl font-bold text-gray-900">
                      Order #{{ order.id }}
                    </h3>
                    <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold uppercase">
                      {{ order.service_type || order.subject || 'General' }}
                    </span>
                    <span class="px-3 py-1.5 bg-gradient-to-r from-yellow-100 to-amber-100 text-amber-700 rounded-lg text-xs font-extrabold uppercase flex items-center gap-1.5 border border-amber-300 shadow-sm">
                      <SparklesIcon class="w-3.5 h-3.5" />
                      <span>Recommended</span>
                    </span>
                    <span v-if="order.match_score" class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold uppercase">
                      Match {{ Math.round(order.match_score) }}%
                    </span>
                  </div>
                  <p class="text-base font-semibold text-gray-900 mb-3 line-clamp-2">
                    {{ order.topic || 'Untitled order' }}
                  </p>
                </div>
                <button
                  @click="viewOrder(order)"
                  class="text-sm font-semibold text-primary-600 hover:text-primary-700 underline whitespace-nowrap shrink-0"
                >
                  View details →
                </button>
              </div>
              
              <!-- Order Details: Horizontal Layout -->
              <div class="flex flex-wrap items-center gap-4 mb-3 text-sm">
                <div class="flex items-center gap-2" v-if="order.pages">
                  <span class="text-gray-500 font-medium">Pages:</span>
                  <span class="font-bold text-gray-900">{{ order.pages }}</span>
                </div>
                <div class="flex items-center gap-2" v-if="order.price">
                  <span class="text-gray-500 font-medium">Price:</span>
                  <span class="font-bold text-green-600">${{ order.price?.toFixed(2) || '0.00' }}</span>
                </div>
                <div class="flex items-center gap-2" v-if="order.potential_payout">
                  <span class="text-gray-500 font-medium">Payout:</span>
                  <span class="font-bold text-green-700">${{ formatCurrency(order.potential_payout) }}</span>
                </div>
                <div class="flex items-center gap-2" v-if="order.deadline">
                  <span class="text-gray-500 font-medium">Deadline:</span>
                  <span class="font-semibold text-gray-900">{{ formatDate(order.deadline) }}</span>
                </div>
              </div>
              
              <!-- Match Tags -->
              <div v-if="order.match_tags?.length" class="flex flex-wrap gap-2 mb-3">
                <span
                  v-for="tag in order.match_tags.slice(0, 5)"
                  :key="`${order.id}-rec-tag-${tag}`"
                  class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold uppercase tracking-wide"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
            
            <!-- Right Section: Actions -->
            <div class="flex flex-col gap-2 lg:w-48 lg:shrink-0">
              <button
                @click="takeOrder(order)"
                :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders || isOrderRequested(order)"
                class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{
                  'bg-emerald-600 hover:bg-emerald-700 text-white': !takingOrder && canTakeOrders && !isOrderRequested(order),
                  'bg-gray-400 text-white cursor-not-allowed': !canTakeOrders || isOrderRequested(order)
                }"
                :title="!canTakeOrders ? 'You have reached your order limit' : (isOrderRequested(order) ? 'You have already requested this order' : 'Take this order immediately')"
              >
                <span v-if="takingOrder === order.id" class="animate-spin">
                  <ArrowPathIcon class="w-4 h-4" />
                </span>
                <CheckCircleIcon v-else class="w-4 h-4" />
                <span>{{ takingOrder === order.id ? 'Taking...' : 'Take Order' }}</span>
              </button>
              <button
                @click="openRequestModal(order)"
                :disabled="isOrderRequested(order) || requestingOrder === order.id || takingOrder === order.id"
                class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{
                  'bg-violet-600 hover:bg-violet-700 text-white': !isOrderRequested(order) && !requestingOrder,
                  'bg-gray-400 text-white cursor-not-allowed': isOrderRequested(order)
                }"
                :title="isOrderRequested(order) ? 'You have already requested this order' : 'Request this order (requires admin approval)'"
              >
                <span v-if="requestingOrder === order.id" class="animate-spin">
                  <ArrowPathIcon class="w-4 h-4" />
                </span>
                <CheckCircleIcon v-else-if="isOrderRequested(order)" class="w-4 h-4" />
                <ClipboardDocumentListIcon v-else class="w-4 h-4" />
                <span>{{ isOrderRequested(order) ? 'Requested' : (requestingOrder === order.id ? 'Requesting...' : 'Request') }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      </div>

    <!-- Tabs -->
    <div id="order-queue-tabs" class="bg-white rounded-lg shadow-sm">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'available'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'available'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Available Orders ({{ availableOrders.length }})
          </button>
          <button
            @click="activeTab = 'preferred'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'preferred'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Preferred Orders ({{ preferredOrders.length }})
          </button>
          <button
            @click="activeTab = 'requests'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'requests'
                ? 'border-yellow-500 text-yellow-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Pending Requests ({{ pendingRequests.length }})
          </button>
          <button
            @click="activeTab = 'accepted-requests'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'accepted-requests'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Accepted Requests ({{ acceptedRequests.length }})
          </button>
          <button
            @click="activeTab = 'pending-assignments'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'pending-assignments'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Pending Assignments ({{ pendingAssignments.length }})
          </button>
          <button
            @click="activeTab = 'pending-preferred'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'pending-preferred'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Pending Preferred ({{ pendingPreferredAssignments.length }})
          </button>
        </nav>
      </div>

        <!-- Filters -->
        <div class="p-6 border-b-2 border-gray-200 bg-gradient-to-br from-gray-50 to-white">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-md">
              <FunnelIcon class="w-5 h-5 text-white" />
            </div>
            <h3 class="text-lg font-extrabold text-gray-900">Filters & Sorting</h3>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Service Type
              </label>
              <select
                v-model="filters.service_type"
                @change="filterOrders"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
              >
                <option value="">All Types</option>
                <option
                  v-for="type in serviceTypes"
                  :key="type"
                  :value="type"
                >
                  {{ type }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Min Price
              </label>
              <input
                v-model.number="filters.min_price"
                type="number"
                @input="filterOrders"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
                placeholder="0"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Max Pages
              </label>
              <input
                v-model.number="filters.max_pages"
                type="number"
                @input="filterOrders"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm placeholder-gray-400"
                placeholder="Any"
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-700 uppercase tracking-wide mb-2">
                Sort By
              </label>
              <select
                v-model="sortOption"
                class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors shadow-sm"
              >
                <option value="default">Newest first</option>
                <option value="payout_desc">
                  Potential payout (high → low)
                </option>
                <option value="deadline_asc">Deadline (soonest)</option>
              </select>
            </div>
            <div class="flex items-end">
              <button
                @click="resetFilters"
                class="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-white border-2 border-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm hover:shadow-md"
              >
                <ArrowPathIcon class="w-4 h-4" />
                <span>Reset</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Available Orders Tab -->
        <div v-if="activeTab === 'available'" class="p-6 sm:p-8">
          <div v-if="loading" class="flex flex-col items-center justify-center py-16 gap-4">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
            <p class="text-sm font-medium text-gray-500">Loading orders...</p>
          </div>
          <div
            v-else-if="filteredAvailableOrders.length === 0"
            class="text-center py-16"
          >
            <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-6 shadow-lg">
              <InboxIcon class="w-10 h-10 text-gray-400" />
            </div>
            <p class="text-lg font-semibold text-gray-900 mb-2">
              No available orders found
            </p>
            <p class="text-sm text-gray-500">
              Try adjusting your filters or check back later.
            </p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="order in filteredAvailableOrders"
              :key="order.id"
              class="bg-white border-2 border-gray-200 rounded-xl p-5 sm:p-6 hover:shadow-lg transition-all"
            >
              <div class="flex flex-col lg:flex-row lg:items-start gap-4">
                <!-- Left Section: Order Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-4 mb-3">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-3 mb-2">
                        <h3 class="text-xl font-bold text-gray-900">
                          Order #{{ order.id }}
                        </h3>
                        <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold uppercase">
                          {{ order.service_type }}
                        </span>
                      </div>
                      <p class="text-base font-semibold text-gray-900 mb-3 line-clamp-2">
                        {{ order.topic || 'No topic' }}
                      </p>
                    </div>
                    <button
                      @click="viewOrder(order)"
                      class="text-sm font-semibold text-primary-600 hover:text-primary-700 underline whitespace-nowrap shrink-0"
                    >
                      View details →
                    </button>
                  </div>
                  
                  <!-- Order Details: Horizontal Layout -->
                  <div class="flex flex-wrap items-center gap-4 mb-3 text-sm">
                    <div class="flex items-center gap-2">
                      <span class="text-gray-500 font-medium">Pages:</span>
                      <span class="font-bold text-gray-900">{{ order.pages }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-gray-500 font-medium">Price:</span>
                      <span class="font-bold text-green-600">${{ order.price?.toFixed(2) || '0.00' }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-gray-500 font-medium">Payout:</span>
                      <span class="font-bold text-green-700">${{ formatCurrency(order.potential_payout) }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-gray-500 font-medium">Deadline:</span>
                      <span class="font-semibold text-gray-900">{{ formatDate(order.deadline) }}</span>
                    </div>
                  </div>
                  
                  <!-- Match Tags -->
                  <div
                    v-if="order.match_tags?.length"
                    class="flex flex-wrap gap-2 mb-3"
                  >
                    <span
                      v-for="tag in order.match_tags.slice(0, 5)"
                      :key="`${order.id}-tag-${tag}`"
                      class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold uppercase tracking-wide"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
                
                <!-- Right Section: Actions -->
                <div class="flex flex-col gap-2 lg:w-48 lg:shrink-0">
                  <button
                    @click="takeOrder(order)"
                    :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders || isOrderRequested(order)"
                    class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="{
                      'bg-emerald-600 hover:bg-emerald-700 text-white': !takingOrder && canTakeOrders && !isOrderRequested(order),
                      'bg-gray-400 text-white cursor-not-allowed': !canTakeOrders || isOrderRequested(order)
                    }"
                    :title="!canTakeOrders ? 'You have reached your order limit' : (isOrderRequested(order) ? 'You have already requested this order' : 'Take this order immediately')"
                  >
                    <span>{{ takingOrder === order.id ? '⏳' : '✅' }}</span>
                    <span>{{ takingOrder === order.id ? 'Taking...' : 'Take Order' }}</span>
                  </button>
                  <button
                    @click="openRequestModal(order)"
                    :disabled="isOrderRequested(order) || requestingOrder === order.id || takingOrder === order.id"
                    class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                    :class="{
                      'bg-violet-600 hover:bg-violet-700 text-white': !isOrderRequested(order) && !requestingOrder,
                      'bg-gray-400 text-white cursor-not-allowed': isOrderRequested(order)
                    }"
                    :title="isOrderRequested(order) ? 'You have already requested this order' : 'Request this order (requires admin approval)'"
                  >
                    <span>{{ requestingOrder === order.id ? '⏳' : (isOrderRequested(order) ? '✓' : '📋') }}</span>
                    <span>{{ isOrderRequested(order) ? 'Requested' : (requestingOrder === order.id ? 'Requesting...' : 'Request') }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

      <!-- Preferred Orders Tab -->
      <div v-if="activeTab === 'preferred'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="filteredPreferredOrders.length === 0" class="text-center py-12 text-gray-500">
          <p>No preferred orders found</p>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="order in filteredPreferredOrders"
            :key="order.id"
            class="bg-gradient-to-r from-purple-50 to-white border-2 border-purple-200 rounded-xl p-5 sm:p-6 hover:shadow-lg transition-all"
          >
            <div class="flex flex-col lg:flex-row lg:items-start gap-4">
              <!-- Left Section: Order Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-4 mb-3">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-3 mb-2">
                      <h3 class="text-xl font-bold text-gray-900">
                        Order #{{ order.id }}
                      </h3>
                      <span class="px-2 py-1 bg-purple-200 text-purple-800 rounded text-xs font-semibold uppercase flex items-center gap-1">
                        <span>⭐</span>
                        <span>Preferred</span>
                      </span>
                      <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold uppercase">
                        {{ order.service_type }}
                      </span>
                    </div>
                    <p class="text-base font-semibold text-gray-900 mb-3 line-clamp-2">
                      {{ order.topic || 'No topic' }}
                    </p>
                  </div>
                  <button
                    @click="viewOrder(order)"
                    class="text-sm font-semibold text-primary-600 hover:text-primary-700 underline whitespace-nowrap shrink-0"
                  >
                    View details →
                  </button>
                </div>
                
                <!-- Order Details: Horizontal Layout -->
                <div class="flex flex-wrap items-center gap-4 mb-3 text-sm">
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 font-medium">Pages:</span>
                    <span class="font-bold text-gray-900">{{ order.pages }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 font-medium">Price:</span>
                    <span class="font-bold text-green-600">${{ order.price?.toFixed(2) || '0.00' }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 font-medium">Payout:</span>
                    <span class="font-bold text-green-700">${{ formatCurrency(order.potential_payout) }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 font-medium">Deadline:</span>
                    <span class="font-semibold text-gray-900">{{ formatDate(order.deadline) }}</span>
                  </div>
                </div>
                
                <!-- Match Tags -->
                <div v-if="order.match_tags?.length" class="flex flex-wrap gap-2 mb-3">
                  <span
                    v-for="tag in order.match_tags.slice(0, 5)"
                    :key="`${order.id}-pref-tag-${tag}`"
                    class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-bold uppercase tracking-wide"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              
              <!-- Right Section: Actions -->
              <div class="flex flex-col gap-2 lg:w-48 lg:shrink-0">
                <button 
                  @click="takeOrder(order)" 
                  :disabled="takingOrder === order.id || requestingOrder === order.id || !canTakeOrders || isOrderRequested(order)" 
                  class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="{
                    'bg-emerald-600 hover:bg-emerald-700 text-white': !takingOrder && canTakeOrders && !isOrderRequested(order),
                    'bg-gray-400 text-white cursor-not-allowed': !canTakeOrders || isOrderRequested(order)
                  }"
                  :title="!canTakeOrders ? 'You have reached your order limit' : (isOrderRequested(order) ? 'You have already requested this order' : 'Take this order immediately')"
                >
                  <span>{{ takingOrder === order.id ? '⏳' : '✅' }}</span>
                  <span>{{ takingOrder === order.id ? 'Taking...' : 'Take Order' }}</span>
                </button>
                <button 
                  @click="openRequestModal(order)" 
                  :disabled="isOrderRequested(order) || requestingOrder === order.id || takingOrder === order.id" 
                  class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                  :class="{
                    'bg-violet-600 hover:bg-violet-700 text-white': !isOrderRequested(order) && !requestingOrder,
                    'bg-gray-400 text-white cursor-not-allowed': isOrderRequested(order)
                  }"
                  :title="isOrderRequested(order) ? 'You have already requested this order' : 'Request this order (requires admin approval)'"
                >
                  <span>{{ requestingOrder === order.id ? '⏳' : (isOrderRequested(order) ? '✓' : '📋') }}</span>
                  <span>{{ isOrderRequested(order) ? 'Requested' : (requestingOrder === order.id ? 'Requesting...' : 'Request') }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Requests Tab -->
      <div v-if="activeTab === 'requests'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600"></div>
        </div>
        <div v-else-if="pendingRequests.length === 0" class="text-center py-12 text-gray-500">
          <div class="flex flex-col items-center gap-3">
            <InboxIcon class="w-16 h-16 text-gray-400" />
            <div>
              <p class="text-lg font-medium text-gray-900">No pending requests</p>
              <p class="text-sm text-gray-500 mt-1">You don't have any requests waiting for approval</p>
            </div>
          </div>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="request in pendingRequests"
            :key="request.id"
            class="bg-white border-2 border-yellow-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-gray-900">Order #{{ request.order_id }}</h3>
                  <span class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold uppercase">
                    Pending Review
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Topic:</span> {{ request.order_topic || 'N/A' }}
                </p>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Requested:</span> {{ formatDate(request.created_at) }}
                </p>
                <p v-if="request.reason" class="text-sm text-gray-700 mt-3 p-3 bg-gray-50 rounded-lg">
                  <span class="font-medium">Your reason:</span> {{ request.reason }}
                </p>
              </div>
              <div class="flex flex-col gap-2 ml-4">
                <button
                  @click="viewOrder({ id: request.order_id })"
                  class="px-4 py-2 text-sm font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  View Order
                </button>
                <button
                  @click="cancelRequest(request)"
                  class="px-4 py-2 text-sm font-semibold text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                >
                  Cancel Request
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Accepted Requests Tab -->
      <div v-if="activeTab === 'accepted-requests'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
        </div>
        <div v-else-if="acceptedRequests.length === 0" class="text-center py-12 text-gray-500">
          <div class="flex flex-col items-center gap-3">
            <CheckCircleIcon class="w-16 h-16 text-gray-400" />
            <div>
              <p class="text-lg font-medium text-gray-900">No accepted requests</p>
              <p class="text-sm text-gray-500 mt-1">Accepted requests move to your "My Orders" page</p>
            </div>
          </div>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="request in acceptedRequests"
            :key="request.id"
            class="bg-white border-2 border-green-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-gray-900">Order #{{ request.order_id }}</h3>
                  <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold uppercase">
                    Accepted
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Topic:</span> {{ request.order_topic || 'N/A' }}
                </p>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Accepted:</span> {{ formatDate(request.updated_at || request.created_at) }}
                </p>
                <p class="text-sm text-emerald-600 font-semibold mt-3">
                  ✓ This order has been accepted and should now appear in your "My Orders" page
                </p>
              </div>
              <div class="flex flex-col gap-2 ml-4">
                <button
                  @click="viewOrder({ id: request.order_id })"
                  class="px-4 py-2 text-sm font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  View Order
                </button>
                <router-link
                  :to="'/writer/orders'"
                  class="px-4 py-2 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors text-center"
                >
                  Go to My Orders
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Assignments Tab -->
      <div v-if="activeTab === 'pending-assignments'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
        </div>
        <div v-else-if="pendingAssignments.length === 0" class="text-center py-12">
          <div class="flex flex-col items-center gap-3">
            <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div>
              <p class="text-lg font-medium text-gray-900">No pending assignments</p>
              <p class="text-sm text-gray-500 mt-1">You don't have any orders waiting for your acceptance</p>
            </div>
          </div>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="assignment in pendingAssignments"
            :key="assignment.id"
            class="bg-white border-2 border-orange-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-gray-900">Order #{{ assignment.order_id }}</h3>
                  <span class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-semibold uppercase">
                    Awaiting Your Response
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Assigned by:</span>
                  {{ assignment.assigned_by || 'System' }}
                </p>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Assigned at:</span>
                  {{ formatDate(assignment.assigned_at) }}
                </p>
                <div v-if="assignment.order" class="mt-3">
                  <p class="text-sm font-medium text-gray-700 mb-1">Topic:</p>
                  <p class="text-sm text-gray-900">{{ assignment.order.topic || 'N/A' }}</p>
                  <div class="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p class="text-xs font-medium text-gray-500 uppercase">Pages</p>
                      <p class="text-sm font-semibold text-gray-900">{{ assignment.order.pages || 'N/A' }}</p>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-gray-500 uppercase">Deadline</p>
                      <p class="text-sm font-semibold text-gray-900">{{ formatDate(assignment.order.deadline) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex gap-3 mt-4">
              <button
                @click="acceptAssignment(assignment)"
                :disabled="acceptingAssignment === assignment.id || rejectingAssignment === assignment.id"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="acceptingAssignment === assignment.id">⏳</span>
                <span v-else>✅</span>
                <span>{{ acceptingAssignment === assignment.id ? 'Accepting...' : 'Accept Assignment' }}</span>
              </button>
              <button
                @click="rejectAssignment(assignment)"
                :disabled="acceptingAssignment === assignment.id || rejectingAssignment === assignment.id"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="rejectingAssignment === assignment.id">⏳</span>
                <span v-else>❌</span>
                <span>{{ rejectingAssignment === assignment.id ? 'Rejecting...' : 'Reject Assignment' }}</span>
              </button>
              <button
                @click="viewOrder(assignment.order || { id: assignment.order_id })"
                class="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-lg transition-all"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Preferred Assignments Tab -->
      <div v-if="activeTab === 'pending-preferred'" class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        </div>
        <div v-else-if="pendingPreferredAssignments.length === 0" class="text-center py-12">
          <div class="flex flex-col items-center gap-3">
            <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div>
              <p class="text-lg font-medium text-gray-900">No pending preferred assignments</p>
              <p class="text-sm text-gray-500 mt-1">You don't have any preferred orders waiting for your acceptance</p>
            </div>
          </div>
        </div>
        <div v-else class="space-y-4">
          <div
            v-for="assignment in pendingPreferredAssignments"
            :key="assignment.order_id"
            class="bg-white border-2 border-purple-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-gray-900">Order #{{ assignment.order_id }}</h3>
                  <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold uppercase">
                    Preferred Writer Assignment
                  </span>
                </div>
                <p class="text-sm text-gray-600 mb-2">
                  <span class="font-medium">Created at:</span>
                  {{ formatDate(assignment.created_at) }}
                </p>
                <div v-if="assignment.order" class="mt-3">
                  <p class="text-sm font-medium text-gray-700 mb-1">Topic:</p>
                  <p class="text-sm text-gray-900">{{ assignment.order.topic || 'N/A' }}</p>
                  <div class="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p class="text-xs font-medium text-gray-500 uppercase">Pages</p>
                      <p class="text-sm font-semibold text-gray-900">{{ assignment.order.pages || 'N/A' }}</p>
                    </div>
                    <div>
                      <p class="text-xs font-medium text-gray-500 uppercase">Deadline</p>
                      <p class="text-sm font-semibold text-gray-900">{{ formatDate(assignment.order.deadline) }}</p>
                    </div>
                  </div>
                  <div v-if="assignment.order.total_price" class="mt-3">
                    <p class="text-xs font-medium text-gray-500 uppercase">Total Price</p>
                    <p class="text-sm font-semibold text-green-600">${{ formatCurrency(assignment.order.total_price) }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex gap-3 mt-4">
              <button
                @click="acceptPreferredAssignment(assignment)"
                :disabled="acceptingPreferredAssignment === assignment.order_id || rejectingPreferredAssignment === assignment.order_id"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="acceptingPreferredAssignment === assignment.order_id">⏳</span>
                <span v-else>✅</span>
                <span>{{ acceptingPreferredAssignment === assignment.order_id ? 'Accepting...' : 'Accept Assignment' }}</span>
              </button>
              <button
                @click="rejectPreferredAssignment(assignment)"
                :disabled="acceptingPreferredAssignment === assignment.order_id || rejectingPreferredAssignment === assignment.order_id"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="rejectingPreferredAssignment === assignment.order_id">⏳</span>
                <span v-else>❌</span>
                <span>{{ rejectingPreferredAssignment === assignment.order_id ? 'Rejecting...' : 'Reject Assignment' }}</span>
              </button>
              <button
                @click="viewOrder(assignment.order || { id: assignment.order_id })"
                class="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-lg transition-all"
              >
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Detail Modal -->
    <div v-if="selectedOrder" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Order #{{ selectedOrder.id }}</h2>
            <button @click="selectedOrder = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
              <p class="text-sm text-gray-900">{{ selectedOrder.service_type }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Pages</label>
              <p class="text-sm text-gray-900">{{ selectedOrder.pages }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Price</label>
              <p class="text-sm text-gray-900 font-semibold text-green-600">${{ selectedOrder.price?.toFixed(2) || '0.00' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedOrder.deadline) }}</p>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Topic</label>
            <p class="text-sm text-gray-900">{{ selectedOrder.topic || 'No topic provided' }}</p>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="selectedOrder = null" class="btn btn-secondary">Close</button>
          <button 
            v-if="takesEnabled && !isOrderRequested(selectedOrder)" 
            @click="takeOrder(selectedOrder)" 
            :disabled="takingOrder === selectedOrder.id || requestingOrder === selectedOrder.id || !canTakeOrders" 
            class="btn btn-primary"
            :title="!canTakeOrders ? 'You have reached your order limit' : 'Take this order immediately'"
          >
            {{ takingOrder === selectedOrder.id ? 'Taking...' : 'Take Order' }}
          </button>
          <button 
            v-if="!isOrderRequested(selectedOrder)"
            @click="openRequestModal(selectedOrder)" 
            :disabled="requestingOrder === selectedOrder.id || takingOrder === selectedOrder.id" 
            class="btn btn-primary"
            title="Request this order (requires admin approval)"
          >
            {{ requestingOrder === selectedOrder.id ? 'Requesting...' : 'Request Order' }}
          </button>
          <button 
            v-else
            disabled
            class="btn btn-secondary cursor-not-allowed flex items-center gap-2"
            title="You have already requested this order. Waiting for admin review."
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Already Requested
          </button>
        </div>
      </div>
    </div>

    <!-- Order Request Modal -->
    <Modal
      v-model:visible="showRequestModal"
      title="Request Order"
      size="lg"
      :scrollable="true"
      :max-height="'85vh'"
      @close="closeRequestModal"
    >
      <div v-if="selectedOrderForRequest" class="space-y-6">
        <!-- Order Summary -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-5 border-2 border-blue-200">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h3 class="text-xl font-bold text-gray-900 mb-1">Order #{{ selectedOrderForRequest.id }}</h3>
              <p class="text-base text-gray-700 font-medium">{{ selectedOrderForRequest.topic || 'Untitled Order' }}</p>
            </div>
            <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-xs font-semibold uppercase">
              {{ selectedOrderForRequest.service_type || 'Standard' }}
            </span>
          </div>
          
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div class="bg-white rounded-lg p-3 border border-blue-200">
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Pages</p>
              <p class="text-lg font-bold text-gray-900">
                {{ selectedOrderForRequest.pages || selectedOrderForRequest.number_of_pages || 0 }}
              </p>
            </div>
            <div class="bg-white rounded-lg p-3 border border-blue-200">
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Price</p>
              <p class="text-lg font-bold text-green-600">
                ${{ formatCurrency(selectedOrderForRequest.price || selectedOrderForRequest.total_cost || 0) }}
              </p>
            </div>
            <div class="bg-white rounded-lg p-3 border border-blue-200">
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Deadline</p>
              <p class="text-sm font-semibold text-gray-900">
                {{ formatDate(selectedOrderForRequest.deadline || selectedOrderForRequest.client_deadline) }}
              </p>
            </div>
            <div class="bg-white rounded-lg p-3 border border-blue-200">
              <p class="text-xs text-gray-500 uppercase tracking-wide mb-1">Subject</p>
              <p class="text-sm font-semibold text-gray-900">
                {{ selectedOrderForRequest.subject?.name || 'N/A' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Request Reason -->
        <div class="mt-6">
          <label class="block text-sm font-semibold text-gray-700 mb-2">
            Why are you interested in this order? <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="requestReason"
            rows="6"
            placeholder="Briefly explain why you're a good fit for this order (expertise, availability, experience)."
            class="w-full border-2 border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm resize-none"
            required
            :disabled="requestingOrder === selectedOrderForRequest?.id"
            @keydown.ctrl.enter="requestOrder"
            @keydown.meta.enter="requestOrder"
          ></textarea>
          <div class="mt-2 flex items-start gap-2">
            <svg class="w-5 h-5 text-blue-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-xs text-gray-600">
              <span class="font-semibold">Tip:</span> A detailed, professional reason increases your chances of being selected. 
              Be specific about your qualifications and availability.
            </p>
          </div>
          <div class="mt-2 text-xs text-gray-500">
            <span class="font-medium">Character count:</span> 
            <span :class="requestReason?.length > 500 ? 'text-green-600 font-semibold' : 'text-gray-500'">
              {{ requestReason?.length || 0 }}
            </span>
            / 500+ recommended
          </div>
        </div>

        <!-- Additional Info (if available) -->
        <div v-if="selectedOrderForRequest.instructions || selectedOrderForRequest.requirements" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-yellow-900 mb-2 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Additional Order Information
          </h4>
          <div class="text-sm text-yellow-800 space-y-1">
            <p v-if="selectedOrderForRequest.instructions" class="font-medium">Instructions:</p>
            <p v-if="selectedOrderForRequest.instructions" class="text-xs">{{ selectedOrderForRequest.instructions.substring(0, 200) }}{{ selectedOrderForRequest.instructions.length > 200 ? '...' : '' }}</p>
            <p v-if="selectedOrderForRequest.requirements" class="font-medium mt-2">Requirements:</p>
            <p v-if="selectedOrderForRequest.requirements" class="text-xs">{{ selectedOrderForRequest.requirements.substring(0, 200) }}{{ selectedOrderForRequest.requirements.length > 200 ? '...' : '' }}</p>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="requestError" class="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-red-600 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-sm font-medium text-red-800">{{ requestError }}</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex flex-col sm:flex-row justify-end gap-3 w-full" @click.stop>
          <button
            type="button"
            @click="closeRequestModal"
            :disabled="requestingOrder === selectedOrderForRequest?.id"
            class="order-2 sm:order-1 px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            @click.stop="handleSubmitClick"
            :disabled="!requestReason || !requestReason.trim() || requestingOrder === selectedOrderForRequest?.id"
            class="order-1 sm:order-2 px-8 py-3 text-base font-bold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed disabled:from-gray-400 disabled:to-gray-500 transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none relative z-10"
            style="pointer-events: auto;"
          >
            <span v-if="requestingOrder === selectedOrderForRequest?.id" class="animate-spin text-xl">⏳</span>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ requestingOrder === selectedOrderForRequest?.id ? 'Submitting Request...' : 'Submit Request' }}</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, unref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowPathIcon,
  ClipboardDocumentListIcon,
  StarIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  SparklesIcon,
  ArrowRightIcon,
  FunnelIcon,
  InboxIcon
} from '@heroicons/vue/24/outline'
import writerDashboardAPI from '@/api/writer-dashboard'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import writerManagementAPI from '@/api/writer-management'
import ordersAPI from '@/api/orders'
import writerAssignmentAPI from '@/api/writer-assignment'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { getErrorMessage } from '@/utils/errorHandler'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const { error: showError, success: showSuccess, warning: showWarning } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const activeTab = ref('available')
const availableOrders = ref([])
const preferredOrders = ref([])
const orderRequests = ref([])
const writerRequests = ref([])
const pendingAssignments = ref([])
const pendingPreferredAssignments = ref([])
const stats = ref({})
const takesEnabled = ref(false)
const acceptingAssignment = ref(null)
const rejectingAssignment = ref(null)
const acceptingPreferredAssignment = ref(null)
const rejectingPreferredAssignment = ref(null)
const assignmentReason = ref('')
const filters = ref({
  service_type: '',
  min_price: null,
  max_pages: null,
})
const selectedOrder = ref(null)
const requestingOrder = ref(null)
const takingOrder = ref(null)
const showRequestModal = ref(false)
const selectedOrderForRequest = ref(null)
const requestReason = ref('')
const requestError = ref('')
const requestedOrderIds = ref([])  // Track which orders have been requested
const writerProfile = ref(null)
const activeAssignmentCount = ref(0)
const recommendedOrders = ref([])
const sortOption = ref('default')

const serviceTypes = computed(() => {
  const types = new Set()
  availableOrders.value.forEach(o => {
    if (o.service_type) types.add(o.service_type)
  })
  preferredOrders.value.forEach(o => {
    if (o.service_type) types.add(o.service_type)
  })
  return Array.from(types).sort()
})

const allRequests = computed(() => {
  return [...orderRequests.value, ...writerRequests.value].sort((a, b) => {
    const dateA = new Date(a.created_at || 0)
    const dateB = new Date(b.created_at || 0)
    return dateB - dateA
  })
})

// Separate pending and accepted requests
const pendingRequests = computed(() => {
  return allRequests.value.filter(r => 
    r.status === 'pending' || 
    (!r.status && !r.approved && !r.accepted) ||
    (r.approved === null && r.accepted === null)
  )
})

const acceptedRequests = computed(() => {
  return allRequests.value.filter(r => 
    r.status === 'accepted' || 
    r.status === 'approved' ||
    r.accepted === true ||
    r.approved === true
  )
})

const applyFilters = (orders) => {
  let filtered = [...orders]
  if (filters.value.service_type) {
    filtered = filtered.filter(o => o.service_type === filters.value.service_type)
  }
  if (filters.value.min_price !== null && filters.value.min_price !== undefined) {
    filtered = filtered.filter(o => (o.price || 0) >= filters.value.min_price)
  }
  if (filters.value.max_pages !== null && filters.value.max_pages !== undefined) {
    filtered = filtered.filter(o => (o.pages || 0) <= filters.value.max_pages)
  }
  return filtered
}

const getDeadlineTimestamp = (order) => {
  const raw = order?.deadline || order?.created_at
  if (!raw) return Number.MAX_SAFE_INTEGER
  const date = new Date(raw)
  return Number.isNaN(date.getTime()) ? Number.MAX_SAFE_INTEGER : date.getTime()
}

const applySort = (orders) => {
  if (sortOption.value === 'default') {
    return orders
  }
  const sorted = [...orders]
  if (sortOption.value === 'payout_desc') {
    return sorted.sort((a, b) => (b.potential_payout || 0) - (a.potential_payout || 0))
  }
  if (sortOption.value === 'deadline_asc') {
    return sorted.sort((a, b) => getDeadlineTimestamp(a) - getDeadlineTimestamp(b))
  }
  return sorted
}

// Memoized filtered orders - only recompute when dependencies change
const filteredAvailableOrders = computed(() => {
  // Create a dependency key from filters and sort option
  const filterKey = `${filters.value.service_type}-${filters.value.min_price}-${filters.value.max_pages}-${sortOption.value}`
  
  // If orders haven't changed and filters haven't changed, return cached result
  const filtered = applyFilters(availableOrders.value)
  return applySort(filtered)
})

const filteredPreferredOrders = computed(() => {
  const filtered = applyFilters(preferredOrders.value)
  return applySort(filtered)
})

const levelCapacity = ref({
  level_details: null,
  max_orders: 0,
  active_orders: 0,
  remaining_slots: 0,
})

const levelDetails = computed(() => levelCapacity.value?.level_details || writerProfile.value?.writer_level_details || null)

const takeCapacity = computed(() => {
  // Use data from queue API if available, otherwise fall back to computed values
  if (levelCapacity.value && levelCapacity.value.max_orders > 0) {
    return {
      maxOrders: levelCapacity.value.max_orders,
      active: levelCapacity.value.active_orders,
      remaining: levelCapacity.value.remaining_slots,
    }
  }
  
  // Fallback to computed values
  const maxOrders = levelDetails.value?.max_orders || 0
  const active = activeAssignmentCount.value
  const remaining = Math.max(0, maxOrders - active)
  return { maxOrders, active, remaining }
})

const canTakeOrders = computed(() => takesEnabled.value && takeCapacity.value.remaining > 0)

const capacityPercentage = computed(() => {
  if (takeCapacity.value.maxOrders === 0) return 0
  return Math.min(100, (takeCapacity.value.active / takeCapacity.value.maxOrders) * 100)
})

const capacityColorClass = computed(() => {
  const percentage = capacityPercentage.value
  if (percentage >= 100) return 'text-red-600'
  if (percentage >= 80) return 'text-yellow-600'
  return 'text-green-600'
})

const capacityBarColorClass = computed(() => {
  const percentage = capacityPercentage.value
  if (percentage >= 100) return 'bg-red-500'
  if (percentage >= 80) return 'bg-yellow-500'
  if (percentage >= 60) return 'bg-orange-500'
  return 'bg-green-500'
})

const loadQueue = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getOrderQueue()
    const data = response.data
    
    if (typeof data.takes_enabled === 'boolean') {
      takesEnabled.value = data.takes_enabled
    }
    availableOrders.value = data.available_orders || []
    preferredOrders.value = data.preferred_orders || []
    recommendedOrders.value = data.recommended_orders || []
    orderRequests.value = data.order_requests || []
    writerRequests.value = data.writer_requests || []
    
    // Update level capacity from queue response
    if (data.level_capacity) {
      levelCapacity.value = {
        level_details: data.level_capacity.level_details || null,
        max_orders: data.level_capacity.max_orders || 0,
        active_orders: data.level_capacity.active_orders || 0,
        remaining_slots: data.level_capacity.remaining_slots || 0,
      }
      // Also update activeAssignmentCount to keep it in sync
      activeAssignmentCount.value = data.level_capacity.active_orders || 0
    }
    
    // Track requested order IDs
    requestedOrderIds.value = data.requested_order_ids || []
    
    // Also mark orders as requested if they're in the requests list
    const allRequestedIds = new Set(requestedOrderIds.value)
    orderRequests.value.forEach(r => {
      if (r.order_id) allRequestedIds.add(r.order_id)
    })
    writerRequests.value.forEach(r => {
      if (r.order_id) allRequestedIds.add(r.order_id)
    })
    requestedOrderIds.value = Array.from(allRequestedIds)
    
    stats.value = {
      available_count: availableOrders.value.length,
      preferred_count: preferredOrders.value.length,
      requests_count: pendingRequests.value.length,
      approved_count: acceptedRequests.value.length,
    }
  } catch (error) {
    console.error('Failed to load order queue:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load order queue. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const loadWriterContext = async () => {
  try {
    const profileResponse = await writerManagementAPI.getMyProfile()
    writerProfile.value = profileResponse.data
  } catch (error) {
    console.error('Failed to load writer profile:', error)
  }
  await loadActiveAssignments()
}

const loadActiveAssignments = async () => {
  try {
    const response = await ordersAPI.list({
      assigned_writer: true,
      status__in: 'in_progress,under_editing,revision_requested,on_hold',
      page_size: 1,
    })
    if (typeof response.data?.count === 'number') {
      activeAssignmentCount.value = response.data.count
    } else {
      const results = response.data?.results || response.data || []
      activeAssignmentCount.value = results.length
    }
  } catch (error) {
    console.error('Failed to load active assignments:', error)
  }
}

const isOrderRequested = (order) => {
  if (!order || !order.id) return false
  const orderId = order.id
  return (
    requestedOrderIds.value.includes(orderId) ||
    order.is_requested ||
    orderRequests.value.some(r => r.order_id === orderId) ||
    writerRequests.value.some(r => r.order_id === orderId)
  )
}

const openRequestModal = (order) => {
  if (!order || !order.id) return
  
  // Check if already requested
  if (isOrderRequested(order)) {
    showWarning('You have already requested this order. Please wait for admin review.')
    return
  }
  
  selectedOrderForRequest.value = order
  requestReason.value = ''
  requestError.value = ''
  showRequestModal.value = true
  
  // Focus the textarea after modal opens
  setTimeout(() => {
    const textarea = document.querySelector('textarea[placeholder*="Please provide"]')
    if (textarea) {
      textarea.focus()
    }
  }, 100)
}

const closeRequestModal = () => {
  if (requestingOrder.value) {
    // Don't close if request is in progress
    return
  }
  showRequestModal.value = false
  selectedOrderForRequest.value = null
  requestReason.value = ''
  requestError.value = ''
}

const handleSubmitClick = (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  console.log('Submit button clicked', { 
    requestReason: requestReason.value, 
    hasReason: !!requestReason.value?.trim(),
    selectedOrder: selectedOrderForRequest.value?.id,
    requestingOrder: requestingOrder.value,
    isDisabled: !requestReason.value || !requestReason.value.trim() || requestingOrder.value === selectedOrderForRequest.value?.id
  })
  
  // Check if button should be disabled
  if (!requestReason.value || !requestReason.value.trim()) {
    requestError.value = 'Please provide a reason for requesting this order.'
    return
  }
  
  requestOrder(event)
}

const requestOrder = async (event) => {
  // Prevent default behavior
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  const order = selectedOrderForRequest.value
  if (!order || !order.id) return
  
  // Prevent duplicate requests
  if (requestingOrder.value === order.id) {
    return
  }
  
  // Validate reason
  const reason = requestReason.value?.trim() || ''
  if (!reason) {
    requestError.value = 'Please provide a reason for requesting this order.'
    return
  }
  
  if (reason.length < 20) {
    requestError.value = 'Please provide a more detailed reason (at least 20 characters).'
    return
  }
  
  requestError.value = ''
  
  if (reason.length > 2000) {
    showError('Reason is too long (maximum 2000 characters).')
    return
  }
  
  // Check if already requested
  if (isOrderRequested(order)) {
    showWarning('You have already requested this order. Please wait for admin review.')
    closeRequestModal()
    return
  }
  
  requestingOrder.value = order.id
  
  // Optimistic update: mark order as requested immediately
  const orderId = order.id
  if (!requestedOrderIds.value.includes(orderId)) {
    requestedOrderIds.value.push(orderId)
  }
  
  try {
    await writerOrderRequestsAPI.create({
      order_id: order.id,
      reason: reason,
    })
    
    // Refresh queue to get latest state
    await loadQueue()
    
    showSuccess('Order request submitted successfully! Your request is pending admin review.')
    requestError.value = ''
    closeRequestModal()
    
    if (selectedOrder.value && selectedOrder.value.id === order.id) {
      selectedOrder.value = null
    }
  } catch (error) {
    console.error('Failed to request order:', error)
    
    // Revert optimistic update on error
    requestedOrderIds.value = requestedOrderIds.value.filter(id => id !== orderId)
    
    const errorMsg = getErrorMessage(error, 'Failed to request order. Please try again.')
    requestError.value = errorMsg
    
    // Provide more specific error messages
    if (errorMsg.includes('already requested') || errorMsg.includes('already')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('limit reached') || errorMsg.includes('maximum')) {
      showWarning(errorMsg)
    } else {
      showError(errorMsg)
    }
  } finally {
    requestingOrder.value = null
  }
}

const takeOrder = async (order) => {
  if (!order || !order.id) return
  
  // Prevent duplicate takes
  if (takingOrder.value === order.id) {
    return
  }
  
  // Check if already requested or taken
  if (isOrderRequested(order)) {
    showWarning('You have already requested this order. Please wait for admin review.')
    return
  }
  
  // Validate capacity
  if (!canTakeOrders.value) {
    if (!takesEnabled.value) {
      showWarning('Taking orders directly is currently disabled. Please submit a request instead.')
    } else {
      showWarning(
        `You have reached your current take limit (${takeCapacity.value.maxOrders} orders). ` +
        'Submit existing work or request a hold before taking another order.'
      )
    }
    return
  }
  
  // Confirm action
  const confirmed = await confirm.showDialog(
    `Are you sure you want to take Order #${order.id}?`,
    'Take Order',
    {
      details: `This will assign it to you immediately and you'll be responsible for completing it by the deadline.\n\nCurrent capacity: ${takeCapacity.value.active}/${takeCapacity.value.maxOrders} orders`,
      variant: 'default',
      icon: '📋',
      confirmText: 'Take Order',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) {
    return
  }
  
  takingOrder.value = order.id
  
  // Optimistic update: remove from available orders immediately
  const orderId = order.id
  const wasInAvailable = availableOrders.value.some(o => o.id === orderId)
  const wasInPreferred = preferredOrders.value.some(o => o.id === orderId)
  const wasInRecommended = recommendedOrders.value.some(o => o.id === orderId)
  
  if (wasInAvailable) {
    availableOrders.value = availableOrders.value.filter(o => o.id !== orderId)
  }
  if (wasInPreferred) {
    preferredOrders.value = preferredOrders.value.filter(o => o.id !== orderId)
  }
  if (wasInRecommended) {
    recommendedOrders.value = recommendedOrders.value.filter(o => o.id !== orderId)
  }
  
  // Optimistically update capacity
  const previousActiveCount = activeAssignmentCount.value
  activeAssignmentCount.value = Math.min(activeAssignmentCount.value + 1, takeCapacity.value.maxOrders)
  
  try {
    await writerOrderRequestsAPI.createTake({
      order: order.id,
    })
    
    // Refresh queue and assignments to get latest state
    await Promise.all([
      loadQueue(),
      loadActiveAssignments()
    ])
    
    showSuccess(`Order #${order.id} taken successfully! It has been assigned to you.`)
    
    // Close modal if open
    if (selectedOrder.value && selectedOrder.value.id === order.id) {
      selectedOrder.value = null
    }
  } catch (error) {
    console.error('Failed to take order:', error)
    
    // Revert optimistic updates on error
    if (wasInAvailable || wasInPreferred || wasInRecommended) {
      await loadQueue()
    }
    activeAssignmentCount.value = previousActiveCount
    
    const errorMsg = getErrorMessage(error, 'Failed to take order. Please try again.')
    
    // Provide more specific error messages
    if (errorMsg.includes('already assigned') || errorMsg.includes('already taken')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('not available') || errorMsg.includes('status')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('limit') || errorMsg.includes('maximum')) {
      showWarning(errorMsg)
    } else if (errorMsg.includes('disabled')) {
      showWarning(errorMsg)
    } else {
      showError(errorMsg)
    }
  } finally {
    takingOrder.value = null
  }
}

const viewOrder = (order) => {
  // Navigate to full order detail page so writers can access everything
  // including files, links, instructions, messages, etc.
  if (order && order.id) {
    router.push(`/orders/${order.id}`)
  }
}

const resetFilters = () => {
  filters.value = {
    service_type: '',
    min_price: null,
    max_pages: null,
  }
  sortOption.value = 'default'
}

const filterOrders = () => {
  // Filters are reactive, no action needed
}

const cancelRequest = async (request) => {
  if (!request || !request.id) return
  
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to cancel your request for Order #${request.order_id}? This action cannot be undone.`,
    'Cancel Order Request'
  )
  
  if (!confirmed) return
  
  try {
    // Try to cancel via writer order requests API
    if (request.type === 'writer_request') {
      await writerOrderRequestsAPI.delete(request.id)
    } else {
      // For regular order requests, try the same endpoint
      await writerOrderRequestsAPI.delete(request.id)
    }
    
    showSuccess('Order request cancelled successfully')
    await loadQueue()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to cancel order request. Please try again.')
    showError(errorMsg)
  }
}

const getRequestStatus = (request) => {
  if (request.approved) return 'Approved'
  if (request.status === 'accepted') return 'Accepted'
  if (request.status === 'pending') return 'Pending'
  if (request.status === 'rejected' || request.status === 'declined') return 'Rejected'
  if (request.status === 'expired') return 'Expired'
  return 'Pending'
}

const getRequestStatusBadgeClass = (request) => {
  if (request.approved || request.status === 'accepted') return 'bg-green-100 text-green-800'
  if (request.status === 'pending') return 'bg-yellow-100 text-yellow-800'
  if (request.status === 'rejected' || request.status === 'declined' || request.status === 'expired') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const formatCurrency = (value) => Number(value || 0).toFixed(2)

const scrollToTabs = () => {
  activeTab.value = 'available'
  // Scroll to tabs section after a short delay to ensure tab is active
  setTimeout(() => {
    const tabsElement = document.getElementById('order-queue-tabs')
    if (tabsElement) {
      tabsElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 100)
}

// Removed requestOrderFromCard - now using openRequestModal directly

// Load pending assignments
const loadPendingAssignments = async () => {
  try {
    const response = await writerAssignmentAPI.getPendingAssignments()
    pendingAssignments.value = response.data || []
  } catch (error) {
    console.error('Failed to load pending assignments:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load pending assignments.')
    if (!errorMsg.includes('Only writers')) {
      showError(errorMsg)
    }
  }
}

// Accept an assignment
const acceptAssignment = async (assignment) => {
  if (!assignment || !assignment.id) return
  
  const confirmed = await confirm.showDialog(
    `Accept Assignment for Order #${assignment.order_id}?`,
    'Accept Assignment',
    {
      details: 'Once accepted, the order will move to "In Progress" and you\'ll be responsible for completing it.',
      variant: 'default',
      icon: '✅',
      confirmText: 'Accept',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  acceptingAssignment.value = assignment.id
  
  try {
    await writerAssignmentAPI.acceptAssignment(assignment.id, assignmentReason.value)
    showSuccess(`Assignment accepted! Order #${assignment.order_id} is now in progress.`)
    
    // Remove from pending list
    pendingAssignments.value = pendingAssignments.value.filter(a => a.id !== assignment.id)
    
    // Refresh queue and active assignments
    await Promise.all([
      loadQueue(),
      loadActiveAssignments()
    ])
  } catch (error) {
    console.error('Failed to accept assignment:', error)
    const errorMsg = getErrorMessage(error, 'Failed to accept assignment. Please try again.')
    showError(errorMsg)
  } finally {
    acceptingAssignment.value = null
    assignmentReason.value = ''
  }
}

// Reject an assignment
const rejectAssignment = async (assignment) => {
  if (!assignment || !assignment.id) return
  
  const confirmed = await confirm.showDestructive(
    `Reject Assignment for Order #${assignment.order_id}?`,
    'Reject Assignment',
    {
      details: 'This will return the order to the available pool. Please provide a reason if possible.',
      variant: 'destructive',
      icon: '❌',
      confirmText: 'Reject',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  rejectingAssignment.value = assignment.id
  
  try {
    await writerAssignmentAPI.rejectAssignment(assignment.id, assignmentReason.value)
    showSuccess(`Assignment rejected. Order #${assignment.order_id} has been returned to the available pool.`)
    
    // Remove from pending list
    pendingAssignments.value = pendingAssignments.value.filter(a => a.id !== assignment.id)
    
    // Refresh queue
    await loadQueue()
  } catch (error) {
    console.error('Failed to reject assignment:', error)
    const errorMsg = getErrorMessage(error, 'Failed to reject assignment. Please try again.')
    showError(errorMsg)
  } finally {
    rejectingAssignment.value = null
    assignmentReason.value = ''
  }
}

// Load pending preferred assignments
const loadPendingPreferredAssignments = async () => {
  try {
    const response = await writerAssignmentAPI.getPendingPreferredAssignments()
    pendingPreferredAssignments.value = response.data || []
  } catch (error) {
    console.error('Failed to load pending preferred assignments:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load pending preferred assignments.')
    if (!errorMsg.includes('Only writers')) {
      showError(errorMsg)
    }
  }
}

// Accept a preferred assignment
const acceptPreferredAssignment = async (assignment) => {
  if (!assignment || !assignment.order_id) return
  
  const confirmed = await confirm.showDialog(
    `Accept Preferred Assignment for Order #${assignment.order_id}?`,
    'Accept Preferred Assignment',
    {
      details: 'Once accepted, the order will move to "In Progress" and you\'ll be responsible for completing it.',
      variant: 'default',
      icon: '✅',
      confirmText: 'Accept',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  acceptingPreferredAssignment.value = assignment.order_id
  
  try {
    await writerAssignmentAPI.acceptPreferredAssignment(assignment.order_id)
    showSuccess(`Preferred assignment accepted! Order #${assignment.order_id} is now in progress.`)
    
    // Remove from pending list
    pendingPreferredAssignments.value = pendingPreferredAssignments.value.filter(a => a.order_id !== assignment.order_id)
    
    // Refresh queue and active assignments
    await Promise.all([
      loadQueue(),
      loadActiveAssignments()
    ])
  } catch (error) {
    console.error('Failed to accept preferred assignment:', error)
    const errorMsg = getErrorMessage(error, 'Failed to accept preferred assignment. Please try again.')
    showError(errorMsg)
  } finally {
    acceptingPreferredAssignment.value = null
  }
}

// Reject a preferred assignment
const rejectPreferredAssignment = async (assignment) => {
  if (!assignment || !assignment.order_id) return
  
  const confirmed = await confirm.showDestructive(
    `Reject Preferred Assignment for Order #${assignment.order_id}?`,
    'Reject Preferred Assignment',
    {
      details: 'This will return the order to the available pool. Please provide a reason if possible.',
      variant: 'destructive',
      icon: '❌',
      confirmText: 'Reject',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  rejectingPreferredAssignment.value = assignment.order_id
  
  try {
    await writerAssignmentAPI.rejectPreferredAssignment(assignment.order_id, assignmentReason.value)
    showSuccess(`Preferred assignment rejected. Order #${assignment.order_id} has been returned to the available pool.`)
    
    // Remove from pending list
    pendingPreferredAssignments.value = pendingPreferredAssignments.value.filter(a => a.order_id !== assignment.order_id)
    
    // Refresh queue
    await loadQueue()
  } catch (error) {
    console.error('Failed to reject preferred assignment:', error)
    const errorMsg = getErrorMessage(error, 'Failed to reject preferred assignment. Please try again.')
    showError(errorMsg)
  } finally {
    rejectingPreferredAssignment.value = null
    assignmentReason.value = ''
  }
}

// Watch for tab changes to load pending assignments
watch(activeTab, (newTab) => {
  if (newTab === 'pending-assignments') {
    loadPendingAssignments()
  } else if (newTab === 'pending-preferred') {
    loadPendingPreferredAssignments()
  }
})

onMounted(() => {
  loadQueue()
  loadWriterContext()
  loadPendingAssignments()
  loadPendingPreferredAssignments()
})
</script>

