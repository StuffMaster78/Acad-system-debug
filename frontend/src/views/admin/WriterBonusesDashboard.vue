<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Writer Bonuses</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Reward writers for performance and track bonus spending
        </p>
      </div>
      <button
        @click="openCreateModal"
        class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Bonus
      </button>
    </div>

    <!-- Stats Cards -->
    <div v-if="statistics" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-700 rounded-lg p-6">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Total Bonuses</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ statistics.total_bonuses || 0 }}</p>
        <p class="text-xs text-green-600 dark:text-green-400 mt-1">
          ${{ formatCurrency(statistics.total_amount || 0) }}
        </p>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Paid Bonuses</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ statistics.paid_count || 0 }}</p>
        <p class="text-xs text-blue-600 dark:text-blue-400 mt-1">
          ${{ formatCurrency(statistics.total_paid || 0) }}
        </p>
      </div>
      <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-6">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending Bonuses</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ statistics.pending_count || 0 }}</p>
        <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
          ${{ formatCurrency(statistics.total_pending || 0) }}
        </p>
      </div>
      <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Average Bonus</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">
          ${{ formatCurrency(statistics.average_bonus || 0) }}
        </p>
        <p class="text-xs text-purple-600 dark:text-purple-400 mt-1">
          {{ statistics.recent_bonuses_count || 0 }} recent (30d)
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Writer ID</label>
          <input
            v-model.number="filters.writer_id"
            @input="debouncedSearch"
            type="number"
            placeholder="Filter by writer ID"
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.is_paid" @change="loadBonuses" class="w-full border rounded px-3 py-2">
            <option value="">All</option>
            <option value="true">Paid</option>
            <option value="false">Pending</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Category</label>
          <input
            v-model="filters.category"
            @input="debouncedSearch"
            type="text"
            placeholder="performance, quality, loyalty..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Bonuses Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Amount</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="bonuses.length === 0">
              <td colspan="7" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                No bonuses found
              </td>
            </tr>
            <tr
              v-for="bonus in bonuses"
              :key="bonus.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">#{{ bonus.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                <div>
                  <div class="font-medium">{{ bonus.writer_display || bonus.writer?.username || 'N/A' }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400" v-if="bonus.writer_email">
                    {{ bonus.writer_email }}
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ bonus.category || 'other' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 dark:text-white">
                ${{ formatCurrency(bonus.amount) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    bonus.is_paid
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                  ]"
                >
                  {{ bonus.is_paid ? 'Paid' : 'Pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(bonus.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    v-if="!bonus.is_paid"
                    @click="payBonus(bonus, true)"
                    class="text-green-600 hover:text-green-900 dark:text-green-400"
                    title="Pay & add to wallet"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8c-1.657 0-3 .671-3 1.5S10.343 11 12 11s3 .671 3 1.5S13.657 14 12 14m0-6v.01M12 14v.01M8 8h8a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2v-6a2 2 0 012-2z" />
                    </svg>
                  </button>
                  <button
                    v-if="!bonus.is_paid"
                    @click="payBonus(bonus, false)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    title="Mark as paid (no wallet)"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <button
                    @click="deleteBonus(bonus)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400"
                    title="Delete bonus"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && bonuses.length > 0" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-300">
          Showing {{ bonuses.length }} bonus(es)
        </div>
      </div>
    </div>

    <!-- Create/Edit Bonus Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeCreateModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ editingBonus ? 'Edit Bonus' : 'Add Bonus' }}
            </h3>
            <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveBonus" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Writer ID *</label>
              <input
                v-model.number="bonusForm.writer_id"
                type="number"
                required
                placeholder="Writer ID"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Amount *</label>
              <input
                v-model.number="bonusForm.amount"
                type="number"
                step="0.01"
                min="0"
                required
                placeholder="0.00"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
              <input
                v-model="bonusForm.category"
                type="text"
                placeholder="performance, quality, loyalty..."
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Reason</label>
              <textarea
                v-model="bonusForm.reason"
                rows="3"
                placeholder="Short explanation for the bonus"
                class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:text-white"
              ></textarea>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="bonusForm.add_to_wallet"
                type="checkbox"
                id="add_to_wallet"
                class="rounded"
              />
              <label for="add_to_wallet" class="text-sm text-gray-700 dark:text-gray-300">
                Add to writer's wallet immediately
              </label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                @click="closeCreateModal"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : (editingBonus ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import specialOrdersAPI from '@/api/special-orders'

const { showToast } = useToast()

const loading = ref(true)
const bonuses = ref([])
const statistics = ref(null)

const showCreateModal = ref(false)
const editingBonus = ref(null)
const saving = ref(false)

const filters = ref({
  writer_id: '',
  is_paid: '',
  category: '',
})

const bonusForm = ref({
  writer_id: '',
  amount: 0,
  category: '',
  reason: '',
  add_to_wallet: true,
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadData()
  }, 400)
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      ...filters.value,
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const [listRes, statsRes] = await Promise.all([
      specialOrdersAPI.listWriterBonuses(params),
      specialOrdersAPI.getWriterBonusStatistics(params),
    ])

    bonuses.value = Array.isArray(listRes.data) ? listRes.data : listRes.data.results || []
    statistics.value = statsRes.data
  } catch (error) {
    showToast('Failed to load writer bonuses: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error loading writer bonuses:', error)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    writer_id: '',
    is_paid: '',
    category: '',
  }
  loadData()
}

const openCreateModal = () => {
  editingBonus.value = null
  bonusForm.value = {
    writer_id: '',
    amount: 0,
    category: '',
    reason: '',
    add_to_wallet: true,
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingBonus.value = null
}

const saveBonus = async () => {
  saving.value = true
  try {
    const payload = { ...bonusForm.value }
    if (editingBonus.value) {
      await specialOrdersAPI.updateWriterBonus(editingBonus.value.id, payload)
      showToast('Bonus updated successfully', 'success')
    } else {
      await specialOrdersAPI.createWriterBonus(payload)
      showToast('Bonus created successfully', 'success')
    }
    closeCreateModal()
    await loadData()
  } catch (error) {
    showToast('Failed to save bonus: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error saving bonus:', error)
  } finally {
    saving.value = false
  }
}

const payBonus = async (bonus, addToWallet = true) => {
  if (!confirm(`Mark bonus #${bonus.id} as paid${addToWallet ? ' and add to wallet' : ''}?`)) return
  try {
    await specialOrdersAPI.payWriterBonus(bonus.id, { add_to_wallet: addToWallet })
    showToast('Bonus paid successfully', 'success')
    await loadData()
  } catch (error) {
    showToast('Failed to pay bonus: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error paying bonus:', error)
  }
}

const deleteBonus = async (bonus) => {
  if (!confirm(`Are you sure you want to delete bonus #${bonus.id}?`)) return
  try {
    await specialOrdersAPI.deleteWriterBonus(bonus.id)
    showToast('Bonus deleted successfully', 'success')
    await loadData()
  } catch (error) {
    showToast('Failed to delete bonus: ' + (error.response?.data?.detail || error.message), 'error')
    console.error('Error deleting bonus:', error)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount || 0)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(() => {
  loadData()
})
</script>

