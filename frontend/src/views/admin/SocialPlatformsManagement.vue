<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Social Platforms Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Configure social media platforms for blog sharing</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Platform
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Platforms</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Shares</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total_shares }}</p>
      </div>
    </div>

    <!-- Platforms List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
      
      <div v-else-if="!platforms.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No social platforms found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Add Your First Platform</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Platform</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Share URL</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Shares</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="platform in platforms" :key="platform.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ platform.platform_name || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ platform.display_name || platform.platform_name || '—' }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ platform.share_url_template || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="platform.is_active !== false ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ platform.is_active !== false ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(platform.total_shares || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewPlatform(platform)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editPlatform(platform)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deletePlatform(platform)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingPlatform" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingPlatform ? 'Edit Social Platform' : 'Add Social Platform' }}
          </h3>
        </div>
        <form @submit.prevent="savePlatform" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Platform Name *</label>
            <select
              v-model="platformForm.platform_name"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select Platform</option>
              <option value="facebook">Facebook</option>
              <option value="twitter">Twitter</option>
              <option value="linkedin">LinkedIn</option>
              <option value="pinterest">Pinterest</option>
              <option value="reddit">Reddit</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="email">Email</option>
            </select>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Display Name</label>
          <input
              v-model="platformForm.display_name"
              type="text"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Share URL Template</label>
          <input
              v-model="platformForm.share_url_template"
            type="url"
            placeholder="https://..."
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Use {url} and {title} as placeholders</p>
        </div>
        <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Icon URL</label>
            <input
              v-model="platformForm.icon_url"
              type="url"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
            <select
              v-model="platformForm.is_active"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
        </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingPlatform ? 'Update' : 'Create') }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
        </div>
        </form>
      </div>
    </div>

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
import blogPagesAPI from '@/api/blog-pages'
import { useToast } from '@/composables/useToast'

const { showSuccess, showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const platforms = ref([])
const stats = ref({ total: 0, active: 0, total_shares: 0 })
const showCreateModal = ref(false)
const editingPlatform = ref(null)

const platformForm = ref({
  platform_name: '',
  display_name: '',
  share_url_template: '',
  icon_url: '',
  is_active: true,
})

const loadPlatforms = async () => {
  loading.value = true
  try {
    const res = await blogPagesAPI.listSocialPlatforms({})
    platforms.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: platforms.value.length,
      active: platforms.value.filter(p => p.is_active !== false).length,
      total_shares: platforms.value.reduce((sum, p) => sum + (p.total_shares || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load platforms:', error)
    showError('Failed to load platforms: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const savePlatform = async () => {
  saving.value = true
  try {
    const data = { ...platformForm.value }
    
    if (editingPlatform.value) {
      await blogPagesAPI.updateSocialPlatform(editingPlatform.value.id, data)
      showSuccess('Social platform updated successfully')
    } else {
      await blogPagesAPI.createSocialPlatform(data)
      showSuccess('Social platform created successfully')
    }
    
    closeModal()
    await loadPlatforms()
  } catch (error) {
    console.error('Failed to save platform:', error)
    showError('Failed to save platform: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editPlatform = (platform) => {
  editingPlatform.value = platform
  platformForm.value = {
    platform_name: platform.platform_name || '',
    display_name: platform.display_name || '',
    share_url_template: platform.share_url_template || '',
    icon_url: platform.icon_url || '',
    is_active: platform.is_active !== undefined ? platform.is_active : true,
  }
  showCreateModal.value = true
}

const viewPlatform = (platform) => {
  alert(`Platform: ${platform.display_name || platform.platform_name}\nShares: ${platform.total_shares || 0}\nStatus: ${platform.is_active !== false ? 'Active' : 'Inactive'}`)
}

const deletePlatform = async (platform) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${platform.display_name || platform.platform_name}"?`,
    'Delete Social Platform',
    {
      details: 'This action cannot be undone. The social platform configuration will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteSocialPlatform(platform.id)
    showSuccess('Social platform deleted successfully')
    await loadPlatforms()
  } catch (error) {
    console.error('Failed to delete platform:', error)
    showError('Failed to delete platform: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingPlatform.value = null
  platformForm.value = {
    platform_name: '',
    display_name: '',
    share_url_template: '',
    icon_url: '',
    is_active: true,
  }
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

onMounted(() => {
  loadPlatforms()
})
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
</style>
