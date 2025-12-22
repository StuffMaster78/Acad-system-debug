<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">A/B Tests Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage A/B tests for blog content optimization</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Create A/B Test
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Tests</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ abTests.length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ abTests.filter(t => t.is_active).length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Completed</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ abTests.filter(t => t.winner).length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Total Clicks</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ totalClicks }}</p>
      </div>
    </div>

    <!-- AB Tests Table -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Variant A Clicks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Variant B Clicks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Winner</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="test in abTests"
              :key="test.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                Blog #{{ test.blog || test.blog_id || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ test.click_count_a || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ test.click_count_b || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="test.winner"
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    test.winner === 'A' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                    'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  ]"
                >
                  Variant {{ test.winner }}
                </span>
                <span v-else class="text-sm text-gray-500 dark:text-gray-400">Pending</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    test.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                  ]"
                >
                  {{ test.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="viewDetails(test)"
                  class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                >
                  View
                </button>
                <button
                  @click="deleteTest(test)"
                  class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="abTests.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No A/B tests found. Create your first test to get started.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingTest ? 'Edit A/B Test' : 'Create A/B Test'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Blog ID *</label>
          <input
            v-model.number="form.blog"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Blog post ID"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Variant A Image URL</label>
            <input
              v-model="form.image_a"
              type="url"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="https://..."
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Variant B Image URL</label>
            <input
              v-model="form.image_b"
              type="url"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="https://..."
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
          @click="saveTest"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingTest ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

    <!-- View Details Modal -->
    <Modal
      :visible="showDetailsModal"
      @close="closeDetailsModal"
      title="A/B Test Details"
      size="lg"
    >
      <div v-if="selectedTest" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Blog</p>
            <p class="font-medium text-gray-900 dark:text-white">Blog #{{ selectedTest.blog || selectedTest.blog_id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedTest.is_active ? 'Active' : 'Inactive' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Variant A Clicks</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedTest.click_count_a || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Variant B Clicks</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedTest.click_count_b || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Winner</p>
            <p class="font-medium text-gray-900 dark:text-white">{{ selectedTest.winner ? `Variant ${selectedTest.winner}` : 'Pending' }}</p>
          </div>
        </div>
        <div v-if="selectedTest.image_a" class="mt-4">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Variant A Image</p>
          <img :src="selectedTest.image_a" alt="Variant A" class="max-w-full h-auto rounded-lg" />
        </div>
        <div v-if="selectedTest.image_b" class="mt-4">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Variant B Image</p>
          <img :src="selectedTest.image_b" alt="Variant B" class="max-w-full h-auto rounded-lg" />
        </div>
      </div>
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
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import blogPagesAPI from '@/api/blog-pages'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const abTests = ref([])
const showModal = ref(false)
const showDetailsModal = ref(false)
const editingTest = ref(null)
const selectedTest = ref(null)
const formError = ref('')

const form = ref({
  blog: null,
  image_a: '',
  image_b: '',
  is_active: true,
})

const totalClicks = computed(() => {
  return abTests.value.reduce((sum, test) => {
    return sum + (test.click_count_a || 0) + (test.click_count_b || 0)
  }, 0)
})

const loadTests = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listABTests()
    abTests.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load A/B tests')
    console.error('Error loading tests:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingTest.value = null
  form.value = {
    blog: null,
    image_a: '',
    image_b: '',
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingTest.value = null
  formError.value = ''
}

const saveTest = async () => {
  saving.value = true
  formError.value = ''
  
  try {
    if (editingTest.value) {
      await blogPagesAPI.updateABTest(editingTest.value.id, form.value)
      showSuccess('A/B test updated successfully')
    } else {
      await blogPagesAPI.createABTest(form.value)
      showSuccess('A/B test created successfully')
    }
    
    closeModal()
    loadTests()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save A/B test'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const viewDetails = (test) => {
  selectedTest.value = test
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedTest.value = null
}

const deleteTest = (test) => {
  confirm.showDestructive(
    'Delete A/B Test',
    'Are you sure you want to delete this A/B test?',
    'This action cannot be undone.',
    async () => {
      try {
        await blogPagesAPI.deleteABTest(test.id)
        showSuccess('A/B test deleted successfully')
        loadTests()
      } catch (error) {
        showError('Failed to delete A/B test')
      }
    }
  )
}

onMounted(() => {
  loadTests()
})
</script>

