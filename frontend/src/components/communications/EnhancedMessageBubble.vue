<template>
  <div
    :class="[
      'message-bubble flex gap-3 mb-4',
      isOwnMessage ? 'flex-row-reverse' : 'flex-row'
    ]"
  >
    <!-- Avatar -->
    <div class="shrink-0">
      <div
        :class="[
          'w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm',
          isOwnMessage ? 'bg-primary-600' : 'bg-gray-400'
        ]"
      >
        {{ senderInitials }}
      </div>
    </div>

    <!-- Message Content -->
    <div
      :class="[
        'flex-1 min-w-0',
        isOwnMessage ? 'items-end' : 'items-start'
      ]"
    >
      <!-- Message Header -->
      <div
        :class="[
          'flex items-center gap-2 mb-1',
          isOwnMessage ? 'justify-end' : 'justify-start'
        ]"
      >
        <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ message.sender_display_name || message.sender?.username || 'Unknown' }}
        </span>
        <span class="text-xs text-gray-500 dark:text-gray-400">
          {{ formatTime(message.sent_at) }}
        </span>
        <!-- Read Receipt -->
        <div v-if="isOwnMessage && message.read_receipts?.length > 0" class="flex items-center gap-1">
          <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span class="text-xs text-gray-500">{{ message.read_receipts.length }}</span>
        </div>
      </div>

      <!-- Message Bubble -->
      <div
        :class="[
          'rounded-lg px-4 py-2 max-w-[70%]',
          isOwnMessage
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
        ]"
      >
        <!-- Status / moderation label -->
        <div
          v-if="statusLabel"
          :class="[
            'mb-1 text-[11px] font-semibold uppercase tracking-wide',
            statusClass
          ]"
          :title="moderationTooltip"
          role="status"
          aria-live="polite"
        >
          {{ statusLabel }}
        </div>

        <!-- Reply Preview -->
        <div
          v-if="message.reply_to"
          :class="[
            'mb-2 pb-2 border-l-2 pl-2 text-xs opacity-75',
            isOwnMessage ? 'border-white' : 'border-gray-400'
          ]"
        >
          <div class="font-medium">{{ message.reply_to?.sender_display_name }}</div>
          <div class="truncate">{{ message.reply_to?.message }}</div>
        </div>

        <!-- Message Text -->
        <div
          v-if="!hideContent && message.message"
          class="whitespace-pre-wrap wrap-break-word"
        >
          <template v-for="(segment, index) in parsedMessage" :key="index">
            <span v-if="segment.type === 'text'">{{ segment.content }}</span>
            <router-link
              v-else-if="segment.type === 'link'"
              :to="segment.to"
              :class="[
                'underline font-medium',
                isOwnMessage
                  ? 'text-primary-200 hover:text-primary-100'
                  : 'text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300'
              ]"
            >
              {{ segment.content }}
            </router-link>
          </template>
        </div>

        <!-- Attachment -->
        <div v-if="!hideContent && message.attachment" class="mt-2">
          <div
            class="flex items-center gap-2 p-2 bg-white dark:bg-gray-800 rounded border cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            @click="downloadAttachment"
          >
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
            <span class="text-sm flex-1 truncate">{{ getFileName(message.attachment) }}</span>
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
        </div>

        <!-- Reactions -->
        <div v-if="!hideContent && message.reactions && message.reactions.length > 0" class="mt-2 flex flex-wrap gap-1">
          <button
            v-for="reactionGroup in message.reactions"
            :key="reactionGroup.reaction"
            @click="toggleReaction(reactionGroup.reaction)"
            :class="[
              'flex items-center gap-1 px-2 py-1 rounded-full text-xs border transition-colors',
              hasUserReacted(reactionGroup.reaction)
                ? 'bg-primary-100 dark:bg-primary-900 border-primary-300 dark:border-primary-700'
                : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            <span>{{ reactionGroup.reaction }}</span>
            <span class="font-medium">{{ reactionGroup.count }}</span>
          </button>
        </div>
      </div>

      <!-- Reaction Picker -->
      <div
        v-if="showReactionPicker && !hideContent"
        class="mt-1 flex gap-1 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700"
      >
        <button
          v-for="reaction in availableReactions"
          :key="reaction"
          @click="addReaction(reaction)"
          class="text-2xl hover:scale-125 transition-transform p-1"
        >
          {{ reaction }}
        </button>
      </div>

      <!-- Action Buttons -->
      <div
        :class="[
          'flex items-center gap-2 mt-1 text-xs',
          isOwnMessage ? 'justify-end' : 'justify-start'
        ]"
      >
        <button
          @click="showReactionPicker = !showReactionPicker"
          class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          v-if="!hideContent"
        >
          😊 React
        </button>
        <button
          v-if="!isOwnMessage && !hideContent"
          @click="$emit('reply', message)"
          class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          Reply
        </button>
        
        <!-- Admin Menu -->
        <div v-if="canManageMessage" class="relative">
          <button
            @click="showAdminMenu = !showAdminMenu"
            class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
            Admin
          </button>
          
          <!-- Admin Dropdown Menu -->
          <div
            v-if="showAdminMenu"
            class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
            @click.stop
          >
            <div class="py-1">
              <button
                @click="openEditModal"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit Message
              </button>
              <button
                v-if="!message.is_hidden"
                @click="openShadowModal"
                class="w-full text-left px-4 py-2 text-sm text-orange-700 dark:text-orange-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                Shadow Message
              </button>
              <button
                v-else
                @click="handleUnshadow"
                class="w-full text-left px-4 py-2 text-sm text-green-700 dark:text-green-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Unshadow Message
              </button>
              <button
                @click="handleDelete"
                class="w-full text-left px-4 py-2 text-sm text-red-700 dark:text-red-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Message
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Edit Message Modal -->
      <div
        v-if="showEditModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="showEditModal = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Message</h3>
          <textarea
            v-model="editMessageText"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter message text..."
          ></textarea>
          <div class="flex justify-end gap-2 mt-4">
            <button
              @click="showEditModal = false; editMessageText = ''"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              @click="handleEdit"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Save
            </button>
          </div>
        </div>
      </div>
      
      <!-- Shadow Message Modal -->
      <div
        v-if="showShadowModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="showShadowModal = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Shadow Message</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Shadowing a message will hide it from regular participants. Only admins will be able to see it.
          </p>
          <textarea
            v-model="shadowReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white mb-4"
            placeholder="Enter reason for shadowing (required)..."
          ></textarea>
          <div class="flex justify-end gap-2">
            <button
              @click="showShadowModal = false; shadowReason = ''"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              @click="handleShadow"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              Shadow Message
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import communicationsAPI from '@/api/communications'
import { parseMessageLinks } from '@/utils/messageUtils'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  threadId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['reaction-updated', 'reply', 'attachment-downloaded'])

