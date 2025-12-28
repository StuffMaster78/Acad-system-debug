<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Author Schema Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage structured data (Schema.org) for blog authors</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Author Schema
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Schemas</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active Authors</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">With Images</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.with_images }}</p>
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
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Author</label>
          <input
            v-model="filters.author"
            type="number"
            placeholder="Filter by Author ID..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @input="loadSchemas"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Schemas List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!schemas.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No author schemas found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Schema</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Author</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Image</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Social Links</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="schema in schemas" :key="schema.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ schema.author?.username || schema.author?.email || schema.author_id || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ schema.name || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="schema.image" class="text-green-600 dark:text-green-400">✓</span>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ getSocialLinksCount(schema) }} links
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(schema.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewSchema(schema)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editSchema(schema)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteSchema(schema)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingSchema" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingSchema ? 'Edit Author Schema' : 'Create Author Schema' }}
          </h3>
        </div>
        <form @submit.prevent="saveSchema" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Author ID *</label>
            <input
              v-model.number="schemaForm.author"
              type="number"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
            <input
              v-model="schemaForm.name"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
            <textarea
              v-model="schemaForm.description"
              rows="3"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Image URL</label>
            <input
              v-model="schemaForm.image"
              type="url"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Twitter Handle</label>
              <input
                v-model="schemaForm.twitter_handle"
                type="text"
                placeholder="@username"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">LinkedIn URL</label>
              <input
                v-model="schemaForm.linkedin_url"
                type="url"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingSchema ? 'Update' : 'Create') }}
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
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'

const { showSuccess, showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const schemas = ref([])
const stats = ref({ total: 0, active: 0, with_images: 0 })
const showCreateModal = ref(false)
const editingSchema = ref(null)

const filters = ref({
  search: '',
  author: '',
})

const schemaForm = ref({
  author: null,
  name: '',
  description: '',
  image: '',
  twitter_handle: '',
  linkedin_url: '',
})

const debouncedSearch = debounce(() => {
  loadSchemas()
}, 300)

const loadSchemas = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.author) params.author = filters.value.author
    
    // Note: API method might need to be added
    const res = await blogPagesAPI.listAuthorSchemas(params)
    schemas.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: schemas.value.length,
      active: schemas.value.filter(s => s.author).length,
      with_images: schemas.value.filter(s => s.image).length,
    }
  } catch (error) {
    console.error('Failed to load schemas:', error)
    showError('Failed to load schemas: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveSchema = async () => {
  saving.value = true
  try {
    const data = { ...schemaForm.value }
    
    if (editingSchema.value) {
      await blogPagesAPI.updateAuthorSchema(editingSchema.value.id, data)
      showSuccess('Author schema updated successfully')
    } else {
      await blogPagesAPI.createAuthorSchema(data)
      showSuccess('Author schema created successfully')
    }
    
    closeModal()
    await loadSchemas()
  } catch (error) {
    console.error('Failed to save schema:', error)
    showError('Failed to save schema: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editSchema = (schema) => {
  editingSchema.value = schema
  schemaForm.value = {
    author: schema.author?.id || schema.author_id || null,
    name: schema.name || '',
    description: schema.description || '',
    image: schema.image || '',
    twitter_handle: schema.twitter_handle || '',
    linkedin_url: schema.linkedin_url || '',
  }
  showCreateModal.value = true
}

const viewSchema = (schema) => {
  // Show schema details
  alert(`Author Schema: ${schema.name}\nAuthor: ${schema.author?.username || schema.author_id}\nImage: ${schema.image ? 'Yes' : 'No'}`)
}

const deleteSchema = async (schema) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this author schema?',
    'Delete Author Schema',
    {
      details: 'This action cannot be undone. The author schema will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteAuthorSchema(schema.id)
    showSuccess('Author schema deleted successfully')
    await loadSchemas()
  } catch (error) {
    console.error('Failed to delete schema:', error)
    showError('Failed to delete schema: ' + (error.response?.data?.detail || error.message))
  }
}

const getSocialLinksCount = (schema) => {
  let count = 0
  if (schema.twitter_handle) count++
  if (schema.linkedin_url) count++
  if (schema.facebook_url) count++
  if (schema.website_url) count++
  return count
}

const closeModal = () => {
  showCreateModal.value = false
  editingSchema.value = null
  schemaForm.value = {
    author: null,
    name: '',
    description: '',
    image: '',
    twitter_handle: '',
    linkedin_url: '',
  }
}

const resetFilters = () => {
  filters.value = { search: '', author: '' }
  loadSchemas()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadSchemas()
})
</script>

<style scoped>
@reference "tailwindcss";
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


