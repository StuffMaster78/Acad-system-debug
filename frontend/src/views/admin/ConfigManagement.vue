<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Configuration Management</h1>
        <p class="mt-2 text-gray-600">Manage system configurations (pricing, writer settings, discounts, etc.)</p>
      </div>
    </div>

    <!-- Config Tabs -->
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

    <!-- Pricing Configs -->
    <div v-if="activeTab === 'pricing'" class="space-y-4">
      <!-- Pricing Sub-tabs -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-6">
          <button
            v-for="subTab in pricingSubTabs"
            :key="subTab.id"
            @click="activePricingSubTab = subTab.id"
            :class="[
              'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm',
              activePricingSubTab === subTab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ subTab.label }}
          </button>
        </nav>
      </div>

      <!-- Base Pricing -->
      <div v-if="activePricingSubTab === 'base-pricing'" class="space-y-4">
      <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Base Pricing Configurations</h2>
        <button @click="showPricingModal = true" class="btn btn-primary">Create Pricing Config</button>
      </div>
      
      <div class="card">
        <div v-if="pricingConfigsLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="pricingConfigs.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Base Price/Page</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Base Price/Slide</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technical Multiplier</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Non-Tech Multiplier</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="config in pricingConfigs" :key="config.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="config.website" class="text-sm">
                      <div class="font-medium text-gray-900">{{ config.website.name }}</div>
                      <div class="text-xs text-gray-500">{{ config.website.domain }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4">${{ parseFloat(config.base_price_per_page || 0).toFixed(2) }}</td>
                  <td class="px-6 py-4">${{ parseFloat(config.base_price_per_slide || 0).toFixed(2) }}</td>
                  <td class="px-6 py-4">{{ parseFloat(config.technical_multiplier || 1).toFixed(2) }}x</td>
                  <td class="px-6 py-4">{{ parseFloat(config.non_technical_order_multiplier || 1).toFixed(2) }}x</td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ formatDate(config.updated_at) }}</td>
                <td class="px-6 py-4">
                  <button @click="editPricingConfig(config)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button @click="deletePricingConfig(config.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No pricing configurations found.</div>
        </div>
      </div>

      <!-- Additional Services -->
      <div v-if="activePricingSubTab === 'additional-services'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Additional Services</h2>
          <button @click="createAdditionalService" class="btn btn-primary">Create Additional Service</button>
        </div>
        
        <div class="card">
          <div v-if="additionalServicesLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="additionalServices.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service Name</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="service in additionalServices" :key="service.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="service.website" class="text-sm">
                      <div class="font-medium text-gray-900">{{ service.website_name || service.website?.name || 'N/A' }}</div>
                      <div class="text-xs text-gray-500">{{ service.website_domain || service.website?.domain || '' }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ service.service_name }}</td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ service.description || '—' }}</td>
                  <td class="px-6 py-4">${{ parseFloat(service.cost || 0).toFixed(2) }}</td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ service.slug }}</td>
                  <td class="px-6 py-4">
                    <span :class="service.is_active ? 'px-2 py-1 text-xs rounded bg-green-100 text-green-800' : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-800'">
                      {{ service.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <button @click="editAdditionalService(service)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deleteAdditionalService(service.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No additional services found.</div>
        </div>
      </div>

      <!-- Preferred Writers -->
      <div v-if="activePricingSubTab === 'preferred-writers'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Preferred Writer Configurations</h2>
          <button @click="createPreferredWriterConfig" class="btn btn-primary">Create Preferred Writer Config</button>
        </div>
        
        <div class="card">
          <div v-if="preferredWriterConfigsLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="preferredWriterConfigs.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost (Applies to All Writers)</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="config in preferredWriterConfigs" :key="config.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="config.website" class="text-sm">
                      <div class="font-medium text-gray-900">{{ config.website_name || config.website?.name || 'N/A' }}</div>
                      <div class="text-xs text-gray-500">{{ config.website_domain || config.website?.domain || '' }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm">
                      <div class="font-medium text-gray-900">${{ parseFloat(config.preferred_writer_cost || 0).toFixed(2) }}</div>
                      <div class="text-xs text-gray-500 mt-1">Extra cost for preferred writer selection</div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="config.is_active ? 'px-2 py-1 text-xs rounded bg-green-100 text-green-800' : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-800'">
                      {{ config.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <button @click="editPreferredWriterConfig(config)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deletePreferredWriterConfig(config.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No preferred writer configurations found.</div>
        </div>
      </div>

      <!-- Writer Levels -->
      <div v-if="activePricingSubTab === 'writer-levels'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Writer Level Options (Pricing)</h2>
          <button @click="createWriterLevelOption" class="btn btn-primary">Create Writer Level Option</button>
        </div>
        
        <div class="card">
          <div v-if="writerLevelOptionsLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="writerLevelOptions.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sort Order</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="option in writerLevelOptions" :key="option.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="option.website" class="text-sm">
                      <div class="font-medium text-gray-900">{{ option.website_name || option.website?.name || 'N/A' }}</div>
                      <div class="text-xs text-gray-500">{{ option.website_domain || option.website?.domain || '' }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ option.name }}</td>
                  <td class="px-6 py-4">${{ parseFloat(option.value || 0).toFixed(2) }}</td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ option.description || '—' }}</td>
                  <td class="px-6 py-4">{{ option.sort_order || 0 }}</td>
                  <td class="px-6 py-4">
                    <span :class="option.active ? 'px-2 py-1 text-xs rounded bg-green-100 text-green-800' : 'px-2 py-1 text-xs rounded bg-gray-100 text-gray-800'">
                      {{ option.active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <button @click="editWriterLevelOption(option)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deleteWriterLevelOption(option.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No writer level options found.</div>
        </div>
      </div>

      <!-- Deadline Multipliers -->
      <div v-if="activePricingSubTab === 'deadline-multipliers'" class="space-y-4">
        <div class="flex justify-between items-start gap-4">
          <div>
            <h2 class="text-xl font-semibold">Deadline Multipliers & Rush Mode</h2>
            <p class="mt-1 text-sm text-gray-600 max-w-3xl">
              These multipliers control price and writer earnings based on how soon the client needs the paper.
              Deadlines under <span class="font-semibold">6 hours</span> are treated as
              <span class="font-semibold text-rose-600">Rush</span>, and under
              <span class="font-semibold">24 hours</span> as
              <span class="font-semibold text-amber-600">Same‑day</span> in the order wizard and pricing breakdown.
            </p>
          </div>
          <button 
            @click="createDeadlineMultiplier" 
            class="btn btn-primary"
            type="button"
          >
            Create Deadline Multiplier
          </button>
        </div>
        
        <div class="card">
          <div v-if="deadlineMultipliersLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="deadlineMultipliers.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Label</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hours</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Multiplier</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Urgency</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="multiplier in deadlineMultipliers" :key="multiplier.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="multiplier.website" class="text-sm">
                      <div class="font-medium text-gray-900">{{ multiplier.website_name || multiplier.website?.name || 'N/A' }}</div>
                      <div class="text-xs text-gray-500">{{ multiplier.website_domain || multiplier.website?.domain || '' }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ multiplier.label }}</td>
                  <td class="px-6 py-4">{{ multiplier.hours }}h</td>
                  <td class="px-6 py-4">{{ parseFloat(multiplier.multiplier || 1).toFixed(2) }}x</td>
                  <td class="px-6 py-4">
                    <span
                      :class="[
                        'px-2 py-1 rounded-full text-xs font-semibold',
                        classifyUrgency(multiplier.hours) === 'rush'
                          ? 'bg-rose-100 text-rose-800'
                          : classifyUrgency(multiplier.hours) === 'same_day'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-gray-100 text-gray-700'
                      ]"
                    >
                      {{ formatUrgencyLabel(multiplier.hours) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-500">{{ formatDate(multiplier.updated_at) }}</td>
                  <td class="px-6 py-4">
                    <button @click="editDeadlineMultiplier(multiplier)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deleteDeadlineMultiplier(multiplier.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No deadline multipliers found.</div>
        </div>
      </div>
    </div>

    <!-- Writer Configs -->
    <div v-if="activeTab === 'writer'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Writer Configurations</h2>
        <button @click="showWriterModal = true" class="btn btn-primary">Create Writer Config</button>
      </div>
      
      <div class="card">
        <div v-if="writerConfigsLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="writerConfigs.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Takes Enabled</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in writerConfigs" :key="config.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <div v-if="config.website" class="text-sm">
                    <div class="font-medium text-gray-900">{{ config.website.name }}</div>
                    <div class="text-xs text-gray-500">{{ config.website.domain }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="config.takes_enabled ? 'text-green-600' : 'text-red-600'" class="font-medium">
                    {{ config.takes_enabled ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button @click="editWriterConfig(config)" class="text-blue-600 hover:underline">Edit</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No writer configurations found.</div>
      </div>
    </div>

    <!-- Referrals Tab -->
    <div v-if="activeTab === 'referrals'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Referral Bonus Configurations</h2>
        <button @click="createReferralConfig" class="btn btn-primary">Create Referral Config</button>
      </div>
      
      <div class="card">
        <div v-if="referralConfigsLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="referralConfigs.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">First Order Bonus</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discount Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Discount Amount</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bonus Expiry (Days)</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Referrals/Month</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max Bonus/Month</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in referralConfigs" :key="config.id" class="hover:bg-gray-50">
                <td class="px-6 py-4">
                  <div v-if="config.website" class="text-sm">
                    <div class="font-medium text-gray-900">{{ config.website_name || config.website?.name || 'N/A' }}</div>
                    <div class="text-xs text-gray-500">{{ config.website_domain || config.website?.domain || '' }}</div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="px-6 py-4">${{ parseFloat(config.first_order_bonus || 0).toFixed(2) }}</td>
                <td class="px-6 py-4">
                  <span class="px-2 py-1 text-xs rounded" :class="config.first_order_discount_type === 'percentage' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                    {{ config.first_order_discount_type === 'percentage' ? 'Percentage' : 'Fixed' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  {{ config.first_order_discount_type === 'percentage' ? `${config.first_order_discount_amount}%` : `$${parseFloat(config.first_order_discount_amount || 0).toFixed(2)}` }}
                </td>
                <td class="px-6 py-4">{{ config.bonus_expiry_days || 30 }} days</td>
                <td class="px-6 py-4">{{ config.max_referrals_per_month || 10 }}</td>
                <td class="px-6 py-4">${{ parseFloat(config.max_referral_bonus_per_month || 100).toFixed(2) }}</td>
                <td class="px-6 py-4">
                  <button @click="editReferralConfig(config)" class="text-blue-600 hover:underline mr-2">Edit</button>
                  <button @click="deleteReferralConfig(config.id)" class="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No referral configurations found.</div>
      </div>
    </div>


    <!-- Order Configs -->
    <div v-if="activeTab === 'order-configs'" class="space-y-4">
      <!-- Global Actions Bar -->
      <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="flex items-center gap-4">
            <h3 class="text-lg font-semibold text-gray-900">Order Configurations</h3>
            <span class="text-sm text-gray-500">Organized by website</span>
          </div>
          <div class="flex gap-2 flex-wrap">
            <input
              v-model="orderConfigSearchQuery"
              @input="debouncedOrderConfigSearch"
              type="text"
              placeholder="Search across all websites..."
              class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <button
              v-if="selectedConfigs.length > 0"
              @click="handleBulkDelete"
              :disabled="bulkDeleting"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ bulkDeleting ? 'Deleting...' : `Delete ${selectedConfigs.length} Selected` }}
            </button>
          </div>
        </div>
      </div>

      <!-- Order Config Type Tabs -->
      <div class="border-b border-gray-200 bg-white rounded-lg shadow">
        <nav class="-mb-px flex space-x-8 overflow-x-auto px-4">
          <button
            v-for="configType in orderConfigTypes"
            :key="configType.id"
            @click="activeOrderConfigType = configType.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeOrderConfigType === configType.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ configType.label }}
          </button>
        </nav>
      </div>

      <!-- Configs by Website -->
      <div v-if="orderConfigsLoading" class="flex items-center justify-center py-12 bg-white rounded-lg shadow">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!groupedConfigsByWebsite || Object.keys(groupedConfigsByWebsite).length === 0" class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500">No {{ getActiveOrderConfigType().label.toLowerCase() }} found.</p>
        <button
          @click="showOrderConfigModal = true"
          class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          Create First {{ getActiveOrderConfigType().label }}
        </button>
      </div>

      <div v-else class="space-y-6">
        <!-- Each Website Section -->
        <div 
          v-for="(configs, websiteId) in groupedConfigsByWebsite" 
          :key="websiteId"
          class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden"
        >
          <!-- Website Header (Clickable to toggle) -->
          <div 
            @click="toggleWebsiteSection(websiteId)"
            class="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200 cursor-pointer hover:from-blue-100 hover:to-indigo-100 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <!-- Chevron Icon -->
                <div class="shrink-0">
                  <svg 
                    :class="[
                      'w-5 h-5 text-gray-600 transition-transform duration-200',
                      expandedWebsites.has(websiteId) ? 'transform rotate-90' : ''
                    ]"
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="text-xl font-semibold text-gray-900 tracking-tight">{{ getWebsiteName(websiteId) }}</h3>
                  <p class="text-sm text-gray-500 truncate max-w-xs" :title="getWebsiteDomain(websiteId)">
                    {{ truncateDomain(getWebsiteDomain(websiteId)) }}
                  </p>
                </div>
                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {{ configs.length }} {{ getActiveOrderConfigType().label }}
                </span>
              </div>
              <div class="flex gap-2" @click.stop>
                <button
                  v-if="activeOrderConfigType === 'subjects' || activeOrderConfigType === 'paper-types' || activeOrderConfigType === 'types-of-work'"
                  @click="orderConfigSelectedWebsiteId = websiteId; showCloneTemplateModal = true"
                  class="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                  :title="getCloneTemplateButtonTitle()"
                >
                  📚 Clone from Template
                </button>
                <button
                  @click="orderConfigSelectedWebsiteId = websiteId; showCloneModal = true"
                  class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  📋 Clone from Defaults
                </button>
                <button
                  @click="orderConfigSelectedWebsiteId = websiteId; loadUsageAnalytics"
                  class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700"
                >
                  📊 Analytics
                </button>
                <button
                  @click="orderConfigSelectedWebsiteId = websiteId; handleExportConfigs"
                  class="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
                >
                  📥 Export
                </button>
                <button
                  @click="orderConfigSelectedWebsiteId = websiteId; showImportModal = true"
                  class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
                >
                  📤 Import
                </button>
                <button
                  @click="orderConfigSelectedWebsiteId = websiteId; showOrderConfigModal = true"
                  class="px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700"
                >
                  + Add
                </button>
              </div>
            </div>
          </div>

          <!-- Configs Table for this Website (Collapsible) -->
          <div v-show="expandedWebsites.has(websiteId)" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left">
                    <input
                      type="checkbox"
                      :checked="isWebsiteAllSelected(websiteId)"
                      @change="toggleSelectAllForWebsite(websiteId, $event)"
                      class="rounded border-gray-300"
                    />
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th v-if="usageAnalyticsByWebsite[websiteId]" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage</th>
                  <th v-if="activeOrderConfigType === 'subjects'" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Technical</th>
                  <th v-if="activeOrderConfigType === 'english-types'" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="config in configs" 
                  :key="config.id" 
                  class="hover:bg-gray-50" 
                  :class="{ 'bg-yellow-50': config.usage_count === 0 && usageAnalyticsByWebsite[websiteId] }"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      :value="config.id"
                      v-model="selectedConfigs"
                      class="rounded border-gray-300"
                    />
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center gap-2">
                      <div class="text-sm font-medium text-gray-900">{{ config.name }}</div>
                      <span 
                        v-if="config.is_default" 
                        class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs"
                        title="Default configuration"
                      >
                        Default
                      </span>
                      <span 
                        v-else 
                        class="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs"
                        title="Custom configuration"
                      >
                        Custom
                      </span>
                    </div>
                  </td>
                  <td v-if="usageAnalyticsByWebsite[websiteId]" class="px-6 py-4 whitespace-nowrap">
                    <span 
                      :class="[
                        'px-2 py-1 rounded text-xs font-medium',
                        config.usage_count > 0 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-600'
                      ]"
                      :title="config.usage_count > 0 ? `Used in ${config.usage_count} order(s)` : 'Not used in any orders'"
                    >
                      {{ config.usage_count || 0 }}
                    </span>
                  </td>
                  <td v-if="activeOrderConfigType === 'subjects'" class="px-6 py-4 whitespace-nowrap">
                    <span :class="config.is_technical ? 'px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs' : 'px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs'">
                      {{ config.is_technical ? 'Yes' : 'No' }}
                    </span>
                  </td>
                  <td v-if="activeOrderConfigType === 'english-types'" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ config.code || '—' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      @click="editOrderConfig(config)"
                      class="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      @click="deleteOrderConfig(config)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Clone from Defaults Modal -->
    <div v-if="showCloneModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">Clone from Defaults</h3>
            <button @click="closeCloneModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Select Default Set *
              </label>
              <select
                v-model="selectedDefaultSet"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">-- Select a default set --</option>
                <option v-for="set in availableDefaultSets" :key="set.id" :value="set.id">
                  {{ set.name }} - {{ set.description }}
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                Choose which default configuration set to clone from
              </p>
            </div>
            
            <div>
              <label class="flex items-center">
                <input
                  v-model="clearExistingConfigs"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm text-gray-700">Clear existing configurations before cloning</span>
              </label>
              <p class="text-xs text-gray-500 mt-1 ml-6">
                If checked, all existing configs will be deleted before cloning. Otherwise, only missing configs will be added.
              </p>
            </div>
            
            <div v-if="orderConfigSelectedWebsiteId" class="bg-blue-50 p-3 rounded-lg">
              <p class="text-sm text-gray-700">
                <strong>Target Website:</strong> 
                {{ orderConfigWebsites.find(w => w.id == orderConfigSelectedWebsiteId)?.name || orderConfigWebsites.find(w => w.id == orderConfigSelectedWebsiteId)?.domain || 'N/A' }}
              </p>
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-6 mt-6 border-t">
            <button
              @click="closeCloneModal"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              @click="previewCloneChanges"
              :disabled="!selectedDefaultSet || loadingPreview"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loadingPreview ? 'Loading...' : 'Preview Changes' }}
            </button>
            <button
              @click="handleCloneFromDefaults"
              :disabled="!selectedDefaultSet || cloningDefaults"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ cloningDefaults ? 'Cloning...' : 'Clone Configurations' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Clone from Template Modal (for Subjects & Paper Types) -->
    <div v-if="showCloneTemplateModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">
              Clone {{ getCloneTemplateTitle() }} from Template
            </h3>
            <button @click="closeCloneTemplateModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Filter by Category (Optional)
              </label>
              <select
                v-model="selectedTemplateCategory"
                @change="handleCategoryChange"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Categories</option>
                <option v-for="cat in templateCategories" :key="cat.value" :value="cat.value">
                  {{ cat.label }}
                </option>
              </select>
            </div>
            
            <div v-if="loadingTemplates" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p class="text-gray-600">Loading templates...</p>
            </div>
            
            <div v-else-if="getCurrentTemplates().length === 0" class="text-center py-8 text-gray-500">
              <p>No templates available. Contact superadmin to create templates.</p>
            </div>
            
            <div v-else class="space-y-3">
              <div
                v-for="template in getCurrentTemplates()"
                :key="template.id"
                @click="selectedTemplateId = template.id"
                :class="[
                  'p-4 border-2 rounded-lg cursor-pointer transition-all',
                  selectedTemplateId === template.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                ]"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h4 class="font-semibold text-gray-900">{{ template.name }}</h4>
                    <p class="text-sm text-gray-600 mt-1">{{ template.description || 'No description' }}</p>
                    <div class="flex items-center gap-4 mt-2">
                      <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        {{ template.category_display }}
                      </span>
                      <span class="text-xs text-gray-500">
                        {{ getTemplateCount(template) }} {{ getTemplateCountLabel() }}
                      </span>
                    </div>
                  </div>
                  <div v-if="selectedTemplateId === template.id" class="ml-4">
                    <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="getCurrentWebsiteId()" class="bg-blue-50 p-3 rounded-lg">
              <p class="text-sm text-gray-700">
                <strong>Target Website:</strong> 
                {{ getCurrentWebsiteName() }}
              </p>
            </div>
            <div v-else class="bg-yellow-50 p-3 rounded-lg">
              <p class="text-sm text-yellow-700">
                ⚠️ No website detected. Please select a website from the list above or ensure you are assigned to a website.
              </p>
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-6 mt-6 border-t">
            <button
              @click="closeCloneTemplateModal"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              @click="handleCloneFromTemplate"
              :disabled="!selectedTemplateId || !getCurrentWebsiteId() || cloningTemplate"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ cloningTemplate ? 'Cloning...' : `Clone ${getCloneTemplateTitle()}` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview Clone Changes Modal -->
    <div v-if="showPreviewModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">Preview Clone Changes</h3>
            <button @click="showPreviewModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div v-if="loadingPreview" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading preview...</p>
          </div>
          
          <div v-else-if="clonePreview" class="space-y-4">
            <div class="bg-blue-50 p-4 rounded-lg">
              <p class="text-sm text-gray-700">
                <strong>Summary:</strong> {{ clonePreview.summary.total_to_add }} to add, 
                {{ clonePreview.summary.total_to_remove }} to remove, 
                {{ clonePreview.summary.total_to_keep }} to keep
              </p>
            </div>
            
            <div v-for="(preview, configType) in clonePreview.preview" :key="configType" class="border rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-2 capitalize">{{ configType.replace('_', ' ') }}</h4>
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p class="font-medium text-green-700 mb-1">To Add ({{ preview.to_add.length }})</p>
                  <ul class="space-y-1 max-h-32 overflow-y-auto">
                    <li v-for="item in preview.to_add" :key="item" class="text-green-600">+ {{ item }}</li>
                    <li v-if="preview.to_add.length === 0" class="text-gray-400">None</li>
                  </ul>
                </div>
                <div>
                  <p class="font-medium text-red-700 mb-1">To Remove ({{ preview.to_remove.length }})</p>
                  <ul class="space-y-1 max-h-32 overflow-y-auto">
                    <li v-for="item in preview.to_remove" :key="item" class="text-red-600">- {{ item }}</li>
                    <li v-if="preview.to_remove.length === 0" class="text-gray-400">None</li>
                  </ul>
                </div>
                <div>
                  <p class="font-medium text-gray-700 mb-1">To Keep ({{ preview.to_keep.length }})</p>
                  <ul class="space-y-1 max-h-32 overflow-y-auto">
                    <li v-for="item in preview.to_keep" :key="item" class="text-gray-600">= {{ item }}</li>
                    <li v-if="preview.to_keep.length === 0" class="text-gray-400">None</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end gap-2 pt-4 border-t">
              <button @click="showPreviewModal = false" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Analytics Modal -->
    <div v-if="showUsageAnalyticsModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">Usage Analytics</h3>
            <button @click="showUsageAnalyticsModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div v-if="loadingAnalytics" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p class="text-gray-600">Loading analytics...</p>
          </div>
          
          <div v-else-if="usageAnalyticsData" class="space-y-6">
            <div class="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg">
              <div class="grid grid-cols-4 gap-4 text-center">
                <div>
                  <p class="text-2xl font-bold text-purple-700">{{ usageAnalyticsData.summary.total_configs }}</p>
                  <p class="text-sm text-gray-600">Total Configs</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-green-700">{{ usageAnalyticsData.summary.used_configs }}</p>
                  <p class="text-sm text-gray-600">Used</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-gray-700">{{ usageAnalyticsData.summary.unused_configs }}</p>
                  <p class="text-sm text-gray-600">Unused</p>
                </div>
                <div>
                  <p class="text-2xl font-bold text-blue-700">{{ usageAnalyticsData.summary.usage_percentage }}%</p>
                  <p class="text-sm text-gray-600">Usage Rate</p>
                </div>
              </div>
            </div>
            
            <div v-for="(configs, configType) in usageAnalyticsData.analytics" :key="configType" class="border rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-3 capitalize">{{ configType.replace('_', ' ') }} ({{ configs.length }})</h4>
              <div class="space-y-2 max-h-64 overflow-y-auto">
                <div 
                  v-for="config in configs" 
                  :key="config.id"
                  class="flex items-center justify-between p-2 rounded"
                  :class="config.usage_count > 0 ? 'bg-green-50' : 'bg-yellow-50'"
                >
                  <span class="text-sm font-medium">{{ config.name }}</span>
                  <span 
                    :class="[
                      'px-2 py-1 rounded text-xs font-medium',
                      config.usage_count > 0 ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
                    ]"
                  >
                    {{ config.usage_count }} orders
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-gray-900">Import Configurations</h3>
            <button @click="closeImportModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Upload JSON File
              </label>
              <input
                type="file"
                @change="handleFileSelect"
                accept=".json"
                class="w-full border rounded-lg px-4 py-2"
              />
              <p class="text-xs text-gray-500 mt-1">
                Select a JSON file exported from this system
              </p>
            </div>
            
            <div>
              <label class="flex items-center">
                <input
                  v-model="importSkipExisting"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm text-gray-700">Skip existing configurations</span>
              </label>
            </div>
            
            <div v-if="importResult" class="p-4 rounded-lg" :class="importResult.summary.total_errors > 0 ? 'bg-yellow-50' : 'bg-green-50'">
              <p class="font-medium mb-2">{{ importResult.message }}</p>
              <p class="text-sm">
                Created: {{ importResult.summary.total_created }}, 
                Skipped: {{ importResult.summary.total_skipped }}, 
                Errors: {{ importResult.summary.total_errors }}
              </p>
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-6 mt-6 border-t">
            <button @click="closeImportModal" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
              Cancel
            </button>
            <button
              @click="handleImportConfigs"
              :disabled="!importFile || importing"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ importing ? 'Importing...' : 'Import' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Configs -->
    <div v-if="activeTab === 'notifications'" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-semibold">Notification Profiles</h2>
        <button @click="createNotificationConfig" class="btn btn-primary">Create Profile</button>
      </div>
      
      <div class="card">
        <div v-if="notificationConfigsLoading" class="text-center py-12">Loading...</div>
        <div v-else-if="notificationConfigs.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Default</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">In-App</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in notificationConfigs" :key="config.id">
                <td class="px-6 py-4">{{ config.name }}</td>
                <td class="px-6 py-4">
                  <span v-if="config.is_default" class="text-green-600">Yes</span>
                  <span v-else class="text-gray-400">No</span>
                </td>
                <td class="px-6 py-4">
                  <span :class="config.default_email ? 'text-green-600' : 'text-red-600'">
                    {{ config.default_email ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span :class="config.default_in_app ? 'text-green-600' : 'text-red-600'">
                    {{ config.default_in_app ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button @click="editNotificationConfig(config)" class="text-blue-600 hover:underline">Edit</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-12 text-gray-500">No notification profiles found.</div>
      </div>
    </div>

    <!-- Pricing Config Modal -->
    <div v-if="showPricingModal || editingPricingConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingPricingConfig ? 'Edit' : 'Create' }} Pricing Configuration</h2>
            <button @click="closePricingModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="savePricingConfig" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Base Price Per Page ($) *</label>
                <input v-model.number="pricingForm.base_price_per_page" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Base Price Per Slide ($) *</label>
                <input v-model.number="pricingForm.base_price_per_slide" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Technical Multiplier *</label>
                <input v-model.number="pricingForm.technical_multiplier" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Non-Technical Multiplier *</label>
                <input v-model.number="pricingForm.non_technical_order_multiplier" type="number" step="0.01" min="0" required class="w-full border rounded px-3 py-2" />
              </div>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closePricingModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingPricingConfig ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Referral Config Modal -->
    <div v-if="showReferralModal || editingReferralConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingReferralConfig ? 'Edit Referral Config' : 'Create Referral Config' }}
        </h2>
        <form @submit.prevent="saveReferralConfig" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="referralForm.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Website</option>
              <option v-for="website in referralWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                First Order Bonus ($) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="referralForm.first_order_bonus"
                type="number"
                step="0.01"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="0.00"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Discount Type <span class="text-red-500">*</span>
              </label>
              <select
                v-model="referralForm.first_order_discount_type"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="fixed">Fixed Amount</option>
                <option value="percentage">Percentage</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Discount Amount <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="referralForm.first_order_discount_amount"
                type="number"
                step="0.01"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                :placeholder="referralForm.first_order_discount_type === 'percentage' ? 'e.g., 10 (for 10%)' : 'e.g., 5.00'"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Bonus Expiry (Days) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="referralForm.bonus_expiry_days"
                type="number"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="30"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Max Referrals per Month <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="referralForm.max_referrals_per_month"
                type="number"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="10"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Max Bonus per Month ($) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="referralForm.max_referral_bonus_per_month"
                type="number"
                step="0.01"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="100.00"
              />
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeReferralModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingReferralConfig ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Additional Service Modal -->
    <div v-if="showAdditionalServiceModal || editingAdditionalService" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingAdditionalService ? 'Edit Additional Service' : 'Create Additional Service' }}
        </h2>
        <form @submit.prevent="saveAdditionalService" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="additionalServiceForm.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Website</option>
              <option v-for="website in additionalServicesWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Service Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="additionalServiceForm.service_name"
                type="text"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., Plagiarism Report"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Cost ($) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="additionalServiceForm.cost"
                type="number"
                step="0.01"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="0.00"
              />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Slug <span class="text-red-500">*</span>
              </label>
              <input
                v-model="additionalServiceForm.slug"
                type="text"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., plagiarism-report"
              />
              <p class="text-xs text-gray-500 mt-1">Unique identifier for the service (used in URLs)</p>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="additionalServiceForm.description"
                rows="3"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Service description"
              />
            </div>
            <div>
              <label class="flex items-center">
                <input
                  v-model="additionalServiceForm.is_active"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm">Active</span>
              </label>
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeAdditionalServiceModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingAdditionalService ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Preferred Writer Config Modal -->
    <div v-if="showPreferredWriterModal || editingPreferredWriterConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingPreferredWriterConfig ? 'Edit Preferred Writer Config' : 'Create Preferred Writer Config' }}
        </h2>
        <form @submit.prevent="savePreferredWriterConfig" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="preferredWriterForm.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Website</option>
              <option v-for="website in preferredWriterConfigsWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> This configuration applies to <strong>all writers</strong> for the selected website. 
              When a client selects a preferred writer, this cost will be added to the order.
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Preferred Writer Cost ($) <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="preferredWriterForm.preferred_writer_cost"
              type="number"
              step="0.01"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="0.00"
            />
            <p class="text-xs text-gray-500 mt-1">Extra cost for selecting this preferred writer</p>
          </div>
          <div>
            <label class="flex items-center">
              <input
                v-model="preferredWriterForm.is_active"
                type="checkbox"
                class="mr-2"
              />
              <span class="text-sm">Active</span>
            </label>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closePreferredWriterModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingPreferredWriterConfig ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Writer Level Option Modal -->
    <div v-if="showWriterLevelOptionModal || editingWriterLevelOption" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingWriterLevelOption ? 'Edit Writer Level Option' : 'Create Writer Level Option' }}
        </h2>
        <form @submit.prevent="saveWriterLevelOption" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="writerLevelOptionForm.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Website</option>
              <option v-for="website in writerLevelOptionsWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="writerLevelOptionForm.name"
                type="text"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., Top 10, Advanced"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Value ($) <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="writerLevelOptionForm.value"
                type="number"
                step="0.01"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="0.00"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Sort Order</label>
              <input
                v-model.number="writerLevelOptionForm.sort_order"
                type="number"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="0"
              />
            </div>
            <div>
              <label class="flex items-center mt-6">
                <input
                  v-model="writerLevelOptionForm.active"
                  type="checkbox"
                  class="mr-2"
                />
                <span class="text-sm">Active</span>
              </label>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="writerLevelOptionForm.description"
                rows="3"
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Optional client-facing note"
              />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeWriterLevelOptionModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingWriterLevelOption ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Deadline Multiplier Modal -->
    <div v-if="showDeadlineMultiplierModal || editingDeadlineMultiplier" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingDeadlineMultiplier ? 'Edit Deadline Multiplier' : 'Create Deadline Multiplier' }}
        </h2>
        <form @submit.prevent="saveDeadlineMultiplier" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="deadlineMultiplierForm.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select Website</option>
              <option v-for="website in deadlineMultipliersWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Label <span class="text-red-500">*</span>
            </label>
            <input
              v-model="deadlineMultiplierForm.label"
              type="text"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="e.g., 1 Hour, 1 Day, 2 Days"
            />
            <p class="text-xs text-gray-500 mt-1">Human-readable label for this deadline window</p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Hours <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="deadlineMultiplierForm.hours"
                type="number"
                min="1"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="24"
              />
              <p class="text-xs text-gray-500 mt-1">Deadline in hours (e.g., 24 for 1 day)</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Multiplier <span class="text-red-500">*</span>
              </label>
              <input
                v-model.number="deadlineMultiplierForm.multiplier"
                type="number"
                step="0.01"
                min="0"
                max="10"
                required
                class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="1.5"
              />
              <p class="text-xs text-gray-500 mt-1">Price multiplier (e.g., 1.5 for 50% increase)</p>
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeDeadlineMultiplierModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingDeadlineMultiplier ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Writer Config Modal -->
    <div v-if="showWriterModal || editingWriterConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-2xl w-full p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold">{{ editingWriterConfig ? 'Edit' : 'Create' }} Writer Configuration</h2>
          <button @click="closeWriterModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        
        <form @submit.prevent="saveWriterConfig" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="flex items-center">
                <input v-model="writerForm.takes_enabled" type="checkbox" class="mr-2" />
                <span class="text-sm font-medium">Takes Enabled</span>
              </label>
              <p class="text-xs text-gray-500 mt-1">Allow writers to take orders directly</p>
              <p class="text-xs text-gray-400 mt-2 italic">
                Note: Max requests and max takes are now configured per writer level in the Writer Hierarchy section.
              </p>
            </div>
          </div>
          
          <div class="flex justify-end gap-2 pt-4">
            <button type="button" @click="closeWriterModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : (editingWriterConfig ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Notification Config Modal -->
    <div v-if="showNotificationModal || editingNotificationConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingNotificationConfig ? 'Edit' : 'Create' }} Notification Profile</h2>
            <button @click="closeNotificationModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveNotificationConfig" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="col-span-2">
                <label class="block text-sm font-medium mb-1">Website</label>
                <select v-model="notificationForm.website" class="w-full border rounded px-3 py-2" required>
                  <option value="">Select Website</option>
                  <option v-for="website in notificationWebsites" :key="website.id" :value="website.id">
                    {{ website.name }} ({{ website.domain }})
                  </option>
                </select>
              </div>
              
              <div class="col-span-2">
                <label class="block text-sm font-medium mb-1">Name <span class="text-red-500">*</span></label>
                <input v-model="notificationForm.name" type="text" required class="w-full border rounded px-3 py-2" placeholder="e.g., Default Profile, Quiet Hours" />
              </div>
              
              <div class="col-span-2">
                <label class="block text-sm font-medium mb-1">Description</label>
                <textarea v-model="notificationForm.description" rows="2" class="w-full border rounded px-3 py-2" placeholder="Optional description"></textarea>
              </div>
            </div>
            
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-3">Default Channel Settings</h3>
              <div class="grid grid-cols-2 gap-4">
                <label class="flex items-center">
                  <input v-model="notificationForm.default_email" type="checkbox" class="mr-2" />
                  <span class="text-sm">Default Email</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.default_sms" type="checkbox" class="mr-2" />
                  <span class="text-sm">Default SMS</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.default_push" type="checkbox" class="mr-2" />
                  <span class="text-sm">Default Push</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.default_in_app" type="checkbox" class="mr-2" />
                  <span class="text-sm">Default In-App</span>
                </label>
              </div>
            </div>
            
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-3">Channel Enablement</h3>
              <div class="grid grid-cols-2 gap-4">
                <label class="flex items-center">
                  <input v-model="notificationForm.email_enabled" type="checkbox" class="mr-2" />
                  <span class="text-sm">Email Enabled</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.sms_enabled" type="checkbox" class="mr-2" />
                  <span class="text-sm">SMS Enabled</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.push_enabled" type="checkbox" class="mr-2" />
                  <span class="text-sm">Push Enabled</span>
                </label>
                <label class="flex items-center">
                  <input v-model="notificationForm.in_app_enabled" type="checkbox" class="mr-2" />
                  <span class="text-sm">In-App Enabled</span>
                </label>
              </div>
            </div>
            
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-3">Do Not Disturb (DND)</h3>
              <div class="space-y-4">
                <label class="flex items-center">
                  <input v-model="notificationForm.dnd_enabled" type="checkbox" class="mr-2" />
                  <span class="text-sm">Enable Do Not Disturb</span>
                </label>
                
                <div v-if="notificationForm.dnd_enabled" class="grid grid-cols-2 gap-4 ml-6">
                  <div>
                    <label class="block text-sm font-medium mb-1">Start Hour (0-23)</label>
                    <input v-model.number="notificationForm.dnd_start_hour" type="number" min="0" max="23" class="w-full border rounded px-3 py-2" />
                  </div>
                  <div>
                    <label class="block text-sm font-medium mb-1">End Hour (0-23)</label>
                    <input v-model.number="notificationForm.dnd_end_hour" type="number" min="0" max="23" class="w-full border rounded px-3 py-2" />
                  </div>
                </div>
              </div>
            </div>
            
            <div class="border-t pt-4">
              <label class="flex items-center">
                <input v-model="notificationForm.is_default" type="checkbox" class="mr-2" />
                <span class="text-sm font-medium">Set as Default Profile</span>
              </label>
              <p class="text-xs text-gray-500 mt-1">Default profiles are automatically applied to new users</p>
            </div>
            
            <div class="flex justify-end gap-2 pt-4 border-t">
              <button type="button" @click="closeNotificationModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingNotificationConfig ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Order Config Create/Edit Modal -->
    <div v-if="showOrderConfigModal || editingOrderConfig" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold">
            {{ editingOrderConfig ? 'Edit' : 'Create' }} {{ getActiveOrderConfigType().label }}
          </h2>
          <button @click="closeOrderConfigModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <form @submit.prevent="saveOrderConfig" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Website <span class="text-red-500">*</span>
            </label>
            <select
              v-model="orderConfigFormData.website"
              required
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">Select website</option>
              <option v-for="website in orderConfigWebsites" :key="website.id" :value="website.id">
                {{ formatWebsiteName(website) }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="orderConfigFormData.name"
              type="text"
              required
              placeholder="Enter name"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">{{ getActiveOrderConfigType().nameHint }}</p>
          </div>

          <div v-if="activeOrderConfigType === 'subjects'">
            <label class="flex items-center">
              <input
                v-model="orderConfigFormData.is_technical"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="ml-2 text-sm text-gray-700">Technical Subject</span>
            </label>
            <p class="text-xs text-gray-500 mt-1">Check if this subject requires technical expertise</p>
          </div>

          <div v-if="activeOrderConfigType === 'english-types'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Code <span class="text-red-500">*</span>
            </label>
            <input
              v-model="orderConfigFormData.code"
              type="text"
              required
              placeholder="e.g., US, UK, AU, CA, INT"
              maxlength="10"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">ISO code or abbreviation for this English type</p>
          </div>

          <div v-if="activeOrderConfigType === 'writer-deadline-configs'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Writer Deadline Percentage <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="orderConfigFormData.writer_deadline_percentage"
              type="number"
              min="1"
              max="100"
              required
              placeholder="e.g., 80"
              class="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <p class="text-xs text-gray-500 mt-1">Percentage of client deadline given to writer (e.g., 80 means writer gets 80% of client deadline time)</p>
          </div>

          <div class="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              @click="closeOrderConfigModal"
              class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="savingOrderConfig"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {{ savingOrderConfig ? 'Saving...' : (editingOrderConfig ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>


    <!-- Payment Reminders -->
    <div v-if="activeTab === 'payment-reminders'" class="space-y-6">
      <!-- Reminder Configs Section -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-xl font-semibold">Payment Reminder Configurations</h2>
            <p class="text-sm text-gray-600 mt-1">Set reminders based on deadline percentage (e.g., 30%, 50%, 80%)</p>
          </div>
          <button @click="createReminderConfig" class="btn btn-primary">Create Reminder Config</button>
        </div>
        
        <div class="card">
          <div v-if="paymentReminderConfigsLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="paymentReminderConfigs?.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deadline %</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Channels</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="config in paymentReminderConfigs" :key="config.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="config.website_name" class="text-sm">
                      <div class="font-medium text-gray-900">{{ config.website_name }}</div>
                      <div class="text-xs text-gray-500">{{ config.website_domain }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4 text-sm font-medium">{{ config.name }}</td>
                  <td class="px-6 py-4 text-sm">{{ config.deadline_percentage }}%</td>
                  <td class="px-6 py-4 text-sm">
                    <div class="flex gap-2">
                      <span v-if="config.send_as_notification" class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Notification</span>
                      <span v-if="config.send_as_email" class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Email</span>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="config.is_active ? 'text-green-600' : 'text-red-600'" class="font-medium text-sm">
                      {{ config.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <button @click="editReminderConfig(config)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deleteReminderConfig(config.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No reminder configurations found.</div>
        </div>
      </div>

      <!-- Deletion Messages Section -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-xl font-semibold">Deletion Messages</h2>
            <p class="text-sm text-gray-600 mt-1">Messages sent after payment deadline has passed</p>
          </div>
          <button @click="createDeletionMessage" class="btn btn-primary">Create Deletion Message</button>
        </div>
        
        <div class="card">
          <div v-if="paymentDeletionMessagesLoading" class="text-center py-12">Loading...</div>
          <div v-else-if="paymentDeletionMessages?.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message Preview</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Channels</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="message in paymentDeletionMessages" :key="message.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4">
                    <div v-if="message.website_name" class="text-sm">
                      <div class="font-medium text-gray-900">{{ message.website_name }}</div>
                      <div class="text-xs text-gray-500">{{ message.website_domain }}</div>
                    </div>
                    <span v-else class="text-gray-400">N/A</span>
                  </td>
                  <td class="px-6 py-4 text-sm">{{ message.message.substring(0, 100) }}{{ message.message.length > 100 ? '...' : '' }}</td>
                  <td class="px-6 py-4 text-sm">
                    <div class="flex gap-2">
                      <span v-if="message.send_as_notification" class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Notification</span>
                      <span v-if="message.send_as_email" class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Email</span>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span :class="message.is_active ? 'text-green-600' : 'text-red-600'" class="font-medium text-sm">
                      {{ message.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <button @click="editDeletionMessage(message)" class="text-blue-600 hover:underline mr-2">Edit</button>
                    <button @click="deleteDeletionMessage(message.id)" class="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-12 text-gray-500">No deletion messages found.</div>
        </div>
      </div>
    </div>

    <!-- Reminder Config Modal -->
    <div v-if="showReminderConfigModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4">{{ editingReminderConfig ? 'Edit' : 'Create' }} Payment Reminder Config</h3>
        <form @submit.prevent="saveReminderConfig" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
            <select v-model="reminderConfigForm.website" class="w-full border rounded-lg px-3 py-2" required>
              <option value="">Select Website</option>
              <option v-for="website in paymentReminderConfigsWebsites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="reminderConfigForm.name" type="text" class="w-full border rounded-lg px-3 py-2" placeholder="e.g., First Reminder, Final Warning" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deadline Percentage</label>
            <input v-model="reminderConfigForm.deadline_percentage" type="number" step="0.01" min="0" max="100" class="w-full border rounded-lg px-3 py-2" placeholder="e.g., 30.00 for 30%" required />
            <p class="text-xs text-gray-500 mt-1">Percentage of deadline elapsed when to send (0-100)</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
            <textarea v-model="reminderConfigForm.message" rows="4" class="w-full border rounded-lg px-3 py-2" placeholder="Message to send. Use {order_id}, {topic}, {amount}, {deadline} as placeholders" required></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email Subject (optional)</label>
            <input v-model="reminderConfigForm.email_subject" type="text" class="w-full border rounded-lg px-3 py-2" placeholder="Leave blank for default subject" />
          </div>
          <div class="flex gap-4">
            <label class="flex items-center">
              <input v-model="reminderConfigForm.send_as_notification" type="checkbox" class="mr-2" />
              <span class="text-sm">Send as Notification</span>
            </label>
            <label class="flex items-center">
              <input v-model="reminderConfigForm.send_as_email" type="checkbox" class="mr-2" />
              <span class="text-sm">Send as Email</span>
            </label>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="reminderConfigForm.is_active" type="checkbox" class="mr-2" />
              <span class="text-sm">Active</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
            <input v-model="reminderConfigForm.display_order" type="number" class="w-full border rounded-lg px-3 py-2" placeholder="0" />
            <p class="text-xs text-gray-500 mt-1">Lower numbers appear first</p>
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button type="button" @click="closeReminderConfigModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Deletion Message Modal -->
    <div v-if="showDeletionMessageModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4">{{ editingDeletionMessage ? 'Edit' : 'Create' }} Deletion Message</h3>
        <form @submit.prevent="saveDeletionMessage" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
            <select v-model="deletionMessageForm.website" class="w-full border rounded-lg px-3 py-2" required>
              <option value="">Select Website</option>
              <option v-for="website in paymentDeletionMessagesWebsites" :key="website.id" :value="website.id">
                {{ website.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
            <textarea v-model="deletionMessageForm.message" rows="4" class="w-full border rounded-lg px-3 py-2" placeholder="Message to send when order is deleted. Use {order_id}, {topic}, {deadline} as placeholders" required></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email Subject (optional)</label>
            <input v-model="deletionMessageForm.email_subject" type="text" class="w-full border rounded-lg px-3 py-2" placeholder="Leave blank for default subject" />
          </div>
          <div class="flex gap-4">
            <label class="flex items-center">
              <input v-model="deletionMessageForm.send_as_notification" type="checkbox" class="mr-2" />
              <span class="text-sm">Send as Notification</span>
            </label>
            <label class="flex items-center">
              <input v-model="deletionMessageForm.send_as_email" type="checkbox" class="mr-2" />
              <span class="text-sm">Send as Email</span>
            </label>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="deletionMessageForm.is_active" type="checkbox" class="mr-2" />
              <span class="text-sm">Active</span>
            </label>
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button type="button" @click="closeDeletionMessageModal" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
            <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
    <div v-if="orderConfigError" class="p-3 rounded bg-red-50 text-red-700">{{ orderConfigError }}</div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import adminManagementAPI from '@/api/admin-management'
import orderConfigsAPI from '@/api/orderConfigs'
import websitesAPI from '@/api/websites'
import referralsAPI from '@/api/referrals'
import pricingAPI from '@/api/pricing'
import writerManagementAPI from '@/api/writer-management'
import paymentRemindersAPI from '@/api/payment-reminders'
import apiClient from '@/api/client'
import { debounce } from '@/utils/debounce'
import { exportToCSV } from '@/utils/export'
import { formatWebsiteName } from '@/utils/formatDisplay'
import FilterBar from '@/components/common/FilterBar.vue'
import DataTable from '@/components/common/DataTable.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const authStore = useAuthStore()
const confirm = useConfirmDialog()

const activeTab = ref('pricing')
const activePricingSubTab = ref('base-pricing')
const tabs = [
  { id: 'pricing', label: 'Pricing' },
  { id: 'writer', label: 'Writer' },
  { id: 'order-configs', label: 'Order Configs' },
  { id: 'referrals', label: 'Referrals' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'payment-reminders', label: 'Payment Reminders' },
]

const pricingSubTabs = [
  { id: 'base-pricing', label: 'Base Pricing' },
  { id: 'additional-services', label: 'Additional Services' },
  { id: 'preferred-writers', label: 'Preferred Writers' },
  { id: 'writer-levels', label: 'Writer Levels' },
  { id: 'deadline-multipliers', label: 'Deadline Multipliers' },
]

const pricingConfigs = ref([])
const writerConfigs = ref([])
const notificationConfigs = ref([])
const referralConfigs = ref([])
const referralWebsites = ref([])
const additionalServices = ref([])
const additionalServicesWebsites = ref([])
const preferredWriterConfigs = ref([])
const preferredWriterConfigsWebsites = ref([])
const writerLevelOptions = ref([])
const writerLevelOptionsWebsites = ref([])
const deadlineMultipliers = ref([])
const deadlineMultipliersWebsites = ref([])
const writerDeadlineConfigs = ref([])
const pricingConfigsLoading = ref(false)
const writerConfigsLoading = ref(false)
const notificationConfigsLoading = ref(false)
const referralConfigsLoading = ref(false)
const additionalServicesLoading = ref(false)
const preferredWriterConfigsLoading = ref(false)
const writerLevelOptionsLoading = ref(false)
const deadlineMultipliersLoading = ref(false)

// Payment Reminder refs
const paymentReminderConfigs = ref([])
const paymentReminderConfigsLoading = ref(false)
const paymentReminderConfigsWebsites = ref([])
const paymentDeletionMessages = ref([])
const paymentDeletionMessagesLoading = ref(false)
const paymentDeletionMessagesWebsites = ref([])
const showReminderConfigModal = ref(false)
const showDeletionMessageModal = ref(false)
const editingReminderConfig = ref(null)
const editingDeletionMessage = ref(null)
const reminderConfigForm = ref({
  website: '',
  name: '',
  deadline_percentage: 30.00,
  message: '',
  send_as_notification: true,
  send_as_email: true,
  email_subject: '',
  is_active: true,
  display_order: 0,
})
const deletionMessageForm = ref({
  website: '',
  message: '',
  send_as_notification: true,
  send_as_email: true,
  email_subject: '',
  is_active: true,
})

const showPricingModal = ref(false)
const showWriterModal = ref(false)
const showNotificationModal = ref(false)
const showReferralModal = ref(false)
const showAdditionalServiceModal = ref(false)
const showPreferredWriterModal = ref(false)
const showWriterLevelOptionModal = ref(false)
const showDeadlineMultiplierModal = ref(false)
const editingPricingConfig = ref(null)
const editingWriterConfig = ref(null)
const editingNotificationConfig = ref(null)
const editingReferralConfig = ref(null)
const editingAdditionalService = ref(null)
const editingPreferredWriterConfig = ref(null)
const editingWriterLevelOption = ref(null)
const editingDeadlineMultiplier = ref(null)
const saving = ref(false)

// Rush / Same‑day classification mirrors backend UrgencyService
const classifyUrgency = (hours) => {
  const h = Number(hours || 0)
  if (h <= 6) return 'rush'
  if (h <= 24) return 'same_day'
  return 'standard'
}

const formatUrgencyLabel = (hours) => {
  const level = classifyUrgency(hours)
  if (level === 'rush') return 'Rush'
  if (level === 'same_day') return 'Same‑day'
  return 'Standard'
}

const pricingForm = ref({
  base_price_per_page: 0,
  base_price_per_slide: 0,
  technical_multiplier: 1.0,
  non_technical_order_multiplier: 1.0,
})

const writerForm = ref({
  takes_enabled: true,
})

const notificationForm = ref({
  website: '',
  name: '',
  description: '',
  default_email: true,
  default_sms: false,
  default_push: false,
  default_in_app: true,
  email_enabled: true,
  sms_enabled: false,
  push_enabled: false,
  in_app_enabled: true,
  dnd_enabled: false,
  dnd_start_hour: 22,
  dnd_end_hour: 6,
  is_default: false,
})

const notificationWebsites = ref([])

const referralForm = ref({
  website: '',
  first_order_bonus: 0,
  first_order_discount_type: 'fixed',
  first_order_discount_amount: 0,
  bonus_expiry_days: 30,
  max_referrals_per_month: 10,
  max_referral_bonus_per_month: 100.0,
})

const additionalServiceForm = ref({
  website: '',
  service_name: '',
  description: '',
  cost: 0,
  slug: '',
  is_active: true,
})

const preferredWriterForm = ref({
  website: '',
  preferred_writer_cost: 0,
  is_active: true,
})

const writerLevelOptionForm = ref({
  website: '',
  name: '',
  value: 0,
  description: '',
  active: true,
  sort_order: 0,
})

const deadlineMultiplierForm = ref({
  website: '',
  label: '',
  hours: 24,
  multiplier: 1.0,
})

const message = ref('')
const messageSuccess = ref(false)


// Order Configs state
const orderConfigTypes = [
  {
    id: 'paper-types',
    label: 'Paper Types',
    description: 'Types of papers (Essay, Research Paper, etc.)',
    nameHint: 'e.g., Essay, Research Paper, Dissertation, Thesis'
  },
  {
    id: 'academic-levels',
    label: 'Academic Levels',
    description: 'Academic levels (High School, University, Masters, etc.)',
    nameHint: 'e.g., High School, Undergraduate, Masters, PhD'
  },
  {
    id: 'formatting-styles',
    label: 'Formatting Styles',
    description: 'Citation and formatting styles (APA, MLA, Chicago, etc.)',
    nameHint: 'e.g., APA, MLA, Chicago, Harvard, IEEE'
  },
  {
    id: 'subjects',
    label: 'Subjects',
    description: 'Academic subjects and disciplines',
    nameHint: 'e.g., Mathematics, English, Computer Science, Biology'
  },
  {
    id: 'types-of-work',
    label: 'Types of Work',
    description: 'Types of work requested (Writing, Editing, etc.)',
    nameHint: 'e.g., Writing, Editing, Proofreading, Rewriting'
  },
  {
    id: 'english-types',
    label: 'English Types',
    description: 'English language variants (US, UK, AU, etc.)',
    nameHint: 'e.g., US English, UK English, Australian English'
  }
]

const activeOrderConfigType = ref('paper-types')
const orderConfigSelectedWebsiteId = ref('')
const orderConfigSearchQuery = ref('')
const orderConfigsLoading = ref(false)
const savingOrderConfig = ref(false)
const orderConfigError = ref('')
const populatingDefaults = ref(false)

// Clone from defaults
const showCloneModal = ref(false)
const availableDefaultSets = ref([])
const selectedDefaultSet = ref('')
const clearExistingConfigs = ref(false)
const cloningDefaults = ref(false)
const loadingPreview = ref(false)
const showPreviewModal = ref(false)
const clonePreview = ref(null)

// Clone from templates (for subjects, paper types, and types of work)
const showCloneTemplateModal = ref(false)
const subjectTemplates = ref([])
const paperTypeTemplates = ref([])
const typeOfWorkTemplates = ref([])
const selectedTemplateId = ref('')
const cloningTemplate = ref(false)
const templateCategories = ref([])
const selectedTemplateCategory = ref('')
const loadingTemplates = ref(false)

// Bulk operations
const selectedConfigs = ref([])
const bulkDeleting = ref(false)

// Usage analytics
const showUsageAnalyticsModal = ref(false)
const loadingAnalytics = ref(false)
const usageAnalyticsData = ref(null)
const usageAnalytics = ref(false) // Track if analytics are loaded

// Import/Export
const showImportModal = ref(false)
const importFile = ref(null)
const importSkipExisting = ref(true)
const importing = ref(false)
const importResult = ref(null)

const orderConfigWebsites = ref([])
const orderConfigs = ref([])
const showOrderConfigModal = ref(false)
const editingOrderConfig = ref(null)

const orderConfigFormData = ref({
  website: '',
  name: '',
  is_technical: false,
  code: ''
})

const getActiveOrderConfigType = () => {
  return orderConfigTypes.find(t => t.id === activeOrderConfigType.value) || orderConfigTypes[0]
}

// Helper functions for website info (defined before computed properties that use them)
const getWebsiteName = (websiteId) => {
  if (websiteId === 'unknown') return 'Unknown Website'
  
  // Safety check: ensure orderConfigWebsites.value is an array
  if (Array.isArray(orderConfigWebsites.value)) {
    const website = orderConfigWebsites.value.find(w => w.id == websiteId)
    if (website) return website.name
  }
  
  // Try to get from configs
  if (Array.isArray(orderConfigs.value)) {
    const config = orderConfigs.value.find(c => (c.website?.id || c.website_id || c.website) == websiteId)
    if (config) return config.website?.name || config.website_name || config.website?.domain || 'N/A'
  }
  
  return `Website ${websiteId}`
}

const getWebsiteDomain = (websiteId) => {
  if (websiteId === 'unknown') return ''
  
  // Safety check: ensure orderConfigWebsites.value is an array
  if (Array.isArray(orderConfigWebsites.value)) {
    const website = orderConfigWebsites.value.find(w => w.id == websiteId)
    if (website) return website.domain
  }
  
  // Try to get from configs
  if (Array.isArray(orderConfigs.value)) {
    const config = orderConfigs.value.find(c => (c.website?.id || c.website_id || c.website) == websiteId)
    if (config) return config.website?.domain || config.website_domain || ''
  }
  
  return ''
}

// Truncate domain for display
const truncateDomain = (domain) => {
  if (!domain) return ''
  if (domain.length <= 40) return domain
  return domain.substring(0, 37) + '...'
}

const filteredOrderConfigs = computed(() => {
  let filtered = [...orderConfigs.value]
  
  if (orderConfigSearchQuery.value) {
    const query = orderConfigSearchQuery.value.toLowerCase()
    filtered = filtered.filter(c => 
      c.name?.toLowerCase().includes(query) ||
      c.website?.name?.toLowerCase().includes(query) ||
      c.website?.domain?.toLowerCase().includes(query) ||
      c.website_name?.toLowerCase().includes(query) ||
      c.website_domain?.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

// Group configs by website
const groupedConfigsByWebsite = computed(() => {
  const grouped = {}
  
  filteredOrderConfigs.value.forEach(config => {
    const websiteId = config.website?.id || config.website_id || config.website || 'unknown'
    if (!grouped[websiteId]) {
      grouped[websiteId] = []
    }
    grouped[websiteId].push(config)
  })
  
  // Sort websites by name for consistent display
  const sorted = {}
  Object.keys(grouped).sort((a, b) => {
    const nameA = getWebsiteName(a).toLowerCase()
    const nameB = getWebsiteName(b).toLowerCase()
    return nameA.localeCompare(nameB)
  }).forEach(key => {
    sorted[key] = grouped[key]
  })
  
  return sorted
})

// Website-specific selection
const isWebsiteAllSelected = (websiteId) => {
  const websiteConfigs = groupedConfigsByWebsite.value[websiteId] || []
  if (websiteConfigs.length === 0) return false
  return websiteConfigs.every(config => selectedConfigs.value.includes(config.id))
}

const toggleSelectAllForWebsite = (websiteId, event) => {
  const websiteConfigs = groupedConfigsByWebsite.value[websiteId] || []
  const websiteConfigIds = websiteConfigs.map(c => c.id)
  
  if (event.target.checked) {
    // Add all website configs to selection
    websiteConfigIds.forEach(id => {
      if (!selectedConfigs.value.includes(id)) {
        selectedConfigs.value.push(id)
      }
    })
  } else {
    // Remove all website configs from selection
    selectedConfigs.value = selectedConfigs.value.filter(id => !websiteConfigIds.includes(id))
  }
}

// Usage analytics by website
const usageAnalyticsByWebsite = ref({})

// Collapsible state for website sections
const expandedWebsites = ref(new Set())

// Toggle website section expand/collapse
const toggleWebsiteSection = (websiteId) => {
  if (expandedWebsites.value.has(websiteId)) {
    expandedWebsites.value.delete(websiteId)
  } else {
    expandedWebsites.value.add(websiteId)
  }
}

const debouncedOrderConfigSearch = debounce(() => {
  // Search is handled by computed property
}, 300)

const loadOrderConfigWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites()
    // Ensure it's always an array
    const websites = res.data?.results || res.data || []
    orderConfigWebsites.value = Array.isArray(websites) ? websites : []
  } catch (e) {
    console.error('Failed to load websites:', e)
    orderConfigError.value = 'Failed to load websites'
    // Ensure it's always an array even on error
    orderConfigWebsites.value = []
  }
}

const loadOrderConfigs = async () => {
  orderConfigsLoading.value = true
  orderConfigError.value = ''
  
  // Safety timeout - ensure loading state clears after 30 seconds
  const timeoutId = setTimeout(() => {
    if (orderConfigsLoading.value) {
      console.error('Order configs loading timeout')
      orderConfigsLoading.value = false
      orderConfigError.value = 'Loading timeout - please refresh the page'
      message.value = 'Loading took too long. Please try refreshing the page.'
      messageSuccess.value = false
    }
  }, 30000)
  
  try {
    // Load all configs (no website filter) to show grouped by website
    // Backend will return all configs if no website_id is provided
    const params = {}
    let res
    
    // Loading order configs for selected type
    
    switch (activeOrderConfigType.value) {
      case 'paper-types':
        res = await orderConfigsAPI.getPaperTypes(params)
        break
      case 'academic-levels':
        res = await orderConfigsAPI.getAcademicLevels(params)
        break
      case 'formatting-styles':
        res = await orderConfigsAPI.getFormattingStyles(params)
        break
      case 'subjects':
        res = await orderConfigsAPI.getSubjects(params)
        break
      case 'types-of-work':
        res = await orderConfigsAPI.getTypesOfWork(params)
        break
      case 'english-types':
        res = await orderConfigsAPI.getEnglishTypes(params)
        break
      default:
        res = { data: { results: [] } }
    }
    
    // API response received
    
    // Handle both paginated and non-paginated responses
    let configs = []
    if (res.data?.results) {
      // Paginated response
      configs = res.data.results
      // If there are more pages, load them (optional - can be added later)
    } else if (Array.isArray(res.data)) {
      // Direct array response
      configs = res.data
    } else if (res.data && typeof res.data === 'object') {
      // Try to extract array from response
      configs = Object.values(res.data).find(Array.isArray) || []
    }
    
    // Configs loaded
    
    // Set configs immediately (don't wait for defaults check)
    orderConfigs.value = configs.map(config => ({
      ...config,
      is_default: false // Will be updated asynchronously
    }))
    
    // Mark which configs are defaults (check for each unique website in parallel, non-blocking)
    // This runs asynchronously and doesn't block the UI
    const uniqueWebsiteIds = [...new Set(configs.map(c => {
      const websiteId = c.website?.id || c.website_id || c.website
      return websiteId ? String(websiteId) : null
    }).filter(Boolean))]
    
    // Processing unique website IDs
    
    // Check defaults in parallel (non-blocking) - fire and forget
    if (uniqueWebsiteIds.length > 0) {
      // Don't await - let it run in background
      Promise.all(
        uniqueWebsiteIds.map(async (websiteId) => {
          try {
            const defaultsCheck = await orderConfigsAPI.checkDefaults(websiteId)
            const defaultsData = defaultsCheck.data?.configurations || {}
            
            const configTypeMap = {
              'paper-types': 'paper_types',
              'academic-levels': 'academic_levels',
              'formatting-styles': 'formatting_styles',
              'subjects': 'subjects',
              'types-of-work': 'types_of_work',
              'english-types': 'english_types',
            }
            
            const defaultsList = defaultsData[configTypeMap[activeOrderConfigType.value]] || []
            const defaultsMap = new Map(defaultsList.map(d => [d.id, d.is_default]))
            
            // Update configs with defaults info
            orderConfigs.value = orderConfigs.value.map(config => {
              const configWebsiteId = String(config.website?.id || config.website_id || config.website || '')
              if (configWebsiteId === String(websiteId) && defaultsMap.has(config.id)) {
                return {
                  ...config,
                  is_default: defaultsMap.get(config.id)
                }
              }
              return config
            })
          } catch (e) {
            // If check fails for a website, continue silently
            console.warn(`Failed to check defaults for website ${websiteId}:`, e)
          }
        })
      ).catch(err => {
        console.warn('Error checking defaults (non-critical):', err)
      })
    }
  } catch (e) {
    console.error('Failed to load order configs:', e)
    orderConfigError.value = e.response?.data?.detail || e.message || 'Failed to load configurations'
    message.value = orderConfigError.value
    messageSuccess.value = false
    orderConfigs.value = [] // Set empty array on error
  } finally {
    clearTimeout(timeoutId)
    orderConfigsLoading.value = false
  }
}

// Load available default sets
const loadAvailableDefaultSets = async () => {
  try {
    const res = await orderConfigsAPI.getAvailableDefaultSets()
    availableDefaultSets.value = res.data || []
  } catch (error) {
    console.error('Failed to load default sets:', error)
    availableDefaultSets.value = []
  }
}

// Clone from defaults
const handleCloneFromDefaults = async () => {
  if (!orderConfigSelectedWebsiteId.value) {
    orderConfigError.value = 'Please select a website first'
    return
  }
  
  if (!selectedDefaultSet.value) {
    orderConfigError.value = 'Please select a default set'
    return
  }
  
  cloningDefaults.value = true
  orderConfigError.value = ''
  message.value = ''
  
  try {
    const res = await orderConfigsAPI.cloneFromDefaults(
      orderConfigSelectedWebsiteId.value,
      selectedDefaultSet.value,
      clearExistingConfigs.value
    )
    const summary = res.data?.summary || {}
    const totalCreated = summary.total_created || 0
    const defaultSetName = availableDefaultSets.value.find(s => s.id === selectedDefaultSet.value)?.name || selectedDefaultSet.value
    
    if (totalCreated > 0) {
      message.value = `Successfully cloned ${totalCreated} configuration(s) from "${defaultSetName}" default set`
      messageSuccess.value = true
      closeCloneModal()
      await loadOrderConfigs()
      setTimeout(() => { message.value = '' }, 5000)
    } else {
      message.value = `No new configurations were added. All configs from "${defaultSetName}" already exist.`
      messageSuccess.value = true
      closeCloneModal()
      setTimeout(() => { message.value = '' }, 5000)
    }
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || error.message || 'Failed to clone configurations'
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    cloningDefaults.value = false
  }
}

const closeCloneModal = () => {
  showCloneModal.value = false
  selectedDefaultSet.value = ''
  clearExistingConfigs.value = false
  orderConfigError.value = ''
}

const getCloneTemplateTitle = () => {
  if (activeOrderConfigType.value === 'subjects') return 'Subjects'
  if (activeOrderConfigType.value === 'paper-types') return 'Paper Types'
  if (activeOrderConfigType.value === 'types-of-work') return 'Types of Work'
  return 'Items'
}

const getCurrentTemplates = () => {
  if (activeOrderConfigType.value === 'subjects') return subjectTemplates.value
  if (activeOrderConfigType.value === 'paper-types') return paperTypeTemplates.value
  if (activeOrderConfigType.value === 'types-of-work') return typeOfWorkTemplates.value
  return []
}

const getTemplateCount = (template) => {
  if (activeOrderConfigType.value === 'subjects') return template.subject_count || 0
  if (activeOrderConfigType.value === 'paper-types') return template.paper_type_count || 0
  if (activeOrderConfigType.value === 'types-of-work') return template.type_count || 0
  return 0
}

const getTemplateCountLabel = () => {
  if (activeOrderConfigType.value === 'subjects') return 'subjects'
  if (activeOrderConfigType.value === 'paper-types') return 'paper types'
  if (activeOrderConfigType.value === 'types-of-work') return 'types'
  return 'items'
}

const closeCloneTemplateModal = () => {
  showCloneTemplateModal.value = false
  selectedTemplateId.value = ''
  selectedTemplateCategory.value = ''
  subjectTemplates.value = []
  paperTypeTemplates.value = []
  typeOfWorkTemplates.value = []
  orderConfigError.value = ''
}

const loadSubjectTemplates = async () => {
  loadingTemplates.value = true
  try {
    const params = {}
    if (selectedTemplateCategory.value) {
      params.category = selectedTemplateCategory.value
    }
    const res = await orderConfigsAPI.getSubjectTemplates(params)
    subjectTemplates.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (error) {
    console.error('Failed to load templates:', error)
    message.value = 'Failed to load templates: ' + (error.response?.data?.detail || error.message)
    messageSuccess.value = false
  } finally {
    loadingTemplates.value = false
  }
}

const loadPaperTypeTemplates = async () => {
  loadingTemplates.value = true
  try {
    const params = {}
    if (selectedTemplateCategory.value) {
      params.category = selectedTemplateCategory.value
    }
    const res = await orderConfigsAPI.getPaperTypeTemplates(params)
    paperTypeTemplates.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (error) {
    console.error('Failed to load templates:', error)
    message.value = 'Failed to load templates: ' + (error.response?.data?.detail || error.message)
    messageSuccess.value = false
  } finally {
    loadingTemplates.value = false
  }
}

const loadTypeOfWorkTemplates = async () => {
  loadingTemplates.value = true
  try {
    const params = {}
    if (selectedTemplateCategory.value) {
      params.category = selectedTemplateCategory.value
    }
    const res = await orderConfigsAPI.getTypeOfWorkTemplates(params)
    typeOfWorkTemplates.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (error) {
    console.error('Failed to load templates:', error)
    message.value = 'Failed to load templates: ' + (error.response?.data?.detail || error.message)
    messageSuccess.value = false
  } finally {
    loadingTemplates.value = false
  }
}

const loadTemplateCategories = async () => {
  try {
    if (activeOrderConfigType.value === 'subjects') {
      const res = await orderConfigsAPI.getSubjectTemplateCategories()
      templateCategories.value = Array.isArray(res.data) ? res.data : []
    } else if (activeOrderConfigType.value === 'paper-types') {
      const res = await orderConfigsAPI.getPaperTypeTemplateCategories()
      templateCategories.value = Array.isArray(res.data) ? res.data : []
    } else if (activeOrderConfigType.value === 'types-of-work') {
      const res = await orderConfigsAPI.getTypeOfWorkTemplateCategories()
      templateCategories.value = Array.isArray(res.data) ? res.data : []
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleCloneFromTemplate = async () => {
  if (!selectedTemplateId.value) {
    orderConfigError.value = 'Please select a template'
    return
  }
  
  // Auto-detect website if not set
  const websiteId = orderConfigSelectedWebsiteId.value || getCurrentWebsiteId()
  if (!websiteId) {
    orderConfigError.value = 'Please select a website or ensure you are assigned to a website'
    return
  }
  
  cloningTemplate.value = true
  orderConfigError.value = ''
  message.value = ''
  
  try {
    let res
    if (activeOrderConfigType.value === 'subjects') {
      res = await orderConfigsAPI.cloneSubjectTemplateToWebsite(
        selectedTemplateId.value,
        websiteId,
        true // skip_existing = true
      )
    } else if (activeOrderConfigType.value === 'paper-types') {
      res = await orderConfigsAPI.clonePaperTypeTemplateToWebsite(
        selectedTemplateId.value,
        websiteId,
        true // skip_existing = true
      )
    } else if (activeOrderConfigType.value === 'types-of-work') {
      res = await orderConfigsAPI.cloneTypeOfWorkTemplateToWebsite(
        selectedTemplateId.value,
        websiteId,
        true // skip_existing = true
      )
    } else {
      throw new Error('Invalid config type for template cloning')
    }
    
    const results = res.data?.results || {}
    const created = results.created || 0
    const updated = results.updated || 0
    const skipped = results.skipped || 0
    
    message.value = `Successfully cloned template! Created: ${created}, Updated: ${updated}, Skipped: ${skipped}`
    messageSuccess.value = true
    
    // Reload configs
    await loadOrderConfigs()
    
    // Close modal
    closeCloneTemplateModal()
    
    setTimeout(() => { message.value = '' }, 5000)
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || 'Failed to clone template'
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    cloningTemplate.value = false
  }
}

// Get current website ID from auth store
const getCurrentWebsiteId = () => {
  // First try from orderConfigSelectedWebsiteId (set when clicking clone button)
  if (orderConfigSelectedWebsiteId.value) {
    return orderConfigSelectedWebsiteId.value
  }
  
  // Try from auth store user
  const user = authStore.user
  if (user) {
    if (user.website_id) {
      return user.website_id
    }
    if (user.website?.id) {
      return user.website.id
    }
    if (typeof user.website === 'number') {
      return user.website
    }
  }
  
  // Try from localStorage
  const storedWebsite = localStorage.getItem('current_website')
  if (storedWebsite) {
    const parsed = parseInt(storedWebsite)
    if (!isNaN(parsed)) {
      return parsed
    }
  }
  
  const storedWebsiteId = localStorage.getItem('website_id')
  if (storedWebsiteId) {
    const parsed = parseInt(storedWebsiteId)
    if (!isNaN(parsed)) {
      return parsed
    }
  }
  
  return null
}

// Get current website name
const getCurrentWebsiteName = () => {
  const websiteId = getCurrentWebsiteId()
  if (!websiteId) {
    return 'N/A'
  }
  
  const website = orderConfigWebsites.value.find(w => w.id == websiteId)
  if (website) {
    return website.name
  }
  
  // If not in list, try to get from auth store
  const user = authStore.user
  if (user?.website?.name) {
    return user.website.name
  }
  
  return 'Unknown'
}

// Watch for modal opening to load templates
watch(showCloneTemplateModal, (newVal) => {
  if (newVal) {
    // Auto-detect website if not already set
    if (!orderConfigSelectedWebsiteId.value) {
      const websiteId = getCurrentWebsiteId()
      if (websiteId) {
        orderConfigSelectedWebsiteId.value = websiteId
      }
    }
    
    loadTemplateCategories()
    if (activeOrderConfigType.value === 'subjects') {
      loadSubjectTemplates()
    } else if (activeOrderConfigType.value === 'paper-types') {
      loadPaperTypeTemplates()
    } else if (activeOrderConfigType.value === 'types-of-work') {
      loadTypeOfWorkTemplates()
    }
  }
})

// Handle category change to reload templates
const handleCategoryChange = () => {
  if (showCloneTemplateModal.value) {
    if (activeOrderConfigType.value === 'subjects') {
      loadSubjectTemplates()
    } else if (activeOrderConfigType.value === 'paper-types') {
      loadPaperTypeTemplates()
    } else if (activeOrderConfigType.value === 'types-of-work') {
      loadTypeOfWorkTemplates()
    }
  }
}

// Watch for category change to reload templates
watch(selectedTemplateCategory, () => {
  handleCategoryChange()
})

// Load default sets when modal opens
watch(showCloneModal, (isOpen) => {
  if (isOpen && availableDefaultSets.value.length === 0) {
    loadAvailableDefaultSets()
  }
})

// Clear selections when config type changes
watch(activeOrderConfigType, () => {
  selectedConfigs.value = []
  usageAnalytics.value = false
})

// Preview clone changes
const previewCloneChanges = async () => {
  if (!orderConfigSelectedWebsiteId.value || !selectedDefaultSet.value) return
  
  loadingPreview.value = true
  try {
    const res = await orderConfigsAPI.previewClone(
      orderConfigSelectedWebsiteId.value,
      selectedDefaultSet.value,
      clearExistingConfigs.value
    )
    clonePreview.value = res.data
    showPreviewModal.value = true
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || error.message || 'Failed to load preview'
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    loadingPreview.value = false
  }
}

// Load usage analytics
const loadUsageAnalytics = async () => {
  if (!orderConfigSelectedWebsiteId.value) return
  
  loadingAnalytics.value = true
  showUsageAnalyticsModal.value = true
  try {
    const res = await orderConfigsAPI.getUsageAnalytics(orderConfigSelectedWebsiteId.value)
    usageAnalyticsData.value = res.data
    
    // Merge usage counts into orderConfigs for this website
    const analyticsMap = {}
    const configTypeMap = {
      'paper-types': 'paper_types',
      'formatting-styles': 'formatting_styles',
      'academic-levels': 'academic_levels',
      'subjects': 'subjects',
      'types-of-work': 'types_of_work',
      'english-types': 'english_types',
    }
    
    const currentType = configTypeMap[activeOrderConfigType.value]
    if (currentType && res.data.analytics[currentType]) {
      res.data.analytics[currentType].forEach(item => {
        analyticsMap[item.id] = item.usage_count
      })
      
      // Update usage counts for this website's configs
      orderConfigs.value = orderConfigs.value.map(config => {
        const websiteId = config.website?.id || config.website_id || config.website
        if (websiteId == orderConfigSelectedWebsiteId.value) {
          return {
            ...config,
            usage_count: analyticsMap[config.id] || 0
          }
        }
        return config
      })
      
      // Mark this website as having analytics loaded
      usageAnalyticsByWebsite.value[orderConfigSelectedWebsiteId.value] = true
    }
    
    usageAnalytics.value = true
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || error.message || 'Failed to load analytics'
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    loadingAnalytics.value = false
  }
}

// Bulk operations
const toggleSelectAll = (event) => {
  if (event.target.checked) {
    selectedConfigs.value = filteredOrderConfigs.value.map(c => c.id)
  } else {
    selectedConfigs.value = []
  }
}

const handleBulkDelete = async () => {
  if (!selectedConfigs.value.length) return
  
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete ${selectedConfigs.value.length} selected configuration(s)?`,
    'Delete Selected Configurations',
    {
      details: 'This action cannot be undone. All selected configurations will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  bulkDeleting.value = true
  orderConfigError.value = ''
  message.value = ''
  
  try {
    // Bulk delete doesn't require website_id, it validates from the configs themselves
    const res = await orderConfigsAPI.bulkDelete(
      activeOrderConfigType.value,
      selectedConfigs.value,
      null // website_id is optional, backend will validate from configs
    )
    
    message.value = res.data.message || `Successfully deleted ${res.data.deleted_count} configuration(s)`
    messageSuccess.value = true
    selectedConfigs.value = []
    await loadOrderConfigs()
    setTimeout(() => { message.value = '' }, 5000)
  } catch (error) {
    const errorData = error.response?.data
    if (errorData?.used_configs && errorData.used_configs.length > 0) {
      const usedNames = errorData.used_configs.map(c => c.name).join(', ')
      orderConfigError.value = `${errorData.message} Used configs: ${usedNames}`
    } else {
      orderConfigError.value = errorData?.detail || error.message || 'Failed to delete configurations'
    }
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    bulkDeleting.value = false
  }
}

// Export/Import
const handleExportConfigs = async () => {
  if (!orderConfigSelectedWebsiteId.value) return
  
  try {
    const res = await orderConfigsAPI.exportConfigs(orderConfigSelectedWebsiteId.value)
    const dataStr = JSON.stringify(res.data, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `order-configs-${res.data.website.name}-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
    
    message.value = 'Configurations exported successfully'
    messageSuccess.value = true
    setTimeout(() => { message.value = '' }, 3000)
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || error.message || 'Failed to export configurations'
    message.value = orderConfigError.value
    messageSuccess.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'application/json') {
    importFile.value = file
  } else {
    orderConfigError.value = 'Please select a valid JSON file'
    message.value = orderConfigError.value
    messageSuccess.value = false
  }
}

const handleImportConfigs = async () => {
  if (!importFile.value || !orderConfigSelectedWebsiteId.value) return
  
  importing.value = true
  importResult.value = null
  orderConfigError.value = ''
  message.value = ''
  
  try {
    const fileContent = await importFile.value.text()
    const jsonData = JSON.parse(fileContent)
    
    if (!jsonData.configurations) {
      throw new Error('Invalid file format. Missing configurations data.')
    }
    
    const res = await orderConfigsAPI.importConfigs(
      orderConfigSelectedWebsiteId.value,
      jsonData.configurations,
      importSkipExisting.value
    )
    
    importResult.value = res.data
    message.value = res.data.message
    messageSuccess.value = res.data.summary.total_errors === 0
    
    if (res.data.summary.total_errors === 0) {
      await loadOrderConfigs()
      setTimeout(() => {
        closeImportModal()
        message.value = ''
      }, 3000)
    }
  } catch (error) {
    orderConfigError.value = error.response?.data?.detail || error.message || 'Failed to import configurations'
    message.value = orderConfigError.value
    messageSuccess.value = false
  } finally {
    importing.value = false
  }
}

const closeImportModal = () => {
  showImportModal.value = false
  importFile.value = null
  importResult.value = null
  importSkipExisting.value = true
  orderConfigError.value = ''
}

// Legacy function for backward compatibility (kept but deprecated)
const populateDefaultsForWebsite = async () => {
  if (!orderConfigSelectedWebsiteId.value) {
    orderConfigError.value = 'Please select a website first'
    return
  }
  
  populatingDefaults.value = true
  orderConfigError.value = ''
  message.value = ''
  
  try {
    const res = await orderConfigsAPI.populateDefaults(orderConfigSelectedWebsiteId.value, 'general')
    const summary = res.data?.summary || {}
    const totalCreated = summary.total_created || 0
    
    if (totalCreated > 0) {
      message.value = `Successfully populated ${totalCreated} default configuration(s)`
      messageSuccess.value = true
      await loadOrderConfigs()
      setTimeout(() => { message.value = '' }, 5000)
    } else {
      message.value = 'All default configurations already exist for this website'
      messageSuccess.value = true
      setTimeout(() => { message.value = '' }, 3000)
    }
  } catch (e) {
    orderConfigError.value = e?.response?.data?.detail || 'Failed to populate defaults'
    messageSuccess.value = false
  } finally {
    populatingDefaults.value = false
  }
}

const editOrderConfig = (config) => {
  editingOrderConfig.value = config
  orderConfigFormData.value = {
    website: typeof config.website === 'object' ? config.website.id : config.website || '',
    name: config.name || '',
    is_technical: config.is_technical || false,
    code: config.code || '',
    writer_deadline_percentage: config.writer_deadline_percentage || 80
  }
  showOrderConfigModal.value = true
}

const deleteOrderConfig = async (config) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${config.name}"?`,
    'Delete Configuration',
    {
      details: 'This action cannot be undone. The configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    let apiCall
    switch (activeOrderConfigType.value) {
      case 'paper-types':
        apiCall = orderConfigsAPI.deletePaperType?.(config.id)
        break
      case 'academic-levels':
        apiCall = orderConfigsAPI.deleteAcademicLevel?.(config.id)
        break
      case 'formatting-styles':
        apiCall = orderConfigsAPI.deleteFormattingStyle?.(config.id)
        break
      case 'subjects':
        apiCall = orderConfigsAPI.deleteSubject?.(config.id)
        break
      case 'types-of-work':
        apiCall = orderConfigsAPI.deleteTypeOfWork?.(config.id)
        break
      case 'english-types':
        apiCall = orderConfigsAPI.deleteEnglishType?.(config.id)
        break
      case 'writer-deadline-configs':
        apiCall = orderConfigsAPI.deleteWriterDeadlineConfig?.(config.id)
        break
    }
    
    if (apiCall) {
      await apiCall
      message.value = `"${config.name}" deleted successfully`
      messageSuccess.value = true
      await loadOrderConfigs()
      setTimeout(() => { message.value = '' }, 3000)
    }
  } catch (e) {
    orderConfigError.value = e?.response?.data?.detail || 'Failed to delete configuration'
  }
}

const saveOrderConfig = async () => {
  savingOrderConfig.value = true
  orderConfigError.value = ''
  message.value = ''
  
  try {
    const data = {
      website: orderConfigFormData.value.website,
      name: orderConfigFormData.value.name
    }
    
    if (activeOrderConfigType.value === 'subjects') {
      data.is_technical = orderConfigFormData.value.is_technical
    }
    
    if (activeOrderConfigType.value === 'english-types') {
      data.code = orderConfigFormData.value.code
    }
    
    if (activeOrderConfigType.value === 'writer-deadline-configs') {
      data.writer_deadline_percentage = orderConfigFormData.value.writer_deadline_percentage
    }
    
    let apiCall
    if (editingOrderConfig.value) {
      // Update
      switch (activeOrderConfigType.value) {
        case 'paper-types':
          apiCall = orderConfigsAPI.updatePaperType?.(editingOrderConfig.value.id, data)
          break
        case 'academic-levels':
          apiCall = orderConfigsAPI.updateAcademicLevel?.(editingOrderConfig.value.id, data)
          break
        case 'formatting-styles':
          apiCall = orderConfigsAPI.updateFormattingStyle?.(editingOrderConfig.value.id, data)
          break
        case 'subjects':
          apiCall = orderConfigsAPI.updateSubject?.(editingOrderConfig.value.id, data)
          break
        case 'types-of-work':
          apiCall = orderConfigsAPI.updateTypeOfWork?.(editingOrderConfig.value.id, data)
          break
        case 'english-types':
          apiCall = orderConfigsAPI.updateEnglishType?.(editingOrderConfig.value.id, data)
          break
        case 'writer-deadline-configs':
          apiCall = orderConfigsAPI.updateWriterDeadlineConfig?.(editingOrderConfig.value.id, data)
          break
      }
    } else {
      // Create
      switch (activeOrderConfigType.value) {
        case 'paper-types':
          apiCall = orderConfigsAPI.createPaperType?.(data)
          break
        case 'academic-levels':
          apiCall = orderConfigsAPI.createAcademicLevel?.(data)
          break
        case 'formatting-styles':
          apiCall = orderConfigsAPI.createFormattingStyle?.(data)
          break
        case 'subjects':
          apiCall = orderConfigsAPI.createSubject?.(data)
          break
        case 'types-of-work':
          apiCall = orderConfigsAPI.createTypeOfWork?.(data)
          break
        case 'english-types':
          apiCall = orderConfigsAPI.createEnglishType?.(data)
          break
        case 'writer-deadline-configs':
          apiCall = orderConfigsAPI.createWriterDeadlineConfig?.(data)
          break
      }
    }
    
    if (apiCall) {
      await apiCall
      message.value = editingOrderConfig.value 
        ? `"${orderConfigFormData.value.name}" updated successfully`
        : `"${orderConfigFormData.value.name}" created successfully`
      messageSuccess.value = true
      closeOrderConfigModal()
      await loadOrderConfigs()
      setTimeout(() => { message.value = '' }, 3000)
    }
  } catch (e) {
    orderConfigError.value = e?.response?.data?.detail || e?.response?.data?.name?.[0] || 'Failed to save configuration'
  } finally {
    savingOrderConfig.value = false
  }
}

const closeOrderConfigModal = () => {
  showOrderConfigModal.value = false
  editingOrderConfig.value = null
  orderConfigFormData.value = {
    website: orderConfigSelectedWebsiteId.value || '',
    name: '',
    is_technical: false,
    code: '',
    writer_deadline_percentage: 80
  }
}

const loadPricingConfigs = async () => {
  pricingConfigsLoading.value = true
  try {
    const res = await adminManagementAPI.listPricingConfigs({})
    pricingConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load pricing configs:', e)
  } finally {
    pricingConfigsLoading.value = false
  }
}

const loadWriterConfigs = async () => {
  writerConfigsLoading.value = true
  try {
    const res = await adminManagementAPI.listWriterConfigs({})
    writerConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load writer configs:', e)
  } finally {
    writerConfigsLoading.value = false
  }
}

const loadNotificationConfigs = async () => {
  notificationConfigsLoading.value = true
  try {
    const res = await adminManagementAPI.listNotificationConfigs({})
    notificationConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load notification configs:', e)
  } finally {
    notificationConfigsLoading.value = false
  }
}

const loadReferralConfigs = async () => {
  referralConfigsLoading.value = true
  try {
    const res = await referralsAPI.listConfigs({})
    referralConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load referral configs:', e)
  } finally {
    referralConfigsLoading.value = false
  }
}

const loadReferralWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    referralWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const createReferralConfig = () => {
  editingReferralConfig.value = null
  referralForm.value = {
    website: '',
    first_order_bonus: 0,
    first_order_discount_type: 'fixed',
    first_order_discount_amount: 0,
    bonus_expiry_days: 30,
    max_referrals_per_month: 10,
    max_referral_bonus_per_month: 100.0,
  }
  showReferralModal.value = true
}

const editReferralConfig = (config) => {
  editingReferralConfig.value = config
  referralForm.value = {
    website: config.website || config.website?.id || '',
    first_order_bonus: parseFloat(config.first_order_bonus || 0),
    first_order_discount_type: config.first_order_discount_type || 'fixed',
    first_order_discount_amount: parseFloat(config.first_order_discount_amount || 0),
    bonus_expiry_days: config.bonus_expiry_days || 30,
    max_referrals_per_month: config.max_referrals_per_month || 10,
    max_referral_bonus_per_month: parseFloat(config.max_referral_bonus_per_month || 100),
  }
  showReferralModal.value = true
}

const saveReferralConfig = async () => {
  saving.value = true
  try {
    if (editingReferralConfig.value) {
      await referralsAPI.updateConfig(editingReferralConfig.value.id, referralForm.value)
      message.value = 'Referral configuration updated successfully'
    } else {
      await referralsAPI.createConfig(referralForm.value)
      message.value = 'Referral configuration created successfully'
    }
    messageSuccess.value = true
    closeReferralModal()
    await loadReferralConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteReferralConfig = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this referral configuration?',
    'Delete Referral Configuration',
    {
      details: 'This action cannot be undone. The referral configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await referralsAPI.deleteConfig(id)
    message.value = 'Referral configuration deleted successfully'
    messageSuccess.value = true
    await loadReferralConfigs()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeReferralModal = () => {
  showReferralModal.value = false
  editingReferralConfig.value = null
  referralForm.value = {
    website: '',
    first_order_bonus: 0,
    first_order_discount_type: 'fixed',
    first_order_discount_amount: 0,
    bonus_expiry_days: 30,
    max_referrals_per_month: 10,
    max_referral_bonus_per_month: 100.0,
  }
}

// Additional Services functions
const loadAdditionalServices = async () => {
  additionalServicesLoading.value = true
  try {
    const res = await pricingAPI.listAdditionalServices({})
    additionalServices.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load additional services:', e)
  } finally {
    additionalServicesLoading.value = false
  }
}

const loadAdditionalServicesWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    additionalServicesWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const createAdditionalService = () => {
  editingAdditionalService.value = null
  additionalServiceForm.value = {
    website: '',
    service_name: '',
    description: '',
    cost: 0,
    slug: '',
    is_active: true,
  }
  showAdditionalServiceModal.value = true
}

const editAdditionalService = (service) => {
  editingAdditionalService.value = service
  additionalServiceForm.value = {
    website: service.website || service.website?.id || '',
    service_name: service.service_name || '',
    description: service.description || '',
    cost: parseFloat(service.cost || 0),
    slug: service.slug || '',
    is_active: service.is_active !== false,
  }
  showAdditionalServiceModal.value = true
}

const saveAdditionalService = async () => {
  saving.value = true
  try {
    if (editingAdditionalService.value) {
      await pricingAPI.updateAdditionalService(editingAdditionalService.value.id, additionalServiceForm.value)
      message.value = 'Additional service updated successfully'
    } else {
      await pricingAPI.createAdditionalService(additionalServiceForm.value)
      message.value = 'Additional service created successfully'
    }
    messageSuccess.value = true
    closeAdditionalServiceModal()
    await loadAdditionalServices()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteAdditionalService = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this additional service?',
    'Delete Additional Service',
    {
      details: 'This action cannot be undone. The additional service will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await pricingAPI.deleteAdditionalService(id)
    message.value = 'Additional service deleted successfully'
    messageSuccess.value = true
    await loadAdditionalServices()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeAdditionalServiceModal = () => {
  showAdditionalServiceModal.value = false
  editingAdditionalService.value = null
  additionalServiceForm.value = {
    website: '',
    service_name: '',
    description: '',
    cost: 0,
    slug: '',
    is_active: true,
  }
}

// Preferred Writer Configs functions
const loadPreferredWriterConfigs = async () => {
  preferredWriterConfigsLoading.value = true
  try {
    const res = await pricingAPI.listPreferredWriterConfigs({})
    preferredWriterConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load preferred writer configs:', e)
  } finally {
    preferredWriterConfigsLoading.value = false
  }
}

const loadPreferredWriterConfigsWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    preferredWriterConfigsWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}


const createPreferredWriterConfig = () => {
  editingPreferredWriterConfig.value = null
  preferredWriterForm.value = {
    website: '',
    preferred_writer_cost: 0,
    is_active: true,
  }
  showPreferredWriterModal.value = true
}

const editPreferredWriterConfig = (config) => {
  editingPreferredWriterConfig.value = config
  preferredWriterForm.value = {
    website: config.website || config.website?.id || '',
    preferred_writer_cost: parseFloat(config.preferred_writer_cost || 0),
    is_active: config.is_active !== false,
  }
  showPreferredWriterModal.value = true
}

const savePreferredWriterConfig = async () => {
  saving.value = true
  try {
    if (editingPreferredWriterConfig.value) {
      await pricingAPI.updatePreferredWriterConfig(editingPreferredWriterConfig.value.id, preferredWriterForm.value)
      message.value = 'Preferred writer config updated successfully'
    } else {
      await pricingAPI.createPreferredWriterConfig(preferredWriterForm.value)
      message.value = 'Preferred writer config created successfully'
    }
    messageSuccess.value = true
    closePreferredWriterModal()
    await loadPreferredWriterConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deletePreferredWriterConfig = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this preferred writer config?',
    'Delete Preferred Writer Config',
    {
      details: 'This action cannot be undone. The preferred writer configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await pricingAPI.deletePreferredWriterConfig(id)
    message.value = 'Preferred writer config deleted successfully'
    messageSuccess.value = true
    await loadPreferredWriterConfigs()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closePreferredWriterModal = () => {
  showPreferredWriterModal.value = false
  editingPreferredWriterConfig.value = null
  preferredWriterForm.value = {
    website: '',
    writer: '',
    preferred_writer_cost: 0,
    is_active: true,
  }
}

// Writer Level Options functions
const loadWriterLevelOptions = async () => {
  writerLevelOptionsLoading.value = true
  try {
    const res = await pricingAPI.listWriterLevelOptions({})
    writerLevelOptions.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load writer level options:', e)
  } finally {
    writerLevelOptionsLoading.value = false
  }
}

const loadWriterLevelOptionsWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    writerLevelOptionsWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const createWriterLevelOption = () => {
  editingWriterLevelOption.value = null
  writerLevelOptionForm.value = {
    website: '',
    name: '',
    value: 0,
    description: '',
    active: true,
    sort_order: 0,
  }
  showWriterLevelOptionModal.value = true
}

const editWriterLevelOption = (option) => {
  editingWriterLevelOption.value = option
  writerLevelOptionForm.value = {
    website: option.website || option.website?.id || '',
    name: option.name || '',
    value: parseFloat(option.value || 0),
    description: option.description || '',
    active: option.active !== false,
    sort_order: option.sort_order || 0,
  }
  showWriterLevelOptionModal.value = true
}

const saveWriterLevelOption = async () => {
  saving.value = true
  try {
    if (editingWriterLevelOption.value) {
      await pricingAPI.updateWriterLevelOption(editingWriterLevelOption.value.id, writerLevelOptionForm.value)
      message.value = 'Writer level option updated successfully'
    } else {
      await pricingAPI.createWriterLevelOption(writerLevelOptionForm.value)
      message.value = 'Writer level option created successfully'
    }
    messageSuccess.value = true
    closeWriterLevelOptionModal()
    await loadWriterLevelOptions()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteWriterLevelOption = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this writer level option?',
    'Delete Writer Level Option',
    {
      details: 'This action cannot be undone. The writer level option will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await pricingAPI.deleteWriterLevelOption(id)
    message.value = 'Writer level option deleted successfully'
    messageSuccess.value = true
    await loadWriterLevelOptions()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeWriterLevelOptionModal = () => {
  showWriterLevelOptionModal.value = false
  editingWriterLevelOption.value = null
  writerLevelOptionForm.value = {
    website: '',
    name: '',
    value: 0,
    description: '',
    active: true,
    sort_order: 0,
  }
}

// Deadline Multipliers functions
const loadDeadlineMultipliers = async () => {
  deadlineMultipliersLoading.value = true
  try {
    const res = await pricingAPI.listDeadlineMultipliers({})
    deadlineMultipliers.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load deadline multipliers:', e)
  } finally {
    deadlineMultipliersLoading.value = false
  }
}

const loadDeadlineMultipliersWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    deadlineMultipliersWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const createDeadlineMultiplier = () => {
  editingDeadlineMultiplier.value = null
  deadlineMultiplierForm.value = {
    website: '',
    label: '',
    hours: 24,
    multiplier: 1.0,
  }
  // Ensure websites are loaded
  if (!deadlineMultipliersWebsites.value.length) {
    loadDeadlineMultipliersWebsites()
  }
  showDeadlineMultiplierModal.value = true
}

const editDeadlineMultiplier = (multiplier) => {
  editingDeadlineMultiplier.value = multiplier
  deadlineMultiplierForm.value = {
    website: multiplier.website || multiplier.website?.id || '',
    label: multiplier.label || '',
    hours: multiplier.hours || 24,
    multiplier: parseFloat(multiplier.multiplier || 1.0),
  }
  showDeadlineMultiplierModal.value = true
}

const saveDeadlineMultiplier = async () => {
  saving.value = true
  try {
    if (editingDeadlineMultiplier.value) {
      await pricingAPI.updateDeadlineMultiplier(editingDeadlineMultiplier.value.id, deadlineMultiplierForm.value)
      message.value = 'Deadline multiplier updated successfully'
    } else {
      await pricingAPI.createDeadlineMultiplier(deadlineMultiplierForm.value)
      message.value = 'Deadline multiplier created successfully'
    }
    messageSuccess.value = true
    closeDeadlineMultiplierModal()
    await loadDeadlineMultipliers()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteDeadlineMultiplier = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this deadline multiplier?',
    'Delete Deadline Multiplier',
    {
      details: 'This action cannot be undone. The deadline multiplier will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await pricingAPI.deleteDeadlineMultiplier(id)
    message.value = 'Deadline multiplier deleted successfully'
    messageSuccess.value = true
    await loadDeadlineMultipliers()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeDeadlineMultiplierModal = () => {
  showDeadlineMultiplierModal.value = false
  editingDeadlineMultiplier.value = null
  deadlineMultiplierForm.value = {
    website: '',
    label: '',
    hours: 24,
    multiplier: 1.0,
  }
}

const editPricingConfig = (config) => {
  editingPricingConfig.value = config
  pricingForm.value = {
    base_price_per_page: parseFloat(config.base_price_per_page || 0),
    base_price_per_slide: parseFloat(config.base_price_per_slide || 0),
    technical_multiplier: parseFloat(config.technical_multiplier || 1.0),
    non_technical_order_multiplier: parseFloat(config.non_technical_order_multiplier || 1.0),
  }
  showPricingModal.value = true
}

const savePricingConfig = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingPricingConfig.value) {
      await adminManagementAPI.updatePricingConfig(editingPricingConfig.value.id, pricingForm.value)
      message.value = 'Pricing configuration updated successfully'
    } else {
      await adminManagementAPI.createPricingConfig(pricingForm.value)
      message.value = 'Pricing configuration created successfully'
    }
    messageSuccess.value = true
    closePricingModal()
    await loadPricingConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closePricingModal = () => {
  showPricingModal.value = false
  editingPricingConfig.value = null
  pricingForm.value = {
    base_price_per_page: 0,
    base_price_per_slide: 0,
    technical_multiplier: 1.0,
    non_technical_order_multiplier: 1.0,
  }
}

const deletePricingConfig = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Delete this pricing configuration?',
    'Delete Pricing Configuration',
    {
      details: 'This action cannot be undone. The pricing configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await adminManagementAPI.deletePricingConfig(id)
    message.value = 'Pricing configuration deleted'
    messageSuccess.value = true
    await loadPricingConfigs()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const editWriterConfig = (config) => {
  editingWriterConfig.value = config
  writerForm.value = {
    takes_enabled: config.takes_enabled || false,
  }
  showWriterModal.value = true
}

const saveWriterConfig = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingWriterConfig.value) {
      await adminManagementAPI.updateWriterConfig(editingWriterConfig.value.id, writerForm.value)
      message.value = 'Writer configuration updated successfully'
    } else {
      await adminManagementAPI.createWriterConfig(writerForm.value)
      message.value = 'Writer configuration created successfully'
    }
    messageSuccess.value = true
    closeWriterModal()
    await loadWriterConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeWriterModal = () => {
  showWriterModal.value = false
  editingWriterConfig.value = null
  writerForm.value = {
    takes_enabled: true,
  }
}

const createNotificationConfig = () => {
  editingNotificationConfig.value = null
  notificationForm.value = {
    website: '',
    name: '',
    description: '',
    default_email: true,
    default_sms: false,
    default_push: false,
    default_in_app: true,
    email_enabled: true,
    sms_enabled: false,
    push_enabled: false,
    in_app_enabled: true,
    dnd_enabled: false,
    dnd_start_hour: 22,
    dnd_end_hour: 6,
    is_default: false,
  }
  showNotificationModal.value = true
}

const editNotificationConfig = (config) => {
  editingNotificationConfig.value = config
  notificationForm.value = {
    website: config.website_id || config.website || '',
    name: config.name || '',
    description: config.description || '',
    default_email: config.default_email !== false,
    default_sms: config.default_sms === true,
    default_push: config.default_push === true,
    default_in_app: config.default_in_app !== false,
    email_enabled: config.email_enabled !== false,
    sms_enabled: config.sms_enabled === true,
    push_enabled: config.push_enabled === true,
    in_app_enabled: config.in_app_enabled !== false,
    dnd_enabled: config.dnd_enabled === true,
    dnd_start_hour: config.dnd_start_hour || 22,
    dnd_end_hour: config.dnd_end_hour || 6,
    is_default: config.is_default === true,
  }
  showNotificationModal.value = true
}

const saveNotificationConfig = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingNotificationConfig.value) {
      await adminManagementAPI.updateNotificationConfig(
        editingNotificationConfig.value.id,
        notificationForm.value
      )
      message.value = 'Notification profile updated successfully'
    } else {
      await adminManagementAPI.createNotificationConfig(notificationForm.value)
      message.value = 'Notification profile created successfully'
    }
    messageSuccess.value = true
    closeNotificationModal()
    await loadNotificationConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeNotificationModal = () => {
  showNotificationModal.value = false
  editingNotificationConfig.value = null
  notificationForm.value = {
    website: '',
    name: '',
    description: '',
    default_email: true,
    default_sms: false,
    default_push: false,
    default_in_app: true,
    email_enabled: true,
    sms_enabled: false,
    push_enabled: false,
    in_app_enabled: true,
    dnd_enabled: false,
    dnd_start_hour: 22,
    dnd_end_hour: 6,
    is_default: false,
  }
}

const loadNotificationWebsites = async () => {
  try {
    const res = await websitesAPI.list()
    notificationWebsites.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Discount functions
const loadDiscounts = async () => {
  discountsLoading.value = true
  try {
    const params = {
      page: discountFilters.value.page,
      page_size: discountFilters.value.page_size,
    }
    if (discountFilters.value.search) params.search = discountFilters.value.search
    if (discountFilters.value.website_id) params.website = discountFilters.value.website_id
    if (discountFilters.value.is_active) params.is_active = discountFilters.value.is_active === 'true'
    if (discountFilters.value.discount_type) params.discount_type = discountFilters.value.discount_type

    const res = await discountsAPI.list(params)
    discounts.value = res.data.results || res.data || []
    discountPagination.value = {
      count: res.data.count || discounts.value.length,
      next: res.data.next,
      previous: res.data.previous,
    }
  } catch (e) {
    console.error('Failed to load discounts:', e)
  } finally {
    discountsLoading.value = false
  }
}

const loadDiscountCampaigns = async () => {
  try {
    const res = await discountsAPI.listCampaigns()
    discountCampaigns.value = res.data.results || res.data || []
  } catch (e) {
    console.error('Failed to load campaigns:', e)
  }
}

const loadDiscountStats = async () => {
  try {
    const res = await discountsAPI.getAnalytics('stats')
    discountStats.value = res.data || {}
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const loadDiscountWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    discountWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const formattedDiscounts = computed(() => {
  return discounts.value.map(d => ({
    ...d,
    value: d.discount_type === 'percent' ? `${d.value}%` : `$${parseFloat(d.value).toFixed(2)}`,
    max_uses: d.max_uses || 'Unlimited',
    start_date: formatDate(d.start_date),
    end_date: d.end_date ? formatDate(d.end_date) : 'No expiry',
    is_active: d.is_active ? 'Active' : 'Inactive',
    website_name: d.website_name || 'N/A',
  }))
})

const createDiscount = () => {
  editingDiscount.value = null
  discountForm.value = {
    website: '',
    code: '',
    description: '',
    discount_type: 'percent',
    value: '',
    start_date: new Date().toISOString().slice(0, 16),
    end_date: '',
    max_uses: '',
    per_user_usage_limit: '',
    min_order_value: '',
    max_discount_value: '',
    is_active: true,
    is_general: true,
    stackable: false,
    applies_to_first_order_only: false,
  }
  showDiscountModal.value = true
}

const editDiscount = (discount) => {
  editingDiscount.value = discount
  const rawDiscount = discounts.value.find(d => d.id === discount.id) || discount
  discountForm.value = {
    website: rawDiscount.website,
    code: rawDiscount.code,
    description: rawDiscount.description || '',
    discount_type: rawDiscount.discount_type,
    value: parseFloat(rawDiscount.value) || '',
    start_date: rawDiscount.start_date ? new Date(rawDiscount.start_date).toISOString().slice(0, 16) : '',
    end_date: rawDiscount.end_date ? new Date(rawDiscount.end_date).toISOString().slice(0, 16) : '',
    max_uses: rawDiscount.max_uses || '',
    per_user_usage_limit: rawDiscount.per_user_usage_limit || '',
    min_order_value: rawDiscount.min_order_value ? parseFloat(rawDiscount.min_order_value) : '',
    max_discount_value: rawDiscount.max_discount_value ? parseFloat(rawDiscount.max_discount_value) : '',
    is_active: rawDiscount.is_active,
    is_general: rawDiscount.is_general,
    stackable: rawDiscount.stackable,
    applies_to_first_order_only: rawDiscount.applies_to_first_order_only,
  }
  showDiscountModal.value = true
}

const saveDiscount = async () => {
  discountSaving.value = true
  try {
    const data = { ...discountForm.value }
    if (!data.max_uses) data.max_uses = null
    if (!data.per_user_usage_limit) data.per_user_usage_limit = null
    if (!data.min_order_value) data.min_order_value = null
    if (!data.max_discount_value) data.max_discount_value = null
    if (!data.end_date) data.end_date = null

    if (editingDiscount.value) {
      await discountsAPI.update(editingDiscount.value.id, data)
    } else {
      await discountsAPI.create(data)
    }
    showDiscountModal.value = false
    editingDiscount.value = null
    await loadDiscounts()
    await loadDiscountStats()
  } catch (e) {
    console.error('Failed to save discount:', e)
    alert('Failed to save discount: ' + (e.response?.data?.detail || e.message))
  } finally {
    discountSaving.value = false
  }
}

const toggleDiscountActive = async (discount) => {
  try {
    await discountsAPI.toggleActive(discount.id)
    await loadDiscounts()
    await loadDiscountStats()
  } catch (e) {
    console.error('Failed to toggle discount:', e)
    alert('Failed to toggle discount: ' + (e.response?.data?.detail || e.message))
  }
}

const deleteDiscount = async (discount) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete discount "${discount.code}"?`,
    'Delete Discount',
    {
      details: 'This action cannot be undone. The discount will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await discountsAPI.delete(discount.id)
    await loadDiscounts()
    await loadDiscountStats()
  } catch (e) {
    console.error('Failed to delete discount:', e)
    alert('Failed to delete discount: ' + (e.response?.data?.detail || e.message))
  }
}

const updateDiscountFilter = (key, value) => {
  discountFilters.value[key] = value
  discountFilters.value.page = 1
  loadDiscounts()
}

const clearDiscountFilters = () => {
  discountFilters.value = {
    search: '',
    website_id: '',
    is_active: '',
    discount_type: '',
    page: 1,
    page_size: 50,
  }
  loadDiscounts()
}

const handleDiscountPageChange = (url) => {
  if (!url) return
  const urlObj = new URL(url)
  discountFilters.value.page = parseInt(urlObj.searchParams.get('page')) || 1
  loadDiscounts()
}

const handleDiscountPageSizeChange = () => {
  discountFilters.value.page = 1
  loadDiscounts()
}

const exportDiscountsToCSV = () => {
  exportToCSV(formattedDiscounts.value, 'discounts.csv')
}

// Payment Reminder Functions
const loadPaymentReminderConfigs = async () => {
  paymentReminderConfigsLoading.value = true
  try {
    const res = await paymentRemindersAPI.getReminderConfigs({})
    paymentReminderConfigs.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load payment reminder configs:', e)
  } finally {
    paymentReminderConfigsLoading.value = false
  }
}

const loadPaymentReminderConfigsWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    paymentReminderConfigsWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadPaymentDeletionMessages = async () => {
  paymentDeletionMessagesLoading.value = true
  try {
    const res = await paymentRemindersAPI.getDeletionMessages({})
    paymentDeletionMessages.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load deletion messages:', e)
  } finally {
    paymentDeletionMessagesLoading.value = false
  }
}

const loadPaymentDeletionMessagesWebsites = async () => {
  try {
    const res = await apiClient.get('/websites/websites/')
    paymentDeletionMessagesWebsites.value = res.data.results || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const createReminderConfig = () => {
  editingReminderConfig.value = null
  reminderConfigForm.value = {
    website: '',
    name: '',
    deadline_percentage: '',
    message: '',
    send_as_notification: true,
    send_as_email: true,
    email_subject: '',
    is_active: true,
    display_order: 0,
  }
  showReminderConfigModal.value = true
}

const editReminderConfig = (config) => {
  editingReminderConfig.value = config
  reminderConfigForm.value = {
    website: config.website || config.website?.id || '',
    name: config.name || '',
    deadline_percentage: config.deadline_percentage || '',
    message: config.message || '',
    send_as_notification: config.send_as_notification !== false,
    send_as_email: config.send_as_email !== false,
    email_subject: config.email_subject || '',
    is_active: config.is_active !== false,
    display_order: config.display_order || 0,
  }
  showReminderConfigModal.value = true
}

const saveReminderConfig = async () => {
  saving.value = true
  try {
    if (editingReminderConfig.value) {
      await paymentRemindersAPI.updateReminderConfig(editingReminderConfig.value.id, reminderConfigForm.value)
      message.value = 'Reminder config updated successfully'
    } else {
      await paymentRemindersAPI.createReminderConfig(reminderConfigForm.value)
      message.value = 'Reminder config created successfully'
    }
    messageSuccess.value = true
    closeReminderConfigModal()
    await loadPaymentReminderConfigs()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteReminderConfig = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this reminder config?',
    'Delete Reminder Config',
    {
      details: 'This action cannot be undone. The reminder configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await paymentRemindersAPI.deleteReminderConfig(id)
    message.value = 'Reminder config deleted successfully'
    messageSuccess.value = true
    await loadPaymentReminderConfigs()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeReminderConfigModal = () => {
  showReminderConfigModal.value = false
  editingReminderConfig.value = null
  reminderConfigForm.value = {
    website: '',
    name: '',
    deadline_percentage: '',
    message: '',
    send_as_notification: true,
    send_as_email: true,
    email_subject: '',
    is_active: true,
    display_order: 0,
  }
}

const createDeletionMessage = () => {
  editingDeletionMessage.value = null
  deletionMessageForm.value = {
    website: '',
    message: '',
    send_as_notification: true,
    send_as_email: true,
    email_subject: '',
    is_active: true,
  }
  showDeletionMessageModal.value = true
}

const editDeletionMessage = (message) => {
  editingDeletionMessage.value = message
  deletionMessageForm.value = {
    website: message.website || message.website?.id || '',
    message: message.message || '',
    send_as_notification: message.send_as_notification !== false,
    send_as_email: message.send_as_email !== false,
    email_subject: message.email_subject || '',
    is_active: message.is_active !== false,
  }
  showDeletionMessageModal.value = true
}

const saveDeletionMessage = async () => {
  saving.value = true
  try {
    if (editingDeletionMessage.value) {
      await paymentRemindersAPI.updateDeletionMessage(editingDeletionMessage.value.id, deletionMessageForm.value)
      message.value = 'Deletion message updated successfully'
    } else {
      await paymentRemindersAPI.createDeletionMessage(deletionMessageForm.value)
      message.value = 'Deletion message created successfully'
    }
    messageSuccess.value = true
    closeDeletionMessageModal()
    await loadPaymentDeletionMessages()
  } catch (e) {
    message.value = 'Failed to save: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const deleteDeletionMessage = async (id) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this deletion message?',
    'Delete Deletion Message',
    {
      details: 'This action cannot be undone. The deletion message will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await paymentRemindersAPI.deleteDeletionMessage(id)
    message.value = 'Deletion message deleted successfully'
    messageSuccess.value = true
    await loadPaymentDeletionMessages()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeDeletionMessageModal = () => {
  showDeletionMessageModal.value = false
  editingDeletionMessage.value = null
  deletionMessageForm.value = {
    website: '',
    message: '',
    send_as_notification: true,
    send_as_email: true,
    email_subject: '',
    is_active: true,
  }
}

watch([activeTab, activePricingSubTab], async () => {
  if (activeTab.value === 'pricing') {
    // Load data based on active pricing sub-tab
    if (activePricingSubTab.value === 'base-pricing') {
      if (!pricingConfigs.value.length) {
    loadPricingConfigs()
      }
    } else if (activePricingSubTab.value === 'additional-services') {
      if (!additionalServicesWebsites.value.length) {
        loadAdditionalServicesWebsites()
      }
      loadAdditionalServices()
    } else if (activePricingSubTab.value === 'preferred-writers') {
      if (!preferredWriterConfigsWebsites.value.length) {
        loadPreferredWriterConfigsWebsites()
      }
      loadPreferredWriterConfigs()
    } else if (activePricingSubTab.value === 'writer-levels') {
      if (!writerLevelOptionsWebsites.value.length) {
        loadWriterLevelOptionsWebsites()
      }
      loadWriterLevelOptions()
    } else if (activePricingSubTab.value === 'deadline-multipliers') {
      if (!deadlineMultipliersWebsites.value.length) {
        loadDeadlineMultipliersWebsites()
      }
      loadDeadlineMultipliers()
    }
  } else if (activeTab.value === 'writer' && !writerConfigs.value.length) {
    loadWriterConfigs()
  } else if (activeTab.value === 'order-configs') {
    if (!orderConfigWebsites.value.length) {
      loadOrderConfigWebsites()
    }
    loadOrderConfigs()
  } else if (activeTab.value === 'notifications') {
    if (!notificationConfigs.value.length) {
      loadNotificationConfigs()
    }
    if (!notificationWebsites.value.length) {
      loadNotificationWebsites()
    }
  } else if (activeTab.value === 'referrals') {
    if (!referralWebsites.value.length) {
      loadReferralWebsites()
    }
    loadReferralConfigs()
  } else if (activeTab.value === 'payment-reminders') {
    try {
      if (!paymentReminderConfigsWebsites.value.length) {
        await loadPaymentReminderConfigsWebsites()
      }
      if (!paymentDeletionMessagesWebsites.value.length) {
        await loadPaymentDeletionMessagesWebsites()
      }
      await loadPaymentReminderConfigs()
      await loadPaymentDeletionMessages()
    } catch (error) {
      console.error('Error loading payment reminders:', error)
    }
  }
}, { immediate: false })

watch(activeOrderConfigType, () => {
  if (activeTab.value === 'order-configs') {
    loadOrderConfigs()
  }
})

// Expand all websites by default when configs are loaded
watch([orderConfigs, activeOrderConfigType], () => {
  if (orderConfigs.value.length > 0 && activeTab.value === 'order-configs') {
    // Expand all websites by default
    Object.keys(groupedConfigsByWebsite.value).forEach(websiteId => {
      expandedWebsites.value.add(websiteId)
    })
  }
}, { immediate: true })

// Handle query parameters for direct navigation
const route = useRoute()

// Watch for route query changes to set active tabs
watch(() => route.query, (query) => {
  if (query.tab) {
    if (activeTab.value !== query.tab) {
      activeTab.value = query.tab
    }
  }
  if (query.subtab && activeTab.value === 'pricing') {
    activePricingSubTab.value = query.subtab
  }
}, { immediate: true, deep: true })

onMounted(async () => {
  // Check for query parameters first
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  if (route.query.subtab && activeTab.value === 'pricing') {
    activePricingSubTab.value = route.query.subtab
  }
  
  // Load initial data based on active tab
  if (activeTab.value === 'pricing') {
    if (activePricingSubTab.value === 'base-pricing') {
  await loadPricingConfigs()
    } else if (activePricingSubTab.value === 'deadline-multipliers') {
      if (!deadlineMultipliersWebsites.value.length) {
        await loadDeadlineMultipliersWebsites()
      }
      await loadDeadlineMultipliers()
    }
  } else if (activeTab.value === 'payment-reminders') {
    try {
      if (!paymentReminderConfigsWebsites.value.length) {
        await loadPaymentReminderConfigsWebsites()
      }
      if (!paymentDeletionMessagesWebsites.value.length) {
        await loadPaymentDeletionMessagesWebsites()
      }
      await loadPaymentReminderConfigs()
      await loadPaymentDeletionMessages()
    } catch (error) {
      console.error('Error loading payment reminders:', error)
    }
  }
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

