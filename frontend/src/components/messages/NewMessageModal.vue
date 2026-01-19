<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-bold text-white">New Message</h3>
              <p class="text-sm text-blue-100 mt-1">Start a new conversation</p>
            </div>
            <button 
              @click="$emit('close')" 
              class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors"
              :disabled="sending"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <!-- Flow summary -->
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span class="font-semibold">You ({{ currentUserRoleLabel }})</span>
            <span v-if="activeRecipientTab">
              &nbsp;→&nbsp;<span class="font-semibold">{{ activeRecipientTab.label }}</span>
            </span>
          </div>

          <!-- Recipient Type Selection -->
          <div>
            <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide">
              Step 1 of 3 · Choose who you want to message
            </label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                v-for="tab in recipientTabs"
                :key="tab.id"
                @click="selectedRecipientType = tab.id; selectedRecipient = null"
                :class="[
                  'p-4 border-2 rounded-xl transition-all text-center',
                  selectedRecipientType === tab.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-md'
                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                ]"
              >
                <component :is="tab.icon" class="w-6 h-6 mx-auto mb-2" />
                <p class="text-sm font-medium">{{ tab.label }}</p>
                <p class="mt-1 text-[11px] text-gray-500 dark:text-gray-400" v-if="tab.tooltip">
                  {{ tab.tooltip }}
                </p>
              </button>
            </div>
          </div>

          <!-- Specific Recipient Selection -->
          <div v-if="selectedRecipientType && availableRecipients.length > 0">
            <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide">
              Step 2 of 3 · Select the specific recipient
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="recipientSearch"
                type="text"
                placeholder="Search recipients..."
                class="w-full pl-10 pr-4 py-2.5 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white mb-3"
              />
            </div>
            <div class="max-h-48 overflow-y-auto space-y-2">
              <div
                v-for="recipient in filteredRecipients"
                :key="recipient.id"
                @click="selectRecipient(recipient)"
                :class="[
                  'p-3 border-2 rounded-lg cursor-pointer transition-all',
                  selectedRecipient?.id === recipient.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                ]"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold">
                    {{ (recipient.username || recipient.email || 'U')[0].toUpperCase() }}
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-gray-900 dark:text-white">{{ recipient.username || recipient.email }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ recipient.email }}</p>
                  </div>
                  <div v-if="selectedRecipient?.id === recipient.id" class="shrink-0">
                    <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Message Input -->
          <div v-if="selectedRecipient">
            <!-- To summary -->
            <div class="mb-2 text-xs text-gray-600 dark:text-gray-300">
              To:
              <span class="font-semibold">
                {{ selectedRecipient.username || selectedRecipient.email || 'User' }}
              </span>
              <span v-if="selectedRecipient.role" class="text-gray-500 dark:text-gray-400">
                ({{ selectedRecipient.role.charAt(0).toUpperCase() + selectedRecipient.role.slice(1) }})
              </span>
            </div>
            <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide">
              Step 3 of 3 · Type your message
            </label>
            <textarea
              v-model="message"
              placeholder="Type your message here..."
              rows="6"
              class="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-none"
            ></textarea>
            <p v-if="error" class="mt-2 text-sm text-red-600 dark:text-red-400">{{ error }}</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 flex gap-3">
          <button
            @click="$emit('close')"
            :disabled="sending"
            class="flex-1 px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 rounded-xl text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            @click="sendMessage"
            :disabled="!canSend || sending"
            class="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
          >
            <svg v-if="sending" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ sending ? 'Sending...' : 'Send Message' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, shallowRef } from 'vue'
import { communicationsAPI, usersAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useDebounceFn } from '@vueuse/core'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  defaultRecipientType: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close', 'message-sent'])

const authStore = useAuthStore()
const currentUser = authStore.user

const currentUserRoleLabel = computed(() => {
  const role = currentUser?.role || 'user'
  return role.charAt(0).toUpperCase() + role.slice(1)
})

const selectedRecipientType = ref(props.defaultRecipientType || null)
const selectedRecipient = shallowRef(null) // Use shallowRef for better performance
const lastSelectedRecipientByType = ref(new Map())
const availableRecipients = shallowRef([]) // Use shallowRef for large arrays
const recipientSearch = ref('')
const message = ref('')
const sending = ref(false)
const error = ref('')
const loadingRecipients = ref(false)

// Cache recipients by role to avoid repeated API calls
const recipientsCache = ref(new Map())
const cacheExpiry = 10 * 60 * 1000 // Increased to 10 minutes for better caching

const recipientTabs = computed(() => {
  const role = currentUser?.role
  const tabs = []

  if (role === 'client') {
    tabs.push(
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Message the admin team about your account or orders.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Get help from support for general issues.' },
      { id: 'writer', label: 'Writer', icon: 'WriterIcon', tooltip: 'Talk directly to your assigned writer.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Discuss quality or edits with an editor.' }
    )
  } else if (role === 'writer') {
    tabs.push(
      { id: 'client', label: 'Client', icon: 'ClientIcon', tooltip: 'Message the client about order details.' },
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Contact admin for escalations or clarifications.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Get internal help from support.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Coordinate with editors on revisions.' }
    )
  } else {
    tabs.push(
      { id: 'client', label: 'Client', icon: 'ClientIcon', tooltip: 'Message any client on the platform.' },
      { id: 'writer', label: 'Writer', icon: 'WriterIcon', tooltip: 'Reach out to writers for coordination.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Discuss editing or quality issues.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Internal conversations with support staff.' },
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Conversations between admin/superadmin staff.' }
    )
  }

  return tabs
})

