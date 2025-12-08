<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">SEO Landing Pages</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage SEO-optimized landing pages with block-based content</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create SEO Page
      </button>
    </div>

    <!-- Website Switcher (for superadmins or when multiple websites available) -->
    <div v-if="canSelectWebsite && availableWebsites.length > 1" class="card p-4 dark:bg-gray-800 dark:border-gray-700">
      <WebsiteSwitcher
        v-model="selectedWebsiteId"
        :websites="availableWebsites"
        :can-select-website="canSelectWebsite"
        :show-all-option="true"
        all-option-label="All Websites"
        :label="'Filter by Website'"
        :show-label="true"
        @change="handleWebsiteChange"
      />
    </div>

    <!-- Website Context Banner -->
    <WebsiteContextBanner
      v-if="selectedWebsite"
      :website="selectedWebsite"
      :stats="websiteStats"
    />

    <!-- Filters -->
    <div class="card p-4 dark:bg-gray-800 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by title, slug..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.is_published"
            @change="loadPages"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
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
    <div class="card overflow-hidden dark:bg-gray-800 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else>
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Title</th>
              <th
                v-if="!selectedWebsiteId || canSelectWebsite"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase"
              >
                Website
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Slug</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blocks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Updated</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="page in pages" :key="page.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4">
                <div class="font-medium text-gray-900 dark:text-gray-100">{{ page.title }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ page.slug }}</div>
              </td>
              <td
                v-if="!selectedWebsiteId || canSelectWebsite"
                class="px-6 py-4 whitespace-nowrap"
              >
                <div v-if="page.website" class="text-sm">
                  <div class="font-medium text-gray-900 dark:text-gray-100">{{ page.website.name }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">{{ page.website.domain }}</div>
                </div>
                <span v-else class="text-gray-400 dark:text-gray-500">—</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ page.slug }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="page.is_published ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ page.is_published ? 'Published' : 'Draft' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ (page.blocks || []).length }} blocks
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(page.updated_at || page.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <a :href="`/page/${page.slug}`" target="_blank" class="text-blue-600 dark:text-blue-400 hover:underline">View</a>
                  <button @click="editPage(page)" class="text-blue-600 dark:text-blue-400 hover:underline">Edit</button>
                  <button @click="deletePage(page)" class="text-red-600 dark:text-red-400 hover:underline">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingPage" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-5xl w-full max-h-[90vh] my-auto flex flex-col shadow-xl">
        <!-- Header - Fixed -->
        <div class="flex items-center justify-between p-6 pb-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ editingPage ? 'Edit SEO Page' : 'Create SEO Page' }}</h2>
          <button
            @click="closeModal"
            class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Close modal"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Scrollable Content -->
        <div class="overflow-y-auto flex-1 px-6 py-4">
          <form id="seo-page-form" @submit.prevent="savePage" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website *</label>
                <select
                  v-model="pageForm.website"
                  required
                  :disabled="!canSelectWebsite && availableWebsites.length === 1"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed"
                >
                  <option value="">Select Website</option>
                  <option v-for="website in availableWebsites" :key="website.id" :value="website.id">
                    {{ website.name }} ({{ formatDomain(website.domain) }})
                  </option>
                </select>
                <p v-if="!canSelectWebsite && availableWebsites.length === 1" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  You can only manage content for your assigned website
                </p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Title *</label>
                <input
                  v-model="pageForm.title"
                  type="text"
                  required
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Slug *</label>
                <input
                  v-model="pageForm.slug"
                  type="text"
                  required
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">URL-friendly identifier (e.g., best-essay-writing-service)</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Publish Status</label>
                <label class="flex items-center mt-2">
                  <input
                    v-model="pageForm.is_published"
                    type="checkbox"
                    class="mr-2 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Published</span>
                </label>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Title</label>
                <input
                  v-model="pageForm.meta_title"
                  type="text"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">SEO meta title (defaults to title if empty)</p>
              </div>
              <div>
                <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Description</label>
                <textarea
                  v-model="pageForm.meta_description"
                  rows="2"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                ></textarea>
              </div>
            </div>

            <!-- Block Editor -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
              <BlockEditor
                v-model="pageForm.blocks"
                :website-id="pageForm.website"
              />
            </div>
          </form>
        </div>

        <!-- Footer - Fixed -->
        <div class="flex justify-end gap-2 p-6 pt-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-150"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="seo-page-form"
            :disabled="saving"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors duration-150 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Saving...' : (editingPage ? 'Update' : 'Create') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div
      v-if="message"
      class="p-3 rounded transition-colors duration-200"
      :class="messageSuccess ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import seoPagesAPI from '@/api/seo-pages'
import websitesAPI from '@/api/websites'
import BlockEditor from '@/components/seo/BlockEditor.vue'
import WebsiteSwitcher from '@/components/common/WebsiteSwitcher.vue'
import WebsiteContextBanner from '@/components/common/WebsiteContextBanner.vue'

const pages = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingPage = ref(null)
const availableWebsites = ref([])
const canSelectWebsite = ref(false)
const selectedWebsiteId = ref(null)

const filters = ref({
  search: '',
  is_published: '',
})

// Computed: Selected website object
const selectedWebsite = computed(() => {
  if (!selectedWebsiteId.value) return null
  return availableWebsites.value.find(w => w.id === selectedWebsiteId.value) || null
})

// Computed: Website stats
const websiteStats = computed(() => {
  if (!selectedWebsite.value) return null
  
  const websitePages = pages.value.filter(p => 
    p.website?.id === selectedWebsite.value.id || p.website_id === selectedWebsite.value.id
  )
  
  return {
    totalPosts: websitePages.length,
    publishedPosts: websitePages.filter(p => p.is_published).length,
    draftPosts: websitePages.filter(p => !p.is_published).length,
    totalCategories: 0,
    activeCategories: 0,
    totalAuthors: 0,
  }
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
    
    // Add website filter if a specific website is selected
    if (selectedWebsiteId.value) {
      params.website_id = selectedWebsiteId.value
    }

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
    // Try to get available websites from SEO pages API first
    try {
      const res = await seoPagesAPI.getAvailableWebsites()
      availableWebsites.value = res.data?.websites || []
      canSelectWebsite.value = res.data?.can_select_website || false
    } catch {
      // Fallback to websites API if SEO pages endpoint doesn't exist
      const res = await websitesAPI.listWebsites({ is_active: true })
      availableWebsites.value = res.data?.results || res.data || []
      canSelectWebsite.value = true // Assume true if using fallback
    }
    
    // Auto-select website if only one available or if user can't select
    if (availableWebsites.value.length === 1) {
      selectedWebsiteId.value = availableWebsites.value[0].id
      if (!pageForm.value.website) {
        pageForm.value.website = availableWebsites.value[0].id
      }
    } else if (!canSelectWebsite.value && availableWebsites.value.length > 0) {
      // Regular admin: auto-select their assigned website
      selectedWebsiteId.value = availableWebsites.value[0].id
      if (!pageForm.value.website) {
        pageForm.value.website = availableWebsites.value[0].id
      }
    }
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const handleWebsiteChange = (websiteId) => {
  selectedWebsiteId.value = websiteId
  // Reload pages for the selected website
  loadPages()
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

const formatDomain = (domain) => {
  if (!domain) return ''
  try {
    const url = new URL(domain)
    return url.hostname.replace('www.', '')
  } catch {
    return domain.replace(/^https?:\/\//, '').replace('www.', '')
  }
}

onMounted(() => {
  loadPages()
  loadWebsites()
})

// Watch for website changes to reload data
watch(selectedWebsiteId, () => {
  loadPages()
})
</script>

