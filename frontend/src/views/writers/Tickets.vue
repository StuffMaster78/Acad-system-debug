<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">My Support Tickets</h1>
        <p class="mt-2 text-gray-600">Create and manage your support tickets</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">Create Ticket</button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Tickets</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.total_tickets || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Open</p>
        <p class="text-3xl font-bold text-yellow-900">{{ stats.open_tickets || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.in_progress_tickets || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-linear-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Closed</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.closed_tickets || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Tickets Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="ticketsLoading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else-if="tickets.length === 0" class="text-center py-12">
        <div class="text-4xl mb-4">🎫</div>
        <p class="text-gray-600 text-lg">No tickets found</p>
        <p class="text-sm text-gray-400 mt-2">Create a ticket to get support</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-linear-to-r from-gray-50 via-gray-50 to-gray-100">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                ID
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Title
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Assigned To
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Status
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Priority
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Category
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Created
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b border-gray-200">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="(ticket, index) in tickets"
              :key="ticket.id"
              :class="[
                'transition-all duration-150 hover:bg-blue-50/50 cursor-pointer',
                index % 2 === 0 ? 'bg-white' : 'bg-gray-50/30'
              ]"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-bold text-gray-900">#{{ ticket.id }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 max-w-md">{{ ticket.title }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div
                    v-if="ticket.assigned_to"
                    class="shrink-0 h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-primary-600 text-xs font-semibold">
                      {{ ticket.assigned_to.username[0].toUpperCase() }}
                    </span>
                  </div>
                  <div class="ml-3">
                    <div class="text-sm text-gray-900">
                      {{ ticket.assigned_to ? ticket.assigned_to.username : 'Unassigned' }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="getStatusBadgeClass(ticket.status)"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border"
                >
                  <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="getStatusDotClass(ticket.status)"></span>
                  {{ ticket.status_display || ticket.status }}
                </span>
              </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="getPriorityBadgeClass(ticket.priority)"
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border"
              >
                <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="getPriorityDotClass(ticket.priority)"></span>
                {{ ticket.priority_display || ticket.priority }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm text-gray-700 font-medium">
                {{ ticket.category_display || ticket.category || 'N/A' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ formatDate(ticket.created_at) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ formatTime(ticket.created_at) }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <button
                @click.stop="viewTicket(ticket)"
                class="text-primary-600 hover:text-primary-800 font-medium transition-colors"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b">
          <h2 class="text-2xl font-bold text-gray-900">Create Support Ticket</h2>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Title *</label>
            <input v-model="ticketForm.title" type="text" class="w-full border rounded px-3 py-2" placeholder="Enter ticket title" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Category *</label>
            <select v-model="ticketForm.category" class="w-full border rounded px-3 py-2">
              <option value="">Select category</option>
              <option value="general">General Inquiry</option>
              <option value="payment">Payment Issues</option>
              <option value="technical">Technical Support</option>
              <option value="feedback">Feedback</option>
              <option value="order">Order Issues</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Priority</label>
            <select v-model="ticketForm.priority" class="w-full border rounded px-3 py-2">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Description *</label>
            <textarea v-model="ticketForm.description" rows="6" class="w-full border rounded px-3 py-2" placeholder="Describe your issue..."></textarea>
          </div>
        </div>
        <div class="p-6 border-t flex justify-end space-x-3">
          <button @click="closeCreateModal" class="btn btn-secondary">Cancel</button>
          <button @click="createTicket" :disabled="savingTicket" class="btn btn-primary">
            {{ savingTicket ? 'Creating...' : 'Create Ticket' }}
          </button>
        </div>
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Created</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedTicket.created_at) }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Updated</label>
              <p class="text-sm text-gray-900">{{ formatDate(selectedTicket.updated_at) }}</p>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { debounce } from '@/utils/debounce'
import writerTicketsAPI from '@/api/writer-tickets'

const tickets = ref([])
const ticketsLoading = ref(false)
const stats = ref({})
const filters = ref({
  search: '',
  status: '',
  priority: '',
})
const showCreateModal = ref(false)
const ticketForm = ref({
  title: '',
  category: '',
  priority: 'medium',
  description: '',
})
const savingTicket = ref(false)
const selectedTicket = ref(null)
const messages = ref([])
const messagesLoading = ref(false)
const messageForm = ref({
  message: '',
})
const sendingMessage = ref(false)

const loadTickets = async () => {
  ticketsLoading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    
    const response = await writerTicketsAPI.list(params)
    tickets.value = response.data.results || response.data || []
    
    // Calculate stats
    stats.value = {
      total_tickets: tickets.value.length,
      open_tickets: tickets.value.filter(t => t.status === 'open').length,
      in_progress_tickets: tickets.value.filter(t => t.status === 'in_progress').length,
      closed_tickets: tickets.value.filter(t => t.status === 'closed').length,
    }
  } catch (error) {
    console.error('Failed to load tickets:', error)
  } finally {
    ticketsLoading.value = false
  }
}

const createTicket = async () => {
  if (!ticketForm.value.title || !ticketForm.value.category || !ticketForm.value.description) {
    alert('Please fill in all required fields')
    return
  }
  
  savingTicket.value = true
  try {
    await writerTicketsAPI.create(ticketForm.value)
    await loadTickets()
    closeCreateModal()
  } catch (error) {
    console.error('Failed to create ticket:', error)
    alert('Failed to create ticket. Please try again.')
  } finally {
    savingTicket.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  ticketForm.value = {
    title: '',
    category: '',
    priority: 'medium',
    description: '',
  }
}

const viewTicket = async (ticket) => {
  selectedTicket.value = ticket
  await loadMessages(ticket.id)
}

const loadMessages = async (ticketId) => {
  messagesLoading.value = true
  try {
    const response = await writerTicketsAPI.listMessages({ ticket: ticketId })
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
    await writerTicketsAPI.createMessage({
      ticket: selectedTicket.value.id,
      message: messageForm.value.message,
    })
    messageForm.value.message = ''
    await loadMessages(selectedTicket.value.id)
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message. Please try again.')
  } finally {
    sendingMessage.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    priority: '',
  }
  loadTickets()
}

const debouncedSearch = debounce(() => {
  loadTickets()
}, 500)

const getStatusBadgeClass = (status) => {
  const classes = {
    open: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    in_progress: 'bg-blue-100 text-blue-800 border-blue-200',
    closed: 'bg-green-100 text-green-800 border-green-200',
    awaiting_response: 'bg-orange-100 text-orange-800 border-orange-200',
    escalated: 'bg-red-100 text-red-800 border-red-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 border-gray-200'
}

const getStatusDotClass = (status) => {
  const classes = {
    open: 'bg-yellow-500',
    in_progress: 'bg-blue-500',
    closed: 'bg-green-500',
    awaiting_response: 'bg-orange-500',
    escalated: 'bg-red-500',
  }
  return classes[status] || 'bg-gray-500'
}

const getPriorityBadgeClass = (priority) => {
  const classes = {
    low: 'bg-gray-100 text-gray-800 border-gray-200',
    medium: 'bg-blue-100 text-blue-800 border-blue-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200',
  }
  return classes[priority] || 'bg-gray-100 text-gray-800 border-gray-200'
}

const getPriorityDotClass = (priority) => {
  const classes = {
    low: 'bg-gray-500',
    medium: 'bg-blue-500',
    high: 'bg-orange-500',
    critical: 'bg-red-500',
  }
  return classes[priority] || 'bg-gray-500'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadTickets()
})
</script>

