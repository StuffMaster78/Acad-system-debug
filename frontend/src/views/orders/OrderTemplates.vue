<template>
  <div class="order-templates p-6">
    <PageHeader 
      title="Order Templates" 
      subtitle="Save and reuse your order configurations for quick reordering"
      :show-refresh="true"
      @refresh="loadTemplates"
    />
    
    <!-- Loading State -->
    <div v-if="loading" class="mt-6">
      <SkeletonLoader type="list" :rows="5" />
    </div>
    
    <!-- Error State -->
    <ErrorBoundary v-else-if="error" :error-message="error" @retry="loadTemplates">
      <div class="mt-6">
        <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 rounded">
          <p class="text-red-800 dark:text-red-200">{{ error }}</p>
          <button @click="loadTemplates" class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
            Retry
          </button>
        </div>
      </div>
    </ErrorBoundary>
    
    <!-- Empty State -->
    <EmptyState
      v-else-if="!loading && !error && templates.length === 0"
      icon="📋"
      title="No Templates Yet"
      description="Create your first order template to save time on future orders. Templates allow you to quickly reorder with the same settings."
      action-label="Create Template"
      :action-handler="openCreateModal"
    />
    
    <!-- Templates Grid -->
    <div v-else-if="!loading && !error" class="mt-6">
      <!-- Action Bar -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <button
            @click.prevent="openCreateModal"
            type="button"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>➕</span>
            Create Template
          </button>
          <button
            @click="showMostUsed = !showMostUsed"
            :class="[
              'px-4 py-2 rounded-lg transition-colors flex items-center gap-2',
              showMostUsed 
                ? 'bg-primary-100 text-primary-700 border border-primary-300' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            <span>⭐</span>
            Most Used
          </button>
          <button
            @click="showRecent = !showRecent"
            :class="[
              'px-4 py-2 rounded-lg transition-colors flex items-center gap-2',
              showRecent 
                ? 'bg-primary-100 text-primary-700 border border-primary-300' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            <span>🕒</span>
            Recent
          </button>
        </div>
        <div class="flex items-center gap-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search templates..."
            class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>
      
      <!-- Templates Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                {{ template.name }}
              </h3>
              <p v-if="template.description" class="text-sm text-gray-600 dark:text-gray-400">
                {{ template.description }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 dark:text-gray-400">
                Used {{ template.usage_count }}x
              </span>
            </div>
          </div>
          
          <!-- Template Details -->
          <div class="space-y-2 mb-4 text-sm">
            <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <span class="font-medium">Topic:</span>
              <span class="truncate">{{ template.topic }}</span>
            </div>
            <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <span class="font-medium">Type:</span>
              <span>{{ template.paper_type_name || 'N/A' }}</span>
            </div>
            <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <span class="font-medium">Level:</span>
              <span>{{ template.academic_level_name || 'N/A' }}</span>
            </div>
            <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
              <span class="font-medium">Pages:</span>
              <span>{{ template.number_of_pages }}</span>
            </div>
            <div v-if="template.last_used_at" class="text-xs text-gray-500 dark:text-gray-400">
              Last used: {{ formatDate(template.last_used_at) }}
            </div>
          </div>
          
          <!-- Actions -->
          <div class="flex items-center gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="createOrderFromTemplate(template)"
              :disabled="creatingOrder === template.id"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              {{ creatingOrder === template.id ? 'Creating...' : 'Create Order' }}
            </button>
            <button
              @click="openEditModal(template)"
              class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors text-sm"
              title="Edit Template"
            >
              ✏️
            </button>
            <button
              @click="confirmDelete(template)"
              class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors text-sm"
              title="Delete Template"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      :show="showDeleteConfirm"
      title="Delete Template"
      message="Are you sure you want to delete this template? This action cannot be undone."
      variant="danger"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="deleteTemplate"
      @cancel="showDeleteConfirm = false"
      @update:show="showDeleteConfirm = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { orderTemplatesAPI } from '@/api'
import PageHeader from '@/components/common/PageHeader.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { success, error: showError } = useToast()

const loading = ref(false)
const error = ref(null)
const templates = ref([])
const searchQuery = ref('')
const showMostUsed = ref(false)
const showRecent = ref(false)
const creatingOrder = ref(null)
const showDeleteConfirm = ref(false)
const templateToDelete = ref(null)

const filteredTemplates = computed(() => {
  let filtered = templates.value
  
  if (showMostUsed.value) {
    filtered = [...filtered].sort((a, b) => b.usage_count - a.usage_count)
  } else if (showRecent.value) {
    filtered = filtered.filter(t => t.last_used_at).sort((a, b) => 
      new Date(b.last_used_at) - new Date(a.last_used_at)
    )
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t => 
      t.name.toLowerCase().includes(query) ||
      t.topic.toLowerCase().includes(query) ||
      (t.description && t.description.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

const loadTemplates = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await orderTemplatesAPI.list()
    templates.value = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to load templates')
    console.error('Failed to load templates:', err)
  } finally {
    loading.value = false
  }
}


const openCreateModal = () => {
  router.push('/orders/templates/create')
}

const openEditModal = (template) => {
  router.push(`/orders/templates/${template.id}/edit`)
}


const createOrderFromTemplate = async (template) => {
  creatingOrder.value = template.id
  try {
    const response = await orderTemplatesAPI.createOrderFromTemplate(template.id, {})
    success('Order created successfully from template')
    router.push(`/orders/${response.data.order.id}`)
  } catch (err) {
    showError(getErrorMessage(err, 'Failed to create order from template'))
  } finally {
    creatingOrder.value = null
  }
}

const confirmDelete = (template) => {
  templateToDelete.value = template
  showDeleteConfirm.value = true
}

const deleteTemplate = async () => {
  if (!templateToDelete.value) return
  
  try {
    await orderTemplatesAPI.delete(templateToDelete.value.id)
    success('Template deleted successfully')
    await loadTemplates()
  } catch (err) {
    showError(getErrorMessage(err, 'Failed to delete template'))
  } finally {
    showDeleteConfirm.value = false
    templateToDelete.value = null
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadTemplates()
})
</script>

