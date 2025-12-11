<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Screened Words Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage words that are automatically flagged in messages</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="showBulkAddModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Bulk Add
        </button>
        <button
          @click="showAddModal = true"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Word
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4" v-if="stats">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Words</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_screened_words || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Flagged</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.total_flagged_messages || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Recent (7 days)</p>
        <p class="text-3xl font-bold text-orange-600 dark:text-orange-400">{{ stats.recent_flagged_count || 0 }}</p>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search words..."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <button
          @click="loadScreenedWords"
          :disabled="loading"
          class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Words List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading screened words...</p>
      </div>
      <div v-else-if="filteredWords.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <p class="text-lg font-medium">No screened words found</p>
        <p class="text-sm mt-2">Add your first word to start filtering messages</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Word</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="word in filteredWords"
              :key="word.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ word.word }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center gap-3">
                  <button
                    @click="editWord(word)"
                    class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteWord(word)"
                    class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click.self="closeModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full mx-auto my-auto">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">
            {{ showEditModal ? 'Edit Screened Word' : 'Add Screened Word' }}
          </h3>
          <button
            @click="closeModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Word <span class="text-red-500">*</span>
            </label>
            <input
              v-model="wordForm.word"
              type="text"
              placeholder="Enter word to screen..."
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
              @keyup.enter="saveWord"
            />
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Words are case-insensitive and will be automatically converted to lowercase
            </p>
          </div>
          <div v-if="formError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <p class="text-sm text-red-700 dark:text-red-400">{{ formError }}</p>
          </div>
          <div class="flex gap-3 pt-4">
            <button
              @click="closeModal"
              class="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              @click="saveWord"
              :disabled="saving || !wordForm.word.trim()"
              class="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
            >
              <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ saving ? 'Saving...' : (showEditModal ? 'Update' : 'Add') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Bulk Add Modal -->
    <div
      v-if="showBulkAddModal"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click.self="closeBulkModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full mx-auto my-auto max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">Bulk Add Screened Words</h3>
          <button
            @click="closeBulkModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Words (one per line or comma-separated)
            </label>
            <textarea
              v-model="bulkWordsText"
              rows="10"
              placeholder="Enter words, one per line or separated by commas..."
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100 font-mono text-sm"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              You can paste multiple words, one per line or separated by commas
            </p>
          </div>
          <div v-if="bulkResult" class="space-y-2">
            <div v-if="bulkResult.created_count > 0" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <p class="text-sm font-medium text-green-700 dark:text-green-400">
                ✓ Successfully added {{ bulkResult.created_count }} word(s)
              </p>
            </div>
            <div v-if="bulkResult.error_count > 0" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <p class="text-sm font-medium text-red-700 dark:text-red-400 mb-2">
                ✗ {{ bulkResult.error_count }} error(s) occurred
              </p>
              <ul class="text-xs text-red-600 dark:text-red-400 list-disc list-inside space-y-1">
                <li v-for="(error, index) in bulkResult.errors" :key="index">{{ error }}</li>
              </ul>
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button
              @click="closeBulkModal"
              class="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Close
            </button>
            <button
              @click="bulkAddWords"
              :disabled="saving || !bulkWordsText.trim()"
              class="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
            >
              <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ saving ? 'Adding...' : 'Add Words' }}
            </button>
          </div>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const words = ref([])
const stats = ref(null)
const searchQuery = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showBulkAddModal = ref(false)
const wordForm = ref({ word: '' })
const editingWord = ref(null)
const formError = ref('')
const bulkWordsText = ref('')
const bulkResult = ref(null)

const filteredWords = computed(() => {
  if (!searchQuery.value.trim()) {
    return words.value
  }
  const query = searchQuery.value.toLowerCase()
  return words.value.filter(w => w.word.toLowerCase().includes(query))
})

const loadScreenedWords = async () => {
  loading.value = true
  try {
    const response = await adminManagementAPI.get('/configs/screened-words/')
    words.value = response.data.results || response.data || []
    words.value.sort((a, b) => a.word.localeCompare(b.word))
  } catch (error) {
    console.error('Failed to load screened words:', error)
    showError('Failed to load screened words: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await adminManagementAPI.get('/configs/screened-words/stats/')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const saveWord = async () => {
  if (!wordForm.value.word.trim()) {
    formError.value = 'Please enter a word'
    return
  }

  saving.value = true
  formError.value = ''

  try {
    if (showEditModal.value && editingWord.value) {
      // Update existing word
      await adminManagementAPI.patch(`/configs/screened-words/${editingWord.value.id}/`, {
        word: wordForm.value.word.trim().toLowerCase()
      })
      showSuccess('Screened word updated successfully')
    } else {
      // Create new word
      await adminManagementAPI.post('/configs/screened-words/', {
        word: wordForm.value.word.trim().toLowerCase()
      })
      showSuccess('Screened word added successfully')
    }
    
    closeModal()
    await loadScreenedWords()
    await loadStats()
  } catch (error) {
    const errorMsg = error.response?.data?.word?.[0] || error.response?.data?.detail || error.message
    formError.value = errorMsg
    showError('Failed to save word: ' + errorMsg)
  } finally {
    saving.value = false
  }
}

const editWord = (word) => {
  editingWord.value = word
  wordForm.value.word = word.word
  showEditModal.value = true
  formError.value = ''
}

const deleteWord = async (word) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete the word "${word.word}"? This action cannot be undone.`,
    'Delete Screened Word',
    {
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )

  if (!confirmed) return

  try {
    await adminManagementAPI.delete(`/configs/screened-words/${word.id}/`)
    showSuccess('Screened word deleted successfully')
    await loadScreenedWords()
    await loadStats()
  } catch (error) {
    showError('Failed to delete word: ' + (error.response?.data?.detail || error.message))
  }
}

const bulkAddWords = async () => {
  if (!bulkWordsText.value.trim()) {
    return
  }

  saving.value = true
  bulkResult.value = null

  try {
    // Parse words from text (support both newline and comma separation)
    const text = bulkWordsText.value.trim()
    const wordList = text
      .split(/[,\n]/)
      .map(w => w.trim())
      .filter(w => w.length > 0)
      .map(w => w.toLowerCase())

    if (wordList.length === 0) {
      showError('Please enter at least one word')
      return
    }

    const response = await adminManagementAPI.post('/configs/screened-words/bulk_create/', {
      words: wordList
    })

    bulkResult.value = response.data
    showSuccess(`Successfully added ${response.data.created_count} word(s)`)
    
    // Clear text if all succeeded
    if (response.data.error_count === 0) {
      bulkWordsText.value = ''
    }
    
    await loadScreenedWords()
    await loadStats()
  } catch (error) {
    showError('Failed to bulk add words: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  wordForm.value = { word: '' }
  editingWord.value = null
  formError.value = ''
}

const closeBulkModal = () => {
  showBulkAddModal.value = false
  bulkWordsText.value = ''
  bulkResult.value = null
}

onMounted(async () => {
  await Promise.all([loadScreenedWords(), loadStats()])
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

