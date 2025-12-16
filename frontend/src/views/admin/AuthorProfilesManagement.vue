<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Author Profiles Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Create and manage blog author profiles</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Author
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Authors</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Posts</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.total_posts) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Top Author</p>
        <p class="text-sm font-bold text-purple-600 dark:text-purple-400 truncate">{{ stats.top_author || '—' }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search authors..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
          <select
            v-model="filters.website"
            @change="loadAuthors"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Authors List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!authors.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No authors found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Author</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Bio</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Posts</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="author in authors" :key="author.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ author.name || author.user?.username || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ author.email || author.user?.email || '—' }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ author.bio || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(author.post_count || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="author.is_active !== false ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ author.is_active !== false ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewAuthor(author)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editAuthor(author)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteAuthor(author)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingAuthor" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingAuthor ? 'Edit Author Profile' : 'Create Author Profile' }}
          </h3>
        </div>
        <form @submit.prevent="saveAuthor" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">User ID *</label>
            <input
              v-model.number="authorForm.user"
              type="number"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">ID of the user account to link to this author profile</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name</label>
            <input
              v-model="authorForm.name"
              type="text"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Email</label>
            <input
              v-model="authorForm.email"
              type="email"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Bio</label>
            <textarea
              v-model="authorForm.bio"
              rows="4"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Profile Image URL</label>
            <input
              v-model="authorForm.profile_image"
              type="url"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
            <select
              v-model="authorForm.is_active"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingAuthor ? 'Update' : 'Create') }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const authors = ref([])
const websites = ref([])
const stats = ref({ total: 0, active: 0, total_posts: 0, top_author: '' })
const showCreateModal = ref(false)
const editingAuthor = ref(null)

const filters = ref({
  search: '',
  website: '',
})

const authorForm = ref({
  user: null,
  name: '',
  email: '',
  bio: '',
  profile_image: '',
  is_active: true,
})

const debouncedSearch = debounce(() => {
  loadAuthors()
}, 300)

const loadAuthors = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    
    const res = await blogPagesAPI.listAuthors(params)
    authors.value = res.data?.results || res.data || []
    
    // Calculate stats
    const totalPosts = authors.value.reduce((sum, a) => sum + (a.post_count || 0), 0)
    const sortedByPosts = [...authors.value].sort((a, b) => (b.post_count || 0) - (a.post_count || 0))
    const topAuthor = sortedByPosts[0]
    
    stats.value = {
      total: authors.value.length,
      active: authors.value.filter(a => a.is_active !== false).length,
      total_posts: totalPosts,
      top_author: topAuthor ? (topAuthor.name || topAuthor.user?.username) : '—',
    }
  } catch (error) {
    console.error('Failed to load authors:', error)
    showError('Failed to load authors: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    websites.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const saveAuthor = async () => {
  saving.value = true
  try {
    const data = { ...authorForm.value }
    
    if (editingAuthor.value) {
      await blogPagesAPI.updateAuthor(editingAuthor.value.id, data)
      showSuccess('Author profile updated successfully')
    } else {
      await blogPagesAPI.createAuthor(data)
      showSuccess('Author profile created successfully')
    }
    
    closeModal()
    await loadAuthors()
  } catch (error) {
    console.error('Failed to save author:', error)
    showError('Failed to save author: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editAuthor = (author) => {
  editingAuthor.value = author
  authorForm.value = {
    user: author.user?.id || author.user_id || null,
    name: author.name || '',
    email: author.email || '',
    bio: author.bio || '',
    profile_image: author.profile_image || '',
    is_active: author.is_active !== undefined ? author.is_active : true,
  }
  showCreateModal.value = true
}

const viewAuthor = (author) => {
  alert(`Author: ${author.name || author.user?.username}\nEmail: ${author.email || author.user?.email || 'N/A'}\nPosts: ${author.post_count || 0}\nStatus: ${author.is_active !== false ? 'Active' : 'Inactive'}`)
}

const deleteAuthor = async (author) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${author.name || author.user?.username || 'this author'}"?`,
    'Delete Author Profile',
    {
      details: 'This action cannot be undone. The author profile will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteAuthor(author.id)
    showSuccess('Author profile deleted successfully')
    await loadAuthors()
  } catch (error) {
    console.error('Failed to delete author:', error)
    showError('Failed to delete author: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingAuthor.value = null
  authorForm.value = {
    user: null,
    name: '',
    email: '',
    bio: '',
    profile_image: '',
    is_active: true,
  }
}

const resetFilters = () => {
  filters.value = { search: '', website: '' }
  loadAuthors()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

onMounted(async () => {
  await Promise.all([loadAuthors(), loadWebsites()])
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

