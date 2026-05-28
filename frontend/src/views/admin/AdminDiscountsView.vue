<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900">Discounts</h1>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 border-b border-gray-200">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-md transition-colors',
          activeTab === tab.key
            ? 'bg-white border border-b-white border-gray-200 text-blue-600 -mb-px'
            : 'text-gray-500 hover:text-gray-700',
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Dashboard -->
    <div v-if="activeTab === 'dashboard'" class="space-y-6">
      <div v-if="summary" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Total Discounts</p>
          <p class="text-2xl font-bold text-gray-900">{{ summary.total_discounts }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Working</p>
          <p class="text-2xl font-bold text-green-600">{{ summary.working_discounts }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Scheduled</p>
          <p class="text-2xl font-bold text-blue-600">{{ summary.scheduled_discounts }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Expired</p>
          <p class="text-2xl font-bold text-gray-500">{{ summary.expired_discounts }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Total Redemptions</p>
          <p class="text-2xl font-bold text-gray-900">{{ summary.total_redemptions }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Total Discount Given</p>
          <p class="text-2xl font-bold text-red-600">${{ summary.total_discount_given }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Distinct Clients</p>
          <p class="text-2xl font-bold text-purple-600">{{ summary.distinct_clients }}</p>
        </div>
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <p class="text-xs text-gray-500">Archived</p>
          <p class="text-2xl font-bold text-gray-400">{{ summary.archived_discounts }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- By origin -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">By Origin</h3>
          <div v-if="originGroups.length" class="space-y-2">
            <div v-for="g in originGroups" :key="g.origin" class="flex items-center gap-2">
              <span class="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded capitalize">{{ g.origin }}</span>
              <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-blue-500 rounded-full"
                  :style="{ width: originMax ? `${(g.total / originMax) * 100}%` : '0%' }"
                />
              </div>
              <span class="text-xs text-gray-600 w-8 text-right">{{ g.total }}</span>
            </div>
          </div>
          <p v-else class="text-xs text-gray-400">No data.</p>
        </div>

        <!-- Expiring soon -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-gray-700">Expiring Soon</h3>
            <select v-model="expireDays" @change="loadExpiring" class="text-xs border border-gray-200 rounded px-2 py-1">
              <option :value="3">3 days</option>
              <option :value="7">7 days</option>
              <option :value="14">14 days</option>
              <option :value="30">30 days</option>
            </select>
          </div>
          <div v-if="expiringDiscounts.length" class="space-y-2">
            <div v-for="d in expiringDiscounts" :key="d.id" class="flex items-center justify-between text-sm">
              <span class="font-mono text-xs">{{ d.discount_code }}</span>
              <span class="text-gray-500 text-xs">{{ d.ends_at ? new Date(d.ends_at).toLocaleDateString() : '—' }}</span>
            </div>
          </div>
          <p v-else class="text-xs text-gray-400">None expiring in {{ expireDays }} days.</p>
        </div>

        <!-- Top performing -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Top Performing</h3>
          <table class="w-full text-xs">
            <thead>
              <tr class="text-gray-500 border-b border-gray-100">
                <th class="pb-1 text-left">Code</th>
                <th class="pb-1 text-right">Uses</th>
                <th class="pb-1 text-right">Given</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in topDiscounts" :key="d.id" class="border-b border-gray-50">
                <td class="py-1 font-mono">{{ d.discount_code }}</td>
                <td class="py-1 text-right">{{ d.usage_count }}</td>
                <td class="py-1 text-right">${{ d.total_discount_given }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!topDiscounts.length" class="text-xs text-gray-400">No data.</p>
        </div>

        <!-- Unused -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Unused Working Discounts</h3>
          <div v-if="unusedDiscounts.length" class="space-y-2">
            <div v-for="d in unusedDiscounts" :key="d.id" class="flex items-center justify-between text-xs">
              <span class="font-mono">{{ d.discount_code }}</span>
              <span class="text-gray-500">{{ d.name }}</span>
            </div>
          </div>
          <p v-else class="text-xs text-gray-400">All working discounts have been used.</p>
        </div>
      </div>
    </div>

    <!-- Discounts list -->
    <div v-if="activeTab === 'discounts'" class="space-y-4">
      <div class="flex flex-wrap items-center gap-2">
        <div class="flex gap-1">
          <button
            v-for="s in discountStatuses"
            :key="s.value"
            @click="discountStatus = s.value; loadDiscounts()"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium',
              discountStatus === s.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
            ]"
          >{{ s.label }}</button>
        </div>
        <button
          @click="openCreateDiscount"
          class="ml-auto px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >+ New Discount</button>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Code</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Name</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Type</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Value</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Uses</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Given</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Expires</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="d in discounts" :key="d.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-mono text-xs font-semibold">{{ d.discount_code }}</td>
              <td class="px-4 py-3 text-gray-700">{{ d.name }}</td>
              <td class="px-4 py-3 text-gray-500 capitalize">{{ d.discount_type }}</td>
              <td class="px-4 py-3 text-right">
                {{ d.discount_type === 'percentage' ? `${d.discount_value}%` : `$${d.discount_value}` }}
              </td>
              <td class="px-4 py-3 text-right">{{ d.usage_count }}</td>
              <td class="px-4 py-3 text-right">${{ d.total_discount_given }}</td>
              <td class="px-4 py-3">
                <span :class="discountStatusClass(d)">
                  {{ discountStatusLabel(d) }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">
                {{ d.ends_at ? new Date(d.ends_at).toLocaleDateString() : '—' }}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openEditDiscount(d)" class="text-xs text-blue-600 hover:underline">Edit</button>
                  <button v-if="!d.is_archived" @click="archiveDiscount(d)" class="text-xs text-orange-500 hover:underline">Archive</button>
                  <button v-else @click="restoreDiscount(d)" class="text-xs text-green-600 hover:underline">Restore</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!discounts.length" class="text-center text-sm text-gray-400 py-8">No discounts found.</p>
      </div>
    </div>

    <!-- Campaigns -->
    <div v-if="activeTab === 'campaigns'" class="space-y-4">
      <div class="flex justify-end">
        <button
          @click="openCreateCampaign"
          class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >+ New Campaign</button>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Name</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Discounts</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Uses</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Given</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Dates</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="c in campaigns" :key="c.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ c.name }}</td>
              <td class="px-4 py-3 text-right">{{ c.discount_count }}</td>
              <td class="px-4 py-3 text-right">{{ c.usage_count }}</td>
              <td class="px-4 py-3 text-right">${{ c.total_discount_given }}</td>
              <td class="px-4 py-3 text-xs text-gray-500">
                {{ c.starts_at ? new Date(c.starts_at).toLocaleDateString() : '—' }}
                –
                {{ c.ends_at ? new Date(c.ends_at).toLocaleDateString() : '∞' }}
              </td>
              <td class="px-4 py-3">
                <span :class="campaignStatusClass(c)">{{ campaignStatusLabel(c) }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1 flex-wrap">
                  <button @click="openEditCampaign(c)" class="text-xs text-blue-600 hover:underline">Edit</button>
                  <template v-if="!c.is_archived">
                    <button v-if="!c.is_active" @click="activateCampaign(c)" class="text-xs text-green-600 hover:underline">Activate</button>
                    <button v-else @click="deactivateCampaign(c)" class="text-xs text-orange-500 hover:underline">Deactivate</button>
                    <button @click="archiveCampaign(c)" class="text-xs text-red-500 hover:underline">Archive</button>
                  </template>
                  <button v-else @click="restoreCampaign(c)" class="text-xs text-green-600 hover:underline">Restore</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!campaigns.length" class="text-center text-sm text-gray-400 py-8">No campaigns found.</p>
      </div>
    </div>

    <!-- Spend Tiers -->
    <div v-if="activeTab === 'spend-tiers'" class="space-y-4">
      <div class="flex justify-end">
        <button
          @click="openCreateTier"
          class="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
        >+ New Tier</button>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Tier Name</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500">Min. Lifetime Spend</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Discount Code</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Discount</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500">Active</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="t in spendTiers" :key="t.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-900">{{ t.name }}</td>
              <td class="px-4 py-3 text-right font-semibold">${{ t.minimum_lifetime_spend }}</td>
              <td class="px-4 py-3 font-mono text-xs">{{ t.discount.discount_code }}</td>
              <td class="px-4 py-3 text-gray-600">
                {{ t.discount.discount_type === 'percentage' ? `${t.discount.discount_value}%` : `$${t.discount.discount_value}` }}
                off
              </td>
              <td class="px-4 py-3">
                <span :class="t.is_active ? 'text-green-600' : 'text-gray-400'">{{ t.is_active ? 'Yes' : 'No' }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button @click="openEditTier(t)" class="text-xs text-blue-600 hover:underline">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!spendTiers.length" class="text-center text-sm text-gray-400 py-8">No spend tiers configured.</p>
      </div>
    </div>

    <!-- Settings -->
    <div v-if="activeTab === 'settings'" class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Discount Settings -->
        <div class="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h3 class="text-sm font-semibold text-gray-800">Discount Settings</h3>
          <template v-if="settings">
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.allow_manual_codes" class="rounded" />
              Allow manual codes
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.auto_apply_first_order_discount" class="rounded" />
              Auto-apply first order discount
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.allow_code_to_replace_first_order" class="rounded" />
              Allow manual code to replace first-order discount
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.auto_apply_best_discount" class="rounded" />
              Auto-apply best discount
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.allow_discounts_on_orders" class="rounded" />
              Allow discounts on orders
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.allow_discounts_on_special_orders" class="rounded" />
              Allow discounts on special orders
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.allow_discounts_on_class_bundles" class="rounded" />
              Allow discounts on class bundles
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.require_admin_approval_for_campaigns" class="rounded" />
              Require admin approval for campaigns
            </label>
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="settings.notify_admins_on_large_discount" class="rounded" />
              Notify admins on large discounts
            </label>
            <div class="flex items-center gap-3 text-sm">
              <label class="whitespace-nowrap">Large discount threshold ($)</label>
              <input
                type="number"
                v-model="settings.large_discount_threshold"
                class="flex-1 border border-gray-200 rounded px-2 py-1 text-sm"
              />
            </div>
            <button
              @click="saveSettings"
              class="w-full py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
            >Save Discount Settings</button>
          </template>
        </div>

        <!-- First Order Config -->
        <div class="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h3 class="text-sm font-semibold text-gray-800">First Order Discount</h3>
          <template v-if="firstOrderConfig">
            <label class="flex items-center gap-3 text-sm">
              <input type="checkbox" v-model="firstOrderConfig.is_enabled" class="rounded" />
              Enabled
            </label>
            <div class="text-sm space-y-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Discount Type</label>
                <select v-model="firstOrderConfig.discount_type" class="w-full border border-gray-200 rounded px-2 py-1 text-sm">
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Discount Value</label>
                <input type="number" v-model="firstOrderConfig.discount_value" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Max Discount Amount</label>
                <input type="number" v-model="firstOrderConfig.max_discount_amount" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Min Payable Amount</label>
                <input type="number" v-model="firstOrderConfig.min_payable_amount" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
              </div>
              <label class="flex items-center gap-3 text-sm">
                <input type="checkbox" v-model="firstOrderConfig.applies_to_orders" class="rounded" />
                Applies to orders
              </label>
              <label class="flex items-center gap-3 text-sm">
                <input type="checkbox" v-model="firstOrderConfig.applies_to_special_orders" class="rounded" />
                Applies to special orders
              </label>
              <label class="flex items-center gap-3 text-sm">
                <input type="checkbox" v-model="firstOrderConfig.applies_to_class_bundles" class="rounded" />
                Applies to class bundles
              </label>
            </div>
            <button
              @click="saveFirstOrderConfig"
              class="w-full py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
            >Save First Order Config</button>
          </template>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast"
      :class="[
        'fixed bottom-4 right-4 px-4 py-2 rounded-lg text-sm text-white shadow-lg transition-all',
        toast.type === 'error' ? 'bg-red-600' : 'bg-green-600',
      ]"
    >{{ toast.message }}</div>

    <!-- Discount Create/Edit Modal -->
    <div v-if="showDiscountModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6 space-y-4">
        <h2 class="text-lg font-semibold">{{ editingDiscount ? 'Edit Discount' : 'New Discount' }}</h2>

        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2">
            <label class="block text-xs text-gray-500 mb-1">Name *</label>
            <input v-model="discountForm.name" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div v-if="!editingDiscount" class="col-span-2 space-y-2">
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="discountForm.generate_code" class="rounded" />
              Auto-generate code
            </label>
            <div v-if="discountForm.generate_code">
              <label class="block text-xs text-gray-500 mb-1">Code Prefix (optional)</label>
              <input v-model="discountForm.code_prefix" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" placeholder="e.g. SAVE" />
            </div>
            <div v-else>
              <label class="block text-xs text-gray-500 mb-1">Discount Code *</label>
              <input v-model="discountForm.discount_code" class="w-full border border-gray-200 rounded px-2 py-1 text-sm font-mono uppercase" />
            </div>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Type *</label>
            <select v-model="discountForm.discount_type" class="w-full border border-gray-200 rounded px-2 py-1 text-sm">
              <option value="percentage">Percentage</option>
              <option value="fixed">Fixed</option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Value *</label>
            <input type="number" v-model="discountForm.discount_value" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Max Discount ($)</label>
            <input type="number" v-model="discountForm.max_discount_amount" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Min Payable ($)</label>
            <input type="number" v-model="discountForm.min_payable_amount" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Starts At</label>
            <input type="datetime-local" v-model="discountForm.starts_at" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Ends At</label>
            <input type="datetime-local" v-model="discountForm.ends_at" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Usage Limit</label>
            <input type="number" v-model="discountForm.usage_limit" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" placeholder="Unlimited" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Per-Client Limit</label>
            <input type="number" v-model="discountForm.per_client_usage_limit" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" placeholder="Unlimited" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs text-gray-500 mb-1">Description</label>
            <textarea v-model="(discountForm.description as string)" rows="2" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div class="col-span-2 flex flex-wrap gap-4">
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="discountForm.first_order_only" class="rounded" />
              First order only
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input type="checkbox" v-model="discountForm.is_active" class="rounded" />
              Active
            </label>
          </div>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button @click="showDiscountModal = false" class="px-4 py-2 text-sm border border-gray-200 rounded-md hover:bg-gray-50">Cancel</button>
          <button @click="saveDiscount" class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Save</button>
        </div>
      </div>
    </div>

    <!-- Campaign Create/Edit Modal -->
    <div v-if="showCampaignModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h2 class="text-lg font-semibold">{{ editingCampaign ? 'Edit Campaign' : 'New Campaign' }}</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Name *</label>
            <input v-model="campaignForm.name" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Slug</label>
            <input v-model="campaignForm.slug" class="w-full border border-gray-200 rounded px-2 py-1 text-sm font-mono" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Description</label>
            <textarea v-model="(campaignForm.description as string)" rows="2" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Starts At</label>
              <input type="datetime-local" v-model="campaignForm.starts_at" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Ends At</label>
              <input type="datetime-local" v-model="campaignForm.ends_at" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="campaignForm.is_active" class="rounded" />
            Active on creation
          </label>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="showCampaignModal = false" class="px-4 py-2 text-sm border border-gray-200 rounded-md hover:bg-gray-50">Cancel</button>
          <button @click="saveCampaign" class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Save</button>
        </div>
      </div>
    </div>

    <!-- Spend Tier Modal -->
    <div v-if="showTierModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h2 class="text-lg font-semibold">{{ editingTier ? 'Edit Spend Tier' : 'New Spend Tier' }}</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-xs text-gray-500 mb-1">Tier Name *</label>
            <input v-model="tierForm.name" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">Minimum Lifetime Spend ($) *</label>
            <input type="number" v-model="tierForm.minimum_lifetime_spend" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
          </div>
          <template v-if="!editingTier">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Discount Code *</label>
              <input v-model="tierForm.discount_code" class="w-full border border-gray-200 rounded px-2 py-1 text-sm font-mono uppercase" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Discount Type</label>
                <select v-model="tierForm.discount_type" class="w-full border border-gray-200 rounded px-2 py-1 text-sm">
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Discount Value</label>
                <input type="number" v-model="tierForm.discount_value" class="w-full border border-gray-200 rounded px-2 py-1 text-sm" />
              </div>
            </div>
          </template>
          <label class="flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="tierForm.is_active" class="rounded" />
            Active
          </label>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="showTierModal = false" class="px-4 py-2 text-sm border border-gray-200 rounded-md hover:bg-gray-50">Cancel</button>
          <button @click="saveTier" class="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import {
  adminDiscountsApi,
  type Discount,
  type AdminCampaign,
  type SpendTier,
  type DashboardSummary,
  type DiscountOriginGroup,
  type DiscountSettings,
  type FirstOrderConfig,
} from "@/api/adminDiscounts";

const tabs = [
  { key: "dashboard", label: "Dashboard" },
  { key: "discounts", label: "Discounts" },
  { key: "campaigns", label: "Campaigns" },
  { key: "spend-tiers", label: "Spend Tiers" },
  { key: "settings", label: "Settings" },
];

const activeTab = ref("dashboard");

const toast = ref<{ message: string; type: "success" | "error" } | null>(null);
function showToast(message: string, type: "success" | "error" = "success") {
  toast.value = { message, type };
  setTimeout(() => (toast.value = null), 3500);
}

// ── Dashboard ────────────────────────────────────────────────────────────────

const summary = ref<DashboardSummary | null>(null);
const originGroups = ref<DiscountOriginGroup[]>([]);
const expiringDiscounts = ref<Discount[]>([]);
const topDiscounts = ref<Discount[]>([]);
const unusedDiscounts = ref<Discount[]>([]);
const expireDays = ref(7);

const originMax = computed(() =>
  originGroups.value.reduce((m, g) => Math.max(m, g.total), 0)
);

async function loadDashboard() {
  try {
    const [s, o, e, t, u] = await Promise.all([
      adminDiscountsApi.dashboardSummary(),
      adminDiscountsApi.dashboardByOrigin(),
      adminDiscountsApi.dashboardExpiringSoon(expireDays.value),
      adminDiscountsApi.dashboardTopPerforming(8),
      adminDiscountsApi.dashboardUnused(),
    ]);
    summary.value = s.data;
    originGroups.value = o.data;
    expiringDiscounts.value = e.data;
    topDiscounts.value = t.data;
    unusedDiscounts.value = u.data;
  } catch {
    showToast("Failed to load dashboard.", "error");
  }
}

async function loadExpiring() {
  try {
    const r = await adminDiscountsApi.dashboardExpiringSoon(expireDays.value);
    expiringDiscounts.value = r.data;
  } catch {
    showToast("Failed to reload expiring discounts.", "error");
  }
}

// ── Discounts ─────────────────────────────────────────────────────────────────

const discounts = ref<Discount[]>([]);
const discountStatus = ref<string | undefined>(undefined);
const discountStatuses = [
  { label: "All", value: undefined as string | undefined },
  { label: "Working", value: "working" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Expired", value: "expired" },
  { label: "Archived", value: "archived" },
];

function discountStatusLabel(d: Discount): string {
  if (d.is_archived) return "Archived";
  if (!d.is_active) return "Inactive";
  if (d.ends_at && new Date(d.ends_at) < new Date()) return "Expired";
  if (d.starts_at && new Date(d.starts_at) > new Date()) return "Scheduled";
  return "Working";
}

function discountStatusClass(d: Discount): string {
  const base = "text-xs px-2 py-0.5 rounded-full font-medium ";
  const label = discountStatusLabel(d);
  if (label === "Working") return base + "bg-green-100 text-green-700";
  if (label === "Scheduled") return base + "bg-blue-100 text-blue-700";
  if (label === "Expired") return base + "bg-gray-100 text-gray-600";
  if (label === "Archived") return base + "bg-orange-100 text-orange-700";
  return base + "bg-gray-100 text-gray-500";
}

async function loadDiscounts() {
  try {
    const params: Record<string, unknown> = {};
    if (discountStatus.value) params.status = discountStatus.value;
    const r = await adminDiscountsApi.discounts(params);
    discounts.value = Array.isArray(r.data) ? r.data : [];
  } catch {
    showToast("Failed to load discounts.", "error");
  }
}

const showDiscountModal = ref(false);
const editingDiscount = ref<Discount | null>(null);
const discountForm = ref<Record<string, unknown>>({});

function openCreateDiscount() {
  editingDiscount.value = null;
  discountForm.value = {
    name: "",
    discount_code: "",
    generate_code: false,
    code_prefix: "",
    discount_type: "percentage",
    discount_value: "",
    max_discount_amount: null,
    min_payable_amount: "0.00",
    starts_at: "",
    ends_at: "",
    usage_limit: null,
    per_client_usage_limit: null,
    description: "",
    first_order_only: false,
    is_active: true,
  };
  showDiscountModal.value = true;
}

function openEditDiscount(d: Discount) {
  editingDiscount.value = d;
  discountForm.value = {
    name: d.name,
    discount_type: d.discount_type,
    discount_value: d.discount_value,
    max_discount_amount: d.max_discount_amount ?? "",
    min_payable_amount: d.min_payable_amount,
    starts_at: d.starts_at ? d.starts_at.slice(0, 16) : "",
    ends_at: d.ends_at ? d.ends_at.slice(0, 16) : "",
    usage_limit: d.usage_limit ?? "",
    per_client_usage_limit: d.per_client_usage_limit ?? "",
    description: d.description ?? "",
    first_order_only: d.first_order_only,
    is_active: d.is_active,
  };
  showDiscountModal.value = true;
}

async function saveDiscount() {
  try {
    const payload = { ...discountForm.value };
    if (!payload.max_discount_amount) delete payload.max_discount_amount;
    if (!payload.usage_limit) delete payload.usage_limit;
    if (!payload.per_client_usage_limit) delete payload.per_client_usage_limit;
    if (!payload.starts_at) delete payload.starts_at;
    if (!payload.ends_at) delete payload.ends_at;

    if (editingDiscount.value) {
      await adminDiscountsApi.updateDiscount(editingDiscount.value.id, payload);
    } else {
      await adminDiscountsApi.createDiscount(payload);
    }
    showDiscountModal.value = false;
    showToast(editingDiscount.value ? "Discount updated." : "Discount created.");
    loadDiscounts();
  } catch {
    showToast("Failed to save discount.", "error");
  }
}

async function archiveDiscount(d: Discount) {
  try {
    await adminDiscountsApi.archiveDiscount(d.id);
    showToast("Discount archived.");
    loadDiscounts();
  } catch {
    showToast("Failed to archive discount.", "error");
  }
}

async function restoreDiscount(d: Discount) {
  try {
    await adminDiscountsApi.restoreDiscount(d.id);
    showToast("Discount restored.");
    loadDiscounts();
  } catch {
    showToast("Failed to restore discount.", "error");
  }
}

// ── Campaigns ────────────────────────────────────────────────────────────────

const campaigns = ref<AdminCampaign[]>([]);

function campaignStatusLabel(c: AdminCampaign): string {
  if (c.is_archived) return "Archived";
  if (!c.is_active) return "Inactive";
  if (c.ends_at && new Date(c.ends_at) < new Date()) return "Expired";
  if (c.starts_at && new Date(c.starts_at) > new Date()) return "Scheduled";
  return "Active";
}

function campaignStatusClass(c: AdminCampaign): string {
  const base = "text-xs px-2 py-0.5 rounded-full font-medium ";
  const label = campaignStatusLabel(c);
  if (label === "Active") return base + "bg-green-100 text-green-700";
  if (label === "Scheduled") return base + "bg-blue-100 text-blue-700";
  if (label === "Expired") return base + "bg-gray-100 text-gray-600";
  if (label === "Archived") return base + "bg-orange-100 text-orange-700";
  return base + "bg-gray-100 text-gray-500";
}

async function loadCampaigns() {
  try {
    const r = await adminDiscountsApi.campaigns();
    campaigns.value = r.data.campaigns ?? [];
  } catch {
    showToast("Failed to load campaigns.", "error");
  }
}

const showCampaignModal = ref(false);
const editingCampaign = ref<AdminCampaign | null>(null);
const campaignForm = ref<Record<string, unknown>>({});

function openCreateCampaign() {
  editingCampaign.value = null;
  campaignForm.value = { name: "", slug: "", description: "", starts_at: "", ends_at: "", is_active: false };
  showCampaignModal.value = true;
}

function openEditCampaign(c: AdminCampaign) {
  editingCampaign.value = c;
  campaignForm.value = {
    name: c.name,
    slug: c.slug,
    description: c.description ?? "",
    starts_at: c.starts_at ? c.starts_at.slice(0, 16) : "",
    ends_at: c.ends_at ? c.ends_at.slice(0, 16) : "",
    is_active: c.is_active,
  };
  showCampaignModal.value = true;
}

async function saveCampaign() {
  try {
    const payload = { ...campaignForm.value };
    if (!payload.starts_at) delete payload.starts_at;
    if (!payload.ends_at) delete payload.ends_at;

    if (editingCampaign.value) {
      await adminDiscountsApi.updateCampaign(editingCampaign.value.id, payload);
    } else {
      await adminDiscountsApi.createCampaign(payload);
    }
    showCampaignModal.value = false;
    showToast(editingCampaign.value ? "Campaign updated." : "Campaign created.");
    loadCampaigns();
  } catch {
    showToast("Failed to save campaign.", "error");
  }
}

async function activateCampaign(c: AdminCampaign) {
  try {
    await adminDiscountsApi.activateCampaign(c.id);
    showToast("Campaign activated.");
    loadCampaigns();
  } catch {
    showToast("Failed to activate campaign.", "error");
  }
}

async function deactivateCampaign(c: AdminCampaign) {
  try {
    await adminDiscountsApi.deactivateCampaign(c.id);
    showToast("Campaign deactivated.");
    loadCampaigns();
  } catch {
    showToast("Failed to deactivate campaign.", "error");
  }
}

async function archiveCampaign(c: AdminCampaign) {
  try {
    await adminDiscountsApi.archiveCampaign(c.id);
    showToast("Campaign archived.");
    loadCampaigns();
  } catch {
    showToast("Failed to archive campaign.", "error");
  }
}

async function restoreCampaign(c: AdminCampaign) {
  try {
    await adminDiscountsApi.restoreCampaign(c.id);
    showToast("Campaign restored.");
    loadCampaigns();
  } catch {
    showToast("Failed to restore campaign.", "error");
  }
}

// ── Spend Tiers ───────────────────────────────────────────────────────────────

const spendTiers = ref<SpendTier[]>([]);
const showTierModal = ref(false);
const editingTier = ref<SpendTier | null>(null);
const tierForm = ref<Record<string, unknown>>({});

async function loadSpendTiers() {
  try {
    const r = await adminDiscountsApi.spendTiers();
    spendTiers.value = r.data.spend_tiers ?? [];
  } catch {
    showToast("Failed to load spend tiers.", "error");
  }
}

function openCreateTier() {
  editingTier.value = null;
  tierForm.value = {
    name: "",
    minimum_lifetime_spend: "",
    discount_code: "",
    discount_type: "percentage",
    discount_value: "",
    is_active: true,
  };
  showTierModal.value = true;
}

function openEditTier(t: SpendTier) {
  editingTier.value = t;
  tierForm.value = {
    name: t.name,
    minimum_lifetime_spend: t.minimum_lifetime_spend,
    is_active: t.is_active,
  };
  showTierModal.value = true;
}

async function saveTier() {
  try {
    if (editingTier.value) {
      await adminDiscountsApi.updateSpendTier(editingTier.value.id, tierForm.value);
    } else {
      await adminDiscountsApi.createSpendTier(tierForm.value);
    }
    showTierModal.value = false;
    showToast(editingTier.value ? "Tier updated." : "Tier created.");
    loadSpendTiers();
  } catch {
    showToast("Failed to save spend tier.", "error");
  }
}

// ── Settings ──────────────────────────────────────────────────────────────────

const settings = ref<DiscountSettings | null>(null);
const firstOrderConfig = ref<FirstOrderConfig | null>(null);

async function loadSettings() {
  try {
    const [s, f] = await Promise.all([
      adminDiscountsApi.settings(),
      adminDiscountsApi.firstOrderConfig(),
    ]);
    settings.value = s.data;
    firstOrderConfig.value = f.data;
  } catch {
    showToast("Failed to load settings.", "error");
  }
}

async function saveSettings() {
  if (!settings.value) return;
  try {
    await adminDiscountsApi.updateSettings(settings.value);
    showToast("Settings saved.");
  } catch {
    showToast("Failed to save settings.", "error");
  }
}

async function saveFirstOrderConfig() {
  if (!firstOrderConfig.value) return;
  try {
    await adminDiscountsApi.updateFirstOrderConfig(firstOrderConfig.value);
    showToast("First order config saved.");
  } catch {
    showToast("Failed to save config.", "error");
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([
    loadDashboard(),
    loadDiscounts(),
    loadCampaigns(),
    loadSpendTiers(),
    loadSettings(),
  ]);
});
</script>