const authStore = useAuthStore()
const showReactionPicker = ref(false)

const availableReactions = ['👍', '❤️', '😊', '🎉', '✅', '❌', '⚠️', '💡']

const isOwnMessage = computed(() => {
  return props.message.sender?.id === authStore.user?.id || props.message.is_sender
})

const statusLabel = computed(() => {
  const msg = props.message || {}
  // Explicit admin deletion
  if (msg.is_deleted) {
    return 'Deleted by admin'
  }
  // Check if message is hidden/shadowed
  if (msg.is_hidden || msg.is_flagged) {
    // Determine reason for shadowing
    if (msg.attachment || msg.message_type === 'file' || msg.message_type === 'image') {
      return 'Pending review (attachment)'
    }
    if (msg.contains_link || msg.message_type === 'link') {
      return 'Pending review (link)'
    }
    if (msg.is_flagged && !msg.is_unblocked) {
      return 'Flagged (screened words)'
    }
    // Admin shadowing (is_hidden flag)
    if (msg.is_hidden) {
      return 'Shadowed by admin'
    }
  }
  // System shadowing (e.g. auto-moderation)
  if (msg.is_system && (msg.system_type === 'shadowed' || msg.system_type === 'auto_shadow')) {
    return 'Shadowed by system'
  }
  return ''
})

const statusClass = computed(() => {
  const label = statusLabel.value
  if (label.startsWith('Deleted')) {
    return 'text-red-500 dark:text-red-300'
  }
  if (label.startsWith('Shadowed')) {
    return 'text-orange-500 dark:text-orange-300'
  }
  if (label.startsWith('Flagged')) {
    return 'text-amber-600 dark:text-amber-300'
  }
  return 'text-gray-500 dark:text-gray-400'
})

const moderationTooltip = computed(() => {
  const msg = props.message || {}
  if (msg.is_deleted) {
    return 'This message was deleted by an admin. Its original content is hidden from participants.'
  }
  if (msg.is_system && (msg.system_type === 'shadowed' || msg.system_type === 'auto_shadow')) {
    return 'This message was shadowed by the system (for example, due to moderation rules). It is hidden from regular participants.'
  }
  if (msg.is_flagged && !msg.is_unblocked) {
    return 'This message was flagged because it contains screened or banned words. It may require moderator review.'
  }
  return ''
})

const hideContent = computed(() => {
  const msg = props.message || {}
  // Hide full content when admin deleted OR shadowed (by admin or system);
  // still keep the header + status label.
  // Admins can always see the content
  if (canManageMessage.value) return false
  
  // Hide deleted messages
  if (msg.is_deleted) return true
  
  // Hide shadowed/flagged messages (attachments, links, screened words)
  // Writers and clients cannot see shadowed messages until admin approves
  if (msg.is_hidden || (msg.is_flagged && !msg.is_unblocked)) return true
  
  // Hide system shadowed messages
  if (msg.is_system && (msg.system_type === 'shadowed' || msg.system_type === 'auto_shadow')) return true
  
  return false
})

