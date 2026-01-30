<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-2xl w-full shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-bold text-white">New Message</h3>
              <p class="text-sm text-blue-100 mt-1">{{ targetLabel }} #{{ targetId }}</p>
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
        <div class="flex-1 overflow-y-auto p-6 space-y-5">
          <!-- Flow summary -->
          <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
            <span class="font-semibold">You ({{ currentUserRoleLabel }})</span>
            <span v-if="activeRecipientTab">
              &nbsp;→&nbsp;<span class="font-semibold">{{ activeRecipientTab.label }}</span>
            </span>
          </div>

          <!-- Order Context -->
          <section class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
            <p class="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
              About {{ targetLabel }} #{{ targetId }}
            </p>
            <p class="text-xs text-blue-700 dark:text-blue-300">
              This message will be linked to this {{ targetLabelLower }}.
            </p>
          </section>

          <!-- Step 1: Choose who to message -->
          <section class="p-4 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-200 dark:border-gray-700 space-y-3">
            <div class="flex items-center justify-between">
              <label class="block text-sm font-semibold text-gray-800 dark:text-gray-100">
                <span class="flex items-center gap-2">
                  <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-xs font-bold text-white">
                    1
                  </span>
                  Message To
                  <span class="text-red-500">*</span>
                </span>
              </label>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <button
                v-for="tab in visibleRecipientTabs"
                :key="tab.id"
                @click="selectedRecipientType = tab.id; selectedRecipient = null"
                :class="[
                  'p-3 border-2 rounded-xl transition-all text-center flex flex-col items-center justify-center gap-1',
                  selectedRecipientType === tab.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 shadow-sm'
                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                ]"
              >
                <component :is="tab.icon" class="w-5 h-5" />
                <p class="text-xs font-medium">{{ tab.label }}</p>
                <p class="mt-1 text-[11px] text-gray-500 dark:text-gray-400" v-if="tab.tooltip">
                  {{ tab.tooltip }}
                </p>
              </button>
            </div>
          </section>

          <!-- Step 2: Pick a specific recipient (hidden when auto-selected) -->
          <section
            v-if="!selectedRecipient"
            class="p-4 bg-gray-50 dark:bg-gray-900/40 rounded-xl border border-gray-200 dark:border-gray-700 space-y-3"
          >
            <div class="flex items-center justify-between">
              <label class="block text-sm font-semibold text-gray-800 dark:text-gray-100">
                <span class="flex items-center gap-2">
                  <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-xs font-bold text-white">
                    2
                  </span>
                  Select Recipient
                  <span class="text-red-500">*</span>
                </span>
              </label>
              <div v-if="filteredRecipients.length > 0" class="w-40">
                <input
                  v-model="recipientSearch"
                  type="text"
                  placeholder="Search..."
                  class="w-full px-3 py-1.5 text-xs border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                />
              </div>
            </div>

            <div v-if="!selectedRecipientType" class="p-3 text-sm text-gray-500 dark:text-gray-400">
              Choose who you want to message first.
            </div>
            <div v-else-if="loadingRecipients" class="p-3 text-sm text-gray-500 dark:text-gray-400">
              Loading recipients...
            </div>
            <div v-else-if="filteredRecipients.length === 0" class="p-3 text-sm text-gray-500 dark:text-gray-400">
              No {{ selectedRecipientType }} recipients are available for this {{ targetLabelLower }}.
              Try a different recipient type above.
            </div>
            <div v-else class="space-y-2 max-h-40 overflow-y-auto">
              <button
                v-for="recipient in filteredRecipients"
                :key="recipient.id"
                @click="selectRecipient(recipient)"
                class="w-full p-3 text-left border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors flex items-center justify-between gap-3"
              >
                <div class="min-w-0">
                  <div class="font-medium text-sm text-gray-900 dark:text-white truncate">
                    {{ recipient.username || recipient.email || 'User' }}
                  </div>
                  <div v-if="recipient.email" class="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {{ recipient.email }}
                  </div>
                </div>
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 uppercase">
                  {{ (recipient.role || '').replace('_', ' ') || 'recipient' }}
                </span>
              </button>
            </div>
          </section>

          <!-- Step 3: Write your message -->
          <section
            v-if="selectedRecipient"
            class="p-4 bg-white dark:bg-gray-900/60 rounded-xl border border-gray-200 dark:border-gray-700 space-y-2"
          >
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
              :placeholder="`Type your message about this ${targetLabelLower}...`"
              rows="5"
              class="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white resize-none text-sm"
            ></textarea>
            <p v-if="error" class="mt-1 text-xs text-red-600 dark:text-red-400">{{ error }}</p>
          </section>
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
import { ref, computed, watch } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  orderId: {
    type: [Number, String],
    required: false,
    default: null
  },
  specialOrderId: {
    type: [Number, String],
    required: false,
    default: null
  },
  defaultRecipientType: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close', 'message-sent'])

