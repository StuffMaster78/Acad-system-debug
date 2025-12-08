<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Category Publishing Targets</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Set monthly publishing targets per category for each website</p>
      </div>
    </div>

    <!-- Website Switcher -->
    <div class="card p-4 dark:bg-gray-800 dark:border-gray-700">
      <WebsiteSwitcher
        v-model="selectedWebsiteId"
        :websites="availableWebsites"
        :can-select-website="canSelectWebsite"
        :show-all-option="false"
        label="Select Website"
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

    <!-- Loading State -->
    <div v-if="loading" class="card dark:bg-gray-800 dark:border-gray-700">
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span class="ml-3 text-gray-600 dark:text-gray-400">Loading category targets...</span>
      </div>
    </div>

    <!-- Empty State - No Website Selected -->
    <div v-else-if="!selectedWebsiteId" class="card dark:bg-gray-800 dark:border-gray-700">
      <div class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">Select a Website</h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Please select a website to view and manage category publishing targets.</p>
      </div>
    </div>

    <!-- Category Targets List -->
    <div v-else-if="selectedWebsiteId && !loading" class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Category Targets</h2>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-150 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Category Target
        </button>
      </div>

      <div v-if="categoryTargets.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="target in categoryTargets"
          :key="target.id"
          class="card dark:bg-gray-800 dark:border-gray-700 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-lg transition-shadow duration-200"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="font-semibold text-lg text-gray-900 dark:text-gray-100 mb-1">
                {{ target.category_name || 'Unnamed Category' }}
              </h3>
              <p v-if="target.category_slug" class="text-sm text-gray-500 dark:text-gray-400">
                {{ target.category_slug }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="editTarget(target)"
                class="p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors duration-150"
                title="Edit target"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button
                @click="deleteTarget(target.id)"
                class="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors duration-150"
                title="Delete target"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Monthly Target:</span>
              <span class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ target.monthly_target }} posts</span>
            </div>

            <div v-if="target.current_month_stats" class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">This Month:</span>
                <span class="font-semibold text-gray-900 dark:text-gray-100">
                  {{ target.current_month_stats.published || 0 }} / {{ target.current_month_stats.target || target.monthly_target }}
                </span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="getProgressColor(target.current_month_stats.percentage)"
                  :style="{ width: `${Math.min(target.current_month_stats.percentage || 0, 100)}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                {{ Math.round(target.current_month_stats.percentage || 0) }}% complete
              </p>
            </div>
            <div v-else class="text-sm text-gray-500 dark:text-gray-400 italic">
              No statistics available for this month
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
              <span class="text-xs text-gray-500 dark:text-gray-400">Status:</span>
              <span
                :class="target.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'"
                class="px-2 py-1 rounded-full text-xs font-medium"
              >
                {{ target.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="card dark:bg-gray-800 dark:border-gray-700">
        <div class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">No Category Targets</h3>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Get started by creating a category publishing target.</p>
          <button
            @click="showCreateModal = true"
            class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-150"
          >
            Add Category Target
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div
      v-if="errorMessage"
      class="p-4 rounded-lg border transition-colors duration-200"
      :class="errorSuccess ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800'"
    >
      <div class="flex items-center justify-between">
        <span>{{ errorMessage }}</span>
        <button
          @click="errorMessage = ''"
          class="text-current hover:opacity-70"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingTarget" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full max-h-[90vh] my-auto flex flex-col shadow-xl">
        <!-- Header - Fixed -->
        <div class="flex items-center justify-between p-6 pb-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {{ editingTarget ? 'Edit Category Target' : 'Create Category Target' }}
          </h2>
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
          <form id="category-target-form" @submit.prevent="saveTarget" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Category *</label>
              <select
                v-model="targetForm.category_id"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Select Category</option>
                <option
                  v-for="cat in availableCategories"
                  :key="cat.id"
                  :value="cat.id"
                >
                  {{ cat.name }}
                </option>
              </select>
              <p v-if="availableCategories.length === 0" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                No categories available for this website. Create categories first.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Monthly Target *</label>
              <input
                v-model.number="targetForm.monthly_target"
                type="number"
                min="1"
                max="1000"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Number of posts to publish in this category per month
              </p>
            </div>

            <div class="flex items-center">
              <input
                v-model="targetForm.is_active"
                type="checkbox"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700"
              />
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</label>
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
            form="category-target-form"
            :disabled="saving"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors duration-150 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ saving ? 'Saving...' : (editingTarget ? 'Update' : 'Create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'
import WebsiteSwitcher from '@/components/common/WebsiteSwitcher.vue'
import WebsiteContextBanner from '@/components/common/WebsiteContextBanner.vue'

const availableWebsites = ref([])
const canSelectWebsite = ref(true)
const selectedWebsiteId = ref(null)
const categoryTargets = ref([])
const availableCategories = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const editingTarget = ref(null)
const errorMessage = ref('')
const errorSuccess = ref(false)

const targetForm = ref({
  website_id: null,
  category_id: null,
  monthly_target: 1,
  is_active: true
})

// Computed: Selected website object
const selectedWebsite = computed(() => {
  if (!selectedWebsiteId.value) return null
  return availableWebsites.value.find(w => w.id === selectedWebsiteId.value) || null
})

// Computed: Website stats
const websiteStats = computed(() => {
  if (!selectedWebsite.value) return null
  
  return {
    totalPosts: categoryTargets.value.length,
    publishedPosts: categoryTargets.value.filter(t => t.is_active).length,
    draftPosts: categoryTargets.value.filter(t => !t.is_active).length,
    totalCategories: availableCategories.value.length,
    activeCategories: availableCategories.value.filter(c => c.is_active !== false).length,
    totalAuthors: 0,
  }
})

const loadWebsites = async () => {
  try {
    // Try to get available websites from blog pages API first (includes permission info)
    try {
      const res = await blogPagesAPI.getAvailableWebsites()
      availableWebsites.value = res.data?.websites || []
      canSelectWebsite.value = res.data?.can_select_website || false
    } catch {
      // Fallback to websites API if blog pages endpoint doesn't exist
      const res = await websitesAPI.listWebsites({ is_active: true })
      availableWebsites.value = res.data?.results || res.data || []
      canSelectWebsite.value = true // Assume true if using fallback
    }
    
    // Auto-select website if only one available or if user can't select
    if (availableWebsites.value.length === 1) {
      selectedWebsiteId.value = availableWebsites.value[0].id
    } else if (!canSelectWebsite.value && availableWebsites.value.length > 0) {
      // Regular admin: auto-select their assigned website
      selectedWebsiteId.value = availableWebsites.value[0].id
    }
  } catch (e) {
    console.error('Failed to load websites:', e)
    showError('Failed to load websites. Please refresh the page.', false)
  }
}

const loadTargets = async () => {
  if (!selectedWebsiteId.value) {
    categoryTargets.value = []
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const res = await blogPagesAPI.getCategoryTargetsByWebsite({
      website_id: selectedWebsiteId.value
    })
    categoryTargets.value = res.data || []
  } catch (e) {
    console.error('Failed to load category targets:', e)
    showError('Failed to load category targets. Please try again.', false)
    categoryTargets.value = []
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  if (!selectedWebsiteId.value) return

  try {
    const res = await blogPagesAPI.listCategories({
      website: selectedWebsiteId.value
    })
    availableCategories.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load categories:', e)
    showError('Failed to load categories. Please try again.', false)
  }
}

const handleWebsiteChange = (websiteId) => {
  selectedWebsiteId.value = websiteId
  if (websiteId) {
    loadTargets()
    loadCategories()
  } else {
    categoryTargets.value = []
    availableCategories.value = []
  }
}

const editTarget = (target) => {
  editingTarget.value = target
  targetForm.value = {
    website_id: target.website || target.website_id,
    category_id: target.category || target.category_id,
    monthly_target: target.monthly_target || 1,
    is_active: target.is_active !== undefined ? target.is_active : true
  }
  showCreateModal.value = true
}

const saveTarget = async () => {
  saving.value = true
  errorMessage.value = ''
  
  try {
    targetForm.value.website_id = selectedWebsiteId.value

    if (editingTarget.value) {
      await blogPagesAPI.updateCategoryPublishingTarget(editingTarget.value.id, targetForm.value)
      showError('Category target updated successfully!', true)
    } else {
      await blogPagesAPI.createCategoryPublishingTarget(targetForm.value)
      showError('Category target created successfully!', true)
    }

    closeModal()
    await loadTargets()
  } catch (e) {
    console.error('Failed to save target:', e)
    const errorMsg = e.response?.data?.detail || e.response?.data?.message || 'Failed to save category target. Please try again.'
    showError(errorMsg, false)
  } finally {
    saving.value = false
  }
}

const deleteTarget = async (id) => {
  if (!confirm('Are you sure you want to delete this category target? This action cannot be undone.')) return

  try {
    await blogPagesAPI.deleteCategoryPublishingTarget(id)
    showError('Category target deleted successfully!', true)
    await loadTargets()
  } catch (e) {
    console.error('Failed to delete target:', e)
    const errorMsg = e.response?.data?.detail || e.response?.data?.message || 'Failed to delete category target. Please try again.'
    showError(errorMsg, false)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingTarget.value = null
  targetForm.value = {
    website_id: null,
    category_id: null,
    monthly_target: 1,
    is_active: true
  }
}

const showError = (message, success = false) => {
  errorMessage.value = message
  errorSuccess.value = success
  if (success) {
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
  }
}

const getProgressColor = (percentage) => {
  if (percentage >= 100) return 'bg-green-500 dark:bg-green-600'
  if (percentage >= 75) return 'bg-blue-500 dark:bg-blue-600'
  if (percentage >= 50) return 'bg-yellow-500 dark:bg-yellow-600'
  return 'bg-orange-500 dark:bg-orange-600'
}

watch(selectedWebsiteId, () => {
  if (selectedWebsiteId.value) {
    loadTargets()
    loadCategories()
  } else {
    categoryTargets.value = []
    availableCategories.value = []
  }
})

onMounted(async () => {
  await loadWebsites()
})
</script>