const canManageMessage = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'superadmin'
})

const showAdminMenu = ref(false)
const showEditModal = ref(false)
const editMessageText = ref('')
const shadowReason = ref('')
const showShadowModal = ref(false)

const senderInitials = computed(() => {
  const name = props.message.sender_display_name || props.message.sender?.username || 'U'
  return name.substring(0, 2).toUpperCase()
})

const parsedMessage = computed(() => {
  if (!props.message.message) return []
  return parseMessageLinks(props.message.message)
})

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`
  return date.toLocaleDateString()
}

const getFileName = (attachment) => {
  if (typeof attachment === 'string') {
    return attachment.split('/').pop() || 'File'
  }
  return attachment?.name || 'File'
}

const hasUserReacted = (reaction) => {
  const reactionGroup = props.message.reactions?.find(r => r.reaction === reaction)
  if (!reactionGroup) return false
  return reactionGroup.users?.some(u => u.user_id === authStore.user?.id) || false
}

const addReaction = async (reaction) => {
  try {
    if (hasUserReacted(reaction)) {
      await communicationsAPI.removeReaction(props.threadId, props.message.id, reaction)
    } else {
      await communicationsAPI.addReaction(props.threadId, props.message.id, reaction)
    }
    showReactionPicker.value = false
    emit('reaction-updated')
  } catch (error) {
    console.error('Failed to toggle reaction:', error)
  }
}

const toggleReaction = (reaction) => {
  addReaction(reaction)
}

const handleDelete = async () => {
  if (!canManageMessage.value) return
  const confirmed = window.confirm('Delete this message for everyone? This cannot be undone.')
  if (!confirmed) return

  try {
    await communicationsAPI.deleteMessage(props.threadId, props.message.id)
    showAdminMenu.value = false
    emit('reaction-updated') // reuse event to trigger refresh
  } catch (error) {
    console.error('Failed to delete message:', error)
    alert('Failed to delete message: ' + (error.response?.data?.detail || error.message))
  }
}

const handleShadow = async () => {
  if (!canManageMessage.value) return
  if (!shadowReason.value.trim()) {
    alert('Please provide a reason for shadowing this message.')
    return
  }

  try {
    await communicationsAPI.shadowMessage(props.threadId, props.message.id, shadowReason.value)
    showShadowModal.value = false
    shadowReason.value = ''
    showAdminMenu.value = false
    emit('reaction-updated')
  } catch (error) {
    console.error('Failed to shadow message:', error)
    alert('Failed to shadow message: ' + (error.response?.data?.detail || error.message))
  }
}

const handleUnshadow = async () => {
  if (!canManageMessage.value) return
  const confirmed = window.confirm('Unshadow this message? It will be visible to all participants.')
  if (!confirmed) return

  try {
    await communicationsAPI.unshadowMessage(props.threadId, props.message.id)
    showAdminMenu.value = false
    emit('reaction-updated')
  } catch (error) {
    console.error('Failed to unshadow message:', error)
    alert('Failed to unshadow message: ' + (error.response?.data?.detail || error.message))
  }
}

const handleEdit = async () => {
  if (!canManageMessage.value) return
  if (!editMessageText.value.trim()) {
    alert('Message cannot be empty.')
    return
  }

  try {
    await communicationsAPI.editMessage(props.threadId, props.message.id, {
      message: editMessageText.value
    })
    showEditModal.value = false
    editMessageText.value = ''
    showAdminMenu.value = false
    emit('reaction-updated')
  } catch (error) {
    console.error('Failed to edit message:', error)
    alert('Failed to edit message: ' + (error.response?.data?.detail || error.message))
  }
}

const openEditModal = () => {
  editMessageText.value = props.message.message || ''
  showEditModal.value = true
  showAdminMenu.value = false
}

const openShadowModal = () => {
  shadowReason.value = ''
  showShadowModal.value = true
  showAdminMenu.value = false
}

// Close admin menu when clicking outside
let clickOutsideHandler = null
onMounted(() => {
  clickOutsideHandler = (event) => {
    if (showAdminMenu.value && !event.target.closest('.relative')) {
      showAdminMenu.value = false
    }
  }
  document.addEventListener('click', clickOutsideHandler)
})

onUnmounted(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler)
  }
})

const downloadAttachment = async () => {
  try {
    const blob = await communicationsAPI.downloadAttachment(props.threadId, props.message.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = getFileName(props.message.attachment)
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    emit('attachment-downloaded')
  } catch (error) {
    console.error('Failed to download attachment:', error)
  }
}
</script>

<style scoped>
.message-bubble {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

