<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Content Blocks Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Create reusable content blocks and insert them into blog posts</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="activeTab = 'templates'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'templates' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Templates
        </button>
        <button
          @click="activeTab = 'blog-blocks'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'blog-blocks' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Blog Blocks
        </button>
      </div>
    </div>

    <!-- Templates Tab -->
    <div v-if="activeTab === 'templates'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Content Block Templates</h2>
        <button
          @click="openAddTemplateModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Create Template
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Templates</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ templates.length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ templates.filter(t => t.is_active).length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Block Types</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueBlockTypes.length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
          <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">In Use</p>
          <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ templatesInUse }}</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="card p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
          <input
            v-model="templateSearchQuery"
            type="text"
            placeholder="Search templates..."
            class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @input="debouncedLoadTemplates"
          />
          <select
            v-model="blockTypeFilter"
            class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @change="loadTemplates"
          >
            <option value="">All Types</option>
            <option value="table">Data Table</option>
            <option value="info_box">Info Box</option>
            <option value="warning_box">Warning Box</option>
            <option value="tip_box">Tip Box</option>
            <option value="quote">Quote Block</option>
            <option value="statistics">Statistics Block</option>
            <option value="timeline">Timeline</option>
            <option value="comparison">Comparison Table</option>
            <option value="testimonial">Testimonial Block</option>
            <option value="pricing_table">Pricing Table</option>
          </select>
        </div>
      </div>

      <!-- Templates Grid -->
      <div v-if="templatesLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          :class="[
            'card p-4 transition-all',
            !template.is_active ? 'opacity-60' : ''
          ]"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ template.name }}</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatBlockType(template.block_type) }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-semibold rounded-full',
                template.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
              ]"
            >
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div v-if="template.content" class="mb-3">
            <p class="text-xs text-gray-600 dark:text-gray-400 line-clamp-3" v-html="template.content.substring(0, 100)"></p>
          </div>
          <div class="flex gap-2">
            <button
              @click="editTemplate(template)"
              class="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="previewTemplate(template)"
              class="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Preview
            </button>
            <button
              @click="deleteTemplate(template)"
              class="px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
        <div v-if="filteredTemplates.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
          No templates found. Create your first template to get started.
        </div>
      </div>
    </div>

    <!-- Blog Blocks Tab -->
    <div v-if="activeTab === 'blog-blocks'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Content Blocks in Blog Posts</h2>
        <button
          @click="openAddBlogBlockModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Insert Block into Blog
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Blocks</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ blogBlocks.length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ blogBlocks.filter(b => b.is_active).length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique Blogs</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueBlogs.length }}</p>
        </div>
      </div>

      <!-- Blog Blocks Table -->
      <div v-if="blogBlocksLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Template</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Block Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Position</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="block in blogBlocks"
                :key="block.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  Blog #{{ block.blog || block.blog_id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ block.template_name || block.template || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatBlockType(block.block_type || block.template_block_type) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ block.position || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      block.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ block.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="editBlogBlock(block)"
                    class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteBlogBlock(block)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="blogBlocks.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          No content blocks found in blog posts. Insert your first block to get started.
        </div>
      </div>
    </div>

    <!-- Add/Edit Template Modal -->
    <Modal
      :visible="showTemplateModal"
      @close="closeTemplateModal"
      :title="editingTemplate ? 'Edit Content Block Template' : 'Create Content Block Template'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="templateForm.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Template name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Block Type *</label>
          <select
            v-model="templateForm.block_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="table">Data Table</option>
            <option value="info_box">Info Box</option>
            <option value="warning_box">Warning Box</option>
            <option value="tip_box">Tip Box</option>
            <option value="quote">Quote Block</option>
            <option value="statistics">Statistics Block</option>
            <option value="timeline">Timeline</option>
            <option value="comparison">Comparison Table</option>
            <option value="testimonial">Testimonial Block</option>
            <option value="pricing_table">Pricing Table</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Content (HTML) *</label>
          <textarea
            v-model="templateForm.content"
            rows="8"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white font-mono text-sm"
            placeholder="<div class='info-box'>...</div>"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">HTML content for this block. Use template variables like {{data}} for dynamic content.</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template Data (JSON)</label>
          <textarea
            v-model="templateDataJson"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white font-mono text-sm"
            placeholder='{"rows": [], "columns": []}'
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">JSON data for dynamic content (e.g., table rows, statistics values)</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CSS Classes</label>
          <input
            v-model="templateForm.css_classes"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="custom-class another-class"
          />
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="templateForm.is_active"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
          </label>
        </div>
        <div v-if="templateFormError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ templateFormError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeTemplateModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveTemplate"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingTemplate ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

    <!-- Add/Edit Blog Block Modal -->
    <Modal
      :visible="showBlogBlockModal"
      @close="closeBlogBlockModal"
      :title="editingBlogBlock ? 'Edit Blog Content Block' : 'Insert Content Block into Blog'"
      size="md"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Blog ID *</label>
          <input
            v-model.number="blogBlockForm.blog"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Blog post ID"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Template *</label>
          <select
            v-model.number="blogBlockForm.template"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="">Select Template</option>
            <option v-for="template in activeTemplates" :key="template.id" :value="template.id">
              {{ template.name }} ({{ formatBlockType(template.block_type) }})
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Position *</label>
          <input
            v-model.number="blogBlockForm.position"
            type="number"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="0 (paragraph/heading index)"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Position in content where block should appear (0 = top, 1 = after first paragraph, etc.)</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Custom Data (JSON)</label>
          <textarea
            v-model="blogBlockCustomDataJson"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white font-mono text-sm"
            placeholder='{"key": "value"}'
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Blog-specific data overriding template data</p>
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="blogBlockForm.is_active"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
          </label>
        </div>
        <div v-if="blogBlockFormError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ blogBlockFormError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeBlogBlockModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveBlogBlock"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingBlogBlock ? 'Update' : 'Insert') }}
        </button>
      </template>
    </Modal>

    <!-- Preview Modal -->
    <Modal
      :visible="showPreviewModal"
      @close="closePreviewModal"
      title="Template Preview"
      size="lg"
    >
      <div v-if="previewTemplate" class="space-y-4">
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white mb-2">{{ previewTemplate.name }}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">{{ formatBlockType(previewTemplate.block_type) }}</p>
        </div>
        <div class="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
          <div v-html="previewTemplate.content"></div>
        </div>
      </div>
    </Modal>

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
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import blogPagesAPI from '@/api/blog-pages'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const activeTab = ref('templates')
const templatesLoading = ref(false)
const blogBlocksLoading = ref(false)
const saving = ref(false)
const templates = ref([])
const blogBlocks = ref([])
const showTemplateModal = ref(false)
const showBlogBlockModal = ref(false)
const showPreviewModal = ref(false)
const editingTemplate = ref(null)
const editingBlogBlock = ref(null)
const previewTemplate = ref(null)
const templateFormError = ref('')
const blogBlockFormError = ref('')
const templateSearchQuery = ref('')
const blockTypeFilter = ref('')

