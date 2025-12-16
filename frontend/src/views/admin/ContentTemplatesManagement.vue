<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Content Templates Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Create and manage reusable content templates for blog posts</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Template
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Templates</p>
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
            placeholder="Search templates..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Category</label>
          <select
            v-model="filters.category"
            @change="loadTemplates"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Templates List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!templates.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No templates found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Template</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Name</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Description</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Category</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Usage</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="template in templates" :key="template.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ template.name || 'Unnamed Template' }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ template.description || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ template.category?.name || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ template.usage_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="template.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ template.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(template.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewTemplate(template)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editTemplate(template)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="applyTemplate(template)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Apply</button>
                  <button @click="deleteTemplate(template)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingTemplate" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingTemplate ? 'Edit Template' : 'Create Template' }}
          </h3>
        </div>
        <form @submit.prevent="saveTemplate" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name *</label>
            <input
              v-model="templateForm.name"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
            <textarea
              v-model="templateForm.description"
              rows="3"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Template Content *</label>
            <textarea
              v-model="templateForm.content"
              rows="15"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-mono text-sm"
              placeholder="Enter template content with placeholders like {{title}}, {{content}}, etc."
            ></textarea>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Use placeholders like {{title}}, {{content}}, {{author}}, etc.</p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Category</label>
              <select
                v-model="templateForm.category"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="">No Category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
              <select
                v-model="templateForm.is_active"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingTemplate ? 'Update' : 'Create') }}
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
const templates = ref([])
const categories = ref([])
const stats = ref({ total: 0, active: 0, total_usage: 0 })
const showCreateModal = ref(false)
const editingTemplate = ref(null)

const filters = ref({
  search: '',
  category: '',
})

const templateForm = ref({
  name: '',
  description: '',
  content: '',
  category: null,
  is_active: true,
})

const debouncedSearch = debounce(() => {
  loadTemplates()
}, 300)

const loadTemplates = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.category) params.category = filters.value.category
    
    const res = await blogPagesAPI.listContentTemplates(params)
    templates.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: templates.value.length,
      active: templates.value.filter(t => t.is_active).length,
      total_usage: templates.value.reduce((sum, t) => sum + (t.usage_count || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load templates:', error)
    showError('Failed to load templates: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await blogPagesAPI.listCategories({})
    categories.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const saveTemplate = async () => {
  saving.value = true
  try {
    const data = { ...templateForm.value }
    if (!data.category) data.category = null
    
    if (editingTemplate.value) {
      await blogPagesAPI.updateContentTemplate(editingTemplate.value.id, data)
      showSuccess('Template updated successfully')
    } else {
      await blogPagesAPI.createContentTemplate(data)
      showSuccess('Template created successfully')
    }
    
    closeModal()
    await loadTemplates()
  } catch (error) {
    console.error('Failed to save template:', error)
    showError('Failed to save template: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name || '',
    description: template.description || '',
    content: template.content || '',
    category: template.category?.id || template.category || null,
    is_active: template.is_active !== undefined ? template.is_active : true,
  }
  showCreateModal.value = true
}

const viewTemplate = (template) => {
  // Show template details
  showSuccess(`Template: ${template.name}\nUsage: ${template.usage_count || 0}\nStatus: ${template.is_active ? 'Active' : 'Inactive'}`)
}

const applyTemplate = async (template) => {
  const blogPostId = prompt('Enter Blog Post ID to apply this template to:')
  if (!blogPostId) return
  
  try {
    await blogPagesAPI.applyTemplate(template.id, { blog_post_id: parseInt(blogPostId) })
    showSuccess('Template applied successfully')
  } catch (error) {
    console.error('Failed to apply template:', error)
    showError('Failed to apply template: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteTemplate = async (template) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${template.name || 'this template'}"?`,
    'Delete Template',
    {
      details: 'This action cannot be undone. The template will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteContentTemplate(template.id)
    showSuccess('Template deleted successfully')
    await loadTemplates()
  } catch (error) {
    console.error('Failed to delete template:', error)
    showError('Failed to delete template: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingTemplate.value = null
  templateForm.value = {
    name: '',
    description: '',
    content: '',
    category: null,
    is_active: true,
  }
}

const resetFilters = () => {
  filters.value = { search: '', category: '' }
  loadTemplates()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  await Promise.all([loadTemplates(), loadCategories()])
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


