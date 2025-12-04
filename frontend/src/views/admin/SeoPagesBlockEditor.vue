<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">SEO Landing Pages</h1>
        <p class="mt-2 text-gray-600">Manage SEO-optimized landing pages with block-based content</p>
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
            placeholder="Search by title, slug..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.is_published" @change="loadPages" class="w-full border rounded px-3 py-2">
            <option value="">All Status</option>
            <option value="true">Published</option>
            <option value="false">Draft</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- SEO Pages Table -->
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
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Blocks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="page in pages" :key="page.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900">{{ page.title }}</div>
                <div class="text-sm text-gray-500">{{ page.slug }}</div>
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
                {{ (page.blocks || []).length }} blocks
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(page.updated_at || page.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <a :href="`/page/${page.slug}`" target="_blank" class="text-blue-600 hover:underline">View</a>
                  <button @click="editPage(page)" class="text-blue-600 hover:underline">Edit</button>
                  <button @click="deletePage(page)" class="text-red-600 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingPage" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-y-auto">
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
                  v-model="pageForm.website"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="">Select Website</option>
                  <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                    {{ website.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Title *</label>
                <input v-model="pageForm.title" type="text" required class="w-full border rounded px-3 py-2" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Slug *</label>
                <input v-model="pageForm.slug" type="text" required class="w-full border rounded px-3 py-2" />
                <p class="text-xs text-gray-500 mt-1">URL-friendly identifier (e.g., best-essay-writing-service)</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Publish Status</label>
                <label class="flex items-center mt-2">
                  <input v-model="pageForm.is_published" type="checkbox" class="mr-2" />
                  <span class="text-sm">Published</span>
                </label>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title</label>
                <input v-model="pageForm.meta_title" type="text" class="w-full border rounded px-3 py-2" />
                <p class="text-xs text-gray-500 mt-1">SEO meta title (defaults to title if empty)</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description</label>
                <textarea v-model="pageForm.meta_description" rows="2" class="w-full border rounded px-3 py-2"></textarea>
              </div>
            </div>

            <!-- Block Editor -->
            <div class="border-t pt-4">
              <BlockEditor
                v-model="pageForm.blocks"
                :website-id="pageForm.website"
              />
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
import { ref, onMounted } from 'vue'
import seoPagesAPI from '@/api/seo-pages'
import websitesAPI from '@/api/websites'
import BlockEditor from '@/components/seo/BlockEditor.vue'

const pages = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingPage = ref(null)
const availableWebsites = ref([])

const filters = ref({
  search: '',
  is_published: '',
})

const pageForm = ref({
  website: null,
  title: '',
  slug: '',
  meta_title: '',
  meta_description: '',
  blocks: [],
  is_published: false,
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
    if (filters.value.is_published) params.is_published = filters.value.is_published

    const res = await seoPagesAPI.list(params)
    pages.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    message.value = 'Failed to load pages: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    availableWebsites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const savePage = async () => {
  saving.value = true
  message.value = ''
  try {
    const formData = {
      website: pageForm.value.website,
      title: pageForm.value.title,
      slug: pageForm.value.slug,
      meta_title: pageForm.value.meta_title,
      meta_description: pageForm.value.meta_description,
      blocks: pageForm.value.blocks.map(block => {
        const cleanBlock = { type: block.type }
        if (block.type === 'paragraph') cleanBlock.content = block.content
        if (block.type === 'heading') {
          cleanBlock.level = block.level || 2
          cleanBlock.content = block.content
        }
        if (block.type === 'image') {
          cleanBlock.url = block.url || block.asset?.url || ''
          cleanBlock.alt = block.alt || ''
          cleanBlock.caption = block.caption || ''
        }
        if (block.type === 'cta') {
          cleanBlock.title = block.title || ''
          cleanBlock.description = block.description || ''
          cleanBlock.button_text = block.button_text || ''
          cleanBlock.button_url = block.button_url || ''
        }
        if (block.type === 'list') {
          cleanBlock.style = block.style || 'unordered'
          cleanBlock.items = (block.items || []).filter(item => item.trim())
        }
        return cleanBlock
      }),
      is_published: pageForm.value.is_published,
    }

    if (editingPage.value) {
      await seoPagesAPI.update(editingPage.value.id, formData)
      message.value = 'SEO page updated successfully'
    } else {
      await seoPagesAPI.create(formData)
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
    website: page.website?.id || null,
    title: page.title || '',
    slug: page.slug || '',
    meta_title: page.meta_title || '',
    meta_description: page.meta_description || '',
    blocks: (page.blocks || []).map(block => ({
      ...block,
      asset: block.url ? { url: block.url } : null
    })),
    is_published: page.is_published || false,
  }
  showCreateModal.value = true
}

const deletePage = async (page) => {
  if (!confirm(`Are you sure you want to delete "${page.title}"?`)) return

  try {
    await seoPagesAPI.delete(page.id)
    message.value = 'SEO page deleted successfully'
    messageSuccess.value = true
    await loadPages()
  } catch (e) {
    message.value = 'Failed to delete page: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingPage.value = null
  pageForm.value = {
    website: null,
    title: '',
    slug: '',
    meta_title: '',
    meta_description: '',
    blocks: [],
    is_published: false,
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    is_published: '',
  }
  loadPages()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadPages()
  loadWebsites()
})
</script>

