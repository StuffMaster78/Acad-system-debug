<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">FAQs Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage FAQ articles for support knowledge base</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Add FAQ</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total FAQs</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Writer FAQs</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.writer_faqs || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Client FAQs</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.client_faqs || 0 }}</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search FAQs by question or answer..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="categoryFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadFAQs"
        >
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <select
          v-model="activeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadFAQs"
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
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading FAQs...</p>
    </div>

    <!-- FAQs List -->
    <div v-else class="space-y-4">
      <div
        v-for="faq in faqs"
        :key="faq.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ faq.question }}
              </h3>
              <span
                v-if="faq.is_active"
                class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
              >
                Active
              </span>
              <span
                v-else
                class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300"
              >
                Inactive
              </span>
              <span
                v-if="faq.category"
                class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
              >
                {{ faq.category_name || faq.category }}
              </span>
            </div>
            <p class="text-gray-600 dark:text-gray-400 mb-2">{{ faq.answer }}</p>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              <span>Created: {{ formatDate(faq.created_at) }}</span>
              <span v-if="faq.updated_at" class="mx-2">•</span>
              <span v-if="faq.updated_at">Updated: {{ formatDate(faq.updated_at) }}</span>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="editFAQ(faq)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteFAQ(faq)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div v-if="faqs.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No FAQs found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingFAQ ? 'Edit FAQ' : 'Create FAQ'"
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
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Question *</label>
          <input
            v-model="form.question"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter FAQ question"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Answer *</label>
          <textarea
            v-model="form.answer"
            rows="6"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter FAQ answer"
          ></textarea>
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
          @click="saveFAQ"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingFAQ ? 'Update' : 'Create') }}
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
import supportManagementAPI from '@/api/support-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const faqs = ref([])
const categories = ref([])
const stats = ref({})
const searchQuery = ref('')
const categoryFilter = ref('')
const activeFilter = ref('')
const showModal = ref(false)
const editingFAQ = ref(null)
const formError = ref('')

const form = ref({
  category: null,
  question: '',
  answer: '',
  is_active: true,
})

const canSave = computed(() => {
  return form.value.category && form.value.question.trim() && form.value.answer.trim()
})

const debouncedSearch = debounce(() => {
  loadFAQs()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadFAQs = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (categoryFilter.value) params.category = categoryFilter.value
    if (activeFilter.value !== '') params.is_active = activeFilter.value === 'true'
    const response = await supportManagementAPI.listFAQs(params)
    faqs.value = response.data.results || response.data || []
    
    stats.value = {
      total: faqs.value.length,
      active: faqs.value.filter(f => f.is_active).length,
      writer_faqs: faqs.value.filter(f => f.category_type === 'writer' || f.category_name?.includes('Writer')).length,
      client_faqs: faqs.value.filter(f => f.category_type === 'client' || f.category_name?.includes('Client')).length,
    }
  } catch (error) {
    showError('Failed to load FAQs')
    console.error('Error loading FAQs:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  // Categories would come from a separate endpoint if available
  // For now, we'll use a placeholder
  categories.value = []
}

const openCreateModal = () => {
  editingFAQ.value = null
  form.value = {
    category: null,
    question: '',
    answer: '',
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const editFAQ = (faq) => {
  editingFAQ.value = faq
  form.value = {
    category: faq.category || faq.category_id || null,
    question: faq.question || '',
    answer: faq.answer || '',
    is_active: faq.is_active !== undefined ? faq.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingFAQ.value = null
  formError.value = ''
}

const saveFAQ = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingFAQ.value) {
      await supportManagementAPI.updateFAQ(editingFAQ.value.id, form.value)
      showSuccess('FAQ updated successfully')
    } else {
      await supportManagementAPI.createFAQ(form.value)
      showSuccess('FAQ created successfully')
    }
    closeModal()
    loadFAQs()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save FAQ'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteFAQ = (faq) => {
  confirm.showDestructive(
    'Delete FAQ',
    `Are you sure you want to delete this FAQ?`,
    `Question: "${faq.question}"\n\nThis action cannot be undone.`,
    async () => {
      try {
        await supportManagementAPI.deleteFAQ(faq.id)
        showSuccess('FAQ deleted successfully')
        loadFAQs()
      } catch (error) {
        showError('Failed to delete FAQ')
        console.error('Error deleting FAQ:', error)
      }
    }
  )
}

onMounted(() => {
  loadFAQs()
  loadCategories()
})
</script>

