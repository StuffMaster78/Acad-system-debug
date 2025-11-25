<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">SEO Pages Management</h1>
        <p class="mt-2 text-gray-600">Manage service pages, SEO metadata, FAQs, and resources</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create SEO Page
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by title..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.is_active" @change="loadPages" class="w-full border rounded px-3 py-2">
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Service Pages Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Views</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="page in pages" :key="page.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900">{{ page.title }}</div>
                <div class="text-sm text-gray-500">{{ page.short_description || page.header || '' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="page.website" class="text-sm">
                  <div class="font-medium text-gray-900">{{ page.website.name }}</div>
                  <div class="text-xs text-gray-500">{{ page.website.domain }}</div>
                </div>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ page.slug }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="page.is_published ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ page.is_published ? 'Published' : 'Draft' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ page.click_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(page.updated_at || page.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <button @click="viewPage(page)" class="text-blue-600 hover:underline">View</button>
                  <button @click="editPage(page)" class="text-blue-600 hover:underline">Edit</button>
                  <button @click="toggleActionsMenu(page.id)" class="text-gray-600 hover:text-gray-900">⋯</button>
                  <div v-if="actionsMenuOpen === page.id" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                    <div class="py-1">
                      <button @click="viewSEO(page)" class="block w-full text-left px-4 py-2 text-sm text-purple-600 hover:bg-gray-100">SEO Settings</button>
                      <button @click="manageFAQs(page)" class="block w-full text-left px-4 py-2 text-sm text-indigo-600 hover:bg-gray-100">Manage FAQs</button>
                      <button @click="manageResources(page)" class="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-gray-100">Manage Resources</button>
                      <button @click="manageCTAs(page)" class="block w-full text-left px-4 py-2 text-sm text-green-600 hover:bg-gray-100">Manage CTAs</button>
                      <button @click="viewEditHistory(page)" class="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">Edit History</button>
                      <button @click="deletePageAction(page)" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">Delete</button>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="!pages.length" class="text-center py-12 text-gray-500">
          No SEO pages found.
        </div>
      </div>
    </div>

    <!-- Create/Edit Page Modal -->
    <div v-if="showCreateModal || editingPage" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingPage ? 'Edit SEO Page' : 'Create SEO Page' }}</h2>
            <button @click="closeModal" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          
          <form @submit.prevent="savePage" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Website *</label>
                <select 
                  v-model="pageForm.website_id" 
                  :disabled="!canSelectWebsite || availableWebsites.length === 0"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Select Website</option>
                  <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                    {{ formatWebsiteName(website) }}
                  </option>
                </select>
                <p v-if="!canSelectWebsite && availableWebsites.length === 0" class="text-xs text-gray-500 mt-1">No websites available</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Title *</label>
                <input v-model="pageForm.title" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Slug</label>
                <input v-model="pageForm.slug" type="text" class="w-full border rounded px-3 py-2" />
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">Short Description</label>
              <textarea v-model="pageForm.short_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">Content *</label>
              <RichTextEditor
                v-model="pageForm.content"
                :required="true"
                placeholder="Write your service page content..."
                toolbar="full"
                height="400px"
                :allow-images="true"
              />
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input v-model="pageForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea v-model="pageForm.meta_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Active</label>
                <input v-model="pageForm.is_active" type="checkbox" class="mt-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Featured</label>
                <input v-model="pageForm.is_featured" type="checkbox" class="mt-2" />
              </div>
            </div>
            
            <!-- FAQs Section -->
            <div class="border-t pt-4">
              <div class="flex items-center justify-between mb-3">
                <label class="block text-sm font-medium">FAQs (Optional)</label>
                <button
                  type="button"
                  @click="addFAQ"
                  class="text-sm text-blue-600 hover:underline"
                >
                  + Add FAQ
                </button>
              </div>
              <div v-if="pageForm.faqs_data && pageForm.faqs_data.length" class="space-y-3">
                <div
                  v-for="(faq, index) in pageForm.faqs_data"
                  :key="index"
                  class="border rounded p-3 bg-gray-50"
                >
                  <div class="flex justify-between items-start mb-2">
                    <span class="text-sm font-medium text-gray-700">FAQ {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeFAQ(index)"
                      class="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-2">
                    <div>
                      <label class="block text-xs font-medium mb-1">Question *</label>
                      <input
                        v-model="faq.question"
                        type="text"
                        required
                        placeholder="Enter question..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">Answer *</label>
                      <RichTextEditor
                        v-model="faq.answer"
                        :required="true"
                        placeholder="Enter answer..."
                        toolbar="basic"
                        height="150px"
                        :allow-images="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 italic">No FAQs added. Click "+ Add FAQ" to add one.</p>
            </div>
            
            <!-- Resources Section -->
            <div class="border-t pt-4">
              <div class="flex items-center justify-between mb-3">
                <label class="block text-sm font-medium">Resources (Optional)</label>
                <button
                  type="button"
                  @click="addResource"
                  class="text-sm text-blue-600 hover:underline"
                >
                  + Add Resource
                </button>
              </div>
              <div v-if="pageForm.resources_data && pageForm.resources_data.length" class="space-y-3">
                <div
                  v-for="(resource, index) in pageForm.resources_data"
                  :key="index"
                  class="border rounded p-3 bg-gray-50"
                >
                  <div class="flex justify-between items-start mb-2">
                    <span class="text-sm font-medium text-gray-700">Resource {{ index + 1 }}</span>
                    <button
                      type="button"
                      @click="removeResource(index)"
                      class="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div class="space-y-2">
                    <div>
                      <label class="block text-xs font-medium mb-1">Title *</label>
                      <input
                        v-model="resource.title"
                        type="text"
                        required
                        placeholder="Resource title..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">URL *</label>
                      <input
                        v-model="resource.url"
                        type="url"
                        required
                        placeholder="https://example.com"
                        class="w-full border rounded px-2 py-1 text-sm"
                      />
                    </div>
                    <div>
                      <label class="block text-xs font-medium mb-1">Description</label>
                      <textarea
                        v-model="resource.description"
                        rows="2"
                        placeholder="Resource description..."
                        class="w-full border rounded px-2 py-1 text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-gray-500 italic">No resources added. Click "+ Add Resource" to add one.</p>
            </div>
            
            <div class="flex justify-end gap-2 pt-4">
              <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" :disabled="saving" class="btn btn-primary">
                {{ saving ? 'Saving...' : (editingPage ? 'Update' : 'Create') }}
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
import { ref, onMounted, watch } from 'vue'
import seoPagesAPI from '@/api/seo-pages'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import { formatWebsiteName } from '@/utils/formatDisplay'

const pages = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingPage = ref(null)
const actionsMenuOpen = ref(null)

// Website selection
const availableWebsites = ref([])
const canSelectWebsite = ref(false)

const filters = ref({
  search: '',
  is_active: '',
})

const pageForm = ref({
  website_id: null,
  title: '',
  slug: '',
  short_description: '',
  content: '',
  meta_title: '',
  meta_description: '',
  is_active: true,
  is_featured: false,
  faqs_data: [],
  resources_data: [],
})

const message = ref('')
const messageSuccess = ref(false)

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadPages()
  }, 500)
}

