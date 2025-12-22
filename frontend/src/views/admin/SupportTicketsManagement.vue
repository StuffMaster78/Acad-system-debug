<template>
  <!-- Loading State -->
  <div v-if="initialLoading" class="p-6 text-center">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-gray-600">Loading...</p>
  </div>
  <!-- Error Display -->
  <div v-else-if="componentError" class="p-6">
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <h2 class="text-xl font-bold text-red-900 mb-2">Error Loading Page</h2>
      <p class="text-red-700 mb-4">{{ componentError }}</p>
      <button @click="window.location.reload()" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
        Reload Page
      </button>
    </div>
  </div>
  <!-- Main Content -->
  <div v-else class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Support Tickets Management</h1>
        <p class="mt-2 text-gray-600">Manage and track support tickets, assignments, and escalations</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">Create Ticket</button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Tickets</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_tickets || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Open</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.open_tickets || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.in_progress_tickets || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Escalated</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.escalated_tickets || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Closed</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.closed_tickets || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
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
          <select v-model="filters.status" @change="loadTickets" class="w-full border rounded px-3 py-2">
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
          <select v-model="filters.priority" @change="loadTickets" class="w-full border rounded px-3 py-2">
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Category</label>
          <select v-model="filters.category" @change="loadTickets" class="w-full border rounded px-3 py-2">
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

    <!-- Tickets Table -->
    <div class="card overflow-hidden">
      <div v-if="ticketsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned To</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="ticket in tickets" :key="ticket.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">#{{ ticket.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ truncateText(ticket.title, 40) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ ticket.created_by_name || ticket.created_by || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ ticket.assigned_to_name || 'Unassigned' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusBadgeClass(ticket.status)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ ticket.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getPriorityBadgeClass(ticket.priority)" class="px-2 py-1 text-xs font-semibold rounded-full">
                {{ ticket.priority }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ ticket.category }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(ticket.created_at) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button @click="viewTicket(ticket)" class="text-blue-600 hover:text-blue-900">View</button>
              <button v-if="!ticket.is_escalated" @click="escalateTicket(ticket.id)" class="text-orange-600 hover:text-orange-900">Escalate</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!ticketsLoading && tickets.length === 0" class="text-center py-12 text-gray-500">
        No tickets found
      </div>
    </div>

    <!-- Ticket Detail Modal -->
    <div v-if="showTicketModal && selectedTicket" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">Ticket #{{ selectedTicket.id }}: {{ selectedTicket.title }}</h3>
            <button @click="closeTicketModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="ticketForm.status" @change="updateTicket" class="w-full border rounded px-3 py-2">
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
                <option value="awaiting_response">Awaiting Response</option>
                <option value="escalated">Escalated</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="ticketForm.priority" @change="updateTicket" class="w-full border rounded px-3 py-2">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
              <select v-model="ticketForm.assigned_to" @change="assignTicket" class="w-full border rounded px-3 py-2">
                <option value="">Unassigned</option>
                <option v-for="user in supportUsers" :key="user.id" :value="user.id">{{ user.username }}</option>
              </select>
            </div>
            <div class="flex items-center">
              <input
                v-model="ticketForm.is_escalated"
                type="checkbox"
                id="is_escalated"
                class="mr-2"
                @change="updateTicket"
              />
              <label for="is_escalated" class="text-sm font-medium text-gray-700">Escalated</label>
            </div>
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <p class="text-sm text-gray-900 bg-gray-50 p-3 rounded">{{ selectedTicket.description }}</p>
          </div>

          <!-- Messages Section -->
          <div class="mb-6">
            <h4 class="text-lg font-semibold mb-3">Messages</h4>
            <div class="space-y-3 max-h-60 overflow-y-auto">
              <div v-for="message in selectedTicket.messages || []" :key="message.id" class="border rounded p-3">
                <div class="flex justify-between items-start mb-2">
                  <span class="text-sm font-medium">{{ message.sender_name || message.sender }}</span>
                  <span class="text-xs text-gray-500">{{ formatDateTime(message.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-900">{{ message.message }}</p>
                <span v-if="message.is_internal" class="text-xs text-gray-500">(Internal)</span>
              </div>
            </div>
            <div class="mt-3">
              <textarea
                v-model="newMessage"
                class="w-full border rounded px-3 py-2"
                rows="3"
                placeholder="Add a message..."
              ></textarea>
              <div class="flex items-center mt-2">
                <input
                  v-model="isInternalMessage"
                  type="checkbox"
                  id="is_internal"
                  class="mr-2"
                />
                <label for="is_internal" class="text-sm text-gray-700">Internal message</label>
              </div>
              <button @click="sendMessage" class="btn btn-primary mt-2" :disabled="sendingMessage">
                {{ sendingMessage ? 'Sending...' : 'Send Message' }}
              </button>
            </div>
          </div>

          <!-- Logs Section -->
          <div>
            <h4 class="text-lg font-semibold mb-3">Activity Log</h4>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div v-for="log in selectedTicket.logs || []" :key="log.id" class="text-sm text-gray-600 border-l-2 pl-3">
                <span class="font-medium">{{ log.performed_by_name || log.performed_by }}</span>
                <span class="mx-2">-</span>
                <span>{{ log.action }}</span>
                <span class="text-xs text-gray-500 ml-2">{{ formatDateTime(log.timestamp) }}</span>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-4">
            <button @click="closeTicketModal" class="btn btn-secondary">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-semibold">Create Ticket</h3>
            <button @click="closeCreateModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <form @submit.prevent="createTicket" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input v-model="createForm.title" type="text" required class="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Description *</label>
              <textarea v-model="createForm.description" required class="w-full border rounded px-3 py-2" rows="4"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select v-model="createForm.priority" class="w-full border rounded px-3 py-2">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
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
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
              <select v-model="createForm.website" class="w-full border rounded px-3 py-2">
                <option value="">Select Website</option>
                <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
              </select>
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="closeCreateModal" class="btn btn-secondary">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="creatingTicket">
                {{ creatingTicket ? 'Creating...' : 'Create Ticket' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supportTicketsAPI, websitesAPI, usersAPI } from '@/api'

const componentError = ref(null)
const initialLoading = ref(true)
const stats = ref({})
const tickets = ref([])
const ticketsLoading = ref(false)
const supportUsers = ref([])
const websites = ref([])

const filters = ref({
  search: '',
  status: '',
  priority: '',
  category: '',
})

const showTicketModal = ref(false)
const showCreateModal = ref(false)
const selectedTicket = ref(null)
const creatingTicket = ref(false)
const sendingMessage = ref(false)
const updatingTicket = ref(false)

const ticketForm = ref({
  status: '',
  priority: '',
  assigned_to: '',
  is_escalated: false,
})

const createForm = ref({
  title: '',
  description: '',
  priority: 'medium',
  category: 'general',
  website: '',
})

const newMessage = ref('')
const isInternalMessage = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const truncateText = (text, maxLength) => {
  if (!text) return 'N/A'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

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

const loadStats = async () => {
  try {
    const response = await supportTicketsAPI.getStatistics()
    const data = response.data
    
    // Calculate stats from tickets
    const allTickets = tickets.value
    stats.value = {
      total_tickets: allTickets.length || data.total_tickets || 0,
      open_tickets: allTickets.filter(t => t.status === 'open').length || data.open_tickets || 0,
      in_progress_tickets: allTickets.filter(t => t.status === 'in_progress').length || data.in_progress_tickets || 0,
      escalated_tickets: allTickets.filter(t => t.is_escalated).length || data.escalated_tickets || 0,
      closed_tickets: allTickets.filter(t => t.status === 'closed').length || data.closed_tickets || 0,
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    // Fallback to calculating from tickets
    const allTickets = tickets.value
    stats.value = {
      total_tickets: allTickets.length,
      open_tickets: allTickets.filter(t => t.status === 'open').length,
      in_progress_tickets: allTickets.filter(t => t.status === 'in_progress').length,
      escalated_tickets: allTickets.filter(t => t.is_escalated).length,
      closed_tickets: allTickets.filter(t => t.status === 'closed').length,
    }
  }
}

const loadTickets = async () => {
  ticketsLoading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.category) params.category = filters.value.category
    
    const response = await supportTicketsAPI.list(params)
    tickets.value = response.data.results || response.data || []
    await loadStats()
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    ticketsLoading.value = false
  }
}

const loadSupportUsers = async () => {
  try {
    // Backend expects role filter as a list; pass multiple roles explicitly
    const response = await usersAPI.list({ role: ['support', 'admin', 'superadmin'] })
    supportUsers.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Failed to load support users:', error)
  }
}

const loadWebsites = async () => {
  try {
    const response = await websitesAPI.listWebsites()
    websites.value = response.data?.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

let searchTimeout = null
const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadTickets()
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    priority: '',
    category: '',
  }
  loadTickets()
}

const viewTicket = async (ticket) => {
  try {
    const response = await supportTicketsAPI.get(ticket.id)
    selectedTicket.value = response.data
    ticketForm.value = {
      status: response.data.status,
      priority: response.data.priority,
      assigned_to: response.data.assigned_to || '',
      is_escalated: response.data.is_escalated || false,
    }
    showTicketModal.value = true
  } catch (error) {
    console.error('Failed to load ticket details:', error)
    selectedTicket.value = ticket
    ticketForm.value = {
      status: ticket.status,
      priority: ticket.priority,
      assigned_to: ticket.assigned_to || '',
      is_escalated: ticket.is_escalated || false,
    }
    showTicketModal.value = true
  }
}

const closeTicketModal = () => {
  showTicketModal.value = false
  selectedTicket.value = null
  newMessage.value = ''
  isInternalMessage.value = false
}

const updateTicket = async () => {
  if (!selectedTicket.value) return
  updatingTicket.value = true
  try {
    await supportTicketsAPI.update(selectedTicket.value.id, {
      status: ticketForm.value.status,
      priority: ticketForm.value.priority,
      is_escalated: ticketForm.value.is_escalated,
    })
    await viewTicket(selectedTicket.value)
    await loadTickets()
  } catch (error) {
    console.error('Failed to update ticket:', error)
    alert('Failed to update ticket')
  } finally {
    updatingTicket.value = false
  }
}

const assignTicket = async () => {
  if (!selectedTicket.value) return
  try {
    await supportTicketsAPI.assign(selectedTicket.value.id, {
      assigned_to: ticketForm.value.assigned_to || null,
    })
    await viewTicket(selectedTicket.value)
    await loadTickets()
  } catch (error) {
    console.error('Failed to assign ticket:', error)
    alert('Failed to assign ticket')
  }
}

const escalateTicket = async (id) => {
  if (!confirm('Are you sure you want to escalate this ticket?')) return
  try {
    await supportTicketsAPI.escalate(id)
    await loadTickets()
  } catch (error) {
    console.error('Failed to escalate ticket:', error)
    alert('Failed to escalate ticket')
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedTicket.value) return
  sendingMessage.value = true
  try {
    await supportTicketsAPI.createMessage({
      ticket: selectedTicket.value.id,
      message: newMessage.value,
      is_internal: isInternalMessage.value,
    })
    newMessage.value = ''
    isInternalMessage.value = false
    await viewTicket(selectedTicket.value)
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message')
  } finally {
    sendingMessage.value = false
  }
}

const createTicket = async () => {
  creatingTicket.value = true
  try {
    await supportTicketsAPI.create(createForm.value)
    await loadTickets()
    closeCreateModal()
  } catch (error) {
    console.error('Failed to create ticket:', error)
    alert(error.response?.data?.detail || 'Failed to create ticket')
  } finally {
    creatingTicket.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  createForm.value = {
    title: '',
    description: '',
    priority: 'medium',
    category: 'general',
    website: '',
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      loadWebsites(),
      loadSupportUsers(),
      loadTickets()
    ])
    initialLoading.value = false
  } catch (error) {
    console.error('Error initializing SupportTicketsManagement:', error)
    componentError.value = error.message || 'Failed to initialize page'
    initialLoading.value = false
  }
})
</script>

<style scoped>
/* Component styles */
</style>

