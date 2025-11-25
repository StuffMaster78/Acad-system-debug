<template>
  <div class="loyalty-management">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Loyalty Management</h1>
      <p class="text-gray-600 mt-2">Manage loyalty points, conversion rates, tiers, and analytics</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Points Issued</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalPointsIssued?.toLocaleString() || 0 }}</p>
          </div>
          <div class="text-blue-500 text-3xl">🎁</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Points Redeemed</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalPointsRedeemed?.toLocaleString() || 0 }}</p>
          </div>
          <div class="text-green-500 text-3xl">💎</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Active Clients</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.activeClients || 0 }}</p>
          </div>
          <div class="text-purple-500 text-3xl">👥</div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Pending Redemptions</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.pendingRedemptions || 0 }}</p>
          </div>
          <div class="text-orange-500 text-3xl">⏳</div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- Conversion Configuration Tab -->
        <div v-if="activeTab === 'conversion'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Conversion Rate Configuration</h2>
          </div>
          
          <div class="bg-gray-50 rounded-lg p-6 max-w-2xl">
            <form @submit.prevent="saveConversionConfig" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Conversion Rate (Points per $1)
                </label>
                <input
                  v-model.number="conversionConfig.conversion_rate"
                  type="number"
                  step="0.01"
                  min="0"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., 10.00"
                  required
                />
                <p class="text-xs text-gray-500 mt-1">How many loyalty points equal $1 in wallet credit</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Minimum Points for Conversion
                </label>
                <input
                  v-model.number="conversionConfig.minimum_points"
                  type="number"
                  min="0"
                  class="w-full border rounded px-3 py-2"
                  placeholder="e.g., 100"
                  required
                />
                <p class="text-xs text-gray-500 mt-1">Minimum points required to convert to wallet</p>
              </div>
              
              <div class="flex items-center">
                <input
                  v-model="conversionConfig.active"
                  type="checkbox"
                  id="active"
                  class="mr-2"
                />
                <label for="active" class="text-sm font-medium text-gray-700">
                  Active
                </label>
              </div>
              
              <div class="flex gap-3">
                <button
                  type="submit"
                  :disabled="savingConfig"
                  class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {{ savingConfig ? 'Saving...' : 'Save Configuration' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Point Management Tab -->
        <div v-if="activeTab === 'points'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Point Management</h2>
            <div class="flex gap-2">
              <button
                @click="showAwardModal = true"
                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Award Points
              </button>
              <button
                @click="showDeductModal = true"
                class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Revoke/Deduct Points
              </button>
              <button
                @click="showTransferModal = true"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Transfer Points
              </button>
            </div>
          </div>

          <!-- Recent Transactions -->
          <div>
            <h3 class="text-lg font-semibold mb-3">Recent Transactions</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="transaction in recentTransactions" :key="transaction.id">
                    <td class="px-4 py-3 text-sm">{{ transaction.client?.user?.username || 'N/A' }}</td>
                    <td class="px-4 py-3 text-sm font-medium" :class="transaction.points > 0 ? 'text-green-600' : 'text-red-600'">
                      {{ transaction.points > 0 ? '+' : '' }}{{ transaction.points }}
                    </td>
                    <td class="px-4 py-3 text-sm">
                      <span class="px-2 py-1 text-xs rounded" :class="getTransactionTypeClass(transaction.transaction_type)">
                        {{ transaction.transaction_type }}
                      </span>
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ transaction.reason || '-' }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(transaction.timestamp) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Tiers Management Tab -->
        <div v-if="activeTab === 'tiers'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Loyalty Tiers</h2>
            <button
              @click="openTierModal()"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Add Tier
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Threshold</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discount %</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Perks</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="tier in tiers" :key="tier.id">
                  <td class="px-4 py-3 text-sm font-medium">{{ tier.name }}</td>
                  <td class="px-4 py-3 text-sm">{{ tier.threshold }} points</td>
                  <td class="px-4 py-3 text-sm">{{ tier.discount_percentage }}%</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ tier.perks || '-' }}</td>
                  <td class="px-4 py-3 text-sm">
                    <button
                      @click="openTierModal(tier)"
                      class="text-blue-600 hover:text-blue-800 mr-3"
                    >
                      Edit
                    </button>
                    <button
                      @click="deleteTier(tier.id)"
                      class="text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Transactions Tab -->
        <div v-if="activeTab === 'transactions'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">All Transactions</h2>
            <div class="flex gap-2">
              <input
                v-model="transactionFilters.search"
                @input="debouncedLoadTransactions"
                type="text"
                placeholder="Search by client..."
                class="border rounded px-3 py-2"
              />
              <select
                v-model="transactionFilters.type"
                @change="loadTransactions"
                class="border rounded px-3 py-2"
              >
                <option value="">All Types</option>
                <option value="add">Add</option>
                <option value="deduct">Deduct</option>
                <option value="redeem">Redeem</option>
                <option value="transfer_in">Transfer In</option>
                <option value="transfer_out">Transfer Out</option>
              </select>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="transaction in transactions" :key="transaction.id">
                  <td class="px-4 py-3 text-sm">{{ transaction.client?.user?.username || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm font-medium" :class="transaction.points > 0 ? 'text-green-600' : 'text-red-600'">
                    {{ transaction.points > 0 ? '+' : '' }}{{ transaction.points }}
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span class="px-2 py-1 text-xs rounded" :class="getTransactionTypeClass(transaction.transaction_type)">
                      {{ transaction.transaction_type }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ transaction.reason || '-' }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(transaction.timestamp) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Redemptions Tab -->
        <div v-if="activeTab === 'redemptions'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Redemption Requests</h2>
            <div class="flex gap-2">
              <select
                v-model="redemptionFilters.status"
                @change="loadRedemptions"
                class="border rounded px-3 py-2"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="redemption in redemptions" :key="redemption.id">
                  <td class="px-4 py-3 text-sm">{{ redemption.client?.user?.username || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm">{{ redemption.item?.name || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm font-medium">{{ redemption.points_used }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span class="px-2 py-1 text-xs rounded" :class="getStatusClass(redemption.status)">
                      {{ redemption.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ formatDate(redemption.created_at) }}</td>
                  <td class="px-4 py-3 text-sm">
                    <div v-if="redemption.status === 'pending'" class="flex gap-2">
                      <button
                        @click="approveRedemption(redemption.id)"
                        class="text-green-600 hover:text-green-800"
                      >
                        Approve
                      </button>
                      <button
                        @click="rejectRedemption(redemption.id)"
                        class="text-red-600 hover:text-red-800"
                      >
                        Reject
                      </button>
                    </div>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Analytics Tab -->
        <div v-if="activeTab === 'analytics'" class="space-y-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-semibold">Loyalty Analytics</h2>
            <div class="flex gap-2">
              <input
                v-model="analyticsDateFrom"
                type="date"
                class="border rounded px-3 py-2"
              />
              <input
                v-model="analyticsDateTo"
                type="date"
                class="border rounded px-3 py-2"
              />
              <button
                @click="calculateAnalytics"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Calculate Analytics
              </button>
            </div>
          </div>

          <!-- Analytics Overview -->
          <div v-if="analyticsData" class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-semibold mb-2">Active Clients</h3>
              <p class="text-2xl font-bold">{{ analyticsData.total_active_clients || 0 }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-semibold mb-2">Points Issued</h3>
              <p class="text-2xl font-bold">{{ analyticsData.total_points_issued?.toLocaleString() || 0 }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-semibold mb-2">Points Redeemed</h3>
              <p class="text-2xl font-bold">{{ analyticsData.total_points_redeemed?.toLocaleString() || 0 }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-semibold mb-2">Points Balance</h3>
              <p class="text-2xl font-bold">{{ analyticsData.total_points_balance?.toLocaleString() || 0 }}</p>
            </div>
          </div>

          <!-- Tier Distribution -->
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-3">Tier Distribution</h3>
            <div v-if="tierDistribution.length > 0" class="bg-white rounded-lg p-4">
              <div v-for="tier in tierDistribution" :key="tier.tier_name" class="mb-2">
                <div class="flex justify-between items-center mb-1">
                  <span class="font-medium">{{ tier.tier_name }}</span>
                  <span class="text-sm text-gray-600">{{ tier.count }} clients ({{ tier.percentage }}%)</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full"
                    :style="{ width: `${tier.percentage}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Top Redemptions -->
          <div>
            <h3 class="text-lg font-semibold mb-3">Top Redemption Items</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points Required</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Redemptions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="item in topRedemptions" :key="item.id">
                    <td class="px-4 py-3 text-sm">{{ item.name }}</td>
                    <td class="px-4 py-3 text-sm">{{ item.points_required }}</td>
                    <td class="px-4 py-3 text-sm font-medium">{{ item.total_redemptions || 0 }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Award Points Modal -->
    <div v-if="showAwardModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">Award Points</h3>
        <form @submit.prevent="handleAwardPoints" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Client ID</label>
            <input
              v-model.number="pointForm.client_id"
              type="number"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Points</label>
            <input
              v-model.number="pointForm.points"
              type="number"
              min="1"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Reason</label>
            <textarea
              v-model="pointForm.reason"
              class="w-full border rounded px-3 py-2"
              rows="3"
              required
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="processingPoint"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {{ processingPoint ? 'Processing...' : 'Award Points' }}
            </button>
            <button
              type="button"
              @click="showAwardModal = false"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Deduct Points Modal -->
    <div v-if="showDeductModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">Revoke/Deduct Points</h3>
        <form @submit.prevent="handleDeductPoints" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Client ID</label>
            <input
              v-model.number="pointForm.client_id"
              type="number"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Points to Deduct</label>
            <input
              v-model.number="pointForm.points"
              type="number"
              min="1"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Reason</label>
            <textarea
              v-model="pointForm.reason"
              class="w-full border rounded px-3 py-2"
              rows="3"
              placeholder="e.g., Points expired, Policy violation, etc."
              required
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="processingPoint"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {{ processingPoint ? 'Processing...' : 'Deduct Points' }}
            </button>
            <button
              type="button"
              @click="showDeductModal = false"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Transfer Points Modal -->
    <div v-if="showTransferModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">Transfer Points</h3>
        <form @submit.prevent="handleTransferPoints" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">From Client ID</label>
            <input
              v-model.number="transferForm.from_client_id"
              type="number"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">To Client ID</label>
            <input
              v-model.number="transferForm.to_client_id"
              type="number"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Points</label>
            <input
              v-model.number="transferForm.points"
              type="number"
              min="1"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Reason</label>
            <textarea
              v-model="transferForm.reason"
              class="w-full border rounded px-3 py-2"
              rows="3"
              required
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="processingPoint"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {{ processingPoint ? 'Processing...' : 'Transfer Points' }}
            </button>
            <button
              type="button"
              @click="showTransferModal = false"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tier Modal -->
    <div v-if="showTierModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4">{{ editingTier ? 'Edit Tier' : 'Add Tier' }}</h3>
        <form @submit.prevent="saveTier" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input
              v-model="tierForm.name"
              type="text"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Threshold (Points)</label>
            <input
              v-model.number="tierForm.threshold"
              type="number"
              min="0"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Discount Percentage</label>
            <input
              v-model.number="tierForm.discount_percentage"
              type="number"
              step="0.01"
              min="0"
              max="100"
              class="w-full border rounded px-3 py-2"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Perks</label>
            <textarea
              v-model="tierForm.perks"
              class="w-full border rounded px-3 py-2"
              rows="3"
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="savingTier"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {{ savingTier ? 'Saving...' : 'Save Tier' }}
            </button>
            <button
              type="button"
              @click="closeTierModal"
              class="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { loyaltyAPI } from '@/api'
import { debounce } from '@/utils/debounce'

const activeTab = ref('conversion')
const tabs = [
  { id: 'conversion', label: 'Conversion Config' },
  { id: 'points', label: 'Point Management' },
  { id: 'tiers', label: 'Tiers' },
  { id: 'transactions', label: 'Transactions' },
  { id: 'redemptions', label: 'Redemptions' },
  { id: 'analytics', label: 'Analytics' },
]

// Stats
const stats = ref({
  totalPointsIssued: 0,
  totalPointsRedeemed: 0,
  activeClients: 0,
  pendingRedemptions: 0,
})

// Conversion Config
const conversionConfig = ref({
  conversion_rate: 0,
  minimum_points: 0,
  active: true,
})
const savingConfig = ref(false)

// Point Management
const showAwardModal = ref(false)
const showDeductModal = ref(false)
const showTransferModal = ref(false)
const processingPoint = ref(false)
const pointForm = ref({
  client_id: null,
  points: null,
  reason: '',
})
const transferForm = ref({
  from_client_id: null,
  to_client_id: null,
  points: null,
  reason: '',
})
const recentTransactions = ref([])

// Tiers
const tiers = ref([])
const showTierModal = ref(false)
const editingTier = ref(null)
const tierForm = ref({
  name: '',
  threshold: 0,
  discount_percentage: 0,
  perks: '',
})
const savingTier = ref(false)

// Transactions
const transactions = ref([])
const transactionFilters = ref({
  search: '',
  type: '',
})

// Redemptions
const redemptions = ref([])
const redemptionFilters = ref({
  status: '',
})

// Analytics
const analyticsData = ref(null)
const analyticsDateFrom = ref('')
const analyticsDateTo = ref('')
const tierDistribution = ref([])
const topRedemptions = ref([])

// Load data
const loadStats = async () => {
  try {
    // Load recent transactions to calculate stats
    const txnResponse = await loyaltyAPI.listTransactions({ page_size: 100 }).catch(() => ({ data: { results: [] } }))
    const allTransactions = txnResponse.data?.results || txnResponse.data || []
    
    stats.value.totalPointsIssued = allTransactions
      .filter(t => t.points > 0)
      .reduce((sum, t) => sum + t.points, 0)
    
    stats.value.totalPointsRedeemed = Math.abs(allTransactions
      .filter(t => t.points < 0)
      .reduce((sum, t) => sum + t.points, 0))
    
    // Load redemptions for pending count
    const redemptionsResponse = await loyaltyAPI.listRedemptionRequests({ status: 'pending' }).catch(() => ({ data: { results: [] } }))
    stats.value.pendingRedemptions = redemptionsResponse.data?.results?.length || redemptionsResponse.data?.length || 0
    
    // Active clients would need a separate endpoint
    stats.value.activeClients = new Set(allTransactions.map(t => t.client?.id).filter(Boolean)).size
  } catch (error) {
    console.error('Error loading stats:', error)
    // Set defaults on error
    stats.value = {
      totalPointsIssued: 0,
      totalPointsRedeemed: 0,
      activeClients: 0,
      pendingRedemptions: 0,
    }
  }
}

const loadConversionConfig = async () => {
  try {
    const response = await loyaltyAPI.getConversionConfig()
    // Handle both list and single object responses
    const configData = Array.isArray(response.data) 
      ? (response.data.length > 0 ? response.data[0] : null)
      : response.data
    
    if (configData) {
      conversionConfig.value = {
        conversion_rate: configData.conversion_rate || 0,
        minimum_points: configData.minimum_points || 0,
        active: configData.active !== false,
      }
    } else {
      // Config doesn't exist yet, use defaults
      conversionConfig.value = {
        conversion_rate: 10,
        minimum_points: 100,
        active: true,
      }
    }
  } catch (error) {
    if (error.response?.status === 404) {
      // Config doesn't exist yet, use defaults
      conversionConfig.value = {
        conversion_rate: 10,
        minimum_points: 100,
        active: true,
      }
    } else {
      console.error('Error loading conversion config:', error)
      // Use defaults on error
      conversionConfig.value = {
        conversion_rate: 10,
        minimum_points: 100,
        active: true,
      }
    }
  }
}

const saveConversionConfig = async () => {
  savingConfig.value = true
  try {
    await loyaltyAPI.updateConversionConfig(conversionConfig.value)
    alert('Conversion configuration saved successfully!')
  } catch (error) {
    console.error('Error saving conversion config:', error)
    alert('Error saving configuration: ' + (error.response?.data?.detail || error.message))
  } finally {
    savingConfig.value = false
  }
}

const loadRecentTransactions = async () => {
  try {
    const response = await loyaltyAPI.listTransactions({ page_size: 10 })
    recentTransactions.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading recent transactions:', error)
    recentTransactions.value = []
  }
}

const loadTransactions = async () => {
  try {
    const params = {}
    if (transactionFilters.value.type) {
      params.transaction_type = transactionFilters.value.type
    }
    const response = await loyaltyAPI.listTransactions(params)
    transactions.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading transactions:', error)
    transactions.value = []
  }
}

const debouncedLoadTransactions = debounce(loadTransactions, 500)

const handleAwardPoints = async () => {
  processingPoint.value = true
  try {
    await loyaltyAPI.awardPoints({
      client_id: pointForm.value.client_id,
      points: pointForm.value.points,
      reason: pointForm.value.reason,
    })
    alert('Points awarded successfully!')
    showAwardModal.value = false
    pointForm.value = { client_id: null, points: null, reason: '' }
    loadRecentTransactions()
    loadTransactions()
    loadStats()
  } catch (error) {
    console.error('Error awarding points:', error)
    alert('Error awarding points: ' + (error.response?.data?.detail || error.message))
  } finally {
    processingPoint.value = false
  }
}

const handleDeductPoints = async () => {
  processingPoint.value = true
  try {
    await loyaltyAPI.deductPoints({
      client_id: pointForm.value.client_id,
      points: pointForm.value.points,
      reason: pointForm.value.reason,
    })
    alert('Points deducted successfully!')
    showDeductModal.value = false
    pointForm.value = { client_id: null, points: null, reason: '' }
    loadRecentTransactions()
    loadTransactions()
    loadStats()
  } catch (error) {
    console.error('Error deducting points:', error)
    alert('Error deducting points: ' + (error.response?.data?.detail || error.message))
  } finally {
    processingPoint.value = false
  }
}

const handleTransferPoints = async () => {
  processingPoint.value = true
  try {
    await loyaltyAPI.transferPoints(transferForm.value)
    alert('Points transferred successfully!')
    showTransferModal.value = false
    transferForm.value = { from_client_id: null, to_client_id: null, points: null, reason: '' }
    loadRecentTransactions()
    loadTransactions()
    loadStats()
  } catch (error) {
    console.error('Error transferring points:', error)
    alert('Error transferring points: ' + (error.response?.data?.detail || error.message))
  } finally {
    processingPoint.value = false
  }
}

const loadTiers = async () => {
  try {
    const response = await loyaltyAPI.listTiers()
    tiers.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading tiers:', error)
    tiers.value = []
  }
}

const openTierModal = (tier = null) => {
  editingTier.value = tier
  if (tier) {
    tierForm.value = {
      name: tier.name,
      threshold: tier.threshold,
      discount_percentage: tier.discount_percentage,
      perks: tier.perks || '',
    }
  } else {
    tierForm.value = {
      name: '',
      threshold: 0,
      discount_percentage: 0,
      perks: '',
    }
  }
  showTierModal.value = true
}

const closeTierModal = () => {
  showTierModal.value = false
  editingTier.value = null
  tierForm.value = {
    name: '',
    threshold: 0,
    discount_percentage: 0,
    perks: '',
  }
}

const saveTier = async () => {
  savingTier.value = true
  try {
    if (editingTier.value) {
      await loyaltyAPI.updateTier(editingTier.value.id, tierForm.value)
    } else {
      await loyaltyAPI.createTier(tierForm.value)
    }
    alert('Tier saved successfully!')
    closeTierModal()
    loadTiers()
  } catch (error) {
    console.error('Error saving tier:', error)
    alert('Error saving tier: ' + (error.response?.data?.detail || error.message))
  } finally {
    savingTier.value = false
  }
}

const deleteTier = async (id) => {
  if (!confirm('Are you sure you want to delete this tier?')) return
  
  try {
    await loyaltyAPI.deleteTier(id)
    alert('Tier deleted successfully!')
    loadTiers()
  } catch (error) {
    console.error('Error deleting tier:', error)
    alert('Error deleting tier: ' + (error.response?.data?.detail || error.message))
  }
}

const loadRedemptions = async () => {
  try {
    const params = {}
    if (redemptionFilters.value.status) {
      params.status = redemptionFilters.value.status
    }
    const response = await loyaltyAPI.listRedemptionRequests(params)
    redemptions.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Error loading redemptions:', error)
    redemptions.value = []
  }
}

const approveRedemption = async (id) => {
  try {
    await loyaltyAPI.approveRedemption(id)
    alert('Redemption approved!')
    loadRedemptions()
    loadStats()
  } catch (error) {
    console.error('Error approving redemption:', error)
    alert('Error approving redemption: ' + (error.response?.data?.detail || error.message))
  }
}

const rejectRedemption = async (id) => {
  const reason = prompt('Enter rejection reason:')
  if (!reason) return
  
  try {
    await loyaltyAPI.rejectRedemption(id, { reason })
    alert('Redemption rejected!')
    loadRedemptions()
  } catch (error) {
    console.error('Error rejecting redemption:', error)
    alert('Error rejecting redemption: ' + (error.response?.data?.detail || error.message))
  }
}

const calculateAnalytics = async () => {
  try {
    // Only calculate if we have dates or if explicitly called
    const data = {}
    if (analyticsDateFrom.value) data.date_from = analyticsDateFrom.value
    if (analyticsDateTo.value) data.date_to = analyticsDateTo.value
    
    // If no dates provided, try to load existing analytics or skip calculation
    if (!analyticsDateFrom.value && !analyticsDateTo.value) {
      // Just load tier distribution and top redemptions without calculating
      try {
        const [tierDist, topRed] = await Promise.all([
          loyaltyAPI.getTierDistribution().catch(() => ({ data: [] })),
          loyaltyAPI.getTopRedemptions(10).catch(() => ({ data: [] })),
        ])
        
        tierDistribution.value = tierDist.data || []
        topRedemptions.value = topRed.data || []
      } catch (err) {
        console.error('Error loading analytics data:', err)
      }
      return
    }
    
    const response = await loyaltyAPI.calculateAnalytics(data)
    analyticsData.value = response.data
    
    // Load additional analytics
    const [tierDist, topRed] = await Promise.all([
      loyaltyAPI.getTierDistribution().catch(() => ({ data: [] })),
      loyaltyAPI.getTopRedemptions(10).catch(() => ({ data: [] })),
    ])
    
    tierDistribution.value = tierDist.data || []
    topRedemptions.value = topRed.data || []
  } catch (error) {
    console.error('Error calculating analytics:', error)
    // Don't show alert on initial load, just log
    if (analyticsDateFrom.value || analyticsDateTo.value) {
      alert('Error calculating analytics: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString()
}

const getTransactionTypeClass = (type) => {
  const classes = {
    add: 'bg-green-100 text-green-800',
    deduct: 'bg-red-100 text-red-800',
    redeem: 'bg-blue-100 text-blue-800',
    transfer_in: 'bg-purple-100 text-purple-800',
    transfer_out: 'bg-orange-100 text-orange-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

// Watch for tab changes
watch(activeTab, (newTab) => {
  if (newTab === 'tiers') {
    loadTiers()
  } else if (newTab === 'transactions') {
    loadTransactions()
  } else if (newTab === 'redemptions') {
    loadRedemptions()
  } else if (newTab === 'analytics') {
    calculateAnalytics()
  }
})

onMounted(async () => {
  // Load critical data first, then load tab-specific data
  try {
    await Promise.all([
      loadStats(),
      loadConversionConfig(),
      loadRecentTransactions(),
    ])
    
    // Load tab-specific data (these can fail without blocking)
    loadTiers().catch(err => console.error('Error loading tiers:', err))
    loadTransactions().catch(err => console.error('Error loading transactions:', err))
    loadRedemptions().catch(err => console.error('Error loading redemptions:', err))
    
    // Analytics can be loaded later or on tab switch
    if (activeTab.value === 'analytics') {
      calculateAnalytics().catch(err => console.error('Error loading analytics:', err))
    }
  } catch (error) {
    console.error('Error initializing component:', error)
  }
})
</script>

<style scoped>
.loyalty-management {
  padding: 1.5rem;
}
</style>