const loadPages = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_active) params.is_active = filters.value.is_active
    
    const res = await seoPagesAPI.listServicePages(params)
    pages.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    message.value = 'Failed to load pages: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const savePage = async () => {
  saving.value = true
  message.value = ''
  try {
    if (editingPage.value) {
      await seoPagesAPI.updateServicePage(editingPage.value.id, pageForm.value)
      message.value = 'SEO page updated successfully'
    } else {
      await seoPagesAPI.createServicePage(pageForm.value)
      message.value = 'SEO page created successfully'
    }
    messageSuccess.value = true
    closeModal()
    await loadPages()
  } catch (e) {
    message.value = 'Failed to save page: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data))
    messageSuccess.value = false
  } finally {
    saving.value = false
  }
}

const editPage = (page) => {
  editingPage.value = page
  pageForm.value = {
    website_id: page.website?.id || null,
    title: page.title || '',
    slug: page.slug || '',
    short_description: page.short_description || '',
    content: page.content || '',
    meta_title: page.meta_title || '',
    meta_description: page.meta_description || '',
    is_active: page.is_active !== undefined ? page.is_active : true,
    is_featured: page.is_featured || false,
    faqs_data: page.faqs?.map(faq => ({
      question: faq.question || '',
      answer: faq.answer || ''
    })) || [],
    resources_data: page.resources?.map(resource => ({
      title: resource.title || '',
      url: resource.url || '',
      description: resource.description || ''
    })) || [],
  }
  showCreateModal.value = true
}

