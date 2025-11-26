<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Notification Groups & Profiles</h1>
        <p class="mt-2 text-gray-600">Manage user groups and their notification profiles</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="loadData"
          :disabled="loading"
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'groups'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'groups'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Groups ({{ groups.length }})
        </button>
        <button
          @click="activeTab = 'profiles'"
          :class="[
            'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'profiles'
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Group Profiles ({{ groupProfiles.length }})
        </button>
      </nav>
    </div>

    <!-- Groups Tab -->
    <div v-if="activeTab === 'groups'" class="space-y-6">
      <!-- Create Group Button -->
      <div class="flex justify-end">
        <button
          @click="showGroupModal = true; editingGroup = null"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Create Group
        </button>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex gap-4">
          <input
            v-model="groupSearch"
            type="text"
            placeholder="Search groups..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <select
            v-model="groupWebsiteFilter"
            class="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Groups List -->
      <div v-if="loading && groups.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="filteredGroups.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <p class="text-gray-500 mb-4">No groups found</p>
        <button
          @click="showGroupModal = true; editingGroup = null"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Create First Group
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="group in filteredGroups"
          :key="group.id"
          class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ group.name }}</h3>
              <p class="text-sm text-gray-500">{{ group.website_name || group.website_domain }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-medium rounded',
                group.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
              ]"
            >
              {{ group.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <p v-if="group.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
            {{ group.description }}
          </p>

          <div class="space-y-2 mb-4">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Users:</span>
              <span class="font-medium">{{ group.user_count || 0 }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Channels:</span>
              <span class="font-medium">{{ group.channels || 'N/A' }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600">Default Channel:</span>
              <span class="font-medium">{{ group.default_channel || 'N/A' }}</span>
            </div>
          </div>

          <div class="flex gap-2 pt-4 border-t border-gray-200">
            <button
              @click="editGroup(group)"
              class="flex-1 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            >
              Edit
            </button>
            <button
              @click="viewGroupUsers(group)"
              class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              Users
            </button>
            <button
              @click="deleteGroup(group)"
              class="px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Group Profiles Tab -->
    <div v-if="activeTab === 'profiles'" class="space-y-6">
      <!-- Create Profile Button -->
      <div class="flex justify-end">
        <button
          @click="showProfileModal = true; editingProfile = null"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          + Create Group Profile
        </button>
      </div>

      <!-- Search and Filters -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex gap-4">
          <input
            v-model="profileSearch"
            type="text"
            placeholder="Search profiles..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <select
            v-model="profileWebsiteFilter"
            class="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
          <select
            v-model="profileGroupFilter"
            class="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">All Groups</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Profiles List -->
      <div v-if="loading && groupProfiles.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="filteredProfiles.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
        <p class="text-gray-500 mb-4">No group profiles found</p>
        <button
          @click="showProfileModal = true; editingProfile = null"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Create First Profile
        </button>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="profile in filteredProfiles"
          :key="profile.id"
          class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="text-lg font-semibold text-gray-900">{{ profile.name }}</h3>
                <span
                  v-if="profile.is_default"
                  class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded"
                >
                  Default
                </span>
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded',
                    profile.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ profile.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <p class="text-sm text-gray-500">
                {{ profile.website_name || profile.website_domain }} • {{ profile.group_name }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <span class="text-xs text-gray-500">Email</span>
              <p :class="['text-sm font-medium', profile.receive_email ? 'text-green-600' : 'text-gray-400']">
                {{ profile.receive_email ? '✓ Enabled' : '✗ Disabled' }}
              </p>
            </div>
            <div>
              <span class="text-xs text-gray-500">In-App</span>
              <p :class="['text-sm font-medium', profile.receive_in_app ? 'text-green-600' : 'text-gray-400']">
                {{ profile.receive_in_app ? '✓ Enabled' : '✗ Disabled' }}
              </p>
            </div>
            <div>
              <span class="text-xs text-gray-500">Push</span>
              <p :class="['text-sm font-medium', profile.receive_push ? 'text-green-600' : 'text-gray-400']">
                {{ profile.receive_push ? '✓ Enabled' : '✗ Disabled' }}
              </p>
            </div>
            <div>
              <span class="text-xs text-gray-500">SMS</span>
              <p :class="['text-sm font-medium', profile.receive_sms ? 'text-green-600' : 'text-gray-400']">
                {{ profile.receive_sms ? '✓ Enabled' : '✗ Disabled' }}
              </p>
            </div>
          </div>

          <div class="flex items-center justify-between text-sm mb-4">
            <div>
              <span class="text-gray-600">Users:</span>
              <span class="font-medium ml-2">{{ profile.user_count || 0 }}</span>
            </div>
            <div>
              <span class="text-gray-600">Role:</span>
              <span class="font-medium ml-2">{{ profile.roles || profile.role_slug || 'N/A' }}</span>
            </div>
          </div>

          <div class="flex gap-2 pt-4 border-t border-gray-200">
            <button
              @click="editProfile(profile)"
              class="flex-1 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            >
              Edit
            </button>
            <button
              v-if="!profile.is_default"
              @click="setDefaultProfile(profile)"
              class="px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              Set Default
            </button>
            <button
              @click="viewProfileUsers(profile)"
              class="px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
            >
              Users
            </button>
            <button
              @click="deleteProfile(profile)"
              class="px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Group Modal -->
    <div
      v-if="showGroupModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showGroupModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingGroup ? 'Edit Group' : 'Create Group' }}
            </h2>
            <button
              @click="showGroupModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="saveGroup" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                v-model="groupForm.name"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Group name"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                v-model="groupForm.description"
                rows="3"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Group description"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website *</label>
              <select
                v-model="groupForm.website"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Select website</option>
                <option v-for="website in websites" :key="website.id" :value="website.id">
                  {{ website.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Channels *</label>
              <input
                v-model="groupForm.channels"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., email,in_app,push"
              />
              <p class="text-xs text-gray-500 mt-1">Comma-separated list: email, in_app, push, sms</p>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Default Channel</label>
                <select
                  v-model="groupForm.default_channel"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="in_app">In-App</option>
                  <option value="email">Email</option>
                  <option value="push">Push</option>
                  <option value="sms">SMS</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Default Priority</label>
                <select
                  v-model="groupForm.default_priority"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <label class="flex items-center">
                <input
                  v-model="groupForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Active</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="groupForm.is_enabled_by_default"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Enabled by Default</span>
              </label>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                @click="showGroupModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Profile Modal -->
    <div
      v-if="showProfileModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showProfileModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-900">
              {{ editingProfile ? 'Edit Group Profile' : 'Create Group Profile' }}
            </h2>
            <button
              @click="showProfileModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="saveProfile" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                v-model="profileForm.name"
                type="text"
                required
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Profile name"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Website *</label>
                <select
                  v-model="profileForm.website"
                  required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select website</option>
                  <option v-for="website in websites" :key="website.id" :value="website.id">
                    {{ website.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Group *</label>
                <select
                  v-model="profileForm.group"
                  required
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select group</option>
                  <option v-for="group in groups" :key="group.id" :value="group.id">
                    {{ group.name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Profile</label>
                <select
                  v-model="profileForm.profile"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select profile (optional)</option>
                  <!-- Profiles would be loaded from notification profiles API -->
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  v-model="profileForm.roles"
                  class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">All Roles</option>
                  <option value="client">Client</option>
                  <option value="writer">Writer</option>
                  <option value="editor">Editor</option>
                  <option value="admin">Admin</option>
                  <option value="support">Support</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Role Slug</label>
              <input
                v-model="profileForm.role_slug"
                type="text"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., writer"
              />
            </div>

            <div class="border-t border-gray-200 pt-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">Delivery Channels</h3>
              <div class="grid grid-cols-2 gap-4">
                <label class="flex items-center">
                  <input
                    v-model="profileForm.receive_email"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Email</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="profileForm.receive_in_app"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">In-App</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="profileForm.receive_push"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">Push</span>
                </label>
                <label class="flex items-center">
                  <input
                    v-model="profileForm.receive_sms"
                    type="checkbox"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="ml-2 text-sm text-gray-700">SMS</span>
                </label>
              </div>
            </div>

            <div class="flex items-center gap-4 pt-4 border-t border-gray-200">
              <label class="flex items-center">
                <input
                  v-model="profileForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Active</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="profileForm.is_default"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="ml-2 text-sm text-gray-700">Default Profile</span>
              </label>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                @click="showProfileModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import notificationGroupsAPI from '@/api/notification-groups'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { success: showSuccess, error: showError } = useToast()

const activeTab = ref('groups')
const loading = ref(false)
const saving = ref(false)
const groups = ref([])
const groupProfiles = ref([])
const websites = ref([])

// Filters
const groupSearch = ref('')
const groupWebsiteFilter = ref('')
const profileSearch = ref('')
const profileWebsiteFilter = ref('')
const profileGroupFilter = ref('')

// Modals
const showGroupModal = ref(false)
const showProfileModal = ref(false)
const editingGroup = ref(null)
const editingProfile = ref(null)

// Forms
const groupForm = ref({
  name: '',
  description: '',
  website: '',
  channels: 'email,in_app',
  default_channel: 'in_app',
  default_priority: 'normal',
  is_active: true,
  is_enabled_by_default: true,
})

const profileForm = ref({
  name: '',
  website: '',
  group: '',
  profile: '',
  roles: '',
  role_slug: '',
  receive_email: true,
  receive_in_app: true,
  receive_push: false,
  receive_sms: false,
  is_active: true,
  is_default: false,
})

const filteredGroups = computed(() => {
  let filtered = groups.value

  if (groupSearch.value) {
    const search = groupSearch.value.toLowerCase()
    filtered = filtered.filter(g =>
      g.name.toLowerCase().includes(search) ||
      (g.description && g.description.toLowerCase().includes(search))
    )
  }

  if (groupWebsiteFilter.value) {
    filtered = filtered.filter(g => g.website == groupWebsiteFilter.value)
  }

  return filtered
})

const filteredProfiles = computed(() => {
  let filtered = groupProfiles.value

  if (profileSearch.value) {
    const search = profileSearch.value.toLowerCase()
    filtered = filtered.filter(p =>
      p.name.toLowerCase().includes(search) ||
      (p.role_slug && p.role_slug.toLowerCase().includes(search))
    )
  }

  if (profileWebsiteFilter.value) {
    filtered = filtered.filter(p => p.website == profileWebsiteFilter.value)
  }

  if (profileGroupFilter.value) {
    filtered = filtered.filter(p => p.group == profileGroupFilter.value)
  }

  return filtered
})

const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadGroups(),
      loadGroupProfiles(),
      loadWebsites()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
    showError(getErrorMessage(error, 'Failed to load data'))
  } finally {
    loading.value = false
  }
}

const loadGroups = async () => {
  try {
    const response = await notificationGroupsAPI.listGroups()
    groups.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load groups:', error)
    groups.value = []
  }
}

const loadGroupProfiles = async () => {
  try {
    const response = await notificationGroupsAPI.listGroupProfiles()
    groupProfiles.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load group profiles:', error)
    groupProfiles.value = []
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
    websites.value = []
  }
}

const editGroup = (group) => {
  editingGroup.value = group
  groupForm.value = {
    name: group.name,
    description: group.description || '',
    website: group.website,
    channels: group.channels || 'email,in_app',
    default_channel: group.default_channel || 'in_app',
    default_priority: group.default_priority || 'normal',
    is_active: group.is_active !== false,
    is_enabled_by_default: group.is_enabled_by_default !== false,
  }
  showGroupModal.value = true
}

const saveGroup = async () => {
  saving.value = true
  try {
    if (editingGroup.value) {
      await notificationGroupsAPI.updateGroup(editingGroup.value.id, groupForm.value)
      showSuccess('Group updated successfully')
    } else {
      await notificationGroupsAPI.createGroup(groupForm.value)
      showSuccess('Group created successfully')
    }
    showGroupModal.value = false
    editingGroup.value = null
    resetGroupForm()
    await loadGroups()
  } catch (error) {
    console.error('Failed to save group:', error)
    showError(getErrorMessage(error, 'Failed to save group'))
  } finally {
    saving.value = false
  }
}

const deleteGroup = async (group) => {
  if (!confirm(`Are you sure you want to delete "${group.name}"?`)) {
    return
  }

  try {
    await notificationGroupsAPI.deleteGroup(group.id)
    showSuccess('Group deleted successfully')
    await loadGroups()
  } catch (error) {
    console.error('Failed to delete group:', error)
    showError(getErrorMessage(error, 'Failed to delete group'))
  }
}

const viewGroupUsers = (group) => {
  // TODO: Implement user management modal
  alert(`View users for group: ${group.name}`)
}

const editProfile = (profile) => {
  editingProfile.value = profile
  profileForm.value = {
    name: profile.name,
    website: profile.website,
    group: profile.group,
    profile: profile.profile || '',
    roles: profile.roles || '',
    role_slug: profile.role_slug || '',
    receive_email: profile.receive_email !== false,
    receive_in_app: profile.receive_in_app !== false,
    receive_push: profile.receive_push || false,
    receive_sms: profile.receive_sms || false,
    is_active: profile.is_active !== false,
    is_default: profile.is_default || false,
  }
  showProfileModal.value = true
}

const saveProfile = async () => {
  saving.value = true
  try {
    if (editingProfile.value) {
      await notificationGroupsAPI.updateGroupProfile(editingProfile.value.id, profileForm.value)
      showSuccess('Group profile updated successfully')
    } else {
      await notificationGroupsAPI.createGroupProfile(profileForm.value)
      showSuccess('Group profile created successfully')
    }
    showProfileModal.value = false
    editingProfile.value = null
    resetProfileForm()
    await loadGroupProfiles()
  } catch (error) {
    console.error('Failed to save profile:', error)
    showError(getErrorMessage(error, 'Failed to save profile'))
  } finally {
    saving.value = false
  }
}

const deleteProfile = async (profile) => {
  if (!confirm(`Are you sure you want to delete "${profile.name}"?`)) {
    return
  }

  try {
    await notificationGroupsAPI.deleteGroupProfile(profile.id)
    showSuccess('Group profile deleted successfully')
    await loadGroupProfiles()
  } catch (error) {
    console.error('Failed to delete profile:', error)
    showError(getErrorMessage(error, 'Failed to delete profile'))
  }
}

const setDefaultProfile = async (profile) => {
  try {
    await notificationGroupsAPI.setDefaultGroupProfile(profile.id)
    showSuccess('Default profile set successfully')
    await loadGroupProfiles()
  } catch (error) {
    console.error('Failed to set default profile:', error)
    showError(getErrorMessage(error, 'Failed to set default profile'))
  }
}

const viewProfileUsers = (profile) => {
  // TODO: Implement user management modal
  alert(`View users for profile: ${profile.name}`)
}

const resetGroupForm = () => {
  groupForm.value = {
    name: '',
    description: '',
    website: '',
    channels: 'email,in_app',
    default_channel: 'in_app',
    default_priority: 'normal',
    is_active: true,
    is_enabled_by_default: true,
  }
}

const resetProfileForm = () => {
  profileForm.value = {
    name: '',
    website: '',
    group: '',
    profile: '',
    roles: '',
    role_slug: '',
    receive_email: true,
    receive_in_app: true,
    receive_push: false,
    receive_sms: false,
    is_active: true,
    is_default: false,
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>

