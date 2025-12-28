<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-5xl w-full shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <h3 class="text-xl font-bold text-white">Message Threads</h3>
              <p class="text-sm text-blue-100 mt-1">
                {{ classType === 'bundle' ? `Class Bundle #${classId}` : `Express Class #${classId}` }}
              </p>
            </div>
            <div class="flex items-center gap-3">
              <button 
                @click="openCreateThreadModal"
                :disabled="availableRecipients.length === 0"
                class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 backdrop-blur-sm"
                title="Send a new message"
              >
                <span>✉️</span>
                <span>New Message</span>
              </button>
              <button 
                @click="$emit('close')" 
                class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-4 text-gray-600 dark:text-gray-400">Loading threads...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="threads.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-lg font-medium">No message threads yet</p>
            <p class="text-sm mt-2">Create a new thread to start communicating</p>
            <div v-if="availableRecipients.length === 0" class="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-sm text-yellow-800 dark:text-yellow-200">
              <p class="font-medium mb-1">⚠️ No recipients available</p>
              <p class="text-xs">Make sure the class has a client or assigned writer, or you have permission to message other users.</p>
            </div>
            <button 
              @click="openCreateThreadModal"
              :disabled="availableRecipients.length === 0"
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Thread
            </button>
          </div>

          <!-- Threads List -->
          <div v-else class="space-y-3">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ threads.length }} Thread{{ threads.length !== 1 ? 's' : '' }}
              </h4>
              <div class="flex gap-2">
                <button 
                  @click="openCreateThreadModal"
                  :disabled="availableRecipients.length === 0"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  title="Create a new message thread"
                >
                  <span>💬</span>
                  <span>New Thread</span>
                </button>
              </div>
            </div>

            <div
              v-for="thread in threads"
              :key="thread.id"
              @click="openThread(thread)"
              class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:border-blue-500 hover:shadow-md cursor-pointer transition-all"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center text-blue-600 dark:text-blue-300 font-semibold">
                      {{ getThreadInitials(thread) }}
                    </div>
                    <div class="flex-1">
                      <h5 class="font-semibold text-gray-900 dark:text-white">
                        {{ thread.subject || 'No Subject' }}
                      </h5>
                      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {{ getParticipantsText(thread) }}
                      </p>
                    </div>
                  </div>
                  <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mt-2">
                    <span>{{ formatDate(thread.created_at) }}</span>
                    <span v-if="thread.messages_count !== undefined">
                      {{ thread.messages_count }} message{{ thread.messages_count !== 1 ? 's' : '' }}
                    </span>
                    <span 
                      v-if="thread.is_active === false"
                      class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-600 dark:text-gray-400"
                    >
                      Archived
                    </span>
                  </div>
                </div>
                <button
                  @click.stop="openThread(thread)"
                  class="ml-4 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Open
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Thread Modal -->
        <div v-if="showCreateThreadModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
          <div class="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold">Create New Thread</h3>
              <button 
                @click="closeCreateThreadModal"
                class="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ✕
              </button>
            </div>

            <form @submit.prevent="createThread" class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-1">Recipient *</label>
                <div v-if="availableRecipients.length === 0" class="p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-sm text-yellow-800 dark:text-yellow-200 mb-2">
                  <p class="font-medium">⚠️ No recipients available</p>
                  <p class="text-xs mt-1">Loading recipients... If this persists, you may not have permission to create threads for this class.</p>
                </div>
                <select 
                  v-model="newThreadForm.recipient_id" 
                  required
                  :disabled="availableRecipients.length === 0"
                  class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="">{{ availableRecipients.length === 0 ? 'No recipients available' : 'Select recipient...' }}</option>
                  <option 
                    v-for="user in availableRecipients" 
                    :key="user.id" 
                    :value="user.id"
                  >
                    {{ user.username || user.email }} ({{ user.role }})
                  </option>
                </select>
                <p v-if="availableRecipients.length > 0" class="text-xs text-gray-500 mt-1">
                  {{ availableRecipients.length }} recipient{{ availableRecipients.length !== 1 ? 's' : '' }} available
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Subject</label>
                <input 
                  v-model="newThreadForm.subject" 
                  type="text"
                  placeholder="Thread subject (optional)"
                  class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Initial Message *</label>
                <textarea 
                  v-model="newThreadForm.initial_message" 
                  required
                  rows="4"
                  placeholder="Type your message here..."
                  class="w-full border rounded px-3 py-2 dark:bg-gray-700 dark:border-gray-600"
                ></textarea>
              </div>

              <div class="flex gap-2 pt-4">
                <button 
                  type="submit"
                  :disabled="creatingThread"
                  class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {{ creatingThread ? 'Creating...' : 'Create Thread' }}
                </button>
                <button 
                  type="button"
                  @click="closeCreateThreadModal"
                  class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Thread View Modal -->
        <ThreadViewModal
          v-if="selectedThread"
          :thread="selectedThread"
          :show="!!selectedThread"
          @close="selectedThread = null"
          @thread-updated="loadThreads"
        />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { classManagementAPI, expressClassesAPI, communicationsAPI } from '@/api'