const templateForm = ref({
  name: '',
  block_type: 'info_box',
  content: '',
  template_data: {},
  css_classes: '',
  is_active: true,
})

const templateDataJson = ref('{}')

const blogBlockForm = ref({
  blog: null,
  template: null,
  position: 0,
  custom_data: {},
  is_active: true,
})

const blogBlockCustomDataJson = ref('{}')

const filteredTemplates = computed(() => {
  let filtered = templates.value
  
  if (templateSearchQuery.value) {
    const query = templateSearchQuery.value.toLowerCase()
    filtered = filtered.filter(t => 
      (t.name && t.name.toLowerCase().includes(query)) ||
      (t.content && t.content.toLowerCase().includes(query))
    )
  }
  
  if (blockTypeFilter.value) {
    filtered = filtered.filter(t => t.block_type === blockTypeFilter.value)
  }
  
  return filtered
})

const uniqueBlockTypes = computed(() => {
  return [...new Set(templates.value.map(t => t.block_type))]
})

const templatesInUse = computed(() => {
  const templateIds = new Set(blogBlocks.value.map(b => b.template || b.template_id).filter(Boolean))
  return templateIds.size
})

const uniqueBlogs = computed(() => {
  return [...new Set(blogBlocks.value.map(b => b.blog || b.blog_id).filter(Boolean))]
})

const activeTemplates = computed(() => {
  return templates.value.filter(t => t.is_active)
})

const debouncedLoadTemplates = debounce(() => {
  loadTemplates()
}, 300)

const formatBlockType = (type) => {
  if (!type) return 'N/A'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const loadTemplates = async () => {
  templatesLoading.value = true
  try {
    const params = {}
    if (blockTypeFilter.value) params.block_type = blockTypeFilter.value
    
    const response = await blogPagesAPI.listContentBlockTemplates(params)
    templates.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load content block templates')
    console.error('Error loading templates:', error)
  } finally {
    templatesLoading.value = false
  }
}

const loadBlogBlocks = async () => {
  blogBlocksLoading.value = true
  try {
    const response = await blogPagesAPI.listBlogContentBlocks()
    blogBlocks.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load blog content blocks')
    console.error('Error loading blog blocks:', error)
  } finally {
    blogBlocksLoading.value = false
  }
}

const openAddTemplateModal = () => {
  editingTemplate.value = null
  templateForm.value = {
    name: '',
    block_type: 'info_box',
    content: '',
    template_data: {},
    css_classes: '',
    is_active: true,
  }
  templateDataJson.value = '{}'
  templateFormError.value = ''
  showTemplateModal.value = true
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name || '',
    block_type: template.block_type || 'info_box',
    content: template.content || '',
    template_data: template.template_data || {},
    css_classes: template.css_classes || '',
    is_active: template.is_active !== undefined ? template.is_active : true,
  }
  templateDataJson.value = JSON.stringify(template.template_data || {}, null, 2)
  templateFormError.value = ''
  showTemplateModal.value = true
}

