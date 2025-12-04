<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Templates & Snippets Manager</h1>
        <p class="mt-2 text-gray-600">Manage reusable content templates and snippets</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedWebsiteId"
          @change="loadData"
          class="border rounded px-3 py-2"
        >
          <option value="">Select Website</option>
          <option v-for="website in websites" :key="website.id" :value="website.id">
            {{ website.name }}
          </option>
        </select>
        <div class="flex gap-2">
          <button
            @click="showTemplateModal = true; editingTemplate = null"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + New Template
          </button>
          <button
            @click="showSnippetModal = true; editingSnippet = null"
            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            + New Snippet
          </button>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b">
      <div class="flex gap-4">
        <button
          @click="activeTab = 'templates'"
          class="px-4 py-2 border-b-2 font-medium"
          :class="activeTab === 'templates' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500'"
        >
          Templates ({{ templates.length }})
        </button>
        <button
          @click="activeTab = 'snippets'"
          class="px-4 py-2 border-b-2 font-medium"
          :class="activeTab === 'snippets' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500'"
        >
          Snippets ({{ snippets.length }})
        </button>
      </div>
    </div>

    <!-- Templates Tab -->
    <div v-if="activeTab === 'templates'" class="card">
      <div class="mb-4 flex items-center justify-between">
        <input
          v-model="templateSearch"
          type="text"
          placeholder="Search templates..."
          class="w-64 px-3 py-2 border rounded"
        />
        <select
          v-model="templateTypeFilter"
          @change="filterTemplates"
          class="px-3 py-2 border rounded"
        >
          <option value="">All Types</option>
          <option value="blog_post">Blog Post</option>
          <option value="service_page">Service Page</option>
          <option value="section">Section</option>
          <option value="cta">CTA Block</option>
        </select>
      </div>

      <div v-if="loadingTemplates" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="filteredTemplates.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-2">
            <div class="flex-1">
              <h3 class="font-semibold text-lg">{{ template.name }}</h3>
              <p class="text-sm text-gray-500">{{ template.template_type }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500">Used {{ template.usage_count }}x</span>
              <button
                @click="editTemplate(template)"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                Edit
              </button>
              <button
                @click="deleteTemplate(template.id)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
          <p v-if="template.description" class="text-sm text-gray-600 mb-2">
            {{ template.description }}
          </p>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span v-if="template.category_name">{{ template.category_name }}</span>
            <span v-if="template.tags_count">{{ template.tags_count }} tags</span>
            <span :class="template.is_active ? 'text-green-600' : 'text-gray-400'">
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-500">
        No templates found. Create one to get started.
      </div>
    </div>

    <!-- Snippets Tab -->
    <div v-if="activeTab === 'snippets'" class="card">
      <div class="mb-4">
        <input
          v-model="snippetSearch"
          type="text"
          placeholder="Search snippets..."
          class="w-64 px-3 py-2 border rounded"
        />
      </div>

      <div v-if="loadingSnippets" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <div v-else-if="filteredSnippets.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="snippet in filteredSnippets"
          :key="snippet.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-2">
            <div class="flex-1">
              <h3 class="font-semibold text-lg">{{ snippet.name }}</h3>
              <p class="text-sm text-gray-500">{{ snippet.snippet_type }}</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500">Used {{ snippet.usage_count }}x</span>
              <button
                @click="editSnippet(snippet)"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                Edit
              </button>
              <button
                @click="deleteSnippet(snippet.id)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
          <p v-if="snippet.description" class="text-sm text-gray-600 mb-2">
            {{ snippet.description }}
          </p>
          <div class="text-xs text-gray-500 mb-2">
            <span :class="snippet.is_active ? 'text-green-600' : 'text-gray-400'">
              {{ snippet.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="text-xs text-gray-400 font-mono bg-gray-50 p-2 rounded max-h-20 overflow-y-auto">
            {{ truncateContent(snippet.content) }}
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-500">
        No snippets found. Create one to get started.
      </div>
    </div>

    <!-- Template Modal -->
    <div
      v-if="showTemplateModal"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click="showTemplateModal = false"
    >
      <div
        class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingTemplate ? 'Edit Template' : 'Create Template' }}</h2>
            <button @click="showTemplateModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>

          <form @submit.prevent="saveTemplate" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Name *</label>
                <input
                  v-model="templateForm.name"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Type *</label>
                <select
                  v-model="templateForm.template_type"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="blog_post">Blog Post</option>
                  <option value="service_page">Service Page</option>
                  <option value="section">Section</option>
                  <option value="cta">CTA Block</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea
                v-model="templateForm.description"
                rows="2"
                class="w-full border rounded px-3 py-2"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Title Template</label>
              <input
                v-model="templateForm.title_template"
                type="text"
                placeholder="e.g., {{title}} - Blog Post"
                class="w-full border rounded px-3 py-2"
              />
              <p class="text-xs text-gray-500 mt-1">Use {{variable}} for dynamic content</p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Content Template</label>
              <textarea
                v-model="templateForm.content_template"
                rows="8"
                class="w-full border rounded px-3 py-2 font-mono text-sm"
                placeholder="Enter HTML content template..."
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Meta Title Template</label>
                <input
                  v-model="templateForm.meta_title_template"
                  type="text"
                  maxlength="60"
                  class="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Meta Description Template</label>
                <textarea
                  v-model="templateForm.meta_description_template"
                  rows="2"
                  maxlength="160"
                  class="w-full border rounded px-3 py-2"
                ></textarea>
              </div>
            </div>

            <div class="flex items-center">
              <input
                v-model="templateForm.is_active"
                type="checkbox"
                class="mr-2"
              />
              <label class="text-sm">Active</label>
            </div>

            <div class="flex justify-end gap-2 pt-4">
              <button
                type="button"
                @click="showTemplateModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                {{ editingTemplate ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Snippet Modal -->
    <div
      v-if="showSnippetModal"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click="showSnippetModal = false"
    >
      <div
        class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold">{{ editingSnippet ? 'Edit Snippet' : 'Create Snippet' }}</h2>
            <button @click="showSnippetModal = false" class="text-gray-500 hover:text-gray-700">✕</button>
          </div>

          <form @submit.prevent="saveSnippet" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium mb-1">Name *</label>
                <input
                  v-model="snippetForm.name"
                  type="text"
                  required
                  class="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-1">Type *</label>
                <select
                  v-model="snippetForm.snippet_type"
                  required
                  class="w-full border rounded px-3 py-2"
                >
                  <option value="text">Text</option>
                  <option value="html">HTML</option>
                  <option value="markdown">Markdown</option>
                  <option value="code">Code Block</option>
                  <option value="table">Table</option>
                  <option value="list">List</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Description</label>
              <textarea
                v-model="snippetForm.description"
                rows="2"
                class="w-full border rounded px-3 py-2"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Content *</label>
              <textarea
                v-model="snippetForm.content"
                rows="10"
                required
                class="w-full border rounded px-3 py-2 font-mono text-sm"
                placeholder="Enter snippet content..."
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Tags</label>
              <input
                v-model="snippetForm.tags"
                type="text"
                placeholder="comma, separated, tags"
                class="w-full border rounded px-3 py-2"
              />
              <p class="text-xs text-gray-500 mt-1">Separate tags with commas</p>
            </div>

            <div class="flex items-center">
              <input
                v-model="snippetForm.is_active"
                type="checkbox"
                class="mr-2"
              />
              <label class="text-sm">Active</label>
            </div>

            <div class="flex justify-end gap-2 pt-4">
              <button
                type="button"
                @click="showSnippetModal = false"
                class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                {{ editingSnippet ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'

const websites = ref([])
const selectedWebsiteId = ref('')
const activeTab = ref('templates')
const templates = ref([])
const snippets = ref([])
const loadingTemplates = ref(false)
const loadingSnippets = ref(false)
const templateSearch = ref('')
const snippetSearch = ref('')
const templateTypeFilter = ref('')
const showTemplateModal = ref(false)
const showSnippetModal = ref(false)
const editingTemplate = ref(null)
const editingSnippet = ref(null)

const templateForm = ref({
  website_id: null,
  name: '',
  description: '',
  template_type: 'blog_post',
  title_template: '',
  content_template: '',
  meta_title_template: '',
  meta_description_template: '',
  is_active: true
})

const snippetForm = ref({
  website_id: null,
  name: '',
  description: '',
  snippet_type: 'text',
  content: '',
  tags: '',
  is_active: true
})

const filteredTemplates = computed(() => {
  let filtered = templates.value

  if (templateSearch.value) {
    const search = templateSearch.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.name.toLowerCase().includes(search) ||
      (t.description && t.description.toLowerCase().includes(search))
    )
  }

  if (templateTypeFilter.value) {
    filtered = filtered.filter(t => t.template_type === templateTypeFilter.value)
  }

  return filtered
})

const filteredSnippets = computed(() => {
  let filtered = snippets.value

  if (snippetSearch.value) {
    const search = snippetSearch.value.toLowerCase()
    filtered = filtered.filter(s =>
      s.name.toLowerCase().includes(search) ||
      (s.description && s.description.toLowerCase().includes(search)) ||
      (s.tags && s.tags.toLowerCase().includes(search))
    )
  }

  return filtered
})

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({})
    websites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadTemplates = async () => {
  if (!selectedWebsiteId.value) {
    templates.value = []
    return
  }

  loadingTemplates.value = true
  try {
    const res = await blogPagesAPI.listContentTemplates({
      website: selectedWebsiteId.value
    })
    templates.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load templates:', e)
  } finally {
    loadingTemplates.value = false
  }
}

const loadSnippets = async () => {
  if (!selectedWebsiteId.value) {
    snippets.value = []
    return
  }

  loadingSnippets.value = true
  try {
    const res = await blogPagesAPI.listContentSnippets({
      website: selectedWebsiteId.value
    })
    snippets.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load snippets:', e)
  } finally {
    loadingSnippets.value = false
  }
}

const loadData = () => {
  loadTemplates()
  loadSnippets()
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    website_id: template.website,
    name: template.name,
    description: template.description || '',
    template_type: template.template_type,
    title_template: template.title_template || '',
    content_template: template.content_template || '',
    meta_title_template: template.meta_title_template || '',
    meta_description_template: template.meta_description_template || '',
    is_active: template.is_active
  }
  showTemplateModal.value = true
}

const editSnippet = (snippet) => {
  editingSnippet.value = snippet
  snippetForm.value = {
    website_id: snippet.website,
    name: snippet.name,
    description: snippet.description || '',
    snippet_type: snippet.snippet_type,
    content: snippet.content,
    tags: snippet.tags || '',
    is_active: snippet.is_active
  }
  showSnippetModal.value = true
}

const saveTemplate = async () => {
  try {
    templateForm.value.website_id = selectedWebsiteId.value

    if (editingTemplate.value) {
      await blogPagesAPI.updateContentTemplate(editingTemplate.value.id, templateForm.value)
    } else {
      await blogPagesAPI.createContentTemplate(templateForm.value)
    }

    showTemplateModal.value = false
    editingTemplate.value = null
    await loadTemplates()
  } catch (e) {
    console.error('Failed to save template:', e)
    alert('Failed to save template. Please try again.')
  }
}

const saveSnippet = async () => {
  try {
    snippetForm.value.website_id = selectedWebsiteId.value

    if (editingSnippet.value) {
      await blogPagesAPI.updateContentSnippet(editingSnippet.value.id, snippetForm.value)
    } else {
      await blogPagesAPI.createContentSnippet(snippetForm.value)
    }

    showSnippetModal.value = false
    editingSnippet.value = null
    await loadSnippets()
  } catch (e) {
    console.error('Failed to save snippet:', e)
    alert('Failed to save snippet. Please try again.')
  }
}

const deleteTemplate = async (id) => {
  if (!confirm('Delete this template?')) return

  try {
    await blogPagesAPI.deleteContentTemplate(id)
    await loadTemplates()
  } catch (e) {
    console.error('Failed to delete template:', e)
    alert('Failed to delete template. Please try again.')
  }
}

const deleteSnippet = async (id) => {
  if (!confirm('Delete this snippet?')) return

  try {
    await blogPagesAPI.deleteContentSnippet(id)
    await loadSnippets()
  } catch (e) {
    console.error('Failed to delete snippet:', e)
    alert('Failed to delete snippet. Please try again.')
  }
}

const truncateContent = (content) => {
  if (!content) return ''
  return content.length > 100 ? content.substring(0, 100) + '...' : content
}

const filterTemplates = () => {
  // Filtering is handled by computed property
}

watch(selectedWebsiteId, () => {
  if (selectedWebsiteId.value) {
    loadData()
  }
})

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}
</style>

