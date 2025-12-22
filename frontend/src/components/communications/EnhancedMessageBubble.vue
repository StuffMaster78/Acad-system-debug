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
        <div v-if="message.message" class="whitespace-pre-wrap break-words">
          {{ message.message }}
        </div>

        <!-- Attachment -->
        <div v-if="message.attachment" class="mt-2">
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
        <div v-if="message.reactions && message.reactions.length > 0" class="mt-2 flex flex-wrap gap-1">
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
        v-if="showReactionPicker"
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
        >
          😊 React
        </button>
        <button
          v-if="!isOwnMessage"
          @click="$emit('reply', message)"
          class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          Reply
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { communicationsAPI } from '@/api'

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

const senderInitials = computed(() => {
  const name = props.message.sender_display_name || props.message.sender?.username || 'U'
  return name.substring(0, 2).toUpperCase()
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

