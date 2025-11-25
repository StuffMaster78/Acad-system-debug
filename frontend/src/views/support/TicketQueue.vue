<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Ticket Queue</h1>
        <p class="mt-2 text-gray-600">Manage and organize support tickets</p>
      </div>
      <button @click="loadTickets" :disabled="loading" class="btn btn-secondary">
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Unassigned</p>
        <p class="text-3xl font-bold text-blue-900">{{ stats.unassigned || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">My Tickets</p>
        <p class="text-3xl font-bold text-green-900">{{ stats.my_tickets || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">High Priority</p>
        <p class="text-3xl font-bold text-red-900">{{ stats.high_priority || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
        <p class="text-sm font-medium text-orange-700 mb-1">Overdue</p>
        <p class="text-3xl font-bold text-orange-900">{{ stats.overdue || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
        <p class="text-sm font-medium text-purple-700 mb-1">Escalated</p>
        <p class="text-3xl font-bold text-purple-900">{{ stats.escalated || 0 }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-lg shadow-sm">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'unassigned'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'unassigned'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Unassigned ({{ unassignedTickets.length }})
          </button>
          <button
            @click="activeTab = 'my_tickets'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'my_tickets'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            My Tickets ({{ myTickets.length }})
          </button>
          <button
            @click="activeTab = 'high_priority'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'high_priority'
                ? 'border-red-500 text-red-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            High Priority ({{ highPriorityTickets.length }})
          </button>
          <button
            @click="activeTab = 'overdue'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'overdue'
                ? 'border-orange-500 text-orange-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Overdue ({{ overdueTickets.length }})
          </button>
        </nav>
      </div>

      <!-- Filters -->
      <div class="p-4 border-b border-gray-200">
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

      <!-- Tickets Table -->
      <div class="p-6">
        <div v-if="loading" class="flex items-center justify-center py-12">
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
            <tr v-for="ticket in displayedTickets" :key="ticket.id" class="hover:bg-gray-50">
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
                {{ ticket.category_display || ticket.category }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(ticket.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button @click="viewTicket(ticket)" class="text-blue-600 hover:text-blue-900 mr-3">View</button>
                <button v-if="!ticket.assigned_to" @click="assignToMe(ticket)" class="text-green-600 hover:text-green-900 mr-3">Assign to Me</button>
                <button v-if="!ticket.is_escalated" @click="escalateTicket(ticket)" class="text-orange-600 hover:text-orange-900">Escalate</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!loading && displayedTickets.length === 0" class="text-center py-12 text-gray-500">
          <p>No tickets found</p>
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { debounce } from '@/utils/debounce'
import supportTicketsAPI from '@/api/support-tickets'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const activeTab = ref('unassigned')
const allTickets = ref([])
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

const unassignedTickets = computed(() => {
  return allTickets.value.filter(t => !t.assigned_to)
})

const myTickets = computed(() => {
  return allTickets.value.filter(t => t.assigned_to?.id === authStore.user?.id)
})

const highPriorityTickets = computed(() => {
  return allTickets.value.filter(t => ['high', 'critical'].includes(t.priority))
})

const overdueTickets = computed(() => {
  // Tickets that are open/in_progress and created more than 48 hours ago
  const now = new Date()
  return allTickets.value.filter(t => {
    if (!['open', 'in_progress'].includes(t.status)) return false
    const created = new Date(t.created_at)
    const hoursSinceCreation = (now - created) / (1000 * 60 * 60)
    return hoursSinceCreation > 48
  })
})

const displayedTickets = computed(() => {
  let tickets = []
  
  if (activeTab.value === 'unassigned') {
    tickets = unassignedTickets.value
  } else if (activeTab.value === 'my_tickets') {
    tickets = myTickets.value
  } else if (activeTab.value === 'high_priority') {
    tickets = highPriorityTickets.value
  } else if (activeTab.value === 'overdue') {
    tickets = overdueTickets.value
  }
  
  // Apply filters
  if (filters.value.status) {
    tickets = tickets.filter(t => t.status === filters.value.status)
  }
  if (filters.value.priority) {
    tickets = tickets.filter(t => t.priority === filters.value.priority)
  }
  if (filters.value.category) {
    tickets = tickets.filter(t => t.category === filters.value.category)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    tickets = tickets.filter(t => 
      t.title.toLowerCase().includes(search) ||
      t.description?.toLowerCase().includes(search)
    )
  }
  
  return tickets
})

const loadTickets = async () => {
  loading.value = true
  try {
    const response = await supportTicketsAPI.list({})
    allTickets.value = response.data.results || response.data || []
    
    // Calculate stats
    stats.value = {
      unassigned: unassignedTickets.value.length,
      my_tickets: myTickets.value.length,
      high_priority: highPriorityTickets.value.length,
      overdue: overdueTickets.value.length,
      escalated: allTickets.value.filter(t => t.is_escalated).length,
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
  if (!confirm('Are you sure you want to escalate this ticket?')) return
  
  try {
    await supportTicketsAPI.escalate(ticket.id)
    await loadTickets()
    if (selectedTicket.value && selectedTicket.value.id === ticket.id) {
      selectedTicket.value = ticket
      await loadTickets()
    }
    alert('Ticket escalated successfully')
  } catch (error) {
    console.error('Failed to escalate ticket:', error)
    alert('Failed to escalate ticket. Please try again.')
  }
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

onMounted(() => {
  loadTickets()
})
</script>

