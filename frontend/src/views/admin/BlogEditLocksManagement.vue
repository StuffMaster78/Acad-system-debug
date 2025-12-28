<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Edit Locks Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage concurrent editing locks for blog posts</p>
      </div>
      <button @click="loadLocks" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active Locks</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Expired Locks</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.expired }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Locks</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Locked Posts</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.locked_posts }}</p>
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
            placeholder="Search posts..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.status"
            @change="loadLocks"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Locks List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!locks.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No edit locks found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Locked By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Locked At</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Expires At</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="lock in locks" :key="lock.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ lock.blog_post?.title || lock.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ lock.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ lock.locked_by?.username || lock.locked_by?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(lock.locked_at || lock.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(lock.expires_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="isLockExpired(lock) ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ isLockExpired(lock) ? 'Expired' : 'Active' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewLock(lock)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="releaseLock(lock)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Release</button>
                  <button @click="deleteLock(lock)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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
const locks = ref([])
const stats = ref({ total: 0, active: 0, expired: 0, locked_posts: 0 })

const filters = ref({
  search: '',
  status: '',
})

const debouncedSearch = debounce(() => {
  loadLocks()
}, 300)

const loadLocks = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    
    const res = await blogPagesAPI.listEditLocks(params)
    locks.value = res.data?.results || res.data || []
    
    // Calculate stats
    const now = new Date()
    const active = locks.value.filter(l => !isLockExpired(l))
    const expired = locks.value.filter(l => isLockExpired(l))
    const uniquePosts = new Set(locks.value.map(l => l.blog_post?.id || l.blog_post_id))
    
    stats.value = {
      total: locks.value.length,
      active: active.length,
      expired: expired.length,
      locked_posts: uniquePosts.size,
    }
    
    // Filter by status if selected
    if (filters.value.status === 'active') {
      locks.value = active
    } else if (filters.value.status === 'expired') {
      locks.value = expired
    }
  } catch (error) {
    console.error('Failed to load locks:', error)
    showError('Failed to load locks: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const isLockExpired = (lock) => {
  if (!lock.expires_at) return false
  return new Date(lock.expires_at) < new Date()
}

const viewLock = (lock) => {
  alert(`Edit Lock\n\nBlog: ${lock.blog_post?.title || lock.blog_post_id}\nLocked By: ${lock.locked_by?.username || lock.locked_by?.email}\nLocked At: ${formatDate(lock.locked_at || lock.created_at)}\nExpires At: ${formatDate(lock.expires_at)}\nStatus: ${isLockExpired(lock) ? 'Expired' : 'Active'}`)
}

const releaseLock = async (lock) => {
  const confirmed = await confirm.showWarning(
    'Are you sure you want to release this edit lock?',
    'Release Edit Lock',
    {
      details: 'This will allow other users to edit the blog post. The lock will be removed.',
      confirmText: 'Release',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.releaseEditLock(lock.id)
    showSuccess('Edit lock released successfully')
    await loadLocks()
  } catch (error) {
    console.error('Failed to release lock:', error)
    showError('Failed to release lock: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteLock = async (lock) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this edit lock?',
    'Delete Edit Lock',
    {
      details: 'This action cannot be undone. The edit lock will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteEditLock(lock.id)
    showSuccess('Edit lock deleted successfully')
    await loadLocks()
  } catch (error) {
    console.error('Failed to delete lock:', error)
    showError('Failed to delete lock: ' + (error.response?.data?.detail || error.message))
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  loadLocks()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadLocks()
})
</script>

<style scoped>
@reference "tailwindcss";
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