const activeRecipientTab = computed(() => {
  return recipientTabs.value.find(t => t.id === selectedRecipientType.value) || null
})

// Optimized filtered recipients with memoization
const filteredRecipients = computed(() => {
  if (!recipientSearch.value.trim()) return availableRecipients.value
  
  const search = recipientSearch.value.toLowerCase().trim()
  // Limit results to first 50 for performance
  const filtered = availableRecipients.value.filter(recipient => {
    const name = (recipient.username || '').toLowerCase()
    const email = (recipient.email || '').toLowerCase()
    return name.includes(search) || email.includes(search)
  })
  
  return filtered.slice(0, 50) // Limit to 50 results for performance
})

const canSend = computed(() => {
  return selectedRecipient.value && message.value.trim().length > 0
})

// Debounced load recipients to prevent rapid API calls
const loadRecipients = useDebounceFn(async () => {
  if (!selectedRecipientType.value) return

  // Map tab IDs to roles
  const roleMap = {
    'admin': ['admin', 'superadmin'],
    'support': ['support'],
    'writer': ['writer'],
    'editor': ['editor'],
    'client': ['client']
  }

  const roles = roleMap[selectedRecipientType.value] || []
  if (roles.length === 0) return

  // Check cache first
  const cacheKey = selectedRecipientType.value
  const cached = recipientsCache.value.get(cacheKey)
  if (cached && (Date.now() - cached.timestamp) < cacheExpiry) {
    availableRecipients.value = cached.data
    const lastSelectedId = lastSelectedRecipientByType.value.get(selectedRecipientType.value)
    if (lastSelectedId) {
      const match = cached.data.find(recipient => recipient.id === lastSelectedId)
      if (match) {
        selectedRecipient.value = match
        return
      }
    }
    // Auto-select if only one recipient
    if (cached.data.length === 1) {
      selectedRecipient.value = cached.data[0]
    }
    return
  }

  loadingRecipients.value = true
  error.value = ''
  
  try {
    // Fetch users with role filter if API supports it, otherwise filter on frontend
    const response = await usersAPI.list({
      is_active: true,
      role: roles[0], // Try to filter by first role if API supports it
      page_size: 100 // Limit to 100 for performance
    })
    
    const allUsers = response.data.results || response.data || []
    // Filter by roles on the frontend (in case API doesn't filter properly)
    const filtered = allUsers.filter(user =>
      roles.includes(user.role)
    )
    
    // Cache the results
    recipientsCache.value.set(cacheKey, {
      data: filtered,
      timestamp: Date.now()
    })
    
    availableRecipients.value = filtered

    const lastSelectedId = lastSelectedRecipientByType.value.get(selectedRecipientType.value)
    if (lastSelectedId) {
      const match = filtered.find(recipient => recipient.id === lastSelectedId)
      if (match) {
        selectedRecipient.value = match
        return
      }
    }

    // If exactly one recipient, auto-select to streamline the flow
    if (filtered.length === 1) {
      selectedRecipient.value = filtered[0]
    }
  } catch (err) {
    if (import.meta.env.DEV) {
      console.error('Failed to load recipients:', err)
    }
    error.value = 'Failed to load recipients. Please try again.'
  } finally {
    loadingRecipients.value = false
  }
}, 300)

const selectRecipient = (recipient) => {
  selectedRecipient.value = recipient
  if (selectedRecipientType.value) {
    lastSelectedRecipientByType.value.set(selectedRecipientType.value, recipient.id)
  }
  error.value = ''
}

const sendMessage = async () => {
  if (!canSend.value) return

  sending.value = true
  error.value = ''

  try {
    // Use the new general thread creation endpoint
    const threadResponse = await communicationsAPI.createGeneralThread(
      selectedRecipient.value.id,
      message.value.trim(),
      'general'
    )
    
    const thread = threadResponse.data.thread || threadResponse.data

    emit('message-sent')
    resetForm()
  } catch (err) {
    console.error('Failed to send message:', err)
    error.value = err.response?.data?.detail || err.response?.data?.error || 'Failed to send message. Please try again.'
  } finally {
    sending.value = false
  }
}

const resetForm = () => {
  // Keep the current recipient type (tab) so the user doesn't have to reselect it
  // when reopening the modal; just clear the concrete recipient and message.
  selectedRecipient.value = null
  availableRecipients.value = []
  recipientSearch.value = ''
  message.value = ''
  error.value = ''
}

watch(selectedRecipientType, (newVal, oldVal) => {
  // When the user changes the tab, clear the current recipient and reload the list
  if (newVal !== oldVal) {
    selectedRecipient.value = null
    recipientSearch.value = ''
    loadRecipients()
  }
})

watch(
  () => filteredRecipients.value,
  (newList) => {
    if (selectedRecipient.value || !newList || newList.length !== 1) return
    selectRecipient(newList[0])
  }
)

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      resetForm()
      // If a default recipient type is provided and no tab is selected yet, set it
      if (!selectedRecipientType.value && props.defaultRecipientType) {
        selectedRecipientType.value = props.defaultRecipientType
        // loadRecipients will be called by the watcher above
      } else if (selectedRecipientType.value) {
        // If a tab is already selected (e.g., admin preselected), just load its recipients
        loadRecipients()
      }
    }
  }
)

// Icon components
const AdminIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>' }
const ClientIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }
const WriterIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>' }
const EditorIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' }
const SupportIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }
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