const closeTemplateModal = () => {
  showTemplateModal.value = false
  editingTemplate.value = null
  templateFormError.value = ''
}

const saveTemplate = async () => {
  saving.value = true
  templateFormError.value = ''
  
  try {
    // Parse template data JSON
    try {
      templateForm.value.template_data = JSON.parse(templateDataJson.value || '{}')
    } catch (e) {
      templateFormError.value = 'Invalid JSON in template data'
      saving.value = false
      return
    }
    
    if (editingTemplate.value) {
      await blogPagesAPI.updateContentBlockTemplate(editingTemplate.value.id, templateForm.value)
      showSuccess('Template updated successfully')
    } else {
      await blogPagesAPI.createContentBlockTemplate(templateForm.value)
      showSuccess('Template created successfully')
    }
    
    closeTemplateModal()
    loadTemplates()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save template'
    templateFormError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const previewTemplate = (template) => {
  previewTemplate.value = template
  showPreviewModal.value = true
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  previewTemplate.value = null
}

const deleteTemplate = (template) => {
  confirm.showDestructive(
    'Delete Template',
    `Are you sure you want to delete "${template.name}"?`,
    'This action cannot be undone. All blog posts using this template will be affected.',
    async () => {
      try {
        await blogPagesAPI.deleteContentBlockTemplate(template.id)
        showSuccess('Template deleted successfully')
        loadTemplates()
        loadBlogBlocks()
      } catch (error) {
        showError('Failed to delete template')
      }
    }
  )
}

const openAddBlogBlockModal = () => {
  editingBlogBlock.value = null
  blogBlockForm.value = {
    blog: null,
    template: null,
    position: 0,
    custom_data: {},
    is_active: true,
  }
  blogBlockCustomDataJson.value = '{}'
  blogBlockFormError.value = ''
  showBlogBlockModal.value = true
}

const editBlogBlock = (block) => {
  editingBlogBlock.value = block
  blogBlockForm.value = {
    blog: block.blog || block.blog_id || null,
    template: block.template || block.template_id || null,
    position: block.position || 0,
    custom_data: block.custom_data || {},
    is_active: block.is_active !== undefined ? block.is_active : true,
  }
  blogBlockCustomDataJson.value = JSON.stringify(block.custom_data || {}, null, 2)
  blogBlockFormError.value = ''
  showBlogBlockModal.value = true
}

const closeBlogBlockModal = () => {
  showBlogBlockModal.value = false
  editingBlogBlock.value = null
  blogBlockFormError.value = ''
}

const saveBlogBlock = async () => {
  saving.value = true
  blogBlockFormError.value = ''
  
  try {
    // Parse custom data JSON
    try {
      blogBlockForm.value.custom_data = JSON.parse(blogBlockCustomDataJson.value || '{}')
    } catch (e) {
      blogBlockFormError.value = 'Invalid JSON in custom data'
      saving.value = false
      return
    }
    
    if (editingBlogBlock.value) {
      await blogPagesAPI.updateBlogContentBlock(editingBlogBlock.value.id, blogBlockForm.value)
      showSuccess('Blog content block updated successfully')
    } else {
      await blogPagesAPI.createBlogContentBlock(blogBlockForm.value)
      showSuccess('Content block inserted into blog successfully')
    }
    
    closeBlogBlockModal()
    loadBlogBlocks()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save blog content block'
    blogBlockFormError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteBlogBlock = (block) => {
  confirm.showDestructive(
    'Remove Content Block',
    'Are you sure you want to remove this content block from the blog post?',
    'This action cannot be undone.',
    async () => {
      try {
        await blogPagesAPI.deleteBlogContentBlock(block.id)
        showSuccess('Content block removed successfully')
        loadBlogBlocks()
      } catch (error) {
        showError('Failed to remove content block')
      }
    }
  )
}

watch(activeTab, (newTab) => {
  if (newTab === 'templates' && templates.value.length === 0) {
    loadTemplates()
  } else if (newTab === 'blog-blocks' && blogBlocks.value.length === 0) {
    loadBlogBlocks()
  }
})

onMounted(() => {
  loadTemplates()
})
</script>

