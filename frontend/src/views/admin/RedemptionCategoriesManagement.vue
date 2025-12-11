<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Redemption Categories</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage categories for redemption items</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Add Category</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Categories</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Items</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total_items || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Inactive</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.inactive || 0 }}</p>
      </div>
    </div>

    <!-- Search -->
    <div class="card p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search categories by name..."
        class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
        @input="debouncedSearch"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading categories...</p>
    </div>

    <!-- Categories List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="category in categories"
        :key="category.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {{ category.name }}
            </h3>
            <p v-if="category.description" class="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {{ category.description }}
            </p>
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  category.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                ]"
              >
                {{ category.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ category.items_count || 0 }} items
              </span>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="editCategory(category)"
              class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
              title="Edit"
            >
              ✏️
            </button>
            <button
              @click="deleteCategory(category)"
              class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
              title="Delete"
            >
              🗑️
            </button>
          </div>
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          Sort Order: {{ category.sort_order || 0 }}
        </div>
      </div>
      <div v-if="categories.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No categories found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingCategory ? 'Edit Category' : 'Create Category'"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Category name (e.g., Discounts, Products)"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Category description"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sort Order</label>
          <input
            v-model.number="form.sort_order"
            type="number"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="0"
          />
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
          @click="saveCategory"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingCategory ? 'Update' : 'Create') }}
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
const categories = ref([])
const stats = ref({})
const searchQuery = ref('')
const showModal = ref(false)
const editingCategory = ref(null)
const formError = ref('')

const form = ref({
  name: '',
  description: '',
  sort_order: 0,
  is_active: true,
})

const canSave = computed(() => {
  return form.value.name.trim()
})

const debouncedSearch = debounce(() => {
  loadCategories()
}, 300)

const loadCategories = async () => {
  loading.value = true
  try {
    const response = await loyaltyAPI.listRedemptionCategories()
    let allCategories = response.data.results || response.data || []
    
    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allCategories = allCategories.filter(cat => 
        cat.name.toLowerCase().includes(query) ||
        (cat.description && cat.description.toLowerCase().includes(query))
      )
    }
    
    categories.value = allCategories
    
    stats.value = {
      total: allCategories.length,
      active: allCategories.filter(c => c.is_active).length,
      inactive: allCategories.filter(c => !c.is_active).length,
      total_items: allCategories.reduce((sum, c) => sum + (c.items_count || 0), 0),
    }
  } catch (error) {
    showError('Failed to load redemption categories')
    console.error('Error loading categories:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingCategory.value = null
  form.value = {
    name: '',
    description: '',
    sort_order: 0,
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const editCategory = (category) => {
  editingCategory.value = category
  form.value = {
    name: category.name || '',
    description: category.description || '',
    sort_order: category.sort_order || 0,
    is_active: category.is_active !== undefined ? category.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
  formError.value = ''
}

const saveCategory = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingCategory.value) {
      await loyaltyAPI.updateRedemptionCategory(editingCategory.value.id, form.value)
      showSuccess('Category updated successfully')
    } else {
      await loyaltyAPI.createRedemptionCategory(form.value)
      showSuccess('Category created successfully')
    }
    closeModal()
    loadCategories()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save category'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteCategory = (category) => {
  confirm.showDestructive(
    'Delete Category',
    `Are you sure you want to delete the category "${category.name}"?`,
    `This action cannot be undone. All items in this category will need to be reassigned.`,
    async () => {
      try {
        await loyaltyAPI.deleteRedemptionCategory(category.id)
        showSuccess('Category deleted successfully')
        loadCategories()
      } catch (error) {
        showError('Failed to delete category')
        console.error('Error deleting category:', error)
      }
    }
  )
}

onMounted(() => {
  loadCategories()
})
</script>

