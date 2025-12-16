<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Content Snippets Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Create and manage reusable content snippets for quick insertion</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Snippet
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Snippets</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Usage Count</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total_usage }}</p>
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
            placeholder="Search snippets..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Type</label>
          <select
            v-model="filters.snippet_type"
            @change="loadSnippets"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Types</option>
            <option value="text">Text</option>
            <option value="html">HTML</option>
            <option value="markdown">Markdown</option>
            <option value="code">Code</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Snippets List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!snippets.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No snippets found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Snippet</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Content Preview</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Usage</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="snippet in snippets" :key="snippet.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ snippet.name || 'Unnamed Snippet' }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ snippet.shortcode || '—' }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ snippet.content?.substring(0, 100) || '—' }}{{ snippet.content?.length > 100 ? '...' : '' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ snippet.snippet_type || 'text' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ snippet.usage_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="snippet.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ snippet.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(snippet.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewSnippet(snippet)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editSnippet(snippet)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="renderSnippet(snippet)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Render</button>
                  <button @click="deleteSnippet(snippet)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingSnippet" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingSnippet ? 'Edit Snippet' : 'Create Snippet' }}
          </h3>
        </div>
        <form @submit.prevent="saveSnippet" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
            <input
              v-model="snippetForm.name"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Shortcode</label>
            <input
              v-model="snippetForm.shortcode"
              type="text"
              placeholder="e.g., [snippet-name]"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Optional: Shortcode to use in content</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content *</label>
            <textarea
              v-model="snippetForm.content"
              rows="10"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-mono text-sm"
            ></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Type</label>
              <select
                v-model="snippetForm.snippet_type"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="text">Text</option>
                <option value="html">HTML</option>
                <option value="markdown">Markdown</option>
                <option value="code">Code</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
              <select
                v-model="snippetForm.is_active"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingSnippet ? 'Update' : 'Create') }}
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
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const snippets = ref([])
const stats = ref({ total: 0, active: 0, total_usage: 0 })
const showCreateModal = ref(false)
const editingSnippet = ref(null)

const filters = ref({
  search: '',
  snippet_type: '',
})

const snippetForm = ref({
  name: '',
  shortcode: '',
  content: '',
  snippet_type: 'text',
  is_active: true,
})

const debouncedSearch = debounce(() => {
  loadSnippets()
}, 300)

const loadSnippets = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.snippet_type) params.snippet_type = filters.value.snippet_type
    
    const res = await blogPagesAPI.listContentSnippets(params)
    snippets.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: snippets.value.length,
      active: snippets.value.filter(s => s.is_active).length,
      total_usage: snippets.value.reduce((sum, s) => sum + (s.usage_count || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load snippets:', error)
    showError('Failed to load snippets: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveSnippet = async () => {
  saving.value = true
  try {
    const data = { ...snippetForm.value }
    
    if (editingSnippet.value) {
      await blogPagesAPI.updateContentSnippet(editingSnippet.value.id, data)
      showSuccess('Snippet updated successfully')
    } else {
      await blogPagesAPI.createContentSnippet(data)
      showSuccess('Snippet created successfully')
    }
    
    closeModal()
    await loadSnippets()
  } catch (error) {
    console.error('Failed to save snippet:', error)
    showError('Failed to save snippet: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editSnippet = (snippet) => {
  editingSnippet.value = snippet
  snippetForm.value = {
    name: snippet.name || '',
    shortcode: snippet.shortcode || '',
    content: snippet.content || '',
    snippet_type: snippet.snippet_type || 'text',
    is_active: snippet.is_active !== undefined ? snippet.is_active : true,
  }
  showCreateModal.value = true
}

const viewSnippet = (snippet) => {
  // Show snippet preview
  alert(`Snippet: ${snippet.name}\nType: ${snippet.snippet_type}\nUsage: ${snippet.usage_count || 0}`)
}

const renderSnippet = async (snippet) => {
  const context = prompt('Enter context data as JSON (optional):')
  let contextData = {}
  if (context) {
    try {
      contextData = JSON.parse(context)
    } catch (e) {
      showError('Invalid JSON format')
      return
    }
  }
  
  try {
    const res = await blogPagesAPI.renderSnippet(snippet.id, contextData)
    alert(`Rendered Snippet:\n\n${res.data?.rendered_content || res.data?.content || 'No content'}`)
  } catch (error) {
    console.error('Failed to render snippet:', error)
    showError('Failed to render snippet: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteSnippet = async (snippet) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${snippet.name || 'this snippet'}"?`,
    'Delete Snippet',
    {
      details: 'This action cannot be undone. The snippet will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteContentSnippet(snippet.id)
    showSuccess('Snippet deleted successfully')
    await loadSnippets()
  } catch (error) {
    console.error('Failed to delete snippet:', error)
    showError('Failed to delete snippet: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingSnippet.value = null
  snippetForm.value = {
    name: '',
    shortcode: '',
    content: '',
    snippet_type: 'text',
    is_active: true,
  }
}

const resetFilters = () => {
  filters.value = { search: '', snippet_type: '' }
  loadSnippets()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadSnippets()
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


