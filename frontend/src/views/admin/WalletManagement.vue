<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4">
    <PageHeader
      title="Wallet Management"
      subtitle="Comprehensive wallet management with transaction history"
      @refresh="loadWallets"
    >
      <template #actions>
        <button 
          @click="exportWallets"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
          title="Export to CSV"
        >
          📥 Export
        </button>
      </template>
    </PageHeader>

    <!-- Wallet Type Tabs -->
    <div class="bg-white rounded-lg shadow border border-gray-200">
      <div class="flex border-b border-gray-200">
        <button
          @click="activeTab = 'clients'"
          :class="[
            'flex-1 px-6 py-4 text-sm font-medium transition-colors border-b-2',
            activeTab === 'clients'
              ? 'border-blue-500 text-blue-600 bg-blue-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          ]"
        >
          <div class="flex items-center justify-center gap-2">
            <div class="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Client Wallets</span>
            <span v-if="summary && activeTab === 'clients'" class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
              {{ summary.total_wallets || 0 }}
            </span>
          </div>
        </button>
        <button
          @click="activeTab = 'writers'"
          :class="[
            'flex-1 px-6 py-4 text-sm font-medium transition-colors border-b-2',
            activeTab === 'writers'
              ? 'border-emerald-500 text-emerald-600 bg-emerald-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          ]"
        >
          <div class="flex items-center justify-center gap-2">
            <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
            <span>Writer Wallets</span>
            <span v-if="writerWallets.length > 0 && activeTab === 'writers'" class="px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
              {{ writerWallets.length }}
            </span>
          </div>
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-4 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-4 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Quick Wallet Adjustment Section -->
    <div v-if="activeTab === 'clients'" class="bg-white p-6 rounded-lg shadow border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-semibold text-gray-900">Quick Wallet Adjustment</h2>
          <p class="text-sm text-gray-600 mt-1">Top up or debit a client wallet by searching for their email or username</p>
        </div>
        <button 
          @click="showQuickAdjust = !showQuickAdjust"
          class="px-4 py-2 text-sm border rounded hover:bg-gray-50"
        >
          {{ showQuickAdjust ? 'Hide' : 'Show' }} Form
        </button>
      </div>

      <div v-if="showQuickAdjust" class="space-y-4">
        <!-- Search Client -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Search Client (Email or Username)</label>
            <div class="flex gap-2">
              <input 
                v-model="quickAdjust.clientSearch"
                @keyup.enter="searchClientWallet"
                type="text" 
                placeholder="Enter client email or username..."
                class="flex-1 border rounded px-3 py-2"
              />
              <button 
                @click="searchClientWallet"
                :disabled="!quickAdjust.clientSearch || searchingWallet"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ searchingWallet ? 'Searching...' : 'Search' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Client Wallet Info -->
        <div v-if="foundWallet" class="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="min-w-0 overflow-hidden">
              <p class="text-xs text-gray-600 mb-1">Client</p>
              <p class="font-semibold text-gray-900 truncate">{{ getUserName(foundWallet.user) }}</p>
              <p class="text-sm text-gray-600 truncate">{{ foundWallet.user?.email }}</p>
            </div>
            <div class="min-w-0 overflow-hidden">
              <p class="text-xs text-gray-600 mb-1">Website</p>
              <p class="font-semibold text-gray-900 truncate">{{ foundWallet.website?.name || 'N/A' }}</p>
            </div>
            <div class="min-w-0 overflow-hidden">
              <p class="text-xs text-gray-600 mb-1">Current Balance</p>
              <p :class="getBalanceColor(foundWallet.balance)" class="text-xl sm:text-2xl font-bold break-all">
                {{ formatCurrency(foundWallet.balance) }}
              </p>
            </div>
            <div class="min-w-0 overflow-hidden">
              <p class="text-xs text-gray-600 mb-1">Loyalty Points</p>
              <p class="text-lg sm:text-xl font-semibold text-gray-900 break-all">{{ (foundWallet.loyalty_points || 0).toLocaleString() }}</p>
            </div>
          </div>
        </div>

        <!-- Adjustment Form -->
        <div v-if="foundWallet" class="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <label class="block text-sm font-medium mb-1">
              Amount <span class="text-gray-500">(Positive = Top Up, Negative = Debit)</span>
            </label>
            <input 
              v-model.number="quickAdjust.amount" 
              type="number" 
              step="0.01"
              placeholder="e.g., 50.00 or -25.00"
              class="w-full border rounded px-3 py-2"
              :class="parseFloat(quickAdjust.amount || 0) < 0 ? 'border-red-300' : 'border-gray-300'"
            />
            <p class="text-xs text-gray-500 mt-1">
              <span v-if="parseFloat(quickAdjust.amount || 0) > 0" class="text-green-600 font-medium">
                ✓ Will add ${{ Math.abs(parseFloat(quickAdjust.amount || 0)).toFixed(2) }} to wallet
                <span v-if="foundWallet" class="ml-2">
                  → New balance: ${{ (parseFloat(foundWallet.balance || 0) + parseFloat(quickAdjust.amount || 0)).toFixed(2) }}
                </span>
              </span>
              <span v-else-if="parseFloat(quickAdjust.amount || 0) < 0" class="text-red-600 font-medium">
                ⚠ Will deduct ${{ Math.abs(parseFloat(quickAdjust.amount || 0)).toFixed(2) }} from wallet
                <span v-if="foundWallet" class="ml-2">
                  → New balance: ${{ (parseFloat(foundWallet.balance || 0) + parseFloat(quickAdjust.amount || 0)).toFixed(2) }}
                  <span v-if="(parseFloat(foundWallet.balance || 0) + parseFloat(quickAdjust.amount || 0)) < 0" class="text-red-800 font-bold">
                    (WARNING: Negative balance!)
                  </span>
                </span>
              </span>
              <span v-else class="text-gray-500">
                Enter positive amount to top up, negative to debit
              </span>
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Transaction Type</label>
            <select v-model="quickAdjust.transaction_type" class="w-full border rounded px-3 py-2">
              <option value="adjustment">Adjustment</option>
              <option value="top-up">Top-Up</option>
              <option value="refund">Refund</option>
              <option value="bonus">Bonus</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Reason/Description *</label>
            <textarea 
              v-model="quickAdjust.reason" 
              required
              rows="2"
              placeholder="Reason for this adjustment..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
          </div>
          <div class="md:col-span-2 flex gap-2">
            <button 
              @click="submitQuickAdjustment"
              :disabled="!quickAdjust.amount || !quickAdjust.reason || processingQuickAdjust"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ processingQuickAdjust ? 'Processing...' : (parseFloat(quickAdjust.amount || 0) >= 0 ? 'Top Up Wallet' : 'Debit Wallet') }}
            </button>
            <button 
              @click="resetQuickAdjust"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Reset
            </button>
          </div>
        </div>

        <div v-if="!foundWallet && quickAdjust.clientSearch && !searchingWallet" class="text-center py-4 text-gray-500">
          No wallet found. Make sure the client exists and has a wallet.
        </div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="summary || activeTab === 'writers'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-if="activeTab === 'clients' && summary" class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-blue-700 truncate">Client Total Balance</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-blue-900 break-all leading-tight" :title="`$${clientTotalBalance.toFixed(2)} (from visible list)`">
          ${{ formatCurrency(clientTotalBalance) }}
        </p>
        <p class="text-xs text-blue-600">{{ clientWallets.length }} wallets (visible)</p>
      </div>
      <div v-if="activeTab === 'clients' && summary" class="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg shadow border border-indigo-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-indigo-700 truncate">Client Wallets</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-indigo-900 break-all leading-tight">
          {{ clientWallets.length }}
        </p>
        <p class="text-xs text-indigo-600">{{ pagination?.count ? `of ${pagination.count} total` : 'visible wallets' }}</p>
      </div>
      <div v-if="activeTab === 'clients' && summary" class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow border border-purple-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-purple-700 truncate">Loyalty Points</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-purple-900 break-all leading-tight">
          {{ clientTotalLoyaltyPoints.toLocaleString() }}
        </p>
        <p class="text-xs text-purple-600">from visible wallets</p>
      </div>
      <div v-if="activeTab === 'clients' && summary" class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow border border-orange-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-orange-700 truncate">Avg Balance</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-orange-900 break-all leading-tight">
          ${{ formatCurrency(clientWallets.length ? (clientTotalBalance / clientWallets.length) : 0) }}
        </p>
        <p class="text-xs text-orange-600">per visible wallet</p>
      </div>
      <div v-if="activeTab === 'writers'" class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg shadow border border-emerald-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-emerald-700 truncate">Writer Total Balance</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-emerald-900 break-all leading-tight" :title="`$${writerTotalBalance.toFixed(2)}`">
          ${{ formatCurrency(writerTotalBalance) }}
        </p>
        <p class="text-xs text-emerald-600">{{ writerWallets.length }} wallets</p>
      </div>
      <div v-if="activeTab === 'writers'" class="bg-gradient-to-br from-teal-50 to-teal-100 rounded-lg shadow border border-teal-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-teal-700 truncate">Writer Wallets</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-teal-900 break-all leading-tight">
          {{ writerWallets.length }}
        </p>
        <p class="text-xs text-teal-600">active wallets</p>
      </div>
      <div v-if="activeTab === 'writers'" class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow border border-green-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-green-700 truncate">Total Earnings</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-green-900 break-all leading-tight" :title="`$${writerTotalEarnings.toFixed(2)}`">
          ${{ formatCurrency(writerTotalEarnings) }}
        </p>
        <p class="text-xs text-green-600">total earnings</p>
      </div>
      <div v-if="activeTab === 'writers'" class="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg shadow border border-cyan-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-cyan-700 truncate">Avg Balance</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-cyan-900 break-all leading-tight">
          ${{ formatCurrency(writerWallets.length ? (writerTotalBalance / writerWallets.length) : 0) }}
        </p>
        <p class="text-xs text-cyan-600">per wallet</p>
      </div>
    </div>

    <!-- Website Totals (Client Wallets Only) -->
    <div v-if="activeTab === 'clients' && summary && summary.website_totals && summary.website_totals.length" class="bg-white p-6 rounded-lg shadow border border-gray-200">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Client Wallet Balance by Website</h2>
        <button 
          @click="showWebsiteTotals = !showWebsiteTotals"
          class="text-sm text-blue-600 hover:text-blue-800"
        >
          {{ showWebsiteTotals ? 'Hide' : 'Show' }} Details
        </button>
      </div>
      <div v-if="showWebsiteTotals" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Domain</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Balance</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Wallets</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Balance</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="site in summary.website_totals" :key="site.website__id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ site.website__name || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <a :href="site.website__domain" target="_blank" class="text-blue-600 hover:underline">
                  {{ site.website__domain || 'N/A' }}
                </a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-right text-green-600">
                ${{ parseFloat(site.total_balance || 0).toFixed(2) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-right">
                {{ site.wallet_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-600">
                ${{ site.wallet_count ? (parseFloat(site.total_balance || 0) / site.wallet_count).toFixed(2) : '0.00' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <button 
                  @click="filterByWebsite(site.website__id)"
                  class="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                >
                  View Wallets
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="(site, index) in summary.website_totals.slice(0, 3)" :key="site.website__id" 
          :class="[
            'p-4 rounded-lg min-w-0 overflow-hidden h-28 flex flex-col justify-between shadow border',
            index === 0 ? 'bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200' : '',
            index === 1 ? 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200' : '',
            index === 2 ? 'bg-gradient-to-br from-rose-50 to-rose-100 border-rose-200' : ''
          ]">
          <div :class="[
            'text-xs font-medium truncate',
            index === 0 ? 'text-amber-700' : '',
            index === 1 ? 'text-orange-700' : '',
            index === 2 ? 'text-rose-700' : ''
          ]">{{ site.website__name }}</div>
          <div :class="[
            'text-base sm:text-lg lg:text-xl font-bold break-all leading-tight',
            index === 0 ? 'text-amber-800' : '',
            index === 1 ? 'text-orange-800' : '',
            index === 2 ? 'text-rose-800' : ''
          ]" :title="`$${parseFloat(site.total_balance || 0).toFixed(2)}`">
            {{ formatCurrency(site.total_balance) }}
          </div>
          <div :class="[
            'text-xs',
            index === 0 ? 'text-amber-600' : '',
            index === 1 ? 'text-orange-600' : '',
            index === 2 ? 'text-rose-600' : ''
          ]">{{ site.wallet_count || 0 }} wallets</div>
        </div>
        <div v-if="summary.website_totals.length > 3" class="p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg flex items-center justify-center h-28 border border-slate-200 shadow">
          <span class="text-sm text-slate-600">+{{ summary.website_totals.length - 3 }} more websites</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow border border-gray-200 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Search</label>
          <input 
            v-model="filters.search" 
            @input="debouncedSearch"
            type="text" 
            placeholder="Email, username, name, phone..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Website</label>
          <select v-model="filters.website" @change="loadWallets" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Min Balance</label>
          <input 
            v-model.number="filters.min_balance" 
            @input="debouncedSearch"
            type="number" 
            step="0.01"
            placeholder="0.00"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Max Balance</label>
          <input 
            v-model.number="filters.max_balance" 
            @input="debouncedSearch"
            type="number" 
            step="0.01"
            placeholder="No limit"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Sort By</label>
          <select v-model="filters.ordering" @change="loadWallets" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors">
            <option value="-balance">Balance (High to Low)</option>
            <option value="balance">Balance (Low to High)</option>
            <option value="-last_updated">Last Updated (Recent)</option>
            <option value="last_updated">Last Updated (Oldest)</option>
            <option value="-loyalty_points">Loyalty Points (High to Low)</option>
            <option value="loyalty_points">Loyalty Points (Low to High)</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm">
            Reset Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Client Wallets Table -->
    <div v-if="activeTab === 'clients'" class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!clientWallets.length" class="text-center py-12">
        <p class="text-gray-500">No client wallets found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" @click="sortBy('client')">
                Client
                <span v-if="filters.ordering === 'client' || filters.ordering === '-client'">▼</span>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" @click="sortBy('balance')">
                Balance
                <span v-if="filters.ordering === 'balance' || filters.ordering === '-balance'">▼</span>
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" @click="sortBy('loyalty_points')">
                Loyalty Points
                <span v-if="filters.ordering === 'loyalty_points' || filters.ordering === '-loyalty_points'">▼</span>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Currency</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" @click="sortBy('last_updated')">
                Last Updated
                <span v-if="filters.ordering === 'last_updated' || filters.ordering === '-last_updated'">▼</span>
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="wallet in clientWallets" :key="wallet.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ getUserName(wallet.user) }}
                  </div>
                  <div class="text-sm text-gray-500">{{ wallet.user?.email || 'N/A' }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ wallet.website?.name || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <span :class="getBalanceColor(wallet.balance)" class="text-sm font-bold">
                  ${{ parseFloat(wallet.balance || 0).toFixed(2) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                {{ wallet.loyalty_points || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ wallet.currency || 'USD' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(wallet.last_updated) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex items-center justify-center gap-2">
                  <button 
                    @click="openAdjustModal(wallet, 'client')"
                    class="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm"
                    title="Adjust Wallet"
                  >
                    Adjust
                  </button>
                  <button 
                    @click="viewWalletDetails(wallet, 'client')"
                    class="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm"
                    title="View Details"
                  >
                    View
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination && (pagination.next || pagination.previous || pagination.count > pageSize)" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
        <div class="text-sm text-gray-700">
          Showing {{ ((pagination.current_page - 1) * pagination.page_size) + 1 }} to 
          {{ Math.min(pagination.current_page * pagination.page_size, pagination.count) }} of 
          {{ pagination.count }} wallets
        </div>
        <div class="flex gap-2 items-center">
          <button 
            @click="loadPage(pagination.previous)"
            :disabled="!pagination.previous"
            class="px-4 py-2 border rounded hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            ← Previous
          </button>
          <span class="px-4 py-2 text-sm text-gray-700">
            Page {{ pagination.current_page }} of {{ pagination.total_pages }}
          </span>
          <button 
            @click="loadPage(pagination.next)"
            :disabled="!pagination.next"
            class="px-4 py-2 border rounded hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            Next →
          </button>
        </div>
        <div>
          <select v-model="pageSize" @change="changePageSize" class="px-3 py-2 border rounded text-sm bg-white">
            <option :value="25">25 per page</option>
            <option :value="50">50 per page</option>
            <option :value="100">100 per page</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Writer Wallets Table -->
    <div v-if="activeTab === 'writers'" class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!writerWallets.length" class="text-center py-12">
        <p class="text-gray-500">No writer wallets found.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Balance</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Earnings</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Fines</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Currency</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="wallet in writerWallets" :key="wallet.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ getUserName(wallet.writer) }}
                  </div>
                  <div class="text-sm text-gray-500">{{ wallet.writer?.email || 'N/A' }}</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ wallet.website?.name || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <span :class="getBalanceColor(wallet.balance)" class="text-sm font-bold">
                  ${{ parseFloat(wallet.balance || 0).toFixed(2) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-green-600">
                ${{ parseFloat(wallet.total_earnings || 0).toFixed(2) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-red-600">
                ${{ parseFloat(wallet.total_fines || 0).toFixed(2) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ wallet.currency || 'USD' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(wallet.last_updated) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex items-center justify-center gap-2">
                  <button 
                    @click="openAdjustModal(wallet, 'writer')"
                    class="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm"
                    title="Adjust Wallet"
                  >
                    Adjust
                  </button>
                  <button 
                    @click="viewWalletDetails(wallet, 'writer')"
                    class="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm"
                    title="View Details"
                  >
                    View
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Adjust Wallet Modal -->
    <div v-if="showAdjustModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div class="bg-white rounded-lg p-6 max-w-md w-full my-auto max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">Adjust Wallet</h2>
        
        <div v-if="selectedWallet" class="mb-4 space-y-2">
          <div>
            <strong>{{ walletType === 'writer' ? 'Writer' : 'Client' }}:</strong> 
            {{ walletType === 'writer' ? getUserName(selectedWallet.writer) : getUserName(selectedWallet.user) }} 
            ({{ walletType === 'writer' ? selectedWallet.writer?.email : selectedWallet.user?.email }})
          </div>
          <div>
            <strong>Website:</strong> {{ selectedWallet.website?.name }}
          </div>
          <div>
            <strong>Current Balance:</strong> 
            <span :class="getBalanceColor(selectedWallet.balance)" class="font-bold">
              ${{ parseFloat(selectedWallet.balance || 0).toFixed(2) }}
            </span>
          </div>
          <div v-if="walletType === 'writer'">
            <strong>Total Earnings:</strong> 
            <span class="text-green-600 font-bold">
              ${{ parseFloat(selectedWallet.total_earnings || 0).toFixed(2) }}
            </span>
          </div>
        </div>

        <form @submit.prevent="submitAdjustment" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Amount</label>
            <input 
              v-model.number="adjustForm.amount" 
              type="number" 
              step="0.01"
              required
              class="w-full border rounded px-3 py-2"
              placeholder="Positive to credit, negative to debit"
            />
            <p class="text-xs text-gray-500 mt-1">
              Enter positive amount (e.g., 50.00) to credit, or negative (e.g., -25.00) to debit.
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Transaction Type</label>
            <select v-model="adjustForm.transaction_type" class="w-full border rounded px-3 py-2">
              <option value="adjustment">Adjustment</option>
              <option v-if="walletType === 'client'" value="top-up">Top-Up</option>
              <option v-if="walletType === 'client'" value="refund">Refund</option>
              <option v-if="walletType === 'client'" value="bonus">Bonus</option>
              <option v-if="walletType === 'writer'" value="Bonus">Bonus</option>
              <option v-if="walletType === 'writer'" value="Reward">Reward</option>
              <option v-if="walletType === 'writer'" value="Fine">Fine</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Reason</label>
            <textarea 
              v-model="adjustForm.reason" 
              required
              rows="3"
              class="w-full border rounded px-3 py-2"
              placeholder="Reason for this adjustment"
            ></textarea>
          </div>

          <div class="flex gap-3">
            <button 
              type="submit" 
              :disabled="adjusting"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {{ adjusting ? 'Processing...' : 'Apply Adjustment' }}
            </button>
            <button 
              type="button" 
              @click="closeAdjustModal"
              class="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Wallet Details Modal -->
    <div v-if="viewingWallet" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-lg max-w-4xl w-full my-auto max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">{{ walletType === 'writer' ? 'Writer' : 'Client' }} Wallet Details</h2>
            <button @click="closeWalletDetails" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
          </div>

          <div class="grid grid-cols-2 gap-6 mb-6">
            <!-- User Info -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">{{ walletType === 'writer' ? 'Writer' : 'Client' }} Information</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Name:</span>
                  <span class="ml-2 text-gray-900">
                    {{ walletType === 'writer' ? getUserName(viewingWallet.writer) : getUserName(viewingWallet.user) }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Email:</span>
                  <span class="ml-2 text-gray-900">
                    {{ walletType === 'writer' ? viewingWallet.writer?.email : viewingWallet.user?.email }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Username:</span>
                  <span class="ml-2 text-gray-900">
                    {{ walletType === 'writer' ? viewingWallet.writer?.username : viewingWallet.user?.username }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Website:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWallet.website?.name || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Wallet Info -->
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2">Wallet Information</h3>
              <div class="space-y-2">
                <div>
                  <span class="text-sm font-medium text-gray-600">Balance:</span>
                  <span :class="getBalanceColor(viewingWallet.balance)" class="ml-2 font-bold text-lg">
                    ${{ parseFloat(viewingWallet.balance || 0).toFixed(2) }}
                  </span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Currency:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWallet.currency || 'USD' }}</span>
                </div>
                <div v-if="walletType === 'client'">
                  <span class="text-sm font-medium text-gray-600">Loyalty Points:</span>
                  <span class="ml-2 text-gray-900">{{ viewingWallet.loyalty_points || 0 }}</span>
                </div>
                <div v-if="walletType === 'writer'">
                  <span class="text-sm font-medium text-gray-600">Total Earnings:</span>
                  <span class="ml-2 text-green-600 font-bold">${{ parseFloat(viewingWallet.total_earnings || 0).toFixed(2) }}</span>
                </div>
                <div v-if="walletType === 'writer'">
                  <span class="text-sm font-medium text-gray-600">Total Fines:</span>
                  <span class="ml-2 text-red-600 font-bold">${{ parseFloat(viewingWallet.total_fines || 0).toFixed(2) }}</span>
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-600">Last Updated:</span>
                  <span class="ml-2 text-gray-900">{{ formatDate(viewingWallet.last_updated) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Transactions -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900 border-b pb-2 flex-1">Transaction History</h3>
              <div class="flex gap-2">
                <button 
                  @click="exportTransactions"
                  class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                  title="Export Transactions"
                >
                  📥 Export
                </button>
                <button 
                  @click="loadMoreTransactions"
                  v-if="transactionPagination && transactionPagination.next"
                  class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Load More
                </button>
              </div>
            </div>
            <div v-if="walletTransactions.length" class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Balance After</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="txn in walletTransactions" :key="txn.id" class="hover:bg-gray-50">
                    <td class="px-4 py-2 text-sm text-gray-500 whitespace-nowrap">
                      {{ formatDate(txn.created_at) }}
                    </td>
                    <td class="px-4 py-2 text-sm">
                      <span class="px-2 py-1 rounded text-xs font-medium" :class="getTransactionTypeClass(txn.transaction_type)">
                        {{ txn.transaction_type }}
                      </span>
                    </td>
                    <td class="px-4 py-2 text-sm text-right font-bold" :class="parseFloat(txn.amount || 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ parseFloat(txn.amount || 0) >= 0 ? '+' : '' }}${{ Math.abs(parseFloat(txn.amount || 0)).toFixed(2) }}
                    </td>
                    <td class="px-4 py-2 text-sm text-gray-600">{{ txn.description || '—' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-500 font-mono text-xs">{{ txn.reference_id || '—' }}</td>
                    <td class="px-4 py-2 text-sm text-gray-700 font-medium">
                      ${{ parseFloat(txn.balance_after || viewingWallet.balance || 0).toFixed(2) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              No transactions found.
            </div>
            <div v-if="transactionPagination && transactionPagination.count" class="mt-4 text-sm text-gray-600 text-center">
              Showing {{ walletTransactions.length }} of {{ transactionPagination.count }} transactions
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="flex gap-2 pt-4 border-t">
            <button @click="openAdjustModal(viewingWallet, walletType); closeWalletDetails()" class="btn btn-primary">Adjust Wallet</button>
            <button @click="closeWalletDetails" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import walletAPI from '@/api/wallet'
import websitesAPI from '@/api/websites'

// Simple debounce function
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const activeTab = ref('clients')
const clientWallets = ref([])
const writerWallets = ref([])
const summary = ref(null)
const loading = ref(true)
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const filters = ref({
  search: '',
  website: '',
  min_balance: '',
  max_balance: '',
  ordering: '-balance',
})

const showWebsiteTotals = ref(true)
const showQuickAdjust = ref(true)
const pagination = ref(null)
const pageSize = ref(25)
const transactionPagination = ref(null)
const foundWallet = ref(null)
const searchingWallet = ref(false)
const processingQuickAdjust = ref(false)
const quickAdjust = ref({
  clientSearch: '',
  amount: '',
  transaction_type: 'adjustment',
  reason: '',
})

const showAdjustModal = ref(false)
const selectedWallet = ref(null)
const viewingWallet = ref(null)
const walletTransactions = ref([])
const walletType = ref('client') // 'client' or 'writer'
const adjusting = ref(false)
const adjustForm = ref({
  amount: 0,
  transaction_type: 'adjustment',
  reason: '',
})

const websites = ref([])

// Client total balance from visible list (matches the displayed wallets)
const clientTotalBalance = computed(() => {
  return clientWallets.value.reduce((sum, w) => sum + parseFloat(w.balance || 0), 0)
})

// Client total loyalty points from visible list
const clientTotalLoyaltyPoints = computed(() => {
  return clientWallets.value.reduce((sum, w) => sum + parseFloat(w.loyalty_points || 0), 0)
})

const writerTotalBalance = computed(() => {
  return writerWallets.value.reduce((sum, w) => sum + parseFloat(w.balance || 0), 0)
})

const writerTotalEarnings = computed(() => {
  return writerWallets.value.reduce((sum, w) => sum + parseFloat(w.total_earnings || 0), 0)
})

const getUserName = (user) => {
  if (!user) return 'N/A'
  if (user.first_name || user.last_name) {
    return `${user.first_name || ''} ${user.last_name || ''}`.trim()
  }
  return user.username || user.email || 'N/A'
}

const getBalanceColor = (balance) => {
  const bal = parseFloat(balance || 0)
  if (bal >= 1000) return 'text-green-600'
  if (bal >= 100) return 'text-blue-600'
  if (bal > 0) return 'text-orange-600'
  return 'text-red-600'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatCurrency = (amount) => {
  const num = parseFloat(amount || 0)
  // Format with commas for thousands
  return `$${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    websites.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
  } catch (e) {
    console.error('Failed to load websites:', e)
    // If websites API fails, we'll extract from wallets as fallback
  }
}

const loadWallets = async (pageUrl = null) => {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (pageUrl) {
      // Extract params from URL
      const url = new URL(pageUrl)
      url.searchParams.forEach((value, key) => {
        params[key] = value
      })
    } else {
      if (filters.value.search) params.search = filters.value.search
      if (filters.value.website) params.website = filters.value.website
      if (filters.value.min_balance !== '' && filters.value.min_balance !== null) {
        params.min_balance = filters.value.min_balance
      }
      if (filters.value.max_balance !== '' && filters.value.max_balance !== null) {
        params.max_balance = filters.value.max_balance
      }
      if (filters.value.ordering) params.ordering = filters.value.ordering
      params.page_size = pageSize.value
    }
    
    // Load client wallets
    const clientRes = await walletAPI.admin.listWallets(params)
    
    // Handle paginated response - Backend returns wallets directly or in results
    if (clientRes.data.wallets) {
      // Backend returns wallets directly with pagination metadata
      clientWallets.value = clientRes.data.wallets || []
      summary.value = clientRes.data.summary || null
      if (clientRes.data.count !== undefined) {
        pagination.value = {
          count: clientRes.data.count,
          next: clientRes.data.next,
          previous: clientRes.data.previous,
          current_page: extractPageNumber(clientRes.data.next) || (clientRes.data.previous ? extractPageNumber(clientRes.data.previous) + 1 : 1),
          page_size: pageSize.value,
          total_pages: Math.ceil((clientRes.data.count || clientWallets.value.length) / pageSize.value)
        }
      } else {
        pagination.value = null
      }
    } else if (clientRes.data.results) {
      // Fallback: DRF standard pagination format
      clientWallets.value = Array.isArray(clientRes.data.results) ? clientRes.data.results : []
      summary.value = clientRes.data.summary || null
      pagination.value = {
        count: clientRes.data.count || clientWallets.value.length,
        next: clientRes.data.next,
        previous: clientRes.data.previous,
        current_page: extractPageNumber(clientRes.data.next) || 1,
        page_size: pageSize.value,
        total_pages: Math.ceil((clientRes.data.count || clientWallets.value.length) / pageSize.value)
      }
    } else {
      // Non-paginated response
      clientWallets.value = []
      summary.value = clientRes.data.summary || null
      pagination.value = null
    }
    
    // Load writer wallets (only if on writers tab or if we want to show both)
    if (activeTab.value === 'writers' || activeTab.value === 'clients') {
      const writerRes = await walletAPI.admin.listWriterWallets(params)
      writerWallets.value = Array.isArray(writerRes.data?.results) ? writerRes.data.results : (writerRes.data || [])
    }
    
    // If websites list is empty, extract from wallets as fallback
    if (!websites.value.length) {
      const siteMap = new Map()
      ;[...clientWallets.value, ...writerWallets.value].forEach(w => {
        const website = w.website || (w.writer ? null : w.website)
        if (website && !siteMap.has(website.id)) {
          siteMap.set(website.id, website)
        }
      })
      websites.value = Array.from(siteMap.values())
    }
  } catch (e) {
    // Only log and set error if it's not a 404 (endpoint doesn't exist)
    if (e?.response?.status !== 404) {
      console.error('Failed to load wallets:', e)
      error.value = e?.response?.data?.detail || e.message || 'Failed to load wallets'
    } else {
      // Endpoint doesn't exist, set empty arrays
      clientWallets.value = []
      writerWallets.value = []
      error.value = null
    }
  } finally {
    loading.value = false
  }
}

const filterByWebsite = (websiteId) => {
  filters.value.website = websiteId
  loadWallets()
}

const resetFilters = () => {
  filters.value = {
    search: '',
    website: '',
    min_balance: '',
    max_balance: '',
    ordering: '-balance',
  }
  pageSize.value = 25
  loadWallets()
}

const sortBy = (field) => {
  if (filters.value.ordering === `-${field}`) {
    filters.value.ordering = field
  } else {
    filters.value.ordering = `-${field}`
  }
  loadWallets()
}

const loadPage = (url) => {
  if (url) {
    loadWallets(url)
  }
}

const changePageSize = () => {
  loadWallets()
}

const exportWallets = () => {
  const data = activeTab.value === 'clients' ? clientWallets.value : writerWallets.value
  const headers = activeTab.value === 'clients' 
    ? ['Client Name', 'Email', 'Website', 'Balance', 'Loyalty Points', 'Currency', 'Last Updated']
    : ['Writer Name', 'Email', 'Website', 'Balance', 'Total Earnings', 'Total Fines', 'Currency', 'Last Updated']
  
  let csv = headers.join(',') + '\n'
  data.forEach(wallet => {
    const row = activeTab.value === 'clients'
      ? [
          `"${getUserName(wallet.user)}"`,
          `"${wallet.user?.email || ''}"`,
          `"${wallet.website?.name || ''}"`,
          wallet.balance || 0,
          wallet.loyalty_points || 0,
          wallet.currency || 'USD',
          formatDate(wallet.last_updated)
        ]
      : [
          `"${getUserName(wallet.writer)}"`,
          `"${wallet.writer?.email || ''}"`,
          `"${wallet.website?.name || ''}"`,
          wallet.balance || 0,
          wallet.total_earnings || 0,
          wallet.total_fines || 0,
          wallet.currency || 'USD',
          formatDate(wallet.last_updated)
        ]
    csv += row.join(',') + '\n'
  })
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${activeTab.value}_wallets_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

const exportTransactions = () => {
  if (!walletTransactions.value.length) return
  
  const headers = ['Date', 'Type', 'Amount', 'Description', 'Reference ID', 'Balance After']
  let csv = headers.join(',') + '\n'
  walletTransactions.value.forEach(txn => {
    const row = [
      formatDate(txn.created_at),
      `"${txn.transaction_type}"`,
      txn.amount || 0,
      `"${(txn.description || '').replace(/"/g, '""')}"`,
      txn.reference_id || '',
      txn.balance_after || viewingWallet.value?.balance || 0
    ]
    csv += row.join(',') + '\n'
  })
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `wallet_transactions_${viewingWallet.value?.id || 'unknown'}_${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

const loadMoreTransactions = async () => {
  if (!transactionPagination.value?.next) return
  
  try {
    const url = new URL(transactionPagination.value.next)
    const params = {}
    url.searchParams.forEach((value, key) => {
      params[key] = value
    })
    
    const res = await walletAPI.admin.getWallet(viewingWallet.value.id, params)
    if (res.data.results) {
      walletTransactions.value = [...walletTransactions.value, ...(res.data.results.transactions || [])]
      transactionPagination.value = {
        count: res.data.count,
        next: res.data.next,
        previous: res.data.previous
      }
    }
  } catch (e) {
    console.error('Failed to load more transactions:', e)
  }
}

const getTransactionTypeClass = (type) => {
  const typeMap = {
    'credit': 'bg-green-100 text-green-800',
    'debit': 'bg-red-100 text-red-800',
    'adjustment': 'bg-blue-100 text-blue-800',
    'top-up': 'bg-purple-100 text-purple-800',
    'refund': 'bg-yellow-100 text-yellow-800',
    'bonus': 'bg-pink-100 text-pink-800',
    'payment': 'bg-gray-100 text-gray-800',
  }
  return typeMap[type?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const extractPageNumber = (url) => {
  if (!url) return 1
  try {
    const urlObj = new URL(url)
    const page = urlObj.searchParams.get('page')
    return page ? parseInt(page) : 1
  } catch {
    return 1
  }
}

const searchClientWallet = async () => {
  if (!quickAdjust.value.clientSearch) return
  
  searchingWallet.value = true
  foundWallet.value = null
  error.value = ''
  
  try {
    // Search for wallet by client email/username
    const params = { search: quickAdjust.value.clientSearch }
    const res = await walletAPI.admin.listWallets(params)
    
    // Get wallets from response
    const wallets = res.data.wallets || (res.data.results?.wallets || res.data.results || [])
    
    if (wallets.length > 0) {
      // Use first matching wallet
      foundWallet.value = wallets[0]
      message.value = `Found wallet for ${getUserName(foundWallet.value.user)}`
      messageSuccess.value = true
      setTimeout(() => { message.value = '' }, 3000)
    } else {
      foundWallet.value = null
      error.value = 'No wallet found for this client. Make sure the client exists and has a wallet.'
    }
  } catch (e) {
    console.error('Failed to search wallet:', e)
    error.value = e?.response?.data?.detail || e.message || 'Failed to search for wallet'
    foundWallet.value = null
  } finally {
    searchingWallet.value = false
  }
}

const submitQuickAdjustment = async () => {
  if (!foundWallet.value || !quickAdjust.value.amount || !quickAdjust.value.reason) return
  
  processingQuickAdjust.value = true
  error.value = ''
  message.value = ''
  
  try {
    const res = await walletAPI.admin.adjustWallet(foundWallet.value.id, {
      amount: parseFloat(quickAdjust.value.amount),
      transaction_type: quickAdjust.value.transaction_type,
      reason: quickAdjust.value.reason,
    })
    
    message.value = res.data.detail || 'Wallet adjusted successfully'
    messageSuccess.value = true
    
    // Update found wallet
    foundWallet.value = res.data.wallet || foundWallet.value
    
    // Reload wallets list
    await loadWallets()
    
    // Reset form but keep client search
    quickAdjust.value.amount = ''
    quickAdjust.value.reason = ''
    quickAdjust.value.transaction_type = 'adjustment'
    
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to adjust wallet'
  } finally {
    processingQuickAdjust.value = false
  }
}

const resetQuickAdjust = () => {
  quickAdjust.value = {
    clientSearch: '',
    amount: '',
    transaction_type: 'adjustment',
    reason: '',
  }
  foundWallet.value = null
  error.value = ''
}

const debouncedSearch = debounce(loadWallets, 500)

const openAdjustModal = (wallet, type = 'client') => {
  selectedWallet.value = wallet
  walletType.value = type
  adjustForm.value = {
    amount: 0,
    transaction_type: 'adjustment',
    reason: '',
  }
  showAdjustModal.value = true
}

const closeAdjustModal = () => {
  showAdjustModal.value = false
  selectedWallet.value = null
  walletType.value = 'client'
}

const viewWalletDetails = async (wallet, type = 'client') => {
  walletType.value = type
  viewingWallet.value = wallet
  walletTransactions.value = []
  transactionPagination.value = null
  
  try {
    if (type === 'writer') {
      const res = await walletAPI.admin.getWriterTransactions(wallet.id)
      walletTransactions.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
      if (res.data.count !== undefined) {
        transactionPagination.value = {
          count: res.data.count,
          next: res.data.next,
          previous: res.data.previous
        }
      }
    } else {
      const res = await walletAPI.admin.getWallet(wallet.id)
      if (res.data.results) {
        walletTransactions.value = res.data.results.transactions || []
        viewingWallet.value = res.data.results.wallet || wallet
        transactionPagination.value = {
          count: res.data.count,
          next: res.data.next,
          previous: res.data.previous
        }
      } else {
        walletTransactions.value = res.data.transactions || []
        viewingWallet.value = res.data.wallet || wallet
        transactionPagination.value = {
          count: walletTransactions.value.length,
          next: null,
          previous: null
        }
      }
    }
  } catch (e) {
    console.error('Failed to load transactions:', e)
    walletTransactions.value = []
    transactionPagination.value = null
  }
}

const closeWalletDetails = () => {
  viewingWallet.value = null
  walletTransactions.value = []
  walletType.value = 'client'
}

const submitAdjustment = async () => {
  if (!selectedWallet.value) return
  
  adjusting.value = true
  error.value = ''
  message.value = ''
  
  try {
    let res
    if (walletType.value === 'writer') {
      res = await walletAPI.admin.adjustWriterWallet(selectedWallet.value.id, adjustForm.value)
    } else {
      res = await walletAPI.admin.adjustWallet(selectedWallet.value.id, adjustForm.value)
    }
    
    message.value = res.data.detail || 'Wallet adjusted successfully'
    messageSuccess.value = true
    
    // Update wallet in appropriate list
    if (walletType.value === 'writer') {
      const index = writerWallets.value.findIndex(w => w.id === selectedWallet.value.id)
      if (index !== -1) {
        writerWallets.value[index] = res.data.wallet
      }
    } else {
      const index = clientWallets.value.findIndex(w => w.id === selectedWallet.value.id)
      if (index !== -1) {
        clientWallets.value[index] = res.data.wallet
      }
    }
    
    // Reload summary
    await loadWallets()
    
    closeAdjustModal()
    
    // Clear message after 5 seconds
    setTimeout(() => {
      message.value = ''
    }, 5000)
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to adjust wallet'
  } finally {
    adjusting.value = false
  }
}

watch(activeTab, () => {
  // Reload when switching tabs to ensure fresh data
  loadWallets()
})

onMounted(async () => {
  // Load websites first, then wallets
  await loadWebsites()
  await loadWallets()
})
</script>