import apiClient from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useErrorHandler } from '@/composables/useErrorHandler'
import ThreadViewModal from '@/components/messages/ThreadViewModal.vue'

const { handleError, handleSuccess, handleWarning } = useErrorHandler()

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  classId: {
    type: [Number, String],
    required: true
  },
  classType: {
    type: String,
    required: true,
    validator: (value) => ['bundle', 'express'].includes(value)
  }
})

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const threads = ref([])
const loading = ref(false)
const showCreateThreadModal = ref(false)
const creatingThread = ref(false)
const selectedThread = ref(null)
const availableRecipients = ref([])

const newThreadForm = ref({
  recipient_id: '',
  subject: '',
  initial_message: ''
})

const loadThreads = async () => {
  if (!props.classId) return
  
  loading.value = true
  try {
    let response
    if (props.classType === 'bundle') {
      response = await classManagementAPI.getThreads(props.classId)
    } else {
      response = await expressClassesAPI.getThreads(props.classId)
    }
    threads.value = response.data || []
  } catch (error) {
    console.error('Failed to load threads:', error)
    // Only show error if it's not a 404 (endpoint might not exist yet)
    if (error?.response?.status !== 404) {
      const errorMessage = error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to load threads'
      console.error('Error details:', errorMessage)
    }
    threads.value = []
  } finally {
    loading.value = false
  }
}

const loadAvailableRecipients = async () => {
  try {
    // First, try to get class-specific participants
    let classData = null
    if (props.classType === 'bundle') {
      const response = await classManagementAPI.getBundle(props.classId)
      classData = response.data
    } else {
      const response = await expressClassesAPI.get(props.classId)
      classData = response.data
    }

    // Build list of potential recipients from class participants
    const recipients = []
    const recipientIds = new Set()
    
    // Add client
    if (classData?.client) {
      const clientId = typeof classData.client === 'object' ? classData.client.id : classData.client
      if (!recipientIds.has(clientId)) {
        recipients.push({
          id: clientId,
          username: typeof classData.client === 'object' ? classData.client.username : null,
          email: typeof classData.client === 'object' ? classData.client.email : null,
          role: 'client'
        })
        recipientIds.add(clientId)
      }
    }

    // Add assigned writer
    if (classData?.assigned_writer) {
      const writerId = typeof classData.assigned_writer === 'object' ? classData.assigned_writer.id : classData.assigned_writer
      if (!recipientIds.has(writerId)) {
        recipients.push({
          id: writerId,
          username: typeof classData.assigned_writer === 'object' ? classData.assigned_writer.username : null,
          email: typeof classData.assigned_writer === 'object' ? classData.assigned_writer.email : null,
          role: 'writer'
        })
        recipientIds.add(writerId)
      }
    }

    // If user is admin/staff/support, also load other staff members and support
    const currentUser = authStore.user
    if (currentUser && (currentUser.is_staff || currentUser.role === 'admin' || currentUser.role === 'superadmin' || currentUser.role === 'editor' || currentUser.role === 'support')) {
      try {
        // Load staff members (admin, editor, superadmin, support)
        const response = await apiClient.get('/users/users/', { 
          params: { role__in: 'admin,editor,superadmin,support', is_active: true } 
        })
        const staff = response.data.results || response.data || []
        // Add staff members that aren't already in the list and aren't the current user
        staff.forEach(staffMember => {
          if (staffMember.id !== currentUser.id && !recipientIds.has(staffMember.id)) {
            recipients.push({
              id: staffMember.id,
              username: staffMember.username,
              email: staffMember.email,
              role: staffMember.role
            })
            recipientIds.add(staffMember.id)
          }
        })
      } catch (error) {
        console.warn('Failed to load staff members:', error)
      }
    }

    // If no recipients found, show a helpful message
    if (recipients.length === 0) {
      console.warn('No available recipients found for class messaging')
    }

    availableRecipients.value = recipients
  } catch (error) {
    console.error('Failed to load recipients:', error)
    availableRecipients.value = []
  }
}

