<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Social Platforms</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage social media platforms for blog sharing</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Add Platform
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Platforms</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ platforms.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ platforms.filter(p => p.is_active).length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Inactive</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ platforms.filter(p => !p.is_active).length }}</p>
      </div>
    </div>

    <!-- Platforms Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="platform in platforms"
        :key="platform.id"
        :class="[
          'card p-4 transition-all',
          !platform.is_active ? 'opacity-60' : ''
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ platform.name }}</h3>
            <p v-if="platform.base_url" class="text-sm text-gray-500 dark:text-gray-400">{{ platform.base_url }}</p>
          </div>
          <span
            :class="[
              'px-2 py-1 text-xs font-semibold rounded-full',
              platform.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
              'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
            ]"
          >
            {{ platform.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div v-if="platform.icon" class="mb-3">
          <img :src="platform.icon" :alt="platform.name" class="h-8 w-8 object-contain" />
        </div>
        <div class="flex gap-2">
          <button
            @click="editPlatform(platform)"
            class="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Edit
          </button>
          <button
            @click="toggleStatus(platform)"
            class="px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            {{ platform.is_active ? 'Deactivate' : 'Activate' }}
          </button>
          <button
            @click="deletePlatform(platform)"
            class="px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
      <div v-if="platforms.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No platforms found. Create your first platform to get started.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingPlatform ? 'Edit Social Platform' : 'Add Social Platform'"
      size="md"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="e.g., Facebook, Twitter"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Base URL</label>
          <input
            v-model="form.base_url"
            type="url"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="https://..."
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Icon URL</label>
          <input
            v-model="form.icon"
            type="url"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="https://..."
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
          @click="savePlatform"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingPlatform ? 'Update' : 'Create') }}
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
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import blogPagesAPI from '@/api/blog-pages'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const platforms = ref([])
const showModal = ref(false)
const editingPlatform = ref(null)
const formError = ref('')

const form = ref({
  name: '',
  base_url: '',
  icon: '',
  is_active: true,
})

const loadPlatforms = async () => {
  loading.value = true
  try {
    const response = await blogPagesAPI.listSocialPlatforms()
    platforms.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load social platforms')
    console.error('Error loading platforms:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingPlatform.value = null
  form.value = {
    name: '',
    base_url: '',
    icon: '',
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const editPlatform = (platform) => {
  editingPlatform.value = platform
  form.value = {
    name: platform.name || '',
    base_url: platform.base_url || '',
    icon: platform.icon || '',
    is_active: platform.is_active !== undefined ? platform.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPlatform.value = null
  formError.value = ''
}

const savePlatform = async () => {
  saving.value = true
  formError.value = ''
  
  try {
    if (editingPlatform.value) {
      await blogPagesAPI.updateSocialPlatform(editingPlatform.value.id, form.value)
      showSuccess('Platform updated successfully')
    } else {
      await blogPagesAPI.createSocialPlatform(form.value)
      showSuccess('Platform created successfully')
    }
    
    closeModal()
    loadPlatforms()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save platform'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (platform) => {
  try {
    await blogPagesAPI.updateSocialPlatform(platform.id, { is_active: !platform.is_active })
    showSuccess(`Platform ${platform.is_active ? 'deactivated' : 'activated'}`)
    loadPlatforms()
  } catch (error) {
    showError('Failed to update platform status')
  }
}

const deletePlatform = (platform) => {
  confirm.showDestructive(
    'Delete Platform',
    `Are you sure you want to delete "${platform.name}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await blogPagesAPI.deleteSocialPlatform(platform.id)
        showSuccess('Platform deleted successfully')
        loadPlatforms()
      } catch (error) {
        showError('Failed to delete platform')
      }
    }
  )
}

onMounted(() => {
  loadPlatforms()
})
</script>