const authStore = useAuthStore()
const currentUser = authStore.user

const targetId = computed(() => props.specialOrderId || props.orderId)
const isSpecial = computed(() => !!props.specialOrderId)
const targetLabel = computed(() => (isSpecial.value ? 'Special Order' : 'Order'))
const targetLabelLower = computed(() => (isSpecial.value ? 'special order' : 'order'))

const currentUserRoleLabel = computed(() => {
  const role = currentUser?.role || 'user'
  return role.charAt(0).toUpperCase() + role.slice(1)
})

const selectedRecipientType = ref(null)
const selectedRecipient = ref(null)
const allOrderRecipients = ref([]) // fetched once per modal open
const availableRecipients = ref([])
const recipientSearch = ref('')
const message = ref('')
const sending = ref(false)
const error = ref('')
const loadingRecipients = ref(false)

const recipientTabs = computed(() => {
  const role = currentUser?.role
  const tabs = []

  if (role === 'client' || role === 'customer') {
    tabs.push(
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Message the admin team about this order.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Get help from support about this order.' },
      { id: 'writer', label: 'Writer', icon: 'WriterIcon', tooltip: 'Talk directly to the assigned writer.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Discuss editing or quality for this order.' }
    )
  } else if (role === 'writer') {
    tabs.push(
      { id: 'client', label: 'Client', icon: 'ClientIcon', tooltip: 'Message the client about order details.' },
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Coordinate with admin about this order.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Get internal help from support.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Work with editors on revisions or reviews.' }
    )
  } else {
    tabs.push(
      { id: 'client', label: 'Client', icon: 'ClientIcon', tooltip: 'Message the client for this order.' },
      { id: 'writer', label: 'Writer', icon: 'WriterIcon', tooltip: 'Talk to the assigned writer for this order.' },
      { id: 'editor', label: 'Editor', icon: 'EditorIcon', tooltip: 'Coordinate with editors on editing/review.' },
      { id: 'support', label: 'Support', icon: 'SupportIcon', tooltip: 'Internal support conversations for this order.' },
      { id: 'admin', label: 'Admin', icon: 'AdminIcon', tooltip: 'Admin/admin conversations related to this order.' }
    )
  }

  return tabs
})

const activeRecipientTab = computed(() => {
  return visibleRecipientTabs.value.find(t => t.id === selectedRecipientType.value) || null
})

// Only show tabs that actually have at least one possible recipient
const visibleRecipientTabs = computed(() => {
  if (!allOrderRecipients.value.length) {
    // Before we know recipients, show all tabs so the user can try them.
    return recipientTabs.value
  }

  const roleMap = {
    admin: ['admin', 'superadmin'],
    support: ['support'],
    writer: ['writer'],
    editor: ['editor'],
    client: ['client', 'customer']
  }

  return recipientTabs.value.filter(tab => {
    const roles = roleMap[tab.id] || []
    if (!roles.length) return false
    return allOrderRecipients.value.some(r => roles.includes(r.role))
  })
})

