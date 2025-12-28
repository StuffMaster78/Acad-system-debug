<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Redemption Items</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage items available for redemption with loyalty points</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Add Item</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Items</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Redemptions</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total_redemptions || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Low Stock</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.low_stock || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search items by name..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="categoryFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadItems"
        >
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <select
          v-model="typeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadItems"
        >
          <option value="">All Types</option>
          <option value="discount">Discount Code</option>
          <option value="cash">Cash/Wallet Credit</option>
          <option value="product">Physical Product</option>
          <option value="service">Service Credit</option>
          <option value="voucher">Voucher/Code</option>
        </select>
        <select
          v-model="activeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadItems"
        >
          <option value="">All Statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading items...</p>
    </div>

    <!-- Items Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {{ item.name }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
              {{ item.description }}
            </p>
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                {{ item.points_required }} points
              </span>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                ]"
              >
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                {{ item.redemption_type ? item.redemption_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A' }}
              </span>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div v-if="item.category_name">
                Category: {{ item.category_name }}
              </div>
              <div v-if="item.total_redemptions !== undefined">
                Redemptions: {{ item.total_redemptions }}
              </div>
              <div v-if="item.stock_quantity !== null && item.stock_quantity !== undefined">
                Stock: {{ item.stock_quantity }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="editItem(item)"
              class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
              title="Edit"
            >
              ✏️
            </button>
            <button
              @click="deleteItem(item)"
              class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
              title="Delete"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
      <div v-if="items.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No items found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingItem ? 'Edit Redemption Item' : 'Create Redemption Item'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category *</label>
          <select
            v-model="form.category"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="">Select Category</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Item name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description *</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Item description"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Points Required *</label>
          <input
            v-model.number="form.points_required"
            type="number"
            min="1"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Redemption Type *</label>
          <select
            v-model="form.redemption_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="discount">Discount Code</option>
            <option value="cash">Cash/Wallet Credit</option>
            <option value="product">Physical Product</option>
            <option value="service">Service Credit</option>
            <option value="voucher">Voucher/Code</option>
          </select>
        </div>
        <div v-if="form.redemption_type === 'discount'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Discount Code</label>
          <input
            v-model="form.discount_code"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="DISCOUNT10"
          />
        </div>
        <div v-if="form.redemption_type === 'discount'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Discount Amount ($)</label>
          <input
            v-model.number="form.discount_amount"
            type="number"
            step="0.01"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="10.00"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Stock Quantity</label>
            <input
              v-model.number="form.stock_quantity"
              type="number"
              min="0"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="Unlimited"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Max Per Client</label>
            <input
              v-model.number="form.max_per_client"
              type="number"
              min="0"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="Unlimited"
            />
          </div>
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_active"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
          </label>
        </div>
        <div v-if="formError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ formError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveItem"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingItem ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

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
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import loyaltyAPI from '@/api/loyalty-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const items = ref([])
const categories = ref([])
const stats = ref({})
const searchQuery = ref('')
const categoryFilter = ref('')
const typeFilter = ref('')
const activeFilter = ref('')
const showModal = ref(false)
const editingItem = ref(null)
const formError = ref('')

const form = ref({
  category: null,
  name: '',
  description: '',
  points_required: 100,
  redemption_type: 'discount',
  discount_code: '',
  discount_amount: null,
  stock_quantity: null,
  max_per_client: null,
  is_active: true,
})

const canSave = computed(() => {
  return form.value.category && form.value.name.trim() && form.value.description.trim() && form.value.points_required > 0
})

const debouncedSearch = debounce(() => {
  loadItems()
}, 300)

const loadCategories = async () => {
  try {
    const response = await loyaltyAPI.listRedemptionCategories()
    categories.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadItems = async () => {
  loading.value = true
  try {
    const params = {}
    if (categoryFilter.value) params.category = categoryFilter.value
    if (typeFilter.value) params.redemption_type = typeFilter.value
    if (activeFilter.value !== '') params.is_active = activeFilter.value === 'true'
    
    const response = await loyaltyAPI.listRedemptionItems(params)
    let allItems = response.data.results || response.data || []
    
    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allItems = allItems.filter(item => 
        item.name.toLowerCase().includes(query) ||
        (item.description && item.description.toLowerCase().includes(query))
      )
    }
    
    items.value = allItems
    
    stats.value = {
      total: allItems.length,
      active: allItems.filter(i => i.is_active).length,
      total_redemptions: allItems.reduce((sum, i) => sum + (i.total_redemptions || 0), 0),
      low_stock: allItems.filter(i => i.stock_quantity !== null && i.stock_quantity < 10).length,
    }
  } catch (error) {
    showError('Failed to load redemption items')
    console.error('Error loading items:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingItem.value = null
  form.value = {
    category: null,
    name: '',
    description: '',
    points_required: 100,
    redemption_type: 'discount',
    discount_code: '',
    discount_amount: null,
    stock_quantity: null,
    max_per_client: null,
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const editItem = (item) => {
  editingItem.value = item
  form.value = {
    category: item.category || item.category_id || null,
    name: item.name || '',
    description: item.description || '',
    points_required: item.points_required || 100,
    redemption_type: item.redemption_type || 'discount',
    discount_code: item.discount_code || '',
    discount_amount: item.discount_amount || null,
    stock_quantity: item.stock_quantity !== undefined ? item.stock_quantity : null,
    max_per_client: item.max_per_client !== undefined ? item.max_per_client : null,
    is_active: item.is_active !== undefined ? item.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingItem.value = null
  formError.value = ''
}

const saveItem = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingItem.value) {
      await loyaltyAPI.updateRedemptionItem(editingItem.value.id, form.value)
      showSuccess('Item updated successfully')
    } else {
      await loyaltyAPI.createRedemptionItem(form.value)
      showSuccess('Item created successfully')
    }
    closeModal()
    loadItems()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save item'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteItem = (item) => {
  confirm.showDestructive(
    'Delete Redemption Item',
    `Are you sure you want to delete "${item.name}"?`,
    `This action cannot be undone. All pending redemption requests for this item will be affected.`,
    async () => {
      try {
        await loyaltyAPI.deleteRedemptionItem(item.id)
        showSuccess('Item deleted successfully')
        loadItems()
      } catch (error) {
        showError('Failed to delete item')
        console.error('Error deleting item:', error)
      }
    }
  )
}

onMounted(() => {
  loadCategories()
  loadItems()
})
</script>