const createThread = async () => {
  if (!newThreadForm.value.recipient_id || !newThreadForm.value.initial_message) {
    if (!newThreadForm.value.recipient_id) {
      handleWarning('Please select a recipient')
    } else if (!newThreadForm.value.initial_message) {
      handleWarning('Please enter an initial message')
    }
    return
  }

  if (availableRecipients.value.length === 0) {
    handleWarning('No recipients available. Please refresh the page or contact support.')
    return
  }

  creatingThread.value = true
  try {
    const data = {
      recipient_id: parseInt(newThreadForm.value.recipient_id),
      subject: newThreadForm.value.subject || undefined,
      initial_message: newThreadForm.value.initial_message
    }

    let response
    if (props.classType === 'bundle') {
      response = await classManagementAPI.createThread(props.classId, data)
    } else {
      response = await expressClassesAPI.createThread(props.classId, data)
    }

    handleSuccess('Thread created successfully')
    closeCreateThreadModal()
    await loadThreads()
    
    // Optionally open the newly created thread
    if (response.data?.id || response.data?.thread_id) {
      const threadId = response.data?.id || response.data?.thread_id
      // Reload threads to get the full thread object
      await loadThreads()
      const newThread = threads.value.find(t => t.id === threadId)
      if (newThread) {
        selectedThread.value = newThread
      }
    }
  } catch (error) {
    console.error('Failed to create thread:', error)
    handleError(error, { action: 'creating thread' })
  } finally {
    creatingThread.value = false
  }
}

const openCreateThreadModal = () => {
  // Ensure recipients are loaded
  if (availableRecipients.value.length === 0) {
    loadAvailableRecipients()
  }
  showCreateThreadModal.value = true
}

const closeCreateThreadModal = () => {
  showCreateThreadModal.value = false
  newThreadForm.value = {
    recipient_id: '',
    subject: '',
    initial_message: ''
  }
}

const openThread = (thread) => {
  selectedThread.value = thread
}

const getThreadInitials = (thread) => {
  if (thread.subject) {
    const words = thread.subject.split(' ')
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase()
    }
    return thread.subject.substring(0, 2).toUpperCase()
  }
  return 'TH'
}

const getParticipantsText = (thread) => {
  const participants = thread.participants || []
  const currentUserId = authStore.user?.id
  
  const otherParticipants = participants.filter(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUserId
  })

  if (otherParticipants.length === 0) return 'No other participants'
  if (otherParticipants.length === 1) {
    const p = otherParticipants[0]
    const name = typeof p === 'object' ? (p.username || p.email) : 'User'
    const role = typeof p === 'object' ? p.role : null
    return role ? `${name} (${role})` : name
  }
  return `${otherParticipants.length} participants`
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString()
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadThreads()
    loadAvailableRecipients()
  } else {
    // Reset when modal closes
    threads.value = []
    availableRecipients.value = []
    selectedThread.value = null
    showCreateThreadModal.value = false
  }
})

watch(() => props.classId, () => {
  if (props.show) {
    loadThreads()
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}
</style>

