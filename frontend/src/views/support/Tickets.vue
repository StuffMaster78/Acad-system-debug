<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Recent Tickets</h1>
        <p class="mt-2 text-gray-600">View and respond to recent support tickets</p>
      </div>
      <div class="flex gap-3">
        <button @click="showCreateModal = true" class="btn btn-primary">
          + Create Ticket
        </button>
        <button @click="loadTickets" :disabled="loading" class="btn btn-secondary">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Open Tickets</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.open || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.in_progress || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">High Priority</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.high_priority || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Resolved Today</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.resolved_today || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search tickets..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="filterTickets" class="w-full border rounded px-3 py-2">
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="closed">Closed</option>
            <option value="awaiting_response">Awaiting Response</option>
            <option value="escalated">Escalated</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Priority</label>
          <select v-model="filters.priority" @change="filterTickets" class="w-full border rounded px-3 py-2">
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Category</label>
          <select v-model="filters.category" @change="filterTickets" class="w-full border rounded px-3 py-2">
            <option value="">All Categories</option>
            <option value="general">General Inquiry</option>
            <option value="payment">Payment Issues</option>
            <option value="technical">Technical Support</option>
            <option value="feedback">Feedback</option>
            <option value="order">Order Issues</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Recent Tickets Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Client</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned To</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="ticket in filteredTickets" :key="ticket.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{{ ticket.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ ticket.title }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ ticket.created_by?.username || ticket.created_by?.email || 'N/A' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ ticket.assigned_to?.username || 'Unassigned' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusBadgeClass(ticket.status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ ticket.status_display || ticket.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getPriorityBadgeClass(ticket.priority)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ ticket.priority_display || ticket.priority }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(ticket.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button @click="viewTicket(ticket)" class="text-blue-600 hover:text-blue-900 mr-3">View</button>
              <button v-if="!ticket.assigned_to" @click="assignToMe(ticket)" class="text-green-600 hover:text-green-900 mr-3">Assign</button>
              <button @click="respondToTicket(ticket)" class="text-purple-600 hover:text-purple-900">Respond</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && filteredTickets.length === 0" class="text-center py-12 text-gray-500">
        <p>No tickets found</p>
      </div>
    </div>

    <!-- Ticket Detail Modal -->
    <div v-if="selectedTicket" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Ticket #{{ selectedTicket.id }}</h2>
            <button @click="selectedTicket = null" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-6">
          <!-- Ticket Info -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <span :class="getStatusBadgeClass(selectedTicket.status)" class="px-3 py-1 text-sm font-semibold rounded-full">
                {{ selectedTicket.status_display || selectedTicket.status }}
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <span :class="getPriorityBadgeClass(selectedTicket.priority)" class="px-3 py-1 text-sm font-semibold rounded-full">
                {{ selectedTicket.priority_display || selectedTicket.priority }}
              </span>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <p class="text-sm text-gray-900">{{ selectedTicket.category_display || selectedTicket.category }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
              <p class="text-sm text-gray-900">{{ selectedTicket.assigned_to ? selectedTicket.assigned_to.username : 'Unassigned' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Created By</label>
              <p class="text-sm text-gray-900">{{ selectedTicket.created_by?.username || selectedTicket.created_by?.email || 'N/A' }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Created</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedTicket.created_at) }}</p>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <p class="text-sm text-gray-900 whitespace-pre-wrap">{{ selectedTicket.description }}</p>
          </div>

          <!-- Messages -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Messages</h3>
            <div v-if="messagesLoading" class="text-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            </div>
            <div v-else class="space-y-4 max-h-64 overflow-y-auto">
              <div v-for="message in messages" :key="message.id" class="border rounded p-3">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-900">{{ message.sender ? message.sender.username : 'System' }}</span>
                  <span class="text-xs text-gray-500">{{ formatDate(message.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-700">{{ message.message }}</p>
              </div>
              <div v-if="messages.length === 0" class="text-center py-4 text-gray-500">
                <p>No messages yet</p>
              </div>
            </div>
          </div>

          <!-- Add Message -->
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3">Add Message</h3>
            <textarea v-model="messageForm.message" rows="4" class="w-full border rounded px-3 py-2" placeholder="Type your message..."></textarea>
            <button @click="sendMessage" :disabled="sendingMessage" class="mt-2 btn btn-primary">
              {{ sendingMessage ? 'Sending...' : 'Send Message' }}
            </button>
          </div>

          <!-- Actions -->
          <div class="border-t pt-4">
            <div class="flex justify-end space-x-3">
              <button v-if="!selectedTicket.assigned_to" @click="assignToMe(selectedTicket)" class="btn btn-secondary">Assign to Me</button>
              <button v-if="!selectedTicket.is_escalated" @click="escalateTicket(selectedTicket)" class="btn btn-warning">Escalate</button>
              <button @click="selectedTicket = null" class="btn btn-secondary">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-gray-900">Create New Ticket</h2>
            <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
        <div class="p-6 space-y-4">
          <!-- User Selection (Recipient) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Ticket For (User) <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model="createForm.userSearch"
                @input="searchUsers"
                @focus="showUserDropdown = true"
                type="text"
                placeholder="Search by username or email..."
                class="w-full border rounded px-3 py-2"
              />
              <div v-if="showUserDropdown && userSearchResults.length" class="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                <div
                  v-for="user in userSearchResults"
                  :key="user.id"
                  @click="selectUser(user)"
                  class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-b-0"
                >
                  <div class="font-medium">{{ user.username }}</div>
                  <div class="text-xs text-gray-500">{{ user.email }} · {{ user.role }}</div>
                </div>
              </div>
              <div v-if="createForm.created_by" class="mt-2 flex items-center gap-2 p-2 bg-gray-50 rounded">
                <span class="text-sm font-medium">{{ selectedUser?.username || 'Selected' }}</span>
                <span class="text-xs text-gray-500">({{ selectedUser?.email }})</span>
                <button @click="clearUserSelection" class="ml-auto text-red-600 text-sm">Remove</button>
              </div>
            </div>
          </div>

          <!-- Title -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Title <span class="text-red-500">*</span>
            </label>
            <input
              v-model="createForm.title"
              type="text"
              placeholder="Ticket title..."
              class="w-full border rounded px-3 py-2"
            />
          </div>

          <!-- Category and Priority -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select v-model="createForm.category" class="w-full border rounded px-3 py-2">
                <option value="general">General Inquiry</option>
                <option value="payment">Payment Issues</option>
                <option value="technical">Technical Support</option>
                <option value="feedback">Feedback</option>
                <option value="order">Order Issues</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="createForm.priority" class="w-full border rounded px-3 py-2">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Description <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="createForm.description"
              rows="5"
              placeholder="Describe the issue..."
              class="w-full border rounded px-3 py-2"
            ></textarea>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 pt-4 border-t">
            <button @click="closeCreateModal" class="btn btn-secondary">Cancel</button>
            <button @click="createTicket" :disabled="creatingTicket || !canCreateTicket" class="btn btn-primary">
              {{ creatingTicket ? 'Creating...' : 'Create Ticket' }}
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { debounce } from '@/utils/debounce'
import supportTicketsAPI from '@/api/support-tickets'
import usersAPI from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const tickets = ref([])
const stats = ref({})
const filters = ref({
  search: '',
  status: '',
  priority: '',
  category: '',
})
const selectedTicket = ref(null)
const messages = ref([])
const messagesLoading = ref(false)
const messageForm = ref({
  message: '',
})
const sendingMessage = ref(false)

// Create Ticket Modal State
const showCreateModal = ref(false)
const creatingTicket = ref(false)
const createForm = ref({
  created_by: null,
  userSearch: '',
  title: '',
  description: '',
  category: 'general',
  priority: 'medium',
})
const userSearchResults = ref([])
const showUserDropdown = ref(false)
const selectedUser = ref(null)

const canCreateTicket = computed(() => {
  return createForm.value.created_by && 
         createForm.value.title?.trim() && 
         createForm.value.description?.trim()
})

const filteredTickets = computed(() => {
  let filtered = [...tickets.value]
  
  // Show only recent tickets (last 50 or last 7 days)
  const now = new Date()
  filtered = filtered.filter(t => {
    const created = new Date(t.created_at)
    const daysSinceCreation = (now - created) / (1000 * 60 * 60 * 24)
    return daysSinceCreation <= 7
  })
  
  // Apply filters
  if (filters.value.status) {
    filtered = filtered.filter(t => t.status === filters.value.status)
  }
  if (filters.value.priority) {
    filtered = filtered.filter(t => t.priority === filters.value.priority)
  }
  if (filters.value.category) {
    filtered = filtered.filter(t => t.category === filters.value.category)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    filtered = filtered.filter(t => 
      t.title.toLowerCase().includes(search) ||
      t.description?.toLowerCase().includes(search)
    )
  }
  
  // Sort by most recent first
  return filtered.sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at)
  }).slice(0, 50) // Limit to 50 most recent
})

const loadTickets = async () => {
  loading.value = true
  try {
    const response = await supportTicketsAPI.list({})
    tickets.value = response.data.results || response.data || []
    
    // Calculate stats
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    stats.value = {
      open: tickets.value.filter(t => t.status === 'open').length,
      in_progress: tickets.value.filter(t => t.status === 'in_progress').length,
      high_priority: tickets.value.filter(t => ['high', 'critical'].includes(t.priority)).length,
      resolved_today: tickets.value.filter(t => {
        if (t.status !== 'closed') return false
        const closed = new Date(t.updated_at || t.created_at)
        return closed >= today
      }).length,
    }
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    loading.value = false
  }
}

const viewTicket = async (ticket) => {
  selectedTicket.value = ticket
  await loadMessages(ticket.id)
}

const loadMessages = async (ticketId) => {
  messagesLoading.value = true
  try {
    const response = await supportTicketsAPI.listMessages({ ticket: ticketId })
    messages.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

const sendMessage = async () => {
  if (!messageForm.value.message.trim()) {
    alert('Please enter a message')
    return
  }
  
  sendingMessage.value = true
  try {
    await supportTicketsAPI.createMessage({
      ticket: selectedTicket.value.id,
      message: messageForm.value.message,
    })
    messageForm.value.message = ''
    await loadMessages(selectedTicket.value.id)
    await loadTickets()
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message. Please try again.')
  } finally {
    sendingMessage.value = false
  }
}

const assignToMe = async (ticket) => {
  try {
    await supportTicketsAPI.assign(ticket.id, {
      assigned_to: authStore.user.id,
    })
    await loadTickets()
    if (selectedTicket.value && selectedTicket.value.id === ticket.id) {
      selectedTicket.value = ticket
      await loadTickets()
    }
    alert('Ticket assigned to you successfully')
  } catch (error) {
    console.error('Failed to assign ticket:', error)
    alert('Failed to assign ticket. Please try again.')
  }
}

const escalateTicket = async (ticket) => {
  const confirmed = await confirm.showDialog(
    'Are you sure you want to escalate this ticket?',
    'Escalate Ticket',
    {
      details: 'Escalating this ticket will notify senior support staff and may change the ticket priority.',
      variant: 'warning',
      icon: '⚠️',
      confirmText: 'Escalate',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await supportTicketsAPI.escalate(ticket.id)
    await loadTickets()
    if (selectedTicket.value && selectedTicket.value.id === ticket.id) {
      selectedTicket.value = ticket
      await loadTickets()
    }
    showSuccess('Ticket escalated successfully')
  } catch (error) {
    console.error('Failed to escalate ticket:', error)
    showError('Failed to escalate ticket. Please try again.')
  }
}

const respondToTicket = (ticket) => {
  viewTicket(ticket)
  // Focus on message input after modal opens
  setTimeout(() => {
    const textarea = document.querySelector('textarea[placeholder="Type your message..."]')
    if (textarea) textarea.focus()
  }, 100)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    priority: '',
    category: '',
  }
}

const filterTickets = () => {
  // Filters are reactive, no action needed
}

const debouncedSearch = debounce(() => {
  // Search is handled by computed property
}, 500)

const getStatusBadgeClass = (status) => {
  const classes = {
    open: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    closed: 'bg-green-100 text-green-800',
    awaiting_response: 'bg-orange-100 text-orange-800',
    escalated: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPriorityBadgeClass = (priority) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

// User Search
const searchUsers = debounce(async () => {
  const query = createForm.value.userSearch.trim()
  if (!query || query.length < 2) {
    userSearchResults.value = []
    return
  }
  
  try {
    // Use the users API with search parameter
    // The endpoint should be /api/v1/users/users/ with search query param
    const response = await usersAPI.list({ search: query })
    // Handle both paginated and non-paginated responses
    const users = response.data?.results || response.data || []
    userSearchResults.value = Array.isArray(users) ? users : []
  } catch (error) {
    console.error('Failed to search users:', error)
    userSearchResults.value = []
  }
}, 300)

const selectUser = (user) => {
  selectedUser.value = user
  createForm.value.created_by = user.id
  createForm.value.userSearch = ''
  showUserDropdown.value = false
  userSearchResults.value = []
}

const clearUserSelection = () => {
  selectedUser.value = null
  createForm.value.created_by = null
  createForm.value.userSearch = ''
  showUserDropdown.value = false
}

// Create Ticket
const createTicket = async () => {
  if (!canCreateTicket.value) {
    alert('Please fill in all required fields and select a user')
    return
  }
  
  creatingTicket.value = true
  try {
    const response = await supportTicketsAPI.create({
      created_by: createForm.value.created_by,
      title: createForm.value.title,
      description: createForm.value.description,
      category: createForm.value.category,
      priority: createForm.value.priority,
    })
    
    // Reset form
    closeCreateModal()
    
    // Reload tickets
    await loadTickets()
    
    // Show success message
    alert('Ticket created successfully!')
    
    // Optionally view the new ticket
    // viewTicket(response.data)
  } catch (error) {
    console.error('Failed to create ticket:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.created_by?.[0] || 'Failed to create ticket. Please try again.'
    alert(errorMsg)
  } finally {
    creatingTicket.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  createForm.value = {
    created_by: null,
    userSearch: '',
    title: '',
    description: '',
    category: 'general',
    priority: 'medium',
  }
  selectedUser.value = null
  userSearchResults.value = []
  showUserDropdown.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showUserDropdown.value = false
  }
}

onMounted(() => {
  loadTickets()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

