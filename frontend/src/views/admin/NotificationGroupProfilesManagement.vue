<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Notification Group Profiles</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage notification preferences for user groups</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Add Profile
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Profiles</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ profiles.length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Default Profiles</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ profiles.filter(p => p.is_default).length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique Groups</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueGroups.length }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Total Users</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ totalUsers }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name or role..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="groupFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadProfiles"
        >
          <option value="">All Groups</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name || group.event_key || `Group #${group.id}` }}
          </option>
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
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Group</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Role</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Users</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="profile in filteredProfiles"
              :key="profile.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ profile.name || 'Unnamed Profile' }}
                </div>
                <div v-if="profile.role_slug" class="text-xs text-gray-500 dark:text-gray-400">
                  {{ profile.role_slug }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.group_name || profile.group || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.roles || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      profile.is_default ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ profile.is_default ? 'Default' : 'Standard' }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ profile.users_count || (Array.isArray(profile.users) ? profile.users.length : 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="editProfile(profile)"
                  class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                >
                  Edit
                </button>
                <button
                  v-if="!profile.is_default"
                  @click="setAsDefault(profile)"
                  class="text-yellow-600 hover:text-yellow-900 dark:text-yellow-400 dark:hover:text-yellow-300 mr-4"
                >
                  Set Default
                </button>
                <button
                  @click="deleteProfile(profile)"
                  class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="filteredProfiles.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No profiles found
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingProfile ? 'Edit Notification Group Profile' : 'Add Notification Group Profile'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="form.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Profile name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Group *</label>
          <select
            v-model.number="form.group"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="">Select Group</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name || group.event_key || `Group #${group.id}` }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role Slug</label>
          <input
            v-model="form.role_slug"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="e.g., client, writer, admin"
          />
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_default"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Set as Default</span>
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
          @click="saveProfile"
          :disabled="saving"
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
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import notificationGroupsAPI from '@/api/notification-groups'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const profiles = ref([])
const groups = ref([])
const searchQuery = ref('')
const groupFilter = ref('')
const showModal = ref(false)
const editingProfile = ref(null)
const formError = ref('')

const form = ref({
  name: '',
  group: null,
  role_slug: '',
  is_default: false,
})

const filteredProfiles = computed(() => {
  let filtered = profiles.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      (p.name && p.name.toLowerCase().includes(query)) ||
      (p.role_slug && p.role_slug.toLowerCase().includes(query))
    )
  }
  
  if (groupFilter.value) {
    filtered = filtered.filter(p => 
      (p.group && p.group == groupFilter.value) ||
      (p.group_id && p.group_id == groupFilter.value)
    )
  }
  
  return filtered
})

const uniqueGroups = computed(() => {
  return [...new Set(profiles.value.map(p => p.group || p.group_id).filter(Boolean))]
})

const totalUsers = computed(() => {
  return profiles.value.reduce((sum, p) => {
    return sum + (p.users_count || (Array.isArray(p.users) ? p.users.length : 0))
  }, 0)
})

const debouncedSearch = debounce(() => {
  loadProfiles()
}, 300)

const loadProfiles = async () => {
  loading.value = true
  try {
    const [profilesResponse, groupsResponse] = await Promise.all([
      notificationGroupsAPI.listGroupProfiles(),
      notificationGroupsAPI.listGroups(),
    ])
    
    profiles.value = profilesResponse.data.results || profilesResponse.data || []
    groups.value = groupsResponse.data.results || groupsResponse.data || []
  } catch (error) {
    showError('Failed to load notification group profiles')
    console.error('Error loading profiles:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingProfile.value = null
  form.value = {
    name: '',
    group: null,
    role_slug: '',
    is_default: false,
  }
  formError.value = ''
  showModal.value = true
}

const editProfile = (profile) => {
  editingProfile.value = profile
  form.value = {
    name: profile.name || '',
    group: profile.group || profile.group_id || null,
    role_slug: profile.role_slug || '',
    is_default: profile.is_default || false,
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
  saving.value = true
  formError.value = ''
  
  try {
    if (editingProfile.value) {
      await notificationGroupsAPI.updateGroupProfile(editingProfile.value.id, form.value)
      showSuccess('Profile updated successfully')
    } else {
      await notificationGroupsAPI.createGroupProfile(form.value)
      showSuccess('Profile created successfully')
    }
    
    if (form.value.is_default && editingProfile.value) {
      await notificationGroupsAPI.setDefaultGroupProfile(editingProfile.value.id)
    }
    
    closeModal()
    loadProfiles()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save profile'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const setAsDefault = async (profile) => {
  try {
    await notificationGroupsAPI.setDefaultGroupProfile(profile.id)
    showSuccess('Profile set as default successfully')
    loadProfiles()
  } catch (error) {
    showError('Failed to set default profile')
  }
}

const deleteProfile = (profile) => {
  confirm.showDestructive(
    'Delete Profile',
    `Are you sure you want to delete "${profile.name}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await notificationGroupsAPI.deleteGroupProfile(profile.id)
        showSuccess('Profile deleted successfully')
        loadProfiles()
      } catch (error) {
        showError('Failed to delete profile')
      }
    }
  )
}

onMounted(() => {
  loadProfiles()
})
</script>

