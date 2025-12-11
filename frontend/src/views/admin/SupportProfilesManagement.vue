<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Support Profiles Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage support staff profiles, skills, and availability</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Add Support Profile</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Profiles</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_profiles || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Suspended</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.suspended || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Handled</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total_handled || 0 }}</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by name, email, or registration ID..."
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @input="debouncedSearch"
          />
        </div>
        <select
          v-model="statusFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadProfiles"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading profiles...</p>
    </div>

    <!-- Profiles Table -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Registration ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Orders Handled</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Disputes</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tickets</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="profiles.length === 0" class="text-center">
              <td colspan="8" class="px-6 py-12 text-gray-500 dark:text-gray-400">
                No support profiles found
              </td>
            </tr>
            <tr
              v-for="profile in profiles"
              :key="profile.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">{{ profile.name }}</div>
                <div v-if="profile.phone_number" class="text-sm text-gray-500 dark:text-gray-400">{{ profile.phone_number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">{{ profile.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-white">{{ profile.registration_id }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    profile.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    profile.status === 'suspended' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                  ]"
                >
                  {{ profile.status.charAt(0).toUpperCase() + profile.status.slice(1) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.orders_handled || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.disputes_handled || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.tickets_handled || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-2">
                  <button
                    @click="editProfile(profile)"
                    class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
                    title="Edit"
                  >
                    ✏️
                  </button>
                  <button
                    @click="deleteProfile(profile)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingProfile ? 'Edit Support Profile' : 'Create Support Profile'"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Support agent name"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="support@example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Registration ID *</label>
          <input
            v-model="form.registration_id"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="SUP-001"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone Number</label>
          <input
            v-model="form.phone_number"
            type="tel"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="+1234567890"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status *</label>
          <select
            v-model="form.status"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="inactive">Inactive</option>
          </select>
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
          @click="saveProfile"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingProfile ? 'Update' : 'Create') }}
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
const profiles = ref([])
const stats = ref({})
const searchQuery = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const editingProfile = ref(null)
const formError = ref('')

const form = ref({
  name: '',
  email: '',
  registration_id: '',
  phone_number: '',
  status: 'active',
  user: null, // Will be set when creating
  website: null, // Will be set from user's website
})

const canSave = computed(() => {
  return form.value.name.trim() && form.value.email.trim() && form.value.registration_id.trim()
})

const debouncedSearch = debounce(() => {
  loadProfiles()
}, 300)

const loadProfiles = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const response = await supportManagementAPI.listSupportProfiles(params)
    profiles.value = response.data.results || response.data || []
    
    // Calculate stats
    stats.value = {
      total_profiles: profiles.value.length,
      active: profiles.value.filter(p => p.status === 'active').length,
      suspended: profiles.value.filter(p => p.status === 'suspended').length,
      total_handled: profiles.value.reduce((sum, p) => sum + (p.orders_handled || 0) + (p.disputes_handled || 0) + (p.tickets_handled || 0), 0),
    }
  } catch (error) {
    showError('Failed to load support profiles')
    console.error('Error loading profiles:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingProfile.value = null
  form.value = {
    name: '',
    email: '',
    registration_id: '',
    phone_number: '',
    status: 'active',
    user: null,
    website: null,
  }
  formError.value = ''
  showModal.value = true
}

const editProfile = (profile) => {
  editingProfile.value = profile
  form.value = {
    name: profile.name || '',
    email: profile.email || '',
    registration_id: profile.registration_id || '',
    phone_number: profile.phone_number || '',
    status: profile.status || 'active',
    user: profile.user || null,
    website: profile.website || null,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingProfile.value = null
  formError.value = ''
}

const saveProfile = async () => {
  if (!canSave.value) return
  
  saving.value = true
  formError.value = ''
  
  try {
    if (editingProfile.value) {
      await supportManagementAPI.updateSupportProfile(editingProfile.value.id, form.value)
      showSuccess('Support profile updated successfully')
    } else {
      await supportManagementAPI.createSupportProfile(form.value)
      showSuccess('Support profile created successfully')
    }
    closeModal()
    loadProfiles()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save support profile'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteProfile = (profile) => {
  confirm.showDestructive(
    'Delete Support Profile',
    `Are you sure you want to delete the support profile for "${profile.name}"?`,
    `This action cannot be undone. All associated data will be permanently removed.`,
    async () => {
      try {
        await supportManagementAPI.deleteSupportProfile(profile.id)
        showSuccess('Support profile deleted successfully')
        loadProfiles()
      } catch (error) {
        showError('Failed to delete support profile')
        console.error('Error deleting profile:', error)
      }
    }
  )
}

onMounted(() => {
  loadProfiles()
})
</script>