const filteredRecipients = computed(() => {
  if (!recipientSearch.value) return availableRecipients.value
  
  const search = recipientSearch.value.toLowerCase()
  return availableRecipients.value.filter(recipient => {
    const name = (recipient.username || '').toLowerCase()
    const email = (recipient.email || '').toLowerCase()
    return name.includes(search) || email.includes(search)
  })
})

const canSend = computed(() => {
  return selectedRecipient.value && message.value.trim().length > 0
})

const loadRecipients = async () => {
  if (!selectedRecipientType.value || !targetId.value) return

  loadingRecipients.value = true
  error.value = ''
  availableRecipients.value = []
  
  try {
    const activeTab = recipientTabs.value.find(t => t.id === selectedRecipientType.value)
    if (!activeTab) return

    // Map tab IDs to roles (matches roles returned by order_recipients API)
    const roleMap = {
      admin: ['admin', 'superadmin'],
      support: ['support'],
      writer: ['writer'],
      editor: ['editor'],
      client: ['client', 'customer']
    }

    const roles = roleMap[selectedRecipientType.value] || []
    if (roles.length === 0) return

    // Fetch once per modal open and cache
    if (!allOrderRecipients.value.length) {
      const response = isSpecial.value
        ? await communicationsAPI.getSpecialOrderRecipients(targetId.value)
        : await communicationsAPI.getOrderRecipients(targetId.value)
      allOrderRecipients.value = response.data || []
    }

    availableRecipients.value = allOrderRecipients.value.filter(recipient =>
      roles.includes(recipient.role)
    )

    // If exactly one recipient matches this type, auto-select it to avoid
    // forcing the user through two redundant steps.
    if (availableRecipients.value.length === 1) {
      selectRecipient(availableRecipients.value[0])
    }
  } catch (err) {
    console.error('Failed to load recipients:', err)
    error.value = 'Failed to load recipients. Please try again.'
  } finally {
    loadingRecipients.value = false
  }
}

const selectRecipient = (recipient) => {
  selectedRecipient.value = recipient
  error.value = ''
}

const sendMessage = async () => {
  if (!canSend.value || !selectedRecipient.value) return

  sending.value = true
  error.value = ''

  try {
    // Use the order-specific thread creation endpoint with explicit recipient
    // This ensures threads are created with only sender + recipient, not all participants
    const threadResponse = isSpecial.value
      ? await communicationsAPI.startThreadForSpecialOrder(targetId.value, selectedRecipient.value.id)
      : await communicationsAPI.startThreadForOrder(targetId.value, selectedRecipient.value.id)
    const thread = threadResponse.data.thread || threadResponse.data

    // Send the message with explicit recipient to ensure it's received
    const messageResponse = await communicationsAPI.sendMessage(thread.id, {
      recipient: selectedRecipient.value.id,
      message: message.value.trim(),
      message_type: 'text'
    })

    // Show success feedback
    emit('message-sent', true) // Emit success
    
    // Close modal after a brief delay to show success
    setTimeout(() => {
      resetForm()
      emit('close')
    }, 500)
  } catch (err) {
    console.error('Failed to send message:', err)
    const errorMsg = err.response?.data?.detail || err.response?.data?.error || 'Failed to send message. Please try again.'
    error.value = errorMsg
    emit('message-sent', false) // Emit failure
  } finally {
    sending.value = false
  }
}

const resetForm = () => {
  // Preserve current tab selection; only clear concrete recipient + message state
  selectedRecipient.value = null
  availableRecipients.value = []
  recipientSearch.value = ''
  message.value = ''
  error.value = ''
}

watch(selectedRecipientType, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    selectedRecipient.value = null
    recipientSearch.value = ''
    loadRecipients()
  }
})

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      resetForm()
      const hasDefault = recipientTabs.value.some(tab => tab.id === props.defaultRecipientType)
      if (hasDefault) {
        selectedRecipientType.value = props.defaultRecipientType
      } else {
        selectedRecipientType.value = recipientTabs.value[0]?.id || null
      }
      if (selectedRecipientType.value) {
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

