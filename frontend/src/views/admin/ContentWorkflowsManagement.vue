<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Content Workflows Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage editorial workflows, review comments, and content transitions</p>
      </div>
      <button @click="loadWorkflows" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Workflows</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">In Review</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.in_review }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.approved }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Pending Comments</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.pending_comments }}</p>
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

    <!-- Workflows List -->
    <div v-if="activeTab === 'workflows'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Blog Post Workflows</h2>
        <div class="flex gap-2">
          <select
            v-model="filters.workflow_status"
            @change="loadWorkflows"
            class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="in_review">In Review</option>
            <option value="approved">Approved</option>
            <option value="published">Published</option>
          </select>
        </div>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!workflows.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No workflows found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Current Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Assigned To</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="workflow in workflows" :key="workflow.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ workflow.blog_post?.title || workflow.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ workflow.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(workflow.current_status)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ workflow.current_status || 'draft' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ workflow.assigned_to?.username || workflow.assigned_to?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(workflow.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewWorkflow(workflow)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="viewComments(workflow)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Comments</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Review Comments -->
    <div v-if="activeTab === 'comments'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Review Comments</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!reviewComments.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No review comments found</p>
      </div>
      <div v-else class="p-6 space-y-4">
        <div
          v-for="comment in reviewComments"
          :key="comment.id"
          class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
        >
          <div class="flex items-start justify-between mb-2">
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ comment.author?.username || comment.author?.email || 'Unknown' }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">{{ formatDate(comment.created_at) }}</p>
            </div>
            <span :class="getCommentTypeBadgeClass(comment.comment_type)" class="px-2 py-1 text-xs font-medium rounded-full">
              {{ comment.comment_type || 'general' }}
            </span>
          </div>
          <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">{{ comment.content }}</p>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            Blog Post: {{ comment.blog_post?.title || comment.blog_post_id || '—' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Workflow Transitions -->
    <div v-if="activeTab === 'transitions'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Workflow Transitions</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!transitions.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No transitions found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">From</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">To</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">User</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="transition in transitions" :key="transition.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ transition.blog_post?.title || transition.blog_post_id || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                  {{ transition.from_status || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ transition.to_status || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ transition.user?.username || transition.user?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(transition.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import { useToast } from '@/composables/useToast'

const { showError } = useToast()

const loading = ref(false)
const activeTab = ref('workflows')
const workflows = ref([])
const reviewComments = ref([])
const transitions = ref([])
const stats = ref({ total: 0, in_review: 0, approved: 0, pending_comments: 0 })

const filters = ref({
  workflow_status: '',
})

const tabs = [
  { id: 'workflows', label: 'Workflows' },
  { id: 'comments', label: 'Review Comments' },
  { id: 'transitions', label: 'Transitions' },
]

const loadWorkflows = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.workflow_status) params.status = filters.value.workflow_status
    
    const res = await blogPagesAPI.listBlogWorkflows(params)
    workflows.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: workflows.value.length,
      in_review: workflows.value.filter(w => w.current_status === 'in_review').length,
      approved: workflows.value.filter(w => w.current_status === 'approved').length,
      pending_comments: reviewComments.value.filter(c => !c.resolved).length,
    }
  } catch (error) {
    console.error('Failed to load workflows:', error)
    showError('Failed to load workflows: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadReviewComments = async () => {
  loading.value = true
  try {
    const res = await blogPagesAPI.listReviewComments({})
    reviewComments.value = res.data?.results || res.data || []
    
    // Update stats
    stats.value.pending_comments = reviewComments.value.filter(c => !c.resolved).length
  } catch (error) {
    console.error('Failed to load review comments:', error)
    showError('Failed to load review comments: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadTransitions = async () => {
  loading.value = true
  try {
    const res = await blogPagesAPI.listWorkflowTransitions({})
    transitions.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load transitions:', error)
    showError('Failed to load transitions: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewWorkflow = (workflow) => {
  // Show workflow details
  alert(`Workflow: ${workflow.id}\nStatus: ${workflow.current_status}\nBlog Post: ${workflow.blog_post?.title || workflow.blog_post_id}`)
}

const viewComments = (workflow) => {
  activeTab.value = 'comments'
  // Filter comments for this workflow
  // In a real implementation, you'd filter by blog_post_id
}

const getStatusBadgeClass = (status) => {
  const classes = {
    draft: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    in_review: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    approved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    published: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const getCommentTypeBadgeClass = (type) => {
  const classes = {
    suggestion: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    issue: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    approval: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    general: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  }
  return classes[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

watch(activeTab, () => {
  if (activeTab.value === 'workflows') {
    loadWorkflows()
  } else if (activeTab.value === 'comments') {
    loadReviewComments()
  } else if (activeTab.value === 'transitions') {
    loadTransitions()
  }
})

onMounted(() => {
  loadWorkflows()
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

