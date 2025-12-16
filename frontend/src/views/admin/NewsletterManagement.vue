<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Newsletter Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Create, manage, and send newsletters to subscribers</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Newsletter
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Newsletters</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Draft</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.draft }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Scheduled</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.scheduled }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Sent</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.sent }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
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
            placeholder="Search newsletters..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.status"
            @change="loadNewsletters"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="sent">Sent</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Newsletters List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!newsletters.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No newsletters found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Subject</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Recipients</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Scheduled</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Sent</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="newsletter in newsletters" :key="newsletter.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ newsletter.title }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ newsletter.subject || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(newsletter.status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ newsletter.status || 'draft' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ newsletter.recipient_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(newsletter.scheduled_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(newsletter.sent_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewNewsletter(newsletter)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editNewsletter(newsletter)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button v-if="newsletter.status === 'draft'" @click="sendNewsletter(newsletter)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Send</button>
                  <button @click="deleteNewsletter(newsletter)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingNewsletter" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingNewsletter ? 'Edit Newsletter' : 'Create Newsletter' }}
          </h3>
        </div>
        <form @submit.prevent="saveNewsletter" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Title *</label>
            <input
              v-model="newsletterForm.title"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Subject *</label>
            <input
              v-model="newsletterForm.subject"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content *</label>
            <textarea
              v-model="newsletterForm.content"
              rows="10"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Scheduled At</label>
              <input
                v-model="newsletterForm.scheduled_at"
                type="datetime-local"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
              <select
                v-model="newsletterForm.status"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="draft">Draft</option>
                <option value="scheduled">Scheduled</option>
                <option value="sent">Sent</option>
              </select>
            </div>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingNewsletter ? 'Update' : 'Create') }}
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
import newslettersAPI from '@/api/newsletters'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'

const { showSuccess, showError } = useToast()

const loading = ref(false)
const saving = ref(false)
const newsletters = ref([])
const stats = ref({ total: 0, draft: 0, scheduled: 0, sent: 0 })
const activeTab = ref('all')
const showCreateModal = ref(false)
const editingNewsletter = ref(null)

const tabs = [
  { id: 'all', label: 'All Newsletters' },
  { id: 'draft', label: 'Drafts' },
  { id: 'scheduled', label: 'Scheduled' },
  { id: 'sent', label: 'Sent' },
]

const filters = ref({
  search: '',
  status: '',
})

const newsletterForm = ref({
  title: '',
  subject: '',
  content: '',
  scheduled_at: '',
  status: 'draft',
})

const debouncedSearch = debounce(() => {
  loadNewsletters()
}, 300)

const loadNewsletters = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (activeTab.value !== 'all') params.status = activeTab.value
    
    const res = await newslettersAPI.listNewsletters(params)
    newsletters.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: newsletters.value.length,
      draft: newsletters.value.filter(n => n.status === 'draft').length,
      scheduled: newsletters.value.filter(n => n.status === 'scheduled').length,
      sent: newsletters.value.filter(n => n.status === 'sent').length,
    }
  } catch (error) {
    console.error('Failed to load newsletters:', error)
    showError('Failed to load newsletters: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveNewsletter = async () => {
  saving.value = true
  try {
    const data = {
      ...newsletterForm.value,
      scheduled_at: newsletterForm.value.scheduled_at || null,
    }
    
    if (editingNewsletter.value) {
      await newslettersAPI.updateNewsletter(editingNewsletter.value.id, data)
      showSuccess('Newsletter updated successfully')
    } else {
      await newslettersAPI.createNewsletter(data)
      showSuccess('Newsletter created successfully')
    }
    
    closeModal()
    await loadNewsletters()
  } catch (error) {
    console.error('Failed to save newsletter:', error)
    showError('Failed to save newsletter: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editNewsletter = (newsletter) => {
  editingNewsletter.value = newsletter
  newsletterForm.value = {
    title: newsletter.title || '',
    subject: newsletter.subject || '',
    content: newsletter.content || '',
    scheduled_at: newsletter.scheduled_at ? new Date(newsletter.scheduled_at).toISOString().slice(0, 16) : '',
    status: newsletter.status || 'draft',
  }
  showCreateModal.value = true
}

const viewNewsletter = (newsletter) => {
  // Navigate to newsletter detail or open view modal
  window.open(`/admin/newsletters/${newsletter.id}`, '_blank')
}

const sendNewsletter = async (newsletter) => {
  const confirmed = await confirm.showWarning(
    `Are you sure you want to send "${newsletter.title}" to all subscribers?`,
    'Send Newsletter',
    {
      details: 'This will send the newsletter to all active subscribers. This action cannot be undone.',
      confirmText: 'Send',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await newslettersAPI.sendNewsletter(newsletter.id, {})
    showSuccess('Newsletter sent successfully')
    await loadNewsletters()
  } catch (error) {
    console.error('Failed to send newsletter:', error)
    showError('Failed to send newsletter: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteNewsletter = async (newsletter) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${newsletter.title}"?`,
    'Delete Newsletter',
    {
      details: 'This action cannot be undone. The newsletter will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await newslettersAPI.deleteNewsletter(newsletter.id)
    showSuccess('Newsletter deleted successfully')
    await loadNewsletters()
  } catch (error) {
    console.error('Failed to delete newsletter:', error)
    showError('Failed to delete newsletter: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingNewsletter.value = null
  newsletterForm.value = {
    title: '',
    subject: '',
    content: '',
    scheduled_at: '',
    status: 'draft',
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  loadNewsletters()
}

const getStatusBadgeClass = (status) => {
  const classes = {
    draft: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    scheduled: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    sent: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

watch(activeTab, () => {
  loadNewsletters()
})

onMounted(() => {
  loadNewsletters()
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