const viewPage = (page) => {
  // TODO: Navigate to page detail view
  console.log('View page:', page)
}

const viewSEO = (page) => {
  // TODO: Open SEO settings modal
  console.log('View SEO for:', page)
}

const manageFAQs = (page) => {
  // Open edit modal with FAQs section
  editPage(page)
}

const manageResources = (page) => {
  // Open edit modal with Resources section
  editPage(page)
}

const addFAQ = () => {
  if (!pageForm.value.faqs_data) {
    pageForm.value.faqs_data = []
  }
  pageForm.value.faqs_data.push({
    question: '',
    answer: ''
  })
}

const removeFAQ = (index) => {
  pageForm.value.faqs_data.splice(index, 1)
}

const addResource = () => {
  if (!pageForm.value.resources_data) {
    pageForm.value.resources_data = []
  }
  pageForm.value.resources_data.push({
    title: '',
    url: '',
    description: ''
  })
}

const removeResource = (index) => {
  pageForm.value.resources_data.splice(index, 1)
}

const manageCTAs = (page) => {
  // TODO: Open CTAs management modal
  console.log('Manage CTAs for:', page)
}

const viewEditHistory = (page) => {
  // TODO: Open edit history modal
  console.log('View edit history for:', page)
}

const deletePageAction = async (page) => {
  if (!confirm(`Delete "${page.title}"?`)) return
  try {
    await seoPagesAPI.deleteServicePage(page.id)
    message.value = 'SEO page deleted'
    messageSuccess.value = true
    await loadPages()
  } catch (e) {
    message.value = 'Failed to delete: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
  actionsMenuOpen.value = null
}

const toggleActionsMenu = (pageId) => {
  actionsMenuOpen.value = actionsMenuOpen.value === pageId ? null : pageId
}

const loadAvailableWebsites = async () => {
  try {
    const res = await seoPagesAPI.getAvailableWebsites()
    availableWebsites.value = res.data?.websites || []
    canSelectWebsite.value = res.data?.can_select_website || false
    
    // If there's only one website available, auto-select it (but still allow selection)
    if (availableWebsites.value.length === 1 && !pageForm.value.website_id) {
      pageForm.value.website_id = availableWebsites.value[0].id
    }
  } catch (e) {
    console.error('Failed to load available websites:', e)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingPage.value = null
  pageForm.value = {
    website_id: null,
    title: '',
    slug: '',
    short_description: '',
    content: '',
    meta_title: '',
    meta_description: '',
    is_active: true,
    is_featured: false,
    faqs_data: [],
    resources_data: [],
  }
}

const resetFilters = () => {
  filters.value = { search: '', is_active: '' }
  loadPages()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

onMounted(async () => {
  await Promise.all([loadPages(), loadAvailableWebsites()])
  
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.relative')) {
      actionsMenuOpen.value = null
    }
  })
})

// Watch for modal opening to load websites if needed
watch(showCreateModal, async (isOpen) => {
  if (isOpen && !availableWebsites.value.length) {
    await loadAvailableWebsites()
  }
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
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
}
.card {
  @apply bg-white rounded-lg shadow-sm p-6;
}
</style>

