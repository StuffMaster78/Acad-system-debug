<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">FAQ Schema Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage FAQ structured data (Schema.org) for blog posts</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create FAQ Schema
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total FAQs</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Questions</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total_questions }}</p>
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
            placeholder="Search FAQs..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Blog Post</label>
          <input
            v-model="filters.blog_post"
            type="number"
            placeholder="Filter by Blog Post ID..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @input="loadFAQs"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- FAQs List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!faqs.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No FAQ schemas found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First FAQ Schema</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Questions</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="faq in faqs" :key="faq.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ faq.blog_post?.title || faq.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ faq.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ faq.questions?.length || faq.question_count || 0 }} questions
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="faq.is_active !== false ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ faq.is_active !== false ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(faq.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewFAQ(faq)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editFAQ(faq)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteFAQ(faq)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingFAQ" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingFAQ ? 'Edit FAQ Schema' : 'Create FAQ Schema' }}
          </h3>
        </div>
        <form @submit.prevent="saveFAQ" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Blog Post ID *</label>
            <input
              v-model.number="faqForm.blog_post"
              type="number"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Questions & Answers *</label>
            <div class="space-y-3">
              <div v-for="(qa, index) in faqForm.questions" :key="index" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Question {{ index + 1 }}</span>
                  <button type="button" @click="removeQuestion(index)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm">Remove</button>
                </div>
                <input
                  v-model="qa.question"
                  type="text"
                  :placeholder="`Question ${index + 1}`"
                  required
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 mb-2"
                />
                <textarea
                  v-model="qa.answer"
                  rows="3"
                  :placeholder="`Answer ${index + 1}`"
                  required
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                ></textarea>
              </div>
              <button type="button" @click="addQuestion" class="btn btn-secondary w-full">
                + Add Question
              </button>
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving || faqForm.questions.length === 0" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingFAQ ? 'Update' : 'Create') }}
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
const faqs = ref([])
const stats = ref({ total: 0, active: 0, total_questions: 0 })
const showCreateModal = ref(false)
const editingFAQ = ref(null)

const filters = ref({
  search: '',
  blog_post: '',
})

const faqForm = ref({
  blog_post: null,
  questions: [{ question: '', answer: '' }],
})

const debouncedSearch = debounce(() => {
  loadFAQs()
}, 300)

const loadFAQs = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    
    const res = await blogPagesAPI.listFAQs(params)
    faqs.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: faqs.value.length,
      active: faqs.value.filter(f => f.is_active !== false).length,
      total_questions: faqs.value.reduce((sum, f) => sum + (f.questions?.length || f.question_count || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load FAQs:', error)
    showError('Failed to load FAQs: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveFAQ = async () => {
  if (faqForm.value.questions.length === 0) {
    showError('Please add at least one question')
    return
  }
  
  saving.value = true
  try {
    const data = {
      blog_post: faqForm.value.blog_post,
      questions: faqForm.value.questions.filter(qa => qa.question && qa.answer),
    }
    
    if (editingFAQ.value) {
      await blogPagesAPI.updateFAQ(editingFAQ.value.id, data)
      showSuccess('FAQ schema updated successfully')
    } else {
      await blogPagesAPI.createFAQ(data)
      showSuccess('FAQ schema created successfully')
    }
    
    closeModal()
    await loadFAQs()
  } catch (error) {
    console.error('Failed to save FAQ:', error)
    showError('Failed to save FAQ: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editFAQ = (faq) => {
  editingFAQ.value = faq
  faqForm.value = {
    blog_post: faq.blog_post?.id || faq.blog_post_id || null,
    questions: faq.questions && faq.questions.length > 0 
      ? faq.questions.map(q => ({ question: q.question || '', answer: q.answer || '' }))
      : [{ question: '', answer: '' }],
  }
  showCreateModal.value = true
}

const viewFAQ = (faq) => {
  // Show FAQ details
  const questions = faq.questions || []
  const preview = questions.map((q, i) => `Q${i + 1}: ${q.question}\nA${i + 1}: ${q.answer}`).join('\n\n')
  alert(`FAQ Schema for: ${faq.blog_post?.title || faq.blog_post_id}\n\n${preview || 'No questions'}`)
}

const deleteFAQ = async (faq) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this FAQ schema?',
    'Delete FAQ Schema',
    {
      details: 'This action cannot be undone. The FAQ schema will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteFAQ(faq.id)
    showSuccess('FAQ schema deleted successfully')
    await loadFAQs()
  } catch (error) {
    console.error('Failed to delete FAQ:', error)
    showError('Failed to delete FAQ: ' + (error.response?.data?.detail || error.message))
  }
}

const addQuestion = () => {
  faqForm.value.questions.push({ question: '', answer: '' })
}

const removeQuestion = (index) => {
  if (faqForm.value.questions.length > 1) {
    faqForm.value.questions.splice(index, 1)
  } else {
    showError('At least one question is required')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingFAQ.value = null
  faqForm.value = {
    blog_post: null,
    questions: [{ question: '', answer: '' }],
  }
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '' }
  loadFAQs()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadFAQs()
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


