<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Blog Authors</h1>
        <p class="text-sm text-gray-600 mt-1">
          Manage author bios, expertise, and social profiles per website.
        </p>
      </div>
      <button
        @click="openCreate"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
      >
        New Author
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex flex-wrap gap-4 items-end">
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Website</label>
        <select
          v-model="filters.website_id"
          @change="loadAuthors"
          class="border rounded px-3 py-2 text-sm"
        >
          <option value="">All websites</option>
          <option v-for="site in websites" :key="site.id" :value="site.id">
            {{ site.name }}
          </option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-700 mb-1">Status</label>
        <select
          v-model="filters.status"
          @change="loadAuthors"
          class="border rounded px-3 py-2 text-sm"
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="all">All</option>
        </select>
      </div>
      <div class="flex-1 min-w-[180px]">
        <label class="block text-xs font-medium text-gray-700 mb-1">Search</label>
        <input
          v-model="filters.search"
          @input="debouncedSearch"
          type="text"
          placeholder="Name, designation, expertise..."
          class="w-full border rounded px-3 py-2 text-sm"
        />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-10 text-gray-500">
        Loading authors…
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Author</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fake?</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active</th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order</th>
            <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="author in authors" :key="author.id">
            <td class="px-4 py-3 text-sm">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center text-xs font-semibold text-gray-700"
                >
                  {{ author.name ? author.name.slice(0, 2).toUpperCase() : '??' }}
                </div>
                <div>
                  <div class="font-medium text-gray-900">{{ author.name || 'Unnamed' }}</div>
                  <div v-if="author.expertise" class="text-xs text-gray-500">
                    {{ author.expertise }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ author.website_name || author.website }}
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ author.designation || '—' }}
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                :class="author.is_fake ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ author.is_fake ? 'Fake' : 'Real' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                :class="author.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
              >
                {{ author.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">
              {{ author.display_order }}
            </td>
            <td class="px-4 py-3 text-sm text-right">
              <button
                @click="openEdit(author)"
                class="text-primary-600 hover:text-primary-800 mr-3"
              >
                Edit
              </button>
              <button
                @click="toggleActive(author)"
                class="text-gray-500 hover:text-gray-700"
              >
                {{ author.is_active ? 'Disable' : 'Enable' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && authors.length === 0" class="py-10 text-center text-gray-500 text-sm">
        No authors found for the current filters.
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingAuthor ? 'Edit Author' : 'Create Author' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="saveAuthor" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <select
                  v-model="authorForm.website"
                  required
                  :disabled="!canSelectWebsite"
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Select Website</option>
                  <option v-for="site in availableWebsites" :key="site.id" :value="site.id">
                    {{ site.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Name *</label>
                <input v-model="authorForm.name" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Designation</label>
                <input v-model="authorForm.designation" type="text" class="w-full border rounded px-3 py-2" placeholder="e.g., Senior Writer" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Expertise</label>
                <input v-model="authorForm.expertise" type="text" class="w-full border rounded px-3 py-2" placeholder="e.g., SEO, Content Writing" />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Bio</label>
              <textarea v-model="authorForm.bio" rows="4" class="w-full border rounded px-3 py-2" placeholder="Author biography..."></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Contact Email</label>
                <input v-model="authorForm.contact_email" type="email" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Display Order</label>
                <input v-model.number="authorForm.display_order" type="number" class="w-full border rounded px-3 py-2" />
              </div>
            </div>

            <!-- Social Links -->
            <div class="border-t pt-4">
              <h3 class="text-lg font-semibold mb-3">Social Links</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium mb-1">Twitter Handle</label>
                  <input v-model="authorForm.twitter_handle" type="text" class="w-full border rounded px-3 py-2" placeholder="@username" />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">LinkedIn Profile</label>
                  <input v-model="authorForm.linkedin_profile" type="url" class="w-full border rounded px-3 py-2" placeholder="https://linkedin.com/in/..." />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">Personal Website</label>
                  <input v-model="authorForm.personal_website" type="url" class="w-full border rounded px-3 py-2" placeholder="https://..." />
                </div>
                <div>
                  <label class="block text-sm font-medium mb-1">Facebook Profile</label>
                  <input v-model="authorForm.facebook_profile" type="url" class="w-full border rounded px-3 py-2" placeholder="https://facebook.com/..." />
                </div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Profile Picture</label>
                <input
                  ref="profilePictureInput"
                  type="file"
                  accept="image/*"
                  @change="handleProfilePictureSelect"
                  class="w-full border rounded px-3 py-2"
                />
                <div v-if="authorForm.profile_picture || profilePicturePreview" class="mt-2">
                  <img
                    :src="profilePicturePreview || authorForm.profile_picture"
                    alt="Profile preview"
                    class="w-32 h-32 object-cover rounded border"
                  />
                </div>
              </div>
              <div class="space-y-3">
                <label class="flex items-center">
                  <input v-model="authorForm.is_active" type="checkbox" class="mr-2" />
                  <span class="text-sm">Active</span>
                </label>
                <label class="flex items-center">
                  <input v-model="authorForm.is_fake" type="checkbox" class="mr-2" />
                  <span class="text-sm">Fake/Persona Author</span>
                </label>
              </div>
            </div>

            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingAuthor ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { blogAuthorsAPI, websitesAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const authors = ref([])
const websites = ref([])
const availableWebsites = ref([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const editingAuthor = ref(null)
const profilePictureInput = ref(null)
const profilePicturePreview = ref(null)

const filters = ref({
  website_id: '',
  status: 'active',
  search: '',
})

const authorForm = ref({
  website: null,
  name: '',
  bio: '',
  designation: '',
  expertise: '',
  contact_email: '',
  twitter_handle: '',
  linkedin_profile: '',
  personal_website: '',
  facebook_profile: '',
  profile_picture: null,
  is_active: true,
  is_fake: false,
  display_order: 0,
})

const message = ref('')
const messageSuccess = ref(false)

const canSelectWebsite = computed(() => {
  return authStore.isSuperAdmin || availableWebsites.value.length > 1
})

let searchTimeout = null

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    websites.value = res.data?.results || res.data || []
    availableWebsites.value = websites.value
  } catch (e) {
    console.error('Failed to load websites', e)
  }
}

const loadAuthors = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.website_id) params.website_id = filters.value.website_id
    if (filters.value.status === 'active') params.is_active = 'true'
    if (filters.value.status === 'inactive') params.is_active = 'false'
    if (filters.value.search) params.search = filters.value.search

    const res = await blogAuthorsAPI.list(params)
    // Handle different response formats (with/without pagination)
    if (Array.isArray(res.data)) {
      authors.value = res.data
    } else if (res.data?.results && Array.isArray(res.data.results)) {
      authors.value = res.data.results
    } else if (Array.isArray(res.data?.data)) {
      authors.value = res.data.data
    } else {
      authors.value = []
    }
  } catch (e) {
    console.error('Failed to load authors', e)
    message.value = 'Failed to load authors: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    authors.value = []
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadAuthors, 400)
}

const handleProfilePictureSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      profilePicturePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
    authorForm.value.profile_picture = file
  }
}

const openCreate = () => {
  editingAuthor.value = null
  authorForm.value = {
    website: availableWebsites.value.length === 1 ? availableWebsites.value[0].id : null,
    name: '',
    bio: '',
    designation: '',
    expertise: '',
    contact_email: '',
    twitter_handle: '',
    linkedin_profile: '',
    personal_website: '',
    facebook_profile: '',
    profile_picture: null,
    is_active: true,
    is_fake: false,
    display_order: 0,
  }
  profilePicturePreview.value = null
  showModal.value = true
}

const openEdit = (author) => {
  editingAuthor.value = author
  authorForm.value = {
    website: author.website?.id || author.website || null,
    name: author.name || '',
    bio: author.bio || '',
    designation: author.designation || '',
    expertise: author.expertise || '',
    contact_email: author.contact_email || '',
    twitter_handle: author.twitter_handle || '',
    linkedin_profile: author.linkedin_profile || '',
    personal_website: author.personal_website || '',
    facebook_profile: author.facebook_profile || '',
    profile_picture: author.profile_picture || null,
    is_active: author.is_active !== undefined ? author.is_active : true,
    is_fake: author.is_fake || false,
    display_order: author.display_order || 0,
  }
  profilePicturePreview.value = author.profile_picture || null
  showModal.value = true
}

const saveAuthor = async () => {
  saving.value = true
  message.value = ''
  try {
    const formData = new FormData()
    formData.append('website', authorForm.value.website)
    formData.append('name', authorForm.value.name)
    if (authorForm.value.bio) formData.append('bio', authorForm.value.bio)
    if (authorForm.value.designation) formData.append('designation', authorForm.value.designation)
    if (authorForm.value.expertise) formData.append('expertise', authorForm.value.expertise)
    if (authorForm.value.contact_email) formData.append('contact_email', authorForm.value.contact_email)
    if (authorForm.value.twitter_handle) formData.append('twitter_handle', authorForm.value.twitter_handle)
    if (authorForm.value.linkedin_profile) formData.append('linkedin_profile', authorForm.value.linkedin_profile)
    if (authorForm.value.personal_website) formData.append('personal_website', authorForm.value.personal_website)
    if (authorForm.value.facebook_profile) formData.append('facebook_profile', authorForm.value.facebook_profile)
    formData.append('is_active', authorForm.value.is_active)
    formData.append('is_fake', authorForm.value.is_fake)
    formData.append('display_order', authorForm.value.display_order)
    
    if (authorForm.value.profile_picture && authorForm.value.profile_picture instanceof File) {
      formData.append('profile_picture', authorForm.value.profile_picture)
    }

    if (editingAuthor.value) {
      await blogAuthorsAPI.update(editingAuthor.value.id, formData)
      message.value = 'Author updated successfully'
    } else {
      await blogAuthorsAPI.create(formData)
      message.value = 'Author created successfully'
    }
    messageSuccess.value = true
    closeModal()
    await loadAuthors()
  } catch (e) {
    message.value = 'Failed to save author: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data) || e.message)
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingAuthor.value = null
  profilePicturePreview.value = null
  if (profilePictureInput.value) {
    profilePictureInput.value.value = ''
  }
}

const toggleActive = async (author) => {
  try {
    await blogAuthorsAPI.update(author.id, { is_active: !author.is_active })
    await loadAuthors()
  } catch (e) {
    console.error('Failed to toggle active', e)
    message.value = 'Failed to toggle active status: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

onMounted(async () => {
  await loadWebsites()
  await loadAuthors()
})
</script>


