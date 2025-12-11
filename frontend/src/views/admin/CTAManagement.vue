<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">CTA Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage call-to-action blocks and placements in blog posts</p>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          <strong>How it works:</strong> Create reusable CTA blocks, then place them in blog posts at specific positions (top, middle, bottom, or after paragraphs/headings).
          Use the "Auto Place" feature to automatically insert CTAs at strategic positions.
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="activeTab = 'blocks'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'blocks' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          CTA Blocks
        </button>
        <button
          @click="activeTab = 'placements'"
          :class="[
            'px-4 py-2 rounded-lg transition-colors',
            activeTab === 'placements' 
              ? 'bg-primary-600 text-white' 
              : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
          ]"
        >
          Placements
        </button>
      </div>
    </div>

    <!-- CTA Blocks Tab -->
    <div v-if="activeTab === 'blocks'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">CTA Blocks</h2>
        <button
          @click="openAddBlockModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Add CTA Block
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Blocks</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ ctaBlocks.length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ ctaBlocks.filter(b => b.is_active).length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
          <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Inactive</p>
          <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ ctaBlocks.filter(b => !b.is_active).length }}</p>
        </div>
      </div>

      <!-- Filters -->
      <div class="card p-4 mb-6">
        <div class="flex flex-col sm:flex-row gap-4">
          <input
            v-model="blockSearchQuery"
            type="text"
            placeholder="Search by name or title..."
            class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @input="debouncedLoadBlocks"
          />
          <select
            v-model="blockTypeFilter"
            class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @change="loadBlocks"
          >
            <option value="">All Types</option>
            <option value="button">Button</option>
            <option value="banner">Banner</option>
            <option value="inline">Inline</option>
            <option value="popup">Popup</option>
            <option value="sidebar">Sidebar</option>
            <option value="footer">Footer</option>
            <option value="form">Form</option>
            <option value="download">Download</option>
            <option value="custom">Custom</option>
          </select>
          <select
            v-model="blockStatusFilter"
            class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            @change="loadBlocks"
          >
            <option value="">All Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
      </div>

      <!-- Blocks Grid -->
      <div v-if="blocksLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="block in filteredBlocks"
          :key="block.id"
          :class="[
            'card p-4 transition-all',
            !block.is_active ? 'opacity-60' : ''
          ]"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ block.name }}</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatCTAType(block.cta_type) }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-semibold rounded-full',
                block.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
              ]"
            >
              {{ block.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div v-if="block.title" class="mb-2">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ block.title }}</p>
          </div>
          <div v-if="block.description" class="mb-2">
            <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{{ block.description }}</p>
          </div>
          <div v-if="block.button_text" class="mb-3">
            <span class="inline-block px-3 py-1 text-sm rounded" :style="getButtonStyle(block)">
              {{ block.button_text }}
            </span>
          </div>
          <div class="flex gap-2">
            <button
              @click="editBlock(block)"
              class="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="toggleBlockStatus(block)"
              class="px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              {{ block.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button
              @click="deleteBlock(block)"
              class="px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
        <div v-if="filteredBlocks.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
          No CTA blocks found
        </div>
      </div>
    </div>

    <!-- Placements Tab -->
    <div v-else-if="activeTab === 'placements'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">CTA Placements</h2>
        <button
          @click="openAddPlacementModal"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Add Placement
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
          <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Placements</p>
          <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ placements.length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
          <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
          <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ placements.filter(p => p.is_active).length }}</p>
        </div>
        <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
          <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Unique Blogs</p>
          <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueBlogs.length }}</p>
        </div>
      </div>

      <!-- Placements Table -->
      <div v-if="placementsLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Blog</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">CTA Block</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Placement Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Position</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="placement in placements"
                :key="placement.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  Blog #{{ placement.blog || placement.blog_id || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ placement.cta_block_name || placement.cta_block || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ formatPlacementType(placement.placement_type) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ placement.position || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded-full',
                      placement.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                    ]"
                  >
                    {{ placement.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="editPlacement(placement)"
                    class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    @click="deletePlacement(placement)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="placements.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
          No placements found
        </div>
      </div>
    </div>

    <!-- Add/Edit Block Modal -->
    <Modal
      :visible="showBlockModal"
      @close="closeBlockModal"
      :title="editingBlock ? 'Edit CTA Block' : 'Add CTA Block'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            v-model="blockForm.name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Internal name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CTA Type *</label>
          <select
            v-model="blockForm.cta_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="button">Button</option>
            <option value="banner">Banner</option>
            <option value="inline">Inline</option>
            <option value="popup">Popup</option>
            <option value="sidebar">Sidebar</option>
            <option value="footer">Footer</option>
            <option value="form">Form</option>
            <option value="download">Download</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title</label>
          <input
            v-model="blockForm.title"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="CTA headline"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
          <textarea
            v-model="blockForm.description"
            rows="3"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="CTA description"
          ></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Button Text</label>
            <input
              v-model="blockForm.button_text"
              type="text"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="e.g., Get Started"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Button URL</label>
            <input
              v-model="blockForm.button_url"
              type="url"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              placeholder="https://..."
            />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Style</label>
            <select
              v-model="blockForm.style"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            >
              <option value="primary">Primary</option>
              <option value="secondary">Secondary</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="danger">Danger</option>
              <option value="info">Info</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
          <div>
            <label class="flex items-center gap-2 mt-6">
              <input
                v-model="blockForm.is_active"
                type="checkbox"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
            </label>
          </div>
        </div>
        <div v-if="blockForm.cta_type === 'custom'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Custom HTML</label>
          <textarea
            v-model="blockForm.custom_html"
            rows="6"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white font-mono text-sm"
            placeholder="<div>Custom HTML...</div>"
          ></textarea>
        </div>
        <div v-if="blockFormError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ blockFormError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeBlockModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveBlock"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingBlock ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

    <!-- Add/Edit Placement Modal -->
    <Modal
      :visible="showPlacementModal"
      @close="closePlacementModal"
      :title="editingPlacement ? 'Edit CTA Placement' : 'Add CTA Placement'"
      size="md"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Blog ID *</label>
          <input
            v-model.number="placementForm.blog"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Blog post ID"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CTA Block *</label>
          <select
            v-model.number="placementForm.cta_block"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="">Select CTA Block</option>
            <option v-for="block in ctaBlocks" :key="block.id" :value="block.id">
              {{ block.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Placement Type *</label>
          <select
            v-model="placementForm.placement_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="top">Top</option>
            <option value="middle">Middle</option>
            <option value="bottom">Bottom</option>
            <option value="sidebar">Sidebar</option>
            <option value="inline">Inline</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Position</label>
          <input
            v-model.number="placementForm.position"
            type="number"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="0"
          />
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="placementForm.is_active"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
          </label>
        </div>
        <div v-if="placementFormError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ placementFormError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closePlacementModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="savePlacement"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingPlacement ? 'Update' : 'Create') }}
        </button>
      </template>
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
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import blogPagesAPI from '@/api/blog-pages'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const activeTab = ref('blocks')
const blocksLoading = ref(false)
const placementsLoading = ref(false)
const saving = ref(false)
const ctaBlocks = ref([])
const placements = ref([])
const showBlockModal = ref(false)
const showPlacementModal = ref(false)
const editingBlock = ref(null)
const editingPlacement = ref(null)
const blockFormError = ref('')
const placementFormError = ref('')
const blockSearchQuery = ref('')
const blockTypeFilter = ref('')
const blockStatusFilter = ref('')

const blockForm = ref({
  name: '',
  cta_type: 'button',
  title: '',
  description: '',
  button_text: '',
  button_url: '',
  style: 'primary',
  is_active: true,
  custom_html: '',
})

const placementForm = ref({
  blog: null,
  cta_block: null,
  placement_type: 'top',
  position: 0,
  is_active: true,
})

const filteredBlocks = computed(() => {
  let filtered = ctaBlocks.value
  
  if (blockSearchQuery.value) {
    const query = blockSearchQuery.value.toLowerCase()
    filtered = filtered.filter(b => 
      (b.name && b.name.toLowerCase().includes(query)) ||
      (b.title && b.title.toLowerCase().includes(query))
    )
  }
  
  if (blockTypeFilter.value) {
    filtered = filtered.filter(b => b.cta_type === blockTypeFilter.value)
  }
  
  if (blockStatusFilter.value !== '') {
    const isActive = blockStatusFilter.value === 'true'
    filtered = filtered.filter(b => b.is_active === isActive)
  }
  
  return filtered
})

const uniqueBlogs = computed(() => {
  return [...new Set(placements.value.map(p => p.blog || p.blog_id))]
})

const debouncedLoadBlocks = debounce(() => {
  loadBlocks()
}, 300)

const formatCTAType = (type) => {
  if (!type) return 'Unknown'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatPlacementType = (type) => {
  if (!type) return 'Unknown'
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const getButtonStyle = (block) => {
  const styleMap = {
    primary: { backgroundColor: '#3B82F6', color: '#FFFFFF' },
    secondary: { backgroundColor: '#6B7280', color: '#FFFFFF' },
    success: { backgroundColor: '#10B981', color: '#FFFFFF' },
    warning: { backgroundColor: '#F59E0B', color: '#FFFFFF' },
    danger: { backgroundColor: '#EF4444', color: '#FFFFFF' },
    info: { backgroundColor: '#06B6D4', color: '#FFFFFF' },
    light: { backgroundColor: '#F3F4F6', color: '#1F2937' },
    dark: { backgroundColor: '#1F2937', color: '#FFFFFF' },
  }
  return styleMap[block.style] || styleMap.primary
}

const loadBlocks = async () => {
  blocksLoading.value = true
  try {
    const params = {}
    if (blockTypeFilter.value) params.cta_type = blockTypeFilter.value
    if (blockStatusFilter.value !== '') params.is_active = blockStatusFilter.value === 'true'
    
    const response = await blogPagesAPI.listCTAs(params)
    ctaBlocks.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load CTA blocks')
    console.error('Error loading blocks:', error)
  } finally {
    blocksLoading.value = false
  }
}

const loadPlacements = async () => {
  placementsLoading.value = true
  try {
    const response = await blogPagesAPI.listCTAPlacements()
    placements.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load CTA placements')
    console.error('Error loading placements:', error)
  } finally {
    placementsLoading.value = false
  }
}

const openAddBlockModal = () => {
  editingBlock.value = null
  blockForm.value = {
    name: '',
    cta_type: 'button',
    title: '',
    description: '',
    button_text: '',
    button_url: '',
    style: 'primary',
    is_active: true,
    custom_html: '',
  }
  blockFormError.value = ''
  showBlockModal.value = true
}

const editBlock = (block) => {
  editingBlock.value = block
  blockForm.value = {
    name: block.name || '',
    cta_type: block.cta_type || 'button',
    title: block.title || '',
    description: block.description || '',
    button_text: block.button_text || '',
    button_url: block.button_url || '',
    style: block.style || 'primary',
    is_active: block.is_active !== undefined ? block.is_active : true,
    custom_html: block.custom_html || '',
  }
  blockFormError.value = ''
  showBlockModal.value = true
}

const closeBlockModal = () => {
  showBlockModal.value = false
  editingBlock.value = null
  blockFormError.value = ''
}

const saveBlock = async () => {
  saving.value = true
  blockFormError.value = ''
  
  try {
    if (editingBlock.value) {
      await blogPagesAPI.updateCTA(editingBlock.value.id, blockForm.value)
      showSuccess('CTA block updated successfully')
    } else {
      await blogPagesAPI.createCTA(blockForm.value)
      showSuccess('CTA block created successfully')
    }
    
    closeBlockModal()
    loadBlocks()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save CTA block'
    blockFormError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const toggleBlockStatus = async (block) => {
  try {
    await blogPagesAPI.updateCTA(block.id, { is_active: !block.is_active })
    showSuccess(`CTA block ${block.is_active ? 'deactivated' : 'activated'}`)
    loadBlocks()
  } catch (error) {
    showError('Failed to update CTA block status')
  }
}

const deleteBlock = (block) => {
  confirm.showDestructive(
    'Delete CTA Block',
    `Are you sure you want to delete "${block.name}"?`,
    'This action cannot be undone. All placements using this block will be affected.',
    async () => {
      try {
        await blogPagesAPI.deleteCTA(block.id)
        showSuccess('CTA block deleted successfully')
        loadBlocks()
      } catch (error) {
        showError('Failed to delete CTA block')
      }
    }
  )
}

const openAddPlacementModal = () => {
  editingPlacement.value = null
  placementForm.value = {
    blog: null,
    cta_block: null,
    placement_type: 'top',
    position: 0,
    is_active: true,
  }
  placementFormError.value = ''
  showPlacementModal.value = true
}

const editPlacement = (placement) => {
  editingPlacement.value = placement
  placementForm.value = {
    blog: placement.blog || placement.blog_id || null,
    cta_block: placement.cta_block || placement.cta_block_id || null,
    placement_type: placement.placement_type || 'top',
    position: placement.position || 0,
    is_active: placement.is_active !== undefined ? placement.is_active : true,
  }
  placementFormError.value = ''
  showPlacementModal.value = true
}

const closePlacementModal = () => {
  showPlacementModal.value = false
  editingPlacement.value = null
  placementFormError.value = ''
}

const savePlacement = async () => {
  saving.value = true
  placementFormError.value = ''
  
  try {
    if (editingPlacement.value) {
      await blogPagesAPI.updateCTAPlacement(editingPlacement.value.id, placementForm.value)
      showSuccess('CTA placement updated successfully')
    } else {
      await blogPagesAPI.createCTAPlacement(placementForm.value)
      showSuccess('CTA placement created successfully')
    }
    
    closePlacementModal()
    loadPlacements()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save CTA placement'
    placementFormError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deletePlacement = (placement) => {
  confirm.showDestructive(
    'Delete CTA Placement',
    'Are you sure you want to delete this CTA placement?',
    'This action cannot be undone.',
    async () => {
      try {
        await blogPagesAPI.deleteCTAPlacement(placement.id)
        showSuccess('CTA placement deleted successfully')
        loadPlacements()
      } catch (error) {
        showError('Failed to delete CTA placement')
      }
    }
  )
}

onMounted(() => {
  loadBlocks()
  loadPlacements()
})
</script>

