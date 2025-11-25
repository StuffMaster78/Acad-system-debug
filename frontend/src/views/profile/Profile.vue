<template>
  <div class="space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Profile</h1>

    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-3 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Account Status -->
    <div class="card p-4">
      <h2 class="text-lg font-semibold mb-3">Account Status</h2>
      <div class="space-y-2 text-sm">
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Status:</span>
          <span :class="statusBadgeClass" class="px-2 py-1 rounded">{{ accountStatus }}</span>
        </div>
        <div v-if="profile?.is_deleted" class="flex items-center justify-between">
          <span class="text-gray-600">Deletion Request:</span>
          <span class="text-red-600">Pending</span>
        </div>
        <div v-if="profile?.deletion_reason" class="text-xs text-gray-500">
          Reason: {{ profile.deletion_reason }}
        </div>
      </div>
    </div>

    <!-- Profile Information -->
    <div class="card p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Profile Information</h2>
        <button @click="editing = !editing" class="text-primary-600 text-sm">{{ editing ? 'Cancel' : 'Edit' }}</button>
      </div>

      <form v-if="editing" @submit.prevent="updateProfile" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Email</label>
            <input v-model="form.email" type="email" class="w-full border rounded px-3 py-2" disabled />
            <p class="text-xs text-gray-500 mt-1">Email changes require admin approval</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Phone Number</label>
            <input v-model="form.phone_number" type="tel" class="w-full border rounded px-3 py-2" />
            <p class="text-xs text-gray-500 mt-1">Phone changes require admin approval</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Country</label>
            <input v-model="form.country" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">State/Province</label>
            <input v-model="form.state" type="text" class="w-full border rounded px-3 py-2" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Bio</label>
          <textarea v-model="form.bio" rows="3" class="w-full border rounded px-3 py-2"></textarea>
        </div>
        <div class="flex gap-3">
          <button :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded disabled:opacity-50">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
          <button type="button" @click="editing = false" class="px-4 py-2 bg-gray-100 rounded">Cancel</button>
        </div>
      </form>

      <div v-else class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-600">Email</label>
            <p class="mt-1 text-gray-900">{{ profile?.user?.email || authStore.user?.email || '—' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Phone Number</label>
            <p class="mt-1 text-gray-900">{{ profile?.phone_number || '—' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Country</label>
            <p class="mt-1 text-gray-900">{{ profile?.country || '—' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">State/Province</label>
            <p class="mt-1 text-gray-900">{{ profile?.state || '—' }}</p>
          </div>
        </div>
        <div v-if="profile?.bio">
          <label class="block text-sm font-medium text-gray-600">Bio</label>
          <SafeHtml 
            :content="profile.bio"
            container-class="mt-1 text-gray-900"
          />
        </div>
      </div>
    </div>

    <!-- Client-specific fields -->
    <div v-if="authStore.isClient" class="card p-4">
      <h2 class="text-lg font-semibold mb-3">Client Information</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <label class="block text-sm font-medium text-gray-600">Registration ID</label>
          <p class="mt-1 text-gray-900">{{ profile?.registration_id || '—' }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600">Loyalty Points</label>
          <p class="mt-1 text-gray-900">{{ profile?.loyalty_points || 0 }}</p>
        </div>
      </div>
    </div>

    <!-- Pending Update Requests -->
    <div v-if="updateRequests.length" class="card p-4">
      <h2 class="text-lg font-semibold mb-3">Pending Update Requests</h2>
      <div class="space-y-2">
        <div v-for="req in updateRequests" :key="req.id" class="p-3 bg-yellow-50 rounded border border-yellow-200">
          <div class="text-sm font-medium">Request #{{ req.id }}</div>
          <div class="text-xs text-gray-600">Status: {{ req.status }}</div>
          <div class="text-xs text-gray-500 mt-1">Requested changes require admin approval</div>
        </div>
      </div>
    </div>

    <!-- Account Deletion -->
    <div class="card p-4 border-red-200">
      <h2 class="text-lg font-semibold mb-3 text-red-700">Danger Zone</h2>
      <div v-if="!showDeletionForm" class="space-y-2">
        <p class="text-sm text-gray-600">Request account deletion. This action requires admin approval.</p>
        <button @click="showDeletionForm = true" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
          Request Account Deletion
        </button>
      </div>
      <form v-else @submit.prevent="requestDeletion" class="space-y-3">
        <div>
          <label class="block text-sm font-medium mb-1">Reason for Deletion *</label>
          <textarea v-model="deletionReason" rows="3" required class="w-full border rounded px-3 py-2"></textarea>
        </div>
        <div class="flex gap-3">
          <button :disabled="deleting" class="px-4 py-2 bg-red-600 text-white rounded disabled:opacity-50">
            {{ deleting ? 'Submitting...' : 'Submit Deletion Request' }}
          </button>
          <button type="button" @click="showDeletionForm = false; deletionReason = ''" class="px-4 py-2 bg-gray-100 rounded">
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import usersAPI from '@/api/users'
import SafeHtml from '@/components/common/SafeHtml.vue'

const authStore = useAuthStore()

const profile = ref(null)
const loading = ref(true)
const editing = ref(false)
const saving = ref(false)
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const form = ref({
  email: '',
  phone_number: '',
  country: '',
  state: '',
  bio: '',
})

const updateRequests = ref([])
const showDeletionForm = ref(false)
const deletionReason = ref('')
const deleting = ref(false)

const accountStatus = computed(() => {
  if (profile.value?.is_deleted) return 'Pending Deletion'
  if (!authStore.user?.is_active) return 'Inactive'
  return 'Active'
})

const statusBadgeClass = computed(() => {
  if (profile.value?.is_deleted) return 'bg-red-100 text-red-700'
  if (!authStore.user?.is_active) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
})

const loadProfile = async () => {
  loading.value = true
  try {
    const res = await usersAPI.getProfile()
    profile.value = res.data
    form.value = {
      email: profile.value.user?.email || authStore.user?.email || '',
      phone_number: profile.value.phone_number || '',
      country: profile.value.country || '',
      state: profile.value.state || '',
      bio: profile.value.bio || '',
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

const loadUpdateRequests = async () => {
  try {
    const res = await usersAPI.getUpdateRequests()
    updateRequests.value = res.data?.pending_requests || []
  } catch (e) {
    // silent
  }
}

const updateProfile = async () => {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await usersAPI.updateProfile(form.value)
    message.value = 'Profile updated. Some changes may require admin approval.'
    messageSuccess.value = true
    editing.value = false
    await loadProfile()
    await loadUpdateRequests()
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to update profile'
  } finally {
    saving.value = false
  }
}

const requestDeletion = async () => {
  deleting.value = true
  error.value = ''
  message.value = ''
  try {
    await usersAPI.requestDeletion(authStore.user.id, deletionReason.value)
    message.value = 'Deletion request submitted. Admin approval required.'
    messageSuccess.value = true
    showDeletionForm.value = false
    deletionReason.value = ''
    await loadProfile()
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Failed to submit deletion request'
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await loadProfile()
  await loadUpdateRequests()
})
</script>
